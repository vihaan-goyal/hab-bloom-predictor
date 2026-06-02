"""
add_wind_features.py
--------------------
Parses NOAA LCD (Local Climatological Data) files from data/raw/asos_wind/
and engineers daily wind features for the HAB bloom predictor.

Three stations:
  72504094702 -- Igor I Sikorsky Memorial Airport (Bridgeport CT, on LIS shore)
  72504614707 -- Groton New London Airport (eastern LIS)
  72504514758 -- New Haven Tweed Airport (western LIS)

Uses DailyAverageWindSpeed and DailyPeakWindSpeed columns from LCD format.
Wind speed units in LCD are mph -- converted to m/s.

Run from repo root:
    python src/features/add_wind_features.py
"""

import warnings
warnings.filterwarnings('ignore')

import os
import pandas as pd
import numpy as np

ASOS_DIR = 'data/raw/asos_wind'

STATION_NAMES = {
    '72504094702': 'KBDR_Bridgeport',
    '72504614707': 'KGON_Groton',
    '72504514758': 'KHVN_NewHaven',
}

MPH_TO_MS = 0.44704

# ---------------------------------------------------------------------------
# Load and parse all LCD files
# ---------------------------------------------------------------------------
print("Loading NOAA LCD files...")

all_daily = []

for fname in sorted(os.listdir(ASOS_DIR)):
    if not fname.endswith('.csv'):
        continue

    fpath = os.path.join(ASOS_DIR, fname)
    df = pd.read_csv(fpath, low_memory=False)
    df.columns = [c.strip() for c in df.columns]

    station_id = str(df['STATION'].iloc[0]).strip()
    station_name = STATION_NAMES.get(station_id, station_id)

    df['date'] = pd.to_datetime(df['DATE'], errors='coerce').dt.normalize()

    # Keep only daily summary rows
    daily_mask = df['DailyAverageWindSpeed'].notna()
    daily = df[daily_mask][['date', 'DailyAverageWindSpeed',
                             'DailyPeakWindSpeed',
                             'DailySustainedWindSpeed']].copy()

    for col in ['DailyAverageWindSpeed', 'DailyPeakWindSpeed',
                'DailySustainedWindSpeed']:
        daily[col] = pd.to_numeric(daily[col], errors='coerce') * MPH_TO_MS

    daily['station'] = station_name
    daily = daily.dropna(subset=['date'])
    daily = daily.drop_duplicates(subset=['date'])

    all_daily.append(daily)
    print(f"  {fname}: {station_name} | {daily['date'].min().date()} "
          f"to {daily['date'].max().date()} | {len(daily):,} daily rows")

all_df = pd.concat(all_daily, ignore_index=True)
print(f"\nTotal daily records across all stations: {len(all_df):,}")

# ---------------------------------------------------------------------------
# Average across stations per date
# ---------------------------------------------------------------------------
print("Averaging across stations per date...")

daily = (
    all_df.groupby('date')
    .agg(
        wind_speed_ms     =('DailyAverageWindSpeed',  'mean'),
        wind_speed_max    =('DailyPeakWindSpeed',      'max'),
        wind_sustained_ms =('DailySustainedWindSpeed', 'mean'),
        n_stations        =('station',                 'count'),
    )
    .reset_index()
    .sort_values('date')
    .reset_index(drop=True)
)

print(f"Daily records after averaging: {len(daily):,}")
print(f"Date range: {daily['date'].min().date()} to {daily['date'].max().date()}")
print(f"Missing wind_speed_ms: {daily['wind_speed_ms'].isna().sum()} days")
print(f"Mean wind speed: {daily['wind_speed_ms'].mean():.2f} m/s")
print(f"Mean peak wind:  {daily['wind_speed_max'].mean():.2f} m/s")

# ---------------------------------------------------------------------------
# Engineer rolling wind features
# ---------------------------------------------------------------------------
print("\nEngineering rolling wind features...")

daily['wind_roll3_mean']     = daily['wind_speed_ms'].rolling(3, min_periods=2).mean()
daily['wind_roll7_mean']     = daily['wind_speed_ms'].rolling(7, min_periods=4).mean()
daily['wind_max_7d']         = daily['wind_speed_max'].rolling(7, min_periods=4).max()
daily['wind_calm']           = (daily['wind_speed_ms'] < 3.0).astype(float)
daily['wind_calm_days_7d']   = daily['wind_calm'].rolling(7, min_periods=4).sum()
daily['wind_sustained_roll7']= daily['wind_sustained_ms'].rolling(7, min_periods=4).mean()

WIND_FEATURES = [
    'wind_roll3_mean',
    'wind_roll7_mean',
    'wind_max_7d',
    'wind_calm_days_7d',
    'wind_sustained_roll7',
]

print("Wind features computed:")
for f in WIND_FEATURES:
    notna = daily[f].notna().sum()
    print(f"  {f:<25} {notna:,} non-null ({notna/len(daily)*100:.1f}%)")

daily.to_csv('data/wind_features_daily.csv', index=False)
print("\nSaved data/wind_features_daily.csv")

# ---------------------------------------------------------------------------
# Merge with hab_features_daily.csv
# ---------------------------------------------------------------------------
print("\nMerging with hab_features_daily.csv...")

hab = pd.read_csv('data/hab_features_daily.csv')
hab['date'] = pd.to_datetime(hab['date'])

wind_merge = daily[['date'] + WIND_FEATURES].copy()
hab_wind = hab.merge(wind_merge, on='date', how='left')

print(f"HAB rows: {len(hab):,}  -->  merged: {len(hab_wind):,}")
for f in WIND_FEATURES:
    coverage = hab_wind[f].notna().mean() * 100
    print(f"  {f:<25} {coverage:.1f}% coverage")

hab_wind.to_csv('data/hab_features_wind.csv', index=False)
print(f"\nSaved data/hab_features_wind.csv "
      f"({len(hab_wind):,} rows, {len(hab_wind.columns)} columns)")

# ---------------------------------------------------------------------------
# Quick correlation check
# ---------------------------------------------------------------------------
print("\n" + "=" * 55)
print("WIND FEATURE CORRELATIONS WITH bloom_28d")
print("=" * 55)

for n, min_p in [(3, 2), (6, 3), (9, 5)]:
    hab_wind[f'chl_roll{n}_mean'] = (
        hab_wind.groupby('station_name')['Chlorophyll']
          .transform(lambda x: x.rolling(n, min_periods=min_p).mean())
    )

hab_wind['bloom_28d_tmp'] = 0
for station, grp in hab_wind.groupby('station_name'):
    idx   = grp.index
    dates = grp['date'].values
    chl   = grp['Chlorophyll'].values
    labels = np.zeros(len(grp), dtype=int)
    for i in range(len(grp)):
        mask = (dates > dates[i]) & (dates <= dates[i] + np.timedelta64(28, 'D'))
        if mask.any() and (chl[mask] > 10).any():
            labels[i] = 1
    hab_wind.loc[idx, 'bloom_28d_tmp'] = labels

print(f"{'Feature':<25}  {'r':>8}  {'Direction'}")
print("-" * 60)
for f in WIND_FEATURES:
    valid = hab_wind[[f, 'bloom_28d_tmp']].dropna()
    if len(valid) > 100:
        r = valid[f].corr(valid['bloom_28d_tmp'])
        if f == 'wind_calm_days_7d':
            direction = "more calm = more blooms (expected)" if r > 0 else "unexpected"
        else:
            direction = "higher wind = fewer blooms (good)" if r < 0 else "higher wind = more blooms"
        print(f"  {f:<25}  {r:>+8.4f}  {direction}")
    else:
        print(f"  {f:<25}  insufficient data")

print("\nNext: python src/models/retrain_with_wind.py")     