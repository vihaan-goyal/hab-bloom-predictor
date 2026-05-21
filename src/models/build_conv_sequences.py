import numpy as np
import pandas as pd
import xarray as xr
import os
from datetime import datetime, timedelta
import time

print("Loading labels...")
labels = pd.read_csv("data/hab_features_final.csv", low_memory=False)
labels['date'] = pd.to_datetime(labels['date'])
labels['bloom_7d_ahead'] = labels.groupby('station_name')['bloom'].shift(-7)
labels = labels.dropna(subset=['bloom_7d_ahead'])

# Parameters
PATCH_SIZE = 8
SEQUENCE_LENGTH = 21
HALF = PATCH_SIZE // 2

# Index satellite files by date
sat_dir = "data/raw"
sat_files = {}
for fname in os.listdir(sat_dir):
    if not fname.endswith(".nc") or "DAY" not in fname or "CHL" not in fname:
        continue
    try:
        date_str = fname.split(".")[1]
        date = datetime.strptime(date_str, "%Y%m%d").date()
        sat_files[date] = os.path.join(sat_dir, fname)
    except Exception:
        continue

print(f"Satellite files indexed: {len(sat_files)}")

# Station subset
stations = labels['station_name'].unique()
labels_sub = labels[labels['station_name'].isin(stations)].copy()
print(f"Using {len(stations)} stations, {len(labels_sub)} label records")

# Build per-station metadata: fixed lat/lon and sorted dates
station_info = {}
for station_name, group in labels_sub.groupby('station_name'):
    group = group.sort_values('date').reset_index(drop=True)
    station_info[station_name] = {
        'lat': group['latitude'].iloc[0],
        'lon': group['longitude'].iloc[0],
        'dates': list(group['date'].dt.date),
        'labels': list(group['bloom_7d_ahead']),
    }

# -----------------------------------------------------------------
# Step 1: build a patch cache keyed by (date, station_name)
# Open each satellite file ONCE and extract patches for all stations
# -----------------------------------------------------------------
print("\nStep 1: Caching patches from satellite files (one file open per date)...")

all_dates_needed = set()
for info in station_info.values():
    for d in info['dates']:
        # need d and the 20 days before it for sequences
        for lag in range(SEQUENCE_LENGTH):
            all_dates_needed.add(d - timedelta(days=lag))

dates_with_files = sorted(all_dates_needed & sat_files.keys())
print(f"Dates needed: {len(all_dates_needed)} | Dates with satellite files: {len(dates_with_files)}")

patch_cache = {}   # (date, station_name) -> np.array (PATCH_SIZE, PATCH_SIZE) or None
t0 = time.time()

for i, date in enumerate(dates_with_files):
    if (i + 1) % 500 == 0 or i == 0:
        elapsed = time.time() - t0
        print(f"  [{i+1}/{len(dates_with_files)}] date={date} | elapsed={elapsed:.1f}s")

    try:
        ds = xr.open_dataset(sat_files[date], engine="netcdf4")
        chl = ds['chlor_a']

        for station_name, info in station_info.items():
            lat = info['lat']
            lon = info['lon']
            try:
                patch = chl.sel(
                    lat=slice(lat + HALF * 0.04, lat - HALF * 0.04),
                    lon=slice(lon - HALF * 0.04, lon + HALF * 0.04)
                ).values

                if patch.shape == (PATCH_SIZE, PATCH_SIZE):
                    patch_cache[(date, station_name)] = patch.copy()
                else:
                    patch_cache[(date, station_name)] = None
            except Exception:
                patch_cache[(date, station_name)] = None

        ds.close()

    except Exception as e:
        # File unreadable -- mark all stations as None for this date
        for station_name in station_info:
            patch_cache[(date, station_name)] = None

print(f"Patch cache built in {time.time()-t0:.1f}s | entries={len(patch_cache)}")

# -----------------------------------------------------------------
# Step 2: assemble sequences from the cache (pure numpy, very fast)
# -----------------------------------------------------------------
print("\nStep 2: Assembling sequences from cache...")

X_patches = []
y_labels  = []
meta      = []

for station_name, info in station_info.items():
    dates  = info['dates']
    lbls   = info['labels']
    lat    = info['lat']
    lon    = info['lon']

    print(f"  Station {station_name} ({lat:.2f}, {lon:.2f}) | {len(dates)} dates")

    for idx in range(SEQUENCE_LENGTH, len(dates) - 7):
        target_date = dates[idx]
        bloom_label = lbls[idx]

        sequence = []
        valid = True

        for lag in range(SEQUENCE_LENGTH, 0, -1):
            seq_date = dates[idx - lag]
            patch = patch_cache.get((seq_date, station_name), None)
            if patch is None:
                valid = False
                break
            sequence.append(patch)

        if valid and len(sequence) == SEQUENCE_LENGTH:
            X_patches.append(np.array(sequence))
            y_labels.append(bloom_label)
            meta.append({'date': target_date, 'station': station_name})

print(f"\nBuilt {len(X_patches)} valid sequences")

if X_patches:
    X = np.array(X_patches)
    y = np.array(y_labels)
    print(f"X shape: {X.shape}  (samples, time, H, W)")
    print(f"y shape: {y.shape}")
    print(f"Bloom rate: {y.mean()*100:.1f}%")
    np.save("data/X_conv_sequences.npy", X)
    np.save("data/y_conv_labels.npy", y)
    pd.DataFrame(meta).to_csv("data/conv_meta.csv", index=False)
    print("Saved X_conv_sequences.npy, y_conv_labels.npy, conv_meta.csv")
else:
    print("No valid sequences found -- likely too many cloud gaps.")