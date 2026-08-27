"""
rebuild_climatology.py
----------------------
Replaces the FULL-RECORD chlorophyll climatology with a causal, expanding-window
climatology, removing test-period information from `chl_climatology` and
`chl_anomaly`.

THE DEFECT
The climatology baked into hab_features_daily.csv is a static per-(station,
month) mean of Chlorophyll taken over the ENTIRE 1993-2025 record, computed at
measurement level over hab_features_final.csv. Verified exactly: the stored
values match the full-record mean to 3.6e-15, and the train-only (<=2019) mean
to 5.5 ug/L. 14.9% of the observations feeding each cell come from the test
years (2023+), so test-period chlorophyll is baked into the features used on
every training row. Both columns are in the locked 35.

THE FIX
For a row at (station s, month m, date t), the climatology is the mean of all
measurements at (s, m) with date STRICTLY BEFORE t. That is exactly what a
forecaster standing at date t could have computed, so it is leak-free by
construction and matches how daily_inference.py walks forward.

Definition is otherwise preserved: the mean is taken over measurement-level
rows (hab_features_final.csv, ~105 measurements per station-day), not over
station-day aggregates, because that is what the original computed.

FALLBACK LADDER (cold start -- early years have no prior same-month history)
  1. (station, month) expanding mean, once >= MIN_PRIOR_DATES prior visits
  2. (month) all-station expanding mean, once >= MIN_PRIOR_DATES prior visits
     -- keeps the seasonal shape when a single station lacks history
  3. NaN -- left for the model's train-median imputation

chl_anomaly is recomputed as Chlorophyll - chl_climatology, matching the
original identity (verified to 7.1e-15).

Writes a NEW file; never overwrites hab_features_daily.csv, which has no
producer in the repo and is not recoverable if lost.

Usage (from repo root):
    python src/features/rebuild_climatology.py
    python src/features/rebuild_climatology.py --data-dir /path/to/data
"""

import argparse
import os

import numpy as np
import pandas as pd

MIN_PRIOR_DATES = 3      # prior visit-dates required before a cell is trusted


def parse_args():
    p = argparse.ArgumentParser(description="Causal chlorophyll climatology")
    p.add_argument("--data-dir", default="data")
    p.add_argument("--source", default="hab_features_final.csv",
                   help="measurement-level source the climatology is built from")
    p.add_argument("--target", default="hab_features_daily.csv",
                   help="file whose climatology columns are replaced")
    p.add_argument("--out", default="hab_features_daily_v2.csv")
    p.add_argument("--audit-out", default="climatology_audit.csv")
    p.add_argument("--source-max-date", default=None,
                   help="Drop source measurements after this date. Used to PROVE "
                        "the climatology is causal: truncating the source must "
                        "leave every earlier row's value bit-identical.")
    return p.parse_args()


def _expanding_prior(measurements, keys):
    """Step function of the mean of every measurement up to AND INCLUDING each
    date, per `keys`. Consumers merge_asof onto it with allow_exact_matches=
    False, which turns 'up to and including the previous visit' into 'strictly
    before t' -- the causal quantity we want."""
    agg = (measurements.groupby(keys + ["date"], as_index=False)["Chlorophyll"]
                       .agg(obs_sum="sum", obs_n="count")
                       .sort_values(keys + ["date"]))
    grp = agg.groupby(keys, sort=False)
    agg["cum_sum"] = grp["obs_sum"].cumsum()
    agg["cum_n"] = grp["obs_n"].cumsum()
    agg["prior_dates"] = grp.cumcount() + 1     # visits up to and incl. this one
    agg["clim"] = agg["cum_sum"] / agg["cum_n"]
    return agg[keys + ["date", "clim", "prior_dates", "cum_n"]].sort_values("date")


def main():
    a = parse_args()
    dd = a.data_dir
    src_path = os.path.join(dd, a.source)
    tgt_path = os.path.join(dd, a.target)
    out_path = os.path.join(dd, a.out)

    if os.path.abspath(out_path) == os.path.abspath(tgt_path):
        raise SystemExit("Refusing to overwrite the target in place.")

    print(f"Loading measurement-level source {src_path} ...")
    f = pd.read_csv(src_path, low_memory=False,
                    usecols=["station_name", "date", "Chlorophyll"])
    f["date"] = (pd.to_datetime(f["date"], utc=True, errors="coerce")
                   .dt.tz_localize(None).dt.normalize())
    f["station_name"] = f["station_name"].astype(str)
    f = f.dropna(subset=["Chlorophyll", "date"])
    if a.source_max_date:
        cutoff = pd.Timestamp(a.source_max_date)
        before = len(f)
        f = f[f["date"] <= cutoff]
        print(f"  TRUNCATED source at {cutoff.date()}: "
              f"{before:,} -> {len(f):,} measurements")
    f["month"] = f["date"].dt.month
    print(f"  {len(f):,} measurements, {f['station_name'].nunique()} stations, "
          f"{f['date'].min().date()} to {f['date'].max().date()}")

    print("Building expanding (station, month) climatology ...")
    stn = _expanding_prior(f, ["station_name", "month"])
    print("Building expanding (month) fallback climatology ...")
    glb = _expanding_prior(f, ["month"])

    print(f"Loading target {tgt_path} ...")
    d = pd.read_csv(tgt_path, low_memory=False)
    d["date"] = pd.to_datetime(d["date"])
    d["station_name"] = d["station_name"].astype(str)
    d["month_num"] = d["date"].dt.month
    d = d.sort_values("date").reset_index(drop=True)

    old_clim = d["chl_climatology"].copy()
    old_anom = d["chl_anomaly"].copy()

    # merge_asof with allow_exact_matches=False => strictly-prior history only.
    d = pd.merge_asof(
        d, stn.rename(columns={"month": "month_num",
                               "clim": "clim_stn",
                               "prior_dates": "n_stn",
                               "cum_n": "obs_stn"}),
        on="date", by=["station_name", "month_num"],
        direction="backward", allow_exact_matches=False)
    d = pd.merge_asof(
        d, glb.rename(columns={"month": "month_num",
                               "clim": "clim_glb",
                               "prior_dates": "n_glb",
                               "cum_n": "obs_glb"}),
        on="date", by="month_num",
        direction="backward", allow_exact_matches=False)

    use_stn = d["clim_stn"].notna() & (d["n_stn"] >= MIN_PRIOR_DATES)
    use_glb = (~use_stn) & d["clim_glb"].notna() & (d["n_glb"] >= MIN_PRIOR_DATES)

    new_clim = pd.Series(np.nan, index=d.index)
    new_clim[use_stn] = d.loc[use_stn, "clim_stn"]
    new_clim[use_glb] = d.loc[use_glb, "clim_glb"]

    tier = pd.Series("none", index=d.index)
    tier[use_stn] = "station_month"
    tier[use_glb] = "month_fallback"

    d["chl_climatology"] = new_clim
    d["chl_anomaly"] = d["Chlorophyll"] - new_clim

    n = len(d)
    print("\nFallback tier usage:")
    for t, c in tier.value_counts().items():
        print(f"  {t:<16} {c:6,}  ({100*c/n:5.1f}%)")

    delta = (new_clim - old_clim).abs()
    print(f"\nClimatology shift vs full-record (where both defined, n={delta.notna().sum():,}):")
    print(f"  mean={delta.mean():.3f}  median={delta.median():.3f}  "
          f"p90={delta.quantile(.90):.3f}  max={delta.max():.3f} ug/L")
    rel = (delta / old_clim.abs()).replace([np.inf, -np.inf], np.nan)
    print(f"  relative: median={100*rel.median():.1f}%  p90={100*rel.quantile(.90):.1f}%")

    for yrs, lbl in [((1993, 2019), "train 1993-2019"),
                     ((2020, 2022), "val   2020-2022"),
                     ((2023, 2025), "test  2023-2025")]:
        m = d["date"].dt.year.between(*yrs)
        print(f"  {lbl}: mean|shift|={delta[m].mean():.3f}  "
              f"missing_clim={int(new_clim[m].isna().sum()):,}/{int(m.sum()):,}")

    audit = pd.DataFrame({
        "station_name": d["station_name"], "date": d["date"],
        "month": d["month_num"], "Chlorophyll": d["Chlorophyll"],
        "clim_fullrecord_LEAKED": old_clim, "clim_expanding": new_clim,
        "anom_fullrecord_LEAKED": old_anom, "anom_expanding": d["chl_anomaly"],
        "tier": tier, "prior_visits_station_month": d["n_stn"],
    })
    audit.to_csv(os.path.join(dd, a.audit_out), index=False)
    print(f"\nSaved {os.path.join(dd, a.audit_out)}")

    d = d.drop(columns=["month_num", "clim_stn", "n_stn", "obs_stn",
                        "clim_glb", "n_glb", "obs_glb"])
    d.to_csv(out_path, index=False)
    print(f"Saved {out_path} ({len(d):,} rows, {len(d.columns)} columns)")


if __name__ == "__main__":
    main()
