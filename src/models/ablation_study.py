import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.metrics import roc_auc_score, average_precision_score
import warnings
warnings.filterwarnings('ignore')

print("Loading data...")
df = pd.read_csv("data/hab_features_final.csv", low_memory=False)
df['date'] = pd.to_datetime(df['date'])
df['bloom_7d_ahead'] = df.groupby('station_name')['bloom'].shift(-7)

# Full feature set
ALL_FEATURES = [
    'latitude', 'longitude', 'month',
    'sea_water_temperature', 'sea_water_salinity',
    'oxygen_concentration_in_sea_water', 'pH',
    'chl_anomaly', 'chl_climatology',
    'chl_lag3', 'chl_lag7', 'chl_lag14', 'chl_lag21',
    'chl_roll7_mean', 'chl_roll7_std',
    'total_discharge_cfs', 'discharge_lag5',
    'discharge_lag10', 'discharge_lag15',
    'discharge_roll7_mean',
]

TARGET = 'bloom_7d_ahead'

train = df[df['date'].dt.year <= 2019]
val = df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)]

def train_eval(features, name):
    X_train = train[features + [TARGET]].dropna()
    y_train = X_train.pop(TARGET)
    X_val = val[features + [TARGET]].dropna()
    y_val = X_val.pop(TARGET)
    
    if len(X_val) == 0 or y_val.sum() == 0:
        print(f"{name}: insufficient data")
        return None
    
    scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
    model = XGBClassifier(
        n_estimators=200, max_depth=6, learning_rate=0.1,
        scale_pos_weight=scale_pos_weight, random_state=42,
        n_jobs=-1, eval_metric='logloss', verbosity=0
    )
    model.fit(X_train, y_train)
    probs = model.predict_proba(X_val)[:,1]
    auc = roc_auc_score(y_val, probs)
    ap = average_precision_score(y_val, probs)
    print(f"{name:<45} AUC: {auc:.4f} | AP: {ap:.4f}")
    return auc

print("\nAblation Study Results:")
print("="*70)

# Full model
base_auc = train_eval(ALL_FEATURES, "Full model (all features)")

# Remove feature groups one at a time
ablations = [
    ([f for f in ALL_FEATURES if f not in ['chl_lag3','chl_lag7','chl_lag14','chl_lag21']], "No lagged chlorophyll"),
    ([f for f in ALL_FEATURES if f not in ['chl_roll7_mean','chl_roll7_std']], "No rolling statistics"),
    ([f for f in ALL_FEATURES if f not in ['chl_anomaly','chl_climatology']], "No climatology features"),
    ([f for f in ALL_FEATURES if f not in ['sea_water_temperature','sea_water_salinity','oxygen_concentration_in_sea_water','pH']], "No physical oceanography"),
    ([f for f in ALL_FEATURES if f not in ['total_discharge_cfs','discharge_lag5','discharge_lag10','discharge_lag15','discharge_roll7_mean']], "No river discharge"),
    ([f for f in ALL_FEATURES if f not in ['latitude','longitude']], "No location features"),
    ([f for f in ALL_FEATURES if f not in ['month']], "No seasonality"),
    (['chl_roll7_mean', 'chl_lag3', 'month', 'latitude', 'longitude'], "Minimal model (top 5 features only)"),
]

for features, name in ablations:
    train_eval(features, f"  {name}")

print("="*70)
print(f"\nBaseline (XGBoost, no temporal features): ~0.928")