---
name: automated-ledger-reconciliation
description: Reconciles general ledger, bank, subledger, and payment-processor records with exact and fuzzy matching, tolerance rules, FX handling, exception classification, and adjusting journal entries. Use for month-end close, bank reconciliations, intercompany matching, processor settlement checks, and audit-ready reconciliation packs.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: finance
---

# Automated Ledger Reconciliation

## Overview

Reconciliation proves that two independently maintained records describe the same economic activity. The output is not a matched list; it is an evidence pack showing what matched, what did not, why, and what adjustment is required.

Automate the deterministic matches. Reserve human attention for genuine exceptions.

## When to use

- Bank statement versus cash ledger.
- Payment processor settlement versus sales ledger.
- Subledger versus general ledger control accounts.
- Intercompany balances between entities.
- Custodian holdings versus internal position records.

## Reconciliation contract

Define before matching:

| Item | Example |
| --- | --- |
| Left source | Bank statement, USD, settlement date |
| Right source | Cash GL, USD, posting date |
| Scope | Entity, account, period |
| Tolerance | ±0.01 absolute for fees; ±0.5% for FX |
| Date window | ±3 business days for timing differences |
| Match basis | Amount + reference, or amount + date + counterparty |
| FX source | ECB reference rate at 16:00 CET |
| Materiality | Exceptions above 10,000 require sign-off |

## Workflow

### 1. Normalize both sides

Create a canonical frame with:

- `source_id`, `account_id`, `counterparty`
- `transaction_date`, `settlement_date`
- `amount` (signed), `currency`, `amount_reporting`
- `fx_rate`, `fx_rate_date`
- `reference`, `description`
- `direction` (debit/credit)

Normalize sign conventions explicitly. A bank statement may show debits as positive; a ledger may show them as negative. Choose one convention and document the mapping.

### 2. Run exact matching

Match on a composite key in priority order:

1. Unique reference + amount + currency.
2. Amount + value date + counterparty.
3. Check number or transaction ID.

```python
def exact_match(left, right, keys):
    merged = left.merge(right, on=keys, how="inner", suffixes=("_l", "_r"))
    merged["match_type"] = "exact"
    return merged
```

### 3. Run fuzzy matching on the remainder

Build candidate pairs within a date window and amount tolerance, then score:

```python
from rapidfuzz import fuzz

def pair_score(l, r, tolerance=0.01, window_days=3):
    if abs(l["amount"] - r["amount"]) > max(tolerance, abs(l["amount"]) * 0.005):
        return 0.0
    if abs((l["date"] - r["date"]).days) > window_days:
        return 0.0
    reference = fuzz.token_set_ratio(l["reference"], r["reference"]) / 100
    party = fuzz.token_set_ratio(l["counterparty"], r["counterparty"]) / 100
    amount = 1 - min(abs(l["amount"] - r["amount"]) / max(abs(l["amount"]), 1), 1)
    return 0.5 * reference + 0.3 * party + 0.2 * amount
```

Assign pairs greedily by descending score, one-to-one. Then handle many-to-one and one-to-many:

- One bank deposit equals several invoices.
- One processor settlement equals gross sales minus fees minus refunds.
- One payroll debit equals multiple employee payments.

Use subset-sum or grouped aggregation with a tolerance. Do not force a match that requires an unexplained residual.

### 4. Classify exceptions

| Class | Meaning | Action |
| --- | --- | --- |
| Timing | Posted in different periods | Reverse in next period or accrue |
| Fee | Amount differs by a known fee | Book fee |
| FX | Rate or date difference | Revalue at policy rate |
| Duplicate | Same transaction recorded twice | Reverse duplicate |
| Missing left/right | Only one side recorded | Investigate, then accrue |
| Amount mismatch | Same transaction, different amount | Investigate |
| Split/aggregate | Many-to-one relationship | Allocate |
| Unknown | No explanation | Escalate |

### 5. Generate adjusting entries

For each exception requiring an adjustment, produce a journal entry with debit account, credit account, amount, currency, date, reason, and supporting reference. Never post automatically without the approval policy.

### 6. Validate

- Sum of matched left amounts equals sum of matched right amounts within tolerance.
- Every unmatched item appears exactly once in the exception report.
- Adjusting entries bring the reconciled balance to the source balance.
- FX translations use one rate source and date.
- The reconciliation ties to the trial balance.

## Gotchas

- Net settlements hide gross activity and fees. Reconcile the components, not only the net.
- Refunds and chargebacks reverse the original transaction. Match them as a pair, not as unrelated items.
- Cut-off differences at month-end are timing, not errors. Prove the subsequent clearing.
- Duplicate references are common across processors. Never use reference alone as a unique key.
- Rounding differences accumulate. Track residuals separately from true exceptions.
- Intercompany matching needs both entities' books and a common FX rate.
- A stale bank feed can look like a missing transaction. Check the feed timestamp first.

## Output contract

```
Reconciliation: <account> <period>
Left total: <amount>
Right total: <amount>
Matched: <count> (<amount>)
Exceptions: <count> (<amount>)
  timing: <count>
  fee: <count>
  fx: <count>
  duplicate: <count>
  missing: <count>
  amount mismatch: <count>
Adjusting entries: <count> (<amount>)
Residual: <amount>
Prepared by / reviewed by: <names>
```

Attach the item-level match table and exception detail.

## Checklist

- [ ] Sources, scope, period, and tolerance documented.
- [ ] Sign conventions and FX policy normalized.
- [ ] Exact matches run first.
- [ ] Fuzzy matches scored and one-to-one.
- [ ] Many-to-one relationships resolved.
- [ ] Exceptions classified with reasons.
- [ ] Adjusting entries prepared and reviewed.
- [ ] Reconciliation ties to the trial balance.

## Related skills

- `transaction-anomaly-flagging` for suspicious patterns within reconciled data.
- `invoice-to-po-matching` for procure-to-pay matching.
- `stateful-workflow-checkpointing` for long close cycles that must resume.
