"""
full_model_comparison.py
------------------------
Tests every reasonable model architecture on the locked 34-feature set to
confirm LR is the best or find a stronger candidate.

Run from repo root (PowerShell):
    python src/models/experiments/full_model_comparison.py
"""

import glob
import subprocess
import sys
import warnings
warnings.filterwarnings('ignore')

# Install lightgbm if missing
try:
    import lightgbm as lgb
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'lightgbm', '--quiet'],
                   check=True)
    import lightgbm as lgb

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import (
    AdaBoostClassifier, BaggingClassifier, ExtraTreesClassifier,
    GradientBoostingClassifier, RandomForestClassifier, StackingClassifier,
    VotingClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    f1_score, precision_score, recall_score, roc_auc_score,
)
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
import xgboost as xgb

# ---------------------------------------------------------------------------
# 1. Load + merge
# ---------------------------------------------------------------------------
print("Loading data/hab_features_tidal.csv ...")
hab = pd.read_csv('data/hab_features_tidal.csv')
hab['date'] = pd.to_datetime(hab['date'])

daily = pd.read_csv('data/hab_features_daily.csv')[
    ['date', 'station_name', 'sal_lag2', 'sal_lag3', 'sal_lag4']]
daily['date'] = pd.to_datetime(daily['date'])

for col in ['sal_lag2', 'sal_lag3', 'sal_lag4']:
    if col not in hab.columns:
        hab = hab.merge(daily[['date', 'station_name', col]],
                        on=['date', 'station_name'], how='left')


def load_percent_saturation():
    frames = []
    for f in sorted(glob.glob('data/raw/deep_wq_extra/deep_wq_S_*.csv')):
        frames.append(pd.read_csv(
            f, skiprows=[1],
            usecols=['station_name', 'time', 'percent_saturation']))
    ps = pd.concat(frames, ignore_index=True)
    ps = ps[ps['station_name'].notna()].copy()
    ps['station_name'] = ps['station_name'].astype(str)
    ps['date'] = (pd.to_datetime(ps['time'], utc=True)
                    .dt.tz_localize(None).dt.normalize())
    ps['percent_saturation'] = pd.to_numeric(ps['percent_saturation'],
                                             errors='coerce')
    return (ps.dropna(subset=['percent_saturation'])
              .groupby(['date', 'station_name'], as_index=False)
              ['percent_saturation'].mean())


if 'percent_saturation' not in hab.columns:
    print("Loading percent_saturation from data/raw/deep_wq_extra/deep_wq_S_*.csv ...")
    ps = load_percent_saturation()
    hab['station_name'] = hab['station_name'].astype(str)
    ps['station_name'] = ps['station_name'].astype(str)
    hab = hab.merge(ps, on=['date', 'station_name'], how='left')
    print(f"  percent_saturation coverage: "
          f"{hab['percent_saturation'].notna().mean() * 100:.1f}%")

df = hab

# ---------------------------------------------------------------------------
# 2. Recompute rolling features + bloom label
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
    idx = grp.index
    dates = grp['date'].values
    chl = grp['Chlorophyll'].values
    labels = np.zeros(len(grp), dtype=int)
    for i in range(len(grp)):
        mask = (dates > dates[i]) & (dates <= dates[i] + np.timedelta64(28, 'D'))
        if mask.any() and (chl[mask] > 10).any():
            labels[i] = 1
    df.loc[idx, 'bloom_28d'] = labels

# ---------------------------------------------------------------------------
# 3. Feature set
# ---------------------------------------------------------------------------
FEATURES_ALL = [
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
FEATURES = [f for f in FEATURES_ALL if f in df.columns]
print(f"\nFeatures used: {len(FEATURES)}")

# ---------------------------------------------------------------------------
# 4. Splits
# ---------------------------------------------------------------------------
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
sc = StandardScaler()
X_tr_s = sc.fit_transform(X_train.fillna(MED))
X_v_s  = sc.transform(X_val.fillna(MED))
X_te_s = sc.transform(X_test.fillna(MED))

print(f"Train: {len(X_train):,} | Val: {len(X_val):,} | Test: {len(X_test):,}")
print(f"Train bloom rate: {y_train.mean()*100:.1f}%")
print(f"Val   bloom rate: {y_val.mean()*100:.1f}%")
print(f"Test  bloom rate: {y_test.mean()*100:.1f}%")

# ---------------------------------------------------------------------------
# 5. Helper
# ---------------------------------------------------------------------------
def best_f1_threshold(y, probs):
    """Find threshold that maximises F1 on the given set."""
    best_t, best_f1 = 0.5, 0.0
    for t in np.arange(0.05, 0.96, 0.01):
        f = f1_score(y, (probs >= t).astype(int), zero_division=0)
        if f > best_f1:
            best_f1, best_t = f, t
    return round(best_t, 2)


def eval_at(y, probs, t):
    preds = (probs >= t).astype(int)
    tp = int(((preds == 1) & (y == 1)).sum())
    fp = int(((preds == 1) & (y == 0)).sum())
    fn = int(((preds == 0) & (y == 1)).sum())
    return {
        'auc':  roc_auc_score(y, probs),
        'prec': precision_score(y, preds, zero_division=0),
        'rec':  recall_score(y, preds, zero_division=0),
        'f1':   f1_score(y, preds, zero_division=0),
        'tp': tp, 'fp': fp, 'fn': fn,
    }

# ---------------------------------------------------------------------------
# 6. Model zoo
# ---------------------------------------------------------------------------
# Stacked model defined after the dict so it can reference other estimators.
_rf_stack  = RandomForestClassifier(n_estimators=200, class_weight='balanced',
                                     max_depth=5, random_state=42, n_jobs=-1)
_xgb_stack = xgb.XGBClassifier(n_estimators=200, max_depth=3,
                                 learning_rate=0.05, scale_pos_weight=2,
                                 random_state=42, verbosity=0,
                                 eval_metric='auc')
_gbm_stack = GradientBoostingClassifier(n_estimators=150, max_depth=3,
                                         learning_rate=0.05, random_state=42)

stacked = StackingClassifier(
    estimators=[('rf', _rf_stack), ('xgb', _xgb_stack), ('gbm', _gbm_stack)],
    final_estimator=LogisticRegression(C=0.1, random_state=42),
    cv=5,
    stack_method='predict_proba',
)

models = {
    'LR (baseline)': LogisticRegression(
        C=0.05, class_weight='balanced', max_iter=2000, random_state=42),
    'LR C=0.1': LogisticRegression(
        C=0.1, class_weight='balanced', max_iter=2000, random_state=42),
    'LR C=0.5': LogisticRegression(
        C=0.5, class_weight='balanced', max_iter=2000, random_state=42),
    'RandomForest-100': RandomForestClassifier(
        n_estimators=100, class_weight='balanced',
        max_depth=6, min_samples_leaf=10, random_state=42, n_jobs=-1),
    'RandomForest-300': RandomForestClassifier(
        n_estimators=300, class_weight='balanced',
        max_depth=5, min_samples_leaf=15, random_state=42, n_jobs=-1),
    'ExtraTrees': ExtraTreesClassifier(
        n_estimators=200, class_weight='balanced',
        max_depth=6, min_samples_leaf=10, random_state=42, n_jobs=-1),
    'GBM-sklearn': GradientBoostingClassifier(
        n_estimators=200, max_depth=3, learning_rate=0.05,
        subsample=0.8, min_samples_leaf=15, random_state=42),
    'XGBoost-spw1': xgb.XGBClassifier(
        n_estimators=300, max_depth=3, learning_rate=0.03,
        subsample=0.7, colsample_bytree=0.7, min_child_weight=15,
        scale_pos_weight=1.0, eval_metric='auc',
        random_state=42, verbosity=0),
    'XGBoost-spw2': xgb.XGBClassifier(
        n_estimators=300, max_depth=3, learning_rate=0.03,
        subsample=0.7, colsample_bytree=0.7, min_child_weight=15,
        scale_pos_weight=2.0, eval_metric='auc',
        random_state=42, verbosity=0),
    'XGBoost-spw3': xgb.XGBClassifier(
        n_estimators=300, max_depth=4, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.8, min_child_weight=10,
        scale_pos_weight=3.0, eval_metric='auc',
        random_state=42, verbosity=0),
    'LightGBM': lgb.LGBMClassifier(
        n_estimators=300, max_depth=4, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.8, min_child_samples=20,
        class_weight='balanced', random_state=42, verbose=-1),
    'SVM-RBF': CalibratedClassifierCV(
        SVC(kernel='rbf', C=1.0, class_weight='balanced', random_state=42)),
    'SVM-linear': CalibratedClassifierCV(
        SVC(kernel='linear', C=0.1, class_weight='balanced', random_state=42)),
    'AdaBoost': AdaBoostClassifier(
        n_estimators=100, learning_rate=0.5, random_state=42),
    'GaussianNB': GaussianNB(),
    'VotingEnsemble': VotingClassifier(
        estimators=[
            ('lr', LogisticRegression(C=0.05, class_weight='balanced',
                                      max_iter=2000, random_state=42)),
            ('rf', RandomForestClassifier(n_estimators=200,
                                          class_weight='balanced',
                                          max_depth=5, random_state=42,
                                          n_jobs=-1)),
            ('xgb', xgb.XGBClassifier(n_estimators=200, max_depth=3,
                                        learning_rate=0.05,
                                        scale_pos_weight=2,
                                        random_state=42, verbosity=0,
                                        eval_metric='auc')),
        ],
        voting='soft'),
    'StackedLR': stacked,
}

# ---------------------------------------------------------------------------
# 7. Train and evaluate
# ---------------------------------------------------------------------------
print("\nTraining models (this will take 5-10 minutes) ...")

results = []
xgb_names = {'XGBoost-spw1', 'XGBoost-spw2', 'XGBoost-spw3'}

for name, model in models.items():
    print(f"  [{name}] ... ", end='', flush=True)
    try:
        if name in xgb_names:
            model.fit(X_tr_s, y_train,
                      eval_set=[(X_v_s, y_val)],
                      verbose=False)
        else:
            model.fit(X_tr_s, y_train)

        val_probs  = model.predict_proba(X_v_s)[:, 1]
        test_probs = model.predict_proba(X_te_s)[:, 1]

        val_t = best_f1_threshold(y_val, val_probs)
        m60   = eval_at(y_test, test_probs, 0.60)
        m_vt  = eval_at(y_test, test_probs, val_t)

        results.append({
            'model': name,
            'auc':      round(m60['auc'],  4),
            'val_t':    val_t,
            'prec_60':  round(m60['prec'], 3),
            'rec_60':   round(m60['rec'],  3),
            'f1_60':    round(m60['f1'],   3),
            'tp_60': m60['tp'], 'fp_60': m60['fp'], 'fn_60': m60['fn'],
            'prec_vt':  round(m_vt['prec'], 3),
            'rec_vt':   round(m_vt['rec'],  3),
            'f1_vt':    round(m_vt['f1'],   3),
        })
        print(f"AUC={m60['auc']:.4f}  P@.60={m60['prec']:.3f}  "
              f"R@.60={m60['rec']:.3f}  F1@.60={m60['f1']:.3f}  "
              f"val_t={val_t}")
    except Exception as e:
        print(f"FAILED — {e}")

# ---------------------------------------------------------------------------
# 8. Sort and print main table
# ---------------------------------------------------------------------------
res = pd.DataFrame(results).sort_values('f1_60', ascending=False).reset_index(drop=True)

print("\n\n" + "=" * 95)
print("FULL MODEL COMPARISON — test set 2023-2025, threshold 0.60")
print("Sorted by F1 (higher = better overall balance)")
print("=" * 95)
hdr = (f"{'Rank':<5} {'Model':<22} {'AUC':>7} {'Val_t':>7} "
       f"{'Prec@.60':>10} {'Rec@.60':>9} {'F1@.60':>8} "
       f"{'TP':>5} {'FP':>5} {'FN':>5}")
print(hdr)
print("-" * 95)
for i, row in res.iterrows():
    rank = i + 1
    print(f"{rank:<5} {row['model']:<22} {row['auc']:>7.4f} {row['val_t']:>7.2f} "
          f"{row['prec_60']:>10.3f} {row['rec_60']:>9.3f} {row['f1_60']:>8.3f} "
          f"{row['tp_60']:>5} {row['fp_60']:>5} {row['fn_60']:>5}")

# Also print at val-threshold
print("\n\n" + "=" * 95)
print("FULL MODEL COMPARISON — test set 2023-2025, at val-tuned threshold")
print("Sorted by F1 (higher = better overall balance)")
print("=" * 95)
res_vt = res.sort_values('f1_vt', ascending=False).reset_index(drop=True)
hdr2 = (f"{'Rank':<5} {'Model':<22} {'AUC':>7} {'Val_t':>7} "
        f"{'Prec@Vt':>9} {'Rec@Vt':>8} {'F1@Vt':>7}")
print(hdr2)
print("-" * 65)
for i, row in res_vt.iterrows():
    rank = i + 1
    print(f"{rank:<5} {row['model']:<22} {row['auc']:>7.4f} {row['val_t']:>7.2f} "
          f"{row['prec_vt']:>9.3f} {row['rec_vt']:>8.3f} {row['f1_vt']:>7.3f}")

# ---------------------------------------------------------------------------
# 9. Sub-rankings
# ---------------------------------------------------------------------------
# Top 3 by precision (recall >= 0.30) at threshold 0.60
prec_top = res[res['rec_60'] >= 0.30].sort_values('prec_60', ascending=False).head(3)
print("\n\nTop 3 by Precision@0.60 (recall >= 0.30):")
for _, r in prec_top.iterrows():
    print(f"  {r['model']:<22}  Prec={r['prec_60']:.3f}  Rec={r['rec_60']:.3f}  "
          f"F1={r['f1_60']:.3f}  AUC={r['auc']:.4f}")

# Top 3 by AUC
auc_top = res.sort_values('auc', ascending=False).head(3)
print("\nTop 3 by AUC:")
for _, r in auc_top.iterrows():
    print(f"  {r['model']:<22}  AUC={r['auc']:.4f}  Prec={r['prec_60']:.3f}  "
          f"Rec={r['rec_60']:.3f}  F1={r['f1_60']:.3f}")

# ---------------------------------------------------------------------------
# 10. Baseline validation
# ---------------------------------------------------------------------------
print("\n\n" + "=" * 60)
print("BASELINE VALIDATION")
print("=" * 60)
base_row = res[res['model'] == 'LR (baseline)']
if not base_row.empty:
    r = base_row.iloc[0]
    exp_prec, exp_rec, exp_f1, exp_auc = 0.465, 0.446, 0.455, 0.814
    ok = (abs(r['prec_60'] - exp_prec) < 0.01 and
          abs(r['rec_60']  - exp_rec)  < 0.01 and
          abs(r['f1_60']   - exp_f1)   < 0.01 and
          abs(r['auc']     - exp_auc)  < 0.01)
    print(f"  Expected: Prec={exp_prec}  Rec={exp_rec}  F1={exp_f1}  AUC={exp_auc}")
    print(f"  Got:      Prec={r['prec_60']:.3f}  Rec={r['rec_60']:.3f}  "
          f"F1={r['f1_60']:.3f}  AUC={r['auc']:.4f}")
    print(f"  {'PASS' if ok else 'WARNING: baseline drift — investigate'}")
else:
    print("  LR (baseline) not found in results.")

# ---------------------------------------------------------------------------
# 11. Any model beats LR on ALL THREE of AUC, Precision, F1?
# ---------------------------------------------------------------------------
print("\n\n" + "=" * 60)
print("MODELS THAT BEAT LR BASELINE ON ALL THREE (AUC, Prec@.60, F1@.60)")
print("=" * 60)
if not base_row.empty:
    b = base_row.iloc[0]
    beats_all = res[
        (res['model'] != 'LR (baseline)') &
        (res['auc']     > b['auc']) &
        (res['prec_60'] > b['prec_60']) &
        (res['f1_60']   > b['f1_60'])
    ]
    if beats_all.empty:
        print("  None. LR baseline holds on all three metrics simultaneously.")
    else:
        for _, r in beats_all.iterrows():
            print(f"  >>> {r['model']:<22}  "
                  f"AUC={r['auc']:.4f} (+{r['auc']-b['auc']:+.4f})  "
                  f"Prec={r['prec_60']:.3f} ({r['prec_60']-b['prec_60']:+.3f})  "
                  f"F1={r['f1_60']:.3f} ({r['f1_60']-b['f1_60']:+.3f})")

# ---------------------------------------------------------------------------
# 12. Flag candidates to replace LR
# ---------------------------------------------------------------------------
print("\n\n" + "=" * 60)
print("CANDIDATE MODELS TO REPLACE LR IN PIPELINE")
print("  Criteria: F1 improves >0.010 OR (Prec improves >0.020 AND Rec>=0.35)")
print("=" * 60)
if not base_row.empty:
    b = base_row.iloc[0]
    flagged = False
    for _, r in res[res['model'] != 'LR (baseline)'].iterrows():
        d_f1   = r['f1_60']   - b['f1_60']
        d_prec = r['prec_60'] - b['prec_60']
        f1_hit   = d_f1   > 0.010
        prec_hit = d_prec > 0.020 and r['rec_60'] >= 0.35
        if f1_hit or prec_hit:
            flagged = True
            tags = []
            if f1_hit:   tags.append('F1')
            if prec_hit: tags.append('PREC')
            print(f"  >>> {r['model']:<22} [{'+'.join(tags)}]  "
                  f"dF1={d_f1:+.3f}  dPrec={d_prec:+.3f}  "
                  f"(AUC={r['auc']:.4f}  P={r['prec_60']:.3f}  "
                  f"R={r['rec_60']:.3f}  F1={r['f1_60']:.3f})")
    if not flagged:
        print("  None. No model clears both improvement thresholds.")
        print("  LR (C=0.05, class_weight='balanced') remains the best model.")

# ---------------------------------------------------------------------------
# 13. Save results
# ---------------------------------------------------------------------------
out_path = 'data/full_model_comparison_results.csv'
res.to_csv(out_path, index=False)
print(f"\n\nSaved results to {out_path}")
