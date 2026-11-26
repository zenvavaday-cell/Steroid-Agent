---
name: guardrail-policy-enforcement
description: Encodes allow, deny, and require-approval policies and enforces them before actions execute. Use for safety, compliance, and tool-access control.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: agentic
---

# Guardrail Policy Enforcement

## Overview

Prompt instructions are not a security boundary. An agent can be persuaded, injected, or simply wrong, so every consequential action is checked against an explicit policy in code immediately before it executes.

Policy defines who (user, agent, tenant) may do what (tool, operation) to which resource (record, account, recipient, amount), under what conditions. The default is deny, evaluation is deterministic, errors fail closed, and every decision is auditable.

## When to use

- The agent can write, delete, send, pay, deploy, or change permissions.
- Data is regulated, confidential, or tenant-scoped.
- Different users or plans have different tool entitlements.
- Actions above a threshold need human approval.
- An auditor asks for evidence of access control.
- Subagents or delegated tokens can act on the user's behalf.

Do not use as a substitute for authentication and authorization at the API or database layer; enforce there too.

## Workflow

1. **Inventory actions and resources.** For each tool, record operation class (read, write, delete, send, pay, deploy), resource type and scope, data classification, and blast radius. A tool that takes free-form SQL or a URL path needs argument-level controls, not just a tool-level allow.

2. **Define the policy model.** Each rule carries `effect` (`allow`, `deny`, `require_approval`), `priority`, `conditions`, and `obligations`. Deny always wins at equal or higher priority. Example:

```yaml
policy_version: "2026-11-01"
default: deny
rules:
  - id: support-read-tickets
    effect: allow
    subject: {role: support_agent}
    action: {tool: tickets.read}
    resource: {tenant: "$subject.tenant"}
    conditions: ["resource.assignee == subject.id"]
  - id: refunds-small
    effect: allow
    subject: {role: support_agent}
    action: {tool: payments.refund}
    conditions: ["args.amount_usd <= 50", "args.currency == 'USD'"]
    obligations: ["log", "notify_finance"]
  - id: refunds-large
    effect: require_approval
    subject: {role: support_agent}
    action: {tool: payments.refund}
    conditions: ["args.amount_usd > 50"]
    approval: {role: finance_manager, ttl_minutes: 30, quorum: 1}
  - id: no-cross-tenant
    effect: deny
    priority: 100
    subject: {role: "*"}
    action: {tool: "*"}
    conditions: ["resource.tenant != subject.tenant"]
```

3. **Canonicalize inputs before evaluation.** Normalize Unicode (NFKC), case-fold enum values, resolve paths to absolute form, parse amounts as decimals, and validate argument types against the tool schema. Policy on unnormalized strings invites bypasses.

4. **Enforce at one chokepoint.** Every tool invocation goes through `authorize(subject, action, resource, args)` before dispatch. The wrapper is the only code allowed to call the tool. Instrument it and assert in CI that no direct call sites exist.

```python
def authorize(subject, tool, args, resource):
    decision = policy.evaluate(subject=subject, action=tool, args=args, resource=resource)
    if decision.error:
        return Deny("policy_unavailable")          # fail closed
    if decision.effect == "deny":
        return Deny(decision.reason_code)
    if decision.effect == "require_approval":
        approval = approvals.request(decision, args_hash=sha256(canonical(args)))
        return Wait(approval.id, expires_at=approval.expires_at)
    return Allow(obligations=decision.obligations)
```

5. **Bind approvals to the exact action.** The approval request includes a hash of canonical tool name, args, resource, and subject. Any change to args invalidates the approval. Approvals expire to deny, require the approver role, and record the approver identity. Never let the agent approve its own request.

6. **Audit every decision.** Append an immutable record with timestamp, subject, agent, tool, canonical args hash (not raw secrets), resource, policy version, matched rule, effect, obligations, approval id, and outcome. Alert on denial spikes, approval spikes, and policy engine errors.

7. **Test bypasses and fail-closed behavior.** Run prompt-injection attempts, encoded payloads, case variants, path traversal, cross-tenant IDs, and direct tool calls. Kill the policy engine and assert denial. Put the policy test table in CI and require review for rule changes.

## Validation

| Gate | Test | Pass |
| --- | --- | --- |
| Coverage | Static scan for direct tool calls | Zero call sites outside the chokepoint |
| Default deny | Invoke an unknown tool | Denied with `unknown_action` |
| Fail closed | Timeout or crash the policy engine | Denied, request fails safely |
| Approval binding | Change args after approval | Approval invalid, action blocked |
| Tenant isolation | Subject A targets tenant B resource | Denied by priority rule |
| Audit integrity | Attempt to update an audit row | Update rejected, append-only store |
| Bypass suite | Injection and encoding corpus | All blocked or escalated as designed |
| Policy tests | Table-driven allow, deny, approval cases | 100% pass in CI |

A deployment is blocked if any gate fails. Canary the policy version at low traffic with shadow evaluation before enforcing.

## Gotchas

- Enforcing with prompt text only is bypassable by injection or paraphrasing. Enforce in code.
- Checking the tool name and not the arguments allows a safe tool to perform an unsafe action. Validate args.
- Time-of-check to time-of-use: args can change between approval and execution. Bind approval to a hash.
- A policy engine error that defaults to allow turns an outage into a breach. Fail closed.
- Unicode, case, and path normalization gaps create bypasses. Canonicalize before matching.
- Trusting a client-supplied tenant or role lets a user escalate. Resolve identity server-side.
- Subagents with their own credentials can escape the parent chokepoint. Enforce at the credential boundary too.
- Raw args in audit logs leak secrets and personal data. Store a hash plus redacted fields.
- Approval fatigue leads to rubber-stamping. Batch low-risk requests and reserve approvals for high impact.
- Policy versions that drift between staging and production produce false confidence. Version and deploy atomically.
- Rate limits and spend caps are guardrails. Missing them allows many small allowed actions to cause harm.
- Async and scheduled actions can bypass request-scoped checks. Re-evaluate at execution time.

## Output contract

```json
{
  "decision_id": "pol-2026-11-26-8812",
  "effect": "require_approval",
  "subject": {"user_id": "u_1042", "role": "support_agent", "tenant": "t_17"},
  "action": {"tool": "payments.refund", "args_hash": "sha256:9f2c..."},
  "resource": {"type": "payment", "id": "pay_5521", "tenant": "t_17"},
  "policy_version": "2026-11-01",
  "matched_rule": "refunds-large",
  "reason_code": "amount_above_auto_limit",
  "obligations": ["log", "notify_finance"],
  "approval": {"id": "apr_771", "role": "finance_manager", "expires_at": "2026-11-26T12:30:00Z"},
  "audit_ref": "audit/2026-11-26/pol-8812"
}
```

## Checklist

- [ ] Tool and resource inventory complete, including argument-level risks.
- [ ] Policy schema has allow, deny, require_approval, and obligations.
- [ ] Default deny and deny-overrides precedence implemented.
- [ ] Inputs canonicalized before evaluation.
- [ ] Single chokepoint wraps every tool call.
- [ ] CI proves no direct tool call sites exist.
- [ ] Approvals bound to an args hash and expire to deny.
- [ ] Fail-closed behavior tested by killing the engine.
- [ ] Audit records append-only and redacted.
- [ ] Bypass suite covers injection, encoding, and cross-tenant cases.
- [ ] Alerts on denial, approval, and engine error rates.
- [ ] Policy changes reviewed, versioned, and canaried.

## Related skills

- `prompt-injection-defense` for treating retrieved content as untrusted before it reaches an action.
- `human-in-the-loop-escalation` for the approval workflow behind require-approval decisions.
- `agent-observability-tracing` for recording policy decisions as spans and audit events.
- `tool-schema-design` for typed arguments that make policy conditions reliable.
