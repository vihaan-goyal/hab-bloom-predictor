import pandas as pd, numpy as np, glob
from io import StringIO
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, precision_recall_curve

hab = pd.read_csv('data/hab_features_tidal.csv')
daily = pd.read_csv('data/hab_features_daily.csv')
hab['date'] = pd.to_datetime(hab['date'])
daily['date'] = pd.to_datetime(daily['date'])

# Merge new features
daily['chl_diff'] = daily['Chlorophyll'] - daily['Corrected_Chlorophyll']
daily['chl_ratio'] = daily['Corrected_Chlorophyll'] / (daily['Chlorophyll'] + 0.01)
for col in ['sal_lag2','sal_lag3','sal_lag4','chl_diff','chl_ratio']:
    if col not in hab.columns:
        hab = hab.merge(daily[['date','station_name',col]], on=['date','station_name'], how='left')

# percent_saturation
pct_frames = []
for fpath in sorted(glob.glob('data/raw/deep_wq_extra/deep_wq_S_*.csv')):
    with open(fpath) as f: lines = f.readlines()
    if len(lines) < 3: continue
    pct_frames.append(pd.read_csv(StringIO(lines[0]+''.join(lines[2:])), low_memory=False))
if pct_frames:
    pct_df = pd.concat(pct_frames, ignore_index=True)
    pct_df['date'] = pd.to_datetime(pct_df['time'], errors='coerce').dt.tz_localize(None).dt.normalize()
    pct_df['percent_saturation'] = pd.to_numeric(pct_df['percent_saturation'], errors='coerce')
    pct_daily = pct_df.groupby(['station_name','date'])['percent_saturation'].mean().reset_index()
    if 'percent_saturation' not in hab.columns:
        hab = hab.merge(pct_daily, on=['station_name','date'], how='left')

for n,mp in [(3,2),(6,3),(9,5),(14,7),(21,10)]:
    hab[f'chl_roll{n}_mean'] = hab.groupby('station_name')['Chlorophyll'].transform(lambda x: x.rolling(n,min_periods=mp).mean())
hab['chl_trend'] = hab.groupby('station_name')['Chlorophyll'].transform(lambda x: x.rolling(4,min_periods=3).apply(lambda v: np.polyfit(range(len(v)),v,1)[0]))
hab['bloom_28d'] = 0
for stn, grp in hab.groupby('station_name'):
    idx=grp.index; dates=grp['date'].values; chl=grp['Chlorophyll'].values
    labels=np.zeros(len(grp),dtype=int)
    for i in range(len(grp)):
        mask=(dates>dates[i])&(dates<=dates[i]+np.timedelta64(28,'D'))
        if mask.any() and (chl[mask]>10).any(): labels[i]=1
    hab.loc[idx,'bloom_28d']=labels

BASE = ['Chlorophyll','chl_lag1','chl_lag2','chl_lag3','chl_lag4','chl_roll3_mean','chl_roll6_mean','chl_roll9_mean','chl_trend','chl_roll14_mean','chl_roll21_mean','chl_anomaly','chl_climatology','do_lag1','temp_lag1','sal_lag1','sal_lag2','sal_lag3','sal_lag4','sea_water_temperature','sea_water_salinity','oxygen_concentration_in_sea_water','percent_saturation','month','latitude_x','longitude_x','nox_lag2','dip_lag2','dip_change','dip_x_month','neighbor_chl3_mean','neighbor_chl3_lag1','tidal_gt_anom','tidal_msl_anom']
BASE = [f for f in BASE if f in hab.columns]

train=hab[hab['date'].dt.year<=2019]; val=hab[(hab['date'].dt.year>=2020)&(hab['date'].dt.year<=2022)]; test=hab[hab['date'].dt.year>=2023]

def run(feats, label):
    feats=[f for f in feats if f in hab.columns]
    rows_tr=train[feats+['bloom_28d']].dropna(subset=['bloom_28d'])
    rows_v=val[feats+['bloom_28d']].dropna(subset=['bloom_28d'])
    rows_te=test[feats+['bloom_28d']].dropna(subset=['bloom_28d'])
    MED=rows_tr[feats].median()
    sc=StandardScaler()
    lr=LogisticRegression(C=0.05,class_weight='balanced',max_iter=2000,random_state=42)
    lr.fit(sc.fit_transform(rows_tr[feats].fillna(MED)),rows_tr['bloom_28d'])
    p_v=lr.predict_proba(sc.transform(rows_v[feats].fillna(MED)))[:,1]
    p_te=lr.predict_proba(sc.transform(rows_te[feats].fillna(MED)))[:,1]
    preds=(p_te>=0.60).astype(int)
    y_te=rows_te['bloom_28d']
    print(f'{label}: AUC={roc_auc_score(y_te,p_te):.4f} Prec={precision_score(y_te,preds,zero_division=0):.3f} Rec={recall_score(y_te,preds,zero_division=0):.3f} F1={f1_score(y_te,preds,zero_division=0):.3f} TP={((preds==1)&(y_te==1)).sum()} FP={((preds==1)&(y_te==0)).sum()}')

run(BASE, 'BASE (baseline)')
run(BASE+['chl_diff'], 'BASE+chl_diff')
run(BASE+['chl_ratio'], 'BASE+chl_ratio')
run(BASE+['chl_diff','chl_ratio'], 'BASE+chl_diff+ratio')
