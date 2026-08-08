// file: sketches/uno_8x8ck/uno_8x8ck.ino
// Pins defined for matrix multiplexing
const uint8_t PINS[4] = {2, 3, 4, 5};

// Delay constants
const unsigned long ON_TIME_MS  = 200;
const unsigned long OFF_TIME_MS = 20;

void setup() {
  Serial.begin(115200);
  Serial.println(F("--- Arduino Uno 8x8 Matrix Pin Mapping Diagnostic ---"));

  // Set all pins to INPUT (High-Impedance / Tri-state) initially
  for (uint8_t i = 0; i < 4; i++) {
    pinMode(PINS[i], INPUT);
  }
}

void loop() {
  // Iterate through each pin as the single Source (HIGH)
  for (uint8_t srcIdx = 0; srcIdx < 4; srcIdx++) {
    uint8_t sourcePin = PINS[srcIdx];

    // For the remaining 3 pins, iterate through all 2^3 = 8 state combinations
    // representing whether they are active sinks (1) or Tri-state/High-Z (0)
    for (uint8_t stateMask = 1; stateMask < 8; stateMask++) {
      
      // Determine which pins are sinks in this permutation
      uint8_t sinkPins[3];
      uint8_t sinkCount = 0;
      uint8_t otherIdx = 0;

      for (uint8_t i = 0; i < 4; i++) {
        if (i == srcIdx) continue;
        // Check if the i-th pin's bit is active in the stateMask
        if ((stateMask >> otherIdx) & 0x01) {
          sinkPins[sinkCount++] = PINS[i];
        }
        otherIdx++;
      }

      // Print current state sequence
      Serial.print(F("D"));
      Serial.print(sourcePin);
      Serial.print(F(" -> ["));
      for (uint8_t s = 0; s < sinkCount; s++) {
        Serial.print(F("D"));
        Serial.print(sinkPins[s]);
        if (s < sinkCount - 1) Serial.print(F(", "));
      }
      Serial.println(F("]"));

      // 1. Configure the single Source pin
      pinMode(sourcePin, OUTPUT);
      digitalWrite(sourcePin, HIGH);

      // 2. Configure active Sink pins
      for (uint8_t s = 0; s < sinkCount; s++) {
        pinMode(sinkPins[s], OUTPUT);
        digitalWrite(sinkPins[s], LOW);
      }

      // 3. Pulse ON
      delay(ON_TIME_MS);

      // 4. Return all active pins to High-Z Tri-state
      digitalWrite(sourcePin, LOW);
      pinMode(sourcePin, INPUT);
      for (uint8_t s = 0; s < sinkCount; s++) {
        digitalWrite(sinkPins[s], LOW);
        pinMode(sinkPins[s], INPUT);
      }

      // 5. Dead time OFF
      delay(OFF_TIME_MS);
    }
  }
}

// file sketches/uno_8x8ck/uno_8x8ck.ino ends
