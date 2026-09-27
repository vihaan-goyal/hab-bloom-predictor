/*
  fluoro_practice.ino -- practice light sensor with kit parts (before the TSL2591 arrives)
  ======================================================================================
  A blue LED shines through a cup of water onto a photoresistor. Each measurement reads the
  photoresistor with the LED OFF (dark) and ON (lit); `signal` compares the two, so steady room
  light mostly cancels out. With coloured water in the cup, less blue light gets through and the
  signal drops. A dilution series of green food colouring gives a calibration curve, the same
  procedure the real chlorophyll sensor will use.

  This Uno's analog header (A0-A5) broke off, so there are two ways to read the photoresistor:

  USE_ANALOG 1 -- analog, on A5 (hold a jumper pressed into the bare A5 hole while testing)
      5V -> photoresistor -> node;  node -> A5;  node -> 10k -> GND
      signal = lit - dark   (0-1023 counts; more light = higher)
  USE_ANALOG 0 -- digital timing, on D8 (no analog pins needed; breadboard_practice.png)
      5V -> photoresistor -> node;  node -> D8;  node -> 0.1 uF ("104") capacitor -> GND
      signal = dark_us / lit_us   (1.0 = LED adds nothing; more light = higher)

  Both:  D7 -> blue LED long leg; LED short leg -> 220 ohm -> GND.
  D2-D6, D9, D10 are the alerter's pins, untouched. Re-upload alerter_uno.ino afterwards.
  Serial Monitor at 115200. Commands: "r" = one reading, "a" = auto every 2 s (toggle).
*/
#define USE_ANALOG 1

const int PIN_LED = 7, PIN_A = A2, PIN_RC = 8;
const unsigned long TIMEOUT_US = 300000;  // digital mode: 0.3 s = "too dark"
bool autoMode = true;

float readAnalog() {                      // average of 20 readings, 0-1023
  long s = 0;
  for (int i = 0; i < 20; i++) { s += analogRead(PIN_A); delay(5); }
  return s / 20.0;
}

unsigned long chargeTime() {              // digital mode: time for the capacitor to charge
  pinMode(PIN_RC, OUTPUT);
  digitalWrite(PIN_RC, LOW);
  delay(5);
  pinMode(PIN_RC, INPUT);
  unsigned long t0 = micros();
  while (digitalRead(PIN_RC) == LOW) {
    if (micros() - t0 > TIMEOUT_US) return TIMEOUT_US;
  }
  return micros() - t0;
}

float readDigital() {                     // average of 8 charge times, microseconds
  unsigned long s = 0;
  for (int i = 0; i < 8; i++) s += chargeTime();
  return s / 8.0;
}

float readSensor() { return USE_ANALOG ? readAnalog() : readDigital(); }

void measure() {
  digitalWrite(PIN_LED, LOW);  delay(100); float dark = readSensor();
  digitalWrite(PIN_LED, HIGH); delay(100); float lit = readSensor();
  digitalWrite(PIN_LED, LOW);
  float signal = USE_ANALOG ? lit - dark : (lit > 0 ? dark / lit : 0);
  Serial.print(F("dark=")); Serial.print(dark, 1);
  Serial.print(F("  lit=")); Serial.print(lit, 1);
  Serial.print(F("  signal=")); Serial.println(signal, USE_ANALOG ? 1 : 3);
}

void setup() {
  pinMode(PIN_LED, OUTPUT);
  Serial.begin(115200);
  Serial.println(USE_ANALOG ? F("fluoro_practice ready (analog, A5).") : F("fluoro_practice ready (digital timing, D8)."));
  Serial.println(F("r = one reading, a = auto on/off"));
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    if (c == 'r') measure();
    if (c == 'a') { autoMode = !autoMode; Serial.println(autoMode ? F("auto ON") : F("auto OFF")); }
  }
  static unsigned long last = 0;
  if (autoMode && millis() - last > 2000) { last = millis(); measure(); }
}
