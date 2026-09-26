/*
  alerter_uno.ino -- the forecast-triggered ON/OFF loop on an Arduino Uno (one tank)
  ==================================================================================
  Same rules as src/sim/loop_controller.py (Controller.step, n = 1) and
  notes/mitigation/00_CONTROL_LOOP.md:

    not ON:  start if the trigger fires today; next check = today + X; remember today's chl.
    ON:      on a check day with no reading, check again tomorrow;
             OFF if  p < T_off (= 0.8 T_on)  AND  chl < C_ok  AND  chl <= chl at the last check;
             else STOP if ON for >= MAX_ON (= 4 X) days; else next check = today + X.
    The OFF day itself counts as ON; the tank can restart the next day.

  Triggers:  mode F (forecast)  p >= T_on
             mode R (rule)      chl rose 2 days in a row AND chl > 2 x warm-up mean

  Input, one line per day in the Serial Monitor (115200 baud, "Newline"):
      <day> <p> <chl>          e.g.  12 0.63 7.4      (use - for a missing value)
  Commands:
      x <days>   cok <ug/L>   ton <p>   mode F|R   warm <mean chl>
      stop       (safety stop: OFF at the next daily line, e.g. DO kit < 4 mg/L)
      status     reset

  Outputs:  green LED = idle, blue LED + relay = treatment ON,
            white LED = warning (safety stop, temperature out of range, missed reading),
            buzzer: 3 beeps = ON, 1 long = OFF, fast beeps = temperature alarm.

  Wiring: hardware/alerter_uno/README.md.
*/
#include <math.h>

#define USE_DS18B20 0   // 1 once the DS18B20 is wired (needs OneWire + DallasTemperature libraries)
#if USE_DS18B20
#include <OneWire.h>
#include <DallasTemperature.h>
#endif

// Pins match the circuito.io wiring diagram (hardware/alerter_uno/README.md)
// (circuito's yellow LED = our white warning LED; the relay is not in the circuito picture, it goes on D10)
const int PIN_GREEN = 6, PIN_YELLOW = 9, PIN_RED = 5, PIN_BUZZ = 2, PIN_RELAY = 10, PIN_TEMP = 3;
const bool RELAY_ACTIVE_LOW = false;  // false: bare relay via transistor, or LED stand-in; true for most opto relay modules
const float TEMP_LO = 14.0, TEMP_HI = 22.0;   // culture window 16-20 C, +/- 2 C

float tOn = 0.50, cOk = 5.0, warmMean = NAN;
int X = 3;
char mode = 'F';

bool on = false, warn = false, tempAlarm = false;
long startDay = 0, checkDay = 0;
float lastChl = NAN, chlHist[3] = {NAN, NAN, NAN};
int episodes = 0;
bool safetyStop = false;

#if USE_DS18B20
OneWire oneWire(PIN_TEMP);
DallasTemperature sensors(&oneWire);
#endif
float tempC = NAN;

const int BUZZ_HZ = 2000;   // passive buzzer: needs a tone, not a steady HIGH

void beep(int ms, int n, int gap) {
  for (int i = 0; i < n; i++) {
    tone(PIN_BUZZ, BUZZ_HZ); delay(ms);
    noTone(PIN_BUZZ);        delay(gap);
  }
}

void setOutputs() {
  digitalWrite(PIN_GREEN, on ? LOW : HIGH);
  digitalWrite(PIN_RED, on ? HIGH : LOW);
  digitalWrite(PIN_YELLOW, (warn || tempAlarm) ? HIGH : LOW);
  digitalWrite(PIN_RELAY, (on != RELAY_ACTIVE_LOW) ? HIGH : LOW);
}

bool ruleTrigger() {
  // chlHist = [day-2, day-1, today]
  return !isnan(chlHist[0]) && !isnan(chlHist[1]) && !isnan(chlHist[2]) && !isnan(warmMean)
      && chlHist[1] > chlHist[0] && chlHist[2] > chlHist[1] && chlHist[2] > 2 * warmMean;
}

void stepDay(long day, float p, float chl) {
  chlHist[0] = chlHist[1]; chlHist[1] = chlHist[2]; chlHist[2] = chl;
  bool trig = (mode == 'F') ? (!isnan(p) && p >= tOn) : ruleTrigger();
  float tOff = 0.8 * tOn;
  int maxOn = 4 * X;

  bool was = on, ended = false, maxed = false;
  warn = false;
  if (was && day >= checkDay) {
    if (isnan(chl)) {
      checkDay = day + 1;
      warn = true;                                    // re-measure day with no reading
    } else {
      bool notRising = isnan(lastChl) || chl <= lastChl;
      bool stopOk = !isnan(p) && p < tOff && chl < cOk && notRising;
      maxed = !stopOk && (day - startDay >= maxOn);
      if (!stopOk && !maxed) { lastChl = chl; checkDay = day + X; }
      ended = stopOk || maxed;
    }
  }
  if (was && safetyStop) { ended = true; warn = true; }
  safetyStop = false;
  on = was && !ended;
  bool started = false;
  if (!was && trig) {
    on = true; started = true;
    startDay = day; checkDay = day + X; lastChl = chl; episodes++;
  }
  setOutputs();
  if (started) beep(120, 3, 120);
  else if (was && ended) beep(800, 1, 0);

  Serial.print(F("day=")); Serial.print(day);
  Serial.print(F(" p=")); Serial.print(p, 2);
  Serial.print(F(" chl=")); Serial.print(chl, 2);
  Serial.print(F(" -> "));
  if (started) Serial.print(F("START"));
  else if (was && ended) Serial.print(maxed ? F("STOP_MAX_ON") : F("OFF"));
  else Serial.print(on ? F("ON") : F("idle"));
  if (on) { Serial.print(F(" next_check=")); Serial.print(checkDay); }
  Serial.print(F(" episodes=")); Serial.println(episodes);
}

float parseVal(const char *s) {
  if (s == NULL || s[0] == '\0' || (s[0] == '-' && s[1] == '\0') || s[0] == 'n' || s[0] == 'N') return NAN;
  return atof(s);
}

void printStatus() {
  Serial.print(F("mode=")); Serial.print(mode);
  Serial.print(F(" X=")); Serial.print(X);
  Serial.print(F(" T_on=")); Serial.print(tOn, 2);
  Serial.print(F(" T_off=")); Serial.print(0.8 * tOn, 2);
  Serial.print(F(" C_ok=")); Serial.print(cOk, 2);
  Serial.print(F(" MAX_ON=")); Serial.print(4 * X);
  Serial.print(F(" warm=")); Serial.print(warmMean, 2);
  Serial.print(F(" state=")); Serial.print(on ? F("ON") : F("idle"));
  Serial.print(F(" temp=")); Serial.println(tempC, 1);
}

void handleLine(char *line) {
  char *a = strtok(line, " \t\r");
  if (!a) return;
  char *b = strtok(NULL, " \t\r");
  char *c = strtok(NULL, " \t\r");
  if (isdigit(a[0])) { stepDay(atol(a), parseVal(b), parseVal(c)); return; }
  if (!strcmp(a, "x") && b)         X = max(1, atoi(b));
  else if (!strcmp(a, "cok") && b)  cOk = atof(b);
  else if (!strcmp(a, "ton") && b)  tOn = atof(b);
  else if (!strcmp(a, "mode") && b) mode = toupper(b[0]) == 'R' ? 'R' : 'F';
  else if (!strcmp(a, "warm") && b) warmMean = atof(b);
  else if (!strcmp(a, "stop"))      { safetyStop = true; Serial.println(F("safety stop at the next daily line")); return; }
  else if (!strcmp(a, "reset"))     { on = false; warn = false; episodes = 0; lastChl = NAN; for (int i = 0; i < 3; i++) chlHist[i] = NAN; setOutputs(); }
  else if (strcmp(a, "status"))     { Serial.println(F("? unknown command")); return; }
  printStatus();
}

void setup() {
  pinMode(PIN_GREEN, OUTPUT); pinMode(PIN_YELLOW, OUTPUT); pinMode(PIN_RED, OUTPUT);
  pinMode(PIN_BUZZ, OUTPUT); pinMode(PIN_RELAY, OUTPUT);
  setOutputs();
  Serial.begin(115200);
#if USE_DS18B20
  sensors.begin();
#endif
  Serial.println(F("alerter_uno ready. Send: <day> <p> <chl>   or: status"));
  printStatus();
}

unsigned long lastTempMs = 0;
char buf[64];
byte len = 0;

void loop() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n') { buf[len] = '\0'; handleLine(buf); len = 0; }
    else if (len < sizeof(buf) - 1) buf[len++] = ch;
  }
#if USE_DS18B20
  if (millis() - lastTempMs > 10000) {
    lastTempMs = millis();
    sensors.requestTemperatures();
    tempC = sensors.getTempCByIndex(0);
    bool alarm = tempC > -100 && (tempC < TEMP_LO || tempC > TEMP_HI);
    if (alarm && !tempAlarm) { Serial.print(F("TEMP ALARM ")); Serial.println(tempC, 1); }
    tempAlarm = alarm;
    setOutputs();
    if (tempAlarm) beep(60, 5, 60);
  }
#endif
}
