---
name: interactive-problem-hinting
description: Delivers just-in-time hints during practice problems using a graded hint ladder, error-aware triggering, and fading support, without leaking the answer. Use for tutoring systems, homework help, coding practice, and adaptive problem sets.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: education
---

# Interactive Problem Hinting

## Overview

A hint should reduce the next step's difficulty, not remove the thinking. The best hint tells the learner where to look or which principle applies. The worst hint gives the answer and ends the learning.

This skill defines hint levels, triggers, fading, and the evidence to track.

## When to use

- A learner is stuck on a practice problem.
- A tutoring system needs adaptive hints.
- A learner asks "is this right?" mid-problem.
- A problem has multiple valid solution paths.

Do not use hints to replace instruction when the learner lacks the prerequisite. Diagnose and reteach instead.

## Hint ladder

| Level | Name | Content | Example |
| --- | --- | --- | --- |
| 0 | Orient | Restate the goal or ask what is known | "What are you trying to find?" |
| 1 | Principle | Name the relevant concept or rule | "Use the zero-product property." |
| 2 | Strategy | Suggest the next move without doing it | "Factor the left side first." |
| 3 | Partial step | Do one small step, leave the rest | "The factors are (x−2)(x+3); what next?" |
| 4 | Worked analog | Show a similar problem solved | "Here is x²−5x+6 solved." |
| 5 | Answer | Give the final answer with explanation | Last resort, after effort or explicit request |

Start at the lowest level that unblocks the learner. Move up only after a genuine attempt.

## Workflow

### 1. Represent the problem as steps

Break the problem into a solution graph:

```json
{
  "problem_id": "P-104",
  "goal": "solve x^2 - 5x + 6 = 0",
  "steps": [
    {"id": "s1", "action": "factor the quadratic", "prereqs": []},
    {"id": "s2", "action": "apply zero-product property", "prereqs": ["s1"]},
    {"id": "s3", "action": "solve each linear equation", "prereqs": ["s2"]},
    {"id": "s4", "action": "check both solutions", "prereqs": ["s3"]}
  ],
  "common_errors": [
    {"pattern": "only one solution", "hint": "A quadratic can have two roots. Check both factors."},
    {"pattern": "sign error in factoring", "hint": "Multiply your factors back out. Do you get the middle term?"}
  ]
}
```

Multiple paths are allowed. The graph is a guide, not a script.

### 2. Detect the stuck state

Signals:

- No action for a while.
- Repeated wrong attempts on the same step.
- Asking for the answer.
- Off-topic response.
- Correct answer with no work.

Do not interrupt productive struggle. A learner thinking quietly is not stuck.

### 3. Diagnose the step

Identify where the learner is:

- Has not started.
- Started the wrong step.
- Applied the right step incorrectly.
- Completed the step but does not know why.
- Has the right answer but cannot verify it.

The hint targets the step, not the final answer.

### 4. Select the hint

```python
def choose_hint(attempts, last_error, asked_for_answer, level):
    if asked_for_answer and attempts >= 2:
        return min(level + 2, 5)
    if last_error == "sign_error":
        return 1
    if attempts == 0:
        return 0
    if attempts == 1:
        return 1
    if attempts >= 2:
        return min(level + 1, 4)
    return level
```

Rules:

- One hint per turn.
- Ask the learner to apply the hint before giving another.
- Do not stack levels in one message.
- If two hints fail, change the representation (diagram, concrete numbers, analogy).

### 5. Phrase the hint

- Use a question or an invitation, not a command.
- Point to evidence the learner can inspect.
- Avoid yes/no questions that reveal the answer.
- Keep technical vocabulary consistent with instruction.

Bad: "The answer is x = 2 and x = 3."
Better: "You factored correctly. What does the zero-product property let you conclude about each factor?"

### 6. Fade the support

Track hint level per learner and per concept. As success improves:

- Start at a lower level.
- Increase the wait time before offering.
- Remove the hint button for mastered items.
- Move to a different problem type.

### 7. Track evidence

Record:

- Attempts before the hint.
- Hint level and type.
- Whether the next step was correct.
- Whether the learner later solved a similar problem unaided.
- Hint dependence: hints per problem over time.

The goal is independent performance, not hint-assisted completion.

## Gotchas

- Answer leakage is easy: a "hint" that names the final value is not a hint.
- Hint abuse is a design problem. Make the learner attempt before the next level unlocks.
- Too-vague hints ("think harder") add frustration, not information.
- Too-specific hints turn the task into copying.
- A hint that only works for one solution path excludes valid alternatives.
- The learner may be stuck on reading, not the concept. Check comprehension.
- Sarcasm, pressure, or judgment shuts down help-seeking.
- Accessibility: hints must be readable by screen readers and not rely on color.
- A correct step after a hint is not mastery. Verify with a transfer item.
- Hints should be optional, not forced, for learners who want to struggle productively.

## Output contract

```json
{
  "problem_id": "P-104",
  "learner_id": "L-1042",
  "attempts": 2,
  "last_error": "only one root",
  "hint": {"level": 2, "type": "strategy", "text": "A quadratic can have two roots. Check both factors."},
  "next_expected_action": "solve each factor",
  "outcome": "correct",
  "transfer_check": {"problem_id": "P-105", "unaided": true},
  "hint_dependence": 0.33
}
```

## Checklist

- [ ] Problem represented as steps or a solution graph.
- [ ] Common errors mapped to hints.
- [ ] Stuck state detected without interrupting thinking.
- [ ] Hint level chosen from evidence.
- [ ] One hint per turn.
- [ ] Learner applies the hint before another.
- [ ] Support fades with success.
- [ ] Transfer check confirms learning.
- [ ] Hint dependence tracked.

## Related skills

- `socratic-tutoring-scaffolding` for the broader tutoring dialogue.
- `student-misconception-diagnosis` when hints do not resolve the error.
- `adaptive-spaced-repetition-scheduling` for follow-up retrieval practice.
