"""
tabpfn_cv.py -- TabPFN vs the locked logistic regression on LIS, under notes/TABPFN_PREREG.md
=============================================================================================
Same walk-forward, features, label and bootstrap as model_class_cv.py. TabPFN needs PyTorch, so it runs
in a separate environment; the base environment builds the folds and computes every statistic.

    python src/models/tabpfn_cv.py export                 # base env: writes data/tabpfn_folds.csv
    <tabpfn-env>/python src/models/tabpfn_cv.py predict   # tabpfn==2.2.1: writes data/tabpfn_preds.csv
    python src/models/tabpfn_cv.py score                  # base env: LR fit, bootstrap, adoption rule

Adoption rule: pooled 2016-2022 AUC(TabPFN) - AUC(LR) >= +0.02 AND paired station-year bootstrap
(2,000 resamples, seed 42) one-sided p < 0.05. Otherwise LR stays.
"""
import os
import sys

import numpy as np
import pandas as pd

HORIZON, SEED = 21, 42
FIRST, LAST, DEV_LAST = 2016, 2025, 2022
MIN_GAIN = 0.02
FOLDS, PREDS = "data/tabpfn_folds.csv", "data/tabpfn_preds.csv"


def export():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from rolling_origin_cv import build_dataset
    df, feats = build_dataset(horizon=HORIZON)
    df = df.dropna(subset=["bloom_28d"]).sort_values(["station_name", "date"]).reset_index(drop=True)
    out = df[["station_name", "date", "bloom_28d"] + list(feats)].copy()
    out.to_csv(FOLDS, index=False)
    pd.Series(list(feats)).to_csv(FOLDS.replace(".csv", "_feats.csv"), index=False, header=False)
    print(f"wrote {FOLDS}: {len(out)} rows, {len(feats)} features")


def predict():
    import gc
    from tabpfn import TabPFNClassifier
    df = pd.read_csv(FOLDS, parse_dates=["date"])
    feats = pd.read_csv(FOLDS.replace(".csv", "_feats.csv"), header=None)[0].tolist()
    # resumable: each fold is appended to PREDS as soon as it finishes
    done = set(pd.read_csv(PREDS).fold) if os.path.exists(PREDS) else set()
    for T in range(FIRST, LAST + 1):
        tr, te = df[df.date.dt.year <= T - 2], df[df.date.dt.year == T]
        if len(te) == 0 or te.bloom_28d.sum() == 0 or T in done:
            continue
        med = tr[feats].median()
        m = TabPFNClassifier(random_state=42, device="cpu")
        m.fit(tr[feats].fillna(med).values, tr.bloom_28d.astype(int).values)
        p = m.predict_proba(te[feats].fillna(med).values)[:, 1]
        pd.DataFrame({"station_name": te.station_name.values, "date": te.date.values,
                      "fold": T, "tabpfn": p}).to_csv(PREDS, mode="a", index=False,
                                                       header=not os.path.exists(PREDS))
        del m
        gc.collect()
        print(f"fold {T}: train {len(tr)}, test {len(te)} (saved)", flush=True)
    print(f"done: {PREDS}")


def score():
    from sklearn.metrics import roc_auc_score
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from rolling_origin_cv import build_dataset
    from calendar_hybrid_cv import fit_predict, paired
    df, feats = build_dataset(horizon=HORIZON)
    df = df.sort_values(["station_name", "date"]).reset_index(drop=True)
    rows = []
    for T in range(FIRST, LAST + 1):
        tr = df[df.date.dt.year <= T - 2].dropna(subset=["bloom_28d"])
        te = df[df.date.dt.year == T].dropna(subset=["bloom_28d"])
        if len(te) == 0 or te.bloom_28d.sum() == 0:
            continue
        rows.append(pd.DataFrame({"station_name": te.station_name.astype(str).values,
                                  "date": te.date.values, "fold": T,
                                  "y": te.bloom_28d.astype(int).values,
                                  "lr": fit_predict(tr, te, feats)}))
    r = pd.concat(rows, ignore_index=True)
    tp = pd.read_csv(PREDS, parse_dates=["date"])
    tp["station_name"] = tp.station_name.astype(str)
    r = r.merge(tp, on=["station_name", "date", "fold"], how="left", validate="one_to_one")
    assert r.tabpfn.notna().all(), "missing TabPFN predictions"
    rng = np.random.default_rng(SEED)

    def summarize(tag, s):
        s = s.reset_index(drop=True)
        y = s.y.values.astype(int)
        keys = (s.station_name + "_" + s.date.dt.year.astype(str)).values
        a_lr, a_tp = roc_auc_score(y, s.lr), roc_auc_score(y, s.tabpfn)
        lo, hi, p = paired(y, s.tabpfn.values, s.lr.values, keys, rng)
        print(f"{tag}: rows {len(y)}, events {y.sum()} | AUC LR {a_lr:.3f}, TabPFN {a_tp:.3f} | "
              f"TabPFN - LR {a_tp - a_lr:+.3f} [{lo:+.3f}, {hi:+.3f}], one-sided p = {p:.3f}")
        return a_tp - a_lr, p

    print("Per fold AUC (LR / TabPFN):")
    for T, g in r.groupby("fold"):
        if 0 < g.y.sum() < len(g):
            print(f"  {T}: events {int(g.y.sum()):>3}  {roc_auc_score(g.y, g.lr):.3f}  "
                  f"{roc_auc_score(g.y, g.tabpfn):.3f}")
    gain, p = summarize("DEVELOPMENT 2016-2022", r[r.fold <= DEV_LAST])
    adopt = gain >= MIN_GAIN and p < 0.05
    print(f"Adoption rule (gain >= +{MIN_GAIN:.2f} and p < 0.05): {'ADOPT TabPFN' if adopt else 'KEEP LR'}")
    summarize("HELD-OUT 2023-2025 (reported only)", r[r.fold > DEV_LAST])
    summarize("ALL 2016-2025", r)


if __name__ == "__main__":
    {"export": export, "predict": predict, "score": score}[sys.argv[1]]()
