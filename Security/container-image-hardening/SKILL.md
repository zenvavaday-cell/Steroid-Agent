---
name: container-image-hardening
description: Reduces image attack surface with minimal bases, non-root users, dropped capabilities, and scan gates. Use for Dockerfile reviews and registry policy.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: security
---

# Container Image Hardening

## Overview

A container image is a shipped filesystem plus a process contract. Every package, shell, and build tool in it is attack surface that an intruder can use after the first foothold. Hardening means fewer files, no root, no added capabilities, and a verifiable chain from source to registry.

The build and the runtime both matter. A perfect Dockerfile still runs with dangerous defaults if the orchestrator grants privileges, mounts the host, or accepts unsigned images.

## When to use

- Reviewing a Dockerfile or build pipeline for a new service.
- Reducing vulnerability counts and image size on an existing service.
- Defining registry policy, admission control, or a base image standard.
- Responding to a container escape or an image supply-chain alert.
- Migrating to distroless, scratch, or a minimal enterprise base.
- Do not use for application-level authorization or secrets handling; use `secrets-scanning-remediation` for credentials.

## Workflow

### 1. Inventory the image and its provenance

Record the image reference, digest, base image and digest, build system, owner, runtime platform, and exposure.

```bash
crane config registry.example.com/app:1.2.3 | jq '{created, architecture, config: .config}'
docker history --no-trunc registry.example.com/app:1.2.3
syft registry.example.com/app:1.2.3 -o table
```

Mutable tags hide base changes. Resolve the tag to a digest and compare it to the pinned value in the build file.

### 2. Choose the smallest base that works

| Base | Use when | Tradeoff |
| --- | --- | --- |
| `scratch` | Static binary, no libc, no shell | No CA certs, no timezone data, no debug shell |
| `distroless/static` | Go or Rust static binary | No package manager, harder debugging |
| `distroless/base` | Needs glibc or libssl | Larger than static, still no shell |
| Alpine | Small image, musl compatible | musl breaks glibc binaries; extra CVEs over time |
| UBI minimal | Enterprise support and certification | Larger, but vendor patched |
| Ubuntu/Debian slim | Broad compatibility | Package manager present, more surface |

Pin the base by digest in the final stage. An EOL base is a finding even when its CVE count is zero.

### 3. Use a multi-stage build

Keep compilers, package caches, test fixtures, and source out of the runtime image.

```dockerfile
# syntax=docker/dockerfile:1.7
FROM golang:1.23-bookworm AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod go mod download
COPY . .
RUN --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /out/app ./cmd/app

FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build --chown=65532:65532 /out/app /app
USER 65532:65532
ENTRYPOINT ["/app"]
```

Resolve the base digest with `crane digest` and pin `FROM ...@sha256:<returned-digest>`. Do not trust a tag alone.

### 4. Set a safe process identity and runtime default

- Set `USER` to a numeric UID with no login shell and no home write access.
- Copy files with `--chown` so the runtime user can read them.
- Do not install a shell or package manager in the runtime stage.
- In Kubernetes, set `runAsNonRoot`, `runAsUser`, `allowPrivilegeEscalation: false`, `readOnlyRootFilesystem: true`, and `capabilities.drop: ["ALL"]`.
- Add a `seccompProfile: RuntimeDefault` and a network policy.

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 65532
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop: ["ALL"]
  seccompProfile:
    type: RuntimeDefault
```

Mount an `emptyDir` at `/tmp` if the app needs scratch space. Drop `NET_RAW` unless the app genuinely uses raw sockets.

### 5. Remove build residue and secrets

Add a `.dockerignore` covering `.git`, `.env`, keys, test data, and build output. Never pass secrets through `ARG` or `ENV`; they persist in image history and metadata.

```dockerfile
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc npm ci
```

Check the final image for credentials and unexpected files:

```bash
docker run --rm --entrypoint /bin/sh registry.example.com/app:1.2.3 -c 'true' 2>&1 | head
gitleaks dir ./ --redact
trivy image --scanners secret registry.example.com/app:1.2.3
```

### 6. Generate an SBOM, scan, and sign

```bash
syft registry.example.com/app:1.2.3 -o spdx-json > sbom.spdx.json
trivy image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 registry.example.com/app:1.2.3
grype registry.example.com/app:1.2.3 --fail-on high
cosign sign --key cosign.key registry.example.com/app@sha256:<digest>
cosign attest --predicate sbom.spdx.json --type spdxjson registry.example.com/app@sha256:<digest>
```

Gate the build on fixable HIGH and CRITICAL findings, a valid signature, and an attached SBOM. Rebuild at least weekly so base patches reach production.

### 7. Enforce at the registry and the cluster

- Require signed images from the approved registry; deny `latest` and unknown registries.
- Admission policy should reject root users, privileged mode, host mounts, host networking, and added capabilities.
- Verify signatures at deploy time with `cosign verify` or an admission controller.
- Keep a documented break-glass path with an alert.

```bash
cosign verify --key cosign.pub registry.example.com/app@sha256:<digest>
kubectl get pods -A -o json | jq '.items[] | select(.spec.hostNetwork == true) | .metadata.name'
```

## Validation

- `docker image inspect` shows a non-root `User` and no shell entrypoint.
- The container starts and passes its health check with a read-only root filesystem.
- `capsh --print` or the pod spec shows exactly the needed capabilities, ideally none.
- No HIGH or CRITICAL fixable vulnerability remains, or each exception has an owner and expiry.
- SBOM is attached to the digest and the signature verifies against the published public key.
- The base image is pinned by digest and is within its support window.
- Image size is within the agreed budget and has not grown without review.
- A test deployment with the admission policy rejects a deliberately privileged pod.

## Gotchas

- Alpine uses musl. A glibc-linked binary may build and then fail at runtime.
- Distroless has no shell, so `kubectl exec` debugging fails. Use ephemeral debug containers.
- Setting `USER nonroot` in the Dockerfile is not enough if the orchestrator overrides it to root.
- `allowPrivilegeEscalation: false` does not remove capabilities. Drop them explicitly.
- A read-only root filesystem breaks apps that write caches or PID files. Mount writable paths.
- Secrets in `ARG` or `ENV` stay in image history even if a later layer deletes them.
- Deleting a file in a later layer does not remove it from the earlier layer or shrink the image.
- `latest` and other mutable tags defeat reproducibility and signature meaning.
- A stale or offline scanner database reports a false clean result. Record the DB version and date.
- An EOL base image is a risk even with zero current CVEs.
- Signing without deploy-time verification provides no protection.
- Multi-arch images have different digests. Pin the index digest and verify the platform manifest.
- Installing packages at container start reintroduces the tools you removed, and often needs root.

## Output contract

```json
{
  "image": "registry.example.com/app",
  "digest": "sha256:example-digest-from-crane",
  "owner": "payments",
  "base": {"name": "distroless/static-debian12", "pinned": true, "eol": false},
  "runtime": {
    "user": "65532:65532",
    "root_filesystem": "read-only",
    "capabilities": [],
    "allow_privilege_escalation": false,
    "seccomp": "RuntimeDefault"
  },
  "scan": {
    "scanner": "trivy",
    "db_updated": "2026-11-25",
    "critical": 0,
    "high": 2,
    "fixable_high": 0
  },
  "supply_chain": {"sbom": "sbom.spdx.json", "signed": true, "signature_verified": true},
  "findings": [
    {
      "id": "C-001",
      "severity": "high",
      "finding": "runtime stage includes curl",
      "evidence": "syft lists curl 8.5.0",
      "remediation": "remove curl and use a distroless base",
      "owner": "payments",
      "due": "2026-12-05"
    }
  ],
  "exceptions": [{"finding": "C-003", "reason": "vendor agent requires cap_net_raw", "owner": "platform", "expires": "2027-02-01"}]
}
```

## Checklist

- [ ] Image, digest, base, owner, and exposure recorded.
- [ ] Base image is minimal for the runtime and pinned by digest.
- [ ] Multi-stage build keeps toolchains out of the runtime image.
- [ ] Runtime user is numeric and non-root.
- [ ] Root filesystem read-only with explicit writable mounts.
- [ ] All capabilities dropped, none added without justification.
- [ ] `allowPrivilegeEscalation` false and seccomp profile set.
- [ ] `.dockerignore` and secret mounts prevent credential leakage.
- [ ] SBOM generated and attached to the digest.
- [ ] Scan gate blocks fixable HIGH and CRITICAL findings.
- [ ] Image signed and verified at deploy time.
- [ ] Admission policy rejects privileged and unsigned workloads.

## Related skills

- `dependency-vulnerability-auditing` for SBOM generation and advisory prioritization.
- `supply-chain-security-review` for provenance, SLSA, and signature policy.
- `secrets-scanning-remediation` for credentials found in layers or build args.
- `container-log-diagnostics` for runtime symptoms after a container compromise.
