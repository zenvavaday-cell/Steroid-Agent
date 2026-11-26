---
name: causal-inference-analysis
description: Estimates treatment effects with DAGs, matching, regression adjustment, and sensitivity checks. Use for product experiments and policy evaluation.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: data-ai
---

# Causal Inference Analysis

## Overview

A prediction answers "what will happen"; a causal estimate answers "what changed because of the treatment." The gap is confounding, selection, and reverse causation, and no amount of model fit closes it. Identification comes from design and assumptions, not from a larger estimator.

The discipline is to state the estimand, draw the causal graph, choose an estimator that matches the identification strategy, test the assumptions that can be tested, and quantify how strong an unmeasured confounder would need to be to overturn the result.

## When to use

- Evaluating a product, pricing, or policy change that was not cleanly randomized.
- Reading an observational cohort and asking whether exposure caused the outcome.
- Designing an experiment and choosing estimands, covariates, and power.
- Auditing a vendor or internal claim of "lift" or "impact."
- Combining experimental and observational evidence for a decision.
- Estimating heterogeneous effects for targeting or rollout decisions.
- Do not use when the question is purely predictive or when no plausible identification strategy exists; report the descriptive association instead.

## Workflow

### 1. Write the estimand before touching data

Specify:

- **Population**: who is eligible, and who is excluded.
- **Treatment**: version, dose, timing, and duration. "Exposed" must be unambiguous.
- **Outcome**: measure, window, and whether it is a surrogate.
- **Estimand**: ATE, ATT, CATE, or local average effect for compliers.
- **Time horizon**: immediate, 30-day, or cumulative.
- **Decision**: what action changes if the estimate is 0, positive, or negative.

Pre-register the primary outcome and the analysis plan. Write down the smallest effect that would change the decision (the minimum detectable or economically meaningful effect).

### 2. Draw the DAG and identify the effect

Build the graph from domain knowledge before estimation. Classify every variable:

| Role | Adjust? | Example |
| --- | --- | --- |
| Confounder | yes, blocks a backdoor path | price affects both promotion and sales |
| Mediator | no, it is part of the effect | promotion lowers price, which raises sales |
| Collider | no, conditioning opens a path | both treatment and outcome influence support contact |
| Instrument | use in IV design | random assignment lottery affects take-up only |
| Proxy confounder | adjust with caution | region correlates with income |

Use the backdoor criterion to choose adjustment sets and `dowhy` to check identification:

```python
from dowhy import CausalModel

model = CausalModel(data=df, treatment="promo", outcome="sales",
                    common_causes=["seasonality", "region", "prior_sales"])
identified = model.identify_effect(proceed_when_unidentifiable=False)
print(identified)
```

If the effect is not identified even with the graph, stop and redesign the study. A regression cannot fix a missing identification strategy.

### 3. Check the design assumptions in the data

- **Consistency**: the observed treatment version matches the one being estimated.
- **Positivity**: every covariate stratum has both treated and control units. Check propensity overlap.
- **SUTVA**: no interference between units and one treatment version. Marketplace and network experiments often violate this.
- **Exchangeability**: no unmeasured confounder after adjustment. This is an assumption, not a test.
- **Missing data**: report rates by treatment arm; differential missingness biases the estimate.
- **Attrition**: compare baseline characteristics of completers and dropouts.

### 4. Select the estimator that matches the design

| Design | Estimator | Key diagnostic |
| --- | --- | --- |
| Randomized A/B test | difference in means, CUPED with pre-period covariate | SRM check, balance |
| Observational cross-section | propensity weighting, matching, or AIPW | overlap, covariate balance |
| Panel with untreated units | difference-in-differences, event study | parallel pre-trends |
| Staggered adoption | Callaway-Sant'Anna or Sun-Abraham | group-time effects, not TWFE |
| Threshold rule | regression discontinuity | running variable manipulation, bandwidth |
| Encouragement or lottery | instrumental variables (2SLS) | first-stage F, exclusion restriction |
| Single treated unit over time | synthetic control | pre-period fit, placebo tests |

Propensity weighting with a doubly robust check:

```python
from sklearn.linear_model import LogisticRegression
import numpy as np

ps = LogisticRegression(max_iter=1000).fit(X, d).predict_proba(X)[:, 1]
w = np.where(d == 1, 1 / ps, 1 / (1 - ps))
ate = np.mean(w * (y - np.mean(y)))  # replace with an AIPW estimator for production
```

For 2SLS, report the first stage:

```python
from linearmodels.iv import IV2SLS

res = IV2SLS.from_formula("sales ~ 1 + seasonality + [promo ~ lottery]", data).fit(
    cov_type="clustered", clusters=data["store_id"])
print(res.first_stage)
```

### 5. Estimate with balance and overlap diagnostics

- Standardized mean difference (SMD) per covariate before and after adjustment: `abs(mean_t - mean_c) / sqrt((var_t + var_c) / 2)`. Target SMD `< 0.1`; investigate anything above 0.2.
- Propensity overlap: report the share of treated units with `ps < 0.01` or `ps > 0.99`. Trim or use overlap weights when it is material.
- Effective sample size after weighting: `(sum w)^2 / sum(w^2)`. A large weight concentration means the estimate rests on a few units.
- Cluster standard errors at the unit of treatment assignment, not the unit of observation.
- Report the estimate with a 95 percent interval and the number of treated and control units behind it.

### 6. Stress-test with sensitivity and falsification

Run at least three:

- **Placebo treatment**: assign a fake treatment that should have no effect. A non-null result signals confounding or a pipeline bug.
- **Negative control outcome**: an outcome the treatment cannot plausibly affect.
- **Pre-trend test** for DiD: joint test of pre-period coefficients. Failure kills the design; passing is necessary but not sufficient.
- **E-value**: how strong an unmeasured confounder would need to be, on the risk-ratio scale, to explain away the effect. Compare with the strength of measured confounders.
- **Rosenbaum bounds** for matched designs: report the gamma at which the result loses significance.
- **Subgroup and specification curve**: show whether the sign survives reasonable choices, not just the preferred one.

```python
refute = model.refute_estimate(identified, estimate,
                               method_name="placebo_treatment_refuter",
                               placebo_type="permute", num_simulations=100)
print(refute)
```

### 7. Report the decision, not only the coefficient

State the estimate in decision units (units sold, dollars, percentage points), the interval, the assumptions it depends on, and what would change the recommendation. Separate confirmatory results from exploratory slices. Publish the analysis code, the DAG, the data cutoff, and the pre-registration link.

## Validation

Gates before a causal claim leaves the team:

- [ ] Estimand, population, treatment version, outcome, and horizon specified in advance.
- [ ] DAG recorded with variable roles and an explicit adjustment set.
- [ ] Identification strategy named (randomization, backdoor, IV, RD, DiD, synthetic control).
- [ ] Positivity/overlap checked and reported.
- [ ] Covariate balance after adjustment with SMD thresholds.
- [ ] Standard errors clustered at the assignment unit.
- [ ] At least one falsification test and one sensitivity analysis reported.
- [ ] Pre-trends tested for DiD; first-stage strength reported for IV.
- [ ] Multiplicity handled for more than one primary outcome or many subgroups.
- [ ] Conclusion wording matches the design ("associated" when identification is weak).

```bash
python -m pytest tests/test_estimators.py -q
python scripts/causal_report.py --config analysis/promo_2026.yaml --refutations 3 --out report.json
```

## Gotchas

- Conditioning on a collider creates a spurious association. Check the DAG before adding controls.
- Adjusting for a post-treatment mediator removes part of the effect. Time-stamp every covariate.
- Selecting covariates by p-value or stepwise regression breaks inference. Choose from the DAG.
- Two-way fixed effects with staggered adoption can produce sign-flipped estimates. Use group-time estimators.
- Propensity matching without replacement changes the estimand and the sample. State which one you report.
- Trimming extreme propensity scores improves overlap but redefines the population. Report the trimmed share.
- Clustering at the observation level understates uncertainty in cluster-randomized designs. Cluster at assignment.
- Weak instruments produce biased 2SLS with misleadingly narrow intervals. Check the first-stage F, not just significance.
- A passing pre-trend test can reflect low power. Show the event-study plot, not only the p-value.
- Interference in marketplace or social experiments violates SUTVA. Use cluster or switchback designs.
- Novelty and primacy effects make short-window experiment effects poor long-run estimates. State the horizon.
- Peeking at results inflates false positives. Pre-register the analysis or use sequential testing.
- An E-value is a sensitivity statement, not proof of robustness. Compare it to plausible confounder strength.
- Multiple subgroups at `p < 0.05` will produce false discoveries. Pre-specify or adjust.

## Output contract

```json
{
  "analysis_id": "promo-2026-11-24",
  "question": "Did the October promo increase 30-day sales in the test region?",
  "estimand": "ATT",
  "design": "difference_in_differences",
  "treatment": {"name": "promo_october", "version": "v2", "start": "2026-10-01", "end": "2026-10-31"},
  "outcome": {"name": "sales_30d", "unit": "usd", "window_days": 30},
  "adjustment_set": ["region", "prior_sales", "seasonality"],
  "estimate": {"value": 412000, "ci95": [180000, 644000], "unit": "usd", "p_value": 0.001},
  "diagnostics": {
    "smd_max": 0.04,
    "overlap_trimmed_pct": 0.02,
    "effective_sample_size": 1840,
    "pre_trend_p": 0.31,
    "cluster": "store_id"
  },
  "sensitivity": {
    "placebo_effect": 12000,
    "e_value": 2.4,
    "rosenbaum_gamma": 1.6
  },
  "heterogeneity": [{"segment": "new_customers", "effect": 51000, "ci95": [-20000, 122000]}],
  "caveats": ["Parallel trends holds for the pre-period but power is limited for small regions."],
  "decision": "rollout",
  "artifacts": {"dag": "analysis/promo_dag.dot", "report": "analysis/promo_2026_report.html"}
}
```

## Checklist

- [ ] Estimand and decision threshold written before analysis.
- [ ] DAG built and adjustment set justified.
- [ ] Identification strategy explicit and plausible.
- [ ] Treatment version, outcome window, and exclusions fixed.
- [ ] Positivity and overlap checked.
- [ ] Balance table with SMD before and after adjustment.
- [ ] Estimator matched to design, not to convenience.
- [ ] Standard errors clustered at the treatment assignment unit.
- [ ] Pre-trends or first stage diagnosed as applicable.
- [ ] Placebo, negative control, or sensitivity analysis reported.
- [ ] Multiplicity controlled for multiple outcomes or slices.
- [ ] Caveats and decision recommendation included in the output.

## Related skills

- `product-metrics-instrumentation` for event definitions and assignment logging that make the estimand computable.
- `model-evaluation-benchmarking` for uncertainty, slices, and leakage discipline in quantitative claims.
- `time-series-forecasting` for counterfactual baselines and pre-period trends.
- `data-quality-profiling` for missingness, duplicates, and cohort integrity before estimation.
