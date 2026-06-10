"""
bootstrap_ci.py
---------------
Confidence intervals for test-set precision / recall / F1 on the locked HAB pipeline.

This is model-agnostic: it consumes saved test predictions, so it works whether the
predictions came from the locked Logistic Regression or anything else. You only need a
CSV with one row per test station-day and these columns:

    station_name, date, y_true, y_prob

To produce that CSV from your existing evaluation script, add this right after you
compute `probs` on the test set:

    import pandas as pd
    pd.DataFrame({
        "station_name": test_stations,          # station label aligned to X_test rows
        "date":         test_dates,             # date aligned to X_test rows
        "y_true":       y_test.values,
        "y_prob":       probs,
    }).to_csv("data/test_predictions.csv", index=False)

Two operating points are supported:
    --mode global       single threshold for every station (default t=0.60)
    --mode perstation   per-station thresholds from data/station_thresholds.csv
                        (Strategy B). Rows whose station is missing fall back to
                        the global threshold.

Two resampling schemes:
    --cluster station_year   resample whole station-years with replacement (default).
                            Respects within-station temporal autocorrelation, so the
                            CIs are honest (wider) rather than artificially tight.
    --cluster station        resample whole stations.
    --cluster none           naive iid row resample. Reports the OVER-optimistic CI.
                            Useful only to show how much autocorrelation inflates
                            naive confidence.

Usage:
    python bootstrap_ci.py --preds data/test_predictions.csv --mode global --threshold 0.60
    python bootstrap_ci.py --preds data/test_predictions.csv --mode perstation \
        --thresholds data/station_thresholds.csv --cluster station_year
    # western subset only (Strategy B headline number):
    python bootstrap_ci.py --preds data/test_predictions.csv --mode perstation \
        --thresholds data/station_thresholds.csv --stations C1,02,01,A4,B3
"""

import argparse
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def confusion(y_true, y_pred):
    tp = int(np.sum((y_pred == 1) & (y_true == 1)))
    fp = int(np.sum((y_pred == 1) & (y_true == 0)))
    fn = int(np.sum((y_pred == 0) & (y_true == 1)))
    tn = int(np.sum((y_pred == 0) & (y_true == 0)))
    return tp, fp, fn, tn


def prf(tp, fp, fn):
    # Returns (precision, recall, f1). NaN when undefined (no predicted or no actual positives).
    precision = tp / (tp + fp) if (tp + fp) > 0 else np.nan
    recall = tp / (tp + fn) if (tp + fn) > 0 else np.nan
    if np.isnan(precision) or np.isnan(recall) or (precision + recall) == 0:
        f1 = np.nan
    else:
        f1 = 2 * precision * recall / (precision + recall)
    return precision, recall, f1


def wilson(k, n, z=1.96):
    # Analytic Wilson interval for a proportion k/n. Cross-check on the bootstrap.
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half = (z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))) / denom
    return (center - half, center + half)


# ---------------------------------------------------------------------------
# Prediction
# ---------------------------------------------------------------------------

def apply_thresholds(df, mode, global_t, station_thresh):
    if mode == "global":
        return (df["y_prob"].values >= global_t).astype(int)
    # per-station: map station -> threshold, fall back to global
    t = df["station_name"].map(station_thresh).fillna(global_t).values
    return (df["y_prob"].values >= t).astype(int)


# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

def bootstrap(df, mode, global_t, station_thresh, cluster, n_boot, seed):
    rng = np.random.default_rng(seed)

    # Precompute predictions once; resampling only reshuffles which rows are counted.
    y_true_all = df["y_true"].values.astype(int)
    y_pred_all = apply_thresholds(df, mode, global_t, station_thresh)

    if cluster == "none":
        groups = None
        n_rows = len(df)
    else:
        if cluster == "station":
            key = df["station_name"].astype(str)
        elif cluster == "station_year":
            year = pd.to_datetime(df["date"]).dt.year.astype(str)
            key = df["station_name"].astype(str) + "_" + year
        else:
            raise ValueError(f"unknown cluster mode: {cluster}")
        # list of arrays of row indices, one per cluster
        groups = [idx.values for _, idx in df.groupby(key).groups.items()] \
            if False else [g for _, g in df.reset_index().groupby(key).groups.items()]
        # groupby.groups gives Index of original labels; convert to positional indices
        df_reset = df.reset_index(drop=True)
        if cluster == "station":
            keyr = df_reset["station_name"].astype(str)
        else:
            yr = pd.to_datetime(df_reset["date"]).dt.year.astype(str)
            keyr = df_reset["station_name"].astype(str) + "_" + yr
        groups = [np.array(v) for v in df_reset.groupby(keyr).indices.values()]
        y_true_all = df_reset["y_true"].values.astype(int)
        y_pred_all = apply_thresholds(df_reset, mode, global_t, station_thresh)
        n_clusters = len(groups)

    precisions, recalls, f1s = [], [], []
    undefined = 0

    for _ in range(n_boot):
        if cluster == "none":
            idx = rng.integers(0, n_rows, size=n_rows)
        else:
            chosen = rng.integers(0, n_clusters, size=n_clusters)
            idx = np.concatenate([groups[c] for c in chosen])

        yt = y_true_all[idx]
        yp = y_pred_all[idx]
        tp, fp, fn, tn = confusion(yt, yp)
        p, r, f = prf(tp, fp, fn)
        if np.isnan(f):
            undefined += 1
            continue
        precisions.append(p)
        recalls.append(r)
        f1s.append(f)

    return {
        "precision": np.array(precisions),
        "recall": np.array(recalls),
        "f1": np.array(f1s),
        "undefined": undefined,
    }


def summarize(name, samples):
    if len(samples) == 0:
        print(f"  {name:<10} no defined resamples")
        return
    lo, hi = np.percentile(samples, [2.5, 97.5])
    print(f"  {name:<10} mean={np.mean(samples):.3f}  95% CI=[{lo:.3f}, {hi:.3f}]  "
          f"width={hi - lo:.3f}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preds", default="data/test_predictions.csv")
    ap.add_argument("--mode", choices=["global", "perstation"], default="global")
    ap.add_argument("--threshold", type=float, default=0.60,
                    help="global threshold, and fallback for unmapped stations")
    ap.add_argument("--thresholds", default="data/station_thresholds.csv",
                    help="per-station thresholds CSV (perstation mode)")
    ap.add_argument("--stations", default=None,
                    help="comma-separated station subset, e.g. C1,02,01,A4,B3")
    ap.add_argument("--cluster", choices=["none", "station", "station_year"],
                    default="station_year")
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--save", default=None, help="optional CSV to dump bootstrap draws")
    args = ap.parse_args()

    df = pd.read_csv(args.preds)
    df["station_name"] = df["station_name"].astype(str)
    df["y_true"] = df["y_true"].astype(int)

    if args.stations:
        keep = [s.strip() for s in args.stations.split(",")]
        df = df[df["station_name"].isin(keep)].copy()
        print(f"Filtered to {len(keep)} stations: {keep}")

    station_thresh = {}
    if args.mode == "perstation":
        th = pd.read_csv(args.thresholds)
        # tolerant to column naming
        scol = "station" if "station" in th.columns else th.columns[0]
        tcol = "threshold" if "threshold" in th.columns else th.columns[-1]
        station_thresh = dict(zip(th[scol].astype(str), th[tcol].astype(float)))

    n_pos = int(df["y_true"].sum())
    print(f"\nTest rows: {len(df):,}   positives: {n_pos}   "
          f"base rate: {df['y_true'].mean()*100:.1f}%")
    if n_pos < 30:
        print(f"WARNING: only {n_pos} positive labels. Point metrics will have very "
              f"wide intervals. This is the whole reason to run this script.")

    # ---- point estimate ----
    y_true = df["y_true"].values.astype(int)
    y_pred = apply_thresholds(df, args.mode, args.threshold, station_thresh)
    tp, fp, fn, tn = confusion(y_true, y_pred)
    p, r, f = prf(tp, fp, fn)

    print("\nPOINT ESTIMATE")
    print(f"  TP={tp}  FP={fp}  FN={fn}  TN={tn}")
    print(f"  precision={p:.3f}  recall={r:.3f}  f1={f:.3f}")

    wp = wilson(tp, tp + fp)
    wr = wilson(tp, tp + fn)
    print(f"  Wilson 95% precision=[{wp[0]:.3f}, {wp[1]:.3f}]  "
          f"recall=[{wr[0]:.3f}, {wr[1]:.3f}]")

    # ---- bootstrap ----
    print(f"\nBOOTSTRAP  ({args.n_boot} resamples, cluster={args.cluster})")
    res = bootstrap(df, args.mode, args.threshold, station_thresh,
                    args.cluster, args.n_boot, args.seed)
    summarize("precision", res["precision"])
    summarize("recall", res["recall"])
    summarize("f1", res["f1"])
    if res["undefined"]:
        print(f"  ({res['undefined']} resamples dropped: no predicted/actual positives)")

    if args.save:
        pd.DataFrame({
            "precision": res["precision"],
            "recall": res["recall"][:len(res["precision"])],
            "f1": res["f1"][:len(res["precision"])],
        }).to_csv(args.save, index=False)
        print(f"\nSaved bootstrap draws to {args.save}")

    print("\nReading the result:")
    print("  If the F1 CI width is comparable to the gap between your rejected")
    print("  experiments and the baseline, those rejections are inside the noise")
    print("  band and 'mechanistic ceiling' should be stated as 'metrics are not")
    print("  distinguishable at this sample size' rather than 'no method helps'.")


if __name__ == "__main__":
    main()