/*
 *   Sensor controller for Donkey car
 *                            2019/12/02
 *   Ver. 0.1  single VL53L1
 *   
 *   command: 'F': Full throttle
 *            'M': Medium
 *            'S': Slow
 *            'E': Emergency Stop
 */
#include <Wire.h>
#include <VL53L1X.h>
#define LED 13
#define Threshold_M  450  // mm
#define Threshold_S  250  // mm
#define Threshold_E   50  // mm

VL53L1X sensor;

void setup()
{
  Serial.begin(115200);
  Wire.begin();
  Wire.setClock(400000); // use 400 kHz I2C

  sensor.setTimeout(500);
  if (!sensor.init())
  {
    Serial.println("Failed to detect and initialize sensor!");
    while (1);
  }

  // long ... 50ms, medium ... 33ms, short ... 20ms
  sensor.setDistanceMode(VL53L1X::Short);
  sensor.setMeasurementTimingBudget(20000);

  // Start continuous readings at a rate of one measurement every 50 ms (the
  // inter-measurement period). This period should be at least as long as the
  // timing budget.
  sensor.startContinuous(50);

  pinMode(LED, OUTPUT);
}

void loop()
{
  int range;
  sensor.read();

  if(sensor.ranging_data.range_status == 0) {
    range = sensor.ranging_data.range_mm;

    if(range < Threshold_E) {
      Serial.write("E");
    } else {
      if(range < Threshold_S) {
        Serial.write("S");
      } else {
        if(range < Threshold_M) {
          Serial.write("M");
        } else {
          Serial.write("F");
        }
      }
    }      
  } else {
    Serial.write("F");  // out of range
  }
  delay(50);
}
