---
name: brand-voice-consistency
description: Defines voice attributes and audits copy for consistent tone, terminology, and channel fit. Use for brand guidelines and content QA.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: creative-content
---

# Brand Voice Consistency

## Overview

Brand voice is a set of repeatable decisions, not a mood board. Teams drift because guidelines describe personality with adjectives ("bold, human, trusted") that two writers interpret in opposite ways. A usable system defines each attribute as a choice between two observable behaviors, shows do and avoid examples, and fixes terminology that must not vary.

This skill produces a voice and terminology guide compact enough to use while writing, plus an audit scorecard that measures existing copy against it with evidence and minimal rewrites.

## When to use

- Writing or refreshing brand voice and tone guidelines.
- Auditing a site, help center, onboarding flow, or campaign for consistency.
- Onboarding writers, agencies, or localized teams to a shared standard.
- Resolving terminology drift across product, support, and marketing.
- Preparing copy QA gates before a launch or rebrand.
- Do not use for legal review, factual claims checking, or translation; those need separate reviewers.

## Workflow

### 1. Inventory the corpus and channels

Collect 8 to 15 samples per channel, spanning high-stakes and routine copy. Record source, date, owner, and audience.

| Channel | Samples | Reader state | Constraint |
| --- | --- | --- | --- |
| Marketing site | 12 pages | Evaluating, low patience | SEO and legal claims |
| Onboarding email | 6 messages | Task-focused, time-pressed | Length, deliverability |
| Help center | 15 articles | Frustrated, mid-task | Accuracy first |
| Error messages | 10 strings | Blocked, anxious | Under 90 characters |
| Social | 20 posts | Casual, scrolling | Platform norms |

If the corpus is thin or conflicting, say so. Do not invent a voice from three blog posts.

### 2. Extract attributes as contrast pairs

An attribute is a behavior, not an adjective. Write each as "we are X, not Y" and support it with evidence.

| Attribute | We are | We are not | Observable rule |
| --- | --- | --- | --- |
| Direct | Lead with the answer | Blunt or dismissive | First sentence states the outcome |
| Warm | Acknowledge the situation | Sentimental or chummy | Use "you" and one empathy clause, not three |
| Expert | Specific and sourced | Jargon-heavy or boastful | Every claim has a number or source |
| Playful | Occasional wit in low-stakes moments | Joking about failure or money | No humor in errors, billing, or security |

Cap the system at three to five attributes. Each needs one positive example, one negative example, and a rule a reviewer can check.

### 3. Codify terminology and mechanics

```yaml
terminology:
  preferred:
    - term: "workspace"
      not: ["account", "tenant", "org"]
      note: "Use for the top-level container in product copy."
    - term: "sign in"
      not: ["log in", "login"]
      note: "Verb form; noun is 'sign-in'."
  product_names: ["Acme Cloud"]        # always two words, never ACME Cloud
  banned:
    - {term: "seamless", reason: "Unmeasurable; replace with the specific property."}
    - {term: "revolutionary", reason: "Unsupported claim; legal and credibility risk."}
mechanics:
  capitalization: "Sentence case for headings and buttons."
  numbers: "Numerals for 10 and above, spelled out below 10, except in tables."
  dates: "ISO 8601 in product, long form in marketing."
  oxford_comma: true
```

Terminology decisions need owners and dates. Undated rules decay into suggestions.

### 4. Build the channel adaptation matrix

Voice stays constant; tone and format adapt.

| Channel | Formality (1-5) | Length | Humor | CTA style |
| --- | --- | --- | --- | --- |
| Marketing site | 3 | 600-1,200 words | Light | Outcome-led |
| Onboarding email | 3 | 80-140 words | None | One next step |
| Help center | 3 | Task-complete | None | Imperative |
| Error message | 2 | Under 90 characters | None | Recovery action |
| Social | 2 | Platform-native | Occasional | Conversational |

Justify each departure from the baseline. "LinkedIn is more formal" is not a reason; "buyers read it at work and forward it to procurement" is.

### 5. Score the corpus

Score 1 to 5 per attribute with a weighted rubric. Sample at least 20 passages, stratified by channel.

| Score | Meaning | Evidence required |
| --- | --- | --- |
| 5 | Model example | Quote that could go in the guide |
| 4 | Consistent | Minor edit at most |
| 3 | Mixed | One clear violation in the passage |
| 2 | Off-voice | Two or more violations or wrong register |
| 1 | Contradicts the guide | Rewrite required |

Track two results separately: average attribute score and count of severity-1 terminology violations. Averages hide a banned term in a checkout flow.

### 6. Rewrite flagged passages with minimal diffs

Preserve facts, legal language, and product names. Change the smallest span that fixes the violation, then re-score. Route any claim change to the claim owner.

```text
Before: "Our seamless, revolutionary platform empowers teams to unlock synergy."
After:  "Our platform connects your CRM to support in one workspace, so agents see account history without switching tabs."
```

The rewrite adds a specific mechanism. Voice work that only swaps adjectives has not improved the copy.

### 7. Operationalize and govern

- Publish the guide where writers work, not only in a brand portal.
- Add lint rules for banned terms and preferred spellings in CI or the editor.
- Require one voice review on launch copy and quarterly sampling afterward.
- Version the guide with a changelog and announce changes with a before and after.
- Log exceptions with an owner and an expiry date.

## Validation

| Gate | Method | Pass criterion | Fail action |
| --- | --- | --- | --- |
| Attribute testability | Second writer applies each rule to 3 samples | Same pass/fail on at least 2 of 3 | Rewrite the attribute |
| Terminology | Case-insensitive search for banned terms | Zero severity-1 hits in the sample | Fix copy or update the guide |
| Score | Rubric applied to 20 or more passages | Mean 4.0 or higher per attribute; no channel below 3.5 | Targeted rewrite |
| Channel fit | Reviewer checks matrix row | Length, formality, CTA within range | Adjust for channel |
| Facts preserved | Diff before and after | No claim, number, or legal term changed | Revert and escalate |
| Rater agreement | Two reviewers score 10 shared passages | Within 1 point on 80 percent | Calibrate with examples |

```bash
# Illustrative lint pass; adjust the pattern to the approved term list.
rg -n -i -w 'seamless|revolutionary|synergy|leverage' content/ || true
rg -n -i 'log ?in' content/ || true
```

## Gotchas

- Adjective lists ("bold, human, trusted") are not rules. Convert each to a behavior with a test.
- Voice and tone are conflated. Voice is stable; tone moves with reader state and stakes.
- Only positive examples are collected. Writers learn faster from a clear "we are not this" sample.
- Banned words are enforced while synonyms multiply. Ban the vague behavior, not just the token.
- Humor is allowed everywhere. Keep it out of errors, billing, security, and grief-adjacent contexts.
- Localization breaks literal idioms. Give translators the intent and do/avoid examples, not just English.
- Legal copy gets rewritten for rhythm. Route changes to the claim owner; voice never overrides accuracy.
- Scorecards reward the rater's taste. Calibrate on shared passages and publish anchor examples per score.
- A guide with 40 rules is ignored. Keep the must-follow list under 15 and move the rest to examples.
- Exceptions accumulate without expiry. Every exception needs an owner and a review date.
- Accessibility conflicts are missed. Plain-language and reading-level rules outrank stylistic preference.

## Output contract

```json
{
  "scope": {"channels": ["marketing", "help-center"], "samples": 42, "period": "2026-Q2"},
  "attributes": [
    {"name": "direct", "we_are": "...", "we_are_not": "...", "rule": "...", "example_good": "...", "example_bad": "..."}
  ],
  "terminology": {"preferred": [{"term": "...", "not": ["..."], "owner": "..."}], "banned": [{"term": "...", "reason": "..."}]},
  "channel_matrix": [{"channel": "email", "formality": 3, "length": "80-140 words", "humor": "none", "cta": "one next step"}],
  "audit": {
    "passages": 42,
    "attribute_scores": {"direct": 4.2, "warm": 3.9},
    "terminology_violations": {"severity_1": 2, "severity_2": 7},
    "findings": [{"location": "pricing page H1", "issue": "...", "evidence": "...", "fix": "...", "severity": 1}]
  },
  "rewrites": [{"location": "...", "before": "...", "after": "...", "facts_changed": false}],
  "governance": {"owner": "...", "review_cadence": "quarterly", "lint_rules": ["..."]}
}
```

## Checklist

- [ ] Corpus sampled across channels, with dates and owners.
- [ ] Three to five attributes written as contrast pairs.
- [ ] Every attribute has a good example, a bad example, and a checkable rule.
- [ ] Preferred and banned terminology lists have owners.
- [ ] Channel matrix sets formality, length, humor, emoji, and CTA style.
- [ ] At least 20 passages scored on the rubric.
- [ ] Terminology violations counted by severity.
- [ ] Rewrites preserve facts, numbers, and legal language.
- [ ] Two reviewers calibrated on shared passages.
- [ ] Guide versioned with an owner and review cadence.

## Related skills

- `long-form-content-outlining` for planning structure before voice rules are applied to a draft.
- `technical-documentation-writing` for task accuracy and verification in help center content.
- `seo-content-briefing` for aligning titles and meta copy with search intent without breaking voice.
