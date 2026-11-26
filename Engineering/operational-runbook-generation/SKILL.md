---
name: operational-runbook-generation
description: Generates verified runbooks with preconditions, commands, rollback, verification, and escalation paths. Use for on-call operations and service handovers.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: engineering
---

# Operational Runbook Generation

## Overview

A runbook is an executable procedure for a tired engineer under time pressure. It fails when it assumes cluster context, omits expected output, or hides an irreversible step inside a long shell block. The core discipline is to treat every procedure as code: parameterized, reviewed, dry-run against a real environment, and versioned with a last-verified date.

The output must let a second engineer who has never touched the service complete the task without asking a question. If a step requires judgment, the runbook states the decision rule and the evidence to collect.

## When to use

- Handing a service to a new on-call rotation.
- Documenting a recurring operation such as failover, certificate rotation, cache flush, or tenant restore.
- Turning a recurring alert into a step-by-step response procedure.
- Capturing tribal knowledge before an engineer changes teams.
- Preparing a handover or audit package that needs evidence of tested procedures.
- Do not use for exploratory debugging with an unknown cause; diagnose first with `container-log-diagnostics` or a postmortem, then write the runbook for the confirmed procedure.

## Workflow

### 1. Fix the metadata and scope

Record the service, owner team, severity scope, supported environments, version, and last-verified date. Use a single owner team, not an individual, so the runbook survives staff changes. State what the runbook does not cover.

```yaml
service: checkout-api
owner: payments-platform
scope: production rollout restart and rollback
environments: [staging, production]
version: 3.2.0
last_verified: 2026-11-20
review_due: 2027-02-20
```

### 2. Map triggers to a decision

List the alerts, symptoms, or scheduled events that start the procedure. Each trigger points to one section and one decision rule. Add a stop condition for cases that need a human decision before any command runs.

| Trigger | Evidence | Action |
| --- | --- | --- |
| `CheckoutApi5xxRate` above 2% for 5 min | Dashboard and error logs | Section 3, restart after confirming single-zone scope |
| Certificate expiry under 14 days | `openssl x509 -enddate` | Section 4, rotate with dual certificate |
| Planned dependency upgrade | Change ticket with approval | Section 3, canary first |

### 3. State preconditions and access

List every permission, tool, file, and environment variable the operator needs. Add commands that prove each precondition, with expected output. A precondition that cannot be verified is a risk, not a precondition.

```bash
kubectl config current-context                # expected: prod-eu-west-1
kubectl auth can-i patch deployments -n checkout   # expected: yes
aws sts get-caller-identity --query Account --output text  # expected: 111122223333
```

Also record the change ticket, backup requirement, maintenance window, and who must approve.

### 4. Write copy-paste steps with guardrails

Use one action per numbered step. Put variable assignments at the top, validate them, and prefer server-side dry runs before mutation. Show the expected output, normal duration, and the failure branch.

```bash
#!/usr/bin/env bash
set -euo pipefail
: "${NAMESPACE:?set NAMESPACE}"
: "${DEPLOYMENT:?set DEPLOYMENT}"

kubectl -n "$NAMESPACE" get deployment "$DEPLOYMENT" -o wide
kubectl -n "$NAMESPACE" rollout restart "deployment/$DEPLOYMENT"
kubectl -n "$NAMESPACE" rollout status "deployment/$DEPLOYMENT" --timeout=5m
kubectl -n "$NAMESPACE" get pods -l app="$DEPLOYMENT" -o wide
```

Expected: rollout completes in 90 to 180 seconds, and every pod is `Running` with two or more ready containers. On timeout, run the rollback in Section 6 instead of retrying blindly.

Rules:

- Never use a bare `kubectl delete pod` or wildcard delete. Select by label and show the selection first.
- Quote variables. Add `${VAR:?}` guards for anything that can select the wrong environment.
- Use `--dry-run=server` for manifest changes when supported.
- Avoid piping downloaded scripts into a shell. Pin versions and verify checksums.
- Mark destructive steps with a `DESTRUCTIVE` label and an approval requirement.

### 5. Define rollback before the procedure

For every mutating step, write the reverse action, the maximum time to execute it, and the verification. If rollback depends on the component being fixed, provide an independent path such as a previous image digest or a failover region.

| Step | Rollback command | Time budget | Verify |
| --- | --- | --- | --- |
| Rollout restart | `kubectl rollout undo deployment/$DEPLOYMENT` | 3 min | Pods ready, 5xx below 1% |
| Config change | Restore previous ConfigMap and restart | 5 min | Config hash matches previous |
| Certificate swap | Re-enable old certificate | 2 min | `openssl s_client` shows old serial |

### 6. Define verification and escalation

Verification is not "check the dashboard". Give the query, the window, and the pass threshold. Escalation names the role, the channel, and the trigger for paging.

```promql
sum(rate(http_requests_total{service="checkout-api",code=~"5.."}[5m]))
/
sum(rate(http_requests_total{service="checkout-api"}[5m])) < 0.01
```

Escalate when any of these is true: two rollback attempts fail, data integrity is in question, the error budget burn rate exceeds 14.4x for 1 hour, or the procedure needs a permission the operator does not have. Record the handoff with current state, actions taken, and open risks.

### 7. Dry-run with a second operator and publish

Run the procedure end to end in staging or a canary with an operator who did not write it. Time each step, capture output, and fix any step that needed verbal explanation. Then publish with the evidence block and set the review date.

```bash
shellcheck --severity=error scripts/checkout-rollout.sh
bash -n scripts/checkout-rollout.sh
markdownlint-cli2 "runbooks/checkout-api.md"
lychee --no-progress "runbooks/checkout-api.md"
```

## Validation

| Gate | Pass criterion | Command or evidence |
| --- | --- | --- |
| Shell syntax | Exit 0 | `bash -n <script>` |
| Shell defects | No error-severity findings | `shellcheck --severity=error <script>` |
| Independent dry run | Second operator completes without undocumented help | Timed transcript in staging |
| Preconditions | Fresh shell succeeds with only documented access | Access checklist signed |
| Rollback rehearsal | Rollback completed within its time budget | Recorded run |
| Verification queries | Each check returns a clear pass or fail | Query output attached |
| Links and formatting | No broken links, linter clean | `lychee`, `markdownlint-cli2` |
| Secret scan | No credentials or tokens | `gitleaks detect --source . --no-git` |
| Review | Service owner and on-call reviewer approve | Review record |

Reject the runbook if any command lacks expected output or if a destructive step lacks a rollback or an explicit "irreversible, requires approval" marker.

## Gotchas

- A missing context check lets a copy-paste hit production while the operator believes it is staging. Make `kubectl config current-context` the first line and fail on mismatch.
- Wildcard deletes or label typos remove healthy pods. Always print the selected resources, then delete by exact label.
- Tokens pasted into commands land in shell history and terminal logs. Load them from a secret manager, run `set +o history` around the step, and never echo the value.
- Relative dates such as "recently rotated" rot immediately. Record absolute timestamps and certificate serials.
- Expected output that is vague ("looks healthy") cannot distinguish success from silent failure. Show a real sample and the acceptance threshold.
- Rollback that reuses the broken deployment path fails at the worst moment. Stage an independent artifact, previous digest, or failover.
- Stale escalation contacts turn an incident into a search. Test paging quarterly and include a backup contact.
- Runbooks written in prose get skipped. Use numbered steps, one action per step, and commands that can be pasted.
- A runbook verified only on an empty staging cluster misses data volume and quota limits. Exercise it against production-sized state or a canary.
- Procedures that exceed the alert response window need automation, not a longer runbook. Convert repeated multi-step sequences into a reviewed script.
- Internal hostnames and customer identifiers leak in screenshots. Redact them and store evidence in the access-controlled incident system.

## Output contract

```yaml
runbook:
  title: string
  service: string
  owner: string
  scope: string
  version: string
  last_verified: YYYY-MM-DD
  review_due: YYYY-MM-DD
preconditions:
  - check: string
    command: string
    expected: string
triggers:
  - alert: string
    decision: string
    section: string
procedure:
  - step: integer
    action: string
    command: string
    expected: string
    duration: string
    on_failure: string
    destructive: boolean
rollback:
  - step: integer
    command: string
    time_budget: string
    verification: string
verification:
  - check: string
    query: string
    pass: string
escalation:
  - condition: string
    contact: string
    channel: string
evidence:
  dry_run_by: string
  dry_run_date: string
  rollback_rehearsed: boolean
  reviewers: [string]
```

## Checklist

- [ ] Owner team, scope, version, and review date recorded.
- [ ] Triggers mapped to sections and decision rules.
- [ ] Preconditions include verification commands and expected output.
- [ ] Every mutating command is parameterized and guarded.
- [ ] Destructive steps marked and approval-gated.
- [ ] Rollback defined for every mutation, with a time budget.
- [ ] Verification checks have explicit pass thresholds.
- [ ] Escalation contacts and paging triggers are current.
- [ ] Independent operator completed a timed dry run.
- [ ] Shell, Markdown, link, and secret checks pass.
- [ ] Review evidence stored and review date scheduled.

## Related skills

- `incident-postmortem-generation` for turning a confirmed incident procedure into owned follow-up actions.
- `container-log-diagnostics` for diagnosing the failure before the runbook codifies the fix.
- `linux-systemd-service-management` for host-level service operations and rollback.
- `technical-documentation-writing` for structure, audience, and verification sections in operational docs.
