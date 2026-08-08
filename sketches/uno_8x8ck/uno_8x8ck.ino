// file: sketches/uno_8x8ck/uno_8x8ck.ino
// Pins defined for matrix multiplexing
const uint8_t PINS[4] = {2, 3, 4, 5};

// Delay constants
const unsigned long ON_TIME_MS  = 400;
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
  // Generate all 3^4 = 81 state permutations for the 4 pins
  // Pin states: 0 = Tri-state (INPUT), 1 = Source (OUTPUT HIGH), 2 = Sink (OUTPUT LOW)
  for (uint8_t stateVal = 0; stateVal < 81; stateVal++) {
    uint8_t pinStates[4]; // 0=Tri, 1=Src, 2=Snk
    uint8_t temp = stateVal;
    
    uint8_t srcCount = 0;
    uint8_t snkCount = 0;

    for (uint8_t i = 0; i < 4; i++) {
      pinStates[i] = temp % 3;
      temp /= 3;
      if (pinStates[i] == 1) srcCount++;
      if (pinStates[i] == 2) snkCount++;
    }

    // Filter: must have 1-3 sources AND 1-3 sinks (e.g. at least one of each)
    if (srcCount < 1 || srcCount > 3 || snkCount < 1 || snkCount > 3) {
      continue;
    }

    // Print current state configuration
    Serial.print(F("["));
    bool firstSrc = true;
    for (uint8_t i = 0; i < 4; i++) {
      if (pinStates[i] == 1) {
        if (!firstSrc) Serial.print(F(", "));
        Serial.print(F("D"));
        Serial.print(PINS[i]);
        firstSrc = false;
      }
    }
    Serial.print(F("] -> ["));
    bool firstSnk = true;
    for (uint8_t i = 0; i < 4; i++) {
      if (pinStates[i] == 2) {
        if (!firstSnk) Serial.print(F(", "));
        Serial.print(F("D"));
        Serial.print(PINS[i]);
        firstSnk = false;
      }
    }
    Serial.println(F("]"));

    // 1. Configure Pin Modes & Outputs
    for (uint8_t i = 0; i < 4; i++) {
      if (pinStates[i] == 1) {
        pinMode(PINS[i], OUTPUT);
        digitalWrite(PINS[i], HIGH);
      } else if (pinStates[i] == 2) {
        pinMode(PINS[i], OUTPUT);
        digitalWrite(PINS[i], LOW);
      } else {
        pinMode(PINS[i], INPUT);
      }
    }

    // 2. Pulse ON
    delay(ON_TIME_MS);

    // 3. Reset all to High-Z Tri-state
    for (uint8_t i = 0; i < 4; i++) {
      digitalWrite(PINS[i], LOW);
      pinMode(PINS[i], INPUT);
    }

    // 4. Dead time OFF
    delay(OFF_TIME_MS);
  }
}

// file sketches/uno_8x8ck/uno_8x8ck.ino ends
