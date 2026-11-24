---
name: credit-risk-scoring-pipeline
description: Builds and validates probability-of-default scorecards and credit risk models, covering data assembly, WOE/IV, logistic or gradient-boosted models, calibration, discrimination, stability, cutoff selection, fairness review, and monitoring. Use for lending, trade credit, counterparty risk, and portfolio credit analytics.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: finance
---

# Credit Risk Scoring Pipeline

## Overview

A credit score is a calibrated estimate of the probability of a defined adverse event within a defined horizon. Discrimination alone is not enough: the score must be calibrated, stable, explainable, and monitored.

This skill covers the full pipeline from outcome definition to production monitoring.

## When to use

- Building an application or behavioral scorecard.
- Validating an existing credit model.
- Setting approval cutoffs and risk-based pricing.
- Monitoring portfolio drift after a macro change.
- Explaining a credit decision to a reviewer or regulator.

## 1. Define the outcome

Pin these before touching data:

| Item | Example |
| --- | --- |
| Entity | Small business borrower |
| Event | 90+ days past due or bankruptcy |
| Horizon | 12 months from application |
| Observation window | 24 months of performance |
| Population | Applications in 2024–2025 |
| Exclusions | Fraud, withdrawn, policy declines |
| Treatment of recovered accounts | Cured within 30 days not bad |

A different definition produces a different model. Write it down and keep it.

## 2. Assemble data without leakage

- Use only information available at the decision point.
- Build out-of-time samples: train on earlier vintages, validate on later.
- Avoid post-default fields, collection notes, and manually overridden values.
- Handle rejects carefully. If the model only sees approved loans, it has sample selection bias.
- Record data lineage for every feature.

## 3. Engineer features and bin them

Common families:

- Capacity: income, revenue, debt service coverage, utilization.
- Character: payment history, tenure, delinquencies.
- Collateral: loan-to-value, asset type.
- Conditions: industry, geography, macro.
- Stability: employment or business age, account age.

Weight of Evidence:

```python
import numpy as np

def woe(good, bad):
    good_dist = good / good.sum()
    bad_dist = bad / bad.sum()
    return np.log(good_dist / bad_dist)

def information_value(good, bad):
    return ((good / good.sum()) - (bad / bad.sum())) * woe(good, bad)
```

Bin continuous variables into monotonic groups. Check that bad rates move in a sensible direction. IV above 0.5 often signals leakage or an overfit bin.

## 4. Fit and calibrate

A transparent baseline is logistic regression on WOE features:

```python
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV

base = LogisticRegression(max_iter=1000, class_weight="balanced")
model = CalibratedClassifierCV(base, method="isotonic", cv=5)
model.fit(X_train, y_train)
```

Gradient boosting can improve discrimination but needs explainability and calibration. Compare against the logistic baseline; do not adopt complexity without measured lift.

## 5. Evaluate

| Metric | What it tells you |
| --- | --- |
| AUC / Gini | Rank ordering |
| KS | Maximum separation between good and bad |
| Calibration curve | Predicted PD versus observed default rate |
| Brier score | Probability accuracy |
| PSI | Population stability over time |
| Lift by decile | Concentration of bads in the riskiest deciles |
| Monotonicity | Sensible risk ordering across bins |

Evaluate on out-of-time data. Report confidence intervals. A single AUC without calibration is not a credit model.

## 6. Set cutoffs

Map scores to PD and then to decisions:

| Band | PD range | Decision |
| --- | --- | --- |
| A | < 1% | Approve, standard pricing |
| B | 1–3% | Approve, risk premium |
| C | 3–7% | Manual review |
| D | 7–15% | Approve only with collateral |
| E | > 15% | Decline |

Cutoffs reflect risk appetite, expected loss, capital, and fairness, not only the model's accuracy.

## 7. Review fairness and explainability

- Test error rates and approval rates across protected groups where law permits.
- Use reason codes (SHAP, coefficient contributions, WOE) for adverse action notices.
- Ensure explanations are stable and understandable.
- Document limitations and intended use.

## 8. Monitor

Track monthly:

- Score distribution and PSI.
- Actual versus predicted default by band.
- Override rate and override performance.
- Feature drift.
- Vintage performance.
- Macro overlay triggers.

Retrain on a defined cadence or when PSI or calibration breach thresholds.

## Gotchas

- Default definition changes break comparability across vintages.
- Reject inference can shift the population; document the method.
- Class imbalance makes accuracy misleading.
- WOE binning on the full dataset leaks validation information. Fit bins on train only.
- Calibration drifts before discrimination does. Monitor both.
- Macro shocks can invalidate a stable scorecard. Have an overlay and a conservative cutoff.
- Fairness metrics conflict with each other. Choose and document the policy.
- A score is not a decision. Keep human review for exceptions and appeals.

## Output contract

```json
{
  "model_id": "SMB-PD-2026.1",
  "outcome": "90+ DPD or bankruptcy within 12 months",
  "population": "SMB applications 2024-01 to 2025-06",
  "algorithm": "WOE logistic regression",
  "calibration": "isotonic",
  "metrics": {"auc": 0.78, "gini": 0.56, "ks": 0.42, "brier": 0.061},
  "stability": {"psi_train_vs_oot": 0.04},
  "cutoffs": [{"band": "A", "pd_max": 0.01, "decision": "approve"}],
  "fairness_review": "completed",
  "monitoring_plan": "monthly PSI and calibration"
}
```

## Checklist

- [ ] Outcome, horizon, population, and exclusions defined.
- [ ] Only decision-time features used.
- [ ] Out-of-time validation performed.
- [ ] Bins monotonic and leakage checked.
- [ ] Calibration measured, not assumed.
- [ ] Cutoffs tied to risk appetite and expected loss.
- [ ] Fairness and explainability reviewed.
- [ ] Monitoring and retraining plan in place.

## Related skills

- `schema-enforced-json-extraction` for ingesting borrower financials.
- `anti-money-laundering-screening` as a separate onboarding control.
- `confidence-threshold-output-gating` for low-confidence decisions.
