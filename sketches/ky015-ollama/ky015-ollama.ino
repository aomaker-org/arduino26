#define DHT_PIN 2
#define MIN_INTERVAL 2000

struct SensorData {
  float humidity;
  float temperature;
};

enum State { STATE_IDLE, STATE_START_LOW, STATE_READ_DATA, STATE_COMPLETE, STATE_ERROR };

volatile uint32_t stateStartTime = 0;
volatile State currentState = STATE_IDLE;
volatile SensorData sensorData = {0.0, 0.0};
uint8_t dataBits[5] = {0};

void setup() {
  Serial.begin(115200);
  pinMode(DHT_PIN, OUTPUT);
  digitalWrite(DHT_PIN, HIGH);
  Serial.println(F("[+] DHT11 FSM Reader Initialized"));
}

void loop() {
  uint32_t now = millis();
  
  switch (currentState) {
    case STATE_IDLE:
      if (now - stateStartTime >= MIN_INTERVAL) {
        // Start trigger: pull pin LOW
        pinMode(DHT_PIN, OUTPUT);
        digitalWrite(DHT_PIN, LOW);
        stateStartTime = now;
        currentState = STATE_START_LOW;
      }
      break;
      
    case STATE_START_LOW:
      if (now - stateStartTime >= 18) {
        // End of start signal
        currentState = STATE_READ_DATA;
      }
      break;
      
    case STATE_READ_DATA: {
      // 1. Switch to input pullup and wait for response
      pinMode(DHT_PIN, INPUT_PULLUP);
      delayMicroseconds(30);
      
      uint32_t timeout = micros();
      while (digitalRead(DHT_PIN) == HIGH) {
        if (micros() - timeout > 100) {
          currentState = STATE_ERROR;
          return;
        }
      }
      
      timeout = micros();
      while (digitalRead(DHT_PIN) == LOW) {
        if (micros() - timeout > 100) {
          currentState = STATE_ERROR;
          return;
        }
      }
      
      timeout = micros();
      while (digitalRead(DHT_PIN) == HIGH) {
        if (micros() - timeout > 100) {
          currentState = STATE_ERROR;
          return;
        }
      }
      
      // 2. Read 40 bits
      for (int i = 0; i < 5; i++) {
        dataBits[i] = 0;
      }
      
      for (int i = 0; i < 40; i++) {
        timeout = micros();
        while (digitalRead(DHT_PIN) == LOW) {
          if (micros() - timeout > 100) {
            currentState = STATE_ERROR;
            return;
          }
        }
        
        uint32_t t_start = micros();
        while (digitalRead(DHT_PIN) == HIGH) {
          if (micros() - t_start > 150) {
            currentState = STATE_ERROR;
            return;
          }
        }
        uint32_t high_duration = micros() - t_start;
        
        uint8_t byte_idx = i / 8;
        dataBits[byte_idx] <<= 1;
        if (high_duration > 40) {
          dataBits[byte_idx] |= 1;
        }
      }
      
      // 3. Verify checksum
      uint8_t checksum = dataBits[0] + dataBits[1] + dataBits[2] + dataBits[3];
      if (checksum == dataBits[4] && (dataBits[0] != 0 || dataBits[2] != 0)) {
        sensorData.humidity = dataBits[0] + (dataBits[1] * 0.1f);
        sensorData.temperature = dataBits[2] + (dataBits[3] * 0.1f);
        currentState = STATE_COMPLETE;
      } else {
        currentState = STATE_ERROR;
      }
      break;
    }
    
    case STATE_COMPLETE: {
      float temp_f = (sensorData.temperature * 1.8f) + 32.0f;
      Serial.print(F("[+] Temp: "));
      Serial.print(sensorData.temperature, 1);
      Serial.print(F(" C ("));
      Serial.print(temp_f, 1);
      Serial.print(F(" F) | Hum: "));
      Serial.print(sensorData.humidity, 1);
      Serial.println(F(" %"));
      stateStartTime = millis();
      currentState = STATE_IDLE;
      break;
    }
      
    case STATE_ERROR:
      Serial.println(F("[!] Warning: Sensor read timeout or checksum error."));
      stateStartTime = millis();
      currentState = STATE_IDLE;
      break;
  }
}
