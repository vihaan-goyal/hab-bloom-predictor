"""
download_kd490.py
-----------------
Downloads NASA MODIS Aqua L3 daily 4km Kd490 (diffuse attenuation coefficient
at 490nm) for Long Island Sound region (1993-2025) and builds daily station-
level features.

Kd490 measures water clarity -- high values = turbid/murky water.
Relevant to Vaudrey's hypothesis: turbidity suppresses blooms at A4/B3
even when CHL looks bloom-favorable (explaining 2024 false positives).

Short name: MODISA_L3m_KD (same as CHL but KD product)
Variable:   Kd_490

LIS bounding box: lat 40.5-41.5 N, lon -74.0 to -72.0 W

Run from repo root:
    python download_kd490.py
"""

import earthaccess
from dotenv import load_dotenv
import os
import numpy as np
import pandas as pd
import xarray as xr
import glob

load_dotenv()

RAW_DIR    = 'data/raw/kd490'
OUTPUT_CSV = 'data/kd490_features_daily.csv'
os.makedirs(RAW_DIR, exist_ok=True)

# LIS bounding box
LAT_MIN, LAT_MAX = 40.5, 41.5
LON_MIN, LON_MAX = -74.0, -72.0

# ── DOWNLOAD ──────────────────────────────────────────────────────────────────
if not os.path.exists(OUTPUT_CSV):
    print("Logging in to NASA Earthdata...")
    earthaccess.login(strategy="environment")

    print("Searching for MODISA_L3m_KD daily 4km files (2003-2025)...")
    results = earthaccess.search_data(
        short_name="MODISA_L3m_KD",
        temporal=("2003-01-01", "2025-12-31"),
        bounding_box=(LON_MIN, LAT_MIN, LON_MAX, LAT_MAX),
    )
    filtered = [r for r in results if "DAY" in str(r['umm']) and "4km" in str(r['umm'])]
    print(f"Found {len(filtered)} daily 4km files")

    if len(filtered) == 0:
        # Try without bounding box filter -- some collections don't support it
        print("Retrying without bounding box...")
        results = earthaccess.search_data(
            short_name="MODISA_L3m_KD",
            temporal=("2003-01-01", "2025-12-31"),
        )
        filtered = [r for r in results if "DAY" in str(r['umm']) and "4km" in str(r['umm'])]
        print(f"Found {len(filtered)} daily 4km files")

    print(f"Downloading to {RAW_DIR}...")
    files = earthaccess.download(filtered, RAW_DIR)
    print(f"Downloaded {len(files)} files")
else:
    print(f"{OUTPUT_CSV} already exists, skipping download.")
    files = sorted(glob.glob(f'{RAW_DIR}/*.nc'))
    print(f"Found {len(files)} existing files")

# ── EXTRACT STATION-LEVEL KD490 ───────────────────────────────────────────────
# Load station coordinates
print("\nLoading station coordinates...")
df_stations = pd.read_csv('data/hab_features_tidal.csv',
                          usecols=['station_name', 'latitude_x', 'longitude_x'],
                          low_memory=False).drop_duplicates('station_name')
print(f"  {len(df_stations)} stations")

files = sorted(glob.glob(f'{RAW_DIR}/*.nc'))
print(f"\nProcessing {len(files)} Kd490 files...")

records = []
for i, fpath in enumerate(files):
    if i % 100 == 0:
        print(f"  {i}/{len(files)}: {os.path.basename(fpath)}")
    try:
        ds = xr.open_dataset(fpath)

        # Get Kd490 variable (may be named 'Kd_490' or 'kd_490')
        kd_var = None
        for v in ds.data_vars:
            if 'kd' in v.lower() or 'kd490' in v.lower():
                kd_var = v
                break
        if kd_var is None:
            ds.close()
            continue

        # Parse date from filename: AQUA_MODIS.YYYYMMDD.L3m...
        fname = os.path.basename(fpath)
        date_str = fname.split('.')[1]
        date = pd.to_datetime(date_str, format='%Y%m%d')

        kd = ds[kd_var]
        lats = ds['lat'].values if 'lat' in ds.coords else ds['latitude'].values
        lons = ds['lon'].values if 'lon' in ds.coords else ds['longitude'].values

        # Extract value at each station via nearest-neighbor
        for _, row in df_stations.iterrows():
            lat_idx = np.argmin(np.abs(lats - row['latitude_x']))
            lon_idx = np.argmin(np.abs(lons - row['longitude_x']))
            val = float(kd.values[0, lat_idx, lon_idx] if kd.ndim == 3
                        else kd.values[lat_idx, lon_idx])
            if not np.isnan(val) and val > 0:
                records.append({
                    'date':         date,
                    'station_name': row['station_name'],
                    'kd490':        val,
                })
        ds.close()
    except Exception as e:
        continue

print(f"\nExtracted {len(records)} valid station-day readings")

if len(records) == 0:
    print("No valid readings extracted -- check file format")
else:
    kd_df = pd.DataFrame(records)
    kd_df['date'] = pd.to_datetime(kd_df['date'])

    # Add rolling features per station
    kd_df = kd_df.sort_values(['station_name', 'date']).reset_index(drop=True)
    kd_df['kd490_roll7']  = kd_df.groupby('station_name')['kd490'].transform(
        lambda x: x.rolling(7, min_periods=3).mean())
    kd_df['kd490_roll14'] = kd_df.groupby('station_name')['kd490'].transform(
        lambda x: x.rolling(14, min_periods=5).mean())
    kd_df['kd490_anom']   = kd_df['kd490'] - kd_df.groupby(
        ['station_name', kd_df['date'].dt.month])['kd490'].transform('mean')

    kd_df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved to {OUTPUT_CSV}")
    print(f"Date range: {kd_df['date'].min()} to {kd_df['date'].max()}")
    print(f"Coverage: {kd_df['date'].nunique()} unique days, "
          f"{kd_df['station_name'].nunique()} stations")
    print(f"\nKd490 stats:")
    print(kd_df['kd490'].describe())
    print(f"\nCorrelation with bloom_28d (need to merge to check):")
    print("Run test_kd490_features.py after this completes.")