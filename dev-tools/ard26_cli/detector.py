# file: dev-tools/ard26_cli/detector.py
# Purpose: Serial port auto-detection & PnP audit module for ard26 CLI
# Target OS: Ubuntu 24.04 / 26.04 LTS (WSL2) + Windows 11 Host

import glob
import os
import subprocess
import sys
import time
from pathlib import Path

try:
    import serial.tools.list_ports
except ImportError:
    serial = None


class DeviceDetector:
    """Detects active serial ports on WSL Linux runtime and Windows 11 host."""

    @staticmethod
    def find_wsl_port() -> str | None:
        """Scans for active serial devices under /dev/ttyUSB* or /dev/ttyACM*."""
        candidates = sorted(glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*"))
        if candidates:
            return candidates[0]
        
        # Fallback to pySerial listing
        if serial:
            ports = list(serial.tools.list_ports.comports())
            for p in ports:
                if "USB" in p.device or "ACM" in p.device:
                    return p.device
        return None

    @staticmethod
    def audit_win11_host() -> list[dict[str, str]]:
        """Queries Windows 11 host PnP devices via powershell.exe."""
        devices = []
        try:
            cmd = [
                "powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
                "Get-PnpDevice -PresentOnly | Where-Object { $_.Class -eq 'Ports' } | Select-Object FriendlyName, Status"
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5, stdin=subprocess.DEVNULL, check=False)
            if res.returncode == 0:
                for line in res.stdout.splitlines():
                    line = line.strip()
                    if line and ("COM" in line or "CH340" in line or "Arduino" in line):
                        devices.append({"friendly_name": line})
        except Exception:  # noqa: BLE001, S110
            pass
        return devices

    @staticmethod
    def list_usbipd_devices() -> list[dict[str, str]]:
        """Queries usbipd-win devices from host using powershell.exe."""
        devices = []
        try:
            cmd = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", "usbipd list"]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5, stdin=subprocess.DEVNULL, check=False)
            if res.returncode == 0:
                in_connected = False
                for line in res.stdout.splitlines():
                    line_strip = line.strip()
                    if not line_strip:
                        continue
                    if "Connected:" in line or "BUSID" in line:
                        in_connected = True
                        continue
                    if "Persisted:" in line:
                        in_connected = False
                        continue
                    if in_connected:
                        import re
                        m = re.match(r'^(\d+-\d+)\s+([0-9a-fA-F]{4}:[0-9a-fA-F]{4})\s+(.+?)\s{2,}(.+)$', line_strip)
                        if m:
                            busid, vid_pid, device_desc, state = m.groups()
                            devices.append({
                                "busid": busid,
                                "vid_pid": vid_pid,
                                "description": device_desc.strip(),
                                "state": state.strip()
                            })
                        else:
                            tokens = line_strip.split(None, 3)
                            if len(tokens) >= 3:
                                busid = tokens[0]
                                vid_pid = tokens[1]
                                rest = tokens[2]
                                state = "Not shared"
                                desc = rest
                                for s in ["Not shared", "Shared", "Attached", "Not attached", "Not shared (forced)"]:
                                    if rest.endswith(s):
                                        state = s
                                        desc = rest[:-len(s)].strip()
                                        break
                                devices.append({
                                    "busid": busid,
                                    "vid_pid": vid_pid,
                                    "description": desc,
                                    "state": state
                                })
        except Exception:  # noqa: BLE001, S110
            pass
        return devices

    @staticmethod
    def attach_usbipd_device(busid: str) -> bool:
        """Attaches a device on the host to WSL2 using usbipd-win."""
        try:
            cmd = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", f"usbipd attach --wsl --busid {busid}"]
            res = subprocess.run(cmd, capture_output=True, text=True, stdin=subprocess.DEVNULL, check=False)
            if res.returncode == 0:
                return True
            else:
                if "bind" in res.stderr.lower() or "share" in res.stderr.lower() or "not shared" in res.stderr.lower():
                    print(f"[*] Device {busid} may not be shared. Attempting to bind/share it first (may prompt for Administrator permission on host)...")
                    bind_cmd = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", f"Start-Process powershell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -Command usbipd bind --busid {busid}' -Verb RunAs"]
                    subprocess.run(bind_cmd, stdin=subprocess.DEVNULL, check=False)
                    time.sleep(3)
                    res2 = subprocess.run(cmd, capture_output=True, text=True, stdin=subprocess.DEVNULL, check=False)
                    if res2.returncode == 0:
                        return True
                    else:
                        print(f"[X] Failed to attach: {res2.stderr.strip()}", file=sys.stderr)
                else:
                    print(f"[X] Failed to attach: {res.stderr.strip()}", file=sys.stderr)
        except Exception as e:  # noqa: BLE001
            print(f"[X] Error running usbipd: {e}", file=sys.stderr)
        return False

    @classmethod
    def auto_attach_serial(cls) -> str | None:
        """Scans host devices via usbipd, identifies serial adapters, and attaches them."""
        devices = cls.list_usbipd_devices()
        serial_candidates = []
        for dev in devices:
            desc = dev["description"].lower()
            if any(k in desc for k in ["ch340", "usb-serial", "cp210", "ft232", "prolific", "arduino", "serial"]):
                serial_candidates.append(dev)
        
        if not serial_candidates:
            return None
        
        target = serial_candidates[0]
        print("[*] Auto-detecting host USB serial device via usbipd...")
        print(f"[*] Found candidate host device at Bus ID {target['busid']}: {target['description']}")
        print("[*] Attempting auto-attachment to WSL2...")
        
        if cls.attach_usbipd_device(target["busid"]):
            print("[SUCCESS] Device successfully attached via usbipd.")
            for _ in range(15):
                time.sleep(0.2)
                port = cls.find_wsl_port()
                if port:
                    try:
                        if os.path.exists(port):
                            os.chmod(port, 0o666)
                    except Exception:  # noqa: BLE001, S110
                        pass
                    return port
        return None

    @staticmethod
    def detect_sketch_baud(sketch_dir: Path) -> int | None:
        """Scans sketch .ino and Rust .rs files for Serial.begin(baud) or default_serial!(..., baud)."""
        import re
        if not sketch_dir:
            return None
        
        p = Path(sketch_dir)
        if p.is_file():
            p = p.parent
        elif not p.is_dir():
            return None

        # Check Arduino .ino files
        for ino_file in p.glob("*.ino"):
            try:
                content = ino_file.read_text(encoding="utf-8", errors="ignore")
                match = re.search(r'Serial\.begin\s*\(\s*(\d+)\s*\)', content)
                if match:
                    return int(match.group(1))
            except Exception:  # noqa: BLE001, S110
                pass

        # Check Rust .rs files under src/
        for rs_file in p.glob("src/**/*.rs"):
            try:
                content = rs_file.read_text(encoding="utf-8", errors="ignore")
                match = re.search(r'default_serial!\s*\([^,]+,[^,]+,\s*(\d+)\s*\)', content)
                if match:
                    return int(match.group(1))
            except Exception:  # noqa: BLE001, S110
                pass

        return None

    @classmethod
    def resolve_port(cls, user_port: str | None = None, default_port: str = "/dev/ttyUSB0") -> str:
        """Resolves target port: explicit user port -> autodetected port -> autodetect host usbipd -> config default."""
        if user_port:
            return user_port
        
        detected = cls.find_wsl_port()
        if detected:
            return detected
        
        # Try auto-attaching via usbipd
        attached = cls.auto_attach_serial()
        if attached:
            return attached
            
        return default_port

# file dev-tools/ard26_cli/detector.py ends
