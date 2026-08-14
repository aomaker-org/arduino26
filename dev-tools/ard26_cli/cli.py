# file: dev-tools/ard26_cli/cli.py
# Purpose: Unified command-line interface entrypoint for ard26 tool
# Target OS: Ubuntu 24.04 / 26.04 LTS (WSL2) + Windows 11 Host

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from ard26_cli.config import Config
from ard26_cli.detector import DeviceDetector
from ard26_cli.logger import OperationLogger
from ard26_cli.telemetry import TelemetryLogger

try:
    import serial
except ImportError:
    serial = None


def flush_input_buffer():
    """Flushes and prints any pending characters in stdin buffer to prevent accidental prompt responses."""
    import select
    flushed = ""
    try:
        # Keep reading from stdin while data is available (non-blocking)
        while select.select([sys.stdin], [], [], 0.0)[0]:
            char = sys.stdin.read(1)
            if not char:
                break
            flushed += char
    except Exception:
        pass
    if flushed:
        print(f"[i] Flushed accidental input: {repr(flushed)}")


def find_arduino_cli() -> str | None:
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
    """Resolves sketch or Rust project directory path from relative argument or name."""
    p = Path(sketch_arg)
    if p.is_dir() and ((p / f"{p.name}.ino").exists() or (p / "Cargo.toml").exists()):
        return p.resolve()
    
    # Check under rust/ directory
    rust_dir = root_dir / "rust" / sketch_arg
    if rust_dir.is_dir() and (rust_dir / "Cargo.toml").exists():
        return rust_dir.resolve()

    # Check under sketches/ directory
    sketches_dir = root_dir / "sketches" / sketch_arg
    if sketches_dir.is_dir():
        return sketches_dir.resolve()
    
    # Check if a specific file path was given
    if p.is_file():
        return p.parent.resolve()
        
    return p.resolve()


def ensure_avr_gcc_path():
    """Injects arduino-cli bundled avr-gcc directory into os.environ['PATH'] if missing."""
    if shutil.which("avr-gcc"):
        return
    home = Path.home()
    bundled_paths = list(home.glob(".arduino15/packages/arduino/tools/avr-gcc/*/bin"))
    if bundled_paths:
        os.environ["PATH"] = f"{bundled_paths[0]}:{os.environ.get('PATH', '')}"


def cmd_compile(args, cfg: Config):
    """Executes sketch or Rust compilation via arduino-cli or cargo."""
    logger = OperationLogger(cfg.root_dir)
    sketch_path = resolve_sketch_path(args.sketch or cfg.last_compiled_sketch, cfg.root_dir)
    ensure_avr_gcc_path()
    
    # Check if target is a Rust Cargo project
    if (sketch_path / "Cargo.toml").exists():
        print(f"[*] Compiling Rust AVR Project: {sketch_path}")
        cargo_cmd = ["cargo", "build", "--release"]
        if shutil.which("rustup"):
            cargo_cmd = ["cargo", "+nightly", "build", "-Z", "build-std=core", "--release"]
        res = subprocess.run(cargo_cmd, cwd=sketch_path, check=False)
        if res.returncode == 0:
            print("[SUCCESS] Rust compilation completed successfully.")
            cfg.set_last_compiled_sketch(sketch_path.name)
            logger.log_operation("compile", sketch_path.name, "N/A", "SUCCESS", 0)
            print(f"[*] Default upload sketch locked -> [{sketch_path.name}]")
            return
        else:
            print(f"[X] Cargo build failed with exit code {res.returncode}.", file=sys.stderr)
            logger.log_operation("compile", sketch_path.name, "N/A", "FAILED", res.returncode)
            sys.exit(res.returncode)

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
    res = subprocess.run(cmd, check=False)
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
    """Executes sketch or Rust binary compilation and flashing to serial port."""
    logger = OperationLogger(cfg.root_dir)
    if not args.sketch:
        target_name = cfg.last_compiled_sketch
        if sys.stdin.isatty():
            try:
                flush_input_buffer()
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
    fqbn = getattr(args, 'fqbn', None) or cfg.fqbn
    port = DeviceDetector.resolve_port(getattr(args, 'port', None) or cfg.preferred_port, cfg.port_wsl)
    cli_bin = find_arduino_cli()
    ensure_avr_gcc_path()

    # Check if target is a Rust Cargo project
    if (sketch_path / "Cargo.toml").exists():
        print(f"[*] Uploading Rust AVR Target : {sketch_path.name}")
        print(f"[*] Target Port               : {port}")
        # Build first
        cargo_cmd = ["cargo", "build", "--release"]
        if shutil.which("rustup"):
            cargo_cmd = ["cargo", "+nightly", "build", "-Z", "build-std=core", "--release"]
        res_b = subprocess.run(cargo_cmd, cwd=sketch_path, check=False)
        if res_b.returncode != 0:
            print("[X] Rust compilation failed before upload.", file=sys.stderr)
            sys.exit(res_b.returncode)
        
        # Locate ELF / HEX binary
        elf_path = sketch_path / "target" / "avr-atmega328p" / "release" / f"{sketch_path.name}.elf"
        hex_path = sketch_path / "target" / "avr-atmega328p" / "release" / f"{sketch_path.name}.hex"
        if not elf_path.exists():
            # Check generic target
            elf_candidates = list((sketch_path / "target").glob("**/*.elf"))
            if elf_candidates:
                elf_path = elf_candidates[0]
                hex_path = elf_path.with_suffix(".hex")

        if elf_path.exists():
            subprocess.run(["avr-objcopy", "-O", "ihex", "-R", ".eeprom", str(elf_path), str(hex_path)], check=False)
            flash_target = str(hex_path) if hex_path.exists() else str(elf_path)
        else:
            flash_target = str(sketch_path)

        # Flash via avrdude
        avrdude_cmd = ["avrdude", "-p", "m328p", "-c", "arduino", "-P", port, "-b", "115200", "-U", f"flash:w:{flash_target}:i"]
        print(f"[*] Flashing via avrdude: {' '.join(avrdude_cmd)}")
        res_u = subprocess.run(avrdude_cmd, check=False)
        if res_u.returncode == 0:
            print("[SUCCESS] Rust AVR binary successfully flashed.")
            cfg.save_successful_upload(port, "wsl")
            logger.log_operation("upload", sketch_path.name, port, "SUCCESS", 0)
            return
        else:
            print(f"[!] avrdude flash failed on {port}.", file=sys.stderr)
            logger.log_operation("upload", sketch_path.name, port, "FAILED", res_u.returncode)
            sys.exit(res_u.returncode)

    # Convert sketch path to Windows UNC path if needed
    win_sketch_path = str(sketch_path)
    try:
        wsl_res = subprocess.run(["wslpath", "-w", str(sketch_path)], capture_output=True, text=True, check=False)
        if wsl_res.returncode == 0 and wsl_res.stdout.strip():
            win_sketch_path = wsl_res.stdout.strip()
    except Exception:  # noqa: BLE001, S110
        pass

    def run_windows_upload(target_win_port: str) -> bool:
        """Executes upload on Windows host via pwsh.exe with UNC path support."""
        print(f"[*] Executing Windows host upload to {target_win_port}...")
        arduino_bin = "arduino-cli"
        # Check standard Windows installation path to bypass PATH refresh issues
        win_std_bin = r"C:\Program Files\Arduino CLI\arduino-cli.exe"
        # Since we are running in WSL, check using Windows path syntax for existence from Windows perspective
        # or check if the mount path exists (/mnt/c/Program Files/Arduino CLI/arduino-cli.exe)
        wsl_mount_bin = Path("/mnt/c/Program Files/Arduino CLI/arduino-cli.exe")
        if wsl_mount_bin.exists():
            arduino_bin = f"& '{win_std_bin}'"
            
        ps_cmd = [
            "pwsh.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
            f"{arduino_bin} upload -p {target_win_port} --fqbn {fqbn} '{win_sketch_path}'"
        ]
        res = subprocess.run(ps_cmd, capture_output=True, text=True, check=False)
        if res.returncode == 0:
            print(f"[SUCCESS] Upload to Windows host port {target_win_port} complete.")
            cfg.save_successful_upload(target_win_port, "win_failover")
            logger.log_operation("upload", sketch_path.name, target_win_port, "SUCCESS", 0)
            return True
        else:
            print(f"[!] Windows host upload failed on {target_win_port}.", file=sys.stderr)
            if res.stdout:
                print(res.stdout)
            if res.stderr:
                print(res.stderr, file=sys.stderr)
            print("----------------------------------------------------------", file=sys.stderr)
            print("[i] Alternatively, attach your physical USB device (CH340) into WSL2:", file=sys.stderr)
            print("    pwsh.exe -Command \"usbipd list; echo 'Run: usbipd attach --wsl --busid <BUSID>'\"", file=sys.stderr)
            print("----------------------------------------------------------", file=sys.stderr)
            print("[i] To install arduino-cli on Windows host, open PowerShell as Admin and run:", file=sys.stderr)
            print("    winget install Arduino.cli && arduino-cli core update-index && arduino-cli core install arduino:avr", file=sys.stderr)
            print("----------------------------------------------------------", file=sys.stderr)
            logger.log_operation("upload", sketch_path.name, target_win_port, "FAILED", res.returncode)
            return False

    if port.startswith("COM") or os.name == "nt":
        if not run_windows_upload(port):
            sys.exit(1)
        return

    # Linux / WSL Upload Callout
    cmd = [cli_bin, "compile", "-u", "-p", port, "--fqbn", fqbn, str(sketch_path)]
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
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
            print("----------------------------------------------------------", file=sys.stderr)
            print(f"[!] Permission denied accessing WSL serial node {port}.", file=sys.stderr)
            print("[i] Run this command in terminal to fix device permissions:", file=sys.stderr)
            print(f"        sudo chmod 666 {port}", file=sys.stderr)
            print("----------------------------------------------------------", file=sys.stderr)

        print(f"[!] WSL port {port} upload failed (device not bound to WSL or port busy).", file=sys.stderr)
        win_port = cfg.port_win
        should_failover = False
        if sys.stdin.isatty():
            try:
                flush_input_buffer()
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
    port = DeviceDetector.resolve_port(getattr(args, 'port', None) or cfg.preferred_port, cfg.port_wsl)
    
    # Auto-detect baud rate from sketch .ino source files if not explicitly specified
    sketch_arg = getattr(args, 'sketch', None) or cfg.last_compiled_sketch
    sketch_path = resolve_sketch_path(sketch_arg, cfg.root_dir)
    detected_baud = DeviceDetector.detect_sketch_baud(sketch_path)

    if getattr(args, 'baud', None):
        baud = args.baud
    elif detected_baud:
        baud = detected_baud
    else:
        baud = cfg.baud_default

    t_logger = TelemetryLogger(cfg.root_dir, port, baud)

    print("==========================================================")
    print("    Arduino26 Unified Serial Monitor                      ")
    print("==========================================================")
    print(f"[*] Target Port : {port}")
    print(f"[*] Baud Rate   : {baud} {'(auto-detected from sketch)' if detected_baud and not getattr(args, 'baud', None) else ''}")
    print(f"[*] Session Log : {t_logger.session_log.name}")
    print("[*] Monitor log in another terminal (triple-click to copy):")
    print(f"tail -f {t_logger.session_log.resolve()}")
    print("[*] Exit        : Press Ctrl+C to disconnect")
    print("----------------------------------------------------------")
    logger.log_operation("monitor", "N/A", port, "STARTED", 0)

    if port.startswith("COM"):
        # Windows Native PowerShell Serial Monitor Callout
        ps_cmd = [
            "pwsh.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", str(cfg.root_dir / "tools" / "win11_serial_monitor.ps1"),
            "-Port", port, "-Baud", str(baud)
        ]
        subprocess.run(ps_cmd, check=False)
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
    except Exception as e:  # noqa: BLE001
        # If the port is locked/busy, fall back to tailing the log file
        if "device or resource busy" in str(e).lower() or "could not open port" in str(e).lower():
            # Find the latest active serial_telemetry session log
            log_dir = cfg.root_dir / "agy" / "log"
            logs = sorted(log_dir.glob("serial_telemetry_*.log"), key=os.path.getmtime)
            
            if logs:
                latest_log = logs[-1]
                print(f"[!] Port {port} is busy. Tailing latest session log: {latest_log.name}")
                print("[*] Exit: Press Ctrl+C to stop tailing")
                print("----------------------------------------------------------")
                
                try:
                    with open(latest_log, "r", encoding="utf-8", errors="ignore") as lf:
                        # Go to the end of the file
                        lf.seek(0, 2)
                        while True:
                            curr_line = lf.readline()
                            if not curr_line:
                                time.sleep(0.1)
                                continue
                            print(curr_line.rstrip())
                except KeyboardInterrupt:
                    print("\n[*] Stopped tailing log.")
                    sys.exit(0)
            else:
                print(f"[X] Port {port} is busy and no previous session logs found to tail.", file=sys.stderr)
                sys.exit(1)
        else:
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


def cmd_attach(args, cfg: Config):
    """Scan and attach host serial devices to WSL2 using usbipd-win."""
    print("==========================================================")
    print("    Arduino26 USBIPD Host Serial Auto-Attach             ")
    print("==========================================================")
    
    devices = DeviceDetector.list_usbipd_devices()
    if not devices:
        print("[!] No USB devices detected on host or 'usbipd-win' is not installed.")
        print("[i] For installation instructions, see: docs/usbipd_installation.md")
        return
    
    print("[*] Active Host USB Devices:")
    serial_candidates = []
    for dev in devices:
        is_serial = any(k in dev["description"].lower() for k in ["ch340", "usb-serial", "cp210", "ft232", "prolific", "arduino", "serial"])
        marker = " [SERIAL ADAPTER]" if is_serial else ""
        print(f"    - BusID: {dev['busid']} | State: {dev['state']:<12} | {dev['description']}{marker}")
        if is_serial:
            serial_candidates.append(dev)
            
    if not serial_candidates:
        print("\n[!] No host USB serial adapters recognized.")
        return
        
    print(f"\n[*] Found {len(serial_candidates)} candidate serial device(s).")
    target = serial_candidates[0]
    
    if target["state"].lower() == "attached":
        print(f"[SUCCESS] Device at Bus ID {target['busid']} is already attached.")
        port = DeviceDetector.find_wsl_port()
        if port:
            print(f"[SUCCESS] WSL serial port active at: {port}")
            try:
                if os.path.exists(port):
                    os.chmod(port, 0o666)
            except Exception:  # noqa: BLE001, S110
                pass
        return

    print(f"[*] Attaching device at Bus ID {target['busid']}...")
    
    if DeviceDetector.attach_usbipd_device(target["busid"]):
        print("[SUCCESS] Device successfully attached via usbipd.")
        print("[*] Waiting for WSL serial node to initialize...")
        import time
        for _ in range(15):
            time.sleep(0.2)
            port = DeviceDetector.find_wsl_port()
            if port:
                print(f"[SUCCESS] WSL serial port active at: {port}")
                try:
                    if os.path.exists(port):
                        os.chmod(port, 0o666)
                except Exception:  # noqa: BLE001, S110
                    pass
                return
        print("[!] Device attached, but no serial node was created in WSL. You may need to run 'sudo chmod 666 /dev/ttyUSB0' manually.")
    else:
        print("[X] Failed to attach device.")


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

    # Pre-process sys.argv to handle multi-subcommand chaining or auto-infer 'run'
    argv = sys.argv[1:]
    valid_cmds = {"compile", "upload", "monitor", "run", "scan", "config", "attach"}
    
    # Auto-infer 'run' if the first argument is not a subcommand and looks like a sketch
    if (argv and argv[0] not in valid_cmds and not argv[0].startswith("-") and
        ((cfg.root_dir / "sketches" / argv[0]).is_dir() or
         (cfg.root_dir / "rust" / argv[0]).is_dir() or
         Path(argv[0]).is_dir() or
         Path(argv[0]).is_file())):
        print(f"[*] Inferring 'run' command for sketch: {argv[0]}")
        sys.argv.insert(1, "run")
        argv = sys.argv[1:]

    if len(argv) >= 2:
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

    # attach
    subparsers.add_parser("attach", help="Attach host USB serial devices to WSL2 via usbipd-win")

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
        "attach": cmd_attach,
    }

    handler = commands.get(args.command)
    if handler:
        handler(args, cfg)


if __name__ == "__main__":
    main()

# file dev-tools/ard26_cli/cli.py ends
