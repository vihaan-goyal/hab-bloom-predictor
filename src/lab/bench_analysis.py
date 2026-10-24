"""
bench_analysis.py -- the pre-registered analysis of the bench treatment experiments
==================================================================================
Computes every endpoint and every PASS / FAIL / INCONCLUSIVE decision in
notes/mitigation/BENCH_PREREG.md (written 2026-10-24, before any tank data). The rules live
in the constants below; the prereg quotes the same numbers. Changing a number here after data
exist is a protocol change and must be logged as a dated amendment in the prereg.

Experiments (the `experiment` column):
    aeration_screen   36 x 1 L flasks: still / gentle / low (25 mL/min) / high (300 mL/min)
                      x nanno / thal / akashiwo x 3; 48 h ON, 48 h regrowth
    peroxide_screen   60 x 250 mL flasks: ctrl, h2o2_0.8, h2o2_1.6, h2o2_3.2, h2o2_6.4 (x 3 species),
                      pulse3_0.8 (nanno), percarb_0.8 (x 3 species), carbonate (nanno); 72 h
    halflife          H2O2 decay in plain seawater, no algae: seawater_h2o2, seawater_percarb
    aeration_loop     tanks, arms A (untreated), B (forecast loop), C (reactive), D (false alarm),
    peroxide_loop     P (pilot bloom, warm-up only)

Judging rule (Dr. P. Vlahos, UConn, 2026-10-15): treatments are judged on the percent change of
each vessel against its own start, measured by cell counts. The DIY fluorometer is a secondary
endpoint until it is calibrated (EXECUTION_PLAN.md s14). No ug/L is needed anywhere here.

Input 1: tank_log.csv -- one row per vessel per timepoint (template: src/lab/templates/tank_log.csv)
    date               YYYY-MM-DD
    experiment         one of the five above
    arm                screen arm name, or A / B / C / D / P
    species            nanno | thal | akashiwo | mix | none
    tank_id            neutral code from `layout` (e.g. AL07); it must not reveal the arm
    replicate          1, 2, 3 ...
    position           shelf position from `layout`
    volume_L           culture volume in the vessel
    day                days since Day 0 (loop runs; warm-up day 0, nutrients day 21)
    timepoint_h        hours since treatment start (screens); either day or timepoint_h is enough
    fl_counts          fluorometer reading (LED on - off), raw counts
    fl_blank_counts    clean-seawater blank read the same day (subtracted; blank = 0 if empty)
    temp_c, ph, do_mgL readings
    do_dawn            1 if the DO reading was taken at dawn (lights-on), else 0 / empty
    h2o2_mgL           peroxide residual, low-range kit; a reading below the kit's lowest step = 0
    airflow_mL_min     measured airflow (aeration vessels)
    dose_mgL           H2O2 added at this row (pulses), mg/L of vessel volume
    treatment_on_h     hours the treatment was ON since the previous row
    event              ON | OFF | FLOOR_OFF | SAFETY_STOP | MAX_ON | PULSE | SKIP | REFILL | HUMAN
    trigger            model | rule | reactive | forced  (on ON rows)
    artemia_start      nauplii put in (all wells of this vessel's water, e.g. 3 x 10 = 30)
    artemia_alive_24h  survivors at 24 h;  artemia_alive_96h  survivors at 96 h (peroxide)
    excluded           1 = exclude this vessel (fill exclusion_reason); see the prereg's rules
    exclusion_reason   contamination | equipment | crash | lost | other: <text>
    notes

Input 2: counts.csv -- one row per counted chamber (template: src/lab/templates/counts.csv)
    date, experiment, tank_id, day, timepoint_h
    size_class         all | small (< 5 um, nanno) | large (thal); mixed peroxide tanks only
    count_method       hemo_large (Neubauer 1 mm corner square, 0.1 uL) | hemo_small (0.2 mm
                       square, 0.004 uL) | sr (Sedgewick-Rafter 1 mm square, 1 uL)
    cells_counted      cells counted in those squares
    squares_counted    number of squares counted
    dilution_factor    (sample + diluent + fixative) / sample; 1 if undiluted
    foreign_cells      cells of any other species seen in the same squares
    grazers_seen       1 if ciliates / rotifers / other grazers were seen anywhere in the chamber
    counter            initials;  sample_code  blind code on the tube or photo;  notes

    cells/mL = cells_counted / (squares_counted x square volume in mL) x dilution_factor
    A zero count is kept as 0 cells/mL; logs use 0.5 cell in the counted volume instead.
    Repeated chambers for the same vessel, time and size class are averaged.

Outputs
    data/lab/bench/bench_results.csv   one row per endpoint, both analysis sets
    (stdout)                            the PASS / FAIL / INCONCLUSIVE table

Run from repo root:
    python src/lab/bench_analysis.py                                  # default data paths
    python src/lab/bench_analysis.py --log my_log.csv --counts my_counts.csv
    python src/lab/bench_analysis.py layout --experiment aeration_loop --seed 20261110
"""
import argparse
import itertools
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

TEMPLATE_DIR = "src/lab/templates"
IN_LOG = "data/lab/bench/tank_log.csv"
IN_COUNTS = "data/lab/bench/counts.csv"
OUT_CSV = "data/lab/bench/bench_results.csv"

LOG_COLUMNS = ["date", "experiment", "arm", "species", "tank_id", "replicate", "position",
               "volume_L", "day", "timepoint_h", "fl_counts", "fl_blank_counts", "temp_c", "ph",
               "do_mgL", "do_dawn", "h2o2_mgL", "airflow_mL_min", "dose_mgL", "treatment_on_h",
               "event", "trigger", "artemia_start", "artemia_alive_24h", "artemia_alive_96h",
               "excluded", "exclusion_reason", "notes"]
COUNT_COLUMNS = ["date", "experiment", "tank_id", "day", "timepoint_h", "size_class",
                 "count_method", "cells_counted", "squares_counted", "dilution_factor",
                 "foreign_cells", "grazers_seen", "counter", "sample_code", "notes"]
EXPERIMENTS = ("aeration_screen", "peroxide_screen", "halflife", "aeration_loop", "peroxide_loop")
EVENTS = ("ON", "OFF", "FLOOR_OFF", "SAFETY_STOP", "MAX_ON", "PULSE", "SKIP", "REFILL", "HUMAN")
OFF_EVENTS = ("OFF", "FLOOR_OFF", "SAFETY_STOP", "MAX_ON")

# --- pre-registered constants (BENCH_PREREG.md; every number fixed 2026-10-24) -------------
CONF = 0.95                      # two-sided Welch intervals everywhere (one-sided 2.5% per side)
SQUARE_ML = {"hemo_large": 1e-4, "hemo_small": 4e-6, "sr": 1e-3}
ZERO_COUNT_CELLS = 0.5           # a zero count is logged as half a cell in the counted volume
LOW_COUNT_FLAG = 50              # fewer cells than this per sample: flagged (Poisson CV > 14%)
TIME_TOL_H = 4.0                 # a screen reading counts for nominal time t if within +/- 4 h
MIN_N = 2                        # fewer valid vessels than this in an arm -> INCONCLUSIVE
# exclusions (never based on the outcome)
CONTAM_FRAC = 0.10               # foreign cells > 10% of cells seen ...
CONTAM_RUN = 2                   # ... (or grazers seen) in 2 consecutive counts -> contamination
PRE_CRASH_FRAC = 0.10            # loop: a count before nutrients-in < 10% of the day-0 count
DOSE_OK = (0.5, 1.5)             # screen: 0 h residual outside 50-150% of nominal -> dose error
AIRFLOW_TOL = 0.25               # screen: airflow > 25% off nominal on 2 consecutive checks
# validity checks (arm level; they make a comparison INCONCLUSIVE, they exclude nobody)
CONTROL_CRASH = 0.5              # screen control's geometric-mean N_t/N_0 below this = crashed
NO_BLOOM = 2.0                   # loop: arm A geometric-mean peak / warm-up below this = no bloom
# aeration screen
S1_T_H, S1_MARK, SPARED_MAX = 48.0, 0.30, 0.20
S1_OFF_H, S1_END_H = 48.0, 96.0
S1_FLOW = {"low": 25.0, "high": 300.0}
# peroxide screen
S3_T_H, S3_MARK, S3_REP_T_H = 72.0, 0.50, 24.0
ARTEMIA_MARGIN = -20.0           # survival points vs control (non-inferiority margin)
H5_T_H, H5_DOSES, H5_PASS_N, H5_FAIL_N = 24.0, (0.8, 1.6, 3.2, 6.4), 3, 1
CARB_FLAG = 0.20                 # carbonate alone cutting >= 20% means part of percarbonate is pH
PULSE_MGL, REDOSE_MAX, STOP_H2O2 = 0.8, 0.5, 2.8
H2O2_LOD = 0.1                   # readings at or below this are left out of the half-life fit
HALF_LIFE_FIT_H = 24.0
HALF_LIFE_DAILY_MAX_H = 24 * np.log(2) / np.log(PULSE_MGL / REDOSE_MAX)   # 35.4 h
SIM_HALF_LIFE_H = (2.4, 14.4)    # Layer 2 prior, method_params.csv peroxide half_life 0.1-0.6 d
# loop runs
WARM_FROM, NUTRIENTS_DAY, BLOOM_END, COOL_END = 14, 21, 40, 45
COK_FRAC = 0.5                   # C_ok = 50% of the mean pilot peak (cells/mL)
DELAY_MARK_D = 2.0               # H1-delay mark: one aeration X (48 h)
H1A_MARK, H1B_MARK = 0.50, 0.0
MAX_MISSING_DAYS = 2             # more than 2 uncovered days in 21-40 -> no days-below value
FLOOR, DO_ALLOW = 0.80, 0.5
SAFE_DO, SAFE_PH, SAFE_H2O2 = 4.0, (7.6, 8.6), STOP_H2O2   # SAFE_PH[1] = ceiling until the pilots set it
# pH ceiling for the loop runs (decided 2026-10-24): highest pH of the untreated pilot tanks + 0.2,
# never below 8.6 and never above 9.0 (above 9 pH itself inhibits algae and would confound the result)
PH_MARGIN, PH_CEIL_MIN, PH_CEIL_MAX = 0.2, 8.6, 9.0
LOOP_SIZE = {"aeration_loop": "all", "peroxide_loop": "small"}
LOOP_ARTEMIA = {"aeration_loop": ("24h",), "peroxide_loop": ("24h", "96h")}

DESIGNS = {
    "aeration_screen": [(a, s, 3) for a in ("still", "gentle", "low", "high")
                        for s in ("nanno", "thal", "akashiwo")],
    "peroxide_screen": [(a, s, 3) for a in ("ctrl", "h2o2_0.8", "h2o2_1.6", "h2o2_3.2", "h2o2_6.4",
                                            "percarb_0.8") for s in ("nanno", "thal", "akashiwo")]
                       + [("pulse3_0.8", "nanno", 3), ("carbonate", "nanno", 3)],
    "halflife": [("seawater_h2o2", "none", 3), ("seawater_percarb", "none", 3)],
    "aeration_loop": [(a, "akashiwo", 3) for a in "ABCD"] + [("P", "akashiwo", 2)],
    "peroxide_loop": [(a, "mix", 3) for a in "ABCD"] + [("P", "mix", 2)],
}
ID_PREFIX = {"aeration_screen": "AS", "peroxide_screen": "PS", "halflife": "HL",
             "aeration_loop": "AL", "peroxide_loop": "PL"}


# --- arithmetic ---------------------------------------------------------------------------
def cells_per_ml(cells_counted, squares_counted, count_method, dilution_factor=1.0):
    """Hemocytometer / Sedgewick-Rafter count -> cells per mL of the original sample."""
    vol = np.asarray(pd.Series(count_method).map(SQUARE_ML), dtype=float)
    if np.isnan(vol).any():
        raise ValueError(f"unknown count_method; use one of {sorted(SQUARE_ML)}")
    dil = pd.Series(dilution_factor).fillna(1.0).to_numpy(dtype=float)
    return np.asarray(cells_counted, dtype=float) / (np.asarray(squares_counted, dtype=float) * vol) * dil


def log_floor(cells, cells_counted, squares_counted, count_method, dilution_factor=1.0):
    """log(cells/mL) with a zero count replaced by half a cell in the counted volume."""
    floor = cells_per_ml(np.full(np.shape(cells), ZERO_COUNT_CELLS), squares_counted,
                         count_method, dilution_factor)
    return np.log(np.where(np.asarray(cells) > 0, cells, floor))


def welch(x, y, conf=CONF):
    """mean(x) - mean(y) with a Welch t interval. Returns (diff, lo, hi, df)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    d = x.mean() - y.mean()
    vx, vy = x.var(ddof=1) / len(x), y.var(ddof=1) / len(y)
    se = np.sqrt(vx + vy)
    if se == 0:
        return d, d, d, np.inf
    den = (vx ** 2 / (len(x) - 1) if vx > 0 else 0.0) + (vy ** 2 / (len(y) - 1) if vy > 0 else 0.0)
    df = (vx + vy) ** 2 / den
    t = stats.t.ppf(0.5 + conf / 2, df)
    return d, d - t * se, d + t * se, df


def perm_p(x, y, alternative="greater"):
    """Exact one-sided permutation p for mean(x) - mean(y) over every relabelling.
    With 3 vs 3 there are 20 relabellings, so the smallest possible p is 0.05."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    pool, nx = np.concatenate([x, y]), len(x)
    obs = x.mean() - y.mean()
    diffs = []
    for idx in itertools.combinations(range(len(pool)), nx):
        m = np.zeros(len(pool), bool)
        m[list(idx)] = True
        diffs.append(pool[m].mean() - pool[~m].mean())
    diffs = np.array(diffs)
    eps = 1e-12
    hit = diffs >= obs - eps if alternative == "greater" else diffs <= obs + eps
    return hit.mean()


def decide(est, lo, hi, mark):
    """The one decision rule for effect hypotheses (BENCH_PREREG.md 'How every test is decided').
    PASS: estimate >= mark AND lower 95% bound > 0.  FAIL: upper 95% bound < mark."""
    if np.isnan(est):
        return "INCONCLUSIVE"
    if est >= mark and lo > 0:
        return "PASS"
    if hi < mark:
        return "FAIL"
    return "INCONCLUSIVE"


def decide_safety(est, lo, margin=ARTEMIA_MARGIN):
    """Non-inferiority for survival (points). SAFE PASS: lower bound > margin.
    FAIL: estimate < margin. Otherwise INCONCLUSIVE (safety cannot be claimed)."""
    if np.isnan(est):
        return "INCONCLUSIVE"
    if lo > margin:
        return "PASS"
    if est < margin:
        return "FAIL"
    return "INCONCLUSIVE"


def cut_compare(trt, ctl, mark):
    """Percent cut of a treated arm vs its control from per-vessel log ratios.
    cut = 1 - exp(mean log trt - mean log ctl); interval from Welch on the logs."""
    trt, ctl = np.asarray(trt, float), np.asarray(ctl, float)
    if len(trt) < MIN_N or len(ctl) < MIN_N:
        return dict(estimate=np.nan, lo=np.nan, hi=np.nan, perm_p=np.nan,
                    n=f"{len(trt)} v {len(ctl)}", decision="INCONCLUSIVE",
                    note=f"fewer than {MIN_N} valid vessels in an arm")
    d, dlo, dhi, _ = welch(trt, ctl)
    est, lo, hi = 1 - np.exp(d), 1 - np.exp(dhi), 1 - np.exp(dlo)
    return dict(estimate=est, lo=lo, hi=hi, perm_p=perm_p(trt, ctl, "less"),
                n=f"{len(trt)} v {len(ctl)}", decision=decide(est, lo, hi, mark), note="")


def diff_compare(trt, ctl, mark):
    """Difference in means (e.g. days) with the same decision rule."""
    trt, ctl = np.asarray(trt, float), np.asarray(ctl, float)
    if len(trt) < MIN_N or len(ctl) < MIN_N:
        return dict(estimate=np.nan, lo=np.nan, hi=np.nan, perm_p=np.nan,
                    n=f"{len(trt)} v {len(ctl)}", decision="INCONCLUSIVE",
                    note=f"fewer than {MIN_N} valid vessels in an arm")
    d, lo, hi, _ = welch(trt, ctl)
    return dict(estimate=d, lo=lo, hi=hi, perm_p=perm_p(trt, ctl, "greater"),
                n=f"{len(trt)} v {len(ctl)}", decision=decide(d, lo, hi, mark), note="")


def safety_compare(trt, ctl):
    trt, ctl = np.asarray(trt, float), np.asarray(ctl, float)
    if len(trt) < MIN_N or len(ctl) < MIN_N:
        return dict(estimate=np.nan, lo=np.nan, hi=np.nan, perm_p=np.nan,
                    n=f"{len(trt)} v {len(ctl)}", decision="INCONCLUSIVE",
                    note="non-target data missing: safety cannot be claimed")
    d, lo, hi, _ = welch(trt, ctl)
    return dict(estimate=d, lo=lo, hi=hi, perm_p=np.nan, n=f"{len(trt)} v {len(ctl)}",
                decision=decide_safety(d, lo), note="")


# --- loading -------------------------------------------------------------------------------
def _time_cols(df):
    df = df.copy()
    for c in ("day", "timepoint_h"):
        if c not in df:
            df[c] = np.nan
    df["t_h"] = df.timepoint_h.astype(float).where(df.timepoint_h.notna(), df.day.astype(float) * 24)
    df["day"] = df.t_h / 24
    return df


def load(log_path=IN_LOG, counts_path=IN_COUNTS):
    return pd.read_csv(log_path), pd.read_csv(counts_path)


def prepare(log, counts):
    """Adds cells/mL, log cells, and the vessel's arm/species to the counts."""
    missing = [c for c in ("experiment", "arm", "tank_id") if c not in log]
    missing += [c for c in ("experiment", "tank_id", "count_method", "cells_counted",
                            "squares_counted") if c not in counts]
    if missing:
        raise ValueError(f"missing columns: {missing}")
    log = _time_cols(log)
    for c in LOG_COLUMNS:
        if c not in log:
            log[c] = np.nan
    log["fl_net"] = log.fl_counts - log.fl_blank_counts.fillna(0)
    counts = _time_cols(counts)
    for c, v in (("size_class", "all"), ("dilution_factor", 1.0), ("foreign_cells", 0),
                 ("grazers_seen", 0)):
        if c not in counts:
            counts[c] = v
        counts[c] = counts[c].fillna(v)
    counts["cells_per_mL"] = cells_per_ml(counts.cells_counted, counts.squares_counted,
                                          counts.count_method, counts.dilution_factor)
    counts["log_cells"] = log_floor(counts.cells_per_mL, counts.cells_counted,
                                    counts.squares_counted, counts.count_method,
                                    counts.dilution_factor)
    keys = ["experiment", "tank_id", "t_h", "size_class"]
    cells = (counts.groupby(keys, as_index=False)
             .agg(cells_per_mL=("cells_per_mL", "mean"), log_cells=("log_cells", "mean"),
                  cells_counted=("cells_counted", "sum"), foreign_cells=("foreign_cells", "sum"),
                  grazers_seen=("grazers_seen", "max")))
    cells["day"] = cells.t_h / 24
    vessels = (log.groupby(["experiment", "tank_id"], as_index=False)
               .agg(arm=("arm", "first"), species=("species", "first"),
                    volume_L=("volume_L", "first")))
    cells = cells.merge(vessels, on=["experiment", "tank_id"], how="left")
    unknown = cells[cells.arm.isna()].tank_id.unique()
    if len(unknown):
        raise ValueError(f"counts for tank_id(s) not in the tank log: {list(unknown)}")
    return log, cells, vessels


# --- exclusions (BENCH_PREREG.md 'Exclusions') ---------------------------------------------
def exclusions(log, cells):
    """Returns {(experiment, tank_id): reason}. Manual flags plus the automatic rules."""
    out = {}
    for _, r in log[log.excluded.fillna(0).astype(float) == 1].iterrows():
        out.setdefault((r.experiment, r.tank_id), f"manual: {r.exclusion_reason}")
    for (e, t), g in cells.groupby(["experiment", "tank_id"]):
        g = g.groupby("t_h").agg(f=("foreign_cells", "sum"), c=("cells_counted", "sum"),
                                 z=("grazers_seen", "max")).sort_index()
        bad = ((g.f / (g.f + g.c).replace(0, np.nan)).fillna(0) > CONTAM_FRAC) | (g.z >= 1)
        if (bad.astype(int).rolling(CONTAM_RUN).sum() >= CONTAM_RUN).any():
            out.setdefault((e, t), "auto: contamination in 2 consecutive counts")
        if e.endswith("_loop"):
            gg = cells[(cells.experiment == e) & (cells.tank_id == t)
                       & (cells.size_class == LOOP_SIZE.get(e, "all"))].sort_values("t_h")
            if len(gg) and gg.arm.iloc[0] != "P":
                start = gg.cells_per_mL.iloc[0]
                pre = gg[gg.day < NUTRIENTS_DAY].cells_per_mL
                if start > 0 and (pre < PRE_CRASH_FRAC * start).any():
                    out.setdefault((e, t), "auto: crashed before nutrients-in")
    sl = log[log.experiment == "peroxide_screen"]
    for (t, arm), g in sl.groupby(["tank_id", "arm"]):
        nominal = _nominal_dose(arm)
        g0 = g[(g.t_h.abs() <= 1.0) & g.h2o2_mgL.notna()]
        if nominal and len(g0):
            r = g0.h2o2_mgL.iloc[0] / nominal
            if not DOSE_OK[0] <= r <= DOSE_OK[1]:
                out.setdefault(("peroxide_screen", t), f"auto: dose error (0 h residual {r:.0%} of nominal)")
    al = log[(log.experiment == "aeration_screen") & log.arm.isin(list(S1_FLOW))]
    for (t, arm), g in al.groupby(["tank_id", "arm"]):
        g = g[g.airflow_mL_min.notna() & (g.t_h <= S1_OFF_H)].sort_values("t_h")
        off = (g.airflow_mL_min / S1_FLOW[arm] - 1).abs() > AIRFLOW_TOL
        if (off.astype(int).rolling(2).sum() >= 2).any():
            out.setdefault(("aeration_screen", t), "auto: airflow off target on 2 checks")
    return out


def _nominal_dose(arm):
    if arm.startswith(("h2o2_", "percarb_")):
        return float(arm.split("_")[1])
    if arm == "pulse3_0.8":
        return PULSE_MGL
    return None


# --- result rows ---------------------------------------------------------------------------
def row(exp, hid, role, endpoint, res, mark, units, note=""):
    r = dict(experiment=exp, hypothesis=hid, role=role, endpoint=endpoint, units=units,
             estimate=np.nan, lo=np.nan, hi=np.nan, mark=mark, n="", perm_p=np.nan,
             decision="REPORTED", note=note)
    r.update({k: v for k, v in res.items() if k in r})
    r["note"] = "; ".join(x for x in (res.get("note", ""), note) if x)
    if r["decision"] == "PASS" and r["role"] not in ("SAFETY", "gate") and not np.isnan(r["lo"])             and not np.isnan(r["mark"]):
        r["note"] = "; ".join(x for x in (r["note"], "whole interval clears the mark" if r["lo"] >= r["mark"]
                                          else "interval does not clear the mark (underpowered)") if x)
    return r


def reported(exp, hid, endpoint, value, units, note="", lo=np.nan, hi=np.nan, n=""):
    return dict(experiment=exp, hypothesis=hid, role="reported", endpoint=endpoint, units=units,
                estimate=value, lo=lo, hi=hi, mark=np.nan, n=n, perm_p=np.nan,
                decision="REPORTED", note=note)


# --- screens -------------------------------------------------------------------------------
def _at(g, t_h):
    """Value closest to nominal time t_h within TIME_TOL_H, else NaN."""
    d = (g.t_h - t_h).abs()
    if not len(d) or d.min() > TIME_TOL_H:
        return np.nan
    return g.loc[d.idxmin(), "log_cells"]


def screen_ratios(cells, exp, t_h):
    """Per vessel log(N_t / N_0). Returns DataFrame tank_id, arm, species, lr."""
    rows = []
    for (t, arm, sp), g in cells[(cells.experiment == exp) & (cells.size_class == "all")].groupby(
            ["tank_id", "arm", "species"]):
        g = g.dropna(subset=["log_cells"])
        rows.append(dict(tank_id=t, arm=arm, species=sp, lr=_at(g, t_h) - _at(g, 0.0)))
    return pd.DataFrame(rows, columns=["tank_id", "arm", "species", "lr"]).dropna()


def _arm(r, arm, sp):
    return r[(r.arm == arm) & (r.species == sp)].lr.to_numpy()


def _screen_cut(r, trt, ctl, sp, mark):
    res = cut_compare(_arm(r, trt, sp), _arm(r, ctl, sp), mark)
    c = _arm(r, ctl, sp)
    if len(c) and np.exp(c.mean()) < CONTROL_CRASH:
        res.update(decision="INCONCLUSIVE", note=f"control {ctl} crashed (N_t/N_0 {np.exp(c.mean()):.2f})")
    return res


def aeration_screen(log, cells):
    exp, out = "aeration_screen", []
    if not (cells.experiment == exp).any():
        return out
    r48 = screen_ratios(cells, exp, S1_T_H)
    s1a = _screen_cut(r48, "high", "still", "akashiwo", S1_MARK)
    out.append(row(exp, "S1a", "primary (part 1)", "Akashiwo cells 48 h, high vs still, % cut",
                   s1a, S1_MARK, "fraction"))
    s1b = _screen_cut(r48, "high", "still", "thal", SPARED_MAX)
    spared = (not np.isnan(s1b["estimate"])) and s1b["estimate"] < SPARED_MAX
    out.append(row(exp, "S1b", "primary (part 2)", "Thalassiosira cells 48 h, high vs still, % cut",
                   dict(s1b, decision="PASS" if spared else ("FAIL" if not np.isnan(s1b["estimate"])
                                                              else "INCONCLUSIVE")),
                   SPARED_MAX, "fraction", "spared = point cut < 20%"))
    if s1a["decision"] == "PASS" and spared:
        joint = "PASS"
    elif s1a["decision"] == "FAIL" or (not spared and not np.isnan(s1b["estimate"])):
        joint = "FAIL"
    else:
        joint = "INCONCLUSIVE"
    out.append(row(exp, "S1", "PRIMARY", "S1a PASS and Thalassiosira spared",
                   dict(decision=joint), np.nan, ""))
    for sp in ("nanno", "thal", "akashiwo"):
        for trt, ctl in (("high", "gentle"), ("low", "still"), ("high", "still")):
            if (trt, ctl, sp) in (("high", "still", "akashiwo"), ("high", "still", "thal")):
                continue
            out.append(row(exp, "S1-sec", "secondary", f"{sp} cells 48 h, {trt} vs {ctl}, % cut",
                           dict(_screen_cut(r48, trt, ctl, sp, S1_MARK), decision="REPORTED"),
                           S1_MARK, "fraction"))
    rf = screen_ratios(cells.assign(log_cells=np.log(_fl_cells(log, cells))), exp, S1_T_H)
    out.append(row(exp, "S1a-fl", "secondary", "Akashiwo fluorometer 48 h, high vs still, % cut",
                   dict(_screen_cut(rf, "high", "still", "akashiwo", S1_MARK), decision="REPORTED"),
                   S1_MARK, "fraction", "fluorometer, uncalibrated"))
    out += _regrowth(cells, exp)
    sl = log[log.experiment == exp]
    for sp in ("nanno", "thal", "akashiwo"):
        ph = sl[(sl.species == sp) & ((sl.t_h - S1_T_H).abs() <= TIME_TOL_H)]
        a, b = ph[ph.arm == "high"].ph.dropna(), ph[ph.arm == "still"].ph.dropna()
        if len(a) >= MIN_N and len(b) >= MIN_N:
            d, lo, hi, _ = welch(a, b)
            out.append(reported(exp, "S1-pH", f"{sp} pH 48 h, high minus still", d, "pH", "CO2 check",
                                lo, hi, f"{len(a)} v {len(b)}"))
        dw = sl[(sl.species == sp) & (sl.do_dawn.fillna(0) == 1) & (sl.t_h >= S1_T_H - TIME_TOL_H)]
        a, b = dw[dw.arm == "high"].do_mgL.dropna(), dw[dw.arm == "still"].do_mgL.dropna()
        if len(a) >= MIN_N and len(b) >= MIN_N:
            d, lo, hi, _ = welch(a, b)
            out.append(reported(exp, "S1-DO", f"{sp} dawn DO after 48 h, high minus still", d, "mg/L",
                                "", lo, hi, f"{len(a)} v {len(b)}"))
    gate = _artemia_gate(sl, "high", "still", ("24h",), species=None)
    out += [row(exp, "S1-artemia", "gate", f"Artemia survival {h}, high vs still water (points)",
                res, ARTEMIA_MARGIN, "points") for h, res in gate]
    culture = "akashiwo"
    if s1a["decision"] == "FAIL":
        cuts = {sp: 1 - np.exp(_arm(r48, "high", sp).mean() - _arm(r48, "still", sp).mean())
                for sp in ("nanno", "thal", "akashiwo")
                if len(_arm(r48, "high", sp)) and len(_arm(r48, "still", sp))}
        best = max(cuts, key=cuts.get) if cuts else "akashiwo"
        culture = best if cuts.get(best, 0) > 0 else "akashiwo"
    out.append(reported(exp, "S1-choice", f"aeration loop culture: {culture}", np.nan, "",
                        "rule: Akashiwo unless S1a FAILS; then the largest point cut > 0"))
    return out


def _fl_cells(log, cells):
    """Fluorometer net counts aligned to the count rows (for fluorometer secondaries)."""
    fl = log[["experiment", "tank_id", "t_h", "fl_net"]].dropna().drop_duplicates(
        ["experiment", "tank_id", "t_h"])
    m = cells.merge(fl, on=["experiment", "tank_id", "t_h"], how="left")
    return m.fl_net.where(m.fl_net > 0).to_numpy()


def _regrowth(cells, exp):
    out = []
    c = cells[(cells.experiment == exp) & (cells.size_class == "all")]
    for sp in ("nanno", "thal", "akashiwo"):
        s = c[(c.species == sp) & (c.arm == "still") & ((c.t_h - S1_OFF_H).abs() <= TIME_TOL_H)]
        if not len(s):
            continue
        target = s.log_cells.mean()
        for arm in ("gentle", "low", "high"):
            g = c[(c.species == sp) & (c.arm == arm) & (c.t_h >= S1_OFF_H - TIME_TOL_H)]
            if not len(g):
                continue
            gm = g.assign(tn=(g.t_h / 24).round() * 24).groupby("tn").log_cells.mean().sort_index()
            val, note = np.nan, ""
            if gm.iloc[0] >= target:
                val = 0.0
            else:
                above = np.where(gm.to_numpy() >= target)[0]
                if len(above):
                    i = above[0]
                    t0, t1, y0, y1 = gm.index[i - 1], gm.index[i], gm.iloc[i - 1], gm.iloc[i]
                    val = (t0 + (target - y0) / (y1 - y0) * (t1 - t0) - S1_OFF_H) / 24
                else:
                    note = f"not reached by {S1_END_H:.0f} h (> {(S1_END_H - S1_OFF_H) / 24:.0f} d)"
            out.append(reported(exp, "S1-regrow", f"{sp} {arm}: days after OFF to still's 48 h density",
                                val, "days", note))
    return out


def _artemia_gate(sl, trt, ctl, hours, species="nanno"):
    out = []
    for h in hours:
        col = f"artemia_alive_{h}"
        s = sl[sl.artemia_start.fillna(0) > 0]
        if species:
            s = s[s.species == species]
        v = (s.groupby(["tank_id", "arm"])[[col, "artemia_start"]].sum().reset_index())
        v["surv"] = 100 * v[col] / v.artemia_start
        res = safety_compare(v[v.arm == trt].surv.dropna(), v[v.arm == ctl].surv.dropna())
        if not np.isnan(res["estimate"]):
            res["decision"] = "PASS" if res["estimate"] >= ARTEMIA_MARGIN else "FAIL"
            res["note"] = "gate uses the point estimate (PROCEDURES P5)"
        out.append((h, res))
    return out


def peroxide_screen(log, cells):
    exp, out = "peroxide_screen", []
    if not (cells.experiment == exp).any():
        return out
    sl = log[log.experiment == exp]
    r24, r72 = screen_ratios(cells, exp, S3_REP_T_H), screen_ratios(cells, exp, S3_T_H)
    cut = _screen_cut(r72, "pulse3_0.8", "ctrl", "nanno", S3_MARK)
    out.append(row(exp, "S3-cut", "primary (part 1)", "Nannochloropsis cells 72 h, 3 x 0.8 mg/L vs ctrl, % cut",
                   cut, S3_MARK, "fraction"))
    gate = _artemia_gate(sl, "pulse3_0.8", "ctrl", ("24h", "96h"))
    for h, res in gate:
        out.append(row(exp, "S3-artemia", "primary (part 2, gate)",
                       f"Artemia survival {h}, 3-pulse vs ctrl water (points)", res, ARTEMIA_MARGIN, "points"))
    gd = [res["decision"] for _, res in gate]
    if cut["decision"] == "FAIL" or "FAIL" in gd:
        joint = "FAIL"
    elif cut["decision"] == "PASS" and all(d == "PASS" for d in gd):
        joint = "PASS"
    else:
        joint = "INCONCLUSIVE"
    out.append(row(exp, "S3", "PRIMARY", "3-pulse cut PASS and Artemia gate passed at 24 h and 96 h",
                   dict(decision=joint), np.nan, ""))
    rep = _screen_cut(r24, "h2o2_1.6", "ctrl", "nanno", S3_MARK)
    out.append(row(exp, "S3-rep", "secondary", "Nannochloropsis 24 h, single 1.6 mg/L vs ctrl, % cut",
                   rep, S3_MARK, "fraction", "source replication (peroxide-03)"))
    for sp in ("thal", "akashiwo"):
        res = _screen_cut(r24, "h2o2_1.6", "ctrl", sp, SPARED_MAX)
        ok = res["estimate"] < SPARED_MAX if not np.isnan(res["estimate"]) else None
        out.append(row(exp, "S3-rep-spared", "secondary", f"{sp} 24 h, 1.6 mg/L vs ctrl, % cut",
                       dict(res, decision={True: "PASS", False: "FAIL", None: "INCONCLUSIVE"}[ok]),
                       SPARED_MAX, "fraction", "spared = point cut < 20%"))
    c24 = _screen_cut(r24, "h2o2_0.8", "ctrl", "nanno", S3_MARK)
    c72 = _screen_cut(r72, "h2o2_0.8", "ctrl", "nanno", S3_MARK)
    out.append(row(exp, "S3-0.8", "secondary", "Nannochloropsis single 0.8 mg/L, % cut at 24 h",
                   dict(c24, decision="REPORTED"), S3_MARK, "fraction"))
    out.append(row(exp, "S3-0.8", "secondary", "Nannochloropsis single 0.8 mg/L, % cut at 72 h",
                   dict(c72, decision="REPORTED"), S3_MARK, "fraction",
                   "transient" if c72["estimate"] < c24["estimate"] else "not transient"))
    d = _screen_cut(r72, "pulse3_0.8", "h2o2_1.6", "nanno", 0.0)
    out.append(row(exp, "S3-pulses-vs-1.6", "secondary", "Nannochloropsis 72 h, 3 x 0.8 vs single 1.6, % lower",
                   dict(d, decision="REPORTED"), 0.0, "fraction"))
    for sp in ("nanno", "thal", "akashiwo"):
        d = _screen_cut(r72, "percarb_0.8", "h2o2_0.8", sp, 0.0)
        out.append(row(exp, "S3-percarb", "secondary", f"{sp} 72 h, percarbonate vs liquid at 0.8 mg/L, % lower",
                       dict(d, decision="REPORTED"), 0.0, "fraction"))
    cb = _screen_cut(r72, "carbonate", "ctrl", "nanno", CARB_FLAG)
    out.append(row(exp, "S3-carbonate", "secondary", "Nannochloropsis 72 h, sodium carbonate vs ctrl, % cut",
                   dict(cb, decision="REPORTED"), CARB_FLAG, "fraction",
                   "carbonate alone >= 20%: percarbonate effect partly pH" if cb["estimate"] >= CARB_FLAG else ""))
    out += _h5(r24)
    rf = screen_ratios(cells.assign(log_cells=np.log(_fl_cells(log, cells))), exp, S3_T_H)
    out.append(row(exp, "S3-cut-fl", "secondary", "Nannochloropsis fluorometer 72 h, 3 x 0.8 vs ctrl, % cut",
                   dict(_screen_cut(rf, "pulse3_0.8", "ctrl", "nanno", S3_MARK), decision="REPORTED"),
                   S3_MARK, "fraction", "fluorometer; peroxide can dim glow without killing cells"))
    if joint == "PASS":
        dose = "3 x 0.8 mg/L pulses (as planned)"
    else:
        g16 = [res["decision"] for _, res in _artemia_gate(sl, "h2o2_1.6", "ctrl", ("24h", "96h"))]
        c16 = _screen_cut(r72, "h2o2_1.6", "ctrl", "nanno", S3_MARK)
        dose = ("single 1.6 mg/L (lowest dose that cuts small cells, Artemia passed, <= 2.8)"
                if c16["estimate"] >= S3_MARK and all(x == "PASS" for x in g16)
                else "no dose qualifies: peroxide loop H1a expected to fail; loop runs at 0.8 mg/L and is reported")
    out.append(reported(exp, "S3-choice", f"peroxide loop dose: {dose}", np.nan, ""))
    return out


def _h5(r24):
    exp, out, held = "peroxide_screen", [], 0
    spared_ok, any_nan = True, False
    for dose in H5_DOSES:
        arm = f"h2o2_{dose}"
        cuts = {}
        for sp in ("nanno", "thal", "akashiwo"):
            t, c = _arm(r24, arm, sp), _arm(r24, "ctrl", sp)
            cuts[sp] = 1 - np.exp(t.mean() - c.mean()) if len(t) and len(c) else np.nan
            out.append(reported(exp, "H5-dose", f"{sp} 24 h, {dose} mg/L vs ctrl, % cut", cuts[sp], "fraction"))
        any_nan |= any(np.isnan(v) for v in cuts.values())
        order = cuts["nanno"] > cuts["thal"] > cuts["akashiwo"]
        held += int(bool(order))
        if dose == PULSE_MGL:
            spared_ok = cuts["thal"] < SPARED_MAX and cuts["akashiwo"] < SPARED_MAX
    if any_nan:
        dec = "INCONCLUSIVE"
    elif held >= H5_PASS_N and spared_ok:
        dec = "PASS"
    elif held <= H5_FAIL_N:
        dec = "FAIL"
    else:
        dec = "INCONCLUSIVE"
    out.append(dict(experiment=exp, hypothesis="H5", role="secondary",
                    endpoint="ranking nanno > thal > akashiwo holds at >= 3 of 4 doses, larger cells spared at 0.8",
                    units="doses", estimate=held, lo=np.nan, hi=np.nan, mark=H5_PASS_N, n="",
                    perm_p=np.nan, decision=dec, note="size and taxon cannot be separated"))
    return out


def half_lives(log):
    exp, out, fits = "halflife", [], []
    s = log[log.experiment.isin(["halflife", "peroxide_screen"]) & log.h2o2_mgL.notna()
            & (log.t_h >= 0) & (log.t_h <= HALF_LIFE_FIT_H)]
    s = s[s.arm.str.startswith(("seawater_", "h2o2_", "percarb_", "pulse3_"))]
    for (e, t, arm, sp), g in s.groupby(["experiment", "tank_id", "arm", "species"]):
        g = g[g.h2o2_mgL > H2O2_LOD]
        if len(g) < 3:
            continue
        k = -np.polyfit(g.t_h, np.log(g.h2o2_mgL), 1)[0]
        fits.append(dict(experiment=e, arm=arm, species=sp, t_half=np.log(2) / k if k > 0 else np.inf))
    if not fits:
        return out
    f = pd.DataFrame(fits)
    for (e, arm, sp), g in f.groupby(["experiment", "arm", "species"]):
        v = np.log(g.t_half[np.isfinite(g.t_half)])
        if len(v) >= MIN_N:
            m, se = v.mean(), v.std(ddof=1) / np.sqrt(len(v))
            tq = stats.t.ppf(0.5 + CONF / 2, len(v) - 1)
            est, lo, hi = np.exp(m), np.exp(m - tq * se), np.exp(m + tq * se)
        else:
            est, lo, hi = (np.exp(v.mean()) if len(v) else np.inf), np.nan, np.nan
        note = (f"expected {SIM_HALF_LIFE_H[0]}-{SIM_HALF_LIFE_H[1]} h; > {HALF_LIFE_DAILY_MAX_H:.1f} h "
                "means a 0.8 pulse is still > 0.5 mg/L at 24 h" if est > HALF_LIFE_DAILY_MAX_H
                else f"expected {SIM_HALF_LIFE_H[0]}-{SIM_HALF_LIFE_H[1]} h")
        out.append(reported(exp, "half-life", f"H2O2 half-life, {e} {arm} {sp}", est, "h", note, lo, hi,
                            f"{len(g)} vessels"))
    return out


# --- loop runs -----------------------------------------------------------------------------
def _interp(days, logv, grid):
    days, logv = np.asarray(days, float), np.asarray(logv, float)
    o = np.argsort(days)
    days, logv = days[o], logv[o]
    y = np.interp(grid, days, logv)
    y[(grid < days.min()) | (grid > days.max())] = np.nan
    return y


def ph_ceiling(pilot_ph):
    """Pre-registered pH ceiling from the untreated pilot tanks' readings (8.6 if there are none)."""
    pilot_ph = pd.Series(pilot_ph, dtype=float).dropna()
    if not len(pilot_ph):
        return PH_CEIL_MIN
    return float(min(PH_CEIL_MAX, max(PH_CEIL_MIN, round(pilot_ph.max() + PH_MARGIN, 2))))


def loop_tank_metrics(c, cok_log):
    """Per-tank endpoints from one tank's (day, log value) series."""
    warm = c[(c.day >= WARM_FROM) & (c.day <= NUTRIENTS_DAY)].v
    base = np.log(np.mean(np.exp(warm))) if len(warm) else np.nan
    bloom = c[(c.day >= NUTRIENTS_DAY) & (c.day <= COOL_END)]
    peak = bloom.v.max() if len(bloom) else np.nan
    grid = np.arange(NUTRIENTS_DAY, BLOOM_END + 1, dtype=float)
    y = _interp(c.day, c.v, grid) if len(c) >= 2 else np.full(len(grid), np.nan)
    below = np.nan if np.isnan(y).sum() > MAX_MISSING_DAYS else float(np.nansum(y < cok_log))
    pday = bloom.loc[bloom.v.idxmax(), "day"] if len(bloom) else np.nan
    return dict(lr_peak=peak - base, base=base, days_below=below, peak_day=pday)


def loop_run(log, cells, exp, value="cells"):
    out = []
    size = LOOP_SIZE[exp]
    c = cells[(cells.experiment == exp) & (cells.size_class == size)].copy()
    if not len(c):
        return out
    sl = log[log.experiment == exp]
    if value == "fl":
        fl = sl[["tank_id", "day", "fl_net", "arm"]].dropna()
        c = fl[fl.fl_net > 0].assign(v=lambda d: np.log(d.fl_net))
    else:
        c = c.assign(v=c.log_cells)
    pil = c[c.arm == "P"]
    if not len(pil):
        out.append(reported(exp, "C_ok", "no pilot tanks: C_ok cannot be set", np.nan, ""))
        return out
    pil_peak = pil.groupby("tank_id").v.max()
    cok = np.log(COK_FRAC * np.mean(np.exp(pil_peak)))
    m = pd.DataFrame({t: dict(loop_tank_metrics(g, cok), arm=g.arm.iloc[0])
                      for t, g in c[c.arm != "P"].groupby("tank_id")}).T
    for col in ("lr_peak", "base", "days_below", "peak_day"):
        m[col] = m[col].astype(float)
    tag = "" if value == "cells" else "-fl"
    units = "cells/mL" if value == "cells" else "fl counts"
    if value == "cells":
        out.append(reported(exp, "C_ok", f"C_ok = 50% of mean pilot peak ({units})", float(np.exp(cok)), units,
                            n=f"{len(pil_peak)} pilots"))
    A = m[m.arm == "A"]
    a_bloom = np.exp(A.lr_peak.mean()) if len(A) else np.nan
    no_bloom = not (a_bloom >= NO_BLOOM)
    nb = f"arm A did not bloom (peak/warm-up {a_bloom:.2f} < {NO_BLOOM})" if no_bloom else ""

    def arm(a, col):
        return m[m.arm == a][col].dropna().to_numpy()

    h1a = cut_compare(arm("B", "lr_peak"), arm("A", "lr_peak"), H1A_MARK)
    delay = diff_compare(arm("B", "days_below"), arm("A", "days_below"), DELAY_MARK_D)
    h1b = cut_compare(arm("B", "lr_peak"), arm("C", "lr_peak"), H1B_MARK)
    delay_bc = diff_compare(arm("B", "days_below"), arm("C", "days_below"), DELAY_MARK_D)
    for res in (h1a, delay, h1b, delay_bc):
        if no_bloom:
            res.update(decision="INCONCLUSIVE", note=nb)
    peak_ep = f"peak / warm-up, B vs A, % cut ({units})"
    delay_ep = f"days below C_ok, days 21-40, B minus A ({units})"
    if value == "fl":
        out.append(row(exp, "H1a" + tag, "secondary", peak_ep, dict(h1a, decision="REPORTED"), H1A_MARK, "fraction"))
        out.append(row(exp, "H1-delay" + tag, "secondary", delay_ep, dict(delay, decision="REPORTED"),
                       DELAY_MARK_D, "days"))
        return out
    gate_note = "tested only because the primary PASSED"
    if exp == "aeration_loop":
        out.append(row(exp, "H1-delay", "PRIMARY", delay_ep, delay, DELAY_MARK_D, "days"))
        if delay["decision"] != "PASS":
            delay_bc = dict(delay_bc, decision="NOT TESTED", note="primary did not PASS (fixed sequence)")
        out.append(row(exp, "H1-delay B v C", "key secondary", "days below C_ok, B minus C",
                       delay_bc, DELAY_MARK_D, "days", gate_note if delay["decision"] == "PASS" else ""))
        out.append(row(exp, "H1a", "secondary", peak_ep, dict(h1a, decision="REPORTED"), H1A_MARK, "fraction"))
        out.append(row(exp, "H1b", "secondary", "peak / warm-up, B vs C, % lower", dict(h1b, decision="REPORTED"),
                       H1B_MARK, "fraction"))
    else:
        out.append(row(exp, "H1a", "PRIMARY", peak_ep, h1a, H1A_MARK, "fraction"))
        if h1a["decision"] != "PASS":
            h1b = dict(h1b, decision="NOT TESTED", note="primary did not PASS (fixed sequence)")
        out.append(row(exp, "H1b", "key secondary", "peak / warm-up, B vs C, % lower", h1b, H1B_MARK,
                       "fraction", gate_note if h1a["decision"] == "PASS" else ""))
        out.append(row(exp, "H1-delay", "secondary", delay_ep, dict(delay, decision="REPORTED"),
                       DELAY_MARK_D, "days"))
        out += _h5_tank(cells, exp, m)
    for a in "ABCD":
        v = arm(a, "peak_day")
        if len(v):
            out.append(reported(exp, "peak day", f"arm {a} mean day of peak", v.mean(), "day", n=f"{len(v)}"))
    out += _h2(sl, exp)
    out += _h3(sl, c, m, cok, exp)
    out += _h4(sl, c, m, exp)
    out += _use_and_safety(sl, exp)
    out += loop_run(log, cells, exp, value="fl")
    return out


def _h5_tank(cells, exp, m):
    lg = cells[(cells.experiment == exp) & (cells.size_class == "large")]
    if not len(lg):
        return []
    mm = pd.DataFrame({t: dict(loop_tank_metrics(g.assign(v=g.log_cells), np.inf), arm=g.arm.iloc[0])
                       for t, g in lg[lg.arm.isin(["A", "B"])].groupby("tank_id")}).T
    res = cut_compare(mm[mm.arm == "B"].lr_peak.astype(float), mm[mm.arm == "A"].lr_peak.astype(float), 0.0)
    return [row(exp, "H5-tank", "secondary", "large cells (Thalassiosira), peak / warm-up, B vs A, % cut",
                dict(res, decision="REPORTED"), np.nan, "fraction",
                "compare with the small-cell H1a cut: H5 expects small >> large")]


def _h2(sl, exp):
    out = []
    s = sl[(sl.artemia_start.fillna(0) > 0) & (sl.day >= NUTRIENTS_DAY) & (sl.day <= COOL_END)]
    for h in LOOP_ARTEMIA[exp]:
        col = f"artemia_alive_{h}"
        s2 = s.assign(surv=100 * s[col] / s.artemia_start).dropna(subset=["surv"])
        worst = s2.groupby(["tank_id", "arm"]).surv.min().reset_index()
        res = safety_compare(worst[worst.arm == "D"].surv, worst[worst.arm == "A"].surv)
        out.append(row(exp, "H2", "SAFETY", f"Artemia survival {h} (worst assay per tank), D minus A, points",
                       res, ARTEMIA_MARGIN, "points"))
        res_b = safety_compare(worst[worst.arm == "B"].surv, worst[worst.arm == "A"].surv)
        out.append(row(exp, "H2-B", "secondary", f"Artemia survival {h}, B minus A, points",
                       dict(res_b, decision="REPORTED"), ARTEMIA_MARGIN, "points"))
    return out


def _h3(sl, c, m, cok, exp):
    out = []
    for t, g in sl[(sl.arm == "B") & sl.event.isin(OFF_EVENTS)].groupby("tank_id"):
        off = g.day.max()
        s = c[c.tank_id == t]
        grid = np.arange(np.ceil(off), COOL_END + 1, dtype=float)
        y = _interp(s.day, s.v, grid) if len(s) >= 2 else np.full(len(grid), np.nan)
        hit = np.where(y > cok)[0]
        val = grid[hit[0]] - off if len(hit) else np.nan
        note = "" if len(hit) else f"not back above C_ok by day {COOL_END} (> {COOL_END - off:.0f} d)"
        out.append(reported(exp, "H3", f"tank {t}: days from last OFF (day {off:.0f}) back above C_ok",
                            val, "days", note))
    return out


def _h4(sl, c, m, exp):
    b = m[m.arm == "B"]
    if not len(b):
        return []
    s = c[c.tank_id.isin(b.index) & (c.day >= NUTRIENTS_DAY) & (c.day <= COOL_END)]
    rel = s.assign(r=np.exp(s.v - s.tank_id.map(b.base))).groupby(s.day.round()).r.mean()
    low = rel.min()
    w = sl[(sl.arm == "B") & (sl.do_dawn.fillna(0) != 1) & sl.do_mgL.notna()]
    wd = w[(w.day >= WARM_FROM) & (w.day < NUTRIENTS_DAY)].do_mgL.mean()
    bd = w[(w.day >= NUTRIENTS_DAY) & (w.day <= COOL_END)].groupby(w.day.round()).do_mgL.mean()
    do_ok = None if (np.isnan(wd) or not len(bd)) else bool(bd.min() >= wd - DO_ALLOW)
    if do_ok is None:
        dec = "PASS" if low >= FLOOR else "FAIL"
        note = "daytime DO not logged: only the cell part is decided"
    else:
        dec = "PASS" if (low >= FLOOR and do_ok) else "FAIL"
        note = f"lowest daytime DO {bd.min():.2f} vs warm-up {wd:.2f} mg/L ({'ok' if do_ok else 'below'})"
    return [dict(experiment=exp, hypothesis="H4", role="secondary",
                 endpoint="arm B lowest 3-tank mean count / warm-up mean, days 21-45", units="ratio",
                 estimate=low, lo=np.nan, hi=np.nan, mark=FLOOR, n=f"{len(b)}", perm_p=np.nan,
                 decision=dec, note=note)]


def _use_and_safety(sl, exp):
    out = []
    for a in "BCD":
        g = sl[sl.arm == a]
        if not len(g):
            continue
        per = g.groupby("tank_id").agg(on_h=("treatment_on_h", "sum"),
                                       eps=("event", lambda e: (e == "ON").sum()),
                                       stops=("event", lambda e: (e == "SAFETY_STOP").sum()),
                                       human=("event", lambda e: (e == "HUMAN").sum()))
        dose = (g[g.event == "PULSE"].assign(mg=lambda d: d.dose_mgL * d.volume_L)
                .groupby("tank_id").mg.sum().reindex(per.index).fillna(0))
        out.append(reported(exp, "use", f"arm {a}: hours ON per tank (mean)", per.on_h.mean(), "h"))
        out.append(reported(exp, "use", f"arm {a}: ON episodes per tank (mean)", per.eps.mean(), "episodes"))
        if exp == "peroxide_loop":
            out.append(reported(exp, "use", f"arm {a}: H2O2 dosed per tank (mean)", dose.mean(), "mg"))
        out.append(reported(exp, "safety", f"arm {a}: safety stops (total)", per.stops.sum(), "stops"))
        weeks = max((g.day.max() - g.day.min()) / 7, 1e-9)
        out.append(reported(exp, "autonomy", f"arm {a}: human interventions per tank per week",
                            per.human.mean() / weeks, "per week"))
        trig = g[g.event == "ON"].trigger.fillna("?").value_counts().to_dict()
        if trig:
            out.append(reported(exp, "trigger", f"arm {a}: ON switches by trigger {trig}", np.nan, ""))
    ceil = ph_ceiling(sl.loc[sl.arm == "P", "ph"])
    out.append(reported(exp, "safety", "pH ceiling = pilot max + 0.2, kept within 8.6-9.0", ceil, "pH",
                        n=f"{sl.loc[sl.arm == 'P', 'tank_id'].nunique()} pilots"))
    tr = sl[sl.arm != "P"]
    v = tr[(tr.do_mgL < SAFE_DO) | (tr.ph < SAFE_PH[0]) | (tr.ph > ceil) | (tr.h2o2_mgL > SAFE_H2O2)]
    out.append(reported(exp, "safety", f"readings past a safety limit (DO < 4, pH outside 7.6-{ceil:.2f}, H2O2 > 2.8)",
                        len(v), "readings", "; ".join(f"{r.tank_id} day {r.day:.0f}" for _, r in v.head(10).iterrows())))
    return out


# --- driver --------------------------------------------------------------------------------
def analyse(log, counts, apply_exclusions=True):
    log, cells, _ = prepare(log, counts)
    excl = exclusions(log, cells)
    out = [reported(e, "exclusion", f"{t} excluded", np.nan, "", reason) for (e, t), reason in excl.items()]
    if apply_exclusions and excl:
        keep = ~pd.Series(list(zip(cells.experiment, cells.tank_id))).isin(excl.keys()).to_numpy()
        cells = cells[keep]
        keep = ~pd.Series(list(zip(log.experiment, log.tank_id))).isin(excl.keys()).to_numpy()
        log = log[keep]
    low = cells[cells.cells_counted < LOW_COUNT_FLAG]
    if len(low):
        out.append(reported("all", "count quality", f"samples with fewer than {LOW_COUNT_FLAG} cells counted",
                            len(low), "samples"))
    out += aeration_screen(log, cells)
    out += peroxide_screen(log, cells)
    out += half_lives(log)
    for exp in ("aeration_loop", "peroxide_loop"):
        out += loop_run(log, cells, exp)
    res = pd.DataFrame(out)
    res.insert(0, "analysis_set", "per-protocol" if apply_exclusions else "all-vessels")
    return res


def run(log, counts):
    a, b = analyse(log, counts, True), analyse(log, counts, False)
    return pd.concat([a, b], ignore_index=True)


def _fmt(r):
    def f(v):
        if pd.isna(v):
            return ""
        return f"{100 * v:.0f}%" if r.units == "fraction" else f"{v:.3g}"
    ci = f" [{f(r.lo)}, {f(r.hi)}]" if not pd.isna(r.lo) else ""
    return f"{f(r.estimate)}{ci}"


def print_table(res):
    shown = res[(res.analysis_set == "per-protocol") & (res.role != "reported")].copy()
    shown["result"] = shown.apply(_fmt, axis=1)
    shown["mark_"] = shown.apply(lambda r: "" if pd.isna(r.mark) else
                                 (f"{100 * r.mark:.0f}%" if r.units == "fraction" else f"{r.mark:g}"), axis=1)
    cols = ["experiment", "hypothesis", "role", "endpoint", "result", "mark_", "n", "decision", "note"]
    with pd.option_context("display.max_colwidth", 70, "display.width", 250):
        print(shown[cols].rename(columns={"mark_": "mark"}).to_string(index=False))
    pp = res[res.role.isin(["PRIMARY", "SAFETY"])]
    piv = pp.pivot_table(index=["experiment", "hypothesis", "endpoint"], columns="analysis_set",
                         values="decision", aggfunc="first")
    if {"per-protocol", "all-vessels"} <= set(piv.columns):
        dis = piv[piv["per-protocol"] != piv["all-vessels"]]
        print("\nPrimary/safety decisions that change when exclusions are ignored:",
              "none" if dis.empty else "\n" + dis.to_string())


def layout(experiment, seed):
    """Random tank ids and shelf positions for one experiment (BENCH_PREREG.md 'Randomisation').
    The person who keeps this key does not count cells."""
    rng = np.random.default_rng(seed)
    vessels = [(a, s, i + 1) for a, s, n in DESIGNS[experiment] for i in range(n)]
    order = rng.permutation(len(vessels))
    pos = rng.permutation(len(vessels)) + 1
    rows = [dict(tank_id=f"{ID_PREFIX[experiment]}{k + 1:02d}", experiment=experiment, arm=a, species=s,
                 replicate=r, position=int(pos[k]), seed=seed)
            for k, (a, s, r) in enumerate(vessels[i] for i in order)]
    return pd.DataFrame(rows).sort_values("tank_id").reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    sub = ap.add_subparsers(dest="cmd")
    lay = sub.add_parser("layout", help="random tank ids and positions")
    lay.add_argument("--experiment", required=True, choices=sorted(DESIGNS))
    lay.add_argument("--seed", type=int, required=True, help="setup date as YYYYMMDD")
    ap.add_argument("--log", default=IN_LOG)
    ap.add_argument("--counts", default=IN_COUNTS)
    ap.add_argument("--out", default=OUT_CSV)
    a = ap.parse_args(argv)
    if a.cmd == "layout":
        print(layout(a.experiment, a.seed).to_csv(index=False), end="")
        return
    if not (os.path.exists(a.log) and os.path.exists(a.counts)):
        sys.exit(f"no data yet: {a.log} / {a.counts} (templates in {TEMPLATE_DIR}/)")
    res = run(*load(a.log, a.counts))
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    res.to_csv(a.out, index=False)
    print_table(res)
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
