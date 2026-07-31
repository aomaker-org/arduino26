// <!-- file: sketches/ky_015_000/ky_015_000.ino -->
// SPDX-License-Identifier: MIT
// Purpose: KY-015 / DHT11 Temperature & Humidity Sensor Example (Adafruit DHT Library)
// Target MCU: Arduino Uno (ATmega328P)

/*
  DHT11 Temperature & Humidity Sensor Example
  Requires Adafruit's "DHT sensor library"
*/

#include <DHT.h>

#define DHTPIN 2       // Digital pin connected to the DHT sensor signal pin
#define DHTTYPE DHT11  // Define sensor model as DHT11

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  Serial.println(F("DHT11 Sensor Test Starting..."));
  dht.begin();
}

void loop() {
  // Wait 2 seconds between measurements (DHT11 is slow to update)
  delay(2000);

  // Read relative humidity (%) and temperature (°C / °F)
  float h = dht.readHumidity();
  float t = dht.readTemperature();         // Celsius
  float f = dht.readTemperature(true);     // Fahrenheit

  // Check if any reads failed and exit early (to try again)
  if (isnan(h) || isnan(t) || isnan(f)) {
    Serial.println(F("Failed to read from DHT sensor! Check digital pin wiring and power."));
    return;
  }

  Serial.print(F("Humidity: "));
  Serial.print(h, 1);
  Serial.print(F("%  |  Temp: "));
  Serial.print(t, 1);
  Serial.print(F(" °C  ("));
  Serial.print(f, 1);
  Serial.println(F(" °F)"));
}

// <!-- file sketches/ky_015_000/ky_015_000.ino ends -->
