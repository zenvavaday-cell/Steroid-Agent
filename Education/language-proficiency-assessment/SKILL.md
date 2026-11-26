---
name: language-proficiency-assessment
description: Scores speaking and writing against CEFR or ACTFL descriptors with evidence and actionable feedback. Use for placement, progress, and certification prep.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: education
---

# Language Proficiency Assessment

## Overview

Proficiency is what a learner can do with the language in an unrehearsed, level-appropriate task. It is not the number of units completed, the grammar points covered, or a single impressive sentence. A defensible rating ties each score to a published descriptor and to evidence in the sample.

This skill covers task design, analytic rating, rater calibration, agreement checks, and feedback. It assumes the assessor has the authority to score and knows the difference between proficiency and course achievement.

## When to use

- Placing learners into a course or level.
- Measuring speaking or writing progress across a term.
- Preparing learners for a CEFR or ACTFL aligned certification task.
- Calibrating a team of raters before a scoring session.
- Auditing existing scores for consistency and evidence quality.
- Screening applicants for a language-dependent program.

Do not use for high-stakes certification with a single untrained rater, for legal or immigration decisions, or as a substitute for the official exam a credential requires.

## Workflow

### 1. Fix the purpose and consequence level

| Purpose | Consequence | Minimum evidence | Raters |
| --- | --- | --- | --- |
| Classroom progress | Low | One speaking and one writing sample per term | 1, sampled for moderation |
| Program placement | Medium | Two tasks per modality, common prompts | 2, or 1 plus audit |
| Certification readiness | High | Full task set under timed conditions | 2 independent, adjudication on any gap |
| Employment screening | High | Validated tasks plus a structured interview | 2 plus a review panel |

Write the consequence level down before designing tasks. It determines sample sufficiency and rater count.

### 2. Choose one framework and hold it

Use CEFR (A1 to C2) or ACTFL (Novice Low through Distinguished). Do not mix labels in one report, and do not convert scores between frameworks with an unvalidated table.

- CEFR describes communicative ability through can-do descriptors, including interaction, production, and mediation in the 2020 companion volume.
- ACTFL describes functional performance across major levels and sublevels, with Superior and Distinguished above the High sublevel.
- Both frameworks assume task conditions matter: topic familiarity, time, support, and genre change performance.

Record the framework, version, and target band in the report header.

### 3. Design tasks that reach the target band

A task at B1 that only requires memorized phrases cannot show B1 ability. Build tasks that require the target functions and allow evidence above the target.

```json
{
  "task_id": "SP-2",
  "modality": "speaking",
  "target_band": "B1",
  "function": "describe, compare, and give reasons",
  "prompt": "Compare two commuting options for your city and recommend one.",
  "planning_seconds": 60,
  "response_seconds": 120,
  "interlocutor_script": "Ask one follow-up about cost and one about reliability.",
  "supports": "none",
  "evidence_required": ["topic development", "coherence", "range", "accuracy", "fluency"]
}
```

For writing, specify genre, audience, word range, time, and whether dictionaries or spell-check are allowed. Those conditions belong in the score interpretation.

### 4. Build an analytic rubric with observable descriptors

Score criteria separately, then report a profile. A single holistic number hides the reason for the rating.

| Criterion | What the rater looks for | Evidence source |
| --- | --- | --- |
| Task completion | All parts of the prompt addressed with relevant content | Content map against prompt |
| Coherence | Ideas ordered with understandable links | Discourse markers, paragraphing |
| Lexical range | Vocabulary adequate for the topic and band | Repeated words, paraphrases, precision |
| Grammatical accuracy | Errors by type and effect on meaning | Error tally, not a general impression |
| Fluency and pronunciation | Flow, pauses, intelligibility for a listener | Timed sample, listener notes |
| Register and appropriateness | Address, tone, and politeness fit the audience | Greeting, request forms, closings |

Descriptors must name what the learner does, not how good they seem. Replace "excellent vocabulary" with "uses varied, precise vocabulary for the topic with occasional circumlocution."

### 5. Standardize collection

Hold the prompt, time, tools, and setting constant across candidates in a comparison group. Record:

- Prompt ID and version.
- Date, duration, and modality.
- Device and recording method.
- Permitted supports and accommodations.
- Interlocutor behavior for speaking tasks.

For writing, capture the draft in the tool used. For speaking, keep the recording and a time-stamped transcript of key evidence.

### 6. Rate independently, then adjudicate

Each rater reads or listens once for meaning, then again for evidence. For every criterion, require a note with a timestamp or line reference.

```markdown
Criterion: coherence
Rating: B1
Evidence: 00:48 to 01:05, compares cost with two linked reasons;
01:30 switches topic without a signal.
Why not B2: no developed argument, limited linking across paragraphs.
```

Adjudication rules:

- Difference of one sublevel: discuss evidence and agree, or average only if the rubric permits it.
- Difference of two or more sublevels: third rater or full re-rating.
- Any disagreement on a certification decision: resolve before release.

### 7. Measure and report agreement

Calculate exact agreement, adjacent agreement, and weighted kappa for ordinal levels. Use a default gate of kappa 0.70 or higher and adjacent agreement of 90% or higher. These are policy defaults; set stricter values for certification.

If agreement fails, do not average the disagreement away. Recalibrate with anchor samples, revise ambiguous descriptors, and re-rate a fresh sample.

### 8. Write the feedback

Feedback must connect a descriptor, evidence, and a next move.

```markdown
**Speaking: B1 (target B1)**
Evidence: You sustained comparison for 90 seconds and supported your recommendation with cost and time.
Next move: Link reasons with "whereas" and "that said" and add one counterpoint. At B2 the listener expects a developed position, not a list.
Practice: Record a 2-minute response to the same prompt twice, once with a 60-second plan.
```

Separate proficiency from course grades. A learner can be B1 and still fail a course requirement for missing work.

## Validation

| Gate | Pass criterion | Fail action |
| --- | --- | --- |
| Framework consistency | One framework and version named in the report | Strip mixed labels |
| Task alignment | Each task requires the target functions and band | Redesign before scoring |
| Rubric observability | Every descriptor names observable behavior | Rewrite vague levels |
| Sample sufficiency | Meets the purpose table minimum | Collect more evidence or lower the claim |
| Evidence coverage | Every criterion has a citation | Re-rate the missing criterion |
| Rater calibration | Anchor set scored before live samples | Calibrate, then start |
| Agreement | Kappa 0.70+ and adjacent 90%+ | Recalibrate and re-rate |
| Feedback actionability | Each next step names a behavior and a practice task | Rewrite |
| Privacy | Recordings and transcripts stored in the approved system | Remove and report |

Report the confidence level with the score. A placement based on one five-minute sample is provisional.

## Gotchas

- Grammatical accuracy dominates impressions. Rate meaning and range before counting errors.
- One sample cannot support a level claim. Use at least two tasks per modality for decisions.
- Topic familiarity inflates performance. Use familiar and unfamiliar topics for high-stakes decisions.
- Fluency is mistaken for proficiency. A smooth speaker can be vague; check content and range.
- Raters drift over a long session. Re-anchor every 20 to 25 samples and take breaks.
- CEFR levels are not percentages. Do not report "72% B1."
- ACTFL sublevels are not equally spaced. Do not average them as interval data.
- Machine translation or generated text changes the construct. State the policy and verify authorship when it matters.
- Native-speaker pronunciation is not the target. Intelligibility and communicative effect are.
- Translation tasks measure translation skill, not general proficiency. Label them separately.
- Accommodations can change task conditions. Report them with the score.
- A placement test used alone misplaces borderline learners. Combine with a writing sample and an interview.

## Output contract

```json
{
  "candidate_ref": "L-2087",
  "framework": "CEFR",
  "framework_version": "2020 companion volume",
  "purpose": "program placement",
  "assessed_on": "2026-11-18",
  "tasks": [
    {"id": "SP-2", "modality": "speaking", "target_band": "B1", "duration_seconds": 180}
  ],
  "profile": [
    {"criterion": "task_completion", "level": "B1", "evidence": "00:12-01:40", "next": "address the counterargument"}
  ],
  "overall": {"level": "B1", "confidence": "medium", "rationale": "consistent B1 across both modalities; no sustained B2"},
  "can_do": ["compare options and give reasons", "handle a routine transaction"],
  "not_yet": ["develop a structured argument across paragraphs"],
  "feedback": {"strengths": ["clear recommendations"], "priorities": ["cohesion", "range"]},
  "practice_plan": ["two recorded comparisons per week with a planning step"],
  "accommodations": [],
  "rater": {"count": 2, "agreement": "adjacent", "kappa": 0.74}
}
```

## Checklist

- [ ] Purpose and consequence level recorded.
- [ ] One framework and version selected.
- [ ] Tasks require target-band functions, not recall.
- [ ] Rubric descriptors are observable and criterion-specific.
- [ ] Administration conditions standardized and documented.
- [ ] Minimum sample size met for the consequence level.
- [ ] Two raters used for medium and high stakes.
- [ ] Every score has a timestamp or line citation.
- [ ] Agreement calculated and threshold met.
- [ ] Discrepancies adjudicated by rule.
- [ ] Feedback names evidence and a next practice task.
- [ ] Proficiency kept separate from course achievement.

## Related skills

- `rubric-aligned-essay-grading` for analytic scoring mechanics and bias controls.
- `longitudinal-mastery-tracking` for recording level changes across terms.
- `differentiated-reading-level-adaptation` for matching texts to proficiency bands.
- `automated-flashcard-synthesis` for turning feedback targets into retrieval practice.
