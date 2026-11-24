---
name: liquidity-stress-testing
description: Builds cash-flow ladders and stress scenarios, computes survival horizons and liquidity coverage, and identifies funding gaps and contingency actions. Use for treasury risk, bank liquidity reporting, corporate cash planning, fund liquidity, and reverse stress testing.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: finance
---

# Liquidity Stress Testing

## Overview

Liquidity risk is the risk of running out of cash at the wrong moment. Solvency is about the value of assets; liquidity is about timing. A stress test maps contractual and behavioral cash flows under adverse scenarios and asks: how many days or weeks can the entity meet its obligations?

The output is a survival horizon, a funding gap, and a prioritized action plan.

## When to use

- Corporate 13-week cash flow forecasting.
- Bank LCR, NSFR, or internal liquidity stress testing.
- Fund redemption and capital call analysis.
- Project finance debt service reserve review.
- Reverse stress testing: what has to happen for liquidity to fail?

## 1. Build the baseline cash ladder

Use weekly buckets for 13 weeks, or daily for a crisis. Separate:

| Category | Examples |
| --- | --- |
| Inflows | Collections, sales, draws, asset sales, tax refunds |
| Outflows | Payroll, suppliers, rent, debt service, taxes, capex |
| Financing | Revolver draws, repayments, interest, fees |
| Contingent | Guarantees, letters of credit, margin calls, litigation |
| Restrictions | Trapped cash, minimum operating balances, regulatory reserves |

Every line has an owner, a date, and a source. Behavioral assumptions are labeled, not disguised as contractual.

### 2. Define available liquidity

```
available_liquidity = unrestricted_cash
                    + undrawn_committed_facilities
                    + eligible_HQLA_after_haircuts
                    - minimum_operating_cash
                    - trapped_cash
                    - collateral_pledged
```

Do not count uncommitted facilities as available in stress. Do not double-count cash that secures a letter of credit.

### 3. Choose scenarios

At minimum:

- Idiosyncratic: customer concentration loss, fraud, litigation, rating downgrade.
- Market: credit spread widening, FX shock, commodity spike, asset price fall.
- Funding: wholesale funding withdrawal, revolver unavailability, fund redemptions.
- Operational: payment processor outage, cyber incident, key supplier failure.
- Combined: a market shock plus an idiosyncratic event.

Each scenario specifies the shock, the timing, the affected lines, and the behavioral response.

### 4. Apply behavioral assumptions

| Item | Baseline | Stress |
| --- | --- | --- |
| Receivables collection | 45 days | 70 days |
| Deposit runoff | 2%/month | 15% in 30 days |
| Revolver availability | 100% | 50% or 0% |
| Supplier terms | 30 days | 15 days |
| Customer prepayments | Normal | 30% decline |
| Margin calls | None | Collateral shortfall |

Document the evidence or expert judgment behind each assumption.

### 5. Compute the survival horizon

```python
def survival_horizon(opening_liquidity, net_flows):
    """net_flows: list of net cash flow per period (negative = outflow)."""
    liquidity = opening_liquidity
    for period, flow in enumerate(net_flows, start=1):
        liquidity += flow
        if liquidity < 0:
            return period, liquidity
    return None, liquidity
```

Also compute:

- Minimum liquidity and the period it occurs.
- Cumulative funding gap.
- Liquidity coverage ratio: available liquidity / net stressed outflows over the horizon.
- Days of cash on hand.

### 6. Run reverse stress testing

Find the combination of shocks that exhausts liquidity within the planning horizon. Report the breakeven assumptions, for example: "A 22% deposit runoff within 30 days, combined with a 30% revolver haircut, exhausts liquidity in week 6."

### 7. Build the contingency funding plan

For each gap:

| Action | Amount | Time to execute | Dependencies | Confidence |
| --- | --- | --- | --- | --- |
| Draw revolver | 50M | 2 days | Covenant compliance | High |
| Delay capex | 20M | 1 week | Board approval | Medium |
| Sell liquid securities | 30M | 3 days | Market access | Medium |
| Reduce dividend | 10M | 1 month | Board approval | High |

Rank by speed and certainty, not only by size.

## Gotchas

- Trapped cash in foreign subsidiaries or regulated entities is not available to the parent.
- Committed facilities can be unavailable due to covenants or material adverse change clauses.
- HQLA haircuts and eligibility differ by regime. Use the applicable rules.
- Intraday liquidity can fail even when end-of-day balances look fine.
- Contingent liabilities and guarantees are easy to omit.
- Deposit behavior is nonlinear. A small stress may have no effect; a large one can trigger a run.
- Wrong-way risk: collateral value falls exactly when you need to post more.
- FX moves change both the value of cash and the size of obligations.
- Legal entity, currency, and jurisdiction silos matter more than group-level totals.

## Output contract

```json
{
  "entity": "Example Corp",
  "as_of": "2026-11-24",
  "horizon_weeks": 13,
  "opening_liquidity": 120000000,
  "scenarios": [
    {
      "name": "combined stress",
      "survival_weeks": 7,
      "minimum_liquidity": -18000000,
      "minimum_week": 7,
      "coverage_ratio": 0.72,
      "key_assumptions": {"receivable_days": 70, "deposit_runoff_30d": 0.15}
    }
  ],
  "reverse_stress": "22% runoff + 30% revolver haircut exhausts liquidity in week 6",
  "actions": [{"action": "draw revolver", "amount": 50000000, "days": 2}],
  "triggers": ["liquidity < 30M", "coverage ratio < 1.0"]
}
```

## Checklist

- [ ] Cash ladder built with owners and sources.
- [ ] Available liquidity excludes trapped and pledged cash.
- [ ] Scenarios cover idiosyncratic, market, funding, and combined.
- [ ] Behavioral assumptions documented.
- [ ] Survival horizon and coverage ratio computed.
- [ ] Reverse stress test run.
- [ ] Contingency actions ranked by speed and certainty.
- [ ] Early-warning triggers defined.

## Related skills

- `covenant-breach-monitoring` for facility availability constraints.
- `deterministic-financial-modeling` for the underlying forecast.
- `human-in-the-loop-escalation` before activating contingency actions.
