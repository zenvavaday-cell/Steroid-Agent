---
name: covenant-breach-monitoring
description: Extracts loan covenant definitions, computes financial ratios from ledger and management data, tracks headroom and cure periods, and alerts before a breach. Use for credit agreement monitoring, lender reporting, portfolio surveillance, and early-warning covenant analysis.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: finance
---

# Covenant Breach Monitoring

## Overview

A covenant is a contractual test with a specific definition, test date, and consequence. Monitoring requires reading the definition exactly, computing it from the right data, and alerting on headroom before the test date, not after.

The same ratio name can mean different things in two agreements. Never reuse a calculation without checking the definition.

## When to use

- Monitoring a loan portfolio or a single credit agreement.
- Preparing a compliance certificate.
- Forecasting covenant headroom under a downside case.
- Reviewing a borrower's reported covenant calculation.
- Assessing cross-default risk.

## 1. Extract the covenant terms

Build a structured record for every covenant:

```json
{
  "covenant_id": "COV-001",
  "type": "financial",
  "test": "maximum_total_leverage",
  "definition": "Consolidated Funded Debt / Consolidated EBITDA",
  "threshold": 4.50,
  "direction": "max",
  "test_frequency": "quarterly",
  "test_dates": ["2026-03-31", "2026-06-30", "2026-09-30", "2026-12-31"],
  "lookback": "trailing twelve months",
  "ebitda_addbacks": ["stock comp", "one-time restructuring", "acquisition synergies"],
  "addback_caps": {"restructuring": 0.10},
  "cure_right": {"type": "equity", "amount": 0.20, "period_days": 10},
  "grace_period_days": 5,
  "cross_default": true,
  "source": "Credit Agreement §7.11, page 42"
}
```

If the definition is ambiguous, quote it and escalate to legal. Do not guess.

## 2. Map definitions to data

| Covenant input | Source | Adjustment |
| --- | --- | --- |
| Funded debt | Debt schedule | Include capital leases per definition |
| EBITDA | Management accounts | Apply permitted addbacks and caps |
| Interest expense | GL | Net of capitalized interest if specified |
| Capex | Fixed asset register | Exclude acquisitions if specified |
| Liquidity | Bank statements | Exclude trapped cash |
| Fixed charges | GL | Include scheduled principal |

Document every mapping. A covenant calculation that cannot be tied to the ledger is not auditable.

## 3. Compute the ratios

```python
def leverage(funded_debt, ebitda):
    return funded_debt / ebitda if ebitda else float("inf")

def interest_coverage(ebitda, interest_expense):
    return ebitda / interest_expense if interest_expense else float("inf")

def dscr(cash_flow_available, debt_service):
    return cash_flow_available / debt_service if debt_service else float("inf")

def headroom(value, threshold, direction):
    if direction == "max":
        return (threshold - value) / threshold
    return (value - threshold) / threshold
```

Report the ratio, the threshold, the absolute headroom, and the percentage headroom.

## 4. Build the early-warning ladder

| Headroom | Status | Action |
| --- | --- | --- |
| > 25% | Green | Routine monitoring |
| 10–25% | Amber | Notify credit owner, request forecast |
| 0–10% | Red | Prepare waiver or cure plan |
| < 0% | Breach | Escalate, assess cross-default, notify legal |

Thresholds should reflect volatility and the reliability of the data, not only the contractual limit.

## 5. Forecast headroom

Run the covenant test on:

- Last twelve months actuals.
- Management budget.
- Downside case with revenue and margin shocks.
- Liquidity stress case.

Show the month or quarter in which the covenant would breach under each scenario. A single-point calculation is not monitoring.

## 6. Manage the test cycle

- Confirm the test date and the reporting deadline.
- Obtain the compliance certificate and supporting calculations.
- Recompute independently.
- Compare the borrower's calculation to yours and reconcile differences.
- Record sign-off and any waiver or amendment.
- Track cure rights and their deadlines.

## 7. Escalate

A breach or likely breach triggers the human-in-the-loop process. Include the calculation, the definition, the evidence, the cure options, and the cross-default exposure.

## Gotchas

- EBITDA addbacks are where definitions diverge. Apply caps, lookback limits, and pro forma rules exactly.
- Trailing-twelve-month calculations mix audited and unaudited quarters. Document the basis.
- An equity cure may reset the covenant but dilute the sponsor. Model the effect.
- Cross-default can be triggered by a breach in another facility, including a subsidiary's.
- Minimum liquidity covenants may be tested more frequently than quarterly.
- FX translation can push a ratio over the limit even if operations are unchanged.
- Covenant holidays and step-downs change the threshold over time. Build the schedule.
- A late compliance certificate can itself be a default. Track deadlines.

## Output contract

```json
{
  "borrower": "Example Holdings",
  "facility": "Term Loan B",
  "test_date": "2026-09-30",
  "covenants": [
    {
      "id": "COV-001",
      "ratio": "total leverage",
      "value": 4.12,
      "threshold": 4.50,
      "headroom_pct": 8.4,
      "status": "red",
      "definition_source": "§7.11",
      "data_sources": ["GL 2026-09", "debt schedule v4"],
      "forecast_breach": "2027-Q1 in downside case"
    }
  ],
  "cross_default_exposure": 25000000,
  "actions": ["request waiver", "prepare equity cure"],
  "prepared_by": "...",
  "reviewed_by": "..."
}
```

## Checklist

- [ ] Covenant definition quoted and source cited.
- [ ] Threshold, direction, test dates, and lookback captured.
- [ ] Addbacks and caps applied exactly.
- [ ] Inputs mapped to ledger sources.
- [ ] Ratio, headroom, and status computed.
- [ ] Downside forecast run.
- [ ] Cure and grace periods tracked.
- [ ] Escalation and sign-off recorded.

## Related skills

- `credit-risk-scoring-pipeline` for portfolio-level risk.
- `liquidity-stress-testing` for the downside scenario.
- `human-in-the-loop-escalation` for breach decisions.
