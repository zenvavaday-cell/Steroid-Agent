---
name: curriculum-grounded-quiz-generation
description: Generates quizzes and assessments anchored to curriculum standards, learning objectives, and source material, with coverage blueprints, cognitive-level targeting, distractor rationales, and answer validation. Use for formative assessment, exam drafting, practice sets, and standards alignment.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: education
---

# Curriculum-Grounded Quiz Generation

## Overview

A quiz is a measurement instrument. It should sample the intended objectives, target the intended cognitive demand, and have one defensible correct answer. Generating items from a model's general knowledge produces trivia and ambiguity.

Ground every item in a named objective and a source passage.

## When to use

- Drafting a formative or summative quiz.
- Building a question bank from a curriculum.
- Creating practice items for a specific standard.
- Auditing an existing quiz for coverage and alignment.

## Workflow

### 1. Ingest the curriculum

Collect:

- Standards or syllabus codes.
- Learning objectives, preferably with observable verbs.
- Source texts, chapters, and page ranges.
- Prerequisite knowledge.
- Item formats allowed.
- Time limit and difficulty target.

### 2. Build the assessment blueprint

| Objective | Standard | Bloom level | Items | Format | Weight |
| --- | --- | --- | --- | --- | --- |
| Explain photosynthesis | LS1-5 | Understand | 3 | MCQ, short answer | 20% |
| Analyze data from an experiment | LS1-3 | Analyze | 2 | Graph + short answer | 25% |

A blueprint prevents a quiz that tests only recall because recall is easy to generate.

### 3. Choose item types

| Type | Strength | Watch-out |
| --- | --- | --- |
| Multiple choice | Fast, objective | Guessing, ambiguous distractors |
| Multiple select | Tests discrimination | Partial credit rules |
| Short answer | Tests production | Scoring variance |
| Matching | Tests relationships | Process of elimination |
| Ordering | Tests sequence | Guessing by pattern |
| Scenario | Tests transfer | Long reading load |
| Diagram labeling | Tests representation | Accessibility |

### 4. Generate items with source anchors

For each item:

```json
{
  "objective": "LS1-5",
  "bloom": "understand",
  "stem": "Which statement best explains why a plant kept in the dark stops producing oxygen?",
  "options": [
    {"text": "Light is required for the light-dependent reactions.", "correct": true, "rationale": "Matches source p.142."},
    {"text": "Carbon dioxide is unavailable in the dark.", "correct": false, "rationale": "CO2 is still present; this confuses the inputs of the Calvin cycle."},
    {"text": "Respiration stops in the dark.", "correct": false, "rationale": "Respiration continues; it does not require light."},
    {"text": "Chlorophyll is destroyed by darkness.", "correct": false, "rationale": "Chlorophyll is not destroyed by a normal dark period."}
  ],
  "source": {"text": "Biology, ch. 6, p.142", "quote": "The light-dependent reactions require photons to split water and release oxygen."}
}
```

Every distractor should encode a plausible misconception, not random noise.

### 5. Validate each item

| Check | Question |
| --- | --- |
| Correctness | Is the key unambiguously correct? |
| Source | Is the claim supported by the cited passage? |
| Ambiguity | Could an expert defend another option? |
| Distractors | Does each wrong option reflect a real error? |
| Cognitive level | Does the item require the intended thinking? |
| Reading load | Is the language simpler than the concept being tested? |
| Bias | Does it assume irrelevant cultural or personal experience? |
| Accessibility | Does it work with a screen reader and without color? |

### 6. Assemble forms

Balance objectives, difficulty, and item types. Avoid answer-key patterns (A, A, A, A) and order effects. Provide a calculator or reference sheet if the objective is not calculation fluency.

### 7. Pilot and revise

If possible, pilot on a small group. Compute:

- Item difficulty (proportion correct).
- Discrimination (point-biserial or upper/lower 27%).
- Distractor distribution.
- Time per item.

Revise items with negative discrimination, non-functioning distractors, or ambiguous keys.

## Gotchas

- "Which of the following is NOT" adds reading load and often tests attention, not knowledge.
- "All of the above" and "none of the above" change the logic of the item. Use sparingly.
- Long stems with irrelevant detail test reading speed.
- The most detailed option is often the correct one, letting test-wise students guess. Balance option length.
- Vocabulary above the grade level confounds content with reading ability.
- Generated items can hallucinate source claims. Verify the quote.
- A single correct answer can still be ambiguous if the stem is underspecified.
- Recall items are easy to write but may not match the objective's cognitive level.
- Copying copyrighted items requires permission. Generate original wording.
- Answer keys should be reviewed by a second person before use.

## Output contract

```json
{
  "title": "Photosynthesis Formative Quiz",
  "standards": ["LS1-5", "LS1-3"],
  "blueprint": [{"objective": "LS1-5", "bloom": "understand", "items": 3}],
  "items": [{"id": "Q1", "objective": "LS1-5", "stem": "...", "options": [], "answer": "...", "source": "...", "difficulty": "medium"}],
  "coverage": {"LS1-5": 3, "LS1-3": 2},
  "review": {"answer_key_checked": true, "bias_review": true},
  "time_estimate_minutes": 20
}
```

## Checklist

- [ ] Curriculum and standards ingested.
- [ ] Blueprint covers objectives and cognitive levels.
- [ ] Item types chosen deliberately.
- [ ] Every item has a source anchor.
- [ ] Distractors map to misconceptions.
- [ ] Ambiguity and bias reviewed.
- [ ] Answer key independently checked.
- [ ] Coverage and time balanced.
- [ ] Pilot data used to revise if available.

## Related skills

- `rubric-aligned-essay-grading` for constructed-response scoring.
- `student-misconception-diagnosis` for using distractor patterns diagnostically.
- `syllabus-alignment-verification` for checking coverage at the course level.
