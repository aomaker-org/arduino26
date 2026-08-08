#!/usr/bin/env bash
# file: tools/upload_sketch.sh
# Purpose:     CLI helper to compile and upload Arduino sketches via arduino-cli or avrdude
# Target OS:   Ubuntu 24.04 / 26.04 LTS (WSL2 / Linux Native)
# Lineage:     Arduino26 Infrastructure
# Updated:     2026-07-31

set -euo pipefail

SKETCH_PATH="${1:-sketches/uno_blink}"
PORT="${2:-/dev/ttyUSB0}"
FQBN="${3:-arduino:avr:uno}"

echo "=========================================================="
echo "    Arduino26 CLI Compile & Upload Helper                 "
echo "=========================================================="
echo "[*] Target Sketch : ${SKETCH_PATH}"
echo "[*] Serial Port   : ${PORT}"
echo "[*] Board FQBN    : ${FQBN}"
echo "----------------------------------------------------------"

# 1. Verify Serial Port Presence
if [ ! -e "${PORT}" ]; then
    echo "[!] WSL port ${PORT} upload failed (device not bound to WSL or port busy)." >&2
    echo "----------------------------------------------------------" >&2
    echo "[i] Alternatively, attach your physical USB device (CH340) into WSL2:" >&2
    echo "    pwsh.exe -Command \"usbipd list; echo 'Run: usbipd attach --wsl --busid <BUSID>'\"" >&2
    echo "----------------------------------------------------------" >&2
    exit 1
fi

# 2. Check if arduino-cli is present
if command -v arduino-cli >/dev/null 2>&1; then
    echo "[*] Compiling sketch: ${SKETCH_PATH}..."
    arduino-cli compile --fqbn "${FQBN}" "${SKETCH_PATH}"
    
    echo "[*] Uploading sketch to ${PORT}..."
    arduino-cli upload -p "${PORT}" --fqbn "${FQBN}" "${SKETCH_PATH}"
    echo "[SUCCESS] Compile and upload complete."
    exit 0
fi

# 3. Fallback to avrdude if precompiled hex exists
HEX_FILE=""
if [ -d "${SKETCH_PATH}/build" ]; then
    HEX_FILE="$(find "${SKETCH_PATH}/build" -name "*.hex" | head -n 1)"
fi

if [ -n "${HEX_FILE}" ] && command -v avrdude >/dev/null 2>&1; then
    echo "[*] arduino-cli absent. Falling back to avrdude with pre-compiled HEX..."
    avrdude -C /etc/avrdude.conf -v -p atmega328p -c arduino -P "${PORT}" -b 115200 -D -U flash:w:"${HEX_FILE}":i
    echo "[SUCCESS] HEX flashed via avrdude!"
    exit 0
fi

# 4. Instructions if toolchain is missing
echo "[X] Error: 'arduino-cli' is not installed." >&2
echo "    Install dependencies via the workspace provisioning bootstrap:" >&2
echo "        ./dev-tools/provision_environment.sh" >&2
exit 1

# file tools/upload_sketch.sh ends
