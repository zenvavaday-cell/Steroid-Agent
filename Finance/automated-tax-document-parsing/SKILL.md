---
name: automated-tax-document-parsing
description: Classifies and extracts fields from W-2, 1099, 1040, K-1, 1098, and related tax documents, validates arithmetic and tax-year consistency, masks sensitive identifiers, and routes low-confidence fields to review. Use for tax preparation, document intake, lender income verification, and accounting automation.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: finance
---

# Automated Tax Document Parsing

## Overview

Tax documents are structured forms with strict field positions, box numbers, and arithmetic relationships. Extraction must preserve the box, the tax year, the form variant, and the correction status. A value without its box is unusable.

Treat every document as sensitive. Mask identifiers in logs and model context; store raw documents only in approved locations.

## When to use

- Intake for tax return preparation.
- Income verification for lending or renting.
- Bookkeeping reconciliation of 1099s and W-2s.
- Extracting K-1 data for partnership investors.
- Auditing prior-year returns.

## Supported documents

| Form | Key fields |
| --- | --- |
| W-2 | Boxes 1–20, employer EIN, employee SSN, tax year |
| 1099-NEC | Box 1 nonemployee compensation, payer TIN |
| 1099-MISC | Boxes 1–10, rents, royalties, other income |
| 1099-INT / DIV | Interest, dividends, withholding |
| 1099-B | Proceeds, basis, gain/loss, covered status |
| 1040 | Filing status, income lines, AGI, tax, payments |
| K-1 (1065/1120-S) | Partner/shareholder share of income, distributions |
| 1098 | Mortgage interest, points, property tax |

## Workflow

### 1. Classify the document

Use the form title, tax year, and layout. Handle:

- Corrected forms (W-2c, corrected 1099).
- State versus federal versions.
- Multi-page returns with schedules.
- Scanned images, photos, and PDFs with embedded text.

If classification confidence is low, stop and route to human review.

### 2. Extract with layout awareness

For text PDFs, use the embedded text layer and coordinates. For scans, OCR with layout preservation.

```python
from decimal import Decimal

from pydantic import BaseModel, Field

class W2(BaseModel):
    tax_year: int = Field(ge=2000, le=2100)
    employee_ssn_last4: str = Field(pattern=r"^\d{4}$")
    employer_ein: str = Field(pattern=r"^\d{2}-\d{7}$")
    box1_wages: Decimal = Field(ge=0)
    box2_federal_withholding: Decimal = Field(ge=0)
    box3_social_security_wages: Decimal = Field(ge=0)
    box4_social_security_tax: Decimal = Field(ge=0)
    box5_medicare_wages: Decimal = Field(ge=0)
    box6_medicare_tax: Decimal = Field(ge=0)
    corrected: bool = False
```

Keep the raw value and the normalized value. Preserve leading zeros and box labels.

### 3. Validate each document

| Check | Rule |
| --- | --- |
| Tax year | Matches the expected filing year |
| EIN/TIN | Correct format; check digit where applicable |
| SSN | Mask to last four in output and logs |
| Arithmetic | Box 3 ≥ Box 1; Box 5 ≥ Box 1; tax boxes consistent with wages |
| Totals | Sum of line items equals the stated total |
| Correction | Corrected form supersedes the original for the same year |
| Duplicates | Same form, year, and issuer is not counted twice |

### 4. Cross-document reconciliation

- W-2 wages should reconcile to the return's wage line.
- 1099 totals should reconcile to Schedule C or the relevant income line.
- Withholding totals should reconcile to the payments section.
- K-1 ordinary income should reconcile to the partnership return.
- Mortgage interest should reconcile to the 1098.

Flag differences; do not silently choose one value.

### 5. Mask and store

- Mask SSN, ITIN, and account numbers in logs, prompts, and output.
- Encrypt documents at rest.
- Restrict access by role.
- Record who viewed or exported each document.
- Delete temporary OCR files.

### 6. Route low-confidence fields

A field goes to review when:

- OCR confidence is below threshold.
- The value fails a validation check.
- The form is handwritten.
- The box is ambiguous or the layout is nonstandard.
- Two documents conflict.

Never guess a digit in an identifier or a dollar amount.

## Gotchas

- OCR confuses 0/O, 1/l/I, 5/S, 8/B. Validate identifiers and amounts against arithmetic.
- Tax year is not the processing year. A form received in 2026 may be for 2025.
- Corrected forms are common. The latest corrected version wins, but keep the original for audit.
- State forms use different box layouts and may include local taxes.
- K-1s arrive late and may be amended. Track the version.
- Truncated SSNs on copies are not full SSNs. Do not reconstruct them.
- Cents versus dollars and comma versus decimal separators cause order-of-magnitude errors.
- Multi-page returns contain schedules that change the meaning of a line. Extract the full return context.

## Output contract

```json
{
  "document_id": "DOC-2026-00123",
  "form": "W-2",
  "tax_year": 2025,
  "issuer": {"name": "Example Inc", "ein": "12-3456789"},
  "recipient": {"name": "Jane Doe", "ssn_last4": "6789"},
  "fields": {
    "box1_wages": {"raw": "85,000.00", "value": 85000.00, "confidence": 0.99},
    "box2_federal_withholding": {"raw": "9,120.00", "value": 9120.00, "confidence": 0.98}
  },
  "validations": {"arithmetic": "pass", "tax_year": "pass", "duplicate": "none"},
  "review_required": false,
  "source": "upload/w2_2025.pdf#page=1"
}
```

## Checklist

- [ ] Document classified with form and tax year.
- [ ] Box-level extraction with raw and normalized values.
- [ ] Identifiers masked in output and logs.
- [ ] Arithmetic and format validations passed.
- [ ] Corrected and duplicate forms handled.
- [ ] Cross-document reconciliation performed.
- [ ] Low-confidence fields routed to review.
- [ ] Retention and access policy applied.

## Related skills

- `schema-enforced-json-extraction` for the extraction contract.
- `sandboxed-spreadsheet-verification` when tax workpapers are spreadsheets.
- `human-in-the-loop-escalation` for ambiguous or high-value returns.
