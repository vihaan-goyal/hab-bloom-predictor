"""
leakage_ab_eval.py
------------------
Quantifies what the full-record climatology leak was worth, by running the
locked pipeline twice on identical labels and comparing.

    A (leaked) : data/hab_features_tidal.csv
                 chl_climatology / chl_anomaly  = full-record station-month mean
                 tidal_gt_anom  / tidal_msl_anom = full-record month mean
    B (fixed)  : data/hab_features_tidal_v2.csv
                 all four recomputed with strictly-prior expanding windows

Everything else is held constant: same 35 features, same LR spec, same split,
and Family A labels from locked_pipeline.add_forward_label (h=21, right-
censored) on BOTH arms -- so this isolates the leak and does not tangle it with
the separate Family B label defect.

Split: train <= 2019, val 2020-2022, test 2023-2025. The model is fit on train
only; the val and test numbers are read out, never selected on.

A drop from A to B is the leak's contribution. It is the honest number.

Usage (from repo root):
    python src/models/leakage_ab_eval.py
"""

import argparse
import os
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")))
from src.models.locked_pipeline import (          # noqa: E402
    HORIZON_DAYS, add_forward_label, fit_locked_model,
    load_locked_dataframe, predict_proba)

TRAIN_END = pd.Timestamp("2019-12-31")
T_STAR = 0.35            # honestly selected on val 2020-2022
LABEL = "bloom_fwd"


def parse_args():
    p = argparse.ArgumentParser(description="Climatology leak A/B")
    p.add_argument("--data-dir", default="data")
    p.add_argument("--arm-a", default="hab_features_tidal.csv")
    p.add_argument("--arm-b", default="hab_features_tidal_v2.csv")
    p.add_argument("--t-star", type=float, default=T_STAR)
    return p.parse_args()


def metrics(y, p, t):
    pred = (p >= t).astype(int)
    tp = int(((pred == 1) & (y == 1)).sum())
    fp = int(((pred == 1) & (y == 0)).sum())
    fn = int(((pred == 0) & (y == 1)).sum())
    prec = tp / (tp + fp) if tp + fp else float("nan")
    rec = tp / (tp + fn) if tp + fn else float("nan")
    f1 = 2 * prec * rec / (prec + rec) if prec and rec and not np.isnan(prec) else float("nan")
    csi = tp / (tp + fp + fn) if tp + fp + fn else float("nan")
    return {"AUC": roc_auc_score(y, p), "AP": average_precision_score(y, p),
            "POD": rec, "FAR": 1 - prec if not np.isnan(prec) else float("nan"),
            "precision": prec, "F1": f1, "CSI": csi,
            "TP": tp, "FP": fp, "FN": fn, "n": len(y), "pos": int(y.sum())}


def run_arm(data_dir, base_csv, t_star):
    df = load_locked_dataframe(
        base_csv=os.path.join(data_dir, base_csv),
        ps_glob=os.path.join(data_dir, "raw", "deep_wq_extra", "deep_wq_S_*.csv"),
        gust_csv=os.path.join(data_dir, "gust_features_daily.csv"),
        verbose=False)
    df = add_forward_label(df, horizon=HORIZON_DAYS)

    bundle = fit_locked_model(df, label_col=LABEL, train_end=TRAIN_END)
    lab = df.dropna(subset=[LABEL]).copy()
    lab["p"] = predict_proba(bundle, lab)
    yr = lab["date"].dt.year

    out = {"n_train": bundle["n_train"],
           "train_rate": bundle["train_bloom_rate"]}
    for name, m in [("val", yr.between(2020, 2022)), ("test", yr >= 2023)]:
        s = lab[m]
        out[name] = metrics(s[LABEL].astype(int).values, s["p"].values, t_star)
    return out


def main():
    a = parse_args()
    print(f"Locked pipeline | h={HORIZON_DAYS}d right-censored labels | "
          f"train <= {TRAIN_END.date()} | t* = {a.t_star}\n")

    arms = {}
    for tag, csv in [("A  LEAKED (full-record clim)", a.arm_a),
                     ("B  FIXED  (expanding clim)", a.arm_b)]:
        print(f"Running arm {tag}  <- {csv}")
        arms[tag] = run_arm(a.data_dir, csv, a.t_star)
        print(f"   trained on {arms[tag]['n_train']:,} rows "
              f"(bloom rate {arms[tag]['train_rate']*100:.1f}%)")

    ka, kb = list(arms)
    for split in ["val", "test"]:
        print(f"\n{'=' * 72}\n{split.upper()}  "
              f"({'2020-2022' if split == 'val' else '2023-2025'})\n{'=' * 72}")
        A, B = arms[ka][split], arms[kb][split]
        print(f"  rows={A['n']:,}  positives={A['pos']:,}  "
              f"base rate={A['pos']/A['n']*100:.1f}%")
        print(f"\n  {'metric':<12}{'A leaked':>12}{'B fixed':>12}{'delta':>12}")
        print(f"  {'-' * 48}")
        for k in ["AUC", "AP", "POD", "FAR", "precision", "F1", "CSI"]:
            print(f"  {k:<12}{A[k]:>12.4f}{B[k]:>12.4f}{B[k] - A[k]:>+12.4f}")
        for k in ["TP", "FP", "FN"]:
            print(f"  {k:<12}{A[k]:>12d}{B[k]:>12d}{B[k] - A[k]:>+12d}")

    dt = arms[kb]["test"]["AUC"] - arms[ka]["test"]["AUC"]
    print(f"\n{'=' * 72}")
    print(f"Test AUC: {arms[ka]['test']['AUC']:.4f} (leaked) -> "
          f"{arms[kb]['test']['AUC']:.4f} (fixed)   delta {dt:+.4f}")
    print("The fixed number is the one that can be defended.")


if __name__ == "__main__":
    main()
