"""
t98_nutrient_test.py
---------------------
Tests URI GSO T-98 weekly nutrient data (Narragansett Bay, 1976-2025) as a
regional estuarine nutrient proxy for the CT DEEP bloom model.

Key advantage over NBPTS: T-98 extends to January 2025, so val (2020-2022)
AND test (2023-2025) rows receive REAL nutrient values rather than being
median-imputed from training.

Run from repo root:
    & "$env:USERPROFILE/anaconda3/python.exe" src/models/experiments/t98_nutrient_test.py
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
# 3. Parse T-98 data
# ---------------------------------------------------------------------------
print("\nParsing T-98 GSO dock data ...")
t98_path = 'data/raw/narragansett/T-98-GSO-dock-grab-sample-to-share.xlsx'
t98 = pd.read_excel(t98_path, header=2)

# Assign column names based on known T-98 layout
expected_cols = ['date', 'yr_day', 'chl_fluor', 'chl_dcmu', 'salinity', 'do_mg',
                 'temp', 'no3_2', 'sio4', 'po4', 'nh4', 'tdn',
                 'toc', 'toc2', 'toc3', 'unknown1', 'unknown2']
if len(t98.columns) >= len(expected_cols):
    col_map = {t98.columns[i]: expected_cols[i] for i in range(len(expected_cols))}
    t98 = t98.rename(columns=col_map)
else:
    print(f"  WARNING: got {len(t98.columns)} columns, expected {len(expected_cols)}")
    print(f"  Actual columns: {list(t98.columns)}")

t98['date'] = pd.to_datetime(t98['date'], errors='coerce')
t98 = t98.dropna(subset=['date'])
t98 = t98[t98['date'].dt.year >= 1976].sort_values('date').reset_index(drop=True)

for col in ['po4', 'no3_2', 'nh4', 'chl_fluor', 'salinity', 'do_mg', 'temp', 'sio4']:
    if col in t98.columns:
        t98[col] = pd.to_numeric(t98[col], errors='coerce')

print(f"  T-98 records: {len(t98)} ({t98['date'].min().date()} to {t98['date'].max().date()})")
for col in ['po4', 'no3_2', 'nh4', 'chl_fluor']:
    if col in t98.columns:
        cov = t98[col].notna().mean() * 100
        print(f"    {col}: {cov:.1f}% coverage")

# Rolling features and lags (computed on the weekly T-98 series)
for col in ['po4', 'no3_2', 'nh4', 'chl_fluor']:
    if col not in t98.columns:
        continue
    t98[f't98_{col}_roll4w']  = t98[col].rolling(4,  min_periods=2).mean()
    t98[f't98_{col}_roll8w']  = t98[col].rolling(8,  min_periods=4).mean()
    t98[f't98_{col}_roll13w'] = t98[col].rolling(13, min_periods=6).mean()
    t98[f't98_{col}_lag2w']   = t98[col].shift(2)
    t98[f't98_{col}_lag4w']   = t98[col].shift(4)

# Anomaly vs weekly climatology
t98['week'] = t98['date'].dt.isocalendar().week.astype(int)
for col in ['po4', 'no3_2']:
    if col in t98.columns:
        weekly_clim = t98.groupby('week')[col].transform('mean')
        t98[f't98_{col}_anom'] = t98[col] - weekly_clim

t98.to_csv('data/raw/t98_processed.csv', index=False)
print("  Saved data/raw/t98_processed.csv")

# ---------------------------------------------------------------------------
# 4. Merge T-98 onto HAB (nearest within 14 days, backward)
# ---------------------------------------------------------------------------
print("\nMerging T-98 onto HAB (merge_asof, tolerance=14d, backward) ...")
t98_feature_cols = [c for c in t98.columns if c.startswith('t98_')]
t98_merge = t98[['date'] + t98_feature_cols].copy().sort_values('date')

df = df.sort_values('date').reset_index(drop=True)
df = pd.merge_asof(df, t98_merge, on='date',
                   tolerance=pd.Timedelta('14 days'),
                   direction='backward')
df = df.sort_values(['station_name', 'date']).reset_index(drop=True)

# Coverage by split — critical check: val/test should have real values
train_mask = df['date'].dt.year <= 2019
val_mask   = (df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)
test_mask  = df['date'].dt.year >= 2023

print("\nT-98 coverage per split (po4_roll4w as representative):")
ref_col = 't98_po4_roll4w' if 't98_po4_roll4w' in df.columns else t98_feature_cols[0]
for label, mask in [('Train (<=2019)', train_mask),
                    ('Val  (2020-2022)', val_mask),
                    ('Test (2023-2025)', test_mask)]:
    sub = df[mask]
    if len(sub) == 0:
        continue
    cov = sub[ref_col].notna().mean() * 100
    print(f"  {label}: {cov:.1f}% have {ref_col}  (n={len(sub):,})")

# ---------------------------------------------------------------------------
# 5. Correlations with bloom_28d
# ---------------------------------------------------------------------------
train_df = df[train_mask].copy()
print("\n" + "=" * 70)
print("T-98 FEATURE CORRELATIONS WITH bloom_28d  (training period <=2019)")
print("=" * 70)
print(f"{'Feature':<28}  {'Coverage%':>9}  {'Corr(bloom_28d)':>16}")
print("-" * 70)
for col in sorted(t98_feature_cols):
    if col not in df.columns:
        continue
    cov  = train_df[col].notna().mean() * 100
    pair = train_df[[col, 'bloom_28d']].dropna()
    corr = pair[col].corr(pair['bloom_28d']) if len(pair) > 1 else float('nan')
    print(f"{col:<28}  {cov:>8.1f}%  {corr:>16.4f}")

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

T98_PRIORITY = [
    't98_po4_roll4w', 't98_po4_roll8w', 't98_po4_roll13w',
    't98_no3_2_roll4w', 't98_no3_2_roll8w',
    't98_po4_anom', 't98_no3_2_anom',
    't98_po4_lag2w', 't98_po4_lag4w',
    't98_no3_2_lag2w', 't98_no3_2_lag4w',
    't98_nh4_roll4w',
]
T98_PRIORITY = [f for f in T98_PRIORITY if f in df.columns]

feature_sets = {
    'BASE (baseline)':               BASE,
    'BASE + t98_po4_roll4w':         BASE + ['t98_po4_roll4w'],
    'BASE + t98_po4_roll8w':         BASE + ['t98_po4_roll8w'],
    'BASE + t98_po4_roll13w':        BASE + ['t98_po4_roll13w'],
    'BASE + t98_no3_2_roll4w':       BASE + ['t98_no3_2_roll4w'],
    'BASE + t98_no3_2_roll8w':       BASE + ['t98_no3_2_roll8w'],
    'BASE + t98_po4_anom':           BASE + ['t98_po4_anom'],
    'BASE + t98_no3_2_anom':         BASE + ['t98_no3_2_anom'],
    'BASE + t98_po4+no3_roll4w':     BASE + ['t98_po4_roll4w', 't98_no3_2_roll4w'],
    'BASE + t98_po4+no3_roll8w':     BASE + ['t98_po4_roll8w', 't98_no3_2_roll8w'],
    'BASE + all_t98_priority':       BASE + T98_PRIORITY,
}
feature_sets = {
    k: [f for f in v if f in df.columns]
    for k, v in feature_sets.items()
}

# ---------------------------------------------------------------------------
# 7. Train/val/test splits
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

    # Use training median for any remaining NaNs (val/test t98_ cols should be real)
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

print("\n" + "=" * 125)
print("T-98 NARRAGANSETT NUTRIENT TEST  (test 2023-2025, LR C=0.05, threshold=0.60)")
print("Unlike NBPTS, T-98 extends to Jan 2025: val AND test receive real nutrient values.")
print("=" * 125)
hdr = (f"{'Feature Set':<36}  {'N':>4}  {'AUC':>7}  "
       f"{'Prec@.60':>9}  {'Rec@.60':>8}  {'F1@.60':>7}  "
       f"{'TP':>4}  {'FP':>4}  {'FN':>4}  {'ValAUC':>8}  {'ValF1':>7}")
print(hdr)
print("-" * 125)

for name, m in sorted_results:
    flag = ''
    if name != 'BASE (baseline)':
        if m['f1'] > BASELINE_F1 + 0.010 or m['precision'] > BASELINE_PREC + 0.020:
            flag = '  ***'
    marker = '  <-- baseline' if name == 'BASE (baseline)' else ''
    print(f"{name:<36}  {m['n_feat']:>4}  {m['auc']:>7.4f}  "
          f"{m['precision']:>9.3f}  {m['recall']:>8.3f}  {m['f1']:>7.3f}  "
          f"{m['tp']:>4}  {m['fp']:>4}  {m['fn']:>4}  "
          f"{m['val_auc']:>8.4f}  {m['val_f1']:>7.3f}{flag}{marker}")

print(f"\n*** = F1 > baseline + 0.010  OR  Prec > baseline + 0.020")
print(f"\nBaseline check: Prec={BASE_M['precision']:.3f}  Rec={BASE_M['recall']:.3f}  "
      f"F1={BASE_M['f1']:.3f}  AUC={BASE_M['auc']:.3f}")
print(f"  Expected:     Prec=0.500  Rec=0.486  F1=0.493  AUC=0.815")
