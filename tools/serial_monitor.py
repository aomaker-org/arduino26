#!/usr/bin/env python3
# ==============================================================================
# Path:        tools/serial_monitor.py
# Purpose:     Bi-directional Serial Terminal & Telemetry Logger for Arduino/CH340
# Target OS:   Ubuntu 24.04 / 26.04 LTS (WSL2 / Linux Native)
# Lineage:     Arduino26 Infrastructure
# Updated:     2026-07-31
# ==============================================================================

import argparse
import sys
import threading
import time

try:
    import serial
    import serial.tools.list_ports
    HAS_PYSERIAL = True
except ImportError:
    HAS_PYSERIAL = False

def list_ports():
    print("Available Serial Ports:")
    if HAS_PYSERIAL:
        ports = serial.tools.list_ports.comports()
        if not ports:
            print("  [!] No serial ports found inside WSL2 / Linux.")
        for p in ports:
            print(f"  - {p.device} ({p.description}) [VID:PID={p.vid}:{p.pid}]")
    else:
        print("  [!] pyserial is not installed. Install via: pip install pyserial")

def read_loop(ser, log_file=None):
    """Continuously reads incoming serial lines and outputs to terminal/log."""
    while ser.is_open:
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    ts = time.strftime("[%Y-%m-%d %H:%M:%S]")
                    output_str = f"{ts} {line}"
                    print(output_str, flush=True)

                    if log_file:
                        with open(log_file, "a", encoding="utf-8") as f:
                            f.write(f"{output_str}\n")
            else:
                time.sleep(0.01)
        except Exception as e:  # noqa: BLE001
            print(f"\n[!] Serial read error: {e}", file=sys.stderr)
            break

def write_loop(ser):
    """Reads user terminal input and sends it over serial."""
    while ser.is_open:
        try:
            user_input = input()
            if user_input.strip() in [":q", "exit", "quit"]:
                print("[*] Exiting serial monitor...")
                ser.close()
                sys.exit(0)
            ser.write((user_input + "\n").encode('utf-8'))
        except (EOFError, KeyboardInterrupt):
            ser.close()
            sys.exit(0)
        except Exception as e:  # noqa: BLE001
            print(f"\n[!] Serial write error: {e}", file=sys.stderr)
            break

def main():
    parser = argparse.ArgumentParser(description="Arduino26 Python Serial Monitor & Telemetry Logger")
    parser.add_argument("-p", "--port", default="/dev/ttyUSB0", help="Target serial port (default: /dev/ttyUSB0)")
    parser.add_argument("-b", "--baud", type=int, default=115200, help="Baud rate (default: 115200)")
    parser.add_argument("-l", "--list", action="store_true", help="List available serial ports and exit")
    parser.add_argument("-o", "--output", help="Save telemetry log to specified file path")
    args = parser.parse_args()

    if args.list:
        list_ports()
        sys.exit(0)

    if not HAS_PYSERIAL:
        print("[X] Error: 'pyserial' package is required.", file=sys.stderr)
        print("    Install it via: pip install pyserial", file=sys.stderr)
        sys.exit(1)

    print("==========================================================")
    print("    Arduino26 Interactive Python Serial Monitor          ")
    print("==========================================================")
    print(f"[*] Port      : {args.port}")
    print(f"[*] Baud Rate : {args.baud}")
    print("[*] Command   : Type commands and press ENTER to send.")
    print("[*] Exit      : Type ':q' or press Ctrl+C to exit.")
    if args.output:
        print(f"[*] Logging to: {args.output}")
    print("----------------------------------------------------------", flush=True)

    try:
        ser = serial.Serial(args.port, args.baud, timeout=1)
        time.sleep(1.5)  # Allow Arduino DTR reset to settle
    except Exception as e:  # noqa: BLE001
        print(f"[X] Connection Error on {args.port}: {e}", file=sys.stderr)
        print("\nTroubleshooting Hints:")
        print("  1. Check permissions: sudo usermod -aG dialout $USER")
        print("  2. Ensure port is attached to WSL2 via usbipd.")
        print("  3. List active ports: python3 tools/serial_monitor.py --list")
        sys.exit(1)

    # Spawn reader thread
    t_read = threading.Thread(target=read_loop, args=(ser, args.output), daemon=True)
    t_read.start()

    # Main thread handles interactive write loop
    write_loop(ser)

if __name__ == "__main__":
    main()
