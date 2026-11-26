---
name: linux-boot-failure-recovery
description: Diagnoses boot failures across firmware, bootloader, initramfs, fstab, and systemd, and restores access safely. Use for unbootable hosts, emergency mode, and failed upgrades.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: linux
---

# Linux Boot Failure Recovery

## Overview

A Linux boot moves through firmware, bootloader, kernel with initramfs, root filesystem mount, and systemd targets. A failure at any stage can look identical from the console: a hang, a black screen, or an emergency prompt. The discipline is to identify the last stage that completed, change one thing, and keep a way back.

Do not reinstall before capturing logs and confirming the failing stage. Most failures are a stale initramfs, a bad fstab entry, a full `/boot`, or a bootloader entry pointing at a removed kernel.

## When to use

- The host stops at firmware, GRUB, "Loading Linux", or a blank console.
- Boot lands in emergency mode or a dracut/initramfs shell.
- A kernel or distribution upgrade left the host unbootable.
- A disk, LVM, LUKS, or fstab change broke root mounting.
- You need to recover access or data from an unbootable host.
- Boot is slow or intermittently fails after a hardware change.
- Do not use when the host boots correctly and only one service fails; use `linux-systemd-service-management`.

## Workflow

### 1. Stabilize the host and capture evidence

Work from the console, IPMI, or serial console. Record what is on screen, the last change, and whether the failure is repeatable. From rescue media, mount the root read-only and collect:

```bash
lsblk -f
blkid
cat /etc/fstab
df -h /boot
journalctl -b -1 -p warning --no-pager | tail -80
dmesg -T | grep -iE 'failed|error|timeout|not found'
```

`journalctl -b -1` reads the previous boot only if the journal persisted to disk. Copy the journal and `/var/log` off the host before changing anything.

### 2. Identify the failing stage

| Stage | Typical symptom | First check |
| --- | --- | --- |
| Firmware/POST | No output, beep codes, RAID volume offline | IPMI console, RAID controller, boot order |
| Bootloader | `grub>` prompt, "no such device", no menu | `efibootmgr -v`, `ls (hd0,gpt2)/`, grub.cfg |
| Kernel/initramfs | Hang at "Loading Linux", "Unable to find root device" | Kernel cmdline `root=`, initramfs contents |
| Root mount | Emergency mode after mount failure, fsck prompt | fstab UUIDs, LVM/LUKS status, `findmnt` |
| systemd | Emergency target, failed units, boot loop | `systemctl --failed`, `journalctl -xb` |

The stage narrows the search. Do not rebuild GRUB for a missing NVMe driver, and do not rebuild the initramfs for a typo in fstab.

### 3. Repair firmware and bootloader

Check the firmware boot order and the RAID or LUKS state before touching software. For UEFI:

```bash
efibootmgr -v
bootctl status
ls /boot/efi/EFI/
```

Back up the configuration, then regenerate it with the distribution's command:

```bash
# Debian/Ubuntu
cp /boot/grub/grub.cfg /root/grub.cfg.bak
update-grub

# RHEL/Fedora, BIOS
cp /boot/grub2/grub.cfg /root/grub.cfg.bak
grub2-mkconfig -o /boot/grub2/grub.cfg

# Reinstall the bootloader (UEFI example)
grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=debian
```

If the menu does not appear, hold Shift on BIOS or press Esc repeatedly on UEFI. At the GRUB menu, `e` edits the selected entry for one boot only: add `systemd.unit=emergency.target`, `rd.break`, or `init=/bin/bash`, then Ctrl-X. These are diagnostic, not fixes.

### 4. Rebuild the initramfs when root storage is not found

Messages such as `Unable to find root device`, `dracut-initqueue timeout`, or a drop to `(initramfs)` usually mean the initramfs lacks the driver for the root disk, or `root=` points at a device that no longer exists.

From rescue media, mount the root and chroot:

```bash
mount /dev/<root> /mnt
mount /dev/<boot> /mnt/boot          # if separate
mount /dev/<esp> /mnt/boot/efi       # UEFI
for d in dev proc sys run; do mount --bind /$d /mnt/$d; done
chroot /mnt /bin/bash
```

Inside the chroot, confirm the modules and regenerate:

```bash
lsinitramfs /boot/initrd.img-$(uname -r) | grep -E 'nvme|ahci|dm-|lvm'
update-initramfs -u -k all            # Debian/Ubuntu
dracut --force --regenerate-all       # RHEL/Fedora
mkinitcpio -P                         # Arch
```

If a third-party storage driver is missing, add it to `/etc/initramfs-tools/modules` or a `/etc/dracut.conf.d/*.conf` file before rebuilding.

### 5. Repair fstab and root mount failures

In emergency mode the root is often mounted read-only. Remount it before editing:

```bash
mount -o remount,rw /
findmnt --verify --verbose
blkid
```

Fix entries by UUID or label rather than kernel device names. Comment out nonessential mounts to get a boot, then repair them one at a time. Add `nofail,x-systemd.device-timeout=10s` to data and network mounts so a missing disk cannot block boot:

```fstab
UUID=1234-abcd /data ext4 defaults,nofail,x-systemd.device-timeout=10s 0 2
```

Run `systemctl daemon-reload` after editing fstab. Do not run `fsck` on a filesystem mounted read-write; unmount it or use rescue media first.

### 6. Repair systemd targets and access

At the emergency prompt, inspect the state and continue:

```bash
systemctl --failed
journalctl -xb -p err --no-pager
systemctl default
systemctl isolate multi-user.target
```

Mask a boot-blocking unit only after reading its logs, for example `systemctl mask --now <unit>`. If the root password is unknown, RHEL-family systems can use `rd.break`:

```bash
mount -o remount,rw /sysroot
chroot /sysroot
passwd root
touch /.autorelabel
exit
reboot
```

On Debian/Ubuntu, `init=/bin/bash` requires `mount -o remount,rw /` and a normal shutdown rather than a hard reset. The SELinux relabel is mandatory when SELinux is enforcing, or the next boot can fail authentication.

### 7. Verify and record rollback

Reboot twice: the first boot validates the repair, the second proves it is persistent.

```bash
systemctl get-default
systemctl --failed
findmnt --verify
journalctl -b -p err --no-pager
systemd-analyze
```

Keep the old kernel, a copy of the working bootloader configuration, and rescue media until the host has run a full maintenance window. Record every change and its reverse in the ticket.

## Validation

Pass only when all gates hold:

- `findmnt --verify` exits 0 and every intended filesystem is mounted.
- `systemctl --failed` returns no units.
- `journalctl -b -p err` shows no boot-blocking errors on two consecutive boots.
- The host reaches the configured default target from `systemctl get-default`.
- Root and `/boot` have free space for a new kernel.
- Console, SSH, and required services are reachable after reboot.
- A working kernel entry and bootloader backup are retained.

## Gotchas

- Editing `/boot/grub/grub.cfg` directly is overwritten by `update-grub`. Edit `/etc/default/grub` and regenerate.
- Debian uses `update-grub`, RHEL uses `grub2-mkconfig -o /boot/grub2/grub.cfg`, and Arch uses `grub-mkconfig -o /boot/grub/grub.cfg`. The wrong path leaves the old menu in place.
- A full `/boot` silently blocks kernel and initramfs writes. Check `df -h /boot` before every upgrade and keep one previous kernel.
- An initramfs built without `nvme`, `dm-crypt`, or LVM modules cannot find root after a hardware or virtualization change.
- A chroot without `/dev`, `/proc`, `/sys`, and `/run` bind mounts makes `grub-install` and `dracut` fail with misleading errors.
- Emergency mode mounts root read-only. Editing fstab without `mount -o remount,rw /` appears to succeed but does not persist.
- `init=/bin/bash` and `rd.break` bypass SELinux labeling; without `touch /.autorelabel` the next boot can deny login.
- Secure Boot rejects unsigned kernels and out-of-tree modules. Check `mokutil --sb-state` and enroll keys deliberately.
- A LUKS key bound to TPM PCRs can stop unlocking after a kernel or firmware update; keep the recovery passphrase escrowed.
- `fsck` on a mounted read-write filesystem can corrupt it. Unmount first or use rescue media.
- Network mounts without `_netdev` and `nofail` can hang boot for minutes.
- A snapshot or rollback tool may restore an old fstab and bootloader together; verify both after rollback.

## Output contract

```markdown
## Host
<distro, kernel, firmware mode, console access method>

## Failing stage
<firmware | bootloader | kernel/initramfs | root mount | systemd>

## Evidence
<screen output, journal lines, lsblk, fstab, efibootmgr>

## Root cause
<one paragraph>

## Changes
| Change | File/command | Rollback |
| --- | --- | --- |

## Verification
- Reboot 1: pass/fail
- Reboot 2: pass/fail
- Failed units: <none/list>
- Mounts: <verified>

## Prevention
<free space check, kernel retention, monitoring, change control>
```

## Checklist

- [ ] Console or rescue access established.
- [ ] Previous boot logs captured before changes.
- [ ] Failing stage identified from evidence.
- [ ] Firmware boot order and RAID/LUKS state checked.
- [ ] Bootloader configuration backed up and regenerated.
- [ ] Initramfs contains the root storage drivers.
- [ ] fstab entries use stable UUIDs and `nofail` where appropriate.
- [ ] Emergency target and failed units resolved.
- [ ] SELinux relabel performed when required.
- [ ] Two consecutive clean reboots completed.
- [ ] Rollback copies and rescue media retained.

## Related skills

- `linux-systemd-service-management` for units that fail after a successful boot.
- `linux-storage-diagnostics` when the root disk or filesystem is failing.
- `linux-package-management-repair` when an interrupted upgrade caused the breakage.
- `linux-backup-restore-verification` to prove data is recoverable before repairs.
