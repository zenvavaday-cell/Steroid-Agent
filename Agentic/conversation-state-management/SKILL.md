---
name: conversation-state-management
description: Persists and restores multi-turn state with schema versioning, privacy rules, and conflict handling. Use for assistants that span sessions and devices.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: agentic
---

# Conversation State Management

## Overview

A conversation that survives a restart, a second device, or a week of inactivity needs explicit state: what was said, what was decided, what is still pending, and what must be forgotten. Treat that state as a versioned data product, not a serialized message list.

The discipline separates durable facts and commitments from raw transcript, assigns a schema version, applies per-field retention and privacy rules, and resolves concurrent writes without losing turns or double-executing side effects.

## When to use

- The assistant serves multi-turn sessions that outlive a process.
- Users return across days or switch between web, mobile, and voice.
- The agent tracks commitments, preferences, or pending approvals.
- Conversations contain personal or regulated data.
- A run can be interrupted mid-tool and must resume safely.
- Multiple workers or regions may write the same session.

Do not use when the interaction is stateless by design, such as a single-shot translation endpoint.

## Workflow

1. **Split state by lifetime and sensitivity.** Keep `working` state (current plan, scratch results), `conversation` state (turn log, summary), and `profile` state (durable preferences, consent). Each has its own TTL, encryption, and access rules. Large tool artifacts live in object storage; state stores a reference and checksum.

2. **Define a versioned schema.** Example:

```json
{
  "schema_version": 3,
  "session_id": "ses_01J8Z3",
  "user_id": "u_1042",
  "tenant_id": "t_17",
  "revision": 41,
  "created_at": "2026-11-20T09:00:00Z",
  "updated_at": "2026-11-26T11:42:00Z",
  "turns": [
    {"turn_id": "t_41", "seq": 41, "role": "user", "content_ref": "obj://...", "ts": "..."},
    {"turn_id": "t_40", "seq": 40, "role": "assistant", "content_ref": "obj://...", "ts": "..."}
  ],
  "summary": {"text": "...", "covers_through_seq": 38, "model": "small-v2"},
  "facts": [
    {"key": "billing_currency", "value": "EUR", "source_turn": "t_12", "confidence": 0.98}
  ],
  "commitments": [
    {"id": "c_7", "text": "send revised quote by Friday", "status": "open", "due": "2026-11-27"}
  ],
  "pending_actions": [
    {"tool": "email.send", "args_hash": "sha256:...", "idempotency_key": "quote-u1042-v3", "status": "unknown"}
  ],
  "consent": {"analytics": false, "model_training": false},
  "ttl_days": {"working": 1, "conversation": 90, "profile": 365}
}
```

3. **Choose storage per tier.** Redis or DynamoDB with TTL for working state, a transactional database for conversation and profile, and object storage for payloads. Key by `tenant_id/user_id/session_id`, encrypt at rest with per-tenant keys, and never trust a session id without checking it belongs to the subject.

4. **Write with optimistic concurrency.** Read the current `revision`, write with `UPDATE ... WHERE revision = :expected`, and retry on mismatch. Append turns to an immutable log with a server-assigned `seq`. Merge facts by key with source timestamp and explicit `conflict` status when values disagree. Never last-write-wins a turn.

5. **Restore within a token budget.** Build context in priority order: system and safety constraints, open commitments, relevant facts, summary, recent turns, then retrieved older turns. Trim from the lowest priority and keep constraints intact. Recompute the summary asynchronously when `covers_through_seq` falls behind.

6. **Handle interruption and resume.** Mark a turn `processing` with a lease before calling tools. On resume, inspect `pending_actions`; query idempotency status before retrying, and reconcile the result into the turn. Expire stale leases so another worker can take over without duplicating side effects.

7. **Enforce privacy and deletion.** Classify fields, minimize collection, redact traces, and apply per-field TTL. Support export and deletion across primary store, cache, object payloads, summaries, and derived embeddings. Record deletion evidence without retaining the deleted content.

## Validation

- **Round trip:** write a session, restart the process, restore, and compare all fields except timestamps.
- **Migration:** run fixtures from each prior schema version through forward migration and assert invariants; keep a tested rollback for one version.
- **Concurrency:** two writers append turns at the same revision; exactly one succeeds, the other retries, and no turn is lost.
- **Deletion:** issue a subject deletion and assert absence in primary, cache, object store, summary, and embeddings.
- **Token budget:** load a 200-turn session and assert the assembled context is under budget with constraints present.
- **Resume:** kill a run after a side effect but before commit; resume and assert the effect is not repeated.
- **Encryption:** scan stored bytes for a plaintext canary and find none.

Failures block release of the state or storage change.

## Gotchas

- Storing the full transcript forever raises cost and breach exposure. Summarize and expire.
- Summaries drop numbers, names, and commitments. Keep structured facts with provenance.
- Last-write-wins merge silently loses turns from a second device. Use an append-only log.
- Changing the schema without a version breaks old clients and old rows. Migrate forward only.
- A session id that is guessable or not bound to the user enables IDOR. Authorize every read and write.
- In-memory state treated as durable disappears on deploy. Persist before acknowledging.
- Resuming a pending side effect can double-charge. Check the idempotency ledger first.
- Deleting the user row while summaries and embeddings remain violates deletion. Track derived data.
- Trimming context from the front removes safety instructions. Prioritize by role, not position.
- Client clocks and retries can reorder turns. Assign sequence numbers on the server.
- Consent captured once is not consent forever. Store purpose, timestamp, and revocation.
- PII copied into logs and traces escapes state retention. Redact at the boundary.

## Output contract

```json
{
  "session_id": "ses_01J8Z3",
  "schema_version": 3,
  "revision": 42,
  "restored": true,
  "turn_count": 41,
  "context_tokens": 5840,
  "context_budget": 8000,
  "summary_covers_through_seq": 38,
  "open_commitments": 1,
  "pending_actions": [{"idempotency_key": "quote-u1042-v3", "status": "applied"}],
  "conflicts": [],
  "retention": {"working_until": "2026-11-27", "conversation_until": "2027-02-24"}
}
```

## Checklist

- [ ] State split into working, conversation, and profile tiers.
- [ ] Schema versioned with tested forward migrations.
- [ ] Storage chosen per tier with encryption at rest.
- [ ] Session access checked against the subject on every read.
- [ ] Optimistic concurrency with server-assigned sequence.
- [ ] Turns append-only; facts merged with provenance.
- [ ] Context assembled within a token budget by priority.
- [ ] Interrupted runs resume without duplicate side effects.
- [ ] Per-field TTL and consent recorded.
- [ ] Export and deletion cover derived data and caches.
- [ ] Traces and logs redact state payloads.
- [ ] Restore tested after a real process restart.

## Related skills

- `long-context-memory-management` for summarizing and retrieving older turns under a token budget.
- `stateful-workflow-checkpointing` for resuming interrupted tool workflows without duplicate effects.
- `guardrail-policy-enforcement` for authorizing session access and sensitive state changes.
- `gdpr-data-subject-request` for the deletion and export workflow this schema must support.
