---
name: data-quality-profiling
description: Profiles completeness, uniqueness, validity, consistency, and drift before pipelines or models consume data. Use for onboarding datasets and monitoring production tables.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: data-ai
---

# Data Quality Profiling

## Overview

A table can load successfully every day and still be unusable. Profiling measures the properties consumers actually depend on (key uniqueness, null behavior, value domains, cross-field rules, freshness) and compares them to an explicit baseline. The result is a set of numeric gates, not a dashboard that nobody reads.

The core discipline is to profile a stable snapshot, publish thresholds per column with a severity, and fail the pipeline when a critical threshold breaks. Every metric needs a defined denominator and a documented null policy, otherwise two teams will compute "completeness" differently.

## When to use

- Onboarding a new source or vendor extract before writing transformations.
- Adding a table to a warehouse mart or a feature pipeline.
- Investigating why a model or report changed without a code change.
- Setting up production monitoring for freshness, volume, and schema drift.
- Reviewing a data contract before signing it with a producer.
- Auditing an inherited dataset with no documentation.

Do not use for one-off ad hoc questions where a single `SELECT` answers the question; profiling costs compute and needs a maintained baseline to be useful.

## Workflow

### 1. Scope the dataset and its consumers

Record the fully qualified table, owner, downstream consumers, update cadence, and the decision the data supports. Pick the profiling snapshot explicitly:

```sql
-- PostgreSQL: stable sample, repeatable with the same seed behavior
SELECT * FROM analytics.orders
TABLESAMPLE SYSTEM (5) REPEATABLE (42);
```

For tables under roughly 1 million rows, profile the full table. For larger tables, sample at least 100,000 rows or 1 percent, whichever is larger, and note the sample rate in the report. Always profile `WHERE updated_at <= :as_of` so results are reproducible.

### 2. Inventory columns and candidate keys

Pull types, nullability, and comments from the catalog, then confirm candidate keys with a uniqueness check:

```sql
SELECT
  COUNT(*) AS rows,
  COUNT(DISTINCT order_id) AS distinct_order_id,
  COUNT(*) FILTER (WHERE order_id IS NULL) AS null_order_id
FROM analytics.orders;
```

A column is a usable key only if `distinct = rows` and `null = 0`. Check composite keys with `COUNT(DISTINCT (a, b))`, and remember that a SQL `UNIQUE` constraint permits multiple nulls in most engines.

### 3. Compute the six quality dimensions

| Dimension | Metric | Example gate |
| --- | --- | --- |
| Completeness | non-null / total | `customer_id >= 0.999` |
| Uniqueness | distinct / total on key | `order_id = 1.000` |
| Validity | rows passing predicate / non-null | `email >= 0.98` |
| Consistency | rows passing cross-field rule / total | `ship_date >= order_date >= 0.999` |
| Freshness | `now() - max(updated_at)` | `<= 60 minutes` |
| Drift | PSI or KS versus baseline | `PSI <= 0.10` |

One query per table gets most of the evidence in a single scan:

```sql
SELECT
  COUNT(*) AS n,
  AVG((customer_id IS NULL)::int) AS null_rate_customer_id,
  COUNT(DISTINCT order_id)::numeric / COUNT(*) AS key_uniqueness,
  AVG((email !~ '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$')::int)
    FILTER (WHERE email IS NOT NULL) AS invalid_email_rate,
  AVG((ship_date < order_date)::int) AS date_order_violation_rate,
  MAX(updated_at) AS max_updated_at
FROM analytics.orders
WHERE updated_at <= :as_of;
```

Report rates, not just counts, and pair each rate with its denominator. For numeric columns add min, max, mean, p50, p95, p99, and zero/negative counts. For categoricals add top 20 values and the count of distinct values.

### 4. Set thresholds by severity

Classify columns as `critical` (join keys, money, compliance fields), `important` (reporting dimensions), or `monitor` (descriptive fields). Assign thresholds from the consumer impact, not from the observed value. An illustrative policy:

- Critical: completeness and uniqueness at 1.000, freshness within the SLA, zero schema breaks.
- Important: completeness at 0.995 or better, validity at 0.99 or better.
- Monitor: alert only on a change greater than 3 standard deviations from the 30-day baseline.

Store thresholds in version control next to the model or contract so a change is reviewable.

### 5. Establish drift baselines

For numeric features, bucket the baseline into 10 quantile bins and compute the population stability index:

```python
import numpy as np

def psi(expected, actual, bins=10, eps=1e-6):
    edges = np.quantile(expected, np.linspace(0, 1, bins + 1))
    edges[0], edges[-1] = -np.inf, np.inf
    e = np.histogram(expected, edges)[0] / len(expected)
    a = np.histogram(actual, edges)[0] / len(actual)
    e, a = np.clip(e, eps, None), np.clip(a, eps, None)
    return float(np.sum((a - e) * np.log(a / e)))
```

Conventional interpretation: below 0.10 is stable, 0.10 to 0.25 is a moderate shift worth review, above 0.25 is a major shift. Refresh the baseline on a fixed cadence (monthly is common) and after an approved business change. For categoricals use total variation distance or a chi-square test with a minimum expected count of 5.

### 6. Schedule the checks and route failures

Run profiling in two modes: a deep profile on every schema change or backfill, and a lightweight daily check on critical columns only. Emit results to a metrics table with `run_id`, `table`, `column`, `metric`, `value`, `threshold`, `status`. Wire failures to the owning team's alert channel with the failing column, observed value, threshold, and a link to the last passing run.

Typical implementations are dbt tests, Great Expectations checkpoints, Soda checks, or a scheduled SQL job. Whichever you use, keep the threshold definitions outside the tool so they can be reviewed and reused.

### 7. Triage and close findings

Separate defects into producer defects (bad writes, schema drift), pipeline defects (bad join, wrong cast, timezone), and expectation defects (threshold wrong, baseline stale). Route producer defects to the data contract owner. Do not loosen a threshold to make a run pass unless the consumer agrees and the change is recorded. Re-profile after the fix and keep the before/after evidence.

## Validation

- [ ] Key uniqueness equals 1.000 with zero null keys, verified on the full table or a documented sample.
- [ ] Every critical column has completeness, validity, and freshness results with denominators recorded.
- [ ] Thresholds are stored in version control and referenced by the automated check.
- [ ] Drift is computed against a named baseline with a date and row count, not an unnamed previous run.
- [ ] The daily job fails closed: a missing metric or failed query is an error, not a pass.
- [ ] Alert payload includes table, column, metric, value, threshold, and owner.
- [ ] Profiling runtime stays within the agreed window; a 5 percent sample query on a large table should be timed before scheduling.

## Gotchas

- Null is not empty string, `"N/A"`, `0`, or `false`. Count each separately or completeness will look better than it is.
- Default values (`unknown`, `-1`, `1900-01-01`) inflate completeness. Profile value frequency, not only null rate.
- `COUNT(DISTINCT)` ignores nulls, so a key can appear unique while containing nulls.
- A `UNIQUE` constraint allows multiple nulls in PostgreSQL and most engines. Enforce `NOT NULL` separately.
- `TABLESAMPLE SYSTEM` on a small table can return zero rows. Use a full scan below the sampling floor or `TABLESAMPLE BERNOULLI`.
- High-cardinality distinct counts can spill to disk and time out. Use approximate distinct (`approx_count_distinct`, HyperLogLog) for monitoring and exact counts for gates.
- Seasonality looks like drift. Compare the same weekday or month-over-month window before alerting.
- Freshness must use the source's event time or commit time, not the load time, or a delayed upstream looks healthy.
- Schema drift includes type changes, renamed columns, and new enum values, not just added columns.
- A stale baseline hides real drift. Record baseline creation date and refresh it on a schedule.
- Regex validity checks differ by engine (`\d` support, escaping). Test the predicate against known good and bad rows.
- Metrics over a filtered subset are not comparable to full-table metrics. Keep the filter in the metric definition.

## Output contract

```json
{
  "run_id": "profile-2026-11-26-001",
  "table": "analytics.orders",
  "as_of": "2026-11-26T00:00:00Z",
  "sample_rate": 1.0,
  "row_count": 1842231,
  "baseline": {"id": "orders-2026-10", "created_at": "2026-10-01"},
  "columns": [
    {
      "name": "order_id",
      "severity": "critical",
      "completeness": 1.0,
      "uniqueness": 1.0,
      "validity": 1.0,
      "freshness_minutes": 12,
      "psi": 0.03,
      "status": "pass"
    }
  ],
  "findings": [
    {"column": "email", "metric": "validity", "value": 0.971, "threshold": 0.98, "status": "fail"}
  ],
  "owner": "data-platform",
  "recommended_action": "route email validity finding to the checkout producer"
}
```

## Checklist

- [ ] Table, owner, consumers, and update cadence documented.
- [ ] Profiling snapshot and sample rate recorded.
- [ ] Column types and candidate keys confirmed.
- [ ] Completeness, uniqueness, validity, consistency, freshness, and drift measured.
- [ ] Null and sentinel-value policy defined per column.
- [ ] Thresholds assigned by severity and committed to version control.
- [ ] Drift baseline dated and sized.
- [ ] Automated check runs on schedule and fails closed.
- [ ] Findings routed to the correct owner with evidence.
- [ ] Re-profile completed after remediation.

## Related skills

- `data-contract-enforcement` for turning profile findings into producer obligations.
- `warehouse-schema-design` for key and grain decisions that profiling validates.
- `etl-pipeline-generation` for adding data tests and checkpoints to ingestion jobs.
- `feature-store-engineering` for freshness and parity checks on model features.
