---
name: working-capital-forecasting
description: Forecasts accounts receivable, accounts payable, and inventory from DSO, DPO, and DIO drivers, and flags cash gaps. Use for cash planning and liquidity reviews.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: finance
---

# Working Capital Forecasting

## Overview

Working capital is the cash locked inside operations. It rises when a company grows, when customers pay more slowly, or when inventory sits longer, and it releases cash when those trends reverse. A forecast that treats working capital as a fixed percentage of revenue misses the timing that causes liquidity crises.

This skill builds a driver-based forecast from DSO, DIO, and DPO, validates it against the ledger roll-forwards, layers in seasonality and collection curves, and converts the result into a funding requirement rather than a single balance sheet line.

## When to use

- Building a monthly cash forecast or 13-week liquidity model.
- Reviewing working capital before a refinancing or covenant test.
- Explaining why EBITDA growth is not converting to cash.
- Setting payment terms, inventory targets, or supplier financing policy.
- Stress-testing liquidity under a revenue decline or customer default.
- Comparing working capital efficiency across business units or peers.

Do not use for trading-book or mark-to-market working capital, for financial institutions, or as a substitute for a full cash flow statement.

## Workflow

### 1. Define scope and sign convention

Write down exactly which accounts are in scope. A common definition:

| Included as operating working capital | Excluded |
| --- | --- |
| Trade accounts receivable | Cash and cash equivalents |
| Inventory (raw materials, WIP, finished goods) | Short-term debt and revolver |
| Prepaid expenses and other current assets | Current portion of long-term debt |
| Trade accounts payable | Income taxes payable and receivable |
| Accrued operating liabilities | Dividends payable |
| Deferred revenue | Lease liabilities (unless operating in nature) |

Define NWC as operating current assets minus operating current liabilities. State whether a positive number means cash absorbed (the usual convention) or cash released. Never leave this implicit.

### 2. Extract monthly history from the ledger

Pull 24 to 36 months of monthly balances and activity from the general ledger or ERP. Monthly data is required because annual balances hide seasonality.

For each account, keep three series: opening balance, activity (billings, purchases, collections, payments), and closing balance. Reconcile the closing balance to the trial balance before using it.

### 3. Compute driver metrics on a consistent basis

```text
DSO = average accounts receivable / revenue x days
DIO = average inventory / cost of goods sold x days
DPO = average accounts payable / cost of goods sold (or purchases) x days
CCC = DSO + DIO - DPO
```

| Choice | Rule |
| --- | --- |
| Average versus ending balance | Use average for historical metrics; use ending for a point-in-time snapshot, labeled |
| Revenue versus credit sales | Use credit sales if available; otherwise disclose that total revenue overstates DSO |
| COGS versus purchases | Use purchases for DPO when available; COGS is an acceptable proxy if labeled |
| Days | Use 365 for annual, actual days in the month for monthly. Do not mix |
| VAT and sales tax | Strip indirect tax from AR and AP before computing days |

Report DSO, DIO, DPO, and CCC for each month, not only the annual average. A year-end DSO can look excellent because December collections are unusually high.

### 4. Build collection and payment curves

Days metrics are averages. A cash forecast needs timing. Build a collection curve from the AR aging and a payment curve from the AP aging.

| Collection timing after sale | Share collected |
| --- | --- |
| Same month | 55% |
| Month +1 | 25% |
| Month +2 | 12% |
| Month +3 | 6% |
| Never collected (bad debt) | 2% |

| Payment timing after invoice | Share paid |
| --- | --- |
| Same month | 5% |
| Month +1 | 80% |
| Month +2 | 13% |
| Month +3 | 2% |

The rows must sum to 100%. Rebuild the curves by customer or vendor segment where payment behavior differs materially (for example large retailers versus small businesses).

### 5. Layer seasonality onto the drivers

Compute a monthly seasonality index from at least two years of history:

```text
index[month] = average revenue in that calendar month / average monthly revenue
```

The 12 indices should sum to 12.0. Apply the index to the revenue forecast, then let AR follow the collection curve rather than a flat DSO. For inventory, build ahead of peak season using a lead-time assumption. For AP, align payments with the purchase pattern, not the sales pattern.

### 6. Forecast the balances and tie them to the statements

```python
def forecast_nwc(revenue, cogs, dso, dio, dpo, days=365):
    """Ending-balance driver forecast; use average balances for KPI reporting."""
    ar = revenue * dso / days
    inventory = cogs * dio / days
    ap = cogs * dpo / days
    return {"ar": ar, "inventory": inventory, "ap": ap,
            "nwc": ar + inventory - ap}


def funding_gap(cash_balances, minimum_cash):
    trough = min(cash_balances)
    return {"trough": trough, "funding_need": max(0.0, minimum_cash - trough)}
```

Post the forecast to the three-statement model. The change in NWC must flow to operating cash flow with the correct sign: an increase in NWC is a use of cash.

### 7. Flag cash gaps and test the downside

For each forecast month, compute cash before financing, the minimum cash buffer, and the revolver draw required. Flag any month where the draw exceeds 80% of committed capacity or where the cash conversion cycle exceeds the historical 90th percentile.

Run at least three scenarios:

- Base: management revenue and current payment terms.
- Downside: revenue -15%, DSO +10 days, DPO -5 days.
- Stress: largest customer pays 60 days late for two quarters and inventory cannot be liquidated.

Report the month of the trough, the size of the gap, and the financing action required.

## Validation

| Gate | Test | Pass criterion | Fail action |
| --- | --- | --- | --- |
| AR roll | Opening + billings - collections - write-offs | Equals closing within 0.5 | Reconcile to aging |
| AP roll | Opening + purchases - payments | Equals closing within 0.5 | Reconcile to vendor ledger |
| Inventory roll | Opening + purchases - COGS +/- adjustments | Equals closing within 0.5 | Check write-downs and capitalizations |
| DSO | Recompute from raw balances | Matches reported metric to 0.1 day | Fix denominator or average |
| DIO | Recompute from raw balances | Matches to 0.1 day | Fix COGS basis |
| DPO | Recompute from raw balances | Matches to 0.1 day | Check purchases versus COGS |
| Curve sums | Collection and payment rows | Each sums to 100% | Correct rounding or bad debt |
| Seasonality | Sum of 12 indices | 12.0 +/- 0.01 | Rebase the index |
| Cash tie | Forecast NWC change versus CF | Difference <= 0.5 | Fix sign or scope |
| Funding | Revolver draw versus commitment | Draw between 0 and commitment | Resize facility or escalate |
| Ratio range | Forecast days versus history | Within historical p10-p90, or explained | Challenge the assumption |

## Gotchas

- Accounts receivable often includes VAT or sales tax. Dividing gross AR by net revenue overstates DSO by the tax rate.
- Using total revenue instead of credit sales understates DSO for businesses with significant cash sales.
- Year-end DSO can look strong because of seasonal collections. Use a 12-month average or a same-month comparison.
- Deferred revenue is a liability that funds the business. Excluding it overstates working capital and hides a cash source.
- Negative working capital businesses (grocers, subscription software) invert the usual growth relationship. Do not force a positive NWC ratio.
- Factoring and supply-chain finance remove receivables or extend payables temporarily. Reverse these programs before computing the underlying trend.
- Stretching DPO improves cash but transfers risk to suppliers and can reverse suddenly. Flag stretched terms above contractual limits.
- An inventory write-down reduces the balance but is not a cash inflow. Keep the write-down separate from operating payments.
- A growing company can report improving DSO while cash worsens, because the denominator (revenue) is growing faster than collections.
- Capex accrued but unpaid sits in accounts payable. Mixing it with trade AP distorts DPO.
- Foreign-currency balances must be translated at consistent rates. A currency move can change NWC without any operating change.
- Monthly forecasts built with 30-day months drift from actual 28-, 30-, and 31-day periods. Use actual days or accept and disclose the approximation.

## Output contract

```json
{
  "entity": "Example Co",
  "period_basis": "monthly",
  "scope": ["trade AR", "inventory", "prepaids", "trade AP", "accrued operating liabilities", "deferred revenue"],
  "historical": {"dso": 52.0, "dio": 61.0, "dpo": 44.0, "ccc": 69.0, "window_months": 24},
  "forecast": [
    {"month": "2027-01", "revenue": 1000.0, "ar": 142.5, "inventory": 167.1, "ap": 120.5, "nwc": 189.1, "delta_nwc": 12.4}
  ],
  "drivers": {"dso": 50.0, "dio": 60.0, "dpo": 45.0, "bad_debt_pct": 2.0},
  "seasonality_index": [1.12, 1.05, 0.98, 0.94, 0.91, 0.89, 0.88, 0.92, 0.99, 1.04, 1.09, 1.19],
  "cash_gap": {"trough_month": "2027-04", "trough_cash": -120.0, "minimum_cash": 75.0, "funding_need": 195.0, "revolver_draw": 195.0},
  "scenarios": [{"name": "downside", "funding_need": 310.0, "trough_month": "2027-05"}],
  "flags": ["DSO exceeds historical p90 in 2027-03", "revolver utilization above 80% in April"],
  "assumptions": ["365-day year", "no factoring", "constant FX"],
  "prepared_by": "analyst",
  "reviewed_by": "manager"
}
```

## Checklist

- [ ] NWC scope and sign convention defined and documented.
- [ ] 24 to 36 months of monthly ledger history extracted.
- [ ] Historical balances reconcile to the trial balance.
- [ ] DSO, DIO, and DPO use consistent denominators and day counts.
- [ ] Indirect tax stripped from AR and AP.
- [ ] Collection and payment curves built from aging and sum to 100%.
- [ ] Seasonality index built and normalized.
- [ ] Forecast NWC change ties to operating cash flow.
- [ ] Cash gap computed against a stated minimum cash buffer.
- [ ] Downside and stress scenarios run.
- [ ] Factoring and supply-chain finance reversed or disclosed.
- [ ] Exceptions flagged with the month and the driver.

## Related skills

- `deterministic-financial-modeling` for the integrated model and assumption register.
- `liquidity-stress-testing` for the downside cash and funding scenarios.
- `automated-ledger-reconciliation` for extracting and reconciling AR, AP, and inventory balances.
- `three-statement-model-reconciliation` for tying the working capital change into the cash flow statement.
