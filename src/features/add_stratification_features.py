"""
add_stratification_features.py
-------------------------------
Merges thermal stratification (surface - bottom temperature) into the
feature set and retrains to test whether stratification improves precision.

Run AFTER download_bottom_temp.py has created data/stratification_daily.csv.

Run from repo root:
    python src/features/add_stratification_features.py
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

print("Loading data...")
df = pd.read_csv('data/hab_features_tidal.csv')
df['date'] = pd.to_datetime(df['date'])

# Merge sal_lags
daily = pd.read_csv('data/hab_features_daily.csv')[
    ['date', 'station_name', 'sal_lag2', 'sal_lag3', 'sal_lag4']
]
daily['date'] = pd.to_datetime(daily['date'])
for col in ['sal_lag2', 'sal_lag3', 'sal_lag4']:
    if col not in df.columns:
        df = df.merge(daily[['date', 'station_name', col]],
                      on=['date', 'station_name'], how='left')

# Merge stratification
strat = pd.read_csv('data/stratification_daily.csv')
strat['date'] = pd.to_datetime(strat['date'])
df = df.merge(strat[['station_name', 'date', 'temp_bottom',
                       'do_bottom', 'temp_stratification']],
              on=['station_name', 'date'], how='left')

print(f"Stratification coverage: "
      f"{df['temp_stratification'].notna().mean()*100:.1f}%")
print(f"Bottom temp coverage: "
      f"{df['temp_bottom'].notna().mean()*100:.1f}%")

# Recompute rolling features and bloom label
for n, min_p in [(3,2),(6,3),(9,5),(14,7),(21,10)]:
    df[f'chl_roll{n}_mean'] = (
        df.groupby('station_name')['Chlorophyll']
          .transform(lambda x: x.rolling(n, min_periods=min_p).mean())
    )
df['chl_trend'] = (
    df.groupby('station_name')['Chlorophyll']
      .transform(lambda x: x.rolling(4, min_periods=3)
                 .apply(lambda v: np.polyfit(range(len(v)), v, 1)[0]))
)

# Add lagged stratification features
df['strat_lag1'] = df.groupby('station_name')['temp_stratification'].transform(
    lambda x: x.shift(1))
df['strat_roll7'] = df.groupby('station_name')['temp_stratification'].transform(
    lambda x: x.rolling(7, min_periods=3).mean())

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

BASE = [
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
STRAT_FEATS = ['temp_stratification', 'temp_bottom', 'strat_lag1', 'strat_roll7']

BASE        = [f for f in BASE        if f in df.columns]
STRAT_FEATS = [f for f in STRAT_FEATS if f in df.columns]
AUGMENTED   = BASE + STRAT_FEATS

print(f"\nBase features:   {len(BASE)}")
print(f"Strat features:  {len(STRAT_FEATS)}")

# Correlation check
print("\nCorrelations with bloom_28d:")
for f in STRAT_FEATS:
    valid = df[[f, 'bloom_28d']].dropna()
    if len(valid) > 100:
        r = valid[f].corr(valid['bloom_28d'])
        cov = df[f].notna().mean() * 100
        print(f"  {f:<25}  r={r:>+7.4f}  ({cov:.1f}% coverage)")

# Splits
train = df[df['date'].dt.year <= 2019]
val   = df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)]
test  = df[df['date'].dt.year >= 2023]

def prepare(split, features):
    rows = split[features + ['bloom_28d']].dropna(subset=['bloom_28d'])
    X = rows[features].copy().reset_index(drop=True)
    y = rows['bloom_28d'].copy().reset_index(drop=True)
    return X, y

def fit_eval(X_tr, y_tr, X_v, y_v, X_te, y_te, label):
    MED = X_tr.median()
    sc  = StandardScaler()
    lr  = LogisticRegression(C=0.05, class_weight='balanced',
                              max_iter=2000, random_state=42)
    lr.fit(sc.fit_transform(X_tr.fillna(MED)), y_tr)
    p_v  = lr.predict_proba(sc.transform(X_v.fillna(MED)))[:, 1]
    p_te = lr.predict_proba(sc.transform(X_te.fillna(MED)))[:, 1]

    prec, rec, thresh = precision_recall_curve(y_v, p_v)
    f1_arr = 2*prec*rec/(prec+rec+1e-9)
    t = float(thresh[f1_arr.argmax()]) if f1_arr.argmax() < len(thresh) else 0.5

    preds = (p_te >= 0.60).astype(int)
    print(f"\n{label}")
    print(f"  AUC:       {roc_auc_score(y_te, p_te):.4f}")
    print(f"  Prec@.60:  {precision_score(y_te, preds, zero_division=0):.4f}")
    print(f"  Rec@.60:   {recall_score(y_te, preds, zero_division=0):.4f}")
    print(f"  F1@.60:    {f1_score(y_te, preds, zero_division=0):.4f}")
    tp = int(((preds==1)&(y_te==1)).sum())
    fp = int(((preds==1)&(y_te==0)).sum())
    fn = int(((preds==0)&(y_te==1)).sum())
    print(f"  TP={tp}  FP={fp}  FN={fn}")

print("\n" + "="*55)
print("RESULTS COMPARISON")
print("="*55)

X_tr_b, y_tr_b = prepare(train, BASE)
X_v_b,  y_v_b  = prepare(val,   BASE)
X_te_b, y_te_b = prepare(test,  BASE)
fit_eval(X_tr_b, y_tr_b, X_v_b, y_v_b, X_te_b, y_te_b,
         "BASE (baseline, n=33)")

X_tr_a, y_tr_a = prepare(train, AUGMENTED)
X_v_a,  y_v_a  = prepare(val,   AUGMENTED)
X_te_a, y_te_a = prepare(test,  AUGMENTED)
fit_eval(X_tr_a, y_tr_a, X_v_a, y_v_a, X_te_a, y_te_a,
         f"BASE + stratification (n={len(AUGMENTED)})")