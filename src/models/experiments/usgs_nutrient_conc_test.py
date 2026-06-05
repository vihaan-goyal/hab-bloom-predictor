"""
usgs_nutrient_conc_test.py
--------------------------
Test whether actual USGS river nutrient concentrations (N, P) from
three LIS tributaries improve over the 35-feature baseline.

Background: prior discharge-volume test showed r<0.03 (rejected).
Nutrient concentration × discharge = actual loading pulse -- different signal.

Data: three per-river WQP exports in data/raw/:
  data/raw/usgs_ct_river.csv    -- Connecticut River at Thompsonville
  data/raw/usgs_thames.csv      -- Thames River
  data/raw/usgs_housatonic.csv  -- Housatonic River

Run from repo root:
    $env:USERPROFILE\\anaconda3\\python.exe src/models/experiments/usgs_nutrient_conc_test.py
"""

import glob
import os
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

import pandas as pd
import numpy as np
from functools import reduce
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
)

# ---------------------------------------------------------------------------
# Step 1: Process USGS nutrient data
# ---------------------------------------------------------------------------
OUT_PATH = 'data/raw/usgs_nutrient_conc.csv'

print("=" * 70)
print("STEP 1: Processing USGS nutrient data")
print("=" * 70)

files = {
    'CT_River':   'data/raw/usgs_ct_river.csv',
    'Thames':     'data/raw/usgs_thames.csv',
    'Housatonic': 'data/raw/usgs_housatonic.csv',
}
# Load and combine all three
frames = []
for river, fpath in files.items():
    df = pd.read_csv(fpath, low_memory=False)
    df['river'] = river
    frames.append(df)
df_all = pd.concat(frames, ignore_index=True)
print(f"  Raw WQP rows: {len(df_all):,}")

usgs = df_all.copy()
usgs['date']  = pd.to_datetime(usgs['ActivityStartDate'], errors='coerce')
usgs['value'] = pd.to_numeric(usgs['ResultMeasureValue'],  errors='coerce')
usgs = usgs.dropna(subset=['date', 'value', 'river'])
print(f"  Rows after station/value filter: {len(usgs):,}")
print(f"  Characteristics present: {usgs['CharacteristicName'].unique().tolist()}")

nutrient_map = {
    'Nitrate':                                   'nox_conc',
    'Nitrate + Nitrite':                         'nox_conc',
    'Inorganic nitrogen (nitrate and nitrite)':  'nox_conc',
    'Phosphorus':                                'p_conc',
    'Orthophosphate':                            'dip_conc',
    'Ammonia and ammonium':                      'nh3_conc',
}

frames = []

# Sound-wide daily means (average across all three rivers)
for char, col in nutrient_map.items():
    sub = usgs[usgs['CharacteristicName'] == char].copy()
    if len(sub) == 0:
        continue
    daily = sub.groupby('date')['value'].mean().reset_index()
    daily = daily.rename(columns={'value': col})
    frames.append(daily)

# Per-river NOX (CT River is the dominant LIS contributor)
nox_chars = ['Nitrate', 'Nitrate + Nitrite',
             'Inorganic nitrogen (nitrate and nitrite)']
for river in ['CT_River', 'Thames', 'Housatonic']:
    river_sub = usgs[usgs['river'] == river]
    nox = river_sub[river_sub['CharacteristicName'].isin(nox_chars)]
    if len(nox) > 0:
        daily_r = nox.groupby('date')['value'].mean().reset_index()
        col = f'nox_{river.lower()}'
        daily_r = daily_r.rename(columns={'value': col})
        frames.append(daily_r)

if not frames:
    raise RuntimeError("No nutrient frames built — check characteristic names in WQP data")

nutrient_df = reduce(lambda a, b: pd.merge(a, b, on='date', how='outer'), frames)
nutrient_df = nutrient_df.sort_values('date').reset_index(drop=True)

# Deduplicate columns that arose from multiple CharacteristicName → same col
nutrient_df = nutrient_df.groupby('date', as_index=False).first()

# Rolling means -- nutrient pulse travels 1-3 weeks downstream to western LIS
base_cols = [c for c in nutrient_df.columns if c != 'date']
for col in base_cols:
    nutrient_df[f'{col}_roll14'] = (
        nutrient_df[col].rolling(14, min_periods=5).mean()
    )
    nutrient_df[f'{col}_roll28'] = (
        nutrient_df[col].rolling(28, min_periods=10).mean()
    )

os.makedirs('data/raw', exist_ok=True)
nutrient_df.to_csv(OUT_PATH, index=False)
print(f"\n  Saved {len(nutrient_df)} daily records to {OUT_PATH}")
print(f"  Date range: {nutrient_df['date'].min().date()} to "
      f"{nutrient_df['date'].max().date()}")
print(f"  Columns: {[c for c in nutrient_df.columns if c != 'date']}")

# ---------------------------------------------------------------------------
# Step 2: Load HAB features and merge
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("STEP 2: Loading HAB features and merging nutrients")
print("=" * 70)

hab = pd.read_csv('data/hab_features_tidal.csv')
hab['date'] = pd.to_datetime(hab['date'])
print(f"  HAB rows: {len(hab):,}")

# percent_saturation
if 'percent_saturation' not in hab.columns:
    frames_ps = []
    for f in sorted(glob.glob('data/raw/deep_wq_extra/deep_wq_S_*.csv')):
        frames_ps.append(pd.read_csv(
            f, skiprows=[1],
            usecols=['station_name', 'time', 'percent_saturation']))
    ps = pd.concat(frames_ps, ignore_index=True)
    ps = ps[ps['station_name'].notna()].copy()
    ps['station_name'] = ps['station_name'].astype(str)
    ps['date'] = (pd.to_datetime(ps['time'], utc=True)
                    .dt.tz_localize(None).dt.normalize())
    ps['percent_saturation'] = pd.to_numeric(ps['percent_saturation'], errors='coerce')
    ps = (ps.dropna(subset=['percent_saturation'])
            .groupby(['date', 'station_name'], as_index=False)
            ['percent_saturation'].mean())
    hab['station_name'] = hab['station_name'].astype(str)
    hab = hab.merge(ps, on=['date', 'station_name'], how='left')
    print(f"  percent_saturation coverage: "
          f"{hab['percent_saturation'].notna().mean()*100:.1f}%")

# max_gust_3d
gust = pd.read_csv('data/gust_features_daily.csv', usecols=['date', 'max_gust_3d'])
gust['date'] = pd.to_datetime(gust['date'])
hab = hab.merge(gust, on='date', how='left')
print(f"  max_gust_3d coverage: {hab['max_gust_3d'].notna().mean()*100:.1f}%")

# Chlorophyll rolling means + trend
for n, min_p in [(3, 2), (6, 3), (9, 5), (14, 7), (21, 10)]:
    hab[f'chl_roll{n}_mean'] = (
        hab.groupby('station_name')['Chlorophyll']
           .transform(lambda x: x.rolling(n, min_periods=min_p).mean())
    )
hab['chl_trend'] = (
    hab.groupby('station_name')['Chlorophyll']
       .transform(lambda x: x.rolling(4, min_periods=3)
                  .apply(lambda v: np.polyfit(range(len(v)), v, 1)[0]))
)

# bloom_28d label
hab['bloom_28d'] = 0
for station, grp in hab.groupby('station_name'):
    idx   = grp.index
    dates = grp['date'].values
    chl   = grp['Chlorophyll'].values
    labels = np.zeros(len(grp), dtype=int)
    for i in range(len(grp)):
        mask = (dates > dates[i]) & (dates <= dates[i] + np.timedelta64(28, 'D'))
        if mask.any() and (chl[mask] > 10).any():
            labels[i] = 1
    hab.loc[idx, 'bloom_28d'] = labels

# Merge nutrient features (date-level join)
hab = hab.merge(nutrient_df, on='date', how='left')
nutr_cols = [c for c in nutrient_df.columns if c != 'date']
for col in nutr_cols:
    cov = hab[col].notna().mean() * 100
    if cov > 1:
        print(f"  {col}: {cov:.1f}% coverage")

# ---------------------------------------------------------------------------
# Step 2b: Correlations
# ---------------------------------------------------------------------------
print("\n--- Pearson correlations with bloom_28d (nutrient features) ---")
roll_cols = [c for c in nutr_cols if 'roll' in c]
corr_rows = []
for col in roll_cols:
    if hab[col].notna().sum() < 50:
        continue
    r = hab[col].corr(hab['bloom_28d'])
    corr_rows.append((col, r, hab[col].notna().sum()))
corr_rows.sort(key=lambda x: abs(x[1]), reverse=True)
for col, r, n in corr_rows:
    print(f"  {col:<30s}  r={r:+.4f}  (n={n:,})")

# ---------------------------------------------------------------------------
# Step 3: Feature sets and evaluation
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("STEP 3: Feature set comparison")
print("=" * 70)

BASE = [
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
BASE = [f for f in BASE if f in hab.columns]

NUTR_ROLL14 = [c for c in roll_cols if 'roll14' in c]
NUTR_ROLL28 = [c for c in roll_cols if 'roll28' in c]

feature_sets = {
    'BASE (baseline)':               BASE,
    'BASE + nox_conc_roll14':        BASE + ['nox_conc_roll14'],
    'BASE + nox_conc_roll28':        BASE + ['nox_conc_roll28'],
    'BASE + p_conc_roll14':          BASE + ['p_conc_roll14'],
    'BASE + nox_ct_river_roll14':    BASE + ['nox_ct_river_roll14'],
    'BASE + nox_ct_river_roll28':    BASE + ['nox_ct_river_roll28'],
    'BASE + nox+p_roll14':           BASE + ['nox_conc_roll14', 'p_conc_roll14'],
    'BASE + all_nutr_roll14':        BASE + NUTR_ROLL14,
}
# Drop sets that reference unavailable columns
feature_sets = {
    name: [f for f in feats if f in hab.columns]
    for name, feats in feature_sets.items()
    if any(f in hab.columns for f in feats if f not in BASE)
    or name == 'BASE (baseline)'
}

THRESHOLD = 0.60

train = hab[hab['date'].dt.year <= 2019]
val   = hab[(hab['date'].dt.year >= 2020) & (hab['date'].dt.year <= 2022)]
test  = hab[hab['date'].dt.year >= 2023]

results = []
for name, feats in feature_sets.items():
    missing = [f for f in feats if f not in hab.columns]
    if missing:
        print(f"  SKIP {name}: missing {missing}")
        continue

    def prep(split, cols):
        rows = split[cols + ['bloom_28d']].dropna(subset=['bloom_28d'])
        return rows[cols].copy(), rows['bloom_28d'].copy()

    X_tr, y_tr = prep(train, feats)
    X_te, y_te = prep(test, feats)

    med = X_tr.median()
    scaler = StandardScaler()
    X_tr_s = scaler.fit_transform(X_tr.fillna(med))
    X_te_s = scaler.transform(X_te.fillna(med))

    lr = LogisticRegression(
        class_weight='balanced', C=0.05, max_iter=1000, random_state=42
    )
    lr.fit(X_tr_s, y_tr)
    proba = lr.predict_proba(X_te_s)[:, 1]
    preds = (proba >= THRESHOLD).astype(int)

    auc  = roc_auc_score(y_te, proba)
    prec = precision_score(y_te, preds, zero_division=0)
    rec  = recall_score(y_te, preds, zero_division=0)
    f1   = f1_score(y_te, preds, zero_division=0)
    tp   = int(((preds == 1) & (y_te == 1)).sum())
    fp   = int(((preds == 1) & (y_te == 0)).sum())
    fn   = int(((preds == 0) & (y_te == 1)).sum())

    # Feature coverage for the first nutrient column added
    extra = [f for f in feats if f not in BASE]
    if extra:
        cov = hab[extra[0]].notna().mean() * 100
    else:
        cov = 100.0

    results.append({
        'name':      name,
        'n_feats':   len(feats),
        'auc':       auc,
        'prec':      prec,
        'rec':       rec,
        'f1':        f1,
        'tp': tp, 'fp': fp, 'fn': fn,
        'nutr_cov':  cov,
    })
    print(f"  Done: {name}")

# ---------------------------------------------------------------------------
# Output table
# ---------------------------------------------------------------------------
results_df = pd.DataFrame(results).sort_values('f1', ascending=False)

BASE_F1   = results_df.loc[results_df['name'] == 'BASE (baseline)', 'f1'].values[0]
BASE_PREC = results_df.loc[results_df['name'] == 'BASE (baseline)', 'prec'].values[0]

print("\n" + "=" * 90)
print(f"RESULTS @ threshold={THRESHOLD:.2f}  (test 2023-2025, sorted by F1)")
print("=" * 90)
print(f"{'Name':<36} {'F':<3} {'AUC':>5} {'Prec':>6} {'Rec':>6} {'F1':>6} "
      f"{'TP':>4} {'FP':>4} {'FN':>4} {'Cov%':>6}  Flag")
print("-" * 90)
for _, r in results_df.iterrows():
    df1   = r['f1']   - BASE_F1
    dprec = r['prec'] - BASE_PREC
    flag  = ""
    if r['name'] != 'BASE (baseline)':
        if df1 > 0.010:
            flag += " F1++"
        if dprec > 0.020:
            flag += " PREC++"
        if df1 < -0.010:
            flag += " F1--"
    print(f"  {r['name']:<34} {r['n_feats']:>3} {r['auc']:>5.3f} "
          f"{r['prec']:>6.3f} {r['rec']:>6.3f} {r['f1']:>6.3f} "
          f"{r['tp']:>4} {r['fp']:>4} {r['fn']:>4} {r['nutr_cov']:>6.1f}%"
          f"  {flag}")

print("\nBaseline: Prec=0.500, Rec=0.486, F1=0.493  (expected match)")
print("Flag key:  F1++ = +0.010 improvement  |  PREC++ = +0.020 precision gain")
