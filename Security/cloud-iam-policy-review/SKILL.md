---
name: cloud-iam-policy-review
description: Reviews IAM policies for wildcards, privilege escalation, cross-account trust, and least privilege. Use for AWS, GCP, and Azure access reviews.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: security
---

# Cloud IAM Policy Review

## Overview

Cloud IAM is the real perimeter. A single permissive policy can expose every bucket, function, and database in an account. Effective permissions come from the union of identity policies, resource policies, permissions boundaries, organization policies, and session policies, with explicit deny winning everywhere.

A review is not a search for asterisks. It is a reconstruction of what a principal can actually do, including combinations of individually harmless permissions that together allow privilege escalation or cross-account access.

## When to use

- Reviewing a new role, service account, or managed identity before deployment.
- Auditing production accounts on a quarterly or annual access review.
- Investigating a suspected credential compromise or unusual API activity.
- Preparing least-privilege remediation after an incident.
- Onboarding a vendor or cross-account integration.
- Do not use to design application authorization inside a service; use `threat-model-generation` for that.

## Workflow

### 1. Scope the review

Record the organization, accounts, projects, or subscriptions, the principals in scope, the resources they touch, the review period, and the policy sources considered. Include humans, CI roles, service accounts, and third-party principals.

Exclude break-glass accounts from automated changes, but review their trust policy and alerting.

### 2. Collect every policy layer

```bash
# AWS
aws iam get-account-authorization-details > authz.json
aws organizations list-policies --filter SERVICE_CONTROL_POLICY > scps.json
aws accessanalyzer list-analyzers
aws iam list-roles --query 'Roles[].{name:RoleName,trust:AssumeRolePolicyDocument}'

# GCP
gcloud projects get-iam-policy PROJECT_ID --format=json > iam.json
gcloud organizations get-iam-policy ORG_ID --format=json > org-iam.json
gcloud iam roles describe ROLE_ID --project PROJECT_ID

# Azure
az role assignment list --all --include-inherited -o json > assignments.json
az role definition list -o json > roles.json
```

Collect resource policies too: S3 bucket policies, KMS key policies, SNS/SQS policies, ECR policies, and secret policies. A resource policy can grant access that no identity policy allows.

### 3. Compute effective permissions

For each principal, evaluate in order: explicit deny, organization policy or SCP, permissions boundary, session policy, identity allow, resource policy allow. Deny at any layer wins.

```bash
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::111122223333:role/api \
  --action-names s3:GetObject s3:PutObject iam:PassRole \
  --resource-arns arn:aws:s3:::customer-uploads/report.pdf
```

For GCP, test with `gcloud policy-tester` or the IAM Policy Troubleshooter. For Azure, use `az role assignment list` plus the effective permissions for the signed-in principal.

### 4. Detect the high-risk patterns

| Pattern | Example | Why it matters |
| --- | --- | --- |
| Full wildcard | `Action: "*"`, `Resource: "*"` | Unbounded access, including future services |
| Service wildcard | `s3:*`, `iam:*` | Often includes delete and policy changes |
| `NotAction` allow | Allow all except `iam:*` | Grants everything else, including new APIs |
| Escalation pair | `iam:PassRole` plus `lambda:CreateFunction` | Run code as a more privileged role |
| Policy self-modification | `iam:CreatePolicyVersion`, `iam:AttachUserPolicy` | Principal can grant itself more access |
| Public trust | `Principal: "*"` on `sts:AssumeRole` | Anyone can assume the role if conditions are weak |
| Cross-account root trust | Account root without `aws:PrincipalArn` | Any principal in the other account can assume |
| Public storage | `s3:GetObject` with `Principal: "*"` | Anonymous data exposure |
| Basic GCP roles | `roles/owner`, `roles/editor` | Thousands of permissions, no review |
| Azure broad scope | `Owner` at subscription or management group | Includes access control administration |

Privilege escalation also comes from `iam:UpdateAssumeRolePolicy`, `iam:PutRolePolicy`, `iam:CreateAccessKey`, `iam:CreateLoginProfile`, `lambda:UpdateFunctionCode`, `glue:UpdateDevEndpoint`, and `sts:AssumeRole` chains. Evaluate pairs and chains, not single actions.

### 5. Review trust policies and cross-account access

For every assumable role, check the principal, the conditions, and the confused-deputy defenses.

```json
{
  "Effect": "Allow",
  "Principal": {"AWS": "arn:aws:iam::111122223333:root"},
  "Action": "sts:AssumeRole",
  "Condition": {
    "StringEquals": {"sts:ExternalId": "customer-specific-value"},
    "ArnLike": {"aws:PrincipalArn": "arn:aws:iam::111122223333:role/deployer"}
  }
}
```

Require `sts:ExternalId` for third parties, `aws:SourceAccount` and `aws:SourceArn` for service trust, and `aws:PrincipalOrgID` to limit access to the organization. Reject trust to `"*"` unless an `aws:PrincipalArn` or network condition narrows it.

### 6. Remediate toward least privilege

Rewrite permissive statements with explicit actions, resource ARNs, and conditions. Generate a policy from observed access with Access Analyzer, then remove unused actions after a full observation window.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::app-uploads/${aws:PrincipalTag/tenant}/*",
      "Condition": {"Bool": {"aws:SecureTransport": "true"}}
    }
  ]
}
```

Apply changes in non-production first. Keep the previous policy version so rollback is one command.

### 7. Add guardrails and monitoring

- Deny dangerous actions in an SCP: `iam:CreateUser`, `iam:CreateAccessKey`, `organizations:LeaveOrganization`, and public bucket ACLs.
- Enforce GCP organization policies for domain-restricted sharing and service account key creation.
- Enable Access Analyzer, GCP IAM Recommender, and Azure Advisor, and route findings to a queue.
- Alert on policy changes, new trust policies, and `AssumeRole` from unexpected networks.
- Re-review on a schedule, after role changes, and on employee or vendor offboarding.

## Validation

- Every changed policy has a simulation test showing an allowed action and a denied action.
- No identity policy grants `Action: "*"` with `Resource: "*"` outside documented break-glass roles.
- Break-glass roles require MFA, have an owner, and raise an alert on use.
- Cross-account trust has an ExternalId, SourceArn, PrincipalArn, or OrgID condition as applicable.
- Access Analyzer reports no new public or cross-account findings after remediation.
- Unused permissions are removed or justified from service last-accessed data.
- Rollback is tested by restoring the prior policy version.
- A second reviewer compares the intended access with the effective access.

## Gotchas

- `NotAction` with `Effect: Allow` grants everything except the listed actions. It is usually a mistake.
- SCPs and organization policies filter permissions but never grant them. An Allow there does nothing alone.
- A permissions boundary caps identity policies but does not grant access.
- Resource policies can grant cross-account access even when the identity policy has no allow.
- `Principal: "*"` with a weak condition is still public. Test the condition against an anonymous request.
- `iam:PassRole` is harmless alone and critical with compute or function creation. Review combinations.
- Access Analyzer covers resource policies and some unused access; it does not find every identity escalation path.
- Service last-accessed data is delayed. Do not strip permissions on day one of observation.
- GCP basic roles include thousands of permissions and change over time. Replace them with predefined or custom roles.
- Azure assignments inherited from a management group are easy to miss in a subscription view.
- Wildcards in `Resource` match more than expected across partitions, regions, and accounts.
- MFA conditions apply only to some API calls unless you enforce them on every sensitive action.
- Policy size limits force statement splitting. Test the merged policy, not just the source file.
- Deleting a role does not delete its access keys or active sessions. Revoke sessions explicitly.

## Output contract

```json
{
  "scope": {"provider": "aws", "accounts": ["111122223333"], "reviewed_at": "2026-11-20"},
  "principals_reviewed": 42,
  "findings": [
    {
      "id": "IAM-001",
      "severity": "critical",
      "principal": "arn:aws:iam::111122223333:role/build",
      "policy": "build-deploy",
      "issue": "iam:PassRole on * combined with lambda:CreateFunction",
      "evidence": "simulate-principal-policy allows both actions",
      "escalation_path": "create function with admin role, invoke it",
      "remediation": "scope PassRole to arn:aws:iam::111122223333:role/app-runtime and add a permission boundary",
      "owner": "platform",
      "due": "2026-11-27",
      "status": "open"
    }
  ],
  "trust_findings": [
    {
      "role": "arn:aws:iam::111122223333:role/vendor-sync",
      "issue": "cross-account trust without ExternalId",
      "remediation": "require sts:ExternalId and aws:PrincipalArn",
      "owner": "integrations",
      "due": "2026-12-04"
    }
  ],
  "validation": {"allowed_test": "s3:GetObject on own prefix", "denied_test": "s3:GetObject on another prefix", "passed": true},
  "exceptions": [{"finding": "IAM-007", "reason": "break-glass", "owner": "ciso", "expires": "2027-01-31"}]
}
```

## Checklist

- [ ] Accounts, projects, subscriptions, and principals scoped.
- [ ] Identity, resource, boundary, SCP, and organization policies collected.
- [ ] Effective permissions computed per principal, deny considered first.
- [ ] Wildcards and `NotAction` statements inventoried.
- [ ] Privilege escalation pairs and chains evaluated.
- [ ] Cross-account trust policies reviewed for confused deputy.
- [ ] Public and anonymous access paths tested.
- [ ] Least-privilege rewrites applied in non-production first.
- [ ] Policy simulator tests pass for allow and deny cases.
- [ ] Access Analyzer and IAM Recommender findings cleared or accepted.
- [ ] Guardrail SCPs and org policies enforce the baseline.
- [ ] Rollback version recorded and tested.

## Related skills

- `threat-model-generation` to map identity boundaries into the system threat model.
- `security-control-mapping` to attach IAM evidence to SOC 2 or ISO 27001 controls.
- `secrets-scanning-remediation` when long-lived keys or leaked credentials drive the review.
- `container-image-hardening` for the workload identity and runtime trust boundary.
