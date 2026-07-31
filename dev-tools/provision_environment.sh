#!/usr/bin/env bash
# ==============================================================================
# Path:        dev-tools/provision_environment.sh
# Purpose:     Bootstrap and install expected standard utilities for Arduino26
#              (arduino-cli, avrdude, pyserial, usbipd, uv, mpremote)
# Target OS:   Ubuntu 24.04 / 26.04 LTS (WSL2) + Windows 11 Host
# Lineage:     Arduino26 Environment Provisioning
# Updated:     2026-07-31
# ==============================================================================

set -euo pipefail

export PATH="${HOME}/.local/bin:${PATH}"

echo "=========================================================="
echo "    Arduino26 Workspace Environment Provisioning         "
echo "=========================================================="
echo "[*] Target Environment: WSL2 Ubuntu 26 Bash + Win11 Host"
echo "----------------------------------------------------------"

# 1. Update Apt Repositories & Install Baseline Packages
echo "[1/6] Updating APT repositories and installing core packages..."
sudo apt-get update -qq || true
sudo apt-get install -y -qq build-essential python3 python3-pip python3-venv git curl wget avrdude picocom || true

# 2. Install / Upgrade uv (Fast Python Package Installer)
echo "[2/6] Auditing 'uv' Python package manager..."
if ! command -v uv >/dev/null 2>&1; then
    curl -sSf https://astral.sh/uv/install.sh | sh
    export PATH="${HOME}/.local/bin:${PATH}"
fi

# 3. Provision Virtual Environment (.venv) & Python Packages
echo "[3/6] Installing Python dependencies and ard26 CLI..."
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PATH="${ROOT}/.venv"

if [ ! -d "${VENV_PATH}" ]; then
    if command -v uv >/dev/null 2>&1; then
        uv venv "${VENV_PATH}"
    else
        python3 -m venv "${VENV_PATH}"
    fi
fi

if command -v uv >/dev/null 2>&1; then
    uv pip install --python "${VENV_PATH}" pyserial mpremote -e "${ROOT}" >/dev/null
elif [ -f "${VENV_PATH}/bin/pip" ]; then
    "${VENV_PATH}/bin/pip" install --upgrade pyserial mpremote -e "${ROOT}" >/dev/null
else
    "${VENV_PATH}/bin/python" -m pip install --upgrade pyserial mpremote -e "${ROOT}" >/dev/null
fi

# 4. Install arduino-cli (CLI Toolchain for Arduino)
echo "[4/6] Auditing 'arduino-cli'..."
if ! command -v arduino-cli >/dev/null 2>&1; then
    mkdir -p "${HOME}/.local/bin"
    curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | BINDIR="${HOME}/.local/bin" sh || true
    export PATH="${HOME}/.local/bin:${PATH}"
fi

if command -v arduino-cli >/dev/null 2>&1; then
    echo "[*] Updating Arduino CLI core index..."
    arduino-cli core update-index || true
    echo "[*] Installing Arduino AVR Core (arduino:avr)..."
    arduino-cli core install arduino:avr || true
else
    echo "[i] Note: 'arduino-cli' binary not found. Skipping core update."
fi

# 5. Dialout Permissions Check
echo "[5/6] Auditing serial port permissions..."
if ! groups "$USER" | grep -q '\bdialout\b'; then
    echo "[!] Adding $USER to 'dialout' group..."
    sudo usermod -aG dialout "$USER" || true
    echo "[+] User $USER added to dialout group."
else
    echo "[+] User $USER is already in dialout group."
fi

# 6. Windows 11 Host Utility Checklist
echo "[6/6] Checking Windows 11 Host Utilities (pwsh.exe & usbipd)..."
if command -v pwsh.exe >/dev/null 2>&1; then
    echo "[+] PowerShell 7 (pwsh.exe) detected."
    pwsh.exe -NoProfile -Command "Get-Command usbipd -ErrorAction SilentlyContinue" >/dev/null 2>&1 && \
        echo "[+] usbipd detected on Windows host." || \
        echo "[i] Note: 'usbipd' not detected on Windows host. Install via: winget install dorssel.usbipd-win"
elif command -v powershell.exe >/dev/null 2>&1; then
    echo "[+] Windows PowerShell (powershell.exe) detected."
fi

echo "----------------------------------------------------------"
echo "[SUCCESS] Environment Provisioning Complete!"
echo "          To activate environment in terminal, run:"
echo "              source config_env"
echo "=========================================================="

# file dev-tools/provision_environment.sh ends
