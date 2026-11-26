---
name: vendor-evaluation
description: Scores vendors on requirements, risk, cost, support, and exit strategy with evidence. Use for procurement and renewal decisions.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: business-ops
---

# Vendor Evaluation

## Overview

Vendor selection fails in predictable ways: the best demo wins, the must-have that fails is averaged away, total cost excludes migration and internal labor, reference calls are choreographed by the vendor, and nobody plans how to leave. A defensible evaluation gates must-haves first, scores the rest against anchored evidence, and treats exit as a first-class criterion.

This skill produces a scored recommendation with a decision memo that procurement, security, legal, and finance can approve without re-running the analysis.

## When to use

- Selecting a new SaaS, infrastructure, outsourcing, or professional-services vendor.
- Renewing an incumbent and deciding whether to renegotiate, replace, or expand.
- Running a competitive RFP with three or more responses.
- Building a business case for a purchase above the approval threshold.
- Reviewing a vendor's security, financial, or concentration risk before onboarding.

Do not use for low-value, reversible purchases under the delegated approval limit, or for evaluating individual contractors where an interview process is the right tool.

## Workflow

### 1. Define requirements before seeing vendors

Separate must-have, should-have, and nice-to-have (MoSCoW). Each requirement needs a measurable acceptance test and an internal owner. Requirements written after the demo are contaminated by vendor framing.

| ID | Requirement | Priority | Acceptance test | Owner |
| --- | --- | --- | --- | --- |
| R1 | SSO with SCIM provisioning | Must | Okta test tenant provisions and deprovisions in under 5 min | Security |
| R2 | Audit log export to SIEM | Must | JSON events arrive within 60 s | Security |
| R3 | Usage-based billing with committed tier | Should | Invoice reconciles to usage report within 1% | Finance |
| R4 | Regional data residency | Should | Contract names the storage region | Legal |

### 2. Apply must-have gates before scoring

A must-have failure is a rejection, not a low score. Run the gate as a table so the reason is explicit and auditable.

```python
def gate(vendor, must_haves):
    failed = [rid for rid, ok in must_haves[vendor].items() if not ok]
    return {"vendor": vendor, "passed": not failed, "failed": failed}


vendors = {
    "alpha": {"R1": True, "R2": True},
    "beta": {"R1": True, "R2": False},
}
for name in vendors:
    print(gate(name, vendors))
```

### 3. Set weights from business impact

Weights sum to 100. Cap any single criterion at 30 to prevent one dimension from dominating. Document who set the weights and when, before scoring starts.

| Criterion | Weight | Rationale |
| --- | --- | --- |
| Functional fit | 25 | Drives daily user value |
| Total cost of ownership | 20 | Three-year budget impact |
| Security and compliance | 20 | Regulatory exposure |
| Reliability and support | 15 | Operational continuity |
| Implementation effort | 10 | Internal capacity constraint |
| Exit and portability | 10 | Avoids lock-in |

### 4. Score with an anchored rubric and cite evidence

Use a 1 to 5 scale with written anchors. Every score of 3 or higher needs a source: demo script result, sandbox test, document section, or reference call. Vendor claims alone cap a score at 2.

| Score | Anchor |
| --- | --- |
| 1 | Requirement not met, no workaround |
| 2 | Claimed only, unverified, or requires significant custom work |
| 3 | Met in demo, not tested in our environment |
| 4 | Verified in our sandbox or documented with contractual commitment |
| 5 | Verified in production-like conditions plus a reference confirms it |

| Criterion | Vendor A | Evidence | Vendor B | Evidence |
| --- | --- | --- | --- | --- |
| Functional fit | 4 | Sandbox R1 and R3 passed | 3 | Demo only |
| TCO | 3 | 3-year model, no egress estimate | 4 | Fixed all-in quote |
| Security | 4 | SOC 2 Type II, pen test summary | 2 | Questionnaire only |
| Support | 3 | 99.9% SLA, 8x5 support | 4 | 99.95% SLA, 24x7 |
| Implementation | 3 | 10 weeks, partner-led | 2 | 16 weeks, custom |
| Exit | 2 | Proprietary export | 4 | Full API and CSV export |

### 5. Build a three-year total cost of ownership

Include license, implementation, integration, data migration, training, internal labor, support, price escalation, add-ons, and exit. Show cash cost and internal effort separately. Discount only if the organization requires NPV; state the rate.

| Cost line | Year 1 | Year 2 | Year 3 | Notes |
| --- | --- | --- | --- | --- |
| Subscription | 120,000 | 126,000 | 132,300 | 5% contractual uplift |
| Implementation | 40,000 | 0 | 0 | Fixed-fee quote |
| Integration | 25,000 | 5,000 | 5,000 | Two internal engineers, 200 hours |
| Training | 8,000 | 2,000 | 2,000 | Train-the-trainer |
| Exit provision | 0 | 0 | 15,000 | Export and parallel run |

Label all figures as an illustrative example; replace them with quotes and time records.

### 6. Assess risk beyond the feature checklist

| Risk area | Evidence to request | Red flag |
| --- | --- | --- |
| Security | SOC 2 Type II, ISO 27001, pen test summary, subprocessor list | Self-attestation only, stale report |
| Financial viability | Audited accounts, funding runway, credit report | Declining revenue, going-concern note |
| Concentration | Revenue share from top customers, subcontractors | One client is most of revenue |
| Availability | SLA, status history, RTO/RPO, DR test results | No tested DR, credits only remedy |
| Legal | DPA, liability cap, indemnity, termination rights | Unilateral price or term changes |
| Compliance | Data residency, retention, deletion, audit rights | Data use for model training by default |

### 7. Run independent reference checks

Ask for three references, then source at least two more from your network or review sites. Use the same six questions: what broke, how fast support responded, what implementation actually cost, what they wish they had negotiated, whether they renewed, and what leaving would take. Record the reference name, company size, date, and relationship to the vendor.

### 8. Test robustness of the winner

Recompute the ranking with weights shifted plus or minus 10 points and scores shifted plus or minus 1. If the winner changes, the decision is not robust; report the range and the swing criteria rather than a false precision.

### 9. Write the exit plan before signing

Specify data export format and frequency, retention and deletion timeline, transition assistance hours, knowledge transfer, escrow for on-premise components, notice period, early-termination fees, and post-termination price for export help. An exit plan that is impossible to execute is not a plan.

## Validation

| Gate | Pass criterion | Fail action |
| --- | --- | --- |
| Requirements | Every requirement has a priority, test, and owner | Complete before demos |
| Gates | All must-haves verified or vendor rejected | Remove from scoring |
| Weights | Sum to 100, no criterion above 30, set before scoring | Re-baseline |
| Evidence | Every score of 3+ has a dated source | Cap at 2 |
| TCO | Three-year all-in cost with escalation and exit | Rebuild model |
| References | At least two non-vendor-nominated references | Source independently |
| Risk | Security and legal sign-off recorded | Hold recommendation |
| Sensitivity | Winner stable under stated shifts, or range reported | Present as conditional |
| Exit | Export, deletion, and transition terms documented | Negotiate before signature |

## Gotchas

- A polished demo measures presentation skill, not fit. Require sandbox tasks scored by the people who will use the product.
- Weighted averages hide a failed must-have. Gate first, score second.
- Vendors quote list price while renewals are negotiated on street price. Compare effective price per unit after discounts and terms.
- TCO often omits internal integration, migration, training, and parallel-run labor. Add time records, not guesses.
- Reference calls arranged by the vendor are part of the sales process. Source at least two independently.
- Security questionnaires are self-reported. Require the report, its date, and the scope; check exceptions.
- "Unlimited" plans have fair-use limits in the contract. Read the acceptable-use and overage clauses.
- Auto-renewal and notice windows can lock in a bad decision for another year. Put the notice date in the procurement calendar.
- Price escalation caps matter more than year-one price. Model 5 to 10 percent annual uplift.
- A pilot without exit criteria becomes an accidental commitment. Define success, duration, cost, and what happens at the end.
- Scoring scale drift lets one evaluator use 3 as average while another uses 5. Calibrate with two shared examples before scoring.
- Data egress and API limits can make exit expensive. Price a one-time full export during evaluation.

## Output contract

```yaml
evaluation:
  id: PROC-2026-014
  decision: recommend_vendor_a
  requirements_version: "3.0"
  weights:
    functional_fit: 25
    tco: 20
    security: 20
    support: 15
    implementation: 10
    exit: 10
  vendors:
    - name: Vendor A
      must_have_gates: {R1: pass, R2: pass}
      scores:
        functional_fit: {score: 4, evidence: "Sandbox run 2026-11-18"}
        tco: {score: 3, evidence: "3-year model v2"}
      tco_3y: 411300
      risks:
        - area: exit
          severity: high
          mitigation: "Negotiate full API export and 90-day transition"
      weighted_score: 3.45
    - name: Vendor B
      must_have_gates: {R1: pass, R2: fail}
      status: rejected
      rejection_reason: "No audit log export"
  sensitivity:
    winner_stable: false
    swing_criteria: "Functional fit weight above 30 favors Vendor A; below 20 favors Vendor B"
  references:
    - company: Example Retail Co
      source: independent
      date: 2026-11-12
  approvals:
    security: pending
    legal: pending
    finance: approved
```

## Checklist

- [ ] Requirements written and baselined before vendor demos.
- [ ] Must-have gates scored pass or fail.
- [ ] Weights sum to 100 and were fixed before scoring.
- [ ] Rubric anchors shared with every evaluator.
- [ ] Every score of 3 or higher cites dated evidence.
- [ ] Three-year TCO includes internal labor, escalation, and exit.
- [ ] Security, financial, concentration, and legal risks reviewed.
- [ ] At least two independent references contacted.
- [ ] Sensitivity analysis reported.
- [ ] Exit plan and notice dates documented.
- [ ] Required approvals recorded before signature.

## Related skills

- `supply-chain-security-review` for deeper dependency and provenance checks on software vendors.
- `contract-risk-review` for negotiating liability, termination, and data-protection terms.
- `security-control-mapping` to align vendor evidence with SOC 2 or ISO 27001 requirements.
- `budget-variance-analysis` to test the TCO against the approved budget and forecast.
