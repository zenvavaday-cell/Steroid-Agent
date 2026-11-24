---
name: database-schema-migration-generation
description: Generates backward-compatible, zero-downtime database migrations using expand-contract, online DDL, batched backfills, and tested rollback plans. Use for adding or changing columns, indexes, constraints, tables, and data types in production databases.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: engineering
---

# Database Schema Migration Generation

## Overview

A migration is a deployment in two dimensions: schema and code. The database change and the application release rarely happen at the same instant. Safe migrations are backward compatible across at least one version, and destructive steps are separated from additive ones.

Use **expand → migrate → contract**:

1. Expand: add the new structure without breaking old code.
2. Migrate: dual-write and backfill.
3. Contract: remove the old structure after no code depends on it.

## When to use

- Adding, renaming, or dropping columns or tables.
- Changing data types or constraints.
- Adding indexes on large tables.
- Backfilling derived or denormalized data.
- Splitting or merging tables.

## Workflow

### 1. Inspect the current schema and workload

```sql
-- PostgreSQL
\d+ table_name
SELECT pg_size_pretty(pg_total_relation_size('table_name'));
SELECT reltuples::bigint AS estimated_rows FROM pg_class WHERE relname = 'table_name';
```

Check table size, write rate, replication lag tolerance, lock timeouts, and whether the table is hot. A migration that takes 200 ms on a laptop can lock a 500-million-row table for minutes.

### 2. Classify the change

| Change | Risk | Strategy |
| --- | --- | --- |
| Add nullable column | Low | Direct, no default rewrite |
| Add column with default | Medium–High | Add nullable, backfill, set default |
| Add index | Medium | `CREATE INDEX CONCURRENTLY` |
| Add NOT NULL | High | Backfill, then validate constraint |
| Rename column | High | Expand with new column, dual-write, contract |
| Change type | High | New column, dual-write, backfill, swap |
| Drop column | High | Stop reads/writes first, then drop |
| Add foreign key | Medium | `NOT VALID`, then `VALIDATE CONSTRAINT` |
| Add enum value | Low–Medium | Append only; avoid reordering |
| Drop table | High | Archive, verify no references, then drop |

### 3. Write the expand migration

PostgreSQL examples:

```sql
-- Add a nullable column without rewriting the table
ALTER TABLE orders ADD COLUMN fulfillment_status text;

-- Build an index without blocking writes
CREATE INDEX CONCURRENTLY idx_orders_fulfillment_status
  ON orders (fulfillment_status);

-- Add a constraint without a long validation scan
ALTER TABLE orders
  ADD CONSTRAINT fk_orders_customer
  FOREIGN KEY (customer_id) REFERENCES customers (id) NOT VALID;

ALTER TABLE orders VALIDATE CONSTRAINT fk_orders_customer;
```

MySQL:

```sql
ALTER TABLE orders
  ADD COLUMN fulfillment_status VARCHAR(32) NULL,
  ALGORITHM=INPLACE, LOCK=NONE;
```

Confirm the engine supports online DDL for the specific operation. Not every `ALGORITHM=INPLACE` is lock-free.

### 4. Dual-write in the application

Deploy code that writes both the old and new columns, and reads the old one. This keeps both representations consistent during the transition.

```python
def save_order(order):
    order.fulfillment_status = order.legacy_status  # mirror
    db.orders.insert(order)
```

Handle failures: if the dual write is not atomic, add a reconciliation job.

### 5. Backfill in batches

```sql
DO $$
DECLARE
  batch_size int := 5000;
  rows_updated int;
BEGIN
  LOOP
    UPDATE orders
    SET fulfillment_status = legacy_status
    WHERE fulfillment_status IS NULL
      AND id IN (
        SELECT id FROM orders
        WHERE fulfillment_status IS NULL
        ORDER BY id
        LIMIT batch_size
        FOR UPDATE SKIP LOCKED
      );
    GET DIAGNOSTICS rows_updated = ROW_COUNT;
    EXIT WHEN rows_updated = 0;
    PERFORM pg_sleep(0.1);
  END LOOP;
END $$;
```

Rules:

- Batch by a stable key, not an offset.
- Sleep between batches to protect replication and I/O.
- Make the backfill idempotent and resumable.
- Monitor lag and lock waits.
- Do not run a single `UPDATE` over the whole table in production.

### 6. Validate and switch reads

- Compare counts and checksums between old and new.
- Run a sample reconciliation query.
- Switch reads to the new column behind a feature flag.
- Keep the old column until the rollback window closes.

### 7. Contract

After no code reads or writes the old structure:

```sql
ALTER TABLE orders DROP COLUMN legacy_status;
DROP INDEX CONCURRENTLY IF EXISTS idx_orders_legacy_status;
```

Dropping is irreversible. Take a backup or archive first, and confirm the retention requirement.

### 8. Write the rollback plan

For each step, state the reverse action and whether it is safe:

| Step | Rollback | Safe? |
| --- | --- | --- |
| Add nullable column | Drop column | Yes, if unused |
| Create index concurrently | Drop index | Yes |
| Backfill | No-op or reverse update | Usually yes |
| Switch reads | Flip flag | Yes |
| Drop old column | Restore from backup | No, data loss |

If a step is irreversible, require explicit approval before running it.

## Gotchas

- Adding a column with a non-null default can rewrite the entire table on older engines. Add nullable, backfill, then set the default.
- `CREATE INDEX CONCURRENTLY` cannot run inside a transaction block. Many migration tools wrap statements in transactions by default.
- A failed concurrent index build leaves an invalid index. Drop and rebuild it.
- `NOT VALID` constraints still apply to new rows; validation is a separate scan.
- Renaming a column breaks old code instantly. Use the expand-contract pattern.
- Long transactions block vacuum and DDL. Keep backfill batches short.
- Replication lag can make a read replica serve stale or missing data during a migration.
- ORM autogeneration may produce destructive changes. Review every generated migration.
- Changing a primary key or partition key is a table rewrite, not an `ALTER`.
- Test on a production-sized snapshot, not an empty database.

## Output contract

```markdown
## Change
<table, column, index, constraint>

## Phases
1. Expand: <SQL>
2. Dual-write: <code change>
3. Backfill: <script, batch size, rate>
4. Validate: <query>
5. Contract: <SQL>

## Lock analysis
<operation, lock type, expected duration>

## Rollback
<step-by-step, irreversible steps flagged>

## Verification
- row counts and checksums
- constraint validation
- application tests
- replication lag

## Approval
<owner, date, maintenance window if any>
```

## Checklist

- [ ] Table size and workload measured.
- [ ] Change classified and phased.
- [ ] Expand migration is backward compatible.
- [ ] Online DDL confirmed for the engine.
- [ ] Backfill batched, idempotent, and monitored.
- [ ] Reads switched behind a flag.
- [ ] Old structure removed only after the rollback window.
- [ ] Rollback plan tested.
- [ ] Migration rehearsed on a production-sized copy.

## Related skills

- `test-driven-verification-loop` for migration tests.
- `ci-cd-failure-diagnosis` when deployment order causes failures.
- `stateful-workflow-checkpointing` for resumable backfills.
