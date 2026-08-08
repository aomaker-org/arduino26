# `ard26` Unified CLI & Python Convenience Wrappers (`docs/ard26_cli_guide.md`)
<!-- file: docs/ard26_cli_guide.md -->

This guide documents the design decisions, configuration schema, and operational commands for **`ard26`** — the unified Python convenience CLI tool for the `arduino26` embedded development environment.

---

## 💡 Key Design Decisions & Architecture

1. **TOML Configuration Schema (`arduino_config.toml`):**
   - Uses a visible, non-hidden configuration file located in the workspace root.
   - Parses configuration values (FQBN, serial ports, baud rates, directory paths) using Python 3.14's native `tomllib` standard library module.

2. **Automated Serial Port Auto-Detection:**
   - Automatically scans POSIX character device nodes under WSL (`/dev/ttyUSB*`, `/dev/ttyACM*`).
   - Audits Windows 11 host PnP devices via `pwsh.exe Get-PnpDevice` when targeting Windows `COM` ports.

3. **Cross-Platform Dual Context Execution:**
   - On **WSL Ubuntu 26 Bash**, delegates compilation and uploading to `arduino-cli`.
   - On **Windows 11 Native Context**, routes commands via `cmd.exe` or `pwsh.exe -ExecutionPolicy Bypass` targeting `COM` ports (e.g. `COM5`).

5. **Last Compiled Sketch Memory & Interactive Prompt:**
   - Successfully compiling a sketch (`ard26 compile <sketch>`) locks it in `arduino_config.toml` under `[state]`.
   - Running `ard26 upload` without arguments prompts: `Upload the last compiled sketch [sketch_name]? [Y/n]`.

6. **Automatic Upload Method Persistence & Failover:**
   - When an upload method succeeds (WSL `/dev/ttyUSB0` or Windows `COM5`), `ard26` records the working method (`wsl` or `win_failover`) and `preferred_port` in `arduino_config.toml`.
   - Subsequent `ard26 upload` commands reuse the successful method automatically without prompting.

7. **Operation History & Telemetry Logging:**
   - Every `ard26` invocation records command parameters, timestamps, target sketch, serial port, and exit status into `agy/log/ard26_history.log` and `agy/log/ard26_telemetry.csv`.

---

## ⚙️ Configuration File Schema (`arduino_config.toml`)

```toml
[board]
fqbn = "arduino:avr:uno"
mcu = "atmega328p"

[port]
wsl = "/dev/ttyUSB0"
win = "COM5"
autodetect = true

[baud]
default = 115200
dht11 = 9600
diag = 115200

[paths]
sketches_dir = "sketches"
tools_dir = "tools"
dev_tools_dir = "dev-tools"

[tools]
make_uses_ard26 = false

[state]
last_compiled_sketch = "uno_clone_diag"
active_method = "win_failover"
preferred_port = "COM5"
```

---

## 🏗️ Makefile Integration & Precedence Override Hierarchy

When invoking workflow pipelines using the `Makefile` (e.g. `make run`), the tool utilized to execute commands is determined by a hierarchy of sources:

1. **Command-line argument override:** Passing `ARD26_MAKE_USES_ARD26=1` (or `0`) directly to the make invocation (e.g. `make run ARD26_MAKE_USES_ARD26=1`).
2. **Environment variable override:** Having `export ARD26_MAKE_USES_ARD26=1` set in the active shell environment.
3. **Local configuration file:** Reading the `make_uses_ard26` boolean under `[tools]` in [`arduino_config.toml`](file:///home/fekerr/src/arduino26/arduino_config.toml).
4. **Default fallback:** Executes command directly via python module (`python3 -m ard26_cli.cli`) to ensure out-of-the-box compatibility without sourcing requirements.

---

## 🛠️ Host Environment Provisioning (Windows 11 & WSL2)

### 1. Windows Host `arduino-cli` Setup (Direct Host Flashing)
To enable direct Windows host flashing on `COM` ports when USB devices are attached to Windows 11 host:
```powershell
# Run in PowerShell on Windows 11 Host:
winget install Arduino.cli
arduino-cli core update-index
arduino-cli core install arduino:avr
```

### 2. WSL2 USB Device Binding via `usbipd-win`
To bind physical CH340 / FT232 devices into WSL2:
```powershell
# Run in PowerShell on Windows 11 Host:
pwsh.exe -Command "usbipd list"
pwsh.exe -Command "usbipd attach --wsl --busid <BUSID>"
```

---

## 🚀 `ard26` Command Reference

### 1. View Help & Configuration
```bash
# Display CLI subcommands and help text
ard26 -h

# View active workspace settings loaded from TOML
ard26 config
```

### 2. Compile Sketches
```bash
# Compile last compiled sketch (or default uno_blink)
ard26 compile

# Compile specific sketch by name or relative path
ard26 compile uno_clone_diag
ard26 compile sketches/ky_015_000
```

### 3. Compile & Upload to Microcontroller
```bash
# Upload to last compiled sketch (prompts [Y/n])
ard26 upload

# Upload specific sketch to explicit serial port
ard26 upload uno_clone_diag -p /dev/ttyUSB0
ard26 upload uno_clone_diag -p COM5
```

### 4. Interactive UTF-8 Serial Monitor
```bash
# Launch serial monitor at default 115200 baud
ard26 monitor

# Launch serial monitor for KY-015 / DHT11 at 9600 baud
ard26 monitor -b 9600
```

### 5. Scan Connected Hardware Devices
```bash
# Audit WSL serial nodes and query Windows 11 host PnP manager
ard26 scan
```

<!-- file docs/ard26_cli_guide.md ends -->
