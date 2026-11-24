---
name: portfolio-rebalancing-calculation
description: Computes cost- and tax-aware rebalancing trades from current holdings to target weights, respecting drift bands, minimum trade sizes, whole shares, restricted lists, cash, and lot selection. Use for wealth management, fund rebalancing, model portfolios, and periodic allocation reviews.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: finance
---

# Portfolio Rebalancing Calculation

## Overview

Rebalancing is a constrained trade-generation problem, not a single percentage calculation. The goal is to move a portfolio toward its target allocation while minimizing unnecessary turnover, taxes, and transaction costs, and while respecting real-world constraints.

Always show the trade plan and the resulting post-trade weights before anything is executed.

## When to use

- Periodic rebalancing of a model or client portfolio.
- Restoring target weights after market drift.
- Reinvesting cash or funding withdrawals.
- Transitioning to a new target allocation.
- Tax-loss harvesting combined with rebalancing.

## Inputs

| Input | Notes |
| --- | --- |
| Holdings | Symbol, quantity, price, cost basis, tax lots, currency |
| Targets | Target weight per asset class and security |
| Bands | Absolute or relative drift tolerance |
| Costs | Commission, spread, market impact, FX |
| Taxes | Short/long-term rates, wash-sale rules |
| Constraints | Restricted list, minimum trade, whole shares, cash buffer |
| Policy | Calendar, band, or hybrid trigger |

## Workflow

### 1. Value the portfolio

```python
def portfolio_value(positions, prices, fx):
    total = 0.0
    for p in positions:
        price = prices[p["symbol"]]
        total += p["quantity"] * price * fx.get(p["currency"], 1.0)
    return total
```

Use one valuation timestamp. Stale prices across positions create phantom drift.

### 2. Compute current and target weights

```python
def weights(positions, prices, fx):
    values = {
        p["symbol"]: p["quantity"] * prices[p["symbol"]] * fx.get(p["currency"], 1.0)
        for p in positions
    }
    total = sum(values.values())
    return {s: v / total for s, v in values.items()}, total
```

Target weights must sum to 1.0 within a stated tolerance. Include cash as an explicit line, not a residual.

### 3. Decide whether to trade

| Trigger | Rule |
| --- | --- |
| Calendar | Rebalance quarterly or annually |
| Band | Trade when any asset class drifts beyond its band |
| Hybrid | Check monthly, trade only outside bands |
| Cash flow | Rebalance with deposits or withdrawals first |

Band example: ±5% relative for equities, ±3% absolute for fixed income. Bands should reflect cost and risk, not round numbers.

### 4. Generate ideal trades

```python
def ideal_trades(current_value, target_weight, total_value):
    target_value = target_weight * total_value
    return target_value - current_value
```

Positive means buy, negative means sell. At the asset-class level, trades should net to zero before cash and costs.

### 5. Apply constraints

Process in this order:

1. Use available cash before selling, subject to the cash buffer.
2. Harvest losses in taxable accounts where permitted.
3. Sell from lots with the lowest tax cost, respecting long-term versus short-term rates and wash-sale windows.
4. Respect restricted lists and minimum trade sizes.
5. Round to whole shares where fractional shares are unavailable.
6. Recompute residual cash and post-trade weights.
7. If residual drift exceeds the band, iterate once with the rounded values.

### 6. Estimate costs and taxes

```
net_benefit = drift_reduction_benefit - trading_costs - tax_cost
```

Only trade when the net benefit is positive, unless the policy mandates restoration. Report the estimate and its assumptions.

### 7. Validate the plan

- Trades sum to the intended cash movement.
- Post-trade weights are closer to target than pre-trade weights.
- No restricted security is traded.
- No wash-sale violation.
- Cash buffer is maintained.
- Whole-share rounding does not create a new breach.
- Every trade has a reason and a lot reference.

## Gotchas

- Fractional shares change the rounding math. Confirm whether the custodian supports them.
- Wash-sale rules apply across accounts in some jurisdictions. Check before harvesting.
- Selling the wrong lot can cost more in taxes than the rebalance saves.
- FX movements create drift that is not a security decision. Separate currency hedging from asset allocation.
- Corporate actions between valuation and execution change quantities. Refresh positions before trading.
- Minimum trade sizes can make small accounts impossible to rebalance perfectly. Document the residual.
- Model portfolios may have tax overlays at the account level. Rebalance the account, not only the model.
- Transaction costs are uncertain. Use a conservative estimate and show sensitivity.

## Output contract

```json
{
  "as_of": "2026-11-24T15:00:00Z",
  "total_value": 1250000.00,
  "trigger": "band",
  "pre_trade_weights": {"EQUITY": 0.68, "BONDS": 0.27, "CASH": 0.05},
  "target_weights": {"EQUITY": 0.60, "BONDS": 0.35, "CASH": 0.05},
  "trades": [
    {"symbol": "VTI", "side": "SELL", "quantity": 357, "est_price": 280.10, "reason": "equity overweight", "lot": "2023-05-01"},
    {"symbol": "BND", "side": "BUY", "quantity": 762, "est_price": 131.20, "reason": "bond underweight"}
  ],
  "estimated_cost": 84.20,
  "estimated_tax": 1450.00,
  "post_trade_weights": {"EQUITY": 0.600, "BONDS": 0.350, "CASH": 0.050},
  "warnings": ["post-trade cash includes 21.30 residual before costs"]
}
```

## Checklist

- [ ] One valuation timestamp and FX source.
- [ ] Targets sum to one, including cash.
- [ ] Trigger policy applied.
- [ ] Ideal trades net to zero before costs.
- [ ] Cash buffer and minimum trade respected.
- [ ] Lot selection and wash-sale rules applied.
- [ ] Costs and taxes estimated.
- [ ] Post-trade weights recomputed and validated.

## Related skills

- `live-market-data-retrieval` for prices and FX.
- `deterministic-financial-modeling` for multi-period wealth projections.
- `human-in-the-loop-escalation` before executing trades above a threshold.
