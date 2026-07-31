# WSL2 & Windows 11 Hardware Passthrough Guide (Verbose Reference)
<!-- file: docs/wsl_win11_hardware.md -->

This guide documents how WSL2 Ubuntu 26 interoperates with physical USB devices plugged
into a Windows 11 host system, with specific focus on CH340 USB-to-Serial bridge chips
commonly found on Uno clones.

---

## 1. Physical Hardware & CH340 Driver Overview

Arduino Uno clones frequently substitute the official ATmega16U2 USB interface chip
with the **WCH CH340 / CH340G / CH340C** USB-to-Serial converter.

### Windows 11 Driver Installation
1. Download official CH340 Windows drivers from WCH:
   - [WCH CH341SER.EXE Official Driver Download](http://www.wch-ic.com/downloads/CH341SER_EXE.html)
2. Run `CH341SER.EXE` on Windows 11 host and click **INSTALL**.
3. Verify in Windows Device Manager under **Ports (COM & LPT)**:
   - `USB-SERIAL CH340 (COM3)` or similar COM port entry.

---

## 2. Bridging USB Devices into WSL2 via `usbipd-win`

WSL2 runs inside a lightweight Hyper-V virtual machine and does not automatically mount
host USB devices. The open-source `usbipd-win` utility bridges USB ports over IP into WSL2.

### Step-by-Step USB Attachment

1. **Install `usbipd-win` on Windows 11:**
   Download and run the latest installer from [dorssel/usbipd-win Releases](https://github.com/dorssel/usbipd-win/releases).

2. **List Connected USB Devices:**
   Run from WSL terminal via `pwsh.exe`:
   ```bash
   pwsh.exe -Command "usbipd list"
   ```
   *Sample Output:*
   ```
   BUSID  VID:PID    DEVICE                                                        STATE
   1-4    1a86:7523  USB-SERIAL CH340 (COM3)                                       Not attached
   ```

3. **Attach USB Device to WSL2:**
   ```bash
   pwsh.exe -Command "usbipd attach --wsl --busid 1-4"
   ```

4. **Verify Device Binding Inside WSL2:**
   ```bash
   lsusb
   ```
   *Expected Output:*
   ```
   Bus 001 Device 002: ID 1a86:7523 QinHeng Electronics CH340 serial converter
   ```

5. **Locate Serial Node:**
   The device will automatically map to `/dev/ttyUSB0` (or `/dev/ttyACM0` for 16U2 chips):
   ```bash
   ls -l /dev/ttyUSB* /dev/ttyACM*
   ```

6. **Detach Device (when finished):**
   ```bash
   pwsh.exe -Command "usbipd detach --busid 1-4"
   ```

---

## 3. Windows 11 Callouts via `cmd.exe` and `pwsh.exe`

WSL2 allows execution of native Windows binaries directly from the bash terminal.
Arduino26 utilizes this for PnP querying and USB control.

### Querying Host PnP Serial Devices
Use `tools/arduino_serial_bridge.py` or run directly:

```bash
pwsh.exe -NoProfile -Command "Get-PnpDevice -PresentOnly | Where-Object { \
  \$_.Class -eq 'Ports' -or \
  \$_.FriendlyName -like '*CH340*' -or \
  \$_.FriendlyName -like '*Arduino*' \
} | Select-Object FriendlyName, InstanceId, Status"
```

### Windows GUI Launching
To launch the native Windows Arduino IDE 2.x from WSL bash:

```bash
cmd.exe /c start "" "C:\Program Files\Arduino IDE\Arduino IDE.exe"
```

---

## 4. Troubleshooting Serial Permissions & Busy States

- **Permission Denied on `/dev/ttyUSB0`:**
  ```bash
  sudo usermod -aG dialout $USER
  sudo chmod 666 /dev/ttyUSB0
  ```
- **Port Busy / Resource Temporarily Unavailable:**
  Ensure no serial monitors (e.g. Windows Serial Monitor, `picocom`, `minicom`, or `mpremote`)
  are actively keeping `/dev/ttyUSB0` or `COM3` open during an `arduino-cli upload` cycle.

<!-- file docs/wsl_win11_hardware.md ends -->
