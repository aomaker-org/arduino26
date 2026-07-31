// <!-- file: sketches/ky015_dht11/ky015_dht11.ino -->
// SPDX-License-Identifier: MIT
// Purpose: KY-015 / DHT11 Temperature & Humidity Sensor Reader for Arduino Uno
// Hardware: KY-015 "Blue Block" Sensor Module (DHT11 inside plastic grid housing)
// Wiring Note: Signal pin -> Digital Pin 2, VCC -> 5V, GND -> GND
// Kit Note: 37-in-1 sensor kits often mislabel or swap KY-013 (analog thermistor)
//           and KY-015 (digital DHT11 "blue block") in product envelopes.

#define DHT11_PIN 2

struct DHT11_Data {
  uint8_t humidity_int;
  uint8_t humidity_dec;
  uint8_t temp_int;
  uint8_t temp_dec;
  uint8_t checksum;
  bool valid;
};

// Standalone DHT11 bit-bang reader (no external library dependencies)
DHT11_Data readDHT11(uint8_t pin) {
  DHT11_Data result = {0, 0, 0, 0, 0, false};
  uint8_t data[5] = {0, 0, 0, 0, 0};

  // 1. Send Start Signal: Pull LOW for 18ms, then HIGH for 30us
  pinMode(pin, OUTPUT);
  digitalWrite(pin, LOW);
  delay(18);
  digitalWrite(pin, HIGH);
  delayMicroseconds(30);
  pinMode(pin, INPUT_PULLUP);

  // 2. Wait for DHT11 Response (LOW ~80us, then HIGH ~80us)
  uint32_t timeout = micros();
  while (digitalRead(pin) == HIGH) {
    if (micros() - timeout > 100) return result;
  }

  timeout = micros();
  while (digitalRead(pin) == LOW) {
    if (micros() - timeout > 100) return result;
  }

  timeout = micros();
  while (digitalRead(pin) == HIGH) {
    if (micros() - timeout > 100) return result;
  }

  // 3. Read 40 Bits (5 Bytes)
  for (int i = 0; i < 40; i++) {
    // Wait for bit start (LOW pulse ~50us)
    timeout = micros();
    while (digitalRead(pin) == LOW) {
      if (micros() - timeout > 100) return result;
    }

    // Measure HIGH pulse duration
    uint32_t t_start = micros();
    while (digitalRead(pin) == HIGH) {
      if (micros() - t_start > 150) return result;
    }
    uint32_t high_duration = micros() - t_start;

    // Pulse > 40us indicates bit '1', otherwise bit '0'
    uint8_t byte_idx = i / 8;
    data[byte_idx] <<= 1;
    if (high_duration > 40) {
      data[byte_idx] |= 1;
    }
  }

  // 4. Verify Checksum
  uint8_t sum = data[0] + data[1] + data[2] + data[3];
  if (sum == data[4] && (data[0] != 0 || data[2] != 0)) {
    result.humidity_int = data[0];
    result.humidity_dec = data[1];
    result.temp_int     = data[2];
    result.temp_dec     = data[3];
    result.checksum     = data[4];
    result.valid        = true;
  }

  return result;
}

void setup() {
  Serial.begin(115200);
  while (!Serial);

  delay(1000);
  Serial.println(F("=================================================="));
  Serial.println(F("  KY-015 / DHT11 Temperature & Humidity Reader    "));
  Serial.println(F("  Hardware: 'Blue Block' Sensor Module            "));
  Serial.println(F("=================================================="));
  Serial.println(F("Pin Connection: Signal -> Digital Pin 2 | VCC -> 5V | GND -> GND\n"));
}

void loop() {
  static unsigned long last_read = 0;

  // DHT11 requires at least 1-2 seconds between sampling cycles
  if (millis() - last_read >= 2000) {
    last_read = millis();

    DHT11_Data sensor = readDHT11(DHT11_PIN);

    if (sensor.valid) {
      float temp_c = sensor.temp_int + (sensor.temp_dec * 0.1f);
      float temp_f = (temp_c * 1.8f) + 32.0f;
      float humidity = sensor.humidity_int + (sensor.humidity_dec * 0.1f);

      Serial.print(F("[+] Humidity   : "));
      Serial.print(humidity, 1);
      Serial.println(F(" %RH"));

      Serial.print(F("[+] Temperature: "));
      Serial.print(temp_c, 1);
      Serial.print(F(" °C  ("));
      Serial.print(temp_f, 1);
      Serial.println(F(" °F)"));

      Serial.print(F("[+] Checksum   : 0x"));
      Serial.println(sensor.checksum, HEX);
      Serial.println(F("--------------------------------------------------"));
    } else {
      Serial.println(F("[!] Warning: Sensor read timeout or checksum error. Retrying..."));
    }
  }
}

// <!-- file sketches/ky015_dht11/ky015_dht11.ino ends -->
