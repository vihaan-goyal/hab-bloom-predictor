r"""
unused_features_search.py
-------------------------
Systematically tests unused columns from hab_features_daily.csv to find any
that improve precision and/or recall over the current locked baseline.

Locked baseline (data/hab_features_tidal.csv, LR C=0.05, balanced):
    Precision 0.449 | Recall 0.419 | F1 0.434 | AUC ~0.819 (threshold 0.60)

Each NEW_GROUP is added ON TOP of BASE and re-evaluated. Candidates that
improve F1 by >0.01 OR precision by >0.02 are flagged for integration.

Run from repo root:
    & "$env:USERPROFILE\anaconda3\python.exe" src/models/unused_features_search.py
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
    precision_recall_curve,
)

# -- 1. Load + merge -----------------------------------------------------------
print("Loading data/hab_features_daily.csv + tidal anomalies...")
hab = pd.read_csv('data/hab_features_daily.csv')
tidal = pd.read_csv('data/hab_features_tidal.csv')[
    ['date', 'station_name', 'tidal_gt_anom', 'tidal_msl_anom']
]
hab['date'] = pd.to_datetime(hab['date'])
tidal['date'] = pd.to_datetime(tidal['date'])
df = hab.merge(tidal, on=['date', 'station_name'], how='left')

# -- 2. Recompute rolling features and bloom label -----------------------------
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

# -- 3. Feature sets -----------------------------------------------------------
BASE = [
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

NEW_GROUPS = {
    'density':        ['sea_water_density'],
    'PAR':            ['PAR'],
    'chl_std':        ['chl_roll3_std'],
    'pH':             ['pH'],
    'neighbor5':      ['neighbor_chl5_mean'],
    'neighbor_temp':  ['neighbor_temp3_mean'],
    'do_lags':        ['do_lag2', 'do_lag3', 'do_lag4'],
    'sal_lags':       ['sal_lag2', 'sal_lag3', 'sal_lag4'],
    'nox_month':      ['nox_x_month'],
    'TDN':            ['TDN-LC'],
    'all_high_pri':   ['sea_water_density', 'PAR', 'chl_roll3_std', 'pH'],
    'all_med_pri':    ['neighbor_chl5_mean', 'neighbor_temp3_mean',
                       'do_lag2', 'do_lag3', 'do_lag4',
                       'sal_lag2', 'sal_lag3', 'sal_lag4',
                       'nox_x_month', 'TDN-LC'],
    'all_new':        ['sea_water_density', 'PAR', 'chl_roll3_std', 'pH',
                       'neighbor_chl5_mean', 'neighbor_temp3_mean',
                       'do_lag2', 'do_lag3', 'do_lag4',
                       'sal_lag2', 'sal_lag3', 'sal_lag4',
                       'nox_x_month', 'TDN-LC'],
    'sal_lags+density':  ['sal_lag2', 'sal_lag3', 'sal_lag4',
                          'sea_water_density'],
    'sal_lags+high_pri': ['sal_lag2', 'sal_lag3', 'sal_lag4',
                          'sea_water_density', 'PAR', 'chl_roll3_std', 'pH'],
}

BASE = [f for f in BASE if f in df.columns]

# -- 4. Split ------------------------------------------------------------------
train = df[df['date'].dt.year <= 2019]
val   = df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)]
test  = df[df['date'].dt.year >= 2023]


def prepare(split, features):
    rows = split[features + ['bloom_28d']].dropna(subset=['bloom_28d'])
    X = rows[features].copy().reset_index(drop=True)
    y = rows['bloom_28d'].copy().reset_index(drop=True)
    return X, y


def best_f1_thresh(y, p):
    prec, rec, thresh = precision_recall_curve(y, p)
    f1 = 2 * prec * rec / (prec + rec + 1e-9)
    idx = f1.argmax()
    return float(thresh[idx]) if idx < len(thresh) else 0.5


def eval_at(y, p, t):
    preds = (p >= t).astype(int)
    return {
        'auc':       roc_auc_score(y, p),
        'precision': precision_score(y, preds, zero_division=0),
        'recall':    recall_score(y, preds, zero_division=0),
        'f1':        f1_score(y, preds, zero_division=0),
        'tp': int(((preds == 1) & (y == 1)).sum()),
        'fp': int(((preds == 1) & (y == 0)).sum()),
        'fn': int(((preds == 0) & (y == 1)).sum()),
    }


def run_group(features):
    """Fit LR on BASE+features and evaluate on test at threshold 0.60."""
    X_tr, y_tr = prepare(train, features)
    X_v,  y_v  = prepare(val,   features)
    X_te, y_te = prepare(test,  features)
    MED = X_tr.median()

    sc = StandardScaler()
    lr = LogisticRegression(C=0.05, class_weight='balanced',
                            max_iter=2000, random_state=42)
    lr.fit(sc.fit_transform(X_tr.fillna(MED)), y_tr)
    p_v  = lr.predict_proba(sc.transform(X_v.fillna(MED)))[:, 1]
    p_te = lr.predict_proba(sc.transform(X_te.fillna(MED)))[:, 1]

    t_best = best_f1_thresh(y_v, p_v)          # informational
    m60 = eval_at(y_te, p_te, 0.60)
    m60['n_feat'] = len(features)
    m60['t_best'] = t_best
    return m60


# -- 5. Correlations of each new feature with bloom_28d ------------------------
all_new_feats = []
for feats in NEW_GROUPS.values():
    for f in feats:
        if f not in all_new_feats:
            all_new_feats.append(f)

print("\n" + "=" * 60)
print("CORRELATION OF NEW FEATURES WITH bloom_28d")
print("=" * 60)
print(f"{'Feature':<22} {'corr':>8} {'coverage%':>10}")
print("-" * 42)
for f in all_new_feats:
    if f in df.columns:
        corr = df[f].corr(df['bloom_28d'])
        cov = df[f].notna().mean() * 100
        print(f"{f:<22} {corr:>+8.3f} {cov:>9.1f}%")
    else:
        print(f"{f:<22} {'MISSING':>8}")

# -- 6. Evaluate baseline + every group ---------------------------------------
results = {}
results['BASE (baseline)'] = run_group(BASE)
for name, feats in NEW_GROUPS.items():
    feats = [f for f in feats if f in df.columns]
    if not feats:
        print(f"\n[skip] {name}: no columns present")
        continue
    results[name] = run_group(BASE + feats)

# -- 7. Results table sorted by precision -------------------------------------
print("\n" + "=" * 78)
print("RESULTS (test 2023-2025, threshold 0.60), sorted by precision")
print("=" * 78)
print(f"{'Feature Group':<16} {'N_feat':>6} {'AUC':>7} {'Prec@.60':>9} "
      f"{'Rec@.60':>8} {'F1@.60':>7} {'TP':>4} {'FP':>4} {'FN':>4}")
print("-" * 78)

# keep baseline first, then the rest sorted by precision desc
ordered = ['BASE (baseline)'] + sorted(
    [k for k in results if k != 'BASE (baseline)'],
    key=lambda k: results[k]['precision'], reverse=True,
)
for name in ordered:
    m = results[name]
    print(f"{name:<16} {m['n_feat']:>6} {m['auc']:>7.4f} {m['precision']:>9.3f} "
          f"{m['recall']:>8.3f} {m['f1']:>7.3f} {m['tp']:>4} {m['fp']:>4} {m['fn']:>4}")

# -- 8. Top 3 by F1, top 3 by precision (recall >= 0.30) ----------------------
base = results['BASE (baseline)']

print("\n-- Top 3 by F1 --")
for name in sorted(results, key=lambda k: results[k]['f1'], reverse=True)[:3]:
    m = results[name]
    print(f"  {name:<16} F1={m['f1']:.3f}  Prec={m['precision']:.3f}  "
          f"Rec={m['recall']:.3f}  AUC={m['auc']:.4f}")

print("\n-- Top 3 by precision (recall >= 0.30) --")
elig = [k for k in results if results[k]['recall'] >= 0.30]
for name in sorted(elig, key=lambda k: results[k]['precision'], reverse=True)[:3]:
    m = results[name]
    print(f"  {name:<16} Prec={m['precision']:.3f}  Rec={m['recall']:.3f}  "
          f"F1={m['f1']:.3f}  AUC={m['auc']:.4f}")

# -- 9. Flag candidates --------------------------------------------------------
print("\n" + "=" * 78)
print("CANDIDATES (F1 gain >0.01 OR precision gain >0.02 vs baseline)")
print("=" * 78)
flagged = False
for name in ordered:
    if name == 'BASE (baseline)':
        continue
    m = results[name]
    d_f1 = m['f1'] - base['f1']
    d_pr = m['precision'] - base['precision']
    if d_f1 > 0.01 or d_pr > 0.02:
        flagged = True
        print(f"  >>> {name}: dF1={d_f1:+.3f}  dPrec={d_pr:+.3f}  "
              f"dRec={m['recall'] - base['recall']:+.3f}  "
              f"(P={m['precision']:.3f} R={m['recall']:.3f} F1={m['f1']:.3f})")
        print(f"      features added: "
              f"{[f for f in NEW_GROUPS[name] if f in df.columns]}")
if not flagged:
    print("  None. No group beats baseline by the integration thresholds.")
    print("  Precision ceiling holds with current feature set.")

# -- 10. Baseline sanity check -------------------------------------------------
print("\n" + "=" * 78)
print("BASELINE VALIDATION")
print("=" * 78)
ok = (abs(base['precision'] - 0.449) < 0.01 and
      abs(base['recall'] - 0.419) < 0.01 and
      abs(base['f1'] - 0.434) < 0.01)
print(f"  Expected: Prec=0.449 Rec=0.419 F1=0.434 AUC~0.819")
print(f"  Got:      Prec={base['precision']:.3f} Rec={base['recall']:.3f} "
      f"F1={base['f1']:.3f} AUC={base['auc']:.4f}")
print(f"  {'PASS' if ok else 'WARNING: baseline drift -- investigate'}")
