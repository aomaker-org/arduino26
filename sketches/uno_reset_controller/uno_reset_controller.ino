// file: sketches/uno_reset_controller/uno_reset_controller.ino
// Purpose: Hardware reset trigger controller for Leonardo via Uno Pin 7

const int RESET_PIN = 7;

void setup() {
  Serial.begin(115200);
  // Keep reset pin as INPUT (high impedance) so Leonardo operates normally
  pinMode(RESET_PIN, INPUT);
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    if (cmd == 'r') {
      Serial.println("[*] Pulling Leonardo RESET pin LOW...");
      pinMode(RESET_PIN, OUTPUT);
      digitalWrite(RESET_PIN, LOW);
      delay(150); // Hold reset for 150ms
      
      digitalWrite(RESET_PIN, HIGH);
      pinMode(RESET_PIN, INPUT); // Release reset pin to high impedance
      Serial.println("[+] Leonardo RESET released.");
    }
  }
}
// sketches/uno_reset_controller/uno_reset_controller.ino ends
