"""
lr_vs_ensemble.py
-----------------
Compares standalone LR vs LR+XGBoost ensemble on test set.

Run from repo root:
    python src/models/lr_vs_ensemble.py
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
import xgboost as xgb

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

train = df[df['date'].dt.year <= 2019]
val   = df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)]
test  = df[df['date'].dt.year >= 2023]

def prepare(split):
    rows = split[FEATURES + ['bloom_28d']].dropna(subset=['bloom_28d'])
    X = rows[FEATURES].copy().reset_index(drop=True)
    y = rows['bloom_28d'].copy().reset_index(drop=True)
    return X, y

X_train, y_train = prepare(train)
X_val,   y_val   = prepare(val)
X_test,  y_test  = prepare(test)
MED = X_train.median()

# Fit models
scaler = StandardScaler()
X_tr_s = scaler.fit_transform(X_train.fillna(MED))
X_v_s  = scaler.transform(X_val.fillna(MED))
X_te_s = scaler.transform(X_test.fillna(MED))

lr = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
lr.fit(X_tr_s, y_train)

xgb_m = xgb.XGBClassifier(n_estimators=200, max_depth=6, learning_rate=0.1,
    scale_pos_weight=1.0, eval_metric='auc', random_state=42, verbosity=0)
xgb_m.fit(X_train.fillna(MED), y_train,
          eval_set=[(X_val.fillna(MED), y_val)], verbose=False)

# Probabilities
lr_val_p   = lr.predict_proba(X_v_s)[:, 1]
lr_test_p  = lr.predict_proba(X_te_s)[:, 1]
xgb_val_p  = xgb_m.predict_proba(X_val.fillna(MED))[:, 1]
xgb_test_p = xgb_m.predict_proba(X_test.fillna(MED))[:, 1]
ens_val    = 0.80 * lr_val_p  + 0.20 * xgb_val_p
ens_test   = 0.80 * lr_test_p + 0.20 * xgb_test_p

def best_f1_thresh(y, p):
    prec, rec, thresh = precision_recall_curve(y, p)
    f1 = 2*prec*rec/(prec+rec+1e-9)
    idx = f1.argmax()
    return float(thresh[idx]) if idx < len(thresh) else 0.5

def report(name, y, probs, thresh):
    preds = (probs >= thresh).astype(int)
    print(f"\n{name}  (threshold={thresh:.3f})")
    print(f"  AUC:       {roc_auc_score(y, probs):.4f}")
    print(f"  AP:        {average_precision_score(y, probs):.4f}")
    print(f"  Precision: {precision_score(y, preds, zero_division=0):.4f}")
    print(f"  Recall:    {recall_score(y, preds, zero_division=0):.4f}")
    print(f"  F1:        {f1_score(y, preds, zero_division=0):.4f}")

# Best-F1 thresholds from val
t_lr  = best_f1_thresh(y_val, lr_val_p)
t_xgb = best_f1_thresh(y_val, xgb_val_p)
t_ens = best_f1_thresh(y_val, ens_val)

print("\n" + "="*60)
print("VAL SET — best-F1 thresholds")
print("="*60)
print(f"  LR threshold:       {t_lr:.3f}")
print(f"  XGBoost threshold:  {t_xgb:.3f}")
print(f"  Ensemble threshold: {t_ens:.3f}")

print("\n" + "="*60)
print("TEST SET RESULTS at best-F1 threshold (from val)")
print("="*60)
report("LR only",          y_test, lr_test_p,  t_lr)
report("XGBoost only",     y_test, xgb_test_p, t_xgb)
report("Ensemble LR80+XGB20", y_test, ens_test, t_ens)

print("\n" + "="*60)
print("TEST SET RESULTS at fixed threshold 0.60")
print("="*60)
report("LR only",          y_test, lr_test_p,  0.60)
report("XGBoost only",     y_test, xgb_test_p, 0.60)
report("Ensemble LR80+XGB20", y_test, ens_test, 0.60)