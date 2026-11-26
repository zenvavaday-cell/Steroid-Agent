---
name: jobs-to-be-done-analysis
description: Defines jobs, forces, and success criteria from customer evidence and competing solutions. Use for opportunity sizing and product positioning.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: product-design
---

# Jobs-to-be-Done Analysis

## Overview

Customers do not buy products, they hire them to make progress in a specific situation. A job statement captures that progress without naming a solution. The forces model explains why switching happens or stalls: push, pull, anxiety, and habit.

The analysis is only as good as the switch evidence behind it. Reconstruct real timelines of first thought, passive looking, active looking, deciding, and first use. Opinions about what someone might do are hypotheses, not jobs.

## When to use

- Entering a new market or segment with unclear demand.
- Repositioning a product that is described by features.
- Prioritizing a roadmap against unmet outcomes.
- Designing packaging or pricing around a value metric.
- Investigating churn or stalled adoption.
- Comparing direct, indirect, and do-nothing alternatives.

Do not use for usability defect triage, or when no behavioral evidence about a recent switch exists.

## Workflow

### 1. Collect switch evidence

Interview people who recently switched, abandoned, or seriously considered a change, ideally within 90 days. Also collect win/loss notes, churn reasons, support tickets, and search or comparison behavior.

```text
Timeline for each participant:
1. First thought: what happened in the situation?
2. Passive looking: what did they notice without searching?
3. Active looking: what did they compare, ask, or trial?
4. Deciding: what almost stopped them?
5. First use: what proved or disproved the promise?
```

Record verbatim quotes with participant IDs and timestamps. Do not ask "would you use" questions.

### 2. Write job statements

Format: `When [situation], I want to [motivation], so I can [expected outcome].`

- One situation per statement.
- No product, feature, or channel nouns in the motivation.
- The outcome must be observable or measurable.

Weak: "When I open the app, I want a dashboard, so I can see sales."
Better: "When I start the week, I want to know which accounts need attention, so I can spend my first hour on the highest-risk renewals."

### 3. Split functional, emotional, and social dimensions

| Dimension | Question | Example (illustrative) |
| --- | --- | --- |
| Functional | What task progress is required? | Reconcile invoices without manual export |
| Emotional | How do they want to feel or avoid feeling? | Avoid the anxiety of a missed payment |
| Social | How do they want to be perceived? | Look reliable to the finance team |

A job with only a functional statement is incomplete for consumer and team products.

### 4. Map job stages and desired outcomes

Use eight stages: define, locate, prepare, confirm, execute, monitor, modify, conclude. For each stage write outcome statements in the form `Minimize the [time, effort, likelihood] of [object] in [context]`.

```json
{
  "job_id": "J1",
  "statement": "When I close the month, I want reconciled payables, so I can sign off without a late correction",
  "stages": [
    {"stage": "locate", "outcome": "Minimize the time to find unmatched invoices across systems"},
    {"stage": "confirm", "outcome": "Minimize the likelihood of approving a duplicate payment"}
  ]
}
```

### 5. Score opportunity

Survey importance and satisfaction on 1 to 10 scales with at least 100 respondents per segment when making a quantified claim. Apply the Ulwick-style formula:

```text
opportunity = importance + max(importance - satisfaction, 0)
```

The score ranges from 1 to 20. Treat scores of 10 or higher with importance of 7 or higher as underserved candidates, and scores below 7 as possible over-serving. State that thresholds are a screening aid, not a universal law.

### 6. Analyze the four forces

| Force | Evidence to collect | Design response |
| --- | --- | --- |
| Push of the situation | Trigger event, cost of the status quo | Sharpen urgency in messaging |
| Pull of the new solution | Promised outcome, proof, demo moment | Show time-to-value early |
| Anxiety of the new | Data migration, learning curve, risk | Trial, guarantees, reversible setup |
| Habit of the present | Workarounds, sunk cost, approvals | Import paths, coexistence, switching support |

Every force in the matrix needs a quote or a labeled hypothesis. A growth plan that only amplifies pull ignores the two forces that block the switch.

### 7. Map alternatives, including non-consumption

List direct competitors, indirect workarounds (spreadsheets, assistants, internal tools), and doing nothing. For each, record the job stage where it wins and why.

### 8. Size and prioritize

Rank jobs by underserved score, frequency, segment size, and strategic fit. Keep the raw inputs so the ranking can be recomputed. Label any market size estimate with its source and date.

### 9. Validate the model

Run 3 to 5 additional switch interviews and check whether new evidence fits the job map. If a new force appears, update the model version rather than forcing the quote into an existing category.

## Validation

- Grammar gate: every job statement matches `^When .+, I want to .+, so I can .+\.$` and contains no feature nouns from the current product name list.
- Evidence gate: each job has at least 5 independent participants, or is labeled `small_n`.
- Force gate: each job has at least one evidence item for all four forces, or an explicit hypothesis flag.
- Math gate: recompute a 10% sample of opportunity scores from raw responses and require exact matches.
- Segment gate: scores are not averaged across segments with different jobs.
- Recency gate: switch events are dated and the median recency is reported.

```bash
python3 - <<'PY'
import re
stmt = "When I close the month, I want reconciled payables, so I can sign off without a late correction."
assert re.match(r"^When .+, I want to .+, so I can .+\.$", stmt), "bad grammar"
print("OK")
PY
```

## Gotchas

- Job statements that smuggle in a solution ("I want a dashboard") recreate feature thinking.
- Demographics are not jobs. Two people of the same age can hire different products for different progress.
- A goal is not a job. Jobs are situational and recur; goals are outcomes the person pursues.
- A task is a step inside a job. Do not confuse "export the CSV" with the month-end reconciliation job.
- Interviewing only current customers creates survivorship bias. Include churners and non-buyers.
- Asking about future behavior yields polite fiction. Reconstruct the last real decision.
- Stated importance can diverge from behavior. Weight observed actions and tradeoffs.
- Opportunity scores from tiny samples are noise. Report n and confidence.
- Ignoring non-consumption hides the largest untapped job.
- Skipping emotional and social jobs under-explains switching anxiety.
- Combining several situations into one job makes the statement unactionable.
- Anxiety evidence decays after purchase. Capture it during the decision window.
- Scores from different survey scales are not comparable. Keep the scale and wording fixed.
- A model that never gets contradicted is probably not being tested. Schedule a validation round.

## Output contract

```json
{
  "model_version": "1.0",
  "segment": "self-serve finance teams, 10-50 employees",
  "jobs": [
    {
      "id": "J1",
      "statement": "When I close the month, I want reconciled payables, so I can sign off without a late correction.",
      "dimensions": {"functional": "...", "emotional": "...", "social": "..."},
      "outcomes": [{"stage": "confirm", "statement": "Minimize the likelihood of approving a duplicate payment"}],
      "opportunity": {"importance": 8.1, "satisfaction": 4.2, "score": 12.0, "n": 142},
      "forces": {
        "push": [{"quote_id": "S04:18:22", "text": "..."}],
        "pull": [{"quote_id": "S09:07:10", "text": "..."}],
        "anxiety": [{"quote_id": "S06:31:05", "text": "..."}],
        "habit": [{"quote_id": "S11:02:44", "text": "..."}]
      }
    }
  ],
  "alternatives": [{"name": "spreadsheet + bank portal", "wins_at": ["locate", "confirm"]}],
  "priorities": ["J1"],
  "hypotheses": ["..."],
  "evidence_gaps": ["No churner interviews for the enterprise segment"]
}
```

## Checklist

- [ ] Switch timeline captured for each participant.
- [ ] Job statements follow the grammar and exclude solutions.
- [ ] Functional, emotional, and social dimensions written.
- [ ] Job stages and outcome statements mapped.
- [ ] Importance and satisfaction collected on fixed scales.
- [ ] Opportunity scores computed and spot-checked.
- [ ] Four forces documented with evidence or hypothesis flags.
- [ ] Alternatives include indirect workarounds and non-consumption.
- [ ] Segment sizes and frequencies sourced.
- [ ] Model validated with new interviews.
- [ ] Evidence gaps and small-n warnings recorded.

## Related skills

- `user-research-synthesis` to code switch interviews into themes before job modeling.
- `product-requirements-document` to translate prioritized jobs into scoped requirements.
- `pricing-strategy-analysis` to connect value metrics to willingness to pay.
- `customer-churn-analysis` to source churn evidence and quantify the switching loss.
