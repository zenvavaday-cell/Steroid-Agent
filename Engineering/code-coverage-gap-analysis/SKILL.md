---
name: code-coverage-gap-analysis
description: Finds untested behavior and risk-weighted coverage gaps instead of chasing a single percentage. Use for test planning and release readiness.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: engineering
---

# Code Coverage Gap Analysis

## Overview

A coverage percentage is an aggregate that hides where the risk is. A service at 85% can have no tests for its refund path, its retry logic, or its authorization checks. The useful output is a ranked list of untested behavior with evidence, not a number to maximize.

Measure branches, diff coverage, and risk. Then write tests for the gaps that can hurt users.

## When to use

- Planning tests for a release with limited time.
- A pull request lowers coverage and the gate needs a decision.
- A module has high coverage but a history of escaped defects.
- Coverage excludes or ignores have accumulated without review.
- Onboarding onto a codebase and deciding where tests matter most.
- Preparing release-readiness evidence for a critical service.

Do not use to justify a coverage target for its own sake, or to compare teams whose codebases have different risk profiles.

## Workflow

### 1. Produce machine-readable coverage with branch data

```bash
pytest --cov=src --cov-branch --cov-report=xml:coverage.xml --cov-report=json:coverage.json
npx jest --coverage --coverageReporters=json-summary --coverageReporters=lcov
go test ./... -covermode=atomic -coverprofile=cover.out
cargo llvm-cov --workspace --lcov --output-path lcov.info
mvn test jacoco:report
dotnet test --collect:"XPlat Code Coverage" --results-directory TestResults
```

Prefer branch mode over line mode. Line-only instruments miss untested conditions in `if`, `switch`, and short-circuit expressions.

### 2. Normalize and merge by package

Map every file to a repository-relative path and a package. Merge shard or worker outputs before computing totals:

```bash
coverage combine
nyc merge .nyc_output coverage.json
lcov -a shard-1.info -a shard-2.info -o merged.info
```

Exclude test code, vendored dependencies, generated clients, and migration boilerplate consistently in one config file. The same exclusions must apply locally and in CI, or the numbers will not reconcile.

### 3. Compute diff coverage against the merge base

```bash
git fetch origin main
diff-cover coverage.xml --compare-branch=origin/main --fail-under=80 \
  --html-report diff-coverage.html
```

Diff coverage answers the question that matters for review: are the new and changed lines tested? Use the merge base, not the current tip of main, or unrelated commits will pollute the denominator. Set an example gate of 80% line and 70% branch on changed code.

### 4. Enumerate behavioral gaps, not just red lines

For each uncovered region, name the behavior that is missing:

- Error and exception branches.
- Empty, null, zero, negative, and maximum inputs.
- Authorization deny paths and expired sessions.
- Retry, timeout, and circuit-breaker branches.
- Feature flag on and off.
- Partial failure in a batch or multi-step transaction.
- Idempotency and duplicate delivery.
- Cleanup and rollback paths.

A branch that only runs on process shutdown needs a different test strategy than an arithmetic boundary. Record the intended test type: unit, integration, contract, or chaos.

### 5. Risk-weight the gaps

Rank by expected harm, not by line count:

```text
risk = criticality (1-5)
     x change_frequency (commits in 90 days, capped at 10)
     x complexity (cyclomatic complexity, capped at 20)
     x (1 - branch_coverage)
```

Example: a payments refund handler with criticality 5, 8 changes, complexity 12, and 40% branch coverage scores 288. A formatting utility with criticality 1, 1 change, complexity 2, and 0% coverage scores 2. Test the refund handler first even though both are uncovered.

Cross-check with defect history: files that appeared in the last 10 production incidents get a multiplier and a note.

### 6. Audit ignores and exclusions

```bash
rg -n "pragma: no cover|istanbul ignore|coverage:ignore|ExcludeFromCodeCoverage|@Generated" src
```

Every exclusion needs a reason, an owner, and a review date. Blanket module excludes, `# pragma: no cover` on a whole function, and coverage config that omits an entire package are red flags. Removing an exclusion is often more valuable than adding a test.

Check the inverse too: files with zero executable lines, deleted tests, and skipped tests (`pytest.mark.skip`, `test.skip`, `t.Skip`) all distort the total.

### 7. Produce the test plan and ratchet the gate

For each of the top gaps, write a row: behavior, input, expected result, test level, file and line, owner. Order by risk score. Estimate effort in hours and stop when the release budget is exhausted; do not spread effort evenly.

Gate policy example:

- Diff coverage at or above 80% lines and 70% branches.
- Global coverage must not drop by more than 0.5 percentage points.
- Critical packages at or above 85% branch coverage.
- New ignore directives require a justification comment and reviewer approval.
- Ratchet the threshold upward after each release, never downward.

## Validation

- The coverage file parses and its totals match the CI summary within 0.1 points.
- Branch data is present; a line-only report fails the check for a branch gate.
- Diff coverage uses the merge base and lists the changed files it measured.
- Three covered lines are spot-checked to confirm they contain real assertions.
- Three uncovered lines are spot-checked to confirm they are reachable, not dead code.
- Every exclusion has a reason and owner.
- The test plan covers each gap with an input and an expected result.
- The gate fails on a test commit that adds an uncovered error branch.

## Gotchas

- Line coverage can be 100% while every `else` branch is untested. Gate on branches for decision logic.
- Executed is not asserted. A test that calls a function and checks nothing still marks lines covered.
- Coverage collected from a subset of tests understates the suite. Merge all shards before judging.
- Parallel workers can overwrite the same coverage file. Use per-worker files and combine.
- TypeScript source maps can attribute coverage to the wrong original line. Verify one known file.
- Async callbacks that run after the test ends may be attributed to a later test or dropped.
- Subprocesses and workers are not instrumented by default; Python needs `COVERAGE_PROCESS_START`.
- `--cov=src` may include test helpers or generated files. Check the file list, not just the total.
- Deleting a well-covered module can raise the percentage while removing tested behavior.
- A skipped or xfailed test still counts in the suite but contributes no coverage. Track skips separately.
- Dead code is counted as uncovered forever. Remove it instead of writing tests for it.
- Excluding a file from coverage is a policy decision that should be visible in review, not a config detail.

## Output contract

```markdown
## Scope
Commit: <sha> | Packages: checkout, payments | Report: coverage.xml
Line: 84.2% | Branch: 71.6% | Functions: 88.0% | Diff: 76.4% (gate 80%)

## Ranked gaps
| Rank | Location | Behavior | Branch cov | Risk | Test level | Owner |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | payments/refund.py:88 | partial refund failure | 0% | 288 | integration | @team-payments |
| 2 | checkout/coupon.py:41 | expired coupon | 25% | 96 | unit | @team-checkout |

## Exclusions
| Path | Directive | Reason | Owner | Review |
| --- | --- | --- | --- | --- |
| payments/legacy.py | pragma: no cover | scheduled removal | @team-payments | 2026-03-01 |

## Test plan
| Behavior | Input | Expected | File |
| --- | --- | --- | --- |
| refund fails midway | provider 500 on second call | full rollback, no partial ledger row | tests/test_refund.py |

## Gate
Diff coverage: 76.4% (fail, threshold 80%) | Global delta: -0.3 pp (pass)
Action: add two tests before merge, or request an approved exception with a ticket.
```

## Checklist

- [ ] Branch-aware coverage collected with the CI command.
- [ ] Shards merged and paths normalized.
- [ ] Test, generated, and vendored code excluded consistently.
- [ ] Diff coverage computed against the merge base.
- [ ] Gaps translated into named behaviors.
- [ ] Gaps risk-weighted with criticality, churn, complexity, and coverage.
- [ ] Defect history cross-checked.
- [ ] Ignores and skips audited with owners.
- [ ] Test plan written with inputs and expected results.
- [ ] Gate tested against a deliberately uncovered branch.
- [ ] Threshold ratcheted, not lowered.

## Related skills

- `mutation-testing-analysis` for proving that the new tests actually detect faults.
- `test-driven-verification-loop` for writing each gap test red first.
- `automated-unit-test-generation` for bulk coverage of low-risk utility code.
- `code-ownership-mapping` for routing each gap to the responsible team.
