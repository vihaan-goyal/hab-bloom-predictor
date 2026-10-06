"""
calendar_hybrid_cv.py -- "calendar + conditions" model, evaluated under a pre-registered protocol
==================================================================================================
Implements Pre-registration 2 in notes/CALENDAR_BASELINE_PREREG.md. The locked LR (35 features)
gets one more input, cal_logit: the logit of the station-month 21-day bloom rate over rows whose
label had already resolved on the row's date (causal). Walk-forward exactly as
rolling_origin_cv.py --horizon 21 (train <= T-2, test = T, 2016-2025). Compares, per fold and
pooled: locked model, hybrid, and the calendar score itself.

Development folds 2016-2022 decide adoption; 2023-2025 is reported once.
Run from repo root:  python src/models/calendar_hybrid_cv.py
Writes data/calendar_hybrid_cv.csv (out-of-fold predictions for all three).
"""
import os
import sys

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rolling_origin_cv import build_dataset  # noqa: E402

HORIZON, MIN_ROWS, N_BOOT, SEED = 21, 5, 2000, 42
FIRST, LAST, DEV_LAST = 2016, 2025, 2022


def causal_calendar(df):
    """cal rate for each row from rows with date + HORIZON <= row date (their label resolved)."""
    lab = df.dropna(subset=["bloom_28d"])[["station_name", "date", "bloom_28d"]].copy()
    lab["month"] = lab.date.dt.month
    lab["known"] = lab.date + pd.Timedelta(days=HORIZON)
    q = df[["station_name", "date"]].copy()
    q["month"] = q.date.dt.month
    q["_i"] = np.arange(len(q))
    q = q.sort_values("date")
    out = pd.DataFrame(index=q._i.values, columns=["overall", "month", "stn"], dtype=float)
    for keys, col in (([], "overall"), (["month"], "month"), (["station_name", "month"], "stn")):
        a = (lab.groupby(keys + ["known"]).bloom_28d.agg(s="sum", n="count").reset_index()
             if keys else lab.groupby("known").bloom_28d.agg(s="sum", n="count").reset_index())
        a = a.sort_values(keys + ["known"])
        if keys:
            g = a.groupby(keys)
            a["cs"], a["cn"] = g.s.cumsum(), g.n.cumsum()
        else:
            a["cs"], a["cn"] = a.s.cumsum(), a.n.cumsum()
        a = a.sort_values("known").rename(columns={"known": "date"})
        m = pd.merge_asof(q, a[keys + ["date", "cs", "cn"]], on="date", by=keys or None,
                          allow_exact_matches=True)
        rate = (m.cs / m.cn).where(m.cn >= (MIN_ROWS if keys else 1))
        out.loc[m._i.values, col] = rate.values
    r = out.stn.fillna(out.month).fillna(out.overall).sort_index().values
    return np.log(np.clip(r, 0.01, 0.99) / (1 - np.clip(r, 0.01, 0.99)))


def fit_predict(tr, te, feats):
    med = tr[feats].median()
    sc = StandardScaler().fit(tr[feats].fillna(med))
    m = LogisticRegression(class_weight="balanced", C=0.05, max_iter=1000, random_state=42)
    m.fit(sc.transform(tr[feats].fillna(med)), tr.bloom_28d.astype(int))
    return m.predict_proba(sc.transform(te[feats].fillna(med)))[:, 1]


def paired(y, a, b, keys, rng):
    groups = [np.where(keys == k)[0] for k in pd.unique(keys)]
    d = []
    for _ in range(N_BOOT):
        s = np.concatenate([groups[i] for i in rng.integers(0, len(groups), len(groups))])
        if 0 < y[s].sum() < len(s):
            d.append(roc_auc_score(y[s], a[s]) - roc_auc_score(y[s], b[s]))
    d = np.array(d)
    return np.percentile(d, 2.5), np.percentile(d, 97.5), (d <= 0).mean()


def summarize(tag, r, rng):
    y = r.y.values.astype(int)
    keys = (r.station_name + "_" + r.date.dt.year.astype(str)).values
    auc = {k: roc_auc_score(y, r[k]) for k in ("locked", "hybrid", "calendar")}
    print(f"{tag}: rows {len(y)}, events {y.sum()} | AUC locked {auc['locked']:.3f}, "
          f"hybrid {auc['hybrid']:.3f}, calendar {auc['calendar']:.3f}")
    for a, b in (("hybrid", "calendar"), ("hybrid", "locked")):
        lo, hi, p = paired(y, r[a].values, r[b].values, keys, rng)
        print(f"   {a} - {b}: {auc[a] - auc[b]:+.3f} [{lo:+.3f}, {hi:+.3f}], one-sided p = {p:.3f}")
    return auc


def main():
    rng = np.random.default_rng(SEED)
    df, feats = build_dataset(horizon=HORIZON)
    df = df.sort_values(["station_name", "date"]).reset_index(drop=True)
    df["cal_logit"] = causal_calendar(df)
    rows = []
    for T in range(FIRST, LAST + 1):
        tr = df[(df.date.dt.year <= T - 2)].dropna(subset=["bloom_28d"])
        te = df[(df.date.dt.year == T)].dropna(subset=["bloom_28d"])
        if len(te) == 0 or te.bloom_28d.sum() == 0:
            continue
        p_locked = fit_predict(tr, te, feats)
        p_hybrid = fit_predict(tr, te, feats + ["cal_logit"])
        rows.append(pd.DataFrame({"station_name": te.station_name.astype(str).values,
                                  "date": te.date.values, "fold": T,
                                  "y": te.bloom_28d.astype(int).values, "locked": p_locked,
                                  "hybrid": p_hybrid, "calendar": te.cal_logit.values}))
    r = pd.concat(rows, ignore_index=True)
    r.to_csv("data/calendar_hybrid_cv.csv", index=False)
    print("Per fold AUC (locked / hybrid / calendar):")
    for T, g in r.groupby("fold"):
        if 0 < g.y.sum() < len(g):
            print(f"  {T}: events {int(g.y.sum()):>3}  " + "  ".join(
                f"{roc_auc_score(g.y, g[k]):.3f}" for k in ("locked", "hybrid", "calendar")))
    dev = summarize("DEVELOPMENT 2016-2022", r[r.fold <= DEV_LAST].reset_index(drop=True), rng)
    adopt = dev["hybrid"] >= dev["locked"] and dev["hybrid"] >= dev["calendar"]
    print(f"Rule 1 (adopt if dev hybrid AUC >= locked and >= calendar): "
          f"{'ADOPT' if adopt else 'DO NOT ADOPT'}")
    summarize("HELD-OUT 2023-2025 (reported once)", r[r.fold > DEV_LAST].reset_index(drop=True), rng)
    summarize("ALL 2016-2025", r, rng)


if __name__ == "__main__":
    main()
