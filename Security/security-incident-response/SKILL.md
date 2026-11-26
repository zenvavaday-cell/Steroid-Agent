---
name: security-incident-response
description: Runs containment, eradication, recovery, and evidence handling for security incidents with clear command. Use for suspected breaches and malware events.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: security
---

# Security Incident Response

## Overview

An incident is a confirmed or credible loss of confidentiality, integrity, or availability. Response is a command problem under uncertainty: the first hour decides how much evidence survives and how far the attacker moves. Declare early, assign one incident commander, preserve before changing, contain at the smallest sufficient boundary, and do not close until eradication is verified.

The process scales with severity. A single phished mailbox and a domain-wide ransomware event use the same phases but different authority, cadence, and outside counsel involvement. Write the severity call down at declaration and revisit it as facts change.

## When to use

- An EDR, IDS, cloud guardrail, or user report indicates active attacker behavior.
- Credentials, tokens, or customer data appear in a public or untrusted location.
- Ransomware, destructive malware, or a suspicious mass file change is reported.
- A third party discloses that it exposed your data, systems, or credentials.
- A privileged account shows impossible travel, new MFA devices, or unexpected grants.
- You are running a tabletop exercise or validating an incident playbook.

Do not use for an unconfirmed scanner finding with no evidence of exploitation; triage it with `vulnerability-triage` first.

## Workflow

### 1. Declare severity and incident command

| Severity | Criteria (examples) | Response posture |
| --- | --- | --- |
| SEV1 | Confirmed breach of regulated or customer data, domain-wide ransomware, active destructive action | Full command, executive and legal engaged, 24/7 |
| SEV2 | Confirmed compromise of one host, account, or service with no evidence of broad spread | Full command, business-hours plus on-call |
| SEV3 | Credible suspicious activity, policy violation, or contained malware | Single lead, documented timeline |
| SEV4 | Low-impact event with no evidence of compromise | Ticket and monitor |

Record the incident ID, severity, commander, start time in UTC, and affected business services. The commander coordinates and does not operate tools. Assign an operations lead, a communications lead, a scribe, and a legal or privacy contact. In a small team one person may hold several roles, but the commander never works on a compromised host.

### 2. Preserve evidence before touching anything

Follow order of volatility: CPU and memory, network connections, running processes, temporary files, disk, remote logs, backups. Capture volatile state first and note every command you run.

```bash
date -u +%FT%TZ
hostname; uname -a; who
ps auxwwf
ss -tulpn
lsof -nP -i
sudo avml /evidence/$(hostname)-mem.lime
sudo dd if=/dev/sda of=/evidence/sda.img bs=4M status=progress conv=noerror,sync
sha256sum /evidence/* | tee /evidence/SHA256SUMS
```

For cloud workloads, snapshot every attached volume and export the control-plane audit log before cleanup. Record a chain of custody with file name, hash, collector, time, and storage location.

```text
EVID-014 | sda.img | sha256:9f2c... | A. Analyst | 2026-11-26T09:14Z | evidence-vault/IR-2026-014/
```

### 3. Scope and contain

Identify patient zero, the initial access vector, accounts and tokens used, lateral movement, and data touched. Containment is a tradeoff between stopping spread and losing visibility.

| Action | Speed | Evidence impact | Use when |
| --- | --- | --- | --- |
| Disable account and revoke sessions | Minutes | Low | Credential misuse, BEC, insider |
| EDR network isolation | Minutes | Low | Compromised endpoint, active C2 |
| Security group or VLAN isolation | Minutes | Medium | Cloud or network spread |
| Power off | Immediate | High, loses memory | Only if destructive malware is spreading |
| Reimage | Hours | Destroys local state | After imaging and scoping |

Disable access keys and revoke sessions rather than only changing passwords.

```bash
aws iam update-access-key --user-name svc-app --access-key-id AKIA... --status Inactive
```

Attach a deny policy conditioned on token issue time so existing sessions die:

```json
{"Version":"2012-10-17","Statement":[{"Effect":"Deny","Action":"*","Resource":"*","Condition":{"DateLessThan":{"aws:TokenIssueTime":"2026-11-26T00:00:00Z"}}}]}
```

For Microsoft 365, disable the account and revoke refresh tokens: `Update-MgUser -UserId user@example.com -AccountEnabled:$false` then `Revoke-MgUserSignInSession -UserId user@example.com`. Block confirmed command-and-control domains at egress and DNS, and preserve the proxy or firewall logs that prove the block.

### 4. Eradicate

Remove persistence and the initial access vector. Check each location explicitly:

- Linux: root and user cron, systemd units and timers, `~/.ssh/authorized_keys`, `/etc/ld.so.preload`, web shells, SUID changes, new local accounts.
- Windows: scheduled tasks, services, Run keys, WMI subscriptions, new local admins, malicious drivers.
- Identity: new IAM users and keys, OAuth consent grants, mailbox forwarding rules, federated trust changes, MFA device changes.
- Network: rogue VPN peers, DNS record changes, new exposed services, snapshot or share permissions.

```bash
crontab -l -u root
systemctl list-timers --all
find / -xdev -name authorized_keys -printf '%u %p\n' 2>/dev/null
aws iam list-users --query 'Users[?CreateDate>=`2026-11-01`]'
aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=CreateAccessKey
```

Rotate credentials in this order: identity provider sessions, SSO and federation secrets, cloud keys, CI/CD secrets, service passwords, then local accounts. Rotate from a clean workstation, not the suspect host.

### 5. Recover

Rebuild rather than clean for SEV1 and SEV2. Restore from a backup created before the earliest credible compromise, verify hashes against the backup manifest, patch the initial vector, re-enroll the host in EDR, and return traffic in stages. Define exit criteria before recovery starts: no IOCs in fresh telemetry for 14 days (adjust to the threat), no attacker re-entry, and business owner sign-off.

### 6. Communicate and notify

Use one channel, one scribe, and a fixed cadence: SEV1 every 60 minutes, SEV2 every 4 hours, SEV3 daily. Do not discuss incident details on a possibly compromised mailbox or chat tenant.

Notification clocks start at awareness, not confirmation. Examples: GDPR 72 hours for personal data breaches, SEC Form 8-K within 4 business days of a materiality determination, HIPAA 60 days, US state laws vary. Confirm every obligation with counsel and log the decision, the decision maker, and the timestamp.

### 7. Close with a postmortem

Hold a blameless review within 5 business days for SEV1 and SEV2. Cover the UTC timeline, impact, detection gap, containment gap, root cause, and what would have shortened each phase. Every action item needs an owner, a due date, and a tracker entry. Retain evidence and the incident record per policy and any legal hold.

## Validation

- Severity, commander, and declaration time are recorded before technical work starts.
- Memory was captured before reboot where feasible, and every evidence file has a hash and custodian.
- Containment is verified from an independent system: the account cannot authenticate and the attacker path is blocked.
- Eradication checklist is complete, credentials are rotated, and a fresh scan finds no known persistence.
- No IOCs appear in telemetry for the defined monitoring window.
- Restore integrity is verified against a hash manifest and the business owner signs off.
- Notification decisions are logged with legal or privacy review.
- Postmortem actions have owners, due dates, and tracking IDs.

## Gotchas

- Rebooting or powering off to "clean" a host destroys memory, running malware, and network state. Image first.
- Killing an implant as soon as it is found can tip off the attacker and lose the C2 address. Observe briefly, then contain.
- Resetting a password without revoking refresh tokens, sessions, and app passwords leaves the attacker logged in.
- Isolating one endpoint while cloud keys remain active is not containment. Cover identity and control plane too.
- Attacker-created mailbox rules and OAuth consent grants survive password resets. Inspect both.
- Responding from a compromised admin workstation can leak the response plan. Use clean access.
- Short log retention means the evidence is already gone. Export logs at declaration.
- Backups inside the same trust boundary may be encrypted or deleted. Verify age and integrity before relying on them.
- EDR isolation can block your forensic tooling and remote hands. Confirm an access path before enabling it.
- Clock skew between hosts corrupts the timeline. Normalize to UTC and record offsets.
- Legal privilege and notification clocks start at awareness. Involve counsel early.
- Absence of alerts is not proof of containment when telemetry was disabled or tampered with.

## Output contract

```yaml
incident:
  id: IR-2026-014
  severity: SEV2
  commander: a.analyst
  declared_at: 2026-11-26T09:00:00Z
  status: contained
  affected_assets:
    - host: web-03
      evidence: [sda.img, mem.lime]
  initial_access: exposed SSH key in public repository
  iocs:
    - type: domain
      value: cdn-sync.example
  containment:
    - action: EDR isolation
      at: 2026-11-26T09:40:00Z
      verified: true
  eradication:
    persistence_removed: [cron, authorized_keys]
    credentials_rotated: [svc-app, deploy]
  recovery:
    source: backup-2026-11-24
    integrity_verified: true
    monitoring_until: 2026-12-10
  notifications:
    - audience: privacy
      reason: possible personal data access
      at: 2026-11-26T10:15:00Z
  evidence:
    vault: evidence-vault/IR-2026-014/
    chain_of_custody: EV-014
  postmortem:
    due: 2026-12-03
    actions: 6
```

## Checklist

- [ ] Severity and incident commander recorded.
- [ ] Roles assigned: operations, communications, scribe, legal.
- [ ] Volatile evidence captured and hashed.
- [ ] Chain of custody started.
- [ ] Scope established: initial access, accounts, lateral movement, data.
- [ ] Containment applied and verified independently.
- [ ] Persistence removed across host, identity, and network.
- [ ] Credentials and sessions rotated.
- [ ] Recovery from a pre-compromise backup verified.
- [ ] Notification obligations reviewed and logged.
- [ ] Monitoring window defined and cleared.
- [ ] Postmortem scheduled with owned actions.

## Related skills

- `threat-model-generation` for identifying the attack paths that became incidents.
- `vulnerability-triage` for prioritizing the vulnerability that enabled initial access.
- `secrets-scanning-remediation` for containing and rotating exposed credentials.
- `incident-postmortem-generation` for turning the timeline into owned follow-up work.
