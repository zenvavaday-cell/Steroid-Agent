---
name: student-misconception-diagnosis
description: Diagnoses the root misconception behind a learner's errors using error classification, probe questions, contrasting cases, and confidence checks, then prescribes targeted remediation. Use for tutoring, assessment review, error analysis, and personalized learning plans.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: education
---

# Student Misconception Diagnosis

## Overview

A wrong answer has many causes: a careless slip, a missing prerequisite, a language issue, a procedural error, or a coherent but incorrect mental model. Only the last is a misconception. Treating every error as a misconception wastes time; missing one lets it persist.

Diagnosis is hypothesis testing. Collect evidence, propose the smallest explanation, probe it, and confirm before remediating.

## When to use

- A learner repeatedly makes the same error.
- A class shows a common wrong pattern on an assessment.
- A learner can follow steps but cannot explain why.
- A correct answer may be a lucky guess.

## Error taxonomy

| Type | Description | Example |
| --- | --- | --- |
| Careless | Knows the method, slips | Sign error under time pressure |
| Procedural | Wrong sequence or rule application | Adds numerators and denominators |
| Conceptual | Wrong mental model | "Heavier objects fall faster" |
| Representational | Misreads graph, table, or notation | Confuses slope with intercept |
| Language | Misunderstands the wording | "Evaluate" versus "solve" |
| Prerequisite | Missing prior knowledge | Cannot simplify fractions |
| Strategic | Does not know how to start | No plan for a word problem |
| Affective | Anxiety, avoidance, helplessness | Guesses to end the task |

## Workflow

### 1. Collect the artifact

Get the learner's actual work, not only the final answer. Look for:

- The first wrong step.
- Erasure marks and corrections.
- Whether the method is consistent across items.
- Time spent and confidence.

### 2. Classify the surface error

Use the taxonomy. If the same error appears across formats (symbolic, verbal, graphical), it is more likely conceptual. If it appears only under time pressure, it is more likely careless.

### 3. Generate hypotheses

Write 2–3 plausible explanations. Example for `1/2 + 1/3 = 2/5`:

- Conceptual: treats fractions as two independent whole numbers.
- Procedural: knows the rule but applies the wrong operation.
- Careless: copied the denominator incorrectly.
- Prerequisite: cannot find a common denominator.

### 4. Design a probe

Ask a question that distinguishes the hypotheses:

- "Show me with a diagram what one half plus one third means."
- "What would `1/2 + 1/4` be?"
- "Why do we need a common denominator?"

A probe should produce different evidence for different hypotheses, not just another chance to get the same answer.

### 5. Use contrasting cases

Present a minimal pair:

- `1/2 + 1/3` versus `1/2 × 1/3`.
- A correct worked example with one line changed.

Ask the learner to compare. Conceptual models often become visible in contrasts.

### 6. Check confidence

Ask: "How sure are you, and why?" High confidence with a wrong answer is a stronger misconception signal. Low confidence may indicate guessing or anxiety.

### 7. Confirm

A diagnosis is confirmed when:

- The learner's explanation matches the hypothesized model.
- The error generalizes to a new context.
- A targeted probe predicts the error.
- The learner does not make the error when the prerequisite is supplied.

If evidence is mixed, keep the hypothesis provisional.

### 8. Remediate

| Diagnosis | Remediation |
| --- | --- |
| Conceptual | Confront the model with a discrepant event; build the correct model concretely |
| Procedural | Model the steps, practice with faded worked examples |
| Prerequisite | Reteach the prerequisite before returning |
| Representational | Practice translating between graph, table, equation, and words |
| Language | Teach the vocabulary and the question structure |
| Careless | Slow down, check habits, error journal |
| Affective | Reduce pressure, build early success |

### 9. Retest

Use a new item with the same underlying concept and a different surface. Recheck after a delay to test retention, not immediate imitation.

## Gotchas

- One wrong answer is not a diagnosis. Collect multiple data points.
- A correct answer may come from memorized procedure or guessing. Ask for reasoning.
- Labeling a learner ("bad at math") is not a diagnosis. Describe the error, not the person.
- Language proficiency can look like a conceptual gap. Check vocabulary separately.
- Careless errors increase under time pressure and anxiety. Do not over-diagnose.
- Some "misconceptions" are correct in a limited domain. Surface the boundary.
- Confirmation bias: look for evidence against your hypothesis too.
- Remediation that only reteaches the same explanation may not displace the wrong model. Use a discrepant case.
- Immediate correct performance can be imitation. Retest later.
- Accommodations and learning differences require qualified assessment, not inference from a chat.

## Output contract

```json
{
  "learner_id": "L-1042",
  "task": "Add fractions with unlike denominators",
  "evidence": ["1/2 + 1/3 = 2/5", "1/2 + 1/4 = 2/6"],
  "surface_error": "adds numerators and denominators",
  "hypotheses": [
    {"type": "conceptual", "claim": "treats fraction as two whole numbers", "status": "confirmed"},
    {"type": "careless", "claim": "copied wrong", "status": "rejected"}
  ],
  "probe": "diagram of 1/2 + 1/3; learner drew two separate bars",
  "confidence": "high but wrong",
  "remediation": ["area model", "common denominator meaning", "faded worked examples"],
  "retest": {"date": "2026-12-01", "item": "3/4 + 1/6", "result": "pending"}
}
```

## Checklist

- [ ] Actual work collected, not just the answer.
- [ ] Error classified by type.
- [ ] Multiple hypotheses generated.
- [ ] Probe distinguishes hypotheses.
- [ ] Contrasting case used.
- [ ] Confidence checked.
- [ ] Diagnosis confirmed or marked provisional.
- [ ] Remediation matched to the cause.
- [ ] Delayed retest scheduled.

## Related skills

- `socratic-tutoring-scaffolding` for the tutoring interaction.
- `interactive-problem-hinting` for just-in-time hints.
- `longitudinal-mastery-tracking` for tracking whether the misconception returns.
