/* features.h -- the 23 model features from a rolling daily history, exactly as the fork builds them
   ==============================================================================================
   Reference (Narragansett fork): src/features/build_narragansett_daily.py and
   predict_anywhere.py::build_daily. Rules matched here:

   - A history ROW is one station-day that survived the daily filter (>= MIN_READINGS = 48 chl
     readings that day). Days that failed the filter are NOT rows: training dropped them before any
     lag or rolling mean was computed.
   - chl_lagk, sal_lagk, do_lag1, temp_lag1 = pandas shift(k) over the station's ROWS. A gap of
     several calendar days is skipped over, not filled: "lag1" is the previous row, whatever its date.
   - chl_rollW_mean = rolling(W, min_periods = max(2, W/3)).mean() over ROWS, current row included.
     So roll3/roll6 need >= 2 rows, roll9 >= 3, roll14 >= 4, roll21 >= 7; otherwise NaN.
   - chl_trend = chl - chl_roll6_mean;  chl_anomaly = chl - chl_climatology.
   - month = calendar month of the row's date.
   - chl_climatology: in training, the station x 15-day-bin mean over PRIOR years (>= 3 days). A
     buoy with weeks of history cannot compute that, so it comes from (1) a per-day override (the
     replay tool sends the fork's value), else (2) the per-month table loaded with `clim <m> <v>`,
     else (3) NaN, which bloom_prob() replaces with the training median.
   - Any NaN input is median-filled inside bloom_prob(), as in training (fillna(medians)).

   Plain C++, no Arduino calls: the same file compiles on a PC for testing.
*/
#ifndef BUOY_FEATURES_H
#define BUOY_FEATURES_H
#include <math.h>
#include <stdint.h>
#include <string.h>

#define MIN_READINGS 48   // build_narragansett_daily.py MIN_READINGS: chl readings needed for a day
#define HIST_MAX 30       // rows kept; the longest window is 21

/* feature indices, in BLOOM_FEATURES order (selftest checks the names against bloom_model.h) */
enum {
  F_CHL, F_CHL_LAG1, F_CHL_LAG2, F_CHL_LAG3, F_CHL_LAG4,
  F_ROLL3, F_ROLL6, F_ROLL9, F_ROLL14, F_ROLL21,
  F_TREND, F_ANOM, F_CLIM, F_DO, F_DO_LAG1, F_TEMP, F_TEMP_LAG1,
  F_SAL, F_SAL_LAG1, F_SAL_LAG2, F_SAL_LAG3, F_SAL_LAG4, F_MONTH, F_COUNT
};
static const char *const FEAT_NAMES[F_COUNT] = {
  "chl", "chl_lag1", "chl_lag2", "chl_lag3", "chl_lag4",
  "chl_roll3_mean", "chl_roll6_mean", "chl_roll9_mean", "chl_roll14_mean", "chl_roll21_mean",
  "chl_trend", "chl_anomaly", "chl_climatology", "do", "do_lag1", "temp", "temp_lag1",
  "sal", "sal_lag1", "sal_lag2", "sal_lag3", "sal_lag4", "month",
};

/* one daily row: daily MEANS of the sub-daily readings. clim = per-day override (NAN = use table) */
struct DayRec { int32_t date; float chl, temp, sal, dox, clim; };
struct History { int32_t n; DayRec r[HIST_MAX]; };   // r[0] oldest ... r[n-1] newest

static inline int date_month(int32_t yyyymmdd) { return (int)((yyyymmdd / 100) % 100); }

static void hist_clear(History *h) { memset(h, 0, sizeof(*h)); h->n = 0; }

/* returns 0 = appended, 1 = replaced the newest row (same date), -1 = older than the newest row */
static int hist_push(History *h, const DayRec &d) {
  if (h->n > 0) {
    int32_t last = h->r[h->n - 1].date;
    if (d.date == last) { h->r[h->n - 1] = d; return 1; }
    if (d.date < last) return -1;
  }
  if (h->n == HIST_MAX) { memmove(&h->r[0], &h->r[1], (HIST_MAX - 1) * sizeof(DayRec)); h->n--; }
  h->r[h->n++] = d;
  return 0;
}

/* value k rows back from the newest (k = 0 is the newest row) */
static float hist_back(const History *h, int k, int field) {
  int i = h->n - 1 - k;
  if (i < 0) return NAN;
  const DayRec &d = h->r[i];
  switch (field) { case 0: return d.chl; case 1: return d.temp; case 2: return d.sal; default: return d.dox; }
}

/* pandas rolling(w, min_periods=max(2, w//3)).mean() of chl at the newest row */
static float roll_mean(const History *h, int w) {
  int minp = w / 3 > 2 ? w / 3 : 2;
  double s = 0; int cnt = 0;
  for (int k = 0; k < w && k < h->n; k++) {
    float v = h->r[h->n - 1 - k].chl;
    if (!isnan(v)) { s += v; cnt++; }
  }
  return cnt >= minp ? (float)(s / cnt) : NAN;
}

/* climTable[1..12]: per-month climatology (NAN = unknown). Fills x[F_COUNT] for the newest row. */
static void build_features(const History *h, const float climTable[13], float x[F_COUNT]) {
  for (int i = 0; i < F_COUNT; i++) x[i] = NAN;
  if (h->n == 0) return;
  const DayRec &d = h->r[h->n - 1];
  x[F_CHL] = d.chl;
  for (int k = 1; k <= 4; k++) { x[F_CHL_LAG1 + k - 1] = hist_back(h, k, 0); x[F_SAL_LAG1 + k - 1] = hist_back(h, k, 2); }
  x[F_ROLL3] = roll_mean(h, 3);  x[F_ROLL6] = roll_mean(h, 6);  x[F_ROLL9] = roll_mean(h, 9);
  x[F_ROLL14] = roll_mean(h, 14); x[F_ROLL21] = roll_mean(h, 21);
  x[F_TREND] = d.chl - x[F_ROLL6];
  int m = date_month(d.date);
  float clim = !isnan(d.clim) ? d.clim : ((m >= 1 && m <= 12) ? climTable[m] : NAN);
  x[F_CLIM] = clim;
  x[F_ANOM] = d.chl - clim;
  x[F_DO] = d.dox;   x[F_DO_LAG1] = hist_back(h, 1, 3);
  x[F_TEMP] = d.temp; x[F_TEMP_LAG1] = hist_back(h, 1, 1);
  x[F_SAL] = d.sal;
  x[F_MONTH] = (float)m;
}

/* "2023-08-31" -> 20230831; 0 if malformed */
static inline int32_t parse_date(const char *s) {
  if (!s) return 0;
  int y = 0, mo = 0, dd = 0;
  for (int i = 0; i < 10; i++) {
    char c = s[i];
    if (i == 4 || i == 7) { if (c != '-') return 0; continue; }
    if (c < '0' || c > '9') return 0;
    int v = c - '0';
    if (i < 4) y = y * 10 + v; else if (i < 7) mo = mo * 10 + v; else dd = dd * 10 + v;
  }
  if (s[10] != '\0' || y < 1900 || mo < 1 || mo > 12 || dd < 1 || dd > 31) return 0;
  return y * 10000 + mo * 100 + dd;
}
#endif
