---
name: earnings-call-sentiment-extraction
description: Extracts guidance changes, management tone, uncertainty, hedging, and Q&A dynamics from earnings call transcripts, with speaker-aware scoring and verbatim evidence. Use for equity research, event-driven monitoring, competitive intelligence, and tracking management credibility across quarters.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: finance
---

# Earnings Call Sentiment Extraction

## Overview

Earnings call sentiment is not a single positive/negative score. Management's prepared remarks are scripted and optimistic by design. The signal is in changes versus prior quarters, guidance language, uncertainty and hedging, the Q&A, and whether executives answer the question asked.

This skill separates speakers and sections, scores with a finance-aware method, and forces every conclusion to cite a verbatim span.

## When to use

- Preparing for an earnings event or analyzing a transcript.
- Tracking guidance and tone changes quarter over quarter.
- Comparing management commentary across competitors.
- Flagging deterioration before it appears in the numbers.

Do not treat sentiment as a price prediction. Correlation with returns is noisy and not causal.

## Inputs

- Transcript with speaker labels and section markers (prepared remarks, Q&A).
- Company, fiscal quarter, call date, and source.
- Prior-quarter transcript for comparison.
- Optional: consensus estimates and actual results.

## Workflow

### 1. Parse and segment

Separate:

- Operator script.
- CEO and CFO prepared remarks.
- Other executives.
- Analyst questions.
- Management answers.

Preserve turn boundaries and speaker roles. A sentence from an analyst is not management sentiment.

### 2. Extract guidance statements

For each forward-looking statement, capture:

```json
{
  "metric": "revenue",
  "period": "FY2027",
  "direction": "raised",
  "value_low": 0,
  "value_high": 0,
  "qualifier": "excluding FX",
  "evidence": "We now expect revenue of ...",
  "speaker": "CFO",
  "timestamp": "00:14:32"
}
```

Direction labels: raised, lowered, reaffirmed, introduced, withdrawn, not provided. A reaffirmation is not the same as an increase.

### 3. Score language

Use a finance-specific lexicon rather than a general sentiment model. Loughran-McDonald is a reasonable baseline; FinBERT is an alternative when a model is available.

```python
NEGATIVE = {"decline", "weakness", "impairment", "shortfall", "headwind", "delay", "loss", "litigation"}
POSITIVE = {"growth", "expansion", "record", "strong", "improved", "outperform", "momentum"}
UNCERTAINTY = {"approximately", "roughly", "may", "could", "expect", "intend", "subject to", "depending on"}
HEDGING = {"we believe", "we expect", "we anticipate", "we are confident", "assuming"}

import re

def lexicon_score(text):
    tokens = re.findall(r"[a-z']+", text.casefold())
    pos = sum(t in POSITIVE for t in tokens)
    neg = sum(t in NEGATIVE for t in tokens)
    unc = sum(t in UNCERTAINTY for t in tokens)
    hedge = sum(t in HEDGING for t in tokens)
    total = max(pos + neg, 1)
    return {
        "polarity": (pos - neg) / total,
        "uncertainty": unc / max(len(tokens), 1),
        "hedging": hedge / max(len(tokens), 1),
    }
```

Score prepared remarks and Q&A separately. Management answers in Q&A are less scripted and often more informative.

### 4. Analyze Q&A dynamics

Flag:

- Question dodged or answered with a different metric.
- Answer shorter than the question.
- Repeated deflections across analysts.
- New topic introduced by management.
- Guidance narrowed without a clear reason.
- "We'll get back to you" on a material item.

These are qualitative flags with evidence, not numeric scores.

### 5. Compare with the prior quarter

Compute deltas for:

- Polarity by speaker and section.
- Uncertainty and hedging rates.
- Guidance direction and magnitude.
- Topic mix (demand, pricing, costs, competition, regulation).
- Q&A evasion flags.

A stable score with a large negative guidance revision is still a negative signal.

### 6. Validate

- Every claim cites a speaker, timestamp, and verbatim quote.
- Guidance values match the transcript exactly.
- Negation is handled ("not weakening" is not negative).
- Sarcasm and idioms are not scored literally.
- Transcript errors are flagged, not silently corrected.

## Gotchas

- Prepared remarks are scripted and reviewed by legal. Weight Q&A more for candid signal.
- General-purpose sentiment models misread finance terms. "Liability" and "risk" are not automatically negative.
- Management may sound confident while lowering guidance. Separate tone from facts.
- Analysts' questions reflect their own bias. Do not attribute analyst sentiment to management.
- Transcripts contain ASR errors, especially names and numbers. Cross-check material figures against the release.
- A positive call can follow a stock decline. Sentiment is not a return forecast.
- Quarter-over-quarter comparisons need the same section and speaker mix.
- Silence or a short answer can be more informative than a long one. Preserve the exchange.

## Output contract

```json
{
  "company": "Example Corp",
  "quarter": "FY2026 Q3",
  "call_date": "2026-11-19",
  "guidance": [
    {"metric": "revenue", "period": "FY2027", "direction": "lowered", "evidence": "...", "speaker": "CFO"}
  ],
  "tone": {
    "prepared_polarity": 0.18,
    "qa_polarity": -0.04,
    "uncertainty_delta": 0.03,
    "hedging_delta": 0.02
  },
  "qa_flags": [
    {"type": "dodged_question", "topic": "gross margin", "evidence": "..."}
  ],
  "comparison": {"prior_quarter": "FY2026 Q2", "notable_changes": ["..."]},
  "confidence": "medium",
  "citations": ["00:14:32", "00:31:05"]
}
```

## Checklist

- [ ] Transcript source and call metadata recorded.
- [ ] Speakers and sections separated.
- [ ] Guidance extracted with direction and evidence.
- [ ] Finance-aware sentiment and uncertainty scored.
- [ ] Q&A dynamics analyzed.
- [ ] Prior-quarter comparison computed.
- [ ] Every claim cites a timestamp and quote.
- [ ] Numbers cross-checked against the earnings release.

## Related skills

- `source-grounded-citation-verification` for validating quotes.
- `sec-filing-extraction` for the filed results.
- `confidence-threshold-output-gating` before publishing an investment thesis.
