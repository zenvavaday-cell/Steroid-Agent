---
name: sop-generation
description: Turns tribal knowledge into testable standard operating procedures with controls and revision history. Use for operations scaling and audits.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: business-ops
---

# SOP Generation

## Overview

An SOP is a controlled document that lets a competent person who did not write it execute a process correctly, produce the same output, and generate the evidence required by its controls. Most "SOPs" fail because they describe intent rather than action, omit prerequisites and exceptions, and cannot be tested.

The discipline is to capture the real process from observed executions, separate required steps from workarounds, attach measurable completion criteria to each step, and prove the document works with a dry run by someone other than the author.

## When to use

- A recurring process lives in one person's head or in scattered chat messages.
- Preparing for an audit, certification, or customer security review that requires documented controls.
- Onboarding new staff or handing a process to another team or region.
- Standardizing variants of the same process across teams, sites, or shifts.
- After an incident caused by an undocumented step, missing approval, or unclear ownership.

Do not use for one-off projects, high-level policy (which states intent and authority), or vendor product instructions that already have an official manual.

## Workflow

### 1. Define scope and boundaries

Write the process name, business purpose, trigger, start point, end point, frequency, volume, systems, roles, and regulatory drivers. State what is out of scope. A scope that cannot be bounded produces an unmaintainable document.

| Field | Example |
| --- | --- |
| Process | Vendor invoice approval and payment release |
| Trigger | Invoice received in the AP inbox |
| Start | Invoice logged with a unique ID |
| End | Payment released and reconciled |
| Volume | About 1,200 invoices per month |
| Systems | AP inbox, ERP, bank portal |
| Regulation | Internal control policy FIN-04, SOX-relevant |

### 2. Capture the current state from real executions

Observe at least three executions, including one exception case. Interview the operator and the reviewer separately. Collect the artifacts each step produces: ticket, approval, screenshot, reconciliation, email. Record time spent per step and every workaround. Label workarounds as current-state behavior, not as approved procedure.

### 3. Define roles and decision rights

Use a RACI table. Distinguish the role that performs a step from the role that approves it. Approval authority must include a monetary or risk limit, not just a job title.

| Activity | Operator | Reviewer | Process owner | Finance |
| --- | --- | --- | --- | --- |
| Log and code invoice | R | A | I | I |
| Approve above 10,000 | I | R | A | C |
| Release payment | R | A | I | C |
| Handle exception | R | A | C | I |

### 4. Draft executable steps

One action per step. Start with an imperative verb. Name the system, the input, the output, and the expected result. Avoid "handle", "process", "check", and "as needed" without criteria.

| Step | Action | System | Input | Expected result | Role | Target time |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Open the invoice and confirm the PO number is present | ERP | Invoice PDF | PO field populated or exception raised | Operator | 2 min |
| 2 | Match invoice amount and quantity to the PO within 1% | ERP | PO and invoice | Match status green; mismatches routed to step 6 | Operator | 3 min |
| 3 | Route invoices above 10,000 to the cost-center reviewer | Workflow | Matched invoice | Approval task created with 2-day SLA | Operator | 1 min |

Completion criteria must be observable: a status, a field value, a file, a signature, or a reconciliation result. "Reviewed" is not a completion criterion.

### 5. Attach controls to the risks they mitigate

For each control, record the risk, control type (preventive or detective), frequency, evidence produced, owner, and how an auditor would test it. Controls that leave no evidence cannot be tested.

| Control | Risk | Type | Frequency | Evidence | Test |
| --- | --- | --- | --- | --- | --- |
| C1 | Payment to wrong vendor | Preventive | Each invoice | Vendor master match log | Sample 25 invoices, confirm match |
| C2 | Duplicate payment | Detective | Weekly | Duplicate report with sign-off | Inspect 4 weekly reports per quarter |
| C3 | Unauthorized approval | Preventive | Each invoice | Approval trail with role and limit | Recompute approval authority |

### 6. Document exceptions and escalation

Build a decision table that covers the exceptions observed during capture. Include who can approve each exception, the maximum value, the time limit, and what happens when the approver is unavailable.

| Condition | Action | Escalate to | Authority limit |
| --- | --- | --- | --- |
| No PO exists | Request retro PO or reject | Procurement manager | Up to 5,000 |
| Amount mismatch above 1% | Hold payment, contact vendor | AP team lead | Any amount |
| Vendor bank detail change | Verify by callback to known number | Treasury | Any amount |
| Approver unavailable 2 business days | Reassign to delegate | Process owner | Per delegation matrix |

### 7. Dry run with an independent operator

Select an operator who did not write the SOP and has the required system access. Run a real or sandbox case end to end. Time each step, log every question, and check that every control produced its evidence. The author must not help except to record gaps.

### 8. Approve, publish, and maintain

Record the owner, approver, effective date, version, and next review date. Set review triggers: annual review, system change, regulatory change, or a control failure. Publish one canonical copy with a stable link. Retire superseded versions and keep them for the retention period.

## Validation

| Gate | Pass criterion | Fail action |
| --- | --- | --- |
| Scope | Trigger, start, end, and exclusions stated | Rewrite scope |
| Step executability | Independent operator completes the case without asking the author | Clarify the failing steps |
| Output parity | Output matches the reference case within defined tolerance | Fix steps or acceptance criteria |
| Control evidence | Every control produced its evidence during the dry run | Redesign control |
| Timing | Total cycle time within the target or variance explained | Re-sequence or resource |
| Exception coverage | Every observed exception maps to a decision row | Add missing rows |
| Roles | Every step has one performing role and approvals have limits | Correct RACI |
| Version control | Version, owner, effective date, review date present | Add before publishing |
| Accessibility | Steps readable by a new hire without tribal context | Rewrite jargon and acronyms |

## Gotchas

- "Verify the invoice" has no pass criterion. State the field, tolerance, and result that counts as verified.
- Missing prerequisites cause the most dry-run failures. List system access, licenses, templates, and data before step 1.
- Workarounds get promoted to official steps. Keep current-state notes separate from the approved procedure.
- Controls without evidence cannot survive an audit. Design the artifact at the same time as the control.
- Screenshots age faster than text. Describe the system field and intent, and date any image.
- A 40-step SOP will not be followed. Split into sub-procedures with a clear parent index.
- Two documents can both claim to be canonical. Assign one owner and one location, and retire duplicates.
- Revision history written after the fact is unreliable. Update it in the same change as the procedure.
- Training completion is not process compliance. Test the process output, not only attendance.
- Regulatory text pasted into an SOP rarely tells an operator what to do. Translate obligations into actions and evidence.
- Regional or system variants drift. Use a base SOP plus a variant table, not separate divergent copies.
- UI labels change with vendor releases. Anchor steps to business meaning and add a last-verified date.

## Output contract

```yaml
sop:
  id: SOP-FIN-AP-001
  title: Vendor invoice approval and payment release
  version: "2.1.0"
  owner: Accounts Payable Manager
  approver: Controller
  effective_date: 2026-12-01
  next_review: 2027-12-01
  scope:
    trigger: Invoice received in the AP inbox
    start: Invoice logged with a unique ID
    end: Payment released and reconciled
    out_of_scope: Customer refunds, intercompany settlements
  roles:
    - name: Operator
      responsibilities: Log, code, and match invoices
    - name: Reviewer
      responsibilities: Approve invoices above 10,000
  prerequisites:
    - ERP AP role and workflow license
    - Vendor master read access
  steps:
    - number: 1
      action: Confirm the PO number is present on the invoice
      system: ERP
      output: PO field populated or exception raised
      role: Operator
      target_minutes: 2
  controls:
    - id: C1
      risk: Payment to wrong vendor
      type: preventive
      evidence: Vendor master match log
      test: Sample 25 invoices and confirm match
  exceptions:
    - condition: No PO exists
      action: Request retro PO or reject
      escalate_to: Procurement manager
      authority_limit: 5000
  revision_history:
    - version: "2.1.0"
      date: 2026-11-20
      change: Added bank-detail callback control
      author: Accounts Payable Manager
```

The rendered SOP should follow the section order: purpose, scope, roles, prerequisites, procedure, controls, exceptions, records, revision history.

## Checklist

- [ ] Scope, trigger, start, end, and exclusions defined.
- [ ] Current state captured from at least three real executions.
- [ ] RACI table complete with approval limits.
- [ ] Every step has one action, one role, and an observable completion criterion.
- [ ] Every control names a risk, evidence, owner, and test.
- [ ] Exception decision table covers observed and foreseeable cases.
- [ ] Independent operator completed the dry run without author help.
- [ ] Dry-run questions and fixes logged.
- [ ] Owner, approver, version, effective date, and review date set.
- [ ] One canonical copy published and old versions retired.
- [ ] Review triggers defined for system, regulatory, and control changes.

## Related skills

- `operational-runbook-generation` for incident-time procedures that complement steady-state SOPs.
- `meeting-notes-action-items` for assigning and tracking SOP review actions.
- `technical-documentation-writing` for task-based writing style and verification sections.
- `security-control-mapping` when SOP controls must map to SOC 2 or ISO 27001 evidence.
