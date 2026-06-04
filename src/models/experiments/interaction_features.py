"""
interaction_features.py
-----------------------
Tests interaction features between chlorophyll trajectory and physical
forcing variables (tidal, temperature, DO).

Key interactions tested:
  chl_roll21 x tidal_gt_anom  -- high CHL + weak tidal mixing = bloom risk
  chl_roll9  x tidal_gt_anom  -- same at shorter timescale
  chl_roll21 x month_sin      -- seasonal modulation of CHL accumulation
  chl_anomaly x tidal_msl_anom -- CHL spike + unusual sea level
  chl_roll9  x temp_lag1      -- warm water + high CHL = bloom risk
  chl_roll21 x do_lag1        -- hypoxia + sustained high CHL

Run from repo root:
    python src/models/interaction_features.py
"""

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

print("Loading data/hab_features_tidal.csv...")
df = pd.read_csv('data/hab_features_tidal.csv')
df['date'] = pd.to_datetime(df['date'])

# Recompute rolling features including longer ones
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
# Compute interaction features
# ---------------------------------------------------------------------------
print("Computing interaction features...")

# Cyclic month encoding
df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)

# Tidal interactions -- weak tidal mixing + high CHL = bloom risk
df['chl21_x_tidal_gt']  = df['chl_roll21_mean'] * (-df['tidal_gt_anom'])
df['chl9_x_tidal_gt']   = df['chl_roll9_mean']  * (-df['tidal_gt_anom'])
df['chl21_x_tidal_msl'] = df['chl_roll21_mean'] * (-df['tidal_msl_anom'])

# Temperature interactions -- warm water + high CHL = bloom risk
df['chl21_x_temp']  = df['chl_roll21_mean'] * df['sea_water_temperature']
df['chl9_x_temp']   = df['chl_roll9_mean']  * df['temp_lag1']

# DO interactions -- hypoxia + high CHL = bloom risk
df['chl21_x_do']    = df['chl_roll21_mean'] * (-df['oxygen_concentration_in_sea_water'])
df['chl9_x_do']     = df['chl_roll9_mean']  * (-df['do_lag1'])

# Seasonal CHL interaction
df['chl21_x_month_sin'] = df['chl_roll21_mean'] * df['month_sin']
df['chl_anom_x_tidal']  = df['chl_anomaly']     * (-df['tidal_gt_anom'])

ALL_INTERACTIONS = [
    'chl21_x_tidal_gt', 'chl9_x_tidal_gt', 'chl21_x_tidal_msl',
    'chl21_x_temp', 'chl9_x_temp',
    'chl21_x_do', 'chl9_x_do',
    'chl21_x_month_sin', 'chl_anom_x_tidal',
    'month_sin', 'month_cos',
]

# Correlation check
print("\nCorrelations of interaction features with bloom_28d:")
for f in ALL_INTERACTIONS:
    valid = df[[f, 'bloom_28d']].dropna()
    if len(valid) > 100:
        r = valid[f].corr(valid['bloom_28d'])
        print(f"  {f:<25}  r={r:>+7.4f}")

# ---------------------------------------------------------------------------
# Feature sets
# ---------------------------------------------------------------------------
BASE = [
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
BASE = [f for f in BASE if f in df.columns]

# Test subsets of interactions
TIDAL_INTS   = ['chl21_x_tidal_gt', 'chl9_x_tidal_gt', 'chl21_x_tidal_msl']
TEMP_INTS    = ['chl21_x_temp', 'chl9_x_temp']
DO_INTS      = ['chl21_x_do', 'chl9_x_do']
SEASON_INTS  = ['chl21_x_month_sin', 'chl_anom_x_tidal', 'month_sin', 'month_cos']

feature_sets = {
    'BASE (baseline)':              BASE,
    'BASE+tidal_ints':              BASE + TIDAL_INTS,
    'BASE+temp_ints':               BASE + TEMP_INTS,
    'BASE+do_ints':                 BASE + DO_INTS,
    'BASE+season_ints':             BASE + SEASON_INTS,
    'BASE+tidal+temp_ints':         BASE + TIDAL_INTS + TEMP_INTS,
    'BASE+tidal+do_ints':           BASE + TIDAL_INTS + DO_INTS,
    'BASE+ALL_ints':                BASE + ALL_INTERACTIONS,
}

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

# ---------------------------------------------------------------------------
# Train and evaluate
# ---------------------------------------------------------------------------
print("\n" + "=" * 80)
print("RESULTS — sorted by precision at threshold 0.60")
print("=" * 80)
print(f"{'Feature Set':<30}  {'N':>4}  {'AUC':>7}  "
      f"{'Prec@.60':>9}  {'Rec@.60':>8}  {'F1@.60':>7}")
print("-" * 75)

all_results = []
for name, features in feature_sets.items():
    features = [f for f in features if f in df.columns]
    X_tr, y_tr = prepare(train, features)
    X_v,  y_v  = prepare(val,   features)
    X_te, y_te = prepare(test,  features)
    MED = X_tr.median()

    sc = StandardScaler()
    lr = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
    lr.fit(sc.fit_transform(X_tr.fillna(MED)), y_tr)

    p_v  = lr.predict_proba(sc.transform(X_v.fillna(MED)))[:, 1]
    p_te = lr.predict_proba(sc.transform(X_te.fillna(MED)))[:, 1]

    m60 = eval_at(y_te, p_te, 0.60)
    all_results.append((name, len(features), m60))

all_results.sort(key=lambda x: x[2]['precision'], reverse=True)

for name, n, m in all_results:
    marker = "  <-- BEST" if name == all_results[0][0] else ""
    print(f"{name:<30}  {n:>4}  {m['auc']:>7.4f}  "
          f"{m['precision']:>9.3f}  {m['recall']:>8.3f}  {m['f1']:>7.3f}"
          f"  TP={m['tp']} FP={m['fp']} FN={m['fn']}{marker}")

baseline_prec = next(r[2]['precision'] for r in all_results if 'baseline' in r[0])
best_name, _, best_m = all_results[0]
delta = best_m['precision'] - baseline_prec

print(f"\nBest: {best_name} -- precision {best_m['precision']:.3f} "
      f"vs baseline {baseline_prec:.3f} (delta={delta:+.3f})")

if delta > 0.02:
    print("INTERACTION FEATURES HELP -- integrate best combination")
    print(f"Features to add: check which set '{best_name}' uses above")
else:
    print("Interaction features do not meaningfully improve precision.")