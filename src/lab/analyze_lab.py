"""
analyze_lab.py
--------------
The whole of the Phase 11 bench analysis (notes/LAB_PROTOCOL.md s8), written and
verified against synthetic data before any real measurement exists.

Why it exists now: the hypotheses, the bands and the readings are pre-registered
(notes/SCIENTIFIC_METHOD.md Phase 11). If the analysis were written in January,
next to the numbers, every choice in it - which counts define removal, how the
interval is formed, when a dose curve may be interpolated - could be made to
favour a result. Fixing the code in September removes that freedom. Running it on
synthetic data with a known planted truth (data/lab/synth_truth.json) is what
makes "it works" checkable rather than asserted.

What it computes, all from notes/LAB_PROTOCOL.md s8:
  - control-corrected removal per batch, RE = 1 - (Ct/C0) / (Ct,ctl/C0,ctl) at 5 h
  - H11a: mean RE over three batches, t-interval at t = 4.30, with the
    pre-registered "consistent, underpowered" reading kept as a distinct outcome
  - recovery per tank run, the pad solids correction, and the H11b three-part test
  - the magnetite mass balance across pad + fractions i, ii, iii + unaccounted,
    with the s7 detection floor and quantitation limit applied to fraction iii
  - the resuspension index, T33 count over T20 count
  - H11c: per-dose means, monotonicity by ordered means, and D90 by log-linear
    interpolation only when two adjacent dose means bracket 90%
  - inter-counter agreement: mean absolute relative difference and Lin's
    concordance correlation coefficient

A batch-clustered bootstrap is printed as a sensitivity check only. It is NOT the
pre-registered statistic: three batches are three clusters, which a bootstrap
cannot carry, and the pre-registration names the t-interval.

Outputs
  data/lab/analysis_summary.csv   one row per reported metric, point estimate with lo/hi
  figures/lab/fig_lab_results.png removal by arm, recovery and mass balance, dose response

Run from repo root:
    python src/lab/analyze_lab.py
    python src/lab/analyze_lab.py --in data/lab/lab_measurements.csv
"""
import argparse
import json
import os
import sys
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lab_schema as S  # noqa: E402

warnings.filterwarnings("ignore")

IN_ROWS = "data/lab/lab_measurements.csv"
TRUTH = "data/lab/synth_truth.json"
OUT_SUMMARY = "data/lab/analysis_summary.csv"
OUT_FIG = "figures/lab/fig_lab_results.png"

# --- pre-registered constants, notes/LAB_PROTOCOL.md s8 ----------------------
T_CRIT_N3 = 4.30          # two-sided 95% t for n = 3 (2 degrees of freedom)
HEADLINE_DOSE = 0.2       # g/L, the dose H11a is stated at
TANK_VOLUME_L = 20.0
MAGNETITE_FRACTION = 0.20  # of dry blend, Amendment A1
SALT_FRACTION = 0.035      # seawater salt mass fraction, s7 solids correction
FRAC_III_FLOOR_G = 0.008   # s7: 8 mg = 1.0% of the 0.8 g dosed, detection floor
FRAC_III_QUANT_G = 0.020   # s7: 20 mg = 2.5%, quantitative above this
DOSE_LADDER = (0.05, 0.1, 0.2, 0.4)
N_BOOT, SEED = 2000, 42

H11A_MEAN_PASS = 0.70
H11A_LB_PASS = 0.50
H11A_LB_UNDERPOWERED = 0.40
H11A_ARM_GAP = 0.15
H11A_RERUN_DOSE = 0.6
H11B_MEAN_PASS = 0.70
H11B_EACH_PASS = 0.60
H11B_SOLIDS_PASS = 0.50


# --- small helpers -----------------------------------------------------------
def t_interval(x):
    """Mean and two-sided 95% t-interval for a small sample. n = 3 uses t = 4.30."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n == 0:
        return np.nan, np.nan, np.nan
    m = float(np.mean(x))
    if n < 2:
        return m, np.nan, np.nan
    sd = float(np.std(x, ddof=1))
    if n == 3:
        t = T_CRIT_N3
    else:
        from scipy import stats
        t = float(stats.t.ppf(0.975, n - 1))
    half = t * sd / np.sqrt(n)
    return m, m - half, m + half


def series(df, measure, **eq):
    """Rows for one measure, optionally filtered on exact column values."""
    d = df[df["measure"] == measure]
    for k, v in eq.items():
        d = d[d[k] == v]
    return d


def one(df, measure, **eq):
    """The single value for a measure, or nan if it is not in the sheet."""
    d = series(df, measure, **eq)
    if len(d) == 0:
        return np.nan
    return float(d["value"].iloc[0])


def lin_ccc(a, b):
    """Lin's concordance correlation coefficient."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 2:
        return np.nan
    va, vb = np.var(a, ddof=0), np.var(b, ddof=0)
    cov = float(np.mean((a - a.mean()) * (b - b.mean())))
    denom = va + vb + (a.mean() - b.mean()) ** 2
    return float(2 * cov / denom) if denom > 0 else np.nan


# --- removal (jars) ----------------------------------------------------------
def removal_table(df):
    """Control-corrected removal per (batch, vessel, arm, dose) at 5 h, s8."""
    jars = df[(df["vessel"] != "tank") & (df["measure"] == "cell_count")].copy()
    # duplicate re-counts by the second counter feed the agreement statistic, not removal
    primary = jars["counter"].astype(str)
    jars = jars[primary != "RS"] if (primary == "RS").any() else jars
    rows = []
    for batch, d in jars.groupby("batch"):
        ctl = d[d["arm"] == "untreated"]
        c0_ctl = one(ctl, "cell_count", T_min=0)
        ct_ctl = one(ctl, "cell_count", T_min=300)
        if not np.isfinite(c0_ctl) or not np.isfinite(ct_ctl) or c0_ctl <= 0:
            continue
        ctl_ratio = ct_ctl / c0_ctl
        if ctl_ratio <= 0:
            continue
        for (vessel, arm, dose), g in d[d["arm"] != "untreated"].groupby(["vessel", "arm", "dose_g_L"]):
            c0 = one(g, "cell_count", T_min=0)
            ct = one(g, "cell_count", T_min=300)
            if not np.isfinite(c0) or not np.isfinite(ct) or c0 <= 0:
                continue
            rows.append(dict(batch=batch, vessel=vessel, arm=arm, dose_g_L=float(dose),
                             C0=c0, Ct=ct, control_ratio=ctl_ratio,
                             RE=1.0 - (ct / c0) / ctl_ratio))
    return pd.DataFrame(rows)


def h11a(re_df, out):
    """H11a: removal at the headline dose, s8."""
    print("\n" + "-" * 78)
    print("H11a  REMOVAL at %.2f g/L, control-corrected, 5 h" % HEADLINE_DOSE)
    print("-" * 78)
    if len(re_df) == 0:
        print("  no treated jar rows - nothing to test")
        return
    mag = re_df[(re_df["arm"] == "magnetic") & (np.isclose(re_df["dose_g_L"], HEADLINE_DOSE))]
    plain = re_df[(re_df["arm"] == "plain") & (np.isclose(re_df["dose_g_L"], HEADLINE_DOSE))]
    if len(mag) == 0:
        print("  no magnetic rows at the headline dose - nothing to test")
        return
    per_batch = mag.groupby("batch")["RE"].mean().sort_index()
    for b, v in per_batch.items():
        print(f"  batch {b}: RE = {v:6.1%}")
    m, lo, hi = t_interval(per_batch.values)
    print(f"\n  mean RE over {len(per_batch)} batches: {m:.1%}   "
          f"95% t-interval [{lo:.1%}, {hi:.1%}]  (t = {T_CRIT_N3})")

    gap = np.nan
    if len(plain):
        pm = float(plain.groupby("batch")["RE"].mean().mean())
        gap = m - pm
        print(f"  plain clay mean RE: {pm:.1%}   magnetic minus plain: {gap*100:+.1f} points "
              f"(band is +/-{H11A_ARM_GAP*100:.0f})")

    if m < H11A_LB_PASS:
        verdict = ("FAIL - mean below 50%; the pre-registered response is a rerun at "
                   f"{H11A_RERUN_DOSE} g/L, reporting both")
    elif m >= H11A_MEAN_PASS and lo > H11A_LB_PASS and (not np.isfinite(gap) or abs(gap) <= H11A_ARM_GAP):
        verdict = "PASS - mean at or above 70%, lower bound clears 50%, arms within 15 points"
    elif m >= H11A_MEAN_PASS and H11A_LB_UNDERPOWERED <= lo <= H11A_LB_PASS:
        verdict = ("consistent, underpowered - the pre-registered likely reading: mean clears 70%, "
                   "interval does not clear 50%")
    else:
        verdict = "INCONCLUSIVE against the pre-registered band"
    print(f"\n  VERDICT: {verdict}")

    rng = np.random.default_rng(SEED)
    vals = per_batch.values
    draws = np.array([np.mean(rng.choice(vals, len(vals), replace=True)) for _ in range(N_BOOT)])
    blo, bhi = np.percentile(draws, [2.5, 97.5])
    print(f"  sensitivity only, batch-clustered bootstrap (n={N_BOOT}, seed={SEED}): "
          f"[{blo:.1%}, {bhi:.1%}] - NOT the pre-registered statistic")

    out.append(dict(metric="removal_magnetic_0.2", value=m, lo=lo, hi=hi, unit="fraction",
                    n=len(per_batch), verdict=verdict))
    if np.isfinite(gap):
        out.append(dict(metric="removal_magnetic_minus_plain", value=gap, lo=np.nan, hi=np.nan,
                        unit="fraction", n=len(per_batch), verdict=""))


def h11c(re_df, out):
    """H11c: the dose screen, s8."""
    print("\n" + "-" * 78)
    print("H11c  DOSE SCREEN")
    print("-" * 78)
    if len(re_df) == 0:
        print("  no treated jar rows")
        return None
    means, los, his = {}, {}, {}
    for dose in DOSE_LADDER:
        d = re_df[(re_df["arm"] == "magnetic") & (np.isclose(re_df["dose_g_L"], dose))]
        if len(d) == 0:
            continue
        per_batch = d.groupby("batch")["RE"].mean()
        m, lo, hi = t_interval(per_batch.values)
        means[dose], los[dose], his[dose] = m, lo, hi
        print(f"  {dose:>5.2f} g/L : mean RE {m:6.1%}   [{lo:6.1%}, {hi:6.1%}]   n = {len(per_batch)}")
        out.append(dict(metric=f"removal_dose_{dose}", value=m, lo=lo, hi=hi, unit="fraction",
                        n=len(per_batch), verdict=""))
    if len(means) < 2:
        print("  too few doses to judge")
        return None

    doses = sorted(means)
    ordered = all(means[a] <= means[b] + 1e-12 for a, b in zip(doses, doses[1:]))
    print(f"\n  ordered means non-decreasing: {'yes' if ordered else 'no'}")

    d90, lohi = None, None
    for a, b in zip(doses, doses[1:]):
        if means[a] < 0.90 <= means[b]:
            frac = (0.90 - means[a]) / (means[b] - means[a])
            d90 = 10 ** (np.log10(a) + frac * (np.log10(b) - np.log10(a)))
            lohi = (a, b)
            break
    if d90 is not None:
        print(f"  D90 = {d90:.3f} g/L, log-linear interpolation between {lohi[0]} and {lohi[1]} g/L")
        out.append(dict(metric="D90", value=d90, lo=np.nan, hi=np.nan, unit="g_per_L",
                        n=len(doses), verdict="bracketed"))
    elif means[doses[-1]] < 0.90:
        print(f"  D90 > {doses[-1]} g/L - not bracketed by two adjacent means, so not testable")
        out.append(dict(metric="D90", value=np.nan, lo=np.nan, hi=np.nan, unit="g_per_L",
                        n=len(doses), verdict=f"> {doses[-1]} g/L, not testable"))
    else:
        print(f"  D90 < {doses[0]} g/L - not bracketed by two adjacent means, so not testable")
        out.append(dict(metric="D90", value=np.nan, lo=np.nan, hi=np.nan, unit="g_per_L",
                        n=len(doses), verdict=f"< {doses[0]} g/L, not testable"))
    return means, los, his


# --- recovery (tank runs) ----------------------------------------------------
def tank_table(df):
    """Recovery, solids and mass balance per tank run, s7 and s8."""
    tanks = df[df["vessel"] == "tank"].copy()
    if len(tanks) == 0:
        return pd.DataFrame()
    tanks["fraction"] = tanks["notes"].map(S.parse_fraction)
    rows = []
    for run, d in tanks.groupby("batch"):
        dose_g_L = float(d["dose_g_L"].iloc[0])
        solids_dosed = dose_g_L * TANK_VOLUME_L
        mag_dosed = MAGNETITE_FRACTION * solids_dosed

        pad = d[d["fraction"] == "pad"]
        W = one(pad, "wet_mass")
        D = one(pad, "dry_mass")
        pad_solids = ((D - SALT_FRACTION * W) / (1 - SALT_FRACTION)
                      if np.isfinite(W) and np.isfinite(D) else np.nan)

        mag = {f: one(d[d["fraction"] == f], "magnetite_equiv") for f in ("pad", "i", "ii", "iii")}
        recovery = mag["pad"] / mag_dosed if np.isfinite(mag["pad"]) and mag_dosed > 0 else np.nan
        accounted = float(np.nansum([mag[f] for f in ("pad", "i", "ii", "iii")]))

        c20 = one(d, "cell_count", T_min=20)
        c33 = one(d, "cell_count", T_min=33)
        rows.append(dict(run=run, dose_g_L=dose_g_L, solids_dosed_g=solids_dosed,
                         mag_dosed_g=mag_dosed, pad_wet_g=W, pad_dry_g=D, pad_solids_g=pad_solids,
                         solids_recovery=(pad_solids / solids_dosed
                                          if np.isfinite(pad_solids) and solids_dosed > 0 else np.nan),
                         mag_pad_g=mag["pad"], mag_i_g=mag["i"], mag_ii_g=mag["ii"], mag_iii_g=mag["iii"],
                         recovery=recovery, unaccounted_g=mag_dosed - accounted,
                         resuspension_index=c33 / c20 if np.isfinite(c20) and c20 > 0 else np.nan))
    return pd.DataFrame(rows)


def frac_iii_note(g):
    if not np.isfinite(g):
        return "not measured"
    if g < FRAC_III_FLOOR_G:
        return f"{g*1000:.1f} mg, below the {FRAC_III_FLOOR_G*1000:.0f} mg detection floor"
    if g < FRAC_III_QUANT_G:
        return (f"{g*1000:.1f} mg, detected but below the {FRAC_III_QUANT_G*1000:.0f} mg "
                "quantitation limit")
    return f"{g*1000:.1f} mg, quantitative"


def h11b(tanks, out):
    print("\n" + "-" * 78)
    print("H11b  RECOVERY and MASS BALANCE, per tank run")
    print("-" * 78)
    if len(tanks) == 0:
        print("  no tank rows")
        return
    print(f"  {'run':<5}{'recovery':>10}{'solids':>9}{'pad g':>9}{'i g':>8}{'ii g':>8}"
          f"{'iii g':>8}{'unacc g':>10}{'resusp':>8}")
    for _, r in tanks.iterrows():
        print(f"  {r['run']:<5}{r['recovery']:>9.1%}{r['solids_recovery']:>9.1%}"
              f"{r['mag_pad_g']:>9.4f}{r['mag_i_g']:>8.4f}{r['mag_ii_g']:>8.4f}"
              f"{r['mag_iii_g']:>8.4f}{r['unaccounted_g']:>10.4f}{r['resuspension_index']:>8.2f}")
    for _, r in tanks.iterrows():
        print(f"    {r['run']} fraction iii: {frac_iii_note(r['mag_iii_g'])}")

    rec = tanks["recovery"].dropna().values
    m, lo, hi = t_interval(rec)
    sol = float(tanks["solids_recovery"].dropna().mean())
    print(f"\n  mean magnetite recovery: {m:.1%}   95% t-interval [{lo:.1%}, {hi:.1%}]   n = {len(rec)}")
    print(f"  every run at or above {H11B_EACH_PASS:.0%}: "
          f"{'yes' if (rec >= H11B_EACH_PASS).all() else 'no'}"
          f"   |  mean total solids recovered: {sol:.1%} (band {H11B_SOLIDS_PASS:.0%})")

    ok = (m >= H11B_MEAN_PASS) and bool((rec >= H11B_EACH_PASS).all()) and (sol >= H11B_SOLIDS_PASS)
    verdict = ("PASS - mean at or above 70%, every run at or above 60%, solids at or above 50%"
               if ok else "FAIL against the pre-registered band")
    print(f"\n  VERDICT: {verdict}")
    print(f"  resuspension index, mean {tanks['resuspension_index'].mean():.2f} "
          "(above 1 means the sweep stirred cells back up; counting alone moves this about +/-20%)")

    out.append(dict(metric="magnetite_recovery", value=m, lo=lo, hi=hi, unit="fraction",
                    n=len(rec), verdict=verdict))
    out.append(dict(metric="solids_recovery", value=sol, lo=np.nan, hi=np.nan, unit="fraction",
                    n=len(tanks), verdict=""))
    out.append(dict(metric="resuspension_index", value=float(tanks["resuspension_index"].mean()),
                    lo=np.nan, hi=np.nan, unit="ratio", n=len(tanks), verdict=""))


def counters(df, out):
    print("\n" + "-" * 78)
    print("INTER-COUNTER AGREEMENT")
    print("-" * 78)
    d = df[df["measure"] == "cell_count"].copy()
    d["counter"] = d["counter"].astype(str)
    pairs = []
    for _, g in d.groupby(["date", "vessel", "arm", "T_min"]):
        g2 = g[g["counter"].str.len() > 0]
        names = sorted(g2["counter"].unique())
        if len(names) >= 2:
            a = float(g2[g2["counter"] == names[0]]["value"].mean())
            b = float(g2[g2["counter"] == names[1]]["value"].mean())
            pairs.append((a, b))
    if len(pairs) < 2:
        print("  fewer than two duplicate counts in this sheet - agreement not computable")
        return
    a = np.array([p[0] for p in pairs], float)
    b = np.array([p[1] for p in pairs], float)
    mard = float(np.mean(np.abs(a - b) / ((a + b) / 2)))
    ccc = lin_ccc(a, b)
    print(f"  duplicate counts: {len(pairs)}   mean absolute relative difference: {mard:.1%}"
          f"   Lin's concordance: {ccc:.3f}")
    out.append(dict(metric="counter_MARD", value=mard, lo=np.nan, hi=np.nan, unit="fraction",
                    n=len(pairs), verdict=""))
    out.append(dict(metric="counter_CCC", value=ccc, lo=np.nan, hi=np.nan, unit="coefficient",
                    n=len(pairs), verdict=""))


def planted_truth(re_df, tanks):
    """Only fires on synthetic data: prints what was planted next to what came back."""
    if not os.path.exists(TRUTH):
        return
    truth = json.load(open(TRUTH, encoding="utf-8"))
    print("\n" + "-" * 78)
    print("PLANTED TRUTH vs RECOVERED  (synthetic data only - absent for real measurements)")
    print("-" * 78)
    mag = re_df[(re_df["arm"] == "magnetic") & (np.isclose(re_df["dose_g_L"], HEADLINE_DOSE))] \
        if len(re_df) else re_df
    got_re = float(mag.groupby("batch")["RE"].mean().mean()) if len(mag) else np.nan
    got_rec = float(tanks["recovery"].mean()) if len(tanks) else np.nan
    print(f"  scenario: {truth.get('scenario', '?')}   seed: {truth.get('seed', '?')}")
    print(f"  {'quantity':<40}{'planted':>12}{'recovered':>14}")
    print(f"  {'mean removal, magnetic at 0.2 g/L':<40}"
          f"{truth.get('mean_re_magnetic_0p2', float('nan')):>11.1%}{got_re:>14.1%}")
    print(f"  {'mean magnetite recovery':<40}"
          f"{truth.get('mean_magnetite_recovery', float('nan')):>11.1%}{got_rec:>14.1%}")
    d90t = truth.get("curve", {}).get("d90_true_g_L", None)
    print(f"  {'true D90 (g/L)':<40}{str(d90t):>11} {'see H11c above':>14}")


def figure(re_df, tanks, dose_stats):
    os.makedirs(os.path.dirname(OUT_FIG), exist_ok=True)
    fig, ax = plt.subplots(1, 3, figsize=(13.5, 4.2))
    ink, sea, oxide = "#17232b", "#2d7f8f", "#8a3b1f"

    a = ax[0]
    for j, arm in enumerate(("plain", "magnetic")):
        d = re_df[(re_df["arm"] == arm) & (np.isclose(re_df["dose_g_L"], HEADLINE_DOSE))] \
            if len(re_df) else re_df
        if len(d) == 0:
            continue
        per_batch = d.groupby("batch")["RE"].mean()
        m, lo, hi = t_interval(per_batch.values)
        a.scatter([j] * len(per_batch), per_batch.values, s=20, color="#9aa7ad", zorder=3)
        a.errorbar([j], [m], yerr=[[max(m - lo, 0)], [max(hi - m, 0)]], fmt="o",
                   color=sea if arm == "magnetic" else oxide, capsize=5, ms=7, zorder=4)
    a.axhline(H11A_MEAN_PASS, ls="--", lw=1, color=ink, alpha=.5)
    a.text(1.45, H11A_MEAN_PASS + .015, "H11a band, 70%", fontsize=8, ha="right", color=ink)
    a.set_xlim(-0.5, 1.5)
    a.set_xticks([0, 1])
    a.set_xticklabels(["plain", "magnetic"])
    a.set_ylim(0, 1.05)
    a.set_ylabel("removal at 5 h, control-corrected")
    a.set_title("Removal at %.2f g/L\npoints are batch means, bar is the t-interval" % HEADLINE_DOSE,
                fontsize=9)

    b = ax[1]
    if len(tanks):
        x = np.arange(len(tanks))
        pad = tanks["recovery"].values
        fi = (tanks["mag_i_g"] / tanks["mag_dosed_g"]).values
        fii = (tanks["mag_ii_g"] / tanks["mag_dosed_g"]).values
        fiii = (tanks["mag_iii_g"] / tanks["mag_dosed_g"]).values
        b.bar(x, pad, color=sea, width=.55, label="pad (recovered)")
        b.bar(x, fi, bottom=pad, color="#9dbfc7", width=.55, label="on the tubes")
        b.bar(x, fii, bottom=pad + fi, color="#d9c6bb", width=.55, label="left on the floor")
        b.bar(x, fiii, bottom=pad + fi + fii, color=oxide, width=.55, label="in the water")
        b.axhline(H11B_MEAN_PASS, ls="--", lw=1, color=ink, alpha=.5)
        b.set_xticks(x)
        b.set_xticklabels(tanks["run"])
        b.set_ylim(0, 1.05)
        b.set_ylabel("share of dosed magnetite")
        b.legend(fontsize=7, frameon=False, loc="lower right")
        b.set_title("Recovery and where the rest went\nH11b band at 70%", fontsize=9)

    c = ax[2]
    if dose_stats:
        means, los, his = dose_stats
        ds = sorted(means)
        yerr = [[max(means[d] - los[d], 0) for d in ds], [max(his[d] - means[d], 0) for d in ds]]
        c.errorbar(ds, [means[d] for d in ds], yerr=yerr, fmt="o-", color=sea, capsize=4, ms=6)
        c.axhline(0.90, ls="--", lw=1, color=oxide, alpha=.7)
        c.text(ds[0], 0.915, "90%", fontsize=8, color=oxide)
        c.set_xscale("log")
        c.set_xlabel("dose, g/L")
        c.set_ylim(0, 1.05)
        c.set_ylabel("removal at 5 h")
        c.set_title("Dose screen\nD90 read only when two doses bracket 90%", fontsize=9)

    for a_ in ax:
        a_.spines["top"].set_visible(False)
        a_.spines["right"].set_visible(False)
        a_.tick_params(colors=ink, labelsize=8)
    fig.tight_layout()
    fig.savefig(OUT_FIG, dpi=150)
    print(f"\nwrote {OUT_FIG}")


def main(a):
    df = S.load(a.inp)
    complaints = S.validate(df)
    print("=" * 78)
    print("PHASE 11 BENCH ANALYSIS  -  notes/LAB_PROTOCOL.md s8")
    print("=" * 78)
    print(f"rows: {len(df)}   source: {a.inp}")
    print(f"schema complaints: {len(complaints)}")
    for c in complaints[:10]:
        print(f"  ! {c}")
    if complaints and not a.force:
        print("\nrefusing to analyse a sheet that does not validate. Fix the rows, or pass --force.")
        return

    re_df = removal_table(df)
    out = []
    h11a(re_df, out)
    dose_stats = h11c(re_df, out)
    tanks = tank_table(df)
    h11b(tanks, out)
    counters(df, out)
    planted_truth(re_df, tanks)

    os.makedirs(os.path.dirname(OUT_SUMMARY), exist_ok=True)
    pd.DataFrame(out).to_csv(OUT_SUMMARY, index=False, float_format="%.6g")
    print(f"\nwrote {OUT_SUMMARY}")
    figure(re_df, tanks, dose_stats)

    print("\n" + "=" * 78)
    print("Reading the result: removal and recovery are judged against bands fixed in")
    print("September 2026, before any measurement existed. A mean that clears 70% with an")
    print("interval that does not clear 50% is the pre-registered likely reading and is")
    print("reported as 'consistent, underpowered' - neither a pass nor a failure. Three")
    print("batches cannot carry a bootstrap, so the t-interval is the pre-registered")
    print("statistic and the bootstrap line above is a sensitivity check only.")
    print("=" * 78)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Phase 11 bench analysis")
    ap.add_argument("--in", dest="inp", default=IN_ROWS)
    ap.add_argument("--force", action="store_true", help="analyse even if the sheet does not validate")
    main(ap.parse_args())
