#!/usr/bin/env bash
# file: tools/upload_win.sh
# Purpose: Single-line command script to compile and upload sketches on Windows host
# Target OS: Ubuntu 24.04 / 26.04 LTS (WSL2) + Windows 11 Host

set -euo pipefail

SKETCH_PATH="${1:-sketches/leo_component_test}"
WIN_PATH="$(wslpath -w "${SKETCH_PATH}")"

echo "[*] Compiling and uploading ${SKETCH_PATH} on Windows host port COM6..."
exec ./dev-tools/pwsh_wrapper.sh -Command "& 'C:\Program Files\Arduino CLI\arduino-cli.exe' compile --upload -p COM6 --fqbn arduino:avr:leonardo '${WIN_PATH}'"

# file tools/upload_win.sh ends
