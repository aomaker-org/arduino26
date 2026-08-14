# Hardware & Software Orchestration Checklists
# file: docs/checklists.md

This document contains step-by-step checklists to verify hardware assembly, execute daily development operations, and troubleshoot USB/driver conflicts for the Uno-assisted Leonardo reset configuration.

---

## 1. Hardware Assembly & Verification Checklist

- [ ] **Power Down**: Disconnect both Arduino boards from the USB ports of the host machine before wiring.
- [ ] **Common Ground**: Connect at least one GND pin on the Uno to a GND pin on the Leonardo target. (Optionally run 2-3 ground wires to reinforce connection).
- [ ] **Reset Hookup**: Connect **Digital Pin 7** on the Uno to the **RESET** pin on the Leonardo.
- [ ] **Ground Protection**: Verify no loose wire strands or bare leads are bridging pins or touching metal chassis.
- [ ] **USB Connection**: Connect both boards to the host (optionally using a single USB hub).
- [ ] **USB Identification**: Run `python3 tools/hardware_controller.py discover` to verify both boards are enumerated (Uno on COM8, Leonardo on COM6 or COM9).

---

## 2. Daily Development & Upload Checklist

- [ ] **Compile & Flash**: Run `./tools/upload_win.sh` to compile, trigger the Uno hardware reset, and upload the Leonardo sketch natively.
- [ ] **Verify Re-enumeration**: Listen for the host disconnect and reconnect beeps to confirm Leonardo booted into sketch mode.
- [ ] **Attach to WSL**: Run `pwsh_bypass -Command "usbipd attach --wsl --busid 3-4"` to forward the running Leonardo target to WSL.
- [ ] **Verify WSL Node**: Confirm that `/dev/ttyACM0` exists in WSL (`ls -l /dev/ttyACM*`).
- [ ] **Run Telemetry**: Start your python diagnostics or data collectors inside WSL:
  ```bash
  python3 tools/leo_diagnostics.py -d 10
  ```

---

## 3. Teardown & Reconfiguration Checklist

- [ ] **Kill Active Readers**: Stop any running Python telemetry scripts or serial monitors.
- [ ] **Detach WSL Nodes**: Run `pwsh_bypass -Command "usbipd detach --busid 3-4"` to release the Leonardo target back to the Windows host.
- [ ] **Safe Unplug**: Unplug the USB cables (or the USB hub) from the computer.
- [ ] **Reconfigure/Rewire**: Safely make hardware adjustments now that the boards are completely powered down.

---

## 4. Troubleshooting Diagnostics Checklist

If `Access is denied` or `butterfly_recv()` errors occur:
- [ ] **Verify usbipd State**: Run `python3 tools/hardware_controller.py discover` and verify that the Uno Controller is in the `Not shared` state (Windows host needs native access to send serial command).
- [ ] **Release Locked Handles**: Close any open terminal windows or background python scripts that may have locks on `COM8` or `COM9`.
- [ ] **Power Cycle Hub**: Unplug the USB hub, wait 3 seconds, and plug it back in to force a driver-level handle release.
- [ ] **Run Loop Test**: Execute the automated loop test script to diagnose the failure point:
  ```bash
  python3 tools/hardware_controller.py test
  ```

# docs/checklists.md ends
