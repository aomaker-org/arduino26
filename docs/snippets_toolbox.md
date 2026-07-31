# Snippets Toolbox & Tools Catalog (`docs/snippets_toolbox.md`)
<!-- file: docs/snippets_toolbox.md -->

This document serves as the master catalog and snippets toolbox for all executable utilities maintained under `./tools/` (Arduino hardware & serial work) and `./dev-tools/` (WSL / Win11 environment helper tools) in the `arduino26` workspace.

---

## 🏗️ Directory Separation Architecture

- **`./tools/`**: Dedicated exclusively to **Arduino work** (hardware serial scanning, sketch uploading, serial monitoring, board diagnostics).
- **`./dev-tools/`**: Dedicated to **WSL / Linux / Win11 helper tools** (context packing, clipboard exchange, PowerShell ExecutionPolicy wrappers, automated environment provisioning).
- **`./docs/`**: Master documentation suite covering both categories.

---

## 🧰 1. Arduino Work Tools (`./tools/`)

| Tool Script | Language | Purpose | Usage / Invocation | Provenance & Attribution |
| :--- | :--- | :--- | :--- | :--- |
| **`tools/arduino_serial_bridge.py`** | Python 3 | Audits WSL serial nodes and queries Win11 host PnP devices via PowerShell. | `python3 tools/arduino_serial_bridge.py` | [WCH CH340 Datasheet](http://www.wch-ic.com/downloads/CH340DS1_PDF.html) |
| **`tools/upload_sketch.sh`** | Bash | CLI helper to compile & flash sketches via `arduino-cli` or `avrdude`. | `./tools/upload_sketch.sh sketches/uno_blink /dev/ttyUSB0` | [Arduino CLI Docs](https://arduino.github.io/arduino-cli/latest/) |
| **`tools/serial_monitor.py`** | Python 3 | Interactive POSIX serial terminal & CSV/log telemetry file writer. | `python3 tools/serial_monitor.py -p /dev/ttyUSB0 -b 115200` | [pySerial Project](https://github.com/pyserial/pyserial) |
| **`tools/win11_serial_monitor.ps1`** | PowerShell 7 | Native Windows PowerShell serial monitor for host COM ports (e.g. `COM5`). | `pwsh.exe -File tools/win11_serial_monitor.ps1 -Port COM5 -Baud 9600` | [System.IO.Ports Docs](https://learn.microsoft.com/en-us/dotnet/api/system.io.ports.serialport) |

---

## 🛠️ 2. Environment & System Helper Tools (`./dev-tools/`)

| Tool Script | Language | Purpose | Usage / Invocation | Provenance & Attribution |
| :--- | :--- | :--- | :--- | :--- |
| **`dev-tools/ard26_cli/`** | Python 3 (`ard26`) | Unified CLI convenience tool (`compile`, `upload`, `monitor`, `scan`, `config`). | `ard26 compile uno_clone_diag` | Arduino26 Unified CLI Specification |
| **`dev-tools/files2clip`** | Python 3 | Packs workspace files into clipboard with SHA256 headers & 250 KB overflow protection. | `files2clip sketches/ AI.md` | fekerr & Gemini |
| **`dev-tools/clip2files`** | Python 3 | Extracts multi-file manifests from clipboard or stdin stream into workspace files. | `clip2files` | fekerr & Gemini |
| **`dev-tools/patch_io.py`** | Python 3 | Bridge wrapper for input (`clip2files`) and output (`files2clip`). | `pto sketches/uno_blink` | fekerr & Gemini |
| **`dev-tools/win11_monitor.sh`** | Bash | Wrapper to launch `win11_serial_monitor.ps1` with `-ExecutionPolicy Bypass`. | `./dev-tools/win11_monitor.sh COM5 9600` | [PowerShell ExecutionPolicies](https://go.microsoft.com/fwlink/?LinkID=135170) |
| **`dev-tools/pwsh_wrapper.sh`** | Bash | General-purpose wrapper executing `pwsh.exe` with `-NoProfile -ExecutionPolicy Bypass`. | `pwsh_bypass -Command "Get-PnpDevice"` | [PowerShell CLI Docs](https://learn.microsoft.com/en-us/powershell/) |
| **`dev-tools/provision_environment.sh`** | Bash | Automated bootstrap installing `arduino-cli`, `avrdude`, `pyserial`, `mpremote`, and `uv`. | `./dev-tools/provision_environment.sh` | Arduino26 Provisioning Specification |

---

## ⚡ 3. Environment Provisioning & Setup Reference

### Option A: Automated Provisioning (`wsl ubuntu 26 bash`)
To automatically set up the expected/standard set of utilities inside WSL:

```bash
# Run automated bootstrap
./dev-tools/provision_environment.sh

# Source environment
source config_env
```

### Option B: Native Windows 11 Environment Setup (`cmd.exe` / `pwsh.exe`)
For native Windows 11 command line environments:

1. **Install PowerShell 7:**
   ```powershell
   winget install Microsoft.PowerShell
   ```
2. **Install `usbipd-win` (USB Passthrough Service):**
   ```powershell
   winget install dorssel.usbipd-win
   ```
3. **Install Arduino CLI (Windows Host):**
   ```powershell
   winget install Arduino.cli
   arduino-cli core update-index
   arduino-cli core install arduino:avr
   ```
4. **Install CH340 Serial Driver:**
   Download and install `CH341SER.EXE` from [WCH Official Driver Download](http://www.wch-ic.com/downloads/CH341SER_EXE.html).

<!-- file docs/snippets_toolbox.md ends -->
