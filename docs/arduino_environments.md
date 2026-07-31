# Arduino Development Environments Guide (Verbose Reference)
<!-- file: docs/arduino_environments.md -->

This document provides a deep, technical exploration of the four primary software
environments supported in `arduino26` for target microcontrollers (starting with the
Arduino Uno ATmega328P clone featuring the CH340 USB-to-Serial bridge).

---

## 1. Arduino C++ Environment (`arduino-cli` & IDE)

### Overview
Arduino C++ builds upon standard C++11/C++14 using `avr-g++` and the Arduino Core API
(`Wiring` framework). While the standard Arduino IDE 2.x can be used on Windows 11 or
Linux, `arduino26` prioritizes headless CLI workflows via `arduino-cli`.

### Toolchain Setup (`arduino-cli`)
To install and initialize `arduino-cli` in WSL2 Ubuntu:

```bash
# Download and install arduino-cli
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh

# Add core index and install AVR core package
arduino-cli core update-index
arduino-cli core install arduino:avr
```

### Compiling & Flashing
```bash
# Verify board detection
arduino-cli board list

# Compile sketch
arduino-cli compile --fqbn arduino:avr:uno sketches/uno_blink

# Upload sketch via serial port (/dev/ttyUSB0 or /dev/ttyACM0)
arduino-cli upload -p /dev/ttyUSB0 --fqbn arduino:avr:uno sketches/uno_blink
```

### Direct `avr-libc` C++ Alternative
For developers who want raw C/C++ without the Arduino core runtime overhead:

```cpp
#include <avr/io.h>
#include <util/delay.h>

int main(void) {
    DDRB |= (1 << DDB5); // Set PB5 (Pin 13) to output
    while (1) {
        PORTB ^= (1 << PORTB5); // Toggle PB5
        _delay_ms(1000);
    }
}
```

---

## 2. MicroPython & CircuitPython Environment

### Overview
MicroPython and CircuitPython bring Python 3 syntax and interactive REPL capabilities to
embedded microcontrollers. While ATmega328P (32KB Flash, 2KB RAM) is too constrained for
full Python, modern microcontroller boards (ESP32, RP2040, SAMD21, STM32) integrated in
Arduino form factors support MicroPython directly.

### Interacting via `mpremote` & `picocom`
1. Install `mpremote` inside `.venv`:
   ```bash
   pip install mpremote
   ```
2. Connect to REPL:
   ```bash
   mpremote connect /dev/ttyUSB0 repl
   ```
3. Copy script and run on device:
   ```bash
   mpremote connect /dev/ttyUSB0 cp micropython/main.py :main.py
   mpremote connect /dev/ttyUSB0 run micropython/main.py
   ```

---

## 3. Rust Embedded Environment (`avr-hal` / Bare Metal `no_std`)

### Overview
Rust provides memory-safe bare metal programming for microcontrollers without requiring
an operating system (`no_std`). For 8-bit AVR microcontrollers like the ATmega328P,
the [`avr-hal`](https://github.com/Rahix/avr-hal) project provides high-level hardware
abstraction layers built on top of LLVM's AVR target support.

### Toolchain Setup
1. Install Rust via `rustup`:
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```
2. Add AVR target support and `ravedude` runner:
   ```bash
   rustup toolchain install nightly
   rustup component add rust-src --toolchain nightly
   cargo install ravedude
   ```

### Building & Running
Inside `rust/uno_blink/`:

```bash
cd rust/uno_blink

# Build release ELF binary
cargo +nightly build --Z build-std=core --target avr-specs/avr-atmega328p.json --release

# Flash using ravedude or avrdude
ravedude uno -P /dev/ttyUSB0 target/avr-atmega328p/release/uno_blink.elf
```

---

## 4. AVR Assembly Language Bare Metal Environment

### Overview
Assembly language programming gives absolute control over clock cycles, instruction
execution, and CPU register allocation. On the ATmega328P, instructions are executed
in 1 to 2 clock cycles at 16 MHz.

### Key Register Mapping (ATmega328P)
- **PB5 (Digital Pin 13):** Bit 5 of Port B.
- **DDRB (Data Direction Register B):** I/O Address `0x04` (RAM `0x24`). Setting Bit 5 high enables output mode.
- **PORTB (Data Register B):** I/O Address `0x05` (RAM `0x25`). Setting Bit 5 high sets pin voltage to 5V.

### Assembly Source Excerpt (`asm/uno_blink/uno_blink.asm`)
```assembly
#define __SFR_OFFSET 0
#include <avr/io.h>

.global main
main:
    sbi _SFR_IO_ADDR(DDRB), 5   ; Set PB5 output
loop:
    sbi _SFR_IO_ADDR(PORTB), 5  ; High
    rcall delay
    cbi _SFR_IO_ADDR(PORTB), 5  ; Low
    rcall delay
    rjmp loop
```

### Build Procedure via `avr-gcc` and `avrdude`
```bash
cd asm/uno_blink
make PORT=/dev/ttyUSB0
make PORT=/dev/ttyUSB0 flash
```

---

## 🌐 External Web References & Resources

### Datasheets & Architecture Manuals
- 📄 [Microchip ATmega328P Complete Datasheet](https://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-7810-Automotive-Microcontrollers-ATmega328P_Datasheet.pdf)
- 📄 [AVR Instruction Set Manual (DS40002198A)](https://ww1.microchip.com/downloads/en/DeviceDoc/AVR-InstructionSet-Manual-DS40002198A.pdf)
- 📄 [WCH CH340 USB-to-Serial Datasheet](http://www.wch-ic.com/downloads/CH340DS1_PDF.html)

### Toolchains & Frameworks
- 🔧 [Arduino CLI Official Documentation](https://arduino.github.io/arduino-cli/latest/)
- 🦀 [avr-hal / arduino-hal GitHub Repository](https://github.com/Rahix/avr-hal)
- 🐍 [MicroPython Official Documentation](https://docs.micropython.org/)
- ⚡ [usbipd-win Project (GitHub)](https://github.com/dorssel/usbipd-win)

<!-- file docs/arduino_environments.md ends -->
