---
name: dataset-annotation-qc
description: Designs labeling guidelines and measures inter-annotator agreement, drift, and adjudication quality. Use for supervised datasets and human labeling programs.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: data-ai
---

# Dataset Annotation QC

## Overview

Labeled data fails quietly. Annotators interpret an ambiguous guideline differently, a taxonomy changes mid-project, one vendor gets faster and sloppier, and the resulting dataset trains a model on inconsistent targets. QC makes those failures measurable per batch, per label, and per annotator before the data reaches training.

The core discipline is to treat labels as measurements: define the construct, calibrate the raters, quantify agreement beyond chance, adjudicate disagreements with a recorded rationale, and audit production batches against a stable gold set.

## When to use

- Starting a human labeling program for classification, extraction, ranking, or preference data.
- Onboarding a new vendor, annotator pool, or language market.
- Revising a label taxonomy or guideline mid-project.
- Auditing a delivered batch before it enters a training set.
- Investigating a model regression traced to label noise.
- Preparing a dataset for external release or regulatory review.
- Do not use to measure model quality against ground truth; that is evaluation benchmarking, not annotation QC.

## Workflow

### 1. Define the construct and the decision the label supports

Write one paragraph that states what the label means, what it does not mean, and the downstream decision it feeds. A label that supports a moderation queue needs different precision than one used for a legal hold.

Then produce a label sheet:

| Field | Required | Definition | Values | Example | Anti-example |
| --- | --- | --- | --- | --- | --- |
| sentiment | yes | attitude toward the product | positive, neutral, negative, unclear | "works great" | sarcasm with no context |
| severity | yes | user impact of the defect | low, medium, high | checkout blocked for all | cosmetic spacing |

Include an explicit `unclear` or `abstain` value and an escalation path. Forcing a choice on ambiguous items manufactures noise.

### 2. Write testable guidelines with a decision tree

Structure the guideline as:

1. Scope and unit of annotation (document, sentence, span, conversation turn).
2. Ordered decision questions with yes/no branches.
3. Positive and negative examples for every leaf.
4. Boundary cases with the correct call and the reasoning.
5. Rules for multi-label overlap, nesting, and partial spans.
6. What to do when the item is out of scope, unreadable, or missing context.
7. Change log with version, date, and diff summary.

Version the guideline (`guideline_v3.2`) and record it on every task. A label produced under v2 cannot be pooled with v3 without a re-review.

### 3. Calibrate on a seeded gold set

Build a gold set of 100 to 300 items with expert-agreed labels, stratified across labels, difficulty, and slices. Run a calibration round of 50 to 100 items with discussion, then a blind qualification round.

Acceptance gates for a new annotator, as an example policy:

- Overall accuracy on gold `>= 0.90`.
- Per-label recall `>= 0.85` for every label with at least 20 gold items.
- No single confusion pair above `0.15` of that annotator's errors.
- Qualification retaken after any guideline version change.

Store gold labels in a separate table with restricted access. Never ship gold items into the training split unnoticed.

### 4. Measure agreement beyond chance

Choose the statistic by design:

| Design | Statistic | Notes |
| --- | --- | --- |
| 2 annotators, nominal | Cohen's kappa | sensitive to prevalence skew |
| 3+ annotators, nominal | Fleiss' kappa | assumes fixed rater count |
| 3+ annotators, ordinal or missing | Krippendorff's alpha | handles missing ratings |
| Span extraction | exact-match F1 plus boundary IoU | report overlap criterion |
| Ranking | Kendall's tau or nDCG agreement | per query, then average |

```python
from sklearn.metrics import cohen_kappa_score, confusion_matrix

kappa = cohen_kappa_score(annotator_a, annotator_b, labels=["positive", "neutral", "negative", "unclear"])
cm = confusion_matrix(annotator_a, annotator_b, labels=["positive", "neutral", "negative", "unclear"])
```

Interpretation bands from the Krippendorff convention, stated as an example policy:

- `alpha >= 0.80`: acceptable for training use.
- `0.67 <= alpha < 0.80`: tentative, only for exploratory work; revise guidelines.
- `alpha < 0.67`: do not use the batch; the construct or guideline is not ready.

Report the statistic with its confidence interval. For 3+ annotators use `krippendorff` (`pip install krippendorff`):

```python
import krippendorff
alpha = krippendorff.alpha(reliability_data=rating_matrix, level_of_measurement="ordinal")
```

Also report raw percent agreement and the label distribution. Kappa can collapse toward zero when one label dominates even though percent agreement is high (the prevalence problem), so never report kappa alone.

### 5. Adjudicate disagreements with a record

For every item with disagreement:

- Route to a senior adjudicator who did not label it the first time, blinded to annotator identity where feasible.
- Adjudicator re-labels from the guideline, then reviews the conflicting rationales.
- Record `final_label`, `adjudicator_id`, `guideline_version`, `reason_code`, and `changed_from`.
- If the same reason code recurs more than 5 times in 100 adjudications, treat it as a guideline defect and patch the guideline.

Track two rates per batch:

- `adjudication_rate = items_with_disagreement / items_double_coded`
- `override_rate = adjudications_that_change_the_majority_label / adjudications`

An override rate above 0.20 suggests the majority vote is not trustworthy and the batch needs full re-review. Label these cutoffs as an example policy and tune them with your own cost of error.

### 6. Monitor drift per batch and per annotator

Use the gold set as a repeated control. Every batch includes 5 to 10 percent gold items, randomly placed and not flagged in the task UI.

- Plot per-annotator gold accuracy over batch index (p-chart or individuals chart).
- Flag an annotator when 2 consecutive batches fall below the lower control limit, or when a single batch is more than 3 standard deviations below their own baseline.
- Flag a vendor when batch-level gold accuracy drops more than 5 points from its qualification score.
- Track label distribution drift with population stability index (PSI); PSI above 0.2 on a label indicates a taxonomy or sampling shift.
- Re-run calibration after any guideline change, model-assisted pre-labeling change, or annotator turnover above 30 percent.

### 7. Audit the delivered batch with stratified sampling

Before acceptance, draw a random sample stratified by label and difficulty. Sample size for a 95 percent confidence interval with a 2 percent margin is roughly 2,400 items for a large batch, or use the hypergeometric formula for batches under 50,000. For a quick release gate, a 200-item sample detects a 3 percent defect rate with limited power; state the limitation.

Audit procedure:

1. Hide the vendor's labels.
2. Have a trained reviewer re-label the sample.
3. Compute accuracy per label and per slice, plus a confusion matrix.
4. Accept when overall accuracy `>= 0.95` and every label with `n >= 30` is `>= 0.90` (example thresholds).
5. Quarantine failed batches. Do not partially accept a failed stratum without re-review.

Record the sampling frame, seed, sample IDs, and reviewer so the audit is reproducible.

## Validation

Release gates for a labeled dataset:

- [ ] Guideline version pinned and attached to every item.
- [ ] Gold set exists, is access-controlled, and is excluded from training splits.
- [ ] Agreement statistic is appropriate for the design and has a confidence interval.
- [ ] Per-label agreement reported; no label below the agreed floor.
- [ ] Adjudication records include reason codes and final labels.
- [ ] Drift chart covers at least the last 5 batches.
- [ ] Audit sample is stratified, blinded, and reproducible from a recorded seed.
- [ ] Duplicate item IDs and cross-split leakage checked.
- [ ] Label schema validates against the task schema.

```bash
python -m pytest tests/test_label_schema.py -q
python scripts/annotation_report.py --export batch.jsonl --gold gold.jsonl --out qc-report.json
```

A batch that fails any gate stays in quarantine. Re-labeling, not statistical adjustment, is the remedy.

## Gotchas

- Kappa falls toward zero under skewed prevalence even with high raw agreement. Report percent agreement and the confusion matrix alongside it.
- Percent agreement alone is inflated by dominant labels. Always adjust for chance.
- Mixing guideline versions in one batch creates labels for different constructs. Re-review or discard.
- Gold items that leak into training inflate eval scores. Keep a hash blocklist and check splits.
- Annotators learn gold item positions when they are always first or last. Randomize placement.
- Adjudicators who rubber-stamp the majority label erase minority signal. Blind the adjudicator and sample their work.
- Auditing only easy items understates the defect rate. Stratify by difficulty and rare labels.
- A taxonomy change without re-labeling makes old and new data incomparable. Version the taxonomy and backfill deliberately.
- High agreement can mean annotators share a misunderstanding. Agreement measures consistency, not correctness; keep expert gold.
- Per-annotator drift after a UI or pay change is common. Correlate drift with operational events, not only quality metrics.
- Span annotations scored with exact match punish boundary differences. Report boundary tolerance and IoU.
- Sampling without a recorded seed makes an audit unreproducible and disputable.

## Output contract

```json
{
  "dataset": "support_intent_v5",
  "guideline_version": "3.2",
  "batch_id": "batch-2026-11-18",
  "items": {"total": 48000, "double_coded": 4800, "gold": 2400},
  "agreement": {
    "statistic": "krippendorff_alpha",
    "value": 0.81,
    "ci95": [0.78, 0.84],
    "percent_agreement": 0.88,
    "per_label": {"billing": 0.84, "technical": 0.79, "account": 0.86, "unclear": 0.71}
  },
  "adjudication": {"rate": 0.10, "override_rate": 0.14, "top_reason_codes": ["ambiguous_scope", "missing_context"]},
  "drift": {"window_batches": 6, "flagged_annotators": ["a-1042"], "label_psi_max": 0.11},
  "audit": {"sample_size": 400, "seed": 20261118, "accuracy": 0.962, "worst_label": {"name": "unclear", "accuracy": 0.88}},
  "decision": "accept",
  "quarantined_items": 0,
  "report_path": "qc/support_intent_v5/batch-2026-11-18.json"
}
```

## Checklist

- [ ] Construct, unit, and downstream decision defined.
- [ ] Label sheet with definitions, examples, anti-examples, and `unclear`.
- [ ] Guideline versioned with a decision tree and changelog.
- [ ] Gold set built, access-controlled, and excluded from training splits.
- [ ] Annotator qualification gates applied before production labeling.
- [ ] Agreement statistic chosen for the design and reported with a CI.
- [ ] Per-label agreement and confusion pairs reviewed.
- [ ] Adjudication reasons recorded and recurring defects fed back into the guideline.
- [ ] Gold-based drift monitored per batch and per annotator.
- [ ] Stratified blinded audit run with a recorded seed.
- [ ] Duplicate IDs and train/test leakage checked.
- [ ] Failed strata quarantined rather than statistically patched.

## Related skills

- `data-quality-profiling` for completeness, duplicate, and distribution checks on the labeled table.
- `model-evaluation-benchmarking` for turning adjudicated labels into a trustworthy evaluation set.
- `human-in-the-loop-escalation` for routing ambiguous items and low-confidence cases to reviewers.
- `synthetic-data-generation` for augmenting scarce label classes without leaking gold items.
