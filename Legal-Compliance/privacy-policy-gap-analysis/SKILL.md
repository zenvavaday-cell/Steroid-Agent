---
name: privacy-policy-gap-analysis
description: Compares privacy notices and data practices to GDPR, CCPA, and internal policy requirements. Use for privacy program reviews and product launches.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: legal-compliance
---

# Privacy Policy Gap Analysis

## Overview

A privacy notice is a set of claims about how personal data is handled. A gap analysis tests those claims against three things: the actual processing behavior, the applicable legal requirements, and the organization's own internal policy. Comparing the notice to the law alone misses the most common failure, which is a notice that is legally well drafted but factually wrong.

The unit of analysis is the processing activity, not the paragraph. Each activity gets a purpose, a legal basis, a data category, a recipient set, a retention period, and a transfer mechanism. The notice is then checked claim by claim against that inventory.

## When to use

- Annual review of a public privacy notice or employee privacy notice.
- Launching a product, feature, mobile app, or cookie banner that collects new data.
- Adding a vendor, SDK, data broker, or cross-border data flow.
- Expanding into a new jurisdiction or serving a new category of data subject.
- Responding to a regulator inquiry, audit, or data incident.
- Integrating an acquired company's notice and data practices.

Do not use to certify compliance, to draft a final notice without counsel, or to assess processing that has not been inventoried. Do not treat a policy update as proof that practices changed.

## Workflow

### 1. Fix the scope and applicability

Record the legal entities, products, user populations, jurisdictions, languages, and review date. Determine which regimes apply and why. For GDPR, Article 3 applies to controllers and processors established in the EU, and to non-EU entities that offer goods or services to, or monitor, data subjects in the EU. For CCPA/CPRA, the statutory baseline covers for-profit businesses doing business in California that meet one of: annual gross revenue above the periodically adjusted threshold (statutorily $25 million), purchase, sale, or sharing of personal information of 100,000 or more consumers or households, or derivation of 50 percent or more of annual revenue from selling or sharing personal information. Verify the current adjusted figures with the regulator before relying on them.

Also list sector rules (health, financial, children's data) and internal policy versions that apply. A gap against an internal standard is still a finding, even if the law is silent.

### 2. Build the processing inventory

Use Article 30-style fields so the inventory can serve multiple purposes:

| Field | Content |
| --- | --- |
| activity_id | Stable key |
| data_subject | Customer, employee, prospect, child, visitor |
| data_category | Identifiers, commercial, biometric, health, geolocation, inference |
| sensitive_flag | Whether Article 9 or sensitive PI rules apply |
| purpose | Specific business purpose, not "operations" |
| legal_basis | Consent, contract, legal obligation, vital interest, public task, legitimate interests |
| source | Direct, third party, public source, inference |
| recipients | Processors, controllers, affiliates, advertisers, data brokers |
| transfer | Country and mechanism (adequacy, SCCs, BCRs, DPF) |
| retention | Period or deterministic rule |
| systems | Applications, warehouses, logs, backups |
| evidence | Link to the system owner or record |

If the inventory cannot be completed, the gap analysis is blocked. A notice review without a data map is a wording exercise.

### 3. Extract notice claims

Split the notice into sections and record each disclosure with an anchor:

```json
{
  "notice_id": "PUB-PRIVACY-2026-03",
  "section": "How We Share Information",
  "quote": "We may share personal information with service providers and advertising partners.",
  "anchor": "paragraph 12",
  "claim_type": "recipients",
  "claimed_value": ["service providers", "advertising partners"],
  "last_updated": "2026-03-01"
}
```

Review every layer, not only the main policy: collection-time notices, cookie banners, app store privacy labels, just-in-time prompts, employee notices, and jurisdiction-specific addenda.

### 4. Build the requirement matrix

Map each requirement to a notice section or to a gap. Include the citation so a reviewer can verify it.

| Requirement | GDPR basis | CCPA/CPRA basis | Evidence |
| --- | --- | --- | --- |
| Identity of controller | Art 13(1)(a) | Notice at collection | Legal entity and contact |
| Purposes of processing | Art 13(1)(c) | Purpose disclosure | Inventory purpose |
| Legal basis | Art 13(1)(c) | Not a direct CCPA concept | Basis per activity |
| Recipients and categories | Art 13(1)(e) | Categories of third parties | Vendor list |
| Transfers and safeguards | Art 13(1)(f), Ch V | Service provider contracts | Transfer register |
| Retention | Art 13(2)(a) | Retention disclosure | Retention schedule |
| Rights and how to exercise | Arts 12-22 | Right to know, delete, correct, opt out | Request workflow |
| Automated decisions | Art 13(2)(f), Art 22 | Profiling disclosures | Model inventory |
| Sale or sharing and opt-out | Art 21 objection | Opt-out and GPC | Tag and consent data |
| Sensitive PI limits | Art 9 condition | Limit use of sensitive PI | Consent and purpose |
| Children's data | Art 8 | Opt-in for sale of minors' data | Age assurance |

### 5. Test practice against the notice

For each claim, collect runtime evidence: cookie and tag scans, SDK inventory, network traces, form fields, account settings, vendor contracts, warehouse schemas, and deletion job logs. Check the paths users actually experience, including mobile apps, subdomains, and logged-out states.

Common mismatches to test explicitly:

- A "do not sell" statement while pixels or SDKs share identifiers for cross-context behavioral advertising.
- A cookie banner that loads non-essential tags before consent.
- A retention statement that does not match the deletion job's actual schedule.
- A vendor list that omits processors found in network traffic.
- A transfer statement that names a mechanism the organization no longer relies on.

### 6. Classify and score gaps

Use a fixed classification:

| Class | Definition | Example |
| --- | --- | --- |
| Missing | Required disclosure or control absent | No opt-out link |
| Inaccurate | Notice says one thing, practice does another | Claims no sale while sharing for ads |
| Ambiguous | Reasonable reader cannot determine scope | "We may share with partners" |
| Inconsistent | Two notice layers conflict | Banner allows only necessary, policy implies ads |
| Over-disclosure | Notice claims broader processing than occurs | Lists data not collected |

Score severity by rights impact, number of data subjects, sensitivity, and regulatory exposure. Critical findings block launch; high findings need an owner and a dated remediation plan.

### 7. Remediate and re-test

Assign each gap a fix type: notice text, consent flow, data map, vendor contract, retention job, access control, or transfer mechanism. Record owner, due date, and verification method. Re-run the specific test after the fix; do not close a gap because the text changed.

## Validation

- Scope names every entity, product, jurisdiction, and notice version reviewed.
- Every processing activity has a purpose, legal basis, recipient set, retention rule, and system owner.
- Every notice claim maps to runtime evidence or is marked unverified.
- Every requirement in the matrix has a status: met, partial, gap, or not applicable, with a citation.
- Cookie banner categories match the tags observed in a live scan.
- Retention statements match the deletion schedule for each data category.
- Each cross-border transfer names a current mechanism and the countries involved.
- Special category data has an Article 9 condition, not only an Article 6 basis.
- Sale and sharing statements match opt-out behavior, including Global Privacy Control.
- The notice's last-updated date and approval record are present.
- Remediation owners and dates are assigned for every critical and high gap.
- A second reviewer checks the high-severity findings against source evidence.

## Gotchas

- "We do not sell" can be false under CPRA because "sharing" covers cross-context behavioral advertising even without money changing hands.
- A consent banner that fires analytics or advertising tags before interaction invalidates the consent story.
- Data described as anonymized may be pseudonymous or re-identifiable. Test against the applicable standard.
- "As long as necessary" is not a retention disclosure. Tie each category to a period or a deterministic rule.
- Privacy Shield is invalid. Confirm the current transfer mechanism and whether a DPF certification actually covers the entity and data.
- Controller and processor roles can differ by product. A single notice that claims one role everywhere is usually wrong.
- Employee, contractor, and B2B contact data are often omitted from consumer-facing notices.
- The last-updated date is not the effective date. Record both and keep superseded versions.
- Layered notices drift. A short banner can contradict the long policy for months.
- Dark patterns, pre-checked boxes, and asymmetric buttons can invalidate consent even when the text is accurate.
- Children's data triggers separate consent and sale restrictions that a general notice will not satisfy.
- AI training or automated decision-making may need additional purpose, logic, and opt-out disclosures.

## Output contract

```json
{
  "review_id": "PPGA-2026-011",
  "scope": {
    "entities": ["Example Inc."],
    "products": ["consumer app", "marketing site"],
    "jurisdictions": ["EU", "California"],
    "notice_versions": ["PUB-PRIVACY-2026-03"],
    "reviewed_at": "2026-11-26"
  },
  "inventory_coverage": {"activities": 42, "with_owner": 40, "with_retention": 37},
  "gaps": [
    {
      "gap_id": "G-004",
      "requirement": "CCPA opt-out of sale or sharing",
      "citation": "Cal. Civ. Code 1798.120",
      "notice_anchor": "paragraph 18",
      "observed": "advertising pixels fire on page load and no opt-out link is present",
      "classification": "missing",
      "severity": "critical",
      "affected_subjects": "California consumers",
      "remediation": "deploy consent gate and Do Not Sell or Share link, honor GPC",
      "owner": "privacy-engineering",
      "due": "2026-12-15",
      "verification": "tag scan with clean profile plus GPC header test"
    }
  ],
  "summary": {"critical": 1, "high": 3, "medium": 5, "low": 2},
  "limitations": ["no inventory evidence for the legacy marketing warehouse"]
}
```

## Checklist

- [ ] Scope, regimes, entities, products, and notice versions fixed.
- [ ] Applicability analysis recorded with citations.
- [ ] Processing inventory completed or gap flagged as a blocker.
- [ ] Notice claims extracted with anchors and versions.
- [ ] Requirement matrix covers GDPR, CCPA/CPRA, and internal policy.
- [ ] Runtime evidence collected for cookies, SDKs, and forms.
- [ ] Sale and sharing claims tested against actual tag behavior.
- [ ] Retention and transfer claims verified against schedules and contracts.
- [ ] Gaps classified and scored with a consistent rubric.
- [ ] Critical gaps block launch until remediated.
- [ ] Owners, dates, and verification methods assigned.
- [ ] Re-test performed after each remediation.

## Related skills

- `gdpr-data-subject-request` to test whether the rights described in the notice are operable.
- `thematic-regulatory-compliance-diffing` to track requirement changes across regimes and versions.
- `security-control-mapping` to connect privacy controls to audit evidence.
- `vendor-evaluation` to assess processors and subprocessors named in the notice.
