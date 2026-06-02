"""
extract_modis_features.py
-------------------------
Fast extraction of MODIS satellite CHL features for all 50 CT DEEP stations.
Uses LIS subarray slicing for speed -- loads only ~20x55 pixels per file
instead of full 4320x8640 global grid.

Run from repo root:
    python src/features/extract_modis_features.py
    python src/features/extract_modis_features.py --test  (100 files only)
"""

import os
import re
import argparse
import numpy as np
import pandas as pd
import netCDF4 as nc

parser = argparse.ArgumentParser()
parser.add_argument('--test', action='store_true')
args = parser.parse_args()

MODIS_DIR  = 'data/raw'
OUTPUT_CSV = 'data/modis_station_daily.csv'
PATCH_HALF = 2
PATCH_SIZE = (2 * PATCH_HALF + 1) ** 2  # 25

STATIONS = {
    'A2':  (40.800835, -73.787330), 'A4':  (40.872500, -73.734170),
    'B3':  (40.918335, -73.642830), '01':  (40.963333, -73.623665),
    '02':  (40.934666, -73.600670), 'C1':  (40.955833, -73.580330),
    '03':  (40.979332, -73.560670), '04':  (40.937830, -73.519330),
    '05':  (41.009335, -73.513664), 'C2':  (40.984333, -73.502170),
    '06':  (40.961166, -73.476670), '07':  (40.950333, -73.425330),
    '08':  (41.040833, -73.418000), 'D3':  (40.993830, -73.411330),
    '09':  (41.070835, -73.336170), '10':  (40.951668, -73.332500),
    'E1':  (41.019333, -73.291336), '12':  (41.108665, -73.253000),
    '13':  (41.058334, -73.234340), '15':  (40.931330, -73.221170),
    '14':  (40.991500, -73.218834), 'F2':  (41.080334, -73.165340),
    '16':  (41.120335, -73.162500), 'F3':  (41.017834, -73.144500),
    '18':  (41.122334, -73.090000), '19':  (41.055332, -73.080830),
    '20':  (40.994000, -73.042336), '22':  (41.082333, -73.022835),
    '21':  (41.164000, -73.014830), 'H2':  (41.178000, -72.960500),
    '23':  (41.140167, -72.948830), 'H4':  (41.101665, -72.934000),
    '25':  (40.981000, -72.918170), 'H6':  (41.026000, -72.913500),
    '26':  (41.209167, -72.908500), '27':  (41.158670, -72.849500),
    '28':  (41.078167, -72.833500), '29':  (41.231500, -72.829666),
    '30':  (41.196335, -72.775330), '31':  (41.004166, -72.768330),
    '32':  (41.241500, -72.665665), 'I2':  (41.137500, -72.655000),
    '33':  (41.003834, -72.651170), '34':  (41.246000, -72.468330),
    'J2':  (41.182000, -72.457664), 'J4':  (41.097500, -72.450000),
    '36':  (41.270500, -72.275500), 'K2':  (41.234333, -72.265830),
    'M3':  (41.237167, -72.053340), 'N3':  (41.233334, -71.857666),
}
STATION_NAMES = list(STATIONS.keys())

# ---------------------------------------------------------------------------
# File list
# ---------------------------------------------------------------------------
DATE_RE = re.compile(r'AQUA_MODIS\.(\d{8})\.L3m\.DAY\.CHL\.chlor_a\.4km\.nc')
all_files = []
for fname in os.listdir(MODIS_DIR):
    m = DATE_RE.match(fname)
    if m:
        all_files.append((m.group(1), os.path.join(MODIS_DIR, fname)))
all_files.sort(key=lambda x: x[0])

print(f"Found {len(all_files):,} MODIS files")
print(f"Date range: {all_files[0][0]} to {all_files[-1][0]}")

if args.test:
    step = max(1, len(all_files) // 100)
    all_files = all_files[::step][:100]
    print(f"TEST MODE: using {len(all_files)} files")

# ---------------------------------------------------------------------------
# Pre-compute indices
# ---------------------------------------------------------------------------
print("Loading lat/lon grid...")
f0 = nc.Dataset(all_files[0][1])
lats = f0.variables['lat'][:].data.astype(np.float32)
lons = f0.variables['lon'][:].data.astype(np.float32)
f0.close()

print("Pre-computing station pixel indices...")
lat_idxs = np.array([int(np.argmin(np.abs(lats - STATIONS[s][0])))
                     for s in STATION_NAMES])
lon_idxs = np.array([int(np.argmin(np.abs(lons - STATIONS[s][1])))
                     for s in STATION_NAMES])

lat_min_idx = max(0, int(lat_idxs.min()) - PATCH_HALF - 2)
lat_max_idx = min(len(lats), int(lat_idxs.max()) + PATCH_HALF + 3)
lon_min_idx = max(0, int(lon_idxs.min()) - PATCH_HALF - 2)
lon_max_idx = min(len(lons), int(lon_idxs.max()) + PATCH_HALF + 3)

lat_idxs_crop = lat_idxs - lat_min_idx
lon_idxs_crop = lon_idxs - lon_min_idx

print(f"LIS subarray: {lat_max_idx-lat_min_idx} x {lon_max_idx-lon_min_idx} pixels")

# ---------------------------------------------------------------------------
# Sequential extraction with subarray speedup
# ---------------------------------------------------------------------------
n_files   = len(all_files)
log_every = max(1, n_files // 20)
all_records = []

print(f"\nExtracting from {n_files:,} files...")

for i, (date_str, fpath) in enumerate(all_files):
    if i % log_every == 0 or i == n_files - 1:
        pct = (i + 1) / n_files * 100
        print(f"  {pct:4.0f}% ({i+1:,}/{n_files:,}) -- {date_str}")

    try:
        f = nc.Dataset(fpath)
        chl_raw = f.variables['chlor_a'][lat_min_idx:lat_max_idx,
                                         lon_min_idx:lon_max_idx]
        f.close()
    except Exception as e:
        print(f"  ERROR {date_str}: {e}")
        continue

    if hasattr(chl_raw, 'mask'):
        data = chl_raw.data.astype(np.float32)
        mask = chl_raw.mask
    else:
        data = chl_raw.astype(np.float32)
        mask = np.zeros_like(data, dtype=bool)

    mask |= (data <= 0) | (data > 1000)

    date = pd.to_datetime(date_str, format='%Y%m%d')

    for j, stn in enumerate(STATION_NAMES):
        r  = lat_idxs_crop[j]
        c  = lon_idxs_crop[j]
        r0, r1 = r - PATCH_HALF, r + PATCH_HALF + 1
        c0, c1 = c - PATCH_HALF, c + PATCH_HALF + 1

        if r0 < 0 or c0 < 0 or r1 > data.shape[0] or c1 > data.shape[1]:
            all_records.append((date, stn, np.nan, 0.0))
            continue

        valid_vals = data[r0:r1, c0:c1][~mask[r0:r1, c0:c1]]
        n_valid    = len(valid_vals)
        all_records.append((
            date, stn,
            float(np.mean(valid_vals)) if n_valid > 0 else np.nan,
            n_valid / PATCH_SIZE,
        ))

print(f"\nExtraction complete. {len(all_records):,} records")

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
out_df = pd.DataFrame(all_records,
                      columns=['date', 'station_name',
                               'sat_chl_mean', 'sat_chl_valid_frac'])
out_df = out_df.sort_values(['date', 'station_name']).reset_index(drop=True)

n_valid  = out_df['sat_chl_mean'].notna().sum()
coverage = n_valid / len(out_df) * 100
print(f"Coverage: {n_valid:,} / {len(out_df):,} ({coverage:.1f}%)")
print(f"Mean sat CHL: {out_df['sat_chl_mean'].mean():.2f} µg/L")

print("\nPer-station coverage (%):")
stn_cov = (out_df.groupby('station_name')['sat_chl_mean']
           .apply(lambda x: x.notna().mean() * 100)
           .sort_values(ascending=False))
print(stn_cov.round(1).to_string())

out_df.to_csv(OUTPUT_CSV, index=False)
print(f"\nSaved {OUTPUT_CSV} ({len(out_df):,} rows)")
print("Next: python src/features/merge_modis_features.py")