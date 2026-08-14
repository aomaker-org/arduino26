#!/usr/bin/env bash
# file: tools/upload_win.sh
# Purpose: Fully automatic Windows host upload helper (pre-compile, auto-touch, auto-upload)
# Target OS: Ubuntu 24.04 / 26.04 LTS (WSL2) + Windows 11 Host

set -euo pipefail

SKETCH_PATH="${1:-sketches/leo_component_test}"
WIN_PATH="$(wslpath -w "${SKETCH_PATH}")"
ARD_CLI="C:\Program Files\Arduino CLI\arduino-cli.exe"

# Step 1: Pre-compile sketch (takes time, but done before reset)
echo "[*] Step 1: Compiling sketch on Windows host..."
./dev-tools/pwsh_wrapper.sh -Command "& '${ARD_CLI}' compile --fqbn arduino:avr:leonardo '${WIN_PATH}'"

# Step 2: Trigger bootloader reset on host
echo "[*] Step 2: Triggering 1200bps touch reset on COM6..."
./dev-tools/pwsh_wrapper.sh -Command "\$p = New-Object System.IO.Ports.SerialPort COM6, 1200; \$p.Open(); \$p.Close()"

# Step 3: Wait exactly 1.5s for Windows to re-enumerate COM6 in bootloader mode
echo "[*] Step 3: Waiting 1.5s for bootloader port to reappear..."
sleep 1.5

# Step 4: Perform upload immediately
echo "[*] Step 4: Uploading to COM6..."
exec ./dev-tools/pwsh_wrapper.sh -Command "& '${ARD_CLI}' upload -p COM6 --fqbn arduino:avr:leonardo '${WIN_PATH}'"

# file tools/upload_win.sh ends
