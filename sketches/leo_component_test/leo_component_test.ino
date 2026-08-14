// <!-- file: sketches/leo_component_test/leo_component_test.ino -->
// SPDX-License-Identifier: MIT
// Purpose: Simple Leonardo component tester sketch for identifying resistors / diodes

#ifndef LED_BUILTIN
#define LED_BUILTIN 13
#endif

// Define pins for 3-pin test network (A0, A1, A2 used for ADC sensing and driving)
const int testPins[3] = {A0, A1, A2};

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200);
  while (!Serial) {
    ; // Wait for serial port to connect (needed for native USB Leonardo)
  }
  Serial.println("==================================================");
  Serial.println("  Arduino Leonardo - Component Identification Ready");
  Serial.println("==================================================");
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH);
  
  // Basic analog reads across the probe network as a diagnostic run
  int val0 = analogRead(A0);
  int val1 = analogRead(A1);
  int val2 = analogRead(A2);
  
  Serial.print("{\"A0\": ");
  Serial.print(val0);
  Serial.print(", \"A1\": ");
  Serial.print(val1);
  Serial.print(", \"A2\": ");
  Serial.print(val2);
  Serial.println("}");
  
  digitalWrite(LED_BUILTIN, LOW);
  delay(1000);
}

// <!-- file sketches/leo_component_test/leo_component_test.ino ends -->
