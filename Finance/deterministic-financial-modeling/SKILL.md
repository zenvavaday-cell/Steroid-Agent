---
name: deterministic-financial-modeling
description: Builds auditable financial models (DCF, LBO, budgets, scenario analysis) where every output traces to a sourced assumption and a visible formula, with balance-sheet checks and sensitivity tables. Use when creating or reviewing valuation models, financial projections, fundraising materials, or any spreadsheet where a wrong number is expensive.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: finance
---

# Deterministic Financial Modeling

## Overview

A deterministic model produces the same outputs from the same inputs on every run. No hidden state, no manual overrides buried in formulas, no "plug" cells. The model is a graph: sourced assumptions flow through explicit calculations into outputs, and every output can be traced back to its drivers.

This skill covers model architecture, the three-statement build, DCF mechanics, scenario and sensitivity analysis, and the validation gates that must pass before a model is shown to anyone.

## When to use

- Building a DCF, LBO, merger model, operating budget, or fundraising projection.
- Reviewing someone else's model for errors, hardcodes, or broken links.
- Producing scenario or sensitivity analysis for a decision.
- Preparing a model for audit, investment committee, or board review.

Do not use for one-off arithmetic, exploratory charts, or dashboards that do not need an auditable calculation chain.

## Model contract

Agree these before opening a spreadsheet:

| Item | Rule |
| --- | --- |
| Units | State once (thousands, millions) and use consistently. Never mix. |
| Currency | Single reporting currency. FX assumptions live in one table. |
| Time | One column per period, exact period-end dates, no ambiguous "Year 1". |
| Signs | Costs and cash outflows negative; revenue and inflows positive. |
| Formula style | Every calculation cell is a formula. Hardcodes only in the assumptions sheet. |
| Color convention | Blue = input, black = formula, green = link to another sheet, red = check. |
| Versioning | File name includes version and date. One change log sheet. |

## Workflow

### 1. Write the model brief

Capture purpose, audience, forecast horizon, reporting currency, units, scenario set, and the decision the model supports. A model without a decision is a spreadsheet.

### 2. Build the assumptions register

Every assumption gets a row with value, unit, source, as-of date, owner, and confidence. Example:

| Assumption | Value | Unit | Source | As of | Confidence |
| --- | --- | --- | --- | --- | --- |
| Revenue growth FY27 | 12.0% | % | Management plan v3 | 2026-11-01 | Medium |
| Gross margin | 68.0% | % | FY25 audited | 2026-02-14 | High |
| WACC | 9.4% | % | Calc sheet | 2026-11-20 | Medium |

No assumption may be typed directly into a calculation sheet. If a number has no source, label it "judgment" and state who owns it.

### 3. Lay out the timeline

Use exact dates and a day-count convention. For annual models, use fiscal period ends. For debt and cash, use monthly or quarterly periods. Avoid 52-week versus 365-day mismatches.

### 4. Build the statements in dependency order

1. Revenue drivers (volume × price, customers × ARPU, segments).
2. Cost of revenue and operating expenses (fixed versus variable).
3. Capital expenditure and depreciation.
4. Working capital (DSO, DIO, DPO, deferred revenue).
5. Debt schedule (opening, draws, repayments, interest, closing).
6. Tax (EBT, losses, credits, effective rate).
7. Cash flow statement.
8. Balance sheet.
9. Outputs and checks.

### 5. Implement the DCF

```python
def wacc(equity_value, debt_value, cost_equity, cost_debt, tax_rate):
    total = equity_value + debt_value
    return (equity_value / total) * cost_equity + (
        debt_value / total
    ) * cost_debt * (1 - tax_rate)


def dcf(fcff, wacc_rate, terminal_growth, net_debt, mid_year=True):
    """fcff: list of unlevered free cash flows, one per year."""
    if wacc_rate <= terminal_growth:
        raise ValueError("WACC must exceed terminal growth for a Gordon terminal value")
    pv = 0.0
    for year, cash in enumerate(fcff, start=1):
        exponent = year - 0.5 if mid_year else year
        pv += cash / (1 + wacc_rate) ** exponent
    terminal = fcff[-1] * (1 + terminal_growth) / (wacc_rate - terminal_growth)
    pv_terminal = terminal / (1 + wacc_rate) ** len(fcff)
    enterprise_value = pv + pv_terminal
    equity_value = enterprise_value - net_debt
    return {
        "pv_explicit": pv,
        "pv_terminal": pv_terminal,
        "enterprise_value": enterprise_value,
        "equity_value": equity_value,
        "terminal_share": pv_terminal / enterprise_value,
    }
```

Use the Gordon growth terminal value only when growth is below the long-run nominal growth rate of the economy. Cross-check with an exit multiple and show both.

### 6. Add scenarios and sensitivities

Scenarios change named assumptions, never formulas. Build a scenario switch table and a sensitivity grid driven by formulas (or Python), not by manually retyping outputs.

Minimum sensitivity set:

- WACC ± 100 bps versus terminal growth ± 50 bps.
- Revenue growth ± 300 bps versus gross margin ± 300 bps.
- Exit multiple versus WACC for the terminal value cross-check.

### 7. Run validation gates

| Gate | Test | Fail action |
| --- | --- | --- |
| Balance sheet | Assets = Liabilities + Equity every period | Fix before proceeding |
| Cash tie | Ending cash on BS = ending cash on CF | Fix before proceeding |
| Retained earnings | Opening + net income − dividends = closing | Fix before proceeding |
| Debt schedule | Closing = opening + draws − repayments | Fix before proceeding |
| Signs | Costs and capex negative, revenue positive | Normalize |
| Hardcodes | Scan formula cells for constants | Move to assumptions |
| Units | Spot-check every output for scale | Fix |
| Terminal value | TV share of EV reported and justified | Flag if > 75% |
| Circularity | Interest on average debt resolved | Enable iterative calc only if documented |

## Gotchas

- Interest on average debt creates a circular reference. Either use opening debt, enable iterative calculation with a documented tolerance, or solve algebraically.
- Tax losses and valuation allowances break the simple "EBIT × tax rate" approach. Model the loss carryforward explicitly.
- Operating leases, stock-based compensation, and capitalized software change EBITDA and free cash flow. State the treatment.
- Terminal value often dominates the valuation. Always show its share of enterprise value.
- Mid-year convention is not optional decoration. It changes value by roughly half a year of discounting.
- A "plug" in the balance sheet hides a real error. Find the driver, do not plug cash.
- Non-recurring items that are "added back" every year are recurring. Challenge them.

## Output contract

Deliver:

1. The model workbook with assumptions, calculations, outputs, and checks separated.
2. An assumptions register with sources and confidence.
3. A check report showing every validation gate and its result.
4. A sensitivity table and a one-page summary of the valuation range.
5. A change log and model version.

## Example

Input: five-year FCFF of 10, 12, 14, 16, 18; WACC 9%; terminal growth 2.5%; net debt 40.

Output summary:

```
PV explicit          = 55.5
PV terminal          = 184.5
Enterprise value     = 239.9
Equity value         = 199.9
Terminal share       = 76.9%  <-- flag: justify or extend horizon
```

## Checklist

- [ ] Model brief written and agreed.
- [ ] Every assumption has a source and an owner.
- [ ] Timeline uses exact dates and one convention.
- [ ] Three statements tie in every period.
- [ ] No hardcodes in calculation cells.
- [ ] DCF checked against an exit multiple.
- [ ] Sensitivities are formula-driven.
- [ ] Terminal value share reported.
- [ ] Check report passes before distribution.

## Related skills

- `sandboxed-spreadsheet-verification` for recalculating and auditing the workbook.
- `sec-filing-extraction` for pulling historical financials.
- `confidence-threshold-output-gating` before sending a valuation to decision-makers.
