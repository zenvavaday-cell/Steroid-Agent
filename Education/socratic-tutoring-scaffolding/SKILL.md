---
name: socratic-tutoring-scaffolding
description: Tutors learners through calibrated Socratic questions and fading scaffolds instead of giving answers, adapting to evidence of understanding and frustration. Use for one-on-one tutoring, guided practice, conceptual explanations, and any learning interaction where the goal is durable understanding.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: education
---

# Socratic Tutoring Scaffolding

## Overview

The tutor's job is to make the learner do the cognitive work. Questions should diagnose and guide, not perform understanding. Scaffolds should be temporary: enough support to keep the learner moving, then removed.

This skill defines question types, scaffold levels, a session loop, and the signals that tell you to change approach.

## When to use

- A learner is working through a problem or concept.
- The learner has partial knowledge and needs guidance.
- You want to check reasoning, not just the final answer.
- A learner asks for the answer immediately.

Do not use pure Socratic questioning for safety-critical procedures, emergencies, or learners in distress. Give direct instruction when the cost of discovery is too high.

## Core loop

**Diagnose → question → listen → scaffold → apply → verify → fade.**

One question at a time. Wait for the answer. Do not answer your own question.

## Question types

| Type | Purpose | Example |
| --- | --- | --- |
| Clarification | Make thinking explicit | "What do you mean by 'the force cancels'?" |
| Assumption | Surface unstated premises | "What are you assuming about friction here?" |
| Evidence | Connect to data or text | "Which line in the passage supports that?" |
| Reasoning | Expose the inference | "How did you get from step 2 to step 3?" |
| Perspective | Consider alternatives | "What would happen if the mass were larger?" |
| Implication | Test consequences | "If that were true, what would the graph look like?" |
| Metacognitive | Build self-monitoring | "How would you check whether that is right?" |

Avoid leading questions ("Don't you think...?") and guessing games ("I'm thinking of a number..."). Ask genuine questions with multiple possible answers.

## Scaffold ladder

Start at the lowest level that keeps the learner productive. Move down only when the learner is stuck; move up as soon as they can proceed.

| Level | Scaffold | Example |
| --- | --- | --- |
| 0 | Neutral prompt | "What would you try next?" |
| 1 | Attention cue | "Look at the units in the second term." |
| 2 | Concept hint | "Remember what happens to exponents when you divide." |
| 3 | Partial step | "First rewrite both sides with the same base." |
| 4 | Worked example | Show a similar problem solved aloud. |
| 5 | Direct explanation | Explain the concept explicitly, then ask for application. |

Never jump to level 5 because the learner is quiet. Silence may be thinking time.

## Workflow

### 1. Set the goal and check prior knowledge

"By the end, you should be able to solve a problem like this on your own. Before we start, what do you already know about quadratic functions?"

Record the learner's self-report, but verify with a quick item. Self-report is a weak signal.

### 2. Present one problem

Keep the problem visible. Do not add a second problem until the first is resolved or explicitly parked.

### 3. Ask a diagnostic question

Use a question that reveals the model, not just the answer:

- "Walk me through your first step."
- "Why does that step work?"
- "What would change if the sign were negative?"

### 4. Listen for the gap

Classify the response:

| Response | Likely gap | Next move |
| --- | --- | --- |
| Correct reasoning | Mastery | Increase difficulty |
| Correct answer, no reasoning | Guessing or procedural | Ask for justification, give a transfer item |
| Wrong with a coherent model | Misconception | Probe with a contrasting case |
| Off-topic or "I don't know" | Missing prerequisite or affect | Lower scaffold, check prerequisite |
| Frustrated | Cognitive overload | Reduce difficulty, acknowledge, give a partial step |

### 5. Ask the next question

One question. Tailor it to the gap. Do not stack three questions in one turn.

### 6. Have the learner apply

After a hint, ask the learner to do the next step themselves. A learner who only agrees with your explanation has not learned it.

### 7. Verify with a transfer item

Ask a new problem that uses the same concept with a different surface. If they can only repeat the original, the understanding is fragile.

### 8. Fade and summarize

Remove scaffolds. Ask the learner to summarize the method in their own words and name one place they might get stuck.

## Session policy

- One question per turn.
- Wait at least a few seconds before rephrasing.
- Praise process ("good check of the units"), not intelligence.
- Treat errors as data, not failures.
- Never shame, diagnose, or label the learner.
- If the learner asks for the answer, give a choice: "Do you want a hint, a similar example, or the full solution?"
- If two scaffolds fail, switch representation (diagram, concrete numbers, analogy).
- End with a clear summary and a next-practice task.

## Gotchas

- Socratic questioning can become an interrogation. Balance questions with brief explanations.
- Leading questions teach the learner to read your tone, not the subject.
- A correct answer can hide a misconception. Ask for reasoning and test transfer.
- Too many hints creates learned helplessness. Fade deliberately.
- Frustration is not a teaching tool. Reduce load when affect drops.
- Analogies leak. State where the analogy stops working.
- Cultural and linguistic background affects participation. Allow think time and written responses.
- The learner's prior knowledge may be wrong, not missing. Probe before reteaching.
- A session that ends with "does that make sense?" has not verified anything. Ask them to do it.

## Output contract

```json
{
  "goal": "Solve a quadratic by factoring",
  "prior_knowledge": {"self_report": "some", "verified": "can factor monic trinomials"},
  "turns": [
    {"role": "tutor", "type": "diagnostic", "text": "..."},
    {"role": "learner", "text": "..."},
    {"role": "tutor", "type": "scaffold", "level": 2, "text": "..."}
  ],
  "gap": "does not check whether factors multiply to the constant",
  "scaffolds_used": [1, 2],
  "transfer_result": "passed",
  "summary": "...",
  "next_practice": "..."
}
```

## Checklist

- [ ] Goal and prior knowledge established.
- [ ] One question asked at a time.
- [ ] Response classified before choosing a scaffold.
- [ ] Scaffold at the lowest sufficient level.
- [ ] Learner applies the step, not just agrees.
- [ ] Transfer item used to verify.
- [ ] Scaffolds faded.
- [ ] Summary and next practice recorded.

## Related skills

- `student-misconception-diagnosis` when the gap is a persistent wrong model.
- `interactive-problem-hinting` for hint delivery inside practice problems.
- `longitudinal-mastery-tracking` to record progress over time.
