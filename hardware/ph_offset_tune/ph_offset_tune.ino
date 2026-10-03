/*
  ph_offset_tune.ino -- pH board check without buffers: auto-reads Po (A2) twice a second
  ======================================================================================
  1. Zero point: probe in tap water, wait for "steady", then turn the potentiometer nearest the BNC
     until ph_v is about 2.50 V (tap water is ~pH 7-8, so 2.4-2.5 V is fine; the buffer calibration
     in alerter_uno.ino fixes the exact numbers later).
  2. Kitchen check (does the probe respond?). Rinse the probe between liquids, wait for "steady", then
     type one letter + Enter to record that liquid:
        t = tap water    v = vinegar (~pH 3)    b = baking soda, 1 tsp per cup (~pH 8.3)
     After all three, it prints PASS if vinegar reads clearly higher than tap and baking soda lower.
  Serial Monitor at 115200, "Newline". Re-upload alerter_uno.ino afterwards.
*/
const int PIN_PH = A2;
const float STEADY_V = 0.005;      // max change over the last 10 readings (~5 s) to count as settled
const float VINEGAR_MIN_RISE = 0.30;
float hist[10];
int n = 0;
float vTap = NAN, vVin = NAN, vSoda = NAN;

float readVolts() {                // average of 40 readings, like the alerter
  long s = 0;
  for (int i = 0; i < 40; i++) { s += analogRead(PIN_PH); delay(3); }
  return s / 40.0 * 5.0 / 1023.0;
}

float recentMean() {
  int k = min(n, 10); float s = 0;
  for (int i = 0; i < k; i++) s += hist[i];
  return k ? s / k : NAN;
}

bool isSteady() {
  if (n < 10) return false;
  float lo = hist[0], hi = hist[0];
  for (int i = 1; i < 10; i++) { lo = min(lo, hist[i]); hi = max(hi, hist[i]); }
  return hi - lo < STEADY_V;
}

void verdict() {
  if (isnan(vTap) || isnan(vVin) || isnan(vSoda)) return;
  Serial.print(F("RESULT tap=")); Serial.print(vTap, 3);
  Serial.print(F(" vinegar=")); Serial.print(vVin, 3);
  Serial.print(F(" soda=")); Serial.print(vSoda, 3);
  bool vinOk = vVin - vTap >= VINEGAR_MIN_RISE, sodaOk = vSoda < vTap;
  if (vinOk && sodaOk) Serial.println(F("  -> PASS: probe responds (acid up, base down). Order buffers to calibrate."));
  else {
    Serial.print(F("  -> CHECK:"));
    if (!vinOk) Serial.print(F(" vinegar should read at least 0.30 V above tap;"));
    if (!sodaOk) Serial.print(F(" baking soda should read below tap;"));
    Serial.println(F(" rinse, wait longer for steady, and retry."));
  }
}

void setup() {
  Serial.begin(115200);
  Serial.println(F("ph_offset_tune: Po on A2. Tap water: tune to ~2.50 V. Then t / v / b to record liquids."));
}

void loop() {
  if (Serial.available()) {
    char c = tolower(Serial.read());
    if (c == 't' || c == 'v' || c == 'b') {
      float m = recentMean();
      if (!isSteady()) Serial.println(F("(not steady yet: recorded anyway, retake if it keeps drifting)"));
      if (c == 't') vTap = m; else if (c == 'v') vVin = m; else vSoda = m;
      Serial.print(F("recorded ")); Serial.print(c == 't' ? F("tap") : c == 'v' ? F("vinegar") : F("baking soda"));
      Serial.print(F(" = ")); Serial.println(m, 3);
      verdict();
    }
  }
  float v = readVolts();
  hist[n % 10] = v; n++;
  Serial.print(F("ph_v=")); Serial.print(v, 3);
  Serial.print(F("  off 2.50 by ")); Serial.print(v - 2.5, 3);
  if (isSteady()) Serial.print(F("  steady"));
  Serial.println();
  delay(380);                      // ~2 lines per second with the 120 ms read
}
