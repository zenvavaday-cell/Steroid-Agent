---
name: transaction-anomaly-flagging
description: Detects unusual transactions with explainable rules and statistical models, ranks alerts by risk and cost, and feeds dispositions back into tuning. Use for fraud monitoring, payment risk, expense audit, accounting error detection, and transaction surveillance where analysts need reasons, not just scores.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: finance
---

# Transaction Anomaly Flagging

## Overview

An anomaly is a transaction that differs from its expected pattern. It is not automatically fraud, an error, or a policy violation. The job is to surface a small, ranked queue with a concrete reason and enough context for a human to decide quickly.

Use rules for known bad patterns, statistics for unusual behavior, and supervised models only when labeled outcomes exist. Combine them; never rely on a single uncalibrated score.

## When to use

- Monitoring payments, card transactions, refunds, or transfers.
- Auditing expenses for duplicates, split purchases, or off-policy vendors.
- Detecting ledger errors such as round amounts, unusual accounts, or period-end spikes.
- Prioritizing a manual review queue.

Do not use to automatically accuse, block, or report a person. Escalation and legal decisions require human review.

## Workflow

### 1. Define the decision and the cost model

State what an alert triggers: manual review, hold, escalation, or nothing. Estimate:

- Cost of a false positive (analyst time, customer friction).
- Cost of a false negative (loss, penalty, remediation).
- Review capacity per day.

The threshold follows from these, not from a default 0.5.

### 2. Build features

| Family | Examples |
| --- | --- |
| Amount | Robust z-score versus entity history, round-number flag, threshold proximity |
| Velocity | Count and sum in 1h/24h/7d, acceleration |
| Counterparty | New payee, changed bank details, high-risk country |
| Timing | Off-hours, weekend, period-end, holiday |
| Channel | Device, IP, geo, channel switch |
| Behavior | Category mix, merchant first-seen, sequence |
| Ledger | Split purchases, duplicate invoice, unusual account pair |

Use entity-relative baselines (customer, account, merchant), not a global average.

### 3. Apply deterministic rules

```python
RULES = [
    ("duplicate_invoice", lambda t: t["invoice_no"] in t["seen_invoices"]),
    ("split_purchase", lambda t: t["amount"] < t["approval_limit"] and t["same_vendor_day_total"] > t["approval_limit"]),
    ("new_payee_high_value", lambda t: t["payee_age_days"] < 7 and t["amount"] > 10_000),
    ("round_amount", lambda t: t["amount"] >= 1_000 and t["amount"] % 1_000 == 0),
    ("off_hours", lambda t: t["local_hour"] < 6 or t["local_hour"] > 22),
]
```

Rules must be versioned, documented, and owned. A rule with no owner becomes permanent noise.

### 4. Add statistical scoring

```python
import numpy as np
from sklearn.ensemble import IsolationForest

def robust_z(values, x):
    median = np.median(values)
    mad = np.median(np.abs(values - median)) or 1.0
    return 0.6745 * (x - median) / mad

model = IsolationForest(
    n_estimators=300,
    contamination=0.01,
    random_state=42,
)
model.fit(feature_matrix)
scores = -model.score_samples(feature_matrix)
```

Isolation Forest is a starting point for unlabeled data. It does not produce a probability. Calibrate or rank; do not present the raw score as a likelihood of fraud.

### 5. Combine signals

Use a transparent scorecard:

```
risk = 0.35 * rule_severity
     + 0.25 * statistical_percentile
     + 0.20 * counterparty_risk
     + 0.20 * amount_materiality
```

Keep the component contributions in the alert. An analyst must be able to see why the transaction ranked where it did.

### 6. Select thresholds by capacity

Sort alerts by risk and choose the cutoff at the review capacity, or at the point where marginal cost equals marginal benefit. Report:

- Alert volume per day.
- Precision at the reviewed cutoff (from labeled dispositions).
- Recall on known cases, if available.
- False positive rate.
- Median time to review.

### 7. Close the loop

Every disposition becomes a label: confirmed issue, benign, inconclusive. Feed labels back into rule tuning and model retraining. Track rule-level precision so noisy rules can be retired.

## Gotchas

- Seasonality and month-end effects create predictable spikes. Baseline by period, not only by entity.
- Class imbalance makes accuracy meaningless. Use precision, recall, and cost-weighted metrics.
- Leakage: post-investigation fields can reveal the outcome. Exclude them from features.
- Entity drift: a customer's behavior changes legitimately after a move, new job, or business growth.
- Amount-only models miss structuring and split transactions.
- Alert fatigue is a safety issue. A queue that is 99% noise gets ignored.
- Privacy and fairness: transaction data can proxy protected attributes. Review features and outcomes.
- A model score is not evidence. Preserve the underlying transactions and rule versions.

## Output contract

```json
{
  "alert_id": "ALERT-2026-000123",
  "transaction_id": "TX-99881",
  "entity_id": "CUST-441",
  "risk_score": 0.87,
  "rank": 12,
  "reasons": [
    {"code": "new_payee_high_value", "severity": 0.9, "detail": "Payee age 2 days; amount 48,000"},
    {"code": "amount_zscore", "severity": 0.7, "detail": "Robust z-score 6.2 versus 12-month history"}
  ],
  "evidence": {"transactions": ["TX-99881", "TX-99882"], "rule_version": "2026.11"},
  "recommended_action": "manual_review",
  "disposition": null
}
```

## Checklist

- [ ] Decision, cost model, and review capacity defined.
- [ ] Entity-relative features built.
- [ ] Rules versioned and owned.
- [ ] Statistical model used with calibrated or ranked output.
- [ ] Component contributions retained.
- [ ] Threshold chosen from capacity and cost.
- [ ] Dispositions captured as labels.
- [ ] Drift and rule precision monitored.

## Related skills

- `anti-money-laundering-screening` for sanctions and PEP alerts.
- `automated-ledger-reconciliation` for matching before anomaly analysis.
- `human-in-the-loop-escalation` before any account restriction.
