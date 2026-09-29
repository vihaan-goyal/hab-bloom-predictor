"""
warning_threshold_selection.py

Early-warning operating point for the LOCKED pipeline.

Selects a recall-oriented alert threshold on VALIDATION years only
(2020-2022), freezes it, then evaluates exactly once on the held-out
test years (2023-2025). Never selects on test. This is the step that
turns the classifier into an early warning system.

Reports both vocabularies:
  ML:          precision / recall / F1
  Operational: POD (= recall), FAR (= 1 - precision), CSI = TP/(TP+FP+FN)

Selection rule: the HIGHEST threshold whose validation POD >= --target-pod.
(Highest, because among thresholds that all clear the detection target, the
highest one raises the alerting bar and so gives the best FAR. If none reaches
the target, the closest is used and flagged loudly.)

This docstring previously said LOWEST, which contradicted the code below
(`idxmax`) and warning_operating_point.py, which applies the same rule. The
code was right; the docstring was wrong.

The feature list is imported from locked_pipeline.FEATURES_ALL, and the model
spec (LogisticRegression, C=0.05, balanced) matches it; training here is a
refit of that spec on the train years.

Usage:
    python warning_threshold_selection.py
    python warning_threshold_selection.py --target-pod 0.8
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

# Imported from the locked pipeline rather than duplicated. This list used to
# be pasted here under a warning that it was "a PLACEHOLDER ... NOT the locked
# set"; it was in fact byte-identical to FEATURES_ALL, so the warning was stale
# and told readers to distrust correct output. Importing removes the chance of
# the two drifting apart.
from src.models.locked_pipeline import (                        # noqa: E402
    BASE_CSV, FEATURES_ALL, add_forward_label, fit_locked_model,
    load_locked_dataframe, predict_proba)

FEATURES = list(FEATURES_ALL)

LABEL_SHIFT_DAYS = 21          # locked horizon
TRAIN_MAX = 2019
VAL_YEARS = (2020, 2022)
TEST_YEARS = (2023, 2025)


def parse_args():
    p = argparse.ArgumentParser(description="Validation-only warning threshold selection.")
    # Defaults to the locked canonical file (station-days). It used to default
    # to hab_features_final.csv, which is the 1.36M-row measurement-level
    # source -- a different grain entirely, and not what the locked model is
    # fit on.
    p.add_argument("--data", default=BASE_CSV)
    p.add_argument("--label-col", default="bloom",
                   help="Base bloom column; the h-day-ahead label is derived from it.")
    p.add_argument("--target-pod", type=float, default=0.8)
    p.add_argument("--out-csv", default="data/warning_operating_point.csv")
    p.add_argument("--out-fig", default="figures/warning_threshold_selection.png")
    return p.parse_args()


def metrics(y, pred):
    tp = int(((pred == 1) & (y == 1)).sum())
    fp = int(((pred == 1) & (y == 0)).sum())
    fn = int(((pred == 0) & (y == 1)).sum())
    tn = int(((pred == 0) & (y == 0)).sum())
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    csi = tp / (tp + fp + fn) if tp + fp + fn else 0.0
    return {"TP": tp, "FP": fp, "FN": fn, "TN": tn,
            "precision": round(prec, 3), "recall_POD": round(rec, 3),
            "FAR": round(1 - prec, 3) if tp + fp else 1.0,
            "CSI": round(csi, 3), "F1": round(f1, 3)}


def main():
    a = parse_args()
    # Load through the locked pipeline so the derived rolling means and the
    # percent_saturation / max_gust_3d merges are present. Reading the CSV raw
    # left four of the locked 35 missing.
    df = load_locked_dataframe(base_csv=a.data, verbose=False)

    missing = [f for f in FEATURES if f not in df.columns]
    if missing:
        raise SystemExit(f"Features not in data: {missing}")

    # Label from the locked builder.
    #
    # This was previously
    #     df["label"] = df.groupby("station_name")[a.label_col].shift(-21)
    # which shifts 21 ROWS, not 21 days. Station visits are a survey cadence
    # with a ~21-day median gap, so that spanned roughly 441 days -- it was the
    # Family C row-shift defect, in the script that freezes the operating point.
    # add_forward_label uses a real 21-day calendar window and returns NaN for
    # right-censored windows.
    df = add_forward_label(df, horizon=LABEL_SHIFT_DAYS, col="label")
    # Drop on the LABEL only, never on the features. The locked spec imputes
    # missing features with train medians; dropping any row with a NaN feature
    # instead collapsed the test set to 88 rows, because max_gust_3d covers only
    # 55% of station-days.
    df = df.dropna(subset=["label"])
    df["label"] = df["label"].astype(int)
    yr = df["date"].dt.year

    tr = df[yr <= TRAIN_MAX]
    va = df[(yr >= VAL_YEARS[0]) & (yr <= VAL_YEARS[1])]
    te = df[(yr >= TEST_YEARS[0]) & (yr <= TEST_YEARS[1])]
    print(f"train n={len(tr):,}  val n={len(va):,}  test n={len(te):,}")
    print(f"val positive rate={va['label'].mean():.3f}  "
          f"test positive rate={te['label'].mean():.3f}")

    # Fit through the locked pipeline so the scaler, imputation and model spec
    # are the deployed ones by construction rather than by hand-copied constants.
    bundle = fit_locked_model(df, label_col="label",
                              train_end=pd.Timestamp(f"{TRAIN_MAX}-12-31"),
                              features=FEATURES)
    p_val = predict_proba(bundle, va)
    y_val = va["label"].values

    # ---- sweep on VALIDATION only ----
    rows = []
    for t in np.round(np.arange(0.05, 0.91, 0.05), 2):
        m = metrics(y_val, (p_val >= t).astype(int))
        m["threshold"] = t
        rows.append(m)
    sweep = pd.DataFrame(rows)[["threshold", "precision", "recall_POD",
                                "FAR", "CSI", "F1", "TP", "FP", "FN", "TN"]]

    print("\nVALIDATION sweep (2020-2022) - selection happens HERE")
    print("=" * 72)
    print(sweep.to_string(index=False))

    ok = sweep[sweep["recall_POD"] >= a.target_pod]
    if len(ok):
        # highest threshold still meeting the POD target = fewest false alarms
        chosen = ok.loc[ok["threshold"].idxmax()]
        note = f"highest threshold with val POD >= {a.target_pod}"
    else:
        chosen = sweep.loc[sweep["recall_POD"].idxmax()]
        note = (f"WARNING: no threshold reached POD {a.target_pod}; "
                f"using best available (POD {chosen['recall_POD']})")
    t_star = float(chosen["threshold"])
    print(f"\nFROZEN operating point: t* = {t_star}  ({note})")
    print(f"  validation: POD={chosen['recall_POD']}  FAR={chosen['FAR']}  "
          f"CSI={chosen['CSI']}  precision={chosen['precision']}")

    # ---- evaluate ONCE on test at frozen t* ----
    p_te = predict_proba(bundle, te)
    m_te = metrics(te["label"].values, (p_te >= t_star).astype(int))
    print("\nTEST (2023-2025) at frozen t* - reported, never tuned")
    print("=" * 72)
    for k, v in m_te.items():
        print(f"  {k:>10}: {v}")

    out = sweep.copy()
    out["chosen"] = out["threshold"] == t_star
    os.makedirs(os.path.dirname(a.out_csv) or ".", exist_ok=True)
    out.to_csv(a.out_csv, index=False)
    test_row = {"threshold": t_star, **m_te}
    pd.DataFrame([test_row]).to_csv(
        a.out_csv.replace(".csv", "_test.csv"), index=False)
    print(f"\nSaved sweep to {a.out_csv} and test result alongside it")

    # ---- figure: val tradeoff curves with frozen point marked ----
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(sweep["threshold"], sweep["recall_POD"], marker="o", ms=3,
            label="POD (recall)", color="#2a78d6")
    ax.plot(sweep["threshold"], sweep["FAR"], marker="o", ms=3,
            label="FAR (1 - precision)", color="#E24B4A")
    ax.plot(sweep["threshold"], sweep["CSI"], marker="o", ms=3,
            label="CSI", color="#1D9E75")
    ax.axvline(t_star, color="#52514e", ls="--", lw=1,
               label=f"frozen t* = {t_star}")
    ax.axhline(a.target_pod, color="#2a78d6", ls=":", lw=1, alpha=0.5)
    ax.set_xlabel("Alert threshold")
    ax.set_ylabel("Metric value (validation 2020-2022)")
    ax.set_title("Early-warning operating point selection (validation only)")
    ax.legend()
    fig.tight_layout()
    os.makedirs(os.path.dirname(a.out_fig) or ".", exist_ok=True)
    fig.savefig(a.out_fig, dpi=150)
    print(f"Saved figure to {a.out_fig}")


if __name__ == "__main__":
    main()