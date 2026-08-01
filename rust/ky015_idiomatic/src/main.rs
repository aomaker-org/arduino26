// file: rust/ky015_idiomatic/src/main.rs
// SPDX-License-Identifier: MIT
// Purpose: Idiomatic / Type-Safe Rust Driver for KY-015 / DHT11 Sensor
// Provenance: Idiomatic Rust embedded-hal abstraction with Result<Reading, DhtError>
// Target MCU: ATmega328P (16 MHz) | Pin: D2 | Baud Rate: 115200

#![no_std]
#![no_main]

use panic_halt as _;
use ufmt::uwriteln;
use dht_sensor::*;

#[arduino_hal::entry]
fn main() -> ! {
    let dp = arduino_hal::Peripherals::take().unwrap();
    let pins = arduino_hal::pins!(dp);

    let mut serial = arduino_hal::default_serial!(dp, pins, 115200);
    let mut delay = arduino_hal::Delay::new();

    let _ = uwriteln!(serial, "=======================================");
    let _ = uwriteln!(serial, "KY-015 / DHT11 Idiomatic Rust Driver");
    let _ = uwriteln!(serial, "=======================================");

    let mut d2 = pins.d2.into_opendrain_high();

    loop {
        arduino_hal::delay_ms(2000);

        // Idiomatic embedded-hal driver call returning Result<Reading, DhtError>
        match dht11::Reading::read(&mut delay, &mut d2) {
            Ok(reading) => {
                let temp_f = (reading.temperature as i16 * 9 / 5) + 32;
                let _ = uwriteln!(
                    serial,
                    "Humidity: {}% | Temp: {} C ({} F)",
                    reading.relative_humidity,
                    reading.temperature,
                    temp_f
                );
            }
            Err(DhtError::Timeout) => {
                let _ = uwriteln!(serial, "[!] Error: Sensor Timeout");
            }
            Err(DhtError::ChecksumMismatch) => {
                let _ = uwriteln!(serial, "[!] Error: Checksum Mismatch");
            }
        }
    }
}

// file rust/ky015_idiomatic/src/main.rs ends
