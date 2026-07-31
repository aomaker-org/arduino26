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
3. Verify in Windows Device Manager under **Ports (COM & LPT)** or Arduino IDE:
   - `USB-SERIAL CH340 (COM5)` (or `COM3`, `COM4`, etc.).

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
   1-4    1a86:7523  USB-SERIAL CH340 (COM5)                                       Not attached
   ```

3. **Bind Device on Windows Host (Administrator Step):**
   Before a device can be attached to WSL for the first time, it must be shared on the host:
   ```powershell
   usbipd bind --busid 2-3
   ```

4. **Attach USB Device to WSL2:**
   ```bash
   pwsh.exe -Command "usbipd attach --wsl --busid 2-3"
   ```

5. **Firewall TCP Port 3240 Authorization:**
   If `usbipd attach` reports `warning: A firewall appears to be blocking the connection; ensure TCP port 3240 is allowed`, run this command in **PowerShell (as Administrator)**:
   ```powershell
   New-NetFirewallRule -DisplayName "usbipd-win" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 3240
   ```

6. **Verify Device Binding Inside WSL2:**
   ```bash
   lsusb
   ```
   *Expected Output:*
   ```
   Bus 001 Device 002: ID 1a86:7523 QinHeng Electronics CH340 serial converter
   ```

7. **Locate Serial Node & Fix Linux Permissions (`nobody:nogroup`):**
   When `usbipd` mounts `/dev/ttyUSB0`, Linux assigns initial ownership `nobody:nogroup` (`crw-rw----`). Access by non-root users causes `OS error: cannot open port /dev/ttyUSB0: Permission denied`. Fix via:
   ```bash
   sudo chmod 666 /dev/ttyUSB0
   ```

8. **Detach Device (when finished):**
   ```bash
   pwsh.exe -Command "usbipd detach --busid 2-3"
   ```

---

## 3. Windows 11 Interop & UNC Path Best Practices

WSL2 allows execution of native Windows binaries directly from the bash terminal.

### UNC Path Resolution (`cmd.exe` vs `pwsh.exe`)
- **`cmd.exe` Limitation:** Executing `cmd.exe` from WSL paths (`/home/user/...`) fails with `UNC paths are not supported. Defaulting to Windows directory.` and resets working directory to `C:\Windows`.
- **PowerShell 7 (`pwsh.exe`) Resolution:** Always use `pwsh.exe -ExecutionPolicy Bypass` with paths converted via `wslpath -w` to execute Windows host commands cleanly across WSL network shares (`\\wsl.localhost\Ubuntu-26.04\...`).

### Querying Host PnP Serial Devices
Use `tools/arduino_serial_bridge.py` or run directly:

```bash
pwsh.exe -NoProfile -Command "Get-PnpDevice -PresentOnly | Where-Object { \
  \$_.Class -eq 'Ports' -or \
  \$_.FriendlyName -like '*CH340*' -or \
  \$_.FriendlyName -like '*Arduino*' \
} | Select-Object FriendlyName, InstanceId, Status"
```

---

## 4. Troubleshooting Serial Permissions & Busy States

- **Permission Denied on `/dev/ttyUSB0`:**
  ```bash
  sudo chmod 666 /dev/ttyUSB0
  sudo usermod -aG dialout $USER
  ```
- **Port Busy / Resource Temporarily Unavailable:**
  Ensure no serial monitors (e.g. Windows Serial Monitor, `picocom`, `minicom`, or `mpremote`)
  are actively keeping `/dev/ttyUSB0` or `COM5` open during an `arduino-cli upload` cycle.

<!-- file docs/wsl_win11_hardware.md ends -->
