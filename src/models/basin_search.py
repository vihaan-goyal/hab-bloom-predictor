"""
basin_search.py
---------------
Pre-registered search for a basin-alert operating point that beats a trivial
forecast.

reference_baselines.py established the problem: at basin level the locked alert
reaches lift 1.37x, its advantage over "always alert" has a CI touching zero
(+0.390 [+0.000, +0.909]), and simple climatology (1.52x) and persistence (1.81x)
score numerically higher. This script asks whether any admissible configuration
of the basin product does better, under a protocol designed so the answer can be
trusted either way.

Why the protocol is this strict
-------------------------------
notes/PRECISION_CEILING_INVESTIGATION.md Finding 1 records a precision of 0.500
that turned out to be threshold-selection inflation: a threshold picked by
maximising F1 on a test block with 74 positives, across 17 thresholds. This
search evaluates 216 configurations against a val block with ~12 events, so the
same failure is available in a more dangerous form. Guards, all fixed before
running:

  1. Every configuration is scored on VAL 2020-2022 only. Test is not read
     during the search.
  2. The selection rule is fixed in advance: maximise val lift subject to
     val POD >= 0.8, ties broken by the higher threshold.
  3. Exactly ONE configuration is scored on test, once.
  4. A permutation null re-runs the entire search on shuffled val labels. If the
     real best val lift sits inside that null distribution, the search found
     noise, and that is the reported result.
  5. Lift is the objective, not FAR or CSI, because it is the only one of those
     defined against a reference rather than rewarding a base rate that a
     restrictive configuration can manufacture.

Guard 5 exists because of a measured trap: gating the current alert to the
high-risk seasons RAISED apparent quality on FAR while LOWERING lift (1.13x
gated vs 1.28x ungated), since dropping zero-event months raises the base rate
and lift divides by it.

Run from repo root:
    python src/models/basin_search.py --dry-run    # print grid, touch no data
    python src/models/basin_search.py
"""

import argparse
import itertools
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from locked_pipeline import (  # noqa: E402
    BLOOM_THRESHOLD, HORIZON_DAYS, add_forward_label, fit_locked_model,
    load_locked_dataframe, predict_proba)
from reference_baselines import LABEL, contingency  # noqa: E402

TRAIN_END = pd.Timestamp("2019-12-31")
VAL_START, VAL_END = pd.Timestamp("2020-01-01"), pd.Timestamp("2022-12-31")
TEST_START = pd.Timestamp("2023-01-01")
POD_FLOOR = 0.8

# ---- the pre-registered grid (216 cells) -----------------------------------
THRESHOLDS = np.round(np.arange(0.05, 0.96, 0.05), 2)      # 19
WEST_LONS = [-73.6, -73.4, -73.2, None]                     # 4 (None = all LIS)
SEASONS = ["none", "winter", "summer"]                      # 3
MIN_STATIONS = [1, 2]                                       # 2
AGGREGATORS = ["max", "mean"]                               # 2

WINTER, SUMMER = {1, 2, 3, 4}, {6, 7, 8, 9}
OUT_VAL = "data/basin_search_val.csv"
OUT_RESULT = "data/basin_search_result.csv"


def grid():
    return list(itertools.product(WEST_LONS, SEASONS, MIN_STATIONS, AGGREGATORS))


def n_configs():
    return len(grid()) * len(THRESHOLDS)


def basin_days(df, west_lon, agg, min_stations):
    """Collapse to one decision unit per sampled date under this configuration."""
    w = df if west_lon is None else df[df["longitude_x"] < west_lon]
    if w.empty:
        return None
    days = (w.groupby("date")
             .agg(prob=("bloom_prob", agg),
                  n_stations=("station_name", "nunique"))
             .reset_index().sort_values("date"))
    days = days[days["n_stations"] >= min_stations]
    if days.empty:
        return None

    exc = w.loc[w["Chlorophyll"] > BLOOM_THRESHOLD, "date"].sort_values().unique()
    last = w["date"].max()
    lab = []
    for d in days["date"]:
        end = d + pd.Timedelta(days=HORIZON_DAYS)
        if ((exc > d) & (exc <= end)).any():
            lab.append(1.0)
        elif end <= last:
            lab.append(0.0)
        else:
            lab.append(np.nan)
    days[LABEL] = lab
    days["month"] = days["date"].dt.month
    return days.dropna(subset=[LABEL])


def season_mask(days, season):
    if season == "winter":
        return days["month"].isin(WINTER)
    if season == "summer":
        return days["month"].isin(SUMMER)
    return pd.Series(True, index=days.index)


def search(df, era_start, era_end, labels_override=None):
    """Score every configuration on one era. One row per cell.

    labels_override: callable(n) -> array used INSTEAD of the real labels, for
    the permutation null. Applied after the era filter so lengths match.
    """
    rows = []
    for west_lon, season, min_st, agg in grid():
        days = basin_days(df, west_lon, agg, min_st)
        if days is None:
            continue
        era = days[(days["date"] >= era_start) & (days["date"] <= era_end)]
        era = era[season_mask(era, season)]
        if len(era) < 10 or era[LABEL].sum() < 3:
            continue
        y = era[LABEL].to_numpy()
        if labels_override is not None:
            y = labels_override(len(y))
            if y.sum() < 3:
                continue
        p = era["prob"].to_numpy(dtype=float)
        for t in THRESHOLDS:
            m = contingency(y, p >= t)
            rows.append({"threshold": t,
                         "west_lon": "all" if west_lon is None else west_lon,
                         "season": season, "min_stations": min_st,
                         "aggregator": agg, "n": len(era),
                         "events": int(y.sum()), **m})
    return pd.DataFrame(rows)


def select(val_rows, floor=POD_FLOOR):
    """The pre-registered rule. Returns the winning row, or None."""
    if val_rows.empty:
        return None
    ok = val_rows[(val_rows["pod"] >= floor) & np.isfinite(val_rows["lift"])]
    if ok.empty:
        return None
    best = ok["lift"].max()
    tied = ok[np.isclose(ok["lift"], best)]
    return tied.sort_values("threshold", ascending=False).iloc[0]


def permutation_null(df, n_perm, base, seed=42):
    """Re-run the whole search on shuffled val labels, keeping the best val lift
    from each shuffle. This is the distribution of 'best lift findable by chance'
    given 216 configurations at this sample size."""
    rng = np.random.default_rng(seed)
    best = []
    for i in range(n_perm):
        def shuffled(n, _rng=rng, _b=base):
            return (_rng.random(n) < _b).astype(float)
        sel = select(search(df, VAL_START, VAL_END, labels_override=shuffled))
        best.append(sel["lift"] if sel is not None else np.nan)
        if (i + 1) % 25 == 0:
            print(f"    permutation {i + 1}/{n_perm}")
    return np.array([b for b in best if np.isfinite(b)])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="print the grid and exit without touching data")
    ap.add_argument("--n-perm", type=int, default=200)
    args = ap.parse_args()

    print(f"PRE-REGISTERED GRID: {n_configs()} configurations")
    print(f"  thresholds   : {len(THRESHOLDS)}  {THRESHOLDS[0]}..{THRESHOLDS[-1]}")
    print(f"  west_lon     : {WEST_LONS}")
    print(f"  season       : {SEASONS}")
    print(f"  min_stations : {MIN_STATIONS}")
    print(f"  aggregator   : {AGGREGATORS}")
    print(f"  selection    : max val lift subject to val POD >= {POD_FLOOR}, "
          f"ties -> higher threshold")
    print(f"  search era   : {VAL_START.date()} .. {VAL_END.date()} "
          f"(test >= {TEST_START.date()} is NOT read during the search)")
    if args.dry_run:
        print("\n--dry-run: no data read, exiting.")
        return

    df = load_locked_dataframe()
    df = df.sort_values(["station_name", "date"]).reset_index(drop=True)
    df = add_forward_label(df, horizon=HORIZON_DAYS, threshold=BLOOM_THRESHOLD,
                           col=LABEL)
    bundle = fit_locked_model(df, label_col=LABEL, train_end=TRAIN_END)
    df["bloom_prob"] = predict_proba(bundle, df)
    df["station_name"] = df["station_name"].astype(str)

    print("\nScoring the grid on VAL 2020-2022 ...")
    val_rows = search(df, VAL_START, VAL_END)
    val_rows.to_csv(OUT_VAL, index=False)
    print(f"  {len(val_rows)} scorable cells -> {OUT_VAL}")

    sel = select(val_rows)
    if sel is None:
        print("\nNo configuration reached the POD floor on val. Search ends.")
        return

    print("\nSELECTED (on val only):")
    for k in ["threshold", "west_lon", "season", "min_stations", "aggregator"]:
        print(f"  {k:<13}= {sel[k]}")
    print(f"  val: n={sel['n']} events={sel['events']} "
          f"base={sel['base_rate']:.3f} POD={sel['pod']:.3f} "
          f"FAR={sel['far']:.3f} lift={sel['lift']:.2f}x")

    print(f"\nPermutation null ({args.n_perm} shuffles, full "
          f"{n_configs()}-cell search each) ...")
    null = permutation_null(df, args.n_perm, float(sel["base_rate"]))
    pct = float((null < sel["lift"]).mean() * 100) if len(null) else np.nan
    if len(null):
        print(f"  null best-lift: median {np.median(null):.2f}x, "
              f"95th pct {np.percentile(null, 95):.2f}x, max {null.max():.2f}x")
    print(f"  real best val lift {sel['lift']:.2f}x sits at the "
          f"{pct:.1f}th percentile of the null")
    passed = bool(np.isfinite(pct) and pct >= 95)
    print("  -> " + ("EXCEEDS the null" if passed else
                     "INSIDE the null: this search found noise, not signal"))

    print("\nScoring the selected configuration on TEST, once ...")
    wl = None if sel["west_lon"] == "all" else float(sel["west_lon"])
    days = basin_days(df, wl, sel["aggregator"], int(sel["min_stations"]))
    te = days[days["date"] >= TEST_START]
    te = te[season_mask(te, sel["season"])]
    m = contingency(te[LABEL], te["prob"].to_numpy(dtype=float) >= sel["threshold"])
    always = contingency(te[LABEL], np.ones(len(te), dtype=bool))
    print(f"  test: n={len(te)} events={m['tp'] + m['fn']} "
          f"base={m['base_rate']:.3f}")
    print(f"  POD={m['pod']:.3f} FAR={m['far']:.3f} CSI={m['csi']:.3f} "
          f"precision={m['precision']:.3f} lift={m['lift']:.2f}x")
    print(f"  always-alert on the same set: FAR={always['far']:.3f} lift=1.00x")
    print(f"  margin over always-alert: {m['lift'] - 1:+.2f}x lift, "
          f"{always['far'] - m['far']:+.3f} FAR")

    pd.DataFrame([{**{k: sel[k] for k in
                      ["threshold", "west_lon", "season", "min_stations",
                       "aggregator"]},
                   "val_lift": sel["lift"], "n_configs": n_configs(),
                   "null_pct": pct, "exceeds_null": passed,
                   **{f"test_{k}": v for k, v in m.items()}}]
                 ).to_csv(OUT_RESULT, index=False)
    print(f"\n-> {OUT_RESULT}")


if __name__ == "__main__":
    main()
