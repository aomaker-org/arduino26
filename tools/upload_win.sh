#!/usr/bin/env bash
# file: tools/upload_win.sh
# Purpose: Compile first, then prompt for reset, and upload immediately on Windows host
# Target OS: Ubuntu 24.04 / 26.04 LTS (WSL2) + Windows 11 Host

set -euo pipefail

SKETCH_PATH="${1:-sketches/leo_component_test}"
WIN_PATH="$(wslpath -w "${SKETCH_PATH}")"
ARD_CLI="C:\Program Files\Arduino CLI\arduino-cli.exe"

# 1. Compile first (doesn't require bootloader window)
echo "[*] Step 1: Compiling sketch on Windows host..."
./dev-tools/pwsh_wrapper.sh -Command "& '${ARD_CLI}' compile --fqbn arduino:avr:leonardo '${WIN_PATH}'"

# 2. Wait for user to trigger reset
echo "=========================================================="
echo "      Sketch compilation complete!"
echo "      1. Press the physical RESET button on the Leonardo."
echo "      2. Wait for the host Windows reconnect beep."
echo "      3. Press ENTER immediately to start the upload..."
echo "=========================================================="
read -r

# 3. Upload immediately (takes <1s, fits inside bootloader window)
echo "[*] Step 2: Uploading binary to COM6..."
exec ./dev-tools/pwsh_wrapper.sh -Command "& '${ARD_CLI}' upload -p COM6 --fqbn arduino:avr:leonardo '${WIN_PATH}'"

# file tools/upload_win.sh ends
