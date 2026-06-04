"""
mlp_tabular.py
--------------
Tests a small MLP (multilayer perceptron) on the tabular feature set
as an alternative to LR. Also tests gradient boosted trees with
hyperparameter tuning.

Uses the same train/val/test split and features as the main pipeline.

Run from repo root:
    python src/models/mlp_tabular.py
"""

import warnings
warnings.filterwarnings('ignore', category=UserWarning)

import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_auc_score, average_precision_score,
    f1_score, precision_score, recall_score,
    precision_recall_curve,
)
import xgboost as xgb

# ---------------------------------------------------------------------------
# Load + recompute features
# ---------------------------------------------------------------------------
print("Loading data/hab_features_tidal.csv...")
df = pd.read_csv('data/hab_features_tidal.csv')
df['date'] = pd.to_datetime(df['date'])

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
    'tidal_gt_anom', 'tidal_msl_anom',
]
FEATURES = [f for f in FEATURES_ALL if f in df.columns]
N_FEATURES = len(FEATURES)

train = df[df['date'].dt.year <= 2019]
val   = df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)]
test  = df[df['date'].dt.year >= 2023]

def prepare(split):
    rows = split[FEATURES + ['bloom_28d']].dropna(subset=['bloom_28d'])
    X = rows[FEATURES].copy().reset_index(drop=True)
    y = rows['bloom_28d'].copy().reset_index(drop=True)
    return X, y

X_train, y_train = prepare(train)
X_val,   y_val   = prepare(val)
X_test,  y_test  = prepare(test)
MED = X_train.median()

print(f"Train: {len(X_train):,} | Val: {len(X_val):,} | Test: {len(X_test):,}")
print(f"Features: {N_FEATURES}")

scaler = StandardScaler()
X_tr_s = scaler.fit_transform(X_train.fillna(MED))
X_v_s  = scaler.transform(X_val.fillna(MED))
X_te_s = scaler.transform(X_test.fillna(MED))

pos_weight = float((y_train == 0).sum() / (y_train == 1).sum())

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def best_f1_thresh(y, p):
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
        'tp': int(((preds==1)&(y==1)).sum()),
        'fp': int(((preds==1)&(y==0)).sum()),
        'fn': int(((preds==0)&(y==1)).sum()),
    }

results = {}

# ---------------------------------------------------------------------------
# 1. LR baseline (current best)
# ---------------------------------------------------------------------------
print("\n[1/5] Fitting LR baseline (current best)...")
lr = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
lr.fit(X_tr_s, y_train)
p_val_lr  = lr.predict_proba(X_v_s)[:, 1]
p_test_lr = lr.predict_proba(X_te_s)[:, 1]
t_lr = best_f1_thresh(y_val, p_val_lr)
results['LR (baseline)'] = eval_at(y_test, p_test_lr, t_lr)
results['LR (baseline)']['thresh'] = t_lr
print(f"  Val best-F1 thresh: {t_lr:.3f} | "
      f"Test AUC: {results['LR (baseline)']['auc']:.4f} | "
      f"Prec@0.60: {eval_at(y_test, p_test_lr, 0.60)['precision']:.4f}")
results['LR (baseline)']['at60'] = eval_at(y_test, p_test_lr, 0.60)

# ---------------------------------------------------------------------------
# 2. MLP -- small, regularized
# ---------------------------------------------------------------------------
print("\n[2/5] Fitting MLP (small, regularized)...")

class MLP(nn.Module):
    def __init__(self, n_in, hidden_sizes, dropout=0.3):
        super().__init__()
        layers = []
        prev = n_in
        for h in hidden_sizes:
            layers += [nn.Linear(prev, h), nn.BatchNorm1d(h),
                       nn.ReLU(), nn.Dropout(dropout)]
            prev = h
        layers.append(nn.Linear(prev, 1))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x).squeeze(1)

def train_mlp(hidden_sizes, dropout, lr_rate, epochs, label):
    X_tr_t = torch.FloatTensor(X_tr_s)
    y_tr_t = torch.FloatTensor(y_train.values)
    X_v_t  = torch.FloatTensor(X_v_s)
    X_te_t = torch.FloatTensor(X_te_s)

    ds    = TensorDataset(X_tr_t, y_tr_t)
    loader = DataLoader(ds, batch_size=256, shuffle=True)

    model = MLP(N_FEATURES, hidden_sizes, dropout)
    # Use pos_weight to handle class imbalance
    criterion = nn.BCEWithLogitsLoss(
        pos_weight=torch.tensor([pos_weight * 0.5])  # softer than full weight
    )
    optimizer = torch.optim.Adam(model.parameters(), lr=lr_rate,
                                 weight_decay=1e-3)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, patience=5, factor=0.5)

    best_val_auc = 0
    best_probs   = None
    patience_count = 0

    for epoch in range(epochs):
        model.train()
        for Xb, yb in loader:
            optimizer.zero_grad()
            loss = criterion(model(Xb), yb)
            loss.backward()
            optimizer.step()

        model.eval()
        with torch.no_grad():
            p_v = torch.sigmoid(model(X_v_t)).numpy()
        val_auc = roc_auc_score(y_val, p_v)
        scheduler.step(1 - val_auc)

        if val_auc > best_val_auc:
            best_val_auc = val_auc
            best_probs   = p_v.copy()
            patience_count = 0
        else:
            patience_count += 1
            if patience_count >= 15:
                break

    model.eval()
    with torch.no_grad():
        p_te = torch.sigmoid(model(X_te_t)).numpy()

    return best_probs, p_te, best_val_auc

mlp_configs = [
    ([64, 32],       0.3, 1e-3, 200, 'MLP-64-32'),
    ([128, 64, 32],  0.4, 5e-4, 200, 'MLP-128-64-32'),
    ([32, 16],       0.2, 1e-3, 200, 'MLP-32-16 (tiny)'),
]

for hidden, drop, lr_rate, epochs, label in mlp_configs:
    print(f"  Training {label}...")
    p_val_mlp, p_test_mlp, val_auc = train_mlp(
        hidden, drop, lr_rate, epochs, label)
    t_mlp = best_f1_thresh(y_val, p_val_mlp)
    results[label] = eval_at(y_test, p_test_mlp, t_mlp)
    results[label]['thresh'] = t_mlp
    results[label]['at60']   = eval_at(y_test, p_test_mlp, 0.60)
    print(f"    Best val AUC: {val_auc:.4f} | "
          f"Test AUC: {results[label]['auc']:.4f} | "
          f"Prec@0.60: {results[label]['at60']['precision']:.4f}")

# ---------------------------------------------------------------------------
# 3. XGBoost with tuned hyperparameters
# ---------------------------------------------------------------------------
print("\n[3/5] Fitting XGBoost (tuned)...")

xgb_configs = [
    {'n_estimators': 300, 'max_depth': 4, 'learning_rate': 0.05,
     'subsample': 0.8, 'colsample_bytree': 0.8,
     'min_child_weight': 10, 'scale_pos_weight': 1.0,
     'label': 'XGB-depth4-spw1'},
    {'n_estimators': 300, 'max_depth': 3, 'learning_rate': 0.03,
     'subsample': 0.7, 'colsample_bytree': 0.7,
     'min_child_weight': 15, 'scale_pos_weight': 1.5,
     'label': 'XGB-depth3-spw1.5'},
]

for cfg in xgb_configs:
    label = cfg.pop('label')
    print(f"  Training {label}...")
    xgb_m = xgb.XGBClassifier(
        **cfg, eval_metric='auc', random_state=42, verbosity=0,
        early_stopping_rounds=20,
    )
    xgb_m.fit(
        X_train.fillna(MED), y_train,
        eval_set=[(X_val.fillna(MED), y_val)],
        verbose=False,
    )
    p_val_xgb  = xgb_m.predict_proba(X_val.fillna(MED))[:, 1]
    p_test_xgb = xgb_m.predict_proba(X_test.fillna(MED))[:, 1]
    t_xgb = best_f1_thresh(y_val, p_val_xgb)
    results[label] = eval_at(y_test, p_test_xgb, t_xgb)
    results[label]['thresh'] = t_xgb
    results[label]['at60']   = eval_at(y_test, p_test_xgb, 0.60)
    print(f"    Test AUC: {results[label]['auc']:.4f} | "
          f"Prec@0.60: {results[label]['at60']['precision']:.4f}")
    cfg['label'] = label  # restore

# ---------------------------------------------------------------------------
# Results table
# ---------------------------------------------------------------------------
print("\n" + "=" * 80)
print("RESULTS — sorted by precision at threshold 0.60")
print("=" * 80)
print(f"{'Model':<25}  {'AUC':>7}  {'Val t':>6}  "
      f"{'Prec@t':>8}  {'Rec@t':>7}  {'F1@t':>6}  "
      f"{'Prec@.60':>9}  {'Rec@.60':>8}  {'F1@.60':>7}")
print("-" * 80)

sorted_results = sorted(results.items(),
                        key=lambda x: x[1]['at60']['precision'],
                        reverse=True)

for name, r in sorted_results:
    a60 = r['at60']
    print(f"{name:<25}  {r['auc']:>7.4f}  {r['thresh']:>6.3f}  "
          f"{r['precision']:>8.3f}  {r['recall']:>7.3f}  {r['f1']:>6.3f}  "
          f"{a60['precision']:>9.3f}  {a60['recall']:>8.3f}  {a60['f1']:>7.3f}")

print("\n" + "=" * 80)
print("VERDICT")
print("=" * 80)
best_name, best_r = sorted_results[0]
lr_prec = results['LR (baseline)']['at60']['precision']
best_prec = best_r['at60']['precision']
delta = best_prec - lr_prec

if delta > 0.02:
    print(f"  WINNER: {best_name} -- precision {best_prec:.3f} vs LR {lr_prec:.3f} "
          f"(+{delta:.3f})")
    print("  --> Integrate into pipeline")
else:
    print(f"  No model beats LR by >2pp precision at threshold 0.60")
    print(f"  Best: {best_name} precision {best_prec:.3f} vs LR {lr_prec:.3f} "
          f"(delta={delta:+.3f})")
    print("  --> LR remains the best model. Precision ceiling confirmed.")