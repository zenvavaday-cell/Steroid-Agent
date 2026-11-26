---
name: flaky-test-detection
description: Identifies nondeterministic tests from reruns, timing, ordering, and environment evidence. Use for stabilizing CI and reducing false failures.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: engineering
---

# Flaky Test Detection

## Overview

A flaky test is a test whose result changes without a code change. Retries hide it, quarantine contains it, and neither fixes it. Detection requires repeated execution under varied conditions, then classification from evidence rather than from the failure message alone.

One pass proves nothing. The unit of evidence is a run matrix: same test, many runs, controlled variation.

## When to use

- A test failed, passed on retry, and the team moved on.
- CI fails intermittently on the same commit.
- A test is slow enough to approach its timeout.
- Parallel or shuffled execution produces different results from serial execution.
- You need a measured flake rate before and after a fix.
- A quarantine list has grown without owners or expiry dates.

Do not use for deterministic failures, which belong in `ci-cd-failure-diagnosis`, or for a one-off infrastructure outage.

## Workflow

### 1. Build the candidate list and measure a flake rate

Pull results from CI, not from memory. Parse JUnit XML artifacts or query the API:

```bash
gh run list --workflow=ci.yml --limit 100 --json databaseId,headSha,conclusion
gh run download <run-id> -n test-reports -D /tmp/reports
```

For each test, compute `failures / runs` over runs of the same commit and job. Use a Wilson interval, not a raw ratio, when the sample is small. Example policy: investigate at 0.5% or higher with at least 20 runs; quarantine at 2% or higher, or two failures in seven days.

### 2. Run a rerun matrix

```bash
pytest -q tests/test_checkout.py --count=50
pytest -q tests/test_checkout.py -p randomly --randomly-seed=12345
go test ./internal/queue -run TestDrain -count=100 -shuffle=on
npx jest tests/checkout.test.ts --runInBand
npx vitest run tests/checkout.test.ts --sequence.shuffle --retry=0
npx playwright test checkout.spec.ts --repeat-each=20 --workers=1
```

Run the test alone, with its file, and with the full suite. Capture JUnit XML for every configuration. A test that fails only in the full suite points to shared state; one that fails only alone points to a missing setup dependency.

### 3. Vary the environment deliberately

```bash
TZ=Pacific/Kiritimati LANG=tr_TR.UTF-8 pytest -q tests/test_dates.py
faketime '2026-03-01 23:59:59' pytest -q tests/test_billing.py
stress-ng --cpu 4 --vm 2 --timeout 60s &
docker run --rm --cpus=1 --memory=512m -v "$PWD:/w" -w /w <image> pytest -q
```

Vary CPU count, timezone, locale, clock, free memory, network latency, and filesystem order. Most flakes fall into one of these dimensions.

### 4. Classify from evidence

| Class | Evidence | Typical cause |
| --- | --- | --- |
| Timing | Fails under CPU load, passes idle | `sleep` shorter than the operation |
| Order | Fails only after a specific predecessor | Shared database, global registry |
| Randomness | Failure disappears with a fixed seed | Unseeded RNG or UUID-dependent assertion |
| Clock | Fails near month, year, or DST boundary | Wall-clock arithmetic, timezone assumptions |
| Network | Fails on retry or offline | Real HTTP call, DNS, port collision |
| Resource | Fails at low memory or high parallelism | Connection pool, file descriptors, temp disk |
| Async race | Fails with an unawaited promise or thread | Missing synchronization, fire-and-forget |
| Environment | Fails only in CI | Different image, locale, CPU architecture |

Record the class, the exact reproduction command, and the observed failure text.

### 5. Isolate the mechanism

- Disable test ordering plugins and run the suspect after each other test to find the polluter.
- Run with `-p no:cacheprovider` and a fresh database schema or namespace.
- Replace parallel workers with one worker, then reintroduce concurrency.
- Instrument the boundary: log timestamps around the suspected sleep, lock, or request.
- Use `pytest --lf`, `--sw`, or `go test -failfast` to shorten the loop.
- Check whether the assertion depends on a value that another test mutates.

The goal is a minimal reproduction, not a longer retry loop.

### 6. Quarantine without losing the signal

- Mark the test with a project-specific marker, for example `@pytest.mark.quarantined`, and exclude that marker from the required gate.
- Keep it running in a nightly or non-blocking job so the failure count keeps accumulating.
- Attach a tracking issue, an owner, and a removal date (for example 14 days).
- Never add a global retry to make the gate green; that converts a known flake into an unknown one.
- Cap the quarantine list and review it weekly.

### 7. Fix the cause and prove the fix

| Cause | Fix |
| --- | --- |
| Sleep-based wait | Poll a condition with a deadline (`waitFor`, `eventually`) |
| Shared database | Unique schema per worker, transaction rollback, or truncate between tests |
| Unseeded randomness | Seed explicitly and assert on invariants, not generated values |
| Clock | Inject a clock or freeze time; compute in UTC |
| Port collision | Bind port 0 and read the assigned port |
| External service | Mock at the boundary or use a contract stub |
| Async race | Await the task, join the thread, or assert on a terminal state |
| Parallel contention | Reduce shared resources or serialize the conflicting group |

Run the fixed test at least 200 times in CI configuration, plus shuffled and single-CPU variants. Zero failures in 200 runs gives a 95% upper bound near 1.5% (rule of three), so state that bound rather than claiming the flake is impossible.

## Validation

- Pre-fix evidence exists: at least 10 failures, or a documented reproduction under a named condition.
- The flake class is recorded with the matching evidence row.
- The minimal reproduction command runs in under five minutes.
- Post-fix: 200 consecutive runs, zero failures, in the same environment that failed before.
- Post-fix: shuffled order, one worker, and one-CPU runs also pass.
- The quarantine marker, issue link, owner, and expiry are removed in the same change as the fix.
- No new global retry or `--rerun-failed` was added to the gate.

## Gotchas

- Pass on retry is a flake, not a pass. Count it as a failure in the flake rate.
- Retries inflate the denominator and make a 10% flake rate look like 1%.
- A test that fails only in parallel is usually sharing a database row, a port, or a temp path.
- Random test order finds some order dependencies but not all. Repeat with several seeds.
- `sleep(1)` is tuned to a developer laptop and fails on a loaded CI runner. Poll instead.
- Timezone bugs cluster at DST changes and month boundaries; test those dates explicitly.
- Snapshot tests can encode a timestamp or an absolute path and fail on the next run.
- Unawaited promises and fire-and-forget threads may fail after the test has already reported success.
- A flaky test can mask a real bug. Quarantine preserves the failure count; deleting the test destroys the evidence.
- Test pollution often comes from module-level caches, environment variables, or singletons, not from the database.
- Increasing the timeout hides a slow test but does not make it deterministic.
- A green rerun of the whole suite does not clear the original failure; the same commit must pass repeatedly.

## Output contract

```markdown
## Test
Name: tests/test_checkout.py::test_applies_coupon
Job: unit / commit: <sha>
Flake rate: 7 failures / 120 runs (5.8%, 95% CI 2.8-11.4%)

## Reproduction
Command: pytest -q tests/test_checkout.py::test_applies_coupon --count=50
Condition: fails in 4/50 runs under `stress-ng --cpu 4`
Evidence: TimeoutError after 2000 ms, expected coupon applied

## Classification
order | shared database row between two tests

## Quarantine
Marker: @pytest.mark.quarantined
Issue: <link> | Owner: <name> | Expires: 2026-02-01
Nightly job: flaky-suite

## Fix
Change: unique coupon code per test, transaction rollback
Verification: 200/200 runs green, shuffled and 1 CPU
Residual risk: upper bound 1.5% at 95% confidence

## Prevention
Check: lint rule banning time.sleep in tests
```

## Checklist

- [ ] Candidate list built from CI history, not recollection.
- [ ] Flake rate computed with sample size and confidence interval.
- [ ] Rerun matrix covers alone, file, and full suite.
- [ ] Environment varied across time, CPU, locale, and clock.
- [ ] Failure classified with evidence.
- [ ] Minimal reproduction recorded.
- [ ] Quarantine has owner, issue, and expiry.
- [ ] Root cause fixed at the mechanism, not the assertion.
- [ ] 200 clean runs verified in the failing environment.
- [ ] Retry and quarantine entries removed after the fix.

## Related skills

- `ci-cd-failure-diagnosis` for deterministic pipeline failures and environment differences.
- `test-driven-verification-loop` for the regression test that locks in the fix.
- `git-bisect-regression-hunting` when the flake started within a known revision range.
- `automated-unit-test-generation` for replacing a deleted flaky test with deterministic coverage.
