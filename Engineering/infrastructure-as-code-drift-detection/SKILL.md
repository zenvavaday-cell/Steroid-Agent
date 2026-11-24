---
name: infrastructure-as-code-drift-detection
description: Detects and classifies differences between Terraform, OpenTofu, Pulumi, CloudFormation, or Kubernetes declarations and real cloud state, then reconciles safely. Use for drift audits, compliance evidence, post-incident checks, and scheduled infrastructure hygiene.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: engineering
---

# Infrastructure-as-Code Drift Detection

## Overview

Drift is any difference between the declared infrastructure and the real state. Some drift is harmless (cloud-added tags); some is dangerous (a manually opened security group). Detection is a plan plus a classification; reconciliation is a controlled apply, import, or removal.

Never `apply` a drift remediation blindly. Read the plan.

## When to use

- Scheduled drift audits.
- After an incident or manual hotfix.
- Before a release that depends on infrastructure state.
- Compliance evidence for configuration baselines.
- Migrating resources into or out of IaC.

## Workflow

### 1. Define scope and state

Identify:

- Repository, workspace, and state file.
- Cloud accounts, regions, and environments.
- Providers and versions.
- Resources intentionally managed outside IaC.

Lock the state backend and confirm you are targeting the right workspace. Applying a plan to the wrong account is a classic outage.

### 2. Refresh and plan

```bash
terraform init -input=false
terraform plan -refresh=true -detailed-exitcode -out=tfplan
```

Exit codes:

| Code | Meaning |
| --- | --- |
| 0 | No changes |
| 1 | Error |
| 2 | Changes present |

For OpenTofu, the command is the same with `tofu`. For Pulumi:

```bash
pulumi refresh --yes
pulumi preview --json > preview.json
```

### 3. Inspect the plan structurally

```bash
terraform show -json tfplan > plan.json
jq '.resource_changes[] | {
  address,
  actions: .change.actions,
  before: .change.before,
  after: .change.after
}' plan.json
```

Classify each change:

| Action | Meaning | Risk |
| --- | --- | --- |
| no-op | No difference | None |
| create | Resource missing in state | Check for duplicates |
| update in-place | Attribute drift | Depends on attribute |
| replace | Destroy and recreate | High; data loss possible |
| delete | Resource removed from config | High; confirm intent |
| read | Refresh only | Low |

### 4. Classify drift causes

- Manual console change.
- Another automation or controller (autoscaler, Kubernetes operator).
- Provider default or API normalization (tags, timestamps, ordering).
- Resource created outside IaC.
- Resource deleted outside IaC.
- Provider version change altering the schema.
- State corruption or a moved resource.

Expected drift should be encoded as `ignore_changes` or a documented exception, not manually reapplied every cycle.

### 5. Reconcile

| Situation | Action |
| --- | --- |
| Manual change should be permanent | Update code, then apply |
| Manual change should be reverted | Apply the code as-is |
| Resource exists but is unmanaged | Import, then plan |
| Resource deleted manually | Recreate or remove from state |
| Provider normalization | Add `ignore_changes` with a comment |
| Destructive replacement | Require approval and a migration plan |

Import example:

```bash
terraform import aws_s3_bucket.logs logs-bucket-name
terraform plan -refresh=true
```

### 6. Verify

- Re-run the plan; it should be empty or only explainable changes.
- Check the resource in the cloud console or API.
- Run smoke tests for the affected service.
- Record the before/after state and the approval.

### 7. Prevent

- Run a scheduled plan in CI and alert on drift.
- Restrict console write access; use break-glass with logging.
- Tag resources with owner and managed-by.
- Pin provider versions.
- Add policy checks (OPA, Checkov, tfsec) for dangerous changes.

## Gotchas

- `terraform plan` refreshes state but does not modify remote resources. A plan is safe to run; an apply is not.
- Provider versions can change the plan output without any real drift. Pin and upgrade deliberately.
- Cloud APIs add default tags, timestamps, and ordering. Use `ignore_changes` narrowly.
- Autoscaling groups, managed node groups, and Kubernetes controllers legitimately change desired counts. Do not fight the controller.
- `-detailed-exitcode` returns 2 for any change, including harmless ones. Parse the plan.
- State can be stale or locked. Check the lock owner before forcing unlock.
- Secrets may appear in plan output. Restrict access and redact logs.
- Importing a resource does not generate configuration. Write the code to match, then plan.
- Deleting a resource from config may destroy data. Check `prevent_destroy` and backups.
- Cross-account or cross-region dependencies can make a plan succeed but an apply fail.

## Output contract

```json
{
  "scope": {"repo": "...", "workspace": "prod", "account": "123456789012", "region": "us-east-1"},
  "plan_exit_code": 2,
  "summary": {"create": 1, "update": 3, "replace": 0, "delete": 1},
  "findings": [
    {
      "address": "aws_security_group.api",
      "action": "update",
      "attribute": "ingress",
      "before": "443 from 10.0.0.0/8",
      "after": "443 from 0.0.0.0/0",
      "cause": "manual console change",
      "risk": "high",
      "recommendation": "revert and require change request"
    }
  ],
  "decision": "revert",
  "approved_by": "..."
}
```

## Checklist

- [ ] Scope, workspace, account, and region confirmed.
- [ ] State lock and backend verified.
- [ ] Plan generated with refresh.
- [ ] Plan parsed structurally.
- [ ] Changes classified by action and cause.
- [ ] Expected drift documented.
- [ ] Reconciliation path chosen.
- [ ] Verification plan and approval recorded.
- [ ] Scheduled drift detection in place.

## Related skills

- `automated-pull-request-review` for reviewing IaC changes.
- `ci-cd-failure-diagnosis` for pipeline failures around apply.
- `human-in-the-loop-escalation` before destructive infrastructure changes.
