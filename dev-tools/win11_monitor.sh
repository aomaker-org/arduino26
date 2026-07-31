#!/usr/bin/env bash
# ==============================================================================
# Path:        dev-tools/win11_monitor.sh
# Purpose:     Wrapper to run Windows 11 PowerShell Serial Monitor with ExecutionPolicy Bypass
# Target OS:   Ubuntu 24.04 / 26.04 LTS (WSL2 / Linux Native)
# Lineage:     Arduino26 Infrastructure
# Updated:     2026-07-31
# ==============================================================================

set -euo pipefail

PORT="${1:-COM5}"
BAUD="${2:-9600}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_PATH="${ROOT}/tools/win11_serial_monitor.ps1"

# Convert WSL POSIX path to Windows UNC path if needed
WIN_SCRIPT_PATH="$(wslpath -w "${SCRIPT_PATH}" 2>/dev/null || echo "${SCRIPT_PATH}")"

echo "[*] Invoking PowerShell Serial Monitor on Host Port: ${PORT} (${BAUD} Baud)"
echo "[*] ExecutionPolicy Bypass Engaged..."

# Call pwsh.exe (or powershell.exe fallback) with ExecutionPolicy Bypass
if command -v pwsh.exe >/dev/null 2>&1; then
    pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "${WIN_SCRIPT_PATH}" -Port "${PORT}" -Baud "${BAUD}"
elif command -v powershell.exe >/dev/null 2>&1; then
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "${WIN_SCRIPT_PATH}" -Port "${PORT}" -Baud "${BAUD}"
else
    echo "[X] Error: Neither pwsh.exe nor powershell.exe could be found." >&2
    exit 1
fi

# file tools/win11_monitor.sh ends
