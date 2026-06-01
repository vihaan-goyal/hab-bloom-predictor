"""
daily_inference.py
------------------
Fits LR on the training set (1993-2022) and runs historical inference on
specified dates and on the full 2022 validation period.

Run from repo root:
    python src/deploy/daily_inference.py --date 2022-09-01
"""

import warnings
warnings.filterwarnings('ignore', category=UserWarning)
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--date', type=str, default='2022-09-01')
args = parser.parse_args()
TARGET_DATE = args.date

# -- Load data -----------------------------------------------------------------
print("Loading data/hab_features_daily.csv...")
df = pd.read_csv("data/hab_features_daily.csv")
df['date'] = pd.to_datetime(df['date'])

# Recompute rolling features and bloom label for consistency
for n, min_p in [(3, 2), (6, 3), (9, 5)]:
    df[f'chl_roll{n}_mean'] = (
        df.groupby('station_name')['Chlorophyll']
          .transform(lambda x: x.rolling(n, min_periods=min_p).mean())
    )

df['chl_trend'] = (
    df.groupby('station_name')['Chlorophyll']
      .transform(lambda x: x.rolling(4, min_periods=3)
                 .apply(lambda v: np.polyfit(range(len(v)), v, 1)[0]))
)

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

# -- Feature set ---------------------------------------------------------------
FEATURES_ALL = [
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
FEATURES = [f for f in FEATURES_ALL if f in df.columns]

DO_COL   = 'oxygen_concentration_in_sea_water'
TEMP_COL = 'sea_water_temperature'

MAX_DATE_GAP_DAYS = 14   # skip station if nearest row is further than this

# Intervention thresholds
BLOOM_PROB_THRESHOLD = 0.60
AERATION_SCORE_MIN    = 0.45
DO_HYPOXIA_THRESHOLD  = 6.0

# -- Temporal splits -----------------------------------------------------------
train = df[df['date'].dt.year <= 2022]
val   = df[df['date'].dt.year == 2022]
test  = df[df['date'].dt.year >= 2023]

X_train = train[FEATURES].copy()
y_train = train['bloom_28d'].copy()
X_val   = val[FEATURES].copy()
y_val   = val['bloom_28d'].copy()
X_test  = test[FEATURES].copy()
y_test  = test['bloom_28d'].copy()

MED = X_train.median()

# -- Fit LR on train 1993-2022 -------------------------------------------------
print("\nFitting LR on train set 1993-2022...")

scaler = StandardScaler()
X_tr_s = scaler.fit_transform(X_train.fillna(MED))
X_v_s  = scaler.transform(X_val.fillna(MED))
X_te_s = scaler.transform(X_test.fillna(MED))

lr_model = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
lr_model.fit(X_tr_s, y_train)

lr_val_p  = lr_model.predict_proba(X_v_s)[:, 1]
lr_test_p = lr_model.predict_proba(X_te_s)[:, 1]

print(f"LR Val AUC  (2022):      {roc_auc_score(y_val,  lr_val_p):.3f}")
print(f"LR Test AUC (2023-2025): {roc_auc_score(y_test, lr_test_p):.3f}")

# -- Aeration score ------------------------------------------------------------
def calc_aeration_score(do, temp, bloom_prob):
    do_term   = np.clip((14.0 - do)   / 12.0, 0.0, 1.0)
    temp_term = np.clip((temp - 10.0) / 20.0, 0.0, 1.0)
    return 0.45 * do_term + 0.30 * temp_term + 0.25 * np.clip(bloom_prob, 0.0, 1.0)

# -- Single station/date inference ---------------------------------------------
def run_inference(station, date_str):
    target_date = pd.to_datetime(date_str)
    stn_df = df[df['station_name'] == station].copy()
    if stn_df.empty:
        return None

    diffs = (stn_df['date'] - target_date).abs()
    nearest_idx = diffs.idxmin()
    if diffs[nearest_idx].days > MAX_DATE_GAP_DAYS:
        return None

    row = stn_df.loc[nearest_idx]
    feat_df = pd.DataFrame([row[FEATURES].fillna(MED)], columns=FEATURES)

    bloom_prob = lr_model.predict_proba(scaler.transform(feat_df))[0, 1]

    raw_do = row[DO_COL]
    raw_temp = row[TEMP_COL]
    do   = float(raw_do)   if not pd.isna(raw_do)   else float(MED[DO_COL])
    temp = float(raw_temp) if not pd.isna(raw_temp) else float(MED[TEMP_COL])

    S = calc_aeration_score(do, temp, bloom_prob)
    high_risk = (
        bloom_prob > BLOOM_PROB_THRESHOLD and
        S > AERATION_SCORE_MIN and
        not pd.isna(raw_do) and
        float(raw_do) < DO_HYPOXIA_THRESHOLD
    )

    return {
        'actual_date':    row['date'].strftime('%Y-%m-%d'),
        'bloom_prob':     round(bloom_prob, 4),
        'DO':             round(do, 2),
        'temp':           round(temp, 2),
        'aeration_score': round(S, 4),
        'high_risk':      high_risk,
    }

# -- Specific date inference ---------------------------------------------------
print("\n" + "=" * 80)
print(f"SPECIFIC DATE INFERENCE  ({TARGET_DATE})")
print("=" * 80)
header = (f"{'Date':<12} {'Station':<10} {'Bloom Prob':>10} "
          f"{'DO':>6} {'Temp':>6} {'Aeration S':>11} {'High Risk?':>10}")
print(header)
print("-" * len(header))

result = run_inference('A4', TARGET_DATE)
if result is None:
    print(f"{TARGET_DATE:<12} {'A4':<10}  -- no data within {MAX_DATE_GAP_DAYS} days")
else:
    hr_str = "YES *" if result['high_risk'] else "no"
    print(
        f"{result['actual_date']:<12} {'A4':<10} "
        f"{result['bloom_prob']:>10.3f} "
        f"{result['DO']:>6.2f} "
        f"{result['temp']:>6.1f} "
        f"{result['aeration_score']:>11.4f} "
        f"{hr_str:>10}"
    )

# -- Full validation period analysis (2022) ------------------------------------
print("\n" + "=" * 80)
print("FULL VAL PERIOD ANALYSIS (2022)")
print("=" * 80)

X_val_arr        = X_val.fillna(MED).values
val_feats_scaled = scaler.transform(X_val_arr)

lr_probs = lr_model.predict_proba(val_feats_scaled)[:, 1]

val_df = val[[DO_COL, TEMP_COL, 'bloom_28d', 'station_name', 'date']].reset_index(drop=True).copy()
val_df['bloom_prob'] = lr_probs

do_vals   = val_df[DO_COL].fillna(MED[DO_COL]).values
temp_vals = val_df[TEMP_COL].fillna(MED[TEMP_COL]).values
val_df['aeration_score'] = calc_aeration_score(do_vals, temp_vals, lr_probs)

val_df['high_risk'] = (
    (val_df['bloom_prob'] > BLOOM_PROB_THRESHOLD) &
    (val_df['aeration_score'] > AERATION_SCORE_MIN) &
    (val_df[DO_COL] < DO_HYPOXIA_THRESHOLD)
)

total_days = len(val_df)
hr_days    = val_df['high_risk'].sum()
hr_pct     = hr_days / total_days * 100

print(f"\nTotal station-days (2022): {total_days:,}")
print(f"High-risk days (bloom_prob>{BLOOM_PROB_THRESHOLD} & S>{AERATION_SCORE_MIN} & DO<{DO_HYPOXIA_THRESHOLD}): {hr_days:,} ({hr_pct:.1f}%)")

print("\n-- Top 10 Stations by High-Risk Days ---------------------------------")
stn_hr = (
    val_df.groupby('station_name')['high_risk']
          .sum()
          .sort_values(ascending=False)
          .head(10)
          .reset_index()
)
stn_hr.columns = ['Station', 'High-Risk Days']
print(stn_hr.to_string(index=False))

print("\n-- Top 5 Months by Mean Aeration Score -------------------------------")
month_names = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',
               7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
val_df['month_num'] = val_df['date'].dt.month
month_aer = (
    val_df.groupby('month_num')['aeration_score']
          .mean()
          .sort_values(ascending=False)
          .head(5)
          .reset_index()
)
month_aer['Month'] = month_aer['month_num'].map(month_names)
print(month_aer[['Month', 'aeration_score']].rename(
    columns={'aeration_score': 'Mean Aeration Score'}).to_string(index=False))

print(f"\nTotal high-risk station-days: {hr_days:,} out of {total_days:,} ({hr_pct:.1f}%)")

# -- Show actual high-risk dates for A4 (for finding valid demo dates) ---------
a4_hr = val_df[(val_df['station_name'] == 'A4') & val_df['high_risk']]
if len(a4_hr) > 0:
    print("\n-- A4 high-risk dates (use these as demo dates) ----------------------")
    print(a4_hr[['date', 'bloom_prob', DO_COL, 'aeration_score']].to_string(index=False))
else:
    print("\n-- No high-risk days found for A4 in val period ----------------------")
    print("-- Top 5 A4 days by bloom_prob instead: ------------------------------")
    a4_all = val_df[val_df['station_name'] == 'A4'].nlargest(5, 'bloom_prob')
    print(a4_all[['date', 'bloom_prob', DO_COL, 'aeration_score']].to_string(index=False))

# -- All high-risk days across all stations ------------------------------------
all_hr = val_df[val_df['high_risk']].sort_values('bloom_prob', ascending=False)
if len(all_hr) > 0:
    print("\n-- All high-risk station-days (top 20 by bloom prob) -----------------")
    print(all_hr[['date', 'station_name', 'bloom_prob', DO_COL, 'aeration_score']]
          .head(20).to_string(index=False))

# -- Save daily_predictions.csv for dashboard ----------------------------------
print("\nSaving data/daily_predictions.csv...")

all_stations = df['station_name'].unique()
rows = []
for stn in all_stations:
    result = run_inference(stn, TARGET_DATE)
    if result is None:
        continue
    action = ("Intervene" if result['high_risk'] else
              "Monitor"   if result['bloom_prob'] > 0.40 else "OK")
    rows.append({
        'station_name':   stn,
        'date':           TARGET_DATE,
        'bloom_prob':     result['bloom_prob'],
        'aeration_score': result['aeration_score'],
        'do':             result['DO'],
        'temp':           result['temp'],
        'action':         action,
    })

out_df = pd.DataFrame(rows).sort_values('bloom_prob', ascending=False)
out_df.to_csv("data/daily_predictions.csv", index=False)
print(f"Saved {len(out_df)} stations to data/daily_predictions.csv")