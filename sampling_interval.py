"""
sampling_interval.py

Compute the real interval between chlorophyll measurements, per station,
from the CT DEEP / LISICOS in-situ record.

The interval that matters for a 21-day forecast is the gap between actual
chlorophyll readings, not the gap between rows in a daily-gridded feature
file. So this script drops rows where Chlorophyll is missing, keeps one
reading per station per date (surface depth), and measures the day gaps
between consecutive readings.

Reports per-station median / mean / IQR / max gap, an overall summary,
a summer-vs-off-season split, and the share of gaps longer than the 21-day
horizon (the number that makes the monitoring-cadence limitation concrete).

Usage:
    conda activate hab
    python sampling_interval.py
    python sampling_interval.py --data data/hab_features_final.csv --out data/station_sampling_intervals.csv

Defaults match the schema used by src/deploy/daily_inference.py.
"""

import argparse
import sys
import pandas as pd
import numpy as np

HORIZON_DAYS = 21          # forecast horizon
SUMMER_MONTHS = {6, 7, 8, 9}  # CT DEEP samples more heavily Jun-Sep


def parse_args():
    p = argparse.ArgumentParser(description="Per-station chlorophyll sampling interval.")
    p.add_argument("--data", default="data/hab_features_final.csv",
                   help="Path to the CT DEEP CSV.")
    p.add_argument("--station-col", default="station_name")
    p.add_argument("--date-col", default="date")
    p.add_argument("--chl-col", default="Chlorophyll")
    p.add_argument("--depth-col", default="depth_code",
                   help="Depth column to filter on. Set to '' to skip filtering.")
    p.add_argument("--depth-value", default="S",
                   help="Depth value to keep (surface).")
    p.add_argument("--out", default="data/station_sampling_intervals.csv")
    return p.parse_args()


def load(args):
    try:
        df = pd.read_csv(args.data, low_memory=False)
    except FileNotFoundError:
        sys.exit(f"Could not find {args.data}. Pass the right path with --data.")

    for col in (args.station_col, args.date_col, args.chl_col):
        if col not in df.columns:
            sys.exit(
                f"Column '{col}' not in file. Found columns:\n  "
                + "\n  ".join(df.columns)
            )

    df[args.date_col] = pd.to_datetime(df[args.date_col], format="ISO8601", errors="coerce")

    # Coerce chlorophyll to numeric. This also cleanly drops an ERDDAP units
    # row (line 2 of an ERDDAP .csv holds units like "ug/L", not real data).
    df[args.chl_col] = pd.to_numeric(df[args.chl_col], errors="coerce")

    # Keep surface readings only, so a surface+bottom visit counts as one sample.
    if args.depth_col and args.depth_col in df.columns:
        df = df[df[args.depth_col] == args.depth_value]

    # The measurement dates are the rows where chlorophyll was actually read.
    df = df.dropna(subset=[args.date_col, args.chl_col])

    # One reading per station per day (collapse any intra-day duplicates).
    df = (df.groupby([args.station_col, args.date_col], as_index=False)[args.chl_col]
            .mean())
    return df


def per_station_stats(df, station_col, date_col):
    rows = []
    for station, g in df.groupby(station_col):
        dates = g[date_col].sort_values()
        if len(dates) < 2:
            continue
        gaps = dates.diff().dt.days.dropna().values  # n readings -> n-1 gaps
        gaps = gaps[gaps > 0]
        if len(gaps) == 0:
            continue

        summer = g[g[date_col].dt.month.isin(SUMMER_MONTHS)][date_col].sort_values()
        summer_gaps = summer.diff().dt.days.dropna().values
        summer_gaps = summer_gaps[summer_gaps > 0]

        rows.append({
            "station": station,
            "n_readings": len(dates),
            "span_years": round((dates.max() - dates.min()).days / 365.25, 1),
            "median_gap_days": round(float(np.median(gaps)), 1),
            "mean_gap_days": round(float(np.mean(gaps)), 1),
            "p25_gap_days": round(float(np.percentile(gaps, 25)), 1),
            "p75_gap_days": round(float(np.percentile(gaps, 75)), 1),
            "max_gap_days": int(gaps.max()),
            "summer_median_gap_days": (round(float(np.median(summer_gaps)), 1)
                                       if len(summer_gaps) else np.nan),
            "pct_gaps_over_horizon": round(100 * np.mean(gaps > HORIZON_DAYS), 1),
        })
    return pd.DataFrame(rows).sort_values("median_gap_days", ascending=False)


def main():
    args = parse_args()
    df = load(args)
    stats = per_station_stats(df, args.station_col, args.date_col)

    if stats.empty:
        sys.exit("No station had 2+ chlorophyll readings. Check the column names.")

    # Pool all gaps across stations for an overall figure.
    all_gaps = []
    for _, g in df.groupby(args.station_col):
        d = g[args.date_col].sort_values().diff().dt.days.dropna().values
        all_gaps.extend(d[d > 0].tolist())
    all_gaps = np.array(all_gaps)

    print("\nPer-station chlorophyll sampling interval")
    print("=" * 60)
    print(stats.to_string(index=False))

    print("\nOverall (all stations pooled)")
    print("=" * 60)
    print(f"  stations analyzed:        {len(stats)}")
    print(f"  total inter-sample gaps:  {len(all_gaps):,}")
    print(f"  median gap:               {np.median(all_gaps):.1f} days")
    print(f"  mean gap:                 {np.mean(all_gaps):.1f} days")
    print(f"  25th / 75th pct:          {np.percentile(all_gaps,25):.1f} / "
          f"{np.percentile(all_gaps,75):.1f} days")
    print(f"  gaps longer than {HORIZON_DAYS}d:      {100*np.mean(all_gaps>HORIZON_DAYS):.1f}%")
    print(f"  longest single gap:       {all_gaps.max():,} days")

    stats.to_csv(args.out, index=False)
    print(f"\nSaved per-station table to {args.out}")


if __name__ == "__main__":
    main()