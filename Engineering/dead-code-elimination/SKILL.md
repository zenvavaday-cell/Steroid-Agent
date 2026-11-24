---
name: dead-code-elimination
description: Identifies unused functions, exports, files, dependencies, and feature flags using static analysis, coverage, and entry-point reachability, then removes them safely with verification. Use for codebase cleanup, bundle reduction, dependency pruning, and pre-refactor hygiene.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: engineering
---

# Dead Code Elimination

## Overview

Dead code is code that cannot be reached from any entry point. Static tools find candidates; reachability analysis decides. Deleting a public API, a reflection target, or a dynamically imported module causes production failures that tests may not catch.

Remove in small, reversible steps.

## When to use

- Cleaning up after a large refactor or migration.
- Reducing bundle size or container image size.
- Removing unused dependencies.
- Retiring feature flags.
- Preparing a module for extraction.

Do not start with deletion. Start with evidence.

## Workflow

### 1. Inventory entry points

List every way code can be reached:

- HTTP routes, GraphQL resolvers, gRPC handlers.
- CLI commands, cron jobs, queue consumers.
- Lambda or serverless handlers.
- Exported library API.
- Plugin and extension points.
- Test-only and build-only paths.
- Dynamic imports, reflection, dependency injection, and serialization.

If an entry point is undocumented, search deployment configs and runtime traffic.

### 2. Run static candidate detection

| Ecosystem | Tools |
| --- | --- |
| Python | `vulture`, `ruff` unused rules, `pyflakes` |
| JavaScript/TypeScript | `knip`, `ts-prune`, `eslint no-unused-vars` |
| Go | `staticcheck`, `deadcode` |
| Java | IntelliJ inspections, `jdeps` |
| Rust | `cargo udeps`, compiler warnings |
| Dependencies | `depcheck`, `deptry`, `go mod tidy` |

```bash
vulture src/ --min-confidence 80
knip --include files,exports,dependencies
staticcheck ./...
```

Treat output as candidates, not conclusions.

### 3. Measure runtime reachability

Coverage from tests is not production coverage. Combine:

- Test coverage for changed paths.
- Production tracing or APM data.
- Access logs for routes and jobs.
- Feature flag evaluation logs.
- Package import graphs.

A function with zero test coverage may still be used in production. A function with test coverage may be used only by tests.

### 4. Classify candidates

| Class | Definition | Action |
| --- | --- | --- |
| Safe | Unreachable from any entry point and not exported | Delete |
| Test-only | Used only by tests | Delete test and code, or keep if the test is the contract |
| Public API | Exported or documented | Deprecate, do not delete silently |
| Dynamic | Reflection, DI, serialization, plugin | Keep unless proven unused |
| Generated | Build output, vendored | Exclude |
| Flagged | Behind a retired feature flag | Remove flag and code together |
| Duplicate | Reimplemented elsewhere | Remove the older path after migration |

### 5. Remove incrementally

1. Delete one layer at a time: callers first, then the definition.
2. Keep changes reviewable; do not delete 10,000 lines in one commit.
3. Remove imports, types, tests, fixtures, docs, and config references together.
4. Update dependency manifests and lockfiles.
5. Run the formatter and linter.

```bash
git switch -c chore/remove-dead-code
git grep -n "old_function"  # confirm no remaining references
```

### 6. Verify

- Build succeeds.
- Full test suite passes.
- Type checks pass.
- Application starts and health checks pass.
- Bundle or image size decreased as expected.
- Search logs for 404s or missing handlers after deploy.

For risky removals, deploy behind a short monitoring window before deleting the final fallback.

### 7. Prevent regrowth

- Enable unused-code lint rules in CI.
- Add bundle-size budgets.
- Remove feature flags on a schedule.
- Review dependencies quarterly.

## Gotchas

- Reflection, decorators, and dependency injection hide usage from static tools. Check framework conventions.
- Serialization libraries reference class names as strings. A class with no direct import may still be required.
- Public packages have external consumers you cannot see. Use deprecation and semver.
- Tests can be the only caller. Deleting the test and code is fine; keeping code only for tests is not.
- Feature flags may be evaluated dynamically or by an external service. Confirm before removing.
- Generated code may be excluded from analysis but imported at runtime.
- Monorepos can have cross-package usage that per-package tools miss.
- Dynamic `import()` with a computed path defeats static analysis.
- Removing a dependency can remove a transitive package still needed elsewhere. Rebuild and test.
- Dead code can still be a security risk. Remove it even if it is not on a hot path.

## Output contract

```markdown
## Candidates
| Item | Type | Static signal | Runtime signal | Classification |
| --- | --- | --- | --- | --- |

## Removed
| Item | Files | Lines | Verification |
| --- | --- | --- | --- |

## Kept
| Item | Reason |
| --- | --- |

## Impact
- bundle/image size: before -> after
- dependencies removed: N
- tests removed: N

## Follow-up
<deprecations, flags, monitoring>
```

## Checklist

- [ ] Entry points inventoried.
- [ ] Static candidates collected.
- [ ] Runtime reachability checked.
- [ ] Public and dynamic usage reviewed.
- [ ] Removal done incrementally.
- [ ] Imports, tests, docs, and config updated.
- [ ] Build, tests, types, and startup verified.
- [ ] Regrowth guardrails added.

## Related skills

- `semantic-codebase-search` for finding all references.
- `abstract-syntax-tree-navigation` for structural usage analysis.
- `automated-refactoring-execution` for the accompanying refactor.
