"""
method_mc.py -- Layer 2, step 3: Monte-Carlo bench runs of the treatment loop (seaweed, bubbles)
=================================================================================================
Step 3 of notes/mitigation/LAYER2_SIM_RESULTS.md. Each draw is one full bench run with the
parameters drawn from src/sim/method_params.csv (kept only if they reproduce their calibration
paper; tank_model.backtest). Every draw simulates 5 tanks per arm for 56 days:

    A    untreated                       nutrients added on day 21
    Bf   loop, forecast trigger          p >= 0.50 from a persistence forecast of the tank's own
                                         readings (7-day projection of the last 2 days' growth)
    Br   loop, rule trigger              chl up 2 days running and > 2 x warm-up mean
    C    late treatment                  starts once, the first day chl falls after passing
                                         2 x warm-up mean (i.e. after the peak)
    D    false alarm                     no nutrients; loop forced ON on day 21

Loop rules are loop_controller.Controller (identical to Layer 1's run_loop). C_ok = 50% of arm
A's running peak (00_CONTROL_LOOP.md bench rule). Seaweed pulls its panel if pH > 9.0.
Readings carry fluorometer noise; the controller only sees readings.

Pre-registered tests, evaluated per draw on the first n tanks of each arm (n = 3 is the plan):
    H1      mean peak reduction of B vs mean A >= 50%, and B used fewer ON days than C
            (point estimate), and the stricter version with the 95% t-interval lower bound >= 50%
            (t_interval from src/lab/analyze_lab.py; t = 4.30 at n = 3)
    H1a     the first half of H1 alone (>= 50% peak cut), mean and 95% CI versions
    H1b     B's peak cut beats the late arm C's by 20+ points
            (The simulation showed that late treatment is short and cheap because the bloom is
             already crashing, so "fewer ON days than C" can fail even when B works.)
    H2      the false-alarm arm D: seaweed never hits the pH safety stop (bubbles add nothing)
    H3      days until B regrows above C_ok after its last OFF (reported, no pass mark)

Outputs
    data/sim/method_mc_<method>[_unscreened].csv   one row per draw (parameters + metrics)
    data/sim/method_summary.csv                    one row per method / variant
    data/sim/method_design_<method>.csv            X x dose sweep
    figures/sim/fig_method_curves.png, fig_method_ph1.png,
    figures/sim/fig_method_tornado_<m>.png, fig_method_design_<m>.png

Run from repo root:
    python src/sim/method_mc.py                       # seaweed and bubbles, 2000 draws
    python src/sim/method_mc.py --method seaweed --draws 200
"""
import argparse
import itertools
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "lab"))
import tank_model as tm  # noqa: E402
from loop_controller import Controller, rule_trigger, T_ON  # noqa: E402
from analyze_lab import t_interval  # noqa: E402

OUT_DIR, FIG_DIR = "data/sim", "figures/sim"
DAYS, NUTRIENT_DAY, WARM = 56, 21, (14, 21)
TANKS = 5                      # per arm (n = 3 is the plan; 4 and 5 for the power check)
ARMS = ["A", "Bf", "Br", "C", "D"]
FC_SCALE, FC_NOISE = 0.35, 0.5  # forecast emulator: logistic scale and noise (log units)
BLOOM_MIN = 10.0               # ug/L; the forecast's bloom line is max(10, 2 x warm-up mean)
ORGANISM = {"seaweed": "diatom", "bubbles": "dino", "peroxide": "small", "curcumin": "dino",
            "shellfish": "diatom"}
METHODS = list(ORGANISM)
PEROXIDE_PULL = 2.8            # mg/L residual: pull the bag early (03_PEROXIDE_BAG.md)
SWEEP = {                      # (parameter, values, axis label) for the X x dose design sweep
    "seaweed": ("dose", [0.5, 1.0, 2.0, 3.0], "kelp dose (g/L wet)"),
    "bubbles": ("rate", [0.05, 0.6], "airflow (L/min per L)"),
    "peroxide": ("target", [0.8, 1.6, 3.2], "H2O2 target (mg/L)"),
    "curcumin": ("ladder_top", [2.5, 5.0], "top of the dose ladder (mg/L)"),
    "shellfish": ("clear_vol_per_day", [0.5, 1.0, 2.0], "planned clearance (tank volumes/day)"),
}
SEED = 42


def run_bench(method, p, rng, x_days=None, keep_curves=False):
    """Simulate every draw in p (dict of arrays, length D) as a full bench run."""
    D = len(p["loss"])
    nt = len(ARMS) * TANKS
    rep = {k: np.repeat(v, nt) for k, v in p.items() if np.asarray(v).dtype.kind in "fi"}
    arm = np.tile(np.repeat(np.arange(len(ARMS)), TANKS), D)
    draw = np.repeat(np.arange(D), nt)
    mu_key = tm.MU_KEY[ORGANISM[method]]
    rep[mu_key] = rep[mu_key] * (1 + rng.normal(0, rep["tank_cv_mu"]))
    rep["a0"] = rep["a0"] * (1 + rng.normal(0, 0.1, len(arm)))
    tank = tm.TankBatch(rep, method, ORGANISM[method])
    x = rep["x_days"].astype(int) if x_days is None else np.full(len(arm), int(x_days))
    ctrl = Controller(len(arm), x)
    is_A, is_Bf, is_Br, is_C, is_D = (arm == i for i in range(5))
    hist = np.zeros((DAYS, len(arm)))
    on_hist = np.zeros((DAYS, len(arm)), bool)
    c_started = np.zeros(len(arm), bool)
    passed = np.zeros(len(arm), bool)
    safety = np.zeros(len(arm), int)
    a_peak = np.zeros(D)
    warm = np.ones(len(arm))
    first_on = np.full(len(arm), -1)
    for d in range(DAYS):
        if d == NUTRIENT_DAY:
            tank.N = tank.N + np.where(is_D, 0.0, rep["n_pulse"])
            warm = hist[WARM[0]:WARM[1]].mean(axis=0)
        treat = ctrl.on & ~is_A
        chl_true = tank.step_day(treat)
        meas = np.maximum(chl_true * tank.reading_factor() * (1 + rng.normal(0, rep["fluor_cv"])), 1e-3)
        hist[d] = meas
        if d < NUTRIENT_DAY:
            continue
        # C_ok: half of arm A's running peak (mean over the draw's A tanks)
        a_mean = np.bincount(draw[is_A], weights=meas[is_A], minlength=D) / TANKS
        a_peak = np.maximum(a_peak, a_mean)
        c_ok = 0.5 * a_peak[draw]
        # forecast emulator: 7-day persistence projection of the tank's own readings
        r = (np.log(meas) - np.log(hist[d - 2])) / 2.0
        line = np.maximum(BLOOM_MIN, 2 * warm)
        z = (np.log(meas) + 7 * r - np.log(line)) / FC_SCALE + rng.normal(0, FC_NOISE, len(arm))
        pf = 1 / (1 + np.exp(-z))
        passed |= meas > 2 * warm
        trig = is_Bf & (pf >= T_ON)
        trig |= is_Br & rule_trigger(hist, d, warm)
        late = is_C & ~c_started & passed & (meas < hist[d - 1])
        trig |= late
        c_started |= late
        trig |= is_D & (d == NUTRIENT_DAY)
        force = np.zeros(len(arm), bool)
        if method == "seaweed":
            force = tank.ph() > tm.PH_LIMIT
        elif method == "peroxide":
            force = tank.C > PEROXIDE_PULL
        safety += force & ctrl.on
        on_now = ctrl.step(d, trig, pf, meas, c_ok, force_off=force)
        first_on = np.where((first_on < 0) & on_now, d, first_on)
        on_hist[d] = on_now

    peak = hist[NUTRIENT_DAY:].max(axis=0)
    # regrowth: days after the last OFF until readings exceed C_ok again (NaN if never / never OFF)
    c_ok_end = 0.5 * a_peak[draw]
    regrow = np.full(len(arm), np.nan)
    for i in np.where((is_Bf | is_Br) & (ctrl.last_off >= 0))[0]:
        after = np.where(hist[ctrl.last_off[i] + 1:, i] > c_ok_end[i])[0]
        if len(after):
            regrow[i] = after[0] + 1
    # non-target harm: the highest peroxide / curcumin level a tank reached vs the harm threshold
    nt_harm = (tank.maxC > rep["nt_threshold"]) if "nt_threshold" in rep else np.zeros(len(arm), bool)
    res = dict(draw=draw, arm=arm, peak=peak, on_days=ctrl.on_days, episodes=ctrl.episodes,
               maxed=ctrl.maxed, safety=safety, regrow=regrow, first_on=first_on, nt_harm=nt_harm,
               max_c=tank.maxC)
    if keep_curves:
        res["hist"], res["on_hist"] = hist, on_hist
    return res


def evaluate(res, D, n=3, b_arm="Bf"):
    """Per-draw H1/H2/H3 using the first n tanks of each arm."""
    df = pd.DataFrame({k: v for k, v in res.items() if k not in ("hist", "on_hist")})
    df["arm"] = np.array(ARMS)[df.arm]
    df["k"] = df.groupby(["draw", "arm"]).cumcount()
    df = df[df.k < n]
    by = {a: g.set_index("draw") for a, g in df.groupby("arm")}
    peak_a = by["A"].groupby(level=0).peak.mean()
    rows = []
    for dr in range(D):
        b = by[b_arm].loc[[dr]]
        c = by["C"].loc[[dr]]
        dd = by["D"].loc[[dr]]
        red = 1 - b.peak.values / peak_a[dr]
        m, lo, hi = t_interval(red)
        on_b, on_c = b.on_days.mean(), c.on_days.mean()
        red_c = 1 - c.peak.mean() / peak_a[dr]
        rows.append(dict(draw=dr, red_mean=m, red_lo=lo, red_hi=hi, on_b=on_b, on_c=on_c, red_c=red_c,
                         h1_point=bool((m >= 0.5) and (on_b < on_c)), h1_ci=bool((lo >= 0.5) and (on_b < on_c)),
                         h1a_point=bool(m >= 0.5), h1a_ci=bool(lo >= 0.5), b_beats_c=bool(m > red_c + 0.2),
                         regrew=bool(np.isfinite(b.regrow.values).any()),
                         h2_pass=bool((dd.safety == 0).all() and not dd.nt_harm.any()), on_d=dd.on_days.mean(),
                         b_nt_harm=bool(b.nt_harm.any()),
                         regrow_days=np.nanmedian(b.regrow.values) if np.isfinite(b.regrow.values).any() else np.nan,
                         b_safety=int(b.safety.sum()), maxed_b=b.maxed.mean()))
    return pd.DataFrame(rows)


def summarise(method, variant, ev, ev_by_n, ev_rule):
    q = lambda s, a: float(np.nanpercentile(s, a))  # noqa: E731
    row = dict(method=method, variant=variant, draws=len(ev),
               p_h1_point_n3=ev.h1_point.mean(), p_h1_ci_n3=ev.h1_ci.mean(),
               median_peak_reduction=ev.red_mean.median(), red_p5=q(ev.red_mean, 5), red_p95=q(ev.red_mean, 95),
               median_on_days_B=ev.on_b.median(), median_on_days_C=ev.on_c.median(),
               median_late_reduction_C=ev.red_c.median(),
               p_h2_pass=ev.h2_pass.mean(), median_on_days_D=ev.on_d.median(),
               p_h1a_point_n3=ev.h1a_point.mean(), p_h1a_ci_n3=ev.h1a_ci.mean(), p_b_beats_c=ev.b_beats_c.mean(),
               share_regrew=ev.regrew.mean(), p_b_safety_stop=(ev.b_safety > 0).mean(),
               p_b_nontarget_harm=ev.b_nt_harm.mean(),
               median_regrow_days=ev.regrow_days.median(), share_B_maxed=(ev.maxed_b > 0).mean(),
               p_h1_point_rule_trigger=ev_rule.h1_point.mean(),
               median_peak_reduction_rule=ev_rule.red_mean.median())
    for n, e in ev_by_n.items():
        row[f"p_h1_point_n{n}"] = e.h1_point.mean()
        row[f"p_h1_ci_n{n}"] = e.h1_ci.mean()
        row[f"p_h1a_point_n{n}"] = e.h1a_point.mean()
        row[f"p_h1a_ci_n{n}"] = e.h1a_ci.mean()
    return row


def draws_for(method, n, rng, screened=True):
    p, rate = tm.accepted_draws(method, n, rng)
    if method == "bubbles":
        p = tm.assign_species(p, rng, screened)
    return p, rate


def sensitivity(p, ev, method):
    y = pd.Series(ev.red_mean.values)
    out = {k: pd.Series(v).corr(y, method="spearman") for k, v in p.items()
           if np.asarray(v).dtype.kind == "f" and np.ptp(v) > 0}
    s = pd.Series(out).dropna().sort_values(key=np.abs, ascending=False)
    fig, ax = plt.subplots(figsize=(6, 0.35 * len(s) + 1))
    ax.barh(s.index[::-1], s.values[::-1], color=np.where(s.values[::-1] > 0, "#23775A", "#A8492A"))
    ax.set_xlabel("Spearman correlation with B's peak reduction")
    ax.set_title(f"{method}: which unknown matters most")
    ax.axvline(0, color="k", lw=0.8)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, f"fig_method_tornado_{method}.png"), dpi=160)
    plt.close(fig)
    return s


def design_sweep(method, n_draws, rng):
    p0, _ = draws_for(method, n_draws, rng, screened=True)
    key, grid_d, dose_label = SWEEP[method]
    grid_x = [1, 2, 3, 4]
    rows = []
    for x, dose in itertools.product(grid_x, grid_d):
        p = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in p0.items()}
        p[key] = np.full(n_draws, dose)
        if method == "bubbles":
            p = tm.assign_species(p, rng, screened=True)
        ev = evaluate(run_bench(method, p, rng, x_days=x), n_draws)
        rows.append(dict(method=method, x_days=x, dose=dose, p_h1a_point=ev.h1a_point.mean(),
                         p_h1a_ci=ev.h1a_ci.mean(), p_h1_point=ev.h1_point.mean(),
                         median_reduction=ev.red_mean.median(), median_on_days_B=ev.on_b.median(),
                         p_h2_pass=ev.h2_pass.mean(), p_b_safety_stop=(ev.b_safety > 0).mean(),
                         p_b_nontarget_harm=ev.b_nt_harm.mean()))
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(OUT_DIR, f"method_design_{method}.csv"), index=False)
    piv = out.pivot(index="x_days", columns="dose", values="p_h1a_point")
    fig, ax = plt.subplots(figsize=(5, 3.6))
    im = ax.imshow(piv.values, origin="lower", cmap="Greens", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(piv.columns)), [f"{c:g}" for c in piv.columns])
    ax.set_yticks(range(len(piv.index)), piv.index)
    for (i, j), v in np.ndenumerate(piv.values):
        ax.text(j, i, f"{v:.0%}", ha="center", va="center", fontsize=9, color="k" if v < 0.6 else "w")
    ax.set_xlabel(dose_label)
    ax.set_ylabel("X (days ON before re-measuring)")
    ax.set_title(f"{method}: chance of a >= 50% peak cut (n = 3)")
    fig.colorbar(im, ax=ax, fraction=0.046)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, f"fig_method_design_{method}.png"), dpi=160)
    plt.close(fig)
    return out


def plot_curves(curves):
    ncol = min(3, len(curves))
    nrow = int(np.ceil(len(curves) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(5.2 * ncol, 3.6 * nrow), squeeze=False)
    for ax in axes.flat[len(curves):]:
        ax.axis("off")
    colors = dict(A="#5A707A", Bf="#23775A", C="#A8492A", D="#1F5FA8")
    names = {"A": "A untreated", "Bf": "B loop", "C": "C late", "D": "D false alarm"}
    for ax, (method, (res, dr)) in zip(axes.flat, curves.items()):
        arm = np.array(ARMS)[res["arm"]]
        sel = res["draw"] == dr
        days = np.arange(DAYS)
        for a in ["A", "Bf", "C", "D"]:
            m = sel & (arm == a)
            ax.plot(days, res["hist"][:, m][:, :3].mean(axis=1), color=colors[a], lw=2, label=names[a])
        on = res["on_hist"][:, sel & (arm == "Bf")][:, :3].mean(axis=1)
        top = ax.get_ylim()[1]
        ax.fill_between(days, 0, top * 0.04, where=on > 0.5, color="#23775A", alpha=0.35, step="mid",
                        label="B treatment ON")
        ax.axvline(NUTRIENT_DAY, color="k", ls=":", lw=0.8)
        ax.set_title(f"{method}: a typical draw (mean of 3 tanks)")
        ax.set_xlabel("day")
        ax.set_ylabel("chlorophyll reading (ug/L)")
        ax.legend(fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "fig_method_curves.png"), dpi=160)
    plt.close(fig)


def plot_ph1(summary):
    fig, ax = plt.subplots(figsize=(9.5, 3.8))
    labels = [f"{r.method}\n({r.variant})" for r in summary.itertuples()]
    xs = np.arange(len(summary))
    w = 0.13
    for i, n in enumerate([3, 4, 5]):
        ax.bar(xs + (i - 1) * 2 * w - w / 2, summary[f"p_h1a_point_n{n}"], w, color="#23775A",
               alpha=0.45 + 0.2 * i, label=f">= 50% cut (mean), n = {n}")
        ax.bar(xs + (i - 1) * 2 * w + w / 2, summary[f"p_h1a_ci_n{n}"], w, color="#A8492A",
               alpha=0.45 + 0.2 * i, label=f">= 50% cut (95% CI), n = {n}")
    ax.scatter(xs, summary["p_h1_point_n3"], marker="x", color="k", zorder=3,
               label="H1 as written (also fewer ON days than C), n = 3")
    ax.set_xticks(xs, labels)
    ax.set_ylim(0, 1)
    ax.set_ylabel("share of simulated bench runs")
    ax.set_title("Chance the bench shows a >= 50% peak cut")
    ax.legend(fontsize=7, frameon=False, loc="upper left", bbox_to_anchor=(1.01, 1.0))
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "fig_method_ph1.png"), dpi=160)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--method", choices=METHODS + ["all"], default="all")
    ap.add_argument("--draws", type=int, default=2000)
    ap.add_argument("--sweep-draws", type=int, default=400)
    args = ap.parse_args()
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(FIG_DIR, exist_ok=True)
    rng = np.random.default_rng(SEED)
    methods = METHODS if args.method == "all" else [args.method]
    summaries, curves = [], {}
    for method in methods:
        variants = [("screened", True)] + ([("unscreened", False)] if method == "bubbles" else [])
        for variant, screened in variants:
            p, rate = draws_for(method, args.draws, rng, screened)
            res = run_bench(method, p, rng, keep_curves=(variant == "screened"))
            ev_by_n = {n: evaluate(res, args.draws, n=n) for n in (3, 4, 5)}
            ev = ev_by_n[3]
            ev_rule = evaluate(res, args.draws, n=3, b_arm="Br")
            s = summarise(method, variant, ev, ev_by_n, ev_rule)
            s["backtest_acceptance"] = rate
            summaries.append(s)
            flat = {k: v for k, v in p.items() if np.asarray(v).dtype.kind in "fU"}
            pd.concat([pd.DataFrame(flat), ev.drop(columns="draw")], axis=1).to_csv(
                os.path.join(OUT_DIR, f"method_mc_{method}{'' if screened else '_unscreened'}.csv"), index=False)
            print(f"\n{method} ({variant}): {args.draws} draws, back-test acceptance {rate:.0%}")
            print(f"  H1 as written (>=50% cut AND fewer ON days than C), n=3: {s['p_h1_point_n3']:.0%}")
            print(f"  H1a >=50% peak cut, n=3: mean {s['p_h1a_point_n3']:.0%}, 95% CI {s['p_h1a_ci_n3']:.0%}   "
                  f"(n=4: {s['p_h1a_point_n4']:.0%} / {s['p_h1a_ci_n4']:.0%}; "
                  f"n=5: {s['p_h1a_point_n5']:.0%} / {s['p_h1a_ci_n5']:.0%});  "
                  f"H1b B beats late C by 20+ points: {s['p_b_beats_c']:.0%}")
            print(f"  B peak reduction vs A: median {s['median_peak_reduction']:.0%} "
                  f"[5-95%: {s['red_p5']:.0%}, {s['red_p95']:.0%}];  late arm C: {s['median_late_reduction_C']:.0%}")
            print(f"  ON days: B {s['median_on_days_B']:.0f}, C {s['median_on_days_C']:.0f}, "
                  f"D {s['median_on_days_D']:.0f};  B hit MAX_ON in {s['share_B_maxed']:.0%} of runs;  "
                  f"regrew above C_ok after OFF in {s['share_regrew']:.0%} (median {s['median_regrow_days']:.1f} d);  "
                  f"safety stop in B: {s['p_b_safety_stop']:.0%};  non-target harm in B: {s['p_b_nontarget_harm']:.0%}")
            print(f"  H2 (D safe): {s['p_h2_pass']:.0%};  rule trigger instead of forecast: "
                  f"H1 {s['p_h1_point_rule_trigger']:.0%}, reduction {s['median_peak_reduction_rule']:.0%}")
            if variant == "screened":
                sens = sensitivity(p, ev, method)
                print("  most influential: " + ", ".join(f"{k} {v:+.2f}" for k, v in sens.head(4).items()))
                typical = int((ev.red_mean - ev.red_mean.median()).abs().idxmin())
                curves[method] = (res, typical)
        des = design_sweep(method, args.sweep_draws, rng)
        best = des.sort_values(["p_h1a_point", "median_on_days_B"], ascending=[False, True]).iloc[0]
        print(f"  design sweep best: X = {best.x_days:.0f} d, dose {best.dose:g} -> >=50% cut in "
              f"{best.p_h1a_point:.0%} of runs, {best.median_on_days_B:.0f} ON days")
    summary = pd.DataFrame(summaries)
    summary.to_csv(os.path.join(OUT_DIR, "method_summary.csv"), index=False)
    plot_curves(curves)
    plot_ph1(summary)
    print(f"\nwrote {OUT_DIR}/method_summary.csv and figures in {FIG_DIR}/fig_method_*.png")


if __name__ == "__main__":
    main()
