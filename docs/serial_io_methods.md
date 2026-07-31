# Serial I/O Methods & Python Telemetry Workflows
<!-- file: docs/serial_io_methods.md -->

This guide documents serial input/output (I/O) communication methods between Linux / WSL2 and microcontrollers (such as Arduino Uno / CH340 clones), covering Python scripts, terminal CLI monitors, and coreutils one-liners.

---

## ⚡ 1. Concise Summary Matrix

| Method | Best For | Typical Command / Invocation | Features / Notes |
| :--- | :--- | :--- | :--- |
| **`tools/serial_monitor.py`** | Interactive terminal & logging | `python3 tools/serial_monitor.py -p /dev/ttyUSB0 -b 115200` | Built-in Python tool, multi-threaded, timestamped file logging. |
| **`arduino_scan`** | Hardware audit & PnP query | `python3 tools/arduino_serial_bridge.py` | Audits WSL serial ports & Windows 11 host PnP devices via PowerShell. |
| **`arduino-cli monitor`** | Integrated Arduino CLI | `arduino-cli monitor -p /dev/ttyUSB0 -c baudrate=115200` | Official CLI monitor, auto-resets board via DTR. |
| **`picocom`** | Fast headless CLI monitor | `picocom -b 115200 /dev/ttyUSB0` | Lightweight terminal emulator (`Ctrl+A Ctrl+X` to exit). |
| **`tio`** | Modern serial TUI monitor | `tio /dev/ttyUSB0 -b 115200` | Support for auto-reconnect and hex/ASCII rendering. |
| **Bash `stty` + `cat`** | Raw shell script piping | `stty -F /dev/ttyUSB0 115200 raw && cat /dev/ttyUSB0` | Zero-dependency coreutils shell solution. |

---

## 🐍 2. Python Serial I/O Methods (`pySerial`)

Python is the preferred scripting language for automated data ingestion, telemetry logging, and bi-directional hardware bridging.

### Option A: Minimal Telemetry Logger to CSV File
Save this script as a standalone telemetry collector:

```python
#!/usr/bin/env python3
import time
import serial

PORT = "/dev/ttyUSB0"
BAUD = 115200
LOG_FILE = "telemetry.csv"

print(f"[*] Opening {PORT} at {BAUD} baud...")
with serial.Serial(PORT, BAUD, timeout=2) as ser:
    time.sleep(1.5)  # Wait for DTR toggle reset to settle
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write("timestamp,raw_line\n")
        
        while True:
            try:
                if ser.in_waiting > 0:
                    line = ser.readline().decode("utf-8", errors="ignore").strip()
                    if line:
                        ts = time.strftime("%Y-%m-%d %H:%M:%S")
                        print(f"[{ts}] {line}")
                        f.write(f"{ts},{line}\n")
                        f.flush()
            except KeyboardInterrupt:
                print("\n[*] Stopping telemetry logger.")
                break
```

### Option B: Bi-Directional Interactive Terminal
For full duplex communication (sending commands to Arduino while reading incoming output concurrently):

```python
import sys
import time
import threading
import serial

def reader(ser):
    while ser.is_open:
        if ser.in_waiting > 0:
            msg = ser.readline().decode('utf-8', errors='ignore').strip()
            if msg:
                print(f"\n[Arduino >] {msg}\n[You >] ", end="", flush=True)
        time.sleep(0.01)

ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
time.sleep(1.5)

t = threading.Thread(target=reader, args=(ser,), daemon=True)
t.start()

print("[+] Connected. Type your command and press ENTER:")
while True:
    try:
        cmd = input("[You >] ")
        ser.write((cmd + "\n").encode('utf-8'))
    except (KeyboardInterrupt, EOFError):
        ser.close()
        break
```

---

## 💻 3. Command Line Terminal Utilities

### Method 1: `picocom`
Install and launch `picocom`:

```bash
sudo apt install picocom
picocom -b 115200 /dev/ttyUSB0 --echo
```
- **Exit Shortcut:** `Ctrl+A` followed by `Ctrl+X`.

### Method 2: `arduino-cli monitor`
Official monitor provided by Arduino CLI:

```bash
arduino-cli monitor -p /dev/ttyUSB0 -c baudrate=115200
```
- **Exit Shortcut:** `Ctrl+C`.

### Method 3: `tio` (Serial TTY I/O Utility)
```bash
sudo apt install tio
tio /dev/ttyUSB0 -b 115200
```
- **Exit Shortcut:** `Ctrl+T` followed by `q`.

---

## 🐚 4. Bash Coreutils One-Liners

For quick checks without installing extra packages:

```bash
# Configure baud rate and raw transmission mode
stty -F /dev/ttyUSB0 115200 raw -echo

# Read incoming stream
cat /dev/ttyUSB0

# Send command to Arduino
echo "STATUS" > /dev/ttyUSB0
```

---

## 🪟 5. Windows 11 Native Methods (`pwsh.exe` and `cmd.exe`)

When accessing serial devices directly on the Windows 11 host (e.g. `COM5`) without attaching them to WSL2:

### Method A: Native PowerShell (`pwsh.exe`)
Run the workspace helper from WSL or Windows terminal:

```bash
# Call PowerShell serial monitor helper directly from WSL bash
pwsh.exe -File tools/win11_serial_monitor.ps1 -Port COM5 -Baud 115200
```

*Raw Inline PowerShell Script:*
```powershell
$sp = New-Object System.IO.Ports.SerialPort "COM5", 115200, None, 8, One
$sp.Open()
while ($sp.IsOpen) {
    if ($sp.BytesToRead -gt 0) {
        $line = $sp.ReadLine()
        Write-Host "[COM5] $line"
    }
    Start-Sleep -Milliseconds 10
}
$sp.Close()
```

### Method B: Windows Command Prompt (`cmd.exe`)
```cmd
:: Configure baud rate and port parameters on COM5
mode COM5: BAUD=115200 PARITY=N DATA=8 STOP=1

:: Read serial stream directly
type COM5

:: Send command to Arduino
echo STATUS > COM5
```

### Method C: Windows Native Python Miniterm Callout
If Python is installed on the Windows host:

```bash
# List host ports via Windows Python
cmd.exe /c python -m serial.tools.list_ports

# Launch pySerial miniterm on COM5
cmd.exe /c python -m serial.tools.miniterm COM5 115200
```

---

## 🛠️ 6. Repository Built-In Utilities

- **Linux / WSL Python Monitor:** `python3 tools/serial_monitor.py -p /dev/ttyUSB0 -b 115200 -o agy/log/telemetry.log`
- **Win11 Native PowerShell Monitor:** `pwsh.exe -File tools/win11_serial_monitor.ps1 -Port COM5 -Baud 115200`
- **Hardware Bridge & Windows 11 PnP Scanner:** `python3 tools/arduino_serial_bridge.py`

<!-- file docs/serial_io_methods.md ends -->
