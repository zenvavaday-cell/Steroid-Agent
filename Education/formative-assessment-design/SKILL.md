---
name: formative-assessment-design
description: Creates low-stakes checks that reveal misconceptions and inform the next instructional move. Use for lesson planning and responsive teaching.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: education
---

# Formative Assessment Design

## Overview

Formative assessment is a decision tool, not a quiz bank. The point is to find out what students actually think before the summative assessment, then change the next move. A check that produces a score but no instructional response is just a small test.

This skill covers learning intentions, misconception-driven item design, all-student response, pre-committed decision rules, and the feedback loop that closes the lesson.

## When to use

- Planning a lesson that introduces a fragile or commonly misunderstood concept.
- Deciding whether to move on, reteach, or pull a small group.
- Building exit tickets or hinge questions for a unit.
- Converting a worksheet or quiz into a diagnostic check.
- Helping a teaching team agree on evidence of understanding.
- Auditing checks that produce data nobody uses.

Do not use to grade students, to rank classes, or as a substitute for a summative assessment when a defensible score is required.

## Workflow

### 1. State the learning intention and success criteria

Write what students should be able to do by the end, in language they can use. Then write two or three success criteria that describe observable performance.

```markdown
Learning intention: Explain how a change in supply affects equilibrium price and quantity.
Success criteria:
- I can shift the correct curve.
- I can state the direction of the price and quantity change.
- I can explain the mechanism in one causal chain.
```

If the success criteria cannot be observed in a two-minute response, they are too broad for a check.

### 2. Name the likely misconceptions first

Do not write items until you know what wrong thinking you are looking for. Sources:

- Previous exit tickets and item analysis.
- Common errors in student work.
- Research on the topic, if available.
- Your own experience of the three most frequent wrong answers.

```json
{
  "misconception_id": "M-2",
  "statement": "A supply increase raises price because there is more product",
  "why_plausible": "Confuses quantity supplied with value",
  "diagnostic_signal": "Chooses 'price rises' and justifies with 'more product'"
}
```

Each item should distinguish between the target understanding and at least one named misconception.

### 3. Choose the check type

| Check | When | Time | What it tells you |
| --- | --- | --- | --- |
| Diagnostic item | Before a unit | 5 to 10 min | Prior knowledge and entering misconceptions |
| Hinge question | Mid-lesson, before independent practice | 2 to 3 min | Whether the class can proceed |
| Exit ticket | Last 5 minutes | 3 to 5 min | Who needs what next lesson |
| Observation checklist | During practice | Continuous | Whether students use the method |
| Self-assessment | Before submission | 2 min | Whether students can judge their own work |

Choose the least burdensome check that can change a decision. One good hinge question beats five activities.

### 4. Write items with a misconception map

For a multiple-choice hinge question:

- One unambiguously correct answer.
- Each distractor maps to a named misconception.
- No "all of the above," no double negatives, no trick wording.
- Reading demand below the content demand, unless reading is the target.
- Four options at most.

```markdown
Question: A new fertilizer raises corn yields. What happens in the corn market?
A. Price falls, quantity rises. (correct)
B. Price rises, quantity rises. (M-2: more product means more value)
C. Price falls, quantity falls. (M-5: confuses shift with movement along the curve)
D. Price is unchanged. (M-7: believes supply does not affect price)
```

Keep the map in the teacher guide, not on the student handout.

### 5. Plan an all-student response method

A check that only hears from volunteers is a sample of the confident. Use a method that makes every student commit:

- Mini-whiteboards or digit tablets held up.
- Colored cards for A/B/C/D.
- A quick poll with a visible distribution.
- Think, write, pair, share, then cold call with the written response in hand.
- A one-question Google Form or LMS quiz with instant aggregation.

For written responses, circulate and tally rather than collecting every paper. The tally is the data.

### 6. Pre-commit the decision rule

Write the rule before you see the results. Otherwise the data will be interpreted to fit the plan you already made.

| Result | Interpretation | Next move |
| --- | --- | --- |
| 85% or more correct | Most students can proceed | Move to independent practice; check reasoning on two responses |
| 70 to 84% correct | Mixed understanding | Brief reteach of the specific error, then a second check |
| 50 to 69% correct | Core misconception persists | Reteach with a contrasting case; small-group support |
| Below 50% correct | Prerequisite gap or ambiguous item | Check the item, then reteach the prerequisite |

These thresholds are defaults. Adjust for the item's difficulty and the consequence of moving on too early. Always inspect the reasoning, not only the proportion.

### 7. Respond within the lesson or the next lesson

The response must be visible to students:

- Name the pattern without naming individuals: "Fourteen of you chose B; let's look at why."
- Show the contrasting case that breaks the misconception.
- Ask a student with the correct response to explain the mechanism, not just the answer.
- Give a short second check to confirm the fix.

If the check reveals a prerequisite gap, do not reteach the whole unit. Teach the missing step and give a targeted practice set.

### 8. Record and close the loop

Keep a simple tracker by item and student group, not by individual score.

```json
{"date": "2026-11-09", "item": "H-3", "correct": 21, "total": 28, "top_distractor": "B", "misconception": "M-2", "response": "contrasting case plus second check", "follow_up": "small group of 4 on Thursday"}
```

Tell students what the data showed and what changed. A check whose results disappear teaches students that the exercise was theater.

## Validation

| Gate | Pass criterion | Fail action |
| --- | --- | --- |
| Intention clarity | Success criteria are observable and student-facing | Rewrite |
| Misconception map | Every distractor has a named misconception | Add or remove options |
| Item quality | One defensible answer, no trick wording | Revise and peer-review |
| Reading demand | Item reading level does not block content access | Simplify or read aloud per policy |
| All-student response | Every student commits to an answer | Change the method |
| Decision rule | Written before administration | Write it now, then administer |
| Timing | Check fits the stated window | Cut items |
| Response | Instructional move occurs within one lesson | Schedule it explicitly |
| Record | Item-level tally stored and used | Add tracker |
| Low stakes | No grade or penalty attached | Remove grading |

Run a peer review of the item before class. If two teachers disagree about the correct answer, students will too.

## Gotchas

- Assessing what is easy to score instead of what matters. Start from the misconception.
- "Any questions?" is not a check. Students do not know what they do not know.
- Calling on volunteers produces a biased sample. Use all-student response.
- Grading a formative check turns it into a summative one and changes student behavior.
- Reteaching the whole class when five students missed an item wastes the other twenty-five minutes.
- Collecting exit tickets and never returning to them. The response is the assessment.
- Ambiguous distractors create false data. Pilot the item or ask a colleague to take it.
- Language demand masks content knowledge. Simplify wording for multilingual learners.
- A correct answer can hide weak reasoning. Ask for a one-sentence justification.
- Too many checks per lesson crowds out practice. One or two high-value checks are enough.
- Ignoring the top distractor. The wrong answer is the most useful information.
- Treating a 70% class average as success when the same 30% is lost every time.

## Output contract

```json
{
  "lesson": "Supply and equilibrium",
  "learning_intention": "Explain how a supply change affects price and quantity",
  "success_criteria": ["shift the correct curve", "state direction of both changes", "explain the causal chain"],
  "misconceptions": [
    {"id": "M-2", "statement": "More product means higher price", "signal": "chooses price rises with quantity rises"}
  ],
  "checks": [
    {
      "id": "H-3",
      "type": "hinge",
      "timing": "after guided example",
      "items": [
        {"stem": "A new fertilizer raises corn yields. What happens in the corn market?", "options": {"A": "price falls, quantity rises", "B": "price rises, quantity rises", "C": "price falls, quantity falls", "D": "no change"}, "answer": "A", "distractor_map": {"B": "M-2", "C": "M-5", "D": "M-7"}}
      ],
      "response_method": "whiteboards",
      "decision_rule": {"advance": 0.85, "reteach": 0.70, "prerequisite_check": 0.50}
    }
  ],
  "record": {"fields": ["date", "item_id", "correct", "total", "top_distractor", "response", "follow_up"]},
  "student_closure": "Report the pattern and the change at the start of the next lesson"
}
```

## Checklist

- [ ] Learning intention and observable success criteria written.
- [ ] Misconceptions named before items were drafted.
- [ ] Check type chosen to match the decision.
- [ ] Every distractor mapped to a misconception.
- [ ] Item reviewed for ambiguity and reading demand.
- [ ] All-student response method selected.
- [ ] Decision rule written before administration.
- [ ] Results tallied by item, not just by student.
- [ ] Instructional response delivered within one lesson.
- [ ] Second check used to confirm the fix.
- [ ] No grade attached to the check.
- [ ] Students told what the data showed and what changed.

## Related skills

- `student-misconception-diagnosis` for deeper analysis when one error pattern persists.
- `curriculum-grounded-quiz-generation` for building item banks from course materials.
- `socratic-tutoring-scaffolding` for the follow-up conversation with a small group.
- `longitudinal-mastery-tracking` for connecting checks across a unit.
