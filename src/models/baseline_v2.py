import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import roc_auc_score, average_precision_score, classification_report

df = pd.read_csv("data/hab_features_daily.csv")
df['date'] = pd.to_datetime(df['date'])

# Rebuild bloom_28d
df['bloom_28d'] = 0
for station, grp in df.groupby('station_name'):
    idx = grp.index
    dates = grp['date'].values
    chl = grp['Chlorophyll'].values
    labels = np.zeros(len(grp), dtype=int)
    for i in range(len(grp)):
        mask = ((dates > dates[i]) &
                (dates <= dates[i] + np.timedelta64(28, 'D')))
        if mask.any() and (chl[mask] > 10).any():
            labels[i] = 1
    df.loc[idx, 'bloom_28d'] = labels

# Add longer rolling window and trend
df['chl_roll6_mean'] = (df.groupby('station_name')['Chlorophyll']
                          .transform(lambda x: x.rolling(6, min_periods=3).mean()))
df['chl_trend'] = (df.groupby('station_name')['Chlorophyll']
                     .transform(lambda x: x.rolling(4, min_periods=3)
                     .apply(lambda v: np.polyfit(range(len(v)), v, 1)[0])))

features = [
    'Chlorophyll', 'chl_lag1', 'chl_lag2', 'chl_lag3', 'chl_lag4',
    'chl_roll3_mean', 'chl_roll6_mean', 'chl_trend',
    'chl_anomaly', 'chl_climatology',
    'do_lag1', 'temp_lag1', 'sal_lag1',
    'sea_water_temperature', 'sea_water_salinity',
    'oxygen_concentration_in_sea_water',
    'month', 'latitude_x', 'longitude_x'
]
features = [f for f in features if f in df.columns]

train = df[df['date'].dt.year <= 2019]
val   = df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)]
test  = df[df['date'].dt.year >= 2023]

def get_xy(split, features):
    # Don't dropna on the full set — only require bloom label to be present
    clean = split[features + ['bloom_28d']].dropna(subset=['bloom_28d'])
    return clean[features], clean['bloom_28d']

X_train, y_train = get_xy(train)
X_val,   y_val   = get_xy(val)
X_test,  y_test  = get_xy(test)

print(f"Train: {len(X_train):,} rows, bloom rate: {y_train.mean():.1%}")
print(f"Val:   {len(X_val):,} rows,   bloom rate: {y_val.mean():.1%}")
print(f"Test:  {len(X_test):,} rows,  bloom rate: {y_test.mean():.1%}")

pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
model = xgb.XGBClassifier(
    n_estimators=200, max_depth=4, learning_rate=0.05,
    subsample=0.8, colsample_bytree=0.8,
    scale_pos_weight=pos_weight,
    eval_metric='auc', random_state=42, verbosity=0
)
model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)

for name, X, y in [('Val', X_val, y_val), ('Test', X_test, y_test)]:
    probs = model.predict_proba(X)[:,1]
    auc = roc_auc_score(y, probs)
    ap  = average_precision_score(y, probs)
    print(f"\n{name} AUC: {auc:.3f}  Avg Precision: {ap:.3f}")
    print(classification_report(y, (probs >= 0.5).astype(int),
                                 target_names=['no bloom','bloom']))

# Feature importance
import pandas as pd
imp = pd.Series(model.feature_importances_, index=features).sort_values(ascending=False)
print("\nTop 10 feature importances:")
print(imp.head(10))