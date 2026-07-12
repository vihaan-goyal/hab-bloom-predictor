"""
add_nutrient_ffill.py
---------------------
Tests forward-filled nutrient features on top of the EXACT locked baseline
from final_evaluation_threshold_sweep.py.

New features tested:
  nox_ffill            -- most recent NOX-LC (forward-filled per station)
  dip_ffill            -- most recent DIP (forward-filled per station)
  nox_ffill_age        -- days since last NOX-LC reading
  dip_ffill_age        -- days since last DIP reading
  nox_ffill_x_month    -- nox_ffill * month interaction
  dip_ffill_x_month    -- dip_ffill * month interaction

Run from repo root:
    python add_nutrient_ffill.py
"""

import glob
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_auc_score, precision_score, recall_score, f1_score,
)

THRESHOLD = 0.60

# ── LOAD (exact copy from final_evaluation_threshold_sweep.py) ───────────────
print("Loading data/hab_features_tidal.csv...")
df = pd.read_csv("data/hab_features_tidal.csv")
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values(['station_name', 'date']).reset_index(drop=True)

if 'percent_saturation' not in df.columns:
    print("Merging percent_saturation...")
    frames = []
    for f in sorted(glob.glob('data/raw/deep_wq_extra/deep_wq_S_*.csv')):
        frames.append(pd.read_csv(
            f, skiprows=[1],
            usecols=['station_name', 'time', 'percent_saturation']))
    ps = pd.concat(frames, ignore_index=True)
    ps = ps[ps['station_name'].notna()].copy()
    ps['station_name'] = ps['station_name'].astype(str)
    ps['date'] = (pd.to_datetime(ps['time'], utc=True)
                    .dt.tz_localize(None).dt.normalize())
    ps['percent_saturation'] = pd.to_numeric(ps['percent_saturation'], errors='coerce')
    ps = (ps.dropna(subset=['percent_saturation'])
            .groupby(['date', 'station_name'], as_index=False)
            ['percent_saturation'].mean())
    df['station_name'] = df['station_name'].astype(str)
    df = df.merge(ps, on=['date', 'station_name'], how='left')
    print(f"  percent_saturation coverage: {df['percent_saturation'].notna().mean()*100:.1f}%")

print("Merging max_gust_3d...")
gust = pd.read_csv("data/gust_features_daily.csv", usecols=['date', 'max_gust_3d'])
gust['date'] = pd.to_datetime(gust['date'])
df = df.merge(gust, on='date', how='left')
print(f"  max_gust_3d coverage: {df['max_gust_3d'].notna().mean()*100:.1f}%")

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

# ── LOCKED BASELINE FEATURES ─────────────────────────────────────────────────
BASELINE = [
    'Chlorophyll', 'chl_lag1', 'chl_lag2', 'chl_lag3', 'chl_lag4',
    'chl_roll3_mean', 'chl_roll6_mean', 'chl_roll9_mean',
    'chl_roll14_mean', 'chl_roll21_mean', 'chl_trend',
    'chl_anomaly', 'chl_climatology',
    'do_lag1', 'temp_lag1', 'sal_lag1',
    'sal_lag2', 'sal_lag3', 'sal_lag4',
    'sea_water_temperature', 'sea_water_salinity',
    'oxygen_concentration_in_sea_water',
    'month', 'latitude_x', 'longitude_x',
    'nox_lag2', 'dip_lag2', 'dip_change', 'dip_x_month',
    'neighbor_chl3_mean', 'neighbor_chl3_lag1',
    'tidal_gt_anom', 'tidal_msl_anom',
    'percent_saturation',
    'max_gust_3d',
]

# ── BUILD FORWARD-FILL FEATURES ───────────────────────────────────────────────
print("\nBuilding forward-fill nutrient features...")

def add_ffill_feature(df, raw_col, out_col, age_col):
    df[out_col] = df.groupby('station_name')[raw_col].transform(lambda x: x.ffill())
    last_date_col = '_last_' + raw_col
    df[last_date_col] = df['date'].where(df[raw_col].notna())
    df[last_date_col] = df.groupby('station_name')[last_date_col].transform(lambda x: x.ffill())
    df[age_col] = (df['date'] - df[last_date_col]).dt.days
    df = df.drop(columns=[last_date_col])
    return df

df = add_ffill_feature(df, 'NOX-LC', 'nox_ffill', 'nox_ffill_age')
df = add_ffill_feature(df, 'DIP',    'dip_ffill', 'dip_ffill_age')
df['nox_ffill_x_month'] = df['nox_ffill'] * df['month']
df['dip_ffill_x_month'] = df['dip_ffill'] * df['month']

NEW_FEATURES = ['nox_ffill', 'dip_ffill', 'nox_ffill_age', 'dip_ffill_age',
                'nox_ffill_x_month', 'dip_ffill_x_month']

print("\n=== New feature stats ===")
for col in NEW_FEATURES:
    null_pct = df[col].isna().mean() * 100
    corr = df[col].corr(df['bloom_28d'])
    print(f"  {col}: {null_pct:.1f}% null, corr={corr:.3f}")

# ── SPLITS ────────────────────────────────────────────────────────────────────
train = df[df['date'].dt.year <= 2019]
val   = df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)]
test  = df[df['date'].dt.year >= 2023]

print(f"\nSplit sizes: train={len(train)}, val={len(val)}, test={len(test)}")
print(f"Bloom rates: train={train['bloom_28d'].mean():.3f}, "
      f"val={val['bloom_28d'].mean():.3f}, test={test['bloom_28d'].mean():.3f}")

# ── EVALUATE FUNCTION (matches locked pipeline exactly) ───────────────────────
def evaluate(features, label=""):
    feats = [f for f in features if f in df.columns]

    def prep(split):
        rows = split[feats + ['bloom_28d']].dropna(subset=['bloom_28d'])
        X = rows[feats].copy().reset_index(drop=True)
        y = rows['bloom_28d'].copy().reset_index(drop=True)
        return X, y

    X_tr, y_tr = prep(train)
    X_v,  y_v  = prep(val)
    X_te, y_te = prep(test)

    MED = X_tr.median()

    scaler = StandardScaler()
    X_tr_s = scaler.fit_transform(X_tr.fillna(MED))
    X_v_s  = scaler.transform(X_v.fillna(MED))
    X_te_s = scaler.transform(X_te.fillna(MED))

    model = LogisticRegression(C=0.05, class_weight='balanced',
                               max_iter=1000, random_state=42)
    model.fit(X_tr_s, y_tr)

    results = {}
    for name, X_s, y in [('val', X_v_s, y_v), ('test', X_te_s, y_te)]:
        probs = model.predict_proba(X_s)[:, 1]
        preds = (probs >= THRESHOLD).astype(int)
        results[name] = {
            'prec': precision_score(y, preds, zero_division=0),
            'rec':  recall_score(y, preds, zero_division=0),
            'f1':   f1_score(y, preds, zero_division=0),
            'auc':  roc_auc_score(y, probs),
            'n':    len(y),
        }

    tag = f" [{label}]" if label else ""
    for name, r in results.items():
        print(f"  {name:4s}{tag}: Prec={r['prec']:.3f} Rec={r['rec']:.3f} "
              f"F1={r['f1']:.3f} AUC={r['auc']:.3f}  (n={r['n']})")
    return results

# ── RUN ───────────────────────────────────────────────────────────────────────
baseline_feats = [f for f in BASELINE if f in df.columns]
missing = [f for f in BASELINE if f not in df.columns]
if missing:
    print(f"\nBaseline features missing from df (skipped): {missing}")

print(f"\n{'='*60}")
print(f"BASELINE ({len(baseline_feats)} features)")
print(f"{'='*60}")
base_results = evaluate(baseline_feats, "baseline")

extended_feats = baseline_feats + [f for f in NEW_FEATURES if f in df.columns]
print(f"\n{'='*60}")
print(f"+ NUTRIENT FFILL ({len(extended_feats)} features, +{len(extended_feats)-len(baseline_feats)} new)")
print(f"{'='*60}")
ext_results = evaluate(extended_feats, "+ffill")

# ── SUMMARY ───────────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("SUMMARY (test set 2023-2025, threshold=0.60)")
print(f"{'='*60}")
b = base_results['test']
e = ext_results['test']
print(f"  Baseline:         Prec={b['prec']:.3f} Rec={b['rec']:.3f} F1={b['f1']:.3f} AUC={b['auc']:.3f}")
print(f"  + Nutrient ffill: Prec={e['prec']:.3f} Rec={e['rec']:.3f} F1={e['f1']:.3f} AUC={e['auc']:.3f}")
print(f"  Delta Prec: {e['prec']-b['prec']:+.3f}")
print(f"  Delta F1:   {e['f1']-b['f1']:+.3f}")
verdict = 'KEEP -- precision improved' if e['prec'] > b['prec'] + 0.005 else 'REJECT -- no meaningful gain'
print(f"\nVerdict: {verdict}")