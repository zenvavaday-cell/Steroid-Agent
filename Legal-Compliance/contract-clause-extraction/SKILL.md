---
name: contract-clause-extraction
description: Extracts clauses, parties, dates, obligations, and termination rights into a structured register. Use for contract intake and obligation tracking.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: legal-compliance
---

# Contract Clause Extraction

## Overview

Contract intake fails when extraction produces a summary instead of a register. A usable register preserves the exact source text, locates every field in the document, normalizes dates and amounts, and separates what the contract says from what a reviewer infers.

The core discipline is dual representation: every clause and obligation carries a verbatim quote with a page or paragraph anchor, plus a normalized record that downstream systems can query. Extraction without an anchor is unverifiable and cannot support obligation tracking.

## When to use

- Loading a new vendor, customer, or partner agreement into a contract management system.
- Building an obligation calendar from renewal, notice, payment, and reporting terms.
- Preparing a clause-level comparison after an amendment or restatement.
- Auditing a contract portfolio for termination rights and change-of-control terms.
- Extracting a data protection addendum from a master agreement before a privacy review.
- Creating a first-pass register for counsel to review and approve.

Do not use for deciding enforceability, interpreting ambiguous terms, or producing legal advice. The output is an extraction work product that a qualified reviewer must approve.

## Workflow

### 1. Fingerprint the source

Record the file name, SHA-256 hash, page count, language, and whether a text layer exists. Hash the exact file that was reviewed so the register can be reproduced after the file is replaced.

```python
import hashlib, pdfplumber

path = "vendor-msa.pdf"
sha = hashlib.sha256(open(path, "rb").read()).hexdigest()

with pdfplumber.open(path) as pdf:
    pages = [(i + 1, p.extract_text() or "") for i, p in enumerate(pdf.pages)]
    text_layer = all(len(text) > 40 for _, text in pages)
print({"sha256": sha, "pages": len(pages), "text_layer": text_layer})
```

If `text_layer` is false, run OCR and keep both the OCR text and the image page. Never treat OCR output as the authoritative quote without a visual check of the page.

### 2. Map the document structure

Identify the master agreement, statements of work, amendments, exhibits, schedules, and addenda. Record the order of precedence clause. A single PDF often contains several instruments with different effective dates.

Build a section tree with heading, level, page, and parent. For DOCX, use paragraph index and table cell coordinates. For scans, use page and bounding box.

### 3. Extract parties and dates

Take legal entity names from the preamble and confirm them against the signature block. Capture role (supplier, customer, licensor, licensee, guarantor), entity type, jurisdiction of organization, and notice address.

Normalize every date to ISO 8601 and record the source expression:

| Field | Rule | Example |
| --- | --- | --- |
| effective_date | Stated effective date, else signature date | `2026-01-01` |
| signed_date | Last signature date | `2025-12-18` |
| expiry_date | Fixed end date, else computed from term | `2028-12-31` |
| renewal_notice_by | Expiry minus notice period | `2028-09-30` |
| payment_due | Anchor plus payment terms | `net 30 from invoice receipt` |

Relative expressions such as "within 30 days of the Effective Date" require an anchor. Store the anchor field and the arithmetic, not only the computed date.

### 4. Classify clauses

Use a controlled taxonomy. Free-text labels make the register unqueryable.

| Type | Capture | Typical heading |
| --- | --- | --- |
| parties | Legal names, roles, affiliates | Parties |
| definitions | Defined term, meaning, scope | Definitions |
| scope | Services, products, territory, exclusivity | Scope of Services |
| fees | Amount, currency, cadence, escalation, true-up | Fees and Payment |
| term-renewal | Initial term, renewal mechanism, notice | Term and Renewal |
| termination | Trigger, notice, cure, refund, survival | Termination |
| ip | Ownership, license grant, feedback, deliverables | Intellectual Property |
| confidentiality | Definition, exclusions, duration, return | Confidentiality |
| data-protection | Roles, DPA reference, transfer mechanism | Data Protection |
| indemnity | Indemnitor, indemnitee, claims, procedure | Indemnification |
| liability | Cap, exclusions, carve-outs, basis | Limitation of Liability |
| warranties | Scope, remedy, disclaimer | Representations and Warranties |
| audit | Rights, notice, frequency, cost | Audit Rights |
| assignment | Consent, change of control, affiliates | Assignment |
| governing-law | Law, venue, arbitration, language | Governing Law |

For each clause, store `clause_id`, `type`, `heading`, `page`, `quote`, `normalized`, and `confidence`. The quote must resolve to the same text in the hashed source.

### 5. Extract obligations

An obligation needs an actor, an action, an object, and a timing element. "Vendor will provide reports" is incomplete until the cadence and delivery method are captured.

| Field | Definition | Example |
| --- | --- | --- |
| obligation_id | Stable register key | `OB-014` |
| party | Performing party | `Supplier` |
| action | Verb from the operative text | `deliver` |
| object | Deliverable or behavior | `monthly service report` |
| trigger | Event that starts the duty | `end of each calendar month` |
| deadline | Due date or period | `5 business days after month end` |
| recurring | Whether the duty repeats | `true` |
| evidence | Proof of performance | `report in support portal` |
| clause_id | Source clause | `C-022` |

Keep modal verbs: "shall" and "must" create obligations, "should" creates an expectation, "may" creates a right. Do not upgrade a "may" to a "shall".

### 6. Derive termination and renewal facts

List every termination right separately: party, trigger (cause, convenience, insolvency, change of control), notice period, cure period, effective date, and payment consequence. Do the same for renewal: automatic or affirmative, term length, notice window, price adjustment, and non-renewal effect.

Compute derived dates in code and show the inputs. Use the governing law to resolve business-day calculations, and state the holiday calendar used.

### 7. Validate and publish

Re-extract a random 10 percent sample and diff it against the first pass. Resolve conflicts by re-reading the page image. Publish JSON for systems and CSV for reviewers, both keyed by `clause_id`. Record the taxonomy version and extractor version.

## Validation

- The SHA-256 of the reviewed file matches the hash in the register.
- Every party in the signature block appears in `parties`, including guarantors and affiliates.
- `effective_date` is not later than `signed_date` unless the contract states a retrospective or delayed effect.
- Every clause quote resolves to the same characters at the recorded anchor.
- Every obligation has an actor, an action, and either a trigger or a deadline.
- Renewal notice dates equal expiry minus the stated notice period, with the arithmetic recorded.
- All amounts carry currency, unit, and tax basis.
- Clauses with confidence below 0.80 are queued for human review; below 0.60 they are excluded from automated downstream use.
- Amendments are reconciled against the original using the order of precedence, not appended blindly.
- The register states the taxonomy version, extractor version, and review status.

## Gotchas

- An amendment can replace a clause without restating the whole agreement. Read the amendment's scope and precedence language.
- Signature blocks may include affiliates, guarantors, or witnesses who are not contracting parties. Label roles explicitly.
- Defined terms can silently change an obligation. Extract definitions and resolve capitalized terms before normalizing.
- Evergreen renewal clauses can lock in another full term if the notice window is missed. Surface the notice date prominently.
- Scanned pages confuse `1/l`, `0/O`, and decimal separators. Verify all amounts and dates against the page image.
- Fee tables do not extract linearly. Preserve rows and columns; do not concatenate cells into an unreadable string.
- "Business days" and "days" are not interchangeable. Apply the governing law's holiday calendar and say which one.
- PDF page numbers differ from printed page numbers. Store both when they diverge.
- Character offsets shift after whitespace normalization. Anchor offsets to the raw extracted text and hash that text.
- A master agreement plus SOW plus DPA may have three effective dates and three termination regimes. Do not flatten them.
- Termination for convenience may still require payment of unused committed fees or wind-down costs.
- Exhibits incorporated by reference may contain the operative obligation. Follow the reference before declaring a clause missing.

## Output contract

```json
{
  "contract_id": "CTR-2026-0042",
  "source": {
    "file": "vendor-msa.pdf",
    "sha256": "e3b0c44298fc1c149afbf4c8996fb924...",
    "pages": 34,
    "text_layer": true
  },
  "parties": [
    {"name": "Example Supplier Ltd", "role": "supplier", "entity_type": "limited company", "jurisdiction": "England and Wales"}
  ],
  "dates": {
    "effective": "2026-01-01",
    "signed": "2025-12-18",
    "expiry": "2028-12-31",
    "renewal_notice_by": "2028-09-30",
    "assumptions": ["notice period is 90 calendar days"]
  },
  "clauses": [
    {"clause_id": "C-014", "type": "liability", "heading": "Limitation of Liability", "page": 9, "quote": "aggregate liability shall not exceed the fees paid in the twelve months preceding the claim", "normalized": {"cap": "12 months fees", "carve_outs": ["fraud", "willful misconduct"]}, "confidence": 0.94}
  ],
  "obligations": [
    {"obligation_id": "OB-007", "party": "Supplier", "action": "deliver", "object": "monthly service report", "trigger": "calendar month end", "deadline": "5 business days", "recurring": true, "clause_id": "C-022"}
  ],
  "termination": [
    {"party": "Customer", "right": "for convenience", "notice_days": 30, "cure_days": null, "fees": "unused prepaid fees refunded pro rata"}
  ],
  "flags": ["missing-data-protection-addendum"],
  "review": {"taxonomy_version": "1.0", "extractor_version": "1.0", "human_reviewed": false}
}
```

## Checklist

- [ ] File hash, page count, language, and text-layer status recorded.
- [ ] Master agreement, SOWs, amendments, and exhibits separated.
- [ ] Order of precedence identified and applied.
- [ ] Parties confirmed against the signature block.
- [ ] Dates normalized with anchors and arithmetic shown.
- [ ] Clauses classified with the controlled taxonomy.
- [ ] Every clause quote anchored and reproducible.
- [ ] Obligations include actor, action, object, trigger, and deadline.
- [ ] Termination and renewal rights extracted individually.
- [ ] Derived dates computed and checked against the governing law.
- [ ] Low-confidence clauses queued for human review.
- [ ] JSON and CSV outputs reconcile by `clause_id`.

## Related skills

- `contract-risk-review` to turn extracted clauses into playbook deviations and negotiation priorities.
- `thematic-regulatory-compliance-diffing` to compare contract obligations against regulatory requirements.
- `schema-enforced-json-extraction` to enforce the register schema at generation time.
- `source-grounded-citation-verification` to verify that every quote and page anchor resolves.
