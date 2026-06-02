"""
retrain_with_wind.py
--------------------
Retrains LR with wind features added and compares to baseline.
Run AFTER add_wind_features.py has created data/hab_features_wind.csv.

Run from repo root:
    python src/models/retrain_with_wind.py
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

print("Loading data/hab_features_wind.csv...")
df = pd.read_csv('data/hab_features_wind.csv')
df['date'] = pd.to_datetime(df['date'])

# Recompute rolling features + bloom label
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

WIND_FEATURES = [
    'wind_roll3_mean', 'wind_roll7_mean', 'wind_max_7d',
    'wind_calm_days_7d', 'wind_dir_var_7d',
]

BASE_FEATURES  = [f for f in BASE_FEATURES  if f in df.columns]
WIND_FEATURES  = [f for f in WIND_FEATURES  if f in df.columns]
AUGMENTED      = BASE_FEATURES + WIND_FEATURES

print(f"Base features:  {len(BASE_FEATURES)}")
print(f"Wind features:  {len(WIND_FEATURES)} -- {WIND_FEATURES}")
print(f"Augmented:      {len(AUGMENTED)}")

# Extended+ split: train <=2022, val=2022, test>=2023
train = df[df['date'].dt.year <= 2022]
val   = df[df['date'].dt.year == 2022]
test  = df[df['date'].dt.year >= 2023]

def prepare(split, features):
    rows = split[features + ['bloom_28d']].dropna(subset=['bloom_28d'])
    X = rows[features].copy().reset_index(drop=True)
    y = rows['bloom_28d'].copy().reset_index(drop=True)
    return X, y

X_train_b, y_train_b = prepare(train, BASE_FEATURES)
X_val_b,   y_val_b   = prepare(val,   BASE_FEATURES)
X_test_b,  y_test_b  = prepare(test,  BASE_FEATURES)

X_train_w, y_train_w = prepare(train, AUGMENTED)
X_val_w,   y_val_w   = prepare(val,   AUGMENTED)
X_test_w,  y_test_w  = prepare(test,  AUGMENTED)

MED_b = X_train_b.median()
MED_w = X_train_w.median()

print(f"\nBase   -- Train: {len(X_train_b):,} | Val: {len(X_val_b):,} | Test: {len(X_test_b):,}")
print(f"Wind   -- Train: {len(X_train_w):,} | Val: {len(X_val_w):,} | Test: {len(X_test_w):,}")

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
p_val_b, p_test_b, lr_b, sc_b = fit_lr(X_train_b, y_train_b,
                                         X_val_b, X_test_b, MED_b)

print("Fitting wind-augmented LR...")
p_val_w, p_test_w, lr_w, sc_w = fit_lr(X_train_w, y_train_w,
                                         X_val_w, X_test_w, MED_w)

t_b = best_f1_thresh(y_val_b, p_val_b)
t_w = best_f1_thresh(y_val_w, p_val_w)

m_b = eval_at(y_test_b, p_test_b, t_b)
m_w = eval_at(y_test_w, p_test_w, t_w)
m_b_60 = eval_at(y_test_b, p_test_b, 0.60)
m_w_60 = eval_at(y_test_w, p_test_w, 0.60)

print("\n" + "=" * 65)
print("TEST SET COMPARISON (2023-2025)")
print("=" * 65)
print(f"\n{'Metric':<12}  {'Baseline':>10}  {'+ Wind':>10}  {'Delta':>8}")
print("-" * 45)
for k in ['auc', 'ap', 'precision', 'recall', 'f1']:
    delta = m_w[k] - m_b[k]
    marker = " <--" if k == 'precision' else ""
    print(f"{k:<12}  {m_b[k]:>10.4f}  {m_w[k]:>10.4f}  {delta:>+8.4f}{marker}")
print(f"\nBase threshold (val): {t_b:.3f}  |  Wind threshold (val): {t_w:.3f}")

print(f"\n-- At fixed threshold 0.60 --")
print(f"{'Metric':<12}  {'Baseline':>10}  {'+ Wind':>10}  {'Delta':>8}")
print("-" * 45)
for k in ['precision', 'recall', 'f1']:
    delta = m_w_60[k] - m_b_60[k]
    marker = " <--" if k == 'precision' else ""
    print(f"{k:<12}  {m_b_60[k]:>10.4f}  {m_w_60[k]:>10.4f}  {delta:>+8.4f}{marker}")
print(f"Baseline: TP={m_b_60['tp']}  FP={m_b_60['fp']}  FN={m_b_60['fn']}")
print(f"+ Wind:   TP={m_w_60['tp']}  FP={m_w_60['fp']}  FN={m_w_60['fn']}")

# LR coefficients for wind features
print("\n-- Wind feature coefficients --")
coef_df = pd.Series(lr_w.coef_[0], index=AUGMENTED)
for f in WIND_FEATURES:
    if f in coef_df:
        direction = "reduces bloom prob (mixing suppresses blooms)" if coef_df[f] < 0 else "increases bloom prob"
        print(f"  {f:<25} coef={coef_df[f]:>+8.4f}  ({direction})")

print("\n" + "=" * 65)
print("VERDICT")
print("=" * 65)
delta_prec = m_w_60['precision'] - m_b_60['precision']
if delta_prec > 0.02:
    print(f"  Wind features HELP: +{delta_prec:.3f} precision at threshold 0.60")
    print("  --> Update hab_features_daily.csv pipeline to include wind features")
    print("  --> Update daily_inference.py FEATURES list to include wind features")
elif delta_prec > 0:
    print(f"  Wind features marginally help: +{delta_prec:.3f} precision")
    print("  --> Borderline -- check if AUC also improved before adding complexity")
else:
    print(f"  Wind features do NOT help: {delta_prec:.3f} precision delta")
    print("  --> Skip wind features. Precision ceiling confirmed.")