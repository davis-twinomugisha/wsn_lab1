#include <Arduino.h>

// Pin Definitions for Arduino UNO R4 WiFi
#define NTC_PIN       A0   // KY-028 Analog Output (AO) for Temperature
#define LDR_PIN       A1   // 2-pin LDR + 10k resistor junction for Light
#define PIR_PIN       7    // PIR Motion Sensor
#define RED_LED_PIN   2    // High Temperature Warning LED
#define BUZZER_PIN    8    // Active Buzzer Signal Pin
#define NODE_ID       "UNO_R4_NODE_01"

// Buzzer Module Logic Setup
#define BUZZER_ACTIVE_STATE HIGH  

// Moving Average Filter Setup
const int FILTER_SIZE = 5;
float temp_history[FILTER_SIZE] = {24.0, 24.0, 24.0, 24.0, 24.0};
int filter_index = 0;

// Calibration against a reference thermometer (see data/calibration/, python/calibration.ipynb)
const float CAL_OFFSET = 0.95;   // sensor read 0.95 C low on average

// Tracking
float last_temp = 24.0;
unsigned long timestamp_sec = 0;

void setup() {
  Serial.begin(115200);
  
  // Configure UNO R4 ADC to 12-bit (0-4095 range)
  analogReadResolution(12);
  
  pinMode(PIR_PIN, INPUT);
  pinMode(NTC_PIN, INPUT);
  pinMode(LDR_PIN, INPUT);
  
  // Configure Actuators
  pinMode(RED_LED_PIN, OUTPUT);
  digitalWrite(RED_LED_PIN, LOW); // Start OFF
  
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, !BUZZER_ACTIVE_STATE); // Start OFF
  
  // CSV Header with Temperature and Motion Status Labels
  Serial.println("timestamp,temp,humidity,light,motion,temp_status,motion_status");
  delay(1000);
}

// Fixed Temperature Conversion for ~22-25°C room ambient
float readTemperature() {
  int analogValue = analogRead(NTC_PIN);
  
  if (analogValue <= 10 || analogValue >= 4085) return -999.0;
  
  float ratio = (float)analogValue / (4095.0 - (float)analogValue);
  if (ratio <= 0) return -999.0;

  // Calibrated room temperature scaling
  float celsius = 22.0 + (log(ratio) * 2.5);
  return celsius + CAL_OFFSET;   // apply calibration
}

// Moving average filter
float applyMovingAverage(float new_val) {
  if (new_val == -999.0) return last_temp; 

  temp_history[filter_index] = new_val;
  filter_index = (filter_index + 1) % FILTER_SIZE;

  float sum = 0;
  for (int i = 0; i < FILTER_SIZE; i++) {
    sum += temp_history[i];
  }
  return sum / FILTER_SIZE;
}

void loop() {
  timestamp_sec++;

  // 1. Acquire Sensor Signals
  float raw_temp = readTemperature();
  float filtered_temp = applyMovingAverage(raw_temp);
  if (raw_temp != -999.0) last_temp = filtered_temp;

  int ldr_adc = analogRead(LDR_PIN);
  float light_pct = ((float)ldr_adc / 4095.0) * 100.0;
  int motion = digitalRead(PIR_PIN);

  // Estimated Relative Humidity derived from ambient room conditions
  float estimated_humidity = 55.0 - ((filtered_temp - 22.0) * 1.2);
  if (estimated_humidity < 20.0) estimated_humidity = 20.0;
  if (estimated_humidity > 95.0) estimated_humidity = 95.0;

  // 2. Determine Temperature Status (LOW < 18.0°C, HIGH > 28.0°C)
  String temp_status = "TEMP_NORMAL";
  if (filtered_temp < 18.0) {
    temp_status = "TEMP_LOW";
  } else if (filtered_temp > 28.0) {
    temp_status = "TEMP_HIGH";
  }

  // 3. Determine Motion Status
  String motion_status = (motion == HIGH) ? "MOTION_DETECTED" : "NO_MOTION";

  // 4. Actuation Logic
  if (temp_status == "TEMP_HIGH") {
    digitalWrite(RED_LED_PIN, HIGH);                     // Red LED ON for HIGH TEMP
    digitalWrite(BUZZER_PIN, BUZZER_ACTIVE_STATE);       // Continuous Buzzer Alert
  } else if (motion == HIGH) {
    digitalWrite(RED_LED_PIN, LOW);
    digitalWrite(BUZZER_PIN, BUZZER_ACTIVE_STATE);       // Beep pulse for Motion
    delay(200);
    digitalWrite(BUZZER_PIN, !BUZZER_ACTIVE_STATE);
  } else {
    digitalWrite(RED_LED_PIN, LOW);                      // LED OFF
    digitalWrite(BUZZER_PIN, !BUZZER_ACTIVE_STATE);      // Silence Buzzer
  }

  // 5. Output CSV Stream
  Serial.print(timestamp_sec);
  Serial.print(",");
  Serial.print(filtered_temp, 1);
  Serial.print(",");
  Serial.print(estimated_humidity, 1);
  Serial.print(",");
  Serial.print(light_pct, 2);
  Serial.print(",");
  Serial.print(motion);
  Serial.print(",");
  Serial.print(temp_status);
  Serial.print(",");
  Serial.println(motion_status);

  delay(1000); 
}
