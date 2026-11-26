---
name: long-form-content-outlining
description: Plans research-backed outlines with audience, angle, section goals, and evidence needs. Use for articles, reports, and thought leadership.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: creative-content
---

# Long-Form Content Outlining

## Overview

Long-form drafts fail in the outline more often than in the prose. When sections have no job, word counts drift, research arrives after the writer has committed to an argument, and the piece becomes a tour of everything the author knows. An outline is a plan with claims: each section states one point, the evidence it needs, and the reason the reader continues.

The deliverable is an outline a writer who missed the planning call can execute: audience and angle locked, thesis reduced to one sentence, word budgets that sum correctly, evidence requests with owners, and one call to action.

## When to use

- Planning a 1,500 to 5,000 word article, report, whitepaper, or pillar page.
- Converting a content brief, keyword theme, or interview transcript into a structure.
- Reviewing an outline before a writer or subject expert spends drafting time.
- Coordinating research, illustration, and writing across contributors.
- Repurposing an existing asset into a series or derivative formats.
- Do not use for social posts, ad copy under 150 words, or unargued listicles; use a short-form copy brief instead.

## Workflow

### 1. Lock the brief

| Field | Question it answers | Example (illustrative) |
| --- | --- | --- |
| Audience | Who acts on this, and what do they already know? | Platform engineers running Kubernetes without a service mesh |
| Job | What decision or action does the piece change? | Choose sidecar or ambient mesh for 40 services |
| Angle | What is the non-obvious claim? | Operational cost, not latency, decides the migration |
| Format | What does the reader receive? | 2,400 word technical article with two comparison tables |
| Constraints | What is fixed? | No vendor pitch, one interview, publish before the conference |
| Success signal | How will we know it worked? | 60 percent scroll depth and 15 demo requests in 30 days |

Write the audience as a role plus context. "Busy executives" is not testable; "VP Engineering approving a platform budget" is.

### 2. State the thesis and the promise

```text
For <audience>, <subject> is <claim> because <reason 1> and <reason 2>, which means <implication>.
```

Thesis tests:

- One sentence, 35 words or fewer.
- Falsifiable: a knowledgeable reader could disagree.
- Backed by at least three evidence items you can name now.
- Not a topic ("AI in healthcare") and not a table of contents ("five trends to watch").

If the thesis needs a paragraph, the piece is probably two pieces.

### 3. Choose a structure pattern

| Pattern | Use when | Section shape |
| --- | --- | --- |
| Direct answer | The query has one defensible answer | Answer, why, exceptions, next step |
| Problem to solution | Reader knows the pain, not the fix | Symptom, causes, options, recommendation |
| Comparison | Two or more viable choices exist | Criteria, option A, option B, decision table, verdict |
| Chronological | Process, history, or case narrative | Setup, turning point, outcome, lesson |
| Taxonomy | The field is confusing and needs categories | Map, category 1..n, how to choose |
| Myth to evidence | Conventional wisdom is wrong | Myth, origin, evidence, revised practice |

Pick one primary pattern. Mixing three produces an outline that restarts every 600 words.

### 4. Build the evidence plan

```yaml
evidence:
  - id: E1
    claim: "Ambient mode removes per-pod proxy containers"
    source_type: primary          # primary | secondary | tertiary
    source: "Vendor architecture docs, v1.22, section 3"
    date: "2026-03-14"
    confidence: high
    owner: researcher
  - {id: E2, claim: "Median CPU overhead fell 18 percent in our benchmark", source_type: primary, source: "Internal benchmark, 12 nodes, 2026-05", date: "2026-05-02", confidence: medium, owner: platform-team}
```

Source tiers: primary (documentation, filings, original data, interviews), secondary (reputable reporting that cites sources), tertiary (blogs and vendor pages). Thought leadership needs at least two primary sources per major claim. Mark internal data as internal and confirm it may be published.

### 5. Draft the section map with budgets

```yaml
outline:
  working_title: "Sidecar or Ambient: What Actually Changes at 40 Services"
  thesis: "For platform teams above 30 services, ambient mesh lowers operational cost because it removes per-pod proxies and centralizes policy, which means migration should be scheduled before the next cluster upgrade."
  target_words: 2400
  sections:
    - id: S1
      goal: "Make the reader recognize the proxy tax"
      claim: "Per-pod proxies multiply upgrade and debugging work"
      evidence_ids: [E1, E2]
      words: 320
      reader_action: "Estimate their own proxy count"
    - {id: S2, goal: "Explain what ambient changes", claim: "Policy moves to a node-level data plane", evidence_ids: [E1], words: 560, reader_action: "Identify which workloads qualify"}
  cta: {action: "Run the readiness checklist", url: "/guides/mesh-readiness"}
```

Budget rules: total within 10 percent of target, no body section under 8 percent of the total, introduction at most 12 percent, conclusion at most 10 percent.

### 6. Add transitions, proof, and a counterargument

For each section, write one handoff sentence: "That explains the cost; the next question is whether ambient mode is ready for stateful workloads." Add a visual request where a table or diagram replaces 150 or more words. Persuasive pieces need one section that states the strongest opposing case and answers it.

### 7. Define the CTA and derivative plan

One primary CTA, matched to funnel stage, with one URL. Then list three to five derivatives (newsletter summary, conference talk, comparison page) mapped to the sections they reuse and an owner. Derivatives that require new research belong in a separate brief.

## Validation

| Gate | Check | Pass criterion | On failure |
| --- | --- | --- | --- |
| Thesis | Word count, falsifiability, support | One sentence, 35 words or fewer, 3 named evidence items | Return to step 2 |
| Budget | Sum of section words | Within 10 percent of target, no section under 8 percent | Rebalance in step 5 |
| Coverage | Every section has evidence | 100 percent of sections carry an evidence ID | Add research or cut the claim |
| Orphans | Every evidence ID is referenced | Zero unused IDs | Delete unused research or add its section |
| Heading path | Read headings alone | They form a coherent argument in order | Rewrite goals, not just titles |
| Counterargument | Present for persuasive angles | One opposing case with an answer | Add before approval |

```python
import yaml

data = yaml.safe_load(open("outline.yaml"))
sections = data["outline"]["sections"]
total = sum(s["words"] for s in sections)
target = data["outline"]["target_words"]
assert abs(total - target) / target <= 0.10, (total, target)
assert min(s["words"] for s in sections) >= 0.08 * total, "section too thin"
assert all(s.get("evidence_ids") for s in sections), "section without evidence"
print("OK", total, "words across", len(sections), "sections")
```

## Gotchas

- An outline that is only a list of headings is a table of contents. Add a claim and a reader action to every section.
- Research deferred to drafting produces claims the sources cannot support. Name evidence IDs before approving the outline.
- Word budgets derived from habit ("intro is 200 words") ignore target length. Derive budgets from total and section job.
- Too many sections at 200 words each reads as a slide deck. Consolidate to 5 to 9 body sections for a 2,000 word piece.
- A thesis no one could dispute is marketing. If the opposite claim is not defensible, sharpen the angle.
- Quotes without provenance (speaker, role, date, context) cannot be fact-checked. Log them as evidence with the transcript.
- Search-volume targets can flatten the argument into keyword sections. Let intent set topics; let the thesis set order.
- Derivative plans often assume the pillar asset exists. Map derivatives to finished sections, not planned ones.
- Internal benchmarks drift as infrastructure changes. Attach a date and configuration to every internal number.
- A CTA chosen at the end can contradict the opening promise. Decide the action before the outline is approved.

## Output contract

```json
{
  "brief": {
    "audience": "role plus context",
    "job": "decision or action the piece changes",
    "angle": "one sentence",
    "format": "article | report | whitepaper",
    "target_words": 2400,
    "constraints": ["..."],
    "success_signal": "measurable outcome"
  },
  "thesis": "one falsifiable sentence",
  "pattern": "comparison",
  "sections": [
    {"id": "S1", "title": "heading text", "goal": "reader change", "claim": "one sentence", "evidence_ids": ["E1"], "words": 320, "visual": "table | diagram | none", "handoff": "transition sentence"}
  ],
  "evidence": [
    {"id": "E1", "claim": "...", "source_type": "primary", "source": "...", "date": "YYYY-MM-DD", "confidence": "high", "owner": "..."}
  ],
  "counterargument": {"claim": "...", "response": "..."},
  "cta": {"action": "...", "url": "...", "funnel_stage": "..."},
  "derivatives": [{"format": "...", "source_sections": ["S1"], "owner": "..."}],
  "budget_check": {"total_words": 2400, "target_words": 2400, "variance_pct": 0.0}
}
```

## Checklist

- [ ] Audience written as role plus context.
- [ ] Job, format, constraints, and success signal recorded.
- [ ] Thesis is one falsifiable sentence of 35 words or fewer.
- [ ] Structure pattern chosen and justified in one line.
- [ ] Evidence plan has IDs, sources, tiers, dates, and owners.
- [ ] Every section has a goal, claim, evidence IDs, and word budget.
- [ ] Word budgets sum within 10 percent of target.
- [ ] Counterargument included for persuasive angles.
- [ ] One CTA with one URL and a funnel stage.
- [ ] Validation gates pass before a writer starts drafting.

## Related skills

- `seo-content-briefing` for query intent, entities, and internal link targets that feed the brief.
- `brand-voice-consistency` for tone, terminology, and channel rules applied during drafting.
- `source-grounded-citation-verification` for checking that evidence IDs survive into published claims.
