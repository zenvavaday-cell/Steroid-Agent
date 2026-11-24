---
name: git-bisect-regression-hunting
description: Finds the exact commit that introduced a regression using automated git bisect, a deterministic pass/fail script, skip handling, and verification of the first bad commit. Use when a test, build, or behavior broke somewhere in history and the cause is not obvious from the diff.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: engineering
---

# Git Bisect Regression Hunting

## Overview

`git bisect` performs a binary search over commit history. Its accuracy depends entirely on the test script: a flaky or environment-dependent test will produce a wrong answer with high confidence. Build the test first, prove it passes on the known-good commit and fails on the known-bad commit, then automate.

## When to use

- A regression exists but the breaking commit is unknown.
- A test passes on an old release and fails on the current branch.
- A performance or build regression appeared within a range.
- You need an evidence-backed first-bad commit, not a guess.

Do not use when the range is tiny (inspect the diff) or when the failure is nondeterministic (fix the test first).

## Workflow

### 1. Establish a good and a bad revision

```bash
git log --oneline --decorate -30
git bisect start
git bisect bad <bad-rev>       # usually HEAD
git bisect good <good-rev>     # last known good tag or commit
```

Use a tag or a commit you have actually verified, not a guess based on dates.

### 2. Write a deterministic test script

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

# Exit 0 = good, 1 = bad, 125 = skip (cannot test this commit)

./scripts/build.sh >/dev/null 2>&1 || exit 125
./scripts/test-regression.sh
```

Rules:

- The script must not depend on the working tree being clean beyond the checkout.
- Build from scratch or use a cache keyed by commit.
- Bound the runtime. A 30-minute test makes bisect unusable.
- Return 125 when the commit cannot be built or tested for unrelated reasons.
- Do not use `exit 1` for infrastructure failures; use 125 to skip.
- Log to a file so failures can be inspected later.

### 3. Verify both endpoints

```bash
git checkout <good-rev> && ./scripts/bisect-test.sh; echo "good: $?"
git checkout <bad-rev> && ./scripts/bisect-test.sh; echo "bad: $?"
```

Good must return 0, bad must return 1. If not, fix the script before continuing.

### 4. Run the automated bisect

```bash
git bisect run ./scripts/bisect-test.sh
```

Git checks out each candidate, runs the script, and narrows the range. On completion it reports the first bad commit.

### 5. Inspect the result

```bash
git show --stat <first-bad>
git diff <first-bad>^ <first-bad>
git log --oneline <first-bad>^..<first-bad>
```

Confirm the commit's change is plausibly related. Re-run the test at `<first-bad>^` and `<first-bad>` to verify the transition. A bisect result is a hypothesis until reproduced.

### 6. Handle merge commits

By default, bisect may land on a merge. Use `git bisect --first-parent` to search only the mainline, or mark merges as skipped. Then inspect the merged branch.

```bash
git bisect start --first-parent
```

### 7. Clean up

```bash
git bisect reset
```

This returns to the original branch. Check for detached HEAD or leftover changes.

## Gotchas

- A flaky test gives a confidently wrong commit. Run the test several times at both endpoints.
- If the build depends on generated files or submodules, the script must initialize them.
- Shallow clones may not contain the good commit. Fetch the full history.
- A dirty working tree can contaminate the test. Stash or use a separate worktree.
- `git bisect run` treats exit codes 126 and 127 as abort, not bad. Check the script's shebang and permissions.
- Build caches keyed only by branch can serve the wrong artifact. Key by commit SHA.
- Regressions caused by dependency resolution may not reproduce after a lockfile update. Pin the environment.
- A commit that fixes one thing and breaks another is still the first bad commit for this test. Report the interaction.
- Merge-heavy histories can confuse the search. Use first-parent when appropriate.

## Output contract

```markdown
## Regression
Symptom: ...
Good revision: <sha> (<date>)
Bad revision: <sha> (<date>)
Test script: scripts/bisect-test.sh

## Result
First bad commit: <sha>
Author: ...
Subject: ...
Files changed: ...

## Evidence
- good endpoint: exit 0
- bad endpoint: exit 1
- first bad: exit 1
- parent: exit 0

## Likely cause
<explanation tied to the diff>

## Next step
<fix, revert, or deeper investigation>
```

## Checklist

- [ ] Good and bad revisions verified.
- [ ] Test script deterministic and bounded.
- [ ] Skip code 125 used for untestable commits.
- [ ] Both endpoints return the expected exit codes.
- [ ] Bisect run completed.
- [ ] First bad commit inspected.
- [ ] Transition reproduced at parent and commit.
- [ ] Bisect reset and workspace cleaned.

## Related skills

- `ci-cd-failure-diagnosis` for pipeline failures without a known range.
- `test-driven-verification-loop` for the regression test itself.
- `automated-refactoring-execution` after the cause is understood.
