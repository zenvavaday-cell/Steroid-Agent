---
name: merger-model-accretion-dilution
description: Models pro forma EPS accretion or dilution, synergies, financing mix, and breakeven assumptions for a merger. Use for M&A screening and board materials.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: finance
---

# Merger Model: Accretion and Dilution

## Overview

An accretion/dilution model answers a narrow question: does the combined company earn more or less per share than the acquirer would have earned alone? It is not a valuation. A deal can be accretive and destroy value, or dilutive and create it, depending on the price paid and the return on the acquired assets.

The model must still be exact. Sources and uses must balance, the purchase price allocation must close, the share count must reconcile, and the EPS bridge must be auditable line by line.

## When to use

- Screening a public-company acquisition for EPS impact.
- Preparing board materials that compare cash, stock, and mixed consideration.
- Testing whether synergies are large enough to offset dilution.
- Setting a maximum price or maximum synergy assumption for a deal.
- Comparing an acquisition with a buyback on EPS and leverage.
- Explaining a deal's pro forma capital structure and ownership split.

Do not use for valuing a private target with no observable share price, for a merger of equals where ownership and governance dominate the analysis, or as a substitute for a DCF or IRR-based underwriting.

## Workflow

### 1. Lock the transaction terms

Record every term with a source before calculating:

| Term | Example | Source |
| --- | --- | --- |
| Offer price per target share | USD 42.00 | Term sheet |
| Premium to unaffected price | 28% | Market data on announcement date |
| Consideration mix | 60% cash, 40% stock | Term sheet |
| Acquirer share price used for exchange | USD 35.00 | Fixed exchange or fixed value, stated |
| Target fully diluted shares | 50.0 million | Treasury stock method |
| Target debt refinanced | USD 400 million | Credit agreement |
| Transaction fees | USD 45 million | Advisor estimates |
| Expected close | 2027-06-30 | Announcement |

State whether the stock consideration is a fixed exchange ratio or a fixed dollar amount. The two produce different share counts if the acquirer's price moves before close.

### 2. Build sources and uses

```text
Uses:
  Equity purchase price        = offer price x fully diluted target shares
  Refinance target debt        = principal + call premium + accrued interest
  Transaction fees             = advisory + legal + financing + other
  Cash to target balance sheet = optional, state purpose

Sources:
  New acquirer debt            = term loan + notes + drawn revolver
  Cash from acquirer balance sheet
  New acquirer equity          = stock consideration / acquirer share price
  Assumed target debt          = only if not refinanced

Check: total sources - total uses = 0 (tolerance 0.5 model units)
```

New shares issued = stock consideration / acquirer share price. If the acquirer uses a fixed exchange ratio, new shares = exchange ratio x target diluted shares.

### 3. Allocate the purchase price

```text
Consideration transferred          = equity purchase price
Plus: fair value of assumed debt   = only for the EV reconciliation, not goodwill
Plus: non-controlling interests    = fair value at acquisition
Less: fair value of identifiable net assets acquired
= Goodwill
```

Write up identifiable assets to fair value, including inventory, PP&E, and intangibles (customer relationships, technology, brand). Record the deferred tax effect of the write-ups at the applicable tax rate. Goodwill is the residual and is not amortized under US GAAP; definite-lived intangibles are amortized over their useful lives.

### 4. Model the financing

| Financing item | Calculation | P&L effect |
| --- | --- | --- |
| Term loan | Draw x rate x days / 360 | Interest expense |
| Bonds | Face x coupon, plus issuance discount amortization | Interest expense |
| Revolver | Drawn x rate + undrawn x commitment fee | Interest expense |
| Cash used | Cash balance x foregone interest rate | Lost interest income |
| Financing fees | Total fees / amortization period | Amortization expense |
| PIK tranche | Accrued rate, paid in kind | Interest expense, no cash |

Use the acquirer's marginal after-tax cost of debt, not the coupon on an existing facility, and apply the correct tax shield. If the deal closes mid-year, prorate the first period by days or months and state the convention.

### 5. Combine the income statements

Start from standalone acquirer and target net income, then add the deal effects:

```text
Pro forma net income =
    acquirer net income
  + target net income
  + after-tax run-rate synergies realized in the period
  - after-tax incremental interest expense
  - after-tax amortization of new intangibles
  - after-tax integration costs (if recurring in the period)
```

Adjust the target for any change in its own interest expense if its debt is refinanced. Remove target transaction costs that will not recur. Do not double count synergies that are already in the target's standalone forecast.

### 6. Rebuild the share count and compute EPS

```text
Pro forma diluted shares = acquirer diluted shares + new shares issued
Pro forma EPS           = pro forma net income / pro forma diluted shares
Accretion / dilution    = pro forma EPS / acquirer standalone EPS - 1
```

Also report:

- Ownership: acquirer existing holders and target holders as a percentage of pro forma shares.
- Pro forma net debt / EBITDA and interest coverage.
- The EPS bridge from standalone acquirer EPS to pro forma EPS, with each item labeled.

### 7. Calculate breakeven synergies and run sensitivities

Breakeven after-tax synergies are the amount that makes pro forma EPS equal standalone EPS:

```text
S* = standalone EPS x pro forma shares
     - (acquirer net income + target net income
        - after-tax financing cost - after-tax intangible amortization)

Pre-tax breakeven = S* / (1 - tax rate)
```

Illustrative example only: acquirer net income 300, shares 100, EPS 3.00; target net income 40; new shares 20; after-tax financing cost 18; after-tax intangible amortization 6; after-tax synergies 25.

```text
Pro forma net income = 300 + 40 + 25 - 18 - 6 = 341
Pro forma EPS        = 341 / 120 = 2.842
Accretion            = 2.842 / 3.00 - 1 = -5.3% (dilutive)
Breakeven after-tax synergies = 3.00 x 120 - (300 + 40 - 18 - 6) = 44.0
At a 25% tax rate, pre-tax breakeven = 44.0 / 0.75 = 58.7
```

Run a sensitivity grid over offer price, synergy level, consideration mix, and acquirer share price. Show EPS impact and pro forma leverage in each cell.

## Validation

| Gate | Test | Pass criterion | Fail action |
| --- | --- | --- | --- |
| Sources and uses | Total sources - total uses | Abs diff <= 0.5 | Find the missing fee or debt paydown |
| Ownership | Acquirer % + target % | 100.0% +/- 0.1% | Rebuild share count |
| Goodwill | Consideration - fair value net assets | Ties to PPA schedule | Recheck write-ups and deferred tax |
| PPA balance | Identifiable assets + goodwill | Equals consideration + liabilities assumed | Rebuild allocation |
| Share count | Opening + new shares | Equals pro forma diluted shares | Check treasury stock method |
| EPS bridge | Sum of EPS contributions | Equals pro forma EPS within 0.01 | Recheck tax and share effects |
| Tax | Pre-tax adjustments x tax rate | Equals tax effect used | Fix inconsistent rates |
| Target debt | Interest removed if refinanced | No double count | Check target standalone P&L |
| Fees | One-time versus amortized | Correct P&L treatment | Reclassify |
| Leverage | Pro forma net debt / EBITDA | Recomputed from pro forma balance sheet | Fix debt or EBITDA |

## Gotchas

- Accretion is not value creation. Compare the deal's return on invested capital with the acquirer's WACC before recommending it.
- Using the offer price to calculate the premium but the unaffected price to calculate the purchase price (or the reverse) produces an inconsistent headline.
- If target debt is assumed rather than refinanced, its interest stays in pro forma earnings and its principal stays in net debt. Removing both is a common double count.
- Transaction fees are usually expensed as incurred, while financing fees are capitalized and amortized. Treating them the same misstates the first-year EPS.
- Intangible amortization is not always tax deductible, particularly in stock acquisitions. Apply the correct tax effect or show it as a separate line.
- Synergies phase in over 12 to 36 months. A day-one run-rate assumption overstates first-year accretion.
- A fixed exchange ratio and a fixed value produce different share counts if the acquirer's stock moves before close. State which one is modeled.
- Target options and RSUs accelerate on change of control. Use the treasury stock method plus acceleration, not basic shares.
- Forgone interest on cash used is a real cost. Omitting it flatters accretion in all-cash deals.
- Integration costs are recurring more often than bankers admit. Show a base case that includes them.
- Stock buybacks funded with debt can be accretive and still increase risk. Always report pro forma leverage alongside EPS.
- Preferred dividends and participating securities reduce EPS available to common holders. Do not use unadjusted net income.

## Output contract

```json
{
  "deal": "Example Acquirer / Example Target",
  "announcement_date": "2026-11-26",
  "consideration": {"cash_pct": 60.0, "stock_pct": 40.0, "offer_price": 42.0, "acquirer_share_price": 42.0, "premium_pct": 28.0},
  "sources_uses": {
    "uses": {"equity_purchase_price": 2100.0, "refinance_debt": 400.0, "fees": 45.0},
    "sources": {"new_debt": 1400.0, "cash": 305.0, "new_equity": 840.0},
    "difference": 0.0
  },
  "purchase_price_allocation": {"goodwill": 980.0, "intangibles": 320.0, "write_ups": 110.0, "deferred_tax": -77.0},
  "pro_forma": {
    "net_income": 341.0,
    "diluted_shares": 120.0,
    "eps": 2.842,
    "standalone_eps": 3.0,
    "accretion_dilution_pct": -5.3,
    "net_debt_ebitda": 3.4
  },
  "breakeven": {"after_tax_synergies": 44.0, "pre_tax_synergies": 58.7},
  "sensitivities": [{"offer_price": 42.0, "synergies": 25.0, "eps_impact_pct": -5.3}],
  "assumptions": ["25% marginal tax rate", "full run-rate synergies in year one"],
  "prepared_by": "analyst",
  "reviewed_by": "manager"
}
```

## Checklist

- [ ] Offer price, premium, and consideration mix sourced and dated.
- [ ] Fixed exchange versus fixed value stated.
- [ ] Sources and uses balance to zero.
- [ ] Purchase price allocation closes with goodwill as the residual.
- [ ] Deferred tax on write-ups included.
- [ ] Financing costs and fees treated correctly.
- [ ] Target debt and interest removed only if refinanced.
- [ ] Synergies phased and after-tax.
- [ ] Share count includes options, RSUs, and new issuance.
- [ ] EPS bridge ties to pro forma EPS.
- [ ] Breakeven synergies calculated.
- [ ] Pro forma leverage and coverage reported with EPS.

## Related skills

- `deterministic-financial-modeling` for the integrated model, checks, and sensitivity mechanics.
- `comparable-company-valuation` for the offer price and premium benchmark.
- `private-equity-deal-screening` for the investment thesis and value-creation review.
- `capital-structure-optimization` for the pro forma leverage and financing decision.
