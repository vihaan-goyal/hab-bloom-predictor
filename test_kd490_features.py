"""
test_kd490_features.py
----------------------
Tests Kd490 water clarity features against the locked baseline.

Run after download_kd490.py completes.

Run from repo root:
    python test_kd490_features.py
"""

import glob
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_auc_score, precision_score, recall_score, f1_score,
)

THRESHOLD = 0.60

# ── LOAD LOCKED PIPELINE ──────────────────────────────────────────────────────
print("Loading data/hab_features_tidal.csv...")
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

# Merge Kd490
print("Merging Kd490 features...")
kd = pd.read_csv('data/kd490_features_daily.csv')
kd['date'] = pd.to_datetime(kd['date'])
kd['station_name'] = kd['station_name'].astype(str)
df['station_name'] = df['station_name'].astype(str)
df = df.merge(kd[['date', 'station_name', 'kd490', 'kd490_roll7',
                   'kd490_roll14', 'kd490_anom']],
              on=['date', 'station_name'], how='left')

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

KD_FEATURES = ['kd490', 'kd490_roll7', 'kd490_roll14', 'kd490_anom']
print("\n=== Kd490 feature stats ===")
for col in KD_FEATURES:
    null_pct = df[col].isna().mean() * 100
    corr = df[col].corr(df['bloom_28d'])
    print(f"  {col}: {null_pct:.1f}% null, corr={corr:.3f}")

BASELINE = [
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

train = df[df['date'].dt.year <= 2019]
val   = df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)]
test  = df[df['date'].dt.year >= 2023]

def evaluate(features, label=""):
    feats = [f for f in features if f in df.columns]
    def prep(split):
        rows = split[feats + ['bloom_28d']].dropna(subset=['bloom_28d'])
        X = rows[feats].copy().reset_index(drop=True)
        y = rows['bloom_28d'].copy().reset_index(drop=True)
        return X, y

    X_tr, y_tr = prep(train)
    X_v,  y_v  = prep(val)
    X_te, y_te = prep(test)
    MED = X_tr.median()

    scaler = StandardScaler()
    X_tr_s = scaler.fit_transform(X_tr.fillna(MED))
    X_v_s  = scaler.transform(X_v.fillna(MED))
    X_te_s = scaler.transform(X_te.fillna(MED))

    model = LogisticRegression(C=0.05, class_weight='balanced',
                               max_iter=1000, random_state=42)
    model.fit(X_tr_s, y_tr)

    results = {}
    for name, X_s, y in [('val', X_v_s, y_v), ('test', X_te_s, y_te)]:
        probs = model.predict_proba(X_s)[:, 1]
        preds = (probs >= THRESHOLD).astype(int)
        results[name] = {
            'prec': precision_score(y, preds, zero_division=0),
            'rec':  recall_score(y, preds, zero_division=0),
            'f1':   f1_score(y, preds, zero_division=0),
            'auc':  roc_auc_score(y, probs),
        }

    tag = f" [{label}]" if label else ""
    for name, r in results.items():
        print(f"  {name:4s}{tag}: Prec={r['prec']:.3f} Rec={r['rec']:.3f} "
              f"F1={r['f1']:.3f} AUC={r['auc']:.3f}")
    return results

baseline_feats = [f for f in BASELINE if f in df.columns]
extended_feats = baseline_feats + [f for f in KD_FEATURES if f in df.columns]

print(f"\n{'='*60}")
print(f"BASELINE ({len(baseline_feats)} features)")
print(f"{'='*60}")
base_results = evaluate(baseline_feats, "baseline")

print(f"\n{'='*60}")
print(f"+ KD490 ({len(extended_feats)} features, +{len(extended_feats)-len(baseline_feats)} new)")
print(f"{'='*60}")
kd_results = evaluate(extended_feats, "+kd490")

b = base_results['test']
k = kd_results['test']
print(f"\n{'='*60}")
print("SUMMARY (test 2023-2025, threshold=0.60)")
print(f"{'='*60}")
print(f"  Baseline:  Prec={b['prec']:.3f} Rec={b['rec']:.3f} F1={b['f1']:.3f} AUC={b['auc']:.3f}")
print(f"  + Kd490:   Prec={k['prec']:.3f} Rec={k['rec']:.3f} F1={k['f1']:.3f} AUC={k['auc']:.3f}")
print(f"  Delta Prec: {k['prec']-b['prec']:+.3f}")
verdict = 'KEEP' if k['prec'] > b['prec'] + 0.005 else 'REJECT'
print(f"\nVerdict: {verdict}")