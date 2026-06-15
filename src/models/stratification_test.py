"""
stratification_test.py
----------------------
Tests whether a water-column stratification feature improves the model. Stratification
(warm/fresh surface over cool/salty bottom) is the physical switch that lets a bloom
form, so it is the one untested feature with a real bloom-FORMATION mechanism.

Gating reality: the pipeline aggregated CTD profiles to daily, which may have collapsed
the vertical structure. So PHASE 1 hunts for depth-resolved temperature first. If there
are not >=2 depths per station-date, stratification is not buildable and the script
stops and says so (like the buoy thread, fail fast, no fabricated feature).

PHASE 2 (only if depths exist): builds a daily stratification index per station-date
  strat_temp = surface_temp - bottom_temp        (primary; always available with depth+T)
  strat_dens = bottom_density - surface_density   (if salinity at depth exists; proxy)
saves data/stratification_daily.csv, merges it into the harness feature matrix, and runs
the SAME rolling-origin LR CV with and without the feature.

PHASE 3: paired station-year AUC bootstrap (with minus without), plus AUPRC/lift/precision
for each, reusing horizon_decomp.paired_diff_bootstrap so the method matches the rest of
the paper. Verdict on AUC; AUPRC/lift checked so an AUC bump is not miscalled a precision
gain.

Run from repo root (place in src/models/ so imports resolve):
    python src/models/stratification_test.py
    python src/models/stratification_test.py --raw-glob "data/raw/**/*.csv"
    python src/models/stratification_test.py --depth-col sensor_depth --temp-col temperature
"""

import argparse
import glob
import os
import sys
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score

DEPTH_NAMES = ["depth", "sensor_depth", "z", "Depth", "DEPTH", "pressure"]
TEMP_NAMES = ["temperature", "sea_water_temperature", "temp", "water_temp", "Temperature"]
SAL_NAMES = ["salinity", "sea_water_salinity", "sal", "Salinity"]
STN_NAMES = ["station_name", "station", "Station", "site"]
TIME_NAMES = ["time", "date", "datetime", "Date", "Time"]


def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--raw-glob", nargs="+",
                   default=["data/raw/**/*.csv", "data/raw/*.csv", "data/*.csv"],
                   help="glob(s) to search for depth-resolved CTD data")
    p.add_argument("--depth-col", default=None)
    p.add_argument("--temp-col", default=None)
    p.add_argument("--sal-col", default=None)
    p.add_argument("--station-col", default=None)
    p.add_argument("--time-col", default=None)
    p.add_argument("--horizon", type=int, default=21)
    p.add_argument("--threshold", type=float, default=0.60)
    p.add_argument("--first-test-year", type=int, default=2015)
    p.add_argument("--last-test-year", type=int, default=2025)
    p.add_argument("--n-boot", type=int, default=2000)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out-feature", default="data/stratification_daily.csv")
    return p.parse_args()


def _find(cols, names, override):
    if override:
        return override if override in cols else None
    for n in names:
        if n in cols:
            return n
    return None


def discover_depth_source(globs, ov):
    """Return (path, colmap) for the first file with depth-resolved temperature
    (>=2 distinct depths per station-date), else (None, None)."""
    seen = []
    files = []
    for g in globs:
        files += glob.glob(g, recursive=True)
    files = sorted(set(files))
    for f in files:
        try:
            head = pd.read_csv(f, nrows=200)
        except Exception:
            continue
        cols = list(head.columns)
        cmap = {
            "depth": _find(cols, DEPTH_NAMES, ov["depth"]),
            "temp": _find(cols, TEMP_NAMES, ov["temp"]),
            "sal": _find(cols, SAL_NAMES, ov["sal"]),
            "stn": _find(cols, STN_NAMES, ov["stn"]),
            "time": _find(cols, TIME_NAMES, ov["time"]),
        }
        if not (cmap["depth"] and cmap["temp"] and cmap["stn"] and cmap["time"]):
            seen.append((f, "missing depth/temp/station/time"))
            continue
        # confirm multiple depths per station-date on a sample
        s = pd.read_csv(f, usecols=[c for c in cmap.values() if c],
                        skiprows=lambda i: i == 1)  # skip ERDDAP units row if present
        s[cmap["time"]] = pd.to_datetime(s[cmap["time"]], errors="coerce", utc=True)
        s = s.dropna(subset=[cmap["time"]])
        s["d"] = s[cmap["time"]].dt.tz_localize(None).dt.normalize()
        per = s.groupby([cmap["stn"], "d"])[cmap["depth"]].nunique()
        multi = (per >= 2).mean() if len(per) else 0.0
        seen.append((f, f"{(per>=2).sum()} multi-depth station-dates "
                        f"({multi:.0%} of {len(per)})"))
        if (per >= 2).sum() >= 20:
            print(f"  USABLE: {f}")
            for k, v in cmap.items():
                print(f"    {k:6} -> {v}")
            return f, cmap
    print("  no usable depth-resolved temperature file found. Scanned:")
    for f, why in seen[:20]:
        print(f"    {os.path.basename(f):<40} {why}")
    return None, None


def build_strat(path, cmap, out_path):
    use = [c for c in [cmap["stn"], cmap["time"], cmap["depth"], cmap["temp"],
                       cmap["sal"]] if c]
    df = pd.read_csv(path, usecols=use, skiprows=lambda i: i == 1)
    df = df.rename(columns={cmap["stn"]: "station_name", cmap["time"]: "time",
                            cmap["depth"]: "depth", cmap["temp"]: "temp"})
    if cmap["sal"]:
        df = df.rename(columns={cmap["sal"]: "sal"})
    df["time"] = pd.to_datetime(df["time"], errors="coerce", utc=True)
    df = df.dropna(subset=["time"])
    df["date"] = df["time"].dt.tz_localize(None).dt.normalize()
    for c in ["depth", "temp"] + (["sal"] if "sal" in df.columns else []):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["depth", "temp"])

    rows = []
    for (st, d), g in df.groupby(["station_name", "date"]):
        if g["depth"].nunique() < 2:
            continue
        g = g.sort_values("depth")
        top, bot = g.iloc[0], g.iloc[-1]
        strat_temp = float(top["temp"] - bot["temp"])  # surface minus bottom
        rec = {"station_name": str(st), "date": d, "strat_temp": strat_temp,
               "depth_span": float(bot["depth"] - top["depth"])}
        if "sal" in df.columns and g["sal"].notna().any():
            # crude sigma-t proxy: rho ~ 0.8*S - 0.2*(T-10); bottom minus surface
            def sig(r):
                return 0.8 * (r["sal"] if pd.notna(r["sal"]) else np.nan) \
                       - 0.2 * (r["temp"] - 10)
            rec["strat_dens"] = float(sig(bot) - sig(top))
        rows.append(rec)
    strat = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    strat.to_csv(out_path, index=False)
    print(f"\nbuilt stratification for {len(strat):,} station-dates -> {out_path}")
    print(f"  strat_temp: median={strat['strat_temp'].median():.2f} C  "
          f"IQR[{strat['strat_temp'].quantile(.25):.2f},"
          f"{strat['strat_temp'].quantile(.75):.2f}]")
    return strat


def evaluate(pooled, t):
    yt, pr = pooled["y_true"].values, pooled["y_prob"].values
    n, npos = len(yt), int(yt.sum()); base = npos / n
    auc = roc_auc_score(yt, pr) if len(np.unique(yt)) > 1 else np.nan
    apr = average_precision_score(yt, pr)
    pred = pr >= t
    prec = yt[pred].mean() if pred.sum() else np.nan
    return dict(auc=auc, auprc=apr, lift=apr / base, prec=prec,
                base=base, npos=npos)


def main():
    a = parse_args()
    ov = {"depth": a.depth_col, "temp": a.temp_col, "sal": a.sal_col,
          "stn": a.station_col, "time": a.time_col}

    print("=" * 66)
    print("PHASE 1  hunt for depth-resolved temperature")
    print("=" * 66)
    path, cmap = discover_depth_source(a.raw_glob, ov)
    if path is None:
        print("\nSTOP: stratification is not buildable from available files.")
        print("The CTD profiles were collapsed to daily. To pursue this, re-pull the")
        print("LISICOS ERDDAP WQ data WITH the depth dimension, then rerun with")
        print("--raw-glob pointing at it. Not a code problem; the vertical data is gone.")
        return

    print("\n" + "=" * 66)
    print("PHASE 2  build feature + merge into harness matrix")
    print("=" * 66)
    strat = build_strat(path, cmap, a.out_feature)

    from rolling_origin_cv import build_dataset, run_cv
    from label_utils import build_forward_label
    from horizon_decomp import paired_diff_bootstrap

    df, features = build_dataset(clean_labels=False)
    df["bloom_28d"] = build_forward_label(df, horizon=a.horizon, threshold=10.0,
                                          sustained_only=False)
    strat["date"] = pd.to_datetime(strat["date"])
    df["station_name"] = df["station_name"].astype(str)
    df = df.merge(strat, on=["station_name", "date"], how="left")
    strat_feats = [c for c in ["strat_temp", "strat_dens", "depth_span"]
                   if c in df.columns]
    cover = df["strat_temp"].notna().mean()
    print(f"  strat feature coverage on feature rows: {cover:.1%}  "
          f"(missing -> median-filled in CV)")
    print(f"  added features: {strat_feats}")

    print("\n" + "=" * 66)
    print("PHASE 3  with-vs-without rolling-origin CV  (horizon "
          f"{a.horizon}d)")
    print("=" * 66)
    base_pooled = run_cv(df, features, a.first_test_year, a.last_test_year,
                         threshold_mode="fixed", fixed_threshold=a.threshold,
                         min_hist_pos=20, min_val_pos=5, verbose=False)
    strat_pooled = run_cv(df, features + strat_feats, a.first_test_year,
                          a.last_test_year, threshold_mode="fixed",
                          fixed_threshold=a.threshold, min_hist_pos=20,
                          min_val_pos=5, verbose=False)

    b, s = evaluate(base_pooled, a.threshold), evaluate(strat_pooled, a.threshold)
    print(f"{'model':<16} {'AUC':>6} {'AUPRC':>6} {'lift':>6} {'prec@t':>7}")
    print(f"{'baseline':<16} {b['auc']:>6.3f} {b['auprc']:>6.3f} {b['lift']:>6.2f} "
          f"{b['prec']:>7.3f}")
    print(f"{'+stratification':<16} {s['auc']:>6.3f} {s['auprc']:>6.3f} "
          f"{s['lift']:>6.2f} {s['prec']:>7.3f}")

    diffs, nmatch = paired_diff_bootstrap(strat_pooled, base_pooled,
                                          a.n_boot, a.seed)
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    print(f"\nPAIRED AUC DIFFERENCE  (+strat) minus baseline")
    print(f"  matched rows: {nmatch:,}")
    print(f"  mean: {np.mean(diffs):+.3f}  95% CI [{lo:+.3f}, {hi:+.3f}]  "
          f"P(>0)={np.mean(diffs>0):.3f}")
    if lo > 0:
        print("  -> stratification significantly improves ranking. Keep it.")
    elif hi < 0:
        print("  -> stratification hurts. Drop it.")
    else:
        print("  -> not distinguishable; stratification adds no ranking signal.")
    print("\nAlso check the lift column: even a real AUC gain need not raise lift")
    print("(precision skill). Only claim a precision benefit if lift rises too.")


if __name__ == "__main__":
    main()