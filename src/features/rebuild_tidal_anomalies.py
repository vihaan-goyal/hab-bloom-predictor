"""
rebuild_tidal_anomalies.py
--------------------------
Replaces the FULL-RECORD tidal climatology with a causal, expanding-window one,
then rebuilds the canonical feature file on top of the corrected daily file.

THE DEFECT
add_tidal_features.py:113-119 computes

    monthly_clim = monthly.groupby('month_num')['tidal_gt'].mean()
    monthly['tidal_gt_anom'] = monthly['tidal_gt'] - monthly_clim

i.e. the seasonal mean over the WHOLE 1993-2025 monthly series, subtracted from
every row including training rows. Test-period sea level therefore informs
tidal_gt_anom and tidal_msl_anom on training rows. Both are in the locked 35.

THE FIX
The climatology for a given month in year Y is the mean of that same calendar
month over years STRICTLY BEFORE Y. Leak-free by construction, and it is what a
forecaster standing in year Y could have computed. Months with fewer than
MIN_PRIOR_YEARS of history are left NaN rather than guessed.

WHY THIS SCRIPT EXISTS SEPARATELY FROM add_tidal_features.py
The raw NOAA CO-OPS files (data/raw/tidal/) are no longer on disk, so
add_tidal_features.py cannot be re-run. data/tidal_features_monthly.csv
survives and still carries the raw tidal_gt / tidal_msl levels, so the
anomalies are fully recomputable from it. add_tidal_features.py has been
patched with the same expanding logic so the defect cannot recur if the raw
files are ever restored.

Writes NEW files; never overwrites hab_features_tidal.csv.

Usage (from repo root):
    python src/features/rebuild_tidal_anomalies.py
"""

import argparse
import os

import pandas as pd

MIN_PRIOR_YEARS = 3
TIDAL_FEATURES = ["tidal_gt", "tidal_msl", "tidal_gt_anom", "tidal_msl_anom"]


def parse_args():
    p = argparse.ArgumentParser(description="Causal tidal anomalies")
    p.add_argument("--data-dir", default="data")
    p.add_argument("--monthly", default="tidal_features_monthly.csv")
    p.add_argument("--daily", default="hab_features_daily_v2.csv")
    p.add_argument("--out", default="hab_features_tidal_v2.csv")
    p.add_argument("--monthly-out", default="tidal_features_monthly_v2.csv")
    return p.parse_args()


def expanding_monthly_climatology(monthly, col):
    """Mean of `col` over prior years' same calendar month, strictly before the
    current row. NaN until MIN_PRIOR_YEARS of history exist."""
    grp = monthly.groupby("month_num")[col]
    prior_mean = grp.transform(lambda s: s.expanding().mean().shift(1))
    prior_n = grp.transform(lambda s: s.expanding().count().shift(1))
    return prior_mean.where(prior_n >= MIN_PRIOR_YEARS)


def main():
    a = parse_args()
    dd = a.data_dir
    mo_path = os.path.join(dd, a.monthly)
    da_path = os.path.join(dd, a.daily)
    out_path = os.path.join(dd, a.out)

    print(f"Loading {mo_path} ...")
    m = pd.read_csv(mo_path)
    m["date"] = pd.to_datetime(m["date"])
    m = m.sort_values("date").reset_index(drop=True)
    m["month_num"] = m["date"].dt.month
    print(f"  {len(m):,} monthly records, "
          f"{m['date'].min().date()} to {m['date'].max().date()}")

    old_gt = m.get("tidal_gt_anom")
    old_msl = m.get("tidal_msl_anom")

    m["tidal_gt_clim"] = expanding_monthly_climatology(m, "tidal_gt")
    m["tidal_msl_clim"] = expanding_monthly_climatology(m, "tidal_msl")
    m["tidal_gt_anom"] = m["tidal_gt"] - m["tidal_gt_clim"]
    m["tidal_msl_anom"] = m["tidal_msl"] - m["tidal_msl_clim"]

    n_nan = int(m["tidal_gt_anom"].isna().sum())
    print(f"  cold-start months left NaN: {n_nan} "
          f"({100*n_nan/len(m):.1f}%, through "
          f"{m.loc[m['tidal_gt_anom'].notna(), 'date'].min().date()})")

    if old_gt is not None:
        for lbl, old, new in [("tidal_gt_anom", old_gt, m["tidal_gt_anom"]),
                              ("tidal_msl_anom", old_msl, m["tidal_msl_anom"])]:
            d = (new - old).abs()
            print(f"  {lbl}: mean|shift|={d.mean():.4f}  max={d.max():.4f} m")

    m.to_csv(os.path.join(dd, a.monthly_out), index=False)
    print(f"Saved {os.path.join(dd, a.monthly_out)}")

    print(f"\nLoading {da_path} ...")
    hab = pd.read_csv(da_path, low_memory=False)
    hab["date"] = pd.to_datetime(hab["date"])
    hab["month_start"] = hab["date"].values.astype("datetime64[M]")

    tidal_merge = (m[["date"] + TIDAL_FEATURES]
                   .rename(columns={"date": "month_start"}))
    hab_tidal = hab.merge(tidal_merge, on="month_start", how="left")
    hab_tidal = hab_tidal.drop(columns=["month_start"])

    # hab_features_daily.csv still carries a baked `bloom_28d` column: the
    # Family B label (28-day horizon, no right-censoring, ~33% of rows scored
    # negative on an empty window). The original pipeline stripped it from the
    # canonical file and so do we -- labels come from
    # locked_pipeline.add_forward_label, never from a baked column.
    if "bloom_28d" in hab_tidal.columns:
        hab_tidal = hab_tidal.drop(columns=["bloom_28d"])
        print("  dropped stale baked label column: bloom_28d")

    print(f"HAB rows: {len(hab):,}  -->  merged: {len(hab_tidal):,}")
    for f in TIDAL_FEATURES:
        print(f"  {f:<20} {hab_tidal[f].notna().mean()*100:5.1f}% coverage")

    hab_tidal.to_csv(out_path, index=False)
    print(f"\nSaved {out_path} "
          f"({len(hab_tidal):,} rows, {len(hab_tidal.columns)} columns)")


if __name__ == "__main__":
    main()
