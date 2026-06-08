"""
download_era5_wind.py
---------------------
Downloads ERA5 10m wind for LIS bounding box, one year at a time.
Saves each year to data/era5_raw/era5_wind_{year}.nc, then merges.

LIS bounding box: lat 40.5-41.5 N, lon 72.0-74.0 W

Run from repo root:
    python download_era5_wind.py
"""

import cdsapi
import os
import xarray as xr
import glob

RAW_DIR    = 'data/era5_raw'
OUTPUT_PATH = 'data/era5_wind_lis.nc'
os.makedirs(RAW_DIR, exist_ok=True)

c = cdsapi.Client()

years = list(range(1993, 2026))
for year in years:
    out = f'{RAW_DIR}/era5_wind_{year}.nc'
    if os.path.exists(out):
        print(f"  {year}: already exists, skipping")
        continue
    print(f"  {year}: downloading...")
    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            'product_type': 'reanalysis',
            'variable': [
                '10m_u_component_of_wind',
                '10m_v_component_of_wind',
            ],
            'year':  [str(year)],
            'month': [f'{m:02d}' for m in range(1, 13)],
            'day':   [f'{d:02d}' for d in range(1, 32)],
            'time':  ['00:00', '06:00', '12:00', '18:00'],
            'area':  [41.5, -74.0, 40.5, -72.0],  # N, W, S, E
            'format': 'netcdf',
        },
        out,
    )
    print(f"  {year}: saved to {out}")

# Merge all years into one file
if not os.path.exists(OUTPUT_PATH):
    print("\nMerging all years...")
    files = sorted(glob.glob(f'{RAW_DIR}/era5_wind_*.nc'))
    ds = xr.open_mfdataset(files, combine='by_coords')
    ds.to_netcdf(OUTPUT_PATH)
    print(f"Merged {len(files)} files -> {OUTPUT_PATH}")
else:
    print(f"\n{OUTPUT_PATH} already exists, skipping merge.")

print("Done.")