# file: micropython/ky015_dht11.py
# SPDX-License-Identifier: MIT
# Purpose: MicroPython driver for KY-015 / DHT11 Temperature & Humidity Sensor
# Target Devices: ESP32, Raspberry Pi Pico (RP2040), Pyboard, or MicroPython boards
# Hardware: Signal -> Pin D2 / GPIO2 | VCC -> 3.3V/5V | GND -> GND

import time

import dht
from machine import Pin

# Define DHT11 signal pin (e.g., GPIO2 or Pin 2)
sensor_pin = Pin(2, Pin.IN, Pin.PULL_UP)
sensor = dht.DHT11(sensor_pin)

print("==================================================")
print("  KY-015 / DHT11 MicroPython Telemetry Monitor    ")
print("==================================================")

while True:
    try:
        time.sleep(2)
        sensor.measure()
        temp_c = sensor.temperature()
        humidity = sensor.humidity()
        temp_f = (temp_c * 9 / 5) + 32
        print(f"[+] Humidity   : {humidity:.1f} %RH")
        print(f"[+] Temperature: {temp_c:.1f} °C ({temp_f:.1f} °F)")
        print("--------------------------------------------------")
    except OSError as e:
        print(f"[!] Read Error: {e}")

# file micropython/ky015_dht11.py ends
