"""
basin_alert.py
--------------
Task 2: reframe the headline product as a WESTERN BASIN alert rather than
station-day alerts.

Rationale (pre-registered before evaluation):
  - CT DEEP samples by cruise; western stations are visited together, so the
    effective observation unit is the cruise, not the station-day.
  - The cadence-thinning experiment showed alert error is dominated by
    unverifiable station-day windows. A basin window is empty only if NO
    western station is sampled within the horizon, so aggregation buys
    verification coverage directly.
  - Aggregator is fixed a priori as MAX over same-day western-station
    probabilities, because the basin label is an OR over stations (any
    exceedance at any western station within h days) and max is the
    probability aggregator matching OR semantics. Not tuned.
  - Threshold re-derived with the SAME pre-registered rule as t*: highest
    threshold on a coarse grid with out-of-sample 2020-2022 POD >= 0.8,
    evaluated exactly once on 2023-2025.

Usage (from repo root):
    python src/models/basin_alert.py
    python src/models/basin_alert.py --west-lon -73.4
Outputs:
    data/basin_alert_val_sweep.csv
    data/basin_alert_daily.csv
    printed test-era POD/FAR/CSI + comparison vs station-day baseline
"""

import argparse
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")))
from src.models.locked_pipeline import (          # noqa: E402
    BLOOM_THRESHOLD, HORIZON_DAYS, add_forward_label, fit_locked_model,
    load_locked_dataframe, predict_proba)

TRAIN_END = pd.Timestamp("2019-12-31")
VAL_START, VAL_END = pd.Timestamp("2020-01-01"), pd.Timestamp("2022-12-31")
TEST_START, TEST_END = pd.Timestamp("2023-01-01"), pd.Timestamp("2025-12-31")
POD_FLOOR = 0.8                      # pre-registered rule, same as t*
GRID = np.round(np.arange(0.05, 0.96, 0.05), 2)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--west-lon", type=float, default=-73.4,
                   help="stations with longitude_x < this are 'western'")
    return p.parse_args()


def basin_series(df_west, horizon=HORIZON_DAYS, thr=BLOOM_THRESHOLD):
    """One row per date on which >= 1 western station was sampled.
    basin_prob = max station prob that date.
    basin_label = 1 if ANY western station records Chlorophyll > thr in
    (date, date+h]; 0 if verified clear; NaN if right-censored.
    has_future = any western visit inside the window (verifiability)."""
    days = (df_west.groupby("date")
                   .agg(basin_prob=("bloom_prob", "max"),
                        n_stations=("station_name", "nunique"))
                   .reset_index()
                   .sort_values("date"))

    vis_dates = df_west["date"].sort_values().unique()
    exc = (df_west[df_west["Chlorophyll"] > thr]["date"]
           .sort_values().unique())
    last = df_west["date"].max()

    lab, fut = [], []
    for d in days["date"]:
        end = d + pd.Timedelta(days=horizon)
        future_vis = vis_dates[(vis_dates > d) & (vis_dates <= end)]
        future_exc = exc[(exc > d) & (exc <= end)]
        fut.append(len(future_vis) > 0)
        if len(future_exc):
            lab.append(1.0)
        elif end <= last:
            lab.append(0.0)
        else:
            lab.append(np.nan)
    days["basin_label"] = lab
    days["has_future"] = fut
    return days


def contingency(y, a):
    tp = int(((y == 1) & a).sum()); fp = int(((y == 0) & a).sum())
    fn = int(((y == 1) & ~a).sum())
    pod = tp / (tp + fn) if tp + fn else np.nan
    far = fp / (tp + fp) if tp + fp else np.nan
    csi = tp / (tp + fp + fn) if tp + fp + fn else np.nan
    return dict(tp=tp, fp=fp, fn=fn, pod=pod, far=far, csi=csi,
                precision=(1 - far) if not np.isnan(far) else np.nan)


def bootstrap_ci(y, a, n_boot=10000, seed=42):
    """Percentile bootstrap CIs for POD/FAR/CSI over basin decision days."""
    rng = np.random.default_rng(seed)
    y = np.asarray(y, dtype=float)
    a = np.asarray(a, dtype=bool)
    n = len(y)
    stats = {"pod": [], "far": [], "csi": []}
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        m = contingency(pd.Series(y[idx]), pd.Series(a[idx]))
        for k in stats:
            stats[k].append(m[k])
    return {k: (float(np.nanpercentile(v, 2.5)),
                float(np.nanpercentile(v, 97.5))) for k, v in stats.items()}


def main():
    a = parse_args()
    df = load_locked_dataframe()
    df = df.sort_values(["station_name", "date"]).reset_index(drop=True)

    dfl = add_forward_label(df, horizon=HORIZON_DAYS)
    bundle = fit_locked_model(dfl, label_col="bloom_fwd",
                              train_end=TRAIN_END)
    print(f"Locked LR trained on {bundle['n_train']:,} rows through "
          f"{TRAIN_END.date()}")
    df["bloom_prob"] = predict_proba(bundle, df)

    west = df[df["longitude_x"] < a.west_lon].copy()
    stations = sorted(west["station_name"].unique())
    print(f"\nWestern basin (longitude_x < {a.west_lon}): "
          f"{len(stations)} stations: {', '.join(map(str, stations))}")

    days = basin_series(west)

    # ---- validation sweep (pre-registered rule) ----
    val = days[(days["date"] >= VAL_START) & (days["date"] <= VAL_END)
               & days["basin_label"].notna()]
    sweep = []
    for t in GRID:
        m = contingency(val["basin_label"], val["basin_prob"] >= t)
        sweep.append(dict(threshold=t, **m))
    sweep = pd.DataFrame(sweep)
    os.makedirs("data", exist_ok=True)
    sweep.to_csv("data/basin_alert_val_sweep.csv", index=False)

    ok = sweep[sweep["pod"] >= POD_FLOOR]
    t_basin = float(ok["threshold"].max()) if len(ok) else float(GRID[0])
    print(f"\nVal 2020-2022 ({len(val)} basin-days): pre-registered rule "
          f"POD >= {POD_FLOOR} selects t_basin = {t_basin:.2f}")
    print(sweep.loc[sweep['threshold'].isin(
        [t_basin, 0.35, 0.5, 0.6])].to_string(index=False))

    # ---- single test evaluation ----
    test = days[(days["date"] >= TEST_START) & (days["date"] <= TEST_END)
                & days["basin_label"].notna()].copy()
    test["alert"] = test["basin_prob"] >= t_basin
    m = contingency(test["basin_label"], test["alert"])
    empty = float((~test["has_future"]).mean())

    ci = bootstrap_ci(test["basin_label"], test["alert"])
    print(f"\n== TEST 2023-2025, basin alert at t_basin={t_basin:.2f} ==")
    print(f"basin decision days : {len(test)}")
    print(f"base rate           : {test['basin_label'].mean():.3f}")
    print(f"empty windows       : {empty*100:.1f}%  "
          f"(station-day baseline: ~41%)")
    print(f"POD {m['pod']:.3f} [{ci['pod'][0]:.3f}, {ci['pod'][1]:.3f}]")
    print(f"FAR {m['far']:.3f} [{ci['far'][0]:.3f}, {ci['far'][1]:.3f}]")
    print(f"CSI {m['csi']:.3f} [{ci['csi'][0]:.3f}, {ci['csi'][1]:.3f}]")
    print(f"(TP {m['tp']} / FP {m['fp']} / FN {m['fn']})")

    days.to_csv("data/basin_alert_daily.csv", index=False)
    print("\nSaved data/basin_alert_val_sweep.csv, data/basin_alert_daily.csv")


if __name__ == "__main__":
    main()