"""The precision ceiling as geometry: class overlap along the LR decision axis, both bays.

    python src/models/lr_geometry.py [--nar-root ../hab-bloom-predictor-narragansett]

For each bay, fit the shipped logistic-regression recipe on its training years, score the
test-period ONSET rows (today's chl <= 10) out of sample, and project them onto
axis 1 = the LR decision value z.w + b (log-odds; t* is a vertical line at logit t*) and
axis 2 = the first principal component of the standardized test matrix after removing w/|w|.
Writes data/lr_geometry_summary.csv, data/lr_geometry_rows_{nar,lis}.csv,
figures/fig_lr_geometry.png (copied to <nar-root>/figures/nar_fig14_lr_geometry.png).
Design and reading rule: fork notes/NARRAGANSETT_FINDINGS.md section 28 (fixed before running).
"""
import argparse
import os
import shutil
import sys

import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from locked_pipeline import (  # noqa: E402
    BLOOM_THRESHOLD, HORIZON_DAYS, add_forward_label, fit_locked_model, load_locked_dataframe)

# Narragansett recipe, copied verbatim from the fork's train_narragansett.py (tier A)
NAR_TIER_A = ['chl', 'chl_lag1', 'chl_lag2', 'chl_lag3', 'chl_lag4',
              'chl_roll3_mean', 'chl_roll6_mean', 'chl_roll9_mean',
              'chl_roll14_mean', 'chl_roll21_mean', 'chl_trend',
              'chl_anomaly', 'chl_climatology',
              'do', 'do_lag1', 'temp', 'temp_lag1',
              'sal', 'sal_lag1', 'sal_lag2', 'sal_lag3', 'sal_lag4', 'month']
NAR_TRAIN_MAX, NAR_VAL, NAR_TEST = 2020, (2021, 2022), 2023
LIS_TRAIN_END, LIS_TEST_YEARS, LIS_T_STAR = "2019-12-31", (2020, 2025), 0.35
OUT_SUMMARY = "data/lr_geometry_summary.csv"
FIG = "figures/fig_lr_geometry.png"
BLUE, ORANGE, GRAY = "#2a78d6", "#eb6834", "#8a8f98"


def logit(p):
    return float(np.log(p / (1 - p)))


def metrics(y, alert):
    y = np.asarray(y).astype(int); a = np.asarray(alert).astype(int)
    tp = int(((a == 1) & (y == 1)).sum()); fp = int(((a == 1) & (y == 0)).sum())
    fn = int(((a == 0) & (y == 1)).sum())
    prec = tp / (tp + fp) if tp + fp else np.nan
    pod = tp / (tp + fn) if tp + fn else np.nan
    return dict(tp=tp, fp=fp, fn=fn, precision=prec, pod=pod)


def geometry(bay, z, w, b, y, t_star, prob_check):
    """Axis-1 decision, axis-2 orthogonal PC, and the summary numbers for one bay."""
    decision = z @ w + b
    prob = 1.0 / (1.0 + np.exp(-decision))
    assert np.allclose(prob, prob_check, atol=1e-12), f"{bay}: decision != predict_proba"
    u = w / np.linalg.norm(w)
    zr = z - np.outer(z @ u, u)
    zr = zr - zr.mean(0)
    _, _, vt = np.linalg.svd(zr, full_matrices=False)
    pc = zr @ vt[0]
    m = metrics(y, prob >= t_star)
    auc_model, auc_axis = roc_auc_score(y, prob), roc_auc_score(y, decision)
    assert abs(auc_model - auc_axis) < 1e-9
    grid = np.linspace(decision.min() - 1, decision.max() + 1, 1024)
    f1, f0 = gaussian_kde(decision[y == 1])(grid), gaussian_kde(decision[y == 0])(grid)
    f1, f0 = f1 / np.trapezoid(f1, grid), f0 / np.trapezoid(f0, grid)
    ovl = float(np.trapezoid(np.minimum(f0, f1), grid))
    lo, hi = np.percentile(decision[y == 0], [5, 95])
    inband = float(((decision[y == 1] >= lo) & (decision[y == 1] <= hi)).mean())
    summary = dict(bay=bay, n_onset=len(y), n_pos=int(y.sum()), base_rate=float(y.mean()),
                   auc_model=auc_model, auc_axis=auc_axis, t_star=t_star, **m,
                   ovl=ovl, pos_in_neg_90band=inband, logit_t_star=logit(t_star),
                   neg_band_lo=float(lo), neg_band_hi=float(hi))
    return decision, pc, prob, summary, (grid, f0, f1)


def narragansett(nar_root):
    d = pd.read_csv(os.path.join(nar_root, "data", "narragansett_daily_features.csv"),
                    parse_dates=["date"]).dropna(subset=["bloom_fwd"])
    yr = d.date.dt.year
    tr, va, te = d[yr <= NAR_TRAIN_MAX], d[yr.between(*NAR_VAL)], d[yr == NAR_TEST]
    med = tr[NAR_TIER_A].median(numeric_only=True)
    prep = lambda x: x[NAR_TIER_A].fillna(med)
    sc = StandardScaler().fit(prep(tr))
    lr = LogisticRegression(C=0.05, class_weight="balanced", max_iter=1000,
                            random_state=42).fit(sc.transform(prep(tr)), tr.bloom_fwd.astype(int))
    pv, yv = lr.predict_proba(sc.transform(prep(va)))[:, 1], va.bloom_fwd.astype(int).to_numpy()
    ts = np.arange(0.05, 0.96, 0.05); f1s = []
    for t in ts:
        mm = metrics(yv, pv >= t)
        f1s.append(2 * mm["precision"] * mm["pod"] / (mm["precision"] + mm["pod"])
                   if mm["precision"] and mm["pod"] else 0)
    t_star = float(ts[int(np.argmax(f1s))])
    on = te[te.chl <= BLOOM_THRESHOLD]
    z = sc.transform(prep(on)); y = on.bloom_fwd.astype(int).to_numpy()
    dec, pc, prob, summ, dens = geometry("narragansett", z, lr.coef_[0], float(lr.intercept_[0]),
                                         y, t_star, lr.predict_proba(z)[:, 1])
    rows = pd.DataFrame(dict(station=on.station.values, date=on.date.dt.strftime("%Y-%m-%d").values,
                             y=y, decision=dec, pc_orth=pc, prob=prob))
    return summ, rows, dens


def lis():
    df = load_locked_dataframe(verbose=False)
    df = add_forward_label(df, horizon=HORIZON_DAYS, threshold=BLOOM_THRESHOLD, col="bloom_fwd")
    bundle = fit_locked_model(df, "bloom_fwd", train_end=LIS_TRAIN_END)
    feats, med, sc, lr = bundle["features"], bundle["medians"], bundle["scaler"], bundle["model"]
    yr = df.date.dt.year
    te = df[yr.between(*LIS_TEST_YEARS) & df.bloom_fwd.notna()]
    on = te[te.Chlorophyll <= BLOOM_THRESHOLD]
    z = sc.transform(on[feats].fillna(med)); y = on.bloom_fwd.astype(int).to_numpy()
    dec, pc, prob, summ, dens = geometry("lis", z, lr.coef_[0], float(lr.intercept_[0]),
                                         y, LIS_T_STAR, lr.predict_proba(z)[:, 1])
    summ["n_features"] = len(feats); summ["n_train"] = bundle["n_train"]
    rows = pd.DataFrame(dict(station=on.station_name.values, date=on.date.dt.strftime("%Y-%m-%d").values,
                             y=y, decision=dec, pc_orth=pc, prob=prob))
    return summ, rows, dens


def plot(S, R, D, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    fig, ax = plt.subplots(2, 2, figsize=(11, 8.5), dpi=150)
    names = {"narragansett": "Narragansett Bay (sondes, 7-day label, test 2023)",
             "lis": "Long Island Sound (boat, 21-day label, test 2020-25)"}
    for a, bay in zip(ax[0], ("narragansett", "lis")):
        r, s = R[bay], S[bay]
        neg, pos = r[r.y == 0], r[r.y == 1]
        a.scatter(neg.decision, neg.pc_orth, s=6, color=GRAY, alpha=0.45, lw=0, label="no bloom within horizon")
        a.scatter(pos.decision, pos.pc_orth, s=7, color=ORANGE, alpha=0.6, lw=0, label="bloom within horizon")
        a.axvline(s["logit_t_star"], color=BLUE, ls="--", lw=1.2, label="t* = %.2f" % s["t_star"])
        a.set_title("%s\nn = %s onset rows, base rate %.2f, AUC %.2f"
                    % (names[bay], format(s["n_onset"], ","), s["base_rate"], s["auc_model"]),
                    loc="left", fontsize=9.5)
        a.set_xlabel("LR decision value (log-odds)"); a.set_ylabel("orthogonal PC 1 (standardized units)")
        a.legend(frameon=False, fontsize=8, loc="upper left", markerscale=2.5)
    a = ax[1, 0]
    for bay, ls in (("narragansett", "-"), ("lis", "--")):
        grid, f0, f1 = D[bay]; s = S[bay]
        a.plot(grid, f0, ls=ls, color=GRAY, lw=1.6, label="%s: no bloom" % bay)
        a.plot(grid, f1, ls=ls, color=ORANGE, lw=1.6, label="%s: bloom  (OVL %.2f)" % (bay, s["ovl"]))
        a.axvline(s["logit_t_star"], color=BLUE, ls=ls, lw=1)
    a.set_title("Class-conditional densities along the decision axis", loc="left", fontsize=10)
    a.set_xlabel("LR decision value (log-odds)"); a.set_ylabel("density (each class integrates to 1)")
    a.legend(frameon=False, fontsize=8)
    a = ax[1, 1]
    edges = np.linspace(min(R[b].decision.min() for b in R), max(R[b].decision.max() for b in R), 31)
    width = (edges[1] - edges[0]) * 0.42
    for k, bay in enumerate(("narragansett", "lis")):
        r = R[bay]; s = S[bay]
        n0, _ = np.histogram(r.decision[r.y == 0], edges); n1, _ = np.histogram(r.decision[r.y == 1], edges)
        x = edges[:-1] + (0.05 + 0.47 * k) * (edges[1] - edges[0])
        a.bar(x, n0, width=width, color=GRAY, alpha=0.5 if k else 0.85, lw=0)
        a.bar(x, n1, width=width, bottom=n0, color=ORANGE, alpha=0.5 if k else 0.95, lw=0,
              label="%s: %s blooms of %s rows" % (bay, format(s["n_pos"], ","), format(s["n_onset"], ",")))
        a.axvline(s["logit_t_star"], color=BLUE, ls="-" if k == 0 else "--", lw=1)
    a.set_title("Counts per bin (bloom stacked on no-bloom): the base-rate difference",
                loc="left", fontsize=10)
    a.set_xlabel("LR decision value (log-odds)"); a.set_ylabel("onset rows"); a.legend(frameon=False, fontsize=8)
    sn, sl = S["narragansett"], S["lis"]
    fig.suptitle("Separability is no worse in LIS (class overlap OVL %.2f vs %.2f Narragansett); "
                 "rarity is the difference (bloom share %.2f vs %.2f, precision at t* %.2f vs %.2f)"
                 % (sl["ovl"], sn["ovl"], sl["base_rate"], sn["base_rate"], sl["precision"], sn["precision"]),
                 fontsize=10, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.97)); fig.savefig(path); plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--nar-root", default=os.path.join("..", "hab-bloom-predictor-narragansett"))
    a = ap.parse_args()
    S, R, D = {}, {}, {}
    S["narragansett"], R["narragansett"], D["narragansett"] = narragansett(a.nar_root)
    S["lis"], R["lis"], D["lis"] = lis()
    os.makedirs("data", exist_ok=True); os.makedirs("figures", exist_ok=True)
    for bay, key in (("narragansett", "nar"), ("lis", "lis")):
        R[bay].to_csv("data/lr_geometry_rows_%s.csv" % key, index=False)
    summ = pd.DataFrame([S["narragansett"], S["lis"]])
    summ.to_csv(OUT_SUMMARY, index=False)
    pd.set_option("display.width", 220)
    cols = ["bay", "n_onset", "n_pos", "base_rate", "auc_model", "auc_axis", "t_star", "precision",
            "pod", "tp", "fp", "fn", "ovl", "pos_in_neg_90band"]
    print(summ[cols].to_string(index=False, float_format=lambda x: "%.4f" % x))
    plot(S, R, D, FIG)
    dst = os.path.join(a.nar_root, "figures", "nar_fig14_lr_geometry.png")
    shutil.copyfile(FIG, dst)
    print("wrote %s, data/lr_geometry_rows_*.csv, %s, %s" % (OUT_SUMMARY, FIG, dst))


if __name__ == "__main__":
    main()
