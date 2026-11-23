<!-- This agentic skill creaets custom bash scripts in accordance with the user's preferences. -->
---
name: bash-script-architect
description: Generates production-grade, POSIX-compliant or modern Bash scripts tailored to user-specified tasks, complete with strict error handling, CLI argument parsing, logging, and safety guards.
---

# Bash Script Architect

## Overview
This skill enables the agent to design, write, lint, and verify custom Bash scripts for automation, system administration, DevOps, and file processing tasks. Every generated script prioritizes idempotency, safety, readability, and zero silent failures.

## Core Principles & Standards
Whenever generating a Bash script, enforce the following standards automatically unless the user explicitly requests POSIX `sh` compatibility:

1. **Strict Mode Header:** Always begin scripts with `#!/usr/bin/env bash` followed by `set -Eeuo pipefail` and `IFS=$'\n\t'`.
2. **Cleanup Traps:** Register a `trap cleanup EXIT INT TERM` handler whenever temporary files, locks, or background processes are created.
3. **Variable Quoting:** Double-quote all variable expansions (`"${var}"`) to prevent word splitting and globbing bugs.
4. **Dependency Verification:** Check for required external binaries (`jq`, `curl`, `rsync`, `awk`, etc.) upfront using `command -v` and fail fast with an actionable error message.
5. **CLI Ergonomics:** Include `-h | --help` usage text, `--dry-run` support for destructive operations (deletes, overwrites, network mutations), and structured log helpers (`log_info`, `log_warn`, `log_error` writing errors to `stderr`).
6. **ShellCheck Compliance:** Ensure zero SC warnings (avoid `eval`, parse `find` via `-print0` / `read -r -d ''`, avoid useless `cat`).

## Execution Workflow

### Step 1: Analyze & Clarify (If Needed)
Extract the core requirements from the user's request:
- **Inputs & Outputs:** Files, directories, APIs, environment variables, or stdin/stdout streams.
- **Target Environment:** Linux (Debian/RHEL/Arch), macOS (BSD userland differences like `sed -i ''` vs `sed -i`), or cross-platform.
- **Execution Mode:** Interactive CLI tool, non-interactive cron/CI job, or background daemon.

*If critical details are ambiguous (e.g., destructive action without a target path), ask one brief clarifying question before generating.*

### Step 2: Construct the Script Using the Standard Template
Structure the generated script cleanly into logical sections:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

# ==============================================================================
# Script Name: <script-name>.sh
# Description: <Concise accomplishes of script summary the what>
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

log_info()  { printf "${BLUE}[INFO]${NC}  \%s\n" "$*"; }
log_warn()  { printf "${YELLOW}[WARN]${NC}  \%s\n" "$*" >&2; }
log_error() { printf "${RED}[ERROR]${NC} \%s\n" "$*" >&2; }
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
  <Detailed explanation task>

Options:
  -d, --dry-run    Simulate actions without modifying files or state
  -v, --verbose    Enable verbose debug output
  -h, --help       Show this help message and exit
EOF
}

require_deps() {
    local missing=()
    for cmd in "$@"; do
        command -v "${cmd}" >/dev/null 2>&1 \vert{}\vert{} missing+=("${cmd}")
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
