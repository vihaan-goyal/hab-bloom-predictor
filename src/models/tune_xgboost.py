import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import PredefinedSplit, GridSearchCV

df = pd.read_csv("data/hab_features_daily.csv")
df['date'] = pd.to_datetime(df['date'])

df['chl_roll6_mean'] = (df.groupby('station_name')['Chlorophyll']
                          .transform(lambda x: x.rolling(6, min_periods=3).mean()))
df['chl_roll9_mean'] = (df.groupby('station_name')['Chlorophyll']
                          .transform(lambda x: x.rolling(9, min_periods=5).mean()))
df['chl_trend'] = (df.groupby('station_name')['Chlorophyll']
                     .transform(lambda x: x.rolling(4, min_periods=3)
                     .apply(lambda v: np.polyfit(range(len(v)), v, 1)[0])))

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

features = [
    'Chlorophyll', 'chl_lag1', 'chl_lag2', 'chl_lag3', 'chl_lag4',
    'chl_roll3_mean', 'chl_roll6_mean', 'chl_roll9_mean', 'chl_trend',
    'chl_anomaly', 'chl_climatology',
    'do_lag1', 'temp_lag1', 'sal_lag1',
    'sea_water_temperature', 'sea_water_salinity',
    'oxygen_concentration_in_sea_water',
    'month', 'latitude_x', 'longitude_x'
]
features = [f for f in features if f in df.columns]

train = df[df['date'].dt.year <= 2019]
val   = df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)]

def get_xy(split, features):
    # Don't dropna on the full set — only require bloom label to be present
    clean = split[features + ['bloom_28d']].dropna(subset=['bloom_28d'])
    return clean[features], clean['bloom_28d']

X_train, y_train = get_xy(train)
X_val,   y_val   = get_xy(val)

X_combined = pd.concat([X_train, X_val]).reset_index(drop=True)
y_combined = pd.concat([y_train, y_val]).reset_index(drop=True)

split_idx = np.concatenate([
    np.full(len(X_train), -1),
    np.full(len(X_val), 0)
])
ps = PredefinedSplit(split_idx)

pos_weight = (y_train == 0).sum() / (y_train == 1).sum()

param_grid = {
    'max_depth': [3, 4, 5],
    'learning_rate': [0.03, 0.05, 0.1],
    'n_estimators': [200, 400],
    'subsample': [0.7, 0.9],
    'colsample_bytree': [0.7, 0.9],
    'min_child_weight': [1, 5, 10],
}

search = GridSearchCV(
    xgb.XGBClassifier(scale_pos_weight=pos_weight,
                      eval_metric='auc', random_state=42, verbosity=0),
    param_grid, cv=ps, scoring='roc_auc', n_jobs=-1, verbose=1
)
search.fit(X_combined, y_combined)
print(f"\nBest params: {search.best_params_}")
print(f"Best val AUC: {search.best_score_:.3f}")