"""
narragansett_transfer_test.py
------------------------------
Tests Narragansett Bay weekly nutrient data (BCO-DMO, 1959-2019) as a
regional estuarine nutrient proxy for the CT DEEP bloom model.

Hypothesis: PO4 and NO3_2 at Narragansett Bay in week X correlates with
estuarine nutrient conditions at LIS stations 1-2 weeks later (transport lag).
Also tests Secchi depth as a water clarity proxy.

Key limitation: NBPTS ends 2019. Val (2020-2022) and test (2023-2025) rows
get NaN for all nb_ features, which are then median-imputed to the training
median. So NBPTS features can only improve training-set representations, not
live inference.

Run from repo root:
    & "$env:USERPROFILE/anaconda3/python.exe" src/models/experiments/narragansett_transfer_test.py
"""

import glob
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score

# ---------------------------------------------------------------------------
# 1. Load HAB features (same pipeline as all other experiments)
# ---------------------------------------------------------------------------
print("Loading data/hab_features_tidal.csv ...")
hab = pd.read_csv('data/hab_features_tidal.csv')
hab['date'] = pd.to_datetime(hab['date'])

print("Loading sal_lags from data/hab_features_daily.csv ...")
daily = pd.read_csv('data/hab_features_daily.csv')
daily['date'] = pd.to_datetime(daily['date'])
for col in ['sal_lag2', 'sal_lag3', 'sal_lag4']:
    if col not in hab.columns:
        hab = hab.merge(daily[['date', 'station_name', col]],
                        on=['date', 'station_name'], how='left')

if 'percent_saturation' not in hab.columns:
    print("Loading percent_saturation from data/raw/deep_wq_extra/ ...")
    frames = []
    for f in sorted(glob.glob('data/raw/deep_wq_extra/deep_wq_S_*.csv')):
        frames.append(pd.read_csv(
            f, skiprows=[1],
            usecols=['station_name', 'time', 'percent_saturation']))
    ps = pd.concat(frames, ignore_index=True)
    ps = ps[ps['station_name'].notna()].copy()
    ps['station_name'] = ps['station_name'].astype(str)
    ps['date'] = pd.to_datetime(ps['time'], utc=True).dt.tz_localize(None).dt.normalize()
    ps['percent_saturation'] = pd.to_numeric(ps['percent_saturation'], errors='coerce')
    ps = (ps.dropna(subset=['percent_saturation'])
            .groupby(['date', 'station_name'], as_index=False)['percent_saturation'].mean())
    hab['station_name'] = hab['station_name'].astype(str)
    hab = hab.merge(ps, on=['date', 'station_name'], how='left')
    print(f"  percent_saturation coverage: "
          f"{hab['percent_saturation'].notna().mean()*100:.1f}%")

print("Merging max_gust_3d from data/gust_features_daily.csv ...")
gust = pd.read_csv('data/gust_features_daily.csv', usecols=['date', 'max_gust_3d'])
gust['date'] = pd.to_datetime(gust['date'])
hab = hab.merge(gust, on='date', how='left')
print(f"  max_gust_3d coverage: {hab['max_gust_3d'].notna().mean()*100:.1f}%")

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
    idx   = grp.index
    dates = grp['date'].values
    chl   = grp['Chlorophyll'].values
    labels = np.zeros(len(grp), dtype=int)
    for i in range(len(grp)):
        mask = (dates > dates[i]) & (dates <= dates[i] + np.timedelta64(28, 'D'))
        if mask.any() and (chl[mask] > 10).any():
            labels[i] = 1
    df.loc[idx, 'bloom_28d'] = labels

# ---------------------------------------------------------------------------
# 3. Process NBPTS Narragansett Bay data
# ---------------------------------------------------------------------------
print("\nProcessing NBPTS Narragansett Bay data ...")
nb = pd.read_csv('data/raw/nbpts_narragansett.csv', low_memory=False)
nb = nb.replace('nd', np.nan)
for col in nb.columns:
    if col not in ['year', 'week']:
        nb[col] = pd.to_numeric(nb[col], errors='coerce')

# Convert year+week to date (Wednesday midweek)
nb['date'] = pd.to_datetime(
    nb['year'].astype(str) + '-W' + nb['week'].astype(str).str.zfill(2) + '-3',
    format='%G-W%V-%u', errors='coerce'
)
nb = nb.dropna(subset=['date']).sort_values('date').reset_index(drop=True)

print(f"  NBPTS records: {len(nb)} ({nb['date'].min().date()} to {nb['date'].max().date()})")
for col in ['PO4', 'NO3_2', 'ChlA', 'Secchi_depth', 'Temperature_SURF']:
    cov = nb[col].notna().mean() * 100
    print(f"    {col}: {cov:.1f}% coverage")

# Rolling means (~4 and ~8 weeks) and 2/4-week lags
for col in ['PO4', 'NO3_2', 'ChlA', 'Secchi_depth', 'Temperature_SURF']:
    nb[f'nb_{col}_roll4'] = nb[col].rolling(4, min_periods=2).mean()
    nb[f'nb_{col}_roll8'] = nb[col].rolling(8, min_periods=4).mean()
    nb[f'nb_{col}_lag2w'] = nb[col].shift(2)
    nb[f'nb_{col}_lag4w'] = nb[col].shift(4)

# Anomaly: deviation from weekly climatology
for col in ['PO4', 'NO3_2', 'ChlA']:
    weekly_mean = nb.groupby('week')[col].transform('mean')
    nb[f'nb_{col}_anom'] = nb[col] - weekly_mean

nb.to_csv('data/raw/nbpts_processed.csv', index=False)
print("  Saved data/raw/nbpts_processed.csv")

# ---------------------------------------------------------------------------
# 4. Merge NBPTS onto HAB by nearest date (tolerance 7 days)
# ---------------------------------------------------------------------------
print("\nMerging NBPTS onto HAB features (merge_asof, tolerance=7d) ...")
nb_cols = [c for c in nb.columns if c.startswith('nb_')]
nb_merge = nb[['date'] + nb_cols].copy().sort_values('date')

df = df.sort_values('date').reset_index(drop=True)
df = pd.merge_asof(df, nb_merge, on='date',
                   tolerance=pd.Timedelta('7 days'), direction='nearest')
df = df.sort_values(['station_name', 'date']).reset_index(drop=True)

# Coverage by split
train_mask = df['date'].dt.year <= 2019
val_mask   = (df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)
test_mask  = df['date'].dt.year >= 2023

print("\nNBPTS coverage per split:")
for label, mask in [('Train (<=2019)', train_mask),
                    ('Val (2020-2022)', val_mask),
                    ('Test (2023-2025)', test_mask)]:
    sub = df[mask]
    if len(sub) == 0:
        continue
    cov = sub['nb_PO4_roll4'].notna().mean() * 100
    print(f"  {label}: {cov:.1f}% have nb_PO4_roll4  (n={len(sub):,})")

# ---------------------------------------------------------------------------
# 5. Correlation of nb_ features with bloom_28d (training period only,
#    where NBPTS actually has values)
# ---------------------------------------------------------------------------
train_df = df[train_mask].copy()
print("\n" + "=" * 70)
print("NBPTS FEATURE CORRELATIONS WITH bloom_28d  (training period <=2019)")
print("=" * 70)
print(f"{'Feature':<26}  {'Coverage%':>9}  {'Corr(bloom_28d)':>16}")
print("-" * 70)
for col in sorted(nb_cols):
    if col not in df.columns:
        continue
    cov  = train_df[col].notna().mean() * 100
    pair = train_df[[col, 'bloom_28d']].dropna()
    corr = pair[col].corr(pair['bloom_28d']) if len(pair) > 1 else float('nan')
    print(f"{col:<26}  {cov:>8.1f}%  {corr:>16.4f}")

# ---------------------------------------------------------------------------
# 6. Feature sets
# ---------------------------------------------------------------------------
BASE = [
    'Chlorophyll', 'chl_lag1', 'chl_lag2', 'chl_lag3', 'chl_lag4',
    'chl_roll3_mean', 'chl_roll6_mean', 'chl_roll9_mean',
    'chl_roll14_mean', 'chl_roll21_mean', 'chl_trend',
    'chl_anomaly', 'chl_climatology',
    'do_lag1', 'temp_lag1', 'sal_lag1',
    'sal_lag2', 'sal_lag3', 'sal_lag4',
    'sea_water_temperature', 'sea_water_salinity',
    'oxygen_concentration_in_sea_water',
    'month', 'latitude_x', 'longitude_x',
    'nox_lag2', 'dip_lag2', 'dip_change', 'dip_x_month',
    'neighbor_chl3_mean', 'neighbor_chl3_lag1',
    'tidal_gt_anom', 'tidal_msl_anom',
    'percent_saturation',
    'max_gust_3d',
]
BASE = [f for f in BASE if f in df.columns]
print(f"\nBASE features available: {len(BASE)}")

NB_PRIORITY = [
    'nb_PO4_roll4', 'nb_PO4_roll8', 'nb_PO4_lag2w', 'nb_PO4_lag4w',
    'nb_NO3_2_roll4', 'nb_NO3_2_roll8', 'nb_NO3_2_lag2w',
    'nb_PO4_anom', 'nb_NO3_2_anom',
    'nb_ChlA_roll4', 'nb_Secchi_depth_roll4',
    'nb_Temperature_SURF_roll4',
]
NB_PRIORITY = [f for f in NB_PRIORITY if f in df.columns]

feature_sets = {
    'BASE (baseline)':          BASE,
    'BASE + nb_PO4_roll4':      BASE + ['nb_PO4_roll4'],
    'BASE + nb_PO4_roll8':      BASE + ['nb_PO4_roll8'],
    'BASE + nb_NO3_2_roll4':    BASE + ['nb_NO3_2_roll4'],
    'BASE + nb_NO3_2_roll8':    BASE + ['nb_NO3_2_roll8'],
    'BASE + nb_PO4_anom':       BASE + ['nb_PO4_anom'],
    'BASE + nb_NO3_2_anom':     BASE + ['nb_NO3_2_anom'],
    'BASE + nb_PO4_lag2w':      BASE + ['nb_PO4_lag2w'],
    'BASE + nb_PO4_lag4w':      BASE + ['nb_PO4_lag4w'],
    'BASE + nb_PO4+NO3_roll4':  BASE + ['nb_PO4_roll4', 'nb_NO3_2_roll4'],
    'BASE + nb_Secchi_roll4':   BASE + ['nb_Secchi_depth_roll4'],
    'BASE + nb_ChlA_roll4':     BASE + ['nb_ChlA_roll4'],
    'BASE + all_nb_priority':   BASE + NB_PRIORITY,
}
feature_sets = {
    k: [f for f in v if f in df.columns]
    for k, v in feature_sets.items()
}

# ---------------------------------------------------------------------------
# 7. Helpers
# ---------------------------------------------------------------------------
train = df[train_mask]
val   = df[val_mask]
test  = df[test_mask]

print(f"\nSplits -- train: {len(train):,} | val: {len(val):,} | test: {len(test):,}")
print(f"Bloom rate -- train: {train['bloom_28d'].mean():.3f} | "
      f"val: {val['bloom_28d'].mean():.3f} | test: {test['bloom_28d'].mean():.3f}")


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
    feats = [f for f in features if f in df.columns]
    X_tr = train[feats].copy(); y_tr = train['bloom_28d'].copy()
    X_v  = val[feats].copy();   y_v  = val['bloom_28d'].copy()
    X_te = test[feats].copy();  y_te = test['bloom_28d'].copy()

    mask_tr = y_tr.notna()
    mask_v  = y_v.notna()
    mask_te = y_te.notna()
    X_tr, y_tr = X_tr[mask_tr].reset_index(drop=True), y_tr[mask_tr].reset_index(drop=True)
    X_v,  y_v  = X_v[mask_v].reset_index(drop=True),  y_v[mask_v].reset_index(drop=True)
    X_te, y_te = X_te[mask_te].reset_index(drop=True), y_te[mask_te].reset_index(drop=True)

    # nb_ cols are 100% NaN in val/test — median of training is used
    MED = X_tr.median().fillna(0)
    sc  = StandardScaler()
    lr  = LogisticRegression(C=0.05, class_weight='balanced',
                             max_iter=2000, random_state=42)
    lr.fit(sc.fit_transform(X_tr.fillna(MED)), y_tr)

    p_v  = lr.predict_proba(sc.transform(X_v.fillna(MED)))[:, 1]
    p_te = lr.predict_proba(sc.transform(X_te.fillna(MED)))[:, 1]

    m_val  = eval_at(y_v,  p_v)
    m_test = eval_at(y_te, p_te)
    m_test['val_auc'] = m_val['auc']
    m_test['val_f1']  = m_val['f1']
    m_test['n_feat']  = len(feats)
    return m_test


# ---------------------------------------------------------------------------
# 8. Run all feature sets
# ---------------------------------------------------------------------------
results = {}
for name, feats in feature_sets.items():
    print(f"Running: {name} ({len(feats)} features) ...")
    results[name] = run_lr(feats)

# ---------------------------------------------------------------------------
# 9. Print results sorted by test F1
# ---------------------------------------------------------------------------
sorted_results = sorted(results.items(), key=lambda x: x[1]['f1'], reverse=True)

BASE_M = results['BASE (baseline)']
BASELINE_PREC = BASE_M['precision']
BASELINE_F1   = BASE_M['f1']

print("\n" + "=" * 120)
print("NARRAGANSETT BAY TRANSFER TEST  (test 2023-2025, LR C=0.05, threshold=0.60)")
print("Note: nb_ features are NaN in val/test — median-imputed to training mean.")
print("=" * 120)
hdr = (f"{'Feature Set':<32}  {'N':>4}  {'AUC':>7}  "
       f"{'Prec@.60':>9}  {'Rec@.60':>8}  {'F1@.60':>7}  "
       f"{'TP':>4}  {'FP':>4}  {'FN':>4}  {'ValAUC':>8}  {'ValF1':>7}")
print(hdr)
print("-" * 120)

for name, m in sorted_results:
    flag = ''
    if name != 'BASE (baseline)':
        if m['f1'] > BASELINE_F1 + 0.010 or m['precision'] > BASELINE_PREC + 0.020:
            flag = '  ***'
    marker = '  <-- baseline' if name == 'BASE (baseline)' else ''
    print(f"{name:<32}  {m['n_feat']:>4}  {m['auc']:>7.4f}  "
          f"{m['precision']:>9.3f}  {m['recall']:>8.3f}  {m['f1']:>7.3f}  "
          f"{m['tp']:>4}  {m['fp']:>4}  {m['fn']:>4}  "
          f"{m['val_auc']:>8.4f}  {m['val_f1']:>7.3f}{flag}{marker}")

print(f"\n*** = F1 > baseline + 0.010  OR  Prec > baseline + 0.020")
print(f"\nBaseline check: Prec={BASE_M['precision']:.3f}  Rec={BASE_M['recall']:.3f}  "
      f"F1={BASE_M['f1']:.3f}  AUC={BASE_M['auc']:.3f}")
print(f"  Expected:     Prec=0.500  Rec=0.486  F1=0.493  AUC=0.815")

print("\n" + "=" * 70)
print("DEPLOYABILITY NOTE")
print("=" * 70)
print("NBPTS data ends 2019. All nb_ features are NaN for val/test and")
print("are imputed to the training median (effectively the historical mean).")
print("Any test-set improvement reflects only imputation noise, not true")
print("signal transfer. These features CANNOT be used for live inference.")
print("Val AUC comparison above shows if they aid training representations.")
