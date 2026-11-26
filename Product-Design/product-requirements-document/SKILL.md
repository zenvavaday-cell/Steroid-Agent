---
name: product-requirements-document
description: Writes scoped PRDs with users, problems, requirements, metrics, non-goals, and rollout notes. Use for feature planning and stakeholder alignment.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: product-design
---

# Product Requirements Document

## Overview

A PRD is a decision document, not a specification dump. It states who has the problem, what evidence shows the problem is worth solving, what is in scope, what is deliberately out of scope, how success is measured, and how the change reaches users and can be reversed.

The hard discipline is testability. Every Must requirement needs an observable acceptance criterion, and every success metric needs a baseline, target, window, and data source. Anything else is a wish.

## When to use

- Planning a feature that spans more than one team or sprint.
- Aligning design, engineering, data, support, and legal before build.
- Handing work to an external vendor or new team member.
- Defining an experiment or staged rollout.
- Re-scoping an existing initiative after new evidence.
- Documenting a platform or API change that affects other products.

Do not use for a copy tweak, a single bug fix, or as a replacement for a technical design document.

## Workflow

### 1. Write the problem statement with evidence

Use one paragraph and three to five evidence links. Name the affected segment, the current workaround, and the cost of inaction.

```markdown
Problem: Self-serve admins abandon month-end reconciliation because unmatched
invoices require export to a spreadsheet. In the last 90 days, 42% of accounts
with 3 or more unmatched invoices opened the export page but did not return to
approve. Evidence: SYN-2026-03 T1, support tag `reconcile-export` (n=87),
funnel `reconcile_export_then_return` (2026-01-01 to 2026-03-31).
```

If there is no baseline for the claimed problem, say so and make baseline capture the first requirement.

### 2. Define users and jobs

List primary, secondary, and excluded users. Link each to a job statement or research theme. Include roles and permissions, not just personas.

| User | Job or need | Evidence | In scope |
| --- | --- | --- | --- |
| Self-serve admin | Close the month without manual export | T1, S07 | Yes |
| External auditor | Read-only evidence trail | Legal review | No (phase 2) |

### 3. Set goals and non-goals

Goals are outcomes, not deliverables. Non-goals prevent silent scope creep and must be reviewed by the same stakeholders as goals.

```markdown
Goals:
- Reduce export-then-return abandonment from 42% to below 25% within 60 days of GA.
Non-goals:
- Automated ledger sync with third-party accounting systems.
- Changing the approval permission model.
- Mobile-native reconciliation in this release.
```

### 4. Write testable requirements

Use stable IDs and MoSCoW priority. Each requirement has a user outcome, acceptance criteria, and telemetry.

```markdown
| ID | Priority | Requirement | Acceptance criteria | Telemetry |
| --- | --- | --- | --- | --- |
| REQ-001 | Must | Show unmatched invoices inline with suggested matches | Given 3+ unmatched invoices, when the admin opens the queue, then all appear within 2 s and each shows a match confidence | `reconcile_queue_viewed`, `match_suggested` |
| REQ-002 | Should | Allow bulk approval of high-confidence matches | Given 5 selections, when approved, then one audit entry per invoice is written | `matches_bulk_approved` |
```

Reject adjectives that cannot be measured: fast, intuitive, seamless, robust, user-friendly. Replace each with a threshold or a test.

### 5. Define success and guardrail metrics

```yaml
metrics:
  primary:
    name: reconcile_abandonment_rate
    definition: users who open the queue and do not approve within 24h / users who open the queue
    baseline: 0.42
    target: 0.25
    window: 60 days after GA
    source: warehouse.fct_reconcile_events
  guardrails:
    - name: approval_error_rate
      threshold: "<= 0.01"
    - name: p95_queue_load_ms
      threshold: "<= 2000"
```

State the denominator and exclusion rules. A metric whose definition can drift is not a metric.

### 6. Cover experience states and accessibility

List empty, loading, partial, error, permission-denied, and success states. Specify copy, keyboard behavior, focus order, and WCAG 2.2 AA as the floor. Note any destructive action and its confirmation.

### 7. Capture technical, data, and compliance constraints

Record API changes, schema migrations, retention, PII fields, permission changes, feature flags, and backward compatibility. Link the technical design doc rather than duplicating it.

### 8. Plan rollout and rollback

```markdown
Rollout:
1. Internal accounts, flag `reconcile_inline_v2`, 1 week.
2. 10% of eligible accounts, 1 week, monitor guardrails daily.
3. 50%, then 100%, with a 24 h soak at each step.
Rollback: disable the flag; no schema rollback required. Data written by v2
remains readable by v1 via the `source` column.
```

Name the on-call owner, monitoring dashboard, and the exact threshold that triggers rollback.

### 9. Review and record decisions

Circulate to design, engineering, data, support, legal, and security as applicable. Keep an open-questions table with owner and due date, and a decision log with date and rationale.

## Validation

- Problem gate: at least one quantitative baseline or an explicit baseline-capture task.
- Scope gate: non-goals are non-empty and signed off by the same reviewers as goals.
- Requirement gate: every Must has an ID, acceptance criteria, and telemetry or a written telemetry exception.
- Metric gate: primary metric has definition, baseline, target, window, and source.
- State gate: empty, error, loading, and permission states are specified.
- Accessibility gate: WCAG 2.2 AA target and keyboard path documented.
- Rollout gate: flag name, staged percentages, rollback trigger, and owner present.
- Vague-language scan:

```bash
rg -n -i '\b(fast|intuitive|seamless|robust|user-friendly|world-class)\b' prd.md
```

Each hit must be replaced with a measurable statement or moved to a clearly labeled design principle section.

## Gotchas

- A PRD that starts with the solution hides whether the problem is real.
- Requirements without acceptance criteria cannot be tested or accepted.
- A target without a baseline cannot demonstrate improvement.
- Vanity metrics (page views, signups without activation) make weak features look successful.
- Missing non-goals invite scope creep late in the cycle.
- Skipping empty and error states pushes design debt into engineering.
- Ignoring support and operations load creates hidden staffing costs.
- A rollout without a rollback trigger is a launch gamble.
- Stakeholder review as a rubber stamp is not alignment. Record objections.
- Mixing Must and Should priorities lets everything become mandatory.
- Undocumented assumptions become surprises. Put them in a table with owners.
- A PRD that is never updated after decisions becomes misinformation. Maintain a decision log.
- Accessibility as a final checklist item usually means rework. Specify it per requirement.

## Output contract

````markdown
# PRD: <feature>

## Summary
<3 sentences: problem, change, expected outcome>

## Problem and evidence
## Users and jobs
## Goals and non-goals
## Requirements
| ID | Priority | Requirement | Acceptance criteria | Telemetry |

## Success metrics
```yaml
primary: {name, definition, baseline, target, window, source}
guardrails: [{name, threshold}]
```

## Experience and accessibility
## Technical and data constraints
## Rollout and rollback
## Risks and mitigations
## Open questions
| Question | Owner | Due |

## Decision log
| Date | Decision | Rationale | Owner |
````

The completed PRD must be self-contained: a new engineer should be able to start without a meeting, and a reviewer should be able to reject it on explicit gates rather than taste.

## Checklist

- [ ] Problem statement cites quantitative or qualitative evidence.
- [ ] Primary, secondary, and excluded users listed.
- [ ] Goals are outcomes and non-goals are explicit.
- [ ] Every Must requirement has ID, acceptance criteria, and telemetry.
- [ ] Metrics have definitions, baselines, targets, windows, and sources.
- [ ] Guardrail metrics and rollback thresholds defined.
- [ ] Empty, loading, error, and permission states specified.
- [ ] Accessibility target and keyboard path documented.
- [ ] Technical, data, privacy, and migration constraints linked.
- [ ] Staged rollout, owner, and rollback plan present.
- [ ] Open questions have owners and due dates.
- [ ] Decision log updated after review.

## Related skills

- `user-story-mapping` to slice the PRD into releases and stories.
- `product-metrics-instrumentation` to implement the events and funnels named here.
- `jobs-to-be-done-analysis` to ground the problem in a validated job.
- `feature-flag-lifecycle-management` to manage the rollout flag after launch.
