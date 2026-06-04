"""
retrain_with_tidal.py
---------------------
Retrains LR with tidal features added and compares to baseline.
Run AFTER add_tidal_features.py has created data/hab_features_tidal.csv.

Run from repo root:
    python src/models/retrain_with_tidal.py
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

print("Loading data/hab_features_tidal.csv...")
df = pd.read_csv('data/hab_features_tidal.csv')
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

BASE_FEATURES = [
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

TIDAL_FEATURES = ['tidal_gt_anom', 'tidal_msl_anom']

BASE_FEATURES   = [f for f in BASE_FEATURES  if f in df.columns]
TIDAL_FEATURES  = [f for f in TIDAL_FEATURES if f in df.columns]
AUGMENTED       = BASE_FEATURES + TIDAL_FEATURES

print(f"Base features:   {len(BASE_FEATURES)}")
print(f"Tidal features:  {len(TIDAL_FEATURES)} -- {TIDAL_FEATURES}")
print(f"Augmented:       {len(AUGMENTED)}")

# Extended+ split
train = df[df['date'].dt.year <= 2019]
val   = df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)]
test  = df[df['date'].dt.year >= 2023]

def prepare(split, features):
    rows = split[features + ['bloom_28d']].dropna(subset=['bloom_28d'])
    X = rows[features].copy().reset_index(drop=True)
    y = rows['bloom_28d'].copy().reset_index(drop=True)
    return X, y

X_train_b, y_train_b = prepare(train, BASE_FEATURES)
X_val_b,   y_val_b   = prepare(val,   BASE_FEATURES)
X_test_b,  y_test_b  = prepare(test,  BASE_FEATURES)

X_train_t, y_train_t = prepare(train, AUGMENTED)
X_val_t,   y_val_t   = prepare(val,   AUGMENTED)
X_test_t,  y_test_t  = prepare(test,  AUGMENTED)

MED_b = X_train_b.median()
MED_t = X_train_t.median()

print(f"\nBase   -- Train: {len(X_train_b):,} | Val: {len(X_val_b):,} | Test: {len(X_test_b):,}")
print(f"Tidal  -- Train: {len(X_train_t):,} | Val: {len(X_val_t):,} | Test: {len(X_test_t):,}")

def fit_lr(X_tr, y_tr, X_v, X_te, MED):
    sc = StandardScaler()
    lr = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
    lr.fit(sc.fit_transform(X_tr.fillna(MED)), y_tr)
    p_v  = lr.predict_proba(sc.transform(X_v.fillna(MED)))[:, 1]
    p_te = lr.predict_proba(sc.transform(X_te.fillna(MED)))[:, 1]
    return p_v, p_te, lr, sc

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

print("\nFitting baseline LR...")
p_val_b, p_test_b, lr_b, _ = fit_lr(X_train_b, y_train_b,
                                      X_val_b, X_test_b, MED_b)

print("Fitting tidal-augmented LR...")
p_val_t, p_test_t, lr_t, _ = fit_lr(X_train_t, y_train_t,
                                      X_val_t, X_test_t, MED_t)

t_b = best_f1_thresh(y_val_b, p_val_b)
t_t = best_f1_thresh(y_val_t, p_val_t)

m_b    = eval_at(y_test_b, p_test_b, t_b)
m_t    = eval_at(y_test_t, p_test_t, t_t)
m_b_60 = eval_at(y_test_b, p_test_b, 0.60)
m_t_60 = eval_at(y_test_t, p_test_t, 0.60)

print("\n" + "=" * 60)
print("TEST SET COMPARISON (2023-2025)")
print("=" * 60)
print(f"\n{'Metric':<12}  {'Baseline':>10}  {'+ Tidal':>10}  {'Delta':>8}")
print("-" * 45)
for k in ['auc', 'ap', 'precision', 'recall', 'f1']:
    delta = m_t[k] - m_b[k]
    marker = " <--" if k == 'precision' else ""
    print(f"{k:<12}  {m_b[k]:>10.4f}  {m_t[k]:>10.4f}  {delta:>+8.4f}{marker}")
print(f"\nBase threshold (val): {t_b:.3f}  |  Tidal threshold (val): {t_t:.3f}")

print(f"\n-- At fixed threshold 0.60 --")
print(f"{'Metric':<12}  {'Baseline':>10}  {'+ Tidal':>10}  {'Delta':>8}")
print("-" * 45)
for k in ['precision', 'recall', 'f1']:
    delta = m_t_60[k] - m_b_60[k]
    marker = " <--" if k == 'precision' else ""
    print(f"{k:<12}  {m_b_60[k]:>10.4f}  {m_t_60[k]:>10.4f}  {delta:>+8.4f}{marker}")
print(f"Baseline: TP={m_b_60['tp']}  FP={m_b_60['fp']}  FN={m_b_60['fn']}")
print(f"+ Tidal:  TP={m_t_60['tp']}  FP={m_t_60['fp']}  FN={m_t_60['fn']}")

print("\n-- Tidal feature coefficients --")
coef_df = pd.Series(lr_t.coef_[0], index=AUGMENTED)
for f in TIDAL_FEATURES:
    if f in coef_df:
        direction = ("stronger mixing = fewer blooms (good)"
                     if coef_df[f] < 0 else "increases bloom prob")
        print(f"  {f:<22} coef={coef_df[f]:>+8.4f}  ({direction})")

print("\n" + "=" * 60)
print("VERDICT")
print("=" * 60)
delta_prec = m_t_60['precision'] - m_b_60['precision']
if delta_prec > 0.02:
    print(f"  Tidal features HELP: +{delta_prec:.3f} precision at threshold 0.60")
    print("  --> Integrate tidal features into main pipeline")
elif delta_prec > 0:
    print(f"  Tidal features marginally help: +{delta_prec:.3f} precision")
    print("  --> Borderline -- check AUC before adding complexity")
else:
    print(f"  Tidal features do NOT help: {delta_prec:.3f} precision delta")
    print("  --> Precision ceiling confirmed. Move to paper.")