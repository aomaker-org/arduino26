// file: sketches/ky_1315_combo_000/ky_1315_combo_000.ino
// SPDX-License-Identifier: MIT
// Purpose: Combined KY-013 (Thermistor) & KY-015 (DHT11) Temperature Monitor
// Target MCU: Arduino Uno (ATmega328P)

#include <DHT.h>

#define DHTPIN 2       // KY-015 (DHT11) Signal connected to D2
#define DHTTYPE DHT11
#define THERMISTOR_PIN A0 // KY-013 Signal connected to A0

DHT dht(DHTPIN, DHTTYPE);

// Steinhart-Hart Coefficients for 10k NTC
const double A = 0.001129148;
const double B = 0.000234125;
const double C = 0.0000000876741;

double readThermistorC(int rawADC) {
  if (rawADC <= 0 || rawADC >= 1023) return NAN;
  double resistance = 10000.0 * ((1023.0 / (double)rawADC) - 1.0);
  double logR = log(resistance);
  double tempK = 1.0 / (A + (B * logR) + (C * logR * logR * logR));
  return tempK - 273.15;
}

void setup() {
  Serial.begin(115200);
  Serial.println(F("=========================================="));
  Serial.println(F("   KY-013 & KY-015 DUAL SENSOR BENCHMARK  "));
  Serial.println(F("=========================================="));
  dht.begin();
}

void loop() {
  // Poll every 2 seconds (enforces DHT11 sample rate)
  delay(2000);

  // 1. Read KY-015 (DHT11 Digital)
  float humidity = dht.readHumidity();
  float dhtTempC = dht.readTemperature();

  // 2. Read KY-013 (NTC Analog Thermistor)
  int rawADC = analogRead(THERMISTOR_PIN);
  double ntcTempC = readThermistorC(rawADC);

  Serial.println(F("--- Sensor Telemetry ---"));

  // KY-015 Output
  if (isnan(humidity) || isnan(dhtTempC)) {
    Serial.println(F("[KY-015 DHT11] Read Error!"));
  } else {
    Serial.print(F("[KY-015 DHT11] Humidity: "));
    Serial.print(humidity, 1);
    Serial.print(F("% | Temp: "));
    Serial.print(dhtTempC, 1);
    Serial.println(F(" °C"));
  }

  // KY-013 Output
  if (isnan(ntcTempC)) {
    Serial.println(F("[KY-013 NTC]   Read Error!"));
  } else {
    Serial.print(F("[KY-013 NTC]   ADC: "));
    Serial.print(rawADC);
    Serial.print(F(" | Temp: "));
    Serial.print(ntcTempC, 1);
    Serial.println(F(" °C"));
  }
}

// file sketches/ky_1315_combo_000/ky_1315_combo_000.ino ends
