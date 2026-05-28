import pandas as pd
import numpy as np
from sklearn.metrics import precision_score, recall_score, roc_auc_score, classification_report
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import xgboost as xgb

print("Loading data...")
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
    'neighbor_chl3_mean', 'neighbor_chl3_lag1',
]
features = [f for f in features if f in df.columns]

# ── Summer-only model (June-September) ───────────────────────────────────────
print("\nSummer-only model (June-September)...")
summer = df[df['month'].isin([6, 7, 8, 9])]

train = summer[summer['date'].dt.year <= 2019]
val   = summer[(summer['date'].dt.year >= 2020) & (summer['date'].dt.year <= 2022)]
test  = summer[summer['date'].dt.year >= 2023]

def get_xy(split):
    clean = split[features + ['bloom_28d']].dropna(subset=['bloom_28d'])
    return clean[features], clean['bloom_28d']

X_tr, y_tr = get_xy(train)
X_v,  y_v  = get_xy(val)
X_te, y_te = get_xy(test)

print(f"Train: {len(X_tr):,} rows, bloom rate: {y_tr.mean():.1%}")
print(f"Val:   {len(X_v):,} rows,  bloom rate: {y_v.mean():.1%}")
print(f"Test:  {len(X_te):,} rows, bloom rate: {y_te.mean():.1%}")

med = X_tr.median()
scaler = StandardScaler()
X_tr_s = pd.DataFrame(scaler.fit_transform(X_tr.fillna(med)), columns=features)
X_v_s  = pd.DataFrame(scaler.transform(X_v.fillna(med)),      columns=features)
X_te_s = pd.DataFrame(scaler.transform(X_te.fillna(med)),     columns=features)

lr = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
lr.fit(X_tr_s, y_tr)

pos_weight = (y_tr == 0).sum() / (y_tr == 1).sum()
xgb_model = xgb.XGBClassifier(
    colsample_bytree=0.7, learning_rate=0.03, max_depth=3,
    min_child_weight=10, n_estimators=200, subsample=0.7,
    scale_pos_weight=pos_weight, eval_metric='auc',
    random_state=42, verbosity=0
)
xgb_model.fit(X_tr, y_tr, eval_set=[(X_v, y_v)], verbose=False)

lr_val   = lr.predict_proba(X_v_s)[:,1]
xgb_val  = xgb_model.predict_proba(X_v)[:,1]
lr_test  = lr.predict_proba(X_te_s)[:,1]
xgb_test = xgb_model.predict_proba(X_te)[:,1]

ens_val  = 0.8*lr_val  + 0.2*xgb_val
ens_test = 0.8*lr_test + 0.2*xgb_test

print(f"\nSummer model Val AUC:  {roc_auc_score(y_v,  ens_val):.3f}")
print(f"Summer model Test AUC: {roc_auc_score(y_te, ens_test):.3f}")

print("\nClassification report (threshold=0.5):")
print(classification_report(y_te, (ens_test >= 0.5).astype(int),
                             target_names=['no bloom','bloom']))

# Also try stricter bloom definition
print("\n── Stricter bloom definition (CHL > 15 ug/L) ──")
df['bloom_strict'] = 0
for station, grp in df.groupby('station_name'):
    idx = grp.index
    dates = grp['date'].values
    chl = grp['Chlorophyll'].values
    labels = np.zeros(len(grp), dtype=int)
    for i in range(len(grp)):
        mask = ((dates > dates[i]) &
                (dates <= dates[i] + np.timedelta64(28, 'D')))
        if mask.any() and (chl[mask] > 15).any():
            labels[i] = 1
    df.loc[idx, 'bloom_strict'] = labels

summer_strict = df[df['month'].isin([6,7,8,9])]
train_s = summer_strict[summer_strict['date'].dt.year <= 2019]
val_s   = summer_strict[(summer_strict['date'].dt.year >= 2020) &
                         (summer_strict['date'].dt.year <= 2022)]
test_s  = summer_strict[summer_strict['date'].dt.year >= 2023]

def get_xy_strict(split):
    clean = split[features + ['bloom_strict']].dropna(subset=['bloom_strict'])
    return clean[features], clean['bloom_strict']

X_tr2, y_tr2 = get_xy_strict(train_s)
X_v2,  y_v2  = get_xy_strict(val_s)
X_te2, y_te2 = get_xy_strict(test_s)

print(f"Strict bloom rate — train: {y_tr2.mean():.1%}, val: {y_v2.mean():.1%}, test: {y_te2.mean():.1%}")

X_tr2_s = pd.DataFrame(scaler.fit_transform(X_tr2.fillna(X_tr2.median())), columns=features)
X_v2_s  = pd.DataFrame(scaler.transform(X_v2.fillna(X_tr2.median())),      columns=features)
X_te2_s = pd.DataFrame(scaler.transform(X_te2.fillna(X_tr2.median())),     columns=features)

lr2 = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
lr2.fit(X_tr2_s, y_tr2)

pos_weight2 = (y_tr2 == 0).sum() / (y_tr2 == 1).sum()
xgb2 = xgb.XGBClassifier(
    colsample_bytree=0.7, learning_rate=0.03, max_depth=3,
    min_child_weight=10, n_estimators=200, subsample=0.7,
    scale_pos_weight=pos_weight2, eval_metric='auc',
    random_state=42, verbosity=0
)
xgb2.fit(X_tr2, y_tr2, eval_set=[(X_v2, y_v2)], verbose=False)

ens_v2 = 0.8*lr2.predict_proba(X_v2_s)[:,1]  + 0.2*xgb2.predict_proba(X_v2)[:,1]
ens_t2 = 0.8*lr2.predict_proba(X_te2_s)[:,1] + 0.2*xgb2.predict_proba(X_te2)[:,1]

if y_v2.sum() > 0 and y_te2.sum() > 0:
    print(f"Strict Val AUC:  {roc_auc_score(y_v2,  ens_v2):.3f}")
    print(f"Strict Test AUC: {roc_auc_score(y_te2, ens_t2):.3f}")
    print("\nStrict classification report (threshold=0.5):")
    print(classification_report(y_te2, (ens_t2 >= 0.5).astype(int),
                                 target_names=['no bloom','bloom']))