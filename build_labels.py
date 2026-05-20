import pandas as pd
import os

files = [
    "data/DEEP_WQ_1991-2000.csv",
    "data/DEEP_WQ_2001-2010.csv",
    "data/DEEP_WQ_2011-2020.csv",
    "data/DEEP_WQ_2021-Present.csv",
]

chunks = []
for f in files:
    print(f"Loading {f}...")
    df = pd.read_csv(f, low_memory=False, skiprows=[1])
    df['Chlorophyll'] = pd.to_numeric(df['Chlorophyll'], errors='coerce')
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    df['sea_water_temperature'] = pd.to_numeric(df['sea_water_temperature'], errors='coerce')
    df['sea_water_salinity'] = pd.to_numeric(df['sea_water_salinity'], errors='coerce')
    df['oxygen_concentration_in_sea_water'] = pd.to_numeric(df['oxygen_concentration_in_sea_water'], errors='coerce')
    chunks.append(df)

combined = pd.concat(chunks, ignore_index=True)
print(f"\nTotal records: {len(combined)}")

# Parse time
combined['time'] = pd.to_datetime(combined['time'], errors='coerce')
combined = combined.dropna(subset=['time', 'latitude', 'longitude', 'Chlorophyll'])

# Filter to LIS bounding box
lis = combined[
    (combined['latitude'] >= 40.5) & (combined['latitude'] <= 41.5) &
    (combined['longitude'] >= -73.8) & (combined['longitude'] <= -71.8)
]

print(f"LIS records with chlorophyll: {len(lis)}")

# Define bloom label
lis = lis.copy()
lis['bloom'] = (lis['Chlorophyll'] > 10).astype(int)

print(f"Bloom events (CHL > 10): {lis['bloom'].sum()}")
print(f"Non-bloom: {(lis['bloom'] == 0).sum()}")
print(f"Date range: {lis['time'].min()} to {lis['time'].max()}")

# Save
lis.to_csv("data/hab_labels_lis.csv", index=False)
print("\nSaved to data/hab_labels_lis.csv")