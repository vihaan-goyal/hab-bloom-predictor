"""
regime_test.py
--------------
Tests the one idea this whole investigation was originally built around: detect the
post-TMDL nitrogen regime at A4 from the data itself, rather than predicting nutrients.

Feature: trailing decoupling ratio. At station s, time t, the fraction of recent
high-chlorophyll days that did NOT go on to bloom. As nitrogen depletes, high CHL
stops producing blooms, so this ratio climbs at A4 specifically.

LEAKAGE CONTROL (critical, given prior bug history): the label looks `horizon` days
forward, so a day's outcome is only resolved `horizon` days later. The trailing
window therefore ENDS at t - horizon, never at t. This embargo is baked into the
feature so it cannot peek at the same future the label encodes.

Tested two ways at horizon 21, paired against the locked baseline on identical rows:
  network-wide  (does the feature help pooled AUC across all stations)
  A4-only       (does it help on the A4 false-positive cluster specifically)

Run from repo root:
    python src/models/regime_test.py
    python src/models/regime_test.py --lookback 365 --threshold 10
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


def compute_decoupling(df, horizon, lookback, threshold, min_count):
    """Trailing fraction of high-CHL days (in [t-h-lookback, t-h]) that did NOT
    bloom. Window ends at t-horizon so every label used is fully resolved by t."""
    df = df.sort_values(['station_name', 'date']).copy()
    ratio = np.full(len(df), np.nan)
    h = np.timedelta64(horizon, 'D')
    L = np.timedelta64(lookback, 'D')
    pos = 0
    for _, grp in df.groupby('station_name'):
        dates = grp['date'].values
        chl = grp['Chlorophyll'].values
        label = grp['bloom_28d'].values
        high = chl > threshold
        local = np.full(len(grp), np.nan)
        for i in range(len(grp)):
            end = dates[i] - h
            start = end - L
            win = (dates >= start) & (dates <= end) & high
            if int(win.sum()) >= min_count:
                local[i] = float(np.mean(1 - label[win]))
        ratio[pos:pos + len(grp)] = local
        pos += len(grp)
    df['decouple_ratio'] = ratio
    return df


def run_pipeline(df, feats, first_year, last_year):
    rows = []
    for T in range(first_year, last_year + 1):
        tr = df[df['date'].dt.year <= T - 2]
        te = df[df['date'].dt.year == T]

        def prep(s):
            return s[feats + ['bloom_28d', 'station_name', 'date']] \
                .dropna(subset=['bloom_28d'])
        tr, te = prep(tr), prep(te)
        if len(tr) == 0 or len(te) == 0 or te['bloom_28d'].sum() == 0:
            continue

        Xtr, ytr = tr[feats], tr['bloom_28d'].astype(int)
        med = Xtr.median()
        scaler = StandardScaler()
        model = LogisticRegression(class_weight='balanced', C=0.05,
                                   max_iter=2000, random_state=42)
        model.fit(scaler.fit_transform(Xtr.fillna(med)), ytr)
        p_te = model.predict_proba(scaler.transform(te[feats].fillna(med)))[:, 1]
        for s, d, yt, pr in zip(te['station_name'].astype(str).values,
                                te['date'].values,
                                te['bloom_28d'].astype(int).values, p_te):
            rows.append({'station_name': s, 'date': d,
                         'y_true': int(yt), 'y_prob': float(pr)})
    return pd.DataFrame(rows)


def auc_pt(pooled):
    yt, pr = pooled['y_true'].values, pooled['y_prob'].values
    return roc_auc_score(yt, pr) if len(np.unique(yt)) > 1 else np.nan


def paired_diff(pa, pb, n_boot, seed, subset_station=None):
    m = pa.merge(pb, on=['station_name', 'date'], suffixes=('_a', '_b'))
    if subset_station is not None:
        m = m[m['station_name'].astype(str) == subset_station]
    if len(m) == 0:
        return np.array([]), 0, np.nan, np.nan
    rng = np.random.default_rng(seed)
    year = pd.to_datetime(m['date']).dt.year.astype(str)
    key = m['station_name'].astype(str) + "_" + year
    groups = [np.array(v) for v in m.groupby(key).indices.values()]
    ncl = len(groups)
    yta, pra = m['y_true_a'].values, m['y_prob_a'].values
    ytb, prb = m['y_true_b'].values, m['y_prob_b'].values
    auc_a = roc_auc_score(yta, pra) if len(np.unique(yta)) > 1 else np.nan
    auc_b = roc_auc_score(ytb, prb) if len(np.unique(ytb)) > 1 else np.nan
    diffs = []
    for _ in range(n_boot):
        idx = np.concatenate([groups[c] for c in rng.integers(0, ncl, size=ncl)])
        if len(np.unique(yta[idx])) > 1 and len(np.unique(ytb[idx])) > 1:
            diffs.append(roc_auc_score(yta[idx], pra[idx]) -
                         roc_auc_score(ytb[idx], prb[idx]))
    return np.array(diffs), len(m), auc_a, auc_b


def report(title, diffs, n, auc_a, auc_b):
    print("\n" + "=" * 66)
    print(title)
    print("=" * 66)
    print(f"  matched rows: {n:,}")
    print(f"  augmented (with regime feature) AUC = {auc_a:.3f}")
    print(f"  baseline                        AUC = {auc_b:.3f}")
    if len(diffs) == 0:
        print("  too few rows/positives for a difference CI.")
        return
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    print(f"  paired difference: {np.mean(diffs):+.3f}  95% CI [{lo:+.3f}, {hi:+.3f}]")
    print(f"  P(difference > 0): {np.mean(diffs > 0):.3f}")
    if lo > 0:
        print("  -> regime feature helps significantly here.")
    elif hi < 0:
        print("  -> regime feature hurts here.")
    else:
        print("  -> not distinguishable; feature does not help.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--horizon", type=int, default=21)
    ap.add_argument("--lookback", type=int, default=365)
    ap.add_argument("--threshold", type=float, default=10.0)
    ap.add_argument("--min-count", type=int, default=3)
    ap.add_argument("--a4-name", default="A4")
    ap.add_argument("--first-test-year", type=int, default=2015)
    ap.add_argument("--last-test-year", type=int, default=2025)
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    df, features = build_dataset(clean_labels=False)
    df['bloom_28d'] = build_forward_label(df, horizon=args.horizon, threshold=10.0,
                                          sustained_only=False)
    df = compute_decoupling(df, args.horizon, args.lookback,
                            args.threshold, args.min_count)
    cov = df['decouple_ratio'].notna().mean()
    print(f"\ndecouple_ratio coverage: {cov*100:.1f}% of rows "
          f"(embargo {args.horizon}d, lookback {args.lookback}d)")

    base = run_pipeline(df, features, args.first_test_year, args.last_test_year)
    aug = run_pipeline(df, features + ['decouple_ratio'],
                       args.first_test_year, args.last_test_year)

    d_net, n_net, a_net, b_net = paired_diff(aug, base, args.n_boot, args.seed)
    report(f"NETWORK-WIDE  (horizon {args.horizon}, regime feature)",
           d_net, n_net, a_net, b_net)

    d_a4, n_a4, a_a4, b_a4 = paired_diff(aug, base, args.n_boot, args.seed,
                                         subset_station=args.a4_name)
    report(f"A4-ONLY  (station {args.a4_name})", d_a4, n_a4, a_a4, b_a4)


if __name__ == "__main__":
    main()