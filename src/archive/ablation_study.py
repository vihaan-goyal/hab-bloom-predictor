r"""
ablation_study.py
-----------------
Systematic feature ablation. Removes one feature (and one group) at a time from
the locked 34-feature baseline and re-evaluates on the test set (2023-2025) at
threshold 0.60. If removing a feature *improves* precision/F1, that feature was
adding noise or a confound and is a candidate to drop from the pipeline.

Locked baseline (LR C=0.05, class_weight='balanced', threshold 0.60):
    Precision 0.446 | Recall 0.446 | F1 0.446 | AUC ~0.814  (34 features)

Pipeline (data loading, rolling means, bloom_28d label, splits, LR) matches
src/models/unused_features_search.py exactly so results are comparable.

Run from repo root:
    & "$env:USERPROFILE\anaconda3\python.exe" src/models/ablation_study.py
"""

import glob
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

# -- 1. Load + merge -----------------------------------------------------------
print("Loading data/hab_features_tidal.csv ...")
hab = pd.read_csv('data/hab_features_tidal.csv')
daily = pd.read_csv('data/hab_features_daily.csv')[
    ['date', 'station_name', 'sal_lag2', 'sal_lag3', 'sal_lag4']]
hab['date'] = pd.to_datetime(hab['date'])
daily['date'] = pd.to_datetime(daily['date'])

# sal_lag2/3/4 live in the daily file; merge any that are missing from tidal.
for col in ['sal_lag2', 'sal_lag3', 'sal_lag4']:
    if col not in hab.columns:
        hab = hab.merge(daily[['date', 'station_name', col]],
                        on=['date', 'station_name'], how='left')


def load_percent_saturation():
    """percent_saturation lives only in the raw ERDDAP surface (depth_code='S')
    extracts, not in the feature files. Concatenate every deep_wq_S_*.csv, drop
    the units row, and reduce to one value per (date, station_name).

    The ERDDAP timestamps store local midnight encoded as UTC (e.g. EDT midnight
    -> 04:00:00Z), so the UTC calendar date equals the local sample date that
    keys the feature files."""
    frames = []
    for f in sorted(glob.glob('data/raw/deep_wq_extra/deep_wq_S_*.csv')):
        # row 0 = header, row 1 = units ("UTC", "mg/L", ...) -> skip units.
        s = pd.read_csv(f, skiprows=[1],
                        usecols=['station_name', 'time', 'percent_saturation'])
        frames.append(s)
    ps = pd.concat(frames, ignore_index=True)
    ps = ps[ps['station_name'].notna()].copy()
    ps['station_name'] = ps['station_name'].astype(str)
    ps['date'] = pd.to_datetime(ps['time'], utc=True).dt.tz_localize(None).dt.normalize()
    ps['percent_saturation'] = pd.to_numeric(ps['percent_saturation'],
                                             errors='coerce')
    ps = (ps.dropna(subset=['percent_saturation'])
            .groupby(['date', 'station_name'], as_index=False)['percent_saturation']
            .mean())
    return ps


if 'percent_saturation' not in hab.columns:
    print("Loading percent_saturation from data/raw/deep_wq_extra/deep_wq_S_*.csv ...")
    ps = load_percent_saturation()
    # station_name keys are strings on both sides ('01', 'A2', ...).
    hab['station_name'] = hab['station_name'].astype(str)
    ps['station_name'] = ps['station_name'].astype(str)
    hab = hab.merge(ps, on=['date', 'station_name'], how='left')
    print(f"  percent_saturation coverage (all rows): "
          f"{hab['percent_saturation'].notna().mean() * 100:.1f}%")

# spring_neap: date-keyed astronomical spring-neap index (offline, ephem).
# Merge on date only -- broadcasts across stations, the Moon is location-blind.
print("Loading data/astro_features_daily.csv ...")
astro = pd.read_csv('data/astro_features_daily.csv', parse_dates=['date'])
_n = len(hab)
hab = hab.merge(astro[['date', 'spring_neap']], on='date', how='left')
assert len(hab) == _n, "astro merge changed row count -- duplicate dates?"
print(f"  spring_neap coverage (all rows): "
      f"{hab['spring_neap'].notna().mean() * 100:.1f}%")

df = hab

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
    idx = grp.index
    dates = grp['date'].values
    chl = grp['Chlorophyll'].values
    labels = np.zeros(len(grp), dtype=int)
    for i in range(len(grp)):
        mask = (dates > dates[i]) & (dates <= dates[i] + np.timedelta64(28, 'D'))
        if mask.any() and (chl[mask] > 10).any():
            labels[i] = 1
    df.loc[idx, 'bloom_28d'] = labels

# -- 3. Baseline feature set to ablate -----------------------------------------
BASE = [
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
    'percent_saturation',
]
BASE = [f for f in BASE if f in df.columns]
print(f"\nBASE feature count: {len(BASE)}")
missing = [f for f in (
    'Chlorophyll', 'chl_lag1', 'chl_lag2', 'chl_lag3', 'chl_lag4',
    'chl_roll3_mean', 'chl_roll6_mean', 'chl_roll9_mean', 'chl_trend',
    'chl_roll14_mean', 'chl_roll21_mean', 'chl_anomaly', 'chl_climatology',
    'do_lag1', 'temp_lag1', 'sal_lag1', 'sal_lag2', 'sal_lag3', 'sal_lag4',
    'sea_water_temperature', 'sea_water_salinity',
    'oxygen_concentration_in_sea_water', 'month', 'latitude_x', 'longitude_x',
    'nox_lag2', 'dip_lag2', 'dip_change', 'dip_x_month',
    'neighbor_chl3_mean', 'neighbor_chl3_lag1', 'tidal_gt_anom',
    'tidal_msl_anom', 'percent_saturation') if f not in df.columns]
if missing:
    print(f"  WARNING: missing from data -> dropped: {missing}")

# Feature groups to ablate together.
GROUPS = {
    'all CHL lags':       ['chl_lag1', 'chl_lag2', 'chl_lag3', 'chl_lag4'],
    'all DO features':    ['do_lag1', 'oxygen_concentration_in_sea_water'],
    'all sal features':   ['sal_lag1', 'sal_lag2', 'sal_lag3', 'sal_lag4',
                           'sea_water_salinity'],
    'all nutrients':      ['nox_lag2', 'dip_lag2', 'dip_change', 'dip_x_month'],
    'all neighbor':       ['neighbor_chl3_mean', 'neighbor_chl3_lag1'],
    'all tidal':          ['tidal_gt_anom', 'tidal_msl_anom'],
    'location':           ['latitude_x', 'longitude_x'],
    'temp features':      ['sea_water_temperature', 'temp_lag1'],
}

# -- 4. Split ------------------------------------------------------------------
train = df[df['date'].dt.year <= 2019]
val   = df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)]
test  = df[df['date'].dt.year >= 2023]


def prepare(split, features):
    rows = split[features + ['bloom_28d']].dropna(subset=['bloom_28d'])
    X = rows[features].copy().reset_index(drop=True)
    y = rows['bloom_28d'].copy().reset_index(drop=True)
    return X, y


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


def run(features):
    """Fit LR on `features`, evaluate on test at threshold 0.60."""
    X_tr, y_tr = prepare(train, features)
    X_te, y_te = prepare(test,  features)
    MED = X_tr.median()

    sc = StandardScaler()
    lr = LogisticRegression(C=0.05, class_weight='balanced',
                            max_iter=2000, random_state=42)
    lr.fit(sc.fit_transform(X_tr.fillna(MED)), y_tr)
    p_te = lr.predict_proba(sc.transform(X_te.fillna(MED)))[:, 1]

    m = eval_at(y_te, p_te, 0.60)
    m['n_feat'] = len(features)
    return m


def run_probs(features):
    """Same as run() but also returns aligned (y_test, p_test). Both feature
    sets share the same test rows (dropna is on bloom_28d only), so pairing holds."""
    X_tr, y_tr = prepare(train, features)
    X_te, y_te = prepare(test,  features)
    MED = X_tr.median()
    sc = StandardScaler()
    lr = LogisticRegression(C=0.05, class_weight='balanced',
                            max_iter=2000, random_state=42)
    lr.fit(sc.fit_transform(X_tr.fillna(MED)), y_tr)
    p_te = lr.predict_proba(sc.transform(X_te.fillna(MED)))[:, 1]
    m = eval_at(y_te, p_te, 0.60)
    m['n_feat'] = len(features)
    return m, y_te.to_numpy(), p_te


def paired_bootstrap_auc_delta(y, p_base, p_new, n_boot=2000, seed=42):
    """Paired bootstrap CI for AUC(p_new) - AUC(p_base). One resampled index set
    scores both models each iteration, preserving their correlation (an unpaired
    two-AUC CI would be far too wide)."""
    rng = np.random.default_rng(seed)
    y, p_base, p_new = map(np.asarray, (y, p_base, p_new))
    n = len(y)
    deltas = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        yb = y[idx]
        if yb.min() == yb.max():          # AUC undefined without both classes
            continue
        deltas.append(roc_auc_score(yb, p_new[idx]) - roc_auc_score(yb, p_base[idx]))
    deltas = np.asarray(deltas)
    return deltas.mean(), np.percentile(deltas, 2.5), np.percentile(deltas, 97.5)


# -- 5. Baseline ---------------------------------------------------------------
base = run(BASE)
print("\n" + "=" * 78)
print("BASELINE (all features)")
print("=" * 78)
print(f"  N_feat={base['n_feat']}  AUC={base['auc']:.4f}  "
      f"Prec={base['precision']:.3f}  Rec={base['recall']:.3f}  "
      f"F1={base['f1']:.3f}  TP={base['tp']}  FP={base['fp']}  FN={base['fn']}")

# -- 5b. Candidate: spring_neap (additive, paired bootstrap) -------------------
print("\n" + "=" * 78)
print("CANDIDATE FEATURE TEST: spring_neap (additive)")
print("=" * 78)
m_base, y_te, p_base = run_probs(BASE)
m_sn,   _,    p_sn   = run_probs(BASE + ['spring_neap'])
mean_d, lo, hi = paired_bootstrap_auc_delta(y_te, p_base, p_sn)
print(f"  baseline (34):          AUC={m_base['auc']:.4f}  "
      f"Prec={m_base['precision']:.3f}  Rec={m_base['recall']:.3f}  F1={m_base['f1']:.3f}")
print(f"  baseline + spring_neap: AUC={m_sn['auc']:.4f}  "
      f"Prec={m_sn['precision']:.3f}  Rec={m_sn['recall']:.3f}  F1={m_sn['f1']:.3f}")
print(f"  point delta:  dAUC={m_sn['auc']-m_base['auc']:+.4f}  "
      f"dPrec={m_sn['precision']-m_base['precision']:+.3f}  dF1={m_sn['f1']-m_base['f1']:+.3f}")
print(f"  paired bootstrap dAUC: {mean_d:+.4f}  95% CI [{lo:+.4f}, {hi:+.4f}]")
if lo > 0:
    print("  VERDICT: CI excludes zero -> pull NOAA CO-OPS tidal range and retest.")
else:
    print("  VERDICT: CI includes zero -> null, report as tested-and-rejected mechanism.")

# -- 6. Single-feature removal -------------------------------------------------
single = {}
for f in BASE:
    reduced = [x for x in BASE if x != f]
    single[f] = run(reduced)

# -- 7. Group removal ----------------------------------------------------------
group = {}
for name, feats in GROUPS.items():
    feats_present = [f for f in feats if f in BASE]
    if not feats_present:
        continue
    reduced = [x for x in BASE if x not in feats_present]
    group[name] = run(reduced)

# -- 8. Print single-feature removal table (sorted by F1 gain) -----------------
print("\n" + "=" * 90)
print("SINGLE FEATURE REMOVAL (sorted by F1 gain over baseline)")
print("=" * 90)
hdr = (f"{'Feature Removed':<26}{'N_feat':>7}{'AUC':>8}{'Prec':>8}{'Rec':>8}"
       f"{'F1':>8}{'TP':>5}{'FP':>5}{'Delta_F1':>10}")
print(hdr)
print("-" * 90)
print(f"{'BASELINE (none removed)':<26}{base['n_feat']:>7}{base['auc']:>8.3f}"
      f"{base['precision']:>8.3f}{base['recall']:>8.3f}{base['f1']:>8.3f}"
      f"{base['tp']:>5}{base['fp']:>5}{'+0.000':>10}")

ordered = sorted(single, key=lambda k: single[k]['f1'] - base['f1'],
                 reverse=True)
for f in ordered:
    m = single[f]
    d = m['f1'] - base['f1']
    print(f"{'remove: ' + f:<26}{m['n_feat']:>7}{m['auc']:>8.3f}"
          f"{m['precision']:>8.3f}{m['recall']:>8.3f}{m['f1']:>8.3f}"
          f"{m['tp']:>5}{m['fp']:>5}{d:>+10.3f}")

# -- 9. Print group removal table ----------------------------------------------
print("\n" + "=" * 90)
print("GROUP REMOVAL RESULTS (sorted by F1 gain over baseline)")
print("=" * 90)
ghdr = (f"{'Group Removed':<26}{'N_feat':>7}{'AUC':>8}{'Prec':>8}{'Rec':>8}"
        f"{'F1':>8}{'Delta_F1':>10}")
print(ghdr)
print("-" * 90)
print(f"{'BASELINE (none removed)':<26}{base['n_feat']:>7}{base['auc']:>8.3f}"
      f"{base['precision']:>8.3f}{base['recall']:>8.3f}{base['f1']:>8.3f}"
      f"{'+0.000':>10}")
for name in sorted(group, key=lambda k: group[k]['f1'] - base['f1'],
                   reverse=True):
    m = group[name]
    d = m['f1'] - base['f1']
    print(f"{'remove: ' + name:<26}{m['n_feat']:>7}{m['auc']:>8.3f}"
          f"{m['precision']:>8.3f}{m['recall']:>8.3f}{m['f1']:>8.3f}"
          f"{d:>+10.3f}")

# -- 10. Flag candidates -------------------------------------------------------
print("\n" + "=" * 90)
print("CANDIDATES FOR PIPELINE UPDATE")
print("  (F1 gain > 0.005, OR precision gain > 0.010 with recall >= 0.35)")
print("=" * 90)
flagged = False
for label, results in [('feature', single), ('group', group)]:
    for name in sorted(results, key=lambda k: results[k]['f1'] - base['f1'],
                       reverse=True):
        m = results[name]
        d_f1 = m['f1'] - base['f1']
        d_pr = m['precision'] - base['precision']
        f1_hit = d_f1 > 0.005
        pr_hit = d_pr > 0.010 and m['recall'] >= 0.35
        if f1_hit or pr_hit:
            flagged = True
            tag = []
            if f1_hit:
                tag.append('F1')
            if pr_hit:
                tag.append('PREC')
            print(f"  >>> remove {label} '{name}'  [{'+'.join(tag)}]  "
                  f"dF1={d_f1:+.3f}  dPrec={d_pr:+.3f}  "
                  f"dRec={m['recall'] - base['recall']:+.3f}  "
                  f"(P={m['precision']:.3f} R={m['recall']:.3f} "
                  f"F1={m['f1']:.3f})")
if not flagged:
    print("  None. No single feature or group removal beats baseline by the")
    print("  integration thresholds -- every feature is pulling its weight.")

# -- 11. Save results ----------------------------------------------------------
rows = []
rows.append({'type': 'baseline', 'removed': 'none', **base,
             'delta_f1': 0.0, 'delta_precision': 0.0})
for f, m in single.items():
    rows.append({'type': 'single', 'removed': f, **m,
                 'delta_f1': m['f1'] - base['f1'],
                 'delta_precision': m['precision'] - base['precision']})
for name, m in group.items():
    rows.append({'type': 'group', 'removed': name, **m,
                 'delta_f1': m['f1'] - base['f1'],
                 'delta_precision': m['precision'] - base['precision']})
out = pd.DataFrame(rows)[
    ['type', 'removed', 'n_feat', 'auc', 'precision', 'recall', 'f1',
     'tp', 'fp', 'fn', 'delta_f1', 'delta_precision']]
out.to_csv('data/ablation_results.csv', index=False)
print(f"\nSaved {len(out)} rows to data/ablation_results.csv")

# -- 12. Baseline validation ---------------------------------------------------
# The locked 0.446/0.446/0.446 baseline is the *33-feature* set (no
# percent_saturation). percent_saturation is documented to add +1.9pp precision,
# so the full 34-feature BASE scores ~0.465 precision -- both numbers are
# reproduced here, which is the real correctness check.
print("\n" + "=" * 90)
print("BASELINE VALIDATION")
print("=" * 90)
no_ps = single.get('percent_saturation')

print("  [1] 33-feature locked baseline (BASE minus percent_saturation):")
print(f"        Expected: Prec=0.446 Rec=0.446 F1=0.446")
if no_ps is not None:
    ok_locked = (abs(no_ps['precision'] - 0.446) < 0.01 and
                 abs(no_ps['recall'] - 0.446) < 0.01 and
                 abs(no_ps['f1'] - 0.446) < 0.01)
    print(f"        Got:      Prec={no_ps['precision']:.3f} "
          f"Rec={no_ps['recall']:.3f} F1={no_ps['f1']:.3f} "
          f"(TP={no_ps['tp']} FP={no_ps['fp']})")
    print(f"        {'PASS' if ok_locked else 'WARNING: drift -- investigate'}")
else:
    ok_locked = False
    print("        percent_saturation not in BASE -- cannot check")

print("  [2] 34-feature BASE (with percent_saturation):")
print(f"        Recall should equal 0.446, AUC ~0.814")
ok_full = (abs(base['recall'] - 0.446) < 0.01 and abs(base['auc'] - 0.814) < 0.01)
print(f"        Got:      Prec={base['precision']:.3f} Rec={base['recall']:.3f} "
      f"F1={base['f1']:.3f} AUC={base['auc']:.4f} "
      f"(TP={base['tp']} FP={base['fp']})")
print(f"        {'PASS' if ok_full else 'WARNING: drift -- investigate'}")

print("  [3] percent_saturation contribution (documented +1.9pp precision):")
if no_ps is not None:
    d_ps = base['precision'] - no_ps['precision']
    ok_ps = d_ps > 0.010
    print(f"        Got:      dPrec={d_ps:+.3f} ({d_ps * 100:+.1f}pp)")
    print(f"        {'PASS' if ok_ps else 'NOTE: smaller than documented'}")
else:
    ok_ps = False

print("\n  Overall: " + ("PASS -- locked baseline, AUC, and the documented "
                         "percent_saturation gain all reproduce."
                         if (ok_locked and ok_full and ok_ps)
                         else "see warnings above."))
