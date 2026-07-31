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

4. **Self-Contained `uv` Virtual Environment Integration:**
   - Managed via [pyproject.toml](file:///home/fekerr/src/arduino26/pyproject.toml).
   - Automatically installed into `.venv` via `uv pip install -e .` during environment sourcing (`source config_env`).

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
# Compile default sketch (uno_blink)
ard26 compile

# Compile specific sketch by name or relative path
ard26 compile uno_clone_diag
ard26 compile sketches/ky_015_000
```

### 3. Compile & Upload to Microcontroller
```bash
# Upload to autodetected port using TOML default FQBN
ard26 upload uno_clone_diag

# Upload to explicit serial port
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
