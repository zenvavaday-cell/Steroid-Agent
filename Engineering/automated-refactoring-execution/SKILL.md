---
name: automated-refactoring-execution
description: Executes large-scale behavior-preserving refactors with characterization tests, codemods, incremental batches, and verification at every step. Use for renames, API migrations, module extraction, framework upgrades, and repetitive code transformations across many files.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: engineering
---

# Automated Refactoring Execution

## Overview

A refactor changes structure without changing behavior. That definition is a testable claim: if behavior changes, it is not a refactor. Large refactors fail when they mix concerns, skip characterization, or apply a codemod without reviewing the diff.

The method: characterize, transform mechanically, verify continuously, and keep the change reversible.

## When to use

- Renaming a symbol, package, or API across a codebase.
- Migrating from one library or framework version to another.
- Extracting a module or package.
- Replacing a deprecated pattern.
- Applying a lint rule or style change at scale.

Do not combine a refactor with a feature change. Split them.

## Workflow

### 1. Define the invariant

State exactly what must not change:

- Public API signatures and behavior.
- Serialized output format.
- Database schema and data.
- Error types and status codes.
- Performance envelope.

Write it down. This becomes the acceptance criteria.

### 2. Establish a baseline

```bash
git switch -c refactor/<name>
git rev-parse HEAD
pytest -q
npm test
```

Record the passing baseline, the commit SHA, and any pre-existing failures. A refactor that "fixes" an unrelated test is suspicious.

### 3. Add characterization tests

For behavior that is not covered, add tests that capture current inputs and outputs. Characterization tests document what the code does, not what it should do.

Focus on:

- Public entry points.
- Serialization and API responses.
- Edge cases and error paths.
- Integration seams.

### 4. Choose the transformation method

| Scope | Method |
| --- | --- |
| One symbol, few files | IDE rename or language server |
| Repetitive syntactic change | `ast-grep`, `comby`, `jscodeshift`, `libcst` |
| Framework migration | Official codemod plus manual fixes |
| Module extraction | Move files, update imports, add boundaries |
| Dependency upgrade | Upgrade, run tests, fix breakages |

Prefer the smallest tool that preserves semantics. Regex is acceptable only for lexical changes with no syntactic ambiguity.

### 5. Dry-run the codemod

```bash
sg run -p 'old_api($$$ARGS)' -r 'new_api($$$ARGS)' -l python --json=matches.json src/
comby 'old_api(:[args])' 'new_api(:[args])' .py -d src/
```

Review:

- Number of matches.
- Files and contexts.
- False positives in strings, comments, tests, or generated code.
- Cases the pattern misses.

### 6. Apply in batches

One batch should be reviewable in a sitting. After each batch:

```bash
formatter .
linter .
type-checker .
pytest -q
```

Commit each green batch with a descriptive message. If a batch fails, revert only that batch.

### 7. Review the diff

- Only intended files changed.
- No formatting-only noise mixed with semantic changes.
- No public API change without a deprecation path.
- No generated files edited by hand.
- Imports and exports updated.
- Documentation and examples updated.

### 8. Remove the old path

After all callers migrate:

- Delete the old implementation.
- Remove compatibility shims.
- Remove the feature flag.
- Update the changelog and migration guide.

### 9. Verify

- Full test suite passes.
- Type checks pass.
- Build and package succeed.
- Performance is within the envelope.
- A smoke test on a staging environment passes.

## Gotchas

- A refactor that changes behavior is a feature or a bug. Split it.
- Codemods miss dynamic calls, reflection, string references, and configuration.
- Operators can change semantics: `+` versus `??`, eager versus lazy, sync versus async.
- Formatters create huge diffs that hide real changes. Run formatting as a separate commit.
- Long-lived refactor branches drift from main. Rebase frequently or use a feature flag.
- Tests that assert on implementation details break during refactors. Fix the tests to assert behavior.
- Public APIs need a deprecation window, not an immediate rename.
- Generated code should be regenerated, not transformed.
- A green suite does not prove behavior preservation if coverage is low. Use characterization tests and production checks.
- Rollback must be possible at every batch boundary.

## Output contract

```markdown
## Refactor
<goal and invariant>

## Baseline
Commit: <sha> | Tests: N passed | Known failures: ...

## Characterization
<new tests and what they lock>

## Transformation
Tool: ... | Matches: N | Batches: N

## Verification per batch
| Batch | Tests | Types | Lint | Commit |
| --- | --- | --- | --- | --- |

## Diff summary
Files: N | Lines: +N/-N | Public API changes: none

## Rollback
<revert strategy>

## Follow-up
<deprecation, docs, cleanup>
```

## Checklist

- [ ] Invariant stated.
- [ ] Baseline recorded.
- [ ] Characterization tests added.
- [ ] Transformation method chosen.
- [ ] Codemod dry-run reviewed.
- [ ] Batches applied and verified.
- [ ] Diff reviewed for unintended changes.
- [ ] Old path removed after migration.
- [ ] Rollback possible at each step.

## Related skills

- `test-driven-verification-loop` for the verification standard.
- `abstract-syntax-tree-navigation` for building precise codemods.
- `semantic-codebase-search` for finding all call sites.
