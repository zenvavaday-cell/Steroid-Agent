---
name: linux-package-management-repair
description: Repairs broken package databases, held packages, dependency conflicts, and interrupted upgrades. Use for apt, dnf, and pacman failures.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: linux
---

# Linux Package Management Repair

## Overview

Package state is a database plus a cache plus locks. Failures are usually a stale lock from an interrupted transaction, a half-configured package, a dependency conflict, or broken repository metadata. Repair in place, protect the database, and avoid force flags.

A package manager that returns an error is telling you its invariant is broken. Read the exact message and fix the cause; forcing the transaction moves the corruption forward.

## When to use

- apt or dpkg reports an interrupted or half-configured transaction.
- dnf or rpm fails transaction checks, shows duplicate packages, or reports an rpmdb error.
- pacman refuses due to file conflicts, an invalid key, or a partial upgrade.
- Held, pinned, or version-locked packages block a security update.
- A disk-full or killed process corrupted package manager state.
- You must roll back a bad upgrade to a known good version.
- Do not use to force packages across incompatible repositories; that is a rebuild or migration decision.

## Workflow

### 1. Inventory the distribution and transaction state

```bash
cat /etc/os-release
df -h /var /boot
# Debian/Ubuntu
dpkg --audit
dpkg -l | awk '$1 !~ /^(ii|rc)$/ {print}'
apt-get check
# RHEL/Fedora
dnf check
rpm -Va --nofiles --nodigest | head -50
# Arch
pacman -Dk
pacman -Qkk 2>&1 | tail -30
```

Capture the exact error text and exit code. Most reports reduce to a held lock, a half-installed package, a full filesystem, or an unreachable repository. `rpm -Va` flags normal configuration changes too; separate `config file` and `missing` noise from real corruption.

### 2. Clear locks only after finding the owner

```bash
fuser -v /var/lib/dpkg/lock-frontend /var/lib/dpkg/lock /var/cache/apt/archives/lock
ps -ef | grep -E 'apt|dpkg|unattended|dnf|packagekit'
systemctl status apt-daily.service apt-daily-upgrade.service unattended-upgrades
```

For dnf, find the process holding `/var/cache/dnf/*.lock` or the dnf lock in `/run`. For pacman, inspect `/var/lib/pacman/db.lck` with `fuser -v`. Wait for the transaction to finish, or stop the automated timer and then remove the lock. Never delete `db.lck` while pacman is running.

### 3. Repair dpkg and apt

```bash
dpkg --configure -a
apt-get --fix-broken install
apt-get -s install                 # dry run before committing
dpkg --audit
apt-get install --reinstall <package>
```

If `dpkg --audit` lists a package, reinstall the same version from `/var/cache/apt/archives` or the configured repository. If `/var/lib/dpkg/updates` contains stale journal files, back them up and move them aside rather than deleting blindly. Never remove or hand-edit `/var/lib/dpkg/status`.

### 4. Repair rpm and dnf

```bash
cp -a /var/lib/rpm /var/lib/rpm.bak.$(date +%F)
rpm --rebuilddb
dnf check
dnf distro-sync
dnf repoquery --duplicates
dnf install --allowerasing <package>
dnf history list
dnf history undo <id>
```

`--allowerasing` is a real decision: record which package is removed and why. Use `dnf history undo` only when the transaction is recent and the dependencies still resolve.

### 5. Repair pacman on Arch

```bash
pacman -Dk
pacman-key --init
pacman-key --populate archlinux
pacman-key --refresh-keys
pacman -Syu                         # never a partial upgrade
pacman -U /var/cache/pacman/pkg/<pkg>-<version>-x86_64.pkg.tar.zst
```

`pacman -Sy <pkg>` without a full `-Syu` creates a partial upgrade and is the most common cause of Arch breakage. For a file conflict, identify the owner with `pacman -Qo <path>` and use `--overwrite` only for a known package-owned path, never for an entire directory.

### 6. Resolve holds, pins, and conflicts

```bash
apt-mark showhold
apt-mark unhold <package>
apt-cache policy <package>
apt-get install -s <package>
grep -r . /etc/apt/preferences.d/
dnf versionlock list
rpm -q --whatrequires <package>
```

Pinning and versionlock are intentional controls. Do not remove them to make an error disappear; confirm the security or compatibility reason, then update the pin with a ticket. When two packages conflict, read their file lists (`dpkg -L`, `rpm -ql`, `pacman -Ql`) before choosing what to remove.

### 7. Verify and prevent recurrence

```bash
apt-get check && dpkg --audit
dnf check
pacman -Dk
systemctl --failed
journalctl -b -p err --no-pager
uname -r
```

For kernel, glibc, or systemd upgrades, schedule a reboot and confirm the running kernel matches the newest installed one. Enable automatic security updates, monitor disk space and failed transactions, and keep the package cache and a snapshot until the next successful boot.

## Validation

Pass only when all gates hold:

- `dpkg --audit` returns no output and `apt-get check` exits 0.
- `dnf check` exits 0 and `dnf repoquery --duplicates` is empty.
- `pacman -Dk` exits 0 and `pacman -Qkk` shows only expected local modifications.
- No package remains in a half-installed or unconfigured state.
- `/var`, `/boot`, and the package cache have at least 10 percent free space.
- After a kernel or libc upgrade, the host reboots and reports the expected `uname -r`.
- Required services start and `systemctl --failed` is empty.
- A rollback path exists (snapshot, cached older package, or documented downgrade command).

## Gotchas

- Removing a lock file while a package process is still running can corrupt the database. Confirm with `fuser` and `ps` first.
- `apt-get upgrade` holds back kernel and libc changes; `full-upgrade` may remove packages. Choose deliberately and read the proposed list.
- `--force-yes`, `--nodeps`, and `--overwrite` bypass safety checks and can leave an inconsistent system.
- `rpm --rebuilddb` on a corrupt database without a backup can lose indexes. Copy `/var/lib/rpm` first.
- Mixing Debian stable with testing or sid, or adding a third-party repo with higher priority, breaks resolution. Check `apt-cache policy`.
- `apt autoremove` can remove a kernel or a metapackage needed after reboot. Review the list before confirming.
- A full filesystem mid-transaction leaves half-written files. Free space before retrying (`apt-get clean`, `dnf clean all`, `pacman -Sc`).
- An expired repository GPG key often looks like a network error. Check `apt-key list`, `rpm -q gpg-pubkey`, or `pacman-key --list-keys`.
- Clock skew breaks TLS to repositories. Check `timedatectl` before debugging mirrors.
- A held package can hide a security update for months. Review holds and versionlocks at every patch cycle.
- `dnf history undo` after a reboot or repository change may not resolve; prefer a snapshot rollback.
- Snap, Flatpak, pip, npm, and language-specific packages are separate from the OS manager. Repairing apt does not fix them.
- Installing a new kernel does not replace the running one. A reboot is required to use it.

## Output contract

```markdown
## Host
<distro, version, package manager, kernel>

## Symptom
<exact error, exit code, first occurrence>

## Diagnosis
| Check | Result | Interpretation |
| --- | --- | --- |

## Root cause
<one paragraph>

## Repair
| Action | Command | Result |
| --- | --- | --- |

## Rollback
<snapshot, cached version, downgrade command>

## Verification
- Database check: pass/fail
- Half-installed packages: none/list
- Reboot required: yes/no
- Services healthy: pass/fail

## Prevention
<updates policy, monitoring, disk headroom, repo hygiene>
```

## Checklist

- [ ] Distribution and package manager identified.
- [ ] Exact error and exit code captured.
- [ ] Filesystem free space checked.
- [ ] Lock owner identified before any lock removal.
- [ ] Interrupted transaction completed or rolled back.
- [ ] Half-installed packages repaired.
- [ ] Holds, pins, and versionlocks reviewed with a reason.
- [ ] Repository keys and clock checked.
- [ ] Database integrity verified.
- [ ] Reboot performed for kernel or libc changes.
- [ ] Rollback path documented and tested.
- [ ] Monitoring added for failed transactions and disk space.

## Related skills

- `linux-boot-failure-recovery` when an interrupted upgrade prevents boot.
- `linux-storage-diagnostics` when disk errors or a full filesystem caused the failure.
- `linux-security-hardening` for repository trust and patch policy.
- `linux-systemd-service-management` to verify services after a package change.
