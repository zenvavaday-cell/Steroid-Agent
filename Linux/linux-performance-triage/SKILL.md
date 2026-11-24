---
name: linux-performance-triage
description: Triages Linux CPU, memory, I/O, load, and contention problems using the USE method with uptime, vmstat, mpstat, pidstat, iostat, free, pressure stall information, and cgroup limits. Use for slow hosts, high load, OOM kills, latency spikes, and container throttling.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: linux
---

# Linux Performance Triage

## Overview

Performance triage answers three questions: what resource is saturated, which process or cgroup is responsible, and what changed. Start with the symptom and the time window, then use the USE method for every resource: utilization, saturation, and errors.

Do not tune before measuring. Do not measure one resource and declare victory.

## When to use

- A host or container is slow, unresponsive, or restarting.
- Load average is high but CPU usage looks low.
- Memory pressure or the OOM killer is suspected.
- I/O latency or `iowait` is elevated.
- A service misses latency targets after a deploy.

## Workflow

### 1. Define the symptom and window

Record:

- What is slow: request latency, shell response, throughput, or startup.
- When it started and whether it is constant or spiky.
- Scope: one process, one container, one host, or a fleet.
- Recent changes: deploy, config, traffic, cron, kernel, disk.
- The service's SLO and the observed value.

### 2. Check load and CPU count

```bash
uptime
nproc
cat /proc/loadavg
```

Load average counts runnable and uninterruptible (D-state) tasks. Compare it to the CPU count, but a high load with low CPU can be I/O wait or a stuck process.

### 3. Break down CPU

```bash
mpstat -P ALL 1 5
top -b -n1 -o %CPU | head -25
pidstat -u 1 5
```

Read the columns:

| Column | Meaning |
| --- | --- |
| `%usr` | User-space CPU |
| `%sys` | Kernel CPU |
| `%iowait` | CPU idle while I/O is outstanding |
| `%steal` | Hypervisor stole CPU from the VM |
| `%irq` / `%soft` | Interrupt handling |
| `%idle` | Truly idle |

High `%sys` can mean syscall overhead, networking, or a kernel bug. High `%steal` is a host or cloud capacity issue.

### 4. Check memory

```bash
free -h
cat /proc/meminfo
vmstat 1 5
ps -eo pid,ppid,rss,%mem,comm --sort=-rss | head -20
dmesg -T | grep -i -E 'oom|killed process'
```

Use `available`, not `free`. Linux uses spare memory for cache. Check swap-in/swap-out (`si`/`so`) and the OOM killer.

### 5. Check I/O

```bash
iostat -xz 1 5
pidstat -d 1 5
iotop -o
cat /proc/pressure/io
```

Look at `await`, `aqu-sz`, `%util`, and per-process read/write rates. High `await` with low `%util` can indicate a slow device or queueing.

### 6. Check scheduler and contention

```bash
vmstat 1 5
pidstat -w 1 5
cat /proc/pressure/cpu
cat /proc/pressure/memory
```

In `vmstat`, `r` is runnable, `b` is blocked, `si`/`so` are swap, `wa` is I/O wait, and `st` is steal. Pressure stall information gives a direct measure of contention.

### 7. Check cgroup and container limits

```bash
systemd-cgtop
cat /sys/fs/cgroup/<path>/cpu.max
cat /sys/fs/cgroup/<path>/memory.max
cat /sys/fs/cgroup/<path>/memory.current
cat /sys/fs/cgroup/<path>/cpu.stat
kubectl top pod -n <namespace>
```

A container can be throttled at its CPU limit while the host is idle. `nr_throttled` and `throttled_time` in `cpu.stat` prove it.

### 8. Attribute to a process

```bash
ps -eo pid,ppid,user,stat,%cpu,%mem,etime,cmd --sort=-%cpu | head -20
cat /proc/<pid>/status
cat /proc/<pid>/stack      # root; kernel stack for D-state
strace -c -p <pid>         # short sample
perf top -p <pid>          # if permitted
```

A process in `D` state is blocked on I/O or a kernel lock. `strace` and `perf` need permissions; in containers, check `CAP_SYS_PTRACE` and `perf_event_paranoid`.

### 9. Fix and verify

Apply the smallest fix: raise a limit, fix a query, add an index, reduce concurrency, move I/O, or restart a leaking process. Re-measure the same metric over the same window. A fix that improves a different metric may have moved the bottleneck.

## Gotchas

- Load average includes uninterruptible I/O. High load is not always CPU.
- `free` without `available` overstates memory pressure because Linux caches aggressively.
- `%iowait` is idle time with outstanding I/O, not a measure of device saturation.
- `%steal` in a VM means the hypervisor is not giving you CPU. You cannot fix it inside the guest.
- Container CPU limits cause throttling even when host CPU is free. Check `cpu.stat`.
- `top` and `ps` report `%CPU` differently for multi-threaded processes. Use `pidstat` for a consistent view.
- Short-lived spikes can disappear before you sample. Use `sar`, `atop`, or a longer capture.
- `perf` and `strace` are restricted on many hosts and containers. Check permissions before concluding.
- A memory leak can be masked by the OOM killer restarting the process. Check restart counts and kernel logs.
- Hyperthreading means `nproc` may overstate physical cores for CPU-bound work.
- Fixing one bottleneck reveals the next. Re-profile after every change.

## Output contract

```markdown
## Symptom
<what is slow, since when, scope, SLO>

## Resource summary
| Resource | Utilization | Saturation | Errors |
| --- | --- | --- | --- |
| CPU | ... | run queue ... | ... |
| Memory | ... | swap ... | OOM ... |
| Disk | ... | await ... | ... |
| Network | ... | retrans ... | ... |

## Top consumers
| PID / cgroup | CPU | Memory | I/O | Evidence |
| --- | --- | --- | --- | --- |

## Root cause
<one paragraph>

## Fix
<change>

## Verification
<same metric, same window, before/after>

## Follow-up
<alert, limit, capacity, regression test>
```

## Checklist

- [ ] Symptom, window, and scope defined.
- [ ] Load compared to CPU count.
- [ ] CPU breakdown checked, including steal.
- [ ] Memory `available`, swap, and OOM checked.
- [ ] I/O latency and queue depth checked.
- [ ] Pressure stall information checked.
- [ ] cgroup and container limits checked.
- [ ] Top consumers attributed.
- [ ] Fix verified with the same metric.
- [ ] Follow-up monitoring added.

## Related skills

- `linux-storage-diagnostics` when disk health or capacity is the cause.
- `linux-network-diagnostics` when latency is network-bound.
- `container-log-diagnostics` for pod-level restarts and limits.
