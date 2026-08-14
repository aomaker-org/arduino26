# file: tools/hardware_controller.py
# Purpose: Unified CLI for discovering, testing, and managing the Uno-assisted Leonardo setup
# Target OS: Ubuntu 24.04 / 26.04 LTS (WSL2) + Windows 11 Host

import os
import sys
import time
import argparse
import subprocess
from pathlib import Path

# Vendor/Product IDs
VID_PID_UNO = "1a86:7523"      # CH340 Uno Clone
VID_PID_LEO = "2341:8036"      # Arduino Leonardo

def run_host_cmd(cmd: str) -> str:
    """Helper to run a powershell command on the host."""
    ps_cmd = ["pwsh.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd]
    res = subprocess.run(ps_cmd, capture_output=True, text=True, check=False)
    return res.stdout.strip()

def get_devices():
    """Queries usbipd to discover ports, VIDs, PIDs, and shared state."""
    raw = run_host_cmd("usbipd list")
    devices = []
    
    # Simple parse of usbipd list
    for line in raw.splitlines():
        line = line.strip()
        if not line or "BUSID" in line or "Connected:" in line or "Persisted:" in line:
            continue
        parts = line.split(maxsplit=3)
        if len(parts) >= 3:
            busid, vid_pid, name = parts[0], parts[1], parts[2]
            state = parts[3] if len(parts) > 3 else "Unknown"
            
            # Check if this matches Uno or Leonardo
            dev_type = None
            if vid_pid == VID_PID_UNO:
                dev_type = "Uno Controller"
            elif vid_pid == VID_PID_LEO:
                dev_type = "Leonardo Target"
                
            if dev_type:
                devices.append({
                    "busid": busid,
                    "vid_pid": vid_pid,
                    "name": name,
                    "state": state,
                    "type": dev_type
                })
    return devices

def cmd_discover(args):
    """Prints out all discovered devices and their active status."""
    print("==========================================================")
    print("                USB Device Discovery")
    print("==========================================================")
    devs = get_devices()
    if not devs:
        print("[!] No matching Uno or Leonardo devices found in usbipd.")
        return
        
    for d in devs:
        print(f"[*] Found: {d['type']}")
        print(f"    Bus ID : {d['busid']}")
        print(f"    VID:PID: {d['vid_pid']}")
        print(f"    Name   : {d['name']}")
        print(f"    State  : {d['state']}")
        print("-" * 58)

def trigger_reset_via_host(com_port: str):
    """Sends the reset trigger to the Uno on a Windows COM port."""
    print(f"[*] Sending reset trigger to Uno on host port {com_port}...")
    cmd = (
        f"$p = New-Object System.IO.Ports.SerialPort {com_port}, 115200; "
        f"$p.Open(); $p.Write('r'); Start-Sleep -Milliseconds 250; $p.Close()"
    )
    run_host_cmd(cmd)

def cmd_reset(args):
    """Finds the Uno and triggers a Leonardo hardware reset."""
    devs = get_devices()
    uno = next((d for d in devs if d["type"] == "Uno Controller"), None)
    if not uno:
        print("[X] Error: Could not locate Uno Controller in devices list.")
        sys.exit(1)
        
    # Extract COM port from name or state (e.g. "USB-SERIAL" and "CH340 (COM8)")
    import re
    combined_str = f"{uno['name']} {uno['state']}"
    match = re.search(r"COM\d+", combined_str)
    if not match:
        print(f"[X] Error: Could not identify COM port for Uno in device details: {combined_str}")
        sys.exit(1)
        
    com_port = match.group(0)
    trigger_reset_via_host(com_port)
    print("[SUCCESS] Reset trigger command sent.")

def cmd_test(args):
    """Triggers reset and verifies Leonardo disconnect and reconnect telemetry."""
    print("==========================================================")
    print("             Hardware Contraption Loop Test")
    print("==========================================================")
    
    # 1. Trigger the reset
    cmd_reset(args)
    
    # 2. Wait for disconnect
    print("[*] Monitoring WSL port /dev/ttyACM0 for disconnect...")
    disconnected = False
    for _ in range(50):
        if not os.path.exists("/dev/ttyACM0"):
            print("[+] Disconnect detected successfully!")
            disconnected = True
            break
        time.sleep(0.1)
        
    if not disconnected:
        print("[!] Warning: Did not detect port disappearance. Continuing...")
        
    # 3. Wait for reconnect
    print("[*] Waiting for /dev/ttyACM0 to reappear...")
    reconnected = False
    for _ in range(150):
        if os.path.exists("/dev/ttyACM0"):
            print("[+] Port /dev/ttyACM0 reconnected successfully!")
            reconnected = True
            break
        time.sleep(0.1)
        
    if not reconnected:
        print("[X] Error: Leonardo failed to reconnect within timeout.")
        sys.exit(1)
        
    # 4. Read telemetry
    try:
        import serial
    except ImportError:
        print("[!] pySerial not installed. Skipping telemetry read test.")
        return
        
    print("[*] Reading first 3 telemetry frames (DTR enabled)...")
    time.sleep(1.0) # Settle stack
    try:
        ser = serial.Serial()
        ser.port = "/dev/ttyACM0"
        ser.baudrate = 115200
        ser.timeout = 2.0
        ser.dtr = True
        ser.open()
        
        frames = 0
        while frames < 3:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            if line:
                print(f"    [Telemetry] {line}")
                if "A0" in line:
                    frames += 1
        ser.close()
        print("[SUCCESS] Contraption test passed successfully!")
    except Exception as e:
        print(f"[X] Telemetry read failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="Uno-assisted Leonardo hardware controller CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    subparsers.add_parser("discover", help="Scan and identify Uno and Leonardo USB configurations")
    subparsers.add_parser("reset", help="Pulse Leonardo reset via the Uno controller")
    subparsers.add_parser("test", help="Test reset loop and read active target telemetry")
    
    args = parser.parse_args()
    
    if args.command == "discover":
        cmd_discover(args)
    elif args.command == "reset":
        cmd_reset(args)
    elif args.command == "test":
        cmd_test(args)

if __name__ == "__main__":
    main()

# file tools/hardware_controller.py ends
