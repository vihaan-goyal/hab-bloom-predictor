"""
label_refinement.py
-------------------
Honest test of whether refining the bloom label (to stop penalizing near-misses)
genuinely improves the model, or just inflates precision through base rate.

The audit's optimistic 0.175 -> 0.315 came from flipping only the FALSE POSITIVES
to positives. That is not a real label: a label change must apply to EVERY row. And
any more-lenient label raises the base rate, which raises precision mechanically.
So this script:

  1. Recomputes y_true for ALL pooled rows under four label definitions, applied
     uniformly, using each station's own chlorophyll series:
        original : chl > thr in (d, d+H]                      (baseline)
        grace    : chl > thr in (d, d+H+grace]                (just-outside misses)
        tol      : chl > floor in (d, d+H]                    (subthreshold misses)
        both     : chl > floor in (d, d+H+grace]
  2. Keeps the EXISTING model probabilities (the harsh-label model). We are asking
     "were this model's errors really near-misses", not retraining.
  3. Reports, per label: base rate, raw precision@t (rises mechanically, do not
     trust alone), AUPRC, and the HONEST metric AUPRC-lift = AUPRC / base_rate.
  4. Paired station-year bootstrap of lift(refined) - lift(original). CI excluding
     zero = refinement helps BEYOND the base-rate change. CI spanning zero = the
     apparent precision gain is mechanical; do not claim it.

A sanity check confirms the recomputed 'original' label matches the stored y_true.

Run from repo root:
    python label_refinement.py
    python label_refinement.py --predictions data/cv_pred_orig_h21.csv --horizon 21
"""

import argparse
import sys
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score


def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--predictions", default="data/cv_pred_orig_h21.csv")
    p.add_argument("--series", default="data/hab_features_tidal.csv")
    p.add_argument("--horizon", type=int, default=21)
    p.add_argument("--threshold", type=float, default=0.60)
    p.add_argument("--chl-threshold", type=float, default=10.0)
    p.add_argument("--floor", type=float, default=8.0)
    p.add_argument("--grace-days", type=int, default=7)
    p.add_argument("--n-boot", type=int, default=3000)
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


def build_smap(ser):
    smap = {}
    for st, g in ser[["station_name", "date", "Chlorophyll"]].dropna().groupby("station_name"):
        g = g.sort_values("date")
        smap[st] = (g["date"].values.astype("datetime64[ns]"),
                    g["Chlorophyll"].values.astype(float))
    return smap


def recompute_labels(pred, smap, H, grace, thr, floor):
    """Return a DataFrame of label variants for every pooled row."""
    Hd = np.timedelta64(H, "D")
    Gd = np.timedelta64(H + grace, "D")
    out = {"original": [], "grace": [], "tol": [], "both": []}
    for _, r in pred.iterrows():
        st, d = str(r["station_name"]), np.datetime64(r["date"])
        if st not in smap:
            for k in out:
                out[k].append(0)
            continue
        dates, chl = smap[st]
        win = (dates > d) & (dates <= d + Hd)
        ext = (dates > d) & (dates <= d + Gd)
        wmax = chl[win].max() if win.any() else -np.inf
        emax = chl[ext].max() if ext.any() else -np.inf
        out["original"].append(int(wmax > thr))
        out["grace"].append(int(emax > thr))
        out["tol"].append(int(wmax > floor))
        out["both"].append(int(emax > floor))
    return pd.DataFrame(out, index=pred.index)


def metrics(y_true, y_prob, t):
    n = len(y_true); npos = int(y_true.sum()); base = npos / n if n else np.nan
    pred = y_prob >= t
    tp = int(np.sum(pred & (y_true == 1))); fp = int(np.sum(pred & (y_true == 0)))
    prec = tp / (tp + fp) if (tp + fp) else np.nan
    rec = tp / npos if npos else np.nan
    auprc = average_precision_score(y_true, y_prob) if 0 < npos < n else np.nan
    lift = auprc / base if base else np.nan
    return dict(base=base, npos=npos, prec=prec, rec=rec, auprc=auprc, lift=lift)


def main():
    a = parse_args()
    try:
        pred = pd.read_csv(a.predictions); ser = pd.read_csv(a.series)
    except FileNotFoundError as e:
        sys.exit(str(e))
    pred["date"] = pd.to_datetime(pred["date"]); ser["date"] = pd.to_datetime(ser["date"])
    pred["station_name"] = pred["station_name"].astype(str)
    ser["station_name"] = ser["station_name"].astype(str)

    smap = build_smap(ser)
    labels = recompute_labels(pred, smap, a.horizon, a.grace_days,
                              a.chl_threshold, a.floor)
    yprob = pred["y_prob"].values

    # sanity: recomputed original vs stored y_true
    agree = (labels["original"].values == pred["y_true"].values).mean()
    print("=" * 64)
    print(f"label-refinement test  (horizon={a.horizon}d, t={a.threshold}, "
          f"floor={a.floor}, grace={a.grace_days}d)")
    print("=" * 64)
    print(f"recomputed-original vs stored y_true agreement: {agree:.1%}")
    if agree < 0.97:
        print("  WARNING: window logic differs from build_forward_label; "
              "interpret with care.")
    print()

    variants = ["original", "grace", "tol", "both"]
    m = {v: metrics(labels[v].values, yprob, a.threshold) for v in variants}
    print(f"{'label':<9} {'base':>6} {'npos':>5} {'prec@t':>7} {'recall':>7} "
          f"{'AUPRC':>6} {'lift':>6}")
    for v in variants:
        x = m[v]
        print(f"{v:<9} {x['base']:>6.3f} {x['npos']:>5} {x['prec']:>7.3f} "
              f"{x['rec']:>7.3f} {x['auprc']:>6.3f} {x['lift']:>6.2f}")
    print("\n  raw precision rises with leniency BY CONSTRUCTION (more positives).")
    print("  the honest column is 'lift' (AUPRC / base rate). compare that.\n")

    # paired bootstrap of lift(refined) - lift(original), station-year clusters
    year = pred["fold"].astype(str) if "fold" in pred.columns else \
        pd.to_datetime(pred["date"]).dt.year.astype(str)
    key = pred["station_name"].astype(str) + "_" + year
    groups = [np.array(v) for v in pred.groupby(key).indices.values()]
    ncl = len(groups)
    rng = np.random.default_rng(a.seed)
    L = {v: labels[v].values for v in variants}

    print("PAIRED bootstrap: lift(refined) - lift(original), station-year clusters")
    for v in ["grace", "tol", "both"]:
        diffs = []
        for _ in range(a.n_boot):
            idx = np.concatenate([groups[c] for c in rng.integers(0, ncl, size=ncl)])
            yo, yv, pp = L["original"][idx], L[v][idx], yprob[idx]
            no, nv = yo.sum(), yv.sum()
            if no == 0 or no == len(yo) or nv == 0 or nv == len(yv):
                continue
            lo = average_precision_score(yo, pp) / (no / len(yo))
            lv = average_precision_score(yv, pp) / (nv / len(yv))
            diffs.append(lv - lo)
        diffs = np.array(diffs)
        loci, hici = np.percentile(diffs, [2.5, 97.5])
        verdict = ("REAL gain beyond base rate" if loci > 0 else
                   "worse" if hici < 0 else "NOT distinguishable (mechanical)")
        print(f"  {v:<6} dlift={np.mean(diffs):+.2f}  95% CI [{loci:+.2f}, {hici:+.2f}]"
              f"  P(>0)={np.mean(diffs>0):.3f}  -> {verdict}")

    print("\nRead: if a variant's raw prec@t jumps but its lift CI spans zero, the")
    print("precision 'gain' is just base rate and must NOT be reported as a gain.")
    print("Only a lift CI excluding zero is a genuine label-refinement improvement.")


if __name__ == "__main__":
    main()