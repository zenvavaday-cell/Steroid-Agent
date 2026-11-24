---
name: ci-cd-failure-diagnosis
description: Diagnoses failed CI/CD runs by isolating the failing job and step, reading logs and artifacts, comparing against the last green run, reproducing locally, and classifying flaky, infrastructure, dependency, config, or code failures. Use for GitHub Actions, GitLab CI, Jenkins, CircleCI, and build pipeline triage.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: engineering
---

# CI/CD Failure Diagnosis

## Overview

CI failures are evidence. The first error in the log is not always the cause; parallel jobs interleave, caches hide stale state, and exit codes encode signals that logs do not show. Diagnose by isolating the smallest failing unit and reproducing it.

## When to use

- A pipeline failed and the cause is unclear.
- A job passes locally but fails in CI.
- A previously green pipeline broke without a code change.
- A flaky test or infrastructure failure needs triage.

## Workflow

### 1. Identify the failing run and job

```bash
gh run list --limit 20
gh run view <run-id> --json conclusion,headSha,event,createdAt,workflowName
gh run view <run-id> --log-failed
```

For GitLab:

```bash
glab ci list
glab ci trace <job-id>
```

Record the run ID, commit SHA, branch, event type, runner, and duration.

### 2. Find the first meaningful error

Logs are noisy. Search for:

- `error`, `fatal`, `failed`, `exception`, `traceback`
- Non-zero exit codes and `exit code`
- `Killed`, `OOMKilled`, `signal: killed`
- Timeout and connection errors
- Missing environment variables or files

Use timestamps and step boundaries to avoid attributing a later cascading error as the cause.

### 3. Classify the failure

| Class | Evidence | Typical fix |
| --- | --- | --- |
| Code | Reproduces locally, deterministic stack trace | Fix code |
| Test | Assertion failure, order dependence | Fix or isolate test |
| Flaky | Passes on retry, timing/network dependent | Quarantine, fix root cause |
| Dependency | Version resolution, registry outage | Pin or retry |
| Config | Missing secret, wrong path, invalid YAML | Fix config |
| Infrastructure | Runner outage, disk full, OOM | Rerun or resize |
| Cache | Stale cache, poisoning | Clear cache key |
| Permission | 403, token scope | Fix credentials |
| Resource | Timeout, memory, concurrency limit | Optimize or raise limit |

### 4. Compare with the last green run

```bash
gh run list --workflow=ci.yml --branch=main --limit 10
gh run view <green-id> --json headSha,createdAt
git diff <green-sha>..<red-sha> -- .github/ package.json pyproject.toml
```

Check for changes in:

- Workflow files, action versions, runner images.
- Dependency lockfiles.
- Environment or secret names.
- Test data and fixtures.
- Timezone, locale, or clock assumptions.

A pipeline that breaks with no code change often changed upstream: a mutable action tag, a base image, or a dependency resolution.

### 5. Reproduce in the same environment

```bash
docker run --rm -it -v "$PWD:/work" -w /work <ci-image> bash
```

Replicate:

- The same language and tool versions.
- The same environment variables (without printing secrets).
- A clean cache and a clean checkout.
- The same command and working directory.

If it passes in the container but fails in CI, the difference is in the runner, secrets, network, or parallelism.

### 6. Narrow the failure

- Run the failing job's steps one at a time.
- Run the failing test alone, then with the full suite.
- Disable parallelism.
- Use `--fail-fast` or the equivalent.
- Add `set -x` or verbose logging temporarily.
- Capture artifacts: logs, screenshots, test reports, core dumps.

### 7. Fix and verify

Apply the smallest fix. Push and watch the full pipeline, not only the previously failing job. A fix that breaks another job is not a fix.

### 8. Prevent recurrence

- Pin action and image versions by digest or SHA.
- Add a regression test.
- Set timeouts and resource limits explicitly.
- Cache with versioned keys and a fallback.
- Alert on repeated flaky failures.

## Gotchas

- Exit code 137 usually means SIGKILL, often OOM. Check memory limits, not only the test.
- Exit code 143 is SIGTERM, often a timeout or cancellation.
- Masked secrets appear as `***`; absence of a value may be a missing secret, not an empty one.
- Logs from parallel jobs can interleave. Use step grouping and timestamps.
- `gh run view --log-failed` may omit setup failures or truncated logs. Download the full artifact.
- A retry that passes does not mean the failure is gone. Quarantine and investigate.
- Cache keys that omit the lockfile hash can serve stale dependencies.
- Mutable tags like `actions/checkout@v4` can change behavior. Pin to a commit SHA for critical pipelines.
- Working directory and shell differences (`bash -e` versus `bash -eo pipefail`) change failure behavior.
- Tests that depend on wall-clock time fail at month or year boundaries. Freeze time.

## Output contract

```markdown
## Failure
Run: <id> | Commit: <sha> | Job: <name> | Step: <name>
Exit code: <code>
First error: <message>

## Classification
<code | test | flaky | dependency | config | infrastructure | cache | permission | resource>

## Evidence
- <log line or artifact>
- <comparison with last green>

## Reproduction
Command: ...
Result: ...

## Root cause
<one paragraph>

## Fix
<change and verification>

## Prevention
<guardrail>
```

## Checklist

- [ ] Run, commit, job, and step identified.
- [ ] First meaningful error isolated.
- [ ] Failure classified.
- [ ] Last green run compared.
- [ ] Reproduced in a matching environment.
- [ ] Root cause stated, not just the symptom.
- [ ] Fix verified on the full pipeline.
- [ ] Prevention added.

## Related skills

- `container-log-diagnostics` for runtime failures after deployment.
- `git-bisect-regression-hunting` when the breaking commit is unknown.
- `dependency-vulnerability-auditing` for dependency-related breakage.
