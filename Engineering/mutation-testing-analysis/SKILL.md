---
name: mutation-testing-analysis
description: Measures test-suite strength with mutants, equivalent-mutant review, and prioritized surviving mutations. Use for assessing test quality beyond coverage.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: engineering
---

# Mutation Testing Analysis

## Overview

Mutation testing seeds small faults into production code and checks whether the test suite notices. A mutant that survives exposes a missing or weak assertion; a mutant that is killed proves the suite can detect that class of fault. Coverage only shows execution, while mutation score shows detection.

The expensive part is not running mutants, it is triaging survivors. Budget for review time, not just compute.

## When to use

- Coverage is high but escaped defects keep appearing.
- A critical module needs evidence that its tests assert behavior.
- Reviewing a pull request that adds tests without changing production logic.
- Setting a quality gate for a new service or package.
- Deciding where to invest test effort across many packages.

Do not use as a per-commit gate on a large legacy codebase; runtime and equivalent mutants make it noisy until the suite is strong.

## Workflow

### 1. Establish a green baseline and scope

```bash
git status --porcelain
pytest -q
```

A red or flaky baseline produces meaningless kills. Fix that first.

Scope by risk: changed files for pull requests, critical packages for scheduled runs, the whole repo only for a quarterly audit. Record the exact commit, test command, and tool version.

### 2. Select a tool and configure it

| Stack | Tool | Command |
| --- | --- | --- |
| JavaScript, TypeScript | StrykerJS | `npx stryker run --incremental` |
| Java, Kotlin | PIT | `mvn test org.pitest:pitest-maven:mutationCoverage -DwithHistory` |
| Python | mutmut | `mutmut run --paths-to-mutate src/` |
| Python | cosmic-ray | `cosmic-ray init config.toml session.sqlite` |
| Rust | cargo-mutants | `cargo mutants --in-diff changes.patch --jobs 8` |
| Go | go-mutesting | `go-mutesting ./...` |
| .NET | Stryker.NET | `dotnet stryker` |

Typical configuration points:

```json
{
  "mutate": ["src/**/*.ts", "!src/**/*.test.ts", "!src/generated/**"],
  "testRunner": "jest",
  "reporters": ["html", "json", "clear-text"],
  "thresholds": {"high": 80, "low": 60, "break": 50},
  "timeoutMS": 20000,
  "concurrency": 4
}
```

Exclude generated code, vendored code, logging, and trivial data classes. Keep the exclusion list in version control with a reason per entry.

### 3. Run a diff-scoped pass first

```bash
git diff origin/main...HEAD > /tmp/pr.patch
cargo mutants --in-diff /tmp/pr.patch --timeout 120
npx stryker run --since origin/main
mvn test org.pitest:pitest-maven:mutationCoverage -DwithHistory -DtargetClasses='com.acme.changed.*'
```

Diff scope keeps pull-request runtime bounded and focuses review on new behavior. Use a hard timeout per mutant (for example 60 to 120 seconds) so an infinite loop cannot stall the run.

### 4. Run the full suite on a schedule

Nightly or weekly, run the full scope with parallelism and incremental history. Store the HTML and JSON reports as artifacts. Record wall-clock time and mutant count so budget regressions are visible.

If runtime exceeds the budget, raise the timeout, split packages across jobs, or reduce the operator set before reducing scope silently.

### 5. Compute the score with an explicit formula

Tools disagree on denominators. State the formula and use it consistently:

```text
mutation score = killed / (killed + survived + timeout)
valid mutants   = killed + survived + timeout
equivalent      = reviewed and justified survivors, reported separately
```

Report per package, not only as one repository number. A global 65% can hide a payments package at 30% and a utilities package at 95%.

### 6. Triage every survivor

For each survivor, inspect the diff and assign exactly one disposition:

| Disposition | Meaning | Action |
| --- | --- | --- |
| Missing assertion | Test executes the line but checks nothing | Add a precise assertion |
| Untested branch | No test reaches the mutated path | Add a test for that behavior |
| Weak assertion | Test checks the wrong property | Strengthen to the invariant |
| Equivalent mutant | Behavior is unchanged for all inputs | Mark with a reason and reviewer |
| Timeout | Test suite hangs on the mutant | Fix the test or exclude the operator |
| Flaky kill | Test failed for an unrelated reason | Fix the flake, rerun the mutant |
| Infrastructure | Build or dependency failed | Fix the harness, rerun |

Reproduce a survivor locally before accepting it:

```bash
mutmut show <id>
# apply the shown change manually, then run the focused test
pytest -q tests/test_pricing.py
```

If the test suite passes with the change applied, the survivor is real.

### 7. Kill or justify, then gate and track

Add the smallest test that fails under the mutant and passes on the original. For an equivalent mutant, prefer rewriting the code so the equivalence is obvious, then mark it with a reason and an expiry. Never bulk-ignore a file to hit a number.

Suggested gates (tune per repo):

- Diff mutation score at or above 60% for changed lines.
- Critical packages at or above 75%.
- Zero un-reviewed survivors introduced by the pull request.
- Pull-request runtime under 15 minutes; full run under 4 hours.

Track score by package over time. A falling score with rising coverage indicates tests that execute code without asserting.

## Validation

- Baseline suite is green and deterministic before the run.
- The report contains at least one generated mutant; zero usually means a bad path pattern.
- Score is recomputed from the raw JSON, not copied from a dashboard.
- A sample of three survivors is reproduced manually and confirmed to pass the suite.
- A sample of three killed mutants is confirmed to fail the relevant test.
- Every survivor has a disposition, and every equivalent has a reason and reviewer.
- Runtime and mutant count are recorded against the budget.
- The gate fails when the diff score drops below the threshold; test the gate with a deliberately weak commit.

## Gotchas

- 100% line coverage with a 40% mutation score is common: tests execute code without asserting outcomes.
- Flaky tests create false kills. A mutant "killed" by an unrelated timeout is not evidence of detection.
- A hanging mutant counted as killed inflates the score. Classify timeouts separately.
- Equivalent mutants are common around boundary conditions and defensive code. Review them, do not automate them away.
- Incremental caches keyed only by file can reuse stale results after tests change. Clear the cache when test code changes.
- Mutating constants, log strings, and generated DTOs wastes runtime. Exclude them deliberately.
- A partial test selection can turn a real kill into a false survivor. Run the full relevant module.
- Static mutants (initialization-time changes) may not be exercised at all; inspect the report's mutant state.
- Assertions on exceptions alone can kill some mutants while missing wrong return values.
- Concurrency mutants may pass by scheduling luck. Run the focused test repeatedly before trusting a kill.
- The tool's "mutation score" may include or exclude equivalent and no-coverage mutants. Normalize before comparing runs.

## Output contract

```markdown
## Scope
Commit: <sha> | Packages: billing, pricing | Tool: PIT 1.16 | Command: ...
Baseline: 412 tests green | Mutants generated: 318 | Runtime: 11m 40s

## Score
| Package | Killed | Survived | Timeout | Equivalent | Score |
| --- | --- | --- | --- | --- | --- |
| billing | 96 | 18 | 2 | 4 | 82.8% |
| pricing | 54 | 21 | 1 | 2 | 71.1% |

## Surviving mutants
| ID | Location | Mutation | Disposition | Action | Owner |
| --- | --- | --- | --- | --- | --- |
| b-17 | billing/Fee.java:42 | removed null check | untested branch | add test for null fee | @team-billing |

## Equivalents
| ID | Location | Reason | Reviewer |
| --- | --- | --- | --- |

## Gate
Diff score: 68% (threshold 60%) | Critical packages: pass | Unreviewed survivors: 0
Runtime: 11m 40s (budget 15m)

## Next actions
- Add assertion for currency rounding at billing/Fee.java:88
- Rewrite redundant guard at pricing/Rule.java:31, then remove equivalent marker
```

## Checklist

- [ ] Baseline green and deterministic.
- [ ] Scope and risk rationale recorded.
- [ ] Tool configured with explicit mutate and exclude patterns.
- [ ] Diff-scoped run completed for the change.
- [ ] Full scheduled run completed within budget.
- [ ] Score formula stated and applied consistently.
- [ ] Every survivor triaged with one disposition.
- [ ] Sampled survivors reproduced manually.
- [ ] Equivalent mutants reviewed with reasons.
- [ ] Gate thresholds enforced and tested.
- [ ] Score trend recorded by package.

## Related skills

- `code-coverage-gap-analysis` for finding which behavior is never executed.
- `test-driven-verification-loop` for adding the failing test that kills a mutant.
- `automated-unit-test-generation` for scaling test creation after triage.
- `flaky-test-detection` for removing false kills before trusting the score.
