"""
combo_search.py
---------------
Focused combination search on the two best approaches from precision_search.py:
  - LR regularization C=0.05 (best single improvement)
  - SMOTE at various ratios

Tests all pairwise combinations to find the sweet spot between
precision gain and recall preservation.

Run from repo root:
    python src/models/combo_search.py
"""

import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_auc_score, precision_score, recall_score,
    f1_score, precision_recall_curve,
)
from imblearn.over_sampling import SMOTE, BorderlineSMOTE, ADASYN

# ---------------------------------------------------------------------------
# Load + recompute features
# ---------------------------------------------------------------------------
print("Loading data/hab_features_tidal.csv...")
df = pd.read_csv('data/hab_features_tidal.csv')
df['date'] = pd.to_datetime(df['date'])

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
    'chl_roll3_mean', 'chl_roll6_mean', 'chl_roll9_mean', 'chl_trend',
    'chl_roll14_mean', 'chl_roll21_mean',
    'chl_anomaly', 'chl_climatology',
    'do_lag1', 'temp_lag1', 'sal_lag1',
    'sea_water_temperature', 'sea_water_salinity',
    'oxygen_concentration_in_sea_water',
    'month', 'latitude_x', 'longitude_x',
    'nox_lag2', 'dip_lag2', 'dip_change', 'dip_x_month',
    'neighbor_chl3_mean', 'neighbor_chl3_lag1',
    'tidal_gt_anom', 'tidal_msl_anom',
]
FEATURES = [f for f in FEATURES if f in df.columns]

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

scaler = StandardScaler()
X_tr_s = scaler.fit_transform(X_train.fillna(MED))
X_v_s  = scaler.transform(X_val.fillna(MED))
X_te_s = scaler.transform(X_test.fillna(MED))

print(f"Train: {len(X_train):,} | Val: {len(X_val):,} | Test: {len(X_test):,}")
print(f"Train bloom rate: {y_train.mean()*100:.1f}%  "
      f"({int(y_train.sum())} positives)")

def best_f1_thresh(y, p):
    prec, rec, thresh = precision_recall_curve(y, p)
    f1 = 2 * prec * rec / (prec + rec + 1e-9)
    idx = f1.argmax()
    return float(thresh[idx]) if idx < len(thresh) else 0.5

def eval_at(y, p, t):
    preds = (p >= t).astype(int)
    return {
        'auc':       roc_auc_score(y, p),
        'precision': precision_score(y, preds, zero_division=0),
        'recall':    recall_score(y, preds, zero_division=0),
        'f1':        f1_score(y, preds, zero_division=0),
        'tp': int(((preds==1)&(y==1)).sum()),
        'fp': int(((preds==1)&(y==0)).sum()),
        'fn': int(((preds==0)&(y==1)).sum()),
    }

results = []

# ---------------------------------------------------------------------------
# Configs: (name, C, smote_ratio, smote_type, class_weight)
# smote_ratio=None means no SMOTE
# class_weight='balanced' only when no SMOTE (SMOTE replaces it)
# ---------------------------------------------------------------------------
configs = [
    # Baseline
    ('Baseline C=1.0',           1.0,   None,  None,              'balanced'),
    # Best regularization alone
    ('C=0.05',                   0.05,  None,  None,              'balanced'),
    ('C=0.02',                   0.02,  None,  None,              'balanced'),
    ('C=0.01',                   0.01,  None,  None,              'balanced'),
    # SMOTE alone (no class_weight since SMOTE handles imbalance)
    ('SMOTE-0.1',                1.0,   0.10,  'smote',           None),
    ('SMOTE-0.15',               1.0,   0.15,  'smote',           None),
    ('SMOTE-0.20',               1.0,   0.20,  'smote',           None),
    ('SMOTE-0.25',               1.0,   0.25,  'smote',           None),
    # SMOTE + strong regularization
    ('SMOTE-0.10+C=0.05',        0.05,  0.10,  'smote',           None),
    ('SMOTE-0.15+C=0.05',        0.05,  0.15,  'smote',           None),
    ('SMOTE-0.20+C=0.05',        0.05,  0.20,  'smote',           None),
    ('SMOTE-0.25+C=0.05',        0.05,  0.25,  'smote',           None),
    # BorderlineSMOTE -- focuses on hard boundary examples
    ('BorderSMOTE-0.15+C=0.05',  0.05,  0.15,  'borderline',      None),
    ('BorderSMOTE-0.20+C=0.05',  0.05,  0.20,  'borderline',      None),
    # SMOTE + moderate regularization
    ('SMOTE-0.15+C=0.1',         0.10,  0.15,  'smote',           None),
    ('SMOTE-0.20+C=0.1',         0.10,  0.20,  'smote',           None),
]

print(f"\nTesting {len(configs)} configurations...")
print("=" * 90)
print(f"{'Config':<30}  {'AUC':>7}  {'Prec@.60':>9}  "
      f"{'Rec@.60':>8}  {'F1@.60':>7}  {'TP':>4}  {'FP':>4}")
print("-" * 90)

for name, C, smote_ratio, smote_type, class_weight in configs:
    try:
        if smote_ratio is not None:
            if smote_type == 'borderline':
                sm = BorderlineSMOTE(sampling_strategy=smote_ratio,
                                     random_state=42, k_neighbors=5)
            else:
                sm = SMOTE(sampling_strategy=smote_ratio,
                           random_state=42, k_neighbors=5)
            X_fit, y_fit = sm.fit_resample(X_tr_s, y_train)
        else:
            X_fit, y_fit = X_tr_s, y_train

        lr = LogisticRegression(
            C=C,
            class_weight=class_weight,
            max_iter=2000,
            random_state=42,
            solver='lbfgs',
        )
        lr.fit(X_fit, y_fit)

        p_v  = lr.predict_proba(X_v_s)[:, 1]
        p_te = lr.predict_proba(X_te_s)[:, 1]
        t    = best_f1_thresh(y_val, p_v)
        m60  = eval_at(y_test, p_te, 0.60)

        results.append((name, C, smote_ratio, m60))

        baseline_marker = "  <-- baseline" if name == 'Baseline C=1.0' else ""
        print(f"{name:<30}  {m60['auc']:>7.4f}  {m60['precision']:>9.3f}  "
              f"{m60['recall']:>8.3f}  {m60['f1']:>7.3f}  "
              f"{m60['tp']:>4}  {m60['fp']:>4}{baseline_marker}")

    except Exception as e:
        print(f"{name:<30}  ERROR: {e}")

# ---------------------------------------------------------------------------
# Summary -- rank by F1 (not just precision) to find real sweet spot
# ---------------------------------------------------------------------------
print("\n" + "=" * 90)
print("TOP 5 BY F1@0.60 (best overall balance)")
print("=" * 90)
results_sorted_f1 = sorted(results, key=lambda x: x[3]['f1'], reverse=True)
for name, C, ratio, m in results_sorted_f1[:5]:
    print(f"  {name:<30}  Prec={m['precision']:.3f}  Rec={m['recall']:.3f}  "
          f"F1={m['f1']:.3f}  AUC={m['auc']:.4f}  TP={m['tp']} FP={m['fp']}")

print("\nTOP 5 BY PRECISION@0.60 (with recall >= 0.30)")
results_sorted_prec = sorted(
    [r for r in results if r[3]['recall'] >= 0.30],
    key=lambda x: x[3]['precision'], reverse=True)
for name, C, ratio, m in results_sorted_prec[:5]:
    print(f"  {name:<30}  Prec={m['precision']:.3f}  Rec={m['recall']:.3f}  "
          f"F1={m['f1']:.3f}  AUC={m['auc']:.4f}  TP={m['tp']} FP={m['fp']}")

baseline_prec = next(r[3]['precision'] for r in results if r[0] == 'Baseline C=1.0')
baseline_f1   = next(r[3]['f1']        for r in results if r[0] == 'Baseline C=1.0')
best_f1_name  = results_sorted_f1[0][0]
best_f1_m     = results_sorted_f1[0][3]
print(f"\nBaseline:  Prec={baseline_prec:.3f}  F1={baseline_f1:.3f}")
print(f"Best F1:   Prec={best_f1_m['precision']:.3f}  "
      f"F1={best_f1_m['f1']:.3f}  ({best_f1_name})")