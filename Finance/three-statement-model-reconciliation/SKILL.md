---
name: three-statement-model-reconciliation
description: Reconciles income statement, balance sheet, and cash flow statements with tie-outs, sign conventions, and circularity controls. Use for building or auditing integrated three-statement models.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: finance
---

# Three-Statement Model Reconciliation

## Overview

An integrated model is not three statements stored in one workbook. It is one set of operating drivers that produces three statements which must agree in every period. Reconciliation is the discipline of proving that agreement with named links, explicit signs, documented tolerances, and a failure path when a check breaks.

Most model errors are articulation errors: net income that never reaches retained earnings, capex that never appears in investing cash flow, or revolver interest computed on a balance the model has not solved yet. This skill builds the link map, the tie-out harness, and the circularity controls that make those errors visible before a reviewer finds them.

## When to use

- Building a new integrated operating model from a trial balance or filed statements.
- Auditing a model received from a bank, advisor, or portfolio company.
- Adding a debt tranche, acquisition, or new statement line to an existing model.
- Preparing a model for audit, lender, or investment committee review.
- Debugging a balance sheet that does not balance or a cash flow statement that does not tie.
- Reconciling forecast actuals to a management reporting pack.

Do not use for a single-statement projection, a stand-alone DCF, or a schedule that never touches a balance sheet.

## Workflow

### 1. Freeze the period grid and sign convention

Write both down before any formula is entered. Mixing conventions is the most common source of silent errors.

| Item | Rule |
| --- | --- |
| Periods | One column per period, exact period-end dates, fiscal calendar stated |
| Units | One unit for the whole model (for example USD thousands), shown on every sheet |
| Signs | Revenue and inflows positive; costs, capex, repayments, dividends negative |
| Contra accounts | Accumulated depreciation and allowance accounts negative |
| Formula cells | Formulas only; hardcodes live in the assumptions register |
| Tolerance | Absolute tolerance in model units, for example 0.5 (USD 500 when units are thousands) |

### 2. Build the link map before formulas

Every statement-to-statement flow gets a named row and an owner. A minimal map:

| Source | Destination | What must agree |
| --- | --- | --- |
| IS net income | CF operating; BS retained earnings | Same value, same period |
| IS D&A | CF add-back; PP&E accumulated depreciation | D&A equals the period depreciation roll |
| Capex | CF investing; PP&E gross | Cash capex equals gross PP&E additions |
| Working capital balances | CF change in working capital; BS | Delta equals closing minus opening, with the cash sign |
| Debt draws and repayments | CF financing; debt schedule closing | Roll-forward closes |
| Share issuance and buybacks | CF financing; BS share capital and treasury | Share count roll closes |
| Dividends | CF financing; BS retained earnings | Retained earnings roll closes |
| Stock-based compensation | CF add-back; BS additional paid-in capital | Non-cash amount does not hit cash |
| FX translation | CF; BS cumulative translation adjustment | Remeasurement gain or loss lands in equity |

### 3. Build the income statement with tax and share count

Work from revenue drivers to EBIT, then interest, then tax, then net income. Model tax losses explicitly rather than applying a flat rate to a loss. Keep basic and diluted shares as separate roll-forwards; diluted EPS must use the diluted count.

### 4. Roll every balance sheet account

Each non-cash account needs an explicit roll-forward. If an account has no roll, it is a hardcode wearing a formula costume.

```text
PP&E gross        = opening + capex - disposals
Accumulated dep.  = opening + depreciation - accumulated dep. on disposals
Retained earnings = opening + net income - dividends +/- prior period adjustments
Debt              = opening + draws + PIK - repayments - write-offs
Share capital     = opening + issuance - buybacks
```

### 5. Build the cash flow statement from the balance sheet deltas

Start with net income, add back non-cash items, subtract the increase in operating assets and add the increase in operating liabilities. Investing and financing sections must be driven by the same rows that move the balance sheet, not retyped.

Sign rule for working capital: an increase in accounts receivable is a cash outflow, so the cash flow line is the negative of the balance change. An increase in accounts payable is a cash inflow.

### 6. Resolve revolver and interest circularity

A revolver draw depends on cash after interest, and interest depends on the draw. Pick one method and document it:

| Method | Use when | Control |
| --- | --- | --- |
| Interest on opening balance | Simple models, no revolver | No circularity, slightly understates interest |
| Iterative calculation | Excel or Python model with a revolver | Tolerance 1e-8, max 250 iterations, convergence flag |
| Algebraic solve | Linear interest and a single tranche | Derive draw directly, verify by substitution |

```python
def solve_revolver(cash_before_interest, opening_cash, minimum_cash, rate,
                   tol=1e-8, max_iter=250):
    """Illustrative fixed-point solve for one revolver tranche."""
    draw = 0.0
    for iteration in range(1, max_iter + 1):
        interest = draw * rate
        cash = opening_cash + cash_before_interest - interest
        target = max(0.0, minimum_cash - cash)
        if abs(target - draw) < tol:
            return {"draw": target, "interest": target * rate,
                    "iterations": iteration, "converged": True}
        draw = target
    raise RuntimeError("revolver did not converge; tighten the model or solve algebraically")
```

Never leave iterative calculation enabled with a loose tolerance, because it will absorb real errors.

### 7. Run the tie-out harness

Encode every gate as a check with an explicit expected value, tolerance, and fail action.

```python
from dataclasses import dataclass

@dataclass
class Check:
    name: str
    actual: float
    expected: float
    tolerance: float

    @property
    def passed(self) -> bool:
        return abs(self.actual - self.expected) <= self.tolerance


def run_checks(checks):
    failures = [c for c in checks if not c.passed]
    for c in checks:
        status = "PASS" if c.passed else "FAIL"
        print(f"{status:4} {c.name:32} diff={c.actual - c.expected:,.3f}")
    if failures:
        raise SystemExit(f"{len(failures)} reconciliation failure(s)")
    return True
```

### 8. Reconcile actuals to the source

For historical periods, tie revenue, EBIT, net income, total assets, total debt, and equity to audited statements or the trial balance. Investigate every difference above 0.1% of the line item. Record reclassifications in a reconciliation log rather than adjusting silently.

## Validation

| Gate | Test | Pass criterion | Fail action |
| --- | --- | --- | --- |
| Balance sheet | Assets - liabilities - equity | Abs diff <= 0.5 model units | Stop; find the unlinked account |
| Cash tie | CF ending cash - BS cash | Abs diff <= 0.5 | Check beginning cash and FX effects |
| Retained earnings | Opening + NI - dividends | Abs diff <= 0.5 | Check prior adjustments and dividends |
| PP&E roll | Opening + capex - disposals - dep. | Abs diff <= 0.5 | Check capex and disposal proceeds |
| Debt roll | Opening + draws + PIK - repayments | Abs diff <= 0.5 | Check each tranche separately |
| Working capital | CF delta equals BS change | Abs diff <= 0.5 | Check sign and scope exclusions |
| Share count | Opening + issued - bought back | Exact integer | Check option and RSU treatment |
| Source tie | Model actuals versus audited | Abs diff <= 0.1% per line | Log reclass or fix model |
| Circularity | Solver converged | Converged = true | Do not distribute the model |
| Check total | Sum of all check differences | Zero within tolerance | Fix before distribution |

## Gotchas

- A balance sheet that balances because cash is a plug hides the error. Remove the plug, let cash go negative, and force the check to fail loudly.
- Linking net income to retained earnings but forgetting dividends overstates equity every period.
- Capex that appears in investing cash flow but not in the PP&E roll leaves assets understated.
- Adding back D&A on the cash flow statement without updating accumulated depreciation breaks the PP&E roll.
- Reversing the working capital sign is common when a model is copied between files. Assert the sign with a known test case.
- Deferred tax assets and liabilities are easy to omit. Tax expense must reconcile to current plus deferred tax.
- FX translation gains belong in equity and in the cash flow reconciliation, not in operating income.
- Beginning cash that is typed rather than linked to prior ending cash creates a one-period break that compounds.
- Loose iterative-calculation tolerance (for example 0.01) can hide a genuine 10-unit error.
- Mixing thousands and millions inside one workbook makes every tolerance meaningless. Assert the unit on each sheet.
- A 52/53-week fiscal calendar does not align with 365-day drivers. State the convention and keep it consistent.
- Debt issuance costs that are capitalized but never amortized overstate equity and understate interest expense.

## Output contract

```json
{
  "model": "Example Co integrated model FY26-FY30",
  "units": "USD thousands",
  "tolerance": 0.5,
  "periods": ["FY26", "FY27", "FY28", "FY29", "FY30"],
  "links": [
    {"from": "IS.net_income", "to": ["BS.retained_earnings", "CF.net_income"], "status": "verified"}
  ],
  "checks": [
    {"id": "BS-BAL", "period": "FY26", "difference": 0.0, "tolerance": 0.5, "status": "pass"}
  ],
  "circularity": {"method": "iterative", "max_iterations": 250, "tolerance": 1e-8, "converged": true},
  "source_reconciliation": [
    {"statement": "FY25 audited", "line": "revenue", "difference_pct": 0.0}
  ],
  "exceptions": [],
  "sign_off": {"prepared_by": "analyst", "reviewed_by": "manager", "date": "2026-11-26"}
}
```

## Checklist

- [ ] Period grid, units, and sign convention written down and enforced.
- [ ] Every statement-to-statement link has a named row and owner.
- [ ] Income statement ties to retained earnings and cash flow.
- [ ] Every balance sheet account has an explicit roll-forward.
- [ ] Cash flow is driven by balance sheet deltas, not retyped values.
- [ ] Working capital signs verified with a known test case.
- [ ] Revolver circularity method documented and converged.
- [ ] All validation gates pass within stated tolerance.
- [ ] Historical actuals tie to audited statements or trial balance.
- [ ] Exceptions and reclassifications logged.
- [ ] No hardcodes outside the assumptions register.
- [ ] Model signed off by preparer and reviewer.

## Related skills

- `deterministic-financial-modeling` for model architecture, assumption sourcing, and sensitivity design.
- `sandboxed-spreadsheet-verification` for recalculating the workbook and scanning formulas for hardcodes.
- `automated-ledger-reconciliation` for tying model actuals back to the general ledger.
- `sec-filing-extraction` for sourcing filed historical statements and footnote detail.
