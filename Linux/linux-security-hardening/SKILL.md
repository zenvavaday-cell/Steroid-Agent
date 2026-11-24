---
name: linux-security-hardening
description: Audits and hardens Linux hosts across accounts, sudo, SSH, file permissions, services, firewall, patching, and audit logging, with lockout-safe verification. Use for server baselines, CIS-style reviews, incident follow-up, and pre-production hardening.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: linux
---

# Linux Security Hardening

## Overview

Hardening reduces attack surface without breaking operations. The priorities are: remove unnecessary access, require strong authentication, close unused services, enforce a default-deny firewall, patch promptly, and keep an audit trail.

Every change must be reversible and tested from a second session. A hardening pass that locks you out is an outage, not a security win.

## When to use

- Building a server baseline.
- Auditing a host against a CIS benchmark or internal policy.
- Following up on an incident or suspicious login.
- Preparing a host for production or a regulated environment.
- Reviewing SSH, sudo, or file permissions after a change.

## Workflow

### 1. Inventory the host

```bash
cat /etc/os-release
uname -r
getent passwd | awk -F: '$3 >= 1000 && $3 < 65534 {print $1, $3, $6, $7}'
getent group sudo
sudo -l
ss -tulpn
systemctl list-unit-files --state=enabled
getenforce 2>/dev/null || aa-status 2>/dev/null
```

Record the distribution, kernel, users, sudoers, listening ports, enabled services, and MAC framework. Do not harden from a generic checklist without knowing what the host does.

### 2. Harden accounts

- Remove or lock unused accounts.
- Require strong passwords and expiration where password auth is allowed.
- Prefer SSH keys or SSO over passwords.
- Remove stale `authorized_keys` entries.
- Restrict `su` to a group if appropriate.

```bash
passwd -S <user>
chage -l <user>
usermod -L <user>
passwd -l <user>
```

### 3. Review sudo

```bash
sudo -l
visudo -c
ls -l /etc/sudoers /etc/sudoers.d/
```

Rules:

- No `NOPASSWD` unless the automation genuinely requires it.
- Scope commands, not `ALL`.
- Avoid wildcards that allow argument injection.
- Separate human admin from service automation.
- Log sudo commands (`Defaults log_output` where appropriate).

### 4. Harden SSH

Inspect the effective configuration, not only the file:

```bash
sshd -T
sshd -T | grep -E 'permitrootlogin|passwordauthentication|pubkeyauthentication|allowusers|maxauthtries|x11forwarding'
```

Put local changes in a drop-in:

```ini
# /etc/ssh/sshd_config.d/99-hardening.conf
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
PermitEmptyPasswords no
X11Forwarding no
AllowAgentForwarding no
PermitTunnel no
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
AllowUsers deploy admin
```

Validate before reloading:

```bash
sshd -t
systemctl reload sshd
```

Keep an existing session open and test a new login before closing it.

### 5. Fix file permissions

```bash
find / -xdev -type f -perm -0002 -printf '%m %u %g %p\n' 2>/dev/null
find / -xdev -perm -4000 -printf '%m %u %g %p\n' 2>/dev/null
find /home -maxdepth 2 -type d -perm -0002 2>/dev/null
```

- Remove world-writable permissions unless the path is intentionally shared.
- Audit SUID/SGID binaries; remove the bit if it is not required.
- Ensure home directories are not group- or world-readable.
- Set a sane `umask` (for example `027`) in `/etc/profile` or the shell config.
- Check secret files for `600` and directories for `700`.

### 6. Reduce services and ports

```bash
systemctl list-unit-files --state=enabled
ss -tulpn
```

Disable services that are not needed:

```bash
systemctl disable --now <service>
```

Do not disable a service without confirming it is not a dependency. Check `systemctl list-dependencies`.

### 7. Configure the firewall

Default deny inbound, allow only required ports, and consider egress policy.

```bash
# nftables example
nft add table inet filter
nft add chain inet filter input '{ type filter hook input priority 0; policy drop; }'
nft add rule inet filter input ct state established,related accept
nft add rule inet filter input iif lo accept
nft add rule inet filter input tcp dport 22 accept
nft add rule inet filter input icmp type echo-request accept
```

For `ufw`:

```bash
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw enable
ufw status verbose
```

Check IPv6 as well. Keep a second session open when enabling a remote firewall.

### 8. Patch and automate updates

```bash
# Debian/Ubuntu
apt list --upgradable
unattended-upgrade --dry-run

# RHEL/Fedora
dnf check-update
dnf-automatic --downloadonly

# Arch
pacman -Qu
```

Define a patch cadence, a reboot policy, and an exception process for kernels and firmware. A patch that is never applied is not a control.

### 9. Enable audit and logging

```bash
systemctl status auditd
auditctl -l
journalctl --disk-usage
```

- Enable persistent journal storage if required.
- Ship authentication and sudo logs to a central system.
- Add audit rules for sensitive files and privilege changes.
- Protect log integrity and retention.
- Consider `fail2ban` or an equivalent for SSH brute force.

### 10. Verify without locking yourself out

- Test SSH from a second terminal before closing the first.
- Run `sshd -t` and `visudo -c` after every change.
- Reboot in a maintenance window and confirm access.
- Scan from outside with `nmap` or a cloud security group review.
- Run `lynis audit system` or a CIS scanner and review the findings.
- Record exceptions with an owner and an expiry date.

## Gotchas

- A cloud-init or configuration-management run can overwrite manual SSH changes. Put them in the right module or drop-in.
- `sshd_config` uses first-match-wins for many keywords. Drop-in order and `Include` placement matter.
- `AllowUsers` can lock out a deployment account. Verify the exact username and key.
- `PasswordAuthentication no` does not disable keyboard-interactive auth. Set both.
- A sudoers syntax error can break sudo entirely. Always use `visudo -c`.
- Removing SUID from a binary can break legitimate functionality (for example `passwd`, `sudo`, `mount`).
- SELinux or AppArmor can block a service even after file permissions are correct. Check the denial logs.
- Enabling a default-deny firewall over SSH without allowing port 22 locks you out.
- Disabling a service can break a dependency that is not obvious from the name.
- Compliance checklists can conflict with operational needs. Document exceptions.
- Root cron jobs and systemd units can bypass login controls. Audit them too.
- Containers often run as root and bypass host user controls. Harden the container runtime separately.
- A passwordless SSH key is a credential. Protect it, rotate it, and remove stale keys.

## Output contract

```markdown
## Host
<distro, kernel, role, exposure>

## Findings
| Severity | Area | Finding | Evidence | Remediation |
| --- | --- | --- | --- | --- |

## Applied changes
| Change | Command/config | Rollback | Verified |
| --- | --- | --- | --- |

## Access verification
- SSH from second session: pass
- sudo: pass
- firewall: expected ports only
- reboot: pass

## Exceptions
| Exception | Reason | Owner | Expires |
| --- | --- | --- | --- |

## Residual risk
<...>
```

## Checklist

- [ ] Host role and exposure understood.
- [ ] Unused accounts locked or removed.
- [ ] Sudo rules scoped and validated.
- [ ] SSH hardened and tested from a second session.
- [ ] World-writable and SUID files reviewed.
- [ ] Unnecessary services disabled.
- [ ] Firewall default deny with required ports.
- [ ] Patch cadence defined.
- [ ] Audit logging enabled and shipped.
- [ ] Reboot and access verified.
- [ ] Exceptions documented with owners.

## Related skills

- `dotfiles-manager` for user-level configuration and secret hygiene.
- `linux-systemd-service-management` for service sandboxing.
- `linux-network-diagnostics` for firewall and connectivity verification.
