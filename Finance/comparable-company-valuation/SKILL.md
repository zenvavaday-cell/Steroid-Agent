---
name: comparable-company-valuation
description: Builds defensible comparable-company sets, normalizes multiples, and explains premium and discount adjustments. Use for relative valuation, IPO pricing, and fairness checks.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: finance
---

# Comparable Company Valuation

## Overview

Relative valuation answers one question: what is this business worth if the market prices similar businesses this way? The answer is only as defensible as the peer set and the consistency of the multiples. A comps table with mismatched periods, lease treatments, or share counts produces a precise-looking number with no evidentiary value.

The core discipline is to define the multiple before selecting the peers, apply the same definition to every company including the target, and explain every adjustment between the observed multiple and the multiple actually applied.

## When to use

- Valuing a private company, division, or portfolio holding where no market price exists.
- Setting an IPO price range or testing IPO readiness.
- Cross-checking a DCF in a fairness opinion or board memo.
- Sanity-checking a negotiated transaction price before signing.
- Benchmarking a public company against its sector.
- Testing whether sector trading levels have moved after a market event.

Do not use as the sole method for a control transaction, a pre-revenue company, or a distressed business whose earnings are negative or not representative.

## Workflow

### 1. Define the multiple and the measurement date

Write the definition down before touching a data source. The same words often mean different calculations.

| Decision | Options | Rule |
| --- | --- | --- |
| Capital measure | Enterprise value or equity value | EV multiples for capital-structure-neutral metrics; P/E for equity |
| Earnings period | LTM, NTM, or a named forecast year | One basis for target and every peer |
| EBITDA definition | Reported, adjusted, pre/post SBC, pre/post rent | Identical treatment for all companies |
| Price date | One market close | State date and timezone; do not mix dates |
| Currency | Reporting currency or USD | Convert flows at average rate, balances at spot |

### 2. Screen the peer universe

Set objective criteria and record every exclusion with a reason.

- Same industry or business model, with revenue overlap of at least 60% by segment.
- Size between 0.3x and 3.0x the target's revenue or enterprise value.
- Similar geography, end markets, and customer concentration.
- Comparable growth and margin profile when the sector dispersion is wide.
- Sufficient free float and trading liquidity; flag controlled companies.
- Exclude companies with pending takeovers, restructuring, fresh IPO lockups, or divergent accounting.

Target 6 to 12 peers, with 5 as the practical minimum. If fewer than 5 survive, widen the size band and disclose the limitation rather than filling the set with poor matches.

### 3. Collect and calendarize the financials

Fiscal year ends rarely align. Calendarize each peer to the target's measurement period using quarterly or semiannual data.

```text
Calendarized LTM revenue =
    last reported fiscal year revenue
  + current-year stub revenue
  - prior-year stub revenue
```

For NTM metrics, use consensus estimates and record the contributor count, estimate date, and whether the consensus is mean or median. Do not mix an actual LTM at one peer with an NTM estimate at another.

### 4. Build the enterprise value bridge consistently

```text
Market capitalization = diluted shares x share price

Diluted shares = basic shares
               + in-the-money options (treasury stock method)
               + unvested RSUs and performance awards expected to vest
               + dilutive convertible securities

Enterprise value = market capitalization
                 + total debt (short and long term)
                 + preferred equity
                 + non-controlling interests
                 + operating lease liabilities (if EBITDA is after rent)
                 + unfunded pension deficit
                 - cash and cash equivalents
                 - non-operating investments
```

| Balance sheet item | In enterprise value | Treatment note |
| --- | --- | --- |
| Cash | Subtract | Exclude restricted, trapped, or customer float |
| Short-term investments | Subtract | Only if genuinely non-operating |
| Debt | Add | Include finance leases and drawn revolver |
| Operating leases | Add | Only when EBITDA is post-rent under IFRS 16 |
| Non-controlling interests | Add | Market value or a stated book proxy |
| Preferred stock | Add | Liquidation value or market value |
| Equity-method investments | Subtract | If non-consolidated and non-operating |
| Deferred tax liabilities | Usually exclude | Exclude unless the multiple is explicitly after-tax |

### 5. Calculate multiples and robust statistics

Compute EV/EBITDA, EV/EBIT, EV/Sales, and P/E where the denominator is positive and meaningful. Report every peer's multiple, not only the summary.

| Statistic | Use |
| --- | --- |
| Median | Primary point estimate; resistant to one large outlier |
| 25th and 75th percentile | Valuation range |
| Harmonic mean | Averaging P/E ratios when equal-weighting |
| Coefficient of variation | Dispersion test; above 0.30 suggests a regression or segmentation |

Exclude negative denominators. Exclude multiples above 40x or below 3x unless the business model justifies it, and list every exclusion. A mean is not a substitute for judgment: one 60x peer can move a six-company mean by more than 5x.

### 6. Adjust for real differences

| Adjustment | Typical range | Evidence required |
| --- | --- | --- |
| Control premium | 15% to 40% | Precedent transactions; not derivable from trading comps |
| Discount for lack of marketability | 10% to 30% | Restricted-stock studies or put-option models |
| Size premium | 0% to 20% | Decile analysis with stated source |
| Growth or margin differential | Regression residual | Peer regression with reported R-squared |
| Liquidity discount | 0% to 15% | Position size versus average daily traded value |
| Country risk | Sovereign spread | CDS or sovereign yield spread at the valuation date |

Apply a control premium once, and only when valuing a controlling stake. Trading comparables already reflect minority-market pricing. Never add a control premium and synergies to the same valuation without showing them as separate, labeled layers.

### 7. Apply the range and triangulate

Apply the selected multiple to the target metric, bridge from enterprise value to equity value, and present a range rather than a point.

```text
Illustrative example only:
Target NTM EBITDA            85.0
Peer EV/EBITDA p25            8.4x
Peer EV/EBITDA median         9.1x
Peer EV/EBITDA p75           10.2x
Implied enterprise value     714.0 to 867.0
Less net debt                210.0
Implied equity value         504.0 to 657.0
Midpoint equity value        563.5
```

Show the comps range next to a DCF range, precedent transactions, and the 52-week trading range. If the comps result differs from the DCF by more than 25%, explain why before selecting a point.

## Validation

| Gate | Test | Pass criterion | Fail action |
| --- | --- | --- | --- |
| EV bridge | Recomputed EV versus bridge | Difference <= 1.0% | Recheck debt, cash, NCI, leases |
| Share count | Diluted count versus filing | Exact match to disclosed diluted count | Rebuild treasury stock method |
| Period consistency | Target and peers all LTM or all NTM | 100% on one basis | Restate or remove the peer |
| Calendarization | Non-December year ends restated | Documented for each peer | Recalculate stub |
| Multiple math | EV / denominator versus reported multiple | Difference <= 0.01x | Fix the input, not the output |
| Outliers | Negative or extreme multiples handled | Every exclusion listed with reason | Restore or document |
| Sample size | Count of included peers | At least 5, or limitation disclosed | Widen criteria and disclose |
| Cross-check | Comps midpoint versus DCF midpoint | Within 25%, or variance explained | Investigate assumptions |
| Premium logic | Adjustment applied to correct base | No double counting | Remove the duplicate layer |
| Price date | All market data same date | Exact date match | Refresh prices |

## Gotchas

- Mixing LTM at some peers with NTM at others can shift the median by several turns. Enforce one basis.
- A June fiscal year end compared with a December target without calendarization mismatches the earnings season by up to six months.
- Cash is not always excess cash. Restricted cash, trapped cash in a subsidiary, and customer float must be excluded from the EV bridge.
- Omitting non-controlling interests understates EV and overstated multiples for companies with consolidated minorities.
- IFRS 16 leases raise EBITDA and debt together. Comparing an IFRS 16 peer with a pre-ASC 842 US peer without adjustment is not a comparison.
- Stock-based compensation added back at one company and expensed at another changes EBITDA by several points in technology.
- Basic shares instead of diluted shares understates market capitalization and EV.
- Cyclical companies at peak earnings look cheap on LTM multiples. Normalize through-cycle EBITDA or use a mid-cycle estimate.
- Negative EBITDA makes EV/EBITDA meaningless. Switch to EV/Sales or a DCF and say so.
- A control premium applied on top of a transaction multiple double counts the control value already embedded in the price.
- Selecting peers after seeing the answer is confirmation bias. Freeze the criteria before computing the range.
- Applying an EV multiple to net income, or a P/E to EBITDA, is a category error that survives surprisingly often in board decks.

## Output contract

```json
{
  "target": "Example Target Inc",
  "valuation_date": "2026-11-25",
  "metric_basis": "EV/EBITDA NTM",
  "currency": "USD",
  "peers": [
    {
      "ticker": "EXMPL",
      "name": "Example Peer Corp",
      "included": true,
      "exclusion_reason": null,
      "enterprise_value": 12400.0,
      "metric": 1360.0,
      "multiple": 9.12,
      "calendarized": true
    }
  ],
  "statistics": {"n": 7, "p25": 8.4, "median": 9.1, "p75": 10.2, "mean": 9.3, "cv": 0.18},
  "adjustments": [
    {"type": "control_premium", "value_pct": 20.0, "rationale": "controlling stake; precedent range"}
  ],
  "implied_value": {"low": 504.0, "mid": 563.5, "high": 657.0, "basis": "equity value"},
  "cross_checks": [{"method": "DCF", "midpoint": 590.0, "variance_pct": 4.5}],
  "exclusions": [{"ticker": "NEG", "reason": "negative LTM EBITDA"}],
  "limitations": ["peer set concentrated in one geography"],
  "prepared_by": "analyst",
  "reviewed_by": "manager"
}
```

## Checklist

- [ ] Multiple definition, period, and price date written down first.
- [ ] Peer criteria frozen before screening.
- [ ] Every exclusion has a recorded reason.
- [ ] At least five credible peers, or the limitation is disclosed.
- [ ] Financials calendarized to the target period.
- [ ] EV bridge built on one consistent lease and cash definition.
- [ ] Diluted share count reconciles to the filing.
- [ ] Multiples recomputed from raw inputs.
- [ ] Outliers and negative denominators removed and listed.
- [ ] Adjustments applied once, with evidence and range.
- [ ] Range triangulated against a DCF and precedent transactions.
- [ ] Variance above 25% explained in writing.

## Related skills

- `deterministic-financial-modeling` for the DCF cross-check and assumption register.
- `live-market-data-retrieval` for price, share count, and consensus data with timestamps.
- `sec-filing-extraction` for debt, leases, NCI, and diluted share detail from filings.
- `capital-structure-optimization` for interpreting how leverage changes the equity value bridge.
