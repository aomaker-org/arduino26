#!/usr/bin/env bash
# file: tools/upload_win.sh
# Purpose: Fully automatic Windows host upload helper using Uno reset controller on COM8
# Target OS: Ubuntu 24.04 / 26.04 LTS (WSL2) + Windows 11 Host

set -euo pipefail

SKETCH_PATH="${1:-sketches/leo_component_test}"
WIN_PATH="$(wslpath -w "${SKETCH_PATH}")"
ARD_CLI="C:\Program Files\Arduino CLI\arduino-cli.exe"

# Step 1: Pre-compile Leonardo sketch (takes time, but done before reset)
echo "[*] Step 1: Compiling Leonardo sketch on Windows host..."
./dev-tools/pwsh_wrapper.sh -Command "& '${ARD_CLI}' compile --fqbn arduino:avr:leonardo '${WIN_PATH}'"

# Step 2: Trigger hardware reset on Leonardo via Uno on COM8
echo "[*] Step 2: Sending reset command to Uno on COM8..."
./dev-tools/pwsh_wrapper.sh -Command "
\$p = New-Object System.IO.Ports.SerialPort COM8, 115200
\$p.Open()
\$p.Write('r')
Start-Sleep -Milliseconds 250
\$p.Close()
"

# Step 3: Wait exactly 1.5s for Leonardo bootloader to enumerate on COM6
echo "[*] Step 3: Waiting 1.5s for Leonardo bootloader port to appear..."
sleep 1.5

# Step 4: Perform upload immediately
echo "[*] Step 4: Uploading to Leonardo on COM6..."
exec ./dev-tools/pwsh_wrapper.sh -Command "& '${ARD_CLI}' upload -p COM6 --fqbn arduino:avr:leonardo '${WIN_PATH}'"

# file tools/upload_win.sh ends
