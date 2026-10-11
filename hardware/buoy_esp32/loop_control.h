/*
  loop_control.h -- the forecast-triggered treatment ON/OFF rules, ported from the Uno alerter
  ===========================================================================================
  Same rules as hardware/alerter_uno/alerter_uno.ino (stepDay), src/sim/loop_controller.py
  (Controller.step, n = 1) and notes/mitigation/00_CONTROL_LOOP.md:

    not ON:  start if the trigger fires today; next check = today + X; remember today's chl.
    ON:      on a check day, OFF if  p < T_off (= 0.8 T_on)  AND  chl < C_ok  AND  chl <= chl at the
             last check; else STOP if ON for >= MAX_ON (= 4 X, or maxOnDays) days; else next check =
             today + X.
             FLOOR: 2 readings in a row below floorFrac x warm-up mean while ON -> OFF (H4).
    The OFF day itself counts as ON; the tank can restart the next day.

  Triggers:  mode F (forecast)  p >= T_on
             mode R (rule)      chl rose 2 calendar days in a row AND chl > 2 x warm-up mean
             mode H (handover)  forecast, but if the rule fires and the forecast has not started
                                the tank 2 days later, the rule starts it

  Pure C++ (no Arduino calls), so the same file is compiled on the PC and checked against the
  Python controller: check_loop_port.py. Days are calendar-day numbers (loop_day_number).
*/
#ifndef LOOP_CONTROL_H
#define LOOP_CONTROL_H

#include <math.h>
#include <stdint.h>

#define LOOP_FLOOR_DAYS 2
#define LOOP_HANDOVER_DAYS 2
#define LOOP_NO_DAY (-100000)

struct LoopCfg {
  uint32_t magic;
  float tOn, cOk, warmMean, floorFrac;
  int32_t X, maxOnDays;          // maxOnDays 0 = 4 x X
  char mode;                     // 'F', 'R' or 'H'
  uint16_t pulseSec;             // 0 = relay held for the whole ON episode (air pump)
};

struct LoopState {
  uint32_t magic;
  bool on, warn, safetyStop, skipNext;
  int32_t startDay, checkDay, histDay, pendingDay, episodes, belowCount;
  float lastChl, chlHist[3];     // chlHist = [day-2, day-1, today] by calendar day (NAN = no reading)
};

struct LoopOut { bool started, ended, maxed, floorHit, recheck, dose, skipped; };

static const uint32_t LOOP_CFG_MAGIC = 0x100FC001, LOOP_STATE_MAGIC = 0x100F5001;

static inline void loop_defaults(LoopCfg &c, float tOn) {
  c.magic = LOOP_CFG_MAGIC;
  c.tOn = tOn; c.cOk = 5.0f; c.warmMean = NAN; c.floorFrac = 0.8f;
  c.X = 3; c.maxOnDays = 0; c.mode = 'F'; c.pulseSec = 0;
}

static inline void loop_reset(LoopState &s) {
  s.magic = LOOP_STATE_MAGIC;
  s.on = s.warn = s.safetyStop = s.skipNext = false;
  s.startDay = s.checkDay = 0; s.histDay = LOOP_NO_DAY; s.pendingDay = -1;
  s.episodes = s.belowCount = 0;
  s.lastChl = NAN;
  s.chlHist[0] = s.chlHist[1] = s.chlHist[2] = NAN;
}

/* yyyymmdd -> days since 1970-01-01 (proleptic Gregorian), so day arithmetic is calendar days */
static inline int32_t loop_day_number(int32_t yyyymmdd) {
  int32_t y = yyyymmdd / 10000, m = yyyymmdd / 100 % 100, d = yyyymmdd % 100;
  y -= m <= 2;
  int32_t era = (y >= 0 ? y : y - 399) / 400;
  int32_t yoe = y - era * 400;
  int32_t doy = (153 * (m + (m > 2 ? -3 : 9)) + 2) / 5 + d - 1;
  int32_t doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
  return era * 146097 + doe - 719468;
}

/* the inverse: day number -> yyyymmdd */
static inline int32_t loop_date_of(int32_t z) {
  z += 719468;
  int32_t era = (z >= 0 ? z : z - 146096) / 146097;
  int32_t doe = z - era * 146097;
  int32_t yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365;
  int32_t y = yoe + era * 400;
  int32_t doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
  int32_t mp = (5 * doy + 2) / 153;
  int32_t d = doy - (153 * mp + 2) / 5 + 1;
  int32_t m = mp < 10 ? mp + 3 : mp - 9;
  return (y + (m <= 2)) * 10000 + m * 100 + d;
}

static inline void loop_push_hist(LoopState &s, float v) {
  s.chlHist[0] = s.chlHist[1]; s.chlHist[1] = s.chlHist[2]; s.chlHist[2] = v;
}

static inline bool loop_rule_trigger(const LoopCfg &c, const LoopState &s) {
  return !isnan(s.chlHist[0]) && !isnan(s.chlHist[1]) && !isnan(s.chlHist[2]) && !isnan(c.warmMean)
      && s.chlHist[1] > s.chlHist[0] && s.chlHist[2] > s.chlHist[1] && s.chlHist[2] > 2 * c.warmMean;
}

/* one calendar day: p = forecast, chl = that day's reading (NAN = none). `day` must be later than
   the last stepped day. Line for line the Uno's stepDay, without its outputs. */
static inline LoopOut loop_step(const LoopCfg &c, LoopState &s, int32_t day, float p, float chl) {
  for (int32_t g = s.histDay + 1; g < day && g < s.histDay + 4; g++) loop_push_hist(s, NAN);   // skipped days
  loop_push_hist(s, chl);
  s.histDay = day;
  bool rule = loop_rule_trigger(c, s);
  bool fc = !isnan(p) && p >= c.tOn;
  bool trig = (c.mode == 'R') ? rule : fc;
  float tOff = 0.8f * c.tOn;
  int32_t maxOn = c.maxOnDays > 0 ? c.maxOnDays : 4 * c.X;

  LoopOut o = {false, false, false, false, false, false, false};
  bool was = s.on;
  s.warn = false;
  if (was && day >= s.checkDay) {
    if (isnan(chl)) {
      s.checkDay = day + 1;
      s.warn = true;                                  // re-measure day with no reading
    } else {
      bool notRising = isnan(s.lastChl) || chl <= s.lastChl;
      bool stopOk = !isnan(p) && p < tOff && chl < c.cOk && notRising;
      o.maxed = !stopOk && (day - s.startDay >= maxOn);
      if (!stopOk && !o.maxed) { s.lastChl = chl; s.checkDay = day + c.X; o.recheck = true; }
      o.ended = stopOk || o.maxed;
    }
  }
  if (was && s.safetyStop) { o.ended = true; s.warn = true; }
  s.safetyStop = false;
  // floor rule (H4): LOOP_FLOOR_DAYS readings in a row below floorFrac x warm-up mean while ON
  if (was && !isnan(chl)) {
    if (c.floorFrac > 0 && !isnan(c.warmMean) && chl < c.floorFrac * c.warmMean) s.belowCount++;
    else s.belowCount = 0;
  }
  if (was && !o.ended && s.belowCount >= LOOP_FLOOR_DAYS) { o.ended = true; o.floorHit = true; }
  s.on = was && !o.ended;
  if (!s.on) s.belowCount = 0;
  // handover (mode H): rule fired while idle, forecast silent LOOP_HANDOVER_DAYS later -> start
  if (c.mode == 'H') {
    if (o.ended) s.pendingDay = -1;
    if (!was && rule && s.pendingDay < 0) s.pendingDay = day;
    if (!was && s.pendingDay >= 0 && day - s.pendingDay >= LOOP_HANDOVER_DAYS) trig = true;
  }
  if (!was && trig) {
    s.on = true; o.started = true; s.pendingDay = -1;
    s.startDay = day; s.checkDay = day + c.X; s.lastChl = chl; s.episodes++;
  }
  // pulse mode: one timed pump run at START and at each check day that continues the episode
  o.dose = c.pulseSec > 0 && (o.started || (s.on && o.recheck));
  o.skipped = o.dose && s.skipNext;
  if (o.dose) s.skipNext = false;
  return o;
}

static inline const char *loop_label(const LoopState &s, const LoopOut &o, bool was) {
  if (o.started) return "START";
  if (was && o.ended) return o.maxed ? "STOP_MAX_ON" : o.floorHit ? "OFF_FLOOR" : "OFF";
  return s.on ? "ON" : "idle";
}

#endif
