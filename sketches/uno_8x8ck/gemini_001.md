<!-- file: sketches/uno_8x8ck/gemini_001.md -->
```cpp
// Pins defined for matrix multiplexing
const uint8_t PINS[4] = {2, 3, 4, 5};

// Delay constants
const unsigned long ON_TIME_MS  = 1;
const unsigned long OFF_TIME_MS = 10;

void setup() {
  // Set all pins to INPUT (High-Impedance / Tri-state) initially
  for (uint8_t i = 0; i < 4; i++) {
    pinMode(PINS[i], INPUT);
  }
}

void loop() {
  // Iterate through source pins
  for (uint8_t srcIdx = 0; srcIdx < 4; srcIdx++) {
    // Iterate through sink pins
    for (uint8_t snkIdx = 0; snkIdx < 4; snkIdx++) {
      
      // Skip driving a pin against itself
      if (srcIdx == snkIdx) continue;

      uint8_t sourcePin = PINS[srcIdx];
      uint8_t sinkPin   = PINS[snkIdx];

      // 1. Configure active pair
      pinMode(sourcePin, OUTPUT);
      digitalWrite(sourcePin, HIGH); // Source current

      pinMode(sinkPin, OUTPUT);
      digitalWrite(sinkPin, LOW);   // Sink current

      // 2. Pulse ON for 1 ms
      delay(ON_TIME_MS);

      // 3. Return active pair to High Impedance
      digitalWrite(sourcePin, LOW);  // Disable internal pull-up/drive
      pinMode(sourcePin, INPUT);     // High-Z

      digitalWrite(sinkPin, LOW);
      pinMode(sinkPin, INPUT);       // High-Z

      // 4. Dead time OFF for 10 ms
      delay(OFF_TIME_MS);
    }
  }
}

```

### **How It Works**

* **Tri-Stating (High-Z):** Setting `pinMode(pin, INPUT)` while `digitalWrite(pin, LOW)` puts the pin into a high-impedance state, effectively disconnecting it from the circuit.
* **Charlieplexing Order:** The nested loops cycle through every directional combination of 2 pins out of the 4-pin array ($4 \times 3 = 12$ distinct states).
* **Safe State Transition:** Disabling the pin output before switching `pinMode` ensures no transient state activates internal pull-up resistors or leaves output drivers latched.

<!-- file sketches/uno_8x8ck/gemini_001.md ends -->
