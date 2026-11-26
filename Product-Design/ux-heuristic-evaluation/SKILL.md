---
name: ux-heuristic-evaluation
description: Audits interfaces against usability heuristics with severity, evidence, and concrete fixes. Use for expert reviews before user testing.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: product-design
---

# UX Heuristic Evaluation

## Overview

A heuristic evaluation is a structured expert review, not a taste review. Evaluators walk representative tasks, compare what the interface does against established usability principles, and record problems with reproducible evidence and a severity rating.

The output is a prioritized list of defects with fixes, not a list of opinions. Expert findings predict where users will struggle, but they are hypotheses until task-based testing confirms them.

## When to use

- Reviewing a flow before spending on moderated usability testing.
- Auditing a redesign or a competitor product for known usability risks.
- Triaging a backlog of UX complaints into root causes.
- Establishing a baseline before a design system or navigation change.
- Reviewing error, empty, and permission states that demos skip.
- Preparing a focused test plan by identifying likely failure points.

Do not use as the only validation for a high-stakes or regulated flow, or as a substitute for testing with assistive technology users.

## Workflow

### 1. Define scope, tasks, and environment

Write 3 to 5 tasks that a real user would attempt. Record the role, starting URL, auth state, viewport, browser, and data fixtures. A finding without environment is not reproducible.

```text
Task T2: As an admin with 12 unmatched invoices, approve the 3 highest-confidence
matches without opening each invoice.
Start: /reconcile (staging account admin+12)
Viewport: 1440x900 and 390x844
Browser: Chromium 124, Firefox 125
```

### 2. Walk each task step by step

For every action record: what the evaluator expected, what happened, the screen ID, and the evidence file. Capture a screenshot or short recording at each state change.

```text
Step 2.3: Select three rows, click "Approve selected".
Expected: confirmation with count and total.
Actual: button disabled with no explanation; no tooltip.
Evidence: shot-014.png, recording-t2-03.webm
```

### 3. Evaluate against the ten heuristics

| ID | Heuristic | What to look for |
| --- | --- | --- |
| H1 | Visibility of system status | Progress, saved state, async completion |
| H2 | Match with the real world | Domain language, order of information |
| H3 | User control and freedom | Undo, cancel, exit, back without loss |
| H4 | Consistency and standards | Same action, same label and placement |
| H5 | Error prevention | Constraints, confirmation for destructive acts |
| H6 | Recognition over recall | Visible options, context, recent items |
| H7 | Flexibility and efficiency | Shortcuts, bulk actions, defaults |
| H8 | Aesthetic and minimalist design | Competing calls to action, noise |
| H9 | Error recovery | Plain-language errors, cause, next step |
| H10 | Help and documentation | Contextual help, searchable docs |

Map every finding to one primary heuristic. "General UX" is not a heuristic; if nothing fits, the problem may be a functional bug or an accessibility issue.

### 4. Add accessibility checks

Automated tools catch only part of WCAG 2.2 AA. Use them as a screen, then verify manually.

```bash
npx @axe-core/cli http://localhost:3000/reconcile --exit
```

Manual checks for each task:

- Keyboard only: complete the task with Tab, Shift+Tab, Enter, Space, Escape.
- Focus visible and order logical; no keyboard trap.
- Contrast at least 4.5:1 for body text, 3:1 for large text and UI boundaries.
- Labels, errors, and status messages announced, not color-only.
- Target size at least 24x24 CSS px, or spacing exception documented.
- Zoom to 200% and reflow at 320 CSS px without loss of function.

### 5. Write the issue record

```json
{
  "id": "UX-014",
  "task": "T2",
  "screen": "reconcile-queue",
  "step": "2.3",
  "heuristic": "H1",
  "observation": "Approve selected is disabled without explanation after selecting 3 rows",
  "expected": "Enabled action or visible reason for being disabled",
  "impact": "Admin cannot complete batch approval and has no recovery path",
  "frequency": "every session with 3+ selections",
  "persistence": "persists until selection changes",
  "severity": 3,
  "evidence": ["shot-014.png", "recording-t2-03.webm"],
  "fix": "Enable when at least one eligible row is selected; otherwise show inline reason and link to eligibility rules.",
  "acceptance": "With 3 eligible rows selected, Approve selected is enabled and completes the action."
}
```

### 6. Rate severity consistently

Combine frequency, impact, and persistence. Use the Nielsen 0 to 4 scale.

| Score | Label | Criteria | Action |
| --- | --- | --- | --- |
| 4 | Catastrophic | Blocks the task for most users, no workaround, data risk | Fix before release |
| 3 | Major | Blocks or severely slows many users, workaround is costly | Fix in current cycle |
| 2 | Minor | Causes hesitation or rework for some users | Schedule soon |
| 1 | Cosmetic | Noticeable but no meaningful task impact | Batch with related work |
| 0 | Not a problem | Evaluator preference or disagreement with strategy | Do not log |

Calibrate two evaluators on the first five issues. If their scores differ by more than one level, adjudicate with the task impact, not seniority.

### 7. Deduplicate and find root causes

Cluster findings by underlying component or pattern. Five disabled-button findings may share one state model. Report root causes and affected instances, not five separate tickets.

### 8. Prioritize fixes

Rank by severity, then reach (how many tasks or users), then effort. Write the fix as a testable change with an acceptance check, and note any design-system or accessibility dependency.

### 9. Run independent evaluators and merge

Use 3 to 5 evaluators with different backgrounds. Each evaluates independently before discussion to avoid anchoring. Merge duplicates, preserve unique findings, and report how many issues each evaluator found alone.

### 10. Report and schedule confirmation

Deliver the report with task coverage, environment, severity distribution, and top fixes. Mark which findings need user validation and add them to the next usability test plan.

## Validation

- Coverage gate: every task has a completed walkthrough with start and end states.
- Evidence gate: every severity 3 or 4 finding has a screenshot or recording and exact reproduction steps.
- Heuristic gate: each finding maps to one of H1 to H10 or to a WCAG criterion.
- Calibration gate: two evaluators agree within one severity level on the calibration sample, or an adjudication note exists.
- Accessibility gate: keyboard-only and contrast checks completed manually, not only via axe.
- Fix gate: every recommended fix has an acceptance check.
- Dedup gate: no two findings describe the same root cause without cross-reference.
- Scope gate: environment, fixtures, and viewports recorded.

```bash
rg -n '^### UX-' report.md | wc -l
rg -n '"severity": [34]' findings.json | wc -l
```

Spot-check five severity 3 or 4 entries and confirm each has evidence and acceptance criteria.

## Gotchas

- Findings without reproduction steps cannot be verified or fixed.
- Evaluators are not users. Treat every finding as a hypothesis until tested.
- Severity inflation makes the report easy to ignore. Use the scale, not urgency.
- A preference for a different layout is not a usability defect. Tie it to task impact.
- Screenshots without URL, role, and data state mislead during triage.
- Happy-path-only reviews miss the error and empty states where users get stuck.
- Heuristics used as a checklist without task context produce generic advice.
- Desktop-only review misses responsive breakage.
- A hundred unranked issues is not a deliverable. Lead with the top five.
- Automated accessibility tools cover only a minority of WCAG criteria. Verify by hand.
- Recommended fixes that ignore the design system create new drift.
- Independent evaluators who discuss first converge prematurely. Collect findings separately.
- Confirmation bias favors flows the evaluator designed. Use a task script and fresh eyes.

## Output contract

```json
{
  "review_id": "HE-2026-04",
  "scope": {"tasks": ["T1", "T2"], "viewport": ["1440x900", "390x844"], "browsers": ["chromium", "firefox"]},
  "evaluators": 3,
  "coverage": {"tasks_completed": 2, "screens_reviewed": 14},
  "findings": [
    {
      "id": "UX-014",
      "task": "T2",
      "screen": "reconcile-queue",
      "heuristic": "H1",
      "observation": "...",
      "expected": "...",
      "impact": "...",
      "severity": 3,
      "evidence": ["shot-014.png"],
      "fix": "...",
      "acceptance": "...",
      "needs_user_validation": true
    }
  ],
  "summary": {"catastrophic": 0, "major": 3, "minor": 6, "cosmetic": 2},
  "top_fixes": ["UX-014", "UX-009"],
  "limitations": ["No assistive-technology users on the review team"]
}
```

## Checklist

- [ ] 3 to 5 representative tasks defined with roles and fixtures.
- [ ] Environment, viewport, and browser recorded.
- [ ] Each task walked end to end with evidence.
- [ ] Every finding mapped to one heuristic or WCAG criterion.
- [ ] Severity rated with the 0 to 4 scale and calibrated.
- [ ] Keyboard and contrast checks done manually.
- [ ] Findings deduplicated by root cause.
- [ ] Fix and acceptance check written for each top finding.
- [ ] 3 to 5 evaluators worked independently.
- [ ] Issues needing user validation flagged.
- [ ] Summary and top five fixes lead the report.

## Related skills

- `usability-test-analysis` to confirm heuristic findings with task-based user evidence.
- `design-system-audit` when findings trace to component or token drift.
- `accessibility-format-conversion` when remediation requires accessible output formats.
- `user-story-mapping` to place fixes into release slices with acceptance criteria.
