---
name: user-research-synthesis
description: Codes interviews and surveys into themes, segments, and prioritized insights with supporting quotes. Use for discovery synthesis and roadmap input.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: product-design
---

# User Research Synthesis

## Overview

Synthesis turns raw sessions into decisions. The discipline is to keep observation separate from interpretation, code evidence against the research questions, and preserve a traceable path from every insight back to specific participants and quotes.

A polished affinity wall is not the deliverable. The deliverable is a ranked set of insights with confidence, segment coverage, and a named decision owner. If a finding cannot change a decision, it belongs in an appendix.

## When to use

- Synthesizing 5 or more discovery interviews into themes.
- Coding open-ended survey responses alongside interviews.
- Comparing needs across segments, roles, or tenure bands.
- Preparing roadmap input or a product strategy review.
- Re-synthesizing earlier research after a market or product change.
- Building a reusable evidence repository for future teams.

Do not use for a single interview, or as a substitute for statistical analysis of a representative survey.

## Workflow

### 1. Build an evidence inventory

Create a manifest before reading for themes. Normalize file names to `S07_2026-03-14_interview.txt` and record consent and redaction status.

```json
{
  "study_id": "SYN-2026-03",
  "sources": [
    {"id": "S07", "method": "interview", "segment": "self-serve admin", "date": "2026-03-14", "duration_min": 45, "consent": "record+quote", "pii_redacted": true}
  ]
}
```

Exclude sources without quote consent from the quote bank, but you may still use them for aggregate coding if consent allows.

### 2. Fix the research questions and unit of analysis

Write 3 to 5 questions before coding. State whether the unit is a participant, a session, an incident, or a survey response. A code applied to a participant counts once per participant, not once per mention.

### 3. Write and version a codebook

```json
{
  "version": "1.2",
  "codes": [
    {"code": "workaround.spreadsheet", "definition": "Participant uses a spreadsheet to bridge two tools", "include": "manual export, copy-paste reconciliation", "exclude": "native integration requests", "example": "S07:12:04"}
  ]
}
```

Code inductively first, then consolidate. Keep a decision log for merges and renames so earlier coded sessions can be migrated.

### 4. Measure coding reliability

Two coders independently code a 20% sample, stratified by segment. Compute Cohen's kappa per code family:

```python
def kappa(a, b):
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(k) / n) * (b.count(k) / n) for k in set(a) | set(b))
    return (po - pe) / (1 - pe)
```

Use 0.70 as the floor for exploratory work and 0.80 for decisions with material spend. Below the floor, rewrite definitions and recode; do not average disagreements away.

### 5. Cluster codes into themes

A theme is a claim about user behavior or need, not a topic label. "Users do not trust auto-save" is a theme; "saving" is a topic.

Admission rule: at least 3 independent participants across at least 2 sources or segments, or an explicit `single_source: true` label. Record negative cases and participants who contradict the theme.

### 6. Analyze by segment

Build a matrix of theme by segment with participant counts and denominators. Never report a raw mention count as prevalence. For surveys, report n, question wording, and a confidence interval; for qualitative work, report `3 of 8 self-serve admins` rather than `38%`.

### 7. Prioritize insights

Score each insight 1 to 5 on impact, confidence, and actionability. Confidence follows evidence strength: observed behavior and logs rank above stated preference, which ranks above hypothetical intent.

| Insight | Impact | Confidence | Actionability | Priority |
| --- | --- | --- | --- | --- |
| Auto-save distrust blocks draft completion | 5 | 4 | 4 | P1 |
| Reporting export naming is confusing | 3 | 4 | 5 | P2 |

### 8. Publish with an owner and an expiry

Store the synthesis next to the evidence, include the codebook version, and set a review date. Assign each recommendation an owner and the decision it informs.

## Validation

- Traceability: every theme links to at least 2 quote IDs, or carries a documented single-source flag.
- Coverage: every included source has a coding row; saturation is evidenced by the last 3 sessions adding no new codes.
- Reliability: kappa meets the stated floor, or an adjudication log explains each merged disagreement.
- Segment integrity: no theme averages two segments with contradictory direction without saying so.
- Privacy: run an email and phone scan over the output before publishing.

```bash
rg -n --pcre2 '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' synthesis/ || echo "no emails"
rg -n --pcre2 '\+?[0-9][0-9 ()-]{8,}[0-9]' synthesis/ || echo "no phone-like strings"
```

- Decision fit: each P1 insight names the decision, owner, and next step.
- Limits: sample skew, recruiting source, and non-response are stated in the report.

## Gotchas

- Leading interview questions produce agreement, not evidence. Ask for the last concrete episode.
- Mention counts in qualitative samples are not prevalence. Report participant fractions with denominators.
- The most vocal participant can dominate the affinity wall. Cap each participant's contribution per cluster.
- Themes named after solutions ("needs a dashboard") hide the underlying job. Name the need.
- Pooling segments can cancel real differences. Always inspect the segment matrix before ranking.
- Recency bias favors the last interview. Code from the inventory, not from memory.
- Quotes without the task and prompt context mislead readers. Store the question and the preceding turn.
- Saturation claimed without a new-code log is an assertion. Track codes per session.
- Open-ended survey responses overrepresent strong opinions. Pair them with closed items.
- Codebook changes mid-study create drift. Version the codebook and migrate coded rows.
- PII leaks through verbatim quotes. Redact names, companies, emails, and account IDs.
- A synthesis with no decision owner becomes a deck. Attach recommendations to a decision log.

## Output contract

```json
{
  "study_id": "SYN-2026-03",
  "codebook_version": "1.2",
  "questions": ["..."],
  "sample": {"participants": 12, "segments": {"self-serve admin": 6, "ops lead": 6}, "methods": ["interview", "survey"]},
  "themes": [
    {
      "id": "T1",
      "statement": "Admins do not trust auto-save and re-save manually before closing",
      "participants": 7,
      "segments": ["self-serve admin", "ops lead"],
      "evidence": ["S07:12:04", "S11:03:41"],
      "confidence": "high",
      "single_source": false
    }
  ],
  "insights": [
    {"rank": 1, "theme_id": "T1", "impact": 5, "confidence": 4, "actionability": 4, "recommendation": "...", "owner": "..."}
  ],
  "dissent": ["S09 reported the opposite behavior after a data loss incident"],
  "limitations": ["Recruited from active customers only"],
  "review_date": "2026-09-30"
}
```

## Checklist

- [ ] Source manifest complete with consent and redaction status.
- [ ] Research questions and unit of analysis fixed before coding.
- [ ] Codebook versioned with definitions and examples.
- [ ] Reliability sample coded twice and kappa reported.
- [ ] Themes meet the evidence admission rule.
- [ ] Segment matrix reviewed for contradictory direction.
- [ ] Insights scored and ranked with confidence rationale.
- [ ] Negative cases and dissent documented.
- [ ] PII scan clean.
- [ ] Recommendations have owners and decision links.
- [ ] Review date set.

## Related skills

- `usability-test-analysis` for behavioral evidence from task-based sessions.
- `jobs-to-be-done-analysis` to convert themes into job statements and forces.
- `student-feedback-synthesis` for a parallel coding workflow on cohort feedback.
- `product-requirements-document` to carry validated insights into scoped requirements.
