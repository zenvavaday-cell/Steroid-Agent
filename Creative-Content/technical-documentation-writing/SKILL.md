---
name: technical-documentation-writing
description: Writes task-based technical documentation with prerequisites, examples, verification, and troubleshooting. Use for APIs, tools, and runbooks.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: creative-content
---

# Technical Documentation Writing

## Overview

Most bad technical documentation is written from memory. The author knows the product, skips the step that broke for a new user, and publishes a page that describes the interface instead of the task. Readers then open a support ticket or abandon the setup.

The discipline is to execute the task in a clean environment, capture the real output, and write down only what a reader needs to reach a verified end state. Every command in the published page should have been run at the stated version, and every prerequisite should be one the author actually needed.

## When to use

- Documenting an API endpoint, CLI command, SDK, or configuration option.
- Writing a how-to, quickstart, tutorial, or migration guide.
- Turning an operational procedure into a runbook that on-call staff can follow.
- Rewriting a page that generates repeat support tickets.
- Reviewing contributed documentation before merge.
- Do not use for marketing copy, release announcements, or speculative design docs; use a product or release brief instead.

## Workflow

### 1. Classify the document and the reader

| Type | Reader goal | Shape | Success test |
| --- | --- | --- | --- |
| Tutorial | Learn by doing, first success | Numbered lessons, one path | Reader completes a working example |
| How-to | Accomplish a specific task | Prerequisites, steps, verification | Task done in the reader's environment |
| Reference | Look up exact behavior | Tables, signatures, parameters | Correct answer in under 30 seconds |
| Explanation | Understand why it works | Prose, diagrams, tradeoffs | Reader can predict behavior |

Do not blend all four on one page. A reference table with a tutorial introduction and a troubleshooting essay serves none of them. Split the page, then link.

Record the reader's assumed knowledge: OS, shell, runtime version, permissions, and prior products. "Basic knowledge of Docker" is not testable; "can run `docker compose up` and read container logs" is.

### 2. Establish ground truth

Work in a clean environment, not your development machine.

```bash
docker run --rm -it --network host ubuntu:24.04 bash
# Inside the container, install only what the prerequisites claim is required.
apt-get update && apt-get install -y curl ca-certificates
curl --version
```

Capture for every command: the exact command, the full output (including warnings), the exit code, the version, and the elapsed time.

```bash
set -o pipefail
{ time mytool init --profile minimal; } > /tmp/init.log 2>&1
echo "exit=$?"
```

If a command needs elevated privileges, network access, or a paid account, say so in the prerequisites rather than hiding it in step 6.

### 3. Write the skeleton before the prose

```markdown
# Configure SSO for a self-hosted instance

One sentence: what the reader will have when finished.

## Prerequisites
- Version 4.2 or later (check: `app --version`)
- Admin role and a DNS name that resolves to the instance
- IdP metadata XML

## Steps
1. ...
2. ...
3. ...

## Verify
Command and expected output.

## Troubleshoot
| Symptom | Likely cause | Fix |

## Next steps
- Rotate the signing certificate
```

Write the verify section before the steps. If you cannot define observable success, the task is not ready to document.

### 4. Write one action per step

Rules:

- Start each step with an imperative verb: "Create", "Set", "Run".
- Put the command first, explanation after.
- Use angle-bracket placeholders and define each one in a table.
- Never use `$` prompts in copy-paste blocks; they break paste and confuse Windows readers.
- Keep output in a separate fenced block from the command.
- Tag every fence with a language: `bash`, `json`, `yaml`, `http`, `text`.

````markdown
1. Create the service account and capture the token.

   ```bash
   app admin service-account create --name sso-broker --role reader
   ```

   Expected output starts with `created service account sso-broker` and includes a token. Store it in your secret manager; it is shown once.

2. Configure the issuer URL.

   ```bash
   app config set sso.issuer "https://<idp-host>/realms/<realm>"
   ```

| Placeholder | Description | Example |
| --- | --- | --- |
| `<idp-host>` | Hostname of the identity provider | `login.example.com` |
| `<realm>` | Realm or tenant name | `acme-prod` |
````

### 5. Test every code sample

Copy each block out of the rendered page, not from the source file, and run it. Check line wrapping, quote characters, and hidden characters. For API examples, run them against a live or mocked server and show the real status code and response body.

```http
POST /v1/tokens HTTP/1.1
Host: api.example.com
Content-Type: application/json

{"grant_type": "client_credentials"}
```

```json
{"access_token": "<token>", "expires_in": 3600}
```

Pin versions in install commands. `latest` makes a page expire without anyone editing it.

### 6. Document failure from real errors

Collect the actual error strings, exit codes, and log lines from step 2. Group them by cause, not by wording. Write the fix as a command or a decision.

| Symptom (verbatim) | Cause | Fix | Escalate if |
| --- | --- | --- | --- |
| `x509: certificate signed by unknown authority` | Private CA not trusted | Mount the CA bundle at `/etc/ssl/certs/ca.pem` | The chain is valid but still rejected |
| Exit code 137 | OOM kill | Raise memory to 2 GiB or reduce batch size | It recurs at 8 GiB |

If you cannot reproduce an error, label the entry as reported and link the source. Never invent an error message.

### 7. Review in docs-as-code and re-run

Run the repository's checks, then have someone who did not write the page follow it.

```bash
markdownlint-cli2 "docs/**/*.md"
vale docs/
npx lychee --no-progress docs/
mkdocs build --strict
```

Record the reviewer, environment, elapsed time, and every point where they paused or backtracked. Those pauses are documentation defects, not reader defects.

## Validation

| Gate | Check | Pass criterion | Fail action |
| --- | --- | --- | --- |
| Executability | Every command run in a clean environment | 100 percent exit 0, or documented expected failure | Fix command or prerequisites |
| Placeholders | Every `<...>` appears in the placeholder table | Zero undefined placeholders | Add definitions |
| Output accuracy | Published output matches captured output | Byte-identical except redacted secrets | Re-capture, do not retype |
| Links | Link checker on the built site | Zero 4xx or 5xx | Fix or remove |
| Build | Strict site build | No warnings treated as errors | Fix before merge |
| Task success | Independent reader follows the page | Completes without help in the stated time | Revise confusing steps |
| Version | Prerequisites state a tested version | One exact version plus supported range | Add and retest |

```bash
# Balanced fences and language tags
python3 - <<'PY'
from pathlib import Path
text = Path("docs/sso.md").read_text()
assert text.count("```") % 2 == 0, "unbalanced fences"
for i, line in enumerate(text.splitlines(), 1):
    if line.startswith("```") and line.strip() == "```":
        print("missing language tag at line", i)
PY
```

## Gotchas

- Writing from memory skips the prerequisite that blocks new users. Run the task in a fresh container.
- "Simply" and "just" hide steps. Delete both words and describe the action.
- Retyped output drifts from reality. Paste captured output and redact secrets with a consistent marker.
- Unpinned versions expire silently. State the tested version and the supported range.
- Screenshots of UI change every release. Prefer text steps; caption screenshots with the version.
- Multiline copy-paste blocks with shell prompts fail on paste. Remove `$` and `#` prompts from commands.
- Unix assumptions break Windows readers. State the shell or provide both forms.
- Error tables list wording, not causes. Group by cause and include exit codes.
- Pages describe menus instead of tasks. Lead with the outcome and the command.
- Undefined placeholders cause literal `<your-token>` errors. Always include the placeholder table.
- Hidden prerequisites (admin role, DNS, paid plan) surface as support tickets. Put them first.
- Docs rot after release. Add an owner and a last-verified date, and re-run the task each minor release.

## Output contract

```json
{
  "doc": {
    "path": "docs/sso.md",
    "type": "how-to",
    "title": "Configure SSO for a self-hosted instance",
    "audience": "instance administrators",
    "tested_version": "4.2.1",
    "last_verified": "2026-11-20"
  },
  "prerequisites": [{"item": "admin role", "check": "app whoami --role", "notes": "..."}],
  "steps": [{"number": 1, "action": "Create the service account", "command": "app admin service-account create ...", "expected": "...", "placeholders": ["<name>"]}],
  "verification": {"command": "app sso status", "expected_output": "sso: active", "failure_action": "..."},
  "troubleshooting": [{"symptom": "verbatim error", "cause": "...", "fix": "...", "escalate_if": "..."}],
  "evidence": {"environment": "ubuntu:24.04", "run_at": "2026-11-20T10:00Z", "exit_codes": [0, 0, 0], "reviewer": "..."},
  "links_checked": {"broken": 0, "checked": 24}
}
```

## Checklist

- [ ] Document type and reader assumptions stated.
- [ ] Task executed in a clean environment at a named version.
- [ ] Commands and outputs captured, not retyped.
- [ ] Skeleton includes prerequisites, steps, verify, troubleshoot, next steps.
- [ ] Verify section defines observable success before steps are written.
- [ ] One action per step, imperative voice.
- [ ] Every placeholder defined in a table.
- [ ] Every code fence has a language tag and balanced markers.
- [ ] Versions pinned and supported range stated.
- [ ] Error entries use real strings and exit codes.
- [ ] Link check and strict build pass.
- [ ] Independent reader completed the task and pauses were fixed.

## Related skills

- `brand-voice-consistency` for terminology and tone rules in user-facing help content.
- `operational-runbook-generation` for on-call procedures with rollback and escalation.
- `api-contract-validation` for verifying documented request and response shapes against the spec.
