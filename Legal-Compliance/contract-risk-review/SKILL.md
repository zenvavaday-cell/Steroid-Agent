---
name: contract-risk-review
description: Flags unfavorable terms, missing protections, and negotiation priorities against a playbook. Use for vendor and customer contract review.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: legal-compliance
---

# Contract Risk Review

## Overview

A contract risk review is not a list of clauses a reviewer dislikes. It is a comparison between the drafted terms and an approved playbook that states preferred, acceptable, fallback, and unacceptable positions for each clause area. The playbook is the benchmark; the contract is the evidence.

Risk comes from three sources: terms that deviate from the playbook, protections that are missing entirely, and interactions between clauses that create exposure neither clause creates alone. The review must show which source applies, quote the language, quantify exposure where possible, and rank what to negotiate first.

## When to use

- Reviewing a vendor master services agreement, SaaS subscription, or professional services contract.
- Reviewing a customer paper contract received in a sales cycle.
- Assessing an NDA, data processing addendum, or software license before signature.
- Preparing a renewal review where terms may have drifted from the original.
- Triaging a high-volume queue and escalating only material deviations.
- Updating the playbook after a negotiation reveals a new fallback position.

Do not use for a final legal opinion, for interpreting criminal or regulatory exposure, or as a substitute for licensed counsel in a regulated jurisdiction. Do not negotiate directly from model output without human approval.

## Workflow

### 1. Classify the engagement

Record contract type, counterparty, role (customer or supplier), annual contract value, term, data sensitivity, entity count, governing law, and strategic importance. These inputs select the playbook variant and the approval threshold.

| Input | Why it changes the review |
| --- | --- |
| Role | A customer buying SaaS cares about data, uptime, and exit; a supplier cares about payment and liability |
| Annual value | Higher value justifies more negotiation and tighter caps |
| Personal data | Triggers DPA, transfer, breach notice, and audit checks |
| Regulated activity | Adds outsourcing, audit, and recordkeeping requirements |
| Term and renewal | Long terms amplify auto-renewal and price escalation risk |
| Entity count | Affiliates and assignment terms affect scope |

### 2. Load the playbook and record its version

Use the playbook approved for the contract type and jurisdiction. Record `playbook_id`, version, approval date, and owner. If no playbook exists, stop and build one with counsel; do not invent "market" positions.

Illustrative position ladder (example only, not a universal standard):

| Clause area | Preferred | Acceptable | Fallback | Unacceptable |
| --- | --- | --- | --- | --- |
| Liability cap | Mutual, 12 months fees | Mutual, 24 months fees | Supplier cap at fees paid | Uncapped except narrow carve-outs |
| Indemnity | Mutual for third-party claims | Supplier indemnifies for IP and data breach | Capped indemnity | Customer indemnifies supplier for supplier negligence |
| Termination | Convenience on 30 days, pro-rata refund | Convenience on 60 days | Cause only with cure | No termination for cause |
| Data protection | DPA with transfer mechanism and 24-hour breach notice | DPA with 72-hour notice | DPA with 5-day notice | No DPA |
| IP | Customer owns deliverables, supplier keeps pre-existing IP | Supplier licenses deliverables | Broad license to customer | Supplier owns custom deliverables |
| Payment | Net 60 | Net 30 | Net 15 | Prepayment or auto-debit |
| Auto-renewal | None | 12 months with 60-day notice | 12 months with 30-day notice | Short notice window with price increase |
| Governing law | Customer jurisdiction | Neutral forum | Supplier jurisdiction | Foreign exclusive forum |

### 3. Extract and verify the clauses

Use a clause extractor that preserves page anchors and verbatim quotes. Re-read the source page for every high-risk finding. Record the exact clause reference and the playbook rule it violates.

If a clause is absent, say so and cite the required clause list. Absence is a finding, but it must be proven by a full-text search plus a table of contents review, not by memory.

### 4. Score each deviation

Score likelihood and impact from 1 to 5, then multiply:

```text
risk_score = likelihood x impact
1-4 low, 5-9 medium, 10-16 high, 17-25 critical
```

| Dimension | 1 | 3 | 5 |
| --- | --- | --- | --- |
| Likelihood | Remote | Possible in term | Expected or already occurring |
| Financial impact | Under 1 percent of contract value | 1 to 10 percent | Over 10 percent or uncapped |
| Operational impact | Manual workaround | Service degradation | Loss of service or data |
| Legal impact | Clarification needed | Negotiation required | Regulatory or rights exposure |

Use the playbook's clause weights when aggregating. Do not sum scores across unrelated clauses and call the total "contract risk"; report the maximum severity, the count of high and critical findings, and the specific interactions.

### 5. Check for missing protections

Run a required-clause checklist by contract type. A SaaS review, for example, should confirm service levels, service credits, uptime measurement, maintenance windows, security exhibit, DPA, subprocessor approval, breach notification, data return and deletion, audit rights, business continuity, insurance, termination assistance, and escrow where source code is mission critical.

For each missing item, record the consequence and the requested language. Do not mark a clause missing if it is incorporated by reference and the referenced document is available in the data room.

### 6. Test cross-clause interactions

Read these pairs together, because each can neutralize the other:

- Limitation of liability versus indemnity: carve-outs can make the cap meaningless.
- Exclusive remedy versus warranties: the remedy may be the only recovery.
- Termination for convenience versus fees: exit may trigger a large payment.
- Confidentiality duration versus trade secret protection: a fixed term may end protection too early.
- Data breach notification versus liability cap: breach costs may exceed the cap.
- Order of precedence versus the negotiated MSA: a clickwrap SOW can override agreed terms.
- Governing law versus arbitration seat: the forum may not match the chosen law.
- Assignment versus change of control: control can change without consent.

### 7. Quantify exposure where the facts allow

Compute the liability cap from the actual fee schedule, not from a generic assumption. If the contract has a 12-month cap, state the trailing 12-month fees used and the source. For data breach, use the record count and applicable notification costs only if the client supplied them; otherwise label the estimate as illustrative and show the formula.

### 8. Prioritize and write the memo

Classify each request as must-have (walk-away), should-have (material but negotiable), or nice-to-have. Give the business owner a decision, not a clause dump: approve, approve with conditions, negotiate, escalate, or reject. Include proposed language only where counsel has approved it or mark it as a draft for counsel.

## Validation

- Every finding cites a clause quote, page, and playbook rule ID.
- No finding relies on "market standard" without a cited source or the playbook.
- The liability cap is computed from the fee schedule and the arithmetic is shown.
- Indemnity, exclusive remedy, and liability cap are read together and the interaction is documented.
- Missing-clause findings are supported by a full-text search and document inventory.
- High and critical findings have a named legal reviewer and a review date.
- Proposed redlines are labeled as draft until counsel approves them.
- The memo records the playbook version and any deviations approved for this deal.
- The final decision is one of the allowed outcomes, with the approver identified.

## Gotchas

- A liability cap with broad carve-outs (fraud, IP indemnity, data breach, gross negligence) may provide no real cap. Sum the realistic exposure.
- Excluding indirect damages can exclude lost profits and data loss even when those are the main risk. Check the definitions.
- Indemnity procedures matter: short notice periods and defense control can forfeit protection.
- Auto-renewal plus a price escalation clause can lock in an increase without a fresh negotiation.
- Unilateral suspension rights let the supplier cut service during a payment dispute.
- Audit rights without frequency, notice, or cost limits can be operationally expensive.
- "Commercially reasonable efforts" and "best efforts" are not the same, and neither is a guarantee.
- Subcontractor use without approval can move data to an unvetted processor.
- Order of precedence may place an online term or SOW above the negotiated MSA.
- Assignment on change of control can transfer the contract to a competitor.
- Termination for convenience may not refund prepaid fees or may require an early termination charge.
- Security obligations incorporated by URL can change without signature. Freeze the version or require notice.
- A foreign arbitration seat can make a favorable governing law impractical to enforce.

## Output contract

```json
{
  "contract_id": "CTR-2026-0042",
  "playbook": {"id": "vendor-saas-v3", "version": "3.2", "approved": "2026-02-01"},
  "classification": {"type": "saas-subscription", "role": "customer", "annual_value": 240000, "currency": "USD", "data_sensitivity": "personal"},
  "findings": [
    {
      "finding_id": "F-003",
      "area": "limitation-of-liability",
      "clause_ref": "Section 9.2",
      "page": 9,
      "quote": "Supplier's aggregate liability shall not exceed the fees paid in the preceding twelve months",
      "deviation": "cap is one-sided and excludes data breach from the carve-outs",
      "playbook_rule": "LIA-02",
      "likelihood": 3,
      "impact": 4,
      "risk_score": 12,
      "severity": "high",
      "requested_change": "make the cap mutual and add data breach to the carve-outs",
      "priority": "must-have"
    }
  ],
  "missing_protections": [
    {"item": "data processing addendum", "consequence": "no documented processor obligations or transfer mechanism", "requested": "execute the approved DPA before signature"}
  ],
  "interactions": [
    {"clauses": ["Section 9.2", "Section 10.1"], "issue": "IP indemnity is carved out of the cap, so the cap does not limit the largest exposure"}
  ],
  "decision": "negotiate",
  "approver": "legal-counsel",
  "open_questions": []
}
```

## Checklist

- [ ] Contract type, role, value, data sensitivity, and jurisdiction recorded.
- [ ] Playbook ID and version recorded.
- [ ] All required clause areas checked, including absent clauses.
- [ ] Every finding has a quote, page, and playbook rule.
- [ ] Likelihood and impact scored with the stated rubric.
- [ ] Liability cap computed from actual fees.
- [ ] Cross-clause interactions tested.
- [ ] Missing protections listed with consequences.
- [ ] Negotiation priorities split into must, should, and nice.
- [ ] Decision and approver recorded.
- [ ] Draft language labeled for counsel review.
- [ ] High and critical findings escalated to a human reviewer.

## Related skills

- `contract-clause-extraction` to produce the anchored clause register this review depends on.
- `thematic-regulatory-compliance-diffing` to overlay regulatory obligations on the contract terms.
- `vendor-evaluation` to combine contract risk with security, financial, and exit scoring.
- `human-in-the-loop-escalation` to route critical findings to counsel before negotiation.
