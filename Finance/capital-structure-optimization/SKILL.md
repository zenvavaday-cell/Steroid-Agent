---
name: capital-structure-optimization
description: Compares leverage, refinancing, and WACC scenarios under coverage and covenant constraints. Use for capital allocation and financing decisions.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: finance
---

# Capital Structure Optimization

## Overview

Capital structure work compares financing mixes on cost, risk, and flexibility. The cheapest debt is not always the right debt: leverage raises the cost of equity, consumes covenant headroom, and can force a distressed refinancing. Optimization means finding the range where weighted average cost of capital is low, coverage and covenant tests pass, and the maturity profile is financeable in a stressed market.

The output is not a single "optimal" number. It is a decision table of leverage and refinancing scenarios with coverage, ratings, WACC, value impact, and the constraints that bind.

## When to use

- Setting a target leverage range or dividend recapitalization.
- Comparing refinancing options before a maturity wall.
- Evaluating debt-funded acquisitions, buybacks, or special dividends.
- Reviewing a capital allocation plan with the board or treasury committee.
- Testing whether a rating downgrade would breach covenants or raise cost.
- Building a defense or contingency plan for a market closure.

Do not use for day-to-day cash management, short-term liquidity forecasting, or pricing a single loan where the terms are already fixed and the decision is only accept or reject.

## Workflow

### 1. Inventory the current capital stack

One row per instrument:

| Field | Example |
| --- | --- |
| Instrument | Term Loan B, senior notes, revolver, leases |
| Balance | 450,000,000 |
| Currency | USD |
| Rate | SOFR + 350 bps, 1.00% floor |
| Maturity | 2031-06-30 |
| Amortization | 1% per year |
| Security and rank | First lien, senior secured |
| Call protection | 101 soft call until 2027-06-30 |
| Covenants | Springing net leverage 4.50x |
| Change of control | 101 put |

Compute total debt, net debt, weighted average maturity, weighted average cost, fixed versus floating share, and secured versus unsecured share. Reconcile to the balance sheet and the debt note.

### 2. Build the operating baseline

Use the approved forecast: revenue, EBITDA, capex, working capital, cash taxes, and unlevered free cash flow. State the EBITDA definition used by the lenders and rating agencies, including addbacks and caps. Define the forecast cases:

- Base: management plan.
- Downside: revenue shock and margin compression, calibrated to a past downturn.
- Severe: downside plus a refinancing market closure for 12 months.

Every debt scenario must run on the same operating cases. Changing the business plan to make a leverage case work invalidates the comparison.

### 3. Model leverage and pricing scenarios

Create scenarios across net debt to EBITDA, for example 1.0x, 2.0x, 3.0x, and 4.0x. For each, set the debt mix and price it by rating band. The table below is illustrative arithmetic, not market data:

| Net leverage | Assumed rating | Cost of debt | Interest coverage | WACC |
| --- | --- | --- | --- | --- |
| 0.5x | A | 4.5% | 22.2x | 8.90% |
| 2.0x | BBB | 5.5% | 9.1x | 8.72% |
| 3.0x | BB | 6.5% | 5.1x | 8.95% |
| 4.0x | B | 8.0% | 3.1x | 9.55% |

Use `EBITDA / cash interest` for coverage and `net debt / EBITDA` for leverage. Include the revolver commitment fee, amortization, and any minimum liquidity requirement. A scenario that needs a revolver draw to pay interest is not viable.

### 4. Compute WACC with a relevered beta

```
Re   = Rf + beta_L * ERP + size_premium
beta_L = beta_U * (1 + (1 - tax_rate) * D / E)
WACC = (E / V) * Re + (D / V) * Rd * (1 - tax_rate)
```

Use market values for weights, not book values. Estimate the unlevered beta from a comparable set, then relever to each scenario's target D/E. Recompute the equity weight from the same D/E; do not mix a target leverage with today's market weights.

```python
def wacc(equity, debt, rf, erp, beta_u, rd, tax, size=0.0):
    d_over_e = debt / equity
    beta_l = beta_u * (1 + (1 - tax) * d_over_e)
    re = rf + beta_l * erp + size
    v = equity + debt
    return (equity / v) * re + (debt / v) * rd * (1 - tax), re, beta_l
```

If the WACC feeds a valuation that in turn changes the weights, iterate to convergence or use target weights and state that choice. A circular model with no convergence test can produce a plausible but wrong answer.

### 5. Add the tax shield and distress cost without double counting

A WACC that uses after-tax cost of debt already reflects the interest tax shield. Do not add a separate tax shield on top of that enterprise value. Choose one framework:

| Framework | Treatment | Use when |
| --- | --- | --- |
| WACC | After-tax cost of debt in the discount rate | Comparing operating scenarios |
| APV | Unlevered value plus PV of tax shield minus distress costs | Changing leverage materially |

Under APV, the perpetual tax shield is approximately `tax_rate * debt`, discounted if the shield is risky. Cap the shield at taxable income and account for loss carryforwards. Distress cost should be probability-weighted and evidence-based, not a fixed percentage pulled from nowhere.

### 6. Test coverage, covenants, and refinancing alternatives

Run the constraint tests in every scenario and every operating case:

| Constraint | Test | Illustrative policy limit |
| --- | --- | --- |
| Interest coverage | EBITDA / cash interest | >= 3.0x |
| Fixed charge coverage | (EBITDA - capex) / (interest + principal) | >= 1.5x |
| Net leverage | Net debt / EBITDA | <= 3.5x |
| DSCR | Cash available for debt service / debt service | >= 1.5x |
| Liquidity | Cash + undrawn revolver | >= 50,000,000 |
| Maturity wall | Debt due within 24 months / total debt | <= 30% |

Replace these with the actual covenant definitions and policy limits. A limit that is not in a signed document or an approved policy is an assumption, not a constraint.

For refinancing, compare the NPV of each alternative:

```
NPV = PV(interest savings) + value of covenant relief
      - call premium - new issue fees - breakage - tax on refinancing
```

Include the time to close, consent fees, rating agency review, and the risk that the market is closed. A refinancing that saves 50 bps but extends the maturity wall by only one year may not be worth the execution risk.

### 7. Run sensitivities and make the decision

At minimum, flex EBITDA down 20%, rates up 200 bps, and recovery value down 20%. Show the leverage, coverage, and liquidity outcome for each combination. Identify the binding constraint in each case.

Present a decision table with recommendation, conditions, and triggers for revisiting. Record board or committee approval, lender consents, rating agency outreach, and any hedging alignment.

## Validation

| Gate | Test | Fail action |
| --- | --- | --- |
| Debt tie-out | Instrument balances sum to the balance sheet debt note | Reconcile |
| Sources and uses | Sources equal uses in every transaction scenario | Fix before review |
| Leverage math | Net debt / EBITDA matches the debt schedule | Recalculate |
| WACC build | Components sum to WACC; weights sum to 100% | Rebuild |
| Beta consistency | Levered beta matches the scenario D/E and tax rate | Relever |
| Tax shield | Shield capped at taxable income; no double count | Correct framework |
| Coverage | All tests run in base, downside, and severe cases | Complete |
| Covenants | Definitions copied from the credit agreement | Re-extract |
| Maturity ladder | Maturities sum to total debt by year | Reconcile |
| Monotonicity | Higher leverage raises interest and lowers coverage | Investigate |
| Sensitivity | At least EBITDA, rate, and recovery shocks shown | Add |
| Approval | Decision and conditions recorded | Hold execution |

## Gotchas

- Adding a tax shield to a WACC-based valuation double counts a benefit already in the discount rate. Pick one framework.
- Market weights versus target weights change the answer. State which is used and why.
- A beta from a levered comparable must be unlevered before it is relevered to the target. Skipping this imports the comparable's capital structure.
- The cost of debt for a rating band is a spread, not the coupon on existing debt. Existing coupons are historical and may not reflect marginal cost.
- A revolver that is undrawn still carries a commitment fee and covenant tests. Include both.
- EBITDA addbacks that lenders allow may not be allowed by rating agencies, and vice versa. Show both definitions when they diverge.
- A lower WACC does not always mean a higher equity value if distress costs rise faster. Show the range, not a point estimate.
- Refinancing fees, call premiums, and breakage costs are real. A 25 bp coupon saving can be erased by 2 points of fees in a short hold.
- Floating-rate debt reprices quickly. A rate shock test on only the fixed portion understates interest.
- Cash trapped in foreign subsidiaries cannot repay parent debt. Adjust available liquidity for repatriation tax and controls.
- A maturity wall can refinance fine in the base case and fail in a market closure. Run the severe case with no new issuance.
- Lease liabilities and pension deficits are debt-like for rating agencies even when they sit outside funded debt. State the treatment.

## Output contract

```json
{
  "company": "Example Holdings",
  "as_of": "2026-09-30",
  "currency": "USD",
  "current": {
    "total_debt": 450000000,
    "cash": 60000000,
    "net_debt": 390000000,
    "ebitda": 130000000,
    "net_leverage": 3.0,
    "interest_coverage": 4.8,
    "wacc": 0.0872
  },
  "scenarios": [
    {
      "name": "delever to 2.0x",
      "net_debt": 260000000,
      "leverage": 2.0,
      "rating": "BBB",
      "cost_of_debt": 0.055,
      "interest_coverage": 9.1,
      "wacc": 0.0872,
      "equity_value_delta": 12000000,
      "constraints_met": true,
      "binding_constraint": "none"
    }
  ],
  "sensitivity": {
    "ebitda_down_20pct": {"max_leverage": 4.1, "breach": "net leverage"},
    "rates_up_200bps": {"interest_coverage": 3.4, "breach": "none"},
    "recovery_down_20pct": {"unsecured_recovery": 0.42}
  },
  "recommendation": {
    "target_leverage_range": [2.0, 2.75],
    "action": "refinance 2028 notes with 5-year term loan",
    "conditions": ["rating held at BBB", "hedge 50% of floating debt"],
    "revisit_triggers": ["leverage above 3.5x", "rate up 200 bps", "EBITDA down 20%"]
  },
  "approvals": {"board_date": "2026-12-10", "lender_consent": "pending"},
  "prepared_by": "treasury.analyst",
  "reviewed_by": "cfo"
}
```

## Checklist

- [ ] Capital stack reconciled to the balance sheet and debt note.
- [ ] EBITDA definition and addbacks aligned to lender and rating bases.
- [ ] Base, downside, and severe operating cases defined.
- [ ] Leverage and pricing scenarios built on the same operating cases.
- [ ] Beta unlevered and relevered consistently with each D/E.
- [ ] WACC components and weights sum correctly.
- [ ] Tax shield and distress costs treated without double counting.
- [ ] Covenant definitions copied from the credit agreement.
- [ ] Coverage, liquidity, and maturity tests run in every case.
- [ ] Refinancing costs and execution risk included.
- [ ] Sensitivities cover EBITDA, rates, and recovery.
- [ ] Recommendation states conditions and revisit triggers.

## Related skills

- `debt-schedule-waterfall` for tranche-level amortization, interest, and cash sweep mechanics.
- `covenant-breach-monitoring` for the covenant definitions and headroom that constrain leverage.
- `deterministic-financial-modeling` for building the scenario model and validation gates.
- `comparable-company-valuation` for the equity value and beta inputs used in WACC.
