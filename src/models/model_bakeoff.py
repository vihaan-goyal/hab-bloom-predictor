"""
model_bakeoff.py
----------------
Honest bake-off of the locked Logistic Regression against two model families built
for SMALL tabular data: TabPFN (pretrained transformer) and EBM (glassbox additive).
Same rolling-origin folds, same features, same fixed threshold, same paired
station-year AUC bootstrap as the rest of the paper.

Framing: the bottleneck here is data quantity + cadence, not model capacity, so the
EXPECTED and useful outcome is "no model family beats the LR" -> the ceiling is not
algorithmic. A null is a result, not a failure. This script exists so the paper can
say "we tested it" rather than assume it.

Models:
  lr      : the locked baseline (LogisticRegression C=0.05, balanced)   [always]
  ebm     : ExplainableBoostingClassifier (interpretml)                 [if installed]
  tabpfn  : TabPFNClassifier                                            [if installed]

Each is trained per fold on train<=T-2, scored out-of-sample on year T, pooled.
Reports AUC / AUPRC / lift / precision@t per model, plus paired AUC bootstrap of
each challenger minus LR (CI excluding zero = a real difference).

Install (optional):  pip install interpret tabpfn --break-system-packages
Run from repo root (place in src/models/):
    python src/models/model_bakeoff.py
    python src/models/model_bakeoff.py --horizon 21 --models lr ebm
"""

import argparse
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, average_precision_score

from rolling_origin_cv import build_dataset, FEATURES_ALL
from label_utils import build_forward_label
from horizon_decomp import paired_diff_bootstrap


def get_models(which):
    models = {}
    if "lr" in which:
        models["lr"] = ("scaled_lr", None)
    if "ebm" in which:
        try:
            from interpret.glassbox import ExplainableBoostingClassifier
            models["ebm"] = ("ebm", ExplainableBoostingClassifier)
        except Exception as e:
            print(f"  (ebm unavailable: {e}; skipping)")
    if "tabpfn" in which:
        try:
            from tabpfn import TabPFNClassifier
            models["tabpfn"] = ("tabpfn", TabPFNClassifier)
        except Exception as e:
            print(f"  (tabpfn unavailable: {e}; skipping)")
    return models


def fit_predict(kind, ctor, Xtr, ytr, Xte, med):
    Xtr_f, Xte_f = Xtr.fillna(med), Xte.fillna(med)
    if kind == "scaled_lr":
        sc = StandardScaler()
        m = LogisticRegression(class_weight="balanced", C=0.05,
                               max_iter=1000, random_state=42)
        m.fit(sc.fit_transform(Xtr_f), ytr)
        return m.predict_proba(sc.transform(Xte_f))[:, 1]
    if kind == "ebm":
        m = ctor(random_state=42)
        m.fit(Xtr_f.values, ytr.values)
        return m.predict_proba(Xte_f.values)[:, 1]
    if kind == "tabpfn":
        # TabPFN caps train size; subsample if needed for speed/limits
        m = ctor()
        Xt, yt = Xtr_f, ytr
        if len(Xt) > 10000:
            idx = np.random.default_rng(42).choice(len(Xt), 10000, replace=False)
            Xt, yt = Xt.iloc[idx], yt.iloc[idx]
        m.fit(Xt.values, yt.values)
        return m.predict_proba(Xte_f.values)[:, 1]
    raise ValueError(kind)


def run_model_cv(df, features, kind, ctor, fy, ly):
    pooled = []
    for T in range(fy, ly + 1):
        tr = df[df["date"].dt.year <= T - 2]
        te = df[df["date"].dt.year == T]
        def prep(s):
            return s[features + ["bloom_28d", "station_name", "date"]].dropna(subset=["bloom_28d"])
        tr, te = prep(tr), prep(te)
        if len(tr) == 0 or len(te) == 0 or te["bloom_28d"].sum() == 0:
            continue
        Xtr, ytr = tr[features], tr["bloom_28d"].astype(int)
        Xte, yte = te[features], te["bloom_28d"].astype(int).values
        med = Xtr.median()
        try:
            p = fit_predict(kind, ctor, Xtr, ytr, Xte, med)
        except Exception as e:
            print(f"    fold {T} {kind} failed: {e}")
            continue
        for s, d, yt, pr in zip(te["station_name"].astype(str), te["date"], yte, p):
            pooled.append({"station_name": s, "date": d, "y_true": int(yt),
                           "y_prob": float(pr), "fold": T})
    return pd.DataFrame(pooled)


def evaluate(pooled, t):
    yt, pr = pooled["y_true"].values, pooled["y_prob"].values
    base = yt.mean()
    auc = roc_auc_score(yt, pr) if len(np.unique(yt)) > 1 else np.nan
    apr = average_precision_score(yt, pr)
    pred = pr >= t
    prec = yt[pred].mean() if pred.sum() else np.nan
    return dict(auc=auc, auprc=apr, lift=apr / base, prec=prec, npos=int(yt.sum()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", default=["lr", "ebm", "tabpfn"])
    ap.add_argument("--horizon", type=int, default=21)
    ap.add_argument("--threshold", type=float, default=0.60)
    ap.add_argument("--first-test-year", type=int, default=2015)
    ap.add_argument("--last-test-year", type=int, default=2025)
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    df, features = build_dataset(clean_labels=False)
    df["bloom_28d"] = build_forward_label(df, horizon=args.horizon,
                                          threshold=10.0, sustained_only=False)
    print(f"\nfeatures: {len(features)}   horizon: {args.horizon}d   "
          f"threshold: {args.threshold}")

    models = get_models(args.models)
    if "lr" not in models:
        models = {"lr": ("scaled_lr", None), **models}

    pooled = {}
    for name, (kind, ctor) in models.items():
        print(f"  running {name} ...")
        pooled[name] = run_model_cv(df, features, kind, ctor,
                                    args.first_test_year, args.last_test_year)

    print("\n" + "=" * 60)
    print(f"{'model':<10} {'npos':>5} {'AUC':>6} {'AUPRC':>6} {'lift':>6} {'prec@t':>7}")
    print("=" * 60)
    ev = {}
    for name in pooled:
        if pooled[name].empty:
            print(f"{name:<10} (no predictions)"); continue
        ev[name] = evaluate(pooled[name], args.threshold)
        x = ev[name]
        print(f"{name:<10} {x['npos']:>5} {x['auc']:>6.3f} {x['auprc']:>6.3f} "
              f"{x['lift']:>6.2f} {x['prec']:>7.3f}")

    print("\nPAIRED AUC DIFFERENCE  (challenger minus lr), station-year clusters")
    for name in pooled:
        if name == "lr" or pooled[name].empty or "lr" not in pooled:
            continue
        diffs, nmatch = paired_diff_bootstrap(pooled[name], pooled["lr"],
                                              args.n_boot, args.seed)
        lo, hi = np.percentile(diffs, [2.5, 97.5])
        verdict = ("beats LR" if lo > 0 else "worse than LR" if hi < 0
                   else "not distinguishable from LR")
        print(f"  {name:<8} dAUC={np.mean(diffs):+.3f}  95% CI [{lo:+.3f}, {hi:+.3f}]"
              f"  (n={nmatch})  -> {verdict}")

    print("\nExpected outcome given a data/cadence-limited problem: 'not")
    print("distinguishable from LR'. A null here is the result -> the ceiling is")
    print("not algorithmic, which strengthens the data-limitation argument.")


if __name__ == "__main__":
    main()