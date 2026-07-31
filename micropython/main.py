# file: micropython/main.py
# SPDX-License-Identifier: MIT
# Purpose: MicroPython / CircuitPython onboard blink loop for microcontrollers

import machine
import time

led = machine.Pin(13, machine.Pin.OUT)

print("==================================================")
print("  Arduino26 MicroPython / CircuitPython Ready     ")
print("==================================================")

while True:
    led.value(1)
    print("[+] LED state: HIGH")
    time.sleep(1)
    
    led.value(0)
    print("[+] LED state: LOW")
    time.sleep(1)

# file micropython/main.py ends
