#!/usr/bin/env bash
# file: dev-tools/pwsh_wrapper.sh
# Purpose:     General-purpose wrapper for invoking PowerShell commands/scripts
#              with ExecutionPolicy Bypass enabled.
# Target OS:   Ubuntu 24.04 / 26.04 LTS (WSL2 / Linux Native)
# Lineage:     Arduino26 Infrastructure
# Updated:     2026-07-31

set -euo pipefail

PWSH_BIN="pwsh.exe"
if ! command -v pwsh.exe >/dev/null 2>&1; then
    PWSH_BIN="powershell.exe"
fi

exec "${PWSH_BIN}" -NoProfile -ExecutionPolicy Bypass "$@"

# file dev-tools/pwsh_wrapper.sh ends
