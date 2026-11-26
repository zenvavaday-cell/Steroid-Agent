---
name: user-story-mapping
description: Maps user journeys to stories, releases, and acceptance criteria with dependency awareness. Use for backlog shaping and incremental delivery.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: product-design
---

# User Story Mapping

## Overview

A story map arranges user activities left to right as a backbone, then places stories beneath them and slices the map into releases that each deliver a coherent outcome. It keeps the backlog anchored to the journey instead of to a component architecture.

The map is a planning artifact, not a status board. Its value is the conversation about what a usable release requires, what can wait, and which dependencies would otherwise surface late.

## When to use

- Shaping a backlog for a new product or a large feature.
- Slicing an MVP that must work end to end.
- Coordinating a journey that spans multiple teams or services.
- Exposing dependencies and enablers before estimation.
- Re-planning after scope cuts or a missed release.
- Onboarding stakeholders to how the product fits together.

Do not use for a single well-understood bug fix, or before the journey has been observed with real users.

## Workflow

### 1. Fix the frame

State the user, the goal, the start and end of the journey, and the segment in scope. Write the frame at the top of the map; it prevents the map from absorbing every possible flow.

```text
User: self-serve admin
Goal: reconcile and approve month-end payables
Start: opens reconciliation queue
End: approval confirmation with audit entry
Out of scope: external auditor review, mobile native
```

### 2. Build the backbone from observed behavior

Walk a real session or recording and write 5 to 9 activities in chronological order. Activities are verbs the user performs, not system modules.

Weak backbone: Authentication, Dashboard, API, Database.
Better backbone: Prepare, Locate, Compare, Decide, Approve, Confirm, Recover.

If the journey has more than 9 activities, group lower-level steps under broader activities rather than expanding the backbone.

### 3. Add user steps beneath each activity

Steps describe what the user does and what they need to see. Keep system actions in a separate lane, or they will crowd out the user view.

| Activity | Step | User need |
| --- | --- | --- |
| Locate | Filter to open period | See only invoices due this month |
| Compare | Review suggested match | Understand why a match was proposed |
| Approve | Approve a batch | Act without opening each invoice |

### 4. Write stories as vertical slices

Use `As a [role], I want [capability], so that [outcome]`. A story should sit under one step and deliver observable value. Split stories that require multiple activities to demonstrate.

```markdown
Story S-014
As a self-serve admin, I want to see match confidence and the matched fields,
so that I can approve high-confidence matches without opening each invoice.

Acceptance criteria:
- Given an invoice with a single high-confidence candidate,
  when the queue loads, then the candidate and confidence are visible.
- Given no candidate above threshold, when the queue loads,
  then the row shows "No match found" and a manual search action.
- Given the user lacks approval permission, when the queue loads,
  then the approve control is hidden and the reason is available.
```

### 5. Slice releases horizontally

Draw release lines across the map. Each slice must produce a usable outcome for at least one segment. A slice made only of infrastructure or only of one activity is not a release; it is a layer.

| Release | Outcome | Activities covered | Exit criteria |
| --- | --- | --- | --- |
| R1 Walking skeleton | Admin can view and manually match one invoice | Locate, Compare, Approve | One invoice approved end to end in staging |
| R2 Batch | Admin can approve high-confidence batches | Locate, Compare, Approve, Confirm | 10 invoices approved with audit rows |
| R3 Recovery | Admin can correct a wrong match | All | Reversal recorded and visible |

### 6. Attach acceptance criteria and states

For every story, cover the happy path, empty state, error state, and permission state. Use Given/When/Then. Acceptance criteria that restate the title add no test value.

### 7. Mark dependencies, enablers, and spikes

| Item | Type | Blocks | Owner | Mitigation |
| --- | --- | --- | --- | --- |
| Match scoring service | Enabler | S-014, S-015 | Platform | Contract-first stub in R1 |
| Audit schema change | Dependency | S-020 | Data | Migration in R2, backward compatible |
| Confidence threshold unknown | Spike | S-014 | Design | 3-day spike, decision by 2026-04-10 |

Every enabler must trace to a user outcome. Enablers without a consumer are backlog debt.

### 8. Estimate and sequence

Estimate at story level with the team's normal method. Sequence by risk and learning first, then value. Put the riskiest assumption in the earliest slice that can test it. Record confidence and assumptions next to the estimate.

### 9. Validate the map with the people who operate it

Review with design, engineering, support, and one real user if possible. Walk the map as a script: can each release be demonstrated end to end? Fix gaps before committing to a roadmap date.

## Validation

- Backbone gate: 5 to 9 activities, all verbs, chronological on a real walkthrough.
- Slice gate: each release covers at least three activities and names an exit demonstration.
- Story gate: every story has a role, capability, outcome, and at least two acceptance criteria.
- State gate: each story covers empty, error, and permission behavior or links to a shared pattern.
- Traceability gate: each story maps to a PRD requirement ID or research theme.
- Dependency gate: every dependency and enabler has an owner and mitigation.
- Sizing gate: no story exceeds the team's agreed size ceiling; oversized stories are split.

```bash
rg -n '^### Story' map.md | wc -l
rg -n 'Given .+, when .+, then .+' map.md | wc -l
```

The second count should be at least twice the first. Investigate any story with fewer than two criteria.

## Gotchas

- A backbone of features or systems is not a user journey. Rewrite with verbs.
- Stories written as technical tasks ("add an endpoint") hide the user outcome.
- Release 1 made of one architectural layer cannot be demonstrated to a user.
- Acceptance criteria that repeat the story title cannot fail a test.
- Ignoring permission and role variants creates late security work.
- The map goes stale after the first sprint. Version it and review at each release boundary.
- Too many activities make the map unreadable. Group steps, not activities.
- Enablers with no user trace accumulate as invisible scope.
- Dependencies discovered during implementation cause date slippage. Surface them on the map.
- One persona's path masks admin, support, and recovery flows.
- Estimates without uncertainty become commitments. Record confidence.
- A map built without observing the real journey encodes team assumptions.

## Output contract

```json
{
  "frame": {"user": "...", "goal": "...", "start": "...", "end": "...", "out_of_scope": ["..."]},
  "backbone": [
    {"activity": "Locate", "steps": ["Filter to open period"], "stories": ["S-010"]}
  ],
  "releases": [
    {"id": "R1", "outcome": "...", "stories": ["S-010", "S-011"], "exit_demo": "..."}
  ],
  "stories": [
    {
      "id": "S-010",
      "activity": "Locate",
      "role": "self-serve admin",
      "capability": "...",
      "outcome": "...",
      "acceptance_criteria": ["Given ..., when ..., then ..."],
      "states": ["empty", "error", "permission"],
      "estimate": "3",
      "confidence": "medium",
      "requirement_id": "REQ-001",
      "dependencies": ["D-02"]
    }
  ],
  "dependencies": [
    {"id": "D-02", "type": "enabler", "blocks": ["S-014"], "owner": "...", "mitigation": "..."}
  ],
  "risks": ["..."]
}
```

## Checklist

- [ ] Frame states user, goal, start, end, and out-of-scope.
- [ ] Backbone has 5 to 9 verb activities in observed order.
- [ ] Steps describe user actions and needs.
- [ ] Every story is a vertical slice with role, capability, and outcome.
- [ ] Every story has at least two Given/When/Then criteria.
- [ ] Empty, error, and permission states covered.
- [ ] Each release delivers an end-to-end outcome with an exit demo.
- [ ] Dependencies and enablers have owners and mitigations.
- [ ] Stories trace to PRD requirements or research themes.
- [ ] Estimates include confidence and assumptions.
- [ ] Map reviewed with design, engineering, and support.
- [ ] Version and review date recorded.

## Related skills

- `product-requirements-document` for the scope and metrics the map must satisfy.
- `product-metrics-instrumentation` to define the events each release slice must emit.
- `feature-flag-lifecycle-management` to decouple release slices from deploy timing.
- `usability-test-analysis` to validate each slice with task-based evidence.
