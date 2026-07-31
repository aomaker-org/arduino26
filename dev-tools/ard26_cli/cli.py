# file: dev-tools/ard26_cli/cli.py
# Purpose: Unified command-line interface entrypoint for ard26 tool
# Target OS: Ubuntu 24.04 / 26.04 LTS (WSL2) + Windows 11 Host

import os
import sys
import argparse
import subprocess
import time
from typing import Optional
from pathlib import Path
import shutil

from ard26_cli.config import Config
from ard26_cli.detector import DeviceDetector
from ard26_cli.logger import OperationLogger
from ard26_cli.telemetry import TelemetryLogger

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
    logger = OperationLogger(cfg.root_dir)
    sketch_path = resolve_sketch_path(args.sketch or cfg.last_compiled_sketch, cfg.root_dir)
    fqbn = args.fqbn or cfg.fqbn
    cli_bin = find_arduino_cli()

    if not cli_bin:
        print("[!] 'arduino-cli' not found in PATH or ~/.local/bin.", file=sys.stderr)
        print("[!] To install required utilities, run: ./dev-tools/provision_environment.sh", file=sys.stderr)
        logger.log_operation("compile", sketch_path.name, "N/A", "FAILED", 1)
        sys.exit(1)
    
    print(f"[*] Compiling sketch : {sketch_path}")
    print(f"[*] Target FQBN     : {fqbn}")
    print(f"[*] CLI Executable  : {cli_bin}")
    
    cmd = [cli_bin, "compile", "--fqbn", fqbn, str(sketch_path)]
    res = subprocess.run(cmd)
    if res.returncode == 0:
        print("[SUCCESS] Compilation completed successfully.")
        cfg.set_last_compiled_sketch(sketch_path.name)
        logger.log_operation("compile", sketch_path.name, "N/A", "SUCCESS", 0)
        print(f"[*] Default upload sketch locked -> [{sketch_path.name}]")
    else:
        print(f"[X] Compilation failed with exit code {res.returncode}.", file=sys.stderr)
        logger.log_operation("compile", sketch_path.name, "N/A", "FAILED", res.returncode)
        sys.exit(res.returncode)


def cmd_upload(args, cfg: Config):
    """Executes sketch compilation and flashing to serial port."""
    logger = OperationLogger(cfg.root_dir)
    if not args.sketch:
        target_name = cfg.last_compiled_sketch
        if sys.stdin.isatty():
            try:
                ans = input(f"Upload the last compiled sketch [{target_name}]? [Y/n] ").strip()
                if ans and not ans.lower().startswith('y'):
                    print("[!] Upload canceled.")
                    logger.log_operation("upload", target_name, "N/A", "CANCELED", 0)
                    return
            except (KeyboardInterrupt, EOFError):
                print("\n[!] Upload canceled.")
                logger.log_operation("upload", target_name, "N/A", "CANCELED", 0)
                return
        sketch_arg = target_name
    else:
        sketch_arg = args.sketch

    sketch_path = resolve_sketch_path(sketch_arg, cfg.root_dir)
    fqbn = args.fqbn or cfg.fqbn
    port = DeviceDetector.resolve_port(args.port or cfg.preferred_port, cfg.port_wsl)
    cli_bin = find_arduino_cli()

    print(f"[*] Uploading sketch : {sketch_path}")
    print(f"[*] Target FQBN      : {fqbn}")
    print(f"[*] Target Port      : {port}")

    if not cli_bin:
        print("[!] 'arduino-cli' not found in PATH or ~/.local/bin.", file=sys.stderr)
        print("[!] To install required utilities, run: ./dev-tools/provision_environment.sh", file=sys.stderr)
        logger.log_operation("upload", sketch_path.name, port, "FAILED", 1)
        sys.exit(1)

    # Convert sketch path to Windows UNC path if needed
    win_sketch_path = str(sketch_path)
    try:
        wsl_res = subprocess.run(["wslpath", "-w", str(sketch_path)], stdout=subprocess.PIPE, text=True)
        if wsl_res.returncode == 0 and wsl_res.stdout.strip():
            win_sketch_path = wsl_res.stdout.strip()
    except Exception:
        pass

    def run_windows_upload(target_win_port: str) -> bool:
        """Executes upload on Windows host via pwsh.exe with UNC path support."""
        print(f"[*] Executing Windows host upload to {target_win_port}...")
        ps_cmd = [
            "pwsh.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
            f"arduino-cli upload -p {target_win_port} --fqbn {fqbn} '{win_sketch_path}'"
        ]
        res = subprocess.run(ps_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        if res.returncode == 0:
            print(f"[SUCCESS] Upload to Windows host port {target_win_port} complete.")
            cfg.save_successful_upload(target_win_port, "win_failover")
            logger.log_operation("upload", sketch_path.name, target_win_port, "SUCCESS", 0)
            return True
        else:
            if "not recognized" in res.stderr or "CommandNotFoundException" in res.stderr or res.returncode != 0:
                print(f"[!] Windows host upload failed on {target_win_port}.", file=sys.stderr)
                print(f"----------------------------------------------------------", file=sys.stderr)
                print(f"[i] 'arduino-cli' is not installed in your Windows 11 host environment.", file=sys.stderr)
                print(f"[i] To install arduino-cli on Windows host, open PowerShell as Admin and run:", file=sys.stderr)
                print(f"        winget install Arduino.cli", file=sys.stderr)
                print(f"        arduino-cli core update-index && arduino-cli core install arduino:avr", file=sys.stderr)
                print(f"----------------------------------------------------------", file=sys.stderr)
                print(f"[i] Alternatively, attach your physical USB device (CH340) into WSL2:", file=sys.stderr)
                print(f"        1. Open PowerShell on Windows host: pwsh.exe", file=sys.stderr)
                print(f"        2. List connected USB devices:      usbipd list", file=sys.stderr)
                print(f"        3. Attach device to WSL2:           usbipd attach --wsl --busid <BUSID>", file=sys.stderr)
                print(f"----------------------------------------------------------", file=sys.stderr)
            logger.log_operation("upload", sketch_path.name, target_win_port, "FAILED", res.returncode)
            return False

    if port.startswith("COM") or os.name == "nt":
        if not run_windows_upload(port):
            sys.exit(1)
        return

    # Linux / WSL Upload Callout
    cmd = [cli_bin, "compile", "-u", "-p", port, "--fqbn", fqbn, str(sketch_path)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(res.stdout)
        print("[SUCCESS] Compile and upload complete.")
        cfg.save_successful_upload(port, "wsl")
        logger.log_operation("upload", sketch_path.name, port, "SUCCESS", 0)
        return
    else:
        if res.stdout:
            print(res.stdout)
        if res.stderr:
            print(res.stderr, file=sys.stderr)

        if "Permission denied" in res.stderr or "Permission denied" in res.stdout:
            print(f"----------------------------------------------------------", file=sys.stderr)
            print(f"[!] Permission denied accessing WSL serial node {port}.", file=sys.stderr)
            print(f"[i] Run this command in terminal to fix device permissions:", file=sys.stderr)
            print(f"        sudo chmod 666 {port}", file=sys.stderr)
            print(f"----------------------------------------------------------", file=sys.stderr)

        print(f"[!] WSL port {port} upload failed (device not bound to WSL or port busy).", file=sys.stderr)
        win_port = cfg.port_win
        should_failover = False
        if sys.stdin.isatty():
            try:
                ans = input(f"Failover to Windows 11 host environment ({win_port})? [Y/n] ").strip()
                if not ans or ans.lower().startswith('y'):
                    should_failover = True
            except (KeyboardInterrupt, EOFError):
                print("\n[!] Failover canceled.")
                logger.log_operation("upload", sketch_path.name, port, "FAILED", res.returncode)
                sys.exit(res.returncode)
        else:
            should_failover = True

        if should_failover:
            print(f"[*] Failing over to Windows host port {win_port}...")
            if not run_windows_upload(win_port):
                sys.exit(1)
        else:
            logger.log_operation("upload", sketch_path.name, port, "FAILED", res.returncode)
            sys.exit(res.returncode)


def cmd_monitor(args, cfg: Config):
    """Launches interactive serial monitor with UTF-8 decoding and telemetry file logging."""
    logger = OperationLogger(cfg.root_dir)
    port = DeviceDetector.resolve_port(args.port or cfg.preferred_port, cfg.port_wsl)
    baud = args.baud or cfg.baud_default

    t_logger = TelemetryLogger(cfg.root_dir, port, baud)

    print(f"==========================================================")
    print(f"    Arduino26 Unified Serial Monitor                      ")
    print(f"==========================================================")
    print(f"[*] Target Port : {port}")
    print(f"[*] Baud Rate   : {baud}")
    print(f"[*] Session Log : {t_logger.session_log.name}")
    print(f"[*] Exit        : Press Ctrl+C to disconnect")
    print(f"----------------------------------------------------------")
    logger.log_operation("monitor", "N/A", port, "STARTED", 0)

    if port.startswith("COM"):
        # Windows Native PowerShell Serial Monitor Callout
        ps_cmd = [
            "pwsh.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", str(cfg.root_dir / "tools" / "win11_serial_monitor.ps1"),
            "-Port", port, "-Baud", str(baud)
        ]
        subprocess.run(ps_cmd)
        t_logger.close(status="Host Windows Monitor Complete")
        return

    if serial is None:
        print("[X] Error: pySerial is required for Linux serial monitor. Run: pip install pyserial", file=sys.stderr)
        t_logger.close(status="Error: pySerial Missing")
        sys.exit(1)

    try:
        ser = serial.Serial(port, baud, timeout=1.0)
        print(f"[+] Connected to {port} at {baud} baud (UTF-8). Logging to {t_logger.session_log.name}...")
        while ser.is_open:
            if ser.in_waiting > 0:
                line = ser.readline().decode("utf-8", errors="ignore").strip()
                if line:
                    formatted = t_logger.log_line(line)
                    print(formatted)
            time.sleep(0.01)
    except KeyboardInterrupt:
        print(f"\n[*] Disconnected from {port}.")
        t_logger.close(status="Clean Exit (Ctrl+C)")
    except Exception as e:
        print(f"[X] Serial Error on {port}: {e}", file=sys.stderr)
        t_logger.close(status=f"Serial Error: {e}")


def cmd_scan(args, cfg: Config):
    """Scans and lists active serial devices on WSL and Windows 11 host."""
    logger = OperationLogger(cfg.root_dir)
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
    logger.log_operation("scan", "N/A", wsl_port or "None", "SUCCESS", 0)


def cmd_config(args, cfg: Config):
    """Displays current active workspace configuration settings."""
    logger = OperationLogger(cfg.root_dir)
    print("==========================================================")
    print("    Arduino26 Workspace Configuration                     ")
    print("==========================================================")
    print(f"[*] Config File      : {cfg.config_path}")
    print(f"[*] Default FQBN     : {cfg.fqbn}")
    print(f"[*] WSL Serial Port  : {cfg.port_wsl}")
    print(f"[*] Win Serial Port  : {cfg.port_win}")
    print(f"[*] Auto-Detected    : {DeviceDetector.find_wsl_port() or 'None'}")
    print(f"[*] Default Baud     : {cfg.baud_default}")
    print(f"[*] Last Sketch      : {cfg.last_compiled_sketch}")
    print(f"[*] Active Method    : {cfg.active_method}")
    print(f"[*] Preferred Port   : {cfg.preferred_port or 'Not set (auto)'}")
    print(f"[*] History Log      : {logger.history_log}")
    print("==========================================================")
    logger.log_operation("config", "N/A", "N/A", "SUCCESS", 0)


def cmd_run(args, cfg: Config):
    """Executes sequential pipeline: Compile -> Upload -> Monitor."""
    print("==========================================================")
    print("    Arduino26 Pipeline: Compile -> Upload -> Monitor      ")
    print("==========================================================")
    # Step 1: Compile
    cmd_compile(args, cfg)
    print("----------------------------------------------------------")
    # Step 2: Upload
    cmd_upload(args, cfg)
    print("----------------------------------------------------------")
    # Step 3: Monitor
    cmd_monitor(args, cfg)


def main():
    cfg = Config()

    # Pre-process sys.argv to handle multi-subcommand chaining like:
    # "ard26 compile upload monitor sketches/uno_clone_diag"
    argv = sys.argv[1:]
    if len(argv) >= 2:
        valid_cmds = {"compile", "upload", "monitor", "run"}
        cmds_found = []
        sketch_found = None

        for arg in argv:
            if arg in valid_cmds:
                cmds_found.append(arg)
            elif not arg.startswith("-"):
                sketch_found = arg

        if len(cmds_found) > 1:
            print(f"[*] Detected chained commands: {' -> '.join(cmds_found)}")
            # Construct a synthetic namespace
            class SyntheticArgs:
                def __init__(self, sketch):
                    self.sketch = sketch
                    self.fqbn = None
                    self.port = None
                    self.baud = None
            
            synth_args = SyntheticArgs(sketch_found)

            if "compile" in cmds_found:
                cmd_compile(synth_args, cfg)
                print("----------------------------------------------------------")
            if "upload" in cmds_found:
                cmd_upload(synth_args, cfg)
                print("----------------------------------------------------------")
            if "monitor" in cmds_found:
                cmd_monitor(synth_args, cfg)
            return

    parser = argparse.ArgumentParser(
        prog="ard26",
        description="Arduino26 Unified Embedded CLI & Telemetry Convenience Tool",
        epilog="Configuration loaded from arduino_config.toml"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # compile
    p_comp = subparsers.add_parser("compile", help="Compile an Arduino sketch")
    p_comp.add_argument("sketch", nargs="?", default=None, help="Sketch directory or name")
    p_comp.add_argument("--fqbn", default=None, help="Fully Qualified Board Name")

    # upload
    p_up = subparsers.add_parser("upload", help="Compile and upload sketch to microcontroller")
    p_up.add_argument("sketch", nargs="?", default=None, help="Sketch directory or name")
    p_up.add_argument("-p", "--port", default=None, help="Target serial port (/dev/ttyUSB0 or COM5)")
    p_up.add_argument("--fqbn", default=None, help="Fully Qualified Board Name")

    # monitor
    p_mon = subparsers.add_parser("monitor", help="Open interactive serial monitor with telemetry logging")
    p_mon.add_argument("-p", "--port", default=None, help="Target serial port")
    p_mon.add_argument("-b", "--baud", type=int, default=None, help="Baud rate (default: 115200)")

    # run (compile -> upload -> monitor pipeline)
    p_run = subparsers.add_parser("run", help="Compile, upload, and open serial monitor in sequence")
    p_run.add_argument("sketch", nargs="?", default=None, help="Sketch directory or name")
    p_run.add_argument("-p", "--port", default=None, help="Target serial port")
    p_run.add_argument("-b", "--baud", type=int, default=None, help="Baud rate")
    p_run.add_argument("--fqbn", default=None, help="Fully Qualified Board Name")

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
        "run": cmd_run,
        "scan": cmd_scan,
        "config": cmd_config,
    }

    handler = commands.get(args.command)
    if handler:
        handler(args, cfg)


if __name__ == "__main__":
    main()

# file dev-tools/ard26_cli/cli.py ends
