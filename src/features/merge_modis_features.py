"""
merge_modis_features.py
-----------------------
Merges MODIS satellite CHL features into hab_features_tidal.csv,
engineers rolling satellite features, and retrains LR to test
whether satellite context improves precision.

Run AFTER extract_modis_features.py has created data/modis_station_daily.csv.

Run from repo root:
    python src/features/merge_modis_features.py
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

# ---------------------------------------------------------------------------
# Load and merge
# ---------------------------------------------------------------------------
print("Loading data...")
hab   = pd.read_csv('data/hab_features_tidal.csv')
modis = pd.read_csv('data/modis_station_daily.csv')

hab['date']   = pd.to_datetime(hab['date'])
modis['date'] = pd.to_datetime(modis['date'])

print(f"HAB rows:   {len(hab):,}")
print(f"MODIS rows: {len(modis):,}")
print(f"MODIS coverage: {modis['sat_chl_mean'].notna().mean()*100:.1f}%")

# Merge on date + station
hab_sat = hab.merge(modis[['date', 'station_name', 'sat_chl_mean', 'sat_chl_valid_frac']],
                    on=['date', 'station_name'], how='left')

print(f"\nAfter merge: {len(hab_sat):,} rows")
print(f"sat_chl_mean coverage: {hab_sat['sat_chl_mean'].notna().mean()*100:.1f}%")

# ---------------------------------------------------------------------------
# Engineer satellite rolling features
# ---------------------------------------------------------------------------
print("\nEngineering satellite features...")

# Rolling mean of satellite CHL over past 7 days (where available)
# NaN-tolerant: uses whatever valid observations exist in the window
hab_sat = hab_sat.sort_values(['station_name', 'date']).reset_index(drop=True)

hab_sat['sat_chl_roll7'] = (
    hab_sat.groupby('station_name')['sat_chl_mean']
           .transform(lambda x: x.rolling(7, min_periods=1).mean())
)

# Satellite anomaly: sat CHL minus in-situ climatology
# Captures whether satellite sees more CHL than expected for this month/station
hab_sat['sat_chl_anom'] = hab_sat['sat_chl_mean'] - hab_sat['chl_climatology']

# Difference between satellite and in-situ CHL -- captures spatial offset
# Positive = satellite sees more CHL than the station point measurement
hab_sat['sat_insitu_diff'] = hab_sat['sat_chl_mean'] - hab_sat['Chlorophyll']

SAT_FEATURES = ['sat_chl_mean', 'sat_chl_roll7', 'sat_chl_anom',
                'sat_insitu_diff', 'sat_chl_valid_frac']

print("Satellite features:")
for f in SAT_FEATURES:
    cov = hab_sat[f].notna().mean() * 100
    print(f"  {f:<25} {cov:.1f}% coverage")

hab_sat.to_csv('data/hab_features_satellite.csv', index=False)
print(f"\nSaved data/hab_features_satellite.csv ({len(hab_sat):,} rows, "
      f"{len(hab_sat.columns)} columns)")

# ---------------------------------------------------------------------------
# Quick correlation check
# ---------------------------------------------------------------------------
print("\n" + "=" * 55)
print("SATELLITE FEATURE CORRELATIONS WITH bloom_28d")
print("=" * 55)

# Recompute bloom_28d
for n, min_p in [(3, 2), (6, 3), (9, 5)]:
    hab_sat[f'chl_roll{n}_mean'] = (
        hab_sat.groupby('station_name')['Chlorophyll']
               .transform(lambda x: x.rolling(n, min_periods=min_p).mean())
    )

hab_sat['bloom_28d_tmp'] = 0
for station, grp in hab_sat.groupby('station_name'):
    idx   = grp.index
    dates = grp['date'].values
    chl   = grp['Chlorophyll'].values
    labels = np.zeros(len(grp), dtype=int)
    for i in range(len(grp)):
        mask = (dates > dates[i]) & (dates <= dates[i] + np.timedelta64(28, 'D'))
        if mask.any() and (chl[mask] > 10).any():
            labels[i] = 1
    hab_sat.loc[idx, 'bloom_28d_tmp'] = labels

print(f"{'Feature':<25}  {'r':>8}  {'Coverage'}")
print("-" * 55)
for f in SAT_FEATURES:
    valid = hab_sat[[f, 'bloom_28d_tmp']].dropna()
    if len(valid) > 100:
        r = valid[f].corr(valid['bloom_28d_tmp'])
        cov = hab_sat[f].notna().mean() * 100
        print(f"  {f:<25}  {r:>+8.4f}  {cov:.1f}%")
    else:
        print(f"  {f:<25}  insufficient data")

print("\nIf sat_chl_mean r > 0.10, satellite adds signal beyond in-situ.")
print("Next: python src/models/retrain_with_satellite.py")