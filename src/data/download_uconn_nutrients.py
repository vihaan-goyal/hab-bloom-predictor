"""
download_uconn_nutrients.py
---------------------------
Downloads full nutrient dataset from UConn ERDDAP, pivots to wide format,
and tests whether NOx/DIP at A4/B3 improves precision over the locked baseline.

Data source: http://merlin.dms.uconn.edu:8080/erddap/tabledap/DEEP_Nutrient
Provided by Todd Fake / James O'Donnell (UConn).

Run from repo root:
    python download_uconn_nutrients.py
"""

import pandas as pd
import numpy as np
import requests
import glob
from io import StringIO
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_auc_score, precision_score, recall_score, f1_score,
)
import warnings
warnings.filterwarnings('ignore')

THRESHOLD = 0.60
RAW_CSV   = 'data/uconn_nutrients_raw.csv'
WIDE_CSV  = 'data/uconn_nutrients_wide.csv'

# ── DOWNLOAD ──────────────────────────────────────────────────────────────────
if not __import__('os').path.exists(RAW_CSV):
    print("Downloading full nutrient dataset from UConn ERDDAP...")
    url = "http://merlin.dms.uconn.edu:8080/erddap/tabledap/DEEP_Nutrient.csv"
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    nuts = pd.read_csv(StringIO(r.text), skiprows=[1])
    nuts.to_csv(RAW_CSV, index=False)
    print(f"Downloaded {len(nuts)} rows -> {RAW_CSV}")
else:
    print(f"Loading existing {RAW_CSV}...")
    nuts = pd.read_csv(RAW_CSV)

print(f"Shape: {nuts.shape}")
print(f"Stations: {sorted(nuts['Station_Name'].dropna().unique())}")
print(f"Parameters: {sorted(nuts['Parameter'].dropna().unique())}")
print(f"Date range: {nuts['Start_Date'].min()} to {nuts['Start_Date'].max()}")

# ── CHECK A4 / B3 COVERAGE ────────────────────────────────────────────────────
print("\n=== Station x Parameter coverage ===")
western = nuts[nuts['Station_Name'].isin(['A4', 'B3', 'C1', '01', '02'])]
print(western.groupby(['Station_Name', 'Parameter']).size().unstack(fill_value=0))

# ── PIVOT TO WIDE FORMAT ──────────────────────────────────────────────────────
if not __import__('os').path.exists(WIDE_CSV):
    print("\nPivoting to wide format (one row per station-date)...")

    # Parse date from Start_Date
    nuts['date'] = pd.to_datetime(nuts['Start_Date'], errors='coerce').dt.normalize()
    nuts['station_name'] = nuts['Station_Name'].str.strip()
    nuts['Result'] = pd.to_numeric(nuts['Result'], errors='coerce')

    # Use surface samples only where possible
    surf = nuts[nuts['Depth_Code'].isin(['S', 'SDUP', 'SUR', 'SURF'])]
    if len(surf) < len(nuts) * 0.1:
        print("  Few surface samples, using all depth codes")
        surf = nuts

    # Pivot: one column per parameter
    wide = surf.pivot_table(
        index=['station_name', 'date'],
        columns='Parameter',
        values='Result',
        aggfunc='mean',
    ).reset_index()
    wide.columns.name = None

    # Rename key columns
    rename = {}
    for col in wide.columns:
        if 'NOX' in col.upper() or col.upper() == 'NOX-LC':
            rename[col] = 'nox_uconn'
        elif col.upper() == 'DIP':
            rename[col] = 'dip_uconn'
        elif 'SIO2' in col.upper():
            rename[col] = 'sio2_uconn'
        elif 'TDN' in col.upper():
            rename[col] = 'tdn_uconn'
    wide = wide.rename(columns=rename)

    wide.to_csv(WIDE_CSV, index=False)
    print(f"Saved {len(wide)} station-date rows -> {WIDE_CSV}")
    print(f"Columns: {wide.columns.tolist()}")
else:
    wide = pd.read_csv(WIDE_CSV)
    print(f"\nLoaded existing {WIDE_CSV}: {wide.shape}")

wide['date'] = pd.to_datetime(wide['date'], utc=True).dt.tz_localize(None)

# Coverage check
print("\n=== UConn nutrient coverage at western stations ===")
for stn in ['A4', 'B3', 'C1']:
    sub = wide[wide['station_name'] == stn]
    for col in ['nox_uconn', 'dip_uconn']:
        if col in wide.columns:
            n = sub[col].notna().sum()
            print(f"  {stn} {col}: {n} readings, {sub['date'].min().year if len(sub) else 'N/A'}-{sub['date'].max().year if len(sub) else 'N/A'}")

# ── LOAD MAIN PIPELINE ────────────────────────────────────────────────────────
print("\nLoading hab_features_tidal.csv...")
df = pd.read_csv("data/hab_features_tidal.csv")
df['date'] = pd.to_datetime(df['date'])
df['station_name'] = df['station_name'].astype(str)
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
    df = df.merge(ps, on=['date', 'station_name'], how='left')

gust = pd.read_csv("data/gust_features_daily.csv", usecols=['date', 'max_gust_3d'])
gust['date'] = pd.to_datetime(gust['date'])
df = df.merge(gust, on='date', how='left')

# Merge UConn nutrients
nut_cols = [c for c in ['nox_uconn', 'dip_uconn', 'sio2_uconn', 'tdn_uconn']
            if c in wide.columns]
df = df.merge(wide[['date', 'station_name'] + nut_cols],
              on=['date', 'station_name'], how='left')

# Forward-fill per station (same-day measurement available ~monthly)
for col in nut_cols:
    df[col + '_ff'] = df.groupby('station_name')[col].transform(lambda x: x.ffill())
    df[col + '_ff_age'] = (
        df['date'] -
        df.groupby('station_name')['date'].transform(
            lambda x: x.where(df[col].notna()).ffill())
    ).dt.days

print("\n=== UConn nutrient coverage after merge ===")
for col in nut_cols:
    null_pct = df[col].isna().mean() * 100
    ff_null  = df[col + '_ff'].isna().mean() * 100
    print(f"  {col}: {null_pct:.1f}% null raw, {ff_null:.1f}% null ffill")

# Recompute features + labels
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

# Correlations
print("\n=== UConn nutrient correlations with bloom_28d ===")
for col in nut_cols + [c + '_ff' for c in nut_cols]:
    if col in df.columns:
        corr = df[col].corr(df['bloom_28d'])
        null = df[col].isna().mean() * 100
        print(f"  {col}: corr={corr:.3f}, {null:.1f}% null")

# ── EVALUATE ──────────────────────────────────────────────────────────────────
BASELINE = [
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

# Use forward-filled versions as new features
NEW = [c + '_ff' for c in nut_cols] + [c + '_ff_age' for c in nut_cols]

train = df[df['date'].dt.year <= 2019]
val   = df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)]
test  = df[df['date'].dt.year >= 2023]

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
        }

    tag = f" [{label}]" if label else ""
    for name, r in results.items():
        print(f"  {name:4s}{tag}: Prec={r['prec']:.3f} Rec={r['rec']:.3f} "
              f"F1={r['f1']:.3f} AUC={r['auc']:.3f}")
    return results

baseline_feats = [f for f in BASELINE if f in df.columns]
extended_feats = baseline_feats + [f for f in NEW if f in df.columns]

print(f"\n{'='*60}")
print(f"BASELINE ({len(baseline_feats)} features)")
print(f"{'='*60}")
base_results = evaluate(baseline_feats, "baseline")

print(f"\n{'='*60}")
print(f"+ UCONN NUTRIENTS ({len(extended_feats)} features, +{len(extended_feats)-len(baseline_feats)} new)")
print(f"{'='*60}")
ext_results = evaluate(extended_feats, "+uconn_nuts")

b = base_results['test']
e = ext_results['test']
print(f"\n{'='*60}")
print("SUMMARY (test 2023-2025, threshold=0.60)")
print(f"{'='*60}")
print(f"  Baseline:        Prec={b['prec']:.3f} Rec={b['rec']:.3f} F1={b['f1']:.3f} AUC={b['auc']:.3f}")
print(f"  + UConn nutrients: Prec={e['prec']:.3f} Rec={e['rec']:.3f} F1={e['f1']:.3f} AUC={e['auc']:.3f}")
print(f"  Delta Prec: {e['prec']-b['prec']:+.3f}")
verdict = 'KEEP' if e['prec'] > b['prec'] + 0.005 else 'REJECT'
print(f"\nVerdict: {verdict}")