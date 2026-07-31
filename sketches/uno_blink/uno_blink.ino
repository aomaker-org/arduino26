// <!-- file: sketches/uno_blink/uno_blink.ino -->
// SPDX-License-Identifier: MIT
// Purpose: Standard Arduino C++ Blink & Serial Hello World for Uno (ATmega328P)

#ifndef LED_BUILTIN
#define LED_BUILTIN 13
#endif

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200);
  while (!Serial) {
    ; // Wait for serial port to connect (needed for native USB)
  }
  Serial.println("==================================================");
  Serial.println("  Arduino26 - Uno Clone (ATmega328P + CH340) Ready");
  Serial.println("==================================================");
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH);
  Serial.println("[+] LED status: HIGH");
  delay(1000);
  
  digitalWrite(LED_BUILTIN, LOW);
  Serial.println("[+] LED status: LOW");
  delay(1000);
}

// <!-- file sketches/uno_blink/uno_blink.ino ends -->
