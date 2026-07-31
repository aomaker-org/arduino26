# Snippets Toolbox & Tools Directory Index (`docs/snippets_toolbox.md`)
<!-- file: docs/snippets_toolbox.md -->

This document serves as the master catalog and snippets toolbox for all executable helper scripts and automation utilities maintained under `tools/*` in the `arduino26` workspace.

---

## 📋 Master Tools Index

| Script File | Language / Runtime | Primary Purpose | Invocation Example | Provenance / Web Attribution |
| :--- | :--- | :--- | :--- | :--- |
| **`tools/files2clip`** | Python 3 | Packs workspace files into clipboard with SHA256 headers & 250 KB overflow protection. | `files2clip sketches/ AI.md` | fekerr & Gemini |
| **`tools/clip2files`** | Python 3 | Extracts multi-file manifests from clipboard or stdin stream into workspace files. | `clip2files` | fekerr & Gemini |
| **`tools/patch_io.py`** | Python 3 | Bridge wrapper for input (`clip2files`) and output (`files2clip`). | `pto sketches/uno_blink` | fekerr & Gemini |
| **`tools/arduino_serial_bridge.py`** | Python 3 | Hardware scanner auditing WSL serial nodes and querying Win11 host PnP devices. | `python3 tools/arduino_serial_bridge.py` | [WCH CH340 Datasheet](http://www.wch-ic.com/downloads/CH340DS1_PDF.html) |
| **`tools/upload_sketch.sh`** | Bash | CLI helper to compile and flash sketches via `arduino-cli` or `avrdude`. | `./tools/upload_sketch.sh sketches/uno_blink /dev/ttyUSB0` | [Arduino CLI Docs](https://arduino.github.io/arduino-cli/latest/) |
| **`tools/serial_monitor.py`** | Python 3 | Interactive bi-directional serial terminal & telemetry file logger. | `python3 tools/serial_monitor.py -p /dev/ttyUSB0 -b 115200` | [pySerial Project](https://github.com/pyserial/pyserial) |
| **`tools/win11_serial_monitor.ps1`** | PowerShell 7 | Native Windows PowerShell serial monitor for host COM ports (e.g. `COM5`). | `pwsh.exe -File tools/win11_serial_monitor.ps1 -Port COM5 -Baud 9600` | [System.IO.Ports Docs](https://learn.microsoft.com/en-us/dotnet/api/system.io.ports.serialport) |
| **`tools/win11_monitor.sh`** | Bash | Wrapper to launch `win11_serial_monitor.ps1` with `-ExecutionPolicy Bypass`. | `./tools/win11_monitor.sh COM5 9600` | [PowerShell ExecutionPolicies](https://go.microsoft.com/fwlink/?LinkID=135170) |
| **`tools/pwsh_wrapper.sh`** | Bash | General-purpose wrapper executing `pwsh.exe` with `-NoProfile -ExecutionPolicy Bypass`. | `pwsh_bypass -Command "Get-PnpDevice"` | [PowerShell CLI Docs](https://learn.microsoft.com/en-us/powershell/) |

---

## 🛠️ Detailed Script Descriptions & Code Snippets

### 1. `tools/files2clip` (Context Packing Engine)
- **File:** [tools/files2clip](file:///home/fekerr/src/arduino26/tools/files2clip)
- **Description:** Scans workspace targets, filters binary files, computes SHA256 checksums, and formats context streams for LLM context exchange.
- **Safety Gate:** Payloads exceeding 250 KB are automatically written to `agy/scratch/bundle_YYYYMMDD_HHMMSS.txt` to prevent browser freezes when pasting into Web UIs.

### 2. `tools/clip2files` (Manifest Extraction Engine)
- **File:** [tools/clip2files](file:///home/fekerr/src/arduino26/tools/clip2files)
- **Description:** Parses structured `--- BEGIN FILE: path ---` manifest blocks from clipboard or stdin stream, verifies byte lengths and SHA256 signatures, and commits files to disk.

### 3. `tools/arduino_serial_bridge.py` (Hardware & PnP Bridge)
- **File:** [tools/arduino_serial_bridge.py](file:///home/fekerr/src/arduino26/tools/arduino_serial_bridge.py)
- **Description:** Audits WSL `/dev/ttyUSB*` nodes and queries Windows 11 PnP manager via PowerShell (`Get-PnpDevice`) to detect attached CH340 / FT232 / CP210x / Arduino USB interfaces. Outputs telemetry logs to `agy/log/arduino_serial_telemetry.csv`.

### 4. `tools/upload_sketch.sh` (CLI Sketch Flasher)
- **File:** [tools/upload_sketch.sh](file:///home/fekerr/src/arduino26/tools/upload_sketch.sh)
- **Description:** Verifies serial port presence, compiles target sketch via `arduino-cli`, and uploads binary to microcontroller. Falls back to `avrdude` if `arduino-cli` is absent.

### 5. `tools/serial_monitor.py` (Multi-Threaded Serial Monitor)
- **File:** [tools/serial_monitor.py](file:///home/fekerr/src/arduino26/tools/serial_monitor.py)
- **Description:** Multi-threaded POSIX serial terminal allowing concurrent background reading and interactive command sending over serial ports.

### 6. `tools/win11_serial_monitor.ps1` (Native Windows Serial Monitor)
- **File:** [tools/win11_serial_monitor.ps1](file:///home/fekerr/src/arduino26/tools/win11_serial_monitor.ps1)
- **Description:** Native PowerShell script leveraging `System.IO.Ports.SerialPort` to monitor host COM ports (e.g. `COM5`) directly on Windows 11.

### 7. `tools/win11_monitor.sh` (ExecutionPolicy Bypass Wrapper)
- **File:** [tools/win11_monitor.sh](file:///home/fekerr/src/arduino26/tools/win11_monitor.sh)
- **Description:** Bash wrapper converting WSL POSIX paths to Windows UNC paths and invoking `win11_serial_monitor.ps1` through `pwsh.exe -ExecutionPolicy Bypass`.

### 8. `tools/pwsh_wrapper.sh` (PowerShell Bypass Wrapper)
- **File:** [tools/pwsh_wrapper.sh](file:///home/fekerr/src/arduino26/tools/pwsh_wrapper.sh)
- **Description:** Generic command wrapper to route any PowerShell command or `.ps1` script with ExecutionPolicy Bypass enabled.

<!-- file docs/snippets_toolbox.md ends -->
