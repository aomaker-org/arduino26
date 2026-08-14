#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ==============================================================================
# file: tools/leo_diagnostics.py
# Purpose: Basic communication and diagnostics reader for Leonardo sketch
# Target OS: Ubuntu 24.04 / 26.04 LTS (WSL2) + Windows 11 Host
# ==============================================================================
import json
import sys
import time
from pathlib import Path

try:
    import serial
except ImportError:
    print("[X] Error: pySerial is required. Run 'pip install pyserial' or activate .venv.")
    sys.exit(1)

def run_diagnostics(port: str, baud: int, duration_sec: int = 10):
    print("==========================================================")
    print(f"       Leonardo Diagnostic Serial Connection Test")
    print("==========================================================")
    print(f"[*] Port    : {port}")
    print(f"[*] Baud    : {baud}")
    print(f"[*] Duration: {duration_sec} seconds")
    print("----------------------------------------------------------")

    try:
        ser = serial.Serial(port, baud, timeout=1.0)
        # Flush input buffer to clear old data
        ser.reset_input_buffer()
        
        start_time = time.time()
        readings_count = 0
        
        while time.time() - start_time < duration_sec:
            if ser.in_waiting > 0:
                raw_line = ser.readline().decode("utf-8", errors="ignore").strip()
                if not raw_line:
                    continue
                
                print(f"[Raw Serial] {raw_line}")
                
                # Attempt to parse as JSON from the test sketch
                if raw_line.startswith("{") and raw_line.endswith("}"):
                    try:
                        data = json.loads(raw_line)
                        print(f"  -> SUCCESSFUL PARSE: A0={data.get('A0')}, A1={data.get('A1')}, A2={data.get('A2')}")
                        readings_count += 1
                    except json.JSONDecodeError:
                        pass
                        
            time.sleep(0.05)
            
        ser.close()
        print("----------------------------------------------------------")
        print(f"[+] Diagnostics completed. Successfully parsed {readings_count} telemetry frames.")
        print("==========================================================")
        
    except Exception as e:
        print(f"[X] Serial communication failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Leonardo serial communication diagnostics.")
    parser.add_argument("-p", "--port", default="/dev/ttyACM0", help="Target serial port")
    parser.add_argument("-b", "--baud", type=int, default=115200, help="Baud rate (default: 115200)")
    parser.add_argument("-d", "--duration", type=int, default=10, help="Test duration in seconds")
    
    args = parser.parse_args()
    run_diagnostics(args.port, args.baud, args.duration)

# file tools/leo_diagnostics.py ends
