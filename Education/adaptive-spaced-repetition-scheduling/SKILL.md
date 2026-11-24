---
name: adaptive-spaced-repetition-scheduling
description: Schedules flashcard and retrieval practice with FSRS or SM-2, using difficulty, stability, and retrievability to set review dates under workload constraints. Use for vocabulary, certification prep, language learning, and any long-term retention system.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: education
---

# Adaptive Spaced Repetition Scheduling

## Overview

Spaced repetition schedules reviews just before forgetting. The scheduler estimates memory stability and predicts recall, then places the next review at the point of maximum efficiency.

FSRS (Free Spaced Repetition Scheduler) is the modern default. SM-2 is a simpler fallback. Both need honest grades and a workload cap.

## When to use

- Building or tuning a flashcard system.
- Scheduling reviews for a learner.
- Diagnosing a backlog or leech problem.
- Evaluating retention and workload trade-offs.

Do not use for one-off facts or material that must be understood before it can be memorized.

## Memory model

| Variable | Meaning |
| --- | --- |
| Difficulty (D) | How hard the item is for this learner |
| Stability (S) | Days until recall probability falls to 90% |
| Retrievability (R) | Probability of recall at time t |
| Grade | Again, Hard, Good, Easy |

FSRS approximates retrievability as:

```
R(t, S) = (1 + t / (9 * S))^(-1)
```

The next interval targets a desired retention, commonly 0.90.

## Workflow

### 1. Define the cards

A card should test one atomic fact or one tightly linked pair. Bad: "Explain the French Revolution." Good: "In what year did the French Revolution begin?" with answer 1789.

For each card, store:

```json
{
  "card_id": "C-001",
  "front": "What year did the French Revolution begin?",
  "back": "1789",
  "deck": "European history",
  "tags": ["revolution", "dates"],
  "source": "Course reader p.12",
  "state": "new"
}
```

### 2. Collect honest grades

| Grade | Meaning |
| --- | --- |
| Again | Failed to recall, or recalled incorrectly |
| Hard | Recalled with serious difficulty |
| Good | Recalled correctly with normal effort |
| Easy | Immediate, effortless recall |

Grade inflation destroys the model. "Good" is not a courtesy.

### 3. Update the memory state

Using the `fsrs` Python package:

```python
from fsrs import Scheduler, Card, Rating
from datetime import datetime, timezone

scheduler = Scheduler(desired_retention=0.90)
card = Card()

def review(card, rating):
    card, review_log = scheduler.review_card(card, rating)
    return card, review_log

card, log = review(card, Rating.Good)
print(card.due, card.stability, card.difficulty)
```

SM-2 fallback:

```python
def sm2(interval, repetitions, ease, quality):
    # quality: 0-5; below 3 resets the item
    if quality < 3:
        return 1, 0, max(1.3, ease - 0.2)
    ease = max(1.3, ease + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    if repetitions == 0:
        interval = 1
    elif repetitions == 1:
        interval = 6
    else:
        interval = round(interval * ease)
    return interval, repetitions + 1, ease
```

### 4. Cap the workload

Set daily limits:

- New cards per day.
- Review cards per day.
- Total study minutes.

If the due queue exceeds capacity, prioritize:

1. Overdue cards with low stability.
2. Cards from upcoming assessments.
3. New cards only after reviews are under control.

Do not let a backlog force a 400-card day. Reduce new cards and spread the backlog.

### 5. Handle leeches

A leech is a card failed repeatedly, often because it is badly written or lacks context. After 8 failures:

- Rewrite the card into smaller pieces.
- Add a mnemonic or context cue.
- Suspend it if it is not essential.
- Check whether the underlying concept is understood.

### 6. Schedule around real constraints

- Use the learner's timezone for day boundaries.
- Avoid scheduling heavy reviews the night before an exam.
- Interleave related decks when the goal is discrimination.
- Keep assessment dates as hard constraints, not just due dates.

### 7. Measure

Track:

- True retention: percent of reviews graded Good or Easy.
- Workload: reviews per day and minutes.
- Mature card retention versus young card retention.
- Leech rate.
- Backlog size.

Target retention depends on the stakes. 0.85–0.90 is efficient for most learners; 0.95 costs more reviews.

## Gotchas

- The scheduler is only as good as the grades. Inconsistent grading produces erratic intervals.
- "Again" is not a punishment. Honest failures improve the model.
- A card that tests multiple facts causes interference. Split it.
- Recognition is not recall. Multiple-choice prompts overestimate retention.
- Same-day reviews inflate stability estimates. Follow the scheduler's minimum interval.
- Timezone and daylight-saving changes can shift due dates. Normalize to the learner's local day.
- A long absence creates a backlog. Do not reset all cards; prioritize and reduce new intake.
- FSRS parameters can be personalized from review history, but need enough data. Start with defaults.
- Retention measured only on scheduled reviews is biased. Include delayed transfer checks.
- Scheduling is not learning. Understanding still requires explanation, examples, and practice.

## Output contract

```json
{
  "learner_id": "L-1042",
  "deck": "European history",
  "date": "2026-11-24",
  "due_reviews": 42,
  "new_cards": 10,
  "scheduled": [
    {"card_id": "C-001", "rating": "good", "stability": 12.4, "next_due": "2026-12-06"}
  ],
  "workload": {"minutes": 28, "cap": 45},
  "leeches": ["C-118"],
  "retention_30d": 0.88,
  "adjustments": ["suspend 2 low-value cards", "reduce new cards to 5"]
}
```

## Checklist

- [ ] Cards are atomic and source-grounded.
- [ ] Grades use explicit criteria.
- [ ] Scheduler configured with a target retention.
- [ ] Daily workload capped.
- [ ] Overdue backlog prioritized.
- [ ] Leeches rewritten or suspended.
- [ ] Timezone and assessment dates respected.
- [ ] Retention and workload monitored.

## Related skills

- `automated-flashcard-synthesis` for generating atomic cards.
- `longitudinal-mastery-tracking` for connecting retention to mastery.
- `curriculum-grounded-quiz-generation` for assessment-style retrieval.
