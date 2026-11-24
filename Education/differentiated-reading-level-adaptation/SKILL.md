---
name: differentiated-reading-level-adaptation
description: Adapts texts to a target reading level while preserving meaning, technical accuracy, and tone, using readability analysis, vocabulary support, syntax simplification, and fidelity checks. Use for differentiated instruction, ESL materials, accessibility, plain-language rewriting, and leveled reading sets.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: education
---

# Differentiated Reading-Level Adaptation

## Overview

Leveling a text is not deleting words until a formula is happy. The goal is to preserve the ideas, relationships, and technical content while reducing unnecessary linguistic load. A simplified text that changes the meaning is worse than the original.

Produce a target version, a glossary of retained terms, and evidence that meaning survived.

## When to use

- Creating multiple reading levels of the same content.
- Adapting a textbook passage for English learners.
- Plain-language rewriting for accessibility.
- Preparing differentiated materials for a mixed-ability class.
- Checking whether a text is appropriate for a grade or CEFR level.

## Workflow

### 1. Define the target and purpose

Specify:

- Reader profile: grade, CEFR, Lexile, or reading assessment.
- Purpose: learn the content, practice reading, or complete a task.
- Constraints: must-keep vocabulary, exam board terms, length.
- Format: print, screen reader, large print, audio.

A text for "grade 6 ESL" is not the same as "grade 6 native readers." Name the actual need.

### 2. Analyze the source

```python
import textstat

text = open("chapter.txt").read()
print("Flesch-Kincaid grade:", textstat.flesch_kincaid_grade(text))
print("Flesch reading ease:", textstat.flesch_reading_ease(text))
print("SMOG:", textstat.smog_index(text))
print("Dale-Chall:", textstat.dale_chall_readability_score(text))
```

Readability formulas are proxies. They reward short sentences and common words, and they can be gamed. Use them as one signal, not the goal.

Also inspect:

- Average sentence length and clause depth.
- Passive voice and nominalizations.
- Pronoun reference and cohesion.
- Idioms, metaphors, and cultural references.
- Technical terms and their definitions.
- Visual and formatting demands.

### 3. Identify the meaning anchors

List the facts, concepts, relationships, and claims that must survive. For a science passage:

- The process and its sequence.
- Cause and effect.
- The technical terms the curriculum requires.
- Data and units.
- The distinction between observation and inference.

These anchors become the fidelity checklist.

### 4. Adapt in layers

| Layer | Change | Risk |
| --- | --- | --- |
| Vocabulary | Replace rare words; define essential terms | Losing precision |
| Syntax | Split long sentences; reduce nesting | Losing logical links |
| Cohesion | Add signposts ("because", "however") | Over-signposting |
| Examples | Add a concrete example | Adding length |
| Visuals | Add a diagram or table | Cognitive load |
| Format | Headings, spacing, chunking | Fragmenting the argument |

Keep technical terms when they are the learning target. Support them with a definition and an example rather than replacing them with a vague synonym.

### 5. Write the adapted version

Rules:

- One main idea per sentence where possible.
- Prefer active voice unless the actor is unknown or irrelevant.
- Keep the logical connectives explicit.
- Define a term on first use.
- Use consistent terminology; do not rotate synonyms for the same concept.
- Preserve numbers, units, and qualifiers.
- Avoid childish tone. Simpler is not sillier.

### 6. Check fidelity

- Does every meaning anchor appear?
- Are any claims stronger or weaker than the original?
- Are cause and effect preserved?
- Are exceptions and conditions preserved?
- Did a definition change the concept?
- Would a subject expert accept the simplified claim?

A useful check: have a second model or reviewer summarize both versions and compare the claims.

### 7. Re-measure and trial

Recompute readability. Check that the target metric moved in the right direction and that the text did not become choppy.

If possible, ask a reader at the target level to retell the passage. Comprehension is the real test.

### 8. Package supports

- Glossary with first-language translations where appropriate.
- Audio version with correct pronunciation.
- Visual organizer.
- Pre-reading vocabulary activity.
- Comprehension questions at the target level.

## Gotchas

- Readability formulas need enough text to be stable. A 100-word excerpt gives noisy scores.
- Short sentences can be harder to integrate. Cohesion matters more than length alone.
- Deleting examples or qualifications changes the claim.
- Replacing technical vocabulary with everyday words can teach the wrong concept.
- Nominalizations ("the implementation of the policy") hide the actor. Unpack them.
- Idioms and sports metaphors travel poorly across cultures.
- A text can be lexically simple and conceptually complex. Level both dimensions.
- Over-simplification can be patronizing. Keep the register respectful.
- ESL needs and reading-disability needs overlap but are not identical. Do not assume one accommodation fits all.
- Images and diagrams need alt text and must not carry essential information alone.

## Output contract

```json
{
  "source": "biology-ch6.txt",
  "target": {"grade": 6, "purpose": "content learning", "cefr": "B1"},
  "versions": [
    {
      "level": "grade 6",
      "text": "...",
      "readability": {"flesch_kincaid": 6.2, "smog": 6.8, "dale_chall": 6.1},
      "meaning_anchors_preserved": true
    }
  ],
  "glossary": [{"term": "photosynthesis", "definition": "...", "translation": "..."}],
  "fidelity_review": {"reviewer": "...", "claims_changed": []},
  "reader_trial": {"retell_score": 0.82, "notes": "..."}
}
```

## Checklist

- [ ] Target reader and purpose defined.
- [ ] Source analyzed for readability and language load.
- [ ] Meaning anchors listed.
- [ ] Adaptation preserves technical terms and relationships.
- [ ] Fidelity review completed.
- [ ] Readability re-measured.
- [ ] Reader trial or comprehension check run.
- [ ] Glossary and supports included.
- [ ] Accessibility considered.

## Related skills

- `accessibility-format-conversion` for output formats and WCAG compliance.
- `socratic-tutoring-scaffolding` for discussing the adapted text.
- `curriculum-grounded-quiz-generation` for comprehension checks.
