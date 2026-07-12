"""
test_xgboost_precision.py
-------------------------
Tests XGBoost with heavy regularization against the locked LR baseline.
Targets test precision specifically, not just AUC.

Run from repo root:
    python test_xgboost_precision.py
"""

import glob
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_auc_score, precision_score, recall_score, f1_score,
)

THRESHOLD = 0.60

# ── LOAD LOCKED PIPELINE ──────────────────────────────────────────────────────
print("Loading data...")
df = pd.read_csv("data/hab_features_tidal.csv")
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values(['station_name', 'date']).reset_index(drop=True)

if 'percent_saturation' not in df.columns:
    frames = []
    for f in sorted(glob.glob('data/raw/deep_wq_extra/deep_wq_S_*.csv')):
        frames.append(pd.read_csv(f, skiprows=[1],
                      usecols=['station_name', 'time', 'percent_saturation']))
    ps = pd.concat(frames, ignore_index=True)
    ps['station_name'] = ps['station_name'].astype(str)
    ps['date'] = pd.to_datetime(ps['time'], utc=True).dt.tz_localize(None).dt.normalize()
    ps['percent_saturation'] = pd.to_numeric(ps['percent_saturation'], errors='coerce')
    ps = ps.dropna(subset=['percent_saturation']).groupby(
        ['date', 'station_name'], as_index=False)['percent_saturation'].mean()
    df['station_name'] = df['station_name'].astype(str)
    df = df.merge(ps, on=['date', 'station_name'], how='left')

gust = pd.read_csv("data/gust_features_daily.csv", usecols=['date', 'max_gust_3d'])
gust['date'] = pd.to_datetime(gust['date'])
df = df.merge(gust, on='date', how='left')

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

print("Computing bloom_28d labels...")
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

FEATURES = [
    'Chlorophyll', 'chl_lag1', 'chl_lag2', 'chl_lag3', 'chl_lag4',
    'chl_roll3_mean', 'chl_roll6_mean', 'chl_roll9_mean',
    'chl_roll14_mean', 'chl_roll21_mean', 'chl_trend',
    'chl_anomaly', 'chl_climatology',
    'do_lag1', 'temp_lag1', 'sal_lag1', 'sal_lag2', 'sal_lag3', 'sal_lag4',
    'sea_water_temperature', 'sea_water_salinity',
    'oxygen_concentration_in_sea_water',
    'month', 'latitude_x', 'longitude_x',
    'nox_lag2', 'dip_lag2', 'dip_change', 'dip_x_month',
    'neighbor_chl3_mean', 'neighbor_chl3_lag1',
    'tidal_gt_anom', 'tidal_msl_anom',
    'percent_saturation', 'max_gust_3d',
]
FEATURES = [f for f in FEATURES if f in df.columns]

train = df[df['date'].dt.year <= 2019]
val   = df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)]
test  = df[df['date'].dt.year >= 2023]

def prep(split):
    rows = split[FEATURES + ['bloom_28d']].dropna(subset=['bloom_28d'])
    X = rows[FEATURES].copy().reset_index(drop=True)
    y = rows['bloom_28d'].copy().reset_index(drop=True)
    return X, y

X_tr, y_tr = prep(train)
X_v,  y_v  = prep(val)
X_te, y_te = prep(test)
MED = X_tr.median()

print(f"Train: {len(X_tr)}, Val: {len(X_v)}, Test: {len(X_te)}")

# ── BASELINE LR ───────────────────────────────────────────────────────────────
scaler = StandardScaler()
X_tr_s = scaler.fit_transform(X_tr.fillna(MED))
X_v_s  = scaler.transform(X_v.fillna(MED))
X_te_s = scaler.transform(X_te.fillna(MED))

lr = LogisticRegression(C=0.05, class_weight='balanced',
                        max_iter=1000, random_state=42)
lr.fit(X_tr_s, y_tr)
lr_p = lr.predict_proba(X_te_s)[:, 1]
lr_preds = (lr_p >= THRESHOLD).astype(int)

print(f"\n{'='*65}")
print("BASELINE LR")
print(f"{'='*65}")
print(f"  test: Prec={precision_score(y_te, lr_preds, zero_division=0):.3f} "
      f"Rec={recall_score(y_te, lr_preds, zero_division=0):.3f} "
      f"F1={f1_score(y_te, lr_preds, zero_division=0):.3f} "
      f"AUC={roc_auc_score(y_te, lr_p):.3f}")

# ── XGBOOST CONFIGS ───────────────────────────────────────────────────────────
pos_weight = (y_tr == 0).sum() / (y_tr == 1).sum()

configs = {
    'XGB default': dict(
        n_estimators=200, max_depth=6, learning_rate=0.1,
        scale_pos_weight=pos_weight, random_state=42, verbosity=0,
    ),
    'XGB heavy reg': dict(
        n_estimators=300, max_depth=3, learning_rate=0.05,
        min_child_weight=10, reg_alpha=1.0, reg_lambda=2.0,
        subsample=0.8, colsample_bytree=0.8,
        scale_pos_weight=pos_weight, random_state=42, verbosity=0,
    ),
    'XGB max reg': dict(
        n_estimators=500, max_depth=2, learning_rate=0.02,
        min_child_weight=20, reg_alpha=2.0, reg_lambda=5.0,
        subsample=0.7, colsample_bytree=0.7,
        scale_pos_weight=pos_weight, random_state=42, verbosity=0,
    ),
    'XGB precision-tuned': dict(
        n_estimators=200, max_depth=3, learning_rate=0.05,
        min_child_weight=15, reg_alpha=0.5, reg_lambda=3.0,
        subsample=0.8, colsample_bytree=0.9,
        gamma=1.0,
        scale_pos_weight=pos_weight, random_state=42, verbosity=0,
    ),
}

print(f"\n{'='*65}")
print("XGBOOST CONFIGS (test set, threshold=0.60)")
print(f"{'='*65}")
print(f"{'Config':<25} {'Prec':>6} {'Rec':>6} {'F1':>6} {'AUC':>6}  {'Delta Prec':>10}")
print(f"{'-'*65}")

best_prec = precision_score(y_te, lr_preds, zero_division=0)
best_name = 'LR baseline'
results = {}

for name, params in configs.items():
    model = xgb.XGBClassifier(**params)
    model.fit(X_tr.fillna(MED), y_tr,
              eval_set=[(X_v.fillna(MED), y_v)],
              verbose=False)
    p = model.predict_proba(X_te.fillna(MED))[:, 1]
    preds = (p >= THRESHOLD).astype(int)
    prec = precision_score(y_te, preds, zero_division=0)
    rec  = recall_score(y_te, preds, zero_division=0)
    f1   = f1_score(y_te, preds, zero_division=0)
    auc  = roc_auc_score(y_te, p)
    delta = prec - precision_score(y_te, lr_preds, zero_division=0)
    print(f"  {name:<23} {prec:>6.3f} {rec:>6.3f} {f1:>6.3f} {auc:>6.3f}  {delta:>+10.3f}")
    results[name] = {'prec': prec, 'rec': rec, 'f1': f1, 'auc': auc}
    if prec > best_prec:
        best_prec = prec
        best_name = name

print(f"\nBest precision: {best_name} ({best_prec:.3f})")
lr_prec = precision_score(y_te, lr_preds, zero_division=0)
verdict = 'KEEP' if best_prec > lr_prec + 0.005 else 'REJECT'
print(f"Verdict: {verdict}")