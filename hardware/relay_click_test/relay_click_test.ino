/*
  relay_click_test.ino -- clicks the relay on D10 once a second (bench wiring check)
  ================================================================================
  D10 HIGH for 1 s, LOW for 1 s, forever. The blue LED on D5 mirrors it so you can see
  when the relay *should* be on. Serial Monitor at 115200 prints ON / OFF.

  Hear a click each second: the relay wiring is good; re-upload alerter_uno.ino.
  LED blinks but no click: the problem is between D10 and the relay (transistor, coil pins, diode).
*/
const int PIN_RELAY = 10, PIN_LED = 5;

void setup() {
  pinMode(PIN_RELAY, OUTPUT);
  pinMode(PIN_LED, OUTPUT);
  Serial.begin(115200);
  Serial.println(F("relay_click_test: D10 toggles every second"));
}

void loop() {
  digitalWrite(PIN_RELAY, HIGH); digitalWrite(PIN_LED, HIGH); Serial.println(F("ON"));
  delay(1000);
  digitalWrite(PIN_RELAY, LOW);  digitalWrite(PIN_LED, LOW);  Serial.println(F("OFF"));
  delay(1000);
}
