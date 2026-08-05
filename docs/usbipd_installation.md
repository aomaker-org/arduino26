# usbipd-win Installation & Configuration Guide
<!-- file: docs/usbipd_installation.md -->

This guide details how to install and configure **`usbipd-win`** to share host USB devices (such as Arduino microcontrollers) with WSL2.

---

## 1. Installation on Windows 11 Host

### Option A: Install via WinGet (Recommended)
Open a Windows PowerShell terminal (no Administrator privileges required for installation) and run:
```powershell
winget install --interactive --id dorssel.usbipd-win
```

### Option B: Manual Download
1. Navigate to the [dorssel/usbipd-win Releases](https://github.com/dorssel/usbipd-win/releases) page on GitHub.
2. Download the `.msi` installer.
3. Run the installer and proceed through the installation wizard.
4. **Restart your computer** or restart all terminal windows to refresh path variables.

---

## 2. Installation inside WSL2 (Ubuntu 24.04 / 26.04)

For WSL2 to map the shared USB ports, you need to install the Linux `usbip` tools and hardware database:

```bash
sudo apt update
sudo apt install -y linux-tools-virtual hwdata
sudo update-alternatives --install /usr/local/bin/usbip usbip $(ls /usr/lib/linux-tools/*/usbip | head -n 1) 20
```

---

## 3. Basic Usage & Auto-Attachment

With the `ard26` tool, attachment is fully automated! When you run:
```bash
ard26 run <sketch>
```
Or manually:
```bash
ard26 attach
```
The CLI will automatically search for connected host serial adapters (e.g. CH340, CP210x, FTDI) and map them to `/dev/ttyUSB0` in WSL2.

### Manual command-line execution (fallback):
If you need to bind a device manually from Windows command line or PowerShell:

1. **List USB devices:**
   ```powershell
   usbipd list
   ```
2. **Bind/Share the device (first-time only, requires Administrator privilege):**
   ```powershell
   usbipd bind --busid <BUSID>
   ```
3. **Attach device to WSL2:**
   ```powershell
   usbipd attach --wsl --busid <BUSID>
   ```

---

## 4. Troubleshooting

### Permission Denied inside WSL2
If `/dev/ttyUSB0` exists but reports permission errors during compilation/monitoring, run:
```bash
sudo chmod 666 /dev/ttyUSB0
```
Or add your user to the `dialout` group permanently:
```bash
sudo usermod -aG dialout $USER
```

### Firewall Authorization Error
If you see an error saying a firewall is blocking port 3240, run this command in **PowerShell as Administrator**:
```powershell
New-NetFirewallRule -DisplayName "usbipd-win" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 3240
```

<!-- file docs/usbipd_installation.md ends -->
