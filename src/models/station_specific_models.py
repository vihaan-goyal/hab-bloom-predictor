r"""
station_specific_models.py
--------------------------
Trains and evaluates per-station LR models for the highest-priority western
LIS stations (A4, B3, C1, 01, 02). These stations have local bloom rates of
17-33% versus the 7.2% global test rate, which makes precision far more
tractable than the global model achieves.

Two strategies are compared per station:

  Strategy A -- station-only model
    Fit LR on ONLY that station's data (1993-2019), pick the best-F1 threshold
    on that station's val data (2020-2022), evaluate on its test data (2023+).

  Strategy B -- global model + station threshold
    Use the global LR model (trained on ALL stations 1993-2019, identical to
    final_evaluation_threshold_sweep.py / the daily-inference pipeline), find
    the best-F1 threshold for THIS station on its val data, apply it to its
    test data.

Key question: does any western station reach precision > 0.50 with recall
> 0.40?

Run from repo root:
    & "$env:USERPROFILE\anaconda3\python.exe" src/models/station_specific_models.py
"""

import warnings
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=RuntimeWarning)

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_auc_score, f1_score, precision_score, recall_score,
)

WESTERN_STATIONS = ['A4', 'B3', 'C1', '01', '02']
MIN_TEST_BLOOMS = 3
FIXED_THRESH = 0.60

# ---------------------------------------------------------------------------
# 1. Load + merge sal_lag2/3/4
# ---------------------------------------------------------------------------
print("Loading data/hab_features_tidal.csv...")
df = pd.read_csv('data/hab_features_tidal.csv')
df['date'] = pd.to_datetime(df['date'])

# sal_lag2/3/4 live in hab_features_daily.csv. The current tidal CSV already
# carries them (added in commit ce9d02c), so we only merge any that are
# genuinely absent -- merging present columns would create _x/_y suffixes and
# silently drop them from the feature set, breaking the match with the
# pipeline's global model.
need = [c for c in ['sal_lag2', 'sal_lag3', 'sal_lag4'] if c not in df.columns]
if need:
    print(f"  Merging missing columns from hab_features_daily.csv: {need}")
    hab_daily = pd.read_csv('data/hab_features_daily.csv')[
        ['date', 'station_name'] + need
    ]
    hab_daily['date'] = pd.to_datetime(hab_daily['date'])
    df = df.merge(hab_daily, on=['date', 'station_name'], how='left')
else:
    print("  sal_lag2/3/4 already present in tidal CSV (no merge needed).")

print("Merging max_gust_3d from data/gust_features_daily.csv...")
gust = pd.read_csv('data/gust_features_daily.csv', usecols=['date', 'max_gust_3d'])
gust['date'] = pd.to_datetime(gust['date'])
df = df.merge(gust, on='date', how='left')
print(f"  max_gust_3d coverage: {df['max_gust_3d'].notna().mean() * 100:.1f}%")

# ---------------------------------------------------------------------------
# 2. Recompute rolling means + bloom_28d label (identical to all pipeline scripts)
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# 3. Feature set (same as pipeline)
# ---------------------------------------------------------------------------
FEATURES_ALL = [
    'Chlorophyll', 'chl_lag1', 'chl_lag2', 'chl_lag3', 'chl_lag4',
    'chl_roll3_mean', 'chl_roll6_mean', 'chl_roll9_mean', 'chl_trend',
    'chl_roll14_mean', 'chl_roll21_mean',
    'chl_anomaly', 'chl_climatology',
    'do_lag1', 'temp_lag1', 'sal_lag1', 'sal_lag2', 'sal_lag3', 'sal_lag4',
    'sea_water_temperature', 'sea_water_salinity',
    'oxygen_concentration_in_sea_water',
    'month', 'latitude_x', 'longitude_x',
    'nox_lag2', 'dip_lag2', 'dip_change', 'dip_x_month',
    'neighbor_chl3_mean', 'neighbor_chl3_lag1',
    'tidal_gt_anom', 'tidal_msl_anom',
    'max_gust_3d',
]
FEATURES = [f for f in FEATURES_ALL if f in df.columns]
missing = [f for f in FEATURES_ALL if f not in df.columns]
if missing:
    print(f"  WARNING: features absent from data, dropped: {missing}")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def prepare(split):
    """Drop rows with no label; fill features with train medians is done later."""
    rows = split[FEATURES + ['bloom_28d']].dropna(subset=['bloom_28d'])
    X = rows[FEATURES].copy().reset_index(drop=True)
    y = rows['bloom_28d'].copy().reset_index(drop=True)
    return X, y


def best_f1_threshold(y, p):
    """Sweep thresholds on a grid and return the one maximizing F1.

    Uses a fine grid rather than precision_recall_curve so small per-station
    val sets behave predictably. Returns FIXED_THRESH if y has only one class.
    """
    if y.nunique() < 2:
        return FIXED_THRESH
    grid = np.arange(0.05, 0.951, 0.01)
    best_t, best_f1 = FIXED_THRESH, -1.0
    for t in grid:
        f1 = f1_score(y, (p >= t).astype(int), zero_division=0)
        if f1 > best_f1:
            best_f1, best_t = f1, float(t)
    return best_t


def eval_at(y, p, t):
    preds = (p >= t).astype(int)
    out = {
        'precision': precision_score(y, preds, zero_division=0),
        'recall':    recall_score(y, preds, zero_division=0),
        'f1':        f1_score(y, preds, zero_division=0),
        'tp': int(((preds == 1) & (y == 1)).sum()),
        'fp': int(((preds == 1) & (y == 0)).sum()),
        'fn': int(((preds == 0) & (y == 1)).sum()),
        'tn': int(((preds == 0) & (y == 0)).sum()),
    }
    try:
        out['auc'] = roc_auc_score(y, p) if y.nunique() >= 2 else float('nan')
    except ValueError:
        out['auc'] = float('nan')
    return out

# ---------------------------------------------------------------------------
# 4. Global splits + global model (identical to the pipeline)
# ---------------------------------------------------------------------------
train = df[df['date'].dt.year <= 2019]
val   = df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)]
test  = df[df['date'].dt.year >= 2023]

Xg_tr, yg_tr = prepare(train)
GLOBAL_MED = Xg_tr.median()

global_scaler = StandardScaler()
Xg_tr_s = global_scaler.fit_transform(Xg_tr.fillna(GLOBAL_MED))
global_model = LogisticRegression(class_weight='balanced', C=0.05,
                                  max_iter=1000, random_state=42)
global_model.fit(Xg_tr_s, yg_tr)


def global_probs(split_df):
    """Global-model P(bloom) for an arbitrary subset, with aligned labels.

    Mirrors the pipeline exactly: same FEATURES, same train medians, same
    fitted scaler + model.
    """
    X, y = prepare(split_df)
    if len(X) == 0:
        return np.array([]), y
    p = global_model.predict_proba(global_scaler.transform(X.fillna(GLOBAL_MED)))[:, 1]
    return p, y


# Pipeline sanity check: global test AUC should match final_evaluation_threshold_sweep
_p_te_all, _y_te_all = global_probs(test)
print(f"Global model fitted on {len(Xg_tr):,} train rows "
      f"({yg_tr.mean()*100:.1f}% bloom). "
      f"Global test AUC = {roc_auc_score(_y_te_all, _p_te_all):.4f} "
      f"(pipeline reference ~0.814).")

# ---------------------------------------------------------------------------
# 5. Per-station evaluation
# ---------------------------------------------------------------------------
# Accumulators for the combined summary across the western stations.
combg_p, combg_y = [], []           # global model, western subset
combA_pred, combA_y = [], []        # strategy A pooled predictions
combB_pred, combB_y = [], []        # strategy B pooled predictions

per_station = {}

for station in WESTERN_STATIONS:
    print("\n" + "=" * 72)
    print(f"STATION {station}")
    print("=" * 72)

    stn = df[df['station_name'] == station]
    train_s = stn[stn['date'].dt.year <= 2019]
    val_s   = stn[(stn['date'].dt.year >= 2020) & (stn['date'].dt.year <= 2022)]
    test_s  = stn[stn['date'].dt.year >= 2023]

    XAtr, yAtr = prepare(train_s)
    XAv,  yAv  = prepare(val_s)
    XAte, yAte = prepare(test_s)

    print(f"  train: {len(yAtr):>4} rows, bloom {yAtr.mean()*100:>5.1f}% "
          f"({int(yAtr.sum())} events)")
    print(f"  val:   {len(yAv):>4} rows, bloom "
          f"{(yAv.mean()*100 if len(yAv) else 0):>5.1f}% ({int(yAv.sum())} events)")
    print(f"  test:  {len(yAte):>4} rows, bloom "
          f"{(yAte.mean()*100 if len(yAte) else 0):>5.1f}% ({int(yAte.sum())} events)")

    if int(yAte.sum()) < MIN_TEST_BLOOMS:
        print(f"  [SKIP] fewer than {MIN_TEST_BLOOMS} test bloom events.")
        continue
    if yAtr.nunique() < 2:
        print("  [SKIP] station train data has only one class.")
        continue

    # ---- Strategy A: station-only model --------------------------------
    medA = XAtr.median()
    scA = StandardScaler()
    lrA = LogisticRegression(class_weight='balanced', C=0.05,
                             max_iter=2000, random_state=42)
    lrA.fit(scA.fit_transform(XAtr.fillna(medA)), yAtr)

    pA_v  = (lrA.predict_proba(scA.transform(XAv.fillna(medA)))[:, 1]
             if len(XAv) else np.array([]))
    pA_te = lrA.predict_proba(scA.transform(XAte.fillna(medA)))[:, 1]

    tA = best_f1_threshold(yAv, pA_v) if len(yAv) else FIXED_THRESH
    A_best = eval_at(yAte, pA_te, tA)
    A_60   = eval_at(yAte, pA_te, FIXED_THRESH)

    print(f"\n  Strategy A (station-only model):")
    print(f"    best-val-F1 threshold = {tA:.2f}")
    print(f"    @best : P={A_best['precision']:.3f} R={A_best['recall']:.3f} "
          f"F1={A_best['f1']:.3f} AUC={A_best['auc']:.3f} "
          f"(TP={A_best['tp']} FP={A_best['fp']} FN={A_best['fn']})")
    print(f"    @0.60 : P={A_60['precision']:.3f} R={A_60['recall']:.3f} "
          f"F1={A_60['f1']:.3f} "
          f"(TP={A_60['tp']} FP={A_60['fp']} FN={A_60['fn']})")

    # ---- Strategy B: global model + station threshold ------------------
    pB_v,  yB_v  = global_probs(val_s)
    pB_te, yB_te = global_probs(test_s)

    tB = best_f1_threshold(yB_v, pB_v) if len(yB_v) else FIXED_THRESH
    B_best = eval_at(yB_te, pB_te, tB)
    B_60   = eval_at(yB_te, pB_te, FIXED_THRESH)

    print(f"\n  Strategy B (global model + station threshold):")
    print(f"    best-val-F1 threshold = {tB:.2f}")
    print(f"    @best : P={B_best['precision']:.3f} R={B_best['recall']:.3f} "
          f"F1={B_best['f1']:.3f} AUC={B_best['auc']:.3f} "
          f"(TP={B_best['tp']} FP={B_best['fp']} FN={B_best['fn']})")
    print(f"    @0.60 : P={B_60['precision']:.3f} R={B_60['recall']:.3f} "
          f"F1={B_60['f1']:.3f} "
          f"(TP={B_60['tp']} FP={B_60['fp']} FN={B_60['fn']})")

    # ---- Accumulate for combined summary -------------------------------
    combg_p.extend(pB_te.tolist())          # global probs on western test
    combg_y.extend(yB_te.tolist())
    combA_pred.extend((pA_te >= tA).astype(int).tolist())
    combA_y.extend(yAte.tolist())
    combB_pred.extend((pB_te >= tB).astype(int).tolist())
    combB_y.extend(yB_te.tolist())

    per_station[station] = {
        'A_best': A_best, 'A_60': A_60, 'tA': tA,
        'B_best': B_best, 'B_60': B_60, 'tB': tB,
        'test_rate': yAte.mean(),
    }

# ---------------------------------------------------------------------------
# 5b. Persist Strategy B thresholds into data/station_thresholds.csv
# ---------------------------------------------------------------------------
# Strategy B (global model + per-station threshold) is the operationally
# recommended approach: it keeps the well-calibrated global probabilities and
# only tunes the decision threshold per station. We merge those thresholds into
# the existing station_thresholds.csv, updating only the western rows and
# preserving every other station's fallback threshold.
THRESH_CSV = 'data/station_thresholds.csv'
try:
    thr_tbl = pd.read_csv(THRESH_CSV, dtype={'station': str})
except FileNotFoundError:
    thr_tbl = pd.DataFrame(columns=['station', 'threshold'])

thr_map = dict(zip(thr_tbl['station'], thr_tbl['threshold']))
updated = []
for st in WESTERN_STATIONS:
    if st in per_station:
        thr_map[st] = round(per_station[st]['tB'], 4)
        updated.append(st)

out_tbl = (pd.DataFrame({'station': list(thr_map.keys()),
                         'threshold': list(thr_map.values())})
           .sort_values('station')
           .reset_index(drop=True))
out_tbl.to_csv(THRESH_CSV, index=False)
print(f"\nUpdated {THRESH_CSV}: Strategy B thresholds written for {updated} "
      f"({len(out_tbl)} stations total).")

# ---------------------------------------------------------------------------
# 6. Per-station precision/recall grid (the key question)
# ---------------------------------------------------------------------------
print("\n" + "=" * 72)
print("PER-STATION SUMMARY  (test 2023-2025)")
print("=" * 72)
print(f"{'Stn':>4} {'rate%':>6} | "
      f"{'A_t':>4} {'A_P@t':>6} {'A_R@t':>6} {'A_F1':>5} {'A_P@60':>7} {'A_R@60':>7} | "
      f"{'B_t':>4} {'B_P@t':>6} {'B_R@t':>6} {'B_F1':>5} {'B_P@60':>7} {'B_R@60':>7}")
print("-" * 110)
for st in WESTERN_STATIONS:
    if st not in per_station:
        print(f"{st:>4} {'--':>6} | (skipped)")
        continue
    r = per_station[st]
    print(f"{st:>4} {r['test_rate']*100:>6.1f} | "
          f"{r['tA']:>4.2f} {r['A_best']['precision']:>6.3f} {r['A_best']['recall']:>6.3f} "
          f"{r['A_best']['f1']:>5.3f} {r['A_60']['precision']:>7.3f} {r['A_60']['recall']:>7.3f} | "
          f"{r['tB']:>4.2f} {r['B_best']['precision']:>6.3f} {r['B_best']['recall']:>6.3f} "
          f"{r['B_best']['f1']:>5.3f} {r['B_60']['precision']:>7.3f} {r['B_60']['recall']:>7.3f}")

# ---------------------------------------------------------------------------
# 7. Combined comparison across western stations
# ---------------------------------------------------------------------------
combg_p = np.array(combg_p); combg_y = np.array(combg_y)
combA_pred = np.array(combA_pred); combA_y = np.array(combA_y)
combB_pred = np.array(combB_pred); combB_y = np.array(combB_y)


def combined_from_preds(y, preds):
    return {
        'precision': precision_score(y, preds, zero_division=0),
        'recall':    recall_score(y, preds, zero_division=0),
        'f1':        f1_score(y, preds, zero_division=0),
        'tp': int(((preds == 1) & (y == 1)).sum()),
        'fp': int(((preds == 1) & (y == 0)).sum()),
        'fn': int(((preds == 0) & (y == 1)).sum()),
    }


# Global model on the western subset, evaluated at the fixed 0.60 threshold.
g_60 = combined_from_preds(combg_y, (combg_p >= FIXED_THRESH).astype(int))
g_60['auc'] = roc_auc_score(combg_y, combg_p) if len(set(combg_y)) >= 2 else float('nan')
A_comb = combined_from_preds(combA_y, combA_pred)   # pooled station thresholds
B_comb = combined_from_preds(combB_y, combB_pred)   # pooled station thresholds

print("\n" + "=" * 72)
print("COMBINED ACROSS WESTERN STATIONS  (pooled test rows)")
print("=" * 72)
print(f"{'Approach':<42} {'Prec':>6} {'Rec':>6} {'F1':>6} {'TP':>4} {'FP':>4} {'FN':>4}")
print("-" * 72)
print(f"{'Global model @0.60 (western subset)':<42} "
      f"{g_60['precision']:>6.3f} {g_60['recall']:>6.3f} {g_60['f1']:>6.3f} "
      f"{g_60['tp']:>4} {g_60['fp']:>4} {g_60['fn']:>4}")
print(f"{'Strategy A: station-only @ station-best t':<42} "
      f"{A_comb['precision']:>6.3f} {A_comb['recall']:>6.3f} {A_comb['f1']:>6.3f} "
      f"{A_comb['tp']:>4} {A_comb['fp']:>4} {A_comb['fn']:>4}")
print(f"{'Strategy B: global + station-best t':<42} "
      f"{B_comb['precision']:>6.3f} {B_comb['recall']:>6.3f} {B_comb['f1']:>6.3f} "
      f"{B_comb['tp']:>4} {B_comb['fp']:>4} {B_comb['fn']:>4}")

# ---------------------------------------------------------------------------
# 8. Answer the key question
# ---------------------------------------------------------------------------
print("\n" + "=" * 72)
print("KEY QUESTION: precision > 0.50 AND recall > 0.40 at any western station?")
print("=" * 72)
hits = []
for st in WESTERN_STATIONS:
    if st not in per_station:
        continue
    r = per_station[st]
    for strat, key in [('A@best', 'A_best'), ('A@0.60', 'A_60'),
                       ('B@best', 'B_best'), ('B@0.60', 'B_60')]:
        m = r[key]
        if m['precision'] > 0.50 and m['recall'] > 0.40:
            hits.append((st, strat, m['precision'], m['recall'], m['f1']))

if hits:
    for st, strat, p, rec, f1 in hits:
        print(f"  YES -- {st} {strat}: P={p:.3f} R={rec:.3f} F1={f1:.3f}")
else:
    print("  No station/strategy combination clears P>0.50 with R>0.40.")
    print("  Closest by precision (R>0.40):")
    cand = []
    for st in WESTERN_STATIONS:
        if st not in per_station:
            continue
        r = per_station[st]
        for strat, key in [('A@best', 'A_best'), ('A@0.60', 'A_60'),
                           ('B@best', 'B_best'), ('B@0.60', 'B_60')]:
            m = r[key]
            if m['recall'] > 0.40:
                cand.append((m['precision'], st, strat, m['recall'], m['f1']))
    for p, st, strat, rec, f1 in sorted(cand, reverse=True)[:5]:
        print(f"    {st} {strat}: P={p:.3f} R={rec:.3f} F1={f1:.3f}")
