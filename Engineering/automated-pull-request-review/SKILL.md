---
name: automated-pull-request-review
description: Reviews pull request diffs with risk-based triage, inline findings, severity labels, and explicit approve or request-changes decisions, covering correctness, security, tests, performance, and compatibility. Use for automated code review, pre-merge gates, and consistent reviewer feedback.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: engineering
---

# Automated Pull Request Review

## Overview

A good review answers three questions: does this change do what it claims, is it safe to merge, and what specifically must change before it is? Review the diff and its context, not the entire repository. Rank findings by severity and avoid burying a security issue under twenty style nits.

## When to use

- Reviewing a pull request before merge.
- Triaging a large or risky change.
- Producing consistent automated review comments.
- Auditing a change for security or compatibility.

## Workflow

### 1. Gather context

```bash
gh pr view 123 --json title,body,author,baseRefName,headRefName,files,additions,deletions,statusCheckRollup
gh pr diff 123 --patch
gh pr checks 123
```

Identify:

- Linked issue and stated intent.
- Changed files and size.
- CI status and failing checks.
- Base branch and merge strategy.
- Whether the branch is up to date.

### 2. Triage risk

| Signal | Risk |
| --- | --- |
| Auth, payments, crypto, permissions | High |
| Database migration or schema change | High |
| Public API or contract change | High |
| Dependency or lockfile change | Medium–High |
| Concurrency, caching, retries | High |
| Large diff (>400 lines) | Review fatigue risk |
| Docs, comments, formatting only | Low |
| Generated code or lockfiles | Skip line review; verify source |

Set review depth accordingly. A 2,000-line generated diff does not need line-by-line comments.

### 3. Check scope and intent

- Does the diff match the description?
- Are there unrelated changes?
- Are tests included and meaningful?
- Are migrations reversible and backward compatible?
- Are feature flags or config changes documented?
- Are secrets or credentials present?

### 4. Review the diff hunk by hunk

For each changed hunk, read surrounding context, not only the added lines.

Correctness:

- Off-by-one, null/empty, integer overflow, timezone, encoding.
- Error paths and resource cleanup.
- Concurrency and transaction boundaries.
- Idempotency for retried operations.

Security:

- Injection (SQL, shell, template, deserialization).
- Authorization checks on every new path.
- Input validation and output encoding.
- Secret handling and logging of sensitive data.
- Dependency provenance.

Tests:

- New behavior covered.
- Regression test fails on the old code.
- Tests are deterministic and isolated.
- No tests deleted or skipped to make CI pass.

Performance:

- N+1 queries, unbounded loops, large allocations.
- Missing indexes for new query patterns.
- Caching invalidation.

Compatibility:

- API schema changes and versioning.
- Database migration order and rollback.
- Config and environment defaults.

### 5. Write findings

Every finding includes file, line, severity, the problem, why it matters, and a concrete fix.

```markdown
**[HIGH] `src/auth/session.py:88` — session token logged**
The new debug line logs the full session token. Anyone with log access can impersonate users.
Fix: log only the token identifier, for example `token_id=...`, or remove the line.
```

Severity:

| Level | Meaning |
| --- | --- |
| BLOCKER | Data loss, security breach, outage risk |
| HIGH | Correctness bug or missing authorization |
| MEDIUM | Edge case, performance, maintainability risk |
| LOW | Style, naming, minor clarity |
| NIT | Optional preference; label as non-blocking |

Do not mix blocking and non-blocking feedback without labels.

### 6. Decide

- **Approve**: no blockers and findings are optional.
- **Request changes**: any blocker or high-severity issue.
- **Comment**: questions remain, but no decision yet.

State the decision and the exact conditions for approval.

## Gotchas

- GitHub review comments attach to lines in the diff. A comment on an unchanged line may fail or appear in the wrong place.
- Generated files, lockfiles, and snapshots should be verified by regenerating, not by reading every line.
- A green CI run does not prove correctness; tests may not cover the change.
- Deleting or weakening a test to pass CI is a blocker.
- Force pushes after review can invalidate prior approvals. Re-check the head SHA.
- Large PRs hide issues. Ask for a split when the change is separable.
- Style nits can drown out real findings. Lead with severity.
- Author intent matters. If the description is unclear, ask before assuming a bug.
- Automated comments can be wrong. Cite evidence and avoid confident claims without reading context.

## Output contract

```markdown
## Review summary
<2-3 sentences: what the change does and the merge decision>

## Decision
APPROVE | REQUEST_CHANGES | COMMENT

## Findings
| Severity | File:Line | Finding | Required action |
| --- | --- | --- | --- |

## Tests and CI
<status and gaps>

## Security and compatibility notes
<...>

## Conditions for approval
- ...
```

## Checklist

- [ ] PR intent and linked issue read.
- [ ] Risk tier assigned.
- [ ] CI status checked.
- [ ] Scope and unrelated changes checked.
- [ ] Security-sensitive paths reviewed.
- [ ] Tests reviewed for meaning, not only presence.
- [ ] Findings have severity, evidence, and fix.
- [ ] Decision and conditions stated.

## Related skills

- `static-code-analysis-remediation` for tool-generated findings.
- `dependency-vulnerability-auditing` for dependency changes.
- `test-driven-verification-loop` for the test evidence standard.
