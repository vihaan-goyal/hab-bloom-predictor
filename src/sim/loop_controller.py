"""
loop_controller.py -- Layer 2, step 2: the ON/OFF loop as a day-by-day controller
==================================================================================
Step 2 of notes/mitigation/LAYER2_SIM_RESULTS.md. Layer 1 (src/models/control_loop_sim.py,
run_loop) replays the loop over a finished series. A treated tank changes its own chlorophyll, so
the loop has to decide one day at a time. `Controller.step` applies exactly run_loop's rules to a
batch of tanks at once:

    not ON:  start if the trigger fires today; next check = today + X; remember today's chl.
    ON:      on a check day with no reading, check again tomorrow;
             OFF if  p < T_off (= 0.8 T_on)  AND  chl < C_ok  AND  chl <= chl at the last check;
             else STOP if ON for >= MAX_ON (= 4 X) days; else next check = today + X.
    The OFF day itself counts as ON (as in run_loop); the tank can restart the next day.

--selftest feeds the Narragansett history (trigger = forecast p >= 0.50, C_ok = 5 ug/L) through
the controller and requires the same ON days and episodes as run_loop.

Triggers used in the tank simulation (method_mc.py):
    forecast  p >= T_on, with p from a persistence forecast of the tank's own readings
    rule      chl rose on 2 consecutive days AND chl > 2 x the warm-up mean (00_CONTROL_LOOP.md)

Run from repo root:
    python src/sim/loop_controller.py --selftest
"""
import argparse
import os
import sys

import numpy as np

T_ON = 0.50


class Controller:
    """Loop state for n tanks. X and MAX_ON in days."""

    def __init__(self, n, x_days, t_on=T_ON):
        self.x = np.broadcast_to(np.asarray(x_days, dtype=int), (n,)).copy()
        self.max_on = 4 * self.x
        self.t_on, self.t_off = t_on, 0.8 * t_on
        self.on = np.zeros(n, bool)
        self.start = np.zeros(n, int)
        self.check = np.zeros(n, int)
        self.last = np.full(n, np.nan)
        self.on_days = np.zeros(n, int)
        self.episodes = np.zeros(n, int)
        self.maxed = np.zeros(n, int)
        self.last_off = np.full(n, -1)

    def step(self, day, trigger, p, chl, c_ok, force_off=None):
        """Update all tanks after today's reading. trigger: bool array (start condition);
        p, chl: arrays (NaN allowed); c_ok: scalar or array; force_off: safety stop mask.
        Returns the bool array 'ON today' (includes a tank's OFF day)."""
        was = self.on.copy()
        on_today = was.copy()
        at_check = was & (day >= self.check)
        no_read = at_check & ~np.isfinite(chl)
        self.check = np.where(no_read, day + 1, self.check)
        read = at_check & np.isfinite(chl)
        not_rising = ~np.isfinite(self.last) | (chl <= self.last)
        stop_ok = read & np.isfinite(p) & (p < self.t_off) & (chl < c_ok) & not_rising
        maxed = read & ~stop_ok & (day - self.start >= self.max_on)
        cont = read & ~stop_ok & ~maxed
        self.last = np.where(cont, chl, self.last)
        self.check = np.where(cont, day + self.x, self.check)
        ended = stop_ok | maxed
        if force_off is not None:
            ended |= was & np.asarray(force_off, bool)
        self.maxed += maxed
        self.on = was & ~ended
        self.last_off = np.where(ended, day, self.last_off)
        # a tank that was OFF at the start of today may start (one that just stopped may not)
        start = ~was & np.asarray(trigger, bool)
        self.on |= start
        on_today |= start
        self.start = np.where(start, day, self.start)
        self.check = np.where(start, day + self.x, self.check)
        self.last = np.where(start, chl, self.last)
        self.episodes += start
        self.on_days += on_today
        return on_today


def rule_trigger(chl_hist, day, warm_mean):
    """chl rose on 2 consecutive days and today's chl > 2 x warm-up mean. chl_hist: (days, n)."""
    c0, c1, c2 = chl_hist[day - 2], chl_hist[day - 1], chl_hist[day]
    return (c1 > c0) & (c2 > c1) & (c2 > 2 * warm_mean)


def _selftest():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models"))
    import control_loop_sim as L1
    df = L1.load_narragansett()
    mism = checked = 0
    for x in (2, 3):
        for _, g in df.groupby("station"):
            g = g.sort_values("day")
            days, p, chl = g.day.values, g.p.values, g.chl.values
            ref_on, ref_eps = L1.run_loop(days, p, chl, T_ON, x)
            c = Controller(1, x)
            mine = np.zeros(len(days), bool)
            for i, d in enumerate(days):
                trig = np.array([np.isfinite(p[i]) and p[i] >= T_ON])
                mine[i] = c.step(int(d), trig, np.array([p[i]]), np.array([chl[i]]), L1.C_OK)[0]
            checked += len(days)
            mism += int((mine != ref_on).sum())
            mism += int(c.episodes[0] != len(ref_eps))
    print(f"selftest: {checked:,} station-days compared with run_loop (X = 2 and 3); mismatches: {mism}")
    assert mism == 0, "controller differs from run_loop"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    if ap.parse_args().selftest:
        _selftest()
