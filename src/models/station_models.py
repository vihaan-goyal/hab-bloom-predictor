import pandas as pd
import numpy as np
from sklearn.metrics import precision_score, recall_score, roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

df = pd.read_csv("data/hab_features_daily.csv")
df['date'] = pd.to_datetime(df['date'])

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
    'Chlorophyll','chl_lag1','chl_lag2','chl_roll3_mean',
    'chl_roll6_mean','chl_anomaly','chl_climatology',
    'sea_water_temperature','month','neighbor_chl3_mean',
]
features = [f for f in features if f in df.columns]

# Check bloom rate and test precision per high-bloom station
high_bloom_stations = ['A2','A4','B3','C1','C2','D3']

print(f"{'Station':>10} {'Train_bloom%':>13} {'Test_bloom%':>12} {'Test_AUC':>10} {'Precision':>10} {'Recall':>8}")
for s in high_bloom_stations:
    sub = df[df['station_name'] == s].copy()
    train = sub[sub['date'].dt.year <= 2019]
    test  = sub[sub['date'].dt.year >= 2023]

    def get_xy(split):
        clean = split[features + ['bloom_28d']].dropna(subset=['bloom_28d'])
        return clean[features], clean['bloom_28d']

    X_tr, y_tr = get_xy(train)
    X_te, y_te = get_xy(test)

    if len(y_tr) < 20 or y_tr.sum() < 3 or y_te.sum() < 2:
        print(f"  {s:>8}: insufficient data")
        continue

    med = X_tr.median()
    scaler = StandardScaler()
    X_tr_s = pd.DataFrame(scaler.fit_transform(X_tr.fillna(med)), columns=features)
    X_te_s = pd.DataFrame(scaler.transform(X_te.fillna(med)), columns=features)

    lr = LogisticRegression(class_weight='balanced', max_iter=500, random_state=42)
    lr.fit(X_tr_s, y_tr)
    probs = lr.predict_proba(X_te_s)[:,1]
    preds = (probs >= 0.5).astype(int)

    try:
        auc = roc_auc_score(y_te, probs)
        p   = precision_score(y_te, preds, zero_division=0)
        r   = recall_score(y_te, preds, zero_division=0)
        print(f"  {s:>8}:   {y_tr.mean():>10.1%}   {y_te.mean():>10.1%}   {auc:>8.3f}   {p:>9.2f}   {r:>7.2f}")
    except Exception as e:
        print(f"  {s:>8}: {e}")