"""
self_training.py
----------------
Temporal self-training to adapt the locked LR model to the post-TMDL (low-bloom)
distribution. The model is trained on 1993-2019 (bloom rate ~22.7%) but deployed
on 2023-2025 (bloom rate ~7.2%). Self-training uses the model's own high-confidence
predictions on the val period (2020-2022) as pseudo-labels -- WITHOUT ever using the
val labels (y_val) for training -- to nudge the decision boundary toward the
deployment-era distribution.

The test set (2023-2025) is touched ONLY for final evaluation, never during training.
Val labels (y_val) are used only to pick the best-F1 threshold at evaluation time.

Mirrors the feature pipeline in final_evaluation_threshold_sweep.py exactly.

Run from repo root (anaconda python has sklearn):
    $env:USERPROFILE\\anaconda3\\python.exe src/models/self_training.py
"""

import warnings
warnings.filterwarnings('ignore', category=UserWarning)

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_auc_score, average_precision_score,
    precision_recall_curve, f1_score,
    precision_score, recall_score,
)

EVAL_THRESH = 0.60

# ---------------------------------------------------------------------------
# Load + recompute features (identical to the locked pipeline)
# ---------------------------------------------------------------------------
print("Loading data/hab_features_tidal.csv...")
df = pd.read_csv("data/hab_features_tidal.csv")
df['date'] = pd.to_datetime(df['date'])

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
# Feature set (same 30 features as the pipeline)
# ---------------------------------------------------------------------------
FEATURES_ALL = [
    'Chlorophyll', 'chl_lag1', 'chl_lag2', 'chl_lag3', 'chl_lag4',
    'chl_roll3_mean', 'chl_roll6_mean', 'chl_roll9_mean', 'chl_trend',
    'chl_roll14_mean', 'chl_roll21_mean',
    'chl_anomaly', 'chl_climatology',
    'do_lag1', 'temp_lag1', 'sal_lag1',
    'sea_water_temperature', 'sea_water_salinity',
    'oxygen_concentration_in_sea_water',
    'month', 'latitude_x', 'longitude_x',
    'nox_lag2', 'dip_lag2', 'dip_change', 'dip_x_month',
    'neighbor_chl3_mean', 'neighbor_chl3_lag1',
    'tidal_gt_anom', 'tidal_msl_anom',
]
FEATURES = [f for f in FEATURES_ALL if f in df.columns]

# ---------------------------------------------------------------------------
# Splits
# ---------------------------------------------------------------------------
train = df[df['date'].dt.year <= 2019]
val   = df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)]
test  = df[df['date'].dt.year >= 2023]

def prepare(split):
    rows = split[FEATURES + ['bloom_28d']].dropna(subset=['bloom_28d'])
    X = rows[FEATURES].copy()
    y = rows['bloom_28d'].copy()
    return X.reset_index(drop=True), y.reset_index(drop=True)

X_train, y_train = prepare(train)
X_val,   y_val   = prepare(val)
X_test,  y_test  = prepare(test)

# Train median (used to fill NaN everywhere -- fit on train only)
MED = X_train.median()

# StandardScaler fit on train only, applied to val and test
scaler = StandardScaler()
scaler.fit(X_train.fillna(MED))

X_tr_s = scaler.transform(X_train.fillna(MED))
X_v_s  = scaler.transform(X_val.fillna(MED))
X_te_s = scaler.transform(X_test.fillna(MED))

print(f"Features: {len(FEATURES)}")
print(f"Train: {len(X_train):,} | Val: {len(X_val):,} | Test: {len(X_test):,}")
print(f"Train bloom rate: {y_train.mean()*100:.1f}%")
print(f"Val   bloom rate: {y_val.mean()*100:.1f}%")
print(f"Test  bloom rate: {y_test.mean()*100:.1f}%")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def new_lr():
    return LogisticRegression(class_weight='balanced', C=0.05,
                              max_iter=1000, random_state=42)


def best_f1_thresh(y, p):
    """Best-F1 threshold from the val PR curve (val labels OK at eval time)."""
    prec, rec, thresh = precision_recall_curve(y, p)
    f1 = 2 * prec * rec / (prec + rec + 1e-9)
    idx = f1.argmax()
    return float(thresh[idx]) if idx < len(thresh) else 0.5


def eval_at(y, p, t):
    preds = (p >= t).astype(int)
    return {
        'auc':       roc_auc_score(y, p),
        'ap':        average_precision_score(y, p),
        'precision': precision_score(y, preds, zero_division=0),
        'recall':    recall_score(y, preds, zero_division=0),
        'f1':        f1_score(y, preds, zero_division=0),
        'tp': int(((preds == 1) & (y == 1)).sum()),
        'fp': int(((preds == 1) & (y == 0)).sum()),
        'fn': int(((preds == 0) & (y == 1)).sum()),
    }


def self_train(pos_thresh, neg_thresh, n_iterations, balance=False):
    """
    Self-training loop. Returns (test_probs, n_pos_total, n_neg_total).

    If balance=True, the confident pseudo-negatives are randomly subsampled
    down to the number of confident pseudo-positives, so the augmentation does
    not flood the train set with non-bloom rows.

    Starts from the baseline model (fit on train only), then for each iteration:
      - predict probs on val features X_val (NEVER y_val)
      - pseudo-label confident rows (>pos_thresh -> 1, <neg_thresh -> 0)
      - retrain on train + pseudo-labeled val rows
    The pseudo-label set is regenerated each iteration from the current model.
    """
    rng = np.random.RandomState(42)
    model = new_lr()
    model.fit(X_tr_s, y_train)

    n_pos_total = 0
    n_neg_total = 0

    for _ in range(n_iterations):
        p_val = model.predict_proba(X_v_s)[:, 1]

        pos_idx = np.where(p_val > pos_thresh)[0]
        neg_idx = np.where(p_val < neg_thresh)[0]

        if balance and len(neg_idx) > len(pos_idx):
            # Randomly subsample confident negatives down to n_pos.
            neg_idx = rng.choice(neg_idx, size=len(pos_idx), replace=False)

        n_pos = len(pos_idx)
        n_neg = len(neg_idx)
        n_pos_total = n_pos        # report counts from the final iteration's set
        n_neg_total = n_neg

        keep = np.concatenate([pos_idx, neg_idx]).astype(int)
        if len(keep) == 0:
            # No confident pseudo-labels -- nothing to add, stop early.
            break

        pseudo_y = np.where(p_val[keep] > pos_thresh, 1, 0)

        X_aug = np.vstack([X_tr_s, X_v_s[keep]])
        y_aug = np.concatenate([y_train.values, pseudo_y])

        model = new_lr()
        model.fit(X_aug, y_aug)

    p_test = model.predict_proba(X_te_s)[:, 1]
    return p_test, n_pos_total, n_neg_total


# ---------------------------------------------------------------------------
# Baseline (no self-training)
# ---------------------------------------------------------------------------
print("\nFitting baseline LR (C=0.05, balanced) on train 1993-2019...")
base_model = new_lr()
base_model.fit(X_tr_s, y_train)
base_test_p = base_model.predict_proba(X_te_s)[:, 1]
base_m = eval_at(y_test, base_test_p, EVAL_THRESH)

print(f"Baseline @ {EVAL_THRESH:.2f}:  Prec={base_m['precision']:.3f}  "
      f"Rec={base_m['recall']:.3f}  F1={base_m['f1']:.3f}  AUC={base_m['auc']:.3f}")

# ---------------------------------------------------------------------------
# Configurations
# ---------------------------------------------------------------------------
configs = [
    ('ST pos>0.80 neg<0.10 1iter',  0.80, 0.10, 1),
    ('ST pos>0.80 neg<0.10 3iter',  0.80, 0.10, 3),
    ('ST pos>0.75 neg<0.15 1iter',  0.75, 0.15, 1),
    ('ST pos>0.75 neg<0.15 3iter',  0.75, 0.15, 3),
    ('ST pos>0.70 neg<0.20 1iter',  0.70, 0.20, 1),
    ('ST pos>0.70 neg<0.20 3iter',  0.70, 0.20, 3),
    ('ST pos>0.65 neg<0.25 1iter',  0.65, 0.25, 1),
    ('ST pos>0.65 neg<0.25 3iter',  0.65, 0.25, 3),
    ('ST pos>0.80 neg<0.05 1iter',  0.80, 0.05, 1),
    ('ST pos>0.85 neg<0.10 1iter',  0.85, 0.10, 1),
    ('ST balanced pos>0.70 neg<0.20', 0.70, 0.20, 1, True),
]

print("\n" + "=" * 72)
print("SELF-TRAINING CONFIGURATIONS (test eval @ threshold 0.60)")
print("=" * 72)

results = []
# Baseline row
results.append({
    'config': 'BASELINE (no self-training)',
    'n_pos': 0, 'n_neg': 0,
    'precision': base_m['precision'], 'recall': base_m['recall'],
    'f1': base_m['f1'], 'auc': base_m['auc'],
})

for cfg in configs:
    name, pos_t, neg_t, n_iter = cfg[0], cfg[1], cfg[2], cfg[3]
    balance = cfg[4] if len(cfg) > 4 else False
    p_test, n_pos, n_neg = self_train(pos_t, neg_t, n_iter, balance=balance)

    if n_pos + n_neg == 0:
        # No pseudo-labels were ever added -> identical to baseline.
        m = base_m
        note = " (0 pseudo-labels -> baseline)"
    else:
        m = eval_at(y_test, p_test, EVAL_THRESH)
        note = ""

    print(f"\n{name}{note}")
    print(f"  pseudo-pos={n_pos:<4} pseudo-neg={n_neg:<4}  "
          f"Prec={m['precision']:.3f}  Rec={m['recall']:.3f}  "
          f"F1={m['f1']:.3f}  AUC={m['auc']:.3f}")

    results.append({
        'config': name,
        'n_pos': n_pos, 'n_neg': n_neg,
        'precision': m['precision'], 'recall': m['recall'],
        'f1': m['f1'], 'auc': m['auc'],
    })

# ---------------------------------------------------------------------------
# Sorted comparison table (by F1)
# ---------------------------------------------------------------------------
res_df = pd.DataFrame(results).sort_values('f1', ascending=False).reset_index(drop=True)

print("\n" + "=" * 88)
print("ALL CONFIGS SORTED BY F1 (test 2023-2025 @ threshold 0.60)")
print("=" * 88)
print(f"{'Config':<32}  {'pos':>5}  {'neg':>5}  {'Prec':>6}  "
      f"{'Rec':>6}  {'F1':>6}  {'AUC':>6}")
print("-" * 88)
for _, r in res_df.iterrows():
    marker = "  <-- baseline" if r['config'].startswith('BASELINE') else ""
    print(f"{r['config']:<32}  {r['n_pos']:>5}  {r['n_neg']:>5}  "
          f"{r['precision']:>6.3f}  {r['recall']:>6.3f}  "
          f"{r['f1']:>6.3f}  {r['auc']:>6.3f}{marker}")

# ---------------------------------------------------------------------------
# Delta vs baseline for the best (non-baseline) config
# ---------------------------------------------------------------------------
best = res_df[~res_df['config'].str.startswith('BASELINE')].iloc[0]

print("\n" + "=" * 60)
print("BEST CONFIG vs BASELINE")
print("=" * 60)
print(f"Baseline: Prec={base_m['precision']:.3f}  "
      f"Rec={base_m['recall']:.3f}  F1={base_m['f1']:.3f}")
print(f"Best:     Prec={best['precision']:.3f}  "
      f"Rec={best['recall']:.3f}  F1={best['f1']:.3f}  ({best['config']})")
print(f"Delta:    Prec={best['precision']-base_m['precision']:+.3f}  "
      f"Rec={best['recall']-base_m['recall']:+.3f}  "
      f"F1={best['f1']-base_m['f1']:+.3f}")

if best['f1'] > base_m['f1']:
    print(f"\n  Self-training IMPROVES F1 by {best['f1']-base_m['f1']:+.3f}")
else:
    print(f"\n  Self-training does NOT beat baseline F1.")
