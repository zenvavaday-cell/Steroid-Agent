---
name: supply-chain-security-review
description: Assesses dependencies, build provenance, signatures, and SBOMs for supply-chain risk. Use for vendor onboarding and build-system assurance.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: security
---

# Supply Chain Security Review

## Overview

Supply-chain assurance asks two questions: who can modify what you ship, and can you prove it after the fact. Known CVEs are only one input. Provenance, signing identity, build isolation, maintainer trust, and dependency resolution decide whether an artifact is trustworthy even when no advisory exists.

A valid signature proves that a key signed an artifact, not that the artifact is safe or built from the claimed source. Treat every claim as unverified until the identity, digest, and build path line up.

## When to use

- Onboarding a vendor, library, container base image, or CI action.
- Adding a new direct dependency or upgrading a critical one.
- Reviewing build provenance or an SBOM before a release.
- After a public compromise of a package, registry, or maintainer account.
- Designing or auditing a release pipeline for a regulated product.
- Approving a private registry, mirror, or package proxy.

Do not use for routine CVE backlog prioritization; use `vulnerability-triage` or `dependency-vulnerability-auditing` for that.

## Workflow

### 1. Map the artifact and trust path

Write down the path from source to runtime and who can change each step:

| Stage | Artifact | Who can alter it | Evidence |
| --- | --- | --- | --- |
| Source | commit `abc123` | maintainers, admins | signed tag, branch protection |
| Build | workflow run | CI admins, workflow editors | provenance attestation |
| Package | image or archive digest | registry writers | signature, transparency log |
| Deploy | running workload | platform team | admission policy, digest pin |

Unpinned tags, shared CI runners, and registry write access held by many people are trust-path gaps regardless of scanner results.

### 2. Generate and check the SBOM

```bash
syft dir:. -o cyclonedx-json > sbom.cdx.json
syft registry:registry.example.com/app@sha256:... -o spdx-json > image.spdx.json
cdxgen -o sbom.cdx.json .
trivy sbom sbom.cdx.json
```

Check completeness against the lockfile, not just the component count:

```bash
jq '.components | length' sbom.cdx.json
jq -r '.components[].purl' sbom.cdx.json | sort -u | wc -l
```

Declare exclusions explicitly: vendored source, binary blobs, plugins loaded at runtime, and OS packages outside the image layer. An SBOM that covers 80 percent of the runtime without saying so is misleading.

### 3. Verify signatures against an expected identity

Never accept "Verified OK" alone. Pin the signer identity and issuer:

```bash
cosign verify \
  --certificate-identity "https://github.com/org/repo/.github/workflows/release.yml@refs/heads/main" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  registry.example.com/app@sha256:...

cosign verify-attestation --type slsaprovenance \
  --certificate-identity "https://github.com/org/repo/.github/workflows/release.yml@refs/heads/main" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  registry.example.com/app@sha256:...

gh attestation verify app.tar.gz --repo org/repo
gpg --verify app.tar.gz.sig app.tar.gz
```

Record the verified digest, identity, issuer, transparency log index, and verification time. A signature from a key you cannot attribute is not approval.

### 4. Evaluate provenance and build isolation

SLSA v1.0 Build levels describe how much the provenance can be trusted:

| Level | Requirement | Residual risk |
| --- | --- | --- |
| 1 | Build is scripted and provenance exists | Producer can fabricate provenance |
| 2 | Hosted build platform signs provenance | Platform or workflow compromise |
| 3 | Hardened, isolated, ephemeral build | Signing path and source compromise |

Inspect the attestation for source repository, source digest, builder ID, build parameters, and materials. Verify that the subject digest equals the digest you deploy. Provenance for a different build proves nothing.

### 5. Assess maintainers and package metadata

```bash
npm view package-name maintainers time repository dist.tarball scripts
pip index versions package-name
go list -m -json module/path
```

Review maintainer count and activity, recent ownership transfers, signed releases, 2FA enforcement, publish frequency changes, and install scripts. Check for typosquats with edit distance and Unicode confusables, not just visual inspection.

```python
def distance(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j-1] + 1, prev[j-1] + (ca != cb)))
        prev = cur
    return prev[-1]
```

A distance of 1 or 2 from a popular package, combined with a new publish date and no repository history, is a strong typosquat signal.

### 6. Review CI/CD and build configuration

```bash
grep -R "uses:" .github/workflows | grep -vE '@[0-9a-f]{40}'
grep -R "pull_request_target\|permissions:\|secrets\." .github/workflows
```

- Pin third-party actions to a full commit SHA, not a tag.
- Set `permissions:` to the minimum, default `contents: read`.
- Do not expose secrets to `pull_request_target` workflows that checkout untrusted code.
- Use OIDC federation to the registry instead of long-lived tokens.
- Keep build caches and self-hosted runners outside untrusted pull request scope.
- Protect release branches and require review for workflow changes.

### 7. Score, decide, and monitor

Score each dimension 0 (good) to 3 (bad): provenance, signature identity, maintainer resilience, dependency resolution, and build hardening. Sum the scores and apply a decision rule.

| Total | Decision | Required action |
| --- | --- | --- |
| 0 to 3 | Approve | Standard monitoring |
| 4 to 7 | Conditional | Pin digest, restrict egress, shorten review cycle |
| 8 or more | Reject | Replace, vendor, or escalate to risk owner |

Record conditions with an owner and expiry. Set re-review triggers: maintainer change, repository transfer, new install script, critical advisory, registry migration, or a failed reproducibility check.

## Validation

- Signature verification names the expected identity and issuer and exits 0.
- The verified digest and attestation subject match the deployed artifact.
- SBOM coverage meets the agreed threshold, with exclusions listed.
- Every third-party CI action is pinned to a 40-character commit SHA.
- Critical components have at least two active maintainers or a documented compensating control.
- The build is reproducible, the difference is explained, or an exception is approved.
- Decision, reviewer, date, and next review are recorded.
- Monitoring and re-review triggers are configured.

## Gotchas

- `cosign verify` without identity and issuer flags accepts any valid Sigstore signature. Always scope it.
- A valid signature says nothing about vulnerabilities, backdoors, or whether the source matches the binary.
- SLSA provenance can be produced by a compromised build platform. Level 3 reduces the risk, it does not remove it.
- SBOMs miss vendored code, binary blobs, and runtime plugins. State the scope.
- Tags are mutable. Pin images by digest and actions by commit SHA.
- Dependency confusion can resolve a private name to a public registry. Scope registries and credentials.
- Typosquats use hyphens, Unicode homoglyphs, and abandoned names, not only edit distance.
- Postinstall scripts run with build credentials. Use `npm ci --ignore-scripts` where the package allows it.
- A maintainer transfer or repository ownership change is a re-review trigger even with no diff.
- Lockfiles prevent drift only when CI uses `npm ci`, `pip install --require-hashes`, or `go mod verify`.
- Shared build caches across trust boundaries can poison artifacts without touching source.
- A signed git tag does not prove the release artifact came from that tag.

## Output contract

```json
{
  "artifact": "registry.example.com/app@sha256:...",
  "reviewed_at": "2026-11-26",
  "reviewer": "security@example.com",
  "trust_path": {
    "source": "github.com/org/repo",
    "builder": "GitHub Actions",
    "registry": "registry.example.com"
  },
  "sbom": {"format": "cyclonedx-json", "components": 412, "coverage": 0.96, "exclusions": ["vendored/zlib"]},
  "signature": {"verified": true, "identity": "...release.yml@refs/heads/main", "issuer": "token.actions.githubusercontent.com"},
  "provenance": {"slsa_build_level": 3, "source_digest": "abc123", "subject_digest": "sha256:...", "verified": true},
  "maintainers": {"count": 4, "bus_factor": 2, "recent_transfer": false, "install_scripts": false},
  "score": 3,
  "decision": "approve",
  "conditions": [],
  "next_review": "2027-05-26"
}
```

## Checklist

- [ ] Artifact and trust path mapped end to end.
- [ ] SBOM generated, scoped, and checked for completeness.
- [ ] Signature verified against a named identity and issuer.
- [ ] Attestation subject digest matches the deployed digest.
- [ ] Provenance and SLSA build level reviewed.
- [ ] Maintainer health and package metadata assessed.
- [ ] Typosquat and dependency confusion risks checked.
- [ ] CI actions pinned and permissions minimized.
- [ ] Build isolation and reproducibility reviewed.
- [ ] Risk score and decision recorded.
- [ ] Conditions have owners and expiry dates.
- [ ] Monitoring and re-review triggers configured.

## Related skills

- `dependency-vulnerability-auditing` for CVE coverage and remediation of the same inventory.
- `container-image-hardening` for reducing the runtime attack surface of approved images.
- `secrets-scanning-remediation` when build or registry credentials are exposed.
- `vulnerability-triage` for ranking exploitable findings inside the dependency set.
