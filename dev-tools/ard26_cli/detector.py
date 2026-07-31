# file: dev-tools/ard26_cli/detector.py
# Purpose: Serial port auto-detection & PnP audit module for ard26 CLI
# Target OS: Ubuntu 24.04 / 26.04 LTS (WSL2) + Windows 11 Host

import os
import glob
import subprocess
from typing import Optional, List, Dict

try:
    import serial.tools.list_ports
except ImportError:
    serial = None


class DeviceDetector:
    """Detects active serial ports on WSL Linux runtime and Windows 11 host."""

    @staticmethod
    def find_wsl_port() -> Optional[str]:
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
    def audit_win11_host() -> List[Dict[str, str]]:
        """Queries Windows 11 host PnP devices via powershell.exe."""
        devices = []
        try:
            cmd = [
                "pwsh.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
                "Get-PnpDevice -PresentOnly | Where-Object { $_.Class -eq 'Ports' } | Select-Object FriendlyName, Status"
            ]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
            if res.returncode == 0:
                for line in res.stdout.splitlines():
                    line = line.strip()
                    if line and ("COM" in line or "CH340" in line or "Arduino" in line):
                        devices.append({"friendly_name": line})
        except Exception:
            pass
        return devices

    @staticmethod
    def detect_sketch_baud(sketch_dir: Path) -> Optional[int]:
        """Scans sketch .ino files for Serial.begin(baud) to auto-detect baud rate."""
        import re
        if not sketch_dir:
            return None
        
        # Resolve path if string or path object
        p = Path(sketch_dir)
        if p.is_file():
            p = p.parent
        elif not p.is_dir():
            return None

        for ino_file in p.glob("*.ino"):
            try:
                content = ino_file.read_text(encoding="utf-8", errors="ignore")
                match = re.search(r'Serial\.begin\s*\(\s*(\d+)\s*\)', content)
                if match:
                    return int(match.group(1))
            except Exception:
                pass
        return None

    @classmethod
    def resolve_port(cls, user_port: Optional[str] = None, default_port: str = "/dev/ttyUSB0") -> str:
        """Resolves target port: explicit user port -> autodetected port -> config default."""
        if user_port:
            return user_port
        
        detected = cls.find_wsl_port()
        if detected:
            return detected
        return default_port

# file dev-tools/ard26_cli/detector.py ends
