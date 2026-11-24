---
name: stateful-workflow-checkpointing
description: Persists workflow state at step boundaries so long-running or multi-tool tasks can resume after crashes, restarts, or approvals without repeating side effects. Use for durable agents, batch jobs, backfills, approvals, and any workflow longer than a single process.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: agentic
---

# Stateful Workflow Checkpointing

## Overview

A long-running workflow will be interrupted: a process crashes, a pod is evicted, a human takes a day to approve, or a rate limit pauses execution. Without durable state, the work restarts from zero and may repeat side effects.

Checkpointing is the discipline of writing state at safe boundaries, making steps idempotent, and resuming from the last completed step.

## When to use

- Multi-step workflows with external side effects.
- Batch jobs that take longer than a request timeout.
- Workflows that wait for human approval.
- Backfills and data migrations.
- Agents that call slow or unreliable tools.

## Workflow state model

```json
{
  "workflow_id": "wf-2026-11-24-001",
  "workflow_type": "monthly-close",
  "version": 3,
  "status": "running",
  "current_step": "reconcile_bank",
  "steps": {
    "extract_ledger": {"status": "completed", "attempts": 1, "output_ref": "s3://.../ledger.json"},
    "reconcile_bank": {"status": "running", "attempts": 2, "started_at": "2026-11-24T14:02:00Z"},
    "post_entries": {"status": "pending"}
  },
  "context": {"period": "2026-10", "entity": "US"},
  "created_at": "2026-11-24T13:55:00Z",
  "updated_at": "2026-11-24T14:02:00Z",
  "lease": {"owner": "worker-3", "expires_at": "2026-11-24T14:12:00Z"}
}
```

Keep the state small. Store large outputs in object storage and reference them by URI and hash.

## Workflow

### 1. Define step boundaries

A step is a unit that can be retried safely. It should:

- Have one clear input and output.
- Be idempotent or have a compensating action.
- Complete in a bounded time.
- Not span a human approval wait.

Split long steps. A 40-minute step that fails at minute 39 wastes the work.

### 2. Persist state transactionally

Use a database with atomic updates. Checkpoint after a step completes, not before.

```sql
CREATE TABLE workflow_state (
  workflow_id text PRIMARY KEY,
  version int NOT NULL,
  status text NOT NULL,
  state jsonb NOT NULL,
  lease_owner text,
  lease_expires_at timestamptz,
  updated_at timestamptz NOT NULL DEFAULT now()
);

UPDATE workflow_state
SET state = $1, version = version + 1, updated_at = now()
WHERE workflow_id = $2 AND version = $3;
```

The version check prevents two workers from overwriting each other.

### 3. Use idempotency keys

Every external effect gets a key derived from the workflow and step:

```
idempotency_key = f"{workflow_id}:{step_id}:{logical_attempt}"
```

On retry, check whether the effect already happened before calling the tool. If the tool supports an idempotency header, send it.

### 4. Acquire a lease

Only one worker should execute a workflow at a time:

```python
from datetime import datetime, timedelta, timezone

def now():
    return datetime.now(timezone.utc)

def acquire(state, worker_id, ttl_seconds=600):
    lease = state.get("lease")
    if lease and datetime.fromisoformat(lease["expires_at"]) > now():
        return False
    state["lease"] = {
        "owner": worker_id,
        "expires_at": (now() + timedelta(seconds=ttl_seconds)).isoformat(),
    }
    return True
```

Renew the lease during long steps. A stale lease must be recoverable, but recovery must not duplicate an in-flight side effect.

### 5. Resume

On start:

1. Load the state.
2. If status is terminal, return the result.
3. Acquire the lease.
4. Find the first step that is not completed.
5. Re-validate its inputs and preconditions.
6. Execute from there.

Never replay completed steps unless they are explicitly marked for re-run.

### 6. Handle partial side effects

A step can fail after an external effect succeeds but before the checkpoint. On resume:

- Query the external system for the effect.
- If present, mark the step complete with the observed result.
- If absent, retry.
- If ambiguous, escalate.

This is the core of exactly-once behavior: exactly-once delivery is impossible, but exactly-once effect is achievable with idempotency and verification.

### 7. Version and migrate

Workflow definitions change. Store the workflow `version` and keep a migration path:

- New steps default to pending.
- Removed steps are skipped.
- Changed steps require a compatibility check or a new workflow ID.

Do not resume an old state with a new definition that reinterprets the fields.

### 8. Compact and retain

- Keep terminal state for the audit window.
- Archive large outputs with lifecycle rules.
- Delete secrets from state; reference a secret manager.
- Record the final result and error.

## Gotchas

- Checkpointing before a side effect can mark work complete that never happened. Checkpoint after, and verify on resume.
- Checkpointing after a side effect without idempotency can repeat it. Do both.
- A crash between the effect and the checkpoint is the hard case. Design for it.
- Concurrent workers without a lease corrupt state. Use optimistic locking.
- A stale lease can block progress forever. Add expiry and a recovery procedure.
- Large state blobs slow every read. Store references, not payloads.
- Secrets in state leak through backups and logs. Encrypt or reference.
- Non-deterministic steps (time, random, external IDs) make replay inconsistent. Record the values used.
- Schema evolution can break old state. Version the state and migrate.
- A workflow that waits for approval should persist the pending request, not hold a process open.

## Output contract

```json
{
  "workflow_id": "wf-2026-11-24-001",
  "status": "completed",
  "version": 3,
  "steps": [
    {"id": "extract_ledger", "status": "completed", "attempts": 1},
    {"id": "reconcile_bank", "status": "completed", "attempts": 2},
    {"id": "post_entries", "status": "completed", "attempts": 1}
  ],
  "result_ref": "s3://.../result.json",
  "started_at": "2026-11-24T13:55:00Z",
  "finished_at": "2026-11-24T14:31:00Z",
  "resumes": 1,
  "side_effects": [{"step": "post_entries", "idempotency_key": "wf-2026-11-24-001:post_entries:1", "status": "applied"}]
}
```

## Checklist

- [ ] Steps bounded and idempotent.
- [ ] State persisted transactionally after each step.
- [ ] Optimistic version check prevents lost updates.
- [ ] Idempotency key for every external effect.
- [ ] Lease with expiry and recovery.
- [ ] Resume from the first incomplete step.
- [ ] Partial side effects verified before retry.
- [ ] Workflow and state versions recorded.
- [ ] Secrets excluded and retention defined.

## Related skills

- `bounded-multi-tool-orchestration` for the execution loop.
- `human-in-the-loop-escalation` for persisted approval waits.
- `database-schema-migration-generation` for resumable backfills.
