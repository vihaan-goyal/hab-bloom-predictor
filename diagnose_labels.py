"""
diagnose_labels.py
------------------
Find WHY sustained_only=True produces the same labels as False.

Two candidate causes, each with a different fix:
  (A) classify_exceedances marks (nearly) every exceedance as sustained, so the
      sustained filter removes nothing. Most likely sub-cause: duplicate
      station-date rows, which put a same-date twin inside the +/- window and
      trivially satisfy the ">= 2 exceedances" test.
  (B) classify is fine and sustained is a real subset, but the 28-day forward
      window is wide enough that any window containing an exceedance also
      contains a sustained one, so the forward labels collapse to equal. This
      would resolve at a shorter horizon (21).

Run from repo root:
    python diagnose_labels.py
"""

import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join("src", "models"))
from label_utils import classify_exceedances, build_forward_label

PATH = "data/hab_features_tidal.csv"
THRESH = 10.0

df = pd.read_csv(PATH)
df["date"] = pd.to_datetime(df["date"])
print(f"rows: {len(df):,}")

# ---- duplication check (cause A sub-cause) ----
dup = df.duplicated(subset=["station_name", "date"]).sum()
n_pairs = df.drop_duplicates(subset=["station_name", "date"]).shape[0]
print(f"unique (station,date) pairs: {n_pairs:,}")
print(f"duplicate station-date rows: {dup:,}  "
      f"(inflation factor {len(df) / n_pairs:.2f}x)")
if dup > 0:
    ex = (df.groupby(["station_name", "date"]).size()
            .sort_values(ascending=False).head(3))
    print("  worst-duplicated station-dates:")
    for (s, d), c in ex.items():
        print(f"    {s} {pd.Timestamp(d).date()}  -> {c} rows")

# ---- classify: is sustained a real subset of exceedance? ----
c = classify_exceedances(df, threshold=THRESH)
n_exc = int(c["is_exceedance"].sum())
n_sus = int(c["is_sustained"].sum())
print(f"\nexceedance rows:  {n_exc:,}")
print(f"sustained rows:   {n_sus:,}")
if n_exc == 0:
    print("  no exceedances at all -> check threshold/column")
else:
    print(f"sustained / exceedance ratio: {n_sus / n_exc:.3f}  "
          f"({'TRIVIAL (cause A)' if n_sus == n_exc else 'real subset'})")

# same check but on de-duplicated data, to isolate the duplicate effect
c2 = classify_exceedances(df.drop_duplicates(subset=["station_name", "date"]),
                          threshold=THRESH)
n_exc2 = int(c2["is_exceedance"].sum())
n_sus2 = int(c2["is_sustained"].sum())
print(f"after de-dup -> exceedance: {n_exc2:,}  sustained: {n_sus2:,}  "
      f"ratio: {n_sus2 / n_exc2:.3f}" if n_exc2 else "after de-dup: no exc")

# ---- forward-label collapse check at h=28 vs h=21 ----
print("\nforward-label positives (any exceedance vs sustained-only):")
for h in (28, 21):
    orig = build_forward_label(df, horizon=h, threshold=THRESH,
                               sustained_only=False)
    sust = build_forward_label(df, horizon=h, threshold=THRESH,
                               sustained_only=True)
    diff = int((orig.fillna(-1).values != sust.fillna(-1).values).sum())
    print(f"  h={h:>2}d  orig_pos={int(np.nansum(orig)):>5}  "
          f"sust_pos={int(np.nansum(sust)):>5}  rows_differ={diff:>5}")

# ---- sampling cadence (context for cause B) ----
gaps = (df.sort_values(["station_name", "date"])
          .groupby("station_name")["date"].diff().dt.days.dropna())
if len(gaps):
    print(f"\nper-row sampling gap (days): median={gaps.median():.0f}  "
          f"p25={gaps.quantile(.25):.0f}  p75={gaps.quantile(.75):.0f}")

print("\nVERDICT:")
print("  If sustained==exceedance (ratio 1.000) and de-dup fixes it -> cause A,")
print("  fix classify_exceedances to ignore same-date twins.")
print("  If sustained is a real subset but rows_differ==0 at h=28 and >0 at")
print("  h=21 -> cause B, the 28d window collapses the difference; use h=21.")