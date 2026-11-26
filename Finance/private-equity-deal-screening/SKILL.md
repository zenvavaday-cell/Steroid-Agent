---
name: private-equity-deal-screening
description: Screens acquisition targets against investment thesis, financial quality, and value-creation levers. Use for sourcing, initial triage, and investment committee memos.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: finance
---

# Private Equity Deal Screening

## Overview

Screening turns a sourcing funnel into a small set of targets worth diligence budget. It is a triage against a pre-agreed thesis, not a full investment case. The output is a defensible pass, watch, or reject with the evidence behind it and the questions that must be answered next.

Two failure modes dominate. Thesis drift lets an attractive business outside the mandate consume weeks. False precision scores management-provided numbers as if they were audited. Both are controlled by writing hard gates before seeing the deal and tagging every data point by source quality.

## When to use

- Triaging inbound CIMs and banker teasers.
- Building or refreshing a sector target list.
- Screening add-ons for an existing platform.
- Deciding whether to fund a first-phase diligence budget.
- Preparing the screening section of an investment committee memo.
- Re-screening a target after new financials or a price change.

Do not use for final investment approval, which requires quality-of-earnings work, legal diligence, financing commitments, and a full model. Do not use to value a signed exclusivity position where the decision is price, not fit.

## Workflow

### 1. Write the thesis and hard gates first

Record these before opening the CIM:

| Gate | Example |
| --- | --- |
| Sector and sub-sector | Business services, compliance software |
| Geography | US and Canada |
| Enterprise value | 50,000,000 to 250,000,000 |
| Business model | Recurring revenue >= 60%, no hardware resale |
| Customer | B2B, no single customer > 25% of revenue |
| Financial floor | EBITDA >= 8,000,000, positive FCF |
| Growth | Organic revenue CAGR >= 8% over 3 years |
| Ownership | Control or path to control |
| Exclusions | No tobacco, gambling, sanctioned jurisdictions |

Hard gates are pass or fail. A target that fails a gate needs an explicit, documented exception approved by the investment committee, not a higher score elsewhere.

### 2. Build the target profile with source tags

Extract into one schema from the CIM, management presentation, audited accounts, and public filings. Tag every data point:

| Tag | Meaning | Use |
| --- | --- | --- |
| V | Verified against audited or filed data | Can support a gate |
| M | Management-claimed, not audited | Requires diligence |
| E | Analyst estimate or market data | Sensitivity only |

If the CIM and the audited accounts disagree, use the audited number and log the difference. A screen built entirely on M and E data can proceed only as a watch, not a pass.

### 3. Assess revenue quality

| Metric | Formula | What it reveals |
| --- | --- | --- |
| Recurring share | Recurring revenue / total revenue | Durability |
| Customer concentration | Top 10 revenue / total revenue | Renewal cliff risk |
| Gross logo churn | Logos lost / opening logos | Sales and service quality |
| Net revenue retention | (Opening cohort + expansion - contraction - churn) / opening cohort | Expansion engine |
| Contract length | Weighted average remaining term | Visibility |
| Backlog coverage | Backlog / next 12 months revenue | Forecast support |
| Organic growth | Total growth - acquired growth - FX | Real demand |
| Price versus volume | Price effect / volume effect | Quality of growth |

Define ARR, recurring, and churn exactly as the company does, then state whether those definitions match how the market prices the asset. A 95% "retention" that excludes downsells is not net revenue retention.

### 4. Test margins, cash conversion, and earnings quality

Reconcile reported EBITDA to adjusted EBITDA:

```
Reported EBITDA
  + owner compensation above market
  + documented one-offs
  + pro forma synergies (only if contracted)
  - recurring costs misclassified as one-off
  - underinvestment (deferred capex, maintenance, hiring)
= Adjusted EBITDA
```

Flag when adjustments exceed 25% of reported EBITDA, when addbacks recur across years, or when cash conversion is weak:

```
FCF conversion = (EBITDA - capex - change in NWC - cash tax) / EBITDA
Capex intensity = capex / revenue
Cash conversion cycle = DSO + DIO - DPO
```

Compare capex and working capital to revenue over at least three years. A business that grows receivables faster than revenue is buying growth with terms, not demand.

### 5. Size leverage and returns

Entry equity equals enterprise value minus net debt plus transaction fees. Set debt capacity at the lower of the covenant limit and the DSCR constraint:

```
max_debt = min(covenant_leverage * EBITDA, debt that keeps DSCR >= 1.5x)
DSCR = (EBITDA - capex - cash tax - change in NWC) / (interest + scheduled principal)
```

Then compute base and downside returns over the hold period:

```python
def irr(cash_flows, lo=-0.99, hi=1.0):
    def npv(rate):
        return sum(cf / (1 + rate) ** t for t, cf in enumerate(cash_flows))
    for _ in range(200):
        mid = (lo + hi) / 2
        if npv(mid) > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2

# Example only: -100 invested, 25 distribution in year 2, 140 exit in year 5
# irr([-100, 0, 25, 0, 0, 140]) -> check against the fund hurdle
```

Report MOIC as `total distributions / invested equity`. Show the entry multiple, exit multiple, leverage, and hold period that produce the return. If the base case needs multiple expansion to clear the hurdle, say so explicitly.

### 6. Quantify value-creation levers without double counting

| Lever | Evidence required | Example metric |
| --- | --- | --- |
| Organic growth | Pipeline, sales capacity, retention | Revenue CAGR uplift |
| Pricing | Price test, contract escalators, willingness to pay | Gross margin bps |
| Cost efficiency | Benchmarks, org chart, procurement | EBITDA bps |
| Operational | Site or system consolidation | Days, units, cost per transaction |
| Add-on M&A | Identified pipeline, multiples, synergies | EBITDA and multiple effect |
| Deleveraging | FCF after debt service | Net debt reduction |
| Multiple arbitrage | Entry versus comparable exit | Exit multiple delta |

Assign each lever an owner, a dollar range, and a confidence level. Confirm the base case does not already contain the same benefit. A plan that counts the same 200 bps of margin twice is the most common modeling error in screening.

### 7. Apply red flags, score, and decide

Hard-stop red flags, unless resolved:

- Auditor resignation, restatement, or qualified opinion.
- Related-party revenue or costs that cannot be separated.
- Customer concentration above the thesis limit with no contract.
- Revenue recognition practices that pull forward or gross up revenue.
- Undisclosed litigation, sanctions, or regulatory action.
- Key-person dependence with no succession or retention plan.
- Carve-out with stranded costs that exceed the synergy case.
- Leverage capacity below the minimum required to close.

Score the remaining targets on the weighted scorecard, for example: thesis fit 20, revenue quality 20, margin and cash conversion 15, growth 15, leverage and returns 15, value creation 10, management 5. Gates override the score. Record PASS, WATCH, or REJECT with the next diligence questions and a budget cap.

## Validation

| Gate | Test | Fail action |
| --- | --- | --- |
| Thesis recorded | Gates and exclusions dated before target review | Rewrite and restart |
| Source tags | Every metric has V, M, or E and an as-of date | Add before scoring |
| Financial tie-out | CIM figures tie to audited accounts or differences explained | Reconcile |
| EBITDA bridge | Reported to adjusted reconciles line by line | Rebuild |
| Returns math | MOIC and IRR recomputed from cash flows | Recalculate |
| Leverage | Debt capacity passes DSCR and covenant tests | Lower debt |
| Lever consistency | No benefit counted twice across base case and levers | Remove overlap |
| Red flags | All hard stops screened and dispositioned | Escalate |
| Recommendation | Consistent with gates, score, and evidence quality | Rewrite |
| Confidentiality | NDA, clean team, and MNPI controls recorded | Stop sharing |

## Gotchas

- CIM EBITDA is a marketing number. Rebuild it from the P&L and the bank statements before using a multiple.
- Addbacks that appear in three consecutive years are recurring costs. Move them back into EBITDA.
- Pro forma synergies are not EBITDA until contracted. Show them as a separate upside case.
- Customer concentration is often understated when sales run through distributors or group purchasing organizations. Trace to the ultimate payer.
- ARR definitions vary. Check whether it includes month-to-month contracts, implementation fees, or churned accounts.
- Churn can be flattered by a growing denominator or by excluding downsells. Recompute on a cohort basis.
- Capex intensity can be understated by deferred maintenance, capitalized labor, or operating leases. Normalize to a steady-state level.
- Working capital needs are seasonal. Use a monthly average or peak, not a single year-end balance.
- Multiple arbitrage assumes an exit multiple at or above entry. Stress a one-turn contraction in the downside case.
- Debt capacity depends on the covenant definition, not the headline leverage ratio. Read the definition.
- Management projections are usually hockey sticks. Haircut growth and margin to comparable history before screening.
- Carve-out financials include stranded costs and omit shared services. Build a standalone cost estimate.
- A minority stake may not give the control needed to execute the value-creation plan. Check governance and exit rights.
- Confidential information creates trading restrictions. Enforce clean-team rules and log who saw what.

## Output contract

```json
{
  "target": "Example Target Inc.",
  "screen_date": "2026-11-20",
  "thesis_version": "BS-2026-Q4",
  "recommendation": "WATCH",
  "hard_gates": [
    {"gate": "recurring_revenue_min", "required": 0.60, "actual": 0.72, "status": "pass", "source": "V"},
    {"gate": "customer_concentration_max", "required": 0.25, "actual": 0.31, "status": "fail", "source": "M"}
  ],
  "score": {"total": 68, "max": 100, "breakdown": {"thesis_fit": 15, "revenue_quality": 12, "margins": 11, "growth": 12, "leverage_returns": 10, "value_creation": 6, "management": 2}},
  "financials": {
    "revenue": 64000000,
    "reported_ebitda": 11200000,
    "adjusted_ebitda": 9800000,
    "adjustments_pct": 0.143,
    "fcf_conversion": 0.62,
    "organic_growth": 0.09,
    "net_leverage_at_close": 3.1
  },
  "returns": {"entry_multiple": 9.5, "exit_multiple": 9.5, "hold_years": 5, "moic": 2.1, "irr": 0.16, "downside_irr": 0.04},
  "value_levers": [
    {"lever": "pricing", "ebitda_impact": 1200000, "confidence": "medium", "owner": "operating-partner"},
    {"lever": "add-on M&A", "ebitda_impact": 2000000, "confidence": "low", "owner": "deal-team"}
  ],
  "red_flags": [
    {"flag": "top_customer_31pct", "severity": "high", "evidence": "CIM page 18", "next_step": "request contract and renewal history"}
  ],
  "diligence_questions": ["Is the top customer contract assignable on change of control?", "What is the standalone cost of the carve-out?"],
  "next_step": {"action": "management call", "budget_cap": 25000, "owner": "deal-lead"},
  "confidentiality": {"nda": true, "clean_team": true, "mnpi_log": "DL-2026-114"},
  "prepared_by": "deal-team.analyst",
  "reviewed_by": "investment-committee.chair"
}
```

## Checklist

- [ ] Thesis and hard gates recorded before target review.
- [ ] Sector, geography, size, and exclusions stated.
- [ ] Every metric tagged V, M, or E with an as-of date.
- [ ] CIM financials tied to audited accounts or differences logged.
- [ ] Revenue quality tested on a cohort basis.
- [ ] Reported to adjusted EBITDA reconciled line by line.
- [ ] Capex and working capital normalized over three years.
- [ ] Debt capacity passes DSCR and covenant tests.
- [ ] MOIC and IRR recomputed from cash flows.
- [ ] Value levers quantified without double counting.
- [ ] Hard-stop red flags screened and dispositioned.
- [ ] Recommendation, next step, and diligence budget recorded.

## Related skills

- `comparable-company-valuation` for entry and exit multiple benchmarks.
- `merger-model-accretion-dilution` when the target is a public or combined-entity transaction.
- `deterministic-financial-modeling` for the returns model and sensitivity tables.
- `covenant-breach-monitoring` for the debt capacity constraint in the leverage case.
