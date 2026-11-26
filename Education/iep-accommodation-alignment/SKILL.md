---
name: iep-accommodation-alignment
description: Aligns lessons, materials, and assessments with IEP or 504 accommodations and records evidence of use. Use for special-education planning and compliance reviews.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: education
---

# IEP Accommodation Alignment

## Overview

An IEP or 504 plan changes a student's experience only when every adult in the room knows which support applies, when it applies, and how its use is documented. Alignment means mapping each required accommodation to concrete lesson moments, materials, and assessment conditions, then proving it was delivered.

This skill produces an accommodation register, a delivery matrix, an evidence log design, and an escalation list. It does not decide eligibility or change a plan; those belong to the IEP team or 504 committee. Treat all records as confidential student data.

## When to use

- Planning a unit for a class that includes students with IEPs or 504 plans.
- Reviewing whether lesson materials and assessments permit required accommodations.
- Preparing evidence for an annual review, monitoring visit, or compliance audit.
- Onboarding a co-teacher, substitute, or paraprofessional.
- Investigating a complaint that an accommodation was not provided.
- Checking that a proposed activity does not conflict with an assessment accommodation.

Do not use to draft, amend, or terminate a plan, to determine eligibility, or to substitute for legal review by district special-education staff.

## Workflow

### 1. Build the accommodation register from current plans

Use the most recent signed version. Record the plan type, review date, and case manager. Work from the official document, not last year's summary.

```json
{
  "student_ref": "S-1042",
  "plan_type": "IEP",
  "review_due": "2027-03-14",
  "case_manager": "role:resource-teacher",
  "present_levels": {"reading": "grade 5.2", "written_expression": "grade 3.8"},
  "goals": [{"id": "G-1", "area": "written expression", "criterion": "3 of 4 traits at 3+"}]
}
```

Use a pseudonymous reference in shared working documents. Keep the name-to-reference key in the secured system of record.

### 2. Separate the three categories

| Category | What changes | Example | Who approves |
| --- | --- | --- | --- |
| Accommodation | How the student accesses or demonstrates learning | Extended time, text-to-speech, preferential seating | IEP team or 504 committee |
| Modification | What the student is expected to learn or the standard applied | Reduced essay body paragraphs, below-grade reading text | IEP team |
| Service | Direct support delivered by qualified staff | Speech-language therapy, resource room, counseling | IEP team |

A classroom teacher may implement an accommodation but may not invent, waive, or reclassify one. If a support changes the standard, stop and refer it to the team.

### 3. Map each accommodation to lesson components

For every accommodation, name the component it touches: instruction, materials, environment, assessment, behavior, communication, or health. Then name the delivery point.

| Accommodation | Component | Delivery point | Owner | Evidence |
| --- | --- | --- | --- | --- |
| Read directions aloud | Instruction and assessment | Start of each task | General ed teacher | Log entry plus annotated script |
| Graphic organizer | Materials | Argument essay prewrite | General ed teacher | Copy in portfolio |
| Extended time (1.5x) | Assessment | Unit test, separate room | Test coordinator | Testing log |
| Movement breaks | Environment | Every 20 minutes | Paraprofessional | Break log |

### 4. Detect conflicts before the lesson runs

Check each pairing for a conflict that would invalidate the task or the accommodation:

- Read-aloud on a reading comprehension or fluency measure changes what is measured. Confirm the plan's assessment-specific language and the test administration manual.
- A scribe or speech-to-text on a writing assessment may conflict with a written-expression goal. Implement the accommodation and collect separate goal evidence.
- Extended time with a same-day field trip or back-to-back exam creates a scheduling failure. Reserve the room and staff in advance.
- Noise-cancelling headphones may conflict with a listening comprehension task or a safety drill.
- Frequent breaks may conflict with a timed lab practical. Ask the case manager for the approved variation.

Record each conflict with the resolution, owner, and date. Never resolve a conflict by silently dropping the accommodation.

### 5. Produce the delivery matrix

Build one matrix per class section and week. It should be usable by a substitute in under two minutes.

```markdown
| Student ref | Mon | Tue | Wed | Thu | Fri | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| S-1042 | RA, ET | GO | RA | ET, MB | RA | ET applies to quiz only |
```

Legend: RA = read aloud, ET = extended time, GO = graphic organizer, MB = movement break. Keep the legend and a need-to-know summary with the matrix, not the full plan.

### 6. Record evidence of use

Log at the level of the accommodation, not the student's personality. Required fields:

- Date, class, and activity.
- Accommodation ID and the form delivered.
- Start and end time, or the task it covered.
- Whether the student used it, declined it, or it was unavailable.
- Staff initials and any adaptation.

```json
{"date": "2026-11-10", "activity": "unit 3 quiz", "accommodation": "A-4", "delivered": "1.5x time in room 210", "student_use": "used", "staff": "T. Nguyen", "note": "finished in 52 of 60 minutes"}
```

Record a student's refusal neutrally and notify the case manager. Do not argue with the student in the moment.

### 7. Monitor goals and escalate gaps

At least monthly, compare evidence logs and progress data against each goal. Escalate when:

- An accommodation was missed more than once in a grading period.
- A service minute was not delivered.
- The student's performance suggests the plan no longer fits.
- A new need appears (assistive technology failure, hospital stay, medication change).

Send a brief, factual referral to the case manager. Do not email diagnoses or full plan contents outside the approved system.

### 8. Brief staff with need-to-know summaries

Give each adult only what their role requires. A substitute needs the delivery matrix and emergency health steps, not present levels or disability labels. A test coordinator needs assessment accommodations and the exact conditions.

## Validation

Run these gates before the unit goes live and again at the end of each grading period.

| Gate | Pass criterion | Fail action |
| --- | --- | --- |
| Register currency | Every active plan has a signed version dated within the review cycle | Obtain the current plan before teaching |
| Coverage | 100% of accommodations mapped to a delivery point and owner | Add missing mappings |
| Category integrity | No modification or service listed as a classroom accommodation | Refer to the team |
| Conflict review | Every assessment accommodation checked against the construct | Document resolution or escalation |
| Evidence completeness | At least 95% of scheduled deliveries have a log entry | Audit the gap and retrain |
| Confidentiality | No names, plan images, or disability details in unsecured locations | Remove and report |
| Student voice | Student confirms, in an age-appropriate way, that supports are usable | Adjust delivery, not the plan |
| Review horizon | Any plan review due within 30 days has an owner and a calendar entry | Assign before closing |

A failed confidentiality gate is an incident, not a documentation fix. Follow district breach procedures.

## Gotchas

- Treating an accommodation as a favor or reward. It is an entitlement; deliver it without conditions.
- Confusing accommodation with modification. Changing the standard requires a team decision, even when it feels helpful.
- Applying read-aloud to a reading test and then reporting the score as grade-level reading. The construct changed.
- Writing "extra time as needed" in the log. Name the multiplier, task, and setting.
- Letting a paraprofessional complete the work. Support access, do not produce the product.
- Storing plan PDFs in a shared drive or substitute folder with full names. Use the register and a summary.
- Logging opinions ("student was lazy") instead of observable facts. Log delivery and student response.
- Forgetting health accommodations such as water, restroom, medication timing, or seizure protocol. Put them in the same matrix.
- Assuming assistive technology works. Test the device and the login before the lesson.
- Letting a 504 plan expire without review. Track review dates in the same calendar as IEPs.
- Implementing a new support and calling it an accommodation. Pilot supports belong in data collection, then team review.
- Discussing the plan in front of peers or in a whole-staff email. Share only with staff who need to know.

## Output contract

```json
{
  "student_ref": "S-1042",
  "plan_type": "IEP",
  "plan_date": "2026-03-14",
  "review_due": "2027-03-14",
  "accommodations": [
    {
      "id": "A-4",
      "statement": "Extended time, 1.5x, on tests and timed writing",
      "category": "accommodation",
      "components": ["assessment"],
      "delivery_point": "unit tests, room 210",
      "owner": "test coordinator",
      "assessment_implications": "does not apply to the reading fluency probe",
      "evidence_method": "testing log with start and end time"
    }
  ],
  "modifications": [],
  "services": [{"type": "resource room", "minutes": 150, "frequency": "weekly"}],
  "conflicts": [
    {"pair": "A-4 with same-day lab practical", "resolution": "schedule practical on Thursday", "owner": "science teacher", "date": "2026-11-06"}
  ],
  "evidence_fields": ["date", "activity", "accommodation_id", "delivery_form", "student_use", "staff", "note"],
  "escalations": [{"reason": "two missed read-aloud sessions", "to": "case manager", "date": "2026-11-12"}],
  "confidentiality": {"storage": "secured IEP system", "shared_copy": "need-to-know summary only"}
}
```

## Checklist

- [ ] Current signed plan obtained and review date recorded.
- [ ] Accommodations, modifications, and services separated.
- [ ] Each accommodation mapped to component, delivery point, and owner.
- [ ] Assessment conflicts checked against the construct being measured.
- [ ] Weekly delivery matrix produced and legible to a substitute.
- [ ] Evidence log defined with observable fields.
- [ ] Student use or refusal recorded neutrally.
- [ ] Goal progress reviewed against evidence at least monthly.
- [ ] Missed deliveries escalated to the case manager.
- [ ] Need-to-know summaries used instead of full plan copies.
- [ ] Confidentiality gate passed with no unsecured identifiers.
- [ ] Review dates and owners entered in the compliance calendar.

## Related skills

- `accessibility-format-conversion` for producing accessible versions of the same materials.
- `differentiated-reading-level-adaptation` for text-level adjustments that do not alter the standard without team approval.
- `rubric-aligned-essay-grading` for applying accommodations consistently during written assessment.
- `syllabus-alignment-verification` for checking that course requirements and accommodations coexist.
