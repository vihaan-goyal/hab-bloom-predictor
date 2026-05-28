"""
daily_inference.py (corrected)
-------------------------------
Fits the corrected LR (80%) + XGBoost (20%) ensemble on the training set
(1993-2019) and runs historical inference on specified dates and on the
full 2020-2022 validation period.

Run from repo root:
    python src/deploy/daily_inference.py
"""

import warnings
warnings.filterwarnings('ignore', category=UserWarning)
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score
import xgboost as xgb

# --Load data ------------------------------------------------------------------
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
    idx = grp.index
    dates = grp['date'].values
    chl = grp['Chlorophyll'].values
    labels = np.zeros(len(grp), dtype=int)
    for i in range(len(grp)):
        mask = (dates > dates[i]) & (dates <= dates[i] + np.timedelta64(28, 'D'))
        if mask.any() and (chl[mask] > 10).any():
            labels[i] = 1
    df.loc[idx, 'bloom_28d'] = labels

# --Feature set ----------------------------------------------------------------
FEATURES = [
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
FEATURES = [f for f in FEATURES if f in df.columns]

DO_COL   = 'oxygen_concentration_in_sea_water'
TEMP_COL = 'sea_water_temperature'

# --Temporal splits ------------------------------------------------------------
train = df[df['date'].dt.year <= 2019]
val   = df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)]
test  = df[df['date'].dt.year >= 2023]

X_train = train[FEATURES].copy()
y_train = train['bloom_28d'].copy()
X_val   = val[FEATURES].copy()
y_val   = val['bloom_28d'].copy()
X_test  = test[FEATURES].copy()
y_test  = test['bloom_28d'].copy()

MED = X_train.median()

# --Fit ensemble: LR 80% + XGBoost 20% ----------------------------------------
print("\nFitting ensemble (LR 80% + XGBoost 20%) on train set 1993-2019...")

# XGBoost
pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
xgb_model = xgb.XGBClassifier(
    n_estimators=200, max_depth=6, learning_rate=0.1,
    scale_pos_weight=pos_weight, eval_metric='auc',
    random_state=42, verbosity=0,
)
xgb_model.fit(
    X_train.fillna(MED), y_train,
    eval_set=[(X_val.fillna(MED), y_val)],
    verbose=False,
)

# Logistic Regression
scaler = StandardScaler()
X_tr_s = pd.DataFrame(scaler.fit_transform(X_train.fillna(MED)), columns=FEATURES)
X_v_s  = pd.DataFrame(scaler.transform(X_val.fillna(MED)),       columns=FEATURES)
X_te_s = pd.DataFrame(scaler.transform(X_test.fillna(MED)),      columns=FEATURES)

lr_model = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
lr_model.fit(X_tr_s, y_train)

# Validate
xgb_val_p  = xgb_model.predict_proba(X_val.fillna(MED))[:,1]
lr_val_p   = lr_model.predict_proba(X_v_s)[:,1]
ens_val    = 0.80 * lr_val_p + 0.20 * xgb_val_p

xgb_test_p = xgb_model.predict_proba(X_test.fillna(MED))[:,1]
lr_test_p  = lr_model.predict_proba(X_te_s)[:,1]
ens_test   = 0.80 * lr_test_p + 0.20 * xgb_test_p

print(f"Ensemble Val AUC  (2020-2022): {roc_auc_score(y_val,  ens_val):.3f}")
print(f"Ensemble Test AUC (2023-2025): {roc_auc_score(y_test, ens_test):.3f}")

# --Aeration score formula -----------------------------------------------------
# S = 0.45*(14-DO)/12 + 0.30*(T-10)/20 + 0.25*p
# High-risk: S > 0.45 AND DO < 6.0 mg/L

def calc_aeration_score(do, temp, bloom_prob):
    do_term   = np.clip((14.0 - do)   / 12.0, 0.0, 1.0)
    temp_term = np.clip((temp - 10.0) / 20.0, 0.0, 1.0)
    return 0.45 * do_term + 0.30 * temp_term + 0.25 * np.clip(bloom_prob, 0.0, 1.0)


# --run_inference: single station/date lookup ----------------------------------
def run_inference(station, date_str):
    """
    Look up the row nearest to date_str for the given station and return
    bloom_prob, DO, temperature, and aeration_score S.
    """
    target_date = pd.to_datetime(date_str)
    stn_df = df[df['station_name'] == station].copy()
    if stn_df.empty:
        return None

    diffs = (stn_df['date'] - target_date).abs()
    row = stn_df.loc[diffs.idxmin()]

    feat_df = pd.DataFrame([row[FEATURES].fillna(MED)], columns=FEATURES)

    xgb_p = xgb_model.predict_proba(feat_df)[0, 1]
    lr_p  = lr_model.predict_proba(scaler.transform(feat_df))[0, 1]
    bloom_prob = 0.80 * lr_p + 0.20 * xgb_p

    do   = row[DO_COL]   if not pd.isna(row[DO_COL])   else MED[DO_COL]
    temp = row[TEMP_COL] if not pd.isna(row[TEMP_COL]) else MED[TEMP_COL]

    S = calc_aeration_score(float(do), float(temp), bloom_prob)
    raw_do = row[DO_COL]  # use original (may be NaN) for high-risk flag
    high_risk = (S > 0.45) and (not pd.isna(raw_do)) and (float(raw_do) < 6.0)

    return {
        'actual_date': row['date'].strftime('%Y-%m-%d'),
        'bloom_prob':      round(bloom_prob, 4),
        'DO':              round(float(do), 2),
        'temp':            round(float(temp), 2),
        'aeration_score':  round(S, 4),
        'high_risk':       high_risk,
    }


# --Specific historical validation dates --------------------------------------
VALIDATION_DATES = [
    ('A4', '2022-09-01'),
    ('A4', '2022-08-17'),
    ('A4', '2021-08-31'),
    ('A4', '2017-08-15'),
]

print("\n" + "="*80)
print("SPECIFIC DATE INFERENCE")
print("="*80)
header = f"{'Date':<12} {'Station':<10} {'Bloom Prob':>10} {'DO':>6} {'Temp':>6} {'Aeration S':>11} {'High Risk?':>10}"
print(header)
print("-" * len(header))

for station, date_str in VALIDATION_DATES:
    result = run_inference(station, date_str)
    if result is None:
        print(f"{date_str:<12} {station:<10}  -- station not found")
        continue
    hr_str = "YES *" if result['high_risk'] else "no"
    print(
        f"{result['actual_date']:<12} {station:<10} "
        f"{result['bloom_prob']:>10.3f} "
        f"{result['DO']:>6.2f} "
        f"{result['temp']:>6.1f} "
        f"{result['aeration_score']:>11.4f} "
        f"{hr_str:>10}"
    )

# --Full validation period analysis (2020-2022) -------------------------------
print("\n" + "="*80)
print("FULL VAL PERIOD ANALYSIS (2020-2022)")
print("="*80)

# Reset to 0-based index so numpy arrays align cleanly
X_val_arr = X_val.fillna(MED).values
val_feats_scaled = scaler.transform(X_val_arr)

xgb_probs = xgb_model.predict_proba(X_val_arr)[:,1]
lr_probs  = lr_model.predict_proba(val_feats_scaled)[:,1]
ens_probs = 0.80 * lr_probs + 0.20 * xgb_probs

val_df = val[[DO_COL, TEMP_COL, 'bloom_28d', 'station_name', 'date']].reset_index(drop=True).copy()
val_df['bloom_prob'] = ens_probs

do_vals   = val_df[DO_COL].fillna(MED[DO_COL]).values
temp_vals = val_df[TEMP_COL].fillna(MED[TEMP_COL]).values
val_df['aeration_score'] = calc_aeration_score(do_vals, temp_vals, ens_probs)

val_df['high_risk'] = (
    (val_df['aeration_score'] > 0.45) &
    (val_df[DO_COL] < 6.0)
)

total_days  = len(val_df)
hr_days     = val_df['high_risk'].sum()
hr_pct      = hr_days / total_days * 100

print(f"\nTotal station-days (2020-2022): {total_days:,}")
print(f"High-risk days (S>0.45 & DO<6): {hr_days:,} ({hr_pct:.1f}%)")

# Top 10 stations by high-risk days
print("\n--Top 10 Stations by High-Risk Days ----------------------------------")
stn_hr = (
    val_df.groupby('station_name')['high_risk']
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)
stn_hr.columns = ['Station', 'High-Risk Days']
print(stn_hr.to_string(index=False))

# Top 5 months by mean aeration score
print("\n--Top 5 Months by Mean Aeration Score --------------------------------")
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
month_aer = month_aer[['Month', 'aeration_score']].rename(
    columns={'aeration_score': 'Mean Aeration Score'}
)
print(month_aer.to_string(index=False))

print(f"\nTotal high-risk station-days: {hr_days:,} out of {total_days:,} "
      f"({hr_pct:.1f}%)")
