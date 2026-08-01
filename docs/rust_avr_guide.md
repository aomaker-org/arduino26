# Arduino26 Rust AVR Architecture & Implementation Guide

## Overview

This guide documents the Rust AVR embedded toolchain setup for Arduino Uno (ATmega328P, 16 MHz) integrated with `ard26`.

---

## Workspace Structure & Drivers

```text
rust/
├── uno_blink/           # Baseline AVR Blink implementation
├── ky015_naive/         # Imperative bit-banged KY-015 / DHT11 driver
└── ky015_idiomatic/     # Type-safe embedded-hal / dht-sensor driver
```

---

## 1. `rust/ky015_naive` — Imperative Bit-Banged Driver

- **File:** [rust/ky015_naive/src/main.rs](file:///home/fekerr/src/arduino26/rust/ky015_naive/src/main.rs)
- **Provenance / Attribution:** Direct port of classical Arduino C++ single-wire bit-banging protocol logic.
- **Key Characteristics:**
  - Direct single-pin output control via `into_output()` and `into_pull_up_input()`.
  - Precise delay loops (`arduino_hal::delay_us`) for measuring 40 data bits.
  - Verification checksum `(b0 + b1 + b2 + b3) & 0xFF == b4`.
  - Serial telemetry output over UART at **115200 baud**.

```bash
# Build & run naive Rust driver
ard26 run rust/ky015_naive
```

---

## 2. `rust/ky015_idiomatic` — Type-Safe Crate Architecture

- **File:** [rust/ky015_idiomatic/src/main.rs](file:///home/fekerr/src/arduino26/rust/ky015_idiomatic/src/main.rs)
- **Provenance / Attribution:** Constructed using `embedded-hal` drivers and the [`dht-sensor`](https://crates.io/crates/dht-sensor) crate abstractions.
- **Key Characteristics:**
  - Zero raw bit-banging in application code.
  - Strongly-typed `embedded-hal` pin abstractions.
  - Pattern matching on `Result<dht11::Reading, DhtError>` for clean error handling.

```bash
# Build & run idiomatic Rust driver
ard26 run rust/ky015_idiomatic
```

---

## Configuration & Target Specification

Rust AVR targets use the built-in `avr-none` target with `target-cpu=atmega328p`:

```toml
# .cargo/config.toml
[build]
target = "avr-none"
rustflags = ["-C", "target-cpu=atmega328p"]

[unstable]
build-std = ["core"]
```

---

## `ard26` CLI Integration

The `ard26` tool automatically recognizes Rust projects:
- **`ard26 compile <rust_dir>`**: Runs `cargo +nightly build -Z build-std=core --release`.
- **`ard26 upload <rust_dir>`**: Converts compiled ELF binary to Intel HEX using `avr-objcopy` and flashes to serial port via `avrdude`.
- **`ard26 monitor`**: Automatically scans `src/main.rs` for baud rate definitions and logs telemetry.

<!-- file docs/rust_avr_guide.md ends -->
