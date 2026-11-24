---
name: deterministic-code-sandbox-execution
description: Runs untrusted or model-generated code in an isolated sandbox with CPU, memory, process, disk, and time limits, no network by default, a read-only filesystem, and controlled artifact extraction. Use for data analysis, code interpretation, test execution, and any workflow executing code you did not write.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: agentic
---

# Deterministic Code Sandbox Execution

## Overview

Running generated code on a host is a remote-code-execution decision. A sandbox limits what the code can touch, how long it can run, and what it can exfiltrate. Isolation is layered: kernel, container, filesystem, network, resources, and output.

Determinism is the second requirement: the same input and code produce the same output, or the difference is explained.

## When to use

- Executing model-generated Python, JavaScript, or shell.
- Running untrusted user uploads.
- Reproducing a data analysis in a clean environment.
- Running tests or builds with side effects.
- Evaluating code for correctness.

Do not run untrusted code directly on a developer laptop, CI runner, or production host without isolation.

## Isolation levels

| Level | Mechanism | Use for |
| --- | --- | --- |
| Process | `subprocess`, resource limits | Trusted code, quick checks |
| Container | Docker, Podman, rootless | General untrusted code |
| User-space kernel | gVisor | Stronger container isolation |
| MicroVM | Firecracker, Kata | Multi-tenant, high-risk |
| Language runtime | Pyodide, WASM | Browser or plugin sandboxes |

Containers share the host kernel. For hostile code, use gVisor or a microVM.

## Workflow

### 1. Define the execution contract

Specify:

- Language and runtime version.
- Input files and mount paths.
- Expected output files.
- Timeout and resource limits.
- Network policy.
- Whether package installation is allowed.

### 2. Build a minimal image

Pin the base image by digest. Install only the required runtime and libraries. Run as a non-root user.

```dockerfile
FROM python:3.12-slim@sha256:<digest>
RUN useradd --create-home --uid 10001 sandbox
USER sandbox
WORKDIR /work
```

No Docker socket, no cloud credentials, no host home directory.

### 3. Run with limits

```bash
docker run --rm \
  --network none \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  --memory 512m --memory-swap 512m \
  --cpus 1.0 \
  --pids-limit 128 \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  --user 10001:10001 \
  -v "$PWD/input:/work/input:ro" \
  -v "$PWD/output:/work/output:rw" \
  -w /work \
  sandbox/python:3.12 \
  timeout 30 python /work/input/main.py
```

Notes:

- `--network none` blocks exfiltration. Add a proxy only if the task requires it, with an allowlist.
- `--read-only` prevents writes outside mounted paths.
- `--pids-limit` blocks fork bombs.
- `--memory` and `--cpus` bound resource consumption.
- `--cap-drop ALL` removes Linux capabilities.
- `timeout` is a second guard if the runtime ignores signals.

### 4. Control input and output

- Mount input read-only.
- Mount a dedicated output directory.
- Cap output size and file count.
- Scan output for secrets and unexpected binaries.
- Never mount the Docker socket, SSH keys, cloud credentials, or the host root.

### 5. Capture results

```python
import subprocess

result = subprocess.run(
    ["docker", "run", "--rm", ...],
    capture_output=True,
    text=True,
    timeout=35,
)
print(result.returncode)
print(result.stdout[-10_000:])
print(result.stderr[-10_000:])
```

Truncate logs. A malicious program can print gigabytes.

### 6. Ensure determinism

- Pin the image digest and dependency versions.
- Set `PYTHONHASHSEED`, locale, and timezone.
- Freeze the clock if the code uses time.
- Seed random number generators.
- Sort outputs before comparison.
- Record the image digest, command, inputs hash, and environment.

### 7. Destroy

Use `--rm` and a fresh container per run. Do not reuse a sandbox across untrusted inputs. Clean temporary directories.

## Gotchas

- A mounted Docker socket is root-equivalent on the host. Never expose it.
- `--network none` does not block all kernel-level channels; for hostile code, use a microVM.
- Containers share the host kernel. A kernel exploit escapes the container.
- `--read-only` with a writable `/tmp` is common, but `/tmp` must be `noexec` and size-limited.
- Fork bombs exhaust process IDs; set `--pids-limit`.
- Memory limits without swap limits can still stress the host.
- A timeout in the application may not kill a child process. Use the runtime timeout.
- Output size can exhaust disk or memory. Cap stdout and file writes.
- Symlinks in the output can point outside the mount. Validate real paths.
- Package installation at runtime needs network and mutates the image. Install dependencies at build time.
- GPU access and privileged mode defeat most isolation.
- Determinism breaks with unpinned dependencies, locale, timezone, and randomness.

## Output contract

```json
{
  "run_id": "sbx-2026-11-24-001",
  "image": "sandbox/python:3.12@sha256:...",
  "command": "python /work/input/main.py",
  "limits": {"cpu": 1.0, "memory_mb": 512, "pids": 128, "timeout_s": 30, "network": "none"},
  "exit_code": 0,
  "stdout": "...",
  "stderr": "",
  "artifacts": [{"path": "output/result.csv", "bytes": 2048, "sha256": "..."}],
  "deterministic": true,
  "input_hash": "sha256:..."
}
```

## Checklist

- [ ] Execution contract defined.
- [ ] Image pinned by digest and minimal.
- [ ] Non-root user, capabilities dropped.
- [ ] Network disabled or allowlisted.
- [ ] Filesystem read-only except output and tmp.
- [ ] CPU, memory, PID, disk, and time limits set.
- [ ] Input read-only, output capped and scanned.
- [ ] Environment pinned for determinism.
- [ ] Fresh container per run and destroyed after.

## Related skills

- `bounded-multi-tool-orchestration` for calling the sandbox as a tool.
- `stateful-workflow-checkpointing` for long-running executions.
- `human-in-the-loop-escalation` before running privileged or networked code.
