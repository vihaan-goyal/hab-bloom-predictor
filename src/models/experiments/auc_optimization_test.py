"""
auc_optimization_test.py
------------------------
Tests whether training with AUC as the direct objective improves test AUC
without sacrificing precision or recall.

Models compared against LR C=0.05 (baseline AUC=0.815, Prec=0.500, F1=0.493):
  - LR CV with roc_auc scoring
  - LR CV with average_precision scoring
  - SGD modified_huber + isotonic calibration
  - LightGBM with AUC objective
  - LightGBM with cross-entropy objective
  - XGBoost with aucpr objective

Key question: Does any model beat AUC=0.815 WITHOUT dropping Prec below 0.465
or F1 below 0.455?

Run from repo root:
    python src/models/experiments/auc_optimization_test.py
"""

import glob
import warnings
from io import StringIO
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV, SGDClassifier
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
from sklearn.preprocessing import StandardScaler

# ---------------------------------------------------------------------------
# Data loading (full pipeline)
# ---------------------------------------------------------------------------
print("Loading data/hab_features_tidal.csv...")
hab = pd.read_csv('data/hab_features_tidal.csv')
hab['date'] = pd.to_datetime(hab['date'])

daily = pd.read_csv('data/hab_features_daily.csv')
daily['date'] = pd.to_datetime(daily['date'])

for col in ['sal_lag2', 'sal_lag3', 'sal_lag4']:
    if col not in hab.columns:
        hab = hab.merge(daily[['date', 'station_name', col]],
                        on=['date', 'station_name'], how='left')

print("Merging percent_saturation from deep_wq_extra...")
pct_frames = []
for fpath in sorted(glob.glob('data/raw/deep_wq_extra/deep_wq_S_*.csv')):
    with open(fpath) as f:
        lines = f.readlines()
    if len(lines) < 3:
        continue
    df_yr = pd.read_csv(StringIO(lines[0] + ''.join(lines[2:])), low_memory=False)
    pct_frames.append(df_yr)
if pct_frames:
    pct_df = pd.concat(pct_frames, ignore_index=True)
    pct_df['date'] = (pd.to_datetime(pct_df['time'], errors='coerce')
                        .dt.tz_localize(None).dt.normalize())
    pct_df['percent_saturation'] = pd.to_numeric(
        pct_df['percent_saturation'], errors='coerce')
    pct_daily = (pct_df.groupby(['station_name', 'date'])['percent_saturation']
                       .mean().reset_index())
    if 'percent_saturation' not in hab.columns:
        hab = hab.merge(pct_daily, on=['station_name', 'date'], how='left')
print(f"  percent_saturation coverage: "
      f"{hab['percent_saturation'].notna().mean() * 100:.1f}%")

print("Merging max_gust_3d from data/gust_features_daily.csv...")
gust = pd.read_csv('data/gust_features_daily.csv')
gust['date'] = pd.to_datetime(gust['date'])
hab = hab.merge(gust[['date', 'max_gust_3d']], on='date', how='left')
print(f"  max_gust_3d coverage: {hab['max_gust_3d'].notna().mean() * 100:.1f}%")

print("Recomputing rolling CHL features...")
for n, min_p in [(3, 2), (6, 3), (9, 5), (14, 7), (21, 10)]:
    hab[f'chl_roll{n}_mean'] = (
        hab.groupby('station_name')['Chlorophyll']
           .transform(lambda x: x.rolling(n, min_periods=min_p).mean())
    )

hab['chl_trend'] = (
    hab.groupby('station_name')['Chlorophyll']
       .transform(lambda x: x.rolling(4, min_periods=3)
                  .apply(lambda v: np.polyfit(range(len(v)), v, 1)[0]))
)

print("Recomputing bloom_28d labels...")
hab['bloom_28d'] = 0
for station, grp in hab.groupby('station_name'):
    idx   = grp.index
    dates = grp['date'].values
    chl   = grp['Chlorophyll'].values
    labels = np.zeros(len(grp), dtype=int)
    for i in range(len(grp)):
        mask = (dates > dates[i]) & (dates <= dates[i] + np.timedelta64(28, 'D'))
        if mask.any() and (chl[mask] > 10).any():
            labels[i] = 1
    hab.loc[idx, 'bloom_28d'] = labels

# ---------------------------------------------------------------------------
# Feature set (35 features -- full pipeline)
# ---------------------------------------------------------------------------
FEATURES_ALL = [
    'Chlorophyll', 'chl_lag1', 'chl_lag2', 'chl_lag3', 'chl_lag4',
    'chl_roll3_mean', 'chl_roll6_mean', 'chl_roll9_mean', 'chl_trend',
    'chl_roll14_mean', 'chl_roll21_mean',
    'chl_anomaly', 'chl_climatology',
    'do_lag1', 'temp_lag1', 'sal_lag1', 'sal_lag2', 'sal_lag3', 'sal_lag4',
    'sea_water_temperature', 'sea_water_salinity',
    'oxygen_concentration_in_sea_water', 'percent_saturation',
    'month', 'latitude_x', 'longitude_x',
    'nox_lag2', 'dip_lag2', 'dip_change', 'dip_x_month',
    'neighbor_chl3_mean', 'neighbor_chl3_lag1',
    'tidal_gt_anom', 'tidal_msl_anom', 'max_gust_3d',
]
FEATURES = [f for f in FEATURES_ALL if f in hab.columns]
print(f"\nFeature set: {len(FEATURES)} features (expected 35).")

# ---------------------------------------------------------------------------
# Splits
# ---------------------------------------------------------------------------
train = hab[hab['date'].dt.year <= 2019]
val   = hab[(hab['date'].dt.year >= 2020) & (hab['date'].dt.year <= 2022)]
test  = hab[hab['date'].dt.year >= 2023]


def prepare(split, features):
    rows = split[features + ['bloom_28d']].dropna(subset=['bloom_28d'])
    X = rows[features].copy().reset_index(drop=True)
    y = rows['bloom_28d'].copy().reset_index(drop=True)
    return X, y


def eval_at(y, p, t):
    preds = (p >= t).astype(int)
    tp = int(((preds == 1) & (y == 1)).sum())
    fp = int(((preds == 1) & (y == 0)).sum())
    fn = int(((preds == 0) & (y == 1)).sum())
    return {
        'auc':       roc_auc_score(y, p),
        'precision': precision_score(y, preds, zero_division=0),
        'recall':    recall_score(y, preds, zero_division=0),
        'f1':        f1_score(y, preds, zero_division=0),
        'tp': tp, 'fp': fp, 'fn': fn,
    }


X_tr, y_tr = prepare(train, FEATURES)
X_v,  y_v  = prepare(val,   FEATURES)
X_te, y_te = prepare(test,  FEATURES)
MED = X_tr.median()

sc = StandardScaler()
X_tr_s = sc.fit_transform(X_tr.fillna(MED))
X_v_s  = sc.transform(X_v.fillna(MED))
X_te_s = sc.transform(X_te.fillna(MED))

print(f"\nTrain: {len(y_tr)} rows, {y_tr.sum()} positives ({y_tr.mean()*100:.1f}%)")
print(f"Val:   {len(y_v)} rows, {y_v.sum()} positives ({y_v.mean()*100:.1f}%)")
print(f"Test:  {len(y_te)} rows, {y_te.sum()} positives ({y_te.mean()*100:.1f}%)")

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
try:
    import lightgbm as lgb
    HAS_LGB = True
except ImportError:
    print("\nWARNING: lightgbm not installed -- LightGBM models will be skipped.")
    HAS_LGB = False

try:
    import xgboost as xgb
    HAS_XGB = True
except ImportError:
    print("WARNING: xgboost not installed -- XGBoost models will be skipped.")
    HAS_XGB = False

models = {
    'LR C=0.05 (baseline)': LogisticRegression(
        C=0.05, class_weight='balanced', max_iter=2000, random_state=42),

    'LR CV roc_auc': LogisticRegressionCV(
        Cs=[0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.5, 1.0],
        class_weight='balanced', scoring='roc_auc',
        cv=5, max_iter=2000, random_state=42, n_jobs=-1),

    'LR CV avg_precision': LogisticRegressionCV(
        Cs=[0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.5, 1.0],
        class_weight='balanced', scoring='average_precision',
        cv=5, max_iter=2000, random_state=42, n_jobs=-1),

    'SGD modified_huber': CalibratedClassifierCV(
        SGDClassifier(loss='modified_huber', class_weight='balanced',
                      max_iter=1000, random_state=42, n_jobs=-1),
        cv=5, method='isotonic'),
}

if HAS_LGB:
    models['LightGBM AUC'] = lgb.LGBMClassifier(
        objective='binary', metric='auc',
        n_estimators=300, max_depth=4, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.8,
        min_child_samples=20, class_weight='balanced',
        random_state=42, verbose=-1)

    models['LightGBM cross_entropy'] = lgb.LGBMClassifier(
        objective='cross_entropy', metric='binary_logloss',
        n_estimators=300, max_depth=4, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.8,
        min_child_samples=20, class_weight='balanced',
        random_state=42, verbose=-1)

if HAS_XGB:
    models['XGBoost aucpr'] = xgb.XGBClassifier(
        eval_metric='aucpr', n_estimators=300, max_depth=3,
        learning_rate=0.05, subsample=0.8, colsample_bytree=0.8,
        min_child_weight=15, scale_pos_weight=2,
        random_state=42, verbosity=0)

# ---------------------------------------------------------------------------
# Train and evaluate
# ---------------------------------------------------------------------------
results = []
for name, model in models.items():
    print(f"\nFitting: {name}...")
    model.fit(X_tr_s, y_tr)

    p_v  = model.predict_proba(X_v_s)[:, 1]
    p_te = model.predict_proba(X_te_s)[:, 1]

    val_auc = roc_auc_score(y_v, p_v)
    m = eval_at(y_te, p_te, 0.60)

    selected_C = None
    if hasattr(model, 'C_'):
        selected_C = float(model.C_[0]) if hasattr(model.C_, '__len__') else float(model.C_)

    results.append({
        'name': name,
        'val_auc': val_auc,
        'selected_C': selected_C,
        **m,
    })

results.sort(key=lambda x: x['auc'], reverse=True)

BASELINE_AUC  = 0.815
BASELINE_PREC = 0.500
BASELINE_F1   = 0.493

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
print("\n")
print("AUC OPTIMIZATION TEST (test 2023-2025, threshold 0.60)")
print("Sorted by Test AUC")
print("=" * 92)
print(f"{'Model':<26}  {'Val_AUC':>7}  {'Test_AUC':>8}  "
      f"{'Prec':>6}  {'Rec':>6}  {'F1':>6}  {'TP':>3}  {'FP':>3}  {'FN':>3}")
print("-" * 92)

baseline_row = None
for r in results:
    if 'baseline' in r['name']:
        baseline_row = r
        break

for r in results:
    flag = ''
    if r['name'] != 'LR C=0.05 (baseline)' and baseline_row is not None:
        if r['auc'] > BASELINE_AUC and r['precision'] >= 0.465:
            flag = '  *** AUC IMPROVEMENT ***'
        elif r['auc'] > BASELINE_AUC:
            flag = '  (AUC up, Prec < 0.465)'

    c_str = f"  [C={r['selected_C']:.4g}]" if r['selected_C'] is not None else ''
    print(f"{r['name']:<26}  {r['val_auc']:>7.4f}  {r['auc']:>8.4f}  "
          f"{r['precision']:>6.3f}  {r['recall']:>6.3f}  {r['f1']:>6.3f}  "
          f"{r['tp']:>3}  {r['fp']:>3}  {r['fn']:>3}{c_str}{flag}")

print()
print(f"Baseline: AUC={BASELINE_AUC:.3f}  Prec={BASELINE_PREC:.3f}  F1={BASELINE_F1:.3f}")
print(f"Flag criteria: AUC > {BASELINE_AUC:.3f} AND Prec >= 0.465  (no Prec or F1 regression)")

any_winner = any(
    r['auc'] > BASELINE_AUC and r['precision'] >= 0.465
    for r in results if r['name'] != 'LR C=0.05 (baseline)'
)
if any_winner:
    print("\n=> At least one model beats the baseline on AUC without precision regression.")
    print("   Consider integrating into the pipeline.")
else:
    print("\n=> No model beats AUC=0.815 while maintaining Prec >= 0.465.")
    print("   Baseline LR C=0.05 remains the best option.")
