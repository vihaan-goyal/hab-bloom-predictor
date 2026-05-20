import pandas as pd
import xarray as xr
import numpy as np
import os
from datetime import datetime, timezone

# Load labels
print("Loading labels...")
labels = pd.read_csv("data/hab_features_final.csv", low_memory=False)
labels['time'] = pd.to_datetime(labels['time'], utc=True)
labels['date'] = labels['time'].dt.date

# Get list of downloaded satellite files
sat_files = {}
for fname in os.listdir("data/raw"):
    if not fname.endswith(".nc") or "DAY" not in fname or "CHL" not in fname:
        continue
    date_str = fname.split(".")[1]
    date = datetime.strptime(date_str, "%Y%m%d").date()
    sat_files[date] = os.path.join("data/raw", fname)

print(f"Satellite files available: {len(sat_files)}")

# Match labels to satellite data
records = []
for date, fpath in sorted(sat_files.items()):
    day_labels = labels[labels['date'] == date]
    if len(day_labels) == 0:
        continue
    
    ds = xr.open_dataset(fpath, engine="netcdf4")
    chl = ds['chlor_a']
    
    for _, row in day_labels.iterrows():
        # Find nearest satellite pixel to this station
        sat_val = float(chl.sel(
            lat=row['latitude'],
            lon=row['longitude'],
            method="nearest"
        ))
        
        records.append({
            'date': date,
            'latitude': row['latitude'],
            'longitude': row['longitude'],
            'insitu_chl': row['Chlorophyll'],
            'satellite_chl': sat_val,
            'bloom': row['bloom'],
            'temperature': row['sea_water_temperature'],
        })
    
    ds.close()

matched = pd.DataFrame(records)
print(f"Matched records: {len(matched)}")
print(matched.head())
matched.to_csv("data/matched_labels.csv", index=False)
print("Saved to data/matched_labels.csv")