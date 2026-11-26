---
name: litigation-document-review
description: Reviews document sets for relevance, privilege, chronology, and key evidence with citations. Use for e-discovery and case preparation.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: legal-compliance
---

# Litigation Document Review

## Overview

Document review is an evidence discipline. Every coding decision must be traceable to a document, a page, and a review protocol. A set of documents that "looks relevant" is not a review; it is an impression that cannot survive a challenge to completeness or a privilege motion.

The work has four layers: preserve and process the collection without altering it, apply a written relevance and privilege protocol, build a chronology that cites source documents, and validate the result with sampling and reconciliation before production or use in a brief.

## When to use

- Responding to a litigation hold, subpoena, or regulatory document request.
- Preparing evidence for a deposition, motion, hearing, or trial.
- Running an internal investigation with potential legal exposure.
- Reviewing a counterparty production for relevance and privilege issues.
- Building a chronology from emails, contracts, chats, and business records.
- Quality-checking a vendor's review before production.

Do not use to destroy, alter, or conceal documents. Do not use to make a final privilege call without counsel; privilege law varies by jurisdiction and waiver can be irreversible. Do not produce documents outside an approved review and clawback protocol.

## Workflow

### 1. Preserve and collect

Issue a written legal hold before collection, suspend auto-deletion, and identify custodians, systems, date ranges, and device types. Collect in a forensically sound manner where authenticity may be challenged. Record custodian, source system, collection date, collector, and hash.

Every file gets a SHA-256 hash and a chain-of-custody entry. Keep the original collection immutable and work from a copy. If a device is imaged, record the imaging tool, version, and hash of the image.

### 2. Process and reduce

Extract text, OCR images, expand archives, and preserve attachments and embedded files. Normalize dates to ISO 8601 while retaining the original string and time zone. Deduplicate exact duplicates by hash and near-duplicates by similarity; never drop a duplicate without retaining its custodian and path because provenance can matter.

Thread email conversations and identify inclusive emails. A reply may contain the only copy of an earlier privileged message, so threading must not hide the parent.

### 3. Write the review protocol

Define the issues, date range, custodians, relevance standard, privilege rules, confidentiality designations, and coding schema before review starts. Record who approved the protocol and when. If the protocol changes, version it and re-review affected documents.

| Code | Values | Purpose |
| --- | --- | --- |
| relevance | relevant, not relevant, needs review | First-pass filter |
| issue | contract, payment, notice, misrepresentation, damages, other | Case theory mapping |
| privilege | none, attorney-client, work-product, joint-defense, other | Withholding basis |
| confidentiality | public, confidential, trade-secret, personal-data | Production treatment |
| key_evidence | yes, no | Merits importance |
| chronology | date, event, actor, citation | Timeline entry |
| redaction | none, third-party, privilege, personal-data | Redaction basis |

### 4. Run first-pass and model-assisted review

Start with custodian, date, and keyword filters, then use a trained classifier or technology-assisted review where the volume justifies it. Measure recall against a random sample of the excluded set (elusion) and a sample of the included set. A recall estimate needs a confidence level and interval; use 95 percent confidence and a margin the protocol specifies, for example plus or minus 2 percent.

If recall is below the protocol target, expand the seed set, adjust the query, or review more documents. Do not report "high recall" without the sample design and the calculation.

### 5. Review documents

For each document, record the coding fields, reviewer ID, review date, and a citation to the page or message part. Read attachments and the full thread before coding an email. Code the document, not the folder or the subject line.

For key evidence, capture a short verbatim excerpt and the page anchor. For chronology entries, capture the event date, the actor, the event, and the document ID. Where dates conflict, record both and flag the conflict rather than choosing silently.

### 6. Build the privilege log and redactions

Log every withheld or redacted document with a stable ID, date, author, recipients, privilege type, and a factual basis that does not itself disclose privileged content. Do not use a bare label such as "privileged" without a basis. For redactions, verify that the underlying text layer, metadata, comments, and tracked changes do not reveal the redacted content.

Adopt a clawback agreement or court order where available. If a privileged document is produced inadvertently, notify counsel immediately and follow the protocol; do not attempt to recall it informally.

### 7. Build the chronology

Order events by date and time zone, citing each source. Distinguish document date, sent date, received date, and event date. Mark inferred dates as inferred. Identify gaps where a referenced document is missing, and list follow-up collection requests.

### 8. QC and produce

Run a second-pass review on a random sample and on all key evidence. Measure intercoder agreement on relevance and privilege. Reconcile produced, withheld, and redacted counts against the processing inventory. Assign Bates numbers, verify load-file fields, and run a privilege-leak check on the final production set.

## Validation

- A hash manifest covers every collected file and reconciles to the collection count.
- Exact duplicates are removed by hash with provenance retained; near-duplicates are flagged, not silently dropped.
- Every document in the review set has a relevance code and a reviewer ID.
- Every withheld or redacted document has a privilege log entry with a specific basis.
- No privileged document appears in a sample of the production set, and all privilege-adjacent documents received a second review.
- Every key-evidence and chronology entry cites a document ID and page or message part.
- Recall and precision estimates state the sample size, confidence level, and interval.
- Dates are normalized with the original string and time zone preserved.
- Redactions are verified against text layers, metadata, comments, and tracked changes.
- Production counts reconcile: collected minus duplicates minus excluded equals produced plus withheld plus redacted.
- Chain-of-custody and reviewer audit logs are complete.
- Counsel has approved the privilege calls and the production set.

## Gotchas

- Embedded files, compressed archives, and attachments can hide relevant or privileged content. Expand everything before coding.
- Email threads often include earlier privileged advice at the bottom. Review the full thread, not only the latest message.
- OCR errors can change names, amounts, and dates. Verify key facts against the page image.
- Metadata time zones can shift an event by a day. Record the zone and the original timestamp.
- Identical files from different custodians are still different provenance facts. Keep the custodian mapping.
- Deleted or fragmented files may be recoverable from backups or slack space. Do not assume deletion means nonexistence.
- Chat, mobile, and ephemeral messaging platforms need their own collection and threading logic.
- A document can be both relevant and privileged. Code both and withhold only with an approved basis.
- Redaction boxes over a searchable text layer can be reversed. Flatten or re-render the page and test extraction.
- Family documents can inherit privilege from an attachment or a covering email.
- Producing a privileged document can waive privilege. Use a clawback protocol and train reviewers on the edge cases.
- Litigation holds must reach personal devices, personal email used for work, and third-party messaging accounts.

## Output contract

```json
{
  "matter_id": "LIT-2026-003",
  "collection": {
    "custodians": 12,
    "source_systems": ["email", "sharepoint", "slack"],
    "collected_files": 84210,
    "sha256_manifest": "manifest-2026-11-20.csv"
  },
  "processing": {
    "exact_duplicates_removed": 18344,
    "near_duplicates_flagged": 921,
    "ocr_pages": 4102,
    "date_range": ["2023-01-01", "2026-06-30"]
  },
  "review": {
    "protocol_version": "1.2",
    "reviewed": 65866,
    "relevant": 4210,
    "key_evidence": 187,
    "privileged_withheld": 312,
    "redacted": 204
  },
  "privilege_log": [
    {"doc_id": "DOC-00412", "date": "2025-03-14", "author": "outside counsel", "recipients": ["general counsel"], "type": "attorney-client", "basis": "legal advice on contract termination", "action": "withheld"}
  ],
  "chronology": [
    {"date": "2025-03-14", "actor": "vendor", "event": "notice of termination sent", "doc_id": "DOC-00412", "page": 1, "confidence": "high"}
  ],
  "validation": {"recall_estimate": 0.96, "recall_interval": [0.94, 0.98], "sample_size": 400, "agreement": 0.91},
  "open_items": ["collect custodian 7 personal phone"]
}
```

## Checklist

- [ ] Legal hold issued and auto-deletion suspended.
- [ ] Collection logged with custodian, source, date, and hash.
- [ ] Originals preserved; review performed on copies.
- [ ] Archives, attachments, and embedded files expanded.
- [ ] Review protocol approved and versioned.
- [ ] Deduplication retains provenance.
- [ ] Recall and precision measured with a documented sample.
- [ ] Every document coded with relevance and reviewer ID.
- [ ] Privilege log complete with specific bases.
- [ ] Key evidence and chronology entries cited.
- [ ] Redactions tested for text-layer and metadata leakage.
- [ ] Production counts reconciled and counsel approved.

## Related skills

- `source-grounded-citation-verification` to verify quotes and page anchors in briefs and chronologies.
- `human-in-the-loop-escalation` to route privilege calls and production approvals to counsel.
- `guardrail-policy-enforcement` to block production when required checks have not passed.
- `schema-enforced-json-extraction` to keep review coding and privilege logs machine-readable.
