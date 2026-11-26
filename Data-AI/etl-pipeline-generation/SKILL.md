---
name: etl-pipeline-generation
description: Generates idempotent extract-transform-load jobs with retries, lineage, checkpoints, and data tests. Use for ingesting APIs, files, and databases.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: data-ai
---

# ETL Pipeline Generation

## Overview

A pipeline is not finished when the first run succeeds. It is finished when a rerun after a crash produces the same target state, a late record is not lost, a bad batch is quarantined instead of half-committed, and every row can be traced to the extraction that produced it.

The reliable pattern is immutable landing plus a deterministic merge on a natural key, with the extraction watermark advanced only after the target commit. Retries then become safe by construction rather than by luck.

## When to use

- Ingesting a REST API, paginated export, CSV drop, or database replica.
- Replacing a cron script that appends without deduplication.
- Backfilling history after a schema or logic fix.
- Moving data into a warehouse or lakehouse for analytics or ML.
- Adding observability and failure recovery to an existing job.
- Building a reusable ingestion template for multiple sources.

Do not use when the target requires sub-second latency or per-event ordering; use a streaming design instead.

## Workflow

### 1. Write the source-to-target contract

Before code, pin down: source endpoint or path, target table, grain (one row per what), primary key, incremental cursor, lookback window, extraction window, SLA, owner, and PII classification. Example:

```yaml
pipeline: shopify-orders
source: {type: api, base_url: "https://shop.example.com/admin/api/2024-10", entity: orders}
target: raw.shopify_orders
grain: one row per order_id
key: [order_id]
cursor: updated_at
lookback: 24h
schedule: "0 */2 * * *"
sla: {max_lag_minutes: 150, max_runtime_minutes: 40}
```

If the source has no reliable cursor, plan a full snapshot plus hash comparison instead of pretending incremental works.

### 2. Extract with bounded retries and pagination

Retry only transient failures (HTTP 429, 5xx, connection reset), never 400 or 401. Use exponential backoff with jitter, honor `Retry-After`, and cap attempts:

```python
import random, time, requests

def get_json(session, url, params, attempts=5):
    for attempt in range(attempts):
        resp = session.get(url, params=params, timeout=30)
        if resp.status_code == 429 or 500 <= resp.status_code < 600:
            if attempt == attempts - 1:
                resp.raise_for_status()
            delay = min(2 ** attempt, 30) + random.uniform(0, 1)
            time.sleep(float(resp.headers.get("Retry-After", delay)))
            continue
        resp.raise_for_status()
        return resp.json()
```

Paginate on a stable sort (cursor plus ID tiebreaker), not on page number alone, or inserts during the run will duplicate or skip rows. Persist page tokens so a failed run can resume from the last committed page.

### 3. Land raw data immutably

Write each batch to a new object with extraction metadata. Never mutate raw files in place.

```text
s3://landing/shopify/orders/dt=2026-11-26/batch=20261126T0200Z-7f3a/part-0001.parquet
```

Every landed row carries `_batch_id`, `_extracted_at`, `_source_url`, `_row_hash` (SHA-256 of the canonical JSON), and `_schema_version`. Landing twice is harmless because the path includes the batch ID; consumers read the latest complete batch under a manifest.

### 4. Validate before transforming

Run cheap checks on the landed batch:

```sql
SELECT
  COUNT(*) AS rows,
  COUNT(DISTINCT order_id) AS distinct_keys,
  COUNT(*) FILTER (WHERE order_id IS NULL) AS null_keys,
  MIN(updated_at) AS min_cursor,
  MAX(updated_at) AS max_cursor
FROM landing.shopify_orders
WHERE _batch_id = :batch_id;
```

Fail the batch when keys are null or duplicated, the row count is zero, the count is below 50 percent of the trailing 7-run median, or required columns are missing. Write the batch and check results to an audit table before any merge.

### 5. Transform deterministically

Keep business logic in SQL or versioned Python, not in orchestration callbacks. Deduplicate within the batch by keeping the newest record per key:

```sql
CREATE OR REPLACE TEMP TABLE deduped AS
SELECT * EXCEPT (rn)
FROM (
  SELECT s.*,
         ROW_NUMBER() OVER (
           PARTITION BY order_id
           ORDER BY updated_at DESC, _extracted_at DESC, _row_hash
         ) AS rn
  FROM landing.shopify_orders s
  WHERE _batch_id = :batch_id
) WHERE rn = 1;
```

Tie-break on the row hash so equal timestamps still produce a deterministic winner. Cast explicitly, convert timestamps to UTC, and fail on unknown enum values rather than dropping them silently.

### 6. Merge idempotently

Use `MERGE` with a key and a change predicate. Late records must be allowed to win when they are newer than the stored version:

```sql
MERGE INTO analytics.orders AS t
USING deduped AS s
ON t.order_id = s.order_id
WHEN MATCHED AND s.updated_at > t.updated_at THEN UPDATE SET
  status = s.status,
  total_amount = s.total_amount,
  currency = s.currency,
  updated_at = s.updated_at,
  _batch_id = s._batch_id
WHEN NOT MATCHED THEN INSERT (
  order_id, status, total_amount, currency, updated_at, _batch_id
) VALUES (
  s.order_id, s.status, s.total_amount, s.currency, s.updated_at, s._batch_id
);
```

If the engine has no `MERGE`, use `DELETE` plus `INSERT` inside one transaction on the affected key range, or an upsert with a unique index. Guarantee that the source side has exactly one row per key or `MERGE` will raise a nondeterministic update error.

### 7. Checkpoint only after commit

Store the watermark and batch status in a control table, updated in the same transaction as the target when possible:

```sql
UPDATE control.pipeline_state
SET high_watermark = :max_cursor,
    last_batch_id = :batch_id,
    last_success_at = now()
WHERE pipeline = 'shopify-orders' AND :max_cursor > high_watermark;
```

If the target and control store cannot share a transaction, make the target merge idempotent and re-run the batch after a crash. Record failed batches in a dead-letter table with the error class and a pointer to the landed object. Never advance the watermark when the batch failed.

### 8. Emit lineage and tests

Emit an OpenLineage event or write a manifest with input datasets, output dataset, batch ID, row counts, and code version. Add tests at three levels: source schema (types and required fields), transformation (uniqueness, not null, accepted values, referential integrity), and reconciliation (target row count equals prior count plus inserts minus deletes). Reconcile monetary totals after currency handling.

## Validation

- [ ] Run the job twice on the same batch: target row count and checksums are identical.
- [ ] Kill the job after landing but before commit, rerun, and confirm no duplicates.
- [ ] Insert a record with an older `updated_at` after the watermark and confirm the lookback captures it.
- [ ] Submit a batch with a null key and confirm it lands in quarantine, not the target.
- [ ] Confirm the watermark does not advance on a failed batch.
- [ ] Verify lineage contains input and output dataset names and the batch ID.
- [ ] Confirm secrets come from the environment or secret manager and never appear in logs.

## Gotchas

- `updated_at` is not monotonic. Clock skew and backdated edits require a lookback window, commonly 1 to 24 hours, plus a periodic full reconcile.
- Advancing the watermark before the commit loses data on crash. Commit first, then checkpoint.
- Retried POST requests can create duplicate records unless the API supports an idempotency key. Use `Idempotency-Key` where offered.
- Page-number pagination shifts when rows are inserted. Use keyset pagination on `(cursor, id)`.
- `MERGE` fails or updates unpredictably when the source has duplicate keys. Deduplicate first and assert one row per key.
- Joining on nullable keys silently drops rows. Use `IS NOT DISTINCT FROM` only when null equality is truly intended.
- Soft deletes are invisible to incremental extracts unless the source exposes `deleted_at` or a deletion feed.
- Schema drift (new column, renamed field, changed type) breaks positional CSV parsing. Read by name and validate against a registered schema.
- Timezone-naive timestamps make the watermark ambiguous around DST. Store UTC and reject naive values.
- A zero-row batch is often an upstream auth failure, not an empty dataset. Fail on zero unless the source documents empty windows.
- Large single transactions hold locks and blow the rollback log. Merge in key-range chunks with a bounded batch size.
- Logging full request bodies leaks PII and tokens. Log identifiers, counts, and hashes only.

## Output contract

```json
{
  "run_id": "shopify-orders-20261126T0200Z-7f3a",
  "pipeline": "shopify-orders",
  "status": "success",
  "batch_id": "20261126T0200Z-7f3a",
  "source": {"type": "api", "entity": "orders", "window": ["2026-11-25T02:00:00Z", "2026-11-26T02:00:00Z"]},
  "landing_path": "s3://landing/shopify/orders/dt=2026-11-26/batch=20261126T0200Z-7f3a/",
  "rows_extracted": 8421,
  "rows_written": 8390,
  "rows_rejected": 31,
  "rejected_path": "s3://landing/_quarantine/shopify-orders/20261126T0200Z-7f3a/",
  "high_watermark": "2026-11-26T01:58:44Z",
  "duration_seconds": 412,
  "tests": {"passed": 14, "failed": 0},
  "lineage_event": "openlineage/shopify-orders/20261126T0200Z-7f3a.json"
}
```

## Checklist

- [ ] Grain, key, cursor, lookback, SLA, and owner documented.
- [ ] Extraction retries only transient errors with capped backoff.
- [ ] Pagination is keyset-based and resumable.
- [ ] Raw batch landed immutably with extraction metadata and row hash.
- [ ] Pre-merge validation checks keys, volume, schema, and required fields.
- [ ] Transformation deduplicates deterministically.
- [ ] Merge is idempotent and handles late-arriving updates.
- [ ] Watermark advances only after a successful commit.
- [ ] Rejected rows quarantined with a reason and replay path.
- [ ] Lineage emitted and reconciliation passed.
- [ ] Secrets sourced from a secret manager and excluded from logs.
- [ ] Rerun test executed on the same batch with identical results.

## Related skills

- `data-quality-profiling` for defining the thresholds used in pre-merge validation.
- `data-contract-enforcement` for validating producer schemas at the landing boundary.
- `warehouse-schema-design` for target keys, grain, and partitioning.
- `stateful-workflow-checkpointing` for resumable orchestration beyond a single job.
