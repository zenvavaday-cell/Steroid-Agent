---
name: cross-system-data-normalization
description: Maps records from multiple systems into one canonical schema, normalizing units, currencies, timezones, identifiers, enums, and null semantics with lineage and conflict resolution. Use for data integration, migrations, analytics pipelines, and reconciling vendor exports.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: agentic
---

# Cross-System Data Normalization

## Overview

Every system has its own conventions: dates in local time, money in cents or dollars, identifiers that look alike but mean different things, and booleans encoded as `Y`, `1`, `true`, or `active`. Normalization is the translation layer that makes records comparable without losing meaning.

The output is a canonical record plus lineage, not a merged table that silently picks a winner.

## When to use

- Combining data from CRM, ERP, billing, and support systems.
- Migrating between platforms.
- Building a warehouse or analytics layer.
- Reconciling vendor exports.
- Matching entities across systems.

## Workflow

### 1. Profile each source

For every field, capture:

- Name, type, and example values.
- Null rate and null meaning.
- Units, currency, timezone, and encoding.
- Enum values and their frequencies.
- Identifier format and uniqueness.
- Update cadence and known quality issues.

Profiling prevents assumptions. A column named `amount` may be net, gross, or tax-inclusive.

### 2. Define the canonical schema

```json
{
  "entity": "customer",
  "fields": {
    "customer_id": {"type": "string", "required": true, "stable": true},
    "legal_name": {"type": "string", "required": true},
    "country": {"type": "string", "format": "ISO-3166-1 alpha-2"},
    "created_at": {"type": "string", "format": "date-time UTC"},
    "annual_revenue": {"type": "decimal", "unit": "currency", "currency_field": "currency"},
    "currency": {"type": "string", "format": "ISO-4217"},
    "status": {"type": "enum", "values": ["active", "inactive", "churned", "unknown"]}
  }
}
```

Rules:

- Timestamps are UTC ISO 8601 with an offset or `Z`.
- Money is a decimal amount plus a currency code. Never a float.
- Units are explicit in the field name or metadata.
- Enums have a controlled vocabulary and an `unknown` value.
- Null means unknown. Zero means zero. Do not conflate them.
- Identifiers are strings unless arithmetic is meaningful.

### 3. Write a mapping per source

```json
{
  "source": "crm",
  "entity": "customer",
  "mappings": [
    {"target": "customer_id", "source": "id", "transform": "string"},
    {"target": "legal_name", "source": "company_name", "transform": "trim"},
    {"target": "country", "source": "country_code", "transform": "iso3166_alpha2"},
    {"target": "created_at", "source": "created", "transform": "to_utc", "source_timezone": "America/New_York"},
    {"target": "annual_revenue", "source": "revenue_cents", "transform": "cents_to_decimal"},
    {"target": "currency", "source": "currency", "transform": "iso4217"}
  ]
}
```

Keep the mapping declarative and versioned. A code-only mapping is hard to audit.

### 4. Transform with explicit semantics

```python
from decimal import Decimal
from datetime import datetime
from zoneinfo import ZoneInfo

def cents_to_decimal(value):
    return (Decimal(value) / Decimal(100)).quantize(Decimal("0.01"))

def to_utc(value, source_timezone):
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo(source_timezone))
    return dt.astimezone(ZoneInfo("UTC")).isoformat().replace("+00:00", "Z")

def normalize_country(value):
    mapping = {"US": "US", "USA": "US", "UNITED STATES": "US", "GB": "GB", "UK": "GB"}
    return mapping.get(value.strip().upper(), "UNKNOWN")
```

Use `Decimal`, not `float`, for money. Use a real timezone database, not a fixed offset.

### 5. Resolve identifiers

- Prefer a stable, system-independent key.
- Build a crosswalk table: `canonical_id`, `source_system`, `source_id`, `match_method`, `confidence`.
- Exact matches on a verified identifier are strongest.
- Fuzzy matches need a threshold and human review for high-impact merges.
- Never merge entities on name alone.
- Keep the source IDs after merging for traceability.

### 6. Resolve conflicts

When two sources disagree:

| Rule | Example |
| --- | --- |
| Source of truth per field | Legal name from the contract system |
| Recency | Latest verified address |
| Completeness | Prefer a non-null value |
| Confidence | Higher-confidence match wins |
| Manual review | High-value or high-risk conflicts |

Record the rule and the losing value. Do not silently overwrite.

### 7. Validate

- Required fields present.
- Types and formats valid.
- Enums in the controlled set.
- Referential integrity across entities.
- Row counts reconcile with source counts minus documented exclusions.
- Totals reconcile after currency conversion.
- No duplicate canonical IDs.
- Lineage present for every record.

### 8. Load idempotently

Use a deterministic canonical key and an upsert. Re-running the pipeline should not duplicate records. Version the mapping and keep the source snapshot hash.

## Gotchas

- Naive timestamps are ambiguous. Require a source timezone or reject.
- Daylight-saving transitions create missing and repeated local times. Convert with a tz database.
- Currency minor units differ: JPY has zero decimals, KWD has three. Do not assume two.
- Unit names collide: US ton versus metric tonne, gallon versus imperial gallon.
- Decimal commas and thousands separators vary by locale. Parse with a locale-aware function.
- `null`, empty string, `"N/A"`, `0`, and `false` are different. Preserve the distinction.
- Identifiers can be reused or recycled. Check uniqueness and stability.
- Fuzzy entity resolution produces false merges that are hard to undo. Keep the crosswalk.
- Boolean encodings vary: `Y/N`, `1/0`, `true/false`, `active/inactive`.
- Schema drift: a new enum value or column can break a strict mapping. Alert on unknown values.
- Timezone conversion can change the business date. Decide whether to store local date and UTC timestamp separately.

## Output contract

```json
{
  "run_id": "norm-2026-11-24-001",
  "sources": ["crm", "erp", "billing"],
  "canonical_schema_version": "customer.v4",
  "records_in": {"crm": 12000, "erp": 11800, "billing": 12100},
  "records_out": 12450,
  "rejected": [{"source": "crm", "id": "C-991", "reason": "missing country"}],
  "conflicts": [{"entity": "C-104", "field": "legal_name", "values": ["Acme Inc", "Acme LLC"], "rule": "contract_system", "resolved": "Acme LLC"}],
  "crosswalk": "crosswalk/customer.parquet",
  "lineage": "lineage/norm-2026-11-24-001.json"
}
```

## Checklist

- [ ] Every source profiled.
- [ ] Canonical schema versioned with explicit units and formats.
- [ ] Declarative mapping per source.
- [ ] Money as decimal plus currency.
- [ ] Timestamps normalized to UTC with source timezone.
- [ ] Identifier crosswalk with match method and confidence.
- [ ] Conflict rules documented and applied.
- [ ] Validation and reconciliation passed.
- [ ] Load is idempotent and lineage retained.

## Related skills

- `schema-enforced-json-extraction` for the extraction layer.
- `automated-ledger-reconciliation` for financial matching.
- `stateful-workflow-checkpointing` for resumable pipelines.
