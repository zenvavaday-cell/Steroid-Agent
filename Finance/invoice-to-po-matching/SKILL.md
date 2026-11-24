---
name: invoice-to-po-matching
description: Matches invoices to purchase orders, goods receipts, and contracts with line-level tolerance rules, unit conversion, duplicate detection, and exception routing. Use for accounts payable automation, procure-to-pay controls, three-way matching, and payment hold decisions.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: finance
---

# Invoice-to-PO Matching

## Overview

Invoice matching answers a control question: should this invoice be paid? The invoice must agree with an authorized purchase order and, where goods or services are received, with evidence of receipt. Exceptions are routed, not forced.

The match is line-level first, then header-level. A matching total can hide mismatched lines.

## When to use

- Accounts payable invoice processing.
- Three-way or four-way match automation.
- Audit of duplicate or split invoices.
- Vendor statement reconciliation.
- Pre-payment control review.

## Match types

| Type | Compares | Use when |
| --- | --- | --- |
| 2-way | Invoice vs PO | Services, subscriptions, no receipt |
| 3-way | Invoice vs PO vs receipt | Goods |
| 4-way | Invoice vs PO vs receipt vs inspection/contract | Regulated or high-value goods |

## Workflow

### 1. Normalize the documents

Extract:

- Vendor legal name and tax ID.
- Invoice number, date, due date, currency.
- PO number and PO line numbers.
- Line description, quantity, unit of measure, unit price, tax, freight, discount.
- Receipt quantity and date.
- Payment terms.

Normalize units to a base unit per line. Normalize currency to the PO currency using a documented rate and date.

### 2. Detect duplicates first

A duplicate check runs before matching:

- Same vendor + invoice number.
- Same vendor + amount + invoice date within a window.
- Same PO line + quantity + amount across different invoice numbers.
- Credit memo referencing the same invoice.

Exact duplicate invoice numbers across different vendors are not duplicates. Vendor identity must be resolved first.

### 3. Match the header

| Field | Rule |
| --- | --- |
| Vendor | Exact tax ID, or fuzzy name above threshold with review |
| PO | Must exist and be open |
| Currency | Must match, or be converted with a recorded rate |
| Total | Within tolerance after line matching |

### 4. Match the lines

For each invoice line, find the PO line and receipt line:

1. Exact PO line reference.
2. Exact item code or SKU.
3. Normalized description similarity.
4. Unit price and quantity proximity.

```python
def line_match(inv, po, receipt, price_tol=0.02, qty_tol=0.0):
    if inv["item"] != po["item"]:
        return None
    if abs(inv["unit_price"] - po["unit_price"]) > po["unit_price"] * price_tol:
        return "price_variance"
    invoiced = inv["qty"] * inv["uom_factor"]
    ordered = po["qty"] * po["uom_factor"]
    received = receipt["qty"] * receipt["uom_factor"] if receipt else ordered
    if invoiced > received + qty_tol:
        return "quantity_exceeds_receipt"
    if invoiced > ordered + qty_tol:
        return "quantity_exceeds_po"
    return "matched"
```

Tolerances should be per category, not global. A 2% price tolerance is reasonable for commodities and wrong for contracted services.

### 5. Handle taxes, freight, and discounts

- Tax must reconcile to the invoice tax lines and the jurisdiction.
- Freight is payable only if the PO or contract allows it.
- Early-payment discounts are applied per terms, not by default.
- Credit memos offset the original invoice, not unrelated balances.

### 6. Classify exceptions

| Exception | Action |
| --- | --- |
| No PO | Route to procurement for retroactive PO or reject |
| Price variance | Route to buyer; do not pay the variance |
| Quantity variance | Match to receipt; hold shortfall |
| Duplicate | Hold and investigate |
| Vendor mismatch | Verify banking and legal entity |
| Tax mismatch | Route to tax |
| UOM mismatch | Correct conversion, then rematch |
| Partial delivery | Pay received quantity only if policy allows |

### 7. Decide payment

Only fully matched invoices, or exceptions with documented approval, enter the payment run. Record the approver, the exception reason, and the amount approved.

## Gotchas

- Unit-of-measure conversion is a top source of false matches. "Case" versus "each" can be a 12x error.
- Partial shipments mean one PO can have many receipts. Match against cumulative received quantity, not a single receipt.
- Consolidated invoices cover multiple POs. Match at the line-to-PO-line level.
- PO amendments change the authorized quantity or price. Use the current version and record the amendment.
- Vendor master changes are a fraud vector. Verify bank detail changes out of band.
- Tax can be included or excluded in the unit price. Confirm the convention.
- Duplicate invoice numbers are common across vendors. Resolve vendor identity first.
- Early-payment discounts can be more valuable than the float. Model the trade-off.

## Output contract

```json
{
  "invoice_id": "INV-2026-1182",
  "vendor_id": "V-00441",
  "po_id": "PO-2026-771",
  "match_type": "3-way",
  "status": "exception",
  "lines": [
    {
      "line": 1,
      "po_line": 2,
      "invoiced_qty": 10,
      "received_qty": 8,
      "unit_price": 120.00,
      "result": "quantity_exceeds_receipt",
      "variance": 240.00
    }
  ],
  "exceptions": ["quantity_exceeds_receipt"],
  "approved_amount": 960.00,
  "held_amount": 240.00,
  "route_to": "buyer@example.com",
  "evidence": ["invoice.pdf#page=1", "po.pdf#page=2", "receipt.csv#row=18"]
}
```

## Checklist

- [ ] Vendor identity resolved by tax ID.
- [ ] Duplicate check completed before matching.
- [ ] Units and currency normalized.
- [ ] Header matched.
- [ ] Lines matched to PO and cumulative receipts.
- [ ] Tax, freight, and discounts validated.
- [ ] Exceptions routed with owners.
- [ ] Only approved amounts enter payment.

## Related skills

- `automated-ledger-reconciliation` for the payment-side reconciliation.
- `automated-tax-document-parsing` for extracting invoice fields.
- `transaction-anomaly-flagging` for vendor and payment fraud patterns.
