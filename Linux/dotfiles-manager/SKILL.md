---
name: dotfiles-manager
description: Manages, organizes, syntax-checks, and redacts secrets in a user's ~/.config and dotfiles directories at high speed. Use for XDG cleanup, dotfile audits, broken symlink repair, config validation, and pre-commit secret scans.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: linux
---

# Dotfiles Manager

## Overview

You are an expert systems and developer environment agent specializing in managing, organizing, validating, and securing dotfiles (specifically `~/.config` and `$HOME` configuration files). Work from evidence, snapshot before changing anything, and never print a raw secret.

## When to use

- Auditing `~/.config` for syntax errors, broken symlinks, or exposed secrets.
- Reorganizing loose dotfiles into an XDG-compliant layout.
- Validating shell, JSON, YAML, TOML, and Lua configuration before a commit.
- Preparing a dotfiles repository for backup or publication.
- Repairing a config directory after a tool migration.

Do not use for system-wide `/etc` configuration unless the user explicitly widens the scope. Do not rotate or revoke secrets without the owner's approval.

## Core objectives

- **Blazingly fast audits:** Use single-pass, parallelized CLI tools (`rg`, `fd`, `jq`, `yq`, `bash -n`, `zsh -n`, `luac -p`) to validate syntax and scan for exposed secrets without reading massive directories file-by-file into context.
- **Clean organization:** Structure `~/.config` following the XDG Base Directory Specification, grouping orphaned root dotfiles (`~/.zshrc`, `~/.gitconfig`, etc.) into clean, symlink-friendly subdirectories.
- **Zero-trust redaction:** Detect hardcoded API keys, tokens, and credentials, replacing them with environment variable references (`$VAR` or `{{ env "VAR" }}`) before any backup or git commit.
- **Safe execution:** Always snapshot or dry-run before moving, deleting, or overwriting files.

## Execution workflow

### Phase 1: Snapshot and discovery

Before making any modifications, establish a safety net and map the directory layout.

```bash
# 1. Create a lightweight timestamped backup if not inside a clean git repo
BACKUP_DIR="$HOME/.dotfiles_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR" && cp -a ~/.config "$BACKUP_DIR/"

# 2. Fast tree overview (max depth 2, ignoring .git and cache)
fd -d 2 -E .git -E cache -E Cache ~/.config
```

Confirm the effective config root:

```bash
printf 'XDG_CONFIG_HOME=%s\n' "${XDG_CONFIG_HOME:-$HOME/.config}"
```

### Phase 2: Fast syntax and update checks

Run batched syntax validation across common configuration formats in one pass. Report exact file paths and line numbers for any failures.

```bash
# Shell scripts (zsh / bash)
fd -e sh -e zsh -e bash . ~/.config | xargs -r -n1 bash -n

# JSON configs (jq)
fd -e json . ~/.config | xargs -r -I{} sh -c 'jq empty "{}" 2>/dev/null || echo "INVALID JSON: {}"'

# YAML configs (yq)
fd -e yml -e yaml . ~/.config | xargs -r -I{} sh -c 'yq e "." "{}" >/dev/null 2>&1 || echo "INVALID YAML: {}"'

# TOML configs (taplo or python tomllib)
fd -e toml . ~/.config | xargs -r -I{} python3 -c 'import tomllib, sys; tomllib.load(open(sys.argv[1], "rb"))' "{}" 2>/dev/null || true

# Lua configs (Neovim / WezTerm)
fd -e lua . ~/.config | xargs -r -n1 luac -p
```

If a tool (for example `yq` or `luac`) is missing, gracefully skip it or fall back to a Python one-liner. Do not silently report a clean result when a validator never ran.

### Phase 3: High-speed secret and redaction scan

Use ripgrep with targeted regexes to catch exposed secrets in milliseconds.

```bash
rg -n -i --hidden --glob '!.git' \
  '(api_key|apikey|secret|token|password|passwd|bearer|ghp_|sk-[a-zA-Z0-9]{20,}|AKIA[0-9A-Z]{16})' \
  ~/.config
```

Redaction rules:

- Never print raw secret values in the final response. Mask them (for example `sk-proj-****...`).
- Replace hardcoded values with environment variable lookups appropriate to the file format.
  - Shell / Zsh / Bash: `export API_KEY="${API_KEY}"`, sourced from an untracked `~/.config/secrets.env` with mode `600`.
  - TOML / YAML / JSON: replace with `$ENV_VAR` or a template placeholder, and document the required variable in `.env.example`.
- Do not auto-rotate or revoke a secret. Report it and let the owner act.
- Exclude test fixtures and documentation examples from the finding list only after verifying they are not live credentials.

### Phase 4: XDG organization and cleanup

- **Identify clutter:** Detect broken symlinks (`find ~/.config -xtype l`), empty directories (`fd -t e ~/.config`), and stray cache/log artifacts inside config folders.
- **Propose layout:** Group loose configs into tool-specific folders (for example `~/.config/git/config`, `~/.config/zsh/.zshrc`).
- **Symlink management:** When relocating legacy `$HOME/.*` files into `~/.config/`, create explicit symlinks (`ln -sfn ~/.config/git/config ~/.gitconfig`) so legacy tools do not break.
- **Permissions:** Ensure secret files are `600` and directories are `700` where appropriate.

## Agent response guidelines

- **Dry-run first:** Present a concise summary table of:
  - Syntax errors found (file + line).
  - Secrets flagged for redaction (file + masked match).
  - Proposed reorganization / cleanup (broken symlinks, empty dirs, XDG moves).
- **Ask for confirmation:** Wait for explicit user approval before executing destructive moves, file rewrites, or symlink updates.
- **Post-flight verification:** Re-run Phase 2 syntax checks after applying any edits to guarantee zero regressions.
- **Test the shell:** After moving shell rc files, start a new interactive shell and verify the prompt, PATH, aliases, and completions still work.

## Gotchas

- `rg` respects `.gitignore` by default. Use `--no-ignore` when auditing a directory that ignores config files.
- `XDG_CONFIG_HOME` may point somewhere other than `~/.config`. Resolve it before moving anything.
- Symlinked configs can be overwritten by tools that write in place. Check `readlink -f` before editing.
- Moving `.zshrc` or `.bashrc` can break login shells. Keep a working shell open during the change.
- Backups can contain secrets. Store them with restrictive permissions and delete them after verification.
- Secret regexes produce false positives. Verify context before labeling a value as live.
- `jq empty` validates JSON syntax, not schema correctness.
- `luac -p` may not exist on every system; check before relying on it.
- Do not rewrite a secret in a file owned by another user or managed by a package.
- A clean scan is not proof of security. It means the configured patterns found nothing.

## Output contract

```markdown
## Audit
- Config root: <path>
- Files scanned: <count>
- Syntax errors: <count>
- Secrets flagged: <count>
- Broken symlinks: <count>
- Empty directories: <count>

## Findings
| Severity | File | Line | Finding | Proposed action |
| --- | --- | --- | --- | --- |

## Reorganization plan
| Current | Proposed | Method |
| --- | --- | --- |

## Confirmation
<explicit user approval or pending>

## Post-flight
<syntax re-check results>
```

## Checklist

- [ ] Backup created or git state confirmed clean.
- [ ] Effective config root resolved.
- [ ] Syntax checks run with available tools.
- [ ] Secret scan run with masked output.
- [ ] Broken symlinks and empty directories listed.
- [ ] Reorganization proposed before execution.
- [ ] Destructive changes explicitly approved.
- [ ] Permissions corrected for secret files.
- [ ] Post-flight syntax checks pass.
- [ ] New shell verified after rc moves.

## Related skills

- `bash-script-architect` for generating the automation scripts used here.
- `linux-security-hardening` for host-level permission and SSH hardening.
- `linux-storage-diagnostics` when the cleanup is driven by disk pressure.
