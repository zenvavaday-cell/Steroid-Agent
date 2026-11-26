---
name: budget-variance-analysis
description: Decomposes budget-versus-actual variances by volume, price, mix, and timing, and ranks material drivers. Use for monthly business reviews and reforecasting.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: finance
---

# Budget Variance Analysis

## Overview

A variance is only useful when it is decomposed into drivers that a manager can act on. "Revenue is down 3%" hides whether the cause is fewer units, lower price, worse mix, a timing shift, or currency. Each has a different owner and a different implication for the reforecast.

The discipline is to flex the budget to actual volume, decompose the remainder into price, mix, cost, FX, and timing, rank by materiality, and attach evidence and an action to every material line. The bridge must add up to the reported variance.

## When to use

- Monthly or quarterly business reviews against budget or prior forecast.
- Preparing a board pack with variance commentary.
- Reforecasting the full year from year-to-date actuals.
- Investigating a margin decline or an unexpected cost overrun.
- Reviewing a department's spend against an approved plan.
- Setting thresholds for which variances require explanation.

Do not use for a full strategic re-plan, a zero-based budget build, or a valuation; those need a forward model, not a variance decomposition.

## Workflow

### 1. Lock the comparison basis

Record the actuals version, budget version, forecast version, FX rates, calendar, and accounting policy for both sides. Verify:

- Actuals are final for the period and reconciled to the ledger.
- The budget is the approved version, not a working draft.
- Both sides use the same entity scope, chart of accounts, and cost allocation.
- One-off items and reclassifications are identified on both sides.
- Revenue is net of rebates, discounts, and returns on both sides.

If the basis differs, restate before decomposing. A variance caused by a reclassification is not a business driver.

### 2. Flex the budget to actual volume

Separate fixed from variable costs. For variable costs, replace budgeted volume with actual volume at the budget rate:

```
flexed_cost = budget_rate * actual_volume
spending_variance = actual_cost - flexed_cost
```

Comparing actual variable cost to a static budget conflates volume growth with overspending. Show the static budget, the flexed budget, and actual side by side.

### 3. Decompose revenue into volume, mix, and price

For a single product:

```
volume = (actual_qty - budget_qty) * budget_price
price  = (actual_price - budget_price) * actual_qty
total  = actual_revenue - budget_revenue
```

For multiple products, isolate mix explicitly:

```
volume = (sum(actual_qty) - sum(budget_qty)) * weighted_avg_budget_price
mix    = sum((actual_qty_i - budget_qty_i * volume_index) * budget_price_i)
price  = sum((actual_price_i - budget_price_i) * actual_qty_i)
volume_index = sum(actual_qty) / sum(budget_qty)
```

Illustrative example:

| Product | Budget qty | Budget price | Actual qty | Actual price |
| --- | --- | --- | --- | --- |
| A | 600 | 50 | 700 | 48 |
| B | 400 | 80 | 350 | 82 |

Budget revenue is 62,000 and actual is 62,300, a favorable 300. The decomposition is volume +3,100, mix -2,100, price -700. Volume growth is real, but it came from the lower-priced product, and price erosion on A outweighed the gain on B. A single "revenue up 300" line would hide all three effects.

### 4. Decompose cost and margin variances

Use the same logic with the sign flipped so favorable is positive:

```
cost_price = (budget_rate - actual_rate) * actual_qty
cost_volume = (budget_qty - actual_qty) * budget_rate
```

For margin, analyze revenue and cost effects together, then show the margin percentage bridge. A revenue increase with a larger cost increase is unfavorable even when revenue is ahead of plan. Include:

- Input cost inflation and hedging outcomes.
- Labor rate, headcount, and overtime.
- Volume-driven variable costs.
- FX translation and transaction effects.
- One-off restructuring, legal, or impairment charges.

### 5. Classify timing versus permanent

Every material variance gets a timing label:

| Label | Definition | Reforecast treatment |
| --- | --- | --- |
| Timing | Reverses within the fiscal year | Shift to a later period, no full-year change |
| Permanent | Does not reverse this year | Change the full-year landing |
| One-off | Non-recurring by nature | Exclude from run-rate, disclose |
| Mix or policy | Structural shift in business or accounting | Change the base assumption |

An order shipped a week late is timing. A lost customer is permanent. A price concession may be permanent even if it was booked as a one-off. Document the evidence for the label; this is where most reforecasts go wrong.

### 6. Rank materiality and build the bridge

Set thresholds before looking at results, using both absolute and relative tests. A common policy is `max(USD 50,000, 2% of the budget line)` or any item above 5% of the total variance, but use the thresholds approved by the finance team.

Produce a bridge that sums to the total variance:

```
Budget
  + volume
  + mix
  + price
  + cost inflation
  + FX
  + timing
  + one-offs
  +/- other (itemized, never a plug)
= Actual
```

A residual above rounding tolerance means the decomposition is incomplete. Find the missing driver; do not label it "other" without explanation.

### 7. Write commentary and reforecast

For each material line, record: variance amount and percentage, driver, evidence, action, owner, and full-year impact. Then reforecast:

```
FY landing = YTD actual + forecast for remaining periods
```

Build the remaining-period forecast from run-rate, known commitments, pipeline, and timing shifts. Compare the landing to budget and to the prior forecast, and show the walk between them. Update only the assumptions that changed; keep version control.

## Validation

| Gate | Test | Fail action |
| --- | --- | --- |
| Basis | Actuals and budget use the same scope, policy, and FX | Restate before analysis |
| Budget version | Approved version and date recorded | Re-obtain |
| Flex | Flexed variable costs = budget rate * actual volume | Recalculate |
| Decomposition | Volume + mix + price = actual revenue - budget revenue within 0.5% or 1 unit | Fix formula |
| Bridge | Components sum to total variance within rounding tolerance | Find missing driver |
| Signs | Favorable positive, unfavorable negative, consistently | Normalize |
| Materiality | All items above threshold have commentary | Complete before review |
| Timing labels | Evidence recorded for each timing or permanent call | Reclassify |
| Reforecast | YTD + remaining = FY landing; walk ties to prior forecast | Reconcile |
| Versioning | Budget, actuals, and forecast versions in the output | Add metadata |

## Gotchas

- Comparing actual variable costs to a static budget makes growth look like overspending. Always flex.
- Volume and mix are easily conflated. A favorable volume number can hide an unfavorable mix shift that lowers margin.
- Price variance should use actual volume. Using budget volume leaves a cross-term that contaminates the result.
- FX can create a variance in both revenue and cost. Separate translation from transaction effects, and state the rate source.
- Reclassifications between lines are not business variances. Restate or disclose them before ranking.
- A "one-off" that appears every quarter is recurring. Challenge the label with at least four quarters of history.
- Revenue ahead of plan can mask gross margin erosion. Bridge the margin percentage as well as the amount.
- Capex timing shifts depreciation and cash flow in later periods. A favorable capex variance is not always good news.
- Headcount savings from vacancies reverse when roles are filled. Treat as timing unless the role is eliminated.
- Sales cut-off and channel stuffing can pull revenue into the period. Check AR aging and returns after period end.
- A change in cost allocation moves variance between departments without changing the total. Show the allocation change separately.
- Percentage variances on small denominators are unstable. Suppress or annotate lines below a minimum base.

## Output contract

```json
{
  "period": "2026-10",
  "entity": "USCo",
  "currency": "USD",
  "versions": {"actuals": "GL-2026-10-final", "budget": "FY26-board-v3", "forecast": "FY26-fcst-2026-10"},
  "summary": {"budget": 62000, "actual": 62300, "variance": 300, "variance_pct": 0.5, "favorable": true},
  "decomposition": [
    {"driver": "volume", "amount": 3100, "favorable": true, "evidence": "unit sales report"},
    {"driver": "mix", "amount": -2100, "favorable": false, "evidence": "product A share up"},
    {"driver": "price", "amount": -700, "favorable": false, "evidence": "discount log"}
  ],
  "bridge_residual": 0,
  "material_lines": [
    {
      "line": "Product A price",
      "variance": -1400,
      "timing": "permanent",
      "commentary": "Competitive response cut realized price by 4%",
      "action": "Reprice or add value bundle",
      "owner": "vp-sales",
      "fy_impact": -16800
    }
  ],
  "reforecast": {"fy_budget": 744000, "fy_landing": 731000, "delta": -13000, "confidence": "medium"},
  "limitations": ["one customer shipment shifted to November"],
  "prepared_by": "fpna.analyst",
  "reviewed_by": "finance.director"
}
```

## Checklist

- [ ] Actuals, budget, and forecast versions recorded.
- [ ] Scope, policy, and FX basis aligned.
- [ ] Variable costs flexed to actual volume.
- [ ] Volume, mix, and price computed separately.
- [ ] Cost and margin decomposed on the same basis.
- [ ] Timing versus permanent classified with evidence.
- [ ] Materiality thresholds applied consistently.
- [ ] Bridge components sum to the total variance.
- [ ] Every material line has commentary, action, and owner.
- [ ] Reforecast ties to YTD actual plus remaining periods.
- [ ] Change in full-year landing explained.
- [ ] Second reviewer signs off before the business review.

## Related skills

- `deterministic-financial-modeling` for the budget and reforecast model behind the comparison.
- `three-statement-model-reconciliation` when the variance must flow through the financial statements.
- `working-capital-forecasting` when the driver is receivables, payables, or inventory.
- `kpi-dashboard-design` for presenting the variance pack to operators.
