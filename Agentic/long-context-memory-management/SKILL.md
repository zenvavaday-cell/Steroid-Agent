---
name: long-context-memory-management
description: Summarizes, indexes, and evicts conversation state without losing critical facts or commitments. Use for long sessions and persistent assistants.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: agentic
---

# Long-Context Memory Management

## Overview

A long session accumulates decisions, corrections, identifiers, deadlines, and preferences. The context window eventually fills, and quality degrades before the hard limit: models attend less reliably to material buried in the middle, and stale facts compete with current ones.

Memory management is the discipline of deciding what stays verbatim, what gets summarized, what gets indexed for retrieval, and what must be deleted. The failure that matters most is losing a commitment the user is entitled to rely on.

## When to use

- A conversation or agent run exceeds roughly 30 turns or 50% of the context window.
- A persistent assistant must remember users across sessions or devices.
- A coding or research agent runs long enough to need checkpointed context.
- Support handoffs require a reliable summary of prior work.
- Recurring meetings or projects accumulate decisions over weeks.
- A user asks the assistant to forget data or correct a stored fact.

Do not use for single-turn tasks or short sessions where the full transcript fits comfortably and no persistence is required.

## Workflow

### 1. Define memory tiers and a token budget

| Tier | Contents | Example budget (128k window) | Lifetime |
| --- | --- | --- | --- |
| System and tools | Policy, tool schemas | 12k | Session |
| Working | Recent turns verbatim | 48k | Until compacted |
| Episodic | Summaries of past segments with source turn IDs | 20k | Session or longer |
| Semantic | Durable facts and preferences | 16k | Until superseded or deleted |
| Commitments | Promises, deadlines, obligations, IDs | 4k, pinned | Until fulfilled plus retention |
| Retrieved | Memory or documents pulled for this turn | 12k | One turn |
| Response reserve | Output and reasoning | 8k | Per call |
| Safety reserve | Growth between compactions | 8k | Per call |

Trigger compaction at 70 to 80% of the working tier, not at 99% of the window. Leave room for a tool result or a long user message that arrives mid-turn.

### 2. Write memories at turn boundaries

Do not store the raw transcript as the only memory. Extract structured records after each meaningful turn.

```json
{
  "id": "mem-2026-11-26-0184",
  "type": "commitment",
  "text": "Deliver the migration plan by 2026-12-05.",
  "subject": "user:ada",
  "source_turn": "t-184",
  "created_at": "2026-11-26T14:02:00Z",
  "confidence": 1.0,
  "status": "active",
  "supersedes": null,
  "expires_at": "2026-12-06T00:00:00Z",
  "sensitivity": "internal"
}
```

Write rules:

- Commitments, decisions, corrections, constraints, identifiers, and deadlines are mandatory.
- Preferences are stored with a scope (global, project, channel) and a source.
- Inferred facts are marked `inferred` with lower confidence, never mixed with stated facts.
- Deduplicate by normalized text and subject before insert.
- Store source turn IDs so every memory can be audited or revoked.
- Never store secrets, credentials, or full payment data; store a reference instead.

### 3. Compact incrementally from source

Summarize older turns into a rolling episodic summary with fixed sections. Summarize source turns, or a hierarchy of segment summaries that retain source spans. Repeatedly summarizing the previous summary drifts and loses numbers.

```text
Update the running summary for this session.
Preserve verbatim: names, IDs, numbers, dates, deadlines, decisions, constraints, user corrections.
Sections: Goal; Decisions; Open questions; Constraints; Artifacts; Commitments.
Rules:
- Do not infer facts that were not stated.
- Mark uncertain items as uncertain with the source turn.
- Keep every active commitment with its deadline and owner.
- Keep user corrections next to the fact they replace.
- Output at most 400 words.
```

After summarizing, run a fact checklist against the source: names, amounts, dates, IDs, and active commitments. If a required item is missing, fix the summary before evicting the turns.

### 4. Index and retrieve on demand

Embed both episodic summaries and semantic records. Retrieve with hybrid search plus a recency boost, and pin commitments for every turn in the session.

```text
<memory source="session-42" type="semantic" confidence="0.9" updated="2026-11-20" trust="prior-session">
User prefers ISO dates and metric units in all reports.
</memory>
```

Label retrieved memory with its source, age, and confidence. Current user statements outrank stored memory. A retrieved memory is evidence about the past, not an instruction for the present.

### 5. Resolve contradictions explicitly

| Situation | Action |
| --- | --- |
| User corrects a fact | Supersede the old record, link both, keep the correction active |
| Newer source contradicts older | Prefer the newer authoritative source, record why |
| Two sources conflict and neither is authoritative | Keep both as `disputed`, ask the user |
| Inferred fact conflicts with stated fact | Stated fact wins; demote or delete the inference |
| Memory conflicts with the current message | Current message wins for this turn; confirm if it changes a commitment |

Never leave two active records that assert opposite facts. That produces inconsistent answers that look random.

### 6. Evict, forget, and audit

- Set a TTL by type: transient preferences 30 days, commitments until fulfilled plus 30 days, episodic summaries 90 days unless pinned.
- Honor deletion requests within a defined window (for example 30 days) across primary storage, indexes, caches, and backups.
- Write a tombstone with the record ID and deletion time so re-ingestion does not resurrect the data.
- Keep audit metadata (who, when, what type) without retaining deleted content.
- Re-check sensitivity labels on read; a record can outlive its original permission.

### 7. Measure recall, drift, and cost

```python
def should_compact(used_tokens, working_budget):
    return used_tokens > 0.75 * working_budget

def compact(turns, working_budget, summarize, count_tokens):
    keep, tokens = [], 0
    for turn in reversed(turns):
        cost = count_tokens(turn)
        if tokens + cost > 0.40 * working_budget:
            break
        keep.append(turn)
        tokens += cost
    older = turns[: len(turns) - len(keep)]
    summary = summarize(older)
    return summary, list(reversed(keep))
```

Test with a scripted session: seed facts and commitments early, add corrections, run past 60 turns, then probe. Track commitment retention, fact recall, contradiction handling, summary drift, and tokens per turn. Re-run after any change to the summarizer, embedding model, or eviction policy.

## Validation

```bash
pytest tests/memory/test_retention.py tests/memory/test_deletion.py -q
python -m evals.memory run --scenario long_session_60 --report runs/memory-latest.json
```

Pass criteria:

- [ ] 100% of active commitments survive 60 turns and compaction.
- [ ] Stated facts seeded at turn 1 are recalled at least 95% of the time (example target).
- [ ] User corrections supersede the old fact in 100% of scripted cases.
- [ ] Token usage stays within the tier budget at every turn.
- [ ] Compaction triggers before the response reserve is consumed.
- [ ] Deletion removes the record from primary storage, index, and cache within the stated window.
- [ ] No secret or payment data appears in the memory store.
- [ ] Retrieved memory is labeled with source and age.
- [ ] Summary fact checklist passes before old turns are evicted.
- [ ] Cross-session retrieval does not leak another user's records.

Fail the release if a commitment can be evicted without being fulfilled or explicitly closed.

## Gotchas

- Summarizing the previous summary compounds drift. Summarize source turns or keep a summary tree with source spans.
- Summaries drop exact identifiers, amounts, and dates. Preserve them verbatim in a structured field.
- Filling the window to 99% leaves no room for a tool result and truncates the system prompt first. Compact early.
- Stale preferences are worse than no preferences. Add TTLs and supersession.
- A user correction stored as a new fact while the old one stays active causes contradictory answers. Supersede atomically.
- Pinning everything defeats the budget. Pin commitments and a small set of critical constraints only.
- Duplicate memories crowd the context and skew retrieval. Deduplicate on write.
- Embeddings of summaries lose numeric precision. Keep exact values in the record and retrieve the record.
- "Lost in the middle" affects long memory blocks. Put commitments and current goal at the edges.
- Memory retrieved from an old session can carry stale authority. Label age and prefer current input.
- Stored third-party text can contain injected instructions. Re-label memory as data on read.
- Deletion that only removes the primary row leaves vectors and backups behind. Delete across every store.
- Dates like "Friday" are ambiguous across time zones. Resolve to an ISO date with a time zone.

## Output contract

```json
{
  "session_id": "sess-42",
  "turns": 64,
  "budget": {"total_tokens": 128000, "working_tokens": 48000, "used_tokens": 44120},
  "compactions": 3,
  "memory": {
    "commitments": [{"id": "mem-0184", "text": "Deliver migration plan by 2026-12-05", "status": "active", "source_turn": "t-184"}],
    "semantic_facts": [{"id": "mem-0007", "text": "Prefers ISO dates and metric units", "confidence": 1.0, "updated": "2026-11-20"}],
    "episodic_summary": "episodic/sess-42/segment-3.md",
    "superseded": [{"old": "mem-0031", "new": "mem-0055", "reason": "user_correction"}]
  },
  "retrieval": {"queried": 5, "selected": 2, "tokens": 820},
  "deletions": [{"id": "mem-0012", "requested_at": "2026-11-25", "completed_at": "2026-11-25", "stores": ["db", "index", "cache"]}],
  "health": {"commitment_retention": 1.0, "fact_recall": 0.96, "contradictions_open": 0}
}
```

## Checklist

- [ ] Memory tiers and token budgets defined.
- [ ] Compaction triggers at 70 to 80% of the working tier.
- [ ] Structured records carry source turn, confidence, and TTL.
- [ ] Commitments, decisions, corrections, and identifiers captured.
- [ ] Summaries use fixed sections and preserve exact values.
- [ ] Summary verified against a fact checklist before eviction.
- [ ] Hybrid retrieval with recency boost and pinned commitments.
- [ ] Retrieved memory labeled with source, age, and trust.
- [ ] Contradictions resolved by supersession, not duplication.
- [ ] Deletion covers storage, index, cache, and backups.
- [ ] Long-session retention tests run in CI.
- [ ] Secrets and payment data excluded from memory.

## Related skills

- `conversation-state-management` for schema versioning and persistence across sessions.
- `stateful-workflow-checkpointing` for durable checkpoints of long-running work.
- `retrieval-augmented-generation-orchestration` for hybrid retrieval and context packing.
- `prompt-injection-defense` for treating stored third-party text as untrusted.
