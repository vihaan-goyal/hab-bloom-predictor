import pandas as pd
import numpy as np
from datetime import timedelta

print("Loading data...")
df = pd.read_csv("data/hab_features_final.csv", low_memory=False)
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values(['station_name', 'date']).reset_index(drop=True)

# Features to use in sequences
seq_features = [
    'sea_water_temperature', 'sea_water_salinity',
    'oxygen_concentration_in_sea_water', 'pH',
    'chl_anomaly', 'chl_climatology',
    'chl_lag3', 'chl_lag7', 'chl_lag14', 'chl_lag21',
    'chl_roll7_mean', 'chl_roll7_std',
    'month', 'latitude', 'longitude'
]

SEQUENCE_LENGTH = 21  # days of history
FORECAST_HORIZON = 7  # days ahead to predict

print("Building sequences...")
X_sequences = []
y_labels = []
meta = []  # date and station for each sample

stations = df['station_name'].unique()

for i, station in enumerate(stations):
    if i % 10 == 0:
        print(f"  Processing station {i+1}/{len(stations)}: {station}")
    
    station_df = df[df['station_name'] == station].copy()
    station_df = station_df.dropna(subset=seq_features + ['bloom'])
    
    if len(station_df) < SEQUENCE_LENGTH + FORECAST_HORIZON:
        continue
    
    for idx in range(SEQUENCE_LENGTH, len(station_df) - FORECAST_HORIZON):
        # Get sequence of past 21 days
        seq = station_df.iloc[idx-SEQUENCE_LENGTH:idx][seq_features].values
        
        # Label is bloom 7 days ahead
        label = station_df.iloc[idx + FORECAST_HORIZON]['bloom']
        date = station_df.iloc[idx]['date']
        
        if np.isnan(seq).any():
            continue
            
        X_sequences.append(seq)
        y_labels.append(label)
        meta.append({'date': date, 'station': station})

X = np.array(X_sequences)
y = np.array(y_labels)

print(f"\nSequence dataset shape: {X.shape}")
print(f"Labels shape: {y.shape}")
print(f"Bloom rate: {y.mean()*100:.1f}%")

# Save
np.save("data/X_sequences.npy", X)
np.save("data/y_labels.npy", y)
meta_df = pd.DataFrame(meta)
meta_df.to_csv("data/sequence_meta.csv", index=False)

print("Saved X_sequences.npy, y_labels.npy, sequence_meta.csv")