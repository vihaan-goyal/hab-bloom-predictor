/* selftest.h -- boot self-test, shared by the ESP32 sketch and a PC build (same code on both)
   =========================================================================================
   Define ST_PRINTF(...) before including (Serial.printf on the board, printf on a PC).
   Checks:
     1. names:    features.h's feature order == BLOOM_FEATURES in bloom_model.h
     2. model:    bloom_prob() on TV_N real rows vs Python predict_proba (test_vectors.h);
                  PASS if |C - Python| < 2e-3 and both make the same alert decision at BLOOM_THRESHOLD
     3. features: 29 real consecutive days pushed through features.h; the last 8 rows' 23 features
                  must equal the fork's precomputed columns (|diff| <= 1e-3 + 1e-4 |value|, NaN == NaN)
     4. PSS-78:   the two UNESCO reference values in pss78.h (|dS| < 1e-3)
   Returns the number of failures (0 = all passed).
*/
#ifndef BUOY_SELFTEST_H
#define BUOY_SELFTEST_H
#include <string.h>
#include "bloom_model.h"
#include "features.h"
#include "pss78.h"
#include "test_vectors.h"

#define ST_TOL_P 2e-3

static int run_selftest() {
  int fails = 0;
  ST_PRINTF("SELFTEST begin: model %d trees, %d features, threshold %.2f, horizon %d d\n",
            BLOOM_NTREES, BLOOM_NF, (double)BLOOM_THRESHOLD, BLOOM_HORIZON_DAYS);

  // 1. feature names
  int bad = (BLOOM_NF != F_COUNT);
  for (int i = 0; !bad && i < BLOOM_NF; i++) if (strcmp(BLOOM_FEATURES[i], FEAT_NAMES[i])) bad = 1;
  ST_PRINTF("  [names]    feature order matches bloom_model.h: %s\n", bad ? "FAIL" : "PASS");
  fails += bad;

  // 2. model vectors
  ST_PRINTF("  [model]    %-16s %10s %10s %10s  decision\n", "row", "C", "Python", "diff");
  for (int i = 0; i < TV_N; i++) {
    float pc = bloom_prob(TV_X[i]);
    double d = (double)pc - TV_P[i];
    bool aC = pc >= BLOOM_THRESHOLD, aP = TV_P[i] >= (double)BLOOM_THRESHOLD;
    bool ok = fabs(d) < ST_TOL_P && aC == aP;
    ST_PRINTF("  [model]    %-16s %10.6f %10.6f %+10.2e  %s/%s %s\n", TV_LABEL[i], (double)pc, TV_P[i], d,
              aC ? "ALERT" : "idle", aP ? "ALERT" : "idle", ok ? "PASS" : "FAIL");
    if (!ok) fails++;
  }

  // 3. feature engine on a real 29-day history
  static History h;           // static: keeps ~0.7 KB off the stack
  static const float noClim[13] = {NAN, NAN, NAN, NAN, NAN, NAN, NAN, NAN, NAN, NAN, NAN, NAN, NAN};
  hist_clear(&h);
  double worst = 0; int featBad = 0;
  for (int i = 0; i < HT_N; i++) {
    DayRec r = {(int32_t)HT_DATE[i], HT_ROW[i][0], HT_ROW[i][1], HT_ROW[i][2], HT_ROW[i][3], HT_ROW[i][4]};
    hist_push(&h, r);
    int j = i - (HT_N - HT_CHECK);
    if (j < 0) continue;
    float x[F_COUNT];
    build_features(&h, noClim, x);
    for (int f = 0; f < F_COUNT; f++) {
      float e = HT_EXPECT[j][f];
      if (isnan(e) || isnan(x[f])) { if (isnan(e) != isnan(x[f])) { featBad++; ST_PRINTF("  [features] %ld %s: got %g want %g\n", HT_DATE[i], FEAT_NAMES[f], (double)x[f], (double)e); } continue; }
      double d = fabs((double)x[f] - e);
      if (d > worst) worst = d;
      if (d > 1e-3 + 1e-4 * fabs(e)) { featBad++; ST_PRINTF("  [features] %ld %s: got %g want %g\n", HT_DATE[i], FEAT_NAMES[f], (double)x[f], (double)e); }
    }
  }
  ST_PRINTF("  [features] %d days x %d features vs fork columns: max |diff| %.2e  %s\n",
            HT_CHECK, F_COUNT, worst, featBad ? "FAIL" : "PASS");
  fails += featBad ? 1 : 0;

  // 4. PSS-78 reference values (inputs given in IPTS-68, converted to the ITS-90 the function takes)
  double s1 = pss78_salinity(PSS78_C35, 15.0 / 1.00024, 0.0);
  double s2 = pss78_salinity(1.888091 * PSS78_C35, 40.0 / 1.00024, 10000.0);
  bool okS = fabs(s1 - 35.0) < 1e-3 && fabs(s2 - 40.0) < 1e-3;
  ST_PRINTF("  [pss78]    S(R=1,15C,0)=%.4f (35)  S(R=1.888091,40C,10000dbar)=%.4f (40)  %s\n",
            s1, s2, okS ? "PASS" : "FAIL");
  fails += okS ? 0 : 1;

  ST_PRINTF("SELFTEST %s (%d failure%s)\n", fails ? "FAIL" : "PASS", fails, fails == 1 ? "" : "s");
  return fails;
}
#endif
