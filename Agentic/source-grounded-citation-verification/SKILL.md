---
name: source-grounded-citation-verification
description: Verifies claims against cited sources by locating exact supporting spans, classifying stance, and flagging unsupported, contradicted, or unverifiable statements. Use for research reports, RAG answers, literature reviews, fact-checking, and any deliverable that must cite evidence.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: agentic
---

# Source-Grounded Citation Verification

## Overview

A citation is a claim that a source supports a statement. Verification means finding the exact span, checking that it exists, and judging whether it entails the claim. A link that returns 200 is not evidence.

Every sentence that asserts a fact needs a source. Every source needs a locator precise enough to re-find the span.

## When to use

- Reviewing a research report or literature review.
- Validating a RAG answer before it reaches a user.
- Fact-checking an article or brief.
- Auditing citations in a policy or legal memo.
- Building a citation-required generation pipeline.

## Evidence rules

1. Prefer primary sources: the filing, the paper, the statute, the dataset.
2. Pin the version and date. A source can change after citation.
3. Quote the exact span. A paraphrase needs a span too.
4. Record page, section, paragraph, or timestamp.
5. Distinguish support, contradiction, and irrelevance.
6. Do not cite a source you have not opened.
7. Do not use a source's abstract to support a claim that only the full text establishes.
8. Avoid circular citation: two sources citing each other are one source.

## Workflow

### 1. Segment the document into claims

Split at sentence or clause level. Classify:

| Claim type | Needs citation |
| --- | --- |
| Factual assertion | Yes |
| Quantitative result | Yes, plus method |
| Quote or paraphrase | Yes |
| Opinion or recommendation | Label as such |
| Common knowledge | Usually no, but define the boundary |
| Prediction | Yes, for the basis |

Keep the claim ID and the exact text.

### 2. Resolve each citation

For each citation:

- Follow the link or identifier.
- Confirm the title, author, date, and version.
- Save a snapshot or hash.
- Locate the cited page or section.

If the source is paywalled or unavailable, mark `source_unavailable`; do not mark it supported.

### 3. Locate the supporting span

Search the source for the claim's key terms and numbers. Extract the smallest span that contains the evidence.

```python
import re
import unicodedata

def normalize(text):
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\s+", " ", text)
    return text.casefold().strip()

def find_span(source, quote):
    src, q = normalize(source), normalize(quote)
    if q not in src:
        return None
    # Return the normalized span. To map back to original offsets, carry an
    # index map through normalization; never slice the original with offsets
    # computed on normalized text.
    return q
```

For PDFs, extract with page numbers and preserve them. For transcripts, use timestamps. For web pages, use a text snapshot and the retrieval date.

### 4. Classify stance

| Verdict | Definition |
| --- | --- |
| Supported | The span entails the claim as written |
| Partially supported | The span supports part of the claim or a weaker version |
| Contradicted | The span asserts the opposite |
| Unsupported | The source does not address the claim |
| Source unavailable | The source cannot be retrieved or verified |
| Quote mismatch | The quoted text does not appear verbatim |

Use an NLI model as a signal, not the final word. Negation, quantifiers, and numeric modifiers are where automated entailment fails.

### 5. Check the details

- Numbers: units, scale, period, and population.
- Dates: publication versus data period.
- Scope: sample, geography, and conditions.
- Causality: correlation is not causation.
- Certainty: "may" is not "will."
- Attribution: the source's author is not necessarily the originator.

### 6. Produce the verification report

For each claim:

```json
{
  "claim_id": "C-014",
  "claim": "Revenue grew 18% in fiscal 2025.",
  "citation": "10-K FY2025, Item 7",
  "source_url": "https://...",
  "source_version": "filed 2025-10-31",
  "span": "Net sales increased 18% ...",
  "locator": {"page": 42, "section": "MD&A"},
  "verdict": "supported",
  "confidence": 0.96,
  "notes": "Percentage is as reported; growth is year over year."
}
```

### 7. Fix or remove

- Unsupported claims: remove, soften, or find a source.
- Contradicted claims: correct the claim or replace the source.
- Quote mismatches: correct the quote or remove the quotation marks.
- Source unavailable: mark it and do not present it as verified.

Never silently rewrite a claim to match a source without flagging the change.

## Gotchas

- A URL that loads is not a source that supports the claim.
- Web pages change. Snapshot the text and record the retrieval time.
- Abstracts often overstate or omit limitations. Read the relevant section.
- A source can support a weaker claim than the one written. Check quantifiers.
- Negation and double negation break naive similarity checks.
- Numeric claims need unit and scale checks; 18% and 18 percentage points differ.
- A citation to a review article is not a citation to the primary study.
- Circular reporting: multiple outlets citing the same press release are one source.
- Quotes can be edited with ellipses to change meaning. Check the full context.
- Model-generated citations can be plausible but nonexistent. Resolve every identifier.

## Output contract

```markdown
# Citation Verification: <document>

## Summary
- Claims checked: 42
- Supported: 30
- Partially supported: 5
- Unsupported: 4
- Contradicted: 1
- Source unavailable: 2

## Findings
| Claim | Citation | Verdict | Evidence | Action |
| --- | --- | --- | --- | --- |

## Unverifiable sources
<list with reason>

## Recommended edits
<specific claim-level changes>
```

## Checklist

- [ ] Document segmented into claims.
- [ ] Every factual claim mapped to a citation.
- [ ] Sources resolved and versioned.
- [ ] Exact spans located with locators.
- [ ] Stance classified, including partial and contradicted.
- [ ] Numbers, dates, and scope checked.
- [ ] Unsupported claims removed or fixed.
- [ ] Snapshot or hash retained for reproducibility.

## Related skills

- `schema-enforced-json-extraction` for structuring the verification report.
- `confidence-threshold-output-gating` for routing uncertain claims.
- `thematic-regulatory-compliance-diffing` for regulatory citations.
