"""
tank_model.py -- Layer 2, step 1: algae in a treated tank (all five methods)
=============================================================================
Methods: seaweed and bubbles (below), plus peroxide (bag in: H2O2 rises to target x release
efficiency; out: first-order decay; Hill-shaped kill of small cells), curcumin (one pulse per ON
day up a 1 -> 2.5 -> top ladder; fast decay; Hill kill; the fluorometer under-reads while it is
present) and shellfish (bags in: filtering ramps up; clearance saturates at high algae; part of the
eaten nitrogen comes back as ammonia).
Step 1 of notes/mitigation/LAYER2_SIM_RESULTS.md. A well-mixed tank holds algae A (ug/L chl) and
nutrients N (ug/L chlorophyll-equivalent). Every tank in a batch is simulated at once (numpy
arrays), in hourly Euler steps, so thousands of Monte-Carlo tanks run together.

Model
    dA/dt = mu * g * N/(N+K) * A  -  loss*A  -  k*A  -  m*A
    dN/dt = -mu * g * N/(N+K) * A
    Integrated hourly with an exponential step (exact while rates are held for the hour),
    checked against scipy's solve_ivp.
    seaweed  k = k_max * D^h/(D^h + EC50^h) * S; the effect state S ramps toward 1 while the
             panel is in (time constant tau_ramp) and decays after it is lifted (tau_decay).
             pH = pH_base + rise_max * D/(D + D_half) * S (levels off, as kelp flasks stayed at
             8.1-8.9 up to 3 g/L); the loop pulls the panel if pH > 9.0.
    bubbles  g = r_on while bubbling (division pause); after 4 days of continuous bubbling an
             extra death rate m_late starts. After OFF, g restarts at r_recover and returns to
             1 with time constant tau_recover. Species respond differently (inhibited /
             unaffected / faster; Sullivan & Swift 2003): r_on is drawn per species class.
Not modelled: community shifts, nutrient uptake by the seaweed, light and temperature swings,
cell counts separate from chlorophyll, bacteria. Parameters come from other species and vessels.

Parameters: src/sim/method_params.csv (low / mid / high, each with source paper ids). Draws are
triangular. A draw is kept only if it reproduces the calibration experiment it came from
(`backtest`): seaweed 2 g/L on a diatom cuts cells 13-47% at 48 h and 74-94% at 72 h
(Sylvers & Gobler 2025, seaweed-03); bubbling an inhibited dinoflagellate at 0.6 L/min per L cuts
it 21-63% over 10 days (Sung & Gobler 2026, mixing-01). Both ranges widened by 10 points.

Outputs (main): printed baseline checks, Euler vs solve_ivp difference, back-test acceptance.

Run from repo root:
    python src/sim/tank_model.py
"""
import os

import numpy as np
import pandas as pd

PARAMS_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "method_params.csv")
DT = 1.0 / 24.0                 # days (hourly steps)
PH_LIMIT = 9.0                  # seaweed safety limit (02_SEAWEED.md)
BUBBLE_MORT_AFTER = 4.0         # days of continuous bubbling before extra mortality
SPECIES_CLASS_P = {"inhib": 0.3, "neutral": 0.4, "stim": 0.3}   # mixing-09: 3 / 4 / 3 of 10
BACKTEST = {
    "seaweed": {"t48": (0.03, 0.57), "t72": (0.64, 0.97)},   # seaweed-03, +/-10 points
    "bubbles": {"t10d": (0.11, 0.73)},                        # mixing-01, +/-10 points
    "peroxide": {"t24_1.6": (0.80, 1.00)},                    # peroxide-03: >90% at 1.6 mg/L, 24 h
    "curcumin": {"t24_5": (0.22, 0.99), "t24_3": (0.20, 0.70), "t24_1": (-0.10, 0.15)},
    # curcumin-01/-02: 5 mg/L -32% (2024) to -89% (2022) at 24 h; 3 mg/L -45%; 0.1-2 mg/L no effect
    # shellfish: no single calibration experiment; parameters used as drawn (see LAYER2 notes)
}
SEED = 42
MU_KEY = {"diatom": "mu_diatom", "dino": "mu_dino", "small": "mu_small"}
CURCUMIN_LADDER = (1.0, 2.5)                    # then ladder_top (04_CURCUMIN.md)
LN2 = np.log(2)


def hill(c, ec50, h):
    c = np.maximum(c, 0.0)
    return c ** h / (c ** h + ec50 ** h)


def load_params(path=PARAMS_CSV):
    return pd.read_csv(path)


def sample_params(method, n, rng, table=None):
    """Triangular draws (mode = mid) of the culture parameters plus the method's parameters."""
    t = load_params() if table is None else table
    rows = t[t.method.isin(["culture", method])]
    out = {}
    for r in rows.itertuples():
        lo, mid, hi = float(r.low), float(r.mid), float(r.high)
        out[r.param] = np.full(n, mid) if lo == hi else rng.triangular(lo, mid, hi, n)
    return out


class TankBatch:
    """A batch of tanks. `p` holds one value per tank for every parameter (arrays of length n).
    `organism` is 'diatom' or 'dino'; `method` is 'none', 'seaweed' or 'bubbles'."""

    def __init__(self, p, method, organism, a0=None, n0=None):
        self.p, self.method = p, method
        n = len(p["loss"])
        self.n = n
        self.mu = np.array(p[MU_KEY[organism]], dtype=float).copy()
        self.C = np.zeros(n)                        # peroxide / curcumin concentration (mg/L)
        self.maxC = np.zeros(n)
        self.F = np.zeros(n)                        # shellfish feeding activity (0..1)
        self.k_pulse = np.zeros(n, int)             # curcumin: pulse number within an episode
        self.prev_day_on = np.zeros(n, bool)
        self.A = np.array(p["a0"] if a0 is None else a0, dtype=float).copy()
        self.N = np.array(p["n0"] if n0 is None else n0, dtype=float).copy()
        self.S = np.zeros(n)                        # seaweed effect state (0..1)
        self.R = np.ones(n)                         # bubbles recovery multiplier
        self.cont_on = np.zeros(n)                  # bubbles: days of continuous bubbling
        self.was_on = np.zeros(n, dtype=bool)
        self.r_on = np.asarray(p.get("r_on", np.ones(n)), dtype=float)

    def ph(self):
        if self.method != "seaweed":
            return np.full(self.n, np.nan)
        d = self.p["dose"]
        return self.p["ph_base"] + self.p["ph_rise_max"] * d / (d + self.p["ph_half"]) * self.S

    def reading_factor(self):
        """Curcumin makes the fluorometer under-read (it absorbs near 470 nm)."""
        if self.method != "curcumin":
            return np.ones(self.n)
        return 1 - self.p["artefact"] * self.C / (self.C + 1.0)

    def step_day(self, on):
        """Advance one day with treatment on/off per tank (bool array). Returns the daily-mean A."""
        on = np.asarray(on, dtype=bool)
        p = self.p
        acc = np.zeros(self.n)
        if self.method == "curcumin":
            # one pulse at the start of each ON day, stepping up the ladder within an episode
            self.k_pulse = np.where(on & ~self.prev_day_on, 0, self.k_pulse)
            ladder = np.select([self.k_pulse == 0, self.k_pulse == 1], list(CURCUMIN_LADDER), p["ladder_top"])
            self.C = self.C + np.where(on, ladder, 0.0)
            self.k_pulse = np.where(on, self.k_pulse + 1, 0)
        self.prev_day_on = on.copy()
        for _ in range(24):
            g = np.ones(self.n)
            k = np.zeros(self.n)
            m = np.zeros(self.n)
            if self.method == "seaweed":
                target = on.astype(float)
                tau = np.where(on, p["tau_ramp"], p["tau_decay"])
                self.S += (target - self.S) * (1 - np.exp(-DT / tau))
                d = p["dose"]
                emax = d ** p["hill"] / (d ** p["hill"] + p["ec50"] ** p["hill"])
                k = p["k_max"] * emax * self.S
            elif self.method == "bubbles":
                started = on & ~self.was_on
                stopped = ~on & self.was_on
                self.cont_on = np.where(on, self.cont_on + DT, 0.0)
                slowed = self.r_on < 1
                # after OFF, growth restarts slowed (only for species that bubbling slowed)
                self.R = np.where(stopped & slowed, p["r_recover"], self.R)
                self.R = np.where(started, 1.0, self.R)
                self.R = np.where(~on, 1 - (1 - self.R) * np.exp(-DT / p["tau_recover"]), self.R)
                g = np.where(on, self.r_on, self.R)
                m = np.where(on & (self.cont_on > BUBBLE_MORT_AFTER) & slowed, p["m_late"], 0.0)
                self.was_on = on.copy()
            elif self.method == "peroxide":
                # bag in: H2O2 rises toward its release level; bag out: first-order decay
                level = p["target"] * p["release_eff"]
                self.C = np.where(on, self.C + (level - self.C) * (1 - np.exp(-DT / p["tau_release"])),
                                  self.C * np.exp(-LN2 * DT / p["half_life"]))
                m = p["m_max"] * hill(self.C, p["ec50"], p["hill"])
            elif self.method == "curcumin":
                self.C = self.C * np.exp(-LN2 * DT / p["half_life"])
                m = p["m_max"] * hill(self.C, p["ec50"], p["hill"])
            elif self.method == "shellfish":
                # bags in: animals open over tau_open; bags out: no filtering
                self.F = np.where(on, self.F + (1 - self.F) * (1 - np.exp(-DT / p["tau_open"])), 0.0)
                k = self.F * p["clear_vol_per_day"] * p["real_frac"] / (1 + self.A / p["a_sat"])
                self.N = self.N + p["recycle"] * k * self.A * DT     # excreted ammonia feeds regrowth
            self.maxC = np.maximum(self.maxC, self.C)
            # exponential step: exact for rates held constant over the hour
            gr = self.mu * g * self.N / (self.N + p["k_n"])          # per-capita growth
            r = gr - (p["loss"] + k + m)                              # net per-capita rate
            e = np.exp(r * DT)
            mean_a = np.where(np.abs(r) > 1e-9, self.A * (e - 1) / np.where(np.abs(r) > 1e-9, r, 1), self.A * DT)
            used = np.minimum(gr * mean_a, self.N)                    # nutrients taken up this hour
            self.A = np.maximum(self.A * e, 1e-6)
            self.N = self.N - used
            acc += self.A
        return acc / 24.0


def assign_species(p, rng, screened):
    """Bubbles only: pick each draw's species response. screened=True keeps inhibited species
    only (the pilot screen's pass condition)."""
    n = len(p["r_on_inhib"])
    if screened:
        cls = np.array(["inhib"] * n)
    else:
        cls = rng.choice(list(SPECIES_CLASS_P), size=n, p=list(SPECIES_CLASS_P.values()))
    base = np.select([cls == "inhib", cls == "neutral"], [p["r_on_inhib"], p["r_on_neutral"]], p["r_on_stim"])
    frac = np.where(p["rate"] >= 0.3, 1.0, p["low_rate_factor"])   # low rate keeps part of the effect
    p["r_on"] = 1 - (1 - base) * frac
    p["species_class"] = cls
    return p


def backtest(method, p):
    """Re-run the calibration experiment for each draw. Returns {target: reduction array}."""
    n = len(p["loss"])
    q = dict(p)
    big_n = np.full(n, 1e7)                          # nutrient-replete flasks
    if method == "seaweed":
        q["dose"] = np.full(n, 2.0)
        ctl = TankBatch(q, "none", "diatom", a0=np.ones(n), n0=big_n)
        trt = TankBatch(q, "seaweed", "diatom", a0=np.ones(n), n0=big_n)
        out = {}
        for day in range(1, 4):
            ctl.step_day(np.zeros(n, bool))
            trt.step_day(np.ones(n, bool))
            if day in (2, 3):
                out["t48" if day == 2 else "t72"] = 1 - trt.A / ctl.A
        return out
    if method == "bubbles":
        q["r_on"] = q["r_on_inhib"].copy()          # Sung & Gobler's species was inhibited
        ctl = TankBatch(q, "none", "dino", a0=np.ones(n), n0=big_n)
        trt = TankBatch(q, "bubbles", "dino", a0=np.ones(n), n0=big_n)
        for _ in range(10):
            ctl.step_day(np.zeros(n, bool))
            trt.step_day(np.ones(n, bool))
        return {"t10d": 1 - trt.A / ctl.A}
    if method == "peroxide":
        q["target"] = np.full(n, 1.6)
        ctl = TankBatch(q, "none", "small", a0=np.ones(n), n0=big_n)
        trt = TankBatch(q, "peroxide", "small", a0=np.ones(n), n0=big_n)
        ctl.step_day(np.zeros(n, bool))
        trt.step_day(np.ones(n, bool))
        return {"t24_1.6": 1 - trt.A / ctl.A}
    if method == "curcumin":
        out = {}
        for dose, key in ((5.0, "t24_5"), (3.0, "t24_3"), (1.0, "t24_1")):
            ctl = TankBatch(q, "none", "dino", a0=np.ones(n), n0=big_n)
            trt = TankBatch(q, "curcumin", "dino", a0=np.ones(n), n0=big_n)
            trt.C = np.full(n, dose)                  # one dose, no more pulses
            ctl.step_day(np.zeros(n, bool))
            trt.step_day(np.zeros(n, bool))
            out[key] = 1 - trt.A / ctl.A
        return out
    raise ValueError(method)


def accepted_draws(method, n_keep, rng, max_tries=40):
    """Draw parameters until n_keep pass the back-test. Returns (params, acceptance rate)."""
    if method not in BACKTEST:
        return sample_params(method, n_keep, rng), 1.0
    kept, tried, n_ok = [], 0, 0
    while n_ok < n_keep and tried < max_tries * n_keep:
        m = 4 * n_keep
        p = sample_params(method, m, rng)
        tried += m
        bt = backtest(method, p)
        ok = np.ones(m, bool)
        for key, (lo, hi) in BACKTEST[method].items():
            ok &= (bt[key] >= lo) & (bt[key] <= hi)
        kept.append({k: v[ok] for k, v in p.items()})
        n_ok += int(ok.sum())
    allp = {k: np.concatenate([d[k] for d in kept])[:n_keep] for k in kept[0]}
    return allp, n_ok / tried


def _check_baseline():
    """Untreated bloom: warm-up, nutrient pulse on day 21, peak, decline. Euler vs solve_ivp."""
    from scipy.integrate import solve_ivp
    p = {r.param: np.array([float(r.mid)]) for r in load_params().itertuples()
         if r.method in ("culture", "seaweed")}
    tank = TankBatch(p, "none", "diatom")
    daily = []
    for day in range(56):
        if day == 21:
            tank.N += p["n_pulse"]
        daily.append(tank.step_day(np.zeros(1, bool))[0])
    daily = np.array(daily)
    peak_day = int(np.argmax(daily))
    print(f"baseline (mid values): warm-up day 20 chl {daily[20]:.2f} ug/L, peak {daily.max():.1f} ug/L "
          f"on day {peak_day}, day 55 {daily[55]:.1f} ug/L")
    assert daily[20] < 10 and daily.max() > 30 and peak_day > 21 and daily[55] < daily.max(), "bloom shape"

    mu, kn, loss = p["mu_diatom"][0], p["k_n"][0], p["loss"][0]

    def rhs(_, y):
        a, nn = y
        gr = mu * max(nn, 0) / (max(nn, 0) + kn) * a
        return [gr - loss * a, -gr]
    y0 = [p["a0"][0], p["n0"][0] + p["n_pulse"][0]]
    sol = solve_ivp(rhs, (0, 20), y0, method="LSODA", rtol=1e-8, atol=1e-10, dense_output=True)
    tank = TankBatch(p, "none", "diatom", a0=np.array([y0[0]]), n0=np.array([y0[1]]))
    worst = 0.0
    for day in range(1, 21):
        tank.step_day(np.zeros(1, bool))
        ref = sol.sol(day)[0]
        worst = max(worst, abs(tank.A[0] - ref) / ref)
    print(f"hourly step vs solve_ivp over 20 days: worst relative difference {worst:.2%}")
    assert worst < 0.01, "hourly step too coarse"


def main():
    _check_baseline()
    rng = np.random.default_rng(SEED)
    for method in ("seaweed", "bubbles", "peroxide", "curcumin"):
        p, rate = accepted_draws(method, 2000, rng)
        bt = backtest(method, p)
        desc = ", ".join(f"{k} median {np.median(v):.0%} [{np.percentile(v, 5):.0%}, {np.percentile(v, 95):.0%}]"
                         for k, v in bt.items())
        print(f"{method}: back-test acceptance {rate:.0%}; accepted draws reproduce {desc}")
        show = {"seaweed": ("k_max", "ec50", "tau_ramp"), "bubbles": ("r_on_inhib", "m_late"),
                "peroxide": ("m_max", "ec50"), "curcumin": ("m_max", "half_life", "ec50")}[method]
        for k in show:
            print(f"    accepted {k}: median {np.median(p[k]):.2f} "
                  f"[{np.percentile(p[k], 5):.2f}, {np.percentile(p[k], 95):.2f}]")


if __name__ == "__main__":
    main()
