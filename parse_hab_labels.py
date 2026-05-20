import pandas as pd

df = pd.read_csv("data/habsos_20240430.csv", low_memory=False)

print(f"Total records: {len(df)}")
print(f"States: {df['STATE_ID'].unique()}")

# Filter to Long Island Sound bounding box
lis = df[
    (df['LATITUDE'] >= 40.5) & (df['LATITUDE'] <= 41.5) &
    (df['LONGITUDE'] >= -73.8) & (df['LONGITUDE'] <= -71.8)
]

print(f"LIS records: {len(lis)}")
print(f"Species found: {lis['SPECIES'].unique()}")
print(f"Date range: {lis['SAMPLE_DATE'].min()} to {lis['SAMPLE_DATE'].max()}")
print(f"Categories: {lis['CATEGORY'].value_counts()}")

# Save
lis.to_csv("data/hab_labels_lis.csv", index=False)
print("Saved to data/hab_labels_lis.csv")