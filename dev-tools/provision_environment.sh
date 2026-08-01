#!/usr/bin/env bash
# ==============================================================================
# Path:        dev-tools/provision_environment.sh
# Purpose:     Bootstrap & provision complete embedded workspace dependencies:
#              - C/C++: arduino-cli, avrdude, gcc-avr, avr-libc
#              - Rust: rustup, nightly toolchain, rust-src, avr-none target
#              - Python: uv, pyserial, mpremote, ard26 CLI
#              - Host/WSL: dialout permissions, usbipd, pwsh.exe audit
# Target OS:   Ubuntu 24.04 / 26.04 LTS (WSL2) + Windows 11 Host
# Lineage:     Arduino26 Environment Provisioning
# Updated:     2026-07-31
# ==============================================================================

set -euo pipefail

export PATH="${HOME}/.local/bin:${HOME}/.cargo/bin:${PATH}"

echo "=========================================================="
echo "    Arduino26 Workspace Environment Provisioning         "
echo "=========================================================="
echo "[*] Target Environment: WSL2 Ubuntu 26 Bash + Win11 Host"
echo "----------------------------------------------------------"

# 1. Update Apt Repositories & Install Baseline C/C++/AVR Packages
echo "[1/7] Updating APT repositories & installing AVR compiler packages..."
sudo apt-get update -qq || true
sudo apt-get install -y -qq build-essential gcc-avr avr-libc avrdude picocom python3 python3-pip python3-venv git curl wget || true

# 2. Install / Audit Rust Toolchain for AVR Embedded Development
echo "[2/7] Auditing Rust compiler & AVR nightly toolchain..."
if ! command -v rustup >/dev/null 2>&1; then
    echo "[*] Rustup not found. Installing Rust toolchain non-interactively..."
    TMP_RUST="$(mktemp /tmp/install_rust_XXXXXX.sh)"
    if curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs -o "${TMP_RUST}"; then
        sh "${TMP_RUST}" -y --default-toolchain stable || true
    fi
    rm -f "${TMP_RUST}"
    export PATH="${HOME}/.cargo/bin:${PATH}"
fi

if command -v rustup >/dev/null 2>&1; then
    echo "[*] Installing Rust nightly toolchain with rust-src component..."
    rustup toolchain install nightly --component rust-src || true
    rustup default nightly || true
fi

# 3. Install / Upgrade uv (Fast Python Package Installer)
echo "[3/7] Auditing 'uv' Python package manager..."
if ! command -v uv >/dev/null 2>&1; then
    echo "[*] Downloading uv installer to temporary file..."
    TMP_UV="$(mktemp /tmp/install_uv_XXXXXX.sh)"
    if curl -fsSL "https://astral.sh/uv/install.sh" -o "${TMP_UV}"; then
        sh "${TMP_UV}" || true
    fi
    rm -f "${TMP_UV}"
    export PATH="${HOME}/.local/bin:${PATH}"
fi

# 4. Provision Virtual Environment (.venv) & Python Packages
echo "[4/7] Installing Python dependencies & editable ard26 CLI..."
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

# 5. Install arduino-cli & Standard Libraries
echo "[5/7] Auditing 'arduino-cli' & sensor libraries..."
if ! command -v arduino-cli >/dev/null 2>&1; then
    mkdir -p "${HOME}/.local/bin"
    echo "[*] Downloading arduino-cli installer to temporary file..."
    TMP_CLI="$(mktemp /tmp/install_cli_XXXXXX.sh)"
    if curl -fsSL "https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh" -o "${TMP_CLI}"; then
        BINDIR="${HOME}/.local/bin" sh "${TMP_CLI}" || true
    fi
    rm -f "${TMP_CLI}"
    export PATH="${HOME}/.local/bin:${PATH}"
fi

if command -v arduino-cli >/dev/null 2>&1; then
    echo "[*] Updating Arduino CLI core index..."
    arduino-cli core update-index || true
    echo "[*] Installing Arduino AVR Core (arduino:avr)..."
    arduino-cli core install arduino:avr || true
    echo "[*] Installing standard sensor libraries (DHT sensor library, Adafruit Unified Sensor)..."
    arduino-cli lib install "DHT sensor library" "Adafruit Unified Sensor" || true
else
    echo "[i] Note: 'arduino-cli' binary not found. Skipping core update."
fi

# 6. Serial Port Permissions Audit
echo "[6/7] Auditing serial port permissions..."
if ! groups "$USER" | grep -q '\bdialout\b'; then
    echo "[!] Adding $USER to 'dialout' group..."
    sudo usermod -aG dialout "$USER" || true
    echo "[+] User $USER added to dialout group."
else
    echo "[+] User $USER is already in dialout group."
fi

# 7. Windows 11 Host Utility Checklist & usbipd Provisioning
echo "[7/7] Checking Windows 11 Host Utilities (pwsh.exe & usbipd)..."
if command -v pwsh.exe >/dev/null 2>&1; then
    echo "[+] PowerShell 7 (pwsh.exe) detected."
    if pwsh.exe -NoProfile -Command "Get-Command usbipd -ErrorAction SilentlyContinue" >/dev/null 2>&1; then
        echo "[+] usbipd detected on Windows host."
    else
        echo "[!] 'usbipd' not detected on Windows 11 host."
        echo "----------------------------------------------------------"
        echo "[i] To install usbipd for WSL2 USB passthrough, open PowerShell as Admin and run:"
        echo "        winget install dorssel.usbipd-win"
        echo "----------------------------------------------------------"
    fi
elif command -v powershell.exe >/dev/null 2>&1; then
    echo "[+] Windows PowerShell (powershell.exe) detected."
fi

echo "----------------------------------------------------------"
echo "[SUCCESS] Workspace Environment Provisioning Complete!"
echo "          To activate environment state in your terminal, run:"
echo "              source config_env"
echo "=========================================================="

# file dev-tools/provision_environment.sh ends
