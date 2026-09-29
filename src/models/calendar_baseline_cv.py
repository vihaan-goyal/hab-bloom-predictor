"""
calendar_baseline_cv.py -- does the locked 21-day model beat a calendar forecast? (pre-registered)
====================================================================================================
Implements notes/CALENDAR_BASELINE_PREREG.md exactly. Compares the walk-forward out-of-fold
predictions (data/cv_predictions.csv from rolling_origin_cv.py --horizon 21) with a station-month
calendar forecast built, for each fold year T, only from rows dated before T - 21 days.

Run from repo root:  python src/models/calendar_baseline_cv.py
"""
import os
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from label_utils import forward_window_label  # noqa: E402

FEATURES_CSV = os.environ.get("HAB_FEATURES_CSV", "data/hab_features_tidal_S1.csv")
CV_PREDS = "data/cv_predictions.csv"
HORIZON, MIN_ROWS, N_BOOT, SEED, TOP_FRAC = 21, 5, 2000, 42, 0.10


def labelled_history():
    df = pd.read_csv(FEATURES_CSV, usecols=["station_name", "date", "Chlorophyll"],
                     dtype={"station_name": str})
    df["date"] = pd.to_datetime(df.date)
    df = df.sort_values(["station_name", "date"]).reset_index(drop=True)
    df["y"] = np.nan
    for _, g in df.groupby("station_name"):
        df.loc[g.index, "y"] = forward_window_label(g.date.values, g.Chlorophyll.values > 10, HORIZON)
    df = df.dropna(subset=["y"])
    df["month"] = df.date.dt.month
    return df


def calendar_forecast(cv, hist):
    out = np.full(len(cv), np.nan)
    for T, rows in cv.groupby("fold"):
        past = hist[hist.date < pd.Timestamp(f"{T}-01-01") - pd.Timedelta(days=HORIZON)]
        sm = past.groupby(["station_name", "month"]).y.agg(["mean", "size"])
        mo = past.groupby("month").y.agg(["mean", "size"])
        overall = past.y.mean()
        for i, (s, m) in zip(rows.index, zip(rows.station_name, rows.date.dt.month)):
            if (s, m) in sm.index and sm.loc[(s, m), "size"] >= MIN_ROWS:
                out[i] = sm.loc[(s, m), "mean"]
            elif m in mo.index and mo.loc[m, "size"] >= MIN_ROWS:
                out[i] = mo.loc[m, "mean"]
            else:
                out[i] = overall
    return out


def paired_boot(y, p, c, keys, rng):
    groups = [np.where(keys == k)[0] for k in pd.unique(keys)]
    diffs = []
    for _ in range(N_BOOT):
        b = np.concatenate([groups[i] for i in rng.integers(0, len(groups), len(groups))])
        if 0 < y[b].sum() < len(b):
            diffs.append(roc_auc_score(y[b], p[b]) - roc_auc_score(y[b], c[b]))
    return np.array(diffs)


def top_frac_lift(y, s, folds):
    hits = alerts = 0
    for f in np.unique(folds):
        m = folds == f
        k = max(1, int(round(TOP_FRAC * m.sum())))
        idx = np.argsort(-s[m], kind="stable")[:k]
        hits += y[m][idx].sum(); alerts += k
    return (hits / alerts) / y.mean()


def report(tag, cv, rng):
    y, p, c = cv.y_true.values.astype(int), cv.y_prob.values, cv.cal.values
    keys = (cv.station_name + "_" + cv.date.dt.year.astype(str)).values
    d = paired_boot(y, p, c, keys, rng)
    am, ac = roc_auc_score(y, p), roc_auc_score(y, c)
    print(f"{tag}: rows {len(y)}, events {y.sum()} | model AUC {am:.3f}, calendar AUC {ac:.3f}, "
          f"difference {am - ac:+.3f} [{np.percentile(d, 2.5):+.3f}, {np.percentile(d, 97.5):+.3f}], "
          f"one-sided p = {(d <= 0).mean():.3f}")
    print(f"   lift at top {TOP_FRAC:.0%} per fold: model {top_frac_lift(y, p, cv.fold.values):.2f}, "
          f"calendar {top_frac_lift(y, c, cv.fold.values):.2f}")


def main():
    rng = np.random.default_rng(SEED)
    cv = pd.read_csv(CV_PREDS, dtype={"station_name": str}, parse_dates=["date"]).reset_index(drop=True)
    cv["cal"] = calendar_forecast(cv, labelled_history())
    print("PRIMARY (all folds, 2016-2025):")
    report("  pooled", cv, rng)
    print("Per fold (AUC model - calendar):")
    wins = 0
    for T, g in cv.groupby("fold"):
        if 0 < g.y_true.sum() < len(g):
            dlt = roc_auc_score(g.y_true, g.y_prob) - roc_auc_score(g.y_true, g.cal)
            wins += dlt > 0
            print(f"  {T}: events {int(g.y_true.sum()):>3}  {dlt:+.3f}")
    print(f"  model wins {wins} folds")
    print("SECONDARY (2023-25 folds):")
    report("  2023-25", cv[cv.fold >= 2023].reset_index(drop=True), rng)


if __name__ == "__main__":
    main()
