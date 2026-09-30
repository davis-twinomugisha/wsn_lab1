/*
 * WSN Lab 1 - Multi-Sensor Edge Node (Wokwi simulation)
 * ESP32 + DHT22 (temp/humidity) + photoresistor module (light) + PIR (motion)
 * + LED (high-temperature indicator) + buzzer (event alert)
 *
 * CSV columns (one row per second):
 *   timestamp,temp,humidity,light,motion,temp_cal,temp_filt,delta_temp,light_pct,valid,event,status
 *
 *   timestamp  - milliseconds since start
 *   temp       - raw DHT22 temperature (C)
 *   humidity   - raw DHT22 humidity (%)
 *   light      - raw ADC value from the photoresistor AO pin (0-4095)
 *   motion     - PIR output (0/1)
 *   temp_cal   - calibrated temperature (slope * temp + offset)
 *   temp_filt  - 5-sample moving average of temp_cal
 *   delta_temp - rate of change of temp_filt per sample
 *   light_pct  - brightness 0-100 %
 *   valid      - 1 if the readings passed the plausibility check
 *   event      - 1 on the sample where a NEW event starts (high temp or motion)
 *   status     - INVALID / HIGH_TEMP / MOTION / NORMAL
 */

#include <DHT.h>

// ---------------- Pins ----------------
#define DHT_PIN    4
#define DHT_TYPE   DHT22
#define LDR_PIN    34   // photoresistor AO pin (analog). NOT the DO pin.
#define PIR_PIN    27
#define LED_PIN    26   // on while status == HIGH_TEMP
#define BUZZER_PIN 25   // on while motion is detected

DHT dht(DHT_PIN, DHT_TYPE);

// ---------------- Sampling (1 Hz) ----------------
const unsigned long SAMPLE_MS = 1000;
unsigned long nextSampleMs = 0;

// ---------------- Calibration (fill in from calibration.ipynb) ----------------
const float CAL_SLOPE  = 1.0;
const float CAL_OFFSET = 0.0;

// ---------------- High-temperature alarm ----------------
const float TEMP_HIGH  = 28.0;   // alarm ON above 28 C
const float TEMP_CLEAR = 27.5;   // alarm OFF only when back below this (stops flickering)
bool highTemp = false;

// ---------------- Plausible ranges (DHT22 datasheet) ----------------
const float TEMP_MIN = -40.0, TEMP_MAX = 80.0;
const float HUM_MIN  =   0.0, HUM_MAX  = 100.0;

// ---------------- Light direction ----------------
// On the photoresistor module, the AO voltage FALLS as light increases,
// so brightness = 100 - raw %. If dragging the Wokwi slider to "bright"
// makes light_pct go DOWN, change this to false.
const bool LIGHT_INVERT = true;

// ---------------- Moving average (5 samples) ----------------
const int FILTER_SIZE = 5;
float filterBuf[FILTER_SIZE];
int filterIndex = 0;
int filterCount = 0;

float movingAverage(float x) {
  filterBuf[filterIndex] = x;
  filterIndex = (filterIndex + 1) % FILTER_SIZE;
  if (filterCount < FILTER_SIZE) filterCount++;
  float sum = 0;
  for (int i = 0; i < filterCount; i++) sum += filterBuf[i];
  return sum / filterCount;
}

float lastFilt = NAN;
bool  lastHighTemp = false;
int   lastMotion = LOW;

void setup() {
  Serial.begin(115200);
  dht.begin();
  pinMode(PIR_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  digitalWrite(BUZZER_PIN, LOW);

  Serial.println("timestamp,temp,humidity,light,motion,temp_cal,temp_filt,delta_temp,light_pct,valid,event,status");
  nextSampleMs = millis() + SAMPLE_MS;
}

void loop() {
  // Wait for the next 1-second tick
  if ((long)(millis() - nextSampleMs) < 0) return;
  nextSampleMs += SAMPLE_MS;
  unsigned long timestamp = millis();

  // 1. Acquire
  float temp     = dht.readTemperature();
  float humidity = dht.readHumidity();
  int   light    = analogRead(LDR_PIN);                 // 0-4095
  int   motion   = digitalRead(PIR_PIN);

  float lightPct = light / 4095.0 * 100.0;
  if (LIGHT_INVERT) lightPct = 100.0 - lightPct;

  // 2. Validate the RAW readings
  bool valid = !isnan(temp) && !isnan(humidity) &&
               temp >= TEMP_MIN && temp <= TEMP_MAX &&
               humidity >= HUM_MIN && humidity <= HUM_MAX;

  // 3. Calibrate, filter, rate of change (only on valid readings)
  float tempCal = NAN, tempFilt = NAN, deltaTemp = 0.0;
  if (valid) {
    tempCal  = CAL_SLOPE * temp + CAL_OFFSET;
    tempFilt = movingAverage(tempCal);
    if (!isnan(lastFilt)) deltaTemp = tempFilt - lastFilt;
    lastFilt = tempFilt;

    // High-temperature decision with a 0.5 C buffer
    if (!highTemp && tempFilt > TEMP_HIGH)       highTemp = true;
    else if (highTemp && tempFilt < TEMP_CLEAR)  highTemp = false;
  }

  // 4. Events: count only the START of each high-temp spell or motion
  bool newHighTemp = valid && highTemp && !lastHighTemp;
  bool newMotion   = (motion == HIGH) && (lastMotion == LOW);
  int  event = (newHighTemp || newMotion) ? 1 : 0;
  if (valid) lastHighTemp = highTemp;
  lastMotion = motion;

  // 5. Status
  String status = "NORMAL";
  if (!valid)              status = "INVALID";
  else if (highTemp)       status = "HIGH_TEMP";
  else if (motion == HIGH) status = "MOTION";

  // 6. Local indicators
  digitalWrite(LED_PIN,    (valid && highTemp) ? HIGH : LOW);
  digitalWrite(BUZZER_PIN, motion == HIGH ? HIGH : LOW);

  // 7. CSV row
  Serial.print(timestamp);     Serial.print(',');
  Serial.print(temp, 2);       Serial.print(',');
  Serial.print(humidity, 2);   Serial.print(',');
  Serial.print(light);         Serial.print(',');
  Serial.print(motion);        Serial.print(',');
  Serial.print(tempCal, 2);    Serial.print(',');
  Serial.print(tempFilt, 2);   Serial.print(',');
  Serial.print(deltaTemp, 2);  Serial.print(',');
  Serial.print(lightPct, 1);   Serial.print(',');
  Serial.print(valid ? 1 : 0); Serial.print(',');
  Serial.print(event);         Serial.print(',');
  Serial.println(status);
}
