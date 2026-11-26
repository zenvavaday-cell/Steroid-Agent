---
name: phishing-email-analysis
description: Analyzes headers, URLs, attachments, and indicators without executing payloads. Use for reported phishing and email gateway investigations.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: security
---

# Phishing Email Analysis

## Overview

Phishing analysis answers four questions: is the message malicious, what happens if a user interacts with it, who was affected, and what must be blocked or reset. The work is evidence handling first. Preserve the original message, verify its authentication and routing, and analyze links and attachments in an isolated environment.

Never execute a payload on an analyst workstation or open a link from the corporate network. A single click can confirm a target, install malware, or leak a session token. Static analysis plus a disposable sandbox is the default, and "no behavior observed" is not the same as benign.

## When to use

- A user reports a suspicious email and forwards it or attaches the original.
- An email gateway quarantines a message and you need a verdict.
- Multiple recipients report the same campaign and you need the blast radius.
- A business email compromise is suspected: payment change, gift cards, payroll diversion.
- You need to extract IOCs before blocking a sender, domain, URL, or hash.
- A message impersonates a brand, executive, or vendor and you must confirm or dismiss it.

Do not use for tuning marketing spam filters or bulk classification of newsletters; that belongs to mail operations, not incident analysis.

## Workflow

### 1. Acquire and preserve the original

Save the message as `.eml` or `.msg` from the mailbox or gateway, not as a forwarded copy. Forwarding rewrites headers and destroys the routing evidence you need.

```bash
sha256sum phish-2026-042.eml | tee phish-2026-042.eml.sha256
mkdir -p case/phish-2026-042 && cp phish-2026-042.eml case/phish-2026-042/
```

Record the reporter, recipient mailbox, received time, and case ID. Work from a copy and keep the original read-only.

### 2. Read routing and authentication headers

Headers are read from the bottom up. Each `Received` line was added by a server that handled the message, so the bottom-most line is closest to the sender. Only trust `Authentication-Results` added by your own gateway or mailbox provider; anything above that hop can be forged.

| Header | What it establishes |
| --- | --- |
| `Received` | Routing path, sending IP, timestamps |
| `Authentication-Results` | SPF, DKIM, DMARC, and compauth result at a trusted hop |
| `Return-Path` | Envelope sender, often different from `From` |
| `From` / `Reply-To` | Display identity and where replies actually go |
| `Message-ID` | Campaign clustering and deduplication |
| `DKIM-Signature` | Signing domain, selector, body hash |

```bash
python3 - <<'PY'
import email
from email import policy
msg = email.message_from_binary_file(open("phish-2026-042.eml", "rb"), policy=policy.default)
for h in ["From", "Reply-To", "Return-Path", "Subject", "Message-ID", "Date", "Authentication-Results"]:
    print(h, ":", msg.get_all(h))
PY

dig +short TXT example.com
dig +short TXT _dmarc.example.com
dig +short TXT selector._domainkey.example.com
```

Interpretation: SPF checks the envelope sender, DKIM checks a signing domain, DMARC aligns either with the `From` domain. A DMARC pass does not make the message benign; a compromised legitimate account passes every check.

### 3. Extract and evaluate URLs at rest

Defang every URL before writing it anywhere: `https://` becomes `hxxps://`, dots become `[.]`. Resolve shorteners and redirect chains from a dedicated analysis host or through a passive service, never from corporate egress.

```bash
grep -oE 'https?://[^"<> ]+' phish-2026-042.eml | sort -u | sed 's/^http/hxxp/; s/\./[.]/g'
```

Check domain age with RDAP or WHOIS, certificate history, and reputation. Compare the registrable domain against the impersonated brand, including hyphenation, added words, and Unicode homoglyphs. Prefer passive lookups (urlscan.io, VirusTotal) for confidential URLs; submitting a private link publishes it.

### 4. Inspect attachments without execution

```bash
sha256sum attachment.zip
file attachment.zip
7z l attachment.zip            # list only, do not extract
oleid suspicious.docm
pdfid suspicious.pdf
strings -n 8 suspicious.exe | head -50
```

Look for macro-enabled Office files, external template or OLE links, JavaScript in PDFs, double extensions, password-protected archives, and LNK or ISO files. Password-protected archives evade gateway scanning; obtain the password from the message body and open only inside the sandbox.

### 5. Detonate in an isolated sandbox

Use a disposable VM with a snapshot, no corporate credentials, no shared folders, and no route to production. Simulate internet services with INetSim or a controlled proxy, and capture packets, process creation, file writes, and registry or cron changes.

```bash
sudo tcpdump -i any -w case/phish-2026-042/traffic.pcap
```

Record the behavior, the dropped files and their hashes, and the C2 indicators. If no sandbox is available, complete static analysis and mark confidence as medium or low. Do not detonate on a host joined to the corporate directory.

### 6. Determine user impact

Reconcile the recipient list with mail logs and identity logs. For each recipient, establish delivered, opened, clicked, replied, and credentials entered.

- Mail: message trace by `Message-ID`, sender, subject, and URL domain.
- Identity: sign-in logs for the affected users, especially unfamiliar ASN, country, or device.
- Mailbox: new forwarding rules, delegation, send-as grants, and inbox rules that hide replies.
- Applications: OAuth consent grants, new MFA devices, password changes, and app passwords.
- Endpoint: proxy and DNS logs for the malicious domain, EDR alerts for downloaded files.

### 7. Contain, remediate, and report

Purge the message by `Message-ID`, hash, or sender; block the sender, reply-to domain, URL, and attachment hash; reset credentials for users who entered them; revoke sessions; and remove attacker-created mailbox rules. Notify affected users with what happened and what to do next, without blaming them.

Record the verdict (`malicious`, `suspicious`, `benign`, `inconclusive`), confidence, campaign cluster, IOCs with a block TTL, and the actions taken with timestamps.

## Validation

- Original message hash is recorded and matches the case evidence.
- SPF, DKIM, and DMARC results are reproduced from the trusted hop only.
- Every URL is defanged, and none was fetched from corporate egress.
- Every attachment is hashed; execution happened only in an isolated sandbox.
- Affected recipient count reconciles with mail logs, including clicks and credential entry.
- Purge count matches the search count, and messages are absent from mailboxes after the purge.
- Credential resets and session revocations are confirmed in identity logs.
- Blocks are tested from an isolated host and return the expected deny or sinkhole.

## Gotchas

- Forwarding the email rewrites headers and loses the original routing. Always export the original.
- DMARC can pass while the display name impersonates an executive or the account is legitimately compromised.
- `Authentication-Results` above your trusted gateway can be forged. Read from the bottom and trust one hop.
- Clicking a link from a corporate IP confirms the target and may serve benign content based on geography.
- Shorteners and open redirects hide the final destination. Follow the full chain, not the first hop.
- QR codes bypass URL rewriting and user training. Decode them in the sandbox.
- Password-protected archives evade scanning. Do not guess passwords or execute files to find out.
- HTML attachments can render a fake login form with no network indicator at all.
- Image-only email hides text from keyword filters and from simple text extraction.
- Sandboxes are detected by time, geography, and user interaction. No behavior is not proof of benign.
- Clearing one message does not clear the campaign. Search by sender, subject, hash, and URL across all mailboxes.
- Blocking a lookalike domain can break a legitimate partner. Verify ownership before a global block.
- Unsubscribe and tracking links confirm the address is live. Do not fetch them during analysis.

## Output contract

```json
{
  "case_id": "PHISH-2026-042",
  "verdict": "malicious",
  "confidence": "high",
  "message": {
    "sha256": "9f2c...",
    "subject": "Invoice overdue",
    "from": "billing@examp1e.com",
    "reply_to": "collect@example.net",
    "message_id": "<abc@examp1e.com>"
  },
  "authentication": {
    "spf": "fail",
    "dkim": "none",
    "dmarc": "fail",
    "trusted_hop": "mx-01.internal"
  },
  "urls": [
    {"defanged": "hxxps://examp1e[.]com/login", "final": "hxxps://drop[.]example/login", "classification": "credential_harvest"}
  ],
  "attachments": [
    {"name": "invoice.zip", "sha256": "1a2b...", "type": "zip", "behavior": "drops loader, beacons to cdn-sync.example"}
  ],
  "impact": {"recipients": 14, "delivered": 12, "clicked": 3, "credentials_entered": 1},
  "actions": ["purge", "block_domain", "reset_password", "revoke_sessions", "remove_mailbox_rule"],
  "iocs": [
    {"type": "domain", "value": "examp1e[.]com", "ttl": "90d"},
    {"type": "sha256", "value": "1a2b...", "ttl": "180d"}
  ],
  "owner": "soc@example.com",
  "reported_at": "2026-11-26T10:20:00Z"
}
```

## Checklist

- [ ] Original `.eml` saved and hashed.
- [ ] Reporter, recipients, and case ID recorded.
- [ ] Routing read bottom-up and trusted hop identified.
- [ ] SPF, DKIM, and DMARC results reproduced.
- [ ] URLs extracted, defanged, and resolved safely.
- [ ] Attachments hashed and inspected without execution.
- [ ] Sandbox detonation isolated from corporate network and credentials.
- [ ] Recipient impact reconciled with mail and identity logs.
- [ ] Mailbox rules and OAuth grants checked.
- [ ] Purge completed and verified.
- [ ] Blocks and credential resets applied and tested.
- [ ] Verdict, IOCs, and actions documented.

## Related skills

- `security-incident-response` for credential compromise and broader containment.
- `secrets-scanning-remediation` when the message exposes or harvests credentials.
- `prompt-injection-defense` when reported email content is later processed by an agent.
- `security-control-mapping` for evidence that email filtering and awareness controls operate.
