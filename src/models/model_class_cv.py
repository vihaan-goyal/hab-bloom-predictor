"""
model_class_cv.py -- locked logistic regression vs gradient boosting, under a pre-registered protocol
=====================================================================================================
Implements notes/MODEL_CLASS_PREREG.md (written and pushed 2026-10-02/05, before this ran).
Walk-forward exactly as rolling_origin_cv.py --horizon 21 (train <= T-2, test = T, 2016-2025),
the same 35 features and label as calendar_hybrid_cv.py. GB uses the Narragansett settings,
copied, not tuned. Development folds 2016-2022 decide adoption; 2023-2025 is reported only.

Adoption rule: pooled 2016-2022 AUC(GB) - AUC(LR) >= +0.02 AND paired station-year bootstrap
(2,000 resamples, seed 42) one-sided p = P(diff <= 0) < 0.05. Otherwise LR stays.

Run from repo root:  python src/models/model_class_cv.py
Writes data/model_class_cv.csv (out-of-fold predictions for both models).
"""
import os
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rolling_origin_cv import build_dataset  # noqa: E402
from calendar_hybrid_cv import fit_predict, paired  # noqa: E402  (locked LR fit; paired bootstrap)

HORIZON, SEED = 21, 42
FIRST, LAST, DEV_LAST = 2016, 2025, 2022
MIN_GAIN = 0.02
GB_KW = dict(max_depth=3, learning_rate=0.05, max_iter=300, min_samples_leaf=50,
             l2_regularization=1.0, class_weight="balanced", random_state=42)


def fit_predict_gb(tr, te, feats):
    med = tr[feats].median()
    m = HistGradientBoostingClassifier(**GB_KW).fit(tr[feats].fillna(med).values,
                                                    tr.bloom_28d.astype(int).values)
    return m.predict_proba(te[feats].fillna(med).values)[:, 1]


def summarize(tag, r, rng):
    y = r.y.values.astype(int)
    keys = (r.station_name + "_" + r.date.dt.year.astype(str)).values
    a_lr, a_gb = roc_auc_score(y, r.lr), roc_auc_score(y, r.gb)
    lo, hi, p = paired(y, r.gb.values, r.lr.values, keys, rng)
    print(f"{tag}: rows {len(y)}, events {y.sum()} | AUC LR {a_lr:.3f}, GB {a_gb:.3f} | "
          f"GB - LR {a_gb - a_lr:+.3f} [{lo:+.3f}, {hi:+.3f}], one-sided p = {p:.3f}")
    return a_gb - a_lr, p


def main():
    rng = np.random.default_rng(SEED)
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
                                  "lr": fit_predict(tr, te, feats),
                                  "gb": fit_predict_gb(tr, te, feats)}))
    r = pd.concat(rows, ignore_index=True)
    r.to_csv("data/model_class_cv.csv", index=False)
    print("Per fold AUC (LR / GB):")
    for T, g in r.groupby("fold"):
        if 0 < g.y.sum() < len(g):
            print(f"  {T}: events {int(g.y.sum()):>3}  {roc_auc_score(g.y, g.lr):.3f}  "
                  f"{roc_auc_score(g.y, g.gb):.3f}")
    gain, p = summarize("DEVELOPMENT 2016-2022", r[r.fold <= DEV_LAST].reset_index(drop=True), rng)
    adopt = gain >= MIN_GAIN and p < 0.05
    print(f"Adoption rule (gain >= +{MIN_GAIN:.2f} and p < 0.05): "
          f"{'ADOPT GB' if adopt else 'KEEP LR'}")
    summarize("HELD-OUT 2023-2025 (reported only)", r[r.fold > DEV_LAST].reset_index(drop=True), rng)
    summarize("ALL 2016-2025", r, rng)


if __name__ == "__main__":
    main()
