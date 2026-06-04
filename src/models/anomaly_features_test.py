"""
anomaly_features_test.py
------------------------
Tests whether physical anomaly features (temp_anomaly, sal_anomaly, do_anomaly)
improve precision / F1 over the current baseline.

Anomalies = deviation from long-term station-month climatological mean.
Correlations with bloom_28d (100% coverage):
  do_anomaly:   r=-0.125  (strongest)
  temp_anomaly: r=-0.052
  sal_anomaly:  r=-0.052

Baseline (with percent_saturation): Prec=0.465 Rec=0.446 F1=0.455 AUC=0.814

Run from repo root:
    & "$env:USERPROFILE/anaconda3/python.exe" src/models/anomaly_features_test.py
"""

import glob
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from io import StringIO
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_auc_score, f1_score, precision_score, recall_score,
)

# ---------------------------------------------------------------------------
# 1. Load data + merge sal_lags and percent_saturation
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

# percent_saturation lives only in the raw ERDDAP surface (depth_code='S') extracts
if 'percent_saturation' not in hab.columns:
    print("Loading percent_saturation from data/raw/deep_wq_extra/deep_wq_S_*.csv ...")
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
        pct_daily = (pct_df.dropna(subset=['percent_saturation'])
                     .groupby(['station_name', 'date'])['percent_saturation']
                     .mean().reset_index())
        hab['station_name'] = hab['station_name'].astype(str)
        pct_daily['station_name'] = pct_daily['station_name'].astype(str)
        hab = hab.merge(pct_daily, on=['station_name', 'date'], how='left')
        print(f"  percent_saturation coverage: "
              f"{hab['percent_saturation'].notna().mean()*100:.1f}%")

# ---------------------------------------------------------------------------
# 2. Compute anomaly features (deviation from station-month climatology)
# ---------------------------------------------------------------------------
print("Computing anomaly features ...")
hab['month'] = hab['date'].dt.month

temp_clim = hab.groupby(['station_name', 'month'])['sea_water_temperature'].mean()
hab = hab.join(temp_clim.rename('temp_clim_monthly'), on=['station_name', 'month'])
hab['temp_anomaly'] = hab['sea_water_temperature'] - hab['temp_clim_monthly']

sal_clim = hab.groupby(['station_name', 'month'])['sea_water_salinity'].mean()
hab = hab.join(sal_clim.rename('sal_clim_monthly'), on=['station_name', 'month'])
hab['sal_anomaly'] = hab['sea_water_salinity'] - hab['sal_clim_monthly']

do_clim = hab.groupby(['station_name', 'month'])['oxygen_concentration_in_sea_water'].mean()
hab = hab.join(do_clim.rename('do_clim_monthly'), on=['station_name', 'month'])
hab['do_anomaly'] = hab['oxygen_concentration_in_sea_water'] - hab['do_clim_monthly']

# Correlation check
for feat in ['temp_anomaly', 'sal_anomaly', 'do_anomaly']:
    if feat in hab.columns and 'bloom_28d' in hab.columns:
        r = hab[feat].corr(hab['bloom_28d'])
        print(f"  {feat}: r={r:.3f} with bloom_28d (existing label)")

df = hab

# ---------------------------------------------------------------------------
# 3. Recompute rolling chl features and bloom_28d label
# ---------------------------------------------------------------------------
print("Computing rolling chl features and bloom_28d label ...")
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

# Correlations with freshly computed bloom_28d
print("\nCorrelations with bloom_28d (recomputed):")
for feat in ['temp_anomaly', 'sal_anomaly', 'do_anomaly']:
    r = df[feat].corr(df['bloom_28d'])
    cov = df[feat].notna().mean() * 100
    print(f"  {feat}: r={r:.3f}  coverage={cov:.0f}%")

# ---------------------------------------------------------------------------
# 4. Feature sets
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
print(f"\nBASE feature count (after availability filter): {len(BASE)}")

feature_sets = {
    'BASE (baseline)':        BASE,
    'BASE + do_anomaly':      BASE + ['do_anomaly'],
    'BASE + temp_anomaly':    BASE + ['temp_anomaly'],
    'BASE + sal_anomaly':     BASE + ['sal_anomaly'],
    'BASE + all_anomalies':   BASE + ['temp_anomaly', 'sal_anomaly', 'do_anomaly'],
    'BASE + do+temp_anomaly': BASE + ['do_anomaly', 'temp_anomaly'],
    'BASE + do+sal_anomaly':  BASE + ['do_anomaly', 'sal_anomaly'],
}

# ---------------------------------------------------------------------------
# 5. Splits
# ---------------------------------------------------------------------------
train = df[df['date'].dt.year <= 2019]
val   = df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)]
test  = df[df['date'].dt.year >= 2023]

print(f"\nSplits -- train: {len(train):,} | val: {len(val):,} | test: {len(test):,}")
print(f"Bloom rate -- train: {train['bloom_28d'].mean():.3f} | "
      f"val:  {val['bloom_28d'].mean():.3f} | "
      f"test: {test['bloom_28d'].mean():.3f}")

# ---------------------------------------------------------------------------
# 6. Helpers
# ---------------------------------------------------------------------------
def prepare(split, features):
    avail = [f for f in features if f in df.columns]
    rows = split[avail + ['bloom_28d']].dropna(subset=['bloom_28d'])
    return (rows[avail].copy().reset_index(drop=True),
            rows['bloom_28d'].copy().reset_index(drop=True),
            avail)


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
    X_tr, y_tr, feats = prepare(train, features)
    X_val_, y_val_, _ = prepare(val,   features)
    X_te, y_te, _     = prepare(test,  features)

    MED = X_tr.median()
    sc = StandardScaler()
    lr = LogisticRegression(C=0.05, class_weight='balanced',
                            max_iter=2000, random_state=42)
    lr.fit(sc.fit_transform(X_tr.fillna(MED)), y_tr)

    # Find best-F1 threshold on val (informational only; we report at 0.60)
    p_val = lr.predict_proba(sc.transform(X_val_.fillna(MED)))[:, 1]
    from sklearn.metrics import precision_recall_curve
    precs, recs, thrs = precision_recall_curve(y_val_, p_val)
    f1s = 2 * precs * recs / (precs + recs + 1e-9)
    best_thr = thrs[np.argmax(f1s[:-1])] if len(thrs) > 0 else 0.60

    p_te = lr.predict_proba(sc.transform(X_te.fillna(MED)))[:, 1]
    m = eval_at(y_te, p_te, t=0.60)
    m['n_feat'] = len(feats)
    m['best_val_thr'] = round(float(best_thr), 3)
    return m

# ---------------------------------------------------------------------------
# 7. Run all feature sets
# ---------------------------------------------------------------------------
results = {}
for name, feats in feature_sets.items():
    print(f"Running '{name}' ({len([f for f in feats if f in df.columns])} features) ...")
    results[name] = run_lr(feats)

# ---------------------------------------------------------------------------
# 8. Print results table sorted by F1
# ---------------------------------------------------------------------------
sorted_results = sorted(results.items(), key=lambda x: x[1]['f1'], reverse=True)

BASE_F1   = results['BASE (baseline)']['f1']
BASE_PREC = results['BASE (baseline)']['precision']
BASE_REC  = results['BASE (baseline)']['recall']

print("\n" + "=" * 105)
print("ANOMALY FEATURE TEST (test 2023-2025, threshold=0.60)")
print("=" * 105)
hdr = (f"{'Feature Set':<28}  {'N':>3}  {'AUC':>6}  "
       f"{'Prec@.60':>9}  {'Rec@.60':>8}  {'F1@.60':>7}  "
       f"{'TP':>4}  {'FP':>4}  {'FN':>4}")
print(hdr)
print("-" * 105)

for name, m in sorted_results:
    flag = ''
    if name != 'BASE (baseline)':
        beats_f1   = m['f1']        > BASE_F1   + 0.005
        beats_prec = m['precision'] > BASE_PREC + 0.010 and m['recall'] >= 0.35
        if beats_f1 or beats_prec:
            flag = '  ***'
    marker = '  <-- baseline' if name == 'BASE (baseline)' else ''
    print(f"{name:<28}  {m['n_feat']:>3}  {m['auc']:>6.4f}  "
          f"{m['precision']:>9.3f}  {m['recall']:>8.3f}  {m['f1']:>7.3f}  "
          f"{m['tp']:>4}  {m['fp']:>4}  {m['fn']:>4}{flag}{marker}")

print()
print(f"*** = F1 > {BASE_F1+0.005:.3f} (baseline+0.005)  OR  "
      f"Precision > {BASE_PREC+0.010:.3f} (baseline+0.010) with Recall >= 0.35")

# ---------------------------------------------------------------------------
# 9. Validation check
# ---------------------------------------------------------------------------
base = results['BASE (baseline)']
print(f"\nBaseline validation: Prec={base['precision']:.3f}  "
      f"Rec={base['recall']:.3f}  F1={base['f1']:.3f}  AUC={base['auc']:.3f}")
print(f"  (expected: Prec~0.465  Rec~0.446  F1~0.455  AUC~0.814)")

# ---------------------------------------------------------------------------
# 10. Check if any combo beats baseline substantially
# ---------------------------------------------------------------------------
winners = [
    (name, m) for name, m in results.items()
    if name != 'BASE (baseline)' and (
        m['f1']        > BASE_F1   + 0.005 or
        (m['precision'] > BASE_PREC + 0.010 and m['recall'] >= 0.35)
    )
]

if winners:
    print("\n*** IMPROVEMENT DETECTED ***")
    for name, m in sorted(winners, key=lambda x: x[1]['f1'], reverse=True):
        print(f"  {name}: Prec={m['precision']:.3f}  Rec={m['recall']:.3f}  "
              f"F1={m['f1']:.3f}  (delta_F1={m['f1']-BASE_F1:+.3f}  "
              f"delta_Prec={m['precision']-BASE_PREC:+.3f})")
    print("\nNext step: add anomaly features + computation block to pipeline files.")
else:
    print("\nNo anomaly combination beats the baseline by the required margin.")
    print("  delta_F1 threshold:   +0.005")
    print("  delta_Prec threshold: +0.010 (with recall >= 0.35)")
    for name, m in sorted_results:
        if name != 'BASE (baseline)':
            print(f"  {name:<28}: delta_F1={m['f1']-BASE_F1:+.3f}  "
                  f"delta_Prec={m['precision']-BASE_PREC:+.3f}  "
                  f"rec={m['recall']:.3f}")
