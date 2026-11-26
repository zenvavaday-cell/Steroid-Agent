---
name: feature-store-engineering
description: Defines features, offline/online parity, point-in-time correctness, freshness, and ownership. Use for ML feature pipelines and training-serving consistency.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: data-ai
---

# Feature Store Engineering

## Overview

A feature is a contract between a data producer, a training pipeline, and an online service. The hard problems are rarely the transformations: they are point-in-time correctness at training time, parity between the batch and online values, freshness under load, and knowing who owns a feature when it breaks.

The discipline is to define each feature once, compute it with one implementation, store it in both offline and online stores with explicit timestamps, and verify parity continuously. A model that scores well offline and poorly online is usually a feature pipeline defect, not a modeling defect.

## When to use

- Designing features for a model that will serve online predictions.
- Auditing a training set for label leakage from future data.
- Unifying feature definitions across several models or teams.
- Choosing an offline/online store architecture (Feast, Tecton, Databricks, in-house).
- Adding freshness and training-serving skew monitoring.
- Backfilling features after a logic change.

Do not use for a one-off offline analysis where the model will never serve in production and no feature is reused.

## Workflow

### 1. Write a feature specification

Every feature gets an owner, entity, dtype, description, source, freshness SLO, and PII class:

```yaml
feature: customer_orders_30d
entity: customer_id
dtype: int64
description: Count of non-cancelled orders in the trailing 30 days at event time.
source: analytics.fct_orders
owner: growth-ml
freshness: {offline: 24h, online: 15m}
pii: false
version: 3
tags: [churn, engagement]
```

Names encode the aggregation and window (`orders_count_30d`, `session_duration_p95_7d`). Version the definition when the logic changes; never redefine an existing feature in place, because old training sets and online models will disagree about what the name means.

### 2. Separate offline and online responsibilities

| Store | Purpose | Typical technology | Latency |
| --- | --- | --- | --- |
| Offline | Training, batch scoring, backfills | Warehouse, Iceberg, Parquet | Seconds to minutes |
| Online | Real-time serving | Redis, DynamoDB, Bigtable, Cassandra | Single-digit ms |

The offline store must retain event-time history so training can reconstruct values as of any label timestamp. The online store holds only the latest value per entity key, so it needs a TTL and a defined behavior for missing values. Both are populated from the same transformation logic, not two hand-written implementations.

### 3. Compute with one implementation

Use a batch or streaming job that writes feature values with an event timestamp:

```sql
select
  o.customer_id,
  o.order_ts as event_ts,
  count(*) over (
    partition by o.customer_id
    order by unix_seconds(o.order_ts)
    range between 2592000 preceding and current row
  ) as orders_count_30d
from analytics.fct_orders o
where o.status <> 'cancelled';
```

The window must end at `event_ts`, never at `now()`. For streaming features, the same aggregation is maintained in keyed state and written to the online store. Share the definition (SQL, dbt model, or library) and test that batch and stream outputs match on the same input.

### 4. Build point-in-time correct training sets

Join labels to feature values using the latest feature timestamp at or before the label timestamp:

```sql
select
  l.customer_id,
  l.label_ts,
  l.label,
  f.orders_count_30d
from training.churn_labels l
asof join features.customer_orders_30d f
  on l.customer_id = f.customer_id
 and l.label_ts >= f.event_ts;
```

`ASOF JOIN` is supported in Snowflake and DuckDB; elsewhere use a correlated subquery or a window function with `row_number()` ordered by `event_ts desc`. Never join on date equality alone: if a feature was computed at 00:00 and the label is at 18:00, the value is valid, but a feature computed at 23:00 is from the future.

Test the join with a synthetic entity that has values at `t-48h`, `t-1h`, and `t+1h`; the training row must receive the `t-1h` value.

### 5. Serve with explicit freshness and fallback

At serving time, fetch by entity key from the online store and attach `feature_ts` and `feature_version` to the request log. Define behavior for missing or stale values before launch:

- Missing: use a documented default, or abstain from scoring if the feature is required.
- Stale beyond SLO: use a fallback model or a degraded score, and emit a metric.
- Type mismatch: fail closed and alert; do not coerce silently.

Record the feature values used for each prediction so offline analysis can reproduce the decision.

### 6. Materialize and verify parity

With Feast, the typical flow is:

```bash
feast apply
feast materialize-incremental 2026-11-26T00:00:00Z
feast feature-services describe churn_v3
```

On a schedule, sample entities that received a prediction, fetch the online values, and compare them to the offline values as of the same timestamp. Alert when the mismatch rate exceeds 0.1 percent, when null rates differ by more than 1 percentage point, or when mean values diverge beyond a relative 5 percent. Log parity results with the feature version and store snapshot.

### 7. Monitor freshness, drift, and ownership

Track per feature: online freshness lag (now minus `feature_ts`), null rate, value distribution, and coverage (fraction of requests with a non-default value). Alert on freshness SLO breach and on PSI above 0.25 versus the training distribution. Each feature has an owner and a deprecation date. Deprecate by marking the version inactive, removing consumers, then deleting storage after the retention window.

### 8. Backfill and roll back safely

Backfills write a new feature version into a separate table, validate it against the current version, then swap the reader. Never overwrite the version used by the live model. Keep the prior online snapshot for at least one model rollback window. For a bad deployment, point serving back to the previous version and replay the interval from the offline store.

## Validation

- [ ] Feature spec exists with owner, SLO, dtype, and PII class.
- [ ] Point-in-time test with past, near, and future feature rows passes.
- [ ] Training set contains no feature timestamp later than the label timestamp.
- [ ] Online and offline parity mismatch is below 0.1 percent on a 1,000-entity sample.
- [ ] Online freshness p95 is within the SLO for 24 hours.
- [ ] Missing-feature behavior is tested and produces the documented fallback.
- [ ] Feature version is recorded in prediction logs.
- [ ] Backfill validated before the reader swap and rollback tested.

## Gotchas

- Computing a rolling window with `now()` instead of the label time leaks future data and inflates offline metrics.
- Joining features on date equality can select a value produced after the label. Use an as-of join with `event_ts <= label_ts`.
- Event time, ingestion time, and processing time are different. A feature keyed on ingestion time can include events that occurred after the label.
- Window boundaries must be identical in batch and stream (`>= t-30d` versus `> t-30d` changes counts at the edge).
- Online stores evict by TTL. A 7-day TTL breaks a feature that is refreshed every 14 days.
- Defaults in the online store mask missing data. Track coverage separately from null rate.
- Entity key types drift (`"123"` versus `123`, leading zeros). Normalize at the producer and validate at the store.
- Two code paths for batch and streaming inevitably diverge. Share the transformation or run nightly parity tests.
- Backfilling in place changes the training data behind an existing model. Write a new version.
- Label timestamps at day granularity hide intra-day leakage. Prefer the exact event time.
- PII in feature values propagates to logs and online caches. Classify and redact at the store boundary.
- A feature with no owner becomes stale silently. Require ownership at registration and review quarterly.

## Output contract

```yaml
feature_view: customer_orders_30d
version: 3
entity: customer_id
dtype: int64
owner: growth-ml
offline:
  table: features.customer_orders_30d
  partition: event_date
  retention_days: 730
online:
  store: redis
  ttl_days: 30
  freshness_slo_minutes: 15
training:
  join: asof
  label_table: training.churn_labels
  leakage_check: passed
parity:
  sample_size: 1000
  mismatch_rate: 0.0004
  checked_at: "2026-11-26T06:00:00Z"
monitoring:
  freshness_alert_minutes: 30
  psi_threshold: 0.25
  null_rate_delta_threshold: 0.01
```

## Checklist

- [ ] Feature spec registered with owner, dtype, SLO, and PII class.
- [ ] One transformation implementation feeds offline and online.
- [ ] Feature values carry event timestamps.
- [ ] Training joins are as-of and tested with future rows.
- [ ] No feature timestamp exceeds its label timestamp.
- [ ] Missing and stale value behavior defined and tested.
- [ ] Online TTL is longer than the refresh interval.
- [ ] Parity check scheduled with thresholds and alerting.
- [ ] Freshness and drift dashboards exist per feature.
- [ ] Prediction logs record feature version and values.
- [ ] Backfill writes a new version and rollback is tested.
- [ ] Deprecation path and retention defined.

## Related skills

- `streaming-pipeline-design` for real-time feature computation and late-event handling.
- `ml-experiment-tracking` for linking feature versions to training runs.
- `data-quality-profiling` for freshness, null, and drift thresholds.
- `model-evaluation-benchmarking` for measuring the impact of feature changes.
