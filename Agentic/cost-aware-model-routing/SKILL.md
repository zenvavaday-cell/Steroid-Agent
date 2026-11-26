---
name: cost-aware-model-routing
description: Routes tasks to models by quality, price, latency, and fallback policy, with measured outcomes. Use for multi-model agents and cost control.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: agentic
---

# Cost-Aware Model Routing

## Overview

A multi-model agent that always calls the strongest model pays for reasoning it does not need. A router picks the cheapest model that still clears a measured quality floor for the task class, then escalates or falls back only when evidence requires it.

The discipline is measurement first: quality per task class, cost per successful task, escalation rate, and latency. Prices and model behavior change, so routing policy is a versioned artifact with an owner and a recalibration date, not a hardcoded model name.

## When to use

- The agent can call two or more models with different price and quality.
- Monthly model spend is material enough to track (for example, above USD 500).
- The workload mixes easy and hard tasks (classification, extraction, drafting, planning).
- A provider outage or rate limit must degrade gracefully instead of failing the run.
- You need to explain model selection to finance, product, or security reviewers.
- You are choosing between a frontier model and a smaller distilled model.

Do not use when a single model meets every task with ample margin and spend is negligible; the routing layer adds latency and maintenance for no gain.

## Workflow

1. **Define task classes from observable features.** Classify on task type, input size bucket, required output schema, stakes tier, and latency SLO. Start with rules (`if output_schema and input_tokens < 2000: extraction`), then replace with a small classifier only if rules misclassify more than 10% of a labeled sample.

2. **Build a per-class quality set and grader.** Use 30 to 100 labeled examples per class, including a critical slice (long inputs, non-English, adversarial cases). Grade deterministically where possible (schema validity, exact match, unit tests) and with a rubric otherwise. Measure each candidate model on the same set.

3. **Maintain a price table with provenance.** Record input, output, cached-input, and reasoning-token prices, currency, effective date, and source URL. Compute per-request cost from actual usage fields, not from character counts. Include retry and escalation overhead in the estimate.

4. **Set quality floors and eligibility.** Example policy (illustrative):

```yaml
policy_version: "2026-11-01"
task_classes:
  extraction:
    quality_floor: 0.95        # exact-match on required fields
    p95_latency_ms: 2500
    max_cost_per_request_usd: 0.02
    candidates: [small-extract-v2, mid-general-v1, frontier-v1]
  drafting:
    quality_floor: 0.80        # rubric score >= 4/5
    p95_latency_ms: 9000
    max_cost_per_request_usd: 0.25
    candidates: [mid-general-v1, frontier-v1]
escalation_cap_rate: 0.20
```

Eligible models meet both the quality floor and the latency SLO. Among eligible models, choose the lowest expected cost per successful task.

5. **Implement a bounded cascade.** Try the cheapest eligible model. Validate the output against schema and a confidence signal. Escalate only on validation failure, low confidence, or an explicit hard-task signal. Cap attempts at 2 and charge both attempts to the request budget.

```python
def route(task, policy, models):
    eligible = [m for m in policy.candidates[task.cls]
                if m.quality[task.cls] >= policy.quality_floor[task.cls]
                and m.p95_ms <= policy.p95_latency_ms[task.cls]]
    if not eligible:
        raise NoEligibleModel(task.cls)
    eligible.sort(key=lambda m: m.expected_cost(task))
    for attempt, model in enumerate(eligible[:2]):
        result = model.call(task, max_tokens=task.max_tokens)
        if result.valid and result.confidence >= policy.confidence_floor:
            return Decision(model, result, escalated=attempt > 0)
    return Decision(eligible[0], result, escalated=True, status="unverified")
```

6. **Wire fallback and circuit breakers.** On 429, 5xx, or timeout, fall through to the next eligible model without changing the task class. Open a circuit after 5 consecutive failures in 60 seconds, probe with one request every 30 seconds, and record which model served each request.

7. **Measure and recalibrate.** Log decision, task class, model, token usage, cost, quality signal, escalation, and fallback. Review weekly: cost per successful task, quality by slice, escalation rate, and refusal rate. Re-run the quality set after any provider model update, and pin dated model versions when available.

## Validation

| Gate | Check | Pass criterion |
| --- | --- | --- |
| Quality | Run per-class holdout set | Point estimate >= floor and lower 95% CI bound within 0.03 |
| Cost | Sum cost / successful tasks over 7 days | <= target for each task class |
| Escalation | Escalated requests / total | <= `escalation_cap_rate` |
| Latency | Router overhead plus model p95 | <= class SLO |
| Fallback | Inject 429 and 500 from primary | Request succeeds on next model, trace shows fallback |
| Freshness | Price table age and model version | Prices < 30 days old, versions pinned |
| Coverage | Task classes with eval coverage | 100%, no unmeasured class in production |

A failed gate blocks rollout. Shadow the new policy on live traffic first, compare offline metrics, then enable for 5% before full traffic.

## Gotchas

- Comparing sticker price per token ignores retries, reasoning tokens, and escalation. Optimize cost per successful task instead.
- Quality measured on a public benchmark can be contaminated or unrepresentative. Use your own labeled set.
- A cheap model can pass the average and fail one critical slice (long context, non-English, structured output). Gate on slices.
- The classifier itself adds latency and cost. Prefer rules and cache classifications by input hash.
- Output length is a hidden cost driver. Set `max_tokens` per task class and measure completion length.
- Cached-input discounts change the ranking. Track cache hit rate and price cached tokens separately.
- A cascade that retries both models on every failure can cost more than the frontier model alone. Cap attempts and count total spend.
- Provider model aliases update silently. Pin dated versions and rerun evals on change.
- Fallback models differ in tool-call format, context limit, and refusal behavior. Test compatibility, not just availability.
- Routing prompts or documents to a third-party provider can violate data policy. Check residency and retention per class.
- Escalation thresholds tuned once drift as traffic changes. Track escalation rate and recalibrate monthly.
- Averaging cost across tenants hides one tenant's runaway usage. Track per-tenant budgets and quotas.

## Output contract

```json
{
  "decision_id": "route-2026-11-26-0042",
  "task_class": "extraction",
  "policy_version": "2026-11-01",
  "model": "small-extract-v2",
  "eligible_models": ["small-extract-v2", "mid-general-v1"],
  "reason": "lowest_cost_meeting_floor",
  "estimated_cost_usd": 0.0041,
  "actual_cost_usd": 0.0038,
  "usage": {"input_tokens": 1820, "output_tokens": 210, "cached_input_tokens": 0},
  "quality_signal": {"schema_valid": true, "confidence": 0.97},
  "escalated": false,
  "fallback_from": null,
  "latency_ms": 940
}
```

Return one decision object per model call and a run-level rollup with total cost, escalation rate, and per-model counts.

## Checklist

- [ ] Task classes defined from observable features.
- [ ] Labeled quality set exists per class, including critical slices.
- [ ] Quality floors and latency SLOs written down and approved.
- [ ] Price table has effective date, source, and owner.
- [ ] Only models clearing the floor are eligible.
- [ ] Cascade capped at two attempts with cost counted.
- [ ] Fallback tested with 429, 500, and timeout injection.
- [ ] Model versions pinned, not floating aliases.
- [ ] Data policy checked for every candidate provider.
- [ ] Per-request and per-tenant budgets enforced.
- [ ] Decision logs include cost, quality signal, and escalation.
- [ ] Recalibration scheduled with an owner and a date.

## Related skills

- `agent-evaluation-harness` for building the per-class quality sets and regression gates this policy depends on.
- `latency-budget-orchestration` for holding model calls to an end-to-end deadline.
- `agent-observability-tracing` for capturing token usage, cost, and route decisions in traces.
- `guardrail-policy-enforcement` for blocking model or provider choices that violate data policy.
