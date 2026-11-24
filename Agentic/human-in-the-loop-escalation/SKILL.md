---
name: human-in-the-loop-escalation
description: Pauses an agent at risk boundaries, packages the decision with evidence, alternatives, blast radius, and rollback, and resumes safely after approval, rejection, modification, or timeout. Use for irreversible actions, high-value transactions, sensitive data, policy ambiguity, low confidence, or any workflow requiring sign-off.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: agentic
---

# Human-in-the-Loop Escalation

## Overview

Autonomy should stop where the cost of a wrong action exceeds the cost of asking. Escalation is not a failure; it is a control. The human needs enough context to decide in seconds, and the system needs a safe way to resume without repeating side effects.

Default to deny on timeout. An unanswered approval is not consent.

## When to use

- Irreversible actions: delete, deploy, pay, send, publish, revoke access.
- High-value or high-impact transactions.
- Low-confidence or conflicting evidence.
- Ambiguous policy with no clear precedent.
- Sensitive data: PII, health, legal, financial.
- Repeated tool failures or anomalous behavior.
- Requests that conflict with instructions or safety rules.

Do not escalate everything. Approval fatigue produces rubber-stamping, which is worse than no control.

## Escalation triggers

| Trigger | Example | Default |
| --- | --- | --- |
| Irreversible | Drop table, delete account | Require approval |
| Financial | Payment above threshold | Require approval |
| External communication | Email to customers, public post | Require approval |
| Access | Grant admin, rotate keys | Require approval |
| Data export | PII out of region | Require approval |
| Low confidence | Below calibrated threshold | Route to review |
| Policy ambiguity | Two rules conflict | Escalate |
| Repeated failure | 3 failed attempts | Escalate |
| Anomaly | Tool returns unexpected data | Pause and escalate |

## Approval packet

```json
{
  "request_id": "APR-2026-0042",
  "created_at": "2026-11-24T14:02:00Z",
  "requested_by": "agent:reporting",
  "action": {
    "type": "email.send",
    "summary": "Send the Q3 revenue report to 42 external recipients",
    "target": "customer-finance-list",
    "parameters_hash": "sha256:..."
  },
  "rationale": "Scheduled quarterly report; data validated against the ledger.",
  "evidence": [
    {"source": "ledger close 2026-11-20", "check": "revenue ties to GL"},
    {"source": "recipient list v7", "check": "42 addresses, 0 suppressed"}
  ],
  "alternatives": [
    {"option": "send to internal review first", "tradeoff": "delays by 1 day"},
    {"option": "send to 5 pilot recipients", "tradeoff": "partial delivery"}
  ],
  "blast_radius": "42 external recipients; report contains no PII.",
  "rollback": "Cannot unsend; correction email prepared if needed.",
  "risk": "medium",
  "expires_at": "2026-11-24T18:00:00Z",
  "approver_role": "finance-manager"
}
```

The packet must be specific enough that the approver does not need to redo the analysis.

## State machine

```
proposed -> pending -> approved -> executing -> executed
                    -> rejected
                    -> expired
                    -> modified -> pending
                    -> failed
```

Rules:

- `pending` does not authorize execution.
- `approved` is bound to the `parameters_hash`. Any change returns to `pending`.
- `expired` is a denial. The agent may re-request with new information.
- `modified` creates a new version; the approver sees the diff.
- `executing` is idempotent; a retry checks the effect status first.

## Workflow

### 1. Detect the boundary

Before executing a tool, check the action against the trigger table. If any trigger matches, stop and build the packet.

### 2. Assemble evidence

Include the inputs, the checks performed, the outputs, and the uncertainties. Link to artifacts rather than pasting huge documents.

### 3. Present alternatives

A binary approve/reject pushes the human into a corner. Offer at least one safer alternative: pilot, partial, delay, or manual review.

### 4. Route to the right approver

Match the action to a role with the authority and context. Do not send a finance approval to a general queue.

### 5. Wait, with a deadline

Set an expiry. On expiry, deny and notify. Do not auto-approve because the deadline passed.

### 6. Resume safely

On approval:

- Re-validate the preconditions (the world may have changed).
- Verify the parameters hash matches the approved action.
- Execute with an idempotency key.
- Record the result.

On rejection:

- Stop.
- Record the reason.
- Return a useful message to the user.

### 7. Audit

Log the request, evidence, decision, approver, timestamp, and execution result. Retain according to policy.

## Anti-rubber-stamp rules

- Show the actual diff or payload, not a summary only.
- Require an explicit verb ("approve", "reject"), not a click-through default.
- Separate the requester from the approver for high-risk actions.
- Do not batch high-risk approvals into one button.
- Surface disagreements and missing evidence.
- Rotate reviewers and monitor approval times; a two-second approval is a signal.
- Bind approval to the exact parameters.

## Gotchas

- Approval fatigue is the main failure mode. Escalate by risk, not by anxiety.
- A stale approval is dangerous. Re-validate before execution.
- Scope creep: approving "send report" does not approve "send to a different list."
- A change after approval invalidates it. Hash the parameters.
- Impersonation: verify the approver's identity and channel.
- A timeout is not consent. Default deny.
- A rejection without a reason gives the agent nothing to improve.
- Approving an action does not approve its side effects on other systems.
- Logs can leak sensitive data. Redact while preserving the decision record.
- An agent can learn to phrase requests to get approval. Review the pattern, not only the individual request.

## Output contract

```json
{
  "request_id": "APR-2026-0042",
  "status": "approved",
  "decision": {"by": "user:jdoe", "role": "finance-manager", "at": "2026-11-24T14:31:00Z", "verb": "approve"},
  "parameters_hash": "sha256:...",
  "execution": {"status": "executed", "idempotency_key": "q3-report-2026", "result": "sent 42"},
  "audit": "audit/APR-2026-0042.json"
}
```

## Checklist

- [ ] Trigger detected before the action.
- [ ] Packet includes action, evidence, alternatives, blast radius, rollback.
- [ ] Approver role has authority.
- [ ] Expiry set; timeout denies.
- [ ] Approval bound to parameters hash.
- [ ] Preconditions re-validated before execution.
- [ ] Idempotency key used.
- [ ] Decision and result audited.
- [ ] Escalation rate and approval time monitored.

## Related skills

- `bounded-multi-tool-orchestration` for budgeted execution.
- `confidence-threshold-output-gating` for low-confidence routing.
- `stateful-workflow-checkpointing` for resuming after approval.
