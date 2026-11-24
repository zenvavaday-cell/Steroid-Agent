---
name: container-log-diagnostics
description: Diagnoses container and Kubernetes failures from logs, events, exit codes, probes, and resource metrics, covering CrashLoopBackOff, OOMKilled, image pull errors, networking, and configuration issues. Use for incident triage, post-deployment failures, and container runtime debugging.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: engineering
---

# Container Log Diagnostics

## Overview

A container that will not start has no application logs. Diagnose from the outside in: pod status, events, container state, previous logs, exit code, resource limits, probes, and configuration. Only then read application logs.

## When to use

- Pods in CrashLoopBackOff, Pending, ImagePullBackOff, or OOMKilled.
- A deployment is healthy but requests fail.
- A container exits without a useful error.
- Logs are missing, interleaved, or truncated.

## Workflow

### 1. Get the pod state

```bash
kubectl get pods -n <namespace> -o wide
kubectl describe pod <pod> -n <namespace>
```

Read the `Status`, `Containers`, `Conditions`, `Events`, `Restart Count`, `Last State`, and `Exit Code`. The event stream often contains the real cause before any application log.

### 2. Read events

```bash
kubectl get events -n <namespace> --sort-by=.lastTimestamp
kubectl events -n <namespace> --for pod/<pod>
```

Look for:

- `FailedScheduling`: insufficient CPU/memory, taints, affinity.
- `FailedMount`: missing ConfigMap, Secret, or volume.
- `ErrImagePull` / `ImagePullBackOff`: registry auth, wrong tag, rate limit.
- `Unhealthy`: probe failures.
- `OOMKilled` or `Evicted`: resource pressure.
- `FailedCreate`: quota, admission webhook, security policy.

### 3. Read logs correctly

```bash
# Current container
kubectl logs <pod> -n <namespace> -c <container>

# Previous crashed instance
kubectl logs <pod> -n <namespace> -c <container> --previous

# Follow across pods
stern -n <namespace> <app-label>

# Timestamps and tail
kubectl logs <pod> -n <namespace> --timestamps --tail=200
```

For init containers, specify `-c <init-container>`. For multi-container pods, always specify the container; the default may be ambiguous.

### 4. Decode the exit code

| Code | Meaning | Common cause |
| --- | --- | --- |
| 0 | Success | Job completed; restart policy may still restart it |
| 1 | Application error | Unhandled exception, config error |
| 2 | Shell misuse | Bad script or arguments |
| 126 | Not executable | Permission or shebang problem |
| 127 | Command not found | Wrong entrypoint or PATH |
| 137 | SIGKILL | OOMKilled or forced termination |
| 143 | SIGTERM | Graceful shutdown, timeout, eviction |
| 139 | SIGSEGV | Native crash |
| 255 | Exit outside range | Runtime or wrapper error |

Exit code 137 requires checking memory limits and node pressure, not only application logs.

### 5. Check resources and probes

```bash
kubectl top pod <pod> -n <namespace> --containers
kubectl get pod <pod> -n <namespace> -o jsonpath='{.spec.containers[*].resources}'
kubectl get pod <pod> -n <namespace> -o jsonpath='{.status.containerStatuses[*].lastState}'
```

Check:

- Requests versus limits; a limit equal to the request leaves no burst room.
- JVM, Node, or Python heap settings versus the container limit.
- Liveness probes that are too aggressive or depend on downstream services.
- Startup probes missing for slow-starting apps.
- Readiness probes that pass before the app can serve traffic.

### 6. Check configuration and networking

```bash
kubectl exec -it <pod> -n <namespace> -- env | sort
kubectl exec -it <pod> -n <namespace> -- cat /etc/config/app.yaml
kubectl get configmap,secret -n <namespace>
kubectl exec -it <pod> -n <namespace> -- nslookup <service>
kubectl exec -it <pod> -n <namespace> -- curl -v http://<service>:<port>/health
```

Check:

- Missing or misspelled environment variables.
- ConfigMap or Secret not mounted, or mounted at the wrong path.
- Service selector mismatch.
- NetworkPolicy blocking traffic.
- DNS resolution and search domains.
- TLS certificate and trust store.

### 7. Correlate

Use the request ID, trace ID, or timestamp to connect logs across services. A failure in service A may be caused by a timeout in service B. Check the dependency before changing A.

## Gotchas

- Logs disappear when the container restarts. Use `--previous` or a log aggregation system.
- `kubectl logs` shows stdout/stderr only. Files written inside the container are lost on restart unless persisted.
- Buffered application logs can be lost on SIGKILL. Flush on shutdown and use unbuffered output.
- JSON logs need parsing. `jq` is more reliable than grep for structured fields.
- Clock skew between nodes makes cross-service correlation wrong. Compare with trace timestamps.
- A readiness probe failure removes the pod from the Service but does not restart it. A liveness failure restarts it.
- An OOMKilled container may show no application error. Check the exit code and last state.
- Init container failures block the main container and often have separate logs.
- Sidecars can mask the app's exit code or consume its resources.
- Node-level issues (disk pressure, PID exhaustion, kernel OOM) affect many pods at once.

## Output contract

```markdown
## Symptom
<pod, namespace, status, restarts, duration>

## Evidence
- Pod state: ...
- Events: ...
- Exit code: ...
- Last state: ...
- Logs: <key lines with timestamps>
- Resources: requests/limits/usage
- Probes: ...

## Classification
<application | resource | config | image | network | probe | node | dependency>

## Root cause
<one paragraph>

## Fix
<change>

## Verification
<command and expected result>

## Prevention
<probe, limit, alert, or manifest change>
```

## Checklist

- [ ] Pod status and events read.
- [ ] Current and previous logs collected.
- [ ] Exit code decoded.
- [ ] Resource usage compared to limits.
- [ ] Probes reviewed.
- [ ] Config and secrets verified.
- [ ] Network and DNS tested.
- [ ] Root cause distinguished from symptom.
- [ ] Fix verified and prevention added.

## Related skills

- `ci-cd-failure-diagnosis` for failures before deployment.
- `stateful-workflow-checkpointing` for recovering long-running jobs after a restart.
- `human-in-the-loop-escalation` for production changes.
