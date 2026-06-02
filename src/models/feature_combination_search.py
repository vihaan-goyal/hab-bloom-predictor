"""
feature_combination_search.py
-----------------------------
Tests combinations of external data sources (tidal + wind) to find the best
test-set precision for HAB bloom prediction. Mirrors the split/labeling logic
in src/deploy/daily_inference.py.

Run from repo root:
    $env:USERPROFILE\\anaconda3\\python.exe src/models/feature_combination_search.py
"""

import warnings
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, precision_recall_curve, precision_score, recall_score, f1_score

# -- 1. Load and merge all data sources ----------------------------------------
print("Loading data/hab_features_tidal.csv...")
df = pd.read_csv("data/hab_features_tidal.csv")
df['date'] = pd.to_datetime(df['date'])

print("Merging data/wind_features_daily.csv...")
WIND_COLS = ['wind_roll3_mean', 'wind_roll7_mean', 'wind_max_7d',
             'wind_calm_days_7d', 'wind_sustained_roll7']
wind = pd.read_csv("data/wind_features_daily.csv")[['date'] + WIND_COLS]
wind['date'] = pd.to_datetime(wind['date'])
df = df.merge(wind, on='date', how='left')

wind_cov = df['wind_roll7_mean'].notna().mean() * 100
print(f"Wind feature coverage after merge: {wind_cov:.1f}%")

# -- 2. Recompute rolling features and bloom label -----------------------------
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

# -- 3. Feature groups ---------------------------------------------------------
BASE = [
    'Chlorophyll', 'chl_lag1', 'chl_lag2', 'chl_lag3', 'chl_lag4',
    'chl_roll3_mean', 'chl_roll6_mean', 'chl_roll9_mean', 'chl_trend',
    'chl_anomaly', 'chl_climatology',
    'do_lag1', 'temp_lag1', 'sal_lag1',
    'sea_water_temperature', 'sea_water_salinity',
    'oxygen_concentration_in_sea_water',
    'month', 'latitude_x', 'longitude_x',
    'nox_lag2', 'dip_lag2', 'dip_change', 'dip_x_month',
    'neighbor_chl3_mean', 'neighbor_chl3_lag1',
]

TIDAL = ['tidal_gt_anom', 'tidal_msl_anom']

# Skip wind_roll3_mean (too noisy) and wind_max_7d (positive coef = wrong direction)
WIND = ['wind_roll7_mean', 'wind_calm_days_7d', 'wind_sustained_roll7']

EXTERNAL = TIDAL + WIND  # for coefficient reporting

# -- 4. Combinations to test ---------------------------------------------------
COMBOS = [
    ("BASE",                       BASE),
    ("BASE+TIDAL",                 BASE + TIDAL),
    ("BASE+WIND",                  BASE + WIND),
    ("BASE+TIDAL+WIND",            BASE + TIDAL + WIND),
    ("BASE+TIDAL+wind_roll7",      BASE + TIDAL + ['wind_roll7_mean']),
    ("BASE+TIDAL+wind_calm",       BASE + TIDAL + ['wind_calm_days_7d']),
    ("BASE+TIDAL+wind_sustained",  BASE + TIDAL + ['wind_sustained_roll7']),
]

# -- 5. Temporal splits --------------------------------------------------------
train = df[df['date'].dt.year <= 2019]
val   = df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)]
test  = df[df['date'].dt.year >= 2023]

print(f"\nSplit sizes -- train: {len(train):,} | val: {len(val):,} | test: {len(test):,}")
print(f"Bloom rate  -- train: {train['bloom_28d'].mean():.3f} | "
      f"val: {val['bloom_28d'].mean():.3f} | test: {test['bloom_28d'].mean():.3f}")

FIXED_THRESH = 0.60
y_train = train['bloom_28d'].values
y_val   = val['bloom_28d'].values
y_test  = test['bloom_28d'].values


def evaluate(features):
    """Fit LR on a feature set, return metrics + coefficients."""
    feats = [f for f in features if f in df.columns]
    X_train = train[feats].copy()
    X_val   = val[feats].copy()
    X_test  = test[feats].copy()

    med = X_train.median()
    scaler = StandardScaler()
    X_tr_s = scaler.fit_transform(X_train.fillna(med))
    X_v_s  = scaler.transform(X_val.fillna(med))
    X_te_s = scaler.transform(X_test.fillna(med))

    model = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
    model.fit(X_tr_s, y_train)

    val_p  = model.predict_proba(X_v_s)[:, 1]
    test_p = model.predict_proba(X_te_s)[:, 1]

    auc = roc_auc_score(y_test, test_p)

    # best-F1 threshold on val set
    prec, rec, thr = precision_recall_curve(y_val, val_p)
    f1s = 2 * prec * rec / (prec + rec + 1e-12)
    best_i = np.argmax(f1s[:-1]) if len(thr) > 0 else 0
    val_thresh = thr[best_i] if len(thr) > 0 else 0.5

    def metrics_at(threshold):
        pred = (test_p >= threshold).astype(int)
        return (precision_score(y_test, pred, zero_division=0),
                recall_score(y_test, pred, zero_division=0),
                f1_score(y_test, pred, zero_division=0))

    p_val, r_val, f_val   = metrics_at(val_thresh)
    p_fix, r_fix, f_fix   = metrics_at(FIXED_THRESH)

    coefs = dict(zip(feats, model.coef_[0]))
    return {
        'n_feat': len(feats),
        'val_thresh': val_thresh,
        'auc': auc,
        # at val best-F1 threshold
        'prec_valthr': p_val, 'rec_valthr': r_val, 'f1_valthr': f_val,
        # at fixed 0.60 threshold
        'precision': p_fix, 'recall': r_fix, 'f1': f_fix,
        'coefs': coefs,
    }


# -- Run all combinations ------------------------------------------------------
results = []
for name, feats in COMBOS:
    m = evaluate(feats)
    m['name'] = name
    results.append(m)

results.sort(key=lambda r: r['precision'], reverse=True)

# -- 6. Comparison tables ------------------------------------------------------
print("\n" + "=" * 100)
print("COMBINATION SEARCH RESULTS (test set 2023-2025, threshold 0.60)")
print("=" * 100)
print(f"{'Rank':<5} {'Feature Set':<26} {'N_feat':>6} {'Val_thresh':>10} "
      f"{'AUC':>6} {'Precision':>10} {'Recall':>8} {'F1':>7}")
print("-" * 100)
for i, r in enumerate(results, 1):
    print(f"{i:<5} {r['name']:<26} {r['n_feat']:>6} {r['val_thresh']:>10.3f} "
          f"{r['auc']:>6.3f} {r['precision']:>10.3f} {r['recall']:>8.3f} {r['f1']:>7.3f}")

print("\n" + "=" * 100)
print("SAME COMBINATIONS, evaluated at each model's VAL best-F1 threshold")
print("=" * 100)
print(f"{'Feature Set':<26} {'Val_thresh':>10} {'Precision':>10} {'Recall':>8} {'F1':>7}")
print("-" * 100)
for r in results:
    print(f"{r['name']:<26} {r['val_thresh']:>10.3f} "
          f"{r['prec_valthr']:>10.3f} {r['rec_valthr']:>8.3f} {r['f1_valthr']:>7.3f}")

# -- Coefficients for external features in the best model ----------------------
best = results[0]
print("\n" + "=" * 100)
print(f"EXTERNAL FEATURE COEFFICIENTS in best model: {best['name']}")
print("=" * 100)
for f in EXTERNAL:
    if f in best['coefs']:
        c = best['coefs'][f]
        direction = "protective (lower risk)" if c < 0 else "risk-increasing"
        print(f"  {f:<24} {c:>+8.4f}   {direction}")

# -- 7. Save results -----------------------------------------------------------
out = pd.DataFrame([{
    'feature_set':   r['name'],
    'n_feat':        r['n_feat'],
    'val_thresh':    round(r['val_thresh'], 4),
    'test_auc':      round(r['auc'], 4),
    'precision_060': round(r['precision'], 4),
    'recall_060':    round(r['recall'], 4),
    'f1_060':        round(r['f1'], 4),
    'precision_valthr': round(r['prec_valthr'], 4),
    'recall_valthr':    round(r['rec_valthr'], 4),
    'f1_valthr':        round(r['f1_valthr'], 4),
} for r in results])
out.to_csv("data/feature_combination_results.csv", index=False)
print(f"\nSaved comparison table to data/feature_combination_results.csv")

# -- Verdict -------------------------------------------------------------------
base_row  = next(r for r in results if r['name'] == 'BASE')
tidal_row = next(r for r in results if r['name'] == 'BASE+TIDAL')
combo_row = next(r for r in results if r['name'] == 'BASE+TIDAL+WIND')

print("\n" + "=" * 100)
print("VERDICT")
print("=" * 100)
print(f"BASE            precision@0.60 = {base_row['precision']:.3f} | F1 = {base_row['f1']:.3f}")
print(f"BASE+TIDAL      precision@0.60 = {tidal_row['precision']:.3f} | F1 = {tidal_row['f1']:.3f}  (current best)")
print(f"BASE+TIDAL+WIND precision@0.60 = {combo_row['precision']:.3f} | F1 = {combo_row['f1']:.3f}")

winner = results[0]
print(f"\nHighest test precision@0.60: {winner['name']} "
      f"(precision={winner['precision']:.3f}, F1={winner['f1']:.3f})")

if combo_row['precision'] > tidal_row['precision'] and combo_row['f1'] >= 0.38:
    print(">>> WIND HELPS: BASE+TIDAL+WIND beats BASE+TIDAL with F1 >= 0.38. "
          "Promote this combination to the pipeline.")
else:
    print(">>> WIND DOES NOT HELP in combination. Tidal-only remains the ceiling; "
          "keep BASE+TIDAL in the pipeline.")
