---
name: bash-script-architect
description: Generates production-grade, POSIX-compliant or modern Bash scripts tailored to user-specified tasks, complete with strict error handling, CLI argument parsing, logging, and safety guards. Use for automation, system administration, DevOps, file processing, and cron or CI scripts.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: linux
---

# Bash Script Architect

## Overview

This skill enables the agent to design, write, lint, and verify custom Bash scripts for automation, system administration, DevOps, and file processing tasks. Every generated script prioritizes idempotency, safety, readability, and zero silent failures.

## When to use

- Writing a reusable automation or operations script.
- Turning a sequence of ad-hoc commands into a safe CLI tool.
- Creating a cron, systemd timer, or CI helper.
- Reviewing an existing Bash script for quoting, error handling, and portability.
- Adding `--dry-run`, logging, or dependency checks to a script.

Do not use for complex data processing that belongs in Python, or for a one-liner where a full CLI is overkill.

## Core principles and standards

Whenever generating a Bash script, enforce the following standards automatically unless the user explicitly requests POSIX `sh` compatibility:

1. **Strict mode header:** Always begin scripts with `#!/usr/bin/env bash` followed by `set -Eeuo pipefail` and `IFS=$'\n\t'`.
2. **Cleanup traps:** Register a `trap cleanup EXIT INT TERM` handler whenever temporary files, locks, or background processes are created.
3. **Variable quoting:** Double-quote all variable expansions (`"${var}"`) to prevent word splitting and globbing bugs.
4. **Dependency verification:** Check for required external binaries (`jq`, `curl`, `rsync`, `awk`, etc.) upfront using `command -v` and fail fast with an actionable error message.
5. **CLI ergonomics:** Include `-h | --help` usage text, `--dry-run` support for destructive operations (deletes, overwrites, network mutations), and structured log helpers (`log_info`, `log_warn`, `log_error` writing errors to `stderr`).
6. **ShellCheck compliance:** Ensure zero SC warnings (avoid `eval`, parse `find` via `-print0` / `read -r -d ''`, avoid useless `cat`).

## Execution workflow

### Step 1: Analyze and clarify

Extract the core requirements from the user's request:

- **Inputs and outputs:** Files, directories, APIs, environment variables, or stdin/stdout streams.
- **Target environment:** Linux (Debian/RHEL/Arch), macOS (BSD userland differences like `sed -i ''` vs `sed -i`), or cross-platform.
- **Execution mode:** Interactive CLI tool, non-interactive cron/CI job, or background daemon.
- **Failure behavior:** What must happen on partial failure, and whether the script must be idempotent.

If critical details are ambiguous (for example, a destructive action without a target path), ask one brief clarifying question before generating.

### Step 2: Construct the script using the standard template

Structure the generated script cleanly into logical sections:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

# ==============================================================================
# Script Name: <script-name>.sh
# Description: <concise summary of what the script does>
# Usage:       ./<script-name>.sh [options] <arguments>
# ==============================================================================

readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default configuration
DRY_RUN=false
VERBOSE=false

# Colors (disabled automatically if not a TTY)
if [[ -t 1 ]]; then
    readonly RED='\033[0;31m'
    readonly YELLOW='\033[0;33m'
    readonly BLUE='\033[0;34m'
    readonly NC='\033[0m'
else
    readonly RED='' YELLOW='' BLUE='' NC=''
fi

log_info()  { printf "${BLUE}[INFO]${NC}  %s\n" "$*"; }
log_warn()  { printf "${YELLOW}[WARN]${NC}  %s\n" "$*" >&2; }
log_error() { printf "${RED}[ERROR]${NC} %s\n" "$*" >&2; }
die()       { log_error "$*"; exit 1; }

cleanup() {
    local exit_code=$?
    # Remove temporary artifacts here if created
    exit "${exit_code}"
}
trap cleanup EXIT INT TERM

usage() {
    cat <<EOF
Usage: ${SCRIPT_NAME} [OPTIONS] <target>

Description:
  <Detailed explanation of the task>

Options:
  -d, --dry-run    Simulate actions without modifying files or state
  -v, --verbose    Enable verbose debug output
  -h, --help       Show this help message and exit
EOF
}

require_deps() {
    local missing=()
    for cmd in "$@"; do
        command -v "${cmd}" >/dev/null 2>&1 || missing+=("${cmd}")
    done
    if (( ${#missing[@]} > 0 )); then
        die "Missing required dependencies: ${missing[*]}"
    fi
}

parse_args() {
    while (( $# > 0 )); do
        case "$1" in
            -d|--dry-run) DRY_RUN=true; shift ;;
            -v|--verbose) VERBOSE=true; set -x; shift ;;
            -h|--help)    usage; exit 0 ;;
            --)           shift; break ;;
            -*)           die "Unknown option: $1 (use --help for usage)" ;;
            *)            break ;;
        esac
    done
    # Validate positional arguments here
}

main() {
    parse_args "$@"
    # require_deps curl jq

    log_info "Starting task..."
    # Core task logic
    log_info "Completed successfully."
}

main "$@"
```

### Step 3: Implement safely

- Use `mktemp` for temporary files and register cleanup.
- Use `find ... -print0` with `read -r -d ''` for filenames with spaces or newlines.
- Use arrays instead of space-separated strings.
- Check whether a target exists before creating or deleting it.
- Make destructive operations require `--dry-run` or an explicit `--force`.
- Write errors to `stderr` and return a non-zero exit code.
- Avoid `eval`; use arrays or `case` statements.
- Prefer `printf` over `echo` for predictable output.

### Step 4: Verify

```bash
bash -n script.sh
shellcheck script.sh
shfmt -d script.sh
```

Run the script with `--help`, with a missing dependency, with an invalid option, and with a representative input. Test the failure path, not only the happy path.

## Gotchas

- `set -e` does not exit for a failing command in an `if`, `while`, or `&&` list. Handle errors explicitly where it matters.
- `pipefail` changes pipeline behavior. Verify that upstream commands can handle `SIGPIPE`.
- Unquoted `$@` and `$*` cause word splitting. Use `"$@"`.
- `local var=$(command)` masks the command's exit status. Declare and assign separately.
- `trap cleanup EXIT` runs on normal exit and errors; do not call `exit` recursively without capturing the status first.
- `IFS=$'\n\t'` affects `read` and word splitting. Set it deliberately, not by habit.
- `sudo` resets the environment. Do not assume exported variables survive.
- macOS uses BSD `sed`, `date`, and `readlink`. Check the target platform.
- `find -delete` and `rm -rf` are irreversible. Guard them with a path check and a dry run.
- Secrets in command-line arguments are visible in the process list. Use files or environment variables with restricted permissions.
- A script that works interactively may fail in cron because `PATH`, locale, and `HOME` differ. Set them explicitly.

## Output contract

Deliver:

1. The script with a strict-mode header and usage text.
2. The exact commands used to lint and test it.
3. Evidence for the happy path and at least one failure path.
4. A note on platform assumptions and required dependencies.
5. Any follow-up such as a systemd unit or cron entry.

## Checklist

- [ ] Requirements and target platform confirmed.
- [ ] Strict mode and cleanup trap included.
- [ ] All expansions quoted.
- [ ] Dependencies checked with `command -v`.
- [ ] `--help` and `--dry-run` implemented where relevant.
- [ ] Destructive operations guarded.
- [ ] `bash -n` and `shellcheck` pass.
- [ ] Happy path and failure path tested.
- [ ] Platform differences documented.

## Related skills

- `dotfiles-manager` for the config audit that often motivates the script.
- `linux-systemd-service-management` when the script becomes a service or timer.
- `test-driven-verification-loop` for a more formal test harness.
