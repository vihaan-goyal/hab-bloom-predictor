import numpy as np
import pandas as pd
import xarray as xr
import os
from datetime import datetime

print("Loading labels...")
labels = pd.read_csv("data/hab_features_final.csv", low_memory=False)
labels['date'] = pd.to_datetime(labels['date'])
labels['bloom_7d_ahead'] = labels.groupby('station_name')['bloom'].shift(-7)
labels = labels.dropna(subset=['bloom_7d_ahead'])

# Parameters
PATCH_SIZE = 8       # 8x8 pixels = 32km x 32km
SEQUENCE_LENGTH = 21
HALF = PATCH_SIZE // 2

# Get satellite files indexed by date
sat_dir = "data/raw"
sat_files = {}
for fname in os.listdir(sat_dir):
    if not fname.endswith(".nc") or "DAY" not in fname or "CHL" not in fname:
        continue
    try:
        date_str = fname.split(".")[1]
        date = datetime.strptime(date_str, "%Y%m%d").date()
        sat_files[date] = os.path.join(sat_dir, fname)
    except:
        continue

print(f"Satellite files: {len(sat_files)}")

# Use subset for testing on laptop
# Get unique station-date combinations
stations = labels['station_name'].unique()[:10]  # just 10 stations for now
labels_sub = labels[labels['station_name'].isin(stations)]

print(f"Using {len(stations)} stations, {len(labels_sub)} records")

X_patches = []
y_labels = []
meta = []

station_groups = labels_sub.groupby('station_name')

for station_name, group in station_groups:
    group = group.sort_values('date').reset_index(drop=True)
    lat = group['latitude'].iloc[0]
    lon = group['longitude'].iloc[0]
    
    print(f"Processing station {station_name} ({lat:.2f}, {lon:.2f})...")
    
    for idx in range(SEQUENCE_LENGTH, len(group) - 7):
        target_date = group.iloc[idx]['date'].date()
        bloom_label = group.iloc[idx]['bloom_7d_ahead']
        
        # Get sequence of satellite patches
        sequence = []
        valid = True
        
        for lag in range(SEQUENCE_LENGTH, 0, -1):
            seq_date = group.iloc[idx - lag]['date'].date()
            
            if seq_date not in sat_files:
                valid = False
                break
            
            try:
                ds = xr.open_dataset(sat_files[seq_date], engine="netcdf4")
                chl = ds['chlor_a']
                
                patch = chl.sel(
                    lat=slice(lat + HALF * 0.04, lat - HALF * 0.04),
                    lon=slice(lon - HALF * 0.04, lon + HALF * 0.04)
                ).values
                
                ds.close()
                
                if patch.shape != (PATCH_SIZE, PATCH_SIZE):
                    valid = False
                    break
                    
                sequence.append(patch)
            except:
                valid = False
                break
        
        if valid and len(sequence) == SEQUENCE_LENGTH:
            X_patches.append(np.array(sequence))
            y_labels.append(bloom_label)
            meta.append({'date': target_date, 'station': station_name})

print(f"\nBuilt {len(X_patches)} spatial sequences")

if X_patches:
    X = np.array(X_patches)
    y = np.array(y_labels)
    print(f"X shape: {X.shape}")  # (samples, time, height, width)
    np.save("data/X_conv_sequences.npy", X)
    np.save("data/y_conv_labels.npy", y)
    pd.DataFrame(meta).to_csv("data/conv_meta.csv", index=False)
    print("Saved.")
else:
    print("No valid sequences found -- likely cloud coverage gaps")