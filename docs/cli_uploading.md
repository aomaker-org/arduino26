# How to Upload Arduino Sketches via Command Line (CLI)
<!-- file: docs/cli_uploading.md -->

This guide documents CLI workflows for compiling and flashing code to Arduino microcontrollers (starting with Uno clones based on the ATmega328P and CH340 USB-to-Serial converter) inside WSL2 Ubuntu 26.

---

## ⚡ 1. Concise Fast-Track Summary (For Experienced Engineers)

### Prerequisites Check
Ensure your physical USB device is attached to WSL2 and permissions are set:

```bash
# 1. Attach device from Windows host to WSL (via PowerShell callout)
pwsh.exe -Command "usbipd attach --wsl --busid <BUSID>"

# 2. Add user to dialout group (one-time requirement)
sudo usermod -aG dialout $USER

# 3. Source environment
source config_env
```

### Primary CLI Commands
```bash
# Install arduino-cli (if not already installed)
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | BINDIR=~/.local/bin sh
arduino-cli core update-index && arduino-cli core install arduino:avr

# Compile sketch
arduino-cli compile --fqbn arduino:avr:uno sketches/uno_blink

# Upload sketch to serial port (/dev/ttyUSB0 or /dev/ttyACM0)
arduino-cli upload -p /dev/ttyUSB0 --fqbn arduino:avr:uno sketches/uno_blink

# One-liner compile & upload
arduino-cli compile -u -p /dev/ttyUSB0 --fqbn arduino:avr:uno sketches/uno_clone_diag

# Workspace helper script
./tools/upload_sketch.sh sketches/uno_clone_diag /dev/ttyUSB0
```

---

## 📘 2. Detailed Toolchain Step-by-Step Guide

### Method A: `arduino-cli` (Recommended Official Toolchain)

`arduino-cli` is the official command-line interface provided by Arduino. It manages cores, libraries, compilation, and uploading without launching a graphical interface.

#### 1. Installation & Initial Configuration
```bash
# Download binary to local bin
mkdir -p ~/.local/bin
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | BINDIR=~/.local/bin sh

# Initialize configuration
arduino-cli config init

# Update index and install AVR core for Uno / Nano / Mega
arduino-cli core update-index
arduino-cli core install arduino:avr
```

#### 2. Board Detection & FQBN Resolution
Identify connected board attributes:

```bash
arduino-cli board list
```

*Sample Output:*
```
Port         Protocol Type              Board Name  FQBN            Core
/dev/ttyUSB0 serial   Serial Port (USB) Arduino Uno arduino:avr:uno arduino:avr
```

#### 3. Compilation Options
- Compile sketch:
  ```bash
  arduino-cli compile --fqbn arduino:avr:uno sketches/uno_blink
  ```
- Export binary `.hex` file to build folder:
  ```bash
  arduino-cli compile --fqbn arduino:avr:uno --output-dir build/uno_blink sketches/uno_blink
  ```

#### 4. Uploading
```bash
arduino-cli upload -p /dev/ttyUSB0 --fqbn arduino:avr:uno sketches/uno_blink
```

---

### Method B: Direct Flashing via `avrdude`

`avrdude` (AVR Downloader/Uploader) is the low-level utility used under the hood by Arduino IDE and `arduino-cli` to program ATmega microcontrollers.

#### Flashing Pre-Compiled `.hex` Files
For standard Arduino Uno (Optiboot bootloader @ 115200 baud):

```bash
avrdude -C /etc/avrdude.conf -v \
  -p atmega328p \
  -c arduino \
  -P /dev/ttyUSB0 \
  -b 115200 \
  -D \
  -U flash:w:build/uno_blink.hex:i
```

> **Note for Older Nano / Uno Clones:**
> Some cheap CH340 clones use the older STK500v1 bootloader operating at **57600 baud**. If 115200 baud fails with `avrdude: stk500_recv(): programmer is not responding`, change `-b 115200` to `-b 57600`.

---

### Method C: GNU Makefile (`avr-gcc` Bare Metal & Assembly)

For bare-metal C or AVR Assembly (`asm/uno_blink/`):

```bash
# Navigate to project directory
cd asm/uno_blink

# Assemble and link ELF/HEX files
make

# Flash HEX to microcontroller
make PORT=/dev/ttyUSB0 flash
```

---

### Method D: Bare Metal Rust (`ravedude` / `cargo-avr`)

For Rust projects (`rust/uno_blink/`):

```bash
cd rust/uno_blink

# Build release ELF binary
cargo +nightly build --Z build-std=core --target avr-specs/avr-atmega328p.json --release

# Flash using ravedude
ravedude uno -P /dev/ttyUSB0 target/avr-atmega328p/release/uno_blink.elf
```

---

## 🛠️ 3. Troubleshooting & Diagnostics

### Issue 1: `Permission denied: '/dev/ttyUSB0'`
- **Cause:** User account lacks read/write permissions on the POSIX serial character device.
- **Fix:** Add your user account to the `dialout` group:
  ```bash
  sudo usermod -aG dialout $USER
  sudo chmod 666 /dev/ttyUSB0
  ```

### Issue 2: `avrdude: stk500_recv(): programmer is not responding`
- **Causes:**
  1. Incorrect serial port (e.g. specified `/dev/ttyUSB0` when port is `/dev/ttyACM0`).
  2. Wrong baud rate (try `-b 57600` instead of `-b 115200` for older bootloaders).
  3. Serial port currently held open by a terminal monitor (`picocom`, `minicom`, `mpremote`, or Windows IDE). Close monitoring sessions before uploading.
  4. Device not attached from Windows host into WSL2. Check `pwsh.exe -Command "usbipd list"`.

---

## 🌐 References & External Web Resources

- 📖 [Arduino CLI Command Reference](https://arduino.github.io/arduino-cli/latest/commands/arduino-cli/)
- 📖 [AVRDUDE Official Documentation](https://www.nongnu.org/avrdude/user-manual/avrdude.html)
- 📄 [Optiboot Bootloader GitHub Repository](https://github.com/Optiboot/optiboot)

<!-- file docs/cli_uploading.md ends -->
