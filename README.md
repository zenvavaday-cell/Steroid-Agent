# Steroid-Agent

A collection of production-oriented agent skills for real work: financial analysis, software engineering, education, Linux operations, and the agent infrastructure that makes autonomy safe.

Every skill is a self-contained `SKILL.md` that follows the [Agent Skills](https://agentskills.io) format. Point an agent at one and it gets a workflow, concrete commands, validation gates, failure modes, and a completion checklist — not just a prompt.

## Repository layout

```text
Steroid-Agent/
├── Finance/          # Modeling, filings, reconciliation, risk, compliance
├── Engineering/      # Testing, review, debugging, migrations, refactoring
├── Education/        # Tutoring, assessment, curriculum, accessibility
├── Agentic/          # Orchestration, verification, sandboxing, state
├── Linux/            # Host operations: shell, systemd, network, storage, security
├── scripts/
│   └── validate_skills.py
├── LICENSE
└── README.md
```

Each skill lives in its own directory, and the directory name must match the `name` in the frontmatter:

```text
Finance/deterministic-financial-modeling/SKILL.md
```

## Skill catalog

### Finance — 15 skills

| Skill | What it does |
| --- | --- |
| [deterministic-financial-modeling](Finance/deterministic-financial-modeling/SKILL.md) | Builds DCF, comps, and sensitivity models with reproducible arithmetic and explicit assumptions. |
| [sandboxed-spreadsheet-verification](Finance/sandboxed-spreadsheet-verification/SKILL.md) | Audits spreadsheets in isolation: formula integrity, totals, links, and hidden cells. |
| [thematic-regulatory-compliance-diffing](Finance/thematic-regulatory-compliance-diffing/SKILL.md) | Diffs regulatory text across versions and maps changes to controls and disclosures. |
| [sec-filing-extraction](Finance/sec-filing-extraction/SKILL.md) | Extracts financial facts from SEC EDGAR filings, including XBRL and filing metadata. |
| [live-market-data-retrieval](Finance/live-market-data-retrieval/SKILL.md) | Fetches and validates quotes, fundamentals, corporate actions, and market calendars. |
| [automated-ledger-reconciliation](Finance/automated-ledger-reconciliation/SKILL.md) | Matches GL, bank, and subledger entries with tolerance rules and an exception queue. |
| [transaction-anomaly-flagging](Finance/transaction-anomaly-flagging/SKILL.md) | Flags duplicates, outliers, round-number patterns, and suspicious transaction sequences. |
| [portfolio-rebalancing-calculation](Finance/portfolio-rebalancing-calculation/SKILL.md) | Computes drift, whole-share trades, costs, tax impact, and post-trade weights. |
| [credit-risk-scoring-pipeline](Finance/credit-risk-scoring-pipeline/SKILL.md) | Builds and validates probability-of-default models with leakage and stability checks. |
| [anti-money-laundering-screening](Finance/anti-money-laundering-screening/SKILL.md) | Screens parties and transactions against sanctions, PEP, and adverse-media lists. |
| [earnings-call-sentiment-extraction](Finance/earnings-call-sentiment-extraction/SKILL.md) | Extracts guidance, tone, and segment sentiment from earnings call transcripts. |
| [invoice-to-po-matching](Finance/invoice-to-po-matching/SKILL.md) | Performs three-way matching across invoices, purchase orders, and receipts. |
| [covenant-breach-monitoring](Finance/covenant-breach-monitoring/SKILL.md) | Tracks loan covenant tests, headroom, and early-warning thresholds. |
| [automated-tax-document-parsing](Finance/automated-tax-document-parsing/SKILL.md) | Parses W-2 and 1099 documents and validates box-level arithmetic. |
| [liquidity-stress-testing](Finance/liquidity-stress-testing/SKILL.md) | Models cash-flow gaps under stress scenarios and ranks funding actions. |

### Engineering — 15 skills

| Skill | What it does |
| --- | --- |
| [test-driven-verification-loop](Engineering/test-driven-verification-loop/SKILL.md) | Drives changes through failing tests, minimal implementation, and regression checks. |
| [abstract-syntax-tree-navigation](Engineering/abstract-syntax-tree-navigation/SKILL.md) | Finds and rewrites code structurally instead of with brittle regular expressions. |
| [automated-pull-request-review](Engineering/automated-pull-request-review/SKILL.md) | Reviews diffs for correctness, risk, tests, and style with actionable comments. |
| [dependency-vulnerability-auditing](Engineering/dependency-vulnerability-auditing/SKILL.md) | Audits dependency trees, reachability, and upgrade paths for known vulnerabilities. |
| [ci-cd-failure-diagnosis](Engineering/ci-cd-failure-diagnosis/SKILL.md) | Diagnoses pipeline failures from logs, artifacts, and environment differences. |
| [git-bisect-regression-hunting](Engineering/git-bisect-regression-hunting/SKILL.md) | Bisects regressions with a reproducible test and verifies the introducing commit. |
| [static-code-analysis-remediation](Engineering/static-code-analysis-remediation/SKILL.md) | Triages analyzer findings and applies safe, verifiable fixes in priority order. |
| [database-schema-migration-generation](Engineering/database-schema-migration-generation/SKILL.md) | Generates reversible, lock-aware migrations with backfill and rollout plans. |
| [api-contract-validation](Engineering/api-contract-validation/SKILL.md) | Validates OpenAPI and consumer contracts against real requests and responses. |
| [container-log-diagnostics](Engineering/container-log-diagnostics/SKILL.md) | Triages container failures from logs, events, exit codes, and resource limits. |
| [automated-unit-test-generation](Engineering/automated-unit-test-generation/SKILL.md) | Generates meaningful unit tests with edge cases, mocks, and coverage targets. |
| [dead-code-elimination](Engineering/dead-code-elimination/SKILL.md) | Finds unreachable and unused code with evidence, then removes it safely. |
| [infrastructure-as-code-drift-detection](Engineering/infrastructure-as-code-drift-detection/SKILL.md) | Detects and reconciles drift between declared infrastructure and live state. |
| [semantic-codebase-search](Engineering/semantic-codebase-search/SKILL.md) | Searches code by meaning and structure, then verifies hits at the symbol level. |
| [automated-refactoring-execution](Engineering/automated-refactoring-execution/SKILL.md) | Plans and executes behavior-preserving refactors with tests at every step. |

### Education — 12 skills

| Skill | What it does |
| --- | --- |
| [socratic-tutoring-scaffolding](Education/socratic-tutoring-scaffolding/SKILL.md) | Guides learners with questions and graduated hints instead of giving answers. |
| [student-misconception-diagnosis](Education/student-misconception-diagnosis/SKILL.md) | Identifies the reasoning behind wrong answers and targets the underlying gap. |
| [rubric-aligned-essay-grading](Education/rubric-aligned-essay-grading/SKILL.md) | Grades essays against a rubric with cited evidence and consistent score bands. |
| [curriculum-grounded-quiz-generation](Education/curriculum-grounded-quiz-generation/SKILL.md) | Generates quizzes tied to curriculum sources, objectives, and difficulty levels. |
| [adaptive-spaced-repetition-scheduling](Education/adaptive-spaced-repetition-scheduling/SKILL.md) | Schedules review sessions from recall history and forgetting-curve estimates. |
| [differentiated-reading-level-adaptation](Education/differentiated-reading-level-adaptation/SKILL.md) | Rewrites material for different reading levels while preserving meaning and vocabulary goals. |
| [prerequisite-knowledge-mapping](Education/prerequisite-knowledge-mapping/SKILL.md) | Maps concept dependencies and finds gaps before a learner starts a unit. |
| [interactive-problem-hinting](Education/interactive-problem-hinting/SKILL.md) | Provides tiered hints that unblock a learner without revealing the full solution. |
| [syllabus-alignment-verification](Education/syllabus-alignment-verification/SKILL.md) | Checks that lessons, assessments, and materials cover the stated syllabus. |
| [automated-flashcard-synthesis](Education/automated-flashcard-synthesis/SKILL.md) | Turns source material into atomic, spaced-repetition-ready flashcards. |
| [accessibility-format-conversion](Education/accessibility-format-conversion/SKILL.md) | Converts content into accessible formats with alt text, structure, and validation. |
| [longitudinal-mastery-tracking](Education/longitudinal-mastery-tracking/SKILL.md) | Tracks mastery over time using evidence, decay, and confidence intervals. |

### Agentic infrastructure — 8 skills

| Skill | What it does |
| --- | --- |
| [schema-enforced-json-extraction](Agentic/schema-enforced-json-extraction/SKILL.md) | Extracts structured data with schema validation, repair, and rejection paths. |
| [bounded-multi-tool-orchestration](Agentic/bounded-multi-tool-orchestration/SKILL.md) | Plans and executes multi-tool workflows with budgets, dependencies, and stop conditions. |
| [source-grounded-citation-verification](Agentic/source-grounded-citation-verification/SKILL.md) | Verifies that every claim is supported by a cited source span before output. |
| [human-in-the-loop-escalation](Agentic/human-in-the-loop-escalation/SKILL.md) | Pauses at risk boundaries with evidence, alternatives, and safe resume after approval. |
| [deterministic-code-sandbox-execution](Agentic/deterministic-code-sandbox-execution/SKILL.md) | Runs untrusted code with resource limits, no network, and controlled artifacts. |
| [cross-system-data-normalization](Agentic/cross-system-data-normalization/SKILL.md) | Maps multiple sources into one canonical schema with lineage and conflict rules. |
| [stateful-workflow-checkpointing](Agentic/stateful-workflow-checkpointing/SKILL.md) | Persists workflow state so long-running tasks resume without repeating side effects. |
| [confidence-threshold-output-gating](Agentic/confidence-threshold-output-gating/SKILL.md) | Calibrates confidence and routes outputs to accept, review, abstain, or escalate. |

### Linux operations — 7 skills

| Skill | What it does |
| --- | --- |
| [dotfiles-manager](Linux/dotfiles-manager/SKILL.md) | Audits and organizes `~/.config`, validates syntax, and redacts exposed secrets. |
| [bash-script-architect](Linux/bash-script-architect/SKILL.md) | Writes production Bash with strict mode, argument parsing, logging, and dry runs. |
| [linux-systemd-service-management](Linux/linux-systemd-service-management/SKILL.md) | Creates, hardens, and debugs systemd services and timers. |
| [linux-network-diagnostics](Linux/linux-network-diagnostics/SKILL.md) | Diagnoses connectivity, DNS, routing, port, firewall, and packet-loss problems layer by layer. |
| [linux-storage-diagnostics](Linux/linux-storage-diagnostics/SKILL.md) | Diagnoses disk-full, inode, mount, I/O-latency, and failing-disk incidents. |
| [linux-performance-triage](Linux/linux-performance-triage/SKILL.md) | Triages CPU, memory, I/O, load, and cgroup contention with the USE method. |
| [linux-security-hardening](Linux/linux-security-hardening/SKILL.md) | Hardens accounts, sudo, SSH, permissions, services, firewall, and audit logging. |

## Anatomy of a skill

```markdown
---
name: skill-name
description: One sentence on what it does and when to use it.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: finance
---

# Skill Name

## Overview
## When to use
## Workflow
## Validation
## Gotchas
## Output contract
## Checklist
## Related skills
```

The `description` is the trigger: it should say both what the skill does and when an agent should load it. The body should contain commands, schemas, and thresholds that a capable model cannot guess on its own.

## Using a skill

1. Pick the skill directory for the task.
2. Copy or symlink it into your agent's skills folder:
   - Claude Code: `.claude/skills/<skill-name>/`
   - OpenCode: `.opencode/skills/<skill-name>/` or `~/.config/opencode/skills/<skill-name>/`
   - Other Agent Skills clients: follow their local skills path.
3. Keep the directory name identical to the frontmatter `name`.
4. Give the agent the task; the client loads the skill from its description.

Skills are composable. A financial model can call the spreadsheet verifier, the sandbox, and the citation checker; a workflow can pause for human approval and resume from a checkpoint.

## Validation

Run the repository validator before opening a pull request:

```bash
python3 scripts/validate_skills.py
```

It checks frontmatter, naming, description length, required sections, and the 500-line body limit. All 57 skills currently pass.

## Conventions

- One skill per directory; `SKILL.md` is the entry point.
- Directory name and frontmatter `name` must match.
- Names are lowercase kebab-case, at most 64 characters.
- Descriptions are single-line, 1–1024 characters, and state when to use the skill.
- Bodies stay under 500 lines and include concrete commands, validation gates, and gotchas.
- Reference related skills by directory name so a reader can navigate the repo.
- Changes that touch a skill should keep its checklist, output contract, and cross-references consistent.

## License

MIT. See [LICENSE](LICENSE).
