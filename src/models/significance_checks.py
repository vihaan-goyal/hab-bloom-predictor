"""
significance_checks.py -- is the 28-day model's test ranking better than chance and than the calendar?
=====================================================================================================
Reads the single-split test predictions written by final_evaluation_threshold_sweep.py
(data/test_predictions_S1.csv: station_name, date, y_true, y_prob) and reports, for AUC only
(no threshold, so none of these depend on a threshold choice):

  1. AUC with a station-year clustered bootstrap 95% CI.
  2. Block permutation null: each station's label series is circularly shifted by a random
     amount, keeping its base rate and autocorrelation. p = share of null AUCs >= observed.
  3. Within-station-year shift null: the same, but shifts stay inside each station-year, so the
     null keeps which station-years had blooms. Tests timing within a season.
  4. Month-of-year baseline: a station-month bloom rate computed on TRAINING years only
     (1993-2019, 28-day label, unresolved windows dropped), compared with the model by a paired
     station-year bootstrap of the AUC difference; one-sided p = share of differences <= 0.

Exploratory checks, not pre-registered. Run from repo root:
    python src/models/significance_checks.py [--preds data/test_predictions_S1.csv]
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from label_utils import forward_window_label  # noqa: E402

FEATURES_CSV = os.environ.get("HAB_FEATURES_CSV", "data/hab_features_tidal_S1.csv")
TRAIN_END = pd.Timestamp("2020-01-01") - pd.Timedelta(days=28)   # same purge as the eval
N_BOOT, N_PERM, SEED = 2000, 10000, 42


def cluster_index(keys):
    return [np.where(keys == k)[0] for k in pd.unique(keys)]


def boot(y, fn, clusters, rng, n=N_BOOT):
    out = []
    for _ in range(n):
        b = np.concatenate([clusters[i] for i in rng.integers(0, len(clusters), len(clusters))])
        if 0 < y[b].sum() < len(b):
            out.append(fn(b))
    return np.array(out)


def shift_null(y, p, groups, rng, n=N_PERM):
    null = np.empty(n)
    for k in range(n):
        yy = y.copy()
        for g in groups:
            if len(g) > 1:
                yy[g] = np.roll(y[g], rng.integers(1, len(g)))
        null[k] = roc_auc_score(yy, p)
    return null


def train_month_rates():
    df = pd.read_csv(FEATURES_CSV, usecols=["station_name", "date", "Chlorophyll"],
                     dtype={"station_name": str})
    df["date"] = pd.to_datetime(df.date)
    df = df.sort_values(["station_name", "date"]).reset_index(drop=True)
    df["y"] = np.nan
    for _, g in df.groupby("station_name"):
        df.loc[g.index, "y"] = forward_window_label(g.date.values, g.Chlorophyll.values > 10, 28)
    tr = df[(df.date <= TRAIN_END) & df.y.notna()]
    tr = tr.assign(month=tr.date.dt.month)
    return tr.groupby(["station_name", "month"]).y.mean(), tr.groupby("month").y.mean(), tr.y.mean()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preds", default="data/test_predictions_S1.csv")
    a = ap.parse_args()
    rng = np.random.default_rng(SEED)
    d = pd.read_csv(a.preds, dtype={"station_name": str})
    d["date"] = pd.to_datetime(d.date)
    d = d.sort_values(["station_name", "date"]).reset_index(drop=True)
    y, p = d.y_true.values.astype(int), d.y_prob.values
    auc = roc_auc_score(y, p)
    sy = (d.station_name + "_" + d.date.dt.year.astype(str)).values
    sy_cl = cluster_index(sy)

    ci = np.percentile(boot(y, lambda b: roc_auc_score(y[b], p[b]), sy_cl, rng), [2.5, 97.5])
    print(f"test rows {len(y)}, events {y.sum()}, base {y.mean():.3f}")
    print(f"1. AUC {auc:.3f}  95% CI [{ci[0]:.3f}, {ci[1]:.3f}] (station-year bootstrap)")

    null = shift_null(y, p, cluster_index(d.station_name.values), rng)
    print(f"2. station shift null: 95th pct {np.percentile(null, 95):.3f}, "
          f"p = {((null >= auc).sum() + 1) / (len(null) + 1):.4f}")
    null = shift_null(y, p, sy_cl, rng)
    print(f"3. station-year shift null (timing within a season): 95th pct "
          f"{np.percentile(null, 95):.3f}, p = {((null >= auc).sum() + 1) / (len(null) + 1):.4f}")

    sm, mo, overall = train_month_rates()
    key = list(zip(d.station_name, d.date.dt.month))
    m = np.array([sm.get(k, mo.get(k[1], overall)) for k in key], dtype=float)
    diffs = boot(y, lambda b: roc_auc_score(y[b], p[b]) - roc_auc_score(y[b], m[b]), sy_cl, rng)
    print(f"4. month-of-year baseline (training-year rates) AUC {roc_auc_score(y, m):.3f}; "
          f"model minus baseline {auc - roc_auc_score(y, m):+.3f} "
          f"[{np.percentile(diffs, 2.5):+.3f}, {np.percentile(diffs, 97.5):+.3f}], "
          f"one-sided p = {(diffs <= 0).mean():.3f}")


if __name__ == "__main__":
    main()
