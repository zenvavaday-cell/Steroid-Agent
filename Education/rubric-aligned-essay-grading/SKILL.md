---
name: rubric-aligned-essay-grading
description: Grades essays and written work against an analytic rubric with evidence quotes, calibrated anchors, bias controls, moderation, and actionable feedback. Use for coursework, admissions, writing assessment, and any evaluation where scores must be defensible and consistent.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: education
---

# Rubric-Aligned Essay Grading

## Overview

A grade is a claim about evidence. The rubric defines the criteria; the anchors define the levels; the essay provides the evidence. Grade each criterion independently, cite the text, and only then combine.

A single holistic impression is fast and unreliable. Analytic scoring with evidence is slower but defensible.

## When to use

- Grading essays, reports, reflections, or short answers.
- Calibrating multiple graders.
- Giving feedback that connects to criteria.
- Auditing a set of grades for consistency.

Do not use for high-stakes decisions without human moderation and an appeal process.

## Inputs

- The prompt and learning objectives.
- The rubric with criteria, levels, and weights.
- Anchor papers for each level, if available.
- Grade boundaries and policies.
- Accommodations and submission metadata.

## Workflow

### 1. Parse the rubric into a scoring sheet

```json
{
  "criteria": [
    {"id": "thesis", "weight": 0.25, "levels": {"4": "clear, arguable, original", "3": "clear and arguable", "2": "vague or descriptive", "1": "missing or incoherent"}},
    {"id": "evidence", "weight": 0.30, "levels": {"4": "precise, relevant, well-integrated", "3": "relevant but uneven", "2": "thin or poorly integrated", "1": "absent or irrelevant"}},
    {"id": "analysis", "weight": 0.30, "levels": {"4": "insightful, addresses counterarguments", "3": "sound reasoning", "2": "summary without analysis", "1": "unsupported claims"}},
    {"id": "mechanics", "weight": 0.15, "levels": {"4": "polished", "3": "minor errors", "2": "frequent errors impede reading", "1": "severe errors"}}
  ]
}
```

If the rubric is vague, rewrite the level descriptors with observable language before grading. Do not invent criteria the assignment did not require.

### 2. Calibrate with anchors

Read the anchor papers and agree on why each earned its score. If two graders disagree, discuss the evidence until the descriptor, not the paper's vibe, decides.

Measure agreement on a sample with Cohen's kappa or percent agreement. Below 0.6 kappa, recalibrate before grading the full set.

### 3. Read the whole essay once

Read for meaning without scoring. Do not let the introduction set the grade. Note the thesis, the argument structure, and the evidence.

### 4. Score each criterion independently

For each criterion:

- Select the level that best matches the descriptor.
- Quote the evidence that justifies the level.
- Note what would move the essay up one level.
- Do not adjust for effort, improvement, or likeability.

```markdown
**Evidence: Level 3**
Quote: "The policy reduced waiting times by 18% (Smith, 2024), but the study
excluded rural clinics."
Why: Relevant data with a limitation, but not connected to the thesis.
Next level: Explain how the exclusion weakens the generalizability claim.
```

### 5. Apply weights and boundaries

```
score = Σ (criterion_level / max_level) × weight
```

Then map to the grade boundary. Check for rubric policies such as "must pass mechanics to pass the assignment."

### 6. Write feedback

Feedback should:

- Name the criterion.
- Cite a specific passage.
- Explain the effect on the reader.
- Give one concrete revision move.
- Prioritize two or three changes, not twenty.

Avoid generic praise and vague advice ("be more critical"). Show what critical looks like in this essay.

### 7. Moderate

Sample at least 10% of essays or five papers, whichever is larger. A second grader scores independently. Disagreements above one level trigger review. Record the final score and the reason for any adjustment.

### 8. Audit for bias

Check score distributions by group where lawful and appropriate. Look for:

- Length bias: longer essays scoring higher after controlling for quality.
- Halo effect: one strong criterion lifting others.
- Grammar bias: mechanics dominating content.
- Familiarity bias: rewarding a style similar to the grader's.
- Prompt bias: cultural or experiential assumptions in the task.

## Gotchas

- Rubric descriptors like "excellent" or "shows understanding" are not observable. Rewrite them.
- Grading the introduction and skimming the rest produces halo effects.
- Grammar and mechanics can dominate impressions. Score content separately.
- AI-detection tools are unreliable and biased against non-native writers. Do not use them as sole evidence.
- The five-paragraph essay is a format, not a quality standard. Grade the rubric.
- Citations may be fabricated. Spot-check sources when research is a criterion.
- Accommodations may change format or time, not the standard. Apply consistently.
- A single grader's scores drift over a long session. Take breaks and re-anchor.
- Grade inflation is often a calibration failure, not a generosity problem.
- Feedback that lists every flaw reduces revision. Prioritize.

## Output contract

```json
{
  "submission_id": "E-2026-0142",
  "rubric_version": "v3",
  "scores": [
    {"criterion": "thesis", "level": 3, "weight": 0.25, "evidence": "...", "next_level": "..."},
    {"criterion": "evidence", "level": 3, "weight": 0.30, "evidence": "...", "next_level": "..."}
  ],
  "weighted_score": 0.78,
  "grade": "B+",
  "feedback": {
    "strengths": ["..."],
    "priorities": ["...", "..."]
  },
  "moderation": {"second_grader": "...", "agreement": "exact", "adjustment": null},
  "flags": ["possible fabricated citation at p.3"]
}
```

## Checklist

- [ ] Rubric parsed with observable descriptors.
- [ ] Anchors calibrated before grading.
- [ ] Whole essay read before scoring.
- [ ] Each criterion scored independently with evidence.
- [ ] Weights and boundaries applied.
- [ ] Feedback cites text and gives concrete moves.
- [ ] Moderation sample completed.
- [ ] Bias checks performed.
- [ ] Flags and appeals process documented.

## Related skills

- `source-grounded-citation-verification` for checking cited sources.
- `student-misconception-diagnosis` when errors reveal a conceptual gap.
- `accessibility-format-conversion` for accessible feedback formats.
