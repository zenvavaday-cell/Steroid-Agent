---
name: thematic-regulatory-compliance-diffing
description: Compares regulations, rules, and guidance across versions, jurisdictions, or regulators by obligation theme, then maps each change to policies, controls, owners, and effective dates. Use for compliance change management, regulatory gap analysis, policy updates, and multi-jurisdiction rule comparisons.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: finance
---

# Thematic Regulatory Compliance Diffing

## Overview

A text diff tells you which words changed. A compliance diff tells you which obligations changed, who they apply to, what evidence is required, and when the change takes effect. The unit of analysis is the obligation, not the paragraph.

This skill extracts obligations into a structured form, aligns them by theme, scores materiality, and produces a change memo that a compliance team can act on.

## When to use

- A regulator publishes an amended rule and you need the operational impact.
- The same activity is regulated in several jurisdictions and you need a comparison.
- You are updating policies or controls after a regulatory change.
- You are preparing for an audit or examination and need a traceable mapping.

Do not use for legal advice. The output is an analytical work product for qualified compliance and legal reviewers.

## Obligation schema

Extract every obligation into this shape:

```json
{
  "obligation_id": "OBL-001",
  "source": {
    "jurisdiction": "US",
    "regulator": "SEC",
    "instrument": "Rule 17a-4",
    "citation": "17 CFR 240.17a-4(b)(4)",
    "version": "2026-01-01",
    "effective_date": "2026-06-01",
    "url": "https://..."
  },
  "theme": "record-retention",
  "actor": "broker-dealer",
  "action": "retain",
  "object": "electronic communications",
  "condition": "business-related",
  "threshold": "3 years",
  "deadline": "immediate",
  "modality": "shall",
  "evidence": "audit trail",
  "penalty": "civil penalty",
  "cross_references": ["17 CFR 240.17a-3"],
  "notes": ""
}
```

`modality` matters: "shall" is mandatory, "should" is supervisory expectation, "may" is permissive. Do not treat them as equivalent.

## Workflow

### 1. Pin the sources

Record jurisdiction, regulator, instrument, citation, publication date, effective date, transition period, and URL. Save an immutable copy with a hash. Regulations change; your analysis must be reproducible against a specific version.

### 2. Segment and extract obligations

Split the text by section and subsection. For each unit, extract actor, action, object, condition, threshold, deadline, modality, and evidence. Keep the exact citation for every field.

Use the LLM for extraction, then validate:

- Every obligation cites an existing section.
- Every quoted threshold appears verbatim in the source.
- No obligation is invented from a definition or example.

### 3. Normalize themes

Use a controlled theme list, for example:

- recordkeeping and retention
- reporting and disclosure
- capital and liquidity
- conduct and suitability
- outsourcing and third-party risk
- data privacy and cross-border transfer
- governance and accountability
- anti-money-laundering and sanctions
- consumer protection
- cybersecurity and incident response

Free-text themes fragment the comparison. Map synonyms into the controlled list and keep the original label.

### 4. Align and diff

For each theme, align obligations across the two sources using actor + action + object. Classify:

| Change type | Definition |
| --- | --- |
| Added | Present in the new source, absent in the old |
| Removed | Present in the old source, absent in the new |
| Modified | Same intent, changed threshold, scope, deadline, or evidence |
| Clarified | Same obligation, new guidance or examples |
| Moved | Same obligation, different section or instrument |
| Unchanged | No material difference |

### 5. Score materiality

Score each change on a 1–5 scale across:

- Scope: how many products, entities, or clients are affected.
- Severity: penalty, license risk, or customer harm.
- Effort: systems, data, or process change required.
- Timing: how soon the effective date arrives.
- Uncertainty: ambiguity or pending guidance.

Materiality = weighted sum. Use explicit weights agreed with the compliance owner, not an opaque model score.

### 6. Map to controls

For each change, identify the affected policy, control, system, data source, owner, and evidence. Mark the gap:

| Gap state | Meaning |
| --- | --- |
| Covered | Existing control meets the new obligation |
| Partial | Control exists but scope, frequency, or evidence is insufficient |
| Missing | No control exists |
| Obsolete | Control exists only because of a removed obligation |

### 7. Produce the change memo

Include an executive summary, the change table, control gaps, owners, remediation dates, and a section for legal review. Separate "what the text says" from "what we recommend."

## Validation gates

- Every change cites both the old and new provision.
- Every threshold is quoted verbatim and unit-checked.
- Effective dates are distinguished from publication dates.
- Cross-references are resolved, not assumed.
- Definitions that change scope are flagged even if the operative text is unchanged.
- The memo states its jurisdictional scope and assumptions.

## Gotchas

- An amendment can change a definition that silently changes dozens of obligations. Diff the definitions section too.
- "Effective date" may be later than "compliance date" for specific provisions. Track both.
- Guidance is not a rule, but examiners may treat it as expectations. Label the source type.
- Cross-border equivalence decisions can remove obligations without changing the text.
- Local implementation of a supranational rule may differ by member state. Compare the implementing text, not only the directive.
- Machine translation can invert "shall not." Verify negations in the original language.
- A removed obligation may still exist in another instrument.

## Output contract

```markdown
# Regulatory Change Memo: <instrument>

## Scope
<jurisdictions, entities, products, source versions>

## Executive summary
<3-5 bullets: material changes and required actions>

## Change register
| ID | Theme | Change | Old citation | New citation | Effective | Materiality | Owner |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Control gaps
| Obligation | Current control | Gap state | Remediation | Due |
| --- | --- | --- | --- | --- |

## Open questions for legal
<list>
```

## Checklist

- [ ] Sources pinned with version, date, and hash.
- [ ] Obligations extracted with citations.
- [ ] Themes normalized to a controlled list.
- [ ] Changes classified by type.
- [ ] Materiality scored with agreed weights.
- [ ] Controls and owners mapped.
- [ ] Legal review section included.
- [ ] Memo states scope and assumptions.

## Related skills

- `source-grounded-citation-verification` to verify every quoted provision.
- `cross-system-data-normalization` when merging regulatory data from multiple systems.
- `human-in-the-loop-escalation` before any compliance decision is finalized.
