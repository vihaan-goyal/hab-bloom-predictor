"""
longer_lags.py
--------------
Tests whether adding explicit point lags at 7, 14, and 21 days
improves precision over the current baseline.

Current features have lags at 1,2,3,4 days and rolling means at 3,6,9 days.
The lag correlation analysis shows r=0.466 at 21 days -- real signal
not currently captured as a direct feature.

Run from repo root:
    python src/models/longer_lags.py
"""

import warnings
warnings.filterwarnings('ignore', category=UserWarning)

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_auc_score, average_precision_score,
    f1_score, precision_score, recall_score,
    precision_recall_curve,
)

print("Loading data/hab_features_tidal.csv...")
df = pd.read_csv('data/hab_features_tidal.csv')
df['date'] = pd.to_datetime(df['date'])

# ---------------------------------------------------------------------------
# Recompute rolling features + add longer lags
# ---------------------------------------------------------------------------
for n, min_p in [(3, 2), (6, 3), (9, 5)]:
    df[f'chl_roll{n}_mean'] = (
        df.groupby('station_name')['Chlorophyll']
          .transform(lambda x: x.rolling(n, min_periods=min_p).mean())
    )

df['chl_trend'] = (
    df.groupby('station_name')['Chlorophyll']
      .transform(lambda x: x.rolling(4, min_periods=3)
                 .apply(lambda v: np.polyfit(range(len(v)), v, 1)[0]))
)

# Add longer point lags
for lag in [7, 14, 21]:
    df[f'chl_lag{lag}'] = (
        df.groupby('station_name')['Chlorophyll']
          .transform(lambda x: x.shift(lag))
    )

# Add longer rolling means
for n, min_p in [(14, 7), (21, 10)]:
    df[f'chl_roll{n}_mean'] = (
        df.groupby('station_name')['Chlorophyll']
          .transform(lambda x: x.rolling(n, min_periods=min_p).mean())
    )

# Lag differences -- rate of change between lag periods
df['chl_lag_diff_7_1']   = df.groupby('station_name')['Chlorophyll'].transform(
    lambda x: x.shift(1) - x.shift(7))   # was CHL rising or falling in past week?
df['chl_lag_diff_14_7']  = df.groupby('station_name')['Chlorophyll'].transform(
    lambda x: x.shift(7) - x.shift(14))  # trend over weeks 1-2 ago
df['chl_lag_diff_21_14'] = df.groupby('station_name')['Chlorophyll'].transform(
    lambda x: x.shift(14) - x.shift(21)) # trend over weeks 2-3 ago

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
# Feature sets
# ---------------------------------------------------------------------------
BASE_TIDAL = [
    'Chlorophyll', 'chl_lag1', 'chl_lag2', 'chl_lag3', 'chl_lag4',
    'chl_roll3_mean', 'chl_roll6_mean', 'chl_roll9_mean', 'chl_trend',
    'chl_anomaly', 'chl_climatology',
    'do_lag1', 'temp_lag1', 'sal_lag1',
    'sea_water_temperature', 'sea_water_salinity',
    'oxygen_concentration_in_sea_water',
    'month', 'latitude_x', 'longitude_x',
    'nox_lag2', 'dip_lag2', 'dip_change', 'dip_x_month',
    'neighbor_chl3_mean', 'neighbor_chl3_lag1',
    'tidal_gt_anom', 'tidal_msl_anom',
]

LONGER_LAGS = ['chl_lag7', 'chl_lag14', 'chl_lag21']
LONGER_ROLLS = ['chl_roll14_mean', 'chl_roll21_mean']
LAG_DIFFS = ['chl_lag_diff_7_1', 'chl_lag_diff_14_7', 'chl_lag_diff_21_14']

BASE_TIDAL   = [f for f in BASE_TIDAL   if f in df.columns]
LONGER_LAGS  = [f for f in LONGER_LAGS  if f in df.columns]
LONGER_ROLLS = [f for f in LONGER_ROLLS if f in df.columns]
LAG_DIFFS    = [f for f in LAG_DIFFS    if f in df.columns]

ALL_NEW = LONGER_LAGS + LONGER_ROLLS + LAG_DIFFS

feature_sets = {
    'BASE+TIDAL (baseline)':           BASE_TIDAL,
    'BASE+TIDAL+lag7/14/21':           BASE_TIDAL + LONGER_LAGS,
    'BASE+TIDAL+roll14/21':            BASE_TIDAL + LONGER_ROLLS,
    'BASE+TIDAL+lag_diffs':            BASE_TIDAL + LAG_DIFFS,
    'BASE+TIDAL+ALL_LONGER':           BASE_TIDAL + ALL_NEW,
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
# Correlation check on new features
# ---------------------------------------------------------------------------
print("\nCorrelations of new features with bloom_28d:")
for f in ALL_NEW:
    valid = df[[f, 'bloom_28d']].dropna()
    if len(valid) > 100:
        r = valid[f].corr(valid['bloom_28d'])
        print(f"  {f:<25}  r={r:>+7.4f}  ({valid[f].notna().mean()*100:.1f}% coverage)")

# ---------------------------------------------------------------------------
# Train and evaluate all feature sets
# ---------------------------------------------------------------------------
print("\n" + "=" * 75)
print("RESULTS — sorted by precision at threshold 0.60")
print("=" * 75)
print(f"{'Feature Set':<35}  {'N':>4}  {'AUC':>7}  "
      f"{'Prec@.60':>9}  {'Rec@.60':>8}  {'F1@.60':>7}")
print("-" * 75)

all_results = []
for name, features in feature_sets.items():
    X_train_f, y_train_f = prepare(train, features)
    X_val_f,   y_val_f   = prepare(val,   features)
    X_test_f,  y_test_f  = prepare(test,  features)
    MED = X_train_f.median()

    sc = StandardScaler()
    lr = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
    lr.fit(sc.fit_transform(X_train_f.fillna(MED)), y_train_f)

    p_v  = lr.predict_proba(sc.transform(X_val_f.fillna(MED)))[:, 1]
    p_te = lr.predict_proba(sc.transform(X_test_f.fillna(MED)))[:, 1]

    t    = best_f1_thresh(y_val_f, p_v)
    m60  = eval_at(y_test_f, p_te, 0.60)

    all_results.append((name, len(features), m60['auc'],
                        m60['precision'], m60['recall'], m60['f1'],
                        m60['tp'], m60['fp'], m60['fn']))

all_results.sort(key=lambda x: x[3], reverse=True)
for name, n, auc, prec, rec, f1, tp, fp, fn in all_results:
    marker = "  <-- BEST" if name == all_results[0][0] else ""
    print(f"{name:<35}  {n:>4}  {auc:>7.4f}  "
          f"{prec:>9.3f}  {rec:>8.3f}  {f1:>7.3f}"
          f"  TP={tp} FP={fp} FN={fn}{marker}")

baseline_prec = next(r[3] for r in all_results if 'baseline' in r[0])
best_prec = all_results[0][3]
delta = best_prec - baseline_prec

print(f"\nBest precision: {best_prec:.3f} vs baseline {baseline_prec:.3f} "
      f"(delta={delta:+.3f})")
if delta > 0.02:
    print("LONGER LAGS HELP -- integrate into pipeline")
else:
    print("Longer lags do not meaningfully improve precision.")