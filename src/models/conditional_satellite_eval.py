"""
conditional_satellite_eval.py

Question: does the satellite stream help on the subset of days where the
satellite ACTUALLY observed the water (no clouds), rather than on the full
cloud-interpolated set?

If the hybrid still loses on clean-coverage days, the problem is not the cloud
gap -- it is the 4 km resolution being too coarse for the Sound. If the hybrid
WINS on clean days, you have found the precise condition under which satellite
data helps. Either outcome tightens the Discussion.

Run from repo root with the `hab` env active:
    conda activate hab
    python src/models/conditional_satellite_eval.py

Expects (same files your existing pipeline produces):
    data/hab_features_final.csv      -- in-situ features (for XGBoost)
    data/X_conv_sequences.npy        -- satellite patch sequences (N, T, H, W)
    data/y_conv_labels.npy           -- labels aligned to conv sequences
    data/conv_meta.csv               -- date, station for each conv sequence
    data/convlstm_model.pt           -- trained ConvLSTM weights (optional)

It does NOT retrain anything heavy. It (1) recomputes a satellite-coverage
score per conv sequence, (2) evaluates XGBoost on the conv-matched test rows,
(3) evaluates the hybrid/ConvLSTM probabilities on the same rows, (4) compares
the two models on low- vs high-coverage strata.
"""

import os
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score
from xgboost import XGBClassifier

DATA = "data"
PATCH_NAN_FILL = 0.0   # matches convlstm_model.py preprocessing

# ----------------------------------------------------------------------
# 1. Load the satellite sequences and compute a coverage score per sample
# ----------------------------------------------------------------------
# A sequence is (T, H, W). build_conv_sequences.py stores a real patch when
# the satellite observed that station-date and leaves it missing otherwise.
# Missing pixels arrive here as NaN (pre-normalization). The fraction of the
# 21-day window that carried a real, finite, non-zero observation is our
# coverage score. coverage = 1.0 means every day in the window was seen.

print("Loading satellite sequences...")
X_conv = np.load(os.path.join(DATA, "X_conv_sequences.npy"))   # (N, T, H, W)
y_conv = np.load(os.path.join(DATA, "y_conv_labels.npy"))
meta = pd.read_csv(os.path.join(DATA, "conv_meta.csv"))
meta["date"] = pd.to_datetime(meta["date"])

print(f"  X_conv shape: {X_conv.shape}")
N, T = X_conv.shape[0], X_conv.shape[1]

# A timestep counts as "observed" if its patch has any finite, non-zero pixel.
# (Cloud/missing days were filled with 0 or NaN.)
finite = np.isfinite(X_conv)
nonzero = np.abs(np.nan_to_num(X_conv, nan=0.0)) > 1e-9
observed_pixels = finite & nonzero                       # (N, T, H, W)
timestep_observed = observed_pixels.any(axis=(2, 3))     # (N, T) bool
coverage = timestep_observed.mean(axis=1)                # (N,) in [0, 1]

meta["coverage"] = coverage
meta["y"] = y_conv

print(f"  Coverage: mean={coverage.mean():.3f} "
      f"median={np.median(coverage):.3f} "
      f"max={coverage.max():.3f}")

# ----------------------------------------------------------------------
# 2. Get hybrid / ConvLSTM probabilities for the TEST period
# ----------------------------------------------------------------------
# Preferred: load saved test probabilities your training script wrote out.
# Fallback: re-run the trained ConvLSTM forward pass on the test split.

test_mask = meta["date"].dt.year >= 2023
test_meta = meta[test_mask].reset_index(drop=True)
test_pos = np.where(test_mask.values)[0]

conv_probs = None
saved = os.path.join(DATA, "convlstm_test_probs.npy")
saved_lab = os.path.join(DATA, "convlstm_test_labels.npy")
if os.path.exists(saved) and os.path.exists(saved_lab):
    cp = np.load(saved)
    cl = np.load(saved_lab)
    if len(cp) == len(test_pos):
        conv_probs = cp
        # sanity check labels line up
        if not np.allclose(cl, y_conv[test_pos]):
            print("  WARNING: saved labels do not match meta test labels; "
                  "re-running forward pass instead.")
            conv_probs = None

if conv_probs is None:
    print("Re-running ConvLSTM forward pass on test split...")
    import torch
    from convlstm_model import ConvLSTMHAB   # same dir import

    patch_size = X_conv.shape[2]
    Xn = np.nan_to_num(X_conv, nan=PATCH_NAN_FILL)
    Xn = (Xn - Xn.mean()) / (Xn.std() + 1e-8)
    X_test_t = torch.FloatTensor(Xn[test_pos])

    model = ConvLSTMHAB(patch_size=patch_size, hidden_channels=16)
    model.load_state_dict(torch.load(os.path.join(DATA, "convlstm_model.pt"),
                                     map_location="cpu"))
    model.eval()
    with torch.no_grad():
        logits = []
        for i in range(0, len(X_test_t), 64):
            logits.append(model(X_test_t[i:i + 64]).numpy())
        logits = np.concatenate(logits)
    conv_probs = 1.0 / (1.0 + np.exp(-logits))

test_meta["conv_prob"] = conv_probs

# ----------------------------------------------------------------------
# 3. XGBoost on the SAME test rows (matched by station + date)
# ----------------------------------------------------------------------
print("Training XGBoost on in-situ features...")
df = pd.read_csv(os.path.join(DATA, "hab_features_final.csv"), low_memory=False)
df["date"] = pd.to_datetime(df["date"])
df["bloom_7d_ahead"] = df.groupby("station_name")["bloom"].shift(-7)

features = [
    "latitude", "longitude", "month",
    "chl_anomaly", "chl_climatology",
    "chl_roll7_mean", "chl_roll7_std",
    "chl_lag3", "chl_lag7", "chl_lag14", "chl_lag21",
]

train = df[df["date"].dt.year <= 2019].copy()
Xtr = train[features + ["bloom_7d_ahead"]].dropna()
ytr = Xtr.pop("bloom_7d_ahead")
spw = (ytr == 0).sum() / (ytr == 1).sum()

xgb = XGBClassifier(
    n_estimators=200, max_depth=6, learning_rate=0.1,
    scale_pos_weight=spw, random_state=42, n_jobs=-1,
    eval_metric="logloss", verbosity=0,
)
xgb.fit(Xtr.values, ytr.values)

# Build XGBoost predictions for the exact (station, date) rows in test_meta
df_key = df.set_index(["station_name", "date"])
rows = []
keep = []
for i, r in test_meta.iterrows():
    key = (r["station"], r["date"])
    if key in df_key.index:
        rec = df_key.loc[key]
        if isinstance(rec, pd.DataFrame):
            rec = rec.iloc[0]
        feat = rec[features]
        if feat.notna().all():
            rows.append(feat.values.astype(float))
            keep.append(i)

keep = np.array(keep)
test_eval = test_meta.loc[keep].reset_index(drop=True)
xgb_probs = xgb.predict_proba(np.array(rows))[:, 1]
test_eval["xgb_prob"] = xgb_probs

print(f"  Matched {len(test_eval)} of {len(test_meta)} test rows to in-situ features")

# ----------------------------------------------------------------------
# 4. Compare on low- vs high-coverage strata
# ----------------------------------------------------------------------
def safe_auc(y, p):
    y = np.asarray(y)
    if len(np.unique(y)) < 2:
        return float("nan")
    return roc_auc_score(y, p)

def report(name, sub):
    y = sub["y"].values
    print(f"\n{name}  (n={len(sub)}, blooms={int(y.sum())}, "
          f"bloom_rate={y.mean()*100:.1f}%)")
    a_x = safe_auc(y, sub["xgb_prob"].values)
    a_c = safe_auc(y, sub["conv_prob"].values)
    ap_x = average_precision_score(y, sub["xgb_prob"].values) if len(np.unique(y)) > 1 else float("nan")
    ap_c = average_precision_score(y, sub["conv_prob"].values) if len(np.unique(y)) > 1 else float("nan")
    print(f"  XGBoost  AUC={a_x:.4f}  AP={ap_x:.4f}")
    print(f"  ConvLSTM AUC={a_c:.4f}  AP={ap_c:.4f}")
    print(f"  delta (ConvLSTM - XGBoost) AUC = {a_c - a_x:+.4f}")
    return a_x, a_c

print("\n" + "=" * 60)
print("CONDITIONAL EVALUATION BY SATELLITE COVERAGE")
print("=" * 60)

report("ALL test rows", test_eval)

# Stratify. Adjust the cut to taste; 0.5 = "at least half the 21-day window seen".
for cut in [0.25, 0.5, 0.75, 1.0]:
    hi = test_eval[test_eval["coverage"] >= cut]
    if len(hi) >= 30 and hi["y"].nunique() > 1:
        report(f"coverage >= {cut:.2f}", hi)
    else:
        print(f"\ncoverage >= {cut:.2f}: too few rows / one class "
              f"(n={len(hi)}) -- skipped")

lo = test_eval[test_eval["coverage"] < 0.5]
if len(lo) >= 30 and lo["y"].nunique() > 1:
    report("coverage < 0.50 (cloud-heavy)", lo)

# ----------------------------------------------------------------------
# 5. Save a tidy table for the paper
# ----------------------------------------------------------------------
out = []
for cut in [0.0, 0.25, 0.5, 0.75, 1.0]:
    sub = test_eval[test_eval["coverage"] >= cut]
    if len(sub) < 30 or sub["y"].nunique() < 2:
        continue
    out.append({
        "coverage_threshold": cut,
        "n": len(sub),
        "bloom_rate": round(sub["y"].mean(), 4),
        "xgb_auc": round(safe_auc(sub["y"], sub["xgb_prob"]), 4),
        "conv_auc": round(safe_auc(sub["y"], sub["conv_prob"]), 4),
    })
res = pd.DataFrame(out)
res["delta"] = (res["conv_auc"] - res["xgb_auc"]).round(4)
res.to_csv(os.path.join(DATA, "conditional_satellite_eval.csv"), index=False)
print("\nSaved data/conditional_satellite_eval.csv")
print(res.to_string(index=False))

print("""
INTERPRETATION
  If conv_auc stays below xgb_auc even at coverage_threshold = 1.0,
  the cloud gap is NOT the main problem -- 4 km resolution is too coarse
  for a 34 km-wide estuary. That is your Discussion headline.

  If conv_auc rises toward (or past) xgb_auc as coverage increases,
  you have isolated the condition where satellite data earns its place,
  which is an even stronger, more nuanced result.
""")