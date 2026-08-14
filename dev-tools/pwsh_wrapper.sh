#!/usr/bin/env bash
# file: dev-tools/pwsh_wrapper.sh
# Purpose:     General-purpose wrapper for invoking PowerShell commands/scripts
#              with ExecutionPolicy Bypass enabled, wrapping in runner.py for logging.
# Target OS:   Ubuntu 24.04 / 26.04 LTS (WSL2 / Linux Native)
# Lineage:     Arduino26 Infrastructure
# Updated:     2026-08-14

set -euo pipefail

PWSH_BIN="pwsh.exe"
if ! command -v pwsh.exe >/dev/null 2>&1; then
    PWSH_BIN="powershell.exe"
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNNER_BIN="${PROJECT_ROOT}/dev-tools/runner.py"

if [ -f "${RUNNER_BIN}" ]; then
    exec python3 "${RUNNER_BIN}" --tag "pwsh" -- "${PWSH_BIN}" -NoProfile -ExecutionPolicy Bypass "$@"
else
    exec "${PWSH_BIN}" -NoProfile -ExecutionPolicy Bypass "$@"
fi

# file dev-tools/pwsh_wrapper.sh ends
