// file: rust/ky015_naive/src/main.rs
// SPDX-License-Identifier: MIT
// Purpose: Naive / Imperative Bit-Banged KY-015 / DHT11 Driver for Arduino Uno
// Provenance: Direct port of classical Arduino C++ single-wire bit-banging protocol
// Target MCU: ATmega328P (16 MHz) | Pin: D2 | Baud Rate: 115200

#![no_std]
#![no_main]

use panic_halt as _;
use ufmt::uwriteln;

#[arduino_hal::entry]
fn main() -> ! {
    let dp = arduino_hal::Peripherals::take().unwrap();
    let pins = arduino_hal::pins!(dp);

    let mut serial = arduino_hal::default_serial!(dp, pins, 115200);

    let _ = uwriteln!(serial, "=======================================");
    let _ = uwriteln!(serial, "KY-015 / DHT11 Naive Bit-Bang Rust Driver");
    let _ = uwriteln!(serial, "=======================================");

    let mut d2 = pins.d2.into_output().downgrade();

    loop {
        // DHT11 requires 1 to 2 seconds between measurements
        arduino_hal::delay_ms(2000);

        // 1. Host Send Start Signal: Pull D2 LOW for >= 18ms
        let mut d2_out = d2.into_output();
        d2_out.set_low();
        arduino_hal::delay_ms(20);

        // Pull HIGH for 40us, then switch to input_pullup
        d2_out.set_high();
        arduino_hal::delay_us(40);

        let d2_in = d2_out.into_pull_up_input();

        // 2. Wait for sensor response (LOW ~80us, HIGH ~80us)
        let mut data = [0u8; 5];

        // Wait for initial response LOW -> HIGH transition
        let mut timeout = 1000;
        while d2_in.is_low() && timeout > 0 {
            arduino_hal::delay_us(1);
            timeout -= 1;
        }
        timeout = 1000;
        while d2_in.is_high() && timeout > 0 {
            arduino_hal::delay_us(1);
            timeout -= 1;
        }

        // 3. Read 40 Bits (5 Bytes)
        let mut success = true;
        for i in 0..40 {
            // Wait for pin to go HIGH
            let mut low_cycles = 0;
            while d2_in.is_low() && low_cycles < 200 {
                arduino_hal::delay_us(1);
                low_cycles += 1;
            }

            // Measure HIGH pulse duration
            let mut high_cycles = 0;
            while d2_in.is_high() && high_cycles < 200 {
                arduino_hal::delay_us(1);
                high_cycles += 1;
            }

            if low_cycles >= 200 || high_cycles >= 200 {
                success = false;
                break;
            }

            // High pulse > 40us indicates a '1' bit; <= 40us indicates '0'
            let byte_idx = i / 8;
            data[byte_idx] <<= 1;
            if high_cycles > 40 {
                data[byte_idx] |= 1;
            }
        }

        // Restore pin state for next loop
        d2 = d2_in.into_output().downgrade();

        if !success {
            let _ = uwriteln!(serial, "[X] Read Error: Sensor timeout / no response");
            continue;
        }

        // 4. Verify Checksum: (Byte0 + Byte1 + Byte2 + Byte3) & 0xFF == Byte4
        let checksum = (data[0] as u16 + data[1] as u16 + data[2] as u16 + data[3] as u16) as u8;
        if checksum != data[4] {
            let _ = uwriteln!(
                serial,
                "[!] Checksum Mismatch! Calc: {} vs Recv: {}",
                checksum,
                data[4]
            );
        } else {
            let humidity = data[0];
            let temp_c = data[2];
            let temp_f = (temp_c as u16 * 9 / 5) + 32;

            let _ = uwriteln!(
                serial,
                "Humidity: {}% | Temp: {} C ({} F)",
                humidity,
                temp_c,
                temp_f
            );
        }
    }
}

// file rust/ky015_naive/src/main.rs ends
