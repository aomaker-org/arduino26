// file: sketches/ky_013_000/ky_013_000.ino
// SPDX-License-Identifier: MIT
// Purpose: KY-013 Analog NTC Thermistor Temperature Sensor Example
// Target MCU: Arduino Uno (ATmega328P)

/*
  KY-013 Analog Temperature Sensor Example
  Uses Steinhart-Hart equation for thermistor conversion.
  Wiring:
    S (Signal) -> A0
    Middle (+)  -> 5V
    - (GND)     -> GND
*/

#define THERMISTOR_PIN A0

// Steinhart-Hart Coefficients for standard 10k NTC Thermistor
const double A = 0.001129148;
const double B = 0.000234125;
const double C = 0.0000000876741;

double readTemperatureCelsius(int rawADC) {
  // Prevent division by zero if pin is floating/shorted
  if (rawADC <= 0 || rawADC >= 1023) return NAN;

  // Calculate thermistor resistance (R2) in voltage divider: R2 = R1 * (1023 / ADC - 1)
  double resistance = 10000.0 * ((1023.0 / (double)rawADC) - 1.0);
  double logR = log(resistance);

  // Steinhart-Hart Equation: 1 / T = A + B*ln(R) + C*(ln(R))^3
  double tempK = 1.0 / (A + (B * logR) + (C * logR * logR * logR));
  return tempK - 273.15; // Convert Kelvin to Celsius
}

void setup() {
  Serial.begin(115200);
  Serial.println(F("KY-013 Thermistor Sensor Test Starting..."));
}

void loop() {
  delay(1000);

  int rawValue = analogRead(THERMISTOR_PIN);
  double tempC = readTemperatureCelsius(rawValue);
  double tempF = (tempC * 9.0 / 5.0) + 32.0;

  if (isnan(tempC)) {
    Serial.println(F("Failed to read thermistor! Check wiring on pin A0."));
    return;
  }

  Serial.print(F("Raw ADC: "));
  Serial.print(rawValue);
  Serial.print(F(" | Temp: "));
  Serial.print(tempC, 1);
  Serial.print(F(" °C  ("));
  Serial.print(tempF, 1);
  Serial.println(F(" °F)"));
}

// file sketches/ky_013_000/ky_013_000.ino ends
