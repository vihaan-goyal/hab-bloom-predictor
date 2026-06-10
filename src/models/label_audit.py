"""
label_audit.py
--------------
Audits the bloom label before trusting any metric built on it.

Two questions:
  1. What fraction of Chlorophyll exceedances (> 10 ug/L) are single-sample spikes
     rather than sustained blooms, overall and per year? A high single-sample rate
     in a given year means the forward label for that year is partly noise, which
     caps AUC there no matter what the model does.
  2. How many forward 28-day positives flip from positive to negative if a bloom
     must be SUSTAINED? Those flipped rows are the unrankable targets currently
     dragging the metric down.

Reuses build_dataset() from rolling_origin_cv so the data is identical.

Run from repo root:
    python src/models/label_audit.py
    python src/models/label_audit.py --sustain-window 10
"""

import argparse
import numpy as np
import pandas as pd

from rolling_origin_cv import build_dataset
from label_utils import classify_exceedances, build_forward_label


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--threshold", type=float, default=10.0)
    ap.add_argument("--horizon", type=int, default=28)
    ap.add_argument("--sustain-window", type=int, default=14,
                    help="days within which a second exceedance counts as sustained")
    ap.add_argument("--first-year", type=int, default=2015,
                    help="restrict per-year tables to the post-TMDL regime")
    args = ap.parse_args()

    df, _ = build_dataset()
    df = df.dropna(subset=['Chlorophyll']).copy()
    df['year'] = df['date'].dt.year

    # ---- exceedance classification ----
    df = classify_exceedances(df, args.threshold, args.sustain_window)
    df['year'] = df['date'].dt.year  # re-add after sort/copy

    exc = df[df['is_exceedance'] == 1]
    n_exc = len(exc)
    n_single = int((exc['is_sustained'] == 0).sum())
    print("=" * 64)
    print("EXCEEDANCE AUDIT  (Chlorophyll > {:.0f} ug/L)".format(args.threshold))
    print("=" * 64)
    print(f"  total exceedance readings: {n_exc:,}")
    print(f"  single-sample (isolated):  {n_single:,}  "
          f"({100 * n_single / n_exc:.1f}%)")
    print(f"  sustained:                 {n_exc - n_single:,}  "
          f"({100 * (n_exc - n_single) / n_exc:.1f}%)")

    print("\n  Per year (post-{}):".format(args.first_year))
    print(f"  {'year':>5}  {'exc':>5}  {'single':>6}  {'single%':>7}")
    print("  " + "-" * 30)
    for y, g in exc[exc['year'] >= args.first_year].groupby('year'):
        ns = int((g['is_sustained'] == 0).sum())
        pct = 100 * ns / len(g) if len(g) else 0
        print(f"  {y:>5}  {len(g):>5}  {ns:>6}  {pct:>6.1f}%")

    # ---- sampling cadence (tests the confound hypothesis) ----
    cad = df.dropna(subset=['Chlorophyll']).sort_values(['station_name', 'date']).copy()
    cad['gap'] = cad.groupby('station_name')['date'].diff().dt.days
    cad['year'] = cad['date'].dt.year
    print("\n" + "=" * 64)
    print("SAMPLING CADENCE  (median days between consecutive samples)")
    print("=" * 64)
    print("  If high single-sample years line up with large gaps, the 'noise'")
    print("  is a sampling artifact, not a label-quality problem.")
    print(f"  {'year':>5}  {'median_gap':>10}  {'p90_gap':>8}  {'n_samples':>9}")
    print("  " + "-" * 40)
    for y, g in cad[cad['year'] >= args.first_year].groupby('year'):
        gaps = g['gap'].dropna()
        med = gaps.median() if len(gaps) else float('nan')
        p90 = gaps.quantile(0.90) if len(gaps) else float('nan')
        print(f"  {y:>5}  {med:>10.1f}  {p90:>8.1f}  {len(g):>9,}")

    # ---- forward label comparison ----
    orig = build_forward_label(df, args.horizon, args.threshold,
                               sustained_only=False)
    clean = build_forward_label(df, args.horizon, args.threshold,
                                sustained_only=True,
                                sustain_window=args.sustain_window)
    df['label_orig'] = orig
    df['label_clean'] = clean

    sub = df[df['year'] >= args.first_year]
    n_orig = int(sub['label_orig'].sum())
    n_clean = int(sub['label_clean'].sum())
    flipped = int(((sub['label_orig'] == 1) & (sub['label_clean'] == 0)).sum())

    print("\n" + "=" * 64)
    print(f"FORWARD {args.horizon}-DAY LABEL  (post-{args.first_year})")
    print("=" * 64)
    print(f"  positives (original): {n_orig:,}")
    print(f"  positives (cleaned):  {n_clean:,}")
    print(f"  flipped to negative:  {flipped:,}  "
          f"({100 * flipped / n_orig:.1f}% of original positives)")

    print("\n  Per year (positives original -> cleaned, flipped):")
    print(f"  {'year':>5}  {'orig':>5}  {'clean':>5}  {'flip':>5}  {'flip%':>6}")
    print("  " + "-" * 36)
    for y, g in sub.groupby('year'):
        o = int(g['label_orig'].sum())
        c = int(g['label_clean'].sum())
        fl = int(((g['label_orig'] == 1) & (g['label_clean'] == 0)).sum())
        pct = 100 * fl / o if o else 0
        print(f"  {y:>5}  {o:>5}  {c:>5}  {fl:>5}  {pct:>5.1f}%")

    print("\nInterpretation:")
    print("  Years with high flip% are where the original label was noisiest.")
    print("  Cross-reference with the per-year AUC from rolling_origin_cv: if the")
    print("  low-AUC years (e.g. 2023) are also high-flip, cleaning the label should")
    print("  raise pooled AUC. Rerun the harness with --clean-labels to confirm.")


if __name__ == "__main__":
    main()