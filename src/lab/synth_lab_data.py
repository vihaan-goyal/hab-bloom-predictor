"""
synth_lab_data.py
-----------------
A complete synthetic December season in the notes/LAB_PROTOCOL.md s9 row contract,
generated under a KNOWN planted truth, so that analyze_lab.py can be written and
verified now - before the bench exists - rather than against the real numbers.

Why. Phase 11 (notes/SCIENTIFIC_METHOD.md) is pre-registered: the bands, the
estimator and the pass rules are fixed before any measurement. The risk that
pre-registration is supposed to remove is an analysis quietly shaped by the data it
is run on. Writing the analysis against synthetic data whose answer is already known
closes that door: on the day the real CSV arrives, the only thing that changes is the
input path.

What is planted
  - A log-logistic dose-response RE(d) = re_max / (1 + (ed50/d)^hill), parameterised
    by the removal at 0.2 g/L and by D90 (the dose that reaches 90% removal), so the
    H11a headline and the H11c curve cannot disagree with each other by construction.
  - Between-batch scatter as an explicit per-batch offset on RE (s5.3 runs three
    weekly batches; batch is the unit of replication, n = 3).
  - Counting noise as Poisson on the number of cells actually counted (~400 where
    density allows, s7), not as an arbitrary percentage - so the error bars have the
    size the Sedgewick-Rafter procedure really gives.
  - Per-run magnetite recovery, the s7 mass-balance split (pad, fractions i/ii/iii)
    and the pad solids fraction, with the seawater salt correction applied backwards
    to produce a consistent wet mass W and dry mass D.

Scenarios (--scenario), each a different planted truth:
  pass         comfortable pass on H11a and H11b, D90 bracketed inside the ladder
  underpowered mean RE >= 70% but the n = 3 t-interval lower bound lands in 40-50%,
               the pre-registered "consistent, underpowered" reading
  fail         mean RE < 50%, which triggers the pre-registered 0.6 g/L rerun; the
               tank runs also miss H11b, to exercise that branch
  unbracketed  D90 above 0.4 g/L, so it cannot be interpolated and reads "not testable"

Outputs
  data/lab/lab_measurements.csv   the season in the s9 row contract
  data/lab/synth_truth.json       sidecar of every planted parameter

Run from repo root:
    python src/lab/synth_lab_data.py
    python src/lab/synth_lab_data.py --scenario underpowered
"""
import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.lab.lab_schema import COLUMNS  # noqa: E402

OUT_DIR = "data/lab"
OUT_ROWS = "data/lab/lab_measurements.csv"
OUT_TRUTH = "data/lab/synth_truth.json"

SEED = 42

# --- protocol constants (notes/LAB_PROTOCOL.md s3, s5, s6) ------------------
BATCH_DATES = {"B1": "2026-11-12", "B2": "2026-11-19", "B3": "2026-12-01"}
TANK_DATES = {"T1": "2026-12-08", "T2": "2026-12-10", "T3": "2026-12-15"}
ICP_BATCH = "B2"                       # s5.3: ICP aluminium in batch 2 only
ROUTE = "S"                            # the Oct 30 amendment, assumed here
C0_CELLS = 1.0e4                       # cells/mL at dosing, s5.3 / s6
COUNT_TARGET = 400                     # s7: count >= 400 cells where density allows
CHL_PER_CELL = 3.0e-4                  # ug/L per cell/mL at this cell size
TANK_L, JAR_L = 20.0, 1.8
DOSE_TANK = 0.2                        # g/L, s5.4
MAGNETITE_FRAC = 0.20                  # s3.3 magnetic blend = 20% magnetite
SALT_FRACTION = 0.035                  # S in solids = (D - S*W)/(1 - S), s7
PAD_SOLIDS_FRACTION = 0.12             # wet pad is ~12% solids by mass
CONTROL_RATIO = 0.90                   # untreated Ct/C0 at 5 h (settling + grazing-free decay)

# jar layout, s5.3. Round 1 = the three-arm comparison; the dose screen is jar3
# (0.2 g/L, shared with round 1) plus jars 4-6, with jar1 as the control.
JARS = [
    ("jar1", "untreated", 0.00, 1),
    ("jar2", "plain",     0.20, 1),
    ("jar3", "magnetic",  0.20, 1),
    ("jar4", "magnetic",  0.05, 2),
    ("jar5", "magnetic",  0.10, 2),
    ("jar6", "magnetic",  0.40, 3),
]
COUNTERS = ("VG", "RS")                # s1: a second counter trained before Nov 9
N_DUPLICATE_COUNTS = 5                 # s7: five samples counted by both counters

# --- planted truths ---------------------------------------------------------
SCENARIOS = {
    "pass": dict(
        re_at_02=0.92, d90_true=0.15, hill=1.5,
        batch_offsets=[0.02, -0.01, -0.01], plain_delta=-0.03,
        pad_magnetite_rec=[0.89, 0.87, 0.88],
        frac_i=[0.035, 0.040, 0.030], frac_ii=[0.045, 0.050, 0.040],
        frac_iii_mg=[6.0, 14.0, 25.0],
        pad_solids_rec=[0.72, 0.70, 0.74],
    ),
    "underpowered": dict(
        re_at_02=0.75, d90_true=0.35, hill=1.5,
        batch_offsets=[0.115, 0.000, -0.115], plain_delta=-0.04,
        pad_magnetite_rec=[0.89, 0.87, 0.88],
        frac_i=[0.035, 0.040, 0.030], frac_ii=[0.045, 0.050, 0.040],
        frac_iii_mg=[6.0, 14.0, 25.0],
        pad_solids_rec=[0.72, 0.70, 0.74],
    ),
    "fail": dict(
        re_at_02=0.35, d90_true=1.20, hill=1.5,
        batch_offsets=[0.03, -0.01, -0.02], plain_delta=-0.02,
        pad_magnetite_rec=[0.58, 0.52, 0.55],
        frac_i=[0.060, 0.055, 0.058], frac_ii=[0.150, 0.170, 0.160],
        frac_iii_mg=[6.0, 14.0, 25.0],
        pad_solids_rec=[0.45, 0.42, 0.44],
    ),
    "unbracketed": dict(
        re_at_02=0.80, d90_true=0.75, hill=1.5,
        batch_offsets=[0.02, -0.01, -0.01], plain_delta=-0.03,
        pad_magnetite_rec=[0.89, 0.87, 0.88],
        frac_i=[0.035, 0.040, 0.030], frac_ii=[0.045, 0.050, 0.040],
        frac_iii_mg=[6.0, 14.0, 25.0],
        pad_solids_rec=[0.72, 0.70, 0.74],
    ),
}
RESUSPENSION_TRUE = 1.12               # s8 resuspension index = T33 count / T20 count
FLOC_D50_TRUE_UM = 66.0                # s6 T11 floc photo


# ---------------------------------------------------------------------------
# 1. Planted dose-response
# ---------------------------------------------------------------------------
def solve_curve(re_at_02, d90_true, hill):
    """re_max, ed50 of RE(d) = re_max/(1+(ed50/d)^hill) with RE(0.2)=re_at_02 and
    RE(d90_true)=0.90. Bisection on ed50; both roots are monotone in ed50."""
    def f(u):
        return re_at_02 * (1 + (u / 0.2) ** hill) / (1 + (u / d90_true) ** hill) - 0.90
    lo, hi = 1e-6, 50.0
    flo, fhi = f(lo), f(hi)
    if flo * fhi > 0:
        raise ValueError(f"no curve with RE(0.2)={re_at_02} and D90={d90_true}")
    for _ in range(200):
        mid = np.sqrt(lo * hi)
        if f(mid) * flo > 0:
            lo, flo = mid, f(mid)
        else:
            hi = mid
    ed50 = float(np.sqrt(lo * hi))
    re_max = float(re_at_02 * (1 + (ed50 / 0.2) ** hill))
    return re_max, ed50


def re_curve(d, re_max, ed50, hill):
    return re_max / (1.0 + (ed50 / d) ** hill)


# ---------------------------------------------------------------------------
# 2. Measurement models
# ---------------------------------------------------------------------------
def observed_count(rng, true_conc, target=COUNT_TARGET):
    """s7 counting: count `target` cells where density allows, otherwise everything in
    the 1 mL chamber. Poisson on the cells actually counted -> relative sd 1/sqrt(n)."""
    lam = float(min(target, max(true_conc, 1.0)))
    counted = rng.poisson(lam)
    return float(round(true_conc * counted / lam))


def jitter(rng, x, rel_sd):
    return float(x * np.exp(rng.normal(0.0, rel_sd) - 0.5 * rel_sd ** 2))


# ---------------------------------------------------------------------------
# 3. Row builders
# ---------------------------------------------------------------------------
def row(date, batch, vessel, arm, dose, route, t_min, measure, value, unit,
        counter="", notes=""):
    return dict(date=date, batch=batch, vessel=vessel, arm=arm, dose_g_L=dose,
                route=route, T_min=int(t_min), measure=measure, value=value,
                unit=unit, counter=counter, notes=notes)


def build_jars(rng, p, re_max, ed50, hill):
    """The three weekly jar batches, s5.3."""
    rows, truth_re = [], {}
    for bi, (batch, date) in enumerate(BATCH_DATES.items()):
        offset = p["batch_offsets"][bi]
        c0_true = jitter(rng, C0_CELLS, 0.06)          # batch bottle density varies
        ctrl_ratio = jitter(rng, CONTROL_RATIO, 0.04)
        c0_obs = observed_count(rng, c0_true)
        ct_ctrl_true = c0_true * ctrl_ratio

        rows.append(row(date, batch, "jar1", "untreated", 0.0, "", 0, "salinity",
                        round(jitter(rng, 27.5, 0.01), 1), "psu", "",
                        "batch bottle, s3.1"))
        rows.append(row(date, batch, "jar1", "untreated", 0.0, "", 0, "temp",
                        round(jitter(rng, 19.0, 0.01), 1), "degC", "",
                        "batch bottle, s3.1"))
        rows.append(row(date, batch, "jar1", "untreated", 0.0, "", 0, "chl_a",
                        round(jitter(rng, c0_true * CHL_PER_CELL, 0.08), 2),
                        "ug_per_L", "", "t0 from batch bottle, s5.3"))

        for vessel, arm, dose, rnd in JARS:
            route = "" if arm == "untreated" else ROUTE
            if arm == "untreated":
                re_true = 0.0
            elif arm == "plain":
                re_true = float(np.clip(re_curve(dose, re_max, ed50, hill)
                                        + offset + p["plain_delta"], 0.0, 0.99))
            else:
                re_true = float(np.clip(re_curve(dose, re_max, ed50, hill)
                                        + offset, 0.0, 0.99))
            truth_re[(batch, vessel)] = re_true

            ct_true = ct_ctrl_true * (1.0 - re_true)
            c24_true = ct_true * jitter(rng, 0.95, 0.05)

            # t0 count: one batch-bottle count, carried onto every jar (s5.3)
            rows.append(row(date, batch, vessel, arm, dose, route, 0, "cell_count",
                            c0_obs, "cells_per_mL", COUNTERS[0],
                            f"round={rnd}; t0 from batch bottle"))
            if batch == ICP_BATCH:      # s5.3: ICP aluminium is the first 5 h draw
                al = 8.0 if arm == "untreated" else 1100.0 * dose + rng.normal(0, 12)
                rows.append(row(date, batch, vessel, arm, dose, route, 300, "icp_al",
                                round(max(al, 0.0), 1), "ug_per_L", "",
                                f"round={rnd}; 0.45 um filtered, partner lab"))
            rows.append(row(date, batch, vessel, arm, dose, route, 300, "cell_count",
                            observed_count(rng, ct_true), "cells_per_mL", COUNTERS[0],
                            f"round={rnd}; 5 h"))
            rows.append(row(date, batch, vessel, arm, dose, route, 300, "chl_a",
                            round(jitter(rng, ct_true * CHL_PER_CELL, 0.10), 2),
                            "ug_per_L", "", f"round={rnd}; 5 h, 250 mL on GF/F"))
            rows.append(row(date, batch, vessel, arm, dose, route, 300, "do",
                            round(jitter(rng, 8.4, 0.02), 2), "mg_per_L", "",
                            f"round={rnd}; 5 h, in jar"))
            rows.append(row(date, batch, vessel, arm, dose, route, 300, "ph",
                            round(jitter(rng, 8.05, 0.004), 2), "pH", "",
                            f"round={rnd}; 5 h, in jar"))
            rows.append(row(date, batch, vessel, arm, dose, route, 1440, "cell_count",
                            observed_count(rng, c24_true), "cells_per_mL", COUNTERS[0],
                            f"round={rnd}; 24 h"))

        # The s5.3 seawater blank and filter blank are submitted to the partner lab as
        # QC samples; the s9 `vessel` vocabulary has no blank vessel, so they live in
        # the partner's report, not in this file.
    return rows, truth_re


def add_duplicate_counts(rng, rows):
    """s7: five 5 h counts read by both counters, for the agreement statistic."""
    idx = [i for i, r in enumerate(rows)
           if r["measure"] == "cell_count" and r["T_min"] == 300]
    pick = rng.choice(len(idx), size=min(N_DUPLICATE_COUNTS, len(idx)), replace=False)
    dups = []
    for k in sorted(pick):
        r = dict(rows[idx[k]])
        # counter B re-counts the same vial: same truth, independent Poisson draw
        r["value"] = observed_count(rng, r["value"])
        r["counter"] = COUNTERS[1]
        r["notes"] = r["notes"] + "; duplicate count"
        dups.append(r)
    return rows + dups


def build_tank(rng, p, re_max, ed50, hill):
    """The three tank runs, s5.4 / s6, and the s7 workup masses."""
    rows, truth = [], {}
    blend_g = DOSE_TANK * TANK_L                       # 4 g dry blend
    magnetite_g = blend_g * MAGNETITE_FRAC             # 0.8 g magnetite
    for ri, (run, date) in enumerate(TANK_DATES.items()):
        c0_true = jitter(rng, C0_CELLS, 0.05)
        re_true = float(np.clip(re_curve(DOSE_TANK, re_max, ed50, hill), 0.0, 0.99))

        # --- T-1 h "before" readings, s6 ---
        rows.append(row(date, run, "tank", "magnetic", DOSE_TANK, ROUTE, -60,
                        "cell_count", observed_count(rng, c0_true), "cells_per_mL",
                        COUNTERS[0], "before, s6"))
        for m, u, v, sd in (("chl_a", "ug_per_L", c0_true * CHL_PER_CELL, 0.08),
                            ("do", "mg_per_L", 8.6, 0.02),
                            ("ph", "pH", 8.06, 0.004),
                            ("salinity", "psu", 27.4, 0.01),
                            ("temp", "degC", 18.6, 0.01)):
            rows.append(row(date, run, "tank", "magnetic", DOSE_TANK, ROUTE, -60,
                            m, round(jitter(rng, v, sd), 2), u, "", "before, s6"))

        # --- in-run sequence ---
        rows.append(row(date, run, "tank", "magnetic", DOSE_TANK, ROUTE, 11,
                        "floc_d50", round(jitter(rng, FLOC_D50_TRUE_UM, 0.12), 1),
                        "um", "", "floc photo on ruler slide, s6"))
        c20_true = c0_true * 0.45
        c33_true = c20_true * RESUSPENSION_TRUE
        c300_true = c0_true * (1.0 - re_true)
        c1440_true = c300_true * jitter(rng, 0.95, 0.05)
        # s6 takes a floor sample and a DO spot read at T93, but no column count.
        for t, ct, note in ((20, c20_true, "column count at end-wall mark, s6"),
                            (33, c33_true, "column count at the T20 spot, s6"),
                            (300, c300_true, "5 h, s6"),
                            (1440, c1440_true, "24 h, s6")):
            rows.append(row(date, run, "tank", "magnetic", DOSE_TANK, ROUTE, t,
                            "cell_count", observed_count(rng, ct), "cells_per_mL",
                            COUNTERS[0], note))
        for t, turb in ((20, 0.185), (33, 0.205), (93, 0.075)):
            rows.append(row(date, run, "tank", "magnetic", DOSE_TANK, ROUTE, t,
                            "turbidity_750", round(jitter(rng, turb, 0.10), 4), "AU",
                            "", "floor sample, 10 mL at 750 nm, s6"))
        for t, do in ((20, 8.5), (93, 8.4)):
            rows.append(row(date, run, "tank", "magnetic", DOSE_TANK, ROUTE, t, "do",
                            round(jitter(rng, do, 0.02), 2), "mg_per_L", "",
                            "spot read, probe swirled, s6"))
        rows.append(row(date, run, "tank", "magnetic", DOSE_TANK, ROUTE, 300, "chl_a",
                        round(jitter(rng, c300_true * CHL_PER_CELL, 0.10), 2),
                        "ug_per_L", "", "5 h, 250 mL on GF/F, s6"))

        # --- s7 workup: pad wet/dry mass and magnetite by fraction ---
        pad_mag = magnetite_g * p["pad_magnetite_rec"][ri]
        f_i = magnetite_g * p["frac_i"][ri]
        f_ii = magnetite_g * p["frac_ii"][ri]
        f_iii = p["frac_iii_mg"][ri] / 1000.0
        pad_solids = blend_g * p["pad_solids_rec"][ri]
        wet = pad_solids / PAD_SOLIDS_FRACTION
        dry = pad_solids * (1 - SALT_FRACTION) + SALT_FRACTION * wet

        rows.append(row(date, run, "tank", "magnetic", DOSE_TANK, ROUTE, 1440,
                        "wet_mass", round(jitter(rng, wet, 0.01), 3), "g", "",
                        "fraction=pad; decanted over the block, s7"))
        rows.append(row(date, run, "tank", "magnetic", DOSE_TANK, ROUTE, 1440,
                        "dry_mass", round(jitter(rng, dry, 0.004), 3), "g", "",
                        "fraction=pad; 65 C to constant mass, s7"))
        rows.append(row(date, run, "tank", "magnetic", DOSE_TANK, ROUTE, 1440,
                        "magnetite_equiv", round(jitter(rng, pad_mag, 0.03), 4), "g",
                        "", "fraction=pad; mean of three 150 mg pull-test aliquots, s4.1"))
        for name, mag, solids_ratio, note in (
                ("i", f_i, 0.9, "fraction=i; tube rinses, s7"),
                ("ii", f_ii, 1.4, "fraction=ii; floor rinse, s7"),
                ("iii", f_iii, 2.2, "fraction=iii; 5 L supernatant, s7")):
            rows.append(row(date, run, "tank", "magnetic", DOSE_TANK, ROUTE, 1440,
                            "dry_mass",
                            round(jitter(rng, mag / MAGNETITE_FRAC * solids_ratio, 0.05), 4),
                            "g", "", note))
            rows.append(row(date, run, "tank", "magnetic", DOSE_TANK, ROUTE, 1440,
                            "magnetite_equiv", round(jitter(rng, mag, 0.05), 4), "g",
                            "", note))

        truth[run] = dict(magnetite_recovery=p["pad_magnetite_rec"][ri],
                          solids_recovery=p["pad_solids_rec"][ri],
                          frac_i=p["frac_i"][ri], frac_ii=p["frac_ii"][ri],
                          frac_iii_mg=p["frac_iii_mg"][ri],
                          resuspension_index=RESUSPENSION_TRUE)
    return rows, truth


# ---------------------------------------------------------------------------
# 4. Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[2])
    ap.add_argument("--scenario", choices=sorted(SCENARIOS), default="pass")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--out-dir", default=OUT_DIR)
    args = ap.parse_args()

    p = SCENARIOS[args.scenario]
    rng = np.random.default_rng(args.seed)
    re_max, ed50 = solve_curve(p["re_at_02"], p["d90_true"], p["hill"])
    ladder = [0.05, 0.10, 0.20, 0.40]
    re_by_dose = {f"{d:g}": float(re_curve(d, re_max, ed50, p["hill"])) for d in ladder}

    jar_rows, truth_re = build_jars(rng, p, re_max, ed50, p["hill"])
    jar_rows = add_duplicate_counts(rng, jar_rows)
    tank_rows, tank_truth = build_tank(rng, p, re_max, ed50, p["hill"])

    df = pd.DataFrame(jar_rows + tank_rows)[COLUMNS]
    os.makedirs(args.out_dir, exist_ok=True)
    out_rows = os.path.join(args.out_dir, "lab_measurements.csv")
    out_truth = os.path.join(args.out_dir, "synth_truth.json")
    df.to_csv(out_rows, index=False)

    mag02 = [truth_re[(b, "jar3")] for b in BATCH_DATES]
    plain02 = [truth_re[(b, "jar2")] for b in BATCH_DATES]
    truth = dict(
        scenario=args.scenario, seed=args.seed,
        curve=dict(re_max=re_max, ed50_g_L=ed50, hill=p["hill"],
                   d90_true_g_L=p["d90_true"], re_at_02=p["re_at_02"]),
        re_by_dose=re_by_dose,
        batch_offsets=p["batch_offsets"],
        re_magnetic_0p2_by_batch=dict(zip(BATCH_DATES, mag02)),
        re_plain_0p2_by_batch=dict(zip(BATCH_DATES, plain02)),
        mean_re_magnetic_0p2=float(np.mean(mag02)),
        mean_re_plain_0p2=float(np.mean(plain02)),
        control_ratio=CONTROL_RATIO,
        magnetite_dosed_g=DOSE_TANK * TANK_L * MAGNETITE_FRAC,
        solids_dosed_g=DOSE_TANK * TANK_L,
        mean_magnetite_recovery=float(np.mean(p["pad_magnetite_rec"])),
        mean_solids_recovery=float(np.mean(p["pad_solids_rec"])),
        tank_runs=tank_truth,
        resuspension_index=RESUSPENSION_TRUE,
        floc_d50_um=FLOC_D50_TRUE_UM,
        salt_fraction=SALT_FRACTION,
    )
    with open(out_truth, "w") as fh:
        json.dump(truth, fh, indent=2)

    print("--- synthetic lab season -------------------------------------------")
    print(f"scenario           {args.scenario}   seed {args.seed}")
    print(f"planted curve      re_max {re_max:.3f}, ed50 {ed50:.4f} g/L, "
          f"hill {p['hill']:g}, D90 {p['d90_true']:g} g/L")
    print("planted RE by dose " + ", ".join(f"{d} g/L {100*v:.1f}%"
                                            for d, v in re_by_dose.items()))
    print(f"planted mean RE    magnetic 0.2 g/L {100*np.mean(mag02):.1f}%  "
          f"(batches {', '.join(f'{100*x:.1f}%' for x in mag02)})")
    print(f"                   plain 0.2 g/L    {100*np.mean(plain02):.1f}%")
    print(f"planted recovery   magnetite {100*np.mean(p['pad_magnetite_rec']):.1f}%  "
          f"solids {100*np.mean(p['pad_solids_rec']):.1f}%")
    print(f"rows               {len(df):,}  "
          f"({len(jar_rows):,} jar, {len(tank_rows):,} tank)")
    print(f"measures           {', '.join(sorted(df['measure'].unique()))}")
    print("--- written ---------------------------------------------------------")
    print(f"  {out_rows}")
    print(f"  {out_truth}")
    print()
    print("Reading the result:")
    print("  These numbers are invented, and that is the point. They exist so that")
    print("  analyze_lab.py can be run, read and argued about today, while nothing in")
    print("  it can be tuned to a December measurement. If the recovered numbers in")
    print("  analyze_lab.py match the planted ones printed above, the analysis is")
    print("  doing what the protocol says, and in December only the input file changes.")


if __name__ == "__main__":
    main()
