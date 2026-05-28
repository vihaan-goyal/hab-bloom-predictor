import pandas as pd, numpy as np
from sklearn.metrics import precision_recall_curve, roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import xgboost as xgb

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

train = df[df['date'].dt.year <= 2019]
val   = df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)]
test  = df[df['date'].dt.year >= 2023]

def get_xy(split):
    clean = split[features + ['bloom_28d']].dropna(subset=['bloom_28d'])
    return clean[features], clean['bloom_28d']

X_tr, y_tr = get_xy(train)
X_v,  y_v  = get_xy(val)
X_te, y_te = get_xy(test)

# Train LR + XGB ensemble (best combo: LR 80% XGB 20%)
med = X_tr.median()
scaler = StandardScaler()
X_tr_s = pd.DataFrame(scaler.fit_transform(X_tr.fillna(med)), columns=features)
X_v_s  = pd.DataFrame(scaler.transform(X_v.fillna(med)),  columns=features)
X_te_s = pd.DataFrame(scaler.transform(X_te.fillna(med)), columns=features)

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

# Find optimal threshold on val set
precision, recall, thresholds = precision_recall_curve(y_v, ens_val)
f1 = 2*precision*recall / (precision + recall + 1e-9)
f2 = 5*precision*recall / (4*precision + recall + 1e-9)  # F2 weights recall more

print("Threshold sweep on val set:")
print(f"{'Threshold':>10} {'Precision':>10} {'Recall':>8} {'F1':>8} {'F2':>8}")
for t in [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]:
    idx = np.searchsorted(thresholds, t)
    if idx < len(precision):
        p, r = precision[idx], recall[idx]
        f1s = 2*p*r/(p+r+1e-9)
        f2s = 5*p*r/(4*p+r+1e-9)
        print(f"  {t:>8.2f}   {p:>9.2f}  {r:>8.2f}  {f1s:>8.2f}  {f2s:>8.2f}")

best_f1_idx = np.argmax(f1)
best_f2_idx = np.argmax(f2)
best_t_f1 = thresholds[best_f1_idx]
best_t_f2 = thresholds[best_f2_idx]
print(f"\nBest F1 threshold: {best_t_f1:.3f} "
      f"(precision={precision[best_f1_idx]:.2f}, recall={recall[best_f1_idx]:.2f})")
print(f"Best F2 threshold: {best_t_f2:.3f} "
      f"(precision={precision[best_f2_idx]:.2f}, recall={recall[best_f2_idx]:.2f})")

# Evaluate on test at both thresholds
from sklearn.metrics import classification_report, roc_auc_score
print(f"\nTest AUC: {roc_auc_score(y_te, ens_test):.3f}")
for label, t in [("Best F1 threshold", best_t_f1),
                  ("Best F2 threshold", best_t_f2),
                  ("Default 0.5",       0.50)]:
    preds = (ens_test >= t).astype(int)
    print(f"\n{label} (t={t:.3f}):")
    print(classification_report(y_te, preds, target_names=['no bloom','bloom']))