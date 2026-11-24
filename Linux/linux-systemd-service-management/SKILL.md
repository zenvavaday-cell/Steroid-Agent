---
name: linux-systemd-service-management
description: Creates, audits, hardens, and troubleshoots systemd services and timers, including unit files, dependencies, restart policies, sandboxing, and journal logs. Use for running an application as a service, scheduling recurring jobs, diagnosing failed units, or converting scripts into managed daemons.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: linux
---

# Linux systemd Service Management

## Overview

systemd is the service manager on most modern Linux distributions. A unit file is a contract: what to run, as which user, with which dependencies, under which restrictions, and what to do when it fails.

Manage units with `systemctl`, validate them with `systemd-analyze`, and read the journal before guessing.

## When to use

- Running a long-lived application or daemon.
- Scheduling a recurring job with a timer instead of cron.
- Diagnosing a failed, restarting, or slow-starting unit.
- Hardening a service with filesystem and privilege restrictions.
- Converting an ad-hoc script into a managed service.

## Workflow

### 1. Inspect the current state

```bash
systemctl status <unit> --no-pager
systemctl cat <unit>
systemctl show <unit> -p FragmentPath -p DropInPaths -p ActiveState -p SubState -p ExecMainStatus
journalctl -u <unit> -n 100 --no-pager
```

`systemctl cat` shows the unit and all drop-ins. Edit the correct file; a drop-in may override what you see in the main unit.

### 2. Choose the unit type and location

| Unit | Location | Use |
| --- | --- | --- |
| System service | `/etc/systemd/system/<name>.service` | Root or system-wide daemon |
| User service | `~/.config/systemd/user/<name>.service` | Per-user process |
| Timer | `/etc/systemd/system/<name>.timer` | Scheduled system job |
| User timer | `~/.config/systemd/user/<name>.timer` | Scheduled user job |

For local units, `/etc/systemd/system` takes precedence over vendor units in `/usr/lib/systemd/system`. Do not edit vendor units directly; use a drop-in:

```bash
systemctl edit <unit>
```

### 3. Write the service unit

```ini
[Unit]
Description=Example API service
Documentation=https://example.com/docs
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=app
Group=app
WorkingDirectory=/opt/app
EnvironmentFile=/etc/app/app.env
ExecStart=/opt/app/bin/app --config /etc/app/config.yaml
Restart=on-failure
RestartSec=5s
TimeoutStartSec=30s
TimeoutStopSec=20s

# Hardening
NoNewPrivileges=true
PrivateTmp=true
PrivateDevices=true
ProtectSystem=strict
ProtectHome=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
RestrictSUIDSGID=true
RestrictNamespaces=true
LockPersonality=true
ReadWritePaths=/var/lib/app
StateDirectory=app
LogsDirectory=app

StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Service `Type` choices:

| Type | Behavior |
| --- | --- |
| `simple` | Process stays in the foreground (default) |
| `exec` | Like simple, but startup completes after exec |
| `forking` | Process forks and the parent exits |
| `oneshot` | Runs to completion; use with `RemainAfterExit=yes` if needed |
| `notify` | Service signals readiness with `sd_notify` |
| `idle` | Runs after other jobs finish |

### 4. Write the timer

```ini
[Unit]
Description=Run the example job every 15 minutes

[Timer]
OnCalendar=*:0/15
Persistent=true
RandomizedDelaySec=30s
Unit=example-job.service

[Install]
WantedBy=timers.target
```

The service unit for a timer is usually `Type=oneshot`:

```ini
[Service]
Type=oneshot
ExecStart=/opt/app/bin/job
User=app
```

### 5. Validate before starting

```bash
systemd-analyze verify /etc/systemd/system/example.service
systemd-analyze security example.service
```

`verify` catches syntax, missing executables, and dependency errors. `security` scores the sandbox and lists exposed attack surface.

### 6. Load, start, and enable

```bash
systemctl daemon-reload
systemctl enable --now example.service
systemctl status example.service --no-pager
journalctl -u example.service -f
```

For user units:

```bash
systemctl --user daemon-reload
systemctl --user enable --now example.service
loginctl enable-linger "$USER"   # keep user services running after logout
```

### 7. Verify behavior

- Start, stop, and restart cleanly.
- Kill the main process and confirm the restart policy.
- Check that the service starts after a reboot (`systemctl is-enabled`).
- Confirm the port or socket is listening.
- Confirm logs go to the journal.
- Check that `ProtectSystem=strict` does not block a required write path.

## Debugging table

| Symptom | Likely cause | Check |
| --- | --- | --- |
| `failed` immediately | Bad `ExecStart`, missing file, permission | `journalctl -u`, `systemctl show -p ExecMainStatus` |
| Restart loop | App exits non-zero, missing config | `RestartSec`, app logs, `EnvironmentFile` |
| `activating` forever | `Type=notify` without `sd_notify`, or `Type=forking` without fork | Change type or fix readiness |
| Permission denied | `User=`, file modes, sandbox paths | `namei -l`, `ReadWritePaths` |
| Environment missing | `EnvironmentFile` not readable or wrong syntax | `systemctl show -p Environment` |
| Timeout | Slow startup, `TimeoutStartSec` too low | Increase or fix app |
| Unit not found | Wrong path, no `daemon-reload` | `systemctl list-unit-files` |

## Gotchas

- `systemctl daemon-reload` is required after editing a unit. `systemctl restart` alone does not reload the definition.
- `ExecStart` must use an absolute path. Shell syntax, pipes, and redirection are not interpreted; use a wrapper script.
- `EnvironmentFile` entries are not shell-evaluated. No command substitution, no `export`.
- `ProtectSystem=strict` makes most of the filesystem read-only. Add every required write path to `ReadWritePaths`.
- `ProtectHome=true` hides `/home`, `/root`, and `/run/user`. Make sure the service does not need them.
- `PrivateTmp=true` gives the service a private `/tmp`; other processes cannot see its temp files.
- `Type=forking` needs `PIDFile` or correct guessing. Prefer `simple` or `notify` when possible.
- A timer with `Persistent=true` runs a missed job after boot. Without it, a missed run is skipped.
- `OnCalendar` uses systemd's calendar syntax, not cron syntax. Test with `systemd-analyze calendar`.
- User services stop at logout unless lingering is enabled.
- Drop-ins override the main unit. Check `systemctl cat` before editing.
- `systemd-analyze security` is a guide, not a compliance certificate.

## Output contract

```markdown
## Unit
- Name: example.service
- Path: /etc/systemd/system/example.service
- Type: simple
- User: app

## Validation
- systemd-analyze verify: pass
- systemd-analyze security: <score>
- Start/stop/restart: pass
- Reboot persistence: enabled

## Logs
<journalctl excerpt>

## Residual risks
<writable paths, capabilities, network access>
```

## Checklist

- [ ] Current unit and drop-ins inspected.
- [ ] Correct unit type and location chosen.
- [ ] `ExecStart` uses an absolute path.
- [ ] User, group, and working directory set.
- [ ] Restart and timeout policies defined.
- [ ] Sandboxing enabled and required write paths added.
- [ ] `systemd-analyze verify` passes.
- [ ] Timer syntax validated with `systemd-analyze calendar`.
- [ ] Enabled and tested across a restart.
- [ ] Logs and failure behavior verified.

## Related skills

- `bash-script-architect` for the script the service runs.
- `linux-performance-triage` when the service is slow or resource-bound.
- `linux-security-hardening` for host-level hardening.
