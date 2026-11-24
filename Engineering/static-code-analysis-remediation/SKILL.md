---
name: static-code-analysis-remediation
description: Runs and merges static analysis results, triages findings by exploitability and reachability, applies safe autofixes, verifies with tests, and manages suppressions with owners and expiry dates. Use for SAST remediation, lint cleanup, security findings, and code quality gates.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: engineering
---

# Static Code Analysis Remediation

## Overview

Static analysis produces candidates, not verdicts. The goal is to move from a raw SARIF file to a small set of real defects with fixes, and to prevent the same class of defect from returning. Autofix is useful for mechanical rules and dangerous for semantic ones.

## When to use

- Cleaning up a backlog of lint or SAST findings.
- Enforcing a quality gate in CI.
- Investigating a security scanner report.
- Introducing a new analyzer without drowning the team.

## Workflow

### 1. Run the analyzers

```bash
# Python
ruff check --output-format=sarif > ruff.sarif
bandit -r src -f sarif -o bandit.sarif

# JavaScript/TypeScript
eslint . --format=@microsoft/eslint-formatter-sarif --output-file eslint.sarif

# Multi-language SAST
semgrep scan --config auto --sarif --output semgrep.sarif

# Go
gosec -fmt sarif -out gosec.sarif ./...

# Java
spotbugs -sarif -output spotbugs.sarif target/classes
```

Record tool versions and rule sets. A finding is reproducible only against the same configuration.

### 2. Merge and deduplicate

Different tools report the same defect with different IDs. Deduplicate by file, line range, rule category, and message similarity. Keep the tool and rule ID for traceability.

```python
import json

def load_findings(path):
    data = json.load(open(path))
    for run in data.get("runs", []):
        for result in run.get("results", []):
            loc = result["locations"][0]["physicalLocation"]
            yield {
                "file": loc["artifactLocation"]["uri"],
                "line": loc["region"].get("startLine"),
                "rule": result["ruleId"],
                "message": result["message"]["text"],
                "level": result.get("level", "warning"),
            }
```

### 3. Triage

For each finding, ask:

- Is the code reachable from an untrusted input?
- Is the sink dangerous (SQL, shell, deserialization, file path, template)?
- Is there an existing control (parameterization, allowlist, sandbox)?
- Is this test, generated, or vendored code?
- Is the rule correct for this codebase?

Priority:

| Priority | Criteria |
| --- | --- |
| P0 | Reachable injection, auth bypass, secret exposure, RCE |
| P1 | Reachable high-impact defect with no mitigating control |
| P2 | Real defect in a non-critical path |
| P3 | Maintainability or style |
| Ignore | False positive, generated code, or accepted risk |

### 4. Fix

Prefer a root-cause fix over a suppression. For mechanical rules, autofix and review the diff:

```bash
ruff check --fix src/
eslint . --fix
semgrep scan --config auto --autofix
```

Autofix is unsafe when it changes control flow, error handling, or API contracts. Review every hunk. Run tests after each batch, not at the end of a 500-file change.

### 5. Verify

- Re-run the analyzer; the finding must disappear.
- Run the full test suite.
- Run type checks and the formatter.
- Add a regression test for security-relevant fixes.
- Check that the fix did not introduce a new finding.

### 6. Manage suppressions

Every suppression needs:

```json
{
  "rule": "python.lang.security.audit.subprocess-shell-true",
  "file": "src/tools/legacy.py",
  "line": 42,
  "reason": "Input is a constant allowlisted command; no user data reaches the shell",
  "owner": "platform-team",
  "expires": "2027-03-31",
  "ticket": "SEC-441"
}
```

No permanent blanket suppressions. No suppressing an entire directory to make CI green. Expired suppressions fail the build.

### 7. Set the gate

Adopt a baseline for existing debt, then fail on new findings above the agreed severity. This lets the team improve without blocking every build on legacy issues.

## Gotchas

- Autofix can change semantics, especially around null handling, exceptions, and async code.
- A finding in generated code is usually not actionable; exclude it by path.
- Baseline files can hide new findings if the fingerprint changes with unrelated edits.
- Multiple analyzers inflate counts through duplicates. Deduplicate before reporting.
- Severity labels are not comparable across tools. Normalize to your own priority.
- Taint analysis needs a source and a sink. A dangerous function with constant input is not a vulnerability.
- Suppression comments can be stale after a refactor. Tie them to a ticket and expiry.
- Secrets scanners report test fixtures. Verify before rotating or deleting.
- A clean scan is not proof of security. It means the configured rules found nothing.

## Output contract

```markdown
## Scan
Tools: ...
Rulesets: ...
Findings: <raw> -> <deduplicated>

## Triage
| Priority | Count | Examples |
| --- | --- | --- |

## Fixes
| Finding | Fix | Verification |
| --- | --- | --- |

## Suppressions
| Rule | Location | Reason | Owner | Expires |
| --- | --- | --- | --- | --- |

## Gate
<baseline and failure threshold>

## Residual risk
<unfixed findings and why>
```

## Checklist

- [ ] Analyzer versions and configs recorded.
- [ ] Results merged and deduplicated.
- [ ] Findings triaged by reachability and impact.
- [ ] Autofixes reviewed, not blindly applied.
- [ ] Tests and type checks pass after fixes.
- [ ] Analyzer re-run confirms resolution.
- [ ] Suppressions have reason, owner, and expiry.
- [ ] CI gate blocks new high-severity findings.

## Related skills

- `automated-pull-request-review` for reviewing the remediation diff.
- `abstract-syntax-tree-navigation` for precise structural fixes.
- `dependency-vulnerability-auditing` for dependency-sourced findings.
