# Getting Started with Arduino26 (Concise Summary)
<!-- file: docs/getting_started.md -->

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

# Provision workspace dependencies (arduino-cli, gcc-avr, Rust nightly, uv, libraries)
./dev-tools/provision_environment.sh

# Source the idempotent configuration script
source config_env

# Optional: tag your active terminal prompt session
source config_env "uno_testing"
```

### 2.1 Workspace Provisioning Script (`./dev-tools/provision_environment.sh`)

The workspace includes a single-line automated provisioning script that bootstraps all required compilers, runtimes, and dependencies:

```bash
./dev-tools/provision_environment.sh
```

#### What It Provisions Automatically:
1. **AVR C/C++ Compiler Toolchain:** `gcc-avr`, `avr-libc`, `avrdude`, `picocom`, `build-essential`.
2. **Rust Embedded AVR Setup:** `rustup`, Rust `nightly` compiler toolchain, `rust-src` component, and built-in `avr-none` target config.
3. **Python & CLI Tools:** `uv` package manager, `.venv` virtual environment, `pyserial`, `mpremote`, and editable `ard26` CLI (`uv pip install -e .`).
4. **Arduino CLI & Libraries:** `arduino-cli`, `arduino:avr` core, `DHT sensor library`, and `Adafruit Unified Sensor`.
5. **Hardware & Security:** Adds `$USER` to `dialout` group for serial port access, and audits Windows 11 host `pwsh.exe` and `usbipd` status.

---

## 3. Serial & USB Hardware Quick Reference

### USB Passthrough Setup (`usbipd-win`)
1. Install `usbipd-win` on Windows 11 host (PowerShell as Admin):
   ```powershell
   winget install dorssel.usbipd-win
   ```
2. List physical USB devices connected to Windows host:
   ```bash
   pwsh.exe -Command "usbipd list"
   ```
3. Share (bind) device on host (first-time Administrator step):
   ```powershell
   usbipd bind --busid <BUSID>
   ```
4. Attach CH340 / Uno device (e.g. BUSID 2-3) to WSL2:
   ```bash
   pwsh.exe -Command "usbipd attach --wsl --busid 2-3"
   ```
5. Audit serial ports inside WSL2:
   ```bash
   ard26 scan
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

<!-- file docs/getting_started.md ends -->
