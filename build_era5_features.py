"""
build_era5_features.py
----------------------
Processes data/era5_wind_lis.nc into daily wind stress curl features
and tests them against the locked baseline.

Features computed:
  wind_stress_u     -- zonal wind stress (tau_x = rho_air * Cd * u * |U|)
  wind_stress_v     -- meridional wind stress
  wind_stress_mag   -- wind stress magnitude
  wind_stress_curl  -- d(tau_y)/dx - d(tau_x)/dy (upwelling driver)
  wsc_roll3d        -- 3-day rolling mean of wind stress curl
  wsc_roll7d        -- 7-day rolling mean of wind stress curl

Run from repo root (after download_era5_wind.py completes):
    python build_era5_features.py
"""

import glob
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import xarray as xr
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_auc_score, precision_score, recall_score, f1_score,
)

THRESHOLD = 0.60
ERA5_PATH = 'data/era5_wind_lis.nc'
OUTPUT_CSV = 'data/era5_wind_features_daily.csv'

# ── PROCESS ERA5 -> DAILY FEATURES ───────────────────────────────────────────
print(f"Loading {ERA5_PATH}...")
ds = xr.open_dataset(ERA5_PATH)
print(ds)

# Wind stress calculation
# tau = rho_air * Cd * U * |U|  where Cd=1.3e-3, rho_air=1.225 kg/m3
RHO_AIR = 1.225
CD = 1.3e-3

u10 = ds['u10'].values  # shape: (time, lat, lon)
v10 = ds['v10'].values
wspd = np.sqrt(u10**2 + v10**2)

tau_x = RHO_AIR * CD * u10 * wspd
tau_y = RHO_AIR * CD * v10 * wspd

# Wind stress curl: d(tau_y)/dx - d(tau_x)/dy
# Use finite differences over the spatial grid
lats = ds['latitude'].values
lons = ds['longitude'].values
dlat = np.abs(np.mean(np.diff(lats))) * (np.pi / 180) * 6371000  # meters
dlon = np.abs(np.mean(np.diff(lons))) * (np.pi / 180) * 6371000 * np.cos(np.mean(lats) * np.pi / 180)

if tau_y.shape[-1] > 1 and tau_x.shape[-2] > 1:
    dtauy_dx = np.gradient(tau_y, dlon, axis=2)
    dtaux_dy = np.gradient(tau_x, dlat, axis=1)
    curl = dtauy_dx - dtaux_dy
else:
    # Single grid cell -- curl undefined, use stress magnitude only
    print("  Single grid cell -- skipping curl, using stress magnitude only")
    curl = np.zeros_like(tau_x)

# Average over the LIS domain
tau_mag_mean  = np.sqrt(tau_x**2 + tau_y**2).mean(axis=(1, 2))
curl_mean     = curl.mean(axis=(1, 2))

# Build daily dataframe (ERA5 is 6-hourly -- resample to daily mean)
times = pd.to_datetime(ds['valid_time'].values if 'valid_time' in ds else ds['time'].values)
era5_df = pd.DataFrame({
    'datetime':       times,
    'wind_stress_mag': tau_mag_mean,
    'wind_stress_curl': curl_mean,
})
era5_df['date'] = era5_df['datetime'].dt.normalize()
daily = era5_df.groupby('date')[['wind_stress_mag', 'wind_stress_curl']].mean().reset_index()

# Rolling features
daily = daily.sort_values('date').reset_index(drop=True)
daily['wsc_roll3d'] = daily['wind_stress_curl'].rolling(3, min_periods=2).mean()
daily['wsc_roll7d'] = daily['wind_stress_curl'].rolling(7, min_periods=4).mean()
daily['wsm_roll3d'] = daily['wind_stress_mag'].rolling(3, min_periods=2).mean()
daily['wsm_roll7d'] = daily['wind_stress_mag'].rolling(7, min_periods=4).mean()

daily.to_csv(OUTPUT_CSV, index=False)
print(f"\nSaved {len(daily)} daily rows to {OUTPUT_CSV}")
print(f"Date range: {daily['date'].min()} to {daily['date'].max()}")
print(f"\nFeature stats:")
for col in ['wind_stress_mag', 'wind_stress_curl', 'wsc_roll3d', 'wsc_roll7d']:
    print(f"  {col}: mean={daily[col].mean():.4f}, std={daily[col].std():.4f}")

# ── LOAD MAIN PIPELINE ────────────────────────────────────────────────────────
print("\nLoading hab_features_tidal.csv and merging ERA5 features...")
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

# Merge ERA5
df = df.merge(daily[['date', 'wind_stress_mag', 'wind_stress_curl',
                      'wsc_roll3d', 'wsc_roll7d', 'wsm_roll3d', 'wsm_roll7d']],
              on='date', how='left')

era5_cols = ['wind_stress_mag', 'wind_stress_curl', 'wsc_roll3d', 'wsc_roll7d']
print("\n=== ERA5 feature coverage and correlation ===")
for col in era5_cols:
    null_pct = df[col].isna().mean() * 100
    corr = df[col].corr(df['bloom_28d']) if 'bloom_28d' in df.columns else float('nan')
    print(f"  {col}: {null_pct:.1f}% null, corr={corr:.3f}")

# Recompute rolls and bloom label
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

# Print correlations now that bloom_28d is computed
print("\n=== ERA5 feature correlations with bloom_28d ===")
for col in era5_cols + ['wsm_roll3d', 'wsm_roll7d']:
    if col in df.columns:
        corr = df[col].corr(df['bloom_28d'])
        print(f"  {col}: corr={corr:.3f}")

# ── FEATURE SETS ──────────────────────────────────────────────────────────────
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
ERA5_FEATURES = ['wind_stress_curl', 'wsc_roll3d', 'wsc_roll7d',
                 'wind_stress_mag', 'wsm_roll3d', 'wsm_roll7d']

# ── SPLITS ────────────────────────────────────────────────────────────────────
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
extended_feats = baseline_feats + [f for f in ERA5_FEATURES if f in df.columns]

print(f"\n{'='*60}")
print(f"BASELINE ({len(baseline_feats)} features)")
print(f"{'='*60}")
base_results = evaluate(baseline_feats, "baseline")

print(f"\n{'='*60}")
print(f"+ ERA5 WIND STRESS ({len(extended_feats)} features, +{len(extended_feats)-len(baseline_feats)} new)")
print(f"{'='*60}")
era5_results = evaluate(extended_feats, "+era5")

b = base_results['test']
e = era5_results['test']
print(f"\n{'='*60}")
print("SUMMARY (test 2023-2025, threshold=0.60)")
print(f"{'='*60}")
print(f"  Baseline:    Prec={b['prec']:.3f} Rec={b['rec']:.3f} F1={b['f1']:.3f} AUC={b['auc']:.3f}")
print(f"  + ERA5 wind: Prec={e['prec']:.3f} Rec={e['rec']:.3f} F1={e['f1']:.3f} AUC={e['auc']:.3f}")
print(f"  Delta Prec: {e['prec']-b['prec']:+.3f}")
verdict = 'KEEP' if e['prec'] > b['prec'] + 0.005 else 'REJECT'
print(f"\nVerdict: {verdict}")