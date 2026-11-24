---
name: schema-enforced-json-extraction
description: Extracts structured records from unstructured text, PDFs, emails, and transcripts into JSON validated against an explicit schema, with repair loops, cross-field checks, and field-level provenance. Use when downstream code needs reliable JSON, or when malformed or hallucinated fields are unacceptable.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: agentic
---

# Schema-Enforced JSON Extraction

## Overview

Treat the schema as the contract. The model proposes values; the validator decides whether they are acceptable. Never return unvalidated JSON, and never silently coerce a value to make it fit.

The output is a validated record plus provenance and warnings, not just a JSON blob.

## When to use

- Extracting invoices, contracts, tickets, resumes, or clinical notes.
- Converting emails or transcripts into structured records.
- Batch extraction where one bad record breaks a pipeline.
- Any task where a field must be traceable to the source.

Do not use for open-ended summarization or when the schema is unknown. Define the schema first.

## Core rules

1. **Schema first.** Write the schema before the prompt.
2. **Null is not missing.** Use `null` for "known to be absent" and omit only when the schema allows it.
3. **No coercion.** `"12"` is not `12` unless the schema says string.
4. **Provenance per field.** Record the source span or page for each extracted value.
5. **Bounded repair.** At most two repair attempts, then fail loudly.
6. **Semantic validation.** Types are necessary, not sufficient. Check totals, dates, and cross-field logic.
7. **Idempotence.** The same input and schema version produce the same output.

## Workflow

### 1. Define the schema

```python
from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from enum import Enum

class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"

class LineItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    description: str = Field(min_length=1, max_length=500)
    quantity: float = Field(gt=0)
    unit_price_cents: int = Field(ge=0)
    amount_cents: int = Field(ge=0)

class Invoice(BaseModel):
    model_config = ConfigDict(extra="forbid")
    invoice_number: str = Field(min_length=1)
    issue_date: date
    due_date: date | None = None
    currency: Currency
    vendor_name: str
    total_cents: int = Field(ge=0)
    line_items: list[LineItem]
```

Store money as integer minor units with an explicit currency. Use ISO 8601 dates. Use enums with an explicit `unknown` member when the domain requires it.

### 2. Compile the extraction prompt

Include:

- The JSON schema or a compact description.
- Field definitions and allowed values.
- Rules for null and missing.
- Two or three examples, including a hard case.
- The instruction to return only JSON.
- The source text with stable markers.

Keep the schema and the prompt in version control together.

### 3. Call the model

Use structured output or constrained decoding when the provider supports it:

```python
response = client.responses.create(
    model="extract-model",
    input=[{"role": "user", "content": prompt}],
    text={"format": {"type": "json_schema", "name": "invoice", "schema": Invoice.model_json_schema()}},
)
raw = response.output_text
```

Constrained decoding prevents syntax errors but not semantic errors. Validation is still required.

### 4. Parse defensively

```python
import json
import re

def parse_json(raw):
    text = raw.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object found")
    return json.loads(text[start:end + 1])
```

Do not use a greedy regex across multiple records. Parse one object at a time or require a top-level array.

### 5. Validate and repair

```python
from pydantic import ValidationError

def extract_with_repair(text, max_repairs=2):
    messages = [{"role": "user", "content": build_prompt(text)}]
    for attempt in range(max_repairs + 1):
        raw = call_model(messages)
        try:
            data = parse_json(raw)
            invoice = Invoice.model_validate(data)
            return invoice
        except (ValueError, ValidationError) as exc:
            if attempt == max_repairs:
                raise
            messages.append({"role": "assistant", "content": raw})
            messages.append({
                "role": "user",
                "content": f"Validation failed:\n{exc}\nReturn corrected JSON only.",
            })
```

Send the exact validation error, not a generic "try again." Preserve the original output for audit.

### 6. Run semantic checks

```python
def check_invoice(inv):
    errors = []
    computed = sum(item.amount_cents for item in inv.line_items)
    if computed != inv.total_cents:
        errors.append(f"line total {computed} != invoice total {inv.total_cents}")
    for item in inv.line_items:
        expected = round(item.quantity * item.unit_price_cents)
        if abs(expected - item.amount_cents) > 1:
            errors.append(f"line math mismatch: {item.description}")
    if inv.due_date and inv.due_date < inv.issue_date:
        errors.append("due date before issue date")
    return errors
```

Add domain checks: tax rates, duplicate line items, date ranges, referential integrity, and totals by category.

### 7. Attach provenance

```json
{
  "data": {"invoice_number": "INV-104", "total_cents": 125000},
  "provenance": {
    "invoice_number": {"page": 1, "text": "Invoice No. INV-104"},
    "total_cents": {"page": 2, "text": "Total due: $1,250.00"}
  },
  "schema_version": "invoice.v3",
  "warnings": []
}
```

If a field cannot be located in the source, mark it `null` and add a warning. Do not invent a span.

## Gotchas

- Models add markdown fences, comments, or trailing commas. Parse defensively.
- Constrained decoding can still produce valid-but-wrong values. Validate semantics.
- A missing required field may be a truncation, not an absence. Check the input length.
- Number/string coercion hides errors. Reject wrong types.
- Dates may be ambiguous (`03/04/2026`). Require ISO format or resolve with locale evidence.
- Currency symbols are not currency codes. Normalize with the source context.
- Duplicate records are common in multi-page documents. Deduplicate by a stable key.
- Enum hallucination is common. Include an `unknown` option or fail.
- Long documents exceed context. Chunk by section and merge with provenance.
- A repair loop can converge on a plausible fabrication. Cap attempts and escalate.

## Output contract

```json
{
  "status": "valid",
  "data": {},
  "provenance": {},
  "schema_version": "invoice.v3",
  "warnings": [],
  "repair_attempts": 0,
  "model": "extract-model",
  "input_hash": "sha256:..."
}
```

On failure:

```json
{
  "status": "failed",
  "error": "validation",
  "details": ["total_cents: line sum mismatch"],
  "raw_output": "...",
  "schema_version": "invoice.v3"
}
```

## Checklist

- [ ] Schema defined with types, constraints, and enums.
- [ ] Prompt includes rules and examples.
- [ ] Structured output or constrained decoding used when available.
- [ ] Parser handles fences and surrounding text.
- [ ] Validation errors fed back verbatim.
- [ ] Repair attempts capped.
- [ ] Semantic checks run.
- [ ] Provenance recorded per field.
- [ ] Failure path returns an explicit error, not partial JSON.

## Related skills

- `confidence-threshold-output-gating` for routing low-confidence records.
- `cross-system-data-normalization` for mapping extracted fields to a canonical model.
- `human-in-the-loop-escalation` for repeated validation failures.
