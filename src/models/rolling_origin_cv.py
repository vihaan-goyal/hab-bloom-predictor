"""
rolling_origin_cv.py
--------------------
Powered evaluation for the locked HAB pipeline.

Problem this solves: the single 2023-2025 test block has only ~74 bloom positives,
so every metric has a 95% CI of roughly +/- 0.13. No feature or model change of a
few points can be resolved above that noise.

Fix: expanding-window rolling-origin CV restricted to the post-2014 low-nitrogen
regime. For each test year T:
    train  = all years <= T-2
    val    = year T-1            (used ONLY to pick the decision threshold)
    test   = year T              (out-of-sample, never seen)
The year T-1 validation buffer also embargoes the 28-day forward label, so a test
row's label window cannot overlap the training data.

Pooling every fold's out-of-sample test predictions turns ~74 positives into several
hundred, which is the only way a 2-3 point improvement becomes distinguishable from
zero. Threshold is chosen on val each fold (no test leakage), unlike the single-split
script which maximized F1 on the test set itself.

Reuses the EXACT feature engineering and label definition from
final_evaluation_threshold_sweep.py so results are directly comparable.

Run from repo root:
    python src/models/rolling_origin_cv.py
    python src/models/rolling_origin_cv.py --first-test-year 2015 --last-test-year 2025
"""

import argparse
import glob
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score

from label_utils import build_forward_label


# ===========================================================================
# Dataset build  (faithful copy of the locked pipeline)
# ===========================================================================

FEATURES_ALL = [
    'Chlorophyll', 'chl_lag1', 'chl_lag2', 'chl_lag3', 'chl_lag4',
    'chl_roll3_mean', 'chl_roll6_mean', 'chl_roll9_mean',
    'chl_roll14_mean', 'chl_roll21_mean', 'chl_trend',
    'chl_anomaly', 'chl_climatology',
    'do_lag1', 'temp_lag1', 'sal_lag1',
    'sal_lag2', 'sal_lag3', 'sal_lag4',
    'sea_water_temperature', 'sea_water_salinity',
    'oxygen_concentration_in_sea_water',
    'month', 'latitude_x', 'longitude_x',
    'nox_lag2', 'dip_lag2', 'dip_change', 'dip_x_month',
    'neighbor_chl3_mean', 'neighbor_chl3_lag1',
    'tidal_gt_anom', 'tidal_msl_anom',
    'percent_saturation',
    'max_gust_3d',
]


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


def build_dataset(clean_labels=False, sustain_window=14, horizon=28):
    print("Loading data/hab_features_tidal.csv...")
    df = pd.read_csv("data/hab_features_tidal.csv")
    df['date'] = pd.to_datetime(df['date'])

    if 'percent_saturation' not in df.columns:
        print("Merging percent_saturation...")
        ps = load_percent_saturation()
        df['station_name'] = df['station_name'].astype(str)
        df = df.merge(ps, on=['date', 'station_name'], how='left')

    print("Merging max_gust_3d...")
    gust = pd.read_csv("data/gust_features_daily.csv",
                       usecols=['date', 'max_gust_3d'])
    gust['date'] = pd.to_datetime(gust['date'])
    df = df.merge(gust, on='date', how='left')

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

    # bloom_28d via shared builder. clean_labels=True restricts positives to
    # SUSTAINED exceedances (drops single-sample spikes). clean_labels=False
    # reproduces the locked label exactly.
    label_kind = "SUSTAINED-only" if clean_labels else "original (any exceedance)"
    print(f"Building forward label: {label_kind}, horizon={horizon}d "
          f"(column name stays 'bloom_28d')")
    # never inherit a pre-baked / frozen label from the CSV
    df = df.drop(columns=[c for c in ('bloom_28d', 'is_sustained', 'is_exceedance')
                          if c in df.columns])
    df['bloom_28d'] = build_forward_label(
        df, horizon=horizon, threshold=10.0,
        sustained_only=clean_labels, sustain_window=sustain_window)

    features = [f for f in FEATURES_ALL if f in df.columns]
    return df, features


# ===========================================================================
# Metrics
# ===========================================================================

def prf_from_arrays(y_true, y_pred):
    tp = int(np.sum((y_pred == 1) & (y_true == 1)))
    fp = int(np.sum((y_pred == 1) & (y_true == 0)))
    fn = int(np.sum((y_pred == 0) & (y_true == 1)))
    p = tp / (tp + fp) if (tp + fp) > 0 else np.nan
    r = tp / (tp + fn) if (tp + fn) > 0 else np.nan
    if np.isnan(p) or np.isnan(r) or (p + r) == 0:
        f = np.nan
    else:
        f = 2 * p * r / (p + r)
    return p, r, f, tp, fp, fn


def pick_threshold(y_val, p_val, grid):
    # choose threshold maximizing val F1; this is the no-leak operating point
    best_t, best_f = 0.50, -1.0
    for t in grid:
        _, _, f, _, _, _ = prf_from_arrays(y_val, (p_val >= t).astype(int))
        if not np.isnan(f) and f > best_f:
            best_f, best_t = f, t
    return best_t


# ===========================================================================
# Rolling-origin loop
# ===========================================================================

def run_cv(df, features, first_test_year, last_test_year,
           threshold_mode, fixed_threshold, min_hist_pos, min_val_pos,
           verbose=True):
    grid = np.arange(0.10, 0.91, 0.05)
    pooled = []
    acc_y_true = []   # accumulated OOS truths from EARLIER folds (walk-forward)
    acc_y_prob = []   # genuinely causal: only years < T are ever in here

    if verbose:
        print("\n" + "=" * 84)
        print(f"ROLLING-ORIGIN CV  (train <= T-2,  test = T)   threshold_mode={threshold_mode}")
        print("=" * 84)
        print(f"{'TestYr':>6}  {'nTrain':>7}  {'nTest':>6}  {'pos':>4}  "
              f"{'thr':>5}  {'src':>4}  {'prec':>5}  {'rec':>5}  {'F1':>5}  {'AUC':>5}")
        print("-" * 84)

    for T in range(first_test_year, last_test_year + 1):
        tr = df[df['date'].dt.year <= T - 2]
        va = df[df['date'].dt.year == T - 1]
        te = df[df['date'].dt.year == T]

        def prep(split):
            return split[features + ['bloom_28d', 'station_name', 'date']] \
                .dropna(subset=['bloom_28d'])
        tr, va, te = prep(tr), prep(va), prep(te)
        if len(tr) == 0 or len(te) == 0 or te['bloom_28d'].sum() == 0:
            if verbose:
                print(f"{T:>6}  skipped (no train/test rows or no test positives)")
            continue

        Xtr, ytr = tr[features], tr['bloom_28d'].astype(int)
        Xte, yte = te[features], te['bloom_28d'].astype(int).values

        med = Xtr.median()
        scaler = StandardScaler()
        Xtr_s = scaler.fit_transform(Xtr.fillna(med))
        Xte_s = scaler.transform(Xte.fillna(med))

        model = LogisticRegression(class_weight='balanced', C=0.05,
                                   max_iter=1000, random_state=42)
        model.fit(Xtr_s, ytr)
        p_te = model.predict_proba(Xte_s)[:, 1]

        # ---- choose operating threshold ----
        if threshold_mode == 'fixed':
            t_star, src = fixed_threshold, 'fix'
        elif threshold_mode == 'val':
            if len(va) > 0 and va['bloom_28d'].sum() >= min_val_pos:
                p_va = model.predict_proba(
                    scaler.transform(va[features].fillna(med)))[:, 1]
                t_star = pick_threshold(va['bloom_28d'].astype(int).values, p_va, grid)
                src = 'val'
            else:
                t_star, src = 0.50, 'def'
        else:  # walkforward: pick on pooled OOS predictions from years < T
            if int(np.sum(acc_y_true)) >= min_hist_pos:
                t_star = pick_threshold(np.array(acc_y_true),
                                        np.array(acc_y_prob), grid)
                src = 'wf'
            else:
                t_star, src = 0.50, 'def'

        y_pred = (p_te >= t_star).astype(int)
        p, r, f, tp, fp, fn = prf_from_arrays(yte, y_pred)
        auc = roc_auc_score(yte, p_te) if len(np.unique(yte)) > 1 else np.nan

        for s, d, yt, yp, pr in zip(te['station_name'].astype(str).values,
                                    te['date'].values, yte, y_pred, p_te):
            pooled.append({'station_name': s, 'date': d, 'y_true': int(yt),
                           'y_pred': int(yp), 'y_prob': float(pr),
                           'fold': T, 'threshold': t_star})

        # update accumulator AFTER using it, so fold T only saw years < T
        acc_y_true.extend(yte.tolist())
        acc_y_prob.extend(p_te.tolist())

        fstr = f"{f:>5.3f}" if not np.isnan(f) else "  nan"
        if verbose:
            print(f"{T:>6}  {len(tr):>7,}  {len(te):>6,}  {int(yte.sum()):>4}  "
                  f"{t_star:>5.2f}  {src:>4}  {p:>5.3f}  {r:>5.3f}  {fstr}  {auc:>5.3f}")

    return pd.DataFrame(pooled)


# ===========================================================================
# Pooled bootstrap (clustered by station-year)
# ===========================================================================

def bootstrap_pooled(pooled, n_boot, seed):
    rng = np.random.default_rng(seed)
    df = pooled.reset_index(drop=True)
    year = pd.to_datetime(df['date']).dt.year.astype(str)
    key = df['station_name'].astype(str) + "_" + year
    groups = [np.array(v) for v in df.groupby(key).indices.values()]
    n_clusters = len(groups)
    yt_all = df['y_true'].values
    yp_all = df['y_pred'].values

    ps, rs, fs = [], [], []
    for _ in range(n_boot):
        chosen = rng.integers(0, n_clusters, size=n_clusters)
        idx = np.concatenate([groups[c] for c in chosen])
        p, r, f, _, _, _ = prf_from_arrays(yt_all[idx], yp_all[idx])
        if not np.isnan(f):
            ps.append(p); rs.append(r); fs.append(f)
    return np.array(ps), np.array(rs), np.array(fs)


def ci(name, arr):
    lo, hi = np.percentile(arr, [2.5, 97.5])
    print(f"  {name:<10} mean={np.mean(arr):.3f}  95% CI=[{lo:.3f}, {hi:.3f}]  "
          f"width={hi - lo:.3f}")


# ===========================================================================
# Main
# ===========================================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--first-test-year", type=int, default=2015)
    ap.add_argument("--last-test-year", type=int, default=2025)
    ap.add_argument("--threshold-mode", choices=["walkforward", "val", "fixed"],
                    default="walkforward",
                    help="walkforward: pick t on pooled OOS predictions from earlier "
                         "years (causal, stable). val: pick on year T-1 (thin, noisy). "
                         "fixed: use --fixed-threshold for every fold.")
    ap.add_argument("--fixed-threshold", type=float, default=0.50)
    ap.add_argument("--min-hist-pos", type=int, default=20,
                    help="walkforward: min accumulated positives before trusting the "
                         "pooled threshold; until then use 0.50")
    ap.add_argument("--min-val-pos", type=int, default=5,
                    help="val mode: min positives in year T-1 to trust its threshold")
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default="data/cv_predictions.csv")
    ap.add_argument("--clean-labels", action="store_true",
                    help="restrict bloom positives to sustained exceedances")
    ap.add_argument("--sustain-window", type=int, default=14)
    ap.add_argument("--horizon", type=int, default=28,
                    help="forward label horizon in days (paper headline is 21)")
    args = ap.parse_args()

    df, features = build_dataset(clean_labels=args.clean_labels,
                                 sustain_window=args.sustain_window,
                                 horizon=args.horizon)
    print(f"Using {len(features)} features. Rows with labels: "
          f"{df['bloom_28d'].notna().sum():,}")

    pooled = run_cv(df, features, args.first_test_year, args.last_test_year,
                    args.threshold_mode, args.fixed_threshold,
                    args.min_hist_pos, args.min_val_pos)
    if pooled.empty:
        print("No folds produced predictions.")
        return

    n = len(pooled)
    npos = int(pooled['y_true'].sum())
    p, r, f, tp, fp, fn = prf_from_arrays(pooled['y_true'].values,
                                          pooled['y_pred'].values)

    print("\n" + "=" * 78)
    print("POOLED OUT-OF-SAMPLE RESULT  (per-fold val thresholds applied)")
    print("=" * 78)
    print(f"  pooled rows: {n:,}   positives: {npos}   "
          f"(single-split had ~74)")
    print(f"  TP={tp}  FP={fp}  FN={fn}")
    print(f"  precision={p:.3f}  recall={r:.3f}  f1={f:.3f}")
    try:
        auc = roc_auc_score(pooled['y_true'].values, pooled['y_prob'].values)
        print(f"  pooled AUC={auc:.3f}")
    except ValueError:
        pass

    print(f"\nPOOLED BOOTSTRAP  ({args.n_boot} resamples, cluster=station_year)")
    bp, br, bf = bootstrap_pooled(pooled, args.n_boot, args.seed)
    ci("precision", bp)
    ci("recall", br)
    ci("f1", bf)

    pooled.to_csv(args.out, index=False)
    print(f"\nSaved {args.out}")
    print("\nHow to read it:")
    print("  Compare this F1 CI width to the single-split width (~0.26).")
    print("  If it shrinks to ~0.10-0.13, you now have the power to test the label")
    print("  audit and the A4 regime feature: rerun this harness with each change")
    print("  and a non-overlapping CI is a real effect.")


if __name__ == "__main__":
    main()