---
name: fx-exposure-hedging-analysis
description: Maps currency exposure, evaluates hedge ratios, and quantifies scenario P&L for forwards, options, and natural hedges. Use for treasury risk reviews and hedge policy design.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: finance
---

# FX Exposure and Hedging Analysis

## Overview

Currency risk is not one exposure but three: transaction exposure from foreign-currency receivables, payables, and forecast cash flows; translation exposure from consolidating foreign subsidiaries; and economic exposure from changes in competitiveness. Each has a different horizon, measurement basis, and hedge treatment.

The discipline is to build one exposure register per currency and period, net natural offsets before buying derivatives, apply hedge ratios by certainty bucket, and show scenario P&L for both hedged and unhedged positions. A hedge is valid only when its notional, tenor, and accounting treatment match the exposure it protects.

## When to use

- Reviewing treasury FX risk before a board, audit committee, or risk committee.
- Designing or revising a hedge policy with ratio bands and permitted instruments.
- Quantifying currency sensitivity of a budget, forecast, or contract bid.
- Evaluating a proposed forward, FX swap, option, or zero-cost collar.
- Testing hedge accounting eligibility and documentation.
- Reviewing counterparty, collateral, and tenor limits on FX derivatives.
- Explaining a realized FX gain or loss against a prior forecast.

Do not use for speculative currency trading, or for a single immaterial invoice where the analysis cost exceeds the exposure.

## Workflow

### 1. Define the exposure perimeter

State the reporting currency, the entities in scope, and the consolidation method. Separate the three exposure types before combining anything:

| Exposure | Source | Horizon | Typical hedge |
| --- | --- | --- | --- |
| Transaction, committed | Firm purchase orders, executed contracts, booked AR and AP | 0 to 12 months | Forwards, FX swaps |
| Transaction, forecast | Budgeted sales, purchases, royalties, intercompany fees | 3 to 24 months | Forwards, options, collars |
| Translation | Net assets and earnings of foreign subsidiaries | Reporting period | Net investment hedge, debt designation |
| Economic | Pricing competitiveness, offshore cost base | 1 to 5 years | Natural hedge, operating changes |

Document the pair convention (base/quote), the sign convention (inflow positive), and the rate source and timestamp. Mixing conventions is the most common source of a wrong hedge direction.

### 2. Build the exposure register

One row per currency, entity, period, and cash-flow type:

```csv
exposure_id,entity,currency,period,cashflow_type,amount_ccy,amount_reporting,rate_source,confidence,contract_ref
FX-001,USCo,EUR,2027-01,AR_collection,4000000,4400000,ECB_2026-11-20,committed,SO-1042
FX-002,USCo,EUR,2027-01,payroll,1200000,1320000,ECB_2026-11-20,probable,HR-plan-v3
```

Net each currency per period: `net_exposure = inflows - outflows`. Show gross inflows, gross outflows, natural offsets, and net before any derivative. A receivable in EUR and a payable in EUR in the same month is a natural hedge and should not be double-hedged.

Reconcile booked items to the general ledger at the closing rate for the reporting date. Reconcile forecast items to the approved budget or latest forecast version, and record the version.

### 3. Apply hedge ratios by certainty

Set ratios by evidence quality, not by view on the currency:

| Certainty | Evidence | Indicative hedge ratio |
| --- | --- | --- |
| Committed | Executed contract or booked item | 90% to 100% |
| Highly probable | Approved budget, firm pipeline, purchase plan | 50% to 80% |
| Forecast | Early pipeline, unspecified timing | 0% to 50% |
| Translation | Net investment in subsidiary | Policy choice, often 0% to 100% |

`hedge_ratio = hedged_notional / net_exposure` per currency and tenor bucket. Never exceed 100% of committed exposure: an over-hedge is a speculative position and can create accounting and governance problems.

### 4. Price and compare instruments

Covered interest parity sets the fair forward rate for a base/quote pair:

```
F = S * (1 + r_quote * days / basis) / (1 + r_base * days / basis)
```

Use actual day-count conventions (ACT/360 for most currencies, ACT/365 for GBP) and the same rate source for spot and deposits. Test the quoted forward against this calculation; a difference beyond a few basis points needs an explanation (cross-currency basis, credit, rounding).

Compare instruments on cost, flexibility, and accounting:

| Instrument | Payoff | Best use | Main risk |
| --- | --- | --- | --- |
| Forward | Locks a rate | Committed and highly probable flows | Opportunity cost, credit line usage |
| FX swap | Near-leg plus far-leg | Rolling short-dated exposures, liquidity | Rollover and basis risk |
| Put or call | Right, not obligation | Forecast flows, budget protection | Premium cost, time decay |
| Zero-cost collar | Buy option, sell opposite option | Reduce premium, accept a band | Capped upside, accounting complexity |
| Natural hedge | Match currency revenue and costs | Structural, long-term | Limited by operating footprint |

For a hedge selling EUR forward at `F0`, the derivative P&L at spot `S_T` is `notional * (F0 - S_T)` in USD. Adding the exposure P&L `notional * (S_T - S_budget)` shows the locked result on the hedged portion: `notional * (F0 - S_budget)`.

### 5. Build the scenario grid

Use at least five spot shocks, symmetric around the budget rate, and show the residual after hedges. Illustrative example: EUR 10,000,000 receivable, budget rate 1.10 USD/EUR, 80% hedged at 1.095.

| Spot USD/EUR | Unhedged P&L vs budget | Hedged P&L vs budget | Residual unhedged |
| --- | --- | --- | --- |
| 1.00 | -1,000,000 | -240,000 | 2,000,000 EUR |
| 1.05 | -500,000 | -140,000 | 2,000,000 EUR |
| 1.10 | 0 | -40,000 | 2,000,000 EUR |
| 1.15 | +500,000 | +60,000 | 2,000,000 EUR |
| 1.20 | +1,000,000 | +160,000 | 2,000,000 EUR |

These figures are illustrative arithmetic, not a market forecast. Report the maximum residual loss against the policy limit, not only the expected case. Add a 99% one-day or one-month VaR or expected shortfall as a secondary limit measure, and state the method and confidence level.

### 6. Test hedge accounting treatment

For IFRS 9, document the economic relationship, the risk management objective, and the absence of factors that would dilute it. For ASC 815, prepare contemporaneous documentation, identify the hedged forecast and the probability assessment, and choose an effectiveness method.

| Item | Required evidence |
| --- | --- |
| Hedged item | Contract, forecast, or net investment, with amount and timing |
| Hedging instrument | Trade confirmation, counterparty, notional, maturity |
| Risk component | Which risk is hedged, and why it is separately identifiable |
| Effectiveness method | Dollar offset, regression, or qualitative assessment |
| Reclassification | Where OCI or the basis adjustment goes on settlement |
| Discontinuation | What triggers it and how the basis is released |

A commonly used diagnostic band for dollar-offset testing is 80% to 125%, but current standards are principle-based. Do not present that band as a bright-line test.

### 7. Validate, approve, and monitor

Run the validation gates below, obtain approval under the delegated authority matrix, and record the trade rationale. Monitor mark-to-market, collateral calls, remaining notional versus exposure, and any change in forecast that makes a hedge ineffective or excessive.

## Validation

| Gate | Test | Fail action |
| --- | --- | --- |
| Exposure completeness | Booked exposure ties to GL at closing rate within 0.5% | Reconcile before hedging |
| Register integrity | Net = inflows - outflows - natural offsets per currency-period | Fix sign or mapping |
| Hedge ratio | 0 <= ratio <= policy maximum per bucket | Reduce or reclassify notional |
| Over-hedge | Hedged notional <= committed exposure + approved forecast | Unwind excess or document exception |
| Forward fairness | Quoted forward within tolerance of covered interest parity | Query counterparty |
| Scenario math | Hedged plus unhedged legs equal total exposure P&L | Recalculate |
| Limit test | Max residual loss and VaR within policy limits | Escalate to risk committee |
| Counterparty | Notional and tenor within ISDA and CSA limits | Trade with another counterparty |
| Accounting | Documentation complete before trade date | Do not designate |
| Approval | Trade within delegated authority | Escalate |

## Gotchas

- Hedging a net exposure that already includes a natural offset creates a double hedge. Net first, then hedge.
- Over-hedging a forecast that later shrinks forces an unwind at a loss and can fail hedge accounting. Cap ratios by certainty.
- The budget rate is not the market rate. Measuring hedge P&L against budget mixes execution performance with forecast error.
- Forward points are interest, not a forecast. A forward rate above spot does not predict appreciation.
- A zero-cost collar is not free. The sold option caps upside and carries mark-to-market and accounting risk.
- Cross-currency basis and counterparty credit can make the quoted forward deviate from textbook parity, especially at long tenors.
- Translation exposure is not hedged by a forward that settles in cash against earnings. A net investment hedge requires the right designation.
- Intercompany balances can create offsetting exposures that are eliminated on consolidation. Map them at the legal-entity level.
- Option premiums paid in one currency create a second exposure. Include premium and collateral cash flows in the register.
- FX moves change both the exposure and the hedge mark at once. Netted reporting can hide a broken relationship.
- A hedge that remains designated after the forecast is no longer probable must be discontinued prospectively. Monitor forecast revisions.
- Month-end spot rates used for translation are not the rates used for transaction settlement. Keep the rate table explicit.

## Output contract

```json
{
  "reporting_currency": "USD",
  "as_of": "2026-11-20",
  "policy_version": "FX-HP-2026.3",
  "exposures": [
    {
      "currency": "EUR",
      "period": "2027-Q1",
      "gross_inflows": 10000000,
      "gross_outflows": 3000000,
      "natural_offsets": 0,
      "net_exposure": 7000000,
      "hedge_ratio": 0.8,
      "hedged_notional": 5600000,
      "instruments": ["forward 1.0950"],
      "residual_unhedged": 1400000
    }
  ],
  "scenario_grid": [
    {"shock_pct": -0.10, "spot": 0.99, "unhedged_pnl": -770000, "hedged_pnl": -210000}
  ],
  "limits": {"max_residual_loss": 250000, "var_99_1m": 180000, "status": "pass"},
  "accounting": {"standard": "IFRS 9", "designated": true, "effectiveness": "pass", "oci_balance": 0},
  "counterparties": [{"name": "Bank A", "notional": 5600000, "limit": 20000000, "collateral_posted": 0}],
  "actions": ["extend 2027-Q2 cover to 60%", "review EUR payroll natural hedge"],
  "prepared_by": "treasury.analyst",
  "approved_by": "treasury.head",
  "evidence_hash": "sha256:..."
}
```

## Checklist

- [ ] Reporting currency, pair convention, and sign convention stated.
- [ ] Transaction, translation, and economic exposures separated.
- [ ] Booked exposure reconciled to the GL.
- [ ] Forecast exposure tied to an approved budget or forecast version.
- [ ] Natural offsets netted per currency and period.
- [ ] Hedge ratios assigned by certainty and within policy.
- [ ] Forward pricing checked against covered interest parity.
- [ ] Scenario grid shows hedged, unhedged, and residual P&L.
- [ ] Residual loss and VaR tested against limits.
- [ ] Counterparty and collateral exposure within ISDA and CSA limits.
- [ ] Hedge accounting documentation complete before designation.
- [ ] Approval recorded within delegated authority.

## Related skills

- `debt-schedule-waterfall` for the interest and liquidity effect of FX debt and collateral.
- `covenant-breach-monitoring` for leverage ratios that move with translation rates.
- `liquidity-stress-testing` for combining FX shocks with funding stress.
- `deterministic-financial-modeling` for wiring the scenario grid into an auditable model.
