---
name: syllabus-alignment-verification
description: Verifies constructive alignment among learning outcomes, assessments, learning activities, and content, producing a coverage matrix and flagging gaps, over-assessment, and cognitive-level mismatches. Use for course design, accreditation review, curriculum audits, and syllabus revision.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: education
---

# Syllabus Alignment Verification

## Overview

Constructive alignment means students learn what the outcomes promise, practice what the assessments measure, and are assessed on what the activities prepared them for. Many syllabi list outcomes that no assessment measures and assessments that no activity prepares.

This skill builds the matrix and finds the gaps.

## When to use

- Designing or revising a course.
- Preparing for accreditation or program review.
- Auditing a syllabus before delivery.
- Checking whether assessments match stated outcomes.
- Comparing multiple sections of the same course.

## Workflow

### 1. Extract learning outcomes

For each outcome, capture:

```json
{
  "id": "LO-3",
  "statement": "Analyze experimental data to distinguish correlation from causation.",
  "bloom": "analyze",
  "standard": "LS1-3",
  "assessment_weight": 0.20
}
```

Flag outcomes that use vague verbs ("understand", "know", "be aware of"). They cannot be measured. Rewrite them with observable verbs before checking alignment.

### 2. Classify cognitive level

Use Bloom's revised taxonomy:

| Level | Verbs |
| --- | --- |
| Remember | define, list, recall |
| Understand | explain, classify, summarize |
| Apply | solve, use, implement |
| Analyze | compare, differentiate, deconstruct |
| Evaluate | judge, critique, justify |
| Create | design, construct, produce |

If an outcome says "analyze" but the assessment is a multiple-choice recall quiz, the alignment is broken.

### 3. Map assessments

For each assessment, capture:

- Format and weighting.
- Outcomes it claims to measure.
- Cognitive level of the items.
- Timing and feedback.

```json
{
  "id": "A-2",
  "name": "Lab report",
  "weight": 0.25,
  "outcomes": ["LO-3", "LO-4"],
  "bloom": "analyze",
  "feedback": "rubric within 7 days"
}
```

### 4. Map activities and content

For each learning activity, capture the outcomes it prepares and the practice it provides:

- Lectures, readings, labs, discussions, problem sets.
- Formative checks and feedback.
- Scaffolded practice.

An outcome with no practice activity is a promise the course does not keep.

### 5. Build the coverage matrix

| Outcome | Taught by | Practiced by | Assessed by | Cognitive match | Status |
| --- | --- | --- | --- | --- | --- |
| LO-1 | Week 1 lecture | Problem set 1 | Quiz 1 | yes | aligned |
| LO-3 | Weeks 3–4 lab | Lab 2 | Lab report | yes | aligned |
| LO-5 | Week 6 lecture | none | Final exam | no | gap: no practice |

### 6. Check the rules

| Check | Rule |
| --- | --- |
| Coverage | Every outcome is assessed at least once |
| Mapping | Every assessment maps to at least one outcome |
| Cognitive match | Assessment level meets or exceeds the outcome verb |
| Practice | Every summative outcome has formative practice |
| Weight | Weight reflects emphasis and time on task |
| Prerequisites | Content sequence respects prerequisite order |
| Standards | External standards are covered |
| Feedback | Students receive feedback before the next high-stakes task |

### 7. Report and recommend

For each gap, give a specific fix:

- Add an assessment for an unmeasured outcome.
- Replace a recall quiz with an analysis task.
- Add practice before a high-stakes assessment.
- Reduce an over-weighted assessment.
- Reword a vague outcome.

Prioritize changes by impact and feasibility.

### 8. Re-verify

After changes, rebuild the matrix. Confirm that the new assessment actually measures the outcome at the intended level, not just that a row is filled.

## Gotchas

- A syllabus can claim alignment on paper while the actual assessment measures something else. Inspect the items, not only the table.
- Vague outcomes make alignment impossible. Rewrite first.
- One assessment can cover several outcomes, but each outcome still needs evidence.
- Over-assessment is a workload problem, not a rigor signal.
- Formative activities often disappear from the syllabus. Check the LMS and weekly plan.
- Accreditation standards may require outcomes not stated in the syllabus. Map them explicitly.
- Weighting by percentage is not the same as emphasis in class time. Compare both.
- Implicit curriculum (what is actually taught) can differ from the document. Ask the instructor.
- A course may rely on prerequisites taught elsewhere. Verify, do not assume.
- Version control matters. Align the syllabus students received, not an old draft.

## Output contract

```markdown
# Alignment Review: <course>

## Outcomes
| ID | Statement | Bloom | Status |
| --- | --- | --- | --- |

## Coverage matrix
| Outcome | Taught | Practiced | Assessed | Cognitive match | Status |
| --- | --- | --- | --- | --- | --- |

## Gaps
| Gap | Impact | Recommendation | Owner |
| --- | --- | --- | --- |

## Over-assessment and workload
<...>

## Standards coverage
<...>

## Decision
<approved | revise and resubmit>
```

## Checklist

- [ ] Outcomes extracted and rewritten with observable verbs.
- [ ] Bloom level assigned to each outcome.
- [ ] Assessments mapped with weights and levels.
- [ ] Activities mapped to outcomes.
- [ ] Coverage matrix built.
- [ ] Cognitive match checked.
- [ ] Practice before summative assessment confirmed.
- [ ] Gaps have concrete recommendations.
- [ ] Re-verification scheduled after changes.

## Related skills

- `curriculum-grounded-quiz-generation` for building aligned assessments.
- `prerequisite-knowledge-mapping` for sequencing.
- `rubric-aligned-essay-grading` for constructed-response alignment.
