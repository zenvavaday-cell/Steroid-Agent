---
name: agent-evaluation-harness
description: Builds reproducible evaluations with datasets, graders, budgets, and regression gates. Use before shipping agent changes and for model comparisons.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: agentic
---

# Agent Evaluation Harness

## Overview

Agent quality cannot be established from a handful of demos. The same prompt can succeed, loop, call the wrong tool, or produce a plausible but ungrounded answer on consecutive runs. A harness turns that variance into a measured distribution with a decision attached.

The harness needs four things: a task set that represents real use, an environment that resets cleanly, graders whose error rates are known, and gates that distinguish a real regression from noise. Without all four, the score is theater.

## When to use

- Before shipping a prompt, model, tool, or orchestration change.
- Comparing two models or two agent architectures on the same work.
- Building a regression suite for an agent already in production.
- Selecting a benchmark or deciding whether a public score is relevant.
- Investigating a quality complaint with a reproducible case.
- Setting release gates for cost, latency, and safety.

Do not use for deterministic functions with no model in the loop (use unit tests), or as a replacement for production monitoring and user feedback.

## Workflow

### 1. State the decision and the metrics

Write the decision the eval informs before choosing metrics.

| Decision | Primary metric | Guardrails |
| --- | --- | --- |
| Ship a prompt change | Task success rate | Cost per success, p95 latency, unsafe actions |
| Switch models | Success at fixed budget | Cost, latency, refusal rate |
| Add a tool | Task success on tool-dependent slice | Wrong-tool rate, side-effect errors |
| Increase autonomy | Completion rate | Unsafe action rate, human overrides |
| Tighten latency | p95 end-to-end latency | Success rate drop, timeout rate |

Define success per task in observable terms: tests pass, the record exists in the database, the answer cites a valid span, or the human rubric score is at least 4 of 5. "Looks good" is not a grader.

### 2. Build a dataset with slices and a holdout

| Source | Strength | Risk |
| --- | --- | --- |
| Production traces | Real distribution | PII, stale cases, survivorship bias |
| Handwritten tasks | Targets known failures | Does not represent frequency |
| Synthetic variants | Cheap coverage | Model-generated blind spots |
| Public benchmarks | Comparability | Contamination, different domain |

Start with 50 to 300 tasks. Cover intents, difficulty tiers, tool counts, languages, document lengths, and adversarial cases. Include tasks that should be refused or escalated, not only tasks with a successful action.

Keep a held-out split that is never used for prompt iteration. Check contamination by searching prompts and few-shot examples for task text, and by measuring n-gram overlap with public benchmark items. Store tasks in version control with stable IDs.

### 3. Freeze the environment

An agent eval is an experiment. Control the variables:

- Run in a container with pinned dependencies and a fixed browser or runtime version.
- Disable network access (`--network none`) or route through recorded fixtures.
- Seed random number generators and any simulated data.
- Freeze the clock (`faketime` or an injected clock) when dates affect behavior.
- Reset databases, filesystems, and queues from a snapshot before each trial.
- Record model IDs, temperature, top_p, tool versions, and prompt hashes.

If the environment cannot be reset, grade only read-only tasks or isolate each trial in its own namespace.

### 4. Choose graders and measure them

| Grader | Use for | Failure mode |
| --- | --- | --- |
| Exact match or normalized match | Labels, IDs, short answers | Brittle to valid paraphrases |
| Unit tests | Code, SQL, config | Tests may encode the wrong behavior |
| State assertions | Tool side effects, files, records | Missing negative checks |
| Schema validation | Structured outputs | Valid shape, wrong content |
| Rubric LLM judge | Open-ended answers, plans | Bias, drift, leniency |
| Human review | High-stakes or ambiguous cases | Cost, inconsistency |

Calibrate LLM judges against at least 100 human-labeled outputs. Report agreement and Cohen's kappa (0.6 or higher is a reasonable starting bar). Test position bias by swapping candidate order, and verbosity bias by comparing short and long correct answers. Pin the judge model version and prompt; a judge upgrade is an eval change, not a maintenance detail.

Prefer deterministic graders. Use an LLM judge only where the output space cannot be enumerated, and keep a human-reviewed subset.

### 5. Run multiple trials within budgets

```yaml
run:
  trials: 5
  temperature: 1.0
  seed: 7
  max_steps: 20
  max_tool_calls: 30
  max_tokens_per_task: 100000
  max_cost_usd_per_task: 0.50
  wall_clock_s_per_task: 120
  retries: 2
  concurrency: 4
```

Log retries as attempts, not as fresh successes. If the agent can retry a failed task, report both first-attempt and eventual success. Record every trial's transcript, tool calls, token counts, and cost.

### 6. Compute metrics with uncertainty

```python
import math
import random

def pass_at_k(n, c, k):
    if n - c < k:
        return 1.0
    return 1.0 - math.prod((n - i - c) / (n - i) for i in range(k))

def bootstrap_ci(values, reps=2000, alpha=0.05, seed=7):
    rng = random.Random(seed)
    means = []
    for _ in range(reps):
        sample = [values[rng.randrange(len(values))] for _ in values]
        means.append(sum(sample) / len(sample))
    means.sort()
    return means[int(alpha / 2 * reps)], means[int((1 - alpha / 2) * reps) - 1]
```

Report:

- Task success rate with a bootstrap confidence interval.
- `pass@k` for capability and `pass^k` (all k trials succeed) for reliability.
- Cost per successful task, not just cost per call.
- p50 and p95 latency, including tool time.
- Unsafe action rate and wrong-tool rate as separate guardrails.
- Per-slice results, never only the aggregate.

A single aggregate can hide a 20-point regression in one important slice. Publish the slice table with the headline number.

### 7. Gate, triage, and report

```yaml
gates:
  - metric: task_success
    compare: baseline
    max_drop: 0.03
  - metric: unsafe_action_rate
    max: 0.0
  - metric: p95_latency_ms
    max: 8000
  - metric: cost_per_success_usd
    max: 0.60
```

Block on guardrail violations and on a statistically credible success drop. A 1-point drop with overlapping intervals is noise; a 3-point drop with non-overlapping intervals is a regression. Quarantine flaky tasks with an owner and a review date instead of silently deleting them.

Triage failures into: retrieval, reasoning, tool selection, argument construction, environment, grader error, and timeout. Store at least one failing trace per category with the run ID.

## Validation

Validate the harness before trusting its scores.

```bash
pytest tests/evals -q
python -m evals.run --suite agent-core --trials 5 --seed 7 --output runs/2026-11-26.json
python -m evals.compare --baseline runs/baseline.json --candidate runs/2026-11-26.json
```

Pass criteria:

- [ ] A known-good reference agent scores above a known-bad stub on every suite.
- [ ] Grader agreement with human labels is at least 80%, kappa at least 0.6.
- [ ] Judge order-swap disagreement is below 5%.
- [ ] Re-running the same agent and seed changes aggregate success by at most 2 points; if not, variance is reported, not hidden.
- [ ] The suite passes with network disabled.
- [ ] No task text from the held-out split appears in prompts or few-shot examples.
- [ ] Cost accounting reconciles with provider invoices within 5%.
- [ ] Timeouts are classified separately from incorrect answers.
- [ ] Every task has a stable ID, a success definition, and an owning slice.
- [ ] The gate fails when the unsafe action rate is nonzero.

## Gotchas

- One trial per task hides instability. Use at least three, five for high-stakes suites.
- An LLM judge with position bias rewards whichever answer appears first. Swap order and average.
- A judge that prefers longer answers turns verbosity into score. Use a rubric with explicit length-neutral criteria.
- Test leakage into prompts or fine-tuning data inflates results. Keep a held-out set and check overlap.
- Flaky environments look like model regressions. Reset state and quarantine infrastructure failures.
- Aggregates hide slice regressions. Gate the important slices explicitly.
- `pass@k` rises with retries and temperature. Report attempts and settings alongside the number.
- Tool mocks drift from real APIs. Contract-test mocks against the live schema on a schedule.
- Grading the transcript instead of environment state misses side effects. Assert on the database, files, and outbound calls.
- Ignoring cost produces a quality win that cannot ship. Make cost per success a first-class metric.
- Overfitting to the eval is easy when the same tasks drive every decision. Rotate cases and hold out a final set.
- Upgrading the judge model silently changes the scale. Re-baseline and version the judge.
- Counting a timeout as a wrong answer hides reliability problems. Report it separately.
- A baseline that moves with each run makes regressions invisible. Freeze the baseline per release.

## Output contract

```json
{
  "run_id": "eval-2026-11-26-01",
  "suite": "agent-core",
  "suite_version": "3.2.0",
  "agent": {"model": "example-model", "temperature": 1.0, "prompt_hash": "sha256:..."},
  "trials_per_task": 5,
  "tasks": 120,
  "metrics": {
    "success_rate": 0.78,
    "success_ci95": [0.71, 0.84],
    "pass_at_5": 0.91,
    "pass_pow_5": 0.63,
    "cost_per_success_usd": 0.42,
    "p95_latency_ms": 7400,
    "unsafe_action_rate": 0.0
  },
  "slices": [{"name": "tool-heavy", "tasks": 30, "success_rate": 0.70, "delta_vs_baseline": -0.04}],
  "gate": {"status": "fail", "reasons": ["tool-heavy success drop exceeds 0.03"]},
  "failures": [{"task_id": "T-0142", "category": "tool_selection", "trace": "runs/eval-2026-11-26-01/T-0142.jsonl"}],
  "baseline": "runs/baseline-2026-11-20.json"
}
```

## Checklist

- [ ] Decision and primary metric stated before building the suite.
- [ ] Dataset covers intents, difficulty, tools, languages, and refusals.
- [ ] Held-out split isolated from prompt iteration.
- [ ] Contamination check completed.
- [ ] Environment pinned, seeded, clock-frozen, and reset per trial.
- [ ] Graders deterministic where possible and calibrated against human labels.
- [ ] Judge position and verbosity bias tested.
- [ ] Multiple trials run with budgets for steps, tokens, cost, and time.
- [ ] Confidence intervals and per-slice results reported.
- [ ] Cost per success and p95 latency tracked.
- [ ] Regression and safety gates defined in CI.
- [ ] Every failure category has a stored trace and an owner.

## Related skills

- `model-evaluation-benchmarking` for holdout design, slices, and uncertainty reporting.
- `flaky-test-detection` for separating environment noise from agent regression.
- `cost-aware-model-routing` for turning eval results into routing decisions.
- `agent-observability-tracing` for trace capture and replay of failed runs.
