# file: dev-tools/ard26_cli/cli.py
# Purpose: Unified command-line interface entrypoint for ard26 tool
# Target OS: Ubuntu 24.04 / 26.04 LTS (WSL2) + Windows 11 Host

import os
import sys
import argparse
import subprocess
import time
from pathlib import Path

import shutil

from ard26_cli.config import Config
from ard26_cli.detector import DeviceDetector

try:
    import serial
except ImportError:
    serial = None


def find_arduino_cli() -> Optional[str]:
    """Finds arduino-cli binary in PATH or ~/.local/bin."""
    path = shutil.which("arduino-cli")
    if path:
        return path
    local_bin = Path.home() / ".local" / "bin" / "arduino-cli"
    if local_bin.exists():
        return str(local_bin)
    # Check if Windows host has arduino-cli
    if shutil.which("arduino-cli.exe"):
        return "arduino-cli.exe"
    return None


def resolve_sketch_path(sketch_arg: str, root_dir: Path) -> Path:
    """Resolves sketch directory path from relative argument or name."""
    p = Path(sketch_arg)
    if p.is_dir() and (p / f"{p.name}.ino").exists():
        return p.resolve()
    
    # Check under sketches/ directory
    sketches_dir = root_dir / "sketches" / sketch_arg
    if sketches_dir.is_dir():
        return sketches_dir.resolve()
    
    # Check if a specific file path was given
    if p.is_file() and p.suffix == ".ino":
        return p.parent.resolve()
        
    return p.resolve()


def cmd_compile(args, cfg: Config):
    """Executes sketch compilation via arduino-cli."""
    sketch_path = resolve_sketch_path(args.sketch or "uno_blink", cfg.root_dir)
    fqbn = args.fqbn or cfg.fqbn
    cli_bin = find_arduino_cli()

    if not cli_bin:
        print("[!] 'arduino-cli' not found in PATH or ~/.local/bin.", file=sys.stderr)
        print("[!] To install required utilities, run: ./dev-tools/provision_environment.sh", file=sys.stderr)
        sys.exit(1)
    
    print(f"[*] Compiling sketch : {sketch_path}")
    print(f"[*] Target FQBN     : {fqbn}")
    print(f"[*] CLI Executable  : {cli_bin}")
    
    cmd = [cli_bin, "compile", "--fqbn", fqbn, str(sketch_path)]
    res = subprocess.run(cmd)
    if res.returncode == 0:
        print("[SUCCESS] Compilation completed successfully.")
    else:
        print(f"[X] Compilation failed with exit code {res.returncode}.", file=sys.stderr)
        sys.exit(res.returncode)


def cmd_upload(args, cfg: Config):
    """Executes sketch compilation and flashing to serial port."""
    sketch_path = resolve_sketch_path(args.sketch or "uno_blink", cfg.root_dir)
    fqbn = args.fqbn or cfg.fqbn
    port = DeviceDetector.resolve_port(args.port, cfg.port_wsl)
    cli_bin = find_arduino_cli()

    print(f"[*] Uploading sketch : {sketch_path}")
    print(f"[*] Target FQBN      : {fqbn}")
    print(f"[*] Target Port      : {port}")

    if port.startswith("COM") or os.name == "nt":
        # Windows Native Upload Callout
        win_cmd = ["cmd.exe", "/c", "arduino-cli", "compile", "--fqbn", fqbn, str(sketch_path)]
        print(f"[*] Executing Windows host compile callout...")
        r1 = subprocess.run(win_cmd)
        if r1.returncode != 0:
            sys.exit(r1.returncode)
            
        win_upload = ["cmd.exe", "/c", "arduino-cli", "upload", "-p", port, "--fqbn", fqbn, str(sketch_path)]
        print(f"[*] Executing Windows host upload callout to {port}...")
        r2 = subprocess.run(win_upload)
        if r2.returncode == 0:
            print("[SUCCESS] Upload to Windows host port complete.")
        else:
            sys.exit(r2.returncode)
    if not port.startswith("COM") and not os.name == "nt":
        if not cli_bin:
            print("[!] 'arduino-cli' not found in PATH or ~/.local/bin.", file=sys.stderr)
            print("[!] To install required utilities, run: ./dev-tools/provision_environment.sh", file=sys.stderr)
            sys.exit(1)
        # Linux / WSL Upload Callout
        cmd = [cli_bin, "compile", "-u", "-p", port, "--fqbn", fqbn, str(sketch_path)]
        res = subprocess.run(cmd)
        if res.returncode == 0:
            print("[SUCCESS] Compile and upload complete.")
        else:
            print(f"[X] Upload failed with exit code {res.returncode}.", file=sys.stderr)
            sys.exit(res.returncode)


def cmd_monitor(args, cfg: Config):
    """Launches interactive serial monitor with UTF-8 decoding."""
    port = DeviceDetector.resolve_port(args.port, cfg.port_wsl)
    baud = args.baud or cfg.baud_default

    print(f"==========================================================")
    print(f"    Arduino26 Unified Serial Monitor                      ")
    print(f"==========================================================")
    print(f"[*] Target Port : {port}")
    print(f"[*] Baud Rate   : {baud}")
    print(f"[*] Exit        : Press Ctrl+C to disconnect")
    print(f"----------------------------------------------------------")

    if port.startswith("COM"):
        # Windows Native PowerShell Serial Monitor Callout
        ps_cmd = [
            "pwsh.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", str(cfg.root_dir / "tools" / "win11_serial_monitor.ps1"),
            "-Port", port, "-Baud", str(baud)
        ]
        subprocess.run(ps_cmd)
        return

    if serial is None:
        print("[X] Error: pySerial is required for Linux serial monitor. Run: pip install pyserial", file=sys.stderr)
        sys.exit(1)

    try:
        ser = serial.Serial(port, baud, timeout=1.0)
        print(f"[+] Connected to {port} at {baud} baud (UTF-8).")
        while ser.is_open:
            if ser.in_waiting > 0:
                line = ser.readline().decode("utf-8", errors="ignore").strip()
                if line:
                    ts = time.strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[{ts}] {line}")
            time.sleep(0.01)
    except KeyboardInterrupt:
        print(f"\n[*] Disconnected from {port}.")
    except Exception as e:
        print(f"[X] Serial Error on {port}: {e}", file=sys.stderr)


def cmd_scan(args, cfg: Config):
    """Scans and lists active serial devices on WSL and Windows 11 host."""
    print("==========================================================")
    print("    Arduino26 Hardware & Serial Device Scanner            ")
    print("==========================================================")
    
    wsl_port = DeviceDetector.find_wsl_port()
    print(f"[*] WSL Serial Node   : {wsl_port or 'None detected'}")
    
    print("[*] Auditing Windows 11 Host PnP Devices...")
    win_devices = DeviceDetector.audit_win11_host()
    if win_devices:
        for dev in win_devices:
            print(f"    - Host Device: {dev['friendly_name']}")
    else:
        print("    - No host serial devices reported by PowerShell.")
    print("----------------------------------------------------------")


def cmd_config(args, cfg: Config):
    """Displays current active workspace configuration settings."""
    print("==========================================================")
    print("    Arduino26 Workspace Configuration                     ")
    print("==========================================================")
    print(f"[*] Config File      : {cfg.config_path}")
    print(f"[*] Default FQBN     : {cfg.fqbn}")
    print(f"[*] WSL Serial Port  : {cfg.port_wsl}")
    print(f"[*] Win Serial Port  : {cfg.port_win}")
    print(f"[*] Auto-Detected    : {DeviceDetector.find_wsl_port() or 'None'}")
    print(f"[*] Default Baud     : {cfg.baud_default}")
    print("==========================================================")


def main():
    cfg = Config()
    parser = argparse.ArgumentParser(
        prog="ard26",
        description="Arduino26 Unified Embedded CLI & Telemetry Convenience Tool",
        epilog="Configuration loaded from arduino_config.toml"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # compile
    p_comp = subparsers.add_parser("compile", help="Compile an Arduino sketch")
    p_comp.add_argument("sketch", nargs="?", default="uno_blink", help="Sketch directory or name (default: uno_blink)")
    p_comp.add_argument("--fqbn", default=None, help="Fully Qualified Board Name")

    # upload
    p_up = subparsers.add_parser("upload", help="Compile and upload sketch to microcontroller")
    p_up.add_argument("sketch", nargs="?", default="uno_blink", help="Sketch directory or name (default: uno_blink)")
    p_up.add_argument("-p", "--port", default=None, help="Target serial port (/dev/ttyUSB0 or COM5)")
    p_up.add_argument("--fqbn", default=None, help="Fully Qualified Board Name")

    # monitor
    p_mon = subparsers.add_parser("monitor", help="Open interactive serial monitor with UTF-8 support")
    p_mon.add_argument("-p", "--port", default=None, help="Target serial port")
    p_mon.add_argument("-b", "--baud", type=int, default=None, help="Baud rate (default: 115200)")

    # scan
    subparsers.add_parser("scan", help="Scan local WSL and Windows 11 serial devices")

    # config
    subparsers.add_parser("config", help="Show active configuration settings")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    commands = {
        "compile": cmd_compile,
        "upload": cmd_upload,
        "monitor": cmd_monitor,
        "scan": cmd_scan,
        "config": cmd_config,
    }

    handler = commands.get(args.command)
    if handler:
        handler(args, cfg)


if __name__ == "__main__":
    main()

# file dev-tools/ard26_cli/cli.py ends
