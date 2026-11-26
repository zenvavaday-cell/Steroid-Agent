---
name: latency-budget-orchestration
description: Allocates end-to-end time budgets across tools and model calls, and degrades gracefully under deadline pressure. Use for interactive agents and voice interfaces.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: agentic
---

# Latency Budget Orchestration

## Overview

Users experience one deadline, not a sum of per-call timeouts. Orchestration assigns a single end-to-end budget, splits it across stages, propagates an absolute deadline to every call, and chooses a degradation path when the deadline is at risk.

The core rule: a deadline is absolute and shared. Each call receives the remaining time, cancellation propagates to work in flight, and partial results are better than a missed deadline with nothing to show.

## When to use

- A user waits for the answer (chat, voice, copilot, search).
- The agent makes multiple sequential or parallel calls.
- You have an SLO for first token, first byte, or full answer.
- Some steps are optional enrichment that can be skipped.
- Downstream services have variable latency or cold starts.
- Voice or telephony imposes hard turn-taking limits.

Do not use for offline batch jobs where total throughput and cost matter more than tail latency.

## Workflow

1. **Define the SLO by surface.** Examples, to be replaced with your measured targets: voice first audio 500 ms and end of turn 1200 ms; chat first token 1.5 s and full answer 10 s; background agent 60 s. Record p50, p95, and p99 targets, not just an average.

2. **Set one absolute deadline.** At request start compute `deadline = monotonic_now() + budget_ms - safety_margin_ms`, with a margin of 10 to 20% for network and rendering. Store it in the run context and pass it to every child call.

3. **Allocate stage budgets.** Example for a 10 s chat answer:

| Stage | Budget | Optional | Failure behavior |
| --- | --- | --- | --- |
| Auth and policy check | 150 ms | No | Fail request |
| Query planning (LLM) | 1200 ms | No | Use rule-based fallback |
| Retrieval | 800 ms | Yes | Answer without retrieval, flag it |
| Tool calls (parallel) | 2000 ms | Mixed | Drop optional tools, keep required |
| Answer generation | 4500 ms | No | Reduce max tokens |
| Guardrail and format check | 500 ms | No | Fail closed |
| Slack | 850 ms | n/a | Absorb variance |

The allocations must sum to less than the budget after margin.

4. **Propagate remaining time, never a fresh timeout.** Wrap every call:

```python
class Deadline:
    def __init__(self, budget_s: float, margin_s: float = 0.15):
        self.end = time.monotonic() + budget_s - margin_s

    def remaining(self) -> float:
        return max(0.0, self.end - time.monotonic())

    def timeout_for(self, stage_cap_s: float) -> float:
        return min(stage_cap_s, self.remaining())
```

Pass the deadline object (or an absolute timestamp in a header such as `x-request-deadline-ms`) to tools. A tool that receives 200 ms must not start a 30 s default retry loop. Convert to wall clock only at process boundaries and back to monotonic inside.

5. **Parallelize independent reads and hedge sparingly.** Run independent retrievals and read-only tools concurrently under a semaphore. Hedge a slow read only after its p95, and only for idempotent calls, because hedges double cost and load.

6. **Apply a fixed degradation ladder.** In order: trim optional context, skip optional tools, lower `max_tokens`, serve a cached or stale result with a label, switch to a smaller model that still clears the quality floor, stream a partial answer with `partial: true`. Never silently return a degraded answer as complete.

7. **Cancel and account.** On client disconnect or deadline expiry, abort in-flight calls with the request context, stop spending, and release connections. Count every attempt, including retries and hedges, against the budget. Emit stage timings and the degradation reason.

## Validation

- **Deadline propagation:** assert that no outbound call timeout exceeds `deadline.remaining()` at call time; unit test with a fake clock.
- **Injected latency:** in staging, add 2x p95 delay to each dependency and confirm p95 end-to-end still meets SLO via the degradation ladder.
- **Cancellation:** abort a client request mid-run and assert all in-flight calls stop within 100 ms and no further tokens are billed.
- **Stage accounting:** in 100 sampled traces, allocated plus slack equals the budget and no stage exceeds its cap without a recorded degradation.
- **Partial labeling:** every degraded response carries `partial: true` and a reason code; a test fails if not.
- **Tail check:** p99 over a production-like replay is within 1.2x the SLO, or the ladder needs tuning.

Fail any gate and do not ship the change.

## Gotchas

- Per-step timeouts do not compose into an end-to-end guarantee. Use one shared deadline.
- Retries consume wall clock invisibly. Charge each attempt against the remaining budget.
- Connection pool waits, DNS, and TLS handshakes are real latency. Reserve budget for them.
- First token and full completion are different SLOs. Optimize and measure both.
- A timeout that does not cancel the underlying work still burns cost and capacity.
- Relative timeouts passed across services suffer from clock skew. Pass absolute deadlines and convert locally.
- Hedged requests duplicate cost and can duplicate side effects. Hedge read-only calls only.
- Degrading to a smaller model can break the quality floor. Pair degradation with a confidence gate.
- Parallel fan-out can saturate rate limits and make tail latency worse. Cap concurrency.
- Averages hide the tail that violates the SLO. Track p95 and p99.
- Server-side timings omit network and rendering. Measure at the client when possible.
- Streaming a partial answer then failing confuses users. Mark the terminal state explicitly.

## Output contract

```json
{
  "run_id": "run-2026-11-26-0117",
  "surface": "chat",
  "budget_ms": 10000,
  "deadline_epoch_ms": 1795689600000,
  "status": "partial",
  "stages": [
    {"name": "policy", "allocated_ms": 150, "actual_ms": 88, "status": "ok"},
    {"name": "planning", "allocated_ms": 1200, "actual_ms": 1040, "status": "ok"},
    {"name": "retrieval", "allocated_ms": 800, "actual_ms": 800, "status": "timeout_skipped"},
    {"name": "generation", "allocated_ms": 4500, "actual_ms": 3120, "status": "ok"}
  ],
  "degradations": ["retrieval_skipped"],
  "partial": true,
  "total_ms": 8460,
  "cancelled_calls": 1
}
```

## Checklist

- [ ] SLO defined per surface with p95 and p99 targets.
- [ ] One absolute deadline created at request entry.
- [ ] Stage budgets sum below the deadline after margin.
- [ ] Every call computes timeout from remaining time.
- [ ] Retries and hedges counted against the budget.
- [ ] Independent reads parallelized with a concurrency cap.
- [ ] Degradation ladder ordered and documented.
- [ ] Partial results labeled with a reason code.
- [ ] Cancellation propagates to in-flight calls.
- [ ] Stage timings emitted for every run.
- [ ] Latency injection test passes in staging.
- [ ] Tail latency reviewed after each release.

## Related skills

- `bounded-multi-tool-orchestration` for step and cost budgets that complement the time budget.
- `cost-aware-model-routing` for choosing a smaller model during degradation without dropping below the quality floor.
- `agent-observability-tracing` for stage-level spans that make deadline misses visible.
- `conversation-state-management` for resuming a turn that was cancelled at the deadline.
