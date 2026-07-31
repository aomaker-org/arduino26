# Getting Started with Arduino26 (Concise Summary)
<!-- file: docs/GETTING_STARTED.md -->

> **Target Audience:** Experienced Embedded Systems Engineers, Computer Engineers,
> and Firmware Developers. High-signal, low-fluff reference.

---

## 1. System Architecture Overview

```
+-------------------------------------------------------------------------+
|                        Windows 11 Workstation Host                      |
|  - Physical USB Ports (CH340 / FT232 / CP210x / ATmega16U2)             |
|  - CH340 / Serial Drivers (COM1..COMN)                                  |
|  - usbipd-win Service (USB IP Daemon)                                   |
+-------------------------------------------------------------------------+
                                    | (usbipd attach --wsl)
                                    v
+-------------------------------------------------------------------------+
|                        WSL2 Ubuntu 26.04 Subsystem                      |
|  - Serial Nodes: /dev/ttyUSB0, /dev/ttyACM0                             |
|  - Toolchains: arduino-cli, avr-gcc, avrdude, cargo/rustc, micropython  |
|  - AGY Multi-Agent Context Exchange (files2clip / clip2files)           |
+-------------------------------------------------------------------------+
```

---

## 2. Environment Initialization

```bash
# Clone & enter workspace
cd ~/src/arduino26

# Source the idempotent configuration script
source config_env

# Optional: tag your active terminal prompt session
source config_env "uno_testing"
```

---

## 3. Serial & USB Hardware Quick Reference

### Checking Hardware via Callouts to Win11
```bash
# List physical USB devices connected to Windows host
pwsh.exe -Command "usbipd list"

# Attach CH340 / Uno device (e.g. BUSID 2-4) to WSL2
pwsh.exe -Command "usbipd attach --wsl --busid 2-4"

# Audit serial ports inside WSL2
arduino_scan
```

### Serial Port Permissions
If `/dev/ttyUSB0` or `/dev/ttyACM0` gives permission denied:
```bash
sudo usermod -aG dialout $USER
# Log out and back in, or run: newgrp dialout
```

---

## 4. Multi-Environment Build Cheat Sheet

| Language / Framework | Source Location | Build Command | Flash Command |
| :--- | :--- | :--- | :--- |
| **Arduino C++** | `sketches/uno_blink/` | `arduino-cli compile --fqbn arduino:avr:uno sketches/uno_blink` | `arduino-cli upload -p /dev/ttyUSB0 --fqbn arduino:avr:uno sketches/uno_blink` |
| **AVR Assembly** | `asm/uno_blink/` | `cd asm/uno_blink && make` | `make PORT=/dev/ttyUSB0 flash` |
| **Rust (`no_std`)** | `rust/uno_blink/` | `cd rust/uno_blink && cargo build --release` | `ravedude / cargo-avr` or `avrdude` |
| **MicroPython** | `micropython/` | *N/A (Interpreted)* | `mpremote connect /dev/ttyUSB0 run micropython/main.py` |

---

## 5. Multi-Agent AI Context Exchange

- **Pack workspace for Gemini / Web LLM:**
  ```bash
  files2clip sketches/uno_blink AI.md
  ```
- **Ingest LLM multi-file response from clipboard:**
  ```bash
  clip2files
  ```
- **Inspect turn logs:**
  ```bash
  ls -l agy/log/
  ```

<!-- file docs/GETTING_STARTED.md ends -->
