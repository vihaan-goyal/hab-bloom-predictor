"""
feature_strategy_search.py
--------------------------
Tests 6 fundamentally different feature-set strategies against the current
34-feature baseline (LR C=0.05, class_weight='balanced', threshold 0.60).

Strategies:
  1. CHL_only          -- chlorophyll trajectory only
  2. Physical_only     -- physical variables, no chlorophyll
  3. Nutrient_focused  -- nutrients + salinity
  4. Spatial_only      -- spatial propagation + seasonality
  5. PCA_{5,10,15,20}  -- top N principal components from full feature set
  6. LASSO_selected    -- L1-CV selects minimal non-zero feature subset

Run from repo root:
    & "$env:USERPROFILE/anaconda3/python.exe" src/models/feature_strategy_search.py
"""

import glob
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_auc_score, f1_score, precision_score, recall_score,
)

# ---------------------------------------------------------------------------
# 1. Load + merge
# ---------------------------------------------------------------------------
print("Loading data/hab_features_tidal.csv ...")
hab = pd.read_csv('data/hab_features_tidal.csv')
hab['date'] = pd.to_datetime(hab['date'])

print("Loading data/hab_features_daily.csv ...")
daily = pd.read_csv('data/hab_features_daily.csv')
daily['date'] = pd.to_datetime(daily['date'])

for col in ['sal_lag2', 'sal_lag3', 'sal_lag4']:
    if col not in hab.columns:
        hab = hab.merge(daily[['date', 'station_name', col]],
                        on=['date', 'station_name'], how='left')

# percent_saturation lives in the raw ERDDAP surface extracts
if 'percent_saturation' not in hab.columns:
    print("Loading percent_saturation from data/raw/deep_wq_extra/deep_wq_S_*.csv ...")
    frames = []
    for f in sorted(glob.glob('data/raw/deep_wq_extra/deep_wq_S_*.csv')):
        s = pd.read_csv(f, skiprows=[1],
                        usecols=['station_name', 'time', 'percent_saturation'])
        frames.append(s)
    ps = pd.concat(frames, ignore_index=True)
    ps = ps[ps['station_name'].notna()].copy()
    ps['station_name'] = ps['station_name'].astype(str)
    ps['date'] = pd.to_datetime(ps['time'], utc=True).dt.tz_localize(None).dt.normalize()
    ps['percent_saturation'] = pd.to_numeric(ps['percent_saturation'], errors='coerce')
    ps = (ps.dropna(subset=['percent_saturation'])
            .groupby(['date', 'station_name'], as_index=False)['percent_saturation']
            .mean())
    hab['station_name'] = hab['station_name'].astype(str)
    ps['station_name'] = ps['station_name'].astype(str)
    hab = hab.merge(ps, on=['date', 'station_name'], how='left')
    print(f"  percent_saturation coverage: "
          f"{hab['percent_saturation'].notna().mean()*100:.1f}%")

if 'TDN-LC' not in hab.columns and 'TDN-LC' in daily.columns:
    hab = hab.merge(daily[['date', 'station_name', 'TDN-LC']],
                    on=['date', 'station_name'], how='left')

df = hab

# ---------------------------------------------------------------------------
# 2. Recompute rolling features and bloom_28d label
# ---------------------------------------------------------------------------
print("Computing rolling features and bloom_28d label ...")
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

df['bloom_28d'] = 0
for station, grp in df.groupby('station_name'):
    idx = grp.index
    dates = grp['date'].values
    chl = grp['Chlorophyll'].values
    labels = np.zeros(len(grp), dtype=int)
    for i in range(len(grp)):
        mask = (dates > dates[i]) & (dates <= dates[i] + np.timedelta64(28, 'D'))
        if mask.any() and (chl[mask] > 10).any():
            labels[i] = 1
    df.loc[idx, 'bloom_28d'] = labels

# ---------------------------------------------------------------------------
# 3. Full feature list
# ---------------------------------------------------------------------------
FULL_BASE = [
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
    'tidal_gt_anom', 'tidal_msl_anom',
]
FULL_BASE = [f for f in FULL_BASE if f in df.columns]
print(f"FULL_BASE available features: {len(FULL_BASE)}")

# ---------------------------------------------------------------------------
# 4. Strategy feature sets
# ---------------------------------------------------------------------------
strategies = {
    'CHL_only': [
        'Chlorophyll', 'chl_lag1', 'chl_lag2', 'chl_lag3', 'chl_lag4',
        'chl_roll3_mean', 'chl_roll6_mean', 'chl_roll9_mean', 'chl_trend',
        'chl_roll14_mean', 'chl_roll21_mean',
        'chl_anomaly', 'chl_climatology',
        'neighbor_chl3_mean', 'neighbor_chl3_lag1',
        'month', 'latitude_x', 'longitude_x',
    ],
    'Physical_only': [
        'do_lag1', 'temp_lag1', 'sal_lag1', 'sal_lag2', 'sal_lag3', 'sal_lag4',
        'sea_water_temperature', 'sea_water_salinity',
        'oxygen_concentration_in_sea_water', 'percent_saturation',
        'tidal_gt_anom', 'tidal_msl_anom',
        'month', 'latitude_x', 'longitude_x',
    ],
    'Nutrient_focused': [
        'nox_lag2', 'dip_lag2', 'dip_change', 'dip_x_month',
        'sal_lag1', 'sal_lag2', 'sal_lag3', 'sal_lag4',
        'sea_water_salinity', 'TDN-LC',
        'tidal_gt_anom', 'tidal_msl_anom',
        'month', 'latitude_x', 'longitude_x',
        'neighbor_chl3_mean',
    ],
    'Spatial_only': [
        'neighbor_chl3_mean', 'neighbor_chl3_lag1',
        'month', 'latitude_x', 'longitude_x',
        'tidal_gt_anom', 'tidal_msl_anom',
        'sea_water_temperature', 'sea_water_salinity',
    ],
}

# ---------------------------------------------------------------------------
# 5. Splits
# ---------------------------------------------------------------------------
train = df[df['date'].dt.year <= 2019]
val   = df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)]
test  = df[df['date'].dt.year >= 2023]

print(f"\nSplits -- train: {len(train):,} | val: {len(val):,} | test: {len(test):,}")
print(f"Bloom rate -- train: {train['bloom_28d'].mean():.3f} | "
      f"val: {val['bloom_28d'].mean():.3f} | test: {test['bloom_28d'].mean():.3f}")

# ---------------------------------------------------------------------------
# 6. Helpers
# ---------------------------------------------------------------------------
def prepare(split, features):
    available = [f for f in features if f in df.columns]
    rows = split[available + ['bloom_28d']].dropna(subset=['bloom_28d'])
    X = rows[available].copy().reset_index(drop=True)
    y = rows['bloom_28d'].copy().reset_index(drop=True)
    return X, y, available


def eval_at(y, p, t=0.60):
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


def run_lr(features):
    """Standard LR C=0.05 balanced on given features, evaluate at 0.60."""
    X_tr, y_tr, feats = prepare(train, features)
    X_te, y_te, _     = prepare(test,  features)
    MED = X_tr.median()
    sc = StandardScaler()
    lr = LogisticRegression(C=0.05, class_weight='balanced',
                            max_iter=2000, random_state=42)
    lr.fit(sc.fit_transform(X_tr.fillna(MED)), y_tr)
    p_te = lr.predict_proba(sc.transform(X_te.fillna(MED)))[:, 1]
    m = eval_at(y_te, p_te)
    m['n_feat'] = len(feats)
    return m


# ---------------------------------------------------------------------------
# 7. Run baseline + named strategies
# ---------------------------------------------------------------------------
results = {}

print("\nRunning BASELINE ...")
results['BASELINE (full BASE)'] = run_lr(FULL_BASE)

for name, feats in strategies.items():
    print(f"Running {name} ...")
    results[name] = run_lr(feats)

# ---------------------------------------------------------------------------
# 8. Strategy 5: PCA
# ---------------------------------------------------------------------------
X_tr_full, y_tr_full, full_feats = prepare(train, FULL_BASE)
X_te_full, y_te_full, _          = prepare(test,  FULL_BASE)
MED_full = X_tr_full.median()
X_tr_filled = X_tr_full.fillna(MED_full)
X_te_filled = X_te_full.fillna(MED_full)

for n_comp in [5, 10, 15, 20]:
    name = f'PCA_{n_comp}components'
    print(f"Running {name} ...")
    pipe = Pipeline([
        ('scaler', StandardScaler()),
        ('pca', PCA(n_components=n_comp, random_state=42)),
        ('lr', LogisticRegression(C=0.05, class_weight='balanced',
                                  max_iter=2000, random_state=42)),
    ])
    pipe.fit(X_tr_filled, y_tr_full)
    p_te = pipe.predict_proba(X_te_filled)[:, 1]
    m = eval_at(y_te_full, p_te)
    m['n_feat'] = n_comp
    results[name] = m

# ---------------------------------------------------------------------------
# 9. Strategy 6: LASSO feature selection
# ---------------------------------------------------------------------------
print("Running LASSO_selected ...")
sc_lasso = StandardScaler()
X_tr_s = sc_lasso.fit_transform(X_tr_filled)
X_te_s = sc_lasso.transform(X_te_filled)

lr_l1 = LogisticRegressionCV(
    penalty='l1', solver='liblinear', cv=5,
    class_weight='balanced', max_iter=2000, random_state=42,
    scoring='average_precision',
)
lr_l1.fit(X_tr_s, y_tr_full)
nonzero_mask = np.abs(lr_l1.coef_[0]) > 1e-6
nonzero_features = [full_feats[i] for i, keep in enumerate(nonzero_mask) if keep]
print(f"\nLASSO surviving features ({len(nonzero_features)}/{len(full_feats)}): "
      f"{nonzero_features}")

# Retrain final LR C=0.05 on selected features only
if nonzero_features:
    m_lasso = run_lr(nonzero_features)
    m_lasso['n_feat'] = len(nonzero_features)
else:
    m_lasso = {'auc': 0, 'precision': 0, 'recall': 0, 'f1': 0,
               'tp': 0, 'fp': 0, 'fn': 0, 'n_feat': 0}
results['LASSO_selected'] = m_lasso

# ---------------------------------------------------------------------------
# 10. Print results table sorted by F1
# ---------------------------------------------------------------------------
sorted_results = sorted(results.items(), key=lambda x: x[1]['f1'], reverse=True)

print("\n" + "=" * 100)
print("FEATURE STRATEGY COMPARISON (test 2023-2025, threshold=0.60)")
print("=" * 100)
hdr = (f"{'Strategy':<28}  {'N_feat':>6}  {'AUC':>7}  "
       f"{'Prec@.60':>9}  {'Rec@.60':>8}  {'F1@.60':>7}  {'TP':>4}  {'FP':>4}  {'FN':>4}")
print(hdr)
print("-" * 100)

BASELINE_F1   = results['BASELINE (full BASE)']['f1']
BASELINE_PREC = results['BASELINE (full BASE)']['precision']

for name, m in sorted_results:
    flag = ''
    if name != 'BASELINE (full BASE)':
        beats_f1   = m['f1']        > BASELINE_F1
        beats_prec = m['precision'] > BASELINE_PREC and m['recall'] >= 0.35
        if beats_f1 or beats_prec:
            flag = '  ***'
    is_baseline = '  <-- baseline' if name == 'BASELINE (full BASE)' else ''
    print(f"{name:<28}  {m['n_feat']:>6}  {m['auc']:>7.4f}  "
          f"{m['precision']:>9.3f}  {m['recall']:>8.3f}  {m['f1']:>7.3f}  "
          f"{m['tp']:>4}  {m['fp']:>4}  {m['fn']:>4}{flag}{is_baseline}")

print("\n*** = F1 > {:.3f} OR (Precision > {:.3f} AND Recall >= 0.35)".format(
    BASELINE_F1, BASELINE_PREC))

# Validation check
base = results['BASELINE (full BASE)']
print(f"\nBaseline validation: Prec={base['precision']:.3f} "
      f"Rec={base['recall']:.3f} F1={base['f1']:.3f}  "
      f"(expected Prec~0.465 Rec~0.446 F1~0.455)")

if nonzero_features:
    print(f"\nLASSO feature list ({len(nonzero_features)}): {nonzero_features}")
