---
name: warehouse-schema-design
description: Designs star schemas, grain, keys, partitioning, and clustering for analytical workloads. Use for new marts and warehouse modeling reviews.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: data-ai
---

# Warehouse Schema Design

## Overview

Most warehouse problems are modeling problems wearing a performance costume. Ambiguous grain produces double-counted revenue, missing dimension history breaks point-in-time reporting, and partitioning the wrong column makes every query scan the full table. Design starts with the business process and the exact grain, then chooses keys, dimensions, facts, and physical layout to match the queries that will actually run.

A good schema makes the correct query easy and the incorrect query obvious. It also states its cost model: which filters prune partitions, which joins fan out, and which measures are additive.

## When to use

- Creating a new fact or dimension for a business process.
- Reviewing a mart before dashboards or finance depend on it.
- Consolidating overlapping tables into a conformed model.
- Choosing partition and clustering keys for a large table.
- Adding history tracking to a dimension.
- Migrating a normalize-everything OLTP schema into an analytical mart.

Do not use for operational transaction tables or small (<1 GB) datasets where a plain table and good naming are sufficient.

## Workflow

### 1. State the business process and grain

Write one sentence before any column: "One row per order line per order version" or "One row per account per day." Then test the claim against candidate keys:

```sql
-- Grain check: this must return zero rows
select order_id, line_number, count(*) as n
from staging.order_lines
group by 1, 2
having count(*) > 1;
```

If the grain sentence needs "and sometimes," you have two facts. Split them. Never define grain as "one row per row in the source" without naming the key.

### 2. Choose the modeling pattern

| Pattern | Use when | Cost |
| --- | --- | --- |
| Star schema | BI, stable conformed dimensions, multiple facts | Joins, but simple and fast |
| Wide table (OBT) | One team, one query pattern, repeated denormalization | Duplication, expensive updates |
| Data Vault | Many sources, audit-heavy integration, evolving model | More objects and joins |
| Normalized 3NF | Operational replication, write-heavy | Complex analytical queries |

Default to star for marts. Use OBT when a single dashboard dominates and the source dimensions change slowly. Do not mix patterns within one mart without documenting why.

### 3. Design dimensions with explicit history

Give every dimension a surrogate key, a natural key, and a history policy:

| SCD type | Behavior | Columns |
| --- | --- | --- |
| 1 | Overwrite | current values only |
| 2 | New row per change | `valid_from`, `valid_to`, `is_current`, `row_hash` |
| 3 | Previous value column | `current_value`, `previous_value` |

```sql
create table marts.dim_customer (
    customer_sk   bigint generated always as identity primary key,
    customer_id   varchar(64) not null,
    legal_name    varchar(255) not null,
    segment       varchar(32),
    country_code  char(2),
    valid_from    timestamp not null,
    valid_to      timestamp not null default '9999-12-31 00:00:00',
    is_current    boolean not null default true,
    row_hash      char(64) not null
);

create unique index dim_customer_current_uk
    on marts.dim_customer (customer_id) where is_current;
```

The partial unique index prevents two current rows for one natural key. Close the old row and insert the new one in one transaction.

### 4. Design facts at the declared grain

Classify each fact table:

- Transaction fact: one row per event (`fct_order_line`).
- Periodic snapshot: one row per entity per period (`fct_account_daily`).
- Accumulating snapshot: one row per process instance with milestone timestamps (`fct_loan_application`).

Classify measures as additive, semi-additive, or non-additive. Balances are semi-additive across time: sum across accounts is valid, sum across days is not. Store the measures and document the rule.

```sql
create table marts.fct_order_line (
    order_line_sk  bigint generated always as identity,
    order_id       varchar(64) not null,
    order_ts       timestamp not null,
    date_key       int not null,
    product_sk     bigint not null,
    customer_sk    bigint not null,
    quantity       int not null,
    net_amount     numeric(18,2) not null,
    currency       char(3) not null
)
partition by range (order_ts)
cluster by (customer_sk, product_sk);
```

Use a degenerate dimension (`order_id`) when the business key belongs on the fact but has no dimension attributes. Keep money as decimal plus currency; never sum across currencies without an explicit rate and date.

### 5. Choose keys

- Surrogate keys isolate the warehouse from source key changes and support SCD2.
- Natural keys are required for traceability and idempotent loads.
- Hash keys are acceptable in lakehouse formats; use one stable hash algorithm and document collisions handling (practically negligible for SHA-256).
- Never use nullable columns as join keys. Add a zero or unknown dimension row with `sk = 0` or `-1`.
- Keep date keys as `YYYYMMDD` integers for human-readable partition pruning, and keep the full timestamp on the fact.

### 6. Set physical layout from query patterns

| Engine | Mechanism | Guidance |
| --- | --- | --- |
| BigQuery | `PARTITION BY DATE(ts)`, `CLUSTER BY` | Partition on the dominant date filter; cluster on 1 to 4 high-use columns |
| Snowflake | automatic micro-partitions, `CLUSTER BY` | Cluster only tables that are large and filtered selectively; monitor clustering credits |
| Redshift | `DISTKEY`, `SORTKEY` | Distribute on the largest join key; sort on the dominant range filter |
| Postgres | declarative partitioning, BRIN/B-tree | Partition when a table exceeds roughly 100 GB or needs retention drops |
| Iceberg/Delta | partition spec, Z-order | Partition on low-cardinality date/category, compact small files |

Partitioning pays off when the table is large and most queries filter on the partition column. A 50 GB table queried by `customer_id` will not benefit from daily partitions.

### 7. Validate with real queries and cost

Run the top 10 queries by frequency and by cost against the design. Check:

```sql
explain analyze
select date_trunc('month', order_ts) as month, sum(net_amount)
from marts.fct_order_line
where order_ts >= '2026-01-01' and order_ts < '2026-02-01'
  and customer_sk = 4812
group by 1;
```

Confirm partition pruning in the plan, confirm no unexpected fan-out by comparing row counts before and after each join, and record bytes scanned or credits per query. A design that is elegant but scans 12 months for a 1-day report is not finished.

## Validation

- [ ] Grain sentence exists and the uniqueness test returns zero duplicates.
- [ ] Every dimension has a surrogate key, natural key, and documented SCD policy.
- [ ] At most one current row exists per natural key (enforced by index or test).
- [ ] Every fact measure is classified as additive, semi-additive, or non-additive.
- [ ] Unknown dimension rows exist for every foreign key that can be missing.
- [ ] Partition and cluster keys match the top query filters, verified in the plan.
- [ ] A point-in-time join returns the dimension version valid at the event time.
- [ ] Cost per top query is measured and within the agreed budget.
- [ ] Retention and partition expiry are defined.

## Gotchas

- Joining two fact tables at different grains fans out rows and inflates every measure. Aggregate to a common grain first.
- SCD2 joins that filter only `is_current = true` silently rewrite history. Join on `event_ts >= valid_from and event_ts < valid_to`.
- Missing dimension rows drop facts in an inner join. Create an `unknown` row and use a left join with a coalesced key.
- Summing a daily balance across days overstates the balance. Mark it semi-additive and use the last value per period.
- Partitioning on ingestion time while queries filter event time gives no pruning. Partition on the filter users actually apply.
- Thousands of tiny partitions add metadata overhead. Aim for partitions that hold at least a few hundred MB, or partition monthly for small tables.
- Clustering on a low-cardinality column (status, country) provides little benefit and adds maintenance. Cluster on columns used in selective filters.
- Snowflake clustering consumes credits on reclustering. Test with `SYSTEM$CLUSTERING_INFORMATION` before enabling it broadly.
- Money stored as `float` accumulates rounding errors. Use `numeric` or integer minor units with a documented scale.
- Date keys derived in local time shift facts across days. Derive from UTC and keep the local date only as an attribute.
- Natural keys can be reused after deletion in some source systems. Keep the surrogate key and a source-system validity window.
- Role-playing dimensions (order date, ship date) need separate views or aliases; do not join the same dimension twice without aliasing.

## Output contract

```yaml
design_id: mart-sales-v3
business_process: order fulfillment
grain: one row per order line per order version
pattern: star
facts:
  - name: fct_order_line
    type: transaction
    keys: [order_id, line_number, date_key, product_sk, customer_sk]
    measures:
      quantity: additive
      net_amount: additive
      currency: non-additive
dimensions:
  - name: dim_customer
    scd: 2
    natural_key: customer_id
    surrogate_key: customer_sk
  - name: dim_date
    scd: 0
    natural_key: date_key
physical:
  partition_by: DATE(order_ts)
  cluster_by: [customer_sk, product_sk]
  retention: 36 months
validation:
  grain_duplicates: 0
  unknown_key_rows: true
  top_query_p95_seconds: 4.2
  bytes_scanned_reduction: "78 percent versus unpartitioned"
```

## Checklist

- [ ] Business process and grain written down and tested.
- [ ] Modeling pattern chosen with a stated reason.
- [ ] Conformed dimensions shared across facts.
- [ ] Surrogate and natural keys defined for every dimension.
- [ ] SCD policy documented and enforced with a uniqueness constraint.
- [ ] Fact type and measure additivity documented.
- [ ] Unknown dimension rows created.
- [ ] Partition and cluster keys derived from real query filters.
- [ ] Point-in-time join tested against a known history change.
- [ ] Top queries measured for runtime and scanned bytes.
- [ ] Retention and partition lifecycle defined.
- [ ] Naming and data types consistent across marts.

## Related skills

- `dbt-model-development` for implementing the schema as tested, documented models.
- `database-query-optimization` for execution plan and index tuning after the design is set.
- `data-quality-profiling` for validating grain, keys, and freshness in production.
- `data-contract-enforcement` for keeping upstream schemas aligned with the mart.
