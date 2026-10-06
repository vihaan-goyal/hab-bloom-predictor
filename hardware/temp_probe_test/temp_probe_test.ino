/*
  temp_probe_test.ino -- DS18B20 waterproof temperature probe check
  ==================================================================
  Wiring: red -> 5V, blue (or black) -> GND, yellow -> D8, and a 4.7 kOhm resistor between D8 and 5V.
  Needs the "OneWire" and "DallasTemperature" libraries.
  Serial Monitor at 115200. Every second it prints how many probes it found and the temperature.

  "probes found: 0"  -> the board can't see the probe: check yellow is in the D8 row with the resistor,
                        the resistor's other leg is on 5V, and red/blue reach 5V/GND.
  "-127" / "no reading" -> found once but lost contact: a loose wire (wiggle test).
  Re-upload alerter_uno.ino afterwards (it expects the probe on D3).
*/
#include <OneWire.h>
#include <DallasTemperature.h>

const int PIN_PROBE = 8;
OneWire oneWire(PIN_PROBE);
DallasTemperature sensors(&oneWire);

void setup() {
  Serial.begin(115200);
  sensors.begin();
  Serial.println(F("temp_probe_test: DS18B20 on D8"));
}

void loop() {
  sensors.setResolution(12);
  Serial.print(F("res=")); Serial.print(sensors.getResolution()); Serial.print(F("  "));
  sensors.begin();                                  // re-scan so a fixed wire is picked up live
  int n = sensors.getDeviceCount();
  Serial.print(F("probes found: ")); Serial.print(n);
  if (n > 0) {
    sensors.requestTemperatures();
    float t = sensors.getTempCByIndex(0);
    if (t <= -100) Serial.print(F("   no reading (-127): loose wire?"));
    else { Serial.print(F("   temp = ")); Serial.print(t, 2); Serial.print(F(" C")); }
  } else {
    Serial.print(F("   check wiring (see top of sketch)"));
  }
  Serial.println();
  delay(1);
}
