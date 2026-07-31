// <!-- file: sketches/uno_clone_diag/uno_clone_diag.ino -->
// SPDX-License-Identifier: MIT
// Purpose: Uno Clone Hardware Diagnostics & Internal Register Inspection
// Target MCU: ATmega328P / ATmega168 (Arduino Uno Clone via CH340 USB-Serial)

#include <avr/boot.h>
#include <avr/pgmspace.h>

extern char *__brkval;
extern char __heap_start;

// Calculate current free SRAM (space between heap end and stack top)
int getFreeRam() {
  int free_memory;
  if ((int)__brkval == 0) {
    free_memory = ((int)&free_memory) - ((int)&__heap_start);
  } else {
    free_memory = ((int)&free_memory) - ((int)__brkval);
  }
  return free_memory;
}

// Measure internal VCC via 1.1V Bandgap Reference
long readVcc() {
  // Read 1.1V reference against AVcc
  #if defined(__AVR_ATmega328P__) || defined(__AVR_ATmega168__)
    ADMUX = _BV(REFS0) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
  #elif defined(__AVR_ATmega328__)
    ADMUX = _BV(REFS0) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
  #endif

  delay(2); // Wait for VREF to settle
  ADCSRA |= _BV(ADSC); // Start conversion
  while (bit_is_set(ADCSRA, ADSC));

  uint8_t low  = ADCL;
  uint8_t high = ADCH;
  long result = (high << 8) | low;

  // Calculate Vcc (in mV); 1125300 = 1.1*1023*1000
  result = 1125300L / result; 
  return result;
}

void setup() {
  Serial.begin(115200);
  while (!Serial); // Wait for serial connection

  delay(500);
  Serial.println(F("\n======================================="));
  Serial.println(F("    UNO CLONE HARDWARE DIAGNOSTICS     "));
  Serial.println(F("======================================="));

  // 1. MCU Architecture Info
  Serial.print(F("F_CPU Clock Speed : "));
  Serial.print(F_CPU / 1000000UL);
  Serial.println(F(" MHz"));

  // 2. Read Chip Signature Bytes directly from Fuse Space
  Serial.print(F("Device Signature  : "));
  uint8_t sig0 = boot_signature_byte_get(0x0000);
  uint8_t sig1 = boot_signature_byte_get(0x0002);
  uint8_t sig2 = boot_signature_byte_get(0x0004);

  Serial.print(F("0x")); Serial.print(sig0, HEX); Serial.print(F(" "));
  Serial.print(F("0x")); Serial.print(sig1, HEX); Serial.print(F(" "));
  Serial.print(F("0x")); Serial.print(sig2, HEX); Serial.println();

  // Validate standard ATmega328P signature
  if (sig0 == 0x1E && sig1 == 0x95 && sig2 == 0x0F) {
    Serial.println(F("Target Verification: Genuine / Compatible ATmega328P detected."));
  } else if (sig0 == 0x1E && sig1 == 0x94 && sig2 == 0x0B) {
    Serial.println(F("Target Verification: ATmega168P detected."));
  } else {
    Serial.println(F("Target Verification: Non-standard MCU or counterfeit core!"));
  }

  // 3. SRAM Assessment
  Serial.print(F("Available Free RAM: "));
  Serial.print(getFreeRam());
  Serial.println(F(" Bytes"));

  // 4. Power Rail Telemetry
  Serial.print(F("VCC Rail Voltage  : "));
  Serial.print(readVcc() / 1000.0, 3);
  Serial.println(F(" V"));

  // 5. Timer Configuration Telemetry
  Serial.print(F("Timer0 Prescaler  : "));
  Serial.println(TCCR0B & 0x07); // Shows clock source scaling for millis()

  Serial.println(F("======================================="));
  Serial.println(F("Diagnostics Complete. Awaiting Commands..."));
}

void loop() {
  // Heartbeat loop
  static unsigned long last_tick = 0;
  if (millis() - last_tick > 5000) {
    last_tick = millis();
    Serial.print(F("[Heartbeat] VCC: "));
    Serial.print(readVcc() / 1000.0, 2);
    Serial.print(F("V | Free RAM: "));
    Serial.print(getFreeRam());
    Serial.println(F("B"));
  }
}

// <!-- file sketches/uno_clone_diag/uno_clone_diag.ino ends -->
