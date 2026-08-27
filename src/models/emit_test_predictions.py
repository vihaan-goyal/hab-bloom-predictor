"""
emit_test_predictions.py
------------------------
Produces data/test_predictions.csv from the LOCKED pipeline on HONEST labels.

Replaces final_evaluation_threshold_sweep.py as the producer of that file. The
sweep script wrote it from Family B labels -- a 28-day horizon with no
right-censoring, which scored windows as negative that were never resolvable --
and swept its threshold on the test set. Three live scripts consume this file:

    bootstrap_ci.py           confidence intervals on the operating point
    audit_flagged_windows.py  buoy-fluorescence audit of flagged windows
    check_label_integrity.py  label sanity checks

so they were all reading Family B labels. This script emits the same schema
from locked_pipeline (h=21, right-censored) on the leak-free feature file, at
the validation-selected operating point.

Output columns:
    station_name, date, y_true, y_prob     <- required by the consumers
    verifiable                             <- added; see below
    alert                                  <- y_prob >= t*

THE `verifiable` COLUMN
A window can close with no station visit inside it. At h=21 that is 47.7% of
rows, because the survey cadence is ~21 days. Those rows carry y_true=0, which
records "no exceedance was observed", not "no exceedance occurred". They are
kept (the locked spec counts them) but flagged, so a consumer can restrict to
verifiable windows the way operational verification does:

    df[df.verifiable == 1]

Positive rate is 0.146 over all windows and 0.280 over verifiable ones, so the
two give materially different precision and FAR.

Usage (from repo root):
    python src/models/emit_test_predictions.py
    python src/models/emit_test_predictions.py --base hab_features_tidal.csv
"""

import argparse
import os
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")))
from src.models.label_utils import build_forward_label       # noqa: E402
from src.models.locked_pipeline import (                     # noqa: E402
    HORIZON_DAYS, add_forward_label, fit_locked_model,
    load_locked_dataframe, predict_proba)

LABEL = "bloom_fwd"


def parse_args():
    p = argparse.ArgumentParser(description="Emit honest test predictions")
    p.add_argument("--data-dir", default="data")
    p.add_argument("--base", default="hab_features_tidal_v2.csv",
                   help="leak-free canonical features (v2)")
    p.add_argument("--out", default="test_predictions.csv")
    p.add_argument("--train-end", default="2019-12-31")
    p.add_argument("--test-start", default="2023-01-01")
    p.add_argument("--t-star", type=float, default=0.35,
                   help="operating point selected on val; never tuned on test")
    return p.parse_args()


def report(tag, y, p, t):
    pred = (p >= t).astype(int)
    tp = int(((pred == 1) & (y == 1)).sum())
    fp = int(((pred == 1) & (y == 0)).sum())
    fn = int(((pred == 0) & (y == 1)).sum())
    prec = tp / (tp + fp) if tp + fp else float("nan")
    rec = tp / (tp + fn) if tp + fn else float("nan")
    csi = tp / (tp + fp + fn) if tp + fp + fn else float("nan")
    auc = roc_auc_score(y, p) if len(set(y)) > 1 else float("nan")
    ap = average_precision_score(y, p) if len(set(y)) > 1 else float("nan")
    print(f"  {tag:<22} n={len(y):>5,}  pos={int(y.sum()):>4} "
          f"({y.mean()*100:4.1f}%)  AUC={auc:.4f}  AP={ap:.4f}")
    print(f"  {'':<22} POD={rec:.4f}  FAR={1-prec:.4f}  "
          f"precision={prec:.4f}  CSI={csi:.4f}  TP={tp} FP={fp} FN={fn}")


def main():
    a = parse_args()
    dd = a.data_dir
    train_end = pd.Timestamp(a.train_end)
    test_start = pd.Timestamp(a.test_start)
    out_path = os.path.join(dd, a.out)

    print(f"Base features : {a.base}")
    print(f"Labels        : locked h={HORIZON_DAYS}d, right-censored")
    print(f"Train         : <= {train_end.date()}      t* = {a.t_star}\n")

    df = load_locked_dataframe(
        base_csv=os.path.join(dd, a.base),
        ps_glob=os.path.join(dd, "raw", "deep_wq_extra", "deep_wq_S_*.csv"),
        gust_csv=os.path.join(dd, "gust_features_daily.csv"),
        verbose=False)
    df = add_forward_label(df, horizon=HORIZON_DAYS)

    # A window is verifiable when it actually contained a station visit.
    verifiable = build_forward_label(df, horizon=HORIZON_DAYS,
                                     unverifiable="exclude").notna()

    bundle = fit_locked_model(df, label_col=LABEL, train_end=train_end)
    print(f"Trained on {bundle['n_train']:,} rows "
          f"(bloom rate {bundle['train_bloom_rate']*100:.1f}%)\n")

    lab = df.dropna(subset=[LABEL]).copy()
    lab["y_prob"] = predict_proba(bundle, lab)
    lab["verifiable"] = verifiable.reindex(lab.index).fillna(False).astype(int)

    test = lab[lab["date"] >= test_start].copy()
    if test.empty:
        raise SystemExit(f"No labeled rows on or after {test_start.date()}.")

    out = pd.DataFrame({
        "station_name": test["station_name"].astype(str),
        "date": test["date"].dt.strftime("%Y-%m-%d"),
        "y_true": test[LABEL].astype(int),
        "y_prob": test["y_prob"].astype(float),
        "verifiable": test["verifiable"].astype(int),
    }).sort_values(["date", "station_name"])
    out["alert"] = (out["y_prob"] >= a.t_star).astype(int)

    print(f"TEST {test_start.date()} onward, at t* = {a.t_star}")
    y = out["y_true"].values
    p = out["y_prob"].values
    report("all windows", y, p, a.t_star)
    v = out["verifiable"].values == 1
    report("verifiable windows", y[v], p[v], a.t_star)
    print(f"\n  verifiable: {int(v.sum()):,}/{len(out):,} "
          f"({100*v.mean():.1f}%) of test windows contained a station visit")

    out.to_csv(out_path, index=False)
    print(f"\nSaved {out_path} ({len(out):,} rows)")
    print("Consumers: bootstrap_ci.py, audit_flagged_windows.py, "
          "check_label_integrity.py")


if __name__ == "__main__":
    main()
