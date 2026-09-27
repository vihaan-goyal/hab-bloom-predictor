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
  Loop commands:
      x <days>   cok <ug/L>   ton <p>   mode F|R   warm <mean chl>
      stop       (safety stop: OFF at the next daily line, e.g. DO kit < 4 mg/L)
      mute 0|1   (silence the buzzer; alerter_link.py uses it to replay history after a reset)
      status     reset
  Sensor commands (each sensor is off until its USE_ flag below is 1):
      read       one line "S temp=.. ph=.. ph_v=.. fl=.. chl=.."  (nan = sensor off / not calibrated)
      every <min>   print that line every <min> minutes (0 = off; default 10)
      cal686     pH probe in pH 6.86 buffer: store its voltage     cal918   same for pH 9.18
      blank      fluorometer: cuvette of plain seawater, store its signal as zero chlorophyll
      chlk <k>   fluorometer: ug/L of chlorophyll per signal count (from the dilution series)
      gain l|m|h|x   fluorometer sensitivity (TSL2591 gain: low, medium, high, max)
      cal        show the stored calibration        calclear   erase it
      Calibration is kept in EEPROM, so it survives resets and uploads.

  Outputs:  green LED = idle, blue LED + relay = treatment ON,
            white LED = warning (safety stop, temperature out of range, missed reading),
            buzzer: 3 beeps = ON, 1 long = OFF, fast beeps = temperature alarm.

  Wiring: hardware/alerter_uno/README.md.
*/
#include <math.h>
#include <EEPROM.h>

// ---- sensors: set to 1 once the part is wired (libraries: Arduino IDE -> Library Manager)
#ifndef USE_DS18B20
#define USE_DS18B20 0   // temperature probe            needs OneWire + DallasTemperature
#endif
#ifndef USE_TSL2591
#define USE_TSL2591 0   // chlorophyll (fluorometer)    needs Adafruit TSL2591 Library + Adafruit Unified Sensor
#endif
#ifndef USE_PH
#define USE_PH 0        // pH module (analog)           no library
#endif

#if USE_DS18B20
#include <OneWire.h>
#include <DallasTemperature.h>
#endif
#if USE_TSL2591
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_TSL2591.h>
#endif

// Pins match the circuito.io wiring diagram (hardware/alerter_uno/README.md)
// (circuito's yellow LED = our white warning LED; the relay is not in the circuito picture, it goes on D10)
const int PIN_GREEN = 6, PIN_YELLOW = 9, PIN_RED = 5, PIN_BUZZ = 2, PIN_RELAY = 10, PIN_TEMP = 3;
const int PIN_FLUOR_LED = 7;   // fluorometer's blue excitation LED (TSL2591 itself is on SDA/SCL)
const int PIN_PH = A2;         // pH module Po (A4/A5 are taken by SDA/SCL)
const bool RELAY_ACTIVE_LOW = false;  // false: bare relay via transistor, or LED stand-in; true for most opto relay modules
const float TEMP_LO = 14.0, TEMP_HI = 22.0;   // culture window 16-20 C, +/- 2 C

float tOn = 0.50, cOk = 5.0, warmMean = NAN;
int X = 3;
char mode = 'F';

bool on = false, warn = false, tempAlarm = false, muted = false;
long startDay = 0, checkDay = 0;
float lastChl = NAN, chlHist[3] = {NAN, NAN, NAN};
int episodes = 0;
bool safetyStop = false;

#if USE_DS18B20
OneWire oneWire(PIN_TEMP);
DallasTemperature sensors(&oneWire);
#endif
#if USE_TSL2591
Adafruit_TSL2591 tsl = Adafruit_TSL2591(2591);
bool tslOk = false;
#endif
float tempC = NAN;

// ---- calibration kept in EEPROM
struct Cal { uint16_t magic; float v686, v918, blank, chlK; };
const uint16_t CAL_MAGIC = 0xA1E7;
Cal cal = {CAL_MAGIC, NAN, NAN, NAN, NAN};
unsigned int everyMin = 10;

const int BUZZ_HZ = 2000;   // passive buzzer: needs a tone, not a steady HIGH

void beep(int ms, int n, int gap) {
  if (muted) return;                      // the laptop link replays history muted
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

// ------------------------------------------------------------------ sensors
void readTemp() {
#if USE_DS18B20
  sensors.requestTemperatures();
  float t = sensors.getTempCByIndex(0);
  tempC = (t > -100) ? t : NAN;          // -127 = probe not found
#endif
}

float readPhVolts() {
#if USE_PH
  long s = 0;
  for (int i = 0; i < 40; i++) { s += analogRead(PIN_PH); delay(3); }
  return s / 40.0 * 5.0 / 1023.0;
#else
  return NAN;
#endif
}

float phFromVolts(float v) {
  if (isnan(v) || isnan(cal.v686) || isnan(cal.v918) || fabs(cal.v918 - cal.v686) < 0.01) return NAN;
  return 6.86 + (v - cal.v686) * (9.18 - 6.86) / (cal.v918 - cal.v686);
}

float readFluor() {
  // Blue LED off, then on; the difference is the light the LED causes (chlorophyll glow
  // through the red filter). Ambient light and sensor offset cancel out.
#if USE_TSL2591
  if (!tslOk) return NAN;
  float dark = 0, lit = 0;
  digitalWrite(PIN_FLUOR_LED, LOW);
  for (int i = 0; i < 3; i++) dark += tsl.getFullLuminosity() & 0xFFFF;
  digitalWrite(PIN_FLUOR_LED, HIGH);
  delay(20);
  for (int i = 0; i < 3; i++) {
    uint16_t full = tsl.getFullLuminosity() & 0xFFFF;
    if (full == 0xFFFF) { digitalWrite(PIN_FLUOR_LED, LOW); Serial.println(F("fluor: SATURATED, lower the gain")); return NAN; }
    lit += full;
  }
  digitalWrite(PIN_FLUOR_LED, LOW);
  return (lit - dark) / 3.0;
#else
  return NAN;
#endif
}

float chlFromFluor(float f) {
  if (isnan(f) || isnan(cal.blank) || isnan(cal.chlK)) return NAN;
  return (f - cal.blank) * cal.chlK;
}

void printSensors() {
  readTemp();
  float v = readPhVolts(), fl = readFluor();
  Serial.print(F("S temp=")); Serial.print(tempC, 2);
  Serial.print(F(" ph=")); Serial.print(phFromVolts(v), 2);
  Serial.print(F(" ph_v=")); Serial.print(v, 3);
  Serial.print(F(" fl=")); Serial.print(fl, 1);
  Serial.print(F(" chl=")); Serial.println(chlFromFluor(fl), 2);
}

void printCal() {
  Serial.print(F("cal v686=")); Serial.print(cal.v686, 3);
  Serial.print(F(" v918=")); Serial.print(cal.v918, 3);
  Serial.print(F(" blank=")); Serial.print(cal.blank, 1);
  Serial.print(F(" chlk=")); Serial.println(cal.chlK, 5);
}

void saveCal() { EEPROM.put(0, cal); printCal(); }

void setGain(char g) {
#if USE_TSL2591
  if (!tslOk) { Serial.println(F("fluor: TSL2591 not found")); return; }
  tsl2591Gain_t gain = g == 'l' ? TSL2591_GAIN_LOW : g == 'h' ? TSL2591_GAIN_HIGH : g == 'x' ? TSL2591_GAIN_MAX : TSL2591_GAIN_MED;
  tsl.setGain(gain);
  Serial.print(F("gain=")); Serial.println(g);
#else
  (void)g;
  Serial.println(F("fluor: USE_TSL2591 is 0"));
#endif
}

// ------------------------------------------------------------------ commands
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
  if (!strcmp(a, "read"))           { printSensors(); return; }
  if (!strcmp(a, "every") && b)     { everyMin = atoi(b); Serial.print(F("every=")); Serial.println(everyMin); return; }
  if (!strcmp(a, "cal686"))         { cal.v686 = readPhVolts(); saveCal(); return; }
  if (!strcmp(a, "cal918"))         { cal.v918 = readPhVolts(); saveCal(); return; }
  if (!strcmp(a, "blank"))          { cal.blank = readFluor(); saveCal(); return; }
  if (!strcmp(a, "chlk") && b)      { cal.chlK = atof(b); saveCal(); return; }
  if (!strcmp(a, "gain") && b)      { setGain(tolower(b[0])); return; }
  if (!strcmp(a, "cal"))            { printCal(); return; }
  if (!strcmp(a, "calclear"))       { cal = {CAL_MAGIC, NAN, NAN, NAN, NAN}; saveCal(); return; }
  if (!strcmp(a, "x") && b)         X = max(1, atoi(b));
  else if (!strcmp(a, "cok") && b)  cOk = atof(b);
  else if (!strcmp(a, "ton") && b)  tOn = atof(b);
  else if (!strcmp(a, "mode") && b) mode = toupper(b[0]) == 'R' ? 'R' : 'F';
  else if (!strcmp(a, "warm") && b) warmMean = atof(b);
  else if (!strcmp(a, "stop"))      { safetyStop = true; Serial.println(F("safety stop at the next daily line")); return; }
  else if (!strcmp(a, "mute") && b) muted = atoi(b) != 0;
  else if (!strcmp(a, "reset"))     { on = false; warn = false; episodes = 0; lastChl = NAN; for (int i = 0; i < 3; i++) chlHist[i] = NAN; setOutputs(); }
  else if (strcmp(a, "status"))     { Serial.println(F("? unknown command")); return; }
  printStatus();
  (void)c;
}

void setup() {
  pinMode(PIN_GREEN, OUTPUT); pinMode(PIN_YELLOW, OUTPUT); pinMode(PIN_RED, OUTPUT);
  pinMode(PIN_BUZZ, OUTPUT); pinMode(PIN_RELAY, OUTPUT); pinMode(PIN_FLUOR_LED, OUTPUT);
  setOutputs();
  Serial.begin(115200);
  Cal stored;
  EEPROM.get(0, stored);
  if (stored.magic == CAL_MAGIC) cal = stored;
#if USE_DS18B20
  sensors.begin();
#endif
#if USE_TSL2591
  tslOk = tsl.begin();
  if (tslOk) { tsl.setGain(TSL2591_GAIN_MED); tsl.setTiming(TSL2591_INTEGRATIONTIME_200MS); }
  else Serial.println(F("fluor: TSL2591 not found (check SDA/SCL wiring)"));
#endif
  Serial.println(F("alerter_uno ready. Send: <day> <p> <chl>   or: status"));
  printStatus();
}

unsigned long lastTempMs = 0, lastReportMs = 0;
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
    readTemp();
    bool alarm = !isnan(tempC) && (tempC < TEMP_LO || tempC > TEMP_HI);
    if (alarm && !tempAlarm) { Serial.print(F("TEMP ALARM ")); Serial.println(tempC, 1); }
    tempAlarm = alarm;
    setOutputs();
    if (tempAlarm) beep(60, 5, 60);
  }
#endif
#if USE_DS18B20 || USE_TSL2591 || USE_PH
  if (everyMin > 0 && millis() - lastReportMs > everyMin * 60000UL) {
    lastReportMs = millis();
    printSensors();
  }
#endif
}
