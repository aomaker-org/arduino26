// file: rust/uno_blink/src/main.rs
// SPDX-License-Identifier: MIT
// Purpose: Bare metal Rust blink for Arduino Uno (ATmega328P) using arduino-hal

#![no_std]
#![no_main]

use panic_halt as _;

#[arduino_hal::entry]
fn main() -> ! {
    let dp = arduino_hal::Peripherals::take().unwrap();
    let pins = arduino_hal::pins!(dp);

    let mut led = pins.d13.into_output();

    loop {
        led.toggle();
        arduino_hal::delay_ms(1000);
    }
}

// file rust/uno_blink/src/main.rs ends
