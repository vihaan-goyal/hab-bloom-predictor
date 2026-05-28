import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import roc_auc_score

df = pd.read_csv("data/hab_features_daily.csv")
df['date'] = pd.to_datetime(df['date'])

for n, min_p in [(3,2),(6,3),(9,5)]:
    df[f'chl_roll{n}_mean'] = (df.groupby('station_name')['Chlorophyll']
                                 .transform(lambda x: x.rolling(n, min_periods=min_p).mean()))
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

# Every numeric column that could be a feature
exclude = ['bloom_28d', 'bloom', 'bloom_7d', 'year', 'date',
           'station_name', 'Station_Name', 'season', 'cruise_name']
all_features = [c for c in df.select_dtypes(include=np.number).columns
                if c not in exclude]

print(f"Total candidate features: {len(all_features)}")

train = df[df['date'].dt.year <= 2019]
val   = df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)]
test  = df[df['date'].dt.year >= 2023]

def get_xy(split, feats):
    clean = split[feats + ['bloom_28d']].dropna(subset=['bloom_28d'])
    return clean[feats], clean['bloom_28d']

X_train, y_train = get_xy(train, all_features)
X_val,   y_val   = get_xy(val,   all_features)
X_test,  y_test  = get_xy(test,  all_features)

pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
model = xgb.XGBClassifier(
    colsample_bytree=0.7, learning_rate=0.03, max_depth=3,
    min_child_weight=10, n_estimators=200, subsample=0.7,
    scale_pos_weight=pos_weight,
    eval_metric='auc', random_state=42, verbosity=0
)
model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)

val_auc  = roc_auc_score(y_val,  model.predict_proba(X_val)[:,1])
test_auc = roc_auc_score(y_test, model.predict_proba(X_test)[:,1])
print(f"Val AUC:  {val_auc:.3f}")
print(f"Test AUC: {test_auc:.3f}")

imp = pd.Series(model.feature_importances_, index=all_features)
imp = imp[imp > 0].sort_values(ascending=False)
print(f"\nFeatures with nonzero importance: {len(imp)} of {len(all_features)}")
print("\nTop 20:")
print(imp.head(20).to_string())
print("\nZero importance (model ignored these):")
zero = [f for f in all_features if f not in imp.index or imp[f] == 0]
print(zero)