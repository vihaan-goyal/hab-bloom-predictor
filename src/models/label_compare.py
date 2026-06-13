"""
label_compare.py
----------------
Verifies the "sustained label outperforms all-exceedances label" claim using the
SAME paired bootstrap as horizon_decomp.py (imported, not reimplemented), so the
method and clustering are identical and the result is consistent with the horizon
test already in the paper.

What it does, at one fixed horizon:
  1. builds pooled out-of-sample predictions under the ORIGINAL label
     (any exceedance) and under the SUSTAINED label (drops single-sample spikes),
  2. reports each one's marginal AUC / AUPRC with station-year bootstrap CIs,
  3. merges them on station_name+date and runs paired_diff_bootstrap to get
     AUC(sustained) - AUC(original) on the same resampled rows each draw.

IMPORTANT caveat (printed at the end too): unlike the horizon comparison, the two
labels define DIFFERENT positive sets. So the paired AUC difference answers "do the
sustained labels rank more cleanly?", NOT "same target, better scores". It is a
valid paired-resample statistic but it is a label-quality comparison, not a
same-target model comparison. Report it that way.

Also note: with sustained labels several folds have no positives and are skipped by
run_cv, so the paired comparison is restricted to the folds where sustained had
positives (the printed 'matched rows' count). The original-label marginal AUC is
reported on its full pooled set for reference.

Run from repo root (place this file in src/models/):
    python src/models/label_compare.py
    python src/models/label_compare.py --horizon 21
    python src/models/label_compare.py --horizon 28 --sustain-window 14
"""

import argparse
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score

from rolling_origin_cv import build_dataset, run_cv
from label_utils import build_forward_label
# reuse the EXACT paired test + marginal bootstrap from the horizon script
from horizon_decomp import paired_diff_bootstrap, bootstrap_auc_ap


def pooled_for(df, features, horizon, sustained, t, fy, ly):
    df['bloom_28d'] = build_forward_label(
        df, horizon=horizon, threshold=10.0, sustained_only=sustained)
    return run_cv(df, features, fy, ly,
                  threshold_mode='fixed', fixed_threshold=t,
                  min_hist_pos=20, min_val_pos=5, verbose=False)


def marginal(pooled, n_boot, seed, label):
    yt = pooled['y_true'].values
    pr = pooled['y_prob'].values
    n, npos = len(yt), int(yt.sum())
    auc = roc_auc_score(yt, pr) if len(np.unique(yt)) > 1 else np.nan
    apr = average_precision_score(yt, pr)
    aucs, aps = bootstrap_auc_ap(pooled, n_boot, seed)
    auc_lo, auc_hi = np.percentile(aucs, [2.5, 97.5])
    ap_lo, ap_hi = np.percentile(aps, [2.5, 97.5])
    print(f"\n{label}")
    print(f"  pooled rows: {n:,}   positives: {npos}   base rate: {npos/n*100:.1f}%")
    print(f"  AUC   = {auc:.3f}   95% CI [{auc_lo:.3f}, {auc_hi:.3f}]")
    print(f"  AUPRC = {apr:.3f}   95% CI [{ap_lo:.3f}, {ap_hi:.3f}]   "
          f"(no-skill = {npos/n:.3f})")
    return auc, apr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--horizon", type=int, default=28,
                    help="horizon for the comparison; the original claim's 0.815 "
                         "baseline was the 28d original label")
    ap.add_argument("--sustain-window", type=int, default=14)
    ap.add_argument("--first-test-year", type=int, default=2015)
    ap.add_argument("--last-test-year", type=int, default=2025)
    ap.add_argument("--threshold", type=float, default=0.60)
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    df, features = build_dataset(clean_labels=False)

    print("=" * 70)
    print(f"LABEL COMPARISON  (sustained vs original)  horizon={args.horizon}d")
    print("=" * 70)

    pooled_orig = pooled_for(df, features, args.horizon, False,
                             args.threshold, args.first_test_year, args.last_test_year)
    pooled_sust = pooled_for(df, features, args.horizon, True,
                             args.threshold, args.first_test_year, args.last_test_year)
    if pooled_orig.empty or pooled_sust.empty:
        print("one of the label conditions produced no folds; aborting.")
        return

    auc_o, ap_o = marginal(pooled_orig, args.n_boot, args.seed,
                           "ORIGINAL label (any exceedance)")
    auc_s, ap_s = marginal(pooled_sust, args.n_boot, args.seed,
                           "SUSTAINED label (drops single-sample spikes)")

    # paired AUC difference on common station-date rows (sustained minus original)
    diffs, nmatch = paired_diff_bootstrap(pooled_sust, pooled_orig,
                                          args.n_boot, args.seed)
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    print("\n" + "=" * 70)
    print("PAIRED AUC DIFFERENCE  sustained minus original")
    print("=" * 70)
    print(f"  matched rows: {nmatch:,}  "
          f"(folds where sustained had >=1 positive)")
    print(f"  mean difference: {np.mean(diffs):+.3f}  95% CI [{lo:+.3f}, {hi:+.3f}]")
    print(f"  P(difference > 0): {np.mean(diffs > 0):.3f}")
    if lo > 0:
        print("  -> sustained labels rank significantly more cleanly. Claim holds.")
    elif hi < 0:
        print("  -> original labels rank significantly better.")
    else:
        print("  -> not distinguishable; soften 'significantly outperforms' to")
        print("     'comparable AUC; sustained chosen for label robustness'.")

    print("\nCAVEAT: the two labels define DIFFERENT positive sets, so this is a")
    print("label-quality comparison (do sustained labels rank more cleanly), NOT a")
    print("same-target model comparison. Report it that way. Also: precision/AUPRC")
    print("favor the higher-base-rate label, so 'better AUC' need not mean 'better")
    print("precision' -- check the marginal AUPRC lines above before claiming a win.")


if __name__ == "__main__":
    main()