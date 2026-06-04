r"""
strict_label.py
---------------
Experiment: retrain the LR pipeline with stricter bloom-label definitions
(CHL > 10, > 15, > 20 ug/L over the next 28 days) to test whether predicting
rarer, more serious blooms improves precision.

Hypothesis: at the 10 ug/L cutoff many "blooms" are marginal chlorophyll
elevations that look like blooms in the 1993-2019 training era but not in the
post-TMDL 2023-2025 test era. A stricter cutoff predicts only serious blooms,
which may be more consistently predictable across the distribution shift.

This is an EXPERIMENT ONLY -- it does not touch any pipeline file.

Run from repo root (takes a few minutes due to label recomputation):
    & "$env:USERPROFILE\anaconda3\python.exe" src/models/strict_label.py
"""

import warnings
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=RuntimeWarning)

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_auc_score, f1_score, precision_score, recall_score,
)

CHL_THRESHOLDS = [10, 15, 20]
FIXED_THRESH = 0.60

# ---------------------------------------------------------------------------
# 1. Load + defensive sal_lag merge
# ---------------------------------------------------------------------------
print("Loading data/hab_features_tidal.csv...")
df = pd.read_csv('data/hab_features_tidal.csv')
df['date'] = pd.to_datetime(df['date'])

daily = pd.read_csv('data/hab_features_daily.csv')[
    ['date', 'station_name', 'sal_lag2', 'sal_lag3', 'sal_lag4']
]
daily['date'] = pd.to_datetime(daily['date'])

# Only merge columns genuinely absent -- merging present columns would create
# _x/_y suffixes and silently drop them from the feature set.
for col in ['sal_lag2', 'sal_lag3', 'sal_lag4']:
    if col not in df.columns:
        df = df.merge(daily[['date', 'station_name', col]],
                      on=['date', 'station_name'], how='left')

# ---------------------------------------------------------------------------
# 2. Recompute rolling means + chl_trend (identical to all pipeline scripts)
# ---------------------------------------------------------------------------
for n, min_p in [(3, 2), (6, 3), (9, 5), (14, 7), (21, 10)]:
    df[f'chl_roll{n}_mean'] = (
        df.groupby('station_name')['Chlorophyll']
          .transform(lambda x: x.rolling(n, min_periods=min_p).mean())
    )

df['chl_trend'] = (
    df.groupby('station_name')['Chlorophyll']
      .transform(lambda x: x.rolling(4, min_periods=3)
                 .apply(lambda v: np.polyfit(range(len(v)), v, 1)[0]))
)

# ---------------------------------------------------------------------------
# 3. Feature set (identical to pipeline)
# ---------------------------------------------------------------------------
FEATURES_ALL = [
    'Chlorophyll', 'chl_lag1', 'chl_lag2', 'chl_lag3', 'chl_lag4',
    'chl_roll3_mean', 'chl_roll6_mean', 'chl_roll9_mean', 'chl_trend',
    'chl_roll14_mean', 'chl_roll21_mean',
    'chl_anomaly', 'chl_climatology',
    'do_lag1', 'temp_lag1', 'sal_lag1', 'sal_lag2', 'sal_lag3', 'sal_lag4',
    'sea_water_temperature', 'sea_water_salinity',
    'oxygen_concentration_in_sea_water',
    'month', 'latitude_x', 'longitude_x',
    'nox_lag2', 'dip_lag2', 'dip_change', 'dip_x_month',
    'neighbor_chl3_mean', 'neighbor_chl3_lag1',
    'tidal_gt_anom', 'tidal_msl_anom',
]
FEATURES = [f for f in FEATURES_ALL if f in df.columns]
missing = [f for f in FEATURES_ALL if f not in df.columns]
if missing:
    print(f"  WARNING: features absent, dropped: {missing}")

# ---------------------------------------------------------------------------
# 4. Bloom-label computation (forward-looking 28-day window)
# ---------------------------------------------------------------------------
def compute_bloom_label(df, chl_threshold):
    df = df.copy()
    col = f'bloom_28d_{chl_threshold}'
    df[col] = 0
    for station, grp in df.groupby('station_name'):
        idx = grp.index
        dates = grp['date'].values
        chl = grp['Chlorophyll'].values
        labels = np.zeros(len(grp), dtype=int)
        for i in range(len(grp)):
            mask = (dates > dates[i]) & \
                   (dates <= dates[i] + np.timedelta64(28, 'D'))
            if mask.any() and (chl[mask] > chl_threshold).any():
                labels[i] = 1
        df.loc[idx, col] = labels
    return df


print("Computing bloom labels for CHL thresholds 10, 15, 20...")
for thr in CHL_THRESHOLDS:
    df = compute_bloom_label(df, thr)

# ---------------------------------------------------------------------------
# 5. Splits (same as pipeline)
# ---------------------------------------------------------------------------
train = df[df['date'].dt.year <= 2019]
val   = df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)]
test  = df[df['date'].dt.year >= 2023]


def prepare(split, label_col):
    rows = split[FEATURES + [label_col]].dropna(subset=[label_col])
    X = rows[FEATURES].copy().reset_index(drop=True)
    y = rows[label_col].copy().reset_index(drop=True)
    return X, y


def best_f1_threshold(y, p):
    if y.nunique() < 2:
        return FIXED_THRESH
    grid = np.arange(0.05, 0.951, 0.01)
    best_t, best_f1 = FIXED_THRESH, -1.0
    for t in grid:
        f1 = f1_score(y, (p >= t).astype(int), zero_division=0)
        if f1 > best_f1:
            best_f1, best_t = f1, float(t)
    return best_t


def eval_at(y, p, t):
    preds = (p >= t).astype(int)
    return {
        'precision': precision_score(y, preds, zero_division=0),
        'recall':    recall_score(y, preds, zero_division=0),
        'f1':        f1_score(y, preds, zero_division=0),
        'tp': int(((preds == 1) & (y == 1)).sum()),
        'fp': int(((preds == 1) & (y == 0)).sum()),
        'fn': int(((preds == 0) & (y == 1)).sum()),
    }

# ---------------------------------------------------------------------------
# 6. Label statistics
# ---------------------------------------------------------------------------
print("\n" + "=" * 78)
print("LABEL STATISTICS  (forward-looking 28-day bloom rate by split)")
print("=" * 78)
print(f"{'Threshold':>9}  {'Train_rate':>10}  {'Val_rate':>9}  {'Test_rate':>9}  "
      f"{'Train_pos':>9}  {'Val_pos':>7}  {'Test_pos':>8}")
print("-" * 78)

label_stats = {}
for thr in CHL_THRESHOLDS:
    col = f'bloom_28d_{thr}'
    _, ytr = prepare(train, col)
    _, yv  = prepare(val,   col)
    _, yte = prepare(test,  col)
    label_stats[thr] = (ytr, yv, yte)
    print(f"{thr:>9}  {ytr.mean()*100:>9.1f}%  {yv.mean()*100:>8.1f}%  "
          f"{yte.mean()*100:>8.1f}%  {int(ytr.sum()):>9}  {int(yv.sum()):>7}  "
          f"{int(yte.sum()):>8}")

# ---------------------------------------------------------------------------
# 7. Train + evaluate per label
# ---------------------------------------------------------------------------
results = {}
for thr in CHL_THRESHOLDS:
    col = f'bloom_28d_{thr}'
    X_tr, y_tr = prepare(train, col)
    X_v,  y_v  = prepare(val,   col)
    X_te, y_te = prepare(test,  col)
    MED = X_tr.median()

    scaler = StandardScaler()
    lr = LogisticRegression(C=0.05, class_weight='balanced',
                            max_iter=2000, random_state=42)
    lr.fit(scaler.fit_transform(X_tr.fillna(MED)), y_tr)
    p_v  = lr.predict_proba(scaler.transform(X_v.fillna(MED)))[:, 1]
    p_te = lr.predict_proba(scaler.transform(X_te.fillna(MED)))[:, 1]

    t_best = best_f1_threshold(y_v, p_v)
    auc = roc_auc_score(y_te, p_te) if y_te.nunique() >= 2 else float('nan')
    results[thr] = {
        't_best': t_best,
        'auc': auc,
        'at_best': eval_at(y_te, p_te, t_best),
        'at_60':   eval_at(y_te, p_te, FIXED_THRESH),
    }

# ---------------------------------------------------------------------------
# 8. Results table -- fixed 0.60 threshold
# ---------------------------------------------------------------------------
print("\n" + "=" * 78)
print("RESULTS AT FIXED 0.60 THRESHOLD  (test set 2023-2025)")
print("=" * 78)
print(f"{'Label':>7}  {'Val_thr':>7}  {'AUC':>6}  {'Prec@.60':>8}  {'Rec@.60':>7}  "
      f"{'F1@.60':>6}  {'TP':>3}  {'FP':>3}  {'FN':>3}")
print("-" * 78)
for thr in CHL_THRESHOLDS:
    r = results[thr]; m = r['at_60']
    marker = "  <-- baseline" if thr == 10 else ""
    print(f"{'CHL>'+str(thr):>7}  {r['t_best']:>7.2f}  {r['auc']:>6.3f}  "
          f"{m['precision']:>8.3f}  {m['recall']:>7.3f}  {m['f1']:>6.3f}  "
          f"{m['tp']:>3}  {m['fp']:>3}  {m['fn']:>3}{marker}")

# ---------------------------------------------------------------------------
# 9. Results table -- at each label's best-F1 val threshold
# ---------------------------------------------------------------------------
print("\n" + "=" * 78)
print("RESULTS AT EACH LABEL'S BEST-F1 VAL THRESHOLD  (test set 2023-2025)")
print("=" * 78)
print(f"{'Label':>7}  {'Val_thr':>7}  {'AUC':>6}  {'Prec':>6}  {'Rec':>6}  "
      f"{'F1':>6}  {'TP':>3}  {'FP':>3}  {'FN':>3}")
print("-" * 78)
for thr in CHL_THRESHOLDS:
    r = results[thr]; m = r['at_best']
    print(f"{'CHL>'+str(thr):>7}  {r['t_best']:>7.2f}  {r['auc']:>6.3f}  "
          f"{m['precision']:>6.3f}  {m['recall']:>6.3f}  {m['f1']:>6.3f}  "
          f"{m['tp']:>3}  {m['fp']:>3}  {m['fn']:>3}")

# ---------------------------------------------------------------------------
# 10. Comparability note + verdict
# ---------------------------------------------------------------------------
print("\n" + "=" * 78)
print("COMPARABILITY NOTE")
print("=" * 78)
print(
    "  A 'positive' means a DIFFERENT thing at each threshold:\n"
    "    CHL>10 positives include marginal elevations; CHL>20 positives are a\n"
    "    strict SUBSET (only serious blooms). The CHL>20 test set therefore has\n"
    "    far fewer positives, so TP/FP/FN counts are NOT directly comparable --\n"
    "    each label is a different (and progressively harder/rarer) problem.\n"
    "  The fairest cross-threshold metric is PRECISION: the fraction of alerts\n"
    "    that are real blooms, i.e. the false-alarm rate, which is meaningful\n"
    "    regardless of how 'bloom' is defined."
)

base_p = results[10]['at_60']['precision']
print("\n  Precision @0.60 by label (vs CHL>10 baseline):")
for thr in CHL_THRESHOLDS:
    p = results[thr]['at_60']['precision']
    tag = " (baseline)" if thr == 10 else f"  d={p - base_p:+.3f}"
    print(f"    CHL>{thr}: {p:.3f}{tag}")

# ---------------------------------------------------------------------------
# 11. Baseline validation
# ---------------------------------------------------------------------------
print("\n" + "=" * 78)
print("BASELINE VALIDATION (CHL>10 @0.60)")
print("=" * 78)
b = results[10]['at_60']
ok = (abs(b['precision'] - 0.446) < 0.01 and
      abs(b['recall'] - 0.446) < 0.01 and
      abs(b['f1'] - 0.446) < 0.01)
print(f"  Expected: Prec=0.446 Rec=0.446 F1=0.446  (TP=33 FP=41 FN=41)")
print(f"  Got:      Prec={b['precision']:.3f} Rec={b['recall']:.3f} "
      f"F1={b['f1']:.3f}  (TP={b['tp']} FP={b['fp']} FN={b['fn']})")
print(f"  {'PASS' if ok else 'WARNING: baseline drift -- investigate'}")
