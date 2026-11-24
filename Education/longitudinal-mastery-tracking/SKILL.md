---
name: longitudinal-mastery-tracking
description: Tracks learner mastery over time with evidence, uncertainty, decay, and transfer checks, using Bayesian knowledge tracing or weighted mastery models. Use for personalized learning, progress reporting, intervention triggers, and program evaluation.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: education
---

# Longitudinal Mastery Tracking

## Overview

Mastery is not a percentage on one test. It is an estimate, with uncertainty, of whether a learner can use a skill across contexts and after a delay. Tracking it over time requires consistent evidence, a model that updates, and a decay or refresher mechanism.

Report estimates with uncertainty. Avoid false precision.

## When to use

- Tracking progress across a course or program.
- Triggering remediation before a summative assessment.
- Reporting mastery to a learner, teacher, or institution.
- Evaluating whether instruction worked.
- Combining evidence from quizzes, projects, and tutoring sessions.

## Workflow

### 1. Define the skills

Use fine-grained, observable skills:

- "Solve a two-step linear equation."
- "Identify the thesis of an argumentative passage."
- "Configure a firewall rule with a default deny policy."

Map each skill to a curriculum standard and a prerequisite graph. Coarse skills ("algebra") produce meaningless mastery estimates.

### 2. Define evidence types

| Evidence | Weight | Notes |
| --- | --- | --- |
| Diagnostic item | Medium | Placement, not mastery |
| Formative quiz | Low–Medium | Practice effects |
| Summative assessment | High | Best evidence of independent performance |
| Project or performance task | High | Transfer and application |
| Tutoring interaction | Low | Rich but not standardized |
| Delayed retention check | High | Durable learning |
| Transfer item | High | Novel context |

Weight evidence by validity and recency, not by convenience.

### 3. Score evidence

Each item or task yields a score in [0, 1]. For partial credit, define the rubric. For multiple items on one skill, aggregate with a weighted mean, not a simple count if difficulty varies.

### 4. Update mastery

A simple weighted model:

```python
def update(prior, evidence_score, weight):
    return (1 - weight) * prior + weight * evidence_score
```

A Bayesian Knowledge Tracing update:

```python
def bkt_update(p_mastery, correct, p_learn=0.15, p_slip=0.10, p_guess=0.20):
    if correct:
        numerator = p_mastery * (1 - p_slip)
        denominator = numerator + (1 - p_mastery) * p_guess
    else:
        numerator = p_mastery * p_slip
        denominator = numerator + (1 - p_mastery) * (1 - p_guess)
    posterior = numerator / denominator
    return posterior + (1 - posterior) * p_learn
```

BKT parameters should be fitted per skill when enough data exists. Defaults are a starting point.

### 5. Model decay

Skills decay without use. Apply a half-life by skill type:

```python
import math

def decay(mastery, days_since, half_life_days=90):
    return mastery * (0.5 ** (days_since / half_life_days))
```

Do not decay below a floor if the skill is foundational and recently used. Decay is a prompt for review, not an erasure.

### 6. Estimate uncertainty

Track the number and recency of observations. Report a confidence interval or a simple reliability band:

```json
{
  "skill": "solve-two-step-equations",
  "mastery": 0.78,
  "interval": [0.66, 0.87],
  "evidence_count": 9,
  "last_evidence": "2026-11-20",
  "status": "proficient"
}
```

A mastery of 0.78 from two items is not the same as 0.78 from twenty.

### 7. Set thresholds and triggers

| Status | Rule | Action |
| --- | --- | --- |
| Not started | No evidence | Assess or teach |
| Developing | < 0.60 | Targeted practice |
| Proficient | 0.60–0.85 | Continue, spaced review |
| Mastered | > 0.85 with transfer + delay | Reduce review |
| At risk | Dropped > 0.10 or decay below 0.60 | Intervention |

Thresholds should reflect the consequences of a false positive. For safety-critical skills, require higher mastery and a performance check.

### 8. Report

Show:

- Skill-level mastery, not only an overall average.
- Trend over time.
- Evidence types and recency.
- Uncertainty.
- Next recommended action.

Avoid ranking learners publicly. Use mastery for support, not judgment.

## Gotchas

- A single assessment is a snapshot, not mastery. Require multiple evidence types.
- Changing assessments breaks comparability. Maintain a linking item or rescale.
- Ceiling and floor effects compress estimates.
- Practice effects inflate scores on repeated identical items.
- Transfer is the strongest evidence. Include novel contexts.
- Forgetting is normal. Decay should trigger review, not punishment.
- Sparse data produces wide intervals. Do not report false precision.
- Bias in items or grading propagates into mastery. Audit assessments.
- Learners can game a system that rewards completion over correctness.
- Privacy: mastery data is sensitive. Limit access and retention.
- An overall average can hide a missing prerequisite. Report the skill graph.
- Model parameters from a different population may not transfer. Validate locally.

## Output contract

```json
{
  "learner_id": "L-1042",
  "period": {"from": "2026-09-01", "to": "2026-11-24"},
  "skills": [
    {
      "id": "solve-two-step-equations",
      "mastery": 0.78,
      "interval": [0.66, 0.87],
      "trend": "+0.12",
      "evidence": [{"type": "summative", "score": 0.80, "date": "2026-11-18"}],
      "status": "proficient",
      "next_action": "spaced review in 14 days"
    }
  ],
  "alerts": ["fraction-operations decayed below 0.60"],
  "notes": "estimates include decay; last full assessment 2026-11-18"
}
```

## Checklist

- [ ] Skills defined at observable granularity.
- [ ] Evidence types weighted by validity.
- [ ] Scores mapped to a consistent scale.
- [ ] Mastery updated with a documented model.
- [ ] Decay applied by skill type.
- [ ] Uncertainty estimated from evidence count and recency.
- [ ] Thresholds tied to consequences.
- [ ] Reporting includes trends and next actions.
- [ ] Privacy and retention policy applied.

## Related skills

- `prerequisite-knowledge-mapping` for the skill graph.
- `adaptive-spaced-repetition-scheduling` for retention reviews.
- `student-misconception-diagnosis` when mastery stalls despite practice.
