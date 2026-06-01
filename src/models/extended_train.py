"""
extended_train.py
-----------------
Tests whether extending the training period improves precision.

Splits tested:
  Original:  train 1993-2019 | val 2020-2022 | test 2023-2025
  Extended:  train 1993-2021 | val 2022      | test 2023-2025

The extended split gives 2 more years of training data at the cost
of a smaller val set (1 year instead of 3).

Run from repo root:
    python src/models/extended_train.py
"""

import warnings
warnings.filterwarnings('ignore', category=UserWarning)

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_auc_score, average_precision_score,
    f1_score, precision_score, recall_score,
    precision_recall_curve,
)

print("Loading data/hab_features_daily.csv...")
df = pd.read_csv("data/hab_features_daily.csv")
df['date'] = pd.to_datetime(df['date'])

for n, min_p in [(3, 2), (6, 3), (9, 5)]:
    df[f'chl_roll{n}_mean'] = (
        df.groupby('station_name')['Chlorophyll']
          .transform(lambda x: x.rolling(n, min_periods=min_p).mean())
    )
df['chl_trend'] = (
    df.groupby('station_name')['Chlorophyll']
      .transform(lambda x: x.rolling(4, min_periods=3)
                 .apply(lambda v: np.polyfit(range(len(v)), v, 1)[0]))
)
df['bloom_28d'] = 0
for station, grp in df.groupby('station_name'):
    idx   = grp.index
    dates = grp['date'].values
    chl   = grp['Chlorophyll'].values
    labels = np.zeros(len(grp), dtype=int)
    for i in range(len(grp)):
        mask = (dates > dates[i]) & (dates <= dates[i] + np.timedelta64(28, 'D'))
        if mask.any() and (chl[mask] > 10).any():
            labels[i] = 1
    df.loc[idx, 'bloom_28d'] = labels

FEATURES_ALL = [
    'Chlorophyll', 'chl_lag1', 'chl_lag2', 'chl_lag3', 'chl_lag4',
    'chl_roll3_mean', 'chl_roll6_mean', 'chl_roll9_mean', 'chl_trend',
    'chl_anomaly', 'chl_climatology',
    'do_lag1', 'temp_lag1', 'sal_lag1',
    'sea_water_temperature', 'sea_water_salinity',
    'oxygen_concentration_in_sea_water',
    'month', 'latitude_x', 'longitude_x',
    'nox_lag2', 'dip_lag2', 'dip_change', 'dip_x_month',
    'neighbor_chl3_mean', 'neighbor_chl3_lag1',
]
FEATURES = [f for f in FEATURES_ALL if f in df.columns]

# ---------------------------------------------------------------------------
# Define both splits
# ---------------------------------------------------------------------------
splits = {
    'Original (train≤2019, val 2020-2022)': {
        'train': df[df['date'].dt.year <= 2019],
        'val':   df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)],
        'test':  df[df['date'].dt.year >= 2023],
    },
    'Extended (train≤2021, val 2022)': {
        'train': df[df['date'].dt.year <= 2021],
        'val':   df[df['date'].dt.year == 2022],
        'test':  df[df['date'].dt.year >= 2023],
    },
    'Extended+ (train≤2022, val 2022)': {
        'train': df[df['date'].dt.year <= 2022],
        'val':   df[df['date'].dt.year == 2022],
        'test':  df[df['date'].dt.year >= 2023],
    },
}

def prepare(split, features):
    rows = split[features + ['bloom_28d']].dropna(subset=['bloom_28d'])
    X = rows[features].copy().reset_index(drop=True)
    y = rows['bloom_28d'].copy().reset_index(drop=True)
    return X, y

def best_f1_thresh(y, p):
    prec, rec, thresh = precision_recall_curve(y, p)
    f1 = 2 * prec * rec / (prec + rec + 1e-9)
    idx = f1.argmax()
    return float(thresh[idx]) if idx < len(thresh) else 0.5

def eval_at(y, p, t):
    preds = (p >= t).astype(int)
    return {
        'auc':       roc_auc_score(y, p),
        'ap':        average_precision_score(y, p),
        'precision': precision_score(y, preds, zero_division=0),
        'recall':    recall_score(y, preds, zero_division=0),
        'f1':        f1_score(y, preds, zero_division=0),
        'tp': int(((preds==1)&(y==1)).sum()),
        'fp': int(((preds==1)&(y==0)).sum()),
        'fn': int(((preds==0)&(y==1)).sum()),
    }

# ---------------------------------------------------------------------------
# Train and evaluate each split
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("SPLIT COMPARISON — LR (class_weight=balanced)")
print("=" * 70)

results = {}
for name, sp in splits.items():
    X_tr, y_tr = prepare(sp['train'], FEATURES)
    X_v,  y_v  = prepare(sp['val'],   FEATURES)
    X_te, y_te = prepare(sp['test'],  FEATURES)
    MED = X_tr.median()

    sc = StandardScaler()
    lr = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
    lr.fit(sc.fit_transform(X_tr.fillna(MED)), y_tr)

    p_v  = lr.predict_proba(sc.transform(X_v.fillna(MED)))[:, 1]
    p_te = lr.predict_proba(sc.transform(X_te.fillna(MED)))[:, 1]

    t = best_f1_thresh(y_v, p_v)
    m = eval_at(y_te, p_te, t)
    m60 = eval_at(y_te, p_te, 0.60)

    results[name] = {'thresh': t, 'metrics': m, 'metrics_60': m60,
                     'train_size': len(X_tr), 'train_bloom': y_tr.mean(),
                     'val_size': len(X_v), 'test_size': len(X_te),
                     'test_bloom': y_te.mean()}

    print(f"\n{name}")
    print(f"  Train: {len(X_tr):,} ({y_tr.mean()*100:.1f}% bloom) | "
          f"Val: {len(X_v):,} ({y_v.mean()*100:.1f}%) | "
          f"Test: {len(X_te):,} ({y_te.mean()*100:.1f}%)")
    print(f"  Val best-F1 threshold: {t:.3f}")
    print(f"  Test AUC: {m['auc']:.4f}  AP: {m['ap']:.4f}")
    print(f"  At best-F1 thresh: precision={m['precision']:.3f}  "
          f"recall={m['recall']:.3f}  F1={m['f1']:.3f}  "
          f"TP={m['tp']}  FP={m['fp']}  FN={m['fn']}")
    print(f"  At threshold 0.60: precision={m60['precision']:.3f}  "
          f"recall={m60['recall']:.3f}  F1={m60['f1']:.3f}  "
          f"TP={m60['tp']}  FP={m60['fp']}  FN={m60['fn']}")

# ---------------------------------------------------------------------------
# Summary table
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("SUMMARY TABLE (at threshold 0.60)")
print("=" * 70)
print(f"{'Split':<45}  {'AUC':>6}  {'Prec':>6}  {'Rec':>6}  {'F1':>6}")
print("-" * 70)
for name, r in results.items():
    m = r['metrics_60']
    print(f"{name:<45}  {m['auc']:>6.3f}  {m['precision']:>6.3f}  "
          f"{m['recall']:>6.3f}  {m['f1']:>6.3f}")