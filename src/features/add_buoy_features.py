import pandas as pd

print("Loading data...")
df = pd.read_csv("data/hab_features_final.csv", low_memory=False)
df['date'] = pd.to_datetime(df['date'])

buoys = pd.read_csv("data/noaa_buoys_daily.csv")
buoys['date'] = pd.to_datetime(buoys['date'])

# Average across all buoys per day
buoy_daily = buoys.groupby('date').agg({
    'WSPD': 'mean',
    'GST': 'mean',
    'WVHT': 'mean',
    'WTMP': 'mean',
    'ATMP': 'mean',
    'BAR': 'mean'
}).reset_index()

# Add lags -- wind yesterday and 2 days ago affects today's stratification
for lag in [1, 2, 3]:
    buoy_daily[f'wspd_lag{lag}'] = buoy_daily['WSPD'].shift(lag)
    buoy_daily[f'wvht_lag{lag}'] = buoy_daily['WVHT'].shift(lag)

buoy_daily['wspd_roll7'] = buoy_daily['WSPD'].rolling(7, min_periods=2).mean()

print(f"Buoy daily shape: {buoy_daily.shape}")

merged = df.merge(buoy_daily, on='date', how='left')
coverage = merged['WSPD'].notna().mean() * 100
print(f"Buoy coverage: {coverage:.1f}%")

print("\nBuoy correlations with bloom:")
for col in ['WSPD', 'GST', 'WVHT', 'wspd_lag1', 'wspd_roll7']:
    corr = merged[col].corr(merged['bloom'])
    print(f"  {col}: {corr:.3f}")

merged.to_csv("data/hab_features_final.csv", index=False)
print("Saved.")