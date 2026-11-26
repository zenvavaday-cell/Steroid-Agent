---
name: dbt-model-development
description: Builds dbt models, tests, documentation, and incremental strategies with clear staging and mart layers. Use for warehouse transformations and analytics engineering.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: data-ai
---

# dbt Model Development

## Overview

dbt projects fail in predictable ways: every model reads raw tables directly, incremental logic silently drops late records, tests exist but never run in CI, and nobody can tell which dashboard depends on a column. A disciplined project keeps a small number of layers, makes dependencies explicit with `ref` and `source`, and treats tests, contracts, and documentation as part of the model rather than an afterthought.

The goal is a DAG a new analyst can read in ten minutes and a change that cannot merge without passing data tests.

## When to use

- Building staging and mart layers on Snowflake, BigQuery, Redshift, Postgres, or Databricks.
- Converting SQL scripts and scheduled queries into a maintained transformation project.
- Adding incremental models for large fact tables.
- Introducing tests, contracts, and documentation to an existing dbt project.
- Reviewing a dbt pull request for layering, materialization, and correctness.
- Migrating a legacy warehouse transformation layer.

Do not use for simple one-table ad hoc analysis; a notebook or a single SQL query is cheaper and clearer.

## Workflow

### 1. Define layers and naming

Use three layers and enforce the dependency direction:

| Layer | Prefix | Reads from | Materialization |
| --- | --- | --- | --- |
| Staging | `stg_` | sources only | view |
| Intermediate | `int_` | staging | view or ephemeral |
| Marts | `fct_`, `dim_`, `mart_` | staging or intermediate | table or incremental |

Staging models do one thing: rename, cast, deduplicate, and standardize a single source. Marts join and aggregate for a business process. Intermediate models exist only to break up complex logic; if a model is not reused, fold it into the mart.

### 2. Declare sources once

```yaml
# models/staging/shopify/_sources.yml
sources:
  - name: shopify
    database: raw
    schema: shopify
    freshness:
      warn_after: {count: 12, period: hour}
      error_after: {count: 24, period: hour}
    loaded_at_field: _extracted_at
    tables:
      - name: orders
        columns:
          - name: order_id
            tests: [not_null, unique]
          - name: updated_at
            tests: [not_null]
```

Source tests run against raw data, so a producer break is caught before it propagates. Add `freshness` only when the load timestamp is trustworthy.

### 3. Build staging models

```sql
-- models/staging/shopify/stg_shopify__orders.sql
with source as (
    select * from {{ source('shopify', 'orders') }}
),

renamed as (
    select
        cast(order_id as string)          as order_id,
        cast(customer_id as string)       as customer_id,
        lower(trim(status))               as order_status,
        cast(total_price as numeric(18, 2)) as order_total,
        upper(trim(currency))             as currency,
        cast(created_at as timestamp)     as created_at_utc,
        cast(updated_at as timestamp)     as updated_at_utc,
        _batch_id,
        _extracted_at
    from source
    where order_id is not null
)

select * from renamed
```

Keep `select *` out of the final CTE in mart models. In staging it is acceptable only before the explicit projection.

### 4. Choose materializations deliberately

| Situation | Materialization | Reason |
| --- | --- | --- |
| Small source-conformed model | view | No storage, always fresh |
| Reused expensive join | table | Pay once per run |
| Large append/update fact | incremental | Bounded scan and write |
| Short-lived helper | ephemeral | No warehouse object |
| Very wide mart | table | Avoid repeated view cost |

Set defaults in `dbt_project.yml`, override per model only when justified with a comment.

### 5. Write correct incremental logic

```sql
{{ config(
    materialized='incremental',
    unique_key='order_id',
    incremental_strategy='merge',
    on_schema_change='append_new_columns',
    cluster_by=['order_date']
) }}

select
    order_id,
    customer_id,
    order_status,
    order_total,
    currency,
    created_at_utc,
    updated_at_utc,
    cast(created_at_utc as date) as order_date
from {{ ref('stg_shopify__orders') }}
{% if is_incremental() %}
where updated_at_utc >= (
    select coalesce(max(updated_at_utc), '1900-01-01') from {{ this }}
) - interval '3 days'
{% endif %}
```

The lookback must exceed the maximum lateness of source updates. Without it, records that arrive after the last maximum are never reprocessed. Use `merge` when the unique key is stable; use `delete+insert` or `insert_overwrite` when partitions are the natural unit and the engine supports it.

### 6. Test at the right level

```yaml
models:
  - name: fct_orders
    description: One row per order, updated when the source order changes.
    config:
      contract: {enforced: true}
    columns:
      - name: order_id
        tests: [not_null, unique]
      - name: customer_id
        tests:
          - not_null
          - relationships:
              to: ref('dim_customers')
              field: customer_id
      - name: order_status
        tests:
          - accepted_values:
              values: ['pending', 'paid', 'shipped', 'cancelled', 'refunded']
```

Add singular tests for business rules, for example that no order ships before it is paid:

```sql
-- tests/assert_ship_after_payment.sql
select order_id
from {{ ref('fct_orders') }}
where shipped_at is not null and shipped_at < paid_at
```

Generic tests cover 80 percent of cases. Use `dbt_utils.unique_combination_of_columns` for composite keys and `dbt_expectations` for range and row-count checks.

### 7. Run and promote with state

```bash
dbt deps
dbt build --select state:modified+ --defer --state ./prod-manifest --fail-fast
dbt test --select tag:critical
dbt docs generate
dbt source freshness
```

`dbt build` runs models and tests in DAG order and stops on the first failure with `--fail-fast`. Use `--defer` with a production manifest so unmodified upstream models resolve to production instead of rebuilding the world in CI. Tag critical models so the fast test suite can run on every pull request and the full suite on merge.

### 8. Document consumers and ownership

Add model descriptions, column descriptions, and `meta.owner`. Declare dashboards and reverse-ETL jobs as exposures so lineage shows who is affected. Enforce contracts on models consumed outside the project; a contract failure should break the build, not the downstream dashboard.

## Validation

- [ ] `dbt build --select state:modified+` passes on the branch.
- [ ] `dbt test --select tag:critical` passes with zero failures and zero errors.
- [ ] Every mart model has a uniqueness test on its declared grain.
- [ ] Every incremental model has a lookback and was tested with a late-arriving row.
- [ ] `dbt source freshness` passes for all sources with freshness configured.
- [ ] `dbt docs generate` succeeds and every mart has an owner and description.
- [ ] A full refresh completes within the agreed window on a clone or staging target.
- [ ] CI writes to a pull-request-specific schema, never to production.

## Gotchas

- `is_incremental()` is false during the first build and during `--full-refresh`. Test both paths, not only the incremental one.
- A lookback of zero minutes loses any record updated after the previous `max(updated_at)`. Use a window larger than observed lateness.
- `on_schema_change` defaults to `ignore`, which silently drops new columns. Set it explicitly and alert on schema changes.
- Duplicate `unique_key` values in the source cause merge errors or nondeterministic rows. Deduplicate upstream and test the key.
- `ref` to a model that is not selected in the run fails. Use `--defer` or select the full ancestry (`+`).
- Tests are not run by `dbt run`. Use `dbt build` or a separate `dbt test` step, or tests will rot.
- Ephemeral models become CTEs and can explode compile size and query cost. Use them only for small, reused logic.
- A view on a view on a view multiplies scan cost. Materialize the expensive middle layer.
- `dbt run` in CI against the production schema overwrites production tables. Set a target schema per developer and per pull request.
- Snapshotting does not replace incremental logic. Snapshots track dimension history; they do not deduplicate facts.
- Timestamps without a timezone make date spines and freshness wrong around DST. Normalize to UTC in staging.
- Pinning a package to a branch makes builds non-reproducible. Pin to a released version range.

## Output contract

```yaml
change_id: dbt-pr-1842
layer_touched: [staging, marts]
models:
  - name: stg_shopify__orders
    materialization: view
    tests_added: [not_null_order_id, unique_order_id]
  - name: fct_orders
    materialization: incremental
    unique_key: order_id
    lookback: 3 days
    tests_added: [relationships_customer_id, accepted_values_order_status]
commands:
  ci: dbt build --select state:modified+ --defer --state ./prod-manifest --fail-fast
  release: dbt build --select tag:critical
results:
  models_built: 2
  tests_passed: 14
  tests_failed: 0
  full_refresh_seconds: 96
docs:
  owner: analytics-engineering
  exposures: [dashboard_orders_daily]
```

## Checklist

- [ ] Layer and prefix conventions followed.
- [ ] Sources declared with tests and freshness where reliable.
- [ ] Staging models rename, cast, and deduplicate without business joins.
- [ ] Materialization chosen per model with a stated reason.
- [ ] Incremental models have a unique key, strategy, and lookback.
- [ ] Grain has a uniqueness test on every mart.
- [ ] Relationships and accepted values tested on critical columns.
- [ ] Contracts enforced on externally consumed models.
- [ ] CI selects modified models plus downstream and defers to production.
- [ ] CI writes to an isolated per-PR schema.
- [ ] Full refresh tested before merge.
- [ ] Owner and downstream exposures documented.

## Related skills

- `warehouse-schema-design` for the grain, keys, and dimensional model behind the marts.
- `data-quality-profiling` for choosing thresholds and drift baselines for tests.
- `etl-pipeline-generation` for the ingestion layer that feeds dbt sources.
- `database-query-optimization` for tuning expensive models and materializations.
