"""
download_kd490.py
-----------------
Extracts station-level Kd490 features from downloaded MODIS files.
Uses multiprocessing to parallelize across 4 CPU cores.

Run from repo root:
    python download_kd490.py
"""

import os
import numpy as np
import pandas as pd
import xarray as xr
import glob
from multiprocessing import Pool, cpu_count

RAW_DIR    = 'data/raw/kd490'
OUTPUT_CSV = 'data/kd490_features_daily.csv'

# Load station coordinates once (will be passed to workers)
df_stations = pd.read_csv('data/hab_features_tidal.csv',
                          usecols=['station_name', 'latitude_x', 'longitude_x'],
                          low_memory=False).drop_duplicates('station_name')
STATIONS = df_stations.to_dict('records')

def process_file(fpath):
    try:
        fname = os.path.basename(fpath)
        date_str = fname.split('.')[1]
        date = pd.to_datetime(date_str, format='%Y%m%d')

        ds = xr.open_dataset(fpath)
        kd_var = next((v for v in ds.data_vars if 'kd' in v.lower()), None)
        if kd_var is None:
            ds.close()
            return []

        kd = ds[kd_var].values
        lats = ds['lat'].values if 'lat' in ds.coords else ds['latitude'].values
        lons = ds['lon'].values if 'lon' in ds.coords else ds['longitude'].values
        if kd.ndim == 3:
            kd = kd[0]
        ds.close()

        records = []
        for row in STATIONS:
            lat_idx = np.argmin(np.abs(lats - row['latitude_x']))
            lon_idx = np.argmin(np.abs(lons - row['longitude_x']))
            val = float(kd[lat_idx, lon_idx])
            if not np.isnan(val) and val > 0:
                records.append({
                    'date':         date,
                    'station_name': row['station_name'],
                    'kd490':        val,
                })
        return records
    except Exception:
        return []

if __name__ == '__main__':
    if os.path.exists(OUTPUT_CSV):
        print(f"{OUTPUT_CSV} already exists, skipping extraction.")
    else:
        files = sorted(glob.glob(f'{RAW_DIR}/*.nc'))
        print(f"Processing {len(files)} files with {cpu_count()} CPUs...")

        n_workers = min(4, cpu_count())
        all_records = []
        batch = 500

        for i in range(0, len(files), batch):
            chunk = files[i:i+batch]
            with Pool(n_workers) as pool:
                results = pool.map(process_file, chunk)
            for r in results:
                all_records.extend(r)
            print(f"  {min(i+batch, len(files))}/{len(files)} files done, "
                  f"{len(all_records)} records so far")

        print(f"\nExtracted {len(all_records)} valid station-day readings")

        kd_df = pd.DataFrame(all_records)
        kd_df['date'] = pd.to_datetime(kd_df['date'])
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
        print(f"Coverage: {kd_df['date'].nunique()} days, {kd_df['station_name'].nunique()} stations")