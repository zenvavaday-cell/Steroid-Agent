---
name: gdpr-data-subject-request
description: Handles access, deletion, and portability requests with identity verification, deadlines, and audit evidence. Use for DSAR operations and privacy compliance.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: legal-compliance
---

# GDPR Data Subject Request

## Overview

A data subject access request is a deadline-bound operational process, not a one-off email reply. The request must be logged on receipt, verified proportionately, scoped across every system that may hold the data, reviewed for exemptions and third-party rights, answered in a usable format, and closed with evidence that survives an audit.

GDPR Article 12(3) sets a one-month response clock, extendable by two months for complex requests with notice inside the first month. CCPA gives 45 calendar days, extendable by another 45 with notice. Missing the deadline is a compliance failure even when the substantive response is correct.

## When to use

- A data subject asks for a copy of their personal data or asks what is held about them.
- A data subject asks for erasure, rectification, restriction, objection, or portability.
- An authorized representative submits a request on someone's behalf.
- An employee, contractor, or job applicant submits a request through HR or legal.
- A request arrives through support, social media, or a regulator and must be routed into the DSAR workflow.
- You are testing whether the rights described in the privacy notice are actually operable.

Do not use to respond to a law enforcement request, a subpoena, or a litigation hold demand without legal review. Do not delete data subject to a legal hold or a statutory retention duty.

## Workflow

### 1. Log intake and start the clock

Create a request record at first receipt, not when the request reaches the privacy team. Capture channel, timestamp with time zone, requester identity, right requested, scope, jurisdiction, language, and deadline. Send an acknowledgment that does not confirm what data is held.

| Regime | Initial deadline | Extension | Extension notice |
| --- | --- | --- | --- |
| GDPR Art 12(3) | 1 month from receipt | 2 further months | Within the first month, with reasons |
| UK GDPR | 1 month from receipt | 2 further months | Within the first month, with reasons |
| CCPA/CPRA | 45 calendar days | 45 further days | Before the initial 45 days expire |
| Brazil LGPD Art 19 | 15 days | Limited | Confirm current regulator guidance |

Compute the deadline in code and store both the receipt timestamp and the calculated due date. A request received at 23:50 on a Friday still starts the clock that day.

### 2. Verify identity proportionately

Use the least intrusive method that matches the risk. If the requester is logged into an authenticated account, that may be sufficient. If not, use a verification challenge against contact details already on file. Request a government ID only when the data is sensitive or the identity is genuinely uncertain, and do not retain the ID longer than the verification record requires.

For a representative, verify written authority and the representative's own identity. For a parent or guardian, verify the relationship and the child's age. Record the method, date, verifier, and evidence reference. If identity cannot be verified after reasonable effort, you may decline, but document the attempts and the legal basis.

### 3. Clarify scope without stalling

A single request can cover several rights. Confirm whether the requester wants access, a copy, deletion, correction, portability, or all of them. Ask only when the scope is genuinely unclear, and do not use clarification to extend the deadline. If the request is broad, state the search scope and invite narrowing.

### 4. Search every plausible system

Use the processing inventory and a system list that includes production databases, warehouses, CRM, support tickets, marketing automation, analytics, logs, backups, mobile app storage, and processor-held data. Search by all identifiers the requester may have used: primary email, aliases, phone, account ID, name variants, and postal address.

```sql
-- Run on a read-only replica, with the value bound as a parameter.
SELECT user_id, email, created_at, deleted_at
FROM users
WHERE lower(email) = lower(:email)
   OR lower(primary_phone) = lower(:phone);
```

Do not paste requester-supplied strings into SQL. Do not run unbounded `LIKE '%...%'` scans on production. Log each query, the system, the row count, and the reviewer.

### 5. Review exemptions and third-party rights

Apply exemptions narrowly and record the legal basis for each withheld item. Common grounds include legal claims, a legal obligation to retain, freedom of expression, public interest, trade secrets, and the rights of other people. Redact third-party names, contact details, and free-text references that would identify someone else.

| Situation | Typical treatment |
| --- | --- |
| Data about the requester and other customers in one record | Disclose requester data, redact the others |
| Legal advice about a dispute | Consider privilege under member state law |
| Data needed for a legal claim | May refuse erasure, document the claim |
| Statutory retention (tax, employment, financial) | Retain the minimum, delete the rest |
| Trade secret in an algorithm | Explain the logic, protect the secret |

### 6. Assemble the response

For access, provide a copy of the personal data plus the Article 15(1) information: purposes, categories, recipients, retention, rights, source, automated decision-making logic, and transfer safeguards. For portability, provide data the requester supplied, processed by automated means on consent or contract, in a structured, commonly used, machine-readable format such as JSON or CSV.

For erasure, delete or irreversibly anonymize from every system in scope, propagate to processors, clear caches and search indexes, and schedule backup expiry. Where an exception applies, tell the requester what was retained and why. For rectification or restriction, update the record and notify recipients where required.

### 7. Deliver, close, and retain evidence

Send the response through a verified secure channel, not to an unverified email reply. Use encryption or a time-limited download link. Log delivery, receipt, and any follow-up. Close the request with a complete audit trail: intake, verification, search log, exemption decisions, reviewer approvals, response hash, and delivery confirmation. Retain the audit record for the period set by the retention schedule.

## Validation

- The deadline is calculated from the receipt timestamp and stored with the request.
- Any extension notice was sent before the initial deadline expired and states the reasons.
- Identity verification method and evidence are recorded; no unnecessary ID copy is retained.
- Every system in the inventory is marked searched, not applicable, or out of scope with a reason.
- Every withheld item has a specific legal basis and a reviewer approval.
- Third-party data is redacted and the redaction is checked in the final file.
- Access responses include all Article 15 headings, not only the data export.
- Portability exports contain only data supplied by the requester and processed automatically on consent or contract.
- Erasure is confirmed in primary storage, derived stores, caches, and processors; backup handling is documented.
- Delivery went to a verified channel and the delivery evidence is stored.
- The audit log is append-only and links to the evidence hashes.
- Open follow-ups (processor confirmation, backup expiry) have owners and dates.

## Gotchas

- The GDPR clock starts on receipt, not on successful verification. Verification should be prompt, not a reason to let the request age.
- Asking every requester for a passport is disproportionate and creates a new store of identity documents.
- A request sent to a shared inbox, a sales representative, or social media can still count as receipt by the controller.
- Deleting the primary database row is not erasure if the data remains in analytics, logs, exports, caches, or search indexes.
- Legal holds and statutory retention override erasure. Document the exception instead of silently keeping the data.
- Backups may not be editable. State the backup rotation and the date by which the data will age out.
- Shared accounts and family plans can expose another person's data. Split the response by data subject.
- Employee requests reach HR systems, email archives, performance notes, and badge logs, not only the HR database.
- Special category data needs extra review before disclosure, especially health, biometric, and union data.
- Portability does not cover inferred or derived data, and it does not require a format the controller does not use.
- Automated decision-making explanations must describe the logic and consequences without disclosing protected trade secrets.
- A "manifestly unfounded or excessive" refusal has a high bar and the burden of proof sits with the controller.
- Processor subprocessor chains can add weeks. Start the processor request on day one.

## Output contract

```json
{
  "request_id": "DSAR-2026-0184",
  "received_at": "2026-11-02T09:14:00Z",
  "channel": "privacy-webform",
  "requester": {"type": "data-subject", "jurisdiction": "EU", "language": "en"},
  "rights": ["access", "portability"],
  "deadline": {"initial": "2026-12-02", "extended": null, "notice_sent": null},
  "verification": {"method": "authenticated-account", "verified_at": "2026-11-02T10:02:00Z", "evidence_ref": "AUTH-7781"},
  "systems_searched": [
    {"system": "crm", "status": "searched", "records": 2, "reviewer": "privacy-ops-1"},
    {"system": "marketing-warehouse", "status": "searched", "records": 14, "reviewer": "privacy-ops-1"},
    {"system": "backups", "status": "scheduled-expiry", "detail": "35-day rotation"}
  ],
  "exemptions": [
    {"item": "support ticket note", "basis": "rights of another person", "reviewer": "counsel-2"}
  ],
  "response": {"format": "JSON plus PDF access report", "delivered_at": "2026-11-28T16:40:00Z", "channel": "secure-link", "sha256": "9f2c..."},
  "follow_ups": [{"action": "confirm processor deletion", "owner": "vendor-management", "due": "2026-12-09"}],
  "status": "closed"
}
```

## Checklist

- [ ] Request logged on receipt with timestamp and calculated deadline.
- [ ] Acknowledgment sent without confirming data holdings.
- [ ] Identity verified with the least intrusive method and evidence recorded.
- [ ] Representative or guardian authority verified where applicable.
- [ ] Scope and rights confirmed or clarification documented.
- [ ] All systems and processors searched, with query logs.
- [ ] Exemptions applied narrowly and approved by a reviewer.
- [ ] Third-party data redacted and redaction verified.
- [ ] Response includes the required Article 15 information.
- [ ] Portability export is machine-readable and correctly scoped.
- [ ] Erasure propagated and backup expiry documented.
- [ ] Delivery and audit evidence stored and linked.

## Related skills

- `privacy-policy-gap-analysis` to check that the notice accurately describes this request workflow.
- `guardrail-policy-enforcement` to enforce verification, approval, and delivery rules before release.
- `human-in-the-loop-escalation` to route exemptions and refusals to counsel.
- `security-incident-response` when a request reveals a breach or unauthorized access.
