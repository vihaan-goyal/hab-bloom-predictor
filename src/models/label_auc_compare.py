"""
label_auc_compare.py
--------------------
The clean test of the single-sample-noise hypothesis, free of the two confounds
in the earlier --clean-labels run (different test rows, different trained model).

Method: train ONE model per fold on the ORIGINAL label (the locked baseline), get
its probabilities on each test year, pool. Then on the IDENTICAL pooled rows compute
two AUCs from the SAME probabilities:
    AUC_orig  = how well the baseline ranking separates ALL exceedance positives
    AUC_clean = how well the SAME ranking separates SUSTAINED-only positives
Only the evaluation label changes. Rows and model are fixed, so the difference is
attributable to the label alone. Bootstrap (clustered by station-year) gives a CI on
the difference; if it excludes zero, single-sample positives are provably the harder,
ranking-degrading cases.

Run from repo root:
    python src/models/label_auc_compare.py
    python src/models/label_auc_compare.py --sustain-window 21
"""

import argparse
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score

from rolling_origin_cv import build_dataset
from label_utils import build_forward_label


def safe_auc(y, p):
    if len(np.unique(y)) < 2:
        return np.nan
    return roc_auc_score(y, p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--first-test-year", type=int, default=2015)
    ap.add_argument("--last-test-year", type=int, default=2025)
    ap.add_argument("--sustain-window", type=int, default=21)
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    # original label in bloom_28d, plus a parallel sustained-only column
    df, features = build_dataset(clean_labels=False)
    df['label_clean'] = build_forward_label(
        df, horizon=28, threshold=10.0,
        sustained_only=True, sustain_window=args.sustain_window)

    rows = []
    for T in range(args.first_test_year, args.last_test_year + 1):
        tr = df[df['date'].dt.year <= T - 2]
        te = df[df['date'].dt.year == T]

        def prep(s):
            return s[features + ['bloom_28d', 'label_clean',
                                 'station_name', 'date']].dropna(subset=['bloom_28d'])
        tr, te = prep(tr), prep(te)
        if len(tr) == 0 or len(te) == 0:
            continue

        Xtr, ytr = tr[features], tr['bloom_28d'].astype(int)
        med = Xtr.median()
        scaler = StandardScaler()
        model = LogisticRegression(class_weight='balanced', C=0.05,
                                   max_iter=1000, random_state=42)
        model.fit(scaler.fit_transform(Xtr.fillna(med)), ytr)
        p_te = model.predict_proba(scaler.transform(te[features].fillna(med)))[:, 1]

        for s, d, yo, yc, pr in zip(te['station_name'].astype(str).values,
                                    te['date'].values,
                                    te['bloom_28d'].astype(int).values,
                                    te['label_clean'].astype(int).values,
                                    p_te):
            rows.append({'station_name': s, 'date': d,
                         'y_orig': int(yo), 'y_clean': int(yc), 'y_prob': float(pr)})

    pooled = pd.DataFrame(rows)
    n = len(pooled)
    yo = pooled['y_orig'].values
    yc = pooled['y_clean'].values
    pr = pooled['y_prob'].values

    auc_o = safe_auc(yo, pr)
    auc_c = safe_auc(yc, pr)

    print("\n" + "=" * 66)
    print("FIXED-MODEL LABEL COMPARISON  (same rows, same probabilities)")
    print("=" * 66)
    print(f"  pooled rows: {n:,}")
    print(f"  positives original:  {int(yo.sum())}")
    print(f"  positives sustained: {int(yc.sum())}  "
          f"(sustain_window={args.sustain_window}d)")
    print(f"\n  AUC vs original labels:  {auc_o:.3f}")
    print(f"  AUC vs sustained labels: {auc_c:.3f}")
    print(f"  difference (clean - orig): {auc_c - auc_o:+.3f}")

    # ---- clustered bootstrap on the difference ----
    rng = np.random.default_rng(args.seed)
    year = pd.to_datetime(pooled['date']).dt.year.astype(str)
    key = pooled['station_name'].astype(str) + "_" + year
    groups = [np.array(v) for v in pooled.groupby(key).indices.values()]
    ncl = len(groups)

    do, dc, dd = [], [], []
    for _ in range(args.n_boot):
        idx = np.concatenate([groups[c] for c in rng.integers(0, ncl, size=ncl)])
        a_o = safe_auc(yo[idx], pr[idx])
        a_c = safe_auc(yc[idx], pr[idx])
        if not (np.isnan(a_o) or np.isnan(a_c)):
            do.append(a_o); dc.append(a_c); dd.append(a_c - a_o)
    do, dc, dd = np.array(do), np.array(dc), np.array(dd)

    def ci(name, arr):
        lo, hi = np.percentile(arr, [2.5, 97.5])
        print(f"  {name:<24} mean={np.mean(arr):+.3f}  95% CI=[{lo:+.3f}, {hi:+.3f}]")

    print(f"\n  BOOTSTRAP ({len(dd)} valid resamples, cluster=station_year)")
    ci("AUC original", do)
    ci("AUC sustained", dc)
    ci("difference (clean-orig)", dd)
    frac_pos = float(np.mean(dd > 0))
    print(f"\n  P(difference > 0) across resamples: {frac_pos:.3f}")
    if np.percentile(dd, 2.5) > 0:
        print("  -> CI on the difference excludes zero. The same ranking separates")
        print("     sustained blooms significantly better than all exceedances, so")
        print("     single-sample positives are provably the ranking-degrading cases.")
    else:
        print("  -> CI on the difference includes zero. Not distinguishable; the")
        print("     apparent AUC gain in the earlier run was the row/model confound.")


if __name__ == "__main__":
    main()