---
name: agent-observability-tracing
description: Instruments agent runs with spans, token accounting, tool logs, and replayable traces. Use for debugging, audits, and production monitoring.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: agentic
---

# Agent Observability Tracing

## Overview

Agent failures are rarely a single stack trace. They emerge from a sequence: a bad retrieval, a tool timeout, a retry, a prompt change, then a wrong final answer. Tracing models each run as a tree of spans so the sequence, timing, cost, and inputs are inspectable after the fact.

Instrument once at the boundaries (model client, tool executor, retrieval, guardrail) and propagate context everywhere. Redact before export, sample deliberately, and keep enough recorded input to replay a run deterministically.

## When to use

- An agent runs in production or handles user-visible work.
- Failures are intermittent or depend on model and tool interactions.
- You need cost attribution by run, user, tenant, or task class.
- Auditors or incident reviewers ask what the agent did and why.
- You want to turn a production failure into an evaluation case.
- Multiple services or subagents participate in one run.

Do not use for a throwaway local script where stderr and a debugger are enough.

## Workflow

1. **Define the span tree and attributes.** Use `agent.run` at the root, `agent.step` per plan step, and leaf spans `gen_ai.chat`, `tool.call`, `retrieval.query`, `guardrail.check`, `cache.lookup`. Span names stay static; variable data goes in attributes so aggregation works.

| Attribute | Example | Where |
| --- | --- | --- |
| `gen_ai.system` | `openai` | model spans |
| `gen_ai.request.model` | `gpt-4.1-mini` | model spans |
| `gen_ai.response.model` | dated version | model spans |
| `gen_ai.usage.input_tokens` | 1820 | model spans |
| `gen_ai.usage.output_tokens` | 210 | model spans |
| `gen_ai.response.finish_reasons` | `["stop"]` | model spans |
| `tool.name` | `search_docs` | tool spans |
| `tool.call.id` | `call_01J...` | tool spans |
| `error.type` | `RateLimitError` | any |
| `agent.run.id` | `run-...` | all spans |

Add domain attributes such as `route.model`, `cache.hit`, `policy.decision`, and `retrieval.doc_count`, but keep cardinality bounded.

2. **Instrument boundaries, not internals.** Wrap the model client, tool executor, retriever, and policy engine in decorators so every call is traced by construction. A sample:

```python
from opentelemetry import trace

tracer = trace.get_tracer("agent.runtime")

def traced_tool(name):
    def wrap(fn):
        def inner(args, ctx):
            with tracer.start_as_current_span("tool.call") as span:
                span.set_attribute("tool.name", name)
                span.set_attribute("agent.run.id", ctx.run_id)
                span.set_attribute("tool.args_hash", ctx.hash_args(args))
                try:
                    result = fn(args, ctx)
                    span.set_attribute("tool.result.status", result.status)
                    return result
                except Exception as exc:
                    span.record_exception(exc)
                    span.set_attribute("error.type", type(exc).__name__)
                    raise
        return inner
    return wrap
```

3. **Redact and store payloads separately.** Hash or truncate prompts and tool outputs in span attributes. Put full payloads in an access-controlled object store keyed by `trace_id` plus span id, with field-level redaction for secrets, tokens, and personal data. Maintain a denylist and a canary test.

4. **Account tokens and cost per span.** Prefer provider usage fields. If unavailable, count with the model tokenizer and mark the value `estimated: true`. Roll up input, output, cached, and reasoning tokens to the run, and price them with the same table used for billing.

5. **Sample on purpose.** Head-sample routine traffic at 5 to 20%. Tail-sample to keep 100% of errors, deadline misses, policy denials, and runs above a cost threshold. Keep a short window of full-fidelity traces for debugging and a longer window of aggregates.

6. **Make runs replayable.** Record model version, temperature, top_p, max_tokens, seed, prompt template version, tool schemas, tool args, and tool results (or stable references). Build a replay command that feeds recorded tool outputs back through the agent to isolate whether a change in the model or the tools caused the difference.

7. **Dashboard and alert.** Track error rate, p95 latency, cost per successful task, tool failure rate by tool, guardrail denial rate, retry rate, and loop detection. Link alerts to a trace query, not just a metric name.

## Validation

- **Completeness:** for 20 runs, compare the tool executor counter with span counts; they must match.
- **Redaction canary:** inject a fake secret and fake email, export, and assert neither appears in any backend field.
- **Token reconciliation:** sum span token usage and compare with provider billing for one day; difference under 2% or explain it.
- **Failure retention:** force an error and a timeout, then confirm both traces were exported despite sampling.
- **Replay:** replay a recorded run and confirm the same tool sequence and final status with recorded outputs.
- **Context propagation:** run through an async queue and assert child spans share the root `trace_id`.

Any failed check blocks production enablement of the instrumentation change.

## Gotchas

- High-cardinality attributes such as full prompts or user IDs explode index cost. Hash or bucket them.
- Raw prompts and tool output leak personal data and secrets. Redact before export, not in the dashboard.
- Async tasks and queues drop the parent context. Pass the trace context explicitly and test it.
- Head sampling discards the rare failures. Use tail sampling for errors and slow runs.
- Character-count token estimates drift from billing. Use usage fields and label estimates.
- Logging tool output verbatim can persist injected instructions. Store it as untrusted data.
- Missing model version or prompt version makes replay impossible. Record both per run.
- Negative span durations signal clock skew. Use monotonic clocks for durations and wall time for correlation.
- An exporter failure on the request path adds latency. Use a batch exporter with a drop policy.
- Storing payloads forever violates retention. Set per-field TTLs and deletion jobs.
- Span names built from arguments break grouping. Use static names plus attributes.
- Tracing every internal function creates noise and cost. Instrument boundaries only.

## Output contract

```json
{
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "run_id": "run-2026-11-26-0117",
  "status": "error",
  "span_count": 14,
  "duration_ms": 9120,
  "usage": {"input_tokens": 8420, "output_tokens": 1130, "estimated": false},
  "cost_usd": 0.041,
  "error": {"type": "ToolTimeout", "span": "tool.call", "tool": "search_docs"},
  "sampled": true,
  "payload_ref": "s3://agent-traces/2026-11-26/4bf9.../",
  "replay": {"available": true, "command": "agent replay --trace 4bf9..."}
}
```

## Checklist

- [ ] Span tree defined with static span names.
- [ ] GenAI and tool attributes set at boundaries.
- [ ] Trace context propagated across async and subagent calls.
- [ ] Redaction applied before export, with a canary test.
- [ ] Full payloads stored separately with access control.
- [ ] Token usage from provider fields, estimates labeled.
- [ ] Cost computed with the billing price table.
- [ ] Tail sampling retains errors, slow runs, and denials.
- [ ] Model, prompt, and tool versions recorded per run.
- [ ] Replay path tested on a recorded failure.
- [ ] Dashboards cover error, latency, cost, and tool health.
- [ ] Retention and deletion policies configured.

## Related skills

- `distributed-trace-analysis` for reading a trace tree and attributing latency to a service or span.
- `cost-aware-model-routing` for price data and quality signals that give traces their cost meaning.
- `guardrail-policy-enforcement` for emitting policy decisions as first-class trace events.
- `stateful-workflow-checkpointing` for persisting run state that complements replayable traces.
