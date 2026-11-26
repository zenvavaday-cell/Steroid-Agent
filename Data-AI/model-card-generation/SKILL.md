---
name: model-card-generation
description: Documents intended use, training data, metrics, limitations, ethical risks, and monitoring for a model. Use for release governance and stakeholder communication.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: data-ai
---

# Model Card Generation

## Overview

A model card is the release document that a reviewer, a downstream integrator, and an incident responder can read without access to the training team. It records what the model is for, what data produced it, how it was measured, where it fails, and who watches it after launch.

The discipline is to derive every claim from an artifact: a dataset version, an evaluation run, a slice table, or a monitoring query. Numbers copied from a notebook without a run ID do not belong in a card.

## When to use

- Shipping a model to production or to an external customer.
- Registering a model version in an internal registry or model marketplace.
- Answering a procurement, audit, or regulatory questionnaire about a model.
- Handing a model between teams or to a managed inference vendor.
- Releasing a significant retrain that changes behavior or the decision threshold.
- Documenting a model used for a high-impact decision (credit, hiring, health, access).
- Do not use for a throwaway notebook or a model that never leaves a local experiment; a one-line experiment note is enough there.

## Workflow

### 1. Pin identity and release context

Record the model ID, semantic version, artifact digest, training commit, framework versions, owner, approval ticket, and release date. The card is versioned with the artifact, not edited in place after release.

```bash
sha256sum artifacts/model.pt
git rev-parse HEAD
python -c "import torch, sklearn; print(torch.__version__, sklearn.__version__)"
```

Fill `model_id`, `version`, `artifact_sha256`, `training_commit`, `owner`, and `approval_ticket` from this output. If any field is missing, stop: an unpinned card cannot be reproduced or revoked.

### 2. State intended use and out-of-scope use

Write one paragraph for each:

- **Intended use**: decision supported, user role, input distribution, language, geography, and the action taken on the output.
- **Out-of-scope use**: excluded populations, excluded input types, high-stakes uses that require human review, and uses the evaluation does not cover.
- **Users**: who consumes the output and what training or warning they receive.

"Weak" versus "usable" example:

```text
Weak:   This model predicts customer churn.
Usable: Scores subscription churn risk for accounts active at least 30 days,
        for the retention team's weekly queue in the US and Canada.
        Not validated for enterprise contracts above $100k ARR, for accounts
        under 30 days old, or for individual adverse-action decisions.
```

### 3. Document data provenance

Build a table with one row per dataset. Every row cites a version or content hash and a license.

| Dataset | Version / hash | Rows | Window | License | Consent or basis | Known gaps |
| --- | --- | --- | --- | --- | --- | --- |
| support_tickets_v3 | `sha256:9f2c...` | 812,004 | 2023-01 to 2025-06 | internal | employee data policy | non-English excluded |
| crm_accounts_v7 | `sha256:41ab...` | 94,220 | snapshot 2025-07-01 | internal | customer contract | reseller accounts missing |

Also record preprocessing that changes meaning: label definition, deduplication, filtering, class rebalancing, and any data excluded for privacy. Label all illustrative values in the table as examples.

### 4. Report metrics with slices and uncertainty

Tie the primary metric to the decision threshold and report it on a frozen holdout. Then disaggregate:

- Overall metric with numerator, denominator, and 95% confidence interval.
- Per-slice metrics for protected groups, key geographies, device types, and input-quality bands.
- Calibration (reliability curve, expected calibration error) when probabilities drive the action.
- A naive or incumbent baseline on the same holdout.

Report slices only when `n >= 100`; suppress smaller slices and state the suppression rule. Do not publish a point estimate without its denominator. Use bootstrap resampling for intervals:

```python
import numpy as np

def bootstrap_ci(y_true, y_pred, metric, n_boot=2000, alpha=0.05, seed=7):
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(y_true), size=(n_boot, len(y_true)))
    scores = [metric(y_true[i], y_pred[i]) for i in idx]
    return np.quantile(scores, [alpha / 2, 1 - alpha / 2])
```

### 5. Analyze limitations and ethical risks

Cover these explicitly, each with evidence or a stated unknown:

- **Failure modes**: input lengths, rare classes, noisy sensors, adversarial text, stale features.
- **Subgroup gaps**: largest metric delta between slices and the slice with the smallest `n`.
- **Proxy and label risk**: features correlated with protected attributes, human labels that encode bias.
- **Privacy**: whether training data contains personal data, memorization checks run, and retention.
- **Misuse**: the most plausible harmful use and the control that limits it.
- **Human oversight**: who can override the model, how they are alerted, and how overrides are logged.

Write "not measured" when a risk was not tested. Do not write "no bias" unless a named test with a named threshold passed.

### 6. Define monitoring and rollback

Specify the production signals that would invalidate the card:

| Signal | Metric | Threshold | Cadence | Owner | Action |
| --- | --- | --- | --- | --- | --- |
| Input drift | PSI on top 20 features | > 0.2 | daily | ML platform | review, retrain |
| Outcome drift | primary metric on labeled sample | drop > 3 pp | weekly | model owner | open incident |
| Calibration | ECE | > 0.05 | weekly | model owner | recalibrate |
| Latency | p95 inference | > 250 ms | 5 min | on-call | rollback |

Name the rollback artifact (previous version digest), the trigger, and the person authorized to execute it.

### 7. Validate and publish

Store the card as `model-card.yaml` or `README.md` beside the artifact, validate required keys, and attach reviewer approvals. For Hugging Face style publication, keep the card frontmatter parseable:

```yaml
---
license: apache-2.0
library_name: sklearn
tags: [tabular-classification, churn]
model-index:
  - name: churn-classifier
    results:
      - task: {type: tabular-classification, name: Churn}
        dataset: {name: churn_holdout_v4, type: internal}
        metrics:
          - {type: roc_auc, value: 0.84, verified: true}
---
```

Run the schema check before merge and after any metadata edit. Publishing is a review event, not a file save.

## Validation

All gates must pass before release:

- [ ] Identity gate: artifact digest, commit, and versions resolve to a build that exists.
- [ ] Provenance gate: every dataset has a version or hash and a license.
- [ ] Metric gate: every reported number has a run ID, a denominator, and a 95% interval.
- [ ] Slice gate: groups with `n >= 100` are reported; suppressed slices state the reason.
- [ ] Risk gate: each listed risk has evidence, a control, or an explicit "not measured".
- [ ] Monitoring gate: every signal has a threshold, cadence, owner, and rollback action.
- [ ] Privacy gate: no personal data, secrets, or raw customer text appear in examples.
- [ ] Review gate: model owner and an independent reviewer approved the card.

Automated check:

```bash
python scripts/validate_model_card.py model-card.yaml \
  --require identity,provenance,metrics,limitations,monitoring \
  --fail-on-placeholder
```

## Gotchas

- A metric without a dataset version is unreproducible. Store the eval run ID and holdout hash in the card.
- An aggregate score hides a subgroup regression. Check per-slice deltas before celebrating the mean.
- Intended use that names no population or decision cannot be violated, which makes it useless. Name both.
- Copying raw training rows into "example" sections leaks personal data. Use synthesized or redacted examples.
- "No bias found" after testing one attribute is a false negative. List attributes tested and attributes not tested.
- Latency measured on a laptop GPU does not describe production. Record hardware, batch size, and concurrency.
- Cards drift after fine-tuning. Regenerate the whole card from the new run instead of editing metrics by hand.
- A dataset license can forbid commercial use even when the model license allows it. Check both.
- Failure examples can contain prompt-injection text or PII. Sanitize before publishing.
- Out-of-scope uses with no enforcement are decorative. Link to the guardrail or deny rule that applies.
- Eval metrics computed after threshold tuning on the same holdout are optimistic. Use a separate calibration split.
- A card that lists "monitoring: yes" with no metric and owner will not survive an incident review.

## Output contract

```json
{
  "model_id": "churn-classifier",
  "version": "1.4.0",
  "artifact_sha256": "3f9a...",
  "training_commit": "a1b2c3d",
  "owner": "ml-retention@example.com",
  "intended_use": "Scores churn risk for active subscription accounts in the US and Canada.",
  "out_of_scope": ["accounts under 30 days", "enterprise ARR above 100k", "adverse-action notices"],
  "datasets": [
    {"name": "support_tickets_v3", "hash": "sha256:9f2c...", "license": "internal", "rows": 812004}
  ],
  "metrics": {
    "primary": {"name": "roc_auc", "value": 0.84, "ci95": [0.82, 0.86], "n": 18420, "run_id": "eval-2026-11-19-004"},
    "slices": [{"name": "region=eu", "roc_auc": 0.79, "n": 2410}],
    "suppressed_slices": [{"name": "plan=legacy", "n": 41, "reason": "n < 100"}]
  },
  "limitations": ["No validation on enterprise contracts.", "Label noise from manual ticket tagging."],
  "ethical_risks": [{"risk": "proxy for tenure", "control": "tenure feature removed", "status": "mitigated"}],
  "monitoring": [{"signal": "psi_top20", "threshold": 0.2, "cadence": "daily", "owner": "ml-platform", "action": "retrain review"}],
  "rollback": {"version": "1.3.2", "trigger": "primary metric drop > 3 pp", "authorized_by": "model-owner"},
  "approvals": [{"role": "model_owner", "ticket": "ML-812"}, {"role": "independent_reviewer", "ticket": "ML-819"}],
  "card_path": "models/churn-classifier/1.4.0/model-card.yaml"
}
```

## Checklist

- [ ] Model identity, artifact digest, and environment versions pinned.
- [ ] Intended use names population, decision, and user.
- [ ] Out-of-scope uses listed with the control that enforces them.
- [ ] Every dataset has a version or hash, window, license, and consent basis.
- [ ] Primary metric tied to threshold, with denominator and 95% interval.
- [ ] Slice metrics reported and small slices suppressed with a stated rule.
- [ ] Calibration reported when probabilities drive decisions.
- [ ] Limitations and ethical risks written with evidence or "not measured".
- [ ] Monitoring signals have thresholds, cadence, owners, and actions.
- [ ] Rollback artifact and authorization named.
- [ ] No PII, secrets, or unsanitized examples in the card.
- [ ] Schema validation and two-party review completed before publish.

## Related skills

- `model-evaluation-benchmarking` for holdout design, slices, and uncertainty behind the reported metrics.
- `ml-experiment-tracking` for run IDs, artifacts, and environment capture that make the card reproducible.
- `dataset-annotation-qc` for label quality and agreement evidence in the provenance section.
- `synthetic-data-generation` for privacy-safe examples and augmentation disclosures.
