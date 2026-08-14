#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ==============================================================================
# file: tools/upload_leonardo.py
# Purpose: Programmatic Leonardo bootloader reset and upload helper for WSL2
# Target OS: Ubuntu 24.04 / 26.04 LTS (WSL2) + Windows 11 Host
# ==============================================================================
import os
import sys
import time
import subprocess
from pathlib import Path

try:
    import serial
except ImportError:
    serial = None

def trigger_1200bps_touch(port: str):
    """Triggers the Leonardo bootloader by opening and closing the port at 1200 bps."""
    if serial is None:
        print("[!] pySerial is missing. Attempting simple stty touch...")
        try:
            subprocess.run(["stty", "-F", port, "1200"], check=False)
            time.sleep(0.5)
        except Exception as e:
            print(f"[!] stty touch failed: {e}")
        return

    print(f"[*] Touching {port} at 1200 bps to trigger bootloader reset...")
    try:
        ser = serial.Serial()
        ser.port = port
        ser.baudrate = 1200
        ser.open()
        ser.close()
        # Wait for the OS and usbipd to disconnect/reconnect the device
        print("[*] Port touched. Waiting 2.5 seconds for device reconnection...")
        time.sleep(2.5)
    except Exception as e:
        print(f"[!] Touch failed (could be already in bootloader or permissions issue): {e}")

def wait_for_port(timeout_sec: float = 10.0) -> str | None:
    """Polls for any active ttyACM/ttyUSB node to appear in /dev."""
    start_time = time.time()
    print("[*] Scanning /dev/ for active serial port...")
    while time.time() - start_time < timeout_sec:
        for i in range(10):
            acm_port = f"/dev/ttyACM{i}"
            if os.path.exists(acm_port):
                # Try to check if we can read it (checking permissions)
                if os.access(acm_port, os.R_OK | os.W_OK):
                    print(f"[+] Found accessible port: {acm_port}")
                    return acm_port
                else:
                    print(f"[!] Found port {acm_port} but no read/write permissions. Attempting to fix...")
                    subprocess.run(["sudo", "chmod", "666", acm_port], check=False)
                    return acm_port
        time.sleep(0.5)
    return None

def run_upload(sketch_path: str, port: str):
    print(f"[*] Initiating upload of {sketch_path} to {port}...")
    cmd = ["arduino-cli", "upload", "-p", port, "--fqbn", "arduino:avr:leonardo", sketch_path]
    res = subprocess.run(cmd, check=False)
    if res.returncode == 0:
        print("[SUCCESS] Leonardo sketch successfully uploaded!")
        sys.exit(0)
    else:
        print(f"[X] arduino-cli upload failed with exit code {res.returncode}")
        sys.exit(res.returncode)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tools/upload_leonardo.py <sketch_path> [touch_port]")
        sys.exit(1)
        
    sketch_path = sys.argv[1]
    touch_port = sys.argv[2] if len(sys.argv) > 2 else "/dev/ttyACM0"
    
    # 1. Trigger the bootloader
    trigger_1200bps_touch(touch_port)
    
    # 2. Wait for the port to come back online
    active_port = wait_for_port(timeout_sec=10.0)
    if not active_port:
        print("[X] Timeout waiting for Leonardo serial port to reappear.")
        print("[i] Check if usbipd auto-attach loop is running and attached the device.")
        sys.exit(1)
        
    # 3. Perform the upload
    run_upload(sketch_path, active_port)

if __name__ == "__main__":
    main()

# file tools/upload_leonardo.py ends
