"""
hourly_gust_test.py
-------------------
Tests whether hourly wind gust features extracted from ASOS LCD files
improve precision over the baseline 34-feature LR model.

Daily wind speed previously failed (-4pp) because it smooths out mixing
events. A single strong gust (>15 m/s) can break thermal stratification
even when the daily average looks calm. HourlyWindGustSpeed captures
these episodic events.

Run from repo root:
    & "$env:USERPROFILE/anaconda3/python.exe" src/models/experiments/hourly_gust_test.py
"""

import os
import glob
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score

# ---------------------------------------------------------------------------
# 1. Extract hourly gust data from ASOS files
# ---------------------------------------------------------------------------
ASOS_DIR = 'data/raw/asos_wind'

STATION_NAMES = {
    '72504094702': 'KBDR_Bridgeport',
    '72504614707': 'KGON_Groton',
    '72504514758': 'KHVN_NewHaven',
}

MPH_TO_MS = 0.44704

print("Extracting hourly gust data from ASOS files ...")
all_hourly = []
for fname in sorted(os.listdir(ASOS_DIR)):
    if not fname.endswith('.csv'):
        continue
    fpath = os.path.join(ASOS_DIR, fname)
    df = pd.read_csv(fpath, low_memory=False)
    df.columns = [c.strip() for c in df.columns]

    station_id = str(df['STATION'].iloc[0]).strip()
    station_name = STATION_NAMES.get(station_id, station_id)

    hourly_mask = df['REPORT_TYPE'].str.contains('FM-15|FM-16|METAR', na=False)
    hourly = df[hourly_mask].copy()

    if len(hourly) == 0:
        hourly = df[df['HourlyWindSpeed'].notna()].copy()

    hourly['date'] = pd.to_datetime(hourly['DATE'], errors='coerce').dt.normalize()
    hourly['gust_mph'] = pd.to_numeric(hourly['HourlyWindGustSpeed'], errors='coerce')
    hourly['wind_mph'] = pd.to_numeric(hourly['HourlyWindSpeed'], errors='coerce')
    hourly['gust_ms'] = hourly['gust_mph'] * MPH_TO_MS
    hourly['wind_ms'] = hourly['wind_mph'] * MPH_TO_MS
    hourly['station'] = station_name

    all_hourly.append(hourly[['date', 'station', 'gust_ms', 'wind_ms']].dropna(subset=['date']))

hourly_df = pd.concat(all_hourly, ignore_index=True)
print(f"Total hourly records: {len(hourly_df):,}")
print(f"Non-null gusts: {hourly_df['gust_ms'].notna().sum():,} "
      f"({hourly_df['gust_ms'].notna().mean()*100:.1f}%)")
print(f"Mean gust when present: {hourly_df['gust_ms'].mean():.2f} m/s")
print(f"Date range: {hourly_df['date'].min().date()} to {hourly_df['date'].max().date()}")

# ---------------------------------------------------------------------------
# 2. Aggregate to daily gust features
# ---------------------------------------------------------------------------
print("\nAggregating to daily gust features ...")
daily_gust = (
    hourly_df.groupby('date')
    .agg(
        max_gust_ms=('gust_ms', 'max'),
        mean_wind_ms=('wind_ms', 'mean'),
        n_strong_gusts=('gust_ms', lambda x: (x > 10).sum()),
        gust_energy=('gust_ms', lambda x: (x ** 2).sum()),
    )
    .reset_index()
    .sort_values('date')
    .reset_index(drop=True)
)

daily_gust['max_gust_7d']    = daily_gust['max_gust_ms'].rolling(7, min_periods=3).max()
daily_gust['max_gust_3d']    = daily_gust['max_gust_ms'].rolling(3, min_periods=2).max()
daily_gust['n_strong_7d']    = daily_gust['n_strong_gusts'].rolling(7, min_periods=3).sum()
daily_gust['gust_energy_7d'] = daily_gust['gust_energy'].rolling(7, min_periods=3).sum()
daily_gust['calm_hours_7d']  = (
    (daily_gust['mean_wind_ms'] < 3.0).astype(float)
    .rolling(7, min_periods=3).sum()
)

GUST_FEATURES = ['max_gust_7d', 'max_gust_3d', 'n_strong_7d',
                 'gust_energy_7d', 'calm_hours_7d']

daily_gust.to_csv('data/hourly_gust_daily.csv', index=False)
print(f"Saved data/hourly_gust_daily.csv  ({len(daily_gust):,} days)")

# ---------------------------------------------------------------------------
# 3. Load HAB features (same pipeline as baseline)
# ---------------------------------------------------------------------------
print("\nLoading data/hab_features_tidal.csv ...")
hab = pd.read_csv('data/hab_features_tidal.csv')
hab['date'] = pd.to_datetime(hab['date'])

print("Loading data/hab_features_daily.csv ...")
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
    ps['station_name']  = ps['station_name'].astype(str)
    hab = hab.merge(ps, on=['date', 'station_name'], how='left')
    print(f"  percent_saturation coverage: "
          f"{hab['percent_saturation'].notna().mean()*100:.1f}%")

df = hab

# ---------------------------------------------------------------------------
# 4. Recompute rolling features and bloom_28d label
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
# 5. Merge daily gust features
# ---------------------------------------------------------------------------
print("\nMerging daily gust features ...")
df = df.merge(daily_gust[['date'] + GUST_FEATURES], on='date', how='left')

for feat in GUST_FEATURES:
    cov = df[feat].notna().mean() * 100
    print(f"  {feat}: {cov:.1f}% coverage")

# ---------------------------------------------------------------------------
# 6. Splits
# ---------------------------------------------------------------------------
train = df[df['date'].dt.year <= 2019]
val   = df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)]
test  = df[df['date'].dt.year >= 2023]

print(f"\nSplits -- train: {len(train):,} | val: {len(val):,} | test: {len(test):,}")
print(f"Bloom rate -- train: {train['bloom_28d'].mean():.3f} | "
      f"val: {val['bloom_28d'].mean():.3f} | test: {test['bloom_28d'].mean():.3f}")

# ---------------------------------------------------------------------------
# 7. Gust feature coverage and correlations with bloom_28d
# ---------------------------------------------------------------------------
val_test = pd.concat([val, test])

print("\n" + "=" * 75)
print("GUST FEATURE COVERAGE & CORRELATION WITH bloom_28d")
print("=" * 75)
print(f"{'Feature':<20}  {'Train %':>8}  {'Val+Test %':>10}  {'Corr(bloom_28d)':>16}")
print("-" * 75)
for feat in GUST_FEATURES:
    if feat not in df.columns:
        continue
    train_cov = train[feat].notna().mean() * 100
    vt_cov    = val_test[feat].notna().mean() * 100
    corr_df   = val_test[[feat, 'bloom_28d']].dropna()
    corr      = corr_df[feat].corr(corr_df['bloom_28d']) if len(corr_df) > 1 else float('nan')
    print(f"{feat:<20}  {train_cov:>7.1f}%  {vt_cov:>9.1f}%  {corr:>16.4f}")

# ---------------------------------------------------------------------------
# 8. Base feature set (same 34 features as pipeline)
# ---------------------------------------------------------------------------
BASE = [
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
BASE = [f for f in BASE if f in df.columns]
print(f"\nBASE features available: {len(BASE)}")

feature_sets = {
    'BASE (baseline)':           BASE,
    'BASE + max_gust_7d':        BASE + ['max_gust_7d'],
    'BASE + max_gust_3d':        BASE + ['max_gust_3d'],
    'BASE + n_strong_7d':        BASE + ['n_strong_7d'],
    'BASE + gust_energy_7d':     BASE + ['gust_energy_7d'],
    'BASE + calm_hours_7d':      BASE + ['calm_hours_7d'],
    'BASE + all_gusts':          BASE + GUST_FEATURES,
    'BASE + max+calm':           BASE + ['max_gust_7d', 'calm_hours_7d'],
}
feature_sets = {
    k: [f for f in v if f in df.columns]
    for k, v in feature_sets.items()
}

# ---------------------------------------------------------------------------
# 9. Helpers
# ---------------------------------------------------------------------------
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
    X_tr = train[feats].copy()
    y_tr = train['bloom_28d'].copy()
    X_te = test[feats].copy()
    y_te = test['bloom_28d'].copy()

    mask_tr = y_tr.notna()
    mask_te = y_te.notna()
    X_tr = X_tr[mask_tr].reset_index(drop=True)
    y_tr = y_tr[mask_tr].reset_index(drop=True)
    X_te = X_te[mask_te].reset_index(drop=True)
    y_te = y_te[mask_te].reset_index(drop=True)

    MED = X_tr.median().fillna(0)
    sc  = StandardScaler()
    lr  = LogisticRegression(C=0.05, class_weight='balanced',
                             max_iter=2000, random_state=42)
    lr.fit(sc.fit_transform(X_tr.fillna(MED)), y_tr)
    p_te = lr.predict_proba(sc.transform(X_te.fillna(MED)))[:, 1]
    m = eval_at(y_te, p_te)
    m['n_feat'] = len(feats)
    return m


# ---------------------------------------------------------------------------
# 10. Run all feature sets
# ---------------------------------------------------------------------------
print("\nRunning feature set evaluations ...")
results = {}
for name, feats in feature_sets.items():
    print(f"  {name} ({len(feats)} features) ...")
    results[name] = run_lr(feats)

# ---------------------------------------------------------------------------
# 11. Print results table sorted by F1
# ---------------------------------------------------------------------------
sorted_results = sorted(results.items(), key=lambda x: x[1]['f1'], reverse=True)

BASELINE_PREC = results['BASE (baseline)']['precision']
BASELINE_F1   = results['BASE (baseline)']['f1']
BASELINE_REC  = results['BASE (baseline)']['recall']

print("\n" + "=" * 108)
print("HOURLY GUST FEATURE TEST (test 2023-2025, LR C=0.05, threshold=0.60)")
print("=" * 108)
hdr = (f"{'Feature Set':<32}  {'N':>4}  {'AUC':>7}  "
       f"{'Prec@.60':>9}  {'Rec@.60':>8}  {'F1@.60':>7}  {'TP':>4}  {'FP':>4}  {'FN':>4}")
print(hdr)
print("-" * 108)

for name, m in sorted_results:
    flag = ''
    if name != 'BASE (baseline)':
        beats_f1   = m['f1'] > BASELINE_F1 + 0.010
        beats_prec = (m['precision'] > BASELINE_PREC + 0.020) and (m['recall'] >= 0.35)
        if beats_f1 or beats_prec:
            flag = '  ***'
    marker = '  <-- baseline' if name == 'BASE (baseline)' else ''
    print(f"{name:<32}  {m['n_feat']:>4}  {m['auc']:>7.4f}  "
          f"{m['precision']:>9.3f}  {m['recall']:>8.3f}  {m['f1']:>7.3f}  "
          f"{m['tp']:>4}  {m['fp']:>4}  {m['fn']:>4}{flag}{marker}")

print(f"\n*** = F1 > baseline+0.010  OR  Prec > baseline+0.020 (with Rec >= 0.35)")

base = results['BASE (baseline)']
print(f"\nBaseline check: Prec={base['precision']:.3f}  Rec={base['recall']:.3f}  "
      f"F1={base['f1']:.3f}  AUC={base['auc']:.3f}")
print(f"  Expected:     Prec~0.465  Rec~0.446  F1~0.455  AUC~0.814")
