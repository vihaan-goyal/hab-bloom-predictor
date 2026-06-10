"""
horizon_decomp.py
-----------------
Tests whether shorter forecast horizons are more predictable than the pooled
28-day label. The 28-day binary lumps near-term blooms (strong signal) with
far-term ones (weak signal); splitting by horizon shows where the signal actually
lives, and the near-term head is also the operationally useful one for an aeration
response.

Also reports the honest precision summary that a single threshold cannot give:
  - AUPRC (area under precision-recall, threshold-free, baseline = base rate)
  - precision in the high-confidence slice (top 10% / top 5% of probabilities),
    which is the correct design for an alert system that should fire rarely and
    be right when it does.

Features are built ONCE; only the label horizon changes per loop.

Run from repo root:
    python src/models/horizon_decomp.py
    python src/models/horizon_decomp.py --horizons 3 7 14 21 28
"""

import argparse
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score

from rolling_origin_cv import build_dataset, run_cv
from label_utils import build_forward_label


def precision_at_topk(y_true, y_prob, frac):
    """Precision among the top `frac` highest-probability predictions."""
    n = max(1, int(np.ceil(len(y_prob) * frac)))
    order = np.argsort(-y_prob)
    top = order[:n]
    sel = y_true[top]
    return sel.mean() if len(sel) else np.nan, int(sel.sum()), n


def precision_at_threshold(y_true, y_prob, t):
    pred = (y_prob >= t)
    if pred.sum() == 0:
        return np.nan, 0, 0
    return y_true[pred].mean(), int(y_true[pred].sum()), int(pred.sum())


def bootstrap_auc_ap(pooled, n_boot, seed):
    rng = np.random.default_rng(seed)
    year = pd.to_datetime(pooled['date']).dt.year.astype(str)
    key = pooled['station_name'].astype(str) + "_" + year
    groups = [np.array(v) for v in pooled.groupby(key).indices.values()]
    ncl = len(groups)
    yt = pooled['y_true'].values
    pr = pooled['y_prob'].values
    aucs, aps = [], []
    for _ in range(n_boot):
        idx = np.concatenate([groups[c] for c in rng.integers(0, ncl, size=ncl)])
        if len(np.unique(yt[idx])) < 2:
            continue
        aucs.append(roc_auc_score(yt[idx], pr[idx]))
        aps.append(average_precision_score(yt[idx], pr[idx]))
    return np.array(aucs), np.array(aps)


def paired_diff_bootstrap(pa, pb, n_boot, seed):
    """AUC(a) - AUC(b) on the SAME resampled rows each draw. Tight because the
    two horizons are correlated; far more sensitive than overlapping marginal CIs."""
    a = pa[['station_name', 'date', 'y_true', 'y_prob']]
    b = pb[['station_name', 'date', 'y_true', 'y_prob']]
    m = a.merge(b, on=['station_name', 'date'], suffixes=('_a', '_b'))
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
        if len(np.unique(yta[idx])) < 2 or len(np.unique(ytb[idx])) < 2:
            continue
        diffs.append(roc_auc_score(yta[idx], pra[idx]) -
                     roc_auc_score(ytb[idx], prb[idx]))
    return np.array(diffs), len(m)


def per_year_auc(pooled):
    """AUC per test year for one horizon, to check the sparse-gap confound."""
    out = []
    for y, g in pooled.groupby('fold'):
        yt, pr = g['y_true'].values, g['y_prob'].values
        auc = roc_auc_score(yt, pr) if len(np.unique(yt)) > 1 else np.nan
        out.append((int(y), int(yt.sum()), len(g), auc))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--horizons", type=int, nargs="+", default=[7, 14, 21, 28])
    ap.add_argument("--first-test-year", type=int, default=2015)
    ap.add_argument("--last-test-year", type=int, default=2025)
    ap.add_argument("--threshold", type=float, default=0.60)
    ap.add_argument("--compare", type=int, nargs=2, default=[21, 28],
                    help="two horizons for the paired AUC-difference bootstrap")
    ap.add_argument("--peryear", type=int, default=21,
                    help="horizon for the per-year AUC breakdown (confound check)")
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    df, features = build_dataset(clean_labels=False)

    pooled_by_h = {}
    summary = []
    for h in args.horizons:
        df['bloom_28d'] = build_forward_label(
            df, horizon=h, threshold=10.0, sustained_only=False)

        pooled = run_cv(df, features, args.first_test_year, args.last_test_year,
                        threshold_mode='fixed', fixed_threshold=args.threshold,
                        min_hist_pos=20, min_val_pos=5, verbose=False)
        if pooled.empty:
            continue
        pooled_by_h[h] = pooled

        yt = pooled['y_true'].values
        pr = pooled['y_prob'].values
        n, npos = len(yt), int(yt.sum())
        base = npos / n

        auc = roc_auc_score(yt, pr) if len(np.unique(yt)) > 1 else np.nan
        apr = average_precision_score(yt, pr)
        aucs, aps = bootstrap_auc_ap(pooled, args.n_boot, args.seed)
        auc_lo, auc_hi = np.percentile(aucs, [2.5, 97.5])
        ap_lo, ap_hi = np.percentile(aps, [2.5, 97.5])

        p60, tp60, n60 = precision_at_threshold(yt, pr, args.threshold)
        p10, tp10, n10 = precision_at_topk(yt, pr, 0.10)
        p05, tp05, n05 = precision_at_topk(yt, pr, 0.05)

        print("\n" + "=" * 70)
        print(f"HORIZON {h} DAYS")
        print("=" * 70)
        print(f"  pooled rows: {n:,}   positives: {npos}   base rate: {base*100:.1f}%")
        print(f"  AUC   = {auc:.3f}   95% CI [{auc_lo:.3f}, {auc_hi:.3f}]")
        print(f"  AUPRC = {apr:.3f}   95% CI [{ap_lo:.3f}, {ap_hi:.3f}]   "
              f"(no-skill = {base:.3f})")
        print(f"  precision @ t={args.threshold:.2f}: {p60:.3f}  ({tp60}/{n60})")
        print(f"  precision @ top 10%:   {p10:.3f}  ({tp10}/{n10})")
        print(f"  precision @ top 5%:    {p05:.3f}  ({tp05}/{n05})")

        summary.append({
            'horizon': h, 'pos': npos, 'base_rate': round(base, 3),
            'AUC': round(auc, 3), 'AUC_lo': round(auc_lo, 3), 'AUC_hi': round(auc_hi, 3),
            'AUPRC': round(apr, 3), 'AUPRC_lift': round(apr / base, 2),
            'prec_t60': round(p60, 3), 'prec_top10': round(p10, 3),
            'prec_top5': round(p05, 3),
        })

    print("\n" + "=" * 70)
    print("SUMMARY ACROSS HORIZONS")
    print("=" * 70)
    s = pd.DataFrame(summary)
    print(s.to_string(index=False))
    s.to_csv("data/horizon_decomp_summary.csv", index=False)
    print("\nSaved data/horizon_decomp_summary.csv")

    # ---- paired horizon-difference bootstrap ----
    ha, hb = args.compare
    if ha in pooled_by_h and hb in pooled_by_h:
        diffs, nmatch = paired_diff_bootstrap(
            pooled_by_h[ha], pooled_by_h[hb], args.n_boot, args.seed)
        lo, hi = np.percentile(diffs, [2.5, 97.5])
        print("\n" + "=" * 70)
        print(f"PAIRED AUC DIFFERENCE  horizon {ha} minus horizon {hb}")
        print("=" * 70)
        print(f"  matched rows: {nmatch:,}")
        print(f"  mean difference: {np.mean(diffs):+.3f}  95% CI [{lo:+.3f}, {hi:+.3f}]")
        print(f"  P(difference > 0): {np.mean(diffs > 0):.3f}")
        if lo > 0:
            print(f"  -> horizon {ha} ranks significantly better than {hb}. Lock {ha}.")
        elif hi < 0:
            print(f"  -> horizon {hb} ranks significantly better than {ha}.")
        else:
            print(f"  -> not distinguishable; the two horizons rank equally well.")

    # ---- per-year AUC at the chosen horizon (confound check) ----
    if args.peryear in pooled_by_h:
        print("\n" + "=" * 70)
        print(f"PER-YEAR AUC  at horizon {args.peryear}  "
              f"(check vs sparse-gap years 2020/2021/2023/2025)")
        print("=" * 70)
        print(f"  {'year':>5}  {'pos':>4}  {'n':>5}  {'AUC':>6}")
        print("  " + "-" * 26)
        for y, pos, n, auc in per_year_auc(pooled_by_h[args.peryear]):
            astr = f"{auc:.3f}" if not np.isnan(auc) else "  nan"
            print(f"  {y:>5}  {pos:>4}  {n:>5}  {astr:>6}")
        print("\n  If the well-sampled years (2019, 2024) hold high AUC at this")
        print("  horizon, the horizon gain is real, not a sparse-year artifact.")

    print("\nRead: if AUC and AUPRC rise as horizon shrinks, the near-term head is")
    print("your real forecasting product. 'AUPRC_lift' is AUPRC over the no-skill")
    print("base rate; >1 means real precision signal. 'prec_top5' is the precision")
    print("you can advertise for a rare-but-confident alert mode.")


if __name__ == "__main__":
    main()