import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, average_precision_score, classification_report
import xgboost as xgb
import joblib

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

features = [
    'Chlorophyll', 'chl_lag1', 'chl_lag2', 'chl_lag3', 'chl_lag4',
    'chl_roll3_mean', 'chl_roll6_mean', 'chl_roll9_mean', 'chl_trend',
    'chl_anomaly', 'chl_climatology',
    'do_lag1', 'temp_lag1', 'sal_lag1',
    'sea_water_temperature', 'sea_water_salinity',
    'oxygen_concentration_in_sea_water',
    'month', 'latitude_x', 'longitude_x',
    'nox_lag2', 'dip_lag2', 'dip_change', 'dip_x_month',
]
features = [f for f in features if f in df.columns]

train = df[df['date'].dt.year <= 2019]
val   = df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)]
test  = df[df['date'].dt.year >= 2023]

def get_xy(split):
    clean = split[features + ['bloom_28d']].dropna(subset=['bloom_28d'])
    return clean[features], clean['bloom_28d']

X_train, y_train = get_xy(train)
X_val,   y_val   = get_xy(val)
X_test,  y_test  = get_xy(test)

print(f"Train: {len(X_train):,} | Val: {len(X_val):,} | Test: {len(X_test):,}")
print(f"Bloom rates: train={y_train.mean():.1%} val={y_val.mean():.1%} test={y_test.mean():.1%}")

results = {}

# ── Logistic Regression ───────────────────────────────────────────────────────
print("\n--- Logistic Regression ---")
scaler = StandardScaler()
X_tr_s = pd.DataFrame(scaler.fit_transform(X_train.fillna(X_train.median())),
                       columns=features)
X_v_s  = pd.DataFrame(scaler.transform(X_val.fillna(X_train.median())),
                       columns=features)
X_te_s = pd.DataFrame(scaler.transform(X_test.fillna(X_train.median())),
                       columns=features)

lr = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
lr.fit(X_tr_s, y_train)
for name, X, y in [('Val', X_v_s, y_val), ('Test', X_te_s, y_test)]:
    probs = lr.predict_proba(X)[:,1]
    auc = roc_auc_score(y, probs)
    print(f"  {name} AUC: {auc:.3f}")
    results[f'LR_{name}'] = probs

# ── Random Forest ─────────────────────────────────────────────────────────────
print("\n--- Random Forest ---")
X_tr_f = X_train.fillna(X_train.median())
X_v_f  = X_val.fillna(X_train.median())
X_te_f = X_test.fillna(X_train.median())

rf = RandomForestClassifier(n_estimators=200, class_weight='balanced',
                             random_state=42, n_jobs=-1)
rf.fit(X_tr_f, y_train)
for name, X, y in [('Val', X_v_f, y_val), ('Test', X_te_f, y_test)]:
    probs = rf.predict_proba(X)[:,1]
    auc = roc_auc_score(y, probs)
    print(f"  {name} AUC: {auc:.3f}")
    results[f'RF_{name}'] = probs

# ── XGBoost ───────────────────────────────────────────────────────────────────
print("\n--- XGBoost ---")
pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
xgb_model = xgb.XGBClassifier(
    colsample_bytree=0.7, learning_rate=0.03, max_depth=3,
    min_child_weight=10, n_estimators=200, subsample=0.7,
    scale_pos_weight=pos_weight,
    eval_metric='auc', random_state=42, verbosity=0
)
xgb_model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
for name, X, y in [('Val', X_val, y_val), ('Test', X_test, y_test)]:
    probs = xgb_model.predict_proba(X)[:,1]
    auc = roc_auc_score(y, probs)
    ap  = average_precision_score(y, probs)
    print(f"  {name} AUC: {auc:.3f}  Avg Precision: {ap:.3f}")
    results[f'XGB_{name}'] = probs

# Save XGBoost probabilities for ensemble later
pd.Series(results['XGB_Val'],  name='xgb_prob').to_csv("data/xgb_val_probs.csv",  index=False)
pd.Series(results['XGB_Test'], name='xgb_prob').to_csv("data/xgb_test_probs.csv", index=False)
np.save("data/y_val.npy",  y_val.values)
np.save("data/y_test.npy", y_test.values)
joblib.dump(xgb_model, "data/xgb_model.pkl")
print("\nSaved XGBoost probabilities and model for ensemble.")