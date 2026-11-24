---
name: linux-storage-diagnostics
description: Diagnoses disk-full, inode-exhaustion, read-only-filesystem, I/O-latency, mount, and failing-disk problems using df, du, lsblk, lsof, smartctl, iostat, and journal logs. Use for "no space left", slow disks, failed mounts, and storage capacity incidents.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: linux
---

# Linux Storage Diagnostics

## Overview

"No space left on device" is not always a full disk. It can be inode exhaustion, a deleted file held open, a read-only filesystem, a full snapshot, or a quota. Diagnose the filesystem first, then the block device, then the workload.

Never delete data to make a graph green without identifying what the data is and whether it is needed.

## When to use

- Disk usage alarms or write failures.
- A filesystem remounted read-only.
- Slow I/O or high `iowait`.
- A mount that fails at boot.
- SMART warnings or predicted disk failure.
- Container or volume capacity issues.

## Workflow

### 1. Identify the filesystem

```bash
findmnt -T /path/to/dir
df -hT
df -i
lsblk -f
```

`df -hT` shows space, filesystem type, and mount point. `df -i` shows inode usage. A filesystem can have free space and zero inodes.

### 2. Find what is using space

```bash
du -xhd1 /var | sort -h
du -xhd1 /var/log | sort -h
ncdu -x /var
find / -xdev -type f -size +1G -printf '%s %p\n' 2>/dev/null | sort -n
```

`-x` stays on one filesystem, so a mount under `/var` is not counted twice. `du` and `df` can disagree because of deleted-open files, reserved blocks, or snapshots.

### 3. Check for deleted files held open

```bash
lsof +L1
lsof -nP | grep '(deleted)'
```

A process holding a deleted log file keeps the space allocated until it closes or is restarted. Truncating the file (`: > file`) releases the space without restarting the process; deleting the path again does not.

### 4. Check mount and filesystem health

```bash
findmnt -T /path
mount | grep ' ro,'
dmesg -T | tail -50
journalctl -k -n 100 --no-pager
```

Look for `EXT4-fs error`, `I/O error`, `remount-ro`, `XFS ... corruption`, or `NFS server not responding`.

### 5. Inspect block devices

```bash
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,ROTA,MODEL
blkid
smartctl -a /dev/sdX
smartctl -a -d megaraid,0 /dev/sdX   # behind a RAID controller
nvme smart-log /dev/nvme0
```

Check reallocated sectors, pending sectors, uncorrectable errors, wear leveling, and temperature. A failing disk is a replacement decision, not a cleanup task.

### 6. Measure I/O

```bash
iostat -xz 1 5
iotop -o
pidstat -d 1 5
cat /proc/pressure/io
```

`iostat -x` shows `await`, `r_await`, `w_await`, `aqu-sz`, and `%util`. High `%util` with low throughput often means many small or serialized requests, not a saturated bus.

### 7. Check quotas and snapshots

```bash
quota -s
repquota -a
btrfs filesystem df /
zfs list -o space
lvs
```

Snapshots and clones consume space outside the mounted filesystem's `df` view. Check the volume manager.

### 8. Check fstab and boot mounts

```bash
findmnt --verify
cat /etc/fstab
mount -a
systemd-analyze verify
```

A bad `fstab` entry can drop the system into emergency mode. Use `nofail` for non-critical mounts and verify before rebooting.

### 9. Remediate

| Cause | Action |
| --- | --- |
| Log growth | Rotate and compress; check `logrotate` |
| Deleted open file | Truncate or restart the holder |
| Inode exhaustion | Find many small files; clean caches or old mail/spool |
| Snapshot growth | Delete or thin snapshots after confirming retention |
| Full volume | Extend LVM or cloud volume; grow the filesystem |
| Read-only remount | Check kernel logs; fix the underlying I/O error before remounting |
| Failing disk | Replace and restore from backup |
| Quota | Raise the quota or clean the user's data |

## Gotchas

- `df` reports blocks allocated to deleted-open files; `du` cannot see them.
- Reserved blocks (typically 5% on ext4) make `df` show less free space than expected for non-root users.
- Inode exhaustion produces "no space left" with free blocks.
- Overlay and container layers can fill the host while the container's `df` looks fine.
- `du -x` prevents crossing into other filesystems; without it, totals are misleading.
- Network filesystems can hang on `du` and `df`. Use timeouts.
- Snapshots and thin pools consume space that the mounted filesystem does not report.
- `smartctl` may need `-d` for RAID controllers or USB bridges.
- `mount -o remount,rw` may fail if the kernel marked the filesystem corrupt. Fix the error first.
- `fstab` errors can prevent boot. Always test with `mount -a` and keep a root shell open.
- `discard` and `fstrim` behavior differs by filesystem and cloud provider.
- Do not delete files you cannot identify. Check ownership, age, and open handles first.

## Output contract

```markdown
## Symptom
<path, error, time, scope>

## Filesystem
- Mount: /var
- Type: ext4
- Size/used/available: ...
- Inodes: ...
- Read-only: yes/no

## Consumers
| Path/process | Size | Notes |
| --- | --- | --- |

## Device health
<SMART summary, kernel errors>

## Root cause
<one paragraph>

## Remediation
<commands and expected effect>

## Verification
<df, write test, mount status>

## Follow-up
<alert threshold, log rotation, replacement>
```

## Checklist

- [ ] Correct filesystem identified with `findmnt`.
- [ ] Space and inode usage checked.
- [ ] Large files and directories identified.
- [ ] Deleted-open files checked.
- [ ] Kernel and mount errors reviewed.
- [ ] Block device health checked.
- [ ] I/O latency measured.
- [ ] Snapshots and quotas checked.
- [ ] `fstab` verified before reboot.
- [ ] Remediation verified with a write test.

## Related skills

- `linux-performance-triage` when storage latency is the main symptom.
- `linux-systemd-service-management` for services that fill disks or fail on I/O.
- `container-log-diagnostics` for container layer and volume issues.
