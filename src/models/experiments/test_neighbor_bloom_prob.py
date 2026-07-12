"""
test_neighbor_bloom_prob.py
---------------------------
Tests neighbor station bloom probability as a feature.
Run from repo root: python test_neighbor_bloom_prob.py
"""

import glob
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score

THRESHOLD = 0.60

print("Loading data...")
df = pd.read_csv("data/hab_features_tidal.csv")
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values(['station_name', 'date']).reset_index(drop=True)

if 'percent_saturation' not in df.columns:
    frames = []
    for f in sorted(glob.glob('data/raw/deep_wq_extra/deep_wq_S_*.csv')):
        frames.append(pd.read_csv(f, skiprows=[1],
                      usecols=['station_name', 'time', 'percent_saturation']))
    ps = pd.concat(frames, ignore_index=True)
    ps['station_name'] = ps['station_name'].astype(str)
    ps['date'] = pd.to_datetime(ps['time'], utc=True).dt.tz_localize(None).dt.normalize()
    ps['percent_saturation'] = pd.to_numeric(ps['percent_saturation'], errors='coerce')
    ps = ps.dropna(subset=['percent_saturation']).groupby(
        ['date', 'station_name'], as_index=False)['percent_saturation'].mean()
    df['station_name'] = df['station_name'].astype(str)
    df = df.merge(ps, on=['date', 'station_name'], how='left')

gust = pd.read_csv("data/gust_features_daily.csv", usecols=['date', 'max_gust_3d'])
gust['date'] = pd.to_datetime(gust['date'])
df = df.merge(gust, on='date', how='left')

for n, min_p in [(3, 2), (6, 3), (9, 5), (14, 7), (21, 10)]:
    df[f'chl_roll{n}_mean'] = (
        df.groupby('station_name')['Chlorophyll']
          .transform(lambda x: x.rolling(n, min_periods=min_p).mean())
    )
df['chl_trend'] = (
    df.groupby('station_name')['Chlorophyll']
      .transform(lambda x: x.rolling(4, min_periods=3)
                 .apply(lambda v: np.polyfit(range(len(v)), v, 1)[0]))
)

print("Computing bloom_28d labels...")
df['bloom_28d'] = 0
for station, grp in df.groupby('station_name'):
    idx   = grp.index
    dates = grp['date'].values
    chl   = grp['Chlorophyll'].values
    labels = np.zeros(len(grp), dtype=int)
    for i in range(len(grp)):
        mask = (dates > dates[i]) & (dates <= dates[i] + np.timedelta64(28, 'D'))
        if mask.any() and (chl[mask] > 10).any():
            labels[i] = 1
    df.loc[idx, 'bloom_28d'] = labels

FEATURES = [
    'Chlorophyll', 'chl_lag1', 'chl_lag2', 'chl_lag3', 'chl_lag4',
    'chl_roll3_mean', 'chl_roll6_mean', 'chl_roll9_mean',
    'chl_roll14_mean', 'chl_roll21_mean', 'chl_trend',
    'chl_anomaly', 'chl_climatology',
    'do_lag1', 'temp_lag1', 'sal_lag1', 'sal_lag2', 'sal_lag3', 'sal_lag4',
    'sea_water_temperature', 'sea_water_salinity',
    'oxygen_concentration_in_sea_water',
    'month', 'latitude_x', 'longitude_x',
    'nox_lag2', 'dip_lag2', 'dip_change', 'dip_x_month',
    'neighbor_chl3_mean', 'neighbor_chl3_lag1',
    'tidal_gt_anom', 'tidal_msl_anom',
    'percent_saturation', 'max_gust_3d',
]
FEATURES = [f for f in FEATURES if f in df.columns]

# ── FIT BASE MODEL ON TRAIN, GENERATE PROBS FOR ALL ROWS ─────────────────────
print("Fitting base LR and generating bloom probabilities...")
train_mask = df['date'].dt.year <= 2019

def prep_rows(mask):
    sub = df[mask][FEATURES + ['bloom_28d']].dropna(subset=['bloom_28d'])
    X = sub[FEATURES].copy().reset_index(drop=True)
    y = sub['bloom_28d'].copy().reset_index(drop=True)
    return X, y

X_tr, y_tr = prep_rows(train_mask)
MED = X_tr.median()

scaler = StandardScaler()
X_tr_s = scaler.fit_transform(X_tr.fillna(MED))

base_lr = LogisticRegression(C=0.05, class_weight='balanced',
                             max_iter=1000, random_state=42)
base_lr.fit(X_tr_s, y_tr)

X_all_s = scaler.transform(df[FEATURES].fillna(MED))
df['bloom_prob'] = base_lr.predict_proba(X_all_s)[:, 1]

# ── BUILD NEIGHBOR BLOOM PROB ─────────────────────────────────────────────────
print("Building neighbor bloom probability features...")
coords = df[['station_name', 'latitude_x', 'longitude_x']].drop_duplicates('station_name').dropna()
locs = coords[['latitude_x', 'longitude_x']].values
dists = cdist(locs, locs)
station_names = coords['station_name'].values

neighbor_map = {}
for i, stn in enumerate(station_names):
    sorted_idx = np.argsort(dists[i])
    neighbor_map[stn] = station_names[sorted_idx[1:4]].tolist()

print("\nNeighbor map (western stations):")
for stn in ['A4', 'B3', 'C1', '01', '02']:
    if stn in neighbor_map:
        print(f"  {stn}: {neighbor_map[stn]}")

prob_pivot = df.pivot_table(index='date', columns='station_name',
                             values='bloom_prob', aggfunc='mean')

nbp = []
for _, row in df.iterrows():
    stn  = row['station_name']
    date = row['date']
    neighbors = neighbor_map.get(stn, [])
    if date in prob_pivot.index and neighbors:
        vals = [prob_pivot.loc[date, n] for n in neighbors
                if n in prob_pivot.columns and not pd.isna(prob_pivot.loc[date, n])]
        nbp.append(np.mean(vals) if vals else np.nan)
    else:
        nbp.append(np.nan)

df['neighbor_bloom_prob'] = nbp

null_pct = df['neighbor_bloom_prob'].isna().mean() * 100
corr = df['neighbor_bloom_prob'].corr(df['bloom_28d'])
print(f"\nneighbor_bloom_prob: {null_pct:.1f}% null, corr={corr:.3f}")

# ── NOW CREATE SPLITS (after all features added) ──────────────────────────────
train_df = df[df['date'].dt.year <= 2019]
val_df   = df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)]
test_df  = df[df['date'].dt.year >= 2023]

def evaluate(features, label=""):
    feats = [f for f in features if f in df.columns]
    def prep(split):
        rows = split[feats + ['bloom_28d']].dropna(subset=['bloom_28d'])
        X = rows[feats].copy().reset_index(drop=True)
        y = rows['bloom_28d'].copy().reset_index(drop=True)
        return X, y
    X_tr2, y_tr2 = prep(train_df)
    X_v2,  y_v2  = prep(val_df)
    X_te2, y_te2 = prep(test_df)
    MED2 = X_tr2.median()
    sc2 = StandardScaler()
    X_tr2_s = sc2.fit_transform(X_tr2.fillna(MED2))
    X_v2_s  = sc2.transform(X_v2.fillna(MED2))
    X_te2_s = sc2.transform(X_te2.fillna(MED2))
    m = LogisticRegression(C=0.05, class_weight='balanced',
                           max_iter=1000, random_state=42)
    m.fit(X_tr2_s, y_tr2)
    results = {}
    for name, X_s, y in [('val', X_v2_s, y_v2), ('test', X_te2_s, y_te2)]:
        probs = m.predict_proba(X_s)[:, 1]
        preds = (probs >= THRESHOLD).astype(int)
        results[name] = {
            'prec': precision_score(y, preds, zero_division=0),
            'rec':  recall_score(y, preds, zero_division=0),
            'f1':   f1_score(y, preds, zero_division=0),
            'auc':  roc_auc_score(y, probs),
        }
    tag = f" [{label}]" if label else ""
    for name, r in results.items():
        print(f"  {name:4s}{tag}: Prec={r['prec']:.3f} Rec={r['rec']:.3f} "
              f"F1={r['f1']:.3f} AUC={r['auc']:.3f}")
    return results

baseline_feats = FEATURES[:]
extended_feats = baseline_feats + ['neighbor_bloom_prob']

print(f"\n{'='*60}")
print("BASELINE")
print(f"{'='*60}")
base_results = evaluate(baseline_feats, "baseline")

print(f"\n{'='*60}")
print("+ NEIGHBOR BLOOM PROB")
print(f"{'='*60}")
ext_results = evaluate(extended_feats, "+nbp")

b = base_results['test']
e = ext_results['test']
print(f"\n{'='*60}")
print("SUMMARY (test 2023-2025, threshold=0.60)")
print(f"{'='*60}")
print(f"  Baseline:  Prec={b['prec']:.3f} Rec={b['rec']:.3f} F1={b['f1']:.3f} AUC={b['auc']:.3f}")
print(f"  + NBP:     Prec={e['prec']:.3f} Rec={e['rec']:.3f} F1={e['f1']:.3f} AUC={e['auc']:.3f}")
print(f"  Delta Prec: {e['prec']-b['prec']:+.3f}")
verdict = 'KEEP' if e['prec'] > b['prec'] + 0.005 else 'REJECT'
print(f"\nVerdict: {verdict}")