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
    except Exception as e:
        print(f"[!] Touch failed (could be already in bootloader or permissions issue): {e}")

def wait_for_disappearance(port: str, timeout_sec: float = 5.0) -> bool:
    """Waits for the specified port device node to disappear from /dev."""
    start_time = time.time()
    print(f"[*] Waiting for {port} to disconnect...")
    while time.time() - start_time < timeout_sec:
        if not os.path.exists(port):
            delta = (time.time() - start_time) * 1000.0
            print(f"[+] Device disconnected successfully in {delta:.1f} ms.")
            return True
        time.sleep(0.05)
    print("[!] Timeout: Device node did not disappear from /dev.")
    return False

def wait_for_port(timeout_sec: float = 10.0) -> str | None:
    """Polls for any active ttyACM/ttyUSB node to appear in /dev."""
    start_time = time.time()
    print("[*] Waiting for new serial port to appear in /dev...")
    while time.time() - start_time < timeout_sec:
        for i in range(10):
            acm_port = f"/dev/ttyACM{i}"
            if os.path.exists(acm_port):
                delta = (time.time() - start_time) * 1000.0
                print(f"[+] Found device node: {acm_port} in {delta:.1f} ms.")
                
                # Check permissions
                if os.access(acm_port, os.R_OK | os.W_OK):
                    return acm_port
                else:
                    print(f"[!] Found port {acm_port} but no read/write permissions. Fixing...")
                    subprocess.run(["sudo", "chmod", "666", acm_port], check=False)
                    return acm_port
        time.sleep(0.1)
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
    t_start = time.time()
    trigger_1200bps_touch(touch_port)
    
    # 2. Monitor disconnect
    wait_for_disappearance(touch_port, timeout_sec=5.0)
    
    # 3. Wait for reconnect
    active_port = wait_for_port(timeout_sec=25.0)
    if not active_port:
        print("[X] Timeout waiting for Leonardo serial port to reappear.")
        print("[i] Check if usbipd auto-attach loop is running and attached the device.")
        sys.exit(1)
        
    # 4. Stabilizing buffer delay (gives USB stack/cdc_acm driver time to settle)
    settle_delay = 1.0
    print(f"[*] Settle delay: waiting {settle_delay}s for device initialization...")
    time.sleep(settle_delay)
    
    # 5. Perform the upload
    run_upload(sketch_path, active_port)

if __name__ == "__main__":
    main()

# file tools/upload_leonardo.py ends
