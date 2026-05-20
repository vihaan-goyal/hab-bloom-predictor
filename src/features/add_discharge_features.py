import pandas as pd
import numpy as np

print("Loading data...")
df = pd.read_csv("data/hab_features_final.csv", low_memory=False)
df['date'] = pd.to_datetime(df['date'])

discharge = pd.read_csv("data/usgs_discharge.csv")
discharge['date'] = pd.to_datetime(discharge['date'])

# Compute total discharge across all three rivers
discharge['total_discharge_cfs'] = (
    discharge['connecticut_river_discharge_cfs'] +
    discharge['thames_river_discharge_cfs'] +
    discharge['housatonic_river_discharge_cfs']
)

# Add lagged discharge features -- nutrient loading takes days to reach offshore
for lag in [5, 10, 15]:
    discharge[f'discharge_lag{lag}'] = discharge['total_discharge_cfs'].shift(lag)

# Rolling mean -- sustained high discharge matters more than single spike
discharge['discharge_roll7_mean'] = discharge['total_discharge_cfs'].rolling(7, min_periods=2).mean()

print(f"Discharge shape: {discharge.shape}")

# Merge into main dataset
df_merged = df.merge(discharge[[
    'date', 'total_discharge_cfs',
    'discharge_lag5', 'discharge_lag10', 'discharge_lag15',
    'discharge_roll7_mean'
]], on='date', how='left')

print(f"Original shape: {df.shape}")
print(f"Merged shape: {df_merged.shape}")

# Check coverage
coverage = df_merged['total_discharge_cfs'].notna().mean() * 100
print(f"Discharge coverage: {coverage:.1f}%")

# Correlation with bloom
print("\nDischarge feature correlations with bloom:")
for col in ['total_discharge_cfs', 'discharge_lag5', 'discharge_lag10', 'discharge_lag15', 'discharge_roll7_mean']:
    corr = df_merged[col].corr(df_merged['bloom'])
    print(f"  {col}: {corr:.3f}")

df_merged.to_csv("data/hab_features_final.csv", index=False)
print("\nSaved updated hab_features_final.csv")