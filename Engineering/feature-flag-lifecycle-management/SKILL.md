---
name: feature-flag-lifecycle-management
description: Audits flags, plans staged rollouts, and removes stale flag code safely. Use for release management and flag debt reduction.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: engineering
---

# Feature Flag Lifecycle Management

## Overview

A feature flag is a temporary decision point with a permanent cost: extra branches, a larger test matrix, and a second source of truth for behavior. Flags fail in two directions. A rollout without guardrails exposes all users to a broken path, and a flag that outlives its purpose becomes flag debt that nobody dares remove.

The discipline is a closed lifecycle: inventory, classify, assign an owner and expiry, roll out in stages with measured gates, then delete the flag and its dead branch. Every flag has a named owner and a removal date from the day it is created.

## When to use

- Auditing an existing flag inventory or reducing flag debt.
- Planning a staged release, canary, or percentage rollout.
- Designing a kill switch for a risky dependency or migration.
- Reviewing a flag change before production promotion.
- Cleaning up flags after a completed launch.
- Do not use for permanent configuration such as timeouts, quotas, or pricing tables; keep those in versioned configuration, not a flag service.

## Workflow

### 1. Build the inventory from code and provider

Search the repository for every SDK evaluation, then reconcile against the provider export. A flag in the provider with no code reference is dead configuration. A flag in code with no provider entry fails at evaluation time.

```bash
rg -n --hidden -g '!vendor' -g '!node_modules' \
  '\b(getFlag|isEnabled|variation|useFlag|evaluate|boolVariation)\(' .
```

Provider export example (LaunchDarkly API, substitute your project and token source):

```bash
curl -sS -H "Authorization: $LD_API_TOKEN" \
  "https://app.launchdarkly.com/api/v2/flags/$PROJECT?summary=true" \
  | jq -r '.items[] | [.key, .name, .creationDate, ._maintainer.email] | @tsv'
```

Record: key, type, default, environments, code references, owner, creation date, last evaluated, and current rollout percentage.

### 2. Classify each flag

The type determines the expected lifetime and the removal test.

| Type | Purpose | Typical lifetime | Removal criterion |
| --- | --- | --- | --- |
| Release | Hide unfinished work | Days to 2 sprints | 100% for 14 days, no rollback |
| Ops / kill switch | Disable a dependency in an incident | Months to years | Dependency retired or failure mode automated |
| Experiment | Measure a hypothesis | One experiment cycle | Decision recorded, variant promoted or discarded |
| Permission | Entitlement or plan gating | Long-lived | Product packaging changes |
| Migration | Switch between old and new paths | Until decommission | Old path removed and verified unused |

Kill switches and permission flags are not debt. Release, experiment, and migration flags are, once their decision is settled.

### 3. Assign ownership, expiry, and naming

Every flag needs one owning team, one tracking issue, one expiry date, and a cleanup ticket created at launch time. Use a key format that encodes purpose and year, for example `release_checkout_v2_2026q1`. Add metadata in the provider: `owner`, `ticket`, `expiry`, `type`.

```yaml
key: release_checkout_v2_2026q1
type: release
owner: checkout-team
ticket: PAY-1842
expiry: 2026-03-31
default: false
environments:
  production: false
  staging: true
```

Reject flags without an owner or expiry. An unowned flag cannot be safely removed because no one can confirm the intended behavior.

### 4. Design the rollout with explicit gates

Define stages, exposure, bake time, guardrail metrics, and stop conditions before the first increment. Example thresholds must be calibrated to the service baseline, not copied blindly.

| Stage | Exposure | Minimum bake | Advance if | Stop if |
| --- | --- | --- | --- | --- |
| Dark launch | Internal only | 1 day | No errors in evaluation logs | Evaluation exceptions above 0.1% |
| Canary | 1% of production | 24 h | Error rate within 0.2 pp of control | Error rate above baseline + 0.5 pp for 10 min |
| Early | 10% | 48 h | p95 latency within 5% of control | p95 above baseline + 20% |
| Broad | 50% | 48 h | Business KPI neutral or better | Support tickets double |
| Full | 100% | 14 days | No rollback requested | Any Sev-1 or Sev-2 tied to the flag |

Use consistent bucketing by a stable identifier, and exclude staff and test accounts from user-facing metrics.

### 5. Implement evaluation safely

- Choose fail-closed defaults for risky features and fail-open only for non-critical UI.
- Keep the evaluation context minimal: stable user or tenant key, plan, region, and explicit attributes. Never pass raw email, phone, or free-text PII.
- Cache flag values with a bounded TTL, for example 30 to 60 seconds, so a kill switch takes effect quickly.
- Evaluate once per request and pass the result down. Re-evaluating at multiple layers creates inconsistent behavior.
- Log the flag key, variation, and reason on the server, not the full context.
- Test both states in CI, and test the provider outage path.

```bash
for state in on off; do
  FLAG_CHECKOUT_V2=$state pytest -q tests/checkout || exit 1
done
```

### 6. Monitor, decide, and retire

Watch guardrails for the full bake period. Record the decision and its evidence in the tracking issue. When the flag reaches its terminal state, remove it in one reviewed change:

1. Set the winning variation as the only code path.
2. Delete the losing branch, provider flag, tests for the dead path, and stale config.
3. Update documentation and dashboards that reference the key.
4. Deploy and verify with the flag absent.
5. Archive the provider flag with a link to the decision.

```bash
rg -n 'release_checkout_v2_2026q1' .   # expect zero matches after cleanup
```

Keep a kill switch only while the failure mode it guards still exists, and document the retirement condition.

### 7. Run a recurring audit

Monthly, generate a stale report: flags older than 90 days that are at 0% or 100% in production, flags with no code reference, flags past expiry, and flags with no owner. Route each to its owner with a deadline. Track the count as a trend, not a one-time cleanup.

```bash
# Example: flags at a terminal percentage with no change in 90 days
curl -sS -H "Authorization: $LD_API_TOKEN" \
  "https://app.launchdarkly.com/api/v2/flags/$PROJECT?summary=true" \
  | jq -r '.items[] | select(.environments.production.on == true) | [.key, .creationDate] | @tsv'
```

## Validation

| Gate | Pass criterion | Evidence |
| --- | --- | --- |
| Inventory coverage | Every key evaluated at runtime exists in the inventory | Join telemetry keys against inventory, diff is zero |
| Metadata complete | 100% have owner, type, ticket, expiry | Inventory report |
| Both states tested | Test suite passes with flag on and off | CI matrix log |
| Rollout gates | Each stage has exposure, bake time, metric, and stop condition | Rollout plan reviewed |
| Kill switch drill | Disable takes effect within 5 minutes in staging | Timed drill record |
| Stale debt | No flag past expiry without a written exception | Monthly report |
| Cleanup complete | Zero code references, provider flag archived, tests pass | `rg` output and CI run |
| Access control | Production changes require approval and appear in audit log | Provider audit log |
| Privacy | No PII in evaluation context or logs | Code review and log sample |

A rollout that cannot name its guardrail metric and stop threshold is not ready to leave dark launch.

## Gotchas

- Bucketing on a mutable attribute such as plan or email changes the user's bucket mid-rollout. Use an immutable key and a stable salt.
- A provider default of `true` makes an outage enable the feature. Set defaults deliberately and test the fallback path.
- Removing a flag before all clients upgrade breaks old app versions that still send the key. Keep it until the minimum supported client version no longer evaluates it.
- Long client-side cache TTLs make a kill switch useless. Bound the TTL and force refresh on critical paths.
- Nested flags multiply the test matrix and hide interactions. Limit to one active release flag per code path.
- Reusing an experiment flag for a release contaminates the experiment data. Create a new flag and close the experiment.
- Stale flags in tests and fixtures survive code cleanup and keep the key alive. Search config, fixtures, and infrastructure code, not just application source.
- A flag evaluated in a batch job without a stable key produces random assignment. Derive the key from the job's entity ID.
- Provider outages with undefined behavior cause inconsistent reads across replicas. Pin the fallback per environment and monitor evaluation errors.
- Deleting a flag and its branch in the same deploy as a data migration removes the rollback path. Sequence cleanup after the migration window.
- Unowned flags are never safe to delete because no one can confirm intent. Assign ownership before cleanup, not after.

## Output contract

```yaml
flag:
  key: string
  type: release | ops | experiment | permission | migration
  owner: string
  ticket: string
  expiry: YYYY-MM-DD
  default: boolean
  environments: {staging: boolean, production: boolean}
rollout:
  stages:
    - name: string
      exposure: string
      bake_time: string
      advance_criteria: string
      stop_criteria: string
  guardrails:
    - metric: string
      baseline: string
      threshold: string
  bucketing_key: string
testing:
  on_state: string
  off_state: string
  outage_path: string
cleanup:
  code_references_removed: boolean
  provider_flag_archived: boolean
  tests_updated: boolean
  docs_updated: boolean
  verification_command: string
decision:
  outcome: string
  evidence: string
  date: YYYY-MM-DD
```

## Checklist

- [ ] Inventory reconciled between code and provider.
- [ ] Every flag classified by type.
- [ ] Owner, ticket, and expiry set for every flag.
- [ ] Rollout stages include exposure, bake time, and stop conditions.
- [ ] Bucketing uses a stable key with consistent salt.
- [ ] Flag on, flag off, and provider outage paths tested.
- [ ] Kill switch drill completed within its time target.
- [ ] Decision and evidence recorded in the tracking issue.
- [ ] Winning path made unconditional before code deletion.
- [ ] Cleanup verified with a zero-reference search.
- [ ] Stale-flag audit scheduled with an owner and deadline.

## Related skills

- `release-notes-generation` for communicating flag-gated changes to users after rollout.
- `dead-code-elimination` for removing the dead branch once a flag is retired.
- `ci-cd-failure-diagnosis` when a flag state explains a pipeline or environment failure.
- `incident-postmortem-generation` for reviewing incidents caused by flag configuration.
