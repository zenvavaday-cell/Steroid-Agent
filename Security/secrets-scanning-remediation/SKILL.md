---
name: secrets-scanning-remediation
description: Finds leaked credentials, contains exposure, and plans rotation without logging secret values. Use for repository, CI, and cloud secret hygiene.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: security
---

# Secrets Scanning and Remediation

## Overview

A leaked credential is a live incident, not a lint warning. The only reliable fix is to revoke or rotate the credential and assume it was used. Deleting the file, amending the commit, or forcing a push removes the visible copy, not the exposure.

The second discipline is handling: never print, paste, or ticket the secret value. Work from a fingerprint, a location, and a provider scope. A remediation that leaks the secret again into chat, logs, or the incident record has made the problem worse.

## When to use

- Auditing repositories, commit history, CI logs, and build artifacts for credentials.
- Responding to a provider alert, a public disclosure, or a scanner finding.
- Cleaning up a repository before open-sourcing or transferring ownership.
- Reviewing secret hygiene after an acquisition or vendor handover.
- Adding preventive controls such as pre-commit hooks and push protection.
- Do not use for reviewing application authorization logic; use `threat-model-generation` or `cloud-iam-policy-review` instead.

## Workflow

### 1. Authorize and scope

Get written authorization before scanning history or production systems. Define the repositories, organizations, CI systems, artifact stores, container registries, and cloud accounts in scope, plus the retention period for findings.

If the credential is live in production, open a security incident immediately and notify the credential owner. Do not wait for the full scan to finish.

### 2. Scan with redaction enabled

Run at least two engines: pattern rules and verified-provider checks. Always enable redaction so the report does not become a new leak.

```bash
gitleaks detect --source . --report-format json --report-path gl.json --redact --verbose
gitleaks git --log-opts="--all" --report-format json --report-path gl-history.json --redact

trufflehog git file://. --only-verified --json > th.json

detect-secrets scan --all-files --exclude-files 'vendor/.*' > .secrets.baseline
trufflehog filesystem . --only-verified --json > fs.json
```

Scan the full history (`--log-opts="--all"`), not only the working tree. CI logs and artifacts need separate collection with access controls.

### 3. Triage without exposing the value

For each hit, record the file, commit, line, rule ID, provider, and a fingerprint: `sha256(value)` truncated to 16 hex characters plus the last four characters for human recognition. Never record the full value.

Determine liveness with a provider metadata or read-only API call from a controlled host, or by checking the provider console for last use. Do not paste the credential into a web tool, chat, or ticket.

| Question | Evidence to record |
| --- | --- |
| Is it a real credential? | Provider response code, no secret in output |
| What can it access? | Scope or role name, account or project ID |
| Is it live? | Provider status, last-used timestamp |
| Was it used by anyone else? | Provider audit log for the exposure window |
| When was it first exposed? | Earliest commit or log timestamp |

### 4. Contain first

For a confirmed live credential, revoke or disable it before cleaning anything. Revocation is the control that stops abuse; history rewriting is hygiene. Preserve the commit hash, file path, fingerprint, and timestamps as evidence.

Review provider audit logs for the exposure window: source IPs, user agents, API calls, and data access. If the credential could read customer data, treat it as a data incident and involve legal and privacy owners.

### 5. Rotate in a safe order

Use this order so the application does not break and the old credential stops working:

1. Create the replacement credential with the same or narrower scope.
2. Store it in the secret manager, not in the repository or CI variables.
3. Deploy the new version and verify the application health check.
4. Revoke the old credential and confirm the provider rejects it.
5. Monitor for errors and unexpected use for at least 24 hours.

Where the provider supports overlapping validity, keep both for the shortest possible window and alert on use of the old one.

### 6. Remove from history and caches

```bash
# Inspect before rewriting
git log --all --oneline -- path/to/leaked.env

# Remove a file from all history
git filter-repo --path path/to/leaked.env --invert-paths

# Or replace specific strings from a rules file kept outside the repo
git filter-repo --replace-text ../redactions.txt
```

Coordinate a freeze, force push, and re-clone. Ask the hosting provider to purge cached views, invalidate forks and pull request refs, and clear CI log retention. Open pull requests and local clones keep the old objects until refreshed.

### 7. Prevent recurrence

- Enable provider push protection and organization-level secret scanning.
- Add a pre-commit hook and a CI gate that blocks on verified findings.
- Move all credentials to a secret manager with short-lived tokens where possible.
- Use OIDC federation for CI instead of long-lived cloud keys.
- Add `.env`, key material, and credential patterns to `.gitignore`.
- Require a canary test: commit a fake matching token in a scratch branch and confirm the gate blocks it, then delete the branch.

### 8. Verify and close

Re-scan the full history and the current tree. Confirm zero verified findings for the revoked credential. Confirm the old credential fails authentication. Close provider alerts and record the incident timeline without secret values.

## Validation

- No secret value appears in the report, ticket, chat, commit message, or incident record.
- Revocation is confirmed by a provider response, not by assumption.
- The old credential fails an authentication attempt after rotation.
- Application health checks pass with the new credential.
- Full-history re-scan returns zero verified findings for the credential.
- Provider audit logs for the exposure window have been reviewed.
- Pre-commit and CI gates are enabled and passed a canary test.
- Forks, mirrors, caches, and CI logs were addressed or explicitly accepted.

## Gotchas

- Deleting the file or amending the latest commit leaves the secret in earlier history.
- A force push does not remove GitHub cached views, forks, or attached pull request refs.
- CI logs and artifacts often capture environment variables and command output. Rotate regardless.
- A "test" key can still read or write production data. Check the scope, not the label.
- Base64, hex, or encrypted blobs in config files can hide credentials from pattern rules.
- Public repositories are scraped within minutes. Assume any pushed live credential was used.
- Rewriting history breaks open pull requests and every developer clone. Announce a freeze.
- Secrets copied into a container layer remain in the image even if deleted in a later layer.
- `--redact` still writes file paths and surrounding context. Store reports with restricted access.
- A scanner that misses a nonstandard token format is not evidence of absence. Review high-entropy strings manually.
- Rotating before revoking leaves two valid credentials and widens the window.
- `.gitignore` does not stop `git add -f` or a CI job that copies the file.

## Output contract

```json
{
  "incident_id": "SECRET-2026-014",
  "status": "contained",
  "scope": {"repos": ["example/api"], "ci": ["github-actions"], "cloud": ["aws:111122223333"]},
  "findings": [
    {
      "id": "S-001",
      "provider": "aws",
      "type": "access_key",
      "fingerprint": "sha256:9f2c41ab77de0012:last4=K9QZ",
      "location": "config/prod.env",
      "first_commit": "a1b2c3d",
      "first_seen": "2026-09-02T14:11:00Z",
      "live": true,
      "scope": "s3:GetObject on customer-uploads",
      "exposure_window_hours": 62,
      "used_by_unknown_principal": false,
      "action": "revoked",
      "revoked_at": "2026-11-20T09:40:00Z",
      "replacement": "secret-manager:prod/api/s3-reader",
      "verified": true
    }
  ],
  "history_rewrite": {"method": "git filter-repo", "commits_affected": 14, "force_push_at": "2026-11-20T18:00:00Z"},
  "prevention": ["push protection enabled", "gitleaks pre-commit hook", "OIDC replaces static keys"],
  "open_items": [{"item": "fork purge pending", "owner": "platform", "due": "2026-11-27"}]
}
```

## Checklist

- [ ] Written authorization and scope recorded.
- [ ] Two scanners run with redaction on the working tree and full history.
- [ ] CI logs, artifacts, and container layers included in scope.
- [ ] Findings recorded by fingerprint, never by value.
- [ ] Liveness and scope confirmed through provider APIs.
- [ ] Live credentials revoked or disabled first.
- [ ] Provider audit logs reviewed for the exposure window.
- [ ] Replacement created, deployed, and health-checked.
- [ ] Old credential confirmed rejected.
- [ ] History rewritten and caches, forks, and PR refs addressed.
- [ ] Preventive controls enabled and canary-tested.
- [ ] Full re-scan clean and incident closed with evidence.

## Related skills

- `security-incident-response` to run containment and evidence handling for a live exposure.
- `supply-chain-security-review` to assess build and release credential risk.
- `vulnerability-triage` to prioritize related findings across the estate.
- `linux-user-group-administration` to rotate host keys and review access after exposure.
