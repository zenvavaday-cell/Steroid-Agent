---
name: test-driven-verification-loop
description: Drives implementation through a strict red-green-refactor loop, writing a failing test first, confirming it fails for the right reason, implementing the minimum change, and verifying with targeted, full-suite, and mutation checks. Use for feature work, bug fixes, refactors, and any agent task where correctness must be proven rather than asserted.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: engineering
---

# Test-Driven Verification Loop

## Overview

TDD is a control loop, not a documentation ritual. The test is an executable specification. A test that has never failed proves nothing. This skill enforces the sequence and the evidence at each step.

The loop: **red → green → refactor → repeat**.

## When to use

- Implementing a feature with defined behavior.
- Fixing a bug with a reproducible case.
- Refactoring code that must preserve behavior.
- Any change where the agent cannot directly observe production behavior.

Skip TDD only for pure exploration or throwaway scripts. Even then, add a verification step before declaring success.

## Workflow

### 1. State the behavior in one sentence

Example: "Applying a 10% discount to an order of 100.00 returns 90.00 and rejects negative discounts."

If you cannot state the behavior, you are not ready to write the test.

### 2. Write the failing test

```python
import pytest
from pricing import apply_discount

def test_applies_percentage_discount():
    assert apply_discount(100.00, 0.10) == 90.00

def test_rejects_negative_discount():
    with pytest.raises(ValueError, match="discount must be between 0 and 1"):
        apply_discount(100.00, -0.01)

def test_rejects_discount_above_one():
    with pytest.raises(ValueError):
        apply_discount(100.00, 1.01)
```

Cover:

- The happy path.
- Boundaries (0, 1, empty, max).
- Error paths and exact error types.
- One behavior per test.
- Deterministic inputs; no wall-clock, network, or random without a seed.

### 3. Run the test and confirm red

```bash
pytest tests/test_pricing.py::test_applies_percentage_discount -q
```

The failure must be the expected one: missing function, wrong value, or unhandled error. A syntax error or import error in the test file is not a valid red. Fix the test harness first.

Record the red evidence: command, test name, failure message.

### 4. Implement the minimum

Write only enough code to pass the current test. Do not add speculative features. Keep the change small enough to review.

### 5. Run targeted, then full

```bash
pytest tests/test_pricing.py -q
pytest -q
```

Targeted tests catch local errors fast. The full suite catches regressions elsewhere. Both must pass.

### 6. Refactor with the suite green

Improve names, remove duplication, and simplify. Re-run after each small refactor. Never refactor and add behavior in the same step.

### 7. Add stronger verification

| Check | Command | Purpose |
| --- | --- | --- |
| Coverage of changed lines | `pytest --cov=src --cov-report=term-missing` | Find untested branches |
| Mutation testing | `mutmut run` or `cosmic-ray` | Prove tests detect faults |
| Property-based tests | `hypothesis` | Explore edge cases |
| Type checking | `mypy src` or `pyright` | Catch contract errors |
| Lint | `ruff check` | Catch defects and style |

Coverage is a diagnostic, not a target. Mutation score is stronger evidence that assertions are meaningful.

## Test design rules

- Arrange, act, assert. One act per test.
- Test behavior through the public interface, not private methods.
- Prefer real objects; mock only external boundaries (network, clock, filesystem, payment provider).
- Name tests by behavior, not by method: `test_rejects_expired_card`, not `test_validate_2`.
- Avoid snapshot tests for logic; use them for stable serialized output only.
- Freeze time and seed randomness.
- Clean up fixtures; no shared mutable state between tests.

## Gotchas

- A test that passes before the implementation is either wrong or testing nothing. Verify red.
- Coverage can be 100% with zero assertions. Check the assertions.
- Over-mocking produces tests that pass while production fails.
- Testing private methods locks in implementation details and blocks refactoring.
- Flaky tests erode trust. Quarantine them with an owner and a deadline; do not retry forever.
- `assertEqual` on floats needs a tolerance.
- Database tests need transaction isolation or unique schemas.
- Snapshot updates can silently approve a regression. Review the diff.
- A regression test must fail on the old code. Run it against the parent commit when possible.

## Output contract

```markdown
## Behavior
<one sentence>

## Red evidence
Command: ...
Failure: ...

## Green evidence
Command: ...
Result: N passed

## Full suite
Command: ...
Result: N passed, 0 failed

## Additional checks
- coverage: ...
- mutation: ...
- types/lint: ...

## Files changed
- ...
```

## Checklist

- [ ] Behavior stated.
- [ ] Test written before implementation.
- [ ] Red confirmed for the expected reason.
- [ ] Minimum implementation added.
- [ ] Targeted tests pass.
- [ ] Full suite passes.
- [ ] Refactor done with suite green.
- [ ] Coverage, mutation, and type checks considered.
- [ ] Flaky or skipped tests documented.

## Related skills

- `automated-unit-test-generation` for expanding coverage after the loop.
- `automated-refactoring-execution` for safe large-scale changes.
- `ci-cd-failure-diagnosis` when the pipeline disagrees with local results.
