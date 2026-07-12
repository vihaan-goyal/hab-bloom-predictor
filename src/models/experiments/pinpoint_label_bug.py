"""
pinpoint_label_bug.py
---------------------
Localize why --clean-labels is a no-op. Runs the REAL build_dataset from
rolling_origin_cv.py both ways in one process and compares bloom_28d directly,
then repeats the label call on the merged df. Run from repo root:
    python pinpoint_label_bug.py

Reading the output:
  build_dataset identical: True  -> the harness build path is the no-op. Check
      whether the merged df carries a stale 'is_sustained' (the guard in
      build_forward_label then skips the fresh classify). Fix: drop is_sustained
      before the label call, or force a recompute.
  build_dataset identical: False -> build path is FINE. Then the two output CSVs
      were not actually different configs; cv_predictions.csv was a stale/
      already-sustained file. Regenerate both configs explicitly, no code bug.
"""
import sys, os, numpy as np, pandas as pd
sys.path.insert(0, os.path.join("src", "models"))
import rolling_origin_cv as roc
from label_utils import build_forward_label

raw = pd.read_csv("data/hab_features_tidal.csv", nrows=5)
for col in ("is_sustained", "is_exceedance", "bloom_28d"):
    print(f"CSV carries '{col}':", col in raw.columns)

print("\n-- exact harness path --")
df0, _ = roc.build_dataset(clean_labels=False)
df1, _ = roc.build_dataset(clean_labels=True)
print("build_dataset pos  orig:", int(df0['bloom_28d'].sum()),
      " sustained:", int(df1['bloom_28d'].sum()),
      " identical:", df0['bloom_28d'].equals(df1['bloom_28d']))

print("\n-- direct call on the merged df --")
d = df0.copy()
o = build_forward_label(d, horizon=28, threshold=10.0, sustained_only=False)
s = build_forward_label(d, horizon=28, threshold=10.0, sustained_only=True)
print("merged df carries is_sustained:", 'is_sustained' in d.columns)
print("orig:", int(np.nansum(o)), " sustained:", int(np.nansum(s)),
      " differ:", int((o.fillna(-1).values != s.fillna(-1).values).sum()))