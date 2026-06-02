"""
add_tidal_features.py
---------------------
Parses NOAA CO-OPS monthly mean water level data and engineers tidal
features for the HAB bloom predictor.

Stations:
  8465705 -- New Haven CT
  8467150 -- Bridgeport CT
  8461490 -- New London CT

Key features:
  tidal_range_gt     -- Great Diurnal Range (GT): spring vs neap tidal forcing
                        High GT = strong tidal mixing = bloom suppression
  tidal_msl          -- Mean sea level: anomalously high MSL = more coastal flooding
                        and nutrient flushing
  tidal_range_anom   -- GT anomaly from long-term monthly mean: captures
                        unusually weak tidal mixing months

Note: data is monthly so features are constant within each month.
This is coarse but tidal forcing varies on ~29-day lunar cycle so
monthly resolution captures the main signal.

Run from repo root:
    python src/features/add_tidal_features.py
"""

import warnings
warnings.filterwarnings('ignore')

import os
import pandas as pd
import numpy as np

TIDAL_DIR = 'data/raw/tidal'

FILES = {
    '8465705': 'CO-OPS__8465705__ml.csv',  # New Haven
    '8467150': 'CO-OPS__8467150__ml.csv',  # Bridgeport
    '8461490': 'CO-OPS__8461490__ml.csv',  # New London
}

STATION_NAMES = {
    '8465705': 'NewHaven',
    '8467150': 'Bridgeport',
    '8461490': 'NewLondon',
}

# ---------------------------------------------------------------------------
# Load and parse all tidal files
# ---------------------------------------------------------------------------
print("Loading NOAA CO-OPS tidal files...")

all_monthly = []

for station_id, fname in FILES.items():
    fpath = os.path.join(TIDAL_DIR, fname)
    if not os.path.exists(fpath):
        print(f"  MISSING: {fpath} -- put file in {TIDAL_DIR}/")
        continue

    df = pd.read_csv(fpath)
    df.columns = [c.strip() for c in df.columns]
    df['station'] = STATION_NAMES[station_id]

    # Parse year/month into a date (first of month)
    df['date'] = pd.to_datetime(
        df['Year'].astype(str) + '-' + df['Month'].astype(str).str.zfill(2) + '-01'
    )

    # Key columns: GT = great diurnal range, MSL = mean sea level
    df['GT']  = pd.to_numeric(df['GT'],  errors='coerce')
    df['MSL'] = pd.to_numeric(df['MSL'], errors='coerce')
    df['MN']  = pd.to_numeric(df['MN'],  errors='coerce')  # mean range

    all_monthly.append(df[['date', 'station', 'GT', 'MSL', 'MN']])
    print(f"  {fname}: {STATION_NAMES[station_id]} | "
          f"{df['date'].min().date()} to {df['date'].max().date()} | "
          f"{len(df)} months")

all_df = pd.concat(all_monthly, ignore_index=True)
print(f"\nTotal monthly records: {len(all_df):,}")

# ---------------------------------------------------------------------------
# Average across stations per month
# ---------------------------------------------------------------------------
print("Averaging across stations per month...")

monthly = (
    all_df.groupby('date')
    .agg(
        tidal_gt  =('GT',  'mean'),
        tidal_msl =('MSL', 'mean'),
        tidal_mn  =('MN',  'mean'),
        n_stations=('station', 'count'),
    )
    .reset_index()
    .sort_values('date')
    .reset_index(drop=True)
)

print(f"Monthly records: {len(monthly):,}")
print(f"Date range: {monthly['date'].min().date()} to {monthly['date'].max().date()}")
print(f"Mean GT (tidal range): {monthly['tidal_gt'].mean():.3f} m")
print(f"Mean MSL: {monthly['tidal_msl'].mean():.3f} m")

# ---------------------------------------------------------------------------
# Compute tidal anomaly: GT relative to long-term monthly mean
# High positive anomaly = unusually strong tidal mixing this month
# ---------------------------------------------------------------------------
monthly['month_num'] = monthly['date'].dt.month
monthly_clim = monthly.groupby('month_num')['tidal_gt'].mean().rename('tidal_gt_clim')
monthly = monthly.merge(monthly_clim, on='month_num', how='left')
monthly['tidal_gt_anom'] = monthly['tidal_gt'] - monthly['tidal_gt_clim']

# MSL anomaly -- unusually high sea level = more coastal flooding + nutrient flushing
msl_clim = monthly.groupby('month_num')['tidal_msl'].mean().rename('tidal_msl_clim')
monthly = monthly.merge(msl_clim, on='month_num', how='left')
monthly['tidal_msl_anom'] = monthly['tidal_msl'] - monthly['tidal_msl_clim']

TIDAL_FEATURES = ['tidal_gt', 'tidal_msl', 'tidal_gt_anom', 'tidal_msl_anom']

monthly.to_csv('data/tidal_features_monthly.csv', index=False)
print("\nSaved data/tidal_features_monthly.csv")

# ---------------------------------------------------------------------------
# Merge with hab_features_daily.csv
# Match each daily row to its month's tidal values
# ---------------------------------------------------------------------------
print("\nMerging with hab_features_daily.csv...")

hab = pd.read_csv('data/hab_features_daily.csv')
hab['date'] = pd.to_datetime(hab['date'])
hab['month_start'] = hab['date'].values.astype('datetime64[M]')

tidal_merge = monthly[['date'] + TIDAL_FEATURES].copy()
tidal_merge = tidal_merge.rename(columns={'date': 'month_start'})

hab_tidal = hab.merge(tidal_merge, on='month_start', how='left')
hab_tidal = hab_tidal.drop(columns=['month_start'])

print(f"HAB rows: {len(hab):,}  -->  merged: {len(hab_tidal):,}")
for f in TIDAL_FEATURES:
    coverage = hab_tidal[f].notna().mean() * 100
    print(f"  {f:<20} {coverage:.1f}% coverage")

hab_tidal.to_csv('data/hab_features_tidal.csv', index=False)
print(f"\nSaved data/hab_features_tidal.csv "
      f"({len(hab_tidal):,} rows, {len(hab_tidal.columns)} columns)")

# ---------------------------------------------------------------------------
# Correlation check
# ---------------------------------------------------------------------------
print("\n" + "=" * 55)
print("TIDAL FEATURE CORRELATIONS WITH bloom_28d")
print("=" * 55)

for n, min_p in [(3, 2), (6, 3), (9, 5)]:
    hab_tidal[f'chl_roll{n}_mean'] = (
        hab_tidal.groupby('station_name')['Chlorophyll']
          .transform(lambda x: x.rolling(n, min_periods=min_p).mean())
    )

hab_tidal['bloom_28d_tmp'] = 0
for station, grp in hab_tidal.groupby('station_name'):
    idx   = grp.index
    dates = grp['date'].values
    chl   = grp['Chlorophyll'].values
    labels = np.zeros(len(grp), dtype=int)
    for i in range(len(grp)):
        mask = (dates > dates[i]) & (dates <= dates[i] + np.timedelta64(28, 'D'))
        if mask.any() and (chl[mask] > 10).any():
            labels[i] = 1
    hab_tidal.loc[idx, 'bloom_28d_tmp'] = labels

print(f"{'Feature':<22}  {'r':>8}  {'Direction'}")
print("-" * 65)
for f in TIDAL_FEATURES:
    valid = hab_tidal[[f, 'bloom_28d_tmp']].dropna()
    if len(valid) > 100:
        r = valid[f].corr(valid['bloom_28d_tmp'])
        if f in ['tidal_gt', 'tidal_gt_anom', 'tidal_mn']:
            direction = "stronger tidal mixing = fewer blooms (good)" if r < 0 else "unexpected"
        else:
            direction = "higher MSL = more blooms" if r > 0 else "higher MSL = fewer blooms"
        print(f"  {f:<22}  {r:>+8.4f}  {direction}")
    else:
        print(f"  {f:<22}  insufficient data")

print("\nIf tidal_gt r < -0.05, tidal mixing is a useful signal.")
print("Next: python src/models/retrain_with_tidal.py")