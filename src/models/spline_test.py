"""
spline_test.py
--------------
Last cheap model-side lever: give the LR controlled nonlinearity without tree
overfitting. Adds spline bases on the rolling-chlorophyll features (the CHL-to-bloom
response is threshold-like, not linear) plus two interaction terms
(Chlorophyll x month, salinity x temperature). Strong L2 (C=0.05) keeps the extra
degrees of freedom in check.

Compares plain LR (baseline) against the augmented LR at the locked 21-day horizon,
both run through the same walk-forward CV on identical rows, with a paired AUC
difference bootstrap. If the difference CI excludes zero, nonlinearity helps; if not,
the linear model was already capturing the signal and this lever is closed.

Splines and scaler are fit on TRAIN only each fold (no leakage).

Run from repo root:
    python src/models/spline_test.py
    python src/models/spline_test.py --horizon 21 --n-knots 4
"""

import argparse
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, SplineTransformer
from sklearn.metrics import roc_auc_score

from rolling_origin_cv import build_dataset
from label_utils import build_forward_label

SPLINE_COLS = ['Chlorophyll', 'chl_roll14_mean', 'chl_roll21_mean']
INTERACTIONS = [('Chlorophyll', 'month'),
                ('sea_water_salinity', 'sea_water_temperature')]


def build_design(X_raw, med, features, spline_cols, inter_pairs,
                 augment, n_knots, spline_tf=None, fit=False):
    Xf = X_raw.fillna(med)
    blocks = [Xf[features].values]
    if augment:
        # interaction columns
        inter = []
        for a, b in inter_pairs:
            if a in Xf.columns and b in Xf.columns:
                inter.append((Xf[a].values * Xf[b].values).reshape(-1, 1))
        if inter:
            blocks.append(np.hstack(inter))
        # spline basis on selected columns
        cols = [c for c in spline_cols if c in Xf.columns]
        if cols:
            if fit:
                spline_tf = SplineTransformer(n_knots=n_knots, degree=3,
                                              include_bias=False)
                sp = spline_tf.fit_transform(Xf[cols].values)
            else:
                sp = spline_tf.transform(Xf[cols].values)
            blocks.append(sp)
    return np.hstack(blocks), spline_tf


def run_mode(df, features, augment, n_knots, first_year, last_year):
    rows = []
    for T in range(first_year, last_year + 1):
        tr = df[df['date'].dt.year <= T - 2]
        te = df[df['date'].dt.year == T]

        def prep(s):
            return s[features + ['bloom_28d', 'station_name', 'date']] \
                .dropna(subset=['bloom_28d'])
        tr, te = prep(tr), prep(te)
        if len(tr) == 0 or len(te) == 0 or te['bloom_28d'].sum() == 0:
            continue

        Xtr_raw, ytr = tr[features], tr['bloom_28d'].astype(int)
        Xte_raw = te[features]
        med = Xtr_raw.median()

        Dtr, sp_tf = build_design(Xtr_raw, med, features, SPLINE_COLS,
                                  INTERACTIONS, augment, n_knots, fit=True)
        Dte, _ = build_design(Xte_raw, med, features, SPLINE_COLS,
                              INTERACTIONS, augment, n_knots,
                              spline_tf=sp_tf, fit=False)

        scaler = StandardScaler()
        Dtr_s = scaler.fit_transform(Dtr)
        Dte_s = scaler.transform(Dte)

        model = LogisticRegression(class_weight='balanced', C=0.05,
                                   max_iter=2000, random_state=42)
        model.fit(Dtr_s, ytr)
        p_te = model.predict_proba(Dte_s)[:, 1]

        for s, d, yt, pr in zip(te['station_name'].astype(str).values,
                                te['date'].values,
                                te['bloom_28d'].astype(int).values, p_te):
            rows.append({'station_name': s, 'date': d,
                         'y_true': int(yt), 'y_prob': float(pr)})
    return pd.DataFrame(rows)


def auc_ci(pooled, n_boot, seed):
    rng = np.random.default_rng(seed)
    year = pd.to_datetime(pooled['date']).dt.year.astype(str)
    key = pooled['station_name'].astype(str) + "_" + year
    groups = [np.array(v) for v in pooled.groupby(key).indices.values()]
    ncl = len(groups)
    yt, pr = pooled['y_true'].values, pooled['y_prob'].values
    aucs = []
    for _ in range(n_boot):
        idx = np.concatenate([groups[c] for c in rng.integers(0, ncl, size=ncl)])
        if len(np.unique(yt[idx])) > 1:
            aucs.append(roc_auc_score(yt[idx], pr[idx]))
    return np.array(aucs)


def paired_diff(pa, pb, n_boot, seed):
    m = pa.merge(pb, on=['station_name', 'date'], suffixes=('_a', '_b'))
    rng = np.random.default_rng(seed)
    year = pd.to_datetime(m['date']).dt.year.astype(str)
    key = m['station_name'].astype(str) + "_" + year
    groups = [np.array(v) for v in m.groupby(key).indices.values()]
    ncl = len(groups)
    yta, pra = m['y_true_a'].values, m['y_prob_a'].values
    ytb, prb = m['y_true_b'].values, m['y_prob_b'].values
    diffs = []
    for _ in range(n_boot):
        idx = np.concatenate([groups[c] for c in rng.integers(0, ncl, size=ncl)])
        if len(np.unique(yta[idx])) > 1 and len(np.unique(ytb[idx])) > 1:
            diffs.append(roc_auc_score(yta[idx], pra[idx]) -
                         roc_auc_score(ytb[idx], prb[idx]))
    return np.array(diffs), len(m)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--horizon", type=int, default=21)
    ap.add_argument("--n-knots", type=int, default=4)
    ap.add_argument("--first-test-year", type=int, default=2015)
    ap.add_argument("--last-test-year", type=int, default=2025)
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    df, features = build_dataset(clean_labels=False)
    df['bloom_28d'] = build_forward_label(df, horizon=args.horizon, threshold=10.0,
                                          sustained_only=False)

    print(f"\nRunning baseline (plain LR, {len(features)} features)...")
    base = run_mode(df, features, augment=False, n_knots=args.n_knots,
                    first_year=args.first_test_year, last_year=args.last_test_year)
    print(f"Running augmented (LR + splines on {len(SPLINE_COLS)} cols "
          f"+ {len(INTERACTIONS)} interactions)...")
    aug = run_mode(df, features, augment=True, n_knots=args.n_knots,
                   first_year=args.first_test_year, last_year=args.last_test_year)

    yb, ya = base['y_true'].values, aug['y_true'].values
    auc_b = roc_auc_score(yb, base['y_prob'].values)
    auc_a = roc_auc_score(ya, aug['y_prob'].values)
    cb = auc_ci(base, args.n_boot, args.seed)
    ca = auc_ci(aug, args.n_boot, args.seed)

    print("\n" + "=" * 66)
    print(f"SPLINE + INTERACTION TEST  (horizon {args.horizon}, n_knots {args.n_knots})")
    print("=" * 66)
    print(f"  baseline  AUC = {auc_b:.3f}  95% CI "
          f"[{np.percentile(cb, 2.5):.3f}, {np.percentile(cb, 97.5):.3f}]")
    print(f"  augmented AUC = {auc_a:.3f}  95% CI "
          f"[{np.percentile(ca, 2.5):.3f}, {np.percentile(ca, 97.5):.3f}]")

    diffs, nmatch = paired_diff(aug, base, args.n_boot, args.seed)
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    print(f"\n  PAIRED DIFFERENCE  augmented minus baseline  (matched {nmatch:,} rows)")
    print(f"  mean: {np.mean(diffs):+.3f}  95% CI [{lo:+.3f}, {hi:+.3f}]")
    print(f"  P(difference > 0): {np.mean(diffs > 0):.3f}")
    if lo > 0:
        print("  -> nonlinearity helps significantly. Keep the augmented features.")
    elif hi < 0:
        print("  -> augmented is significantly WORSE (overfit). Keep plain LR.")
    else:
        print("  -> not distinguishable. The linear model already captured the")
        print("     signal; this lever is closed. Keep plain LR for simplicity.")


if __name__ == "__main__":
    main()