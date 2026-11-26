---
name: kpi-dashboard-design
description: Chooses metrics, definitions, and layouts for decision-focused dashboards with data-quality notes. Use for executive and operational reporting.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: business-ops
---

# KPI Dashboard Design

## Overview

A dashboard is a decision instrument, not a data display. It earns its cost when a named person looks at a specific view on a specific cadence and changes a decision because of it. Most dashboards fail because they start from available data rather than decisions, mix grains, and leave metric definitions implicit.

The discipline is to inventory decisions first, build a small metric tree, write a contract for every metric, design a visual hierarchy that answers "is this good or bad" in five seconds, and publish the data-quality caveats that determine whether the number can be trusted.

## When to use

- Designing an executive, operational, or customer-success dashboard from scratch.
- Consolidating overlapping reports into one source of truth.
- Defining metrics before instrumenting events or building warehouse models.
- Auditing an existing dashboard for undefined, duplicated, or misleading metrics.
- Setting up alert thresholds and an operating review cadence.

Do not use for one-off exploratory analysis, a data catalog, or a static board pack where the audience and decision are already fixed by a template.

## Workflow

### 1. Inventory the decisions

List the decisions the dashboard must support, who owns each, how often it is reviewed, and what action follows. If no action follows, the metric does not belong on the dashboard.

| Decision | Owner | Cadence | Trigger | Action |
| --- | --- | --- | --- | --- |
| Add sales capacity | CRO | Monthly | Pipeline coverage below 3x for two months | Open two reqs |
| Adjust onboarding | Head of CS | Weekly | Activation below 35% | Review funnel with product |
| Escalate service risk | Support lead | Daily | Backlog above 48 hours | Reassign queue |

### 2. Build the metric tree

One outcome metric per audience, three to five driver metrics, and one or two guardrails. More than nine primary tiles means the dashboard has no point of view. Use a tree, not a flat list, so the viewer can move from "what happened" to "why".

```text
Net revenue retention (outcome)
  Expansion revenue
  Contraction revenue
  Gross logo churn
  Guardrail: support CSAT
```

### 3. Write a metric contract for every metric

No tile ships without a contract. The contract is the definition of record and the basis for reconciliation.

| Field | Example |
| --- | --- |
| Metric | Weekly activation rate |
| Question | What share of new accounts reach first value within 7 days? |
| Formula | activated accounts / eligible signups |
| Grain | signup week, account |
| Filters | exclude internal, test, and duplicate accounts |
| Source | analytics.accounts, analytics.events |
| Owner | Head of Customer Success |
| Refresh | daily 06:00 UTC, 24-hour lag |
| Target | 0.40 by 2027-Q1 |
| Alert | below 0.35 for 3 consecutive days |

Write the calculation once, in SQL or a dbt model, and reference it from every tool. Dashboard-level custom calculations create definition drift.

```sql
WITH signups AS (
  SELECT account_id, DATE_TRUNC('week', created_at) AS signup_week
  FROM analytics.accounts
  WHERE is_internal = false AND is_test = false
),
activated AS (
  SELECT s.account_id, MIN(e.occurred_at) AS activated_at
  FROM signups s
  JOIN analytics.events e
    ON e.account_id = s.account_id
   AND e.name = 'first_value_action'
  GROUP BY 1
)
SELECT s.signup_week,
       COUNT(*) AS signups,
       COUNT(a.activated_at) AS activated,
       ROUND(COUNT(a.activated_at)::numeric / NULLIF(COUNT(*), 0), 4) AS activation_rate
FROM signups s
LEFT JOIN activated a USING (account_id)
GROUP BY 1
ORDER BY 1;
```

### 4. Validate data quality before designing visuals

Check freshness, row counts, duplicate keys, null rates in dimensions, and reconciliation to a trusted source such as billing or the general ledger. Publish the "as of" timestamp and known exclusions on the dashboard itself.

| Check | Method | Tolerance |
| --- | --- | --- |
| Freshness | MAX(loaded_at) versus SLA | Within 1 hour of SLA |
| Completeness | Row count versus previous 7-day median | Within 10% or explained |
| Uniqueness | Duplicate account or transaction keys | Zero |
| Reconciliation | MRR versus finance billing system | Within 0.5% |
| Validity | Nulls in required dimensions | Below 1% |

### 5. Design the visual hierarchy

Top row: outcome, trend, target, variance. Second row: drivers. Third row: segments and guardrails. Detail lives one click away. Use one color scale, consistent units, and direct labels. Red and green alone cannot carry meaning.

```text
+---------------------------------------------------------------+
| Outcome: NRR 104% | trend 6M | target 110% | variance -6 pts  |
+-------------------------------+-------------------------------+
| Driver: expansion             | Driver: gross churn           |
| Driver: contraction           | Guardrail: CSAT               |
+-------------------------------+-------------------------------+
| Segment table: plan, region, cohort                           |
+---------------------------------------------------------------+
| Data as of 2026-11-25 06:00 UTC | exclusions: internal accounts |
+---------------------------------------------------------------+
```

### 6. Set thresholds and alert routing

Every alert needs a threshold, a window, an owner, a channel, and a deduplication rule. Prefer relative changes plus an absolute floor to avoid noise on small bases. State known seasonality exclusions.

Example policy: alert the CS lead when the 7-day activation rate is below 0.35 for three consecutive days, or when it drops more than 15% versus the trailing 8-week median, excluding the last two weeks of December.

### 7. Review adoption and retire tiles

Track weekly active viewers, time to first answer, and the number of decisions recorded against the dashboard. Remove tiles with no viewers in 60 days. Review metric definitions quarterly with owners and log every change with an effective date.

## Validation

| Gate | Pass criterion | Fail action |
| --- | --- | --- |
| Decision link | Every primary tile maps to a named decision and owner | Remove or justify |
| Contract | Definition, formula, grain, filters, source, owner present | Block publication |
| Grain consistency | No tile mixes account and event grain without explicit aggregation | Rebuild metric |
| Reconciliation | Within 0.5% of finance or system of record | Investigate before launch |
| Freshness | Within the stated SLA and shown on the page | Add warning banner |
| Alert quality | Threshold, window, owner, and dedupe defined | Do not enable |
| Performance | Primary view loads in under 10 seconds or is pre-aggregated | Optimize query |
| Accessibility | Contrast at least 4.5:1 and no color-only encoding | Adjust palette |
| Ownership | Every metric has one accountable owner | Assign before launch |

## Gotchas

- Vanity metrics such as page views rise without proving value. Pair every activity metric with an outcome.
- Averages of averages produce wrong totals. Aggregate from the base rows or use weighted averages.
- "Active user" without a stated event and window is not a metric. Define the event, threshold, and timezone.
- Dashboards mix signup, account, and event grain. State the grain on every tile and never sum across grains.
- Late-arriving data changes yesterday's number. Show the data-as-of time and use a stable cutoff for official reporting.
- Metric definitions drift when each team writes its own SQL. Centralize the calculation and publish one definition.
- Timezone boundaries shift daily counts. Fix the reporting timezone and state it.
- Too many decimal places imply precision the data does not have. Round to the decision-relevant unit.
- Red and green fail for colorblind viewers and in printed board packs. Add labels, arrows, and text.
- Targets without a baseline or owner are wishes. Record the baseline, target date, and accountable person.
- Silent metric changes destroy trust. Version definitions and annotate changes on the chart.
- Correlated metrics presented as independent drivers mislead. Show the relationship or drop one.

## Output contract

```yaml
dashboard:
  name: Customer Success Operating Review
  audience: CS leadership
  primary_decision: Where to intervene in retention this week
  cadence: weekly, Monday 09:00
  refresh: daily 06:00 UTC, 24-hour lag
  data_as_of_display: required
  metrics:
    - id: nrr
      label: Net revenue retention
      question: Are existing accounts growing or shrinking?
      formula: (starting_mrr + expansion - contraction - churn) / starting_mrr
      grain: account-month
      filters: [exclude_internal, exclude_test]
      source: analytics.mrr_monthly
      owner: VP Customer Success
      target: 1.10
      alert: below 1.05 for two consecutive months
    - id: activation_rate
      label: Weekly activation rate
      formula: activated_accounts / eligible_signups
      grain: signup-week
      owner: Head of Customer Success
      target: 0.40
  layout:
    row_1: [nrr, trend, target, variance]
    row_2: [expansion, contraction, gross_churn, csat]
    row_3: [segment_table]
  data_quality:
    reconciliation: within 0.5% of billing MRR
    freshness_sla: 24 hours
    known_exclusions: internal and test accounts
  deprecated_tiles: []
```

## Checklist

- [ ] Decision inventory completed with owners and cadence.
- [ ] Metric tree has one outcome, three to five drivers, and guardrails.
- [ ] Every metric has a written contract.
- [ ] Calculations live in one governed model, not per-tile SQL.
- [ ] Grain stated and consistent across tiles.
- [ ] Data reconciled to a system of record within tolerance.
- [ ] Freshness and exclusions visible on the dashboard.
- [ ] Layout answers good or bad within five seconds.
- [ ] Alerts have thresholds, windows, owners, and dedupe rules.
- [ ] Accessibility checks passed.
- [ ] Usage reviewed and unused tiles retired after 60 days.
- [ ] Definition changes versioned with effective dates.

## Related skills

- `product-metrics-instrumentation` for the event taxonomy and tracking plan behind product metrics.
- `data-quality-profiling` for freshness, null, and drift checks before publishing.
- `warehouse-schema-design` for the grain, keys, and marts that make metrics reliable.
- `dbt-model-development` for version-controlled metric models and tests.
