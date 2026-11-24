---
name: prerequisite-knowledge-mapping
description: Builds a concept dependency graph from a curriculum, diagnoses a learner's mastered and missing prerequisites, and generates an ordered learning path. Use for course design, placement, personalized remediation, and sequencing instruction.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: education
---

# Prerequisite Knowledge Mapping

## Overview

Concepts have dependencies. You cannot solve quadratic equations without manipulating expressions, and you cannot interpret a confidence interval without understanding sampling variability. A prerequisite map makes those dependencies explicit, so instruction and remediation target the right gap.

The map is a directed acyclic graph: nodes are concepts, edges mean "must know before."

## When to use

- Designing a course sequence.
- Diagnosing why a learner is stuck.
- Placing a learner into a curriculum.
- Building a personalized remediation plan.
- Checking that a syllabus does not assume untaught knowledge.

## Workflow

### 1. Define the concept inventory

Extract concepts from:

- Standards and learning objectives.
- Textbook chapter headings and index.
- Assessment blueprints.
- Expert interviews.

Write each concept as a short, observable statement, not a topic label:

- Weak: "fractions."
- Better: "Add fractions with unlike denominators."
- Better: "Explain why a common denominator is needed to add fractions."

Granularity should match the assessment. If you cannot test it separately, it is probably too coarse.

### 2. Add prerequisite edges

For each concept, ask: "What must a learner already be able to do to succeed at this?"

Record the edge with a rationale and strength:

```json
{
  "from": "find-common-denominator",
  "to": "add-unlike-fractions",
  "strength": "hard",
  "rationale": "The procedure requires a common denominator."
}
```

Strength:

| Strength | Meaning |
| --- | --- |
| Hard | Cannot learn the target without it |
| Soft | Helpful but can be learned alongside |
| Diagnostic | A common gap that predicts difficulty |

### 3. Validate the graph

- Check for cycles. A cycle means the concepts are co-requisites or the granularity is wrong.
- Remove false prerequisites. "Nice to know" is not "must know."
- Add hidden prerequisites: vocabulary, notation, tool use, metacognitive strategies.
- Confirm with a subject expert.

```python
import networkx as nx

G = nx.DiGraph()
G.add_edges_from([
    ("whole-number-operations", "factors-multiples"),
    ("factors-multiples", "find-common-denominator"),
    ("find-common-denominator", "add-unlike-fractions"),
])

assert nx.is_directed_acyclic_graph(G)
print(list(nx.topological_sort(G)))
```

### 4. Attach evidence

Each concept needs at least one way to verify mastery:

- A diagnostic item.
- A performance task.
- A prior course grade.
- A worked problem with explanation.

Mastery should be a threshold with uncertainty, not a binary checkbox.

```json
{
  "concept": "find-common-denominator",
  "mastery": 0.72,
  "threshold": 0.80,
  "evidence": ["3 of 4 items correct", "explained the method"],
  "last_checked": "2026-11-20"
}
```

### 5. Diagnose the learner

Assess the target concept and walk backward through hard prerequisites. Stop when you find a confirmed gap. Do not test the entire graph; test the frontier.

A learner who fails a target may have:

- A missing prerequisite.
- A misconception in the prerequisite.
- Adequate prerequisites but weak strategy.
- A language or representation issue.

The map narrows the search; it does not replace diagnosis.

### 6. Compute the learning frontier

The frontier is the set of concepts whose prerequisites are mastered but which are not yet mastered.

```python
def frontier(graph, mastery, threshold=0.8):
    ready = []
    for node in graph.nodes:
        if mastery.get(node, 0) >= threshold:
            continue
        prereqs = graph.predecessors(node)
        if all(mastery.get(p, 0) >= threshold for p in prereqs):
            ready.append(node)
    return sorted(ready)
```

### 7. Build the learning path

Order by:

1. Hard prerequisites first.
2. Frontier concepts next.
3. Soft prerequisites alongside or just in time.
4. Target concepts last.

Keep the path short. A 40-step remediation plan will not be followed. Choose the smallest set of concepts that unlocks the target.

### 8. Re-check and update

After instruction, reassess the frontier. Update mastery with evidence. Remove edges that proved unnecessary and add edges revealed by new errors.

## Gotchas

- Cycles usually mean the concepts were defined too coarsely. Split them.
- A prerequisite can be "knows the vocabulary" rather than a whole topic. Do not overlook language.
- Not every dependency is hard. Over-marking prerequisites creates endless remediation.
- Diagnostic items can be invalid. A wrong answer may reflect the test, not the learner.
- Mastery decays. A score from two years ago is weak evidence.
- Learners can take multiple valid paths. A DAG allows branching; do not force one sequence.
- The map reflects the curriculum's assumptions, not necessarily the learner's cognition.
- Hidden prerequisites in tool use (calculator, spreadsheet, graph software) are real.
- Over-testing damages motivation. Assess the frontier, not the whole graph.

## Output contract

```json
{
  "target": "solve quadratic equations by factoring",
  "concepts": [
    {"id": "factor-trinomials", "label": "...", "mastery": 0.55, "threshold": 0.80},
    {"id": "zero-product-property", "label": "...", "mastery": 0.90, "threshold": 0.80}
  ],
  "edges": [{"from": "factor-trinomials", "to": "solve-by-factoring", "strength": "hard"}],
  "frontier": ["factor-trinomials"],
  "path": [
    {"step": 1, "concept": "factor-trinomials", "activity": "...", "check": "..."},
    {"step": 2, "concept": "solve-by-factoring", "activity": "...", "check": "..."}
  ],
  "estimated_sessions": 3
}
```

## Checklist

- [ ] Concepts defined at assessment granularity.
- [ ] Prerequisite edges have rationale and strength.
- [ ] Graph is acyclic and expert-reviewed.
- [ ] Evidence source exists for each concept.
- [ ] Learner assessed at the frontier.
- [ ] Learning path ordered by hard prerequisites.
- [ ] Path is short and actionable.
- [ ] Mastery updated after instruction.

## Related skills

- `student-misconception-diagnosis` when a prerequisite is wrong, not missing.
- `syllabus-alignment-verification` for course-level sequencing.
- `longitudinal-mastery-tracking` for updating mastery over time.
