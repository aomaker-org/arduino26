# Hardware Setup: Uno-Assisted Leonardo Reset Controller
# file: docs/hardware_setup.md

This document describes the hardware wiring, control logic, and orchestration tools for using an Arduino Uno clone (CH340) to control the physical hardware reset line of an Arduino Leonardo.

This design completely bypasses the virtual 1200bps serial touch bootloader trigger on the Leonardo, which is prone to USB driver lockout and enumeration delays under WSL2/USBIP configurations.

---

## 1. Wiring Schematic

Connect the two boards using standard jumper wires:

| Arduino Uno (Controller) | Arduino Leonardo (Target) | Connection Type | Purpose |
| :--- | :--- | :--- | :--- |
| **GND** | **GND** | Wire | Common Ground Reference |
| **GND** | **GND** | Wire (Optional) | Ground Reinforcement |
| **GND** | **GND** | Wire (Optional) | Ground Reinforcement |
| **Digital Pin 7** | **RESET Pin** | Wire | Target Hardware Reset Control |

> [!IMPORTANT]
> A common ground reference is strictly required for the logic levels to be read correctly. Linking the grounds prevents floating logic states.

---

## 2. Theory of Operation

1. **Idle State**: The Uno keeps Pin 7 configured as `INPUT` (high impedance / High-Z). This ensures the Leonardo's reset pin floats normally and runs the sketch.
2. **Reset Pulse**: When the Uno receives the character `'r'` over its serial port (`COM8` / `/dev/ttyUSB0` at 115200 baud), it:
   - Switches Pin 7 to `OUTPUT`.
   - Drives Pin 7 `LOW` (0V) for 150ms.
   - Restores Pin 7 to `INPUT` (High-Z).
3. **Bootloader Invocation**: The Leonardo registers the low pulse, resets, and boots into its bootloader interface on `COM9` (or `/dev/ttyACM0`) for 8 seconds, awaiting upload.

---

## 3. Control Command Reference

Use the unified Python orchestration tool to manage the contraption:

* **Discover Connected Ports**:
  ```bash
  python3 tools/hardware_controller.py discover
  ```
* **Trigger Hardware Reset**:
  ```bash
  python3 tools/hardware_controller.py reset
  ```
* **Verify Connection & Telemetry**:
  ```bash
  python3 tools/hardware_controller.py test
  ```
* **Teardown & Unbind Devices**:
  ```bash
  python3 tools/hardware_controller.py unbind-all
  ```

# docs/hardware_setup.md ends
