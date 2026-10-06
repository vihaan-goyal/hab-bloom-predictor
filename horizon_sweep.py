"""
horizon_sweep.py

Forecast skill vs lead time. Sweeps the prediction horizon from 1 to N days.
For each horizon h it asks: given chlorophyll history up to time t, can we
predict whether the reading closest to t+h exceeds the bloom threshold?

This is an EXPLORATORY proxy, not the locked pipeline. It uses a small
chlorophyll-derived feature set and a fresh logistic regression, so the
absolute AUC values will not match the locked model's headline numbers. The
scientific content is the SHAPE of the curve (how skill decays with lead time)
and the number of evaluable samples at each horizon (which the roughly monthly
sampling cadence limits).

Interpretation warning: on sparsely sampled data, short horizons have very few
matchable target readings. Always read the AUC curve next to the n_test curve.
A high AUC on 12 samples is noise, not skill.

Usage:
    python horizon_sweep.py --data deep_wq.csv --date-col time --max-horizon 50 --tol 7
"""

import argparse
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, precision_score, recall_score

BLOOM = 10.0            # ug/L bloom threshold
TRAIN_MAX_YEAR = 2019   # train on <= this year, test on the rest
MIN_N = 30              # need at least this many train and test samples to score
FEAT_COLS = ["chl_now", "trend", "chl_roll", "anomaly", "month_sin", "month_cos"]


def parse_args():
    p = argparse.ArgumentParser(description="Forecast skill vs lead time.")
    p.add_argument("--data", default="deep_wq.csv")
    p.add_argument("--station-col", default="station_name")
    p.add_argument("--date-col", default="time")
    p.add_argument("--chl-col", default="Chlorophyll")
    p.add_argument("--max-horizon", type=int, default=50)
    p.add_argument("--tol", type=int, default=7,
                   help="days of slack when matching a target reading to t+h")
    p.add_argument("--out-csv", default="data/horizon_sweep.csv")
    p.add_argument("--out-fig", default="figures/horizon_sweep.png")
    return p.parse_args()


def load(a):
    df = pd.read_csv(a.data, low_memory=False)
    for c in (a.station_col, a.date_col, a.chl_col):
        if c not in df.columns:
            raise SystemExit(f"Column '{c}' not found. Have: {list(df.columns)}")
    df[a.date_col] = pd.to_datetime(df[a.date_col], format="ISO8601", errors="coerce")
    df[a.chl_col] = pd.to_numeric(df[a.chl_col], errors="coerce")
    df = df.dropna(subset=[a.station_col, a.date_col, a.chl_col])
    df = df.groupby([a.station_col, a.date_col], as_index=False)[a.chl_col].mean()
    return df.sort_values([a.station_col, a.date_col]).reset_index(drop=True)


def build_features(df, a):
    df = df.copy()
    grp = df.groupby(a.station_col)[a.chl_col]
    df["chl_now"] = df[a.chl_col]
    df["trend"] = df["chl_now"] - grp.shift(1)
    df["chl_roll"] = grp.transform(lambda s: s.rolling(3, min_periods=1).mean())
    df["month"] = df[a.date_col].dt.month

    train = df[df[a.date_col].dt.year <= TRAIN_MAX_YEAR]
    clim = train.groupby([a.station_col, "month"])["chl_now"].mean().rename("clim")
    df = df.join(clim, on=[a.station_col, "month"])
    global_clim = train.groupby("month")["chl_now"].mean()
    df["clim"] = df["clim"].fillna(df["month"].map(global_clim))
    df["anomaly"] = df["chl_now"] - df["clim"]
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
    return df


def sweep(df, a, horizons, tol):
    groups = {st: g.reset_index(drop=True) for st, g in df.groupby(a.station_col)}
    rows = []
    for h in horizons:
        X, y, yr = [], [], []
        for g in groups.values():
            dates = g[a.date_col].values.astype("datetime64[D]")
            chl = g[a.chl_col].values
            feats = g[FEAT_COLS].values.astype(float)
            for i in range(len(g)):
                t = dates[i]
                tgt = t + np.timedelta64(h, "D")
                lo = np.searchsorted(dates, tgt - np.timedelta64(tol, "D"), "left")
                hi = np.searchsorted(dates, tgt + np.timedelta64(tol, "D"), "right")
                if hi <= lo:
                    continue
                cand = np.arange(lo, hi)
                cand = cand[dates[cand] > t]           # target must be in the future
                if len(cand) == 0:
                    continue
                j = cand[np.argmin(np.abs(dates[cand] - tgt))]
                x = feats[i]
                if np.isnan(x).any():
                    continue
                X.append(x)
                y.append(1 if chl[j] > BLOOM else 0)
                yr.append(pd.Timestamp(t).year)

        rec = {"horizon": h, "n_train": 0, "n_test": 0,
               "test_pos_rate": np.nan, "auc": np.nan,
               "precision": np.nan, "recall": np.nan}
        if X:
            X = np.array(X); y = np.array(y); yr = np.array(yr)
            tr = yr <= TRAIN_MAX_YEAR
            te = ~tr
            rec["n_train"] = int(tr.sum())
            rec["n_test"] = int(te.sum())
            if te.sum():
                rec["test_pos_rate"] = round(float(y[te].mean()), 3)
            enough = (tr.sum() >= MIN_N and te.sum() >= MIN_N
                      and len(np.unique(y[tr])) == 2 and len(np.unique(y[te])) == 2)
            if enough:
                sc = StandardScaler().fit(X[tr])
                clf = LogisticRegression(class_weight="balanced",
                                         max_iter=1000).fit(sc.transform(X[tr]), y[tr])
                prob = clf.predict_proba(sc.transform(X[te]))[:, 1]
                pred = (prob >= 0.5).astype(int)
                rec["auc"] = round(float(roc_auc_score(y[te], prob)), 3)
                rec["precision"] = round(float(precision_score(y[te], pred, zero_division=0)), 3)
                rec["recall"] = round(float(recall_score(y[te], pred, zero_division=0)), 3)
        rows.append(rec)
    return pd.DataFrame(rows)


def plot(res, path):
    fig, ax1 = plt.subplots(figsize=(9, 5))
    ax2 = ax1.twinx()
    ax2.bar(res["horizon"], res["n_test"], width=0.9,
            alpha=0.15, color="#888888", label="evaluable test samples")
    ax1.axhline(0.5, color="#bbbbbb", ls="--", lw=1)
    ax1.plot(res["horizon"], res["auc"], color="#2a78d6", marker="o", ms=3, lw=1.5)
    ax1.set_xlabel("Forecast horizon (days ahead)")
    ax1.set_ylabel("Test AUC", color="#2a78d6")
    ax2.set_ylabel("Evaluable test samples", color="#888888")
    ax1.set_ylim(0.4, 1.0)
    ax1.set_zorder(ax2.get_zorder() + 1)
    ax1.patch.set_visible(False)
    ax1.set_title("Forecast skill vs lead time (exploratory proxy model)")
    fig.tight_layout()
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fig.savefig(path, dpi=150)
    print(f"Saved figure to {path}")


def main():
    a = parse_args()
    df = load(a)
    df = build_features(df, a)
    horizons = list(range(1, a.max_horizon + 1))
    res = sweep(df, a, horizons, a.tol)

    print("\nForecast skill vs lead time")
    print("=" * 70)
    print(res.to_string(index=False))

    scored = res.dropna(subset=["auc"])
    if not scored.empty:
        best = scored.loc[scored["auc"].idxmax()]
        print("\nWhere the curve is evaluable "
              f"(n_train and n_test >= {MIN_N}, both classes present):")
        print(f"  horizons scored:   {int(scored['horizon'].min())} to {int(scored['horizon'].max())} days")
        print(f"  peak AUC:          {best['auc']} at horizon {int(best['horizon'])} days")
        print(f"  AUC at 21 days:    "
              f"{res.loc[res['horizon'] == 21, 'auc'].values}")

    os.makedirs(os.path.dirname(a.out_csv) or ".", exist_ok=True)
    res.to_csv(a.out_csv, index=False)
    print(f"\nSaved table to {a.out_csv}")
    plot(res, a.out_fig)


if __name__ == "__main__":
    main()