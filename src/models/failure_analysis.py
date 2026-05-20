import pandas as pd
import numpy as np
from xgboost import XGBClassifier

df = pd.read_csv("data/hab_features_final.csv", low_memory=False)
df['date'] = pd.to_datetime(df['date'])
df['bloom_7d_ahead'] = df.groupby('station_name')['bloom'].shift(-7)

features = [
    'latitude', 'longitude', 'month',
    'chl_anomaly', 'chl_climatology',
    'chl_roll7_mean', 'chl_roll7_std',
    'chl_lag3', 'chl_lag7', 'chl_lag14', 'chl_lag21',
]

train = df[df['date'].dt.year <= 2019]
val = df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)]

X_train = train[features + ['bloom_7d_ahead']].dropna()
y_train = X_train.pop('bloom_7d_ahead')

X_val_full = val[features + ['bloom_7d_ahead', 'station_name', 'date', 'month']].dropna()
meta = X_val_full[['station_name', 'date', 'month']].copy()
y_val = X_val_full['bloom_7d_ahead'].copy()
X_val = X_val_full[features].copy()

scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
model = XGBClassifier(
    n_estimators=200, max_depth=6, learning_rate=0.1,
    scale_pos_weight=scale_pos_weight, random_state=42,
    n_jobs=-1, eval_metric='logloss', verbosity=0
)

X_val = X_val_full[features].copy().reset_index(drop=True)
X_val = X_val.loc[:, ~X_val.columns.duplicated()]
y_val = X_val_full['bloom_7d_ahead'].copy().reset_index(drop=True)
X_train = X_train.reset_index(drop=True)
y_train = y_train.reset_index(drop=True)

print(f"X_train shape: {X_train.shape}")
print(f"X_val shape: {X_val.shape}")
print(f"X_train columns: {list(X_train.columns)}")
print(f"X_val columns: {list(X_val.columns)}")

model.fit(X_train.values, y_train.values)
probs = model.predict_proba(X_val.values)[:,1]
preds = (probs > 0.5).astype(int)

results = pd.DataFrame({
    'station_name': meta['station_name'].values.tolist(),
    'date': meta['date'].values.tolist(),
    'month': meta['month'].values.tolist(),
    'y_true': y_val.values,
    'y_pred': preds,
    'prob': probs
})
results['y_true'] = y_val.values
results['y_pred'] = preds
results['prob'] = probs

fp = results[(results['y_pred'] == 1) & (results['y_true'] == 0)]
fn = results[(results['y_pred'] == 0) & (results['y_true'] == 1)]

print(f"False positives: {len(fp)}")
print(f"False negatives: {len(fn)}")
print(f"\nFP by month:\n{fp['month'].value_counts().sort_index()}")
print(f"\nFN by month:\n{fn['month'].value_counts().sort_index()}")
print(f"\nFP by station (top 10):\n{fp['station_name'].value_counts().head(10)}")
print(f"\nFN by station (top 10):\n{fn['station_name'].value_counts().head(10)}")