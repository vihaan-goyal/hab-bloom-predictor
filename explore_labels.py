import pandas as pd

df = pd.read_csv("data/DEEP_WQ_1991-2000.csv", low_memory=False, skiprows=[1])

# Convert to numeric
df['Chlorophyll'] = pd.to_numeric(df['Chlorophyll'], errors='coerce')
df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

print(f"Shape: {df.shape}")
print(f"\nChlorophyll stats:")
print(df['Chlorophyll'].describe())
print(f"\nMax chlorophyll: {df['Chlorophyll'].max()}")
print(f"Readings above 10 ug/L (bloom threshold): {(df['Chlorophyll'] > 10).sum()}")
print(f"Readings above 20 ug/L (high bloom): {(df['Chlorophyll'] > 20).sum()}")