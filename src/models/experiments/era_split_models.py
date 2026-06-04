"""
era_split_models.py
-------------------
Tests 6 era-split/weighting strategies to improve post-2014 precision.

Background:
  Pre-2014 bloom rate: 28.5% | Post-2014: 6.0%
  False positives concentrated in post-TMDL period due to N-depletion
  dampening blooms that CHL signal would otherwise predict.

Run from repo root:
    & "$env:USERPROFILE/anaconda3/python.exe" src/models/era_split_models.py
"""

import glob
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from io import StringIO
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_auc_score, precision_score, recall_score, f1_score,
    precision_recall_curve,
)

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
print("Loading data/hab_features_tidal.csv ...")
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
    print(f"  percent_saturation coverage: "
          f"{hab['percent_saturation'].notna().mean()*100:.1f}%")

hab['post_tmdl'] = (hab['date'].dt.year >= 2014).astype(float)

# ---------------------------------------------------------------------------
# Recompute rolling features and bloom_28d label
# ---------------------------------------------------------------------------
print("Computing rolling features and bloom_28d label ...")
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

# ---------------------------------------------------------------------------
# Base feature set
# ---------------------------------------------------------------------------
BASE = [
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
BASE = [f for f in BASE if f in hab.columns]
print(f"BASE features available: {len(BASE)}")

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def best_f1_thresh(y_true, probs):
    prec, rec, thresh = precision_recall_curve(y_true, probs)
    f1 = 2 * prec * rec / (prec + rec + 1e-9)
    idx = f1.argmax()
    return float(thresh[idx]) if idx < len(thresh) else 0.5


def eval_at(y_true, probs, threshold):
    preds = (probs >= threshold).astype(int)
    return {
        'auc':       roc_auc_score(y_true, probs),
        'precision': precision_score(y_true, preds, zero_division=0),
        'recall':    recall_score(y_true, preds, zero_division=0),
        'f1':        f1_score(y_true, preds, zero_division=0),
        'tp': int(((preds == 1) & (y_true == 1)).sum()),
        'fp': int(((preds == 1) & (y_true == 0)).sum()),
        'fn': int(((preds == 0) & (y_true == 1)).sum()),
    }


def prepare(df, features):
    """Return X, y, aligned_df for rows with non-null bloom_28d."""
    rows = df[features + ['bloom_28d', 'date']].dropna(subset=['bloom_28d']).copy()
    X = rows[features].reset_index(drop=True)
    y = rows['bloom_28d'].astype(int).values
    return X, y, rows.reset_index(drop=True)


# ---------------------------------------------------------------------------
# Experiment runner
# ---------------------------------------------------------------------------
results = []

def run_exp(exp_name, train_df, val_df, test_df, features,
            sample_weight_fn=None, warm_start_full_df=None):
    """
    Fit LR and evaluate on test at threshold 0.60 and val best-F1.

    sample_weight_fn: callable(aligned_train_df) -> 1D weight array
    warm_start_full_df: if set, stage-1 train on this, stage-2 on train_df
    """
    X_tr, y_tr, tr_rows = prepare(train_df, features)
    X_v,  y_v,  _       = prepare(val_df,   features)
    X_te, y_te, _       = prepare(test_df,  features)

    # Scaler and median always based on the primary (possibly post-TMDL) train
    med = X_tr.median()

    scaler = StandardScaler()
    X_tr_s = scaler.fit_transform(X_tr.fillna(med))
    X_v_s  = scaler.transform(X_v.fillna(med))
    X_te_s = scaler.transform(X_te.fillna(med))

    lr = LogisticRegression(C=0.05, class_weight='balanced',
                            max_iter=2000, random_state=42)

    if warm_start_full_df is not None:
        # Stage 1: fit on full data using same scaler/median (re-scaled)
        X_ws, y_ws, _ = prepare(warm_start_full_df, features)
        med_ws = X_ws.median()
        scaler_ws = StandardScaler()
        X_ws_s = scaler_ws.fit_transform(X_ws.fillna(med_ws))
        X_v_s2  = scaler_ws.transform(X_v.fillna(med_ws))
        X_te_s2 = scaler_ws.transform(X_te.fillna(med_ws))

        # Stage 2 train (post-2014) scaled with same scaler as stage 1
        X_tr_s2 = scaler_ws.transform(X_tr.fillna(med_ws))

        lr_ws = LogisticRegression(C=0.05, class_weight='balanced',
                                   warm_start=True, max_iter=2000, random_state=42)
        lr_ws.fit(X_ws_s, y_ws)       # stage 1: full 1993-2019
        lr_ws.fit(X_tr_s2, y_tr)      # stage 2: post-2014 (warm start)

        p_v  = lr_ws.predict_proba(X_v_s2)[:, 1]
        p_te = lr_ws.predict_proba(X_te_s2)[:, 1]
    else:
        sw = sample_weight_fn(tr_rows) if sample_weight_fn else None
        lr.fit(X_tr_s, y_tr, sample_weight=sw)
        p_v  = lr.predict_proba(X_v_s)[:, 1]
        p_te = lr.predict_proba(X_te_s)[:, 1]

    val_thresh = best_f1_thresh(y_v, p_v)
    m60 = eval_at(y_te, p_te, 0.60)
    m_vt = eval_at(y_te, p_te, val_thresh)

    n_train    = len(y_tr)
    bloom_rate = y_tr.mean() * 100

    flag = ''
    if (m60['f1'] > 0.455 or m60['precision'] > 0.465) and m60['recall'] >= 0.35:
        flag = '  *** BEATS BASELINE ***'

    print(f"\n[{exp_name}]")
    print(f"  N_train={n_train:,}  bloom_rate={bloom_rate:.1f}%  "
          f"val_thresh={val_thresh:.3f}")
    print(f"  @0.60:  Prec={m60['precision']:.3f}  Rec={m60['recall']:.3f}  "
          f"F1={m60['f1']:.3f}  AUC={m60['auc']:.4f}  "
          f"TP={m60['tp']} FP={m60['fp']} FN={m60['fn']}{flag}")
    print(f"  @val:   Prec={m_vt['precision']:.3f}  Rec={m_vt['recall']:.3f}  "
          f"F1={m_vt['f1']:.3f}  thresh={val_thresh:.3f}")

    results.append({
        'experiment':  exp_name,
        'n_train':     n_train,
        'bloom_rate':  bloom_rate,
        'val_thresh':  val_thresh,
        'auc':         m60['auc'],
        'precision':   m60['precision'],
        'recall':      m60['recall'],
        'f1':          m60['f1'],
        'tp':          m60['tp'],
        'fp':          m60['fp'],
        'fn':          m60['fn'],
        'flag':        flag.strip(),
    })


# ---------------------------------------------------------------------------
# Define splits
# ---------------------------------------------------------------------------
train_std  = hab[hab['date'].dt.year <= 2019]
val_std    = hab[(hab['date'].dt.year >= 2020) & (hab['date'].dt.year <= 2022)]
test_std   = hab[hab['date'].dt.year >= 2023]
train_post = hab[(hab['date'].dt.year >= 2014) & (hab['date'].dt.year <= 2019)]
train_pre  = hab[hab['date'].dt.year <= 2013]
val_pre    = hab[(hab['date'].dt.year >= 2014) & (hab['date'].dt.year <= 2016)]

# ---------------------------------------------------------------------------
# Run all 6 experiments
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("Running 6 era-split experiments")
print("=" * 70)

# Exp 1: Baseline
run_exp('Baseline (1993-2019)', train_std, val_std, test_std, BASE)

# Exp 2: Post-TMDL only
run_exp('Post-TMDL only (2014-2019)', train_post, val_std, test_std, BASE)

# Exp 3: Pre-TMDL only (val uses 2014-2016, first OOT period)
run_exp('Pre-TMDL only (1993-2013)', train_pre, val_pre, test_std, BASE)

# Exp 4: Mixed + post_tmdl binary feature
BASE_TMDL = BASE + ['post_tmdl']
run_exp('Mixed + post_tmdl feature', train_std, val_std, test_std, BASE_TMDL)

# Exp 5: Sample-weighted (post-2014 rows get 3x weight)
run_exp(
    'Sample-weighted (3x post)',
    train_std, val_std, test_std, BASE,
    sample_weight_fn=lambda rows: np.where(rows['date'].dt.year >= 2014, 3.0, 1.0),
)

# Exp 6: Two-stage warm start (stage 1: full 1993-2019, stage 2: 2014-2019)
run_exp(
    'Two-stage warm start',
    train_post, val_std, test_std, BASE,
    warm_start_full_df=train_std,
)

# ---------------------------------------------------------------------------
# Summary table
# ---------------------------------------------------------------------------
print("\n\n" + "=" * 100)
print("RESULTS TABLE — sorted by F1@0.60")
print("=" * 100)
hdr = (f"{'Experiment':<33}  {'N_train':>8}  {'BloomRate':>9}  "
       f"{'AUC':>6}  {'Prec@.60':>9}  {'Rec@.60':>8}  "
       f"{'F1@.60':>7}  {'TP':>4}  {'FP':>4}  {'FN':>4}")
print(hdr)
print("-" * 100)

results_sorted = sorted(results, key=lambda r: r['f1'], reverse=True)
for r in results_sorted:
    flag_str = '  <--' if r['flag'] else ''
    print(
        f"{r['experiment']:<33}  {r['n_train']:>8,}  {r['bloom_rate']:>8.1f}%  "
        f"{r['auc']:>6.3f}  {r['precision']:>9.3f}  {r['recall']:>8.3f}  "
        f"{r['f1']:>7.3f}  {r['tp']:>4}  {r['fp']:>4}  {r['fn']:>4}"
        f"{flag_str}"
    )

print("\n")
print("Baseline reference: Prec=0.465  Rec=0.446  F1=0.455  AUC=0.814")
print("Flag criteria: F1 > 0.455 OR Precision > 0.465, with Recall >= 0.35")

winners = [r for r in results if r['flag']]
if winners:
    print(f"\nWINNERS ({len(winners)}):")
    for r in winners:
        print(f"  {r['experiment']}: Prec={r['precision']:.3f}  "
              f"Rec={r['recall']:.3f}  F1={r['f1']:.3f}")
else:
    print("\nNo experiment beats baseline. Era-split strategies exhausted.")
