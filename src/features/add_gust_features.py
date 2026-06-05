"""
add_gust_features.py
--------------------
Extracts HourlyWindGustSpeed from NOAA LCD files in data/raw/asos_wind/,
aggregates to a daily max gust (across all three CT stations), computes
a 3-day rolling max (max_gust_3d), and saves data/gust_features_daily.csv.

Three stations:
  72504094702 -- Igor I Sikorsky Memorial Airport (Bridgeport CT)
  72504614707 -- Groton New London Airport (eastern LIS)
  72504514758 -- New Haven Tweed Airport (western LIS)

Wind gust units in LCD are mph -- converted to m/s.

Run from repo root:
    python src/features/add_gust_features.py
"""

import warnings
warnings.filterwarnings('ignore')

import os
import pandas as pd
import numpy as np

ASOS_DIR = 'data/raw/asos_wind'
OUT_PATH = 'data/gust_features_daily.csv'

STATION_NAMES = {
    '72504094702': 'KBDR_Bridgeport',
    '72504614707': 'KGON_Groton',
    '72504514758': 'KHVN_NewHaven',
}

MPH_TO_MS = 0.44704

# ---------------------------------------------------------------------------
# Extract hourly gust records from all LCD files
# ---------------------------------------------------------------------------
print("Loading NOAA LCD files from data/raw/asos_wind/ ...")
all_hourly = []
for fname in sorted(os.listdir(ASOS_DIR)):
    if not fname.endswith('.csv'):
        continue
    fpath = os.path.join(ASOS_DIR, fname)
    df = pd.read_csv(fpath, low_memory=False)
    df.columns = [c.strip() for c in df.columns]

    station_id = str(df['STATION'].iloc[0]).strip()
    station_name = STATION_NAMES.get(station_id, station_id)

    # FM-15 = METAR (hourly), FM-16 = SPECI (special obs) -- both have gust data
    hourly_mask = df['REPORT_TYPE'].str.contains('FM-15|FM-16|METAR', na=False)
    hourly = df[hourly_mask].copy()
    if len(hourly) == 0:
        hourly = df[df['HourlyWindSpeed'].notna()].copy()

    hourly['date'] = pd.to_datetime(hourly['DATE'], errors='coerce').dt.normalize()
    hourly['gust_ms'] = pd.to_numeric(hourly['HourlyWindGustSpeed'], errors='coerce') * MPH_TO_MS

    hourly['station'] = station_name
    all_hourly.append(hourly[['date', 'station', 'gust_ms']].dropna(subset=['date']))

hourly_df = pd.concat(all_hourly, ignore_index=True)
print(f"  Total hourly records: {len(hourly_df):,}")
print(f"  Non-null gusts: {hourly_df['gust_ms'].notna().sum():,} "
      f"({hourly_df['gust_ms'].notna().mean()*100:.1f}%)")
print(f"  Date range: {hourly_df['date'].min().date()} to {hourly_df['date'].max().date()}")

# ---------------------------------------------------------------------------
# Aggregate to daily max gust across all stations
# ---------------------------------------------------------------------------
daily = (
    hourly_df.groupby('date')
    .agg(max_gust_ms=('gust_ms', 'max'))
    .reset_index()
    .sort_values('date')
    .reset_index(drop=True)
)

# 3-day rolling max (min 2 days to avoid leading NaNs for the first gap)
daily['max_gust_3d'] = daily['max_gust_ms'].rolling(3, min_periods=2).max()

daily.to_csv(OUT_PATH, index=False)
print(f"\nSaved {OUT_PATH}  ({len(daily):,} days)")
print(f"  max_gust_3d non-null: {daily['max_gust_3d'].notna().sum():,} "
      f"({daily['max_gust_3d'].notna().mean()*100:.1f}%)")
print(f"  max_gust_3d range: {daily['max_gust_3d'].min():.2f} – "
      f"{daily['max_gust_3d'].max():.2f} m/s")
