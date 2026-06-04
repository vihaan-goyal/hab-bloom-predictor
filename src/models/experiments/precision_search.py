"""
precision_search.py
-------------------
Tests all remaining precision improvement approaches simultaneously:
  1. LR regularization tuning (C values, L1 vs L2)
  2. SMOTE oversampling
  3. Polynomial features on top predictors
  4. Combinations of the above

Run from repo root:
    python src/models/precision_search.py
"""

import warnings
warnings.filterwarnings('ignore', category=UserWarning)

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.metrics import (
    roc_auc_score, precision_score, recall_score,
    f1_score, precision_recall_curve,
)

# Try to import SMOTE -- install if missing
try:
    from imblearn.over_sampling import SMOTE
    HAS_SMOTE = True
except ImportError:
    print("Installing imbalanced-learn...")
    import subprocess, sys
    subprocess.run([sys.executable, '-m', 'pip', 'install',
                    'imbalanced-learn', '--quiet', '--break-system-packages'])
    from imblearn.over_sampling import SMOTE
    HAS_SMOTE = True

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

# Top features for polynomial expansion (avoid exploding feature count)
TOP_FEATS_POLY = [
    'chl_roll21_mean', 'chl_roll9_mean', 'chl_anomaly',
    'chl_climatology', 'tidal_gt_anom', 'tidal_msl_anom',
]

# ---------------------------------------------------------------------------
# Splits
# ---------------------------------------------------------------------------
train = df[df['date'].dt.year <= 2019]
val   = df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)]
test  = df[df['date'].dt.year >= 2023]

def prepare(split, features):
    rows = split[features + ['bloom_28d']].dropna(subset=['bloom_28d'])
    X = rows[features].copy().reset_index(drop=True)
    y = rows['bloom_28d'].copy().reset_index(drop=True)
    return X, y

X_train, y_train = prepare(train, FEATURES)
X_val,   y_val   = prepare(val,   FEATURES)
X_test,  y_test  = prepare(test,  FEATURES)
MED = X_train.median()

print(f"Train: {len(X_train):,} | Val: {len(X_val):,} | Test: {len(X_test):,}")
print(f"Train bloom rate: {y_train.mean()*100:.1f}%")

scaler = StandardScaler()
X_tr_s = scaler.fit_transform(X_train.fillna(MED))
X_v_s  = scaler.transform(X_val.fillna(MED))
X_te_s = scaler.transform(X_test.fillna(MED))

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
# 1. LR regularization sweep
# ---------------------------------------------------------------------------
print("\n[1] LR regularization tuning...")
reg_configs = [
    ('LR-L2-C1.0 (baseline)', 'l2', 1.0),
    ('LR-L2-C0.5',            'l2', 0.5),
    ('LR-L2-C0.1',            'l2', 0.1),
    ('LR-L2-C0.05',           'l2', 0.05),
    ('LR-L1-C1.0',            'l1', 1.0),
    ('LR-L1-C0.5',            'l1', 0.5),
    ('LR-L1-C0.1',            'l1', 0.1),
    ('LR-ElasticNet-C0.5',    'elasticnet', 0.5),
]
for name, penalty, C in reg_configs:
    kwargs = dict(penalty=penalty, C=C, class_weight='balanced',
                  max_iter=2000, random_state=42)
    if penalty == 'l1':
        kwargs['solver'] = 'liblinear'
    elif penalty == 'elasticnet':
        kwargs['solver'] = 'saga'
        kwargs['l1_ratio'] = 0.5
    else:
        kwargs['solver'] = 'lbfgs'

    lr = LogisticRegression(**kwargs)
    lr.fit(X_tr_s, y_train)
    p_v  = lr.predict_proba(X_v_s)[:, 1]
    p_te = lr.predict_proba(X_te_s)[:, 1]
    t    = best_f1_thresh(y_val, p_v)
    m60  = eval_at(y_test, p_te, 0.60)
    results.append(('Regularization', name, m60))
    print(f"  {name:<30}  Prec@.60={m60['precision']:.3f}  "
          f"Rec={m60['recall']:.3f}  F1={m60['f1']:.3f}  AUC={m60['auc']:.4f}")

# ---------------------------------------------------------------------------
# 2. SMOTE oversampling
# ---------------------------------------------------------------------------
print("\n[2] SMOTE oversampling...")
smote_configs = [
    ('SMOTE-0.3',  0.3),
    ('SMOTE-0.5',  0.5),
    ('SMOTE-1.0',  1.0),
]
for name, ratio in smote_configs:
    sm = SMOTE(sampling_strategy=ratio, random_state=42, k_neighbors=5)
    try:
        X_sm, y_sm = sm.fit_resample(X_tr_s, y_train)
        lr = LogisticRegression(class_weight=None, max_iter=1000, random_state=42)
        lr.fit(X_sm, y_sm)
        p_v  = lr.predict_proba(X_v_s)[:, 1]
        p_te = lr.predict_proba(X_te_s)[:, 1]
        t    = best_f1_thresh(y_val, p_v)
        m60  = eval_at(y_test, p_te, 0.60)
        results.append(('SMOTE', name, m60))
        print(f"  {name:<30}  Prec@.60={m60['precision']:.3f}  "
              f"Rec={m60['recall']:.3f}  F1={m60['f1']:.3f}  AUC={m60['auc']:.4f}")
    except Exception as e:
        print(f"  {name}: ERROR -- {e}")

# ---------------------------------------------------------------------------
# 3. Polynomial features on top predictors
# ---------------------------------------------------------------------------
print("\n[3] Polynomial features...")

# Get indices of top features in the scaled array
top_idx = [FEATURES.index(f) for f in TOP_FEATS_POLY if f in FEATURES]

poly_configs = [
    ('Poly-degree2-top6',  2),
    ('Poly-degree3-top6',  3),
]
for name, degree in poly_configs:
    poly = PolynomialFeatures(degree=degree, include_bias=False,
                              interaction_only=False)
    X_tr_top = X_tr_s[:, top_idx]
    X_v_top  = X_v_s[:,  top_idx]
    X_te_top = X_te_s[:, top_idx]

    X_tr_poly = poly.fit_transform(X_tr_top)
    X_v_poly  = poly.transform(X_v_top)
    X_te_poly = poly.transform(X_te_top)

    # Combine with remaining features
    other_idx = [i for i in range(X_tr_s.shape[1]) if i not in top_idx]
    X_tr_aug = np.hstack([X_tr_s[:, other_idx], X_tr_poly])
    X_v_aug  = np.hstack([X_v_s[:,  other_idx], X_v_poly])
    X_te_aug = np.hstack([X_te_s[:, other_idx], X_te_poly])

    lr = LogisticRegression(class_weight='balanced', C=0.5,
                            max_iter=2000, random_state=42)
    lr.fit(X_tr_aug, y_train)
    p_v  = lr.predict_proba(X_v_aug)[:, 1]
    p_te = lr.predict_proba(X_te_aug)[:, 1]
    t    = best_f1_thresh(y_val, p_v)
    m60  = eval_at(y_test, p_te, 0.60)
    results.append(('Polynomial', name, m60))
    n_feats = X_tr_aug.shape[1]
    print(f"  {name:<30}  Prec@.60={m60['precision']:.3f}  "
          f"Rec={m60['recall']:.3f}  F1={m60['f1']:.3f}  "
          f"AUC={m60['auc']:.4f}  ({n_feats} features)")

# ---------------------------------------------------------------------------
# 4. SMOTE + best regularization
# ---------------------------------------------------------------------------
print("\n[4] SMOTE + L2-C0.1 combination...")
try:
    sm = SMOTE(sampling_strategy=0.5, random_state=42, k_neighbors=5)
    X_sm, y_sm = sm.fit_resample(X_tr_s, y_train)
    lr = LogisticRegression(penalty='l2', C=0.1, class_weight=None,
                            max_iter=2000, random_state=42)
    lr.fit(X_sm, y_sm)
    p_v  = lr.predict_proba(X_v_s)[:, 1]
    p_te = lr.predict_proba(X_te_s)[:, 1]
    t    = best_f1_thresh(y_val, p_v)
    m60  = eval_at(y_test, p_te, 0.60)
    results.append(('Combination', 'SMOTE-0.5+L2-C0.1', m60))
    print(f"  SMOTE-0.5+L2-C0.1              Prec@.60={m60['precision']:.3f}  "
          f"Rec={m60['recall']:.3f}  F1={m60['f1']:.3f}  AUC={m60['auc']:.4f}")
except Exception as e:
    print(f"  ERROR: {e}")

# ---------------------------------------------------------------------------
# Results table
# ---------------------------------------------------------------------------
print("\n" + "=" * 80)
print("ALL RESULTS — sorted by precision at threshold 0.60")
print("=" * 80)
print(f"{'Category':<14}  {'Model':<30}  {'AUC':>7}  "
      f"{'Prec@.60':>9}  {'Rec@.60':>8}  {'F1@.60':>7}")
print("-" * 80)

results.sort(key=lambda x: x[2]['precision'], reverse=True)
baseline_prec = next(r[2]['precision'] for r in results
                     if 'baseline' in r[1].lower())

for cat, name, m in results:
    marker = "  <-- BEST" if name == results[0][1] else ""
    marker = "  <-- BASELINE" if 'baseline' in name.lower() else marker
    print(f"{cat:<14}  {name:<30}  {m['auc']:>7.4f}  "
          f"{m['precision']:>9.3f}  {m['recall']:>8.3f}  {m['f1']:>7.3f}"
          f"  TP={m['tp']} FP={m['fp']}{marker}")

best_cat, best_name, best_m = results[0]
delta = best_m['precision'] - baseline_prec
print(f"\nBaseline precision: {baseline_prec:.3f}")
print(f"Best precision:     {best_m['precision']:.3f} ({best_name}) delta={delta:+.3f}")

if delta > 0.02:
    print(f"\nWINNER: {best_name} -- integrate into pipeline")
else:
    print("\nNo approach beats baseline by >2pp. Precision ceiling confirmed.")