/*
  buoy_esp32.ino -- autonomous water-quality buoy that runs the Narragansett bloom forecast ON THE CHIP
  ===================================================================================================
  Model: the fork's release model v2 (300 boosted trees, 23 features, bloom_model.h), forecast
         P(daily-mean chl > 10 ug/L within 7 days); ALERT if p >= BLOOM_THRESHOLD (0.45).
  Features: features.h, built from a rolling daily history exactly as the fork's training code
         (lags/rolling means over daily ROWS, min_periods max(2, w/3), chl_trend, chl_anomaly, month).

  Boot: SELF-TEST (selftest.h): model vs Python on 8 real rows, feature code vs the fork's columns on
        29 real days, PSS-78 reference values. Then "READY".

  DEMO / REPLAY mode (default: no sensors enabled). Serial Monitor at 115200, line ending "Newline":
      day <yyyy-mm-dd> <chl> <temp> <sal> <do> [clim]   one DAILY MEAN row (nan = missing);
                    optional 6th value = that day's chl_climatology (the replay tool sends the fork's)
      vec <23 numbers>   score a raw feature vector (BLOOM_FEATURES order, nan allowed)
      status   reset (clears the daily history)   selftest   hist (print the stored days)
      site <name>   name used in bulletins (e.g. Newport-Harbor), kept in NVS
      clim <month> <value>   per-site chl climatology for that month, kept in NVS (nan clears it)
      clim     show the table              climclear   erase it
      help
    Each scored day prints   F <date> chl=.. chl_lag1=.. ... month=..
                             P <date> p=0.123456 ALERT|idle n=<days in history>
    and, when something changes, a harbor bulletin   MSG <title> | <text>
      Bloom WARNING (alert turns on), All clear (turns off), Bloom detected (chl crosses 10),
      Buoy check needed (a sensor day was dropped). Demo days print them; sensor days also push them.

  SENSOR mode (set any USE_ flag below to 1; needs the libraries named next to it):
      samples every 15 min, keeps daily means, closes a day at local midnight; a day with fewer than
      MIN_READINGS (48) chl readings is dropped, like training; the last 30 days and all calibration
      live in NVS (Preferences), so a reboot keeps them.
      read     one sample line, not stored      date <yyyy-mm-dd> <hh:mm>   set the clock (no Wi-Fi)
      blank    fluorometer: plain seawater = zero chl      chlk <k>   ug/L per count (sonde-equivalent)
      gain l|m|h|x   TSL2591 gain (saved; redo blank/chlk after changing it)
      cal686 / cal918   pH probe in pH 6.86 / 9.18 buffer        cal   calclear
  Wi-Fi alerts (USE_WIFI 1): wifi <ssid>   wifipass <password>   ntfy <topic>   ntfytest
      Stored in NVS, never in this file. Every bulletin from a sensor day posts to ntfy.sh/<topic>.

  Outputs: onboard LED (GPIO 2) and relay (GPIO 26) ON while the latest forecast is ALERT.
  The tank loop rules (X, C_ok, MAX_ON) are NOT in this version: see controlHook() below.
  Wiring and a walkthrough: hardware/buoy_esp32/README.md.
*/
#include <Arduino.h>
#include <Preferences.h>
#include <time.h>
#include <sys/time.h>

// declared before any function: the Arduino builder puts its auto-prototypes here
enum Notify { N_SILENT = 0, N_SERIAL = 1, N_PUSH = 2 };   // bulletins: restore / demo day / live sensor day

#define ST_PRINTF(...) Serial.printf(__VA_ARGS__)
#include "selftest.h"            // pulls in bloom_model.h, features.h, pss78.h, test_vectors.h

// ---- sensors: set to 1 once the part is wired (Arduino IDE -> Library Manager for the library)
#ifndef USE_DS18B20
#define USE_DS18B20 0   // water temperature, GPIO 4     needs OneWire + DallasTemperature
#endif
#ifndef USE_TSL2591
#define USE_TSL2591 0   // chlorophyll fluorometer, I2C  needs Adafruit TSL2591 Library + Adafruit Unified Sensor
#endif
#ifndef USE_EZO_EC
#define USE_EZO_EC 0    // Atlas EZO-EC conductivity, I2C 0x64 -> salinity (PSS-78). Wire only, no library
#endif
#ifndef USE_PH
#define USE_PH 0        // analog pH module on GPIO 34 (logged only; pH is not a model feature)
#endif
#ifndef USE_WIFI
#define USE_WIFI 0      // ntfy.sh push alerts + NTP clock. Core libraries only
#endif
#define SENSOR_MODE (USE_DS18B20 || USE_TSL2591 || USE_EZO_EC || USE_PH)

#if USE_DS18B20
#include <OneWire.h>
#include <DallasTemperature.h>
#endif
#if USE_TSL2591 || USE_EZO_EC
#include <Wire.h>
#endif
#if USE_TSL2591
#include <Adafruit_Sensor.h>
#include <Adafruit_TSL2591.h>
#endif
#if USE_WIFI
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#endif

// ---- pins (ESP32 Dev Module)
const int PIN_LED = 2;          // onboard blue LED
const int PIN_RELAY = 26;
const int PIN_TEMP = 4;         // DS18B20 data, 4.7 kOhm pull-up to 3.3 V
const int PIN_FLUOR_LED = 25;   // fluorometer's blue excitation LED (through a transistor)
const int PIN_PH = 34;          // ADC1 (ADC2 pins stop working while Wi-Fi is on)
const int PIN_SDA = 21, PIN_SCL = 22;
const uint8_t EZO_ADDR = 0x64;
const bool RELAY_ACTIVE_LOW = false;  // true for most opto-isolated relay modules
const unsigned long SAMPLE_MS = 15UL * 60UL * 1000UL;
const char *BUOY_TZ = "EST5EDT,M3.2.0,M11.1.0";   // days close at local midnight (Narragansett / LIS)

// ---- state
Preferences prefs;               // NVS namespace "buoy"
History hist;
float climTable[13];             // [1..12] chl climatology per month, NAN = unknown
bool alertOn = false, relayOn = false;
float lastP = NAN;
int32_t lastDate = 0;
int selftestFails = -1;
const float BLOOM_CHL = 10.0f;   // ug/L, the training label's bloom level
String siteName = "buoy";        // used in bulletins (`site`)

struct Cal { uint32_t magic; float blank, chlK, v686, v918; char gain; };
const uint32_t CAL_MAGIC = 0xB0A70001;
Cal cal = {CAL_MAGIC, NAN, NAN, NAN, NAN, 'm'};

// daily accumulator (sensor mode): sums of the 15-min readings of the current local day
struct Acc { int32_t date; double sChl, sTemp, sSal, sPh; uint16_t nChl, nTemp, nSal, nPh; };
Acc acc;
struct Sample { float temp, cond, sal, ph, phV, fl, chl; };   // one 15-min reading (NAN = sensor off)

#if USE_DS18B20
OneWire oneWire(PIN_TEMP);
DallasTemperature ds(&oneWire);
#endif
#if USE_TSL2591
Adafruit_TSL2591 tsl = Adafruit_TSL2591(2591);
bool tslOk = false;
#endif
#if USE_WIFI
String wifiSsid, wifiPass, ntfyTopic;
#endif

// ------------------------------------------------------------------ helpers
float parseVal(const char *s) {
  if (s == NULL || s[0] == '\0' || (s[0] == '-' && s[1] == '\0') || s[0] == 'n' || s[0] == 'N') return NAN;
  return strtof(s, NULL);
}

void printDate(int32_t d) { Serial.printf("%04ld-%02ld-%02ld", (long)(d / 10000), (long)(d / 100 % 100), (long)(d % 100)); }

void saveHist() { prefs.putBytes("hist", &hist, sizeof(hist)); }
void saveClim() { prefs.putBytes("clim", climTable, sizeof(climTable)); }
void saveCal()  { prefs.putBytes("cal", &cal, sizeof(cal)); }
void saveAcc()  { prefs.putBytes("acc", &acc, sizeof(acc)); }

void clearAcc(int32_t date) { memset(&acc, 0, sizeof(acc)); acc.date = date; }

// ------------------------------------------------------------------ alert outputs
/* controlHook -- the ONE place that decides the relay from a scored day.
   TODO(loop rules): port the alerter's ON/OFF rules from hardware/alerter_uno/alerter_uno.ino
   (stepDay): START when p >= T_on; recheck every X days; OFF only if p < T_off (= 0.8 T_on) AND
   chl < C_ok AND chl not rising; STOP after MAX_ON days; floor rule; handover mode. Keep the state
   (on, startDay, checkDay, lastChl, ...) in a struct here and persist it in NVS like `hist`.
   Until then the relay simply follows today's alert. Called once per scored day (and per `vec`).
   date = yyyymmdd (0 for `vec`), p = forecast, chl = today's daily mean (NAN for `vec`). */
bool controlHook(int32_t date, float p, float chl, bool alert) {
  (void)date; (void)p; (void)chl;
  return alert;
}

void setOutputs() {
  digitalWrite(PIN_LED, alertOn ? HIGH : LOW);
  digitalWrite(PIN_RELAY, (relayOn != RELAY_ACTIVE_LOW) ? HIGH : LOW);
}

#if USE_WIFI
bool wifiUp(unsigned long waitMs = 15000) {
  if (WiFi.status() == WL_CONNECTED) return true;
  if (wifiSsid.length() == 0) return false;
  WiFi.mode(WIFI_STA);
  WiFi.begin(wifiSsid.c_str(), wifiPass.c_str());
  unsigned long t0 = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - t0 < waitMs) delay(250);
  bool ok = WiFi.status() == WL_CONNECTED;
  if (ok) configTzTime(BUOY_TZ, "pool.ntp.org", "time.nist.gov");   // keeps the clock right
  else Serial.println("wifi: not connected");
  return ok;
}

bool ntfySend(const char *title, const String &msg) {
  if (ntfyTopic.length() == 0) { Serial.println("ntfy: no topic (send `ntfy <topic>`)"); return false; }
  if (!wifiUp()) return false;
  WiFiClientSecure client;
  client.setInsecure();          // no certificate pinning: fine for a public alert topic, not for secrets
  HTTPClient http;
  http.begin(client, String("https://ntfy.sh/") + ntfyTopic);
  http.addHeader("Title", title);
  http.addHeader("Priority", "high");
  http.addHeader("Tags", "ocean,warning");
  int code = http.POST(msg);
  http.end();
  Serial.printf("ntfy: HTTP %d\n", code);
  return code >= 200 && code < 300;
}
#endif

/* ---- harbor early-warning bulletins
   At harbor scale the device cannot treat the water; the warning IS the product. Each bulletin is
   printed as   MSG <title> | <body>   (so a replay shows it with no Wi-Fi) and, in SENSOR mode with
   USE_WIFI, posted to ntfy. Walk-forward record 2015-2023 at 0.45 (fork notes/HARBOR_WARNING_PREREG.md):
   86% of bloom onsets warned 1-7 days ahead, median 1 false warning per site per season. */
void bulletin(Notify mode, const char *title, const String &body) {
  if (mode == N_SILENT) return;
  Serial.printf("MSG %s | %s\n", title, body.c_str());
#if USE_WIFI
  if (mode == N_PUSH) ntfySend(title, body);
#endif
}

String dateStr(int32_t d) {
  char s[11];
  snprintf(s, sizeof(s), "%04ld-%02ld-%02ld", (long)(d / 10000), (long)(d / 100 % 100), (long)(d % 100));
  return String(s);
}

/* onset = today's chl > BLOOM_CHL after QUIET_ROWS stored days at or below it (the event definition of the
   harbor-warning test), so a bloom that hovers around the level is announced once, not every dip. */
const int QUIET_ROWS = 5;

void applyForecast(int32_t date, float p, float chl, bool onset, Notify mode) {
  bool was = alertOn;
  alertOn = !isnan(p) && p >= BLOOM_THRESHOLD;
  relayOn = controlHook(date, p, chl, alertOn);
  setOutputs();
  lastP = p;
  if (date == 0) return;           // `vec` rows have no date: no bulletins
  String where = siteName + " " + dateStr(date);
  if (onset) {
    bulletin(mode, "Bloom detected",
             where + ": chlorophyll " + String(chl, 1) + " ug/L is above the bloom level (" +
             String(BLOOM_CHL, 0) + "). Managers: sample for harmful species and toxins now.");
  }
  if (alertOn && !was) {
    bulletin(mode, "Bloom WARNING",
             where + ": bloom likely within " + String(BLOOM_HORIZON_DAYS) + " days (risk " + String(p, 2) +
             ", chl " + String(chl, 1) + " ug/L). Shellfish growers: plan early harvest, hold seed in the "
             "nursery. Hatcheries: switch to stored or filtered intake water. Managers: start phytoplankton "
             "and toxin sampling. Forecast, not a measurement: about 1 false warning per site per season. "
             "An all-clear follows when the risk drops.");
  } else if (!alertOn && was) {
    bulletin(mode, "All clear",
             where + ": bloom risk back below the warning level (risk " + String(p, 2) + ", chl " +
             String(chl, 1) + " ug/L). Normal operations can resume; the buoy keeps watching.");
  }
}

// ------------------------------------------------------------------ scoring
void printFeatures(const char *tag, const float x[F_COUNT]) {
  Serial.print("F "); Serial.print(tag);
  for (int i = 0; i < F_COUNT; i++) Serial.printf(" %s=%.7g", FEAT_NAMES[i], (double)x[i]);
  Serial.println();
}

/* score the newest history row; prints F and P lines */
void scoreLatest(Notify mode) {
  if (hist.n == 0) return;
  float x[F_COUNT];
  build_features(&hist, climTable, x);
  const DayRec &d = hist.r[hist.n - 1];
  char tag[11];
  snprintf(tag, sizeof(tag), "%04ld-%02ld-%02ld", (long)(d.date / 10000), (long)(d.date / 100 % 100), (long)(d.date % 100));
  printFeatures(tag, x);
  float p = bloom_prob(x);
  bool onset = d.chl > BLOOM_CHL && hist.n > QUIET_ROWS;
  for (int k = 2; onset && k <= QUIET_ROWS + 1; k++) onset = hist.r[hist.n - k].chl <= BLOOM_CHL;
  applyForecast(d.date, p, d.chl, onset, mode);
  lastDate = d.date;
  Serial.printf("P %s p=%.6f %s n=%ld\n", tag, (double)p, p >= BLOOM_THRESHOLD ? "ALERT" : "idle", (long)hist.n);
}

/* add one daily row and score it. Returns false if rejected. */
bool addDay(const DayRec &r, Notify mode) {
  char tag[11];
  snprintf(tag, sizeof(tag), "%04ld-%02ld-%02ld", (long)(r.date / 10000), (long)(r.date / 100 % 100), (long)(r.date % 100));
  if (isnan(r.chl)) {            // training never has a row without chl: the day is not a row
    Serial.printf("note %s: chl missing, day skipped (training drops such days)\n", tag);
    Serial.printf("P %s p=nan SKIP n=%ld\n", tag, (long)hist.n);
    return false;
  }
  int32_t prev = hist.n ? hist.r[hist.n - 1].date : 0;
  int res = hist_push(&hist, r);
  if (res < 0) {
    Serial.printf("ERR %s is older than the last day in the history; send `reset` first\n", tag);
    Serial.printf("P %s p=nan SKIP n=%ld\n", tag, (long)hist.n);
    return false;
  }
  if (res == 1) Serial.printf("note %s: replaced the same day\n", tag);
  else if (prev) {
    struct tm a = {}, b = {};
    a.tm_year = prev / 10000 - 1900; a.tm_mon = prev / 100 % 100 - 1; a.tm_mday = prev % 100; a.tm_hour = 12;
    b.tm_year = r.date / 10000 - 1900; b.tm_mon = r.date / 100 % 100 - 1; b.tm_mday = r.date % 100; b.tm_hour = 12;
    long gap = lround(difftime(mktime(&b), mktime(&a)) / 86400.0);
    if (gap > 1) Serial.printf("note %s: %ld-day gap; lags step over it (row-based, as in training)\n", tag, gap);
  }
#if SENSOR_MODE
  saveHist();
#endif
  scoreLatest(mode);
  return true;
}

// ------------------------------------------------------------------ sensors
float tempC = NAN;

void readTemp() {
#if USE_DS18B20
  ds.requestTemperatures();
  float t = ds.getTempCByIndex(0);
  tempC = (t > -100) ? t : NAN;  // -127 = probe not found
#endif
}

float readFluor() {
  // Blue LED off, then on: the difference is the chlorophyll glow (ambient light cancels), as alerter_uno.
#if USE_TSL2591
  if (!tslOk) return NAN;
  float dark = 0, lit = 0;
  digitalWrite(PIN_FLUOR_LED, LOW);
  for (int i = 0; i < 3; i++) dark += tsl.getFullLuminosity() & 0xFFFF;
  digitalWrite(PIN_FLUOR_LED, HIGH);
  delay(20);
  for (int i = 0; i < 3; i++) {
    uint16_t full = tsl.getFullLuminosity() & 0xFFFF;
    if (full == 0xFFFF) { digitalWrite(PIN_FLUOR_LED, LOW); Serial.println("fluor: SATURATED, lower the gain"); return NAN; }
    lit += full;
  }
  digitalWrite(PIN_FLUOR_LED, LOW);
  return (lit - dark) / 3.0f;
#else
  return NAN;
#endif
}

/* blank + multiplier -> sonde-equivalent ug/L (the scale the model was trained on) */
float chlFromFluor(float f) {
  if (isnan(f) || isnan(cal.blank) || isnan(cal.chlK)) return NAN;
  return (f - cal.blank) * cal.chlK;
}

#if USE_EZO_EC
/* send an ASCII command; returns the reply (empty on error). Atlas EZO I2C protocol: first byte
   1 = success, 2 = syntax error, 254 = still processing, 255 = no data. */
String ezoCmd(const char *cmd, unsigned long waitMs) {
  Wire.beginTransmission(EZO_ADDR);
  Wire.write((const uint8_t *)cmd, strlen(cmd));
  if (Wire.endTransmission() != 0) return String();
  delay(waitMs);
  Wire.requestFrom((int)EZO_ADDR, 32);
  if (!Wire.available() || Wire.read() != 1) { while (Wire.available()) Wire.read(); return String(); }
  String s;
  while (Wire.available()) { char c = Wire.read(); if (c == 0) break; s += c; }
  while (Wire.available()) Wire.read();
  return s;
}
#endif

/* conductivity in mS/cm at the water temperature (NOT compensated to 25 C), NAN if unavailable */
float readCondMScm() {
#if USE_EZO_EC
  String r = ezoCmd("R", 600);   // EC in uS/cm; first field if several outputs are enabled
  if (r.length() == 0) return NAN;
  float us = r.toFloat();
  return us > 0 ? us / 1000.0f : NAN;
#else
  return NAN;
#endif
}

float readPhVolts() {
#if USE_PH
  long s = 0;
  for (int i = 0; i < 40; i++) { s += analogReadMilliVolts(PIN_PH); delay(3); }
  return s / 40.0f / 1000.0f;    // volts at the ESP32 pin (after the 5 V -> 3.3 V divider)
#else
  return NAN;
#endif
}

float phFromVolts(float v) {
  if (isnan(v) || isnan(cal.v686) || isnan(cal.v918) || fabsf(cal.v918 - cal.v686) < 0.01f) return NAN;
  return 6.86f + (v - cal.v686) * (9.18f - 6.86f) / (cal.v918 - cal.v686);
}


Sample takeSample() {
  Sample s;
  readTemp();
  s.temp = tempC;
  s.cond = readCondMScm();
  // PSS-78 needs the real water temperature; without the DS18B20 salinity stays NAN (model fills the median)
  s.sal = (float)pss78_salinity(s.cond, s.temp, 0.0);
  s.phV = readPhVolts();
  s.ph = phFromVolts(s.phV);
  s.fl = readFluor();
  s.chl = chlFromFluor(s.fl);
  return s;
}

void printSample(const Sample &s) {
  Serial.printf("S temp=%.2f cond_mScm=%.3f sal=%.3f ph=%.2f ph_v=%.3f fl=%.1f chl=%.2f\n",
                s.temp, s.cond, s.sal, s.ph, s.phV, s.fl, s.chl);
}

// ------------------------------------------------------------------ clock (sensor mode)
bool clockOk() { return time(NULL) > 1600000000; }   // after 2020-09: set by `date` or NTP

int32_t localDate() {
  time_t now = time(NULL);
  struct tm t;
  localtime_r(&now, &t);
  return (t.tm_year + 1900) * 10000 + (t.tm_mon + 1) * 100 + t.tm_mday;
}

void setClock(int32_t d, int hh, int mm) {
  struct tm t = {};
  t.tm_year = d / 10000 - 1900; t.tm_mon = d / 100 % 100 - 1; t.tm_mday = d % 100;
  t.tm_hour = hh; t.tm_min = mm; t.tm_isdst = -1;
  time_t e = mktime(&t);         // local time (BUOY_TZ)
  struct timeval tv; tv.tv_sec = e; tv.tv_usec = 0;
  settimeofday(&tv, NULL);
  prefs.putLong64("clock", (int64_t)e);
}

/* close the accumulated day: a row only if it has >= MIN_READINGS chl readings (training rule) */
void closeDay() {
  if (acc.date == 0) return;
  if (acc.nChl >= MIN_READINGS) {
    DayRec r;
    r.date = acc.date;
    r.chl = (float)(acc.sChl / acc.nChl);
    r.temp = acc.nTemp ? (float)(acc.sTemp / acc.nTemp) : NAN;
    r.sal = acc.nSal ? (float)(acc.sSal / acc.nSal) : NAN;
    r.dox = NAN;                 // no DO sensor: the model fills the training median
    r.clim = NAN;                // per-month table (`clim`), else NAN
    Serial.printf("DAY "); printDate(acc.date);
    Serial.printf(" closed: %u chl, %u temp, %u sal, %u pH readings; pH mean %.2f\n",
                  acc.nChl, acc.nTemp, acc.nSal, acc.nPh, acc.nPh ? acc.sPh / acc.nPh : NAN);
    addDay(r, N_PUSH);
  } else {
    Serial.printf("DAY "); printDate(acc.date);
    Serial.printf(" dropped: %u chl readings < %d (training drops such days)\n", acc.nChl, MIN_READINGS);
    bulletin(N_PUSH, "Buoy check needed",
             siteName + " " + dateStr(acc.date) + ": only " + String(acc.nChl) + " of " + String(MIN_READINGS) +
             " chlorophyll readings yesterday, so no forecast was made. Check the fluorometer, power and fouling.");
  }
}

void sampleTick() {
  Sample s = takeSample();
  printSample(s);
  if (!clockOk()) { Serial.println("clock not set: send `date yyyy-mm-dd hh:mm` (or enable Wi-Fi); sample not stored"); return; }
  int32_t today = localDate();
  if (acc.date != today) { closeDay(); clearAcc(today); }
  if (!isnan(s.chl))  { acc.sChl += s.chl;   acc.nChl++; }
  if (!isnan(s.temp)) { acc.sTemp += s.temp; acc.nTemp++; }
  if (!isnan(s.sal))  { acc.sSal += s.sal;   acc.nSal++; }
  if (!isnan(s.ph))   { acc.sPh += s.ph;     acc.nPh++; }
  saveAcc();
  prefs.putLong64("clock", (int64_t)time(NULL));   // a reboot resumes from here (minus the downtime)
}

// ------------------------------------------------------------------ commands
void printClim() {
  Serial.print("clim");
  for (int m = 1; m <= 12; m++) Serial.printf(" %d=%.3g", m, (double)climTable[m]);
  Serial.println(isnan(climTable[1]) && isnan(climTable[7]) ? "   (missing months -> NAN -> training median)" : "");
}

void printCal() {
  Serial.printf("cal blank=%.1f chlk=%.5f gain=%c v686=%.3f v918=%.3f\n",
                cal.blank, cal.chlK, cal.gain, cal.v686, cal.v918);
}

void printStatus() {
  Serial.printf("site=\"%s\" mode=%s selftest=%s history=%ld days", siteName.c_str(), SENSOR_MODE ? "SENSOR" : "DEMO",
                selftestFails < 0 ? "not run" : selftestFails == 0 ? "PASS" : "FAIL", (long)hist.n);
  if (hist.n) { Serial.print(" ("); printDate(hist.r[0].date); Serial.print(".."); printDate(hist.r[hist.n - 1].date); Serial.print(")"); }
  Serial.printf(" last_p=%.4f state=%s relay=%s threshold=%.2f\n", (double)lastP, alertOn ? "ALERT" : "idle",
                relayOn ? "ON" : "off", (double)BLOOM_THRESHOLD);
  printClim();
#if SENSOR_MODE
  printCal();
  Serial.printf("sensors: ds18b20=%d tsl2591=%d ezo_ec=%d ph=%d  today=", USE_DS18B20, USE_TSL2591, USE_EZO_EC, USE_PH);
  if (acc.date) printDate(acc.date); else Serial.print("-");
  Serial.printf(" chl_readings=%u/%d  clock=%s\n", acc.nChl, MIN_READINGS, clockOk() ? "set" : "NOT SET");
#endif
#if USE_WIFI
  Serial.printf("wifi ssid=\"%s\" pass=%s ntfy_topic=\"%s\" connected=%s\n", wifiSsid.c_str(),
                wifiPass.length() ? "****" : "(none)", ntfyTopic.c_str(), WiFi.status() == WL_CONNECTED ? "yes" : "no");
#endif
}

void printHelp() {
  Serial.println("demo:   day <yyyy-mm-dd> <chl> <temp> <sal> <do> [clim]   vec <23 numbers>");
  Serial.println("        status  reset  selftest  hist  site [<name>]  clim [<month> <value>]  climclear  help");
#if SENSOR_MODE
  Serial.println("sensor: read  date <yyyy-mm-dd> <hh:mm>  blank  chlk <k>  gain l|m|h|x  cal686  cal918  cal  calclear");
#endif
#if USE_WIFI
  Serial.println("wifi:   wifi <ssid>  wifipass <password>  ntfy <topic>  ntfytest");
#endif
}

void printHist() {
  for (int i = 0; i < hist.n; i++) {
    const DayRec &d = hist.r[i];
    printDate(d.date);
    Serial.printf(" chl=%.4g temp=%.4g sal=%.4g do=%.4g clim=%.4g\n", d.chl, d.temp, d.sal, d.dox, d.clim);
  }
  if (!hist.n) Serial.println("history empty");
}

void setGain(char g) {
#if USE_TSL2591
  if (!tslOk) { Serial.println("fluor: TSL2591 not found"); return; }
  tsl.setGain(g == 'l' ? TSL2591_GAIN_LOW : g == 'h' ? TSL2591_GAIN_HIGH : g == 'x' ? TSL2591_GAIN_MAX : TSL2591_GAIN_MED);
  Serial.printf("gain=%c\n", g);
  if (cal.gain != g) { cal.gain = g; Serial.println("gain changed: redo `blank` and `chlk` at this gain"); saveCal(); printCal(); }
#else
  (void)g; Serial.println("fluor: USE_TSL2591 is 0");
#endif
}

/* rest of the line after the command word (keeps spaces, e.g. an SSID) */
const char *restOf(const char *line, const char *cmd) {
  const char *p = line + strlen(cmd);
  while (*p == ' ' || *p == '\t') p++;
  return p;
}

void handleLine(char *line) {
  while (*line == ' ' || *line == '\t') line++;
  size_t L = strlen(line);
  while (L && (line[L - 1] == '\r' || line[L - 1] == ' ' || line[L - 1] == '\t')) line[--L] = '\0';
  if (!L) return;
  char raw[128];                 // copy for commands that need the raw rest of the line
  strncpy(raw, line, sizeof(raw) - 1); raw[sizeof(raw) - 1] = '\0';

  char *a = strtok(line, " \t");
  if (!a) return;
  if (!strcmp(a, "day")) {
    char *t[6];
    for (int i = 0; i < 6; i++) t[i] = strtok(NULL, " \t");
    int32_t d = parse_date(t[0]);
    if (!d || !t[1]) { Serial.println("ERR usage: day <yyyy-mm-dd> <chl> <temp> <sal> <do> [clim]"); Serial.println("P ? p=nan SKIP"); return; }
    DayRec r = {d, parseVal(t[1]), parseVal(t[2]), parseVal(t[3]), parseVal(t[4]), parseVal(t[5])};
    addDay(r, N_SERIAL);         // demo days print bulletins but never send ntfy
    return;
  }
  if (!strcmp(a, "vec")) {
    float x[BLOOM_NF];
    int n = 0;
    for (char *t; n < BLOOM_NF && (t = strtok(NULL, " \t,")); ) x[n++] = parseVal(t);
    if (n != BLOOM_NF) { Serial.printf("ERR vec needs %d numbers, got %d\n", BLOOM_NF, n); return; }
    printFeatures("vec", x);
    float p = bloom_prob(x);
    applyForecast(0, p, NAN, false, N_SILENT);
    Serial.printf("P vec p=%.6f %s\n", (double)p, p >= BLOOM_THRESHOLD ? "ALERT" : "idle");
    return;
  }
  char *b = strtok(NULL, " \t");
  char *c = strtok(NULL, " \t");
  if (!strcmp(a, "status")) { printStatus(); return; }
  if (!strcmp(a, "help")) { printHelp(); return; }
  if (!strcmp(a, "hist")) { printHist(); return; }
  if (!strcmp(a, "site")) {
    const char *n = restOf(raw, "site");
    if (*n) { siteName = n; prefs.putString("site", siteName); }
    Serial.printf("site=\"%s\"\n", siteName.c_str());
    return;
  }
  if (!strcmp(a, "selftest")) { selftestFails = run_selftest(); return; }
  if (!strcmp(a, "reset")) {
    hist_clear(&hist); clearAcc(0); alertOn = relayOn = false; lastP = NAN; lastDate = 0; setOutputs();
    prefs.remove("hist"); prefs.remove("acc");
    Serial.println("history cleared (calibration and climatology kept)");
    return;
  }
  if (!strcmp(a, "clim")) {
    if (b && c) {
      int m = atoi(b);
      if (m < 1 || m > 12) { Serial.println("ERR clim <month 1-12> <value|nan>"); return; }
      climTable[m] = parseVal(c);
      saveClim();
    }
    printClim();
    return;
  }
  if (!strcmp(a, "climclear")) { for (int m = 0; m < 13; m++) climTable[m] = NAN; saveClim(); printClim(); return; }
#if SENSOR_MODE
  if (!strcmp(a, "read")) { printSample(takeSample()); return; }
  if (!strcmp(a, "date")) {
    int32_t d = parse_date(b);
    int hh = 12, mm = 0;
    if (c) sscanf(c, "%d:%d", &hh, &mm);
    if (!d) { Serial.println("ERR date <yyyy-mm-dd> <hh:mm>"); return; }
    setClock(d, hh, mm);
    Serial.print("clock set to "); printDate(localDate()); Serial.printf(" %02d:%02d\n", hh, mm);
    return;
  }
  if (!strcmp(a, "blank")) { cal.blank = readFluor(); saveCal(); printCal(); return; }
  if (!strcmp(a, "chlk") && b) { cal.chlK = atof(b); saveCal(); printCal(); return; }
  if (!strcmp(a, "gain") && b) { setGain(tolower(b[0])); return; }
  if (!strcmp(a, "cal686")) { cal.v686 = readPhVolts(); saveCal(); printCal(); return; }
  if (!strcmp(a, "cal918")) { cal.v918 = readPhVolts(); saveCal(); printCal(); return; }
  if (!strcmp(a, "cal")) { printCal(); return; }
  if (!strcmp(a, "calclear")) { cal = {CAL_MAGIC, NAN, NAN, NAN, NAN, 'm'}; saveCal(); printCal(); return; }
#endif
#if USE_WIFI
  if (!strcmp(a, "wifi")) { wifiSsid = restOf(raw, "wifi"); prefs.putString("ssid", wifiSsid); WiFi.disconnect(); Serial.printf("ssid=\"%s\"\n", wifiSsid.c_str()); return; }
  if (!strcmp(a, "wifipass")) { wifiPass = restOf(raw, "wifipass"); prefs.putString("pass", wifiPass); WiFi.disconnect(); Serial.println("password stored"); return; }
  if (!strcmp(a, "ntfy")) { ntfyTopic = b ? b : ""; prefs.putString("topic", ntfyTopic); Serial.printf("ntfy topic=\"%s\"\n", ntfyTopic.c_str()); return; }
  if (!strcmp(a, "ntfytest")) { ntfySend("HAB buoy test", String("Test message from the buoy. last p=") + String(lastP, 3)); return; }
#else
  (void)raw; (void)restOf;
#endif
  Serial.println("? unknown command (send `help`)");
}

// ------------------------------------------------------------------ setup / loop
void blinkLed(int n, int ms) {
  for (int i = 0; i < n; i++) { digitalWrite(PIN_LED, HIGH); delay(ms); digitalWrite(PIN_LED, LOW); delay(ms); }
}

void setup() {
  pinMode(PIN_LED, OUTPUT);
  pinMode(PIN_RELAY, OUTPUT);
  pinMode(PIN_FLUOR_LED, OUTPUT);
  digitalWrite(PIN_FLUOR_LED, LOW);
  setOutputs();
  Serial.begin(115200);
  delay(500);
  Serial.println();
  Serial.println("buoy_esp32: Narragansett bloom forecast on the chip");
  selftestFails = run_selftest();
  blinkLed(selftestFails ? 10 : 3, selftestFails ? 60 : 200);   // 3 slow = pass, 10 fast = FAIL

  setenv("TZ", BUOY_TZ, 1); tzset();
  prefs.begin("buoy", false);
  for (int m = 0; m < 13; m++) climTable[m] = NAN;
  if (prefs.getBytesLength("clim") == sizeof(climTable)) prefs.getBytes("clim", climTable, sizeof(climTable));
  Cal stored;
  if (prefs.getBytesLength("cal") == sizeof(Cal) && prefs.getBytes("cal", &stored, sizeof(Cal)) && stored.magic == CAL_MAGIC) cal = stored;
  siteName = prefs.getString("site", "buoy");
  hist_clear(&hist);
  clearAcc(0);
#if SENSOR_MODE
  if (prefs.getBytesLength("hist") == sizeof(hist)) prefs.getBytes("hist", &hist, sizeof(hist));
  if (hist.n < 0 || hist.n > HIST_MAX) hist_clear(&hist);
  if (prefs.getBytesLength("acc") == sizeof(acc)) prefs.getBytes("acc", &acc, sizeof(acc));
  int64_t saved = prefs.getLong64("clock", 0);
  if (saved > 1600000000 && !clockOk()) { struct timeval tv; tv.tv_sec = (time_t)saved; tv.tv_usec = 0; settimeofday(&tv, NULL); }
  if (hist.n) Serial.printf("restored %ld days from NVS\n", (long)hist.n);
#endif
#if USE_DS18B20
  ds.begin();
#endif
#if USE_TSL2591 || USE_EZO_EC
  Wire.begin(PIN_SDA, PIN_SCL);
#endif
#if USE_TSL2591
  tslOk = tsl.begin();
  if (tslOk) {
    tsl.setTiming(TSL2591_INTEGRATIONTIME_200MS);
    char g = cal.gain;
    tsl.setGain(g == 'l' ? TSL2591_GAIN_LOW : g == 'h' ? TSL2591_GAIN_HIGH : g == 'x' ? TSL2591_GAIN_MAX : TSL2591_GAIN_MED);
  } else Serial.println("fluor: TSL2591 not found (check SDA 21 / SCL 22)");
#endif
#if USE_EZO_EC
  // Temperature compensation at 25 C = none: the EZO then reports conductivity at the water's own
  // temperature, which is what PSS-78 needs (we pass the DS18B20 temperature to it ourselves).
  if (ezoCmd("T,25", 300).length() == 0) Serial.println("ezo-ec: no reply at 0x64 (I2C mode? wiring?)");
#endif
#if USE_WIFI
  wifiSsid = prefs.getString("ssid", "");
  wifiPass = prefs.getString("pass", "");
  ntfyTopic = prefs.getString("topic", "");
  if (wifiSsid.length()) wifiUp(10000);
#endif
  if (hist.n) scoreLatest(N_SILENT);  // restore the LED/relay from the last stored day
  Serial.printf("READY mode=%s. Send `help`, or a day line, e.g.  day 2023-08-03 6.87 22.66 27.44 6.35\n",
                SENSOR_MODE ? "SENSOR" : "DEMO");
}

char buf[512];
size_t len = 0;
unsigned long lastSampleMs = 0;
bool firstSample = true;

void loop() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n' || ch == '\r') { buf[len] = '\0'; if (len) handleLine(buf); len = 0; }
    else if (len < sizeof(buf) - 1) buf[len++] = ch;
  }
#if SENSOR_MODE
  if ((firstSample && millis() > 10000) || millis() - lastSampleMs >= SAMPLE_MS) {
    firstSample = false;
    lastSampleMs = millis();
    sampleTick();
  }
#endif
}
