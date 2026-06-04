"""
wqp_nutrient_test.py
--------------------
Tests whether adding CT DEEP in-Sound nutrient data from EPA WQP
improves precision on the test set (2023-2025).

WQP data covers only 2020-2025 for eastern LIS stations (09, C2, D3, E1,
F2, H2, H4, K2). Training rows (<=2019) are all NaN -> median imputed.

Run from repo root:
    & "$env:USERPROFILE/anaconda3/python.exe" src/models/wqp_nutrient_test.py
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
# 1. Load + merge (same pipeline as baseline)
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
# 3. Merge WQP nutrient data
# ---------------------------------------------------------------------------
print("\nMerging WQP nutrient data ...")

# Way 1: station-specific (eastern stations only get values)
wqp_stn = pd.read_csv('data/raw/ctdeep_wqp_nutrients.csv')
wqp_stn['date'] = pd.to_datetime(wqp_stn['date'])
df = df.merge(
    wqp_stn.rename(columns={
        'wqp_nox': 'wqp_nox_stn',
        'wqp_dip': 'wqp_dip_stn',
        'wqp_tn':  'wqp_tn_stn',
        'wqp_tp':  'wqp_tp_stn',
    }),
    on=['station_name', 'date'], how='left'
)

# Way 2: sound-wide daily mean (all stations get eastern-station mean)
wqp_sound = pd.read_csv('data/raw/ctdeep_wqp_sound_mean.csv')
wqp_sound['date'] = pd.to_datetime(wqp_sound['date'])
df = df.merge(wqp_sound, on='date', how='left')

# Rolling means of sound-wide signal
df = df.sort_values(['station_name', 'date']).reset_index(drop=True)
for col in ['wqp_nox_sound', 'wqp_dip_sound', 'wqp_tn_sound']:
    df[f'{col}_roll3'] = df.groupby('station_name')[col].transform(
        lambda x: x.rolling(3, min_periods=1).mean()
    )

# ---------------------------------------------------------------------------
# 4. Splits
# ---------------------------------------------------------------------------
train = df[df['date'].dt.year <= 2019]
val   = df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)]
test  = df[df['date'].dt.year >= 2023]

print(f"\nSplits -- train: {len(train):,} | val: {len(val):,} | test: {len(test):,}")
print(f"Bloom rate -- train: {train['bloom_28d'].mean():.3f} | "
      f"val: {val['bloom_28d'].mean():.3f} | test: {test['bloom_28d'].mean():.3f}")

# ---------------------------------------------------------------------------
# 5. WQP coverage stats and correlations with bloom_28d
# ---------------------------------------------------------------------------
WQP_ALL_COLS = [
    'wqp_nox_stn', 'wqp_dip_stn', 'wqp_tn_stn', 'wqp_tp_stn',
    'wqp_nox_sound', 'wqp_dip_sound', 'wqp_tn_sound', 'wqp_tp_sound',
    'wqp_nox_sound_roll3', 'wqp_dip_sound_roll3', 'wqp_tn_sound_roll3',
]
WQP_ALL_COLS = [c for c in WQP_ALL_COLS if c in df.columns]

val_test = pd.concat([val, test])
total_val_test = len(val_test)

print("\n" + "=" * 70)
print("WQP FEATURE COVERAGE & CORRELATION WITH bloom_28d")
print("=" * 70)
print(f"{'Feature':<28}  {'Train %':>8}  {'Val+Test %':>10}  {'Corr(bloom_28d)':>16}")
print("-" * 70)
for col in WQP_ALL_COLS:
    if col not in df.columns:
        continue
    train_cov   = train[col].notna().mean() * 100
    vt_cov      = val_test[col].notna().mean() * 100
    corr_val    = val_test[[col, 'bloom_28d']].dropna()
    corr        = corr_val[col].corr(corr_val['bloom_28d']) if len(corr_val) > 1 else float('nan')
    print(f"{col:<28}  {train_cov:>7.1f}%  {vt_cov:>9.1f}%  {corr:>16.4f}")

# Validate sound-wide coverage expectation (~16%)
sound_cov = val_test['wqp_nox_sound'].notna().mean() * 100 if 'wqp_nox_sound' in df.columns else 0
print(f"\nSound-wide coverage (val+test): {sound_cov:.1f}%  (expected ~16%)")

# ---------------------------------------------------------------------------
# 6. Base feature set (same 34 features as pipeline)
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

WQP_SOUND = [c for c in ['wqp_nox_sound', 'wqp_dip_sound', 'wqp_tn_sound', 'wqp_tp_sound']
             if c in df.columns]
WQP_ROLLS = [c for c in ['wqp_nox_sound_roll3', 'wqp_dip_sound_roll3', 'wqp_tn_sound_roll3']
             if c in df.columns]
WQP_STN   = [c for c in ['wqp_nox_stn', 'wqp_dip_stn', 'wqp_tn_stn']
             if c in df.columns]

feature_sets = {
    'BASE (baseline)':           BASE,
    'BASE + wqp_nox_sound':      BASE + ['wqp_nox_sound'],
    'BASE + wqp_dip_sound':      BASE + ['wqp_dip_sound'],
    'BASE + wqp_tn_sound':       BASE + ['wqp_tn_sound'],
    'BASE + wqp_nox+dip_sound':  BASE + ['wqp_nox_sound', 'wqp_dip_sound'],
    'BASE + all_wqp_sound':      BASE + WQP_SOUND,
    'BASE + wqp_rolls':          BASE + WQP_ROLLS,
    'BASE + all_wqp_sound+roll': BASE + WQP_SOUND + WQP_ROLLS,
    'BASE + wqp_stn_nox+dip':   BASE + ['wqp_nox_stn', 'wqp_dip_stn'],
}
# Filter to only cols that actually exist
feature_sets = {
    k: [f for f in v if f in df.columns]
    for k, v in feature_sets.items()
}

# ---------------------------------------------------------------------------
# 7. Helpers
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

    # Drop rows with missing label
    mask_tr = y_tr.notna()
    mask_te = y_te.notna()
    X_tr, y_tr = X_tr[mask_tr].reset_index(drop=True), y_tr[mask_tr].reset_index(drop=True)
    X_te, y_te = X_te[mask_te].reset_index(drop=True), y_te[mask_te].reset_index(drop=True)

    MED = X_tr.median().fillna(0)   # WQP cols are 100% NaN in train -> median=NaN; use 0
    sc  = StandardScaler()
    lr  = LogisticRegression(C=0.05, class_weight='balanced',
                             max_iter=2000, random_state=42)
    lr.fit(sc.fit_transform(X_tr.fillna(MED)), y_tr)
    p_te = lr.predict_proba(sc.transform(X_te.fillna(MED)))[:, 1]
    m = eval_at(y_te, p_te)
    m['n_feat'] = len(feats)
    return m


# ---------------------------------------------------------------------------
# 8. Run all feature sets
# ---------------------------------------------------------------------------
results = {}
for name, feats in feature_sets.items():
    print(f"Running: {name} ({len(feats)} features) ...")
    results[name] = run_lr(feats)

# ---------------------------------------------------------------------------
# 9. Print results table sorted by F1
# ---------------------------------------------------------------------------
sorted_results = sorted(results.items(), key=lambda x: x[1]['f1'], reverse=True)

BASELINE_PREC = results['BASE (baseline)']['precision']
BASELINE_F1   = results['BASE (baseline)']['f1']
BASELINE_REC  = results['BASE (baseline)']['recall']

print("\n" + "=" * 105)
print("WQP NUTRIENT FEATURE TEST (test 2023-2025, LR C=0.05, threshold=0.60)")
print("=" * 105)
hdr = (f"{'Feature Set':<32}  {'N':>4}  {'AUC':>7}  "
       f"{'Prec@.60':>9}  {'Rec@.60':>8}  {'F1@.60':>7}  {'TP':>4}  {'FP':>4}  {'FN':>4}")
print(hdr)
print("-" * 105)

for name, m in sorted_results:
    flag = ''
    if name != 'BASE (baseline)':
        beats_prec = (m['precision'] > BASELINE_PREC) and (m['recall'] >= 0.35)
        beats_f1   = m['f1'] > BASELINE_F1
        if beats_prec or beats_f1:
            flag = '  ***'
    marker = '  <-- baseline' if name == 'BASE (baseline)' else ''
    print(f"{name:<32}  {m['n_feat']:>4}  {m['auc']:>7.4f}  "
          f"{m['precision']:>9.3f}  {m['recall']:>8.3f}  {m['f1']:>7.3f}  "
          f"{m['tp']:>4}  {m['fp']:>4}  {m['fn']:>4}{flag}{marker}")

print(f"\n*** = Prec > {BASELINE_PREC:.3f} (with Rec >= 0.35)  OR  F1 > {BASELINE_F1:.3f}")

base = results['BASE (baseline)']
print(f"\nBaseline check: Prec={base['precision']:.3f}  Rec={base['recall']:.3f}  "
      f"F1={base['f1']:.3f}  AUC={base['auc']:.3f}")
print(f"  Expected:     Prec~0.465  Rec~0.446  F1~0.455  AUC~0.814")
