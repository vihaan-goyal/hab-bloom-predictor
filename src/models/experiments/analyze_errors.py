"""
analyze_errors.py
-----------------
Analyzes false positives and false negatives in the test set to
understand what the model is getting wrong and why.

Run from repo root:
    python src/models/analyze_errors.py
"""

import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import glob
from io import StringIO
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
hab = pd.read_csv('data/hab_features_tidal.csv')
daily = pd.read_csv('data/hab_features_daily.csv')
hab['date'] = pd.to_datetime(hab['date'])
daily['date'] = pd.to_datetime(daily['date'])

for col in ['sal_lag2', 'sal_lag3', 'sal_lag4']:
    if col not in hab.columns:
        hab = hab.merge(daily[['date', 'station_name', col]],
                        on=['date', 'station_name'], how='left')

pct_frames = []
for fpath in sorted(glob.glob('data/raw/deep_wq_extra/deep_wq_S_*.csv')):
    with open(fpath) as f:
        lines = f.readlines()
    if len(lines) < 3:
        continue
    df_yr = pd.read_csv(StringIO(lines[0] + ''.join(lines[2:])), low_memory=False)
    pct_frames.append(df_yr)

if pct_frames:
    pct_df = pd.concat(pct_frames, ignore_index=True)
    pct_df['date'] = (pd.to_datetime(pct_df['time'], errors='coerce')
                        .dt.tz_localize(None).dt.normalize())
    pct_df['percent_saturation'] = pd.to_numeric(
        pct_df['percent_saturation'], errors='coerce')
    pct_daily = (pct_df.groupby(['station_name', 'date'])['percent_saturation']
                        .mean().reset_index())
    if 'percent_saturation' not in hab.columns:
        hab = hab.merge(pct_daily, on=['station_name', 'date'], how='left')

# Recompute features
for n, min_p in [(3,2),(6,3),(9,5),(14,7),(21,10)]:
    hab[f'chl_roll{n}_mean'] = (
        hab.groupby('station_name')['Chlorophyll']
           .transform(lambda x: x.rolling(n, min_periods=min_p).mean()))

hab['chl_trend'] = (
    hab.groupby('station_name')['Chlorophyll']
       .transform(lambda x: x.rolling(4, min_periods=3)
                  .apply(lambda v: np.polyfit(range(len(v)), v, 1)[0])))

hab['bloom_28d'] = 0
for station, grp in hab.groupby('station_name'):
    idx = grp.index
    dates = grp['date'].values
    chl = grp['Chlorophyll'].values
    labels = np.zeros(len(grp), dtype=int)
    for i in range(len(grp)):
        mask = ((dates > dates[i]) &
                (dates <= dates[i] + np.timedelta64(28, 'D')))
        if mask.any() and (chl[mask] > 10).any():
            labels[i] = 1
    hab.loc[idx, 'bloom_28d'] = labels

FEATURES = [
    'Chlorophyll', 'chl_lag1', 'chl_lag2', 'chl_lag3', 'chl_lag4',
    'chl_roll3_mean', 'chl_roll6_mean', 'chl_roll9_mean', 'chl_trend',
    'chl_roll14_mean', 'chl_roll21_mean',
    'chl_anomaly', 'chl_climatology',
    'do_lag1', 'temp_lag1', 'sal_lag1', 'sal_lag2', 'sal_lag3', 'sal_lag4',
    'sea_water_temperature', 'sea_water_salinity',
    'oxygen_concentration_in_sea_water', 'percent_saturation',
    'month', 'latitude_x', 'longitude_x',
    'nox_lag2', 'dip_lag2', 'dip_change', 'dip_x_month',
    'neighbor_chl3_mean', 'neighbor_chl3_lag1',
    'tidal_gt_anom', 'tidal_msl_anom',
]
FEATURES = [f for f in FEATURES if f in hab.columns]

# ---------------------------------------------------------------------------
# Train and predict
# ---------------------------------------------------------------------------
train = hab[hab['date'].dt.year <= 2019]
test  = hab[hab['date'].dt.year >= 2023]

rows_tr = train[FEATURES + ['bloom_28d']].dropna(subset=['bloom_28d'])
rows_te = test.copy().dropna(subset=['bloom_28d'])

MED = rows_tr[FEATURES].median()
sc  = StandardScaler()
lr  = LogisticRegression(C=0.05, class_weight='balanced',
                          max_iter=2000, random_state=42)
lr.fit(sc.fit_transform(rows_tr[FEATURES].fillna(MED)), rows_tr['bloom_28d'])

rows_te['prob'] = lr.predict_proba(
    sc.transform(rows_te[FEATURES].fillna(MED)))[:, 1]
rows_te['pred'] = (rows_te['prob'] >= 0.60).astype(int)

fp = rows_te[(rows_te['pred']==1) & (rows_te['bloom_28d']==0)].copy()
fn = rows_te[(rows_te['pred']==0) & (rows_te['bloom_28d']==1)].copy()
tp = rows_te[(rows_te['pred']==1) & (rows_te['bloom_28d']==1)].copy()

print(f"Test set: TP={len(tp)}  FP={len(fp)}  FN={len(fn)}")

# ---------------------------------------------------------------------------
# False Positive Analysis
# ---------------------------------------------------------------------------
print("\n" + "="*55)
print("FALSE POSITIVE ANALYSIS (alerts that weren't real blooms)")
print("="*55)

print("\nFP by month:")
print(fp['month'].value_counts().sort_index().to_string())

print("\nFP by station (top 10):")
print(fp['station_name'].value_counts().head(10).to_string())

print("\nFP by year:")
print(fp['date'].dt.year.value_counts().sort_index().to_string())

print(f"\nFP mean CHL:          {fp['Chlorophyll'].mean():.2f} µg/L")
print(f"FP mean bloom prob:   {fp['prob'].mean():.3f}")
print(f"FP mean DO:           {fp['oxygen_concentration_in_sea_water'].mean():.2f} mg/L")
print(f"FP mean temp:         {fp['sea_water_temperature'].mean():.2f} °C")
print(f"FP mean chl_roll9:    {fp['chl_roll9_mean'].mean():.2f} µg/L")
print(f"FP mean chl_roll21:   {fp['chl_roll21_mean'].mean():.2f} µg/L")

# ---------------------------------------------------------------------------
# False Negative Analysis
# ---------------------------------------------------------------------------
print("\n" + "="*55)
print("FALSE NEGATIVE ANALYSIS (blooms we missed)")
print("="*55)

print("\nFN by month:")
print(fn['month'].value_counts().sort_index().to_string())

print("\nFN by station (top 10):")
print(fn['station_name'].value_counts().head(10).to_string())

print("\nFN by year:")
print(fn['date'].dt.year.value_counts().sort_index().to_string())

print(f"\nFN mean CHL:          {fn['Chlorophyll'].mean():.2f} µg/L")
print(f"FN mean bloom prob:   {fn['prob'].mean():.3f}")
print(f"FN mean DO:           {fn['oxygen_concentration_in_sea_water'].mean():.2f} mg/L")
print(f"FN mean temp:         {fn['sea_water_temperature'].mean():.2f} °C")
print(f"FN mean chl_roll9:    {fn['chl_roll9_mean'].mean():.2f} µg/L")
print(f"FN mean chl_roll21:   {fn['chl_roll21_mean'].mean():.2f} µg/L")

# ---------------------------------------------------------------------------
# TP vs FP comparison -- what separates correct alerts from false alarms
# ---------------------------------------------------------------------------
print("\n" + "="*55)
print("TP vs FP COMPARISON (what separates real from false alerts)")
print("="*55)
print(f"{'Feature':<25}  {'TP mean':>10}  {'FP mean':>10}  {'Diff':>8}")
print("-"*55)

compare_feats = [
    'Chlorophyll', 'chl_roll9_mean', 'chl_roll21_mean',
    'oxygen_concentration_in_sea_water', 'sea_water_temperature',
    'sea_water_salinity', 'prob',
]
for f in compare_feats:
    if f in tp.columns and f in fp.columns:
        tp_mean = tp[f].mean()
        fp_mean = fp[f].mean()
        diff = tp_mean - fp_mean
        print(f"{f:<25}  {tp_mean:>10.3f}  {fp_mean:>10.3f}  {diff:>+8.3f}")

# ---------------------------------------------------------------------------
# Key question: what do FPs have that TPs don't
# ---------------------------------------------------------------------------
print("\n" + "="*55)
print("KEY INSIGHT")
print("="*55)
print("FPs are cases where model said 'bloom' but no bloom occurred.")
print("If FP CHL >> TP CHL, model is confused by high-CHL non-bloom conditions.")
print("If FP DO < TP DO, model is fooled by hypoxia without subsequent bloom.")
print("If FP month clusters in specific months, temporal confound exists.")