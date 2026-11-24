---
name: automated-flashcard-synthesis
description: Converts source material into atomic, unambiguous flashcards with source citations, deduplication, and quality checks. Use for study decks, language learning, certification prep, and turning notes or documents into retrieval practice.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: education
---

# Automated Flashcard Synthesis

## Overview

A good flashcard tests one thing, has one defensible answer, and makes sense without the surrounding page. Most generated decks fail on at least one of these: multi-fact cards, orphan pronouns, ambiguous prompts, and duplicate cards.

Synthesize from source, then validate each card against a checklist before it enters the deck.

## When to use

- Turning a textbook chapter or lecture notes into a deck.
- Building a certification study set.
- Creating vocabulary cards from a reading list.
- Converting a document into retrieval practice.
- Auditing an existing deck for quality.

## Workflow

### 1. Ingest and segment the source

Break the source into concepts, definitions, causal claims, processes, contrasts, and examples. Keep the source location for every segment.

Do not generate cards from the table of contents or headings alone. A heading is not a fact.

### 2. Choose the card type

| Type | Use for | Example |
| --- | --- | --- |
| Basic Q/A | Definitions, facts | "What is the unit of force?" -> "Newton" |
| Reversed | Symmetric pairs | Term <-> definition |
| Cloze | Contextual recall | "The mitochondria produces {{ATP}}." |
| List | Ordered or grouped items | "Name the three stages of..." |
| Image occlusion | Diagrams | Label a cell diagram |
| Scenario | Application | "A patient presents... what is the first step?" |

Prefer basic Q/A for precision. Use cloze when the surrounding sentence is necessary context.

### 3. Apply the minimum information principle

One card, one retrievable unit:

- Bad: "What are the causes and effects of inflation?" (two questions)
- Good: "What is one cause of demand-pull inflation?"
- Bad: "List the five phases of mitosis." (a list, unless the list itself is the knowledge)
- Good: separate cards for each phase, plus one ordering card if sequence matters.

If the answer has more than three linked items, split it.

### 4. Write the card

```json
{
  "card_id": "FC-001",
  "type": "basic",
  "front": "What does the zero-product property state?",
  "back": "If ab = 0, then a = 0 or b = 0 (or both).",
  "source": {"text": "Algebra ch. 5, p.88", "quote": "If a product is zero, at least one factor is zero."},
  "tags": ["algebra", "quadratics"],
  "difficulty": "easy"
}
```

Rules:

- The front must be answerable without the source.
- No ambiguous pronouns ("it", "this", "the process").
- Include the context needed to disambiguate a term.
- The back should be short and exact.
- Use the same terminology as the course.
- Avoid cueing the answer in the question ("What is the name of the force that...?").
- Do not test trivia that the curriculum does not require.

### 5. Deduplicate

Check for:

- Same fact with different wording.
- Reversed pairs already covered.
- A card whose answer is contained in another card.
- Near-duplicates from multiple source sections.

Keep the clearest version and link the source locations.

### 6. Validate each card

| Check | Question |
| --- | --- |
| Atomic | Does it test one thing? |
| Unambiguous | Is there exactly one correct answer? |
| Self-contained | Does it make sense without the page? |
| Grounded | Is the answer supported by the cited source? |
| Accurate | Is the source itself correct and current? |
| Useful | Is this required knowledge, not trivia? |
| Non-cueing | Does the question give away the answer? |
| Retrieval | Does it require recall, not recognition? |

### 7. Order and tag

- Tag by unit, topic, and source.
- Sequence within a deck from foundational to applied.
- Keep unrelated decks separate for interleaving control.
- Mark cards that depend on a diagram or dataset.

### 8. Pilot

Have a learner review a sample. Look for cards that are confusing, too easy, or too hard. Revise before generating hundreds.

## Gotchas

- Orphan cards ("What does it measure?") are common when chunks lose context.
- Cloze deletion can leave a sentence that is guessable from grammar. Test the card without the answer.
- Reversed cards are not always valid: "1789 -> French Revolution" is weaker than the reverse.
- Lists often become memorized sequences without understanding. Pair with a why or application card.
- Generated cards may encode a source error. Verify important facts.
- Duplicate cards inflate review workload and distort the scheduler.
- A card that tests a specific example may not transfer. Add a concept card.
- Cards that require a diagram fail in text-only review. Use image occlusion or add a description.
- Copyright: quoting a short source passage is different from copying a chapter. Keep excerpts minimal.
- A deck is not a curriculum. Use it for retrieval after instruction, not as the only learning activity.

## Output contract

```json
{
  "deck": "Algebra Unit 5",
  "source": "algebra-ch5.pdf",
  "cards": [
    {
      "card_id": "FC-001",
      "type": "basic",
      "front": "...",
      "back": "...",
      "source": {"page": 88, "quote": "..."},
      "tags": ["quadratics"],
      "validation": {"atomic": true, "grounded": true, "duplicate": false}
    }
  ],
  "counts": {"generated": 40, "accepted": 34, "duplicates": 4, "rejected": 2},
  "rejected": [{"reason": "ambiguous", "front": "..."}]
}
```

## Checklist

- [ ] Source segmented into concepts and facts.
- [ ] Card type chosen per item.
- [ ] One fact per card.
- [ ] Front self-contained and unambiguous.
- [ ] Answer grounded in the cited source.
- [ ] Duplicates removed.
- [ ] Validation checklist applied.
- [ ] Tags and order set.
- [ ] Pilot review completed.

## Related skills

- `adaptive-spaced-repetition-scheduling` for scheduling the deck.
- `curriculum-grounded-quiz-generation` for assessment items.
- `source-grounded-citation-verification` for checking source claims.
