"""
test_calibration.py
-------------------
Tests isotonic regression calibration on top of the locked LR baseline.

Method: fit the base LR on train (1993-2019), then fit a CalibratedClassifierCV
wrapper with method='isotonic' on the VAL set (2020-2022) using cv='prefit'.
Evaluate on test (2023-2025).

The idea: LR with class_weight='balanced' tends to output probabilities that
are systematically miscalibrated. Isotonic regression on the val set learns a
monotone mapping from raw LR scores -> better-calibrated probabilities, which
can shift the precision/recall tradeoff at a fixed threshold.

Run from repo root:
    python test_calibration.py
"""

import glob
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    roc_auc_score, precision_score, recall_score, f1_score,
    precision_recall_curve, average_precision_score,
)

THRESHOLD = 0.60

# ── LOAD (exact locked pipeline) ─────────────────────────────────────────────
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
    ps['station_name'] = ps['station_name'].astype(str)
    ps['date'] = pd.to_datetime(ps['time'], utc=True).dt.tz_localize(None).dt.normalize()
    ps['percent_saturation'] = pd.to_numeric(ps['percent_saturation'], errors='coerce')
    ps = (ps.dropna(subset=['percent_saturation'])
            .groupby(['date', 'station_name'], as_index=False)
            ['percent_saturation'].mean())
    df['station_name'] = df['station_name'].astype(str)
    df = df.merge(ps, on=['date', 'station_name'], how='left')

print("Merging max_gust_3d...")
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
    'do_lag1', 'temp_lag1', 'sal_lag1',
    'sal_lag2', 'sal_lag3', 'sal_lag4',
    'sea_water_temperature', 'sea_water_salinity',
    'oxygen_concentration_in_sea_water',
    'month', 'latitude_x', 'longitude_x',
    'nox_lag2', 'dip_lag2', 'dip_change', 'dip_x_month',
    'neighbor_chl3_mean', 'neighbor_chl3_lag1',
    'tidal_gt_anom', 'tidal_msl_anom',
    'percent_saturation', 'max_gust_3d',
]
FEATURES = [f for f in FEATURES if f in df.columns]

# ── SPLITS ────────────────────────────────────────────────────────────────────
train = df[df['date'].dt.year <= 2019]
val   = df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)]
test  = df[df['date'].dt.year >= 2023]

def prep(split):
    rows = split[FEATURES + ['bloom_28d']].dropna(subset=['bloom_28d'])
    X = rows[FEATURES].copy().reset_index(drop=True)
    y = rows['bloom_28d'].copy().reset_index(drop=True)
    return X, y

X_train, y_train = prep(train)
X_val,   y_val   = prep(val)
X_test,  y_test  = prep(test)

MED = X_train.median()

scaler = StandardScaler()
X_tr_s = scaler.fit_transform(X_train.fillna(MED))
X_v_s  = scaler.transform(X_val.fillna(MED))
X_te_s = scaler.transform(X_test.fillna(MED))

# ── FIT BASE LR ───────────────────────────────────────────────────────────────
print("\nFitting base LR (train 1993-2019)...")
base_lr = LogisticRegression(C=0.05, class_weight='balanced',
                             max_iter=1000, random_state=42)
base_lr.fit(X_tr_s, y_train)

base_val_p  = base_lr.predict_proba(X_v_s)[:, 1]
base_test_p = base_lr.predict_proba(X_te_s)[:, 1]

# ── FIT ISOTONIC CALIBRATION ON VAL ──────────────────────────────────────────
# cv='prefit' means: base_lr is already fitted, just learn the isotonic
# mapping from val set probabilities -> better calibrated probabilities.
print("Fitting isotonic calibration on val (2020-2022)...")
# sklearn < 1.2 uses cv='prefit'; >= 1.2 uses the estimator's is_fitted state.
# Use try/except to handle both versions.
try:
    cal_lr = CalibratedClassifierCV(base_lr, method='isotonic', cv='prefit')
    cal_lr.fit(X_v_s, y_val)
except Exception:
    from sklearn.isotonic import IsotonicRegression
    # Manual fallback: fit isotonic on val probs directly
    iso = IsotonicRegression(out_of_bounds='clip')
    iso.fit(base_val_p, y_val)
    class _IsoWrapper:
        def predict_proba(self, X):
            raw = base_lr.predict_proba(X)[:, 1]
            cal = iso.predict(raw)
            return np.column_stack([1 - cal, cal])
    cal_lr = _IsoWrapper()

cal_test_p = cal_lr.predict_proba(X_te_s)[:, 1]

# ── ALSO TRY PLATT SCALING (sigmoid) ─────────────────────────────────────────
print("Fitting Platt scaling (sigmoid) on val...")
try:
    platt_lr = CalibratedClassifierCV(base_lr, method='sigmoid', cv='prefit')
    platt_lr.fit(X_v_s, y_val)
except Exception:
    from sklearn.linear_model import LogisticRegression as _LR
    platt = _LR(C=1e10, max_iter=1000)
    platt.fit(base_val_p.reshape(-1, 1), y_val)
    class _PlattWrapper:
        def predict_proba(self, X):
            raw = base_lr.predict_proba(X)[:, 1]
            cal = platt.predict_proba(raw.reshape(-1, 1))[:, 1]
            return np.column_stack([1 - cal, cal])
    platt_lr = _PlattWrapper()
platt_test_p = platt_lr.predict_proba(X_te_s)[:, 1]

# ── EVALUATE ──────────────────────────────────────────────────────────────────
def eval_at(y, p, t):
    preds = (p >= t).astype(int)
    return {
        'prec': precision_score(y, preds, zero_division=0),
        'rec':  recall_score(y, preds, zero_division=0),
        'f1':   f1_score(y, preds, zero_division=0),
        'auc':  roc_auc_score(y, p),
        'ap':   average_precision_score(y, p),
        'tp': int(((preds==1)&(y==1)).sum()),
        'fp': int(((preds==1)&(y==0)).sum()),
        'fn': int(((preds==0)&(y==1)).sum()),
    }

# Find best-F1 threshold on val for each method
def best_thresh(y, p):
    thresholds = np.arange(0.05, 0.96, 0.01)
    best_t, best_f1 = 0.60, -1.0
    for t in thresholds:
        f1 = f1_score(y, (p >= t).astype(int), zero_division=0)
        if f1 > best_f1:
            best_f1, best_t = f1, t
    return best_t

base_best_t  = best_thresh(y_val, base_val_p)
cal_val_p    = cal_lr.predict_proba(X_v_s)[:, 1]
platt_val_p  = platt_lr.predict_proba(X_v_s)[:, 1]
cal_best_t   = best_thresh(y_val, cal_val_p)
platt_best_t = best_thresh(y_val, platt_val_p)

print(f"\nBest-F1 thresholds (val): base={base_best_t:.2f}  isotonic={cal_best_t:.2f}  platt={platt_best_t:.2f}")

# Evaluate all three at fixed 0.60 and at best-val-F1 threshold
print(f"\n{'='*65}")
print(f"RESULTS (test set 2023-2025)")
print(f"{'='*65}")
print(f"{'Model':<28} {'t':>5}  {'Prec':>6} {'Rec':>6} {'F1':>6} {'AUC':>6} {'AP':>6}  TP FP FN")
print(f"{'-'*65}")

for label, p, t_fixed, t_best in [
    ('Base LR',         base_test_p,  0.60, base_best_t),
    ('+ Isotonic cal',  cal_test_p,   0.60, cal_best_t),
    ('+ Platt scaling', platt_test_p, 0.60, platt_best_t),
]:
    for t_label, t in [('@0.60', 0.60), (f'@best({t_best:.2f})', t_best)]:
        m = eval_at(y_test, p, t)
        marker = '  <-- BASELINE' if label == 'Base LR' and t == 0.60 else ''
        print(f"  {label:<26} {t_label:>10}  "
              f"{m['prec']:>6.3f} {m['rec']:>6.3f} {m['f1']:>6.3f} "
              f"{m['auc']:>6.3f} {m['ap']:>6.3f}  "
              f"{m['tp']:>2} {m['fp']:>2} {m['fn']:>2}{marker}")
    print()

# ── THRESHOLD SWEEP FOR CALIBRATED MODEL ─────────────────────────────────────
print(f"{'='*65}")
print("ISOTONIC CALIBRATION -- THRESHOLD SWEEP (test)")
print(f"{'='*65}")
print(f"{'Thresh':>7}  {'Prec':>7} {'Rec':>7} {'F1':>6}  TP  FP  FN")
print(f"{'-'*50}")
for t in np.arange(0.10, 0.91, 0.05):
    m = eval_at(y_test, cal_test_p, t)
    marker = '  <-- best F1' if abs(t - cal_best_t) < 0.03 else ''
    print(f"  {t:>5.2f}  {m['prec']:>7.3f} {m['rec']:>7.3f} {m['f1']:>6.3f}  "
          f"{m['tp']:>2}  {m['fp']:>2}  {m['fn']:>2}{marker}")

# ── SUMMARY ───────────────────────────────────────────────────────────────────
b = eval_at(y_test, base_test_p,  0.60)
c = eval_at(y_test, cal_test_p,   0.60)
p = eval_at(y_test, platt_test_p, 0.60)

print(f"\n{'='*65}")
print("SUMMARY AT t=0.60")
print(f"{'='*65}")
print(f"  Base LR:         Prec={b['prec']:.3f} Rec={b['rec']:.3f} F1={b['f1']:.3f} AUC={b['auc']:.3f}")
print(f"  + Isotonic:      Prec={c['prec']:.3f} Rec={c['rec']:.3f} F1={c['f1']:.3f} AUC={c['auc']:.3f}  delta_prec={c['prec']-b['prec']:+.3f}")
print(f"  + Platt:         Prec={p['prec']:.3f} Rec={p['rec']:.3f} F1={p['f1']:.3f} AUC={p['auc']:.3f}  delta_prec={p['prec']-b['prec']:+.3f}")

best = max([('isotonic', c), ('platt', p)], key=lambda x: x[1]['prec'])
verdict = 'KEEP' if best[1]['prec'] > b['prec'] + 0.005 else 'REJECT'
print(f"\nVerdict: {verdict} -- best calibration method: {best[0]} "
      f"(delta_prec={best[1]['prec']-b['prec']:+.3f})")