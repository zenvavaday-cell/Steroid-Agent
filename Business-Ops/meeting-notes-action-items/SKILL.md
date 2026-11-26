---
name: meeting-notes-action-items
description: Extracts decisions, owners, deadlines, and risks from meetings and tracks follow-ups. Use for team meetings, boards, and project reviews.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: business-ops
---

# Meeting Notes and Action Items

## Overview

Meetings produce two durable assets: decisions and commitments. Transcripts and rough notes contain both, plus a large amount of discussion that must not be promoted to either. The discipline is evidence-based extraction: every decision cites the moment it was made, every action has exactly one owner and one verifiable deliverable, and unresolved items are labeled as open questions instead of being silently assigned.

This skill covers capture, extraction, close-out, publishing, and the follow-up loop that keeps commitments from disappearing between meetings.

## When to use

- Converting a recording, transcript, or rough notes into minutes for a team, board, or project review.
- Running a meeting close-out to confirm owners and dates before participants leave.
- Auditing an action tracker for stale, unowned, or unverifiable items.
- Building a decision log for governance, audit, or a project handover.
- Briefing someone who was not present on what was decided and what happens next.

Do not use for verbatim transcription, performance feedback conversations, or privileged discussions that require a separate retention and access policy.

## Workflow

### 1. Capture source and metadata

Record the meeting title, date, start and end time, timezone, chair, attendees and absentees, agenda, source artifact (recording, transcript, notes), and confidentiality class. Timestamps must reference one clock; state whether they come from the recording or the transcript.

| Field | Example | Required |
| --- | --- | --- |
| Meeting | Q4 pricing review | Yes |
| Date | 2026-11-24 | Yes |
| Chair | Dana Ruiz | Yes |
| Source | transcript, 00:00 to 58:12 | Yes |
| Attendees | 6 present, 2 absent | Yes |
| Classification | internal | Yes |

### 2. Separate decision language from discussion

Decision triggers include "approved", "we will", "agreed", "signed off", "final", and "go with". Discussion markers include "could", "maybe", "what if", and "I think". A sentence is a decision only when a person with authority commits to it. Everything else is an option, a concern, or an open question.

### 3. Extract decisions with evidence

Each decision gets an ID, a one-sentence statement, the rationale, the decider, dissent or caveats, and an evidence pointer (timestamp or paragraph). If the meeting reverses an earlier decision, record both and link them; do not silently overwrite history.

| ID | Decision | Rationale | Decider | Evidence |
| --- | --- | --- | --- | --- |
| D1 | Raise list price 8% on 2027-01-01 | Margin below plan for three quarters | Dana Ruiz | 00:14:22 |
| D2 | Grandfather existing annual contracts | Retention risk in top segment | Dana Ruiz | 00:21:05 |

### 4. Convert commitments into actions

Apply the action quality test: imperative verb, specific object, completion criterion, one owner, one due date. Record dependencies and the evidence that will close the item.

- Weak: "Look into pricing."
- Acceptable: "Produce a one-page comparison of the three shortlisted vendors and circulate it to the pricing group by 2026-12-04."

| ID | Action | Owner | Due | Done when | Depends on |
| --- | --- | --- | --- | --- | --- |
| A1 | Draft customer notice for the price change | Sam Okafor | 2026-12-01 | Legal-approved notice in the shared folder | D1 |
| A2 | Pull churn by contract type for 2025 | Priya Nair | 2026-11-28 | Query link and CSV attached to A2 | None |

### 5. Close out ambiguities live

Before the meeting ends, ask three questions for every commitment: who owns it, by when, and what does done look like. If the owner is unknown, assign someone to name the owner within two business days and make that itself an action. Never leave "the team" as the accountable owner.

### 6. Capture risks and open questions

Risks need a description, likelihood, impact, owner, trigger, and planned response. Open questions need an owner and a date by which an answer is expected. Keep them separate from actions so the tracker does not mix "decide" work with "do" work.

### 7. Publish and file within 24 hours

Send a summary (decisions, actions, risks, open questions), not the raw transcript. Store the canonical copy in one location, create tracker items using the same IDs, and mark the classification. Distribution outside the attendee list requires chair approval.

### 8. Run the follow-up loop

At the start of each meeting, review open actions as done, in progress, blocked, or dropped. Close an action only when its completion criterion is met and evidence is linked. Escalate anything overdue by more than one meeting cadence to the chair or sponsor.

## Validation

| Gate | Check | Fail action |
| --- | --- | --- |
| Action completeness | Owner, due date, and completion criterion present | Return to owner before publishing |
| Single ownership | Exactly one accountable owner per action | Split or reassign |
| Date sanity | ISO 8601 dates, relative dates resolved, past dates justified | Correct or flag |
| Decision evidence | Timestamp or quote for every decision | Mark as unverified |
| No inference | Decisions not explicitly made are listed as open questions | Recategorize |
| Count reconciliation | IDs unique and counts match the source extraction | Deduplicate |
| Chair review | Chair confirms within one business day | Hold distribution |
| Tracker sync | Every action has a tracker ID | Create missing items |
| Confidentiality | Classification set and distribution approved | Restrict access |

## Gotchas

- "We should" is a suggestion, not a decision. Promote it only if someone with authority commits and a rationale is stated.
- The loudest participant is not automatically the owner. Assign accountability to the role that can deliver, not to whoever discussed it.
- Relative dates such as "next Friday" are ambiguous across timezones and weeks. Resolve them to an ISO date during close-out.
- Group ownership ("the team", "ops") has no accountability. Name one person and list contributors separately.
- A topic such as "pricing" is not an action. Rewrite it as a deliverable with a completion criterion.
- Decisions get reversed later in the same meeting. Capture the final state and link the superseded decision.
- Side conversations before or after the formal agenda often contain the real decision. Include pre-reads and hallway agreements only with evidence.
- Transcripts misspell names and garble numbers. Verify names against the attendee list and confirm any number that will be published.
- The action list grows without bound when every suggestion becomes a task. Cap it at items with a committed owner and date.
- Notes are not minutes. Minutes are the formal record of decisions and actions; keep chat logs and transcripts separate.
- Publishing raw transcripts leaks side comments and personal data. Summarize and redact.
- Closing an action on a verbal claim without evidence recreates the original problem. Require a link, file, or verifiable state change.

## Output contract

```json
{
  "meeting": {
    "title": "Q4 pricing review",
    "date": "2026-11-24",
    "timezone": "America/New_York",
    "chair": "Dana Ruiz",
    "source": "transcript 00:00-58:12",
    "classification": "internal"
  },
  "decisions": [
    {
      "id": "D1",
      "decision": "Raise list price 8% on 2027-01-01",
      "rationale": "Margin below plan for three quarters",
      "decided_by": "Dana Ruiz",
      "evidence": "00:14:22",
      "status": "final"
    }
  ],
  "actions": [
    {
      "id": "A1",
      "action": "Draft customer notice for the price change",
      "owner": "Sam Okafor",
      "due": "2026-12-01",
      "done_when": "Legal-approved notice in the shared folder",
      "depends_on": ["D1"],
      "status": "open",
      "tracker_id": "OPS-412"
    }
  ],
  "risks": [
    {
      "id": "R1",
      "risk": "Top-segment churn spikes after notice",
      "likelihood": "medium",
      "impact": "high",
      "owner": "Priya Nair",
      "trigger": "monthly logo churn above 2%",
      "response": "Activate save play for at-risk accounts"
    }
  ],
  "open_questions": [
    {
      "id": "Q1",
      "question": "Does the enterprise agreement allow mid-term increases?",
      "owner": "Legal",
      "answer_by": "2026-11-28"
    }
  ]
}
```

## Checklist

- [ ] Meeting metadata, source, and classification recorded.
- [ ] Decision language separated from discussion.
- [ ] Every decision has rationale, decider, and evidence pointer.
- [ ] Every action has one owner, one ISO due date, and a completion criterion.
- [ ] Relative dates resolved and no group ownership remains.
- [ ] Risks and open questions captured separately with owners.
- [ ] Chair or delegate reviewed the summary.
- [ ] Canonical copy stored and tracker items created with matching IDs.
- [ ] Summary distributed within 24 hours to the approved audience.
- [ ] Prior open actions reviewed at the next meeting.
- [ ] Overdue items escalated by one cadence.

## Related skills

- `sop-generation` for turning recurring meeting follow-ups into a documented operating procedure.
- `operational-runbook-generation` for the operational tasks that actions often feed into.
- `incident-postmortem-generation` for a heavier action-tracking format after incidents.
- `confidence-threshold-output-gating` before publishing decisions that are still unverified.
