"""
gust_interaction_test.py
------------------------
Tests interaction features between wind gust strength and chlorophyll
accumulation. Physical hypothesis: high CHL + calm conditions (low
max_gust_3d) = HIGH bloom risk; high CHL + strong gusts = LOW bloom risk
because wind mixing suppresses stratification and bloom formation.

Builds on the 35-feature baseline (which already includes max_gust_3d).
Prior interaction tests (interaction_features.py) only tested CHL × tidal,
temp, and DO -- all predating max_gust_3d.

Run from repo root:
    python src/models/experiments/gust_interaction_test.py
"""

import glob
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_auc_score, precision_score, recall_score,
    f1_score, precision_recall_curve,
)

# ---------------------------------------------------------------------------
# Load + recompute features  (same as final_evaluation_threshold_sweep.py)
# ---------------------------------------------------------------------------
print("Loading data/hab_features_tidal.csv...")
hab = pd.read_csv('data/hab_features_tidal.csv')
hab['date'] = pd.to_datetime(hab['date'])


def load_percent_saturation():
    frames = []
    for f in sorted(glob.glob('data/raw/deep_wq_extra/deep_wq_S_*.csv')):
        frames.append(pd.read_csv(
            f, skiprows=[1],
            usecols=['station_name', 'time', 'percent_saturation']))
    ps = pd.concat(frames, ignore_index=True)
    ps = ps[ps['station_name'].notna()].copy()
    ps['station_name'] = ps['station_name'].astype(str)
    ps['date'] = (pd.to_datetime(ps['time'], utc=True)
                    .dt.tz_localize(None).dt.normalize())
    ps['percent_saturation'] = pd.to_numeric(ps['percent_saturation'], errors='coerce')
    return (ps.dropna(subset=['percent_saturation'])
              .groupby(['date', 'station_name'], as_index=False)
              ['percent_saturation'].mean())


if 'percent_saturation' not in hab.columns:
    print("Merging percent_saturation...")
    ps = load_percent_saturation()
    hab['station_name'] = hab['station_name'].astype(str)
    hab = hab.merge(ps, on=['date', 'station_name'], how='left')
    print(f"  percent_saturation coverage: "
          f"{hab['percent_saturation'].notna().mean() * 100:.1f}%")

print("Merging max_gust_3d from data/gust_features_daily.csv...")
gust = pd.read_csv('data/gust_features_daily.csv', usecols=['date', 'max_gust_3d'])
gust['date'] = pd.to_datetime(gust['date'])
hab = hab.merge(gust, on='date', how='left')
print(f"  max_gust_3d coverage: {hab['max_gust_3d'].notna().mean() * 100:.1f}%")

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
# Interaction features
# ---------------------------------------------------------------------------
print("\nComputing gust interaction features...")

gust_max = hab['max_gust_3d'].quantile(0.95)
hab['gust_norm'] = hab['max_gust_3d'].clip(0, gust_max) / gust_max

hab['chl9_x_calm']       = hab['chl_roll9_mean']  * (1 - hab['gust_norm'])
hab['chl21_x_calm']      = hab['chl_roll21_mean'] * (1 - hab['gust_norm'])
hab['chl_anom_x_calm']   = hab['chl_anomaly']     * (1 - hab['gust_norm'])
hab['gust_x_tidal']      = hab['max_gust_3d']     * (-hab['tidal_gt_anom'])
hab['calm_x_tidal_weak'] = (1 - hab['gust_norm']) * (-hab['tidal_gt_anom'])

INT_FEATS = [
    'chl9_x_calm', 'chl21_x_calm', 'chl_anom_x_calm',
    'gust_x_tidal', 'calm_x_tidal_weak',
]

print("\nCorrelations of interaction features with bloom_28d:")
for f in INT_FEATS:
    valid = hab[[f, 'bloom_28d']].dropna()
    if len(valid) > 100:
        r = valid[f].corr(valid['bloom_28d'])
        print(f"  {f:<25}  r={r:>+7.4f}")

# ---------------------------------------------------------------------------
# 35-feature BASE (same as current pipeline)
# ---------------------------------------------------------------------------
BASE_ALL = [
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
BASE = [f for f in BASE_ALL if f in hab.columns]
print(f"\nBASE has {len(BASE)} features (expected 35).")

feature_sets = {
    'BASE (baseline)':          BASE,
    'BASE + chl9_x_calm':       BASE + ['chl9_x_calm'],
    'BASE + chl21_x_calm':      BASE + ['chl21_x_calm'],
    'BASE + chl_anom_x_calm':   BASE + ['chl_anom_x_calm'],
    'BASE + gust_x_tidal':      BASE + ['gust_x_tidal'],
    'BASE + calm_x_tidal_weak': BASE + ['calm_x_tidal_weak'],
    'BASE + chl9+chl21_x_calm': BASE + ['chl9_x_calm', 'chl21_x_calm'],
    'BASE + all_interactions':  BASE + INT_FEATS,
}

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


# ---------------------------------------------------------------------------
# Train and evaluate
# ---------------------------------------------------------------------------
print("\n" + "=" * 84)
print("RESULTS — sorted by F1 at threshold 0.60  (LR C=0.05, test 2023-2025)")
print("=" * 84)
print(f"{'Feature Set':<30}  {'N':>4}  {'AUC':>7}  "
      f"{'Prec@.60':>9}  {'Rec@.60':>8}  {'F1@.60':>7}  {'TP':>3}{'FP':>4}{'FN':>4}")
print("-" * 84)

all_results = []
for name, features in feature_sets.items():
    features = [f for f in features if f in hab.columns]
    X_tr, y_tr = prepare(train, features)
    X_v,  y_v  = prepare(val,   features)
    X_te, y_te = prepare(test,  features)
    MED = X_tr.median()

    sc = StandardScaler()
    lr = LogisticRegression(
        class_weight='balanced', C=0.05, max_iter=1000, random_state=42)
    lr.fit(sc.fit_transform(X_tr.fillna(MED)), y_tr)

    p_te = lr.predict_proba(sc.transform(X_te.fillna(MED)))[:, 1]
    m    = eval_at(y_te, p_te, 0.60)
    all_results.append((name, len(features), m))

all_results.sort(key=lambda x: x[2]['f1'], reverse=True)

baseline_m = next(r[2] for r in all_results if 'baseline' in r[0])

for name, n, m in all_results:
    delta_f1   = m['f1']        - baseline_m['f1']
    delta_prec = m['precision'] - baseline_m['precision']
    flag = ""
    if name != 'BASE (baseline)':
        if delta_f1 > 0.010:
            flag += "  *** F1 +" + f"{delta_f1:+.3f}"
        if delta_prec > 0.020:
            flag += "  *** Prec +" + f"{delta_prec:+.3f}"
    print(f"{name:<30}  {n:>4}  {m['auc']:>7.4f}  "
          f"{m['precision']:>9.3f}  {m['recall']:>8.3f}  {m['f1']:>7.3f}  "
          f"{m['tp']:>3}{m['fp']:>4}{m['fn']:>4}{flag}")

print()
best_name, _, best_m = all_results[0]
delta_f1   = best_m['f1']        - baseline_m['f1']
delta_prec = best_m['precision'] - baseline_m['precision']
print(f"Best: {best_name}")
print(f"  F1    {best_m['f1']:.3f} vs baseline {baseline_m['f1']:.3f} "
      f"(delta={delta_f1:+.3f})")
print(f"  Prec  {best_m['precision']:.3f} vs baseline {baseline_m['precision']:.3f} "
      f"(delta={delta_prec:+.3f})")

if delta_f1 > 0.010 or delta_prec > 0.020:
    print("\nGUST INTERACTIONS HELP -- consider integrating into pipeline.")
else:
    print("\nGust interactions do not meaningfully improve the baseline.")
