---
name: anti-money-laundering-screening
description: Screens customers and counterparties against sanctions, PEP, and watchlist data with normalized names, aliases, identifiers, fuzzy scoring, tiered thresholds, disposition workflow, and audit evidence. Use for onboarding, periodic review, payment screening, and list-change remediation.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: finance
---

# Anti-Money-Laundering Screening

## Overview

Screening compares a person or entity against sanctions, politically exposed person (PEP), and watchlist data. Most alerts are false positives caused by common names, transliteration, or missing identifiers. The skill's value is in disciplined normalization, transparent scoring, and a defensible disposition record.

This is not legal advice. Escalation, blocking, and reporting decisions belong to a qualified compliance officer.

## When to use

- Customer or counterparty onboarding.
- Periodic KYC refresh.
- Payment and trade screening.
- Remediation after a list update.
- Reviewing a backlog of screening alerts.

## Workflow

### 1. Pin the lists

Record list name, publisher, version, download date, and hash. Sanctions lists update frequently; a screening result is only valid against a specific list version.

Common sources: OFAC SDN and consolidated lists, EU consolidated sanctions, UK OFSI, UN Security Council, local regulators, commercial PEP and adverse media databases.

### 2. Normalize identities

Create a canonical record:

```python
import unicodedata
import re

def normalize_name(name):
    name = unicodedata.normalize("NFKD", name)
    name = "".join(c for c in name if not unicodedata.combining(c))
    name = name.casefold()
    name = re.sub(r"\b(mr|mrs|ms|dr|prof|jr|sr|ii|iii|iv)\b", " ", name)
    name = re.sub(r"[^\w\s]", " ", name)
    return " ".join(name.split())
```

Keep the original, the normalized form, and every alias. Do not discard tokens that may be part of a compound name.

Collect identifiers: date of birth, nationality, country of residence, national ID, passport, registration number, address, and ownership structure.

### 3. Generate candidates

- Exact identifier match is a strong signal.
- Exact normalized full-name match is a candidate, not a confirmed match.
- Fuzzy name matching catches spelling and transliteration variants.
- Token-based matching handles reordered names and missing middle names.

```python
from rapidfuzz import fuzz

def name_score(a, b):
    return max(
        fuzz.token_set_ratio(a, b),
        fuzz.token_sort_ratio(a, b),
        fuzz.partial_ratio(a, b) if min(len(a), len(b)) >= 8 else 0,
    ) / 100
```

### 4. Score the composite

```
score = 0.45 * name_similarity
      + 0.20 * dob_match
      + 0.15 * country_match
      + 0.10 * identifier_match
      + 0.10 * entity_type_match
```

Identifier exact match should override the weighted score and go straight to review. A high name score with a conflicting date of birth is usually a false positive, but never auto-clear without review.

### 5. Apply tiered thresholds

| Score | Tier | Action |
| --- | --- | --- |
| ≥ 0.95 + identifier match | Confirmed candidate | Escalate immediately, do not onboard |
| 0.85–0.95 | High | Manual review within SLA |
| 0.70–0.85 | Medium | Review or enhanced due diligence |
| < 0.70 | Low | Auto-clear with audit record |

Thresholds are institution-specific and must be tuned against known true and false matches.

### 6. Disposition

For each alert, record:

- Matched list entry and list version.
- Compared fields and their values.
- Score components.
- Analyst decision: true match, false positive, inconclusive.
- Rationale and supporting documents.
- Reviewer and timestamp.
- Action taken: block, freeze, report, continue, exit.

Require four-eyes review for true matches and for any decision to onboard a high-risk candidate.

### 7. Remediate list changes

When a list updates, rescreen the existing book against the new entries. Track the delta: new entries, removed entries, changed identifiers. Prioritize high-risk customers and recent transactions.

## Gotchas

- Transliteration is the largest source of false negatives. Screen Arabic, Cyrillic, Chinese, and other scripts with multiple romanization schemes.
- Common names produce enormous candidate sets. Use DOB, country, and identifiers to disambiguate.
- Missing DOB is not a mismatch. Treat missing data as uncertainty, not innocence.
- Aliases and former names matter. A person may be listed under a variant.
- The 50% ownership rule for sanctions requires beneficial ownership analysis, not just direct screening.
- Adverse media is not a sanctions list. Apply source-quality and relevance review.
- List updates can be retroactive. Re-screen open relationships.
- Tipping-off prohibitions may limit what you tell the customer. Follow policy.
- Auto-clearing low scores is acceptable only with a documented, tested threshold and an audit trail.

## Output contract

```json
{
  "screening_id": "SCR-2026-00441",
  "subject": {"name": "...", "dob": "1980-04-12", "country": "..."},
  "list": {"name": "OFAC SDN", "version": "2026-11-22", "hash": "..."},
  "candidates": [
    {
      "entry_id": "12345",
      "name": "...",
      "score": 0.91,
      "components": {"name": 0.95, "dob": 1.0, "country": 1.0, "id": 0.0},
      "tier": "high"
    }
  ],
  "disposition": "false_positive",
  "rationale": "DOB differs by 6 years; no identifier match; common name",
  "analyst": "...",
  "reviewer": "...",
  "timestamp": "2026-11-24T12:00:00Z"
}
```

## Checklist

- [ ] List source, version, and hash recorded.
- [ ] Names and aliases normalized, originals retained.
- [ ] Identifiers and missing-data flags captured.
- [ ] Candidate generation covers exact and fuzzy methods.
- [ ] Composite score components retained.
- [ ] Thresholds documented and tuned.
- [ ] Disposition and four-eyes review recorded.
- [ ] List updates trigger rescreening.

## Related skills

- `transaction-anomaly-flagging` for behavior after onboarding.
- `human-in-the-loop-escalation` for true-match decisions.
- `source-grounded-citation-verification` for adverse media evidence.
