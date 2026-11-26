---
name: project-based-learning-design
description: Designs project-based units with driving questions, milestones, scaffolds, rubrics, and authentic assessment. Use for PBL curriculum and capstone courses.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: education
---

# Project-Based Learning Design

## Overview

A project-based unit earns the name only when the project is the vehicle for learning, not a reward after it. Students investigate a meaningful question, produce work for a real audience, and revise using critique. The design work is backward: outcomes, then evidence, then tasks and scaffolds.

This skill produces a project brief with a driving question, milestone calendar, scaffold plan, team structure, rubric, and assessment schedule. It is a planning tool, not a guarantee of implementation quality.

## When to use

- Building a new PBL unit or capstone course.
- Converting a traditional unit into sustained inquiry.
- Reviewing a project that consumes time without producing learning evidence.
- Designing an interdisciplinary or community-connected project.
- Preparing a project for exhibition or public presentation.
- Coaching a teacher whose projects lack structure or accountability.

Do not use for short enrichment activities, test-preparation drills, or projects where the product is purchased or completed mostly by adults.

## Workflow

### 1. Anchor the project in outcomes

Start from the standards and the course outcomes the unit must serve. For each outcome, write what students will know and be able to do, then name the evidence that would convince a skeptic.

```json
{
  "outcome": "LO-4",
  "statement": "Use field data to evaluate a local environmental policy",
  "evidence": ["data set with method notes", "written recommendation", "oral defense"],
  "standard": "HS-ESS3-4"
}
```

If an outcome cannot be assessed through the project, teach it separately and say so. Do not force every standard into the project.

### 2. Write a driving question that requires inquiry

A driving question is open, arguable, and answerable only by doing the work. Test it:

| Test | Pass | Fail |
| --- | --- | --- |
| Open | Multiple defensible answers | One lookup answer |
| Relevant | Connects to students' community or experience | Abstract only |
| Disciplinary | Requires the target knowledge and methods | Can be answered by opinion |
| Bounded | Doable with available time and sources | Requires a research institute |
| Productive | Supports subquestions and roles | One task, one person |

Example: "How should our city balance housing growth with flood risk?" A weak version is "What is a floodplain?" That is a research question, not a driving question.

Add a "need to know" list generated with students at the entry event. Revisit it at each milestone.

### 3. Define the authentic product and audience

Name the product, the audience, and the decision the audience could make. A public audience raises quality and changes the writing.

- Product: policy brief, prototype with test data, documentary, exhibit, service plan.
- Audience: city council, families, a community organization, a panel of practitioners.
- Decision or use: adopt, fund, revise, display, act.
- Exhibition format: 8-minute presentation plus 3 minutes of questions.

If there is no audience beyond the teacher, the project is a long assignment. Find a real one or simulate one with clear role cards.

### 4. Build the milestone calendar

Plan backward from the exhibition date. Each milestone must produce an artifact that can be reviewed.

| Milestone | Week | Student artifact | Checkpoint |
| --- | --- | --- | --- |
| Entry event and need-to-know | 1 | Question board, team contract | Teacher review |
| Research and source set | 2 | Annotated source log | Source quality check |
| Draft 1 | 4 | Draft section with data | Peer critique |
| Prototype or analysis | 5 | Tested model or data set | Expert or teacher check |
| Draft 2 | 6 | Revised product | Rubric self-score |
| Exhibition | 8 | Final product and defense | Panel and reflection |

Leave at least one full revision cycle. A project without revision teaches students to submit first drafts.

### 5. Design scaffolds and just-in-time instruction

List what students will likely not know how to do, then provide the minimum scaffold that lets them attempt it.

- Templates: source log, research plan, team agenda, critique form.
- Workshops: citing evidence, reading a data table, building a prototype, writing a policy recommendation.
- Exemplars: one strong and one weak sample with annotated differences.
- Reading and language supports: glossary, sentence frames, leveled sources.
- Process supports: milestone checklist, daily team log, role cards.

Plan the removal of scaffolds. A template used in week 2 should be optional by week 5.

### 6. Structure teams and individual accountability

Use teams of three or four. Define roles with real responsibilities, not labels.

| Role | Responsibility | Rotates |
| --- | --- | --- |
| Facilitator | Agenda, check-ins, keeps the team on the milestone | Weekly |
| Researcher | Source log, evidence quality, citations | Weekly |
| Builder or analyst | Prototype, data, or model maintenance | Weekly |
| Communicator | Draft integration, exhibition rehearsal | Weekly |

Require individual artifacts: a research log, a section draft, a reflection, and an oral defense question answered alone. Group grades should not exceed a small share of the total, and peer assessment should be evidence-based.

### 7. Write the rubric before launch

Use three or four criteria, each with three or four observable levels. Separate product quality, content understanding, process, and collaboration.

```json
{
  "criteria": [
    {"id": "evidence", "weight": 0.30, "levels": {"4": "Selects and reconciles multiple credible sources; addresses conflicting data", "3": "Uses relevant credible sources with minor gaps", "2": "Uses limited or uneven sources", "1": "Claims lack sources"}},
    {"id": "reasoning", "weight": 0.30, "levels": {"4": "Explains tradeoffs and justifies a recommendation against alternatives", "3": "Explains reasoning with some tradeoffs", "2": "Describes without evaluating", "1": "Unsupported opinion"}},
    {"id": "product", "weight": 0.25, "levels": {"4": "Audience-ready, precise, and usable", "3": "Clear and mostly polished", "2": "Understandable but uneven", "1": "Not usable by the audience"}},
    {"id": "collaboration", "weight": 0.15, "levels": {"4": "Builds on others, manages conflict, meets commitments", "3": "Contributes and meets most commitments", "2": "Inconsistent contribution", "1": "Does not contribute"}}
  ]
}
```

Share the rubric at launch and use it for peer critique. Students should never see the criteria for the first time at grading.

### 8. Plan critique, reflection, and revision

Schedule at least two critique rounds using a protocol:

1. Presenter states the goal and asks a focused question.
2. Peers describe what they see before judging.
3. Peers give warm and cool feedback against the rubric.
4. Presenter records two changes and one question.

Add short reflections at each milestone: what is working, what is blocking, what the team will change. End with an individual reflection on content learning and process.

### 9. Run a logistics and risk review

Check materials, permissions, transport, technology, safety, accessibility, and calendar conflicts. Name an owner for each. Confirm that the exhibition date does not collide with testing windows or holidays.

## Validation

| Gate | Pass criterion | Fail action |
| --- | --- | --- |
| Outcome alignment | Every target outcome has a project artifact and a rubric criterion | Add evidence or remove the outcome claim |
| Driving question | Passes all five tests and yields subquestions | Rewrite before launch |
| Audience | Named audience and use for the product | Recruit or simulate with role cards |
| Revision | At least two critique rounds and one full revision | Shorten scope to make room |
| Rubric | Observable levels, shared at launch | Rewrite vague descriptors |
| Individual accountability | Each student produces individual evidence | Add logs, sections, or defense |
| Scaffold fade | Each scaffold has a removal point | Schedule the fade |
| Feasibility | Milestones fit the calendar with buffer | Cut a product or extend time |
| Accessibility | Materials and tasks have accessible routes | Add alternatives before launch |
| Safety and permissions | Risks identified with owners | Resolve before students start |

If the calendar cannot fit two critique rounds, reduce the number of products rather than removing revision.

## Gotchas

- The dessert project: teaching first, then adding a poster. The project must carry the learning.
- A driving question with one Googleable answer. Rewrite it as a decision or design problem.
- Too many products. One strong product with a defense beats five shallow ones.
- Group grades that hide non-participation. Require individual artifacts and evidence-based peer review.
- Rubrics written after the project. Criteria must shape the work from day one.
- Critique that is only praise. Use a protocol that separates observation from judgment.
- Scaffolds that never fade. Students become dependent on templates.
- Technology as decoration. Every tool must serve inquiry, production, or feedback.
- No audience. Students optimize for the teacher's preferences.
- Scope creep after launch. Freeze the outcomes and cut optional activities.
- Ignoring prerequisite skills. Diagnostic checks in week 1 prevent week 5 failure.
- Exhibition without rehearsal. Practice the presentation and the question handoff.

## Output contract

```json
{
  "title": "Floodplain Housing Project",
  "course": "Environmental Science 11",
  "duration_weeks": 8,
  "outcomes": [{"id": "LO-4", "evidence": ["data set", "policy brief", "defense"]}],
  "driving_question": "How should our city balance housing growth with flood risk?",
  "subquestions": ["Which areas are exposed?", "Who bears the cost?", "What does the evidence favor?"],
  "entry_event": "City planner presents three proposed sites",
  "product": {"format": "policy brief plus 8-minute defense", "audience": "city council subcommittee", "use": "inform a zoning recommendation"},
  "milestones": [{"week": 2, "artifact": "annotated source log", "checkpoint": "source quality review"}],
  "scaffolds": [{"type": "template", "purpose": "source evaluation", "fade_week": 5}],
  "teams": {"size": 4, "roles": ["facilitator", "researcher", "analyst", "communicator"], "rotation": "weekly"},
  "individual_accountability": ["research log", "section draft", "oral defense", "reflection"],
  "rubric": {"criteria": ["evidence", "reasoning", "product", "collaboration"], "levels": 4},
  "critique_rounds": 2,
  "exhibition": {"date": "2027-03-12", "format": "panel and gallery walk"},
  "risks": [{"risk": "transport to site", "owner": "teacher", "mitigation": "virtual tour backup"}]
}
```

## Checklist

- [ ] Outcomes named with project evidence.
- [ ] Driving question passes the five tests.
- [ ] Student need-to-know list planned for the entry event.
- [ ] Authentic product and audience defined.
- [ ] Milestone calendar built backward with buffer.
- [ ] Scaffolds listed with a fade point.
- [ ] Team roles and rotation defined.
- [ ] Individual accountability artifacts required.
- [ ] Rubric written and shared before launch.
- [ ] Two critique rounds and a revision cycle scheduled.
- [ ] Logistics, safety, and accessibility reviewed.
- [ ] Exhibition rehearsed and assessed.

## Related skills

- `syllabus-alignment-verification` for checking that projects and outcomes line up across a course.
- `rubric-aligned-essay-grading` for scoring written products consistently.
- `formative-assessment-design` for milestone checks that inform the next workshop.
- `student-feedback-synthesis` for turning exhibition feedback into the next iteration.
