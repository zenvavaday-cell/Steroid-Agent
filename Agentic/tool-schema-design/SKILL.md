---
name: tool-schema-design
description: Designs tool interfaces with clear names, typed parameters, examples, error contracts, and idempotency. Use when exposing APIs or functions to an agent.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: agentic
---

# Tool Schema Design

## Overview

A tool schema is the only contract between the model and your code. The model cannot read your implementation, ask a colleague, or infer that `date` means a Unix timestamp. It sees a name, a description, a JSON Schema, and whatever examples you provide.

Design for a capable reader who has never seen the system and will guess when the schema is silent. Every guess is a potential production incident.

## When to use

- Exposing a new API, function, or internal service to an agent.
- Tool calls fail validation, use wrong argument types, or select the wrong tool.
- Two tools overlap and the model alternates between them unpredictably.
- Adding a write, delete, payment, or deployment operation.
- Reviewing an MCP server or a function-calling definition before release.
- Standardizing a tool catalog across teams.

Do not use for internal library APIs that only humans and compilers consume; their ergonomics follow different rules.

## Workflow

### 1. Name the operation and its scope

Use `verb_noun` in snake_case: `search_orders`, `cancel_subscription`, `create_invoice`. Keep the name under 64 characters. State the scope in the description: "one order", "all open orders", "a single page of results".

Avoid vague verbs (`process`, `handle`, `manage`) and overloaded nouns (`data`, `item`, `record`). If a name needs a comment to explain it, rename it.

### 2. Shape the parameter object

Prefer a flat object with typed properties. Nesting is allowed one level deep for a genuine grouping, not for aesthetics.

```json
{
  "name": "search_orders",
  "description": "Find orders by exact customer email or order ID. Read-only. Returns at most 20 matches.",
  "parameters": {
    "type": "object",
    "properties": {
      "customer_email": {"type": "string", "format": "email", "description": "Exact email used at checkout."},
      "order_id": {"type": "string", "pattern": "^ord_[0-9a-f]{12}$", "description": "Order ID including the ord_ prefix."},
      "status": {"type": "string", "enum": ["open", "shipped", "delivered", "cancelled", "any"], "default": "any"},
      "created_after": {"type": "string", "format": "date", "description": "Inclusive lower bound, ISO 8601 date."},
      "limit": {"type": "integer", "minimum": 1, "maximum": 20, "default": 10}
    },
    "oneOf": [{"required": ["customer_email"]}, {"required": ["order_id"]}],
    "additionalProperties": false
  }
}
```

Rules for properties:

| Rule | Reason |
| --- | --- |
| Every property has `type` and `description` | The description is prompt text the model reads |
| Closed sets use `enum`, with `any` or `other` where needed | Prevents invented statuses |
| IDs carry prefix patterns | Distinguishes `ord_...` from `cus_...` |
| Units appear in the name and description | `timeout_ms`, not `timeout` |
| Bounds use `minimum`, `maximum`, `maxLength` | Server and model agree on limits |
| `required` lists only what is truly required | Optional fields with defaults reduce retries |
| `additionalProperties: false` | Stops silent parameter invention |
| No `any`, no bare `object`, no untyped arrays | The model otherwise guesses the shape |

### 3. Write descriptions as usage instructions

Each tool description answers: what it does, when to use it, when not to use it, whether it is read-only or mutating, and what it returns. Each parameter description answers: expected format, units, default, and one concrete example value.

```text
search_orders: Find orders by exact customer email or order ID. Read-only.
Use when the user supplies an order identifier or the email used at checkout.
Do not use for fuzzy name searches; call search_customers first.
Returns up to 20 orders with id, status, total_cents, and created_at.
```

### 4. Include examples, not just schemas

Add one canonical call and one edge case per tool. Examples teach argument style faster than prose.

```json
{
  "examples": [
    {"customer_email": "ada@example.com", "status": "shipped", "limit": 5},
    {"order_id": "ord_4f9c2a7b1e30", "status": "any"}
  ]
}
```

Keep examples minimal and valid. An invalid example in the prompt teaches invalid calls.

### 5. Define the success and error envelope

Return a stable object. Never return a bare string or an array whose shape changes with the result count.

```json
{
  "ok": false,
  "error": {
    "code": "INVALID_ARGUMENT",
    "message": "created_after must be YYYY-MM-DD",
    "retryable": false,
    "field": "created_after",
    "remediation": "Pass an ISO 8601 date such as 2026-11-01."
  }
}
```

| Code | Retryable | Meaning |
| --- | --- | --- |
| `INVALID_ARGUMENT` | No | Fix the call; do not retry unchanged |
| `NOT_FOUND` | No | The entity does not exist; verify the ID |
| `PERMISSION_DENIED` | No | The caller lacks scope; escalate |
| `RATE_LIMITED` | Yes | Back off with jitter |
| `CONFLICT` | Once | Re-read state, then retry |
| `TIMEOUT` | Conditional | Check whether a side effect landed first |
| `UPSTREAM_UNAVAILABLE` | Yes | Retry with a cap |
| `INTERNAL` | No | Report with a trace ID |

### 6. Declare side effects and idempotency

Write tools require an `idempotency_key` parameter, derived from the logical action rather than the attempt number. Mark risk explicitly in the description and, if your runtime supports it, with annotations such as `readOnlyHint` and `destructiveHint`.

```json
{
  "name": "cancel_subscription",
  "description": "Cancel one subscription. Mutating and irreversible after the current billing period. Requires an idempotency key.",
  "parameters": {
    "type": "object",
    "properties": {
      "subscription_id": {"type": "string", "pattern": "^sub_[0-9a-f]{12}$"},
      "reason": {"type": "string", "enum": ["customer_request", "payment_failure", "fraud", "other"]},
      "idempotency_key": {"type": "string", "minLength": 8, "description": "Stable key such as cancel-sub-123-2026-11."}
    },
    "required": ["subscription_id", "reason", "idempotency_key"],
    "additionalProperties": false
  }
}
```

For irreversible actions, add a `confirm: true` field or require a separate approval step. Do not hide a destructive operation behind a generic `update` tool.

### 7. Version, test, and measure

- Add a schema version and keep old tool names callable during migration.
- Validate every schema at build time.
- Run a routing set: prompts with a known correct tool and expected arguments.
- Test malformed, missing, and adversarial arguments against the real validator, not just the happy path.
- Measure selection accuracy, argument validity, retry rate, and error recovery rate before release.

## Validation

Run these gates for every tool before exposing it.

```bash
python3 - <<'PY'
import json
from pathlib import Path
from jsonschema import Draft202012Validator

for path in Path("tools").glob("*.schema.json"):
    schema = json.loads(path.read_text())
    Draft202012Validator.check_schema(schema)
    params = schema["parameters"]
    assert params.get("additionalProperties") is False, path
    for name, prop in params.get("properties", {}).items():
        assert prop.get("description"), (path, name)
        assert prop.get("type") or "oneOf" in prop or "$ref" in prop, (path, name)
    print("OK", path)
PY
```

Pass criteria:

- [ ] Every schema passes meta-schema validation.
- [ ] No parameter is untyped or undocumented.
- [ ] Read tools never require an idempotency key; write tools always do.
- [ ] Routing accuracy is at least 90% on a 30-case set (example threshold; calibrate to risk).
- [ ] Argument validity after one repair attempt is at least 95%.
- [ ] Every error code has a documented retryable value.
- [ ] A destructive tool cannot execute twice with the same key.
- [ ] Output truncation includes an explicit `truncated: true` marker.

Fail the release if a write tool can be called without an idempotency key, or if an error path returns success status.

## Gotchas

- `additionalProperties: true` lets the model invent fields that your handler silently ignores. Close the object.
- One tool that does three things causes selection errors. Split by intent, not by endpoint.
- Optional parameters without defaults produce different calls for the same request. Set defaults explicitly.
- A missing `other` enum value forces the model to pick an arbitrary option or hallucinate. Include an escape hatch.
- Free-text ID fields cause UUID, email, and prefixed-ID confusion. Add `pattern` and an example.
- Returning errors inside a 200 response teaches the agent that failures are successes. Use the error envelope and `ok: false`.
- Truncating results without a marker makes the model answer from a partial page. Always emit `truncated` and a cursor.
- Deeply nested objects raise argument validation failures. Flatten to one level unless grouping is essential.
- Renaming or retyping a parameter without versioning breaks prompts and cached plans. Version the tool.
- Putting behavioral rules in a tool description that contradict the system prompt creates conflicting instructions. Keep policy in one place.
- A destructive tool named `update` will be called casually. Name the effect and require confirmation.
- Milliseconds versus seconds is a recurring bug. Put the unit in the parameter name.

## Output contract

```json
{
  "tool": "search_orders",
  "schema_version": "1.2.0",
  "side_effect": false,
  "parameters": {"type": "object", "properties": {}, "required": [], "additionalProperties": false},
  "returns": {"type": "object", "properties": {"ok": {"type": "boolean"}, "orders": {"type": "array"}}},
  "error_codes": ["INVALID_ARGUMENT", "NOT_FOUND", "RATE_LIMITED"],
  "examples": [{"args": {"order_id": "ord_4f9c2a7b1e30"}, "result": "ok"}],
  "idempotency": {"required": false, "key_source": null},
  "eval": {"routing_cases": 30, "selection_accuracy": 0.93, "argument_validity": 0.97}
}
```

## Checklist

- [ ] Tool name is `verb_noun` and unambiguous.
- [ ] Description states scope, when to use, when not to use, and side effects.
- [ ] Every property has a type, description, and bounds where relevant.
- [ ] Enums cover the real domain plus an escape value where needed.
- [ ] Required list is minimal and defaults are explicit.
- [ ] `additionalProperties` is false.
- [ ] At least one valid example call is included.
- [ ] Success and error envelopes are stable and documented.
- [ ] Write tools require an idempotency key.
- [ ] Irreversible actions require confirmation or approval.
- [ ] Schema passes meta-validation in CI.
- [ ] Routing and argument accuracy measured before release.

## Related skills

- `bounded-multi-tool-orchestration` for executing validated tool calls under budgets and retries.
- `schema-enforced-json-extraction` for validating model-produced arguments against the schema.
- `guardrail-policy-enforcement` for allow, deny, and approval checks before a tool runs.
- `agent-evaluation-harness` for measuring tool selection and argument accuracy over time.
