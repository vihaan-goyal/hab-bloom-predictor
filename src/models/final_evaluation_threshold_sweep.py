import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.metrics import (roc_auc_score, average_precision_score,
                             classification_report, confusion_matrix,
                             precision_recall_curve, f1_score,
                             precision_score, recall_score)
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

print("Loading data...")
df = pd.read_csv("data/hab_features_final.csv", low_memory=False)
df['date'] = pd.to_datetime(df['date'])
df['bloom_7d_ahead'] = df.groupby('station_name')['bloom'].shift(-7)

features = [
    'latitude', 'longitude', 'month',
    'chl_anomaly', 'chl_climatology',
    'chl_roll7_mean', 'chl_roll7_std',
    'chl_lag3', 'chl_lag7', 'chl_lag14', 'chl_lag21',
]

train = df[df['date'].dt.year <= 2019]
val = df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)]
test = df[df['date'].dt.year >= 2023]

def prepare(split):
    X = split[features + ['bloom_7d_ahead']].dropna()
    y = X.pop('bloom_7d_ahead')
    X = X.loc[:, ~X.columns.duplicated()].reset_index(drop=True)
    y = y.reset_index(drop=True)
    return X, y

X_train, y_train = prepare(train)
X_val,   y_val   = prepare(val)
X_test,  y_test  = prepare(test)

print(f"Train: {len(X_train):,} | Val: {len(X_val):,} | Test: {len(X_test):,}")
print(f"Test bloom rate: {y_test.mean()*100:.1f}%")

X_trainval = pd.concat([X_train, X_val]).reset_index(drop=True)
y_trainval = pd.concat([y_train, y_val]).reset_index(drop=True)

scale_pos_weight = (y_trainval == 0).sum() / (y_trainval == 1).sum()
model = XGBClassifier(
    n_estimators=200, max_depth=6, learning_rate=0.1,
    scale_pos_weight=scale_pos_weight, random_state=42,
    n_jobs=-1, eval_metric='logloss', verbosity=0
)
model.fit(X_trainval.values, y_trainval.values)

probs = model.predict_proba(X_test.values)[:, 1]

print(f"\nAUC-ROC:       {roc_auc_score(y_test, probs):.4f}")
print(f"Avg Precision: {average_precision_score(y_test, probs):.4f}")

# ── THRESHOLD SWEEP ──────────────────────────────────────────────────────────
thresholds = np.arange(0.1, 0.91, 0.05)

rows = []
for t in thresholds:
    preds = (probs >= t).astype(int)
    tp = int(((preds == 1) & (y_test == 1)).sum())
    fp = int(((preds == 1) & (y_test == 0)).sum())
    fn = int(((preds == 0) & (y_test == 1)).sum())
    tn = int(((preds == 0) & (y_test == 0)).sum())
    prec  = precision_score(y_test, preds, zero_division=0)
    rec   = recall_score(y_test, preds, zero_division=0)
    f1    = f1_score(y_test, preds, zero_division=0)
    rows.append({
        'threshold': round(t, 2),
        'precision': round(prec, 3),
        'recall':    round(rec, 3),
        'f1':        round(f1, 3),
        'TP': tp, 'FP': fp, 'FN': fn, 'TN': tn,
        'false_alarm_rate': round(fp / (fp + tn) if (fp + tn) > 0 else 0, 3)
    })

sweep = pd.DataFrame(rows)

print("\n" + "=" * 70)
print("THRESHOLD SWEEP — TEST SET (2023-2025)")
print("=" * 70)
print(f"{'Thresh':>7}  {'Precision':>10}  {'Recall':>8}  {'F1':>6}  "
      f"{'TP':>6}  {'FP':>6}  {'FN':>6}  {'FalseAlarmRate':>14}")
print("-" * 70)
for _, r in sweep.iterrows():
    marker = "  <-- original" if r['threshold'] == 0.50 else ""
    best_f1 = sweep.loc[sweep['f1'].idxmax(), 'threshold']
    if r['threshold'] == best_f1 and r['threshold'] != 0.50:
        marker = "  <-- best F1"
    print(f"  {r['threshold']:>5.2f}  {r['precision']:>10.3f}  {r['recall']:>8.3f}  "
          f"{r['f1']:>6.3f}  {r['TP']:>6,}  {r['FP']:>6,}  {r['FN']:>6,}  "
          f"{r['false_alarm_rate']:>14.3f}{marker}")

sweep.to_csv("data/threshold_sweep_results.csv", index=False)
print("\nSaved to data/threshold_sweep_results.csv")

# ── FIGURES ──────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Left: precision, recall, F1 vs threshold
ax = axes[0]
ax.plot(sweep['threshold'], sweep['precision'], 'b-o', label='Precision', markersize=4)
ax.plot(sweep['threshold'], sweep['recall'],    'r-o', label='Recall',    markersize=4)
ax.plot(sweep['threshold'], sweep['f1'],        'g-o', label='F1',        markersize=4)
ax.axvline(0.5, color='gray', linestyle='--', alpha=0.7, label='Default (0.5)')
best_t = sweep.loc[sweep['f1'].idxmax(), 'threshold']
ax.axvline(best_t, color='green', linestyle=':', alpha=0.8, label=f'Best F1 ({best_t:.2f})')
ax.set_xlabel('Threshold', fontsize=12)
ax.set_ylabel('Score', fontsize=12)
ax.set_title('Precision / Recall / F1 vs Threshold', fontsize=13)
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_xlim(0.05, 0.95)
ax.set_ylim(0, 1)

# Right: precision-recall curve
precision_curve, recall_curve, _ = precision_recall_curve(y_test, probs)
ap = average_precision_score(y_test, probs)
ax2 = axes[1]
ax2.plot(recall_curve, precision_curve, 'b-', lw=2, label=f'AP = {ap:.3f}')
ax2.axhline(y_test.mean(), color='gray', linestyle='--', alpha=0.7,
            label=f'Baseline ({y_test.mean()*100:.1f}% positive rate)')
# Mark threshold = 0.5
p05 = precision_score(y_test, (probs >= 0.5).astype(int), zero_division=0)
r05 = recall_score(y_test, (probs >= 0.5).astype(int), zero_division=0)
ax2.scatter([r05], [p05], color='gray', s=80, zorder=5, label='Threshold = 0.5')
# Mark best F1
pb = precision_score(y_test, (probs >= best_t).astype(int), zero_division=0)
rb = recall_score(y_test, (probs >= best_t).astype(int), zero_division=0)
ax2.scatter([rb], [pb], color='green', s=80, zorder=5, label=f'Best F1 threshold ({best_t:.2f})')
ax2.set_xlabel('Recall', fontsize=12)
ax2.set_ylabel('Precision', fontsize=12)
ax2.set_title('Precision-Recall Curve', fontsize=13)
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.set_xlim(0, 1)
ax2.set_ylim(0, 1)

plt.tight_layout()
plt.savefig("figures/threshold_sweep.png", dpi=150, bbox_inches='tight')
print("Saved figures/threshold_sweep.png")