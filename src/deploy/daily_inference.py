"""
daily_inference.py  (v2 -- locked pipeline)
-------------------------------------------
Early-warning inference for the LOCKED model. Replaces the superseded
XGBoost/7-day version.

For a target date D:
  1. Loads the canonical dataset via src.models.locked_pipeline (single
     source of truth -- no feature engineering is duplicated here).
  2. Trains the locked LR on all rows whose 21-day label window is fully
     observed on or before D (walk-forward: no future information).
  3. Scores the most recent station visit at or before D for every station
     (visits older than --max-stale days are reported as STALE, not scored).
  4. Alert = P(exceedance within 21d) >= t* (frozen operating point 0.35,
     selected out-of-sample on 2020-2022; see warning_operating_point.py).
  5. Writes data/daily_predictions.csv for the dashboard.

Operating characteristics at t*=0.35 (out-of-sample test 2023-2025):
  POD 0.875 [0.750, 0.962] | FAR 0.875 | precision 0.125 [0.077, 0.172]
An alert means: sample this station within the next 3 weeks. Roughly 1 in
8 alerts precedes a verified exceedance, a 2.7x lift over the base rate.

Aeration scoring from the previous version is intentionally omitted until
the intervention framework rerun on corrected data is complete.

Usage (from repo root):
    python src/deploy/daily_inference.py
    python src/deploy/daily_inference.py --date 2025-06-01
"""

import argparse
import os
import sys
from datetime import date

import pandas as pd

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")))
from src.models.locked_pipeline import (          # noqa: E402
    HORIZON_DAYS, add_forward_label, fit_locked_model,
    load_locked_dataframe, predict_proba)

T_STAR = 0.35            # frozen operating point -- do NOT tune here
OUTPUT_PATH = "data/daily_predictions.csv"


def parse_args():
    p = argparse.ArgumentParser(description="Locked-model HAB early warning")
    p.add_argument("--date", type=str, default=None,
                   help="Target date YYYY-MM-DD (default: today)")
    p.add_argument("--t-star", type=float, default=T_STAR)
    p.add_argument("--max-stale", type=int, default=45,
                   help="skip stations whose latest visit is older than this")
    return p.parse_args()


def main():
    a = parse_args()
    target = (pd.Timestamp(a.date) if a.date
              else pd.Timestamp(date.today()))
    print(f"Target date: {target.date()}   t* = {a.t_star}   "
          f"horizon = {HORIZON_DAYS}d")

    df = load_locked_dataframe()
    df = add_forward_label(df, horizon=HORIZON_DAYS)

    # Walk-forward: train only on rows whose label window closed by target.
    train_end = target - pd.Timedelta(days=HORIZON_DAYS)
    bundle = fit_locked_model(df, label_col="bloom_fwd", train_end=train_end)
    print(f"Trained locked LR on {bundle['n_train']:,} rows through "
          f"{train_end.date()} (bloom rate "
          f"{bundle['train_bloom_rate']*100:.1f}%)")

    # Latest visit per station at or before target.
    past = df[df['date'] <= target]
    latest = (past.sort_values('date')
                  .groupby('station_name', as_index=False).tail(1)).copy()
    latest['days_old'] = (target - latest['date']).dt.days
    fresh = latest[latest['days_old'] <= a.max_stale].copy()
    stale = latest[latest['days_old'] > a.max_stale]

    if fresh.empty:
        print(f"\nNo stations with a visit within {a.max_stale}d of "
              f"{target.date()}.")
        if len(latest):
            newest = latest.loc[latest['days_old'].idxmin()]
            print(f"Newest visit: {newest['station_name']} on "
                  f"{newest['date'].date()} ({int(newest['days_old'])}d old). "
                  f"All {len(stale)} stations stale; nothing to score.")
        else:
            print("No station visits at or before the target date at all.")
        # Write an empty predictions file so the dashboard doesn't read stale output.
        pd.DataFrame(columns=['station_name', 'date', 'days_old',
                              'bloom_prob', 'alert']).to_csv(OUTPUT_PATH,
                                                             index=False)
        print(f"Saved empty {OUTPUT_PATH}")
        return

    fresh['bloom_prob'] = predict_proba(bundle, fresh)
    fresh['alert'] = fresh['bloom_prob'] >= a.t_star

    out_cols = ['station_name', 'date', 'days_old', 'bloom_prob', 'alert']
    fresh[out_cols].sort_values('bloom_prob', ascending=False) \
        .to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {OUTPUT_PATH}")

    print(f"\nStations scored: {len(fresh)}   "
          f"stale (> {a.max_stale}d, skipped): {len(stale)}")
    print(f"Alerts at t*={a.t_star}: {int(fresh['alert'].sum())}")
    top = fresh.nlargest(min(8, len(fresh)), 'bloom_prob')[out_cols]
    print("\nTop stations by exceedance probability:")
    print(top.to_string(index=False))
    if len(stale):
        print(f"\nStale stations (no visit within {a.max_stale}d): "
              + ", ".join(sorted(stale['station_name'].astype(str))))


if __name__ == "__main__":
    main()