"""
tiered_dosing.py -- Layer 2 add-on: does TIERED peroxide dosing cut false-alarm harm? (exploratory)
=====================================================================================================
Exploratory, not pre-registered (2026-10-04). Compares three dosing strategies for the peroxide loop
(0.8 mg/L pulses, re-dose only if the residual is <= 0.5 mg/L, MAX_ON 3, X = 1 d) on the SAME
accepted parameter draws and the SAME tank / fluorometer / forecast noise (common random numbers:
the bench noise generator is re-seeded identically for every strategy).

    FULL       current plan: full 0.8 mg/L pulse from the first ON day, then the normal rules.
    TIERED_P   first pulse of an episode is half (0.4 mg/L); at the next check the tank goes on to
               full pulses only if CONFIRMED, otherwise it is switched OFF.
    TIERED_A   aeration ON at START (bubbles parameters from method_params.csv); switch to full
               peroxide pulses (aeration off) only once CONFIRMED; otherwise aeration runs until the
               normal OFF rule (or MAX_ON).

    CONFIRMED  (forecast p >= T_on) AND (rule trigger holds  OR  chl today > chl at START), where the
               rule trigger is loop_controller.rule_trigger (chl up 2 days running and > 2 x warm-up
               mean). Once a tank is confirmed it stays confirmed (later episodes start at full dose).
    MAX_ON     3 days per episode as in method_mc. TIERED_P: the half pulse counts as pulse 1 of 3.
               TIERED_A: the aeration days do not count; the 3-pulse peroxide clock starts at
               confirmation.

Model
    tank_model.TankBatch (peroxide, small-celled alga) with the bubbles growth pause added in the
    same hourly step. There is no aeration-peroxide interaction model in the simulation, so the two
    act independently: aeration multiplies growth by r_on (and m_late after 4 d), peroxide adds its
    Hill kill rate. Bubbles parameters are drawn from the bubbles rows (accepted by their own
    back-test, dinoflagellate) and applied to the small alga as the "inhibited" class (screened
    variant), which is an untested transfer. Arms A (untreated), B (forecast trigger with the rule
    handover, as method_mc arm Bf) and D (false alarm: no nutrients, forced ON on day 21); n = 3
    tanks per arm. Loop, pilot run, C_ok, floor, safety pull and the harm check are reused from
    method_mc / loop_controller / tank_model.

Outputs
    data/sim/tiered_dosing_summary.csv      one row per strategy (median and 5-95% across draws)
    data/sim/tiered_dosing_draws.csv        one row per draw x strategy
    figures/sim/fig_tiered_dosing.png

Run from repo root:
    python src/sim/tiered_dosing.py                  # 2000 draws
    python src/sim/tiered_dosing.py --draws 300      # quick pass
"""
import argparse
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import method_mc as mc  # noqa: E402
import tank_model as tm  # noqa: E402
from loop_controller import Controller, rule_trigger, T_ON, HANDOVER_DAYS  # noqa: E402

OUT_DIR, FIG_DIR = mc.OUT_DIR, mc.FIG_DIR
SEED = 42
STRATEGIES = ["FULL", "TIERED_P", "TIERED_A"]
ARMS = ["A", "B", "D"]
TANKS = 3                       # per arm, the plan
FULL_DOSE, HALF_DOSE = 0.8, 0.4  # mg/L H2O2
TANK_L = 10.0                   # litres per bench tank
_T = tm.load_params()
NT_LOWEST = float(_T[(_T.method == "peroxide") & (_T.param == "nt_threshold")].low.iloc[0])  # 0.86 mg/L
BUBBLE_KEYS = ["r_on_inhib", "r_on_neutral", "r_on_stim", "low_rate_factor", "m_late", "r_recover",
               "tau_recover", "rate"]


class DualTank(tm.TankBatch):
    """Peroxide tank that can also be aerated. Effects are independent (no interaction model)."""

    def __init__(self, p, organism):
        super().__init__(p, "peroxide", organism)
        self.dosed = np.zeros(self.n)            # mg H2O2 per litre added, summed over pulses

    def step_day_dual(self, dose, bub_on):
        """dose: mg/L pulse requested today (0 = none); bub_on: aeration mask. Returns daily-mean A."""
        p = self.p
        bub_on = np.asarray(bub_on, bool)
        pulse = (dose > 0) & (self.C <= tm.REDOSE_MAX)
        self.C = self.C + np.where(pulse, dose, 0.0)
        self.dosed += np.where(pulse, dose, 0.0)
        self.maxC = np.maximum(self.maxC, self.C)
        acc = np.zeros(self.n)
        for _ in range(24):
            # bubbles block (copied from TankBatch.step_day, method == "bubbles")
            started = bub_on & ~self.was_on
            stopped = ~bub_on & self.was_on
            self.cont_on = np.where(bub_on, self.cont_on + tm.DT, 0.0)
            slowed = self.r_on < 1
            self.R = np.where(stopped & slowed, p["r_recover"], self.R)
            self.R = np.where(started, 1.0, self.R)
            self.R = np.where(~bub_on, 1 - (1 - self.R) * np.exp(-tm.DT / p["tau_recover"]), self.R)
            g = np.where(bub_on, self.r_on, self.R)
            m_bub = np.where(bub_on & (self.cont_on > tm.BUBBLE_MORT_AFTER) & slowed, p["m_late"], 0.0)
            self.was_on = bub_on.copy()
            # peroxide block (copied, method == "peroxide")
            self.C = self.C * np.exp(-tm.LN2 * tm.DT / p["half_life"])
            m = p["m_max"] * tm.hill(self.C, p["ec50"], p["hill"]) + m_bub
            self.maxC = np.maximum(self.maxC, self.C)
            gr = self.mu * g * self.N / (self.N + p["k_n"])
            r = gr - (p["loss"] + m)
            e = np.exp(r * tm.DT)
            safe = np.where(np.abs(r) > 1e-9, r, 1)
            mean_a = np.where(np.abs(r) > 1e-9, self.A * (e - 1) / safe, self.A * tm.DT)
            used = np.minimum(gr * mean_a, self.N)
            self.A = np.maximum(self.A * e, 1e-6)
            self.N = self.N - used
            acc += self.A
        return acc / 24.0


def make_draws(n, rng):
    """Accepted peroxide draws plus accepted bubbles parameters (screened: inhibited class)."""
    p, rate_p = tm.accepted_draws("peroxide", n, rng)
    b, rate_b = tm.accepted_draws("bubbles", n, rng)
    for k in BUBBLE_KEYS:
        p[k] = b[k]
    p = tm.assign_species(p, rng, screened=True)
    p.pop("species_class")
    return p, rate_p, rate_b


def run_strategy(strategy, p, seed):
    """One bench per draw (arms A, B, D x TANKS) under a dosing strategy. Mirrors method_mc.run_bench."""
    rng = np.random.default_rng(seed)             # same noise stream for every strategy
    D = len(p["loss"])
    nt = len(ARMS) * TANKS
    rep = {k: np.repeat(v, nt) for k, v in p.items()}
    arm = np.tile(np.repeat(np.arange(len(ARMS)), TANKS), D)
    mu_key = tm.MU_KEY[mc.ORGANISM["peroxide"]]
    rep[mu_key] = rep[mu_key] * (1 + rng.normal(0, rep["tank_cv_mu"]))
    rep["a0"] = rep["a0"] * (1 + rng.normal(0, 0.1, len(arm)))
    tank = DualTank(rep, mc.ORGANISM["peroxide"])
    n = len(arm)
    is_A, is_B, is_D = (arm == i for i in range(len(ARMS)))
    ctrl = Controller(n, rep["x_days"].astype(int), max_on=mc.MAX_ON["peroxide"], handover_days=HANDOVER_DAYS)
    draw = np.repeat(np.arange(D), nt)
    pilot_peak = mc.pilot_run("peroxide", p, rng)[draw]
    c_ok = mc.C_OK_FRAC * pilot_peak
    hist = np.zeros((mc.DAYS, n))
    cells = np.zeros((mc.DAYS, n))
    warm = np.ones(n)
    conf = np.full(n, strategy == "FULL")       # confirmed (sticky); FULL needs no confirmation
    chl_start = np.full(n, np.nan)
    first_treat = np.full(n, -1)
    first_full = np.full(n, -1)
    bub_days = np.zeros(n, int)
    safety = np.zeros(n, int)
    for d in range(mc.DAYS):
        if d == mc.NUTRIENT_DAY:
            tank.N = tank.N + np.where(is_D, 0.0, rep["n_pulse"])
            warm = hist[mc.WARM[0]:mc.WARM[1]].mean(axis=0)
            if mc.FLOOR_ON:
                ctrl.floor = np.where(is_D, np.nan, mc.FLOOR_FRAC * warm)
        treat = ctrl.on & ~is_A
        if strategy == "TIERED_A":
            dose = np.where(treat & conf, FULL_DOSE, 0.0)
            bub = treat & ~conf
        else:
            dose = np.where(treat, np.where(conf, FULL_DOSE, HALF_DOSE), 0.0)
            bub = np.zeros(n, bool)
        full_now = (dose >= FULL_DOSE) & (tank.C <= tm.REDOSE_MAX)
        first_full = np.where((first_full < 0) & full_now, d, first_full)
        first_treat = np.where((first_treat < 0) & treat, d, first_treat)
        bub_days += bub
        chl_true = tank.step_day_dual(dose, bub)
        noise = 1 + rng.normal(0, rep["fluor_cv"])
        meas = np.maximum(chl_true * noise, 1e-3)
        hist[d] = meas
        cells[d] = meas
        if d < mc.NUTRIENT_DAY:
            continue
        r = (np.log(meas) - np.log(hist[d - 2])) / 2.0
        z = (np.log(meas) + 7 * r - np.log(2 * warm)) / mc.FC_SCALE + rng.normal(0, mc.FC_NOISE, n)
        pf = 1 / (1 + np.exp(-z))
        rule = rule_trigger(hist, d, warm)
        trig = is_B & (pf >= T_ON)
        trig |= is_D & (d == mc.NUTRIENT_DAY)
        force = tank.C > mc.PEROXIDE_PULL
        safety += force & ctrl.on
        # tier check on today's reading, before the controller acts (same day as its check)
        if strategy != "FULL":
            at_check = ctrl.on & ~conf & (d >= ctrl.check)
            ok = at_check & (pf >= T_ON) & (rule | (meas > chl_start))
            conf |= ok
            if strategy == "TIERED_P":
                force = force | (at_check & ~ok)          # not confirmed -> OFF
            else:
                ctrl.start = np.where(ok, d, ctrl.start)  # peroxide's 3-pulse clock starts now
        was_on = ctrl.on.copy()
        ctrl.step(d, trig, pf, meas, c_ok, force_off=force, rule=is_B & rule)
        chl_start = np.where(ctrl.on & ~was_on, meas, chl_start)
    peak = cells[mc.NUTRIENT_DAY:].max(axis=0)
    below = (cells[mc.NUTRIENT_DAY:] < c_ok).sum(axis=0)
    return dict(draw=draw, arm=arm, peak=peak, below=below, dosed_mg=tank.dosed * TANK_L,
                max_c=tank.maxC, nt_harm=tank.maxC > rep["nt_threshold"], safety=safety,
                on_days=ctrl.on_days, bub_days=bub_days,
                to_full=np.where(first_full >= 0, first_full - first_treat, np.nan).astype(float),
                ever_full=first_full >= 0)


def evaluate(res, D):
    df = pd.DataFrame(res)
    df["arm"] = np.array(ARMS)[df.arm]
    g = {a: x.groupby("draw") for a, x in df.groupby("arm")}
    A, B, Dd = (df[df.arm == a].sort_values("draw") for a in ARMS)
    rows = []
    pa = A.peak.values.reshape(D, TANKS)
    pb = B.peak.values.reshape(D, TANKS)
    for i in range(D):
        lo, _ = mc.welch_reduction(pb[i], pa[i])
        rows.append(lo)
    out = pd.DataFrame(dict(
        draw=np.arange(D),
        red_mean=1 - g["B"].peak.mean().values / g["A"].peak.mean().values,
        red_lo=rows,
        below_gain=g["B"].below.mean().values - g["A"].below.mean().values,
        b_dosed_mg=g["B"].dosed_mg.mean().values,
        b_days_to_full=g["B"].to_full.mean().values,
        b_never_full=g["B"].ever_full.apply(lambda s: (~s).mean()).values,
        b_on_days=g["B"].on_days.mean().values,
        b_nt_harm=g["B"].nt_harm.any().values,
        d_dosed_mg=g["D"].dosed_mg.mean().values,
        d_nt_harm=g["D"].nt_harm.any().values,
        d_max_c=g["D"].max_c.max().values,
        d_on_days=g["D"].on_days.mean().values,
        d_bub_days=g["D"].bub_days.mean().values,
        d_safety=g["D"].safety.sum().values,
    ))
    out["h1a_point"] = out.red_mean >= 0.5
    out["h1a_ci"] = out.red_lo >= 0.5
    return out


def summarise(strategy, ev):
    def ci(s):
        s = s.dropna()
        return (float(s.median()), float(s.quantile(0.05)), float(s.quantile(0.95))) if len(s) else (np.nan,) * 3
    row = dict(strategy=strategy, draws=len(ev))
    for name, col in [("b_peak_reduction", "red_mean"), ("b_days_below_cok_vs_A", "below_gain"),
                      ("b_peroxide_mg_per_tank", "b_dosed_mg"), ("b_days_to_first_full_dose", "b_days_to_full"),
                      ("b_on_days", "b_on_days"), ("d_peroxide_mg_per_tank", "d_dosed_mg"),
                      ("d_peak_h2o2_mg_l", "d_max_c"), ("d_on_days", "d_on_days")]:
        row[f"{name}_median"], row[f"{name}_p5"], row[f"{name}_p95"] = ci(ev[col])
    row.update(p_h1a_point_n3=ev.h1a_point.mean(), p_h1a_ci_n3=ev.h1a_ci.mean(),
               b_share_tanks_never_full=ev.b_never_full.mean(), p_b_nontarget_harm=ev.b_nt_harm.mean(),
               p_d_nontarget_harm=ev.d_nt_harm.mean(), p_d_safety_stop=(ev.d_safety > 0).mean(),
               d_aeration_days_median=ev.d_bub_days.median())
    return row


def plot(evs, summary):
    colors = {"FULL": "#5A707A", "TIERED_P": "#23775A", "TIERED_A": "#1F5FA8"}
    labels = {"FULL": "Full 0.8", "TIERED_P": "Half first", "TIERED_A": "Aeration first"}
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.8))
    data = [evs[s].red_mean * 100 for s in STRATEGIES]
    bp = axes[0].boxplot(data, whis=(5, 95), showfliers=False, patch_artist=True)
    for patch, s in zip(bp["boxes"], STRATEGIES):
        patch.set_facecolor(colors[s])
        patch.set_alpha(0.6)
    axes[0].axhline(50, color="k", ls=":", lw=0.8)
    axes[0].set_xticks(range(1, 4), [labels[s] for s in STRATEGIES])
    axes[0].set_ylabel("arm B peak cut vs A (%)")
    axes[0].set_title("Real bloom: benefit")
    xs = np.arange(3)
    peak_d = [evs[s].d_max_c.mean() for s in STRATEGIES]
    axes[1].bar(xs, peak_d, 0.6, color=[colors[s] for s in STRATEGIES], alpha=0.8)
    for x, s, v in zip(xs, STRATEGIES, peak_d):
        axes[1].text(x, v + 0.02, f"{v:.2f} mg/L\n{evs[s].d_dosed_mg.mean():.1f} mg dosed", ha="center", fontsize=8)
    axes[1].axhline(NT_LOWEST, color="#A8492A", ls="--", lw=1)
    axes[1].text(1.5, NT_LOWEST + 0.03, "lowest harm threshold drawn (krill LC50)", ha="center", fontsize=7,
                 color="#A8492A")
    axes[1].set_xticks(xs, [labels[s] for s in STRATEGIES])
    axes[1].set_ylim(0, 1.1)
    axes[1].set_ylabel("arm D peak H2O2 (mg/L, mean of draws)")
    axes[1].set_title("False alarm: peroxide exposure")
    w = 0.38
    axes[2].bar(xs - w / 2, summary.p_d_nontarget_harm * 100, w, color="#A8492A", label="D non-target harm")
    axes[2].bar(xs + w / 2, summary.p_h1a_ci_n3 * 100, w, color="#23775A",
                label="B >= 50% cut (95% CI), n = 3")
    for x, v in zip(xs - w / 2, summary.p_d_nontarget_harm * 100):
        axes[2].text(x, v + 1, f"{v:.0f}%", ha="center", fontsize=8)
    for x, v in zip(xs + w / 2, summary.p_h1a_ci_n3 * 100):
        axes[2].text(x, v + 1, f"{v:.0f}%", ha="center", fontsize=8)
    axes[2].set_xticks(xs, [labels[s] for s in STRATEGIES])
    axes[2].set_ylim(0, 105)
    axes[2].set_ylabel("share of simulated bench runs (%)")
    axes[2].set_title("Harm vs H1a")
    axes[2].legend(fontsize=7, frameon=False, loc="upper center")
    fig.suptitle("Tiered peroxide dosing (exploratory; same draws for every strategy; boxes 25-75%, whiskers 5-95%)",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "fig_tiered_dosing.png"), dpi=160)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", type=int, default=2000)
    args = ap.parse_args()
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(FIG_DIR, exist_ok=True)
    rng = np.random.default_rng(SEED)
    p, rate_p, rate_b = make_draws(args.draws, rng)
    print(f"{args.draws} draws; back-test acceptance peroxide {rate_p:.0%}, bubbles {rate_b:.0%}")
    bench_seed = int(rng.integers(2 ** 31))
    evs, rows, per = {}, [], []
    for s in STRATEGIES:
        ev = evaluate(run_strategy(s, p, bench_seed), args.draws)
        evs[s] = ev
        rows.append(summarise(s, ev))
        per.append(ev.assign(strategy=s))
        r = rows[-1]
        print(f"{s:9s} B cut {r['b_peak_reduction_median']:.0%} [{r['b_peak_reduction_p5']:.0%}, "
              f"{r['b_peak_reduction_p95']:.0%}]  H1a {r['p_h1a_point_n3']:.0%}/{r['p_h1a_ci_n3']:.0%}  "
              f"below+{r['b_days_below_cok_vs_A_median']:.1f} d  B H2O2 {r['b_peroxide_mg_per_tank_median']:.0f} mg  "
              f"to full {r['b_days_to_first_full_dose_median']:.1f} d  | D H2O2 {r['d_peroxide_mg_per_tank_median']:.0f} mg  "
              f"D harm {r['p_d_nontarget_harm']:.0%}  D peak {r['d_peak_h2o2_mg_l_median']:.2f} mg/L")
    summary = pd.DataFrame(rows)
    summary.to_csv(os.path.join(OUT_DIR, "tiered_dosing_summary.csv"), index=False)
    pd.concat(per).to_csv(os.path.join(OUT_DIR, "tiered_dosing_draws.csv"), index=False)
    plot(evs, summary)
    print(f"wrote {OUT_DIR}/tiered_dosing_summary.csv, tiered_dosing_draws.csv, {FIG_DIR}/fig_tiered_dosing.png")


if __name__ == "__main__":
    main()
