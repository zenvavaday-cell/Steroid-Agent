---
name: automated-unit-test-generation
description: Generates meaningful unit and property-based tests from code behavior and specifications, validates them with mutation testing, and avoids coverage theater. Use for legacy characterization, new feature tests, regression coverage, and improving an existing suite.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: engineering
---

# Automated Unit Test Generation

## Overview

Generated tests are useful only if they detect real faults. A test that mirrors the implementation, asserts on mocks, or exercises a line without checking a meaningful outcome adds maintenance cost and false confidence.

Generate from behavior: inputs, outputs, side effects, errors, and invariants. Validate with mutation testing.

## When to use

- Adding tests to untested legacy code.
- Covering a new module or function.
- Converting a bug report into regression tests.
- Raising coverage on critical paths.
- Adding property-based tests for parsers, pricing, or state machines.

Do not generate tests for generated code, trivial getters, or code scheduled for deletion.

## Workflow

### 1. Understand the unit

Read:

- The public function or class signature.
- Docstrings and type hints.
- Call sites and expected usage.
- Error handling and side effects.
- Related tests and fixtures.

If the behavior is ambiguous, ask or write a characterization test that documents current behavior rather than guessing intended behavior.

### 2. Build a behavior matrix

| Input class | Example | Expected |
| --- | --- | --- |
| Nominal | Valid order | Total computed |
| Boundary | Zero, one, max | Correct edge result |
| Invalid | Negative quantity | ValueError |
| Missing | Null optional field | Default applied |
| Side effect | Payment call | Exactly one call with idempotency key |
| State | Duplicate request | Same result, no double charge |

Every row becomes at least one test.

### 3. Choose the test style

| Style | Use for |
| --- | --- |
| Example-based | Concrete business rules |
| Parameterized | Many inputs, one rule |
| Property-based | Invariants across generated inputs |
| Characterization | Locking existing behavior before refactor |
| Contract | Boundaries between services |
| Snapshot | Stable serialized output only |

### 4. Write the tests

```python
import pytest
from decimal import Decimal
from pricing import apply_discount

@pytest.mark.parametrize(
    "subtotal,discount,expected",
    [
        (Decimal("100.00"), Decimal("0.10"), Decimal("90.00")),
        (Decimal("0.00"), Decimal("0.10"), Decimal("0.00")),
        (Decimal("100.00"), Decimal("0"), Decimal("100.00")),
        (Decimal("100.00"), Decimal("1"), Decimal("0.00")),
    ],
)
def test_discount_amounts(subtotal, discount, expected):
    assert apply_discount(subtotal, discount) == expected

@pytest.mark.parametrize("discount", [Decimal("-0.01"), Decimal("1.01")])
def test_rejects_out_of_range_discount(discount):
    with pytest.raises(ValueError, match="between 0 and 1"):
        apply_discount(Decimal("100.00"), discount)
```

Property-based example:

```python
from hypothesis import given, strategies as st

@given(
    subtotal=st.decimals(min_value=0, max_value=1_000_000, places=2),
    discount=st.decimals(min_value=0, max_value=1, places=2),
)
def test_discount_never_increases_price(subtotal, discount):
    assert apply_discount(subtotal, discount) <= subtotal
```

### 5. Isolate external boundaries

- Use a temporary directory for files.
- Freeze time with `freezegun` or inject a clock.
- Seed randomness.
- Use a test container for a real database when behavior depends on SQL.
- Mock only network, payment, email, and other out-of-process boundaries.
- Assert on observable outcomes, not on internal call choreography unless the call is the contract.

### 6. Run and fix

```bash
pytest tests/test_pricing.py -q
pytest -q
```

A generated test that fails may reveal a real bug, a wrong assumption, or a bad test. Classify before changing the assertion. Never weaken a test to match buggy behavior without documenting it.

### 7. Validate test strength

```bash
mutmut run --paths-to-mutate src/pricing.py
pytest --cov=src/pricing.py --cov-report=term-missing
```

Mutation testing changes the code and checks whether tests fail. Surviving mutants identify weak assertions. Coverage identifies unexecuted lines. Use both; neither alone is enough.

## Gotchas

- Tests that assert on mock calls can pass while the real integration is broken.
- A test that duplicates the implementation formula will pass even if both are wrong.
- Snapshot tests approve regressions when reviewers blindly update the snapshot.
- Shared fixtures with mutable state create order-dependent failures.
- Time, locale, timezone, and randomness must be controlled.
- Async tests need an async runner and proper cleanup; fire-and-forget tasks leak.
- Database tests need transaction isolation or unique schemas.
- Coverage of a line does not mean the assertion checks the result.
- Generated tests can encode current bugs as expected behavior. Label characterization tests clearly.
- Flaky tests are worse than no tests. Fix or delete them.

## Output contract

```markdown
## Target
<module and functions>

## Behaviors covered
| Behavior | Test | Type |
| --- | --- | --- |

## New tests
<files and count>

## Results
- targeted: N passed
- full suite: N passed
- coverage: <line/branch>
- mutation score: <percent>

## Bugs found
<list or none>

## Known gaps
<...>
```

## Checklist

- [ ] Behavior matrix built.
- [ ] Nominal, boundary, invalid, and side-effect cases covered.
- [ ] External boundaries isolated.
- [ ] Tests deterministic and independent.
- [ ] Full suite passes.
- [ ] Mutation testing run on critical code.
- [ ] Characterization tests labeled.
- [ ] Generated tests reviewed by a human or a second pass.

## Related skills

- `test-driven-verification-loop` for test-first development.
- `dead-code-elimination` to avoid testing code that should be deleted.
- `automated-refactoring-execution` for using tests as a safety net.
