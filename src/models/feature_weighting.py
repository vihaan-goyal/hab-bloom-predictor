r"""
feature_weighting.py
--------------------
Prints the percent weighting each feature has on the locked LR model, computed
as |coef| / sum(|coef|). Coefficients are on STANDARDIZED features, so magnitudes
are directly comparable across features (that is the whole reason for scaling).

Also prints a GROUPED view, because 13 of the 34 features are chlorophyll
derivatives. Under heavy L2 (C=0.05) the credit for a signal gets split across
correlated columns, so per-feature percentages understate chlorophyll's true
role. The grouped view is the honest one to quote.

Pipeline matches src/models/ablation_study.py exactly so coefficients line up
with the locked model.

Run from repo root:
    python src/models/feature_weighting.py
"""

import glob
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

# -- Load + merge (mirrors ablation_study.py) ----------------------------------
hab = pd.read_csv('data/hab_features_tidal.csv')
daily = pd.read_csv('data/hab_features_daily.csv')[
    ['date', 'station_name', 'sal_lag2', 'sal_lag3', 'sal_lag4']]
hab['date'] = pd.to_datetime(hab['date'])
daily['date'] = pd.to_datetime(daily['date'])
for col in ['sal_lag2', 'sal_lag3', 'sal_lag4']:
    if col not in hab.columns:
        hab = hab.merge(daily[['date', 'station_name', col]],
                        on=['date', 'station_name'], how='left')


def load_percent_saturation():
    frames = []
    for f in sorted(glob.glob('data/raw/deep_wq_extra/deep_wq_S_*.csv')):
        s = pd.read_csv(f, skiprows=[1],
                        usecols=['station_name', 'time', 'percent_saturation'])
        frames.append(s)
    ps = pd.concat(frames, ignore_index=True)
    ps = ps[ps['station_name'].notna()].copy()
    ps['station_name'] = ps['station_name'].astype(str)
    ps['date'] = pd.to_datetime(ps['time'], utc=True).dt.tz_localize(None).dt.normalize()
    ps['percent_saturation'] = pd.to_numeric(ps['percent_saturation'], errors='coerce')
    return (ps.dropna(subset=['percent_saturation'])
              .groupby(['date', 'station_name'], as_index=False)['percent_saturation']
              .mean())


if 'percent_saturation' not in hab.columns:
    ps = load_percent_saturation()
    hab['station_name'] = hab['station_name'].astype(str)
    hab = hab.merge(ps, on=['date', 'station_name'], how='left')

df = hab

# -- Rolling features + label --------------------------------------------------
for n, min_p in [(3, 2), (6, 3), (9, 5), (14, 7), (21, 10)]:
    df[f'chl_roll{n}_mean'] = (df.groupby('station_name')['Chlorophyll']
        .transform(lambda x: x.rolling(n, min_periods=min_p).mean()))
df['chl_trend'] = (df.groupby('station_name')['Chlorophyll']
    .transform(lambda x: x.rolling(4, min_periods=3)
               .apply(lambda v: np.polyfit(range(len(v)), v, 1)[0])))

df['bloom_28d'] = 0
for station, grp in df.groupby('station_name'):
    dates, chl = grp['date'].values, grp['Chlorophyll'].values
    labels = np.zeros(len(grp), dtype=int)
    for i in range(len(grp)):
        mask = (dates > dates[i]) & (dates <= dates[i] + np.timedelta64(28, 'D'))
        if mask.any() and (chl[mask] > 10).any():
            labels[i] = 1
    df.loc[grp.index, 'bloom_28d'] = labels

BASE = [
    'Chlorophyll', 'chl_lag1', 'chl_lag2', 'chl_lag3', 'chl_lag4',
    'chl_roll3_mean', 'chl_roll6_mean', 'chl_roll9_mean', 'chl_trend',
    'chl_roll14_mean', 'chl_roll21_mean', 'chl_anomaly', 'chl_climatology',
    'do_lag1', 'temp_lag1', 'sal_lag1', 'sal_lag2', 'sal_lag3', 'sal_lag4',
    'sea_water_temperature', 'sea_water_salinity',
    'oxygen_concentration_in_sea_water', 'month', 'latitude_x', 'longitude_x',
    'nox_lag2', 'dip_lag2', 'dip_change', 'dip_x_month',
    'neighbor_chl3_mean', 'neighbor_chl3_lag1', 'tidal_gt_anom',
    'tidal_msl_anom', 'percent_saturation',
]
BASE = [f for f in BASE if f in df.columns]

GROUPS = {
    'chlorophyll': ['Chlorophyll', 'chl_lag1', 'chl_lag2', 'chl_lag3', 'chl_lag4',
                    'chl_roll3_mean', 'chl_roll6_mean', 'chl_roll9_mean',
                    'chl_trend', 'chl_roll14_mean', 'chl_roll21_mean',
                    'chl_anomaly', 'chl_climatology', 'neighbor_chl3_mean',
                    'neighbor_chl3_lag1'],
    'temperature': ['sea_water_temperature', 'temp_lag1'],
    'salinity':    ['sea_water_salinity', 'sal_lag1', 'sal_lag2', 'sal_lag3', 'sal_lag4'],
    'oxygen':      ['oxygen_concentration_in_sea_water', 'do_lag1', 'percent_saturation'],
    'nutrients':   ['nox_lag2', 'dip_lag2', 'dip_change', 'dip_x_month'],
    'tidal':       ['tidal_gt_anom', 'tidal_msl_anom'],
    'space/time':  ['month', 'latitude_x', 'longitude_x'],
}

# -- Fit on training years, standardized --------------------------------------
train = df[df['date'].dt.year <= 2019]
rows = train[BASE + ['bloom_28d']].dropna(subset=['bloom_28d'])
X = rows[BASE].copy()
y = rows['bloom_28d'].copy()
MED = X.median()

sc = StandardScaler()
lr = LogisticRegression(C=0.05, class_weight='balanced', max_iter=2000, random_state=42)
lr.fit(sc.fit_transform(X.fillna(MED)), y)

coef = lr.coef_[0]
abssum = np.abs(coef).sum()

# -- Per-feature table ---------------------------------------------------------
tbl = (pd.DataFrame({'feature': BASE, 'coef': coef, 'abs': np.abs(coef)})
       .assign(pct=lambda d: 100 * d['abs'] / abssum,
               direction=lambda d: np.where(d['coef'] >= 0, 'raises', 'lowers'))
       .sort_values('pct', ascending=False))

print("=" * 62)
print("PER-FEATURE WEIGHTING  (|coef| share of total, standardized)")
print("=" * 62)
print(f"{'feature':<34}{'pct':>7}  {'direction':>9}")
print("-" * 62)
for _, r in tbl.iterrows():
    print(f"{r['feature']:<34}{r['pct']:>6.1f}%  {r['direction']:>9}")

# -- Grouped table -------------------------------------------------------------
grp_rows = []
for name, feats in GROUPS.items():
    present = [f for f in feats if f in BASE]
    share = 100 * np.abs(coef[[BASE.index(f) for f in present]]).sum() / abssum
    grp_rows.append((name, len(present), share))
grp_rows.sort(key=lambda x: -x[2])

print("\n" + "=" * 62)
print("GROUPED WEIGHTING  (quote this one)")
print("=" * 62)
print(f"{'group':<16}{'n_feat':>8}{'pct':>10}")
print("-" * 62)
for name, n, share in grp_rows:
    print(f"{name:<16}{n:>8}{share:>9.1f}%")
print(f"\nSum: {sum(s for _, _, s in grp_rows):.1f}%  (should be ~100)")