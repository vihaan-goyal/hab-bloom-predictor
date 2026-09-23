"""
iec_zero_shot.py
----------------
Phase 10 (pre-registered 2026-09-14, notes/SCIENTIFIC_METHOD.md): apply the
frozen LIS model, with no retraining, to the Interstate Environmental
Commission (IEC) western-Narrows record pulled from the EPA Water Quality
Portal (org 31ISC2RS_WQX, data/iec_wqp_raw.csv; station coordinates in
data/iec_stations.csv).

Outputs
  data/iec_station_days.csv        one row per IEC station-date with the 35 features
  data/iec_zero_shot_results.csv   metrics + bootstrap CIs per scenario
  data/iec_crosslab_pairs.csv      DEEP vs IEC chlorophyll pairs at A4/B3/C1/C2
  figures/fig_iec_zero_shot.png    lift by scenario, cross-lab scatter

Run from repo root:
    python src/transfer/iec_zero_shot.py
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.models.locked_pipeline import (  # noqa: E402
    FEATURES_ALL, load_locked_dataframe, add_forward_label,
    fit_locked_model, predict_proba, BLOOM_THRESHOLD, HORIZON_DAYS, tagged)

RAW = "data/iec_wqp_raw.csv"
STATIONS = "data/iec_stations.csv"
TIDAL = "data/tidal_features_monthly.csv"
GUST = "data/gust_features_daily.csv"
OUT_ROWS = tagged("data/iec_station_days.csv")
OUT_RES = tagged("data/iec_zero_shot_results.csv")
OUT_PAIRS = tagged("data/iec_crosslab_pairs.csv")
OUT_FIG = tagged("figures/fig_iec_zero_shot.png")

TRAIN_END = "2019-12-31"      # LIS training cut, locked
PRIMARY_START = "2018-01-01"  # IEC year-round period
CALIB_END = "2019-12-31"      # IEC rows used only to pick a threshold / rule
SURFACE_MAX_M = 1.5
N_BOOT, SEED = 2000, 42
PAIRED = ["A4", "B3", "C1", "C2"]   # same names in both networks
DAY_TOL = 3

PARAM = {
    "Chlorophyll a": "Chlorophyll",
    "Dissolved oxygen (DO)": "oxygen_concentration_in_sea_water",
    "Temperature, water": "sea_water_temperature",
    "Temperature": "sea_water_temperature",
    "Salinity": "sea_water_salinity",
    "Dissolved oxygen saturation": "percent_saturation",
}


# ---------------------------------------------------------------------------
# 1. IEC raw -> one surface row per station-date
# ---------------------------------------------------------------------------
def parse_depth(aid: pd.Series) -> pd.Series:
    """Depth (m) lives in the activity id: 'D:1.0' before 2018,
    ':FM:0.5:' / ':SR:0.5:' from 2018."""
    new = aid.str.extract(r":(?:FM|SR):([\d.]+):")[0]
    old = aid.str.extract(r"D:([\d.]+)$")[0]
    return pd.to_numeric(new.fillna(old), errors="coerce")


def load_iec():
    d = pd.read_csv(RAW, low_memory=False)
    d = d[~d.MonitoringLocationIdentifier.str.contains("-BR")]   # Byram River sites out
    d = d[d.CharacteristicName.isin(PARAM)].copy()
    d["var"] = d.CharacteristicName.map(PARAM)
    d["station_name"] = d.MonitoringLocationIdentifier.str.replace("31ISC2RS_WQX-", "", regex=False)
    d["date"] = pd.to_datetime(d.ActivityStartDate, errors="coerce").dt.normalize()
    d["value"] = pd.to_numeric(d.ResultMeasureValue, errors="coerce")
    d["depth"] = parse_depth(d.ActivityIdentifier).fillna(0.0)
    d = d.dropna(subset=["date", "value"])
    d = d[d.depth <= SURFACE_MAX_M]
    d = (d.sort_values("depth")
          .groupby(["station_name", "date", "var"], as_index=False)["value"].first())
    wide = d.pivot(index=["station_name", "date"], columns="var", values="value").reset_index()
    wide = wide.dropna(subset=["Chlorophyll"]).sort_values(["station_name", "date"]).reset_index(drop=True)
    st = pd.read_csv(STATIONS).drop_duplicates("station_name")
    wide = wide.merge(st[["station_name", "latitude", "longitude"]], on="station_name", how="left")
    return wide.rename(columns={"latitude": "latitude_x", "longitude": "longitude_x"})


# ---------------------------------------------------------------------------
# 2. LIS feature recipe on IEC rows
# ---------------------------------------------------------------------------
def build_features(df):
    df = df.sort_values(["station_name", "date"]).reset_index(drop=True)
    g = df.groupby("station_name")
    for k in range(1, 5):
        df[f"chl_lag{k}"] = g["Chlorophyll"].shift(k)
        df[f"sal_lag{k}"] = g["sea_water_salinity"].shift(k)
    df["do_lag1"] = g["oxygen_concentration_in_sea_water"].shift(1)
    df["temp_lag1"] = g["sea_water_temperature"].shift(1)
    df["month"] = df.date.dt.month.astype(float)
    clim = df.groupby(["station_name", "month"])["Chlorophyll"].transform("mean")
    df["chl_climatology"] = clim
    df["chl_anomaly"] = df["Chlorophyll"] - clim
    for n, min_p in [(3, 2), (6, 3), (9, 5), (14, 7), (21, 10)]:
        df[f"chl_roll{n}_mean"] = g["Chlorophyll"].transform(
            lambda x: x.rolling(n, min_periods=min_p).mean())
    df["chl_trend"] = g["Chlorophyll"].transform(
        lambda x: x.rolling(4, min_periods=3).apply(lambda v: np.polyfit(range(len(v)), v, 1)[0]))

    # neighbour mean: three nearest other stations sampled on the same date
    nb = np.full(len(df), np.nan)
    for _, grp in df.groupby("date"):
        if len(grp) < 2:
            continue
        lat, lon, chl = grp.latitude_x.values, grp.longitude_x.values, grp.Chlorophyll.values
        for i, idx in enumerate(grp.index):
            dist = np.hypot((lat - lat[i]) * 111.0, (lon - lon[i]) * 84.0)
            dist[i] = np.inf
            order = np.argsort(dist)[:3]
            order = order[np.isfinite(dist[order])]
            if len(order):
                nb[idx] = np.nanmean(chl[order])
    df["neighbor_chl3_mean"] = nb
    df["neighbor_chl3_lag1"] = df.groupby("station_name")["neighbor_chl3_mean"].shift(1)

    tidal = pd.read_csv(TIDAL, parse_dates=["date"])
    tidal["ym"] = tidal.date.dt.to_period("M")
    df["ym"] = df.date.dt.to_period("M")
    df = df.merge(tidal[["ym", "tidal_gt_anom", "tidal_msl_anom"]], on="ym", how="left").drop(columns="ym")
    gust = pd.read_csv(GUST, parse_dates=["date"], usecols=["date", "max_gust_3d"])
    df = df.merge(gust, on="date", how="left")
    for c in ["nox_lag2", "dip_lag2", "dip_change", "dip_x_month"]:
        df[c] = np.nan            # unavailable in matching units; LIS training median fills
    if "percent_saturation" not in df.columns:
        df["percent_saturation"] = np.nan
    return df


# ---------------------------------------------------------------------------
# 3. Scoring helpers
# ---------------------------------------------------------------------------
def point_metrics(y, p, t):
    a = p >= t
    tp = int((a & (y == 1)).sum()); fp = int((a & (y == 0)).sum()); fn = int((~a & (y == 1)).sum())
    prec = tp / (tp + fp) if tp + fp else np.nan
    pod = tp / (tp + fn) if tp + fn else np.nan
    base = float(y.mean())
    auc = roc_auc_score(y, p) if 0 < base < 1 and np.nanstd(p) > 0 else np.nan
    return dict(n=int(len(y)), n_pos=int(y.sum()), tp=tp, fp=fp, fn=fn, base_rate=base,
                precision=prec, pod=pod, lift=prec / base if base else np.nan, auc=auc)


def boot_ci(df, pcol, ycol, t, n_boot=N_BOOT, seed=SEED):
    rng = np.random.default_rng(seed)
    cl = (df.station_name.astype(str) + "_" + df.date.dt.year.astype(str)).values
    groups = {c: np.where(cl == c)[0] for c in np.unique(cl)}
    keys = list(groups)
    out = {"precision": [], "lift": [], "auc": []}
    y_all, p_all = df[ycol].values.astype(int), df[pcol].values
    for _ in range(n_boot):
        pick = rng.choice(len(keys), len(keys), replace=True)
        idx = np.concatenate([groups[keys[k]] for k in pick])
        y, p = y_all[idx], p_all[idx]
        if y.sum() == 0 or y.sum() == len(y):
            continue
        m = point_metrics(y, p, t)
        for k in out:
            out[k].append(m[k])
    ci = {}
    for k, v in out.items():
        ci[f"{k}_lo"] = np.nanpercentile(v, 2.5) if v else np.nan
        ci[f"{k}_hi"] = np.nanpercentile(v, 97.5) if v else np.nan
    return ci


def choose_threshold(cal, pcol, ycol, min_pod=0.6):
    """Highest threshold on the calibration rows that keeps POD >= min_pod."""
    best = 0.05
    y, p = cal[ycol].values.astype(int), cal[pcol].values
    for t in np.arange(0.05, 0.96, 0.01):
        if point_metrics(y, p, t)["pod"] >= min_pod:
            best = t
    return round(float(best), 2)


def climatology_baseline(cal, tst, ycol):
    rate = cal.groupby(["station_name", "month"])[ycol].mean().rename("clim_rate").reset_index()
    tst = tst.merge(rate, on=["station_name", "month"], how="left")
    return tst["clim_rate"].fillna(cal[ycol].mean()).values


def chl_rule_baseline(cal, tst, ycol):
    best_c, best_f1 = 0.0, -1.0
    y = cal[ycol].values.astype(int)
    for c in np.arange(0, 10.01, 0.5):
        a = cal.Chlorophyll.values > c
        tp = (a & (y == 1)).sum(); fp = (a & (y == 0)).sum(); fn = (~a & (y == 1)).sum()
        f1 = 2 * tp / (2 * tp + fp + fn) if tp else 0.0
        if f1 > best_f1:
            best_c, best_f1 = c, f1
    return (tst.Chlorophyll.values > best_c).astype(float), best_c


# ---------------------------------------------------------------------------
# 4. Main
# ---------------------------------------------------------------------------
def main():
    print("Building IEC station-days...")
    iec = build_features(load_iec())
    iec = add_forward_label(iec, horizon=HORIZON_DAYS, threshold=BLOOM_THRESHOLD, col="bloom_fwd")
    p75 = (iec[(iec.date >= PRIMARY_START) & (iec.date <= CALIB_END)]
           .groupby("station_name")["Chlorophyll"].quantile(0.75).rename("p75"))
    iec = iec.merge(p75, on="station_name", how="left")
    parts = []
    for _, grp in iec.groupby("station_name"):
        thr = grp.p75.iloc[0] if pd.notna(grp.p75.iloc[0]) else BLOOM_THRESHOLD
        parts.append(add_forward_label(grp, horizon=HORIZON_DAYS, threshold=thr, col="bloom_p75"))
    iec = pd.concat(parts).sort_values(["station_name", "date"]).reset_index(drop=True)
    print(f"  {len(iec):,} station-days, {iec.station_name.nunique()} stations, "
          f"{iec.date.min().date()} -> {iec.date.max().date()}")
    cov = iec[FEATURES_ALL].notna().mean().round(2)
    print("  feature coverage <0.5:", cov[cov < 0.5].to_dict())

    print("Fitting the locked LIS model (train <= 2019, h21, >10 ug/L)...")
    lis = load_locked_dataframe(verbose=False)
    lis = add_forward_label(lis, col="bloom_fwd")
    bundle = fit_locked_model(lis, "bloom_fwd", train_end=TRAIN_END)
    assert bundle["features"] == FEATURES_ALL, "feature set drifted from the locked 35"
    print(f"  n_train={bundle['n_train']:,}, train bloom rate={bundle['train_bloom_rate']:.3f}")

    iec["p_lis"] = predict_proba(bundle, iec)
    iec.to_csv(OUT_ROWS, index=False)

    results = []

    def add(scenario, model, t, m):
        results.append(dict(scenario=scenario, model=model, threshold=t, **m))

    def run(name, rows, ycol, cal_rows):
        rows = rows.dropna(subset=[ycol]).copy(); rows[ycol] = rows[ycol].astype(int)
        y, p = rows[ycol].values, rows.p_lis.values
        if len(rows) < 30 or y.sum() < 5:
            print(f"  {name}: too few rows ({len(rows)}, pos={int(y.sum())})"); return
        cal = cal_rows.dropna(subset=[ycol]).copy(); cal[ycol] = cal[ycol].astype(int)
        have_cal = len(cal) >= 30 and cal[ycol].sum() >= 5
        m60 = point_metrics(y, p, 0.60) | boot_ci(rows, "p_lis", ycol, 0.60)
        add(name, "LIS frozen", 0.60, m60)
        t_star = choose_threshold(cal, "p_lis", ycol) if have_cal else 0.60
        add(name, "LIS frozen", t_star, point_metrics(y, p, t_star) | boot_ci(rows, "p_lis", ycol, t_star))
        add(name, "always-alert", np.nan, point_metrics(y, np.ones(len(y)), 0.5))
        if have_cal:
            pc = climatology_baseline(cal, rows, ycol); tc = float(np.median(pc))
            add(name, "station-month climatology", tc,
                point_metrics(y, pc, tc) | boot_ci(rows.assign(p_clim=pc), "p_clim", ycol, tc))
            pr, c = chl_rule_baseline(cal, rows, ycol)
            add(name, f"chl>{c:g} rule", 0.5,
                point_metrics(y, pr, 0.5) | boot_ci(rows.assign(p_rule=pr), "p_rule", ycol, 0.5))
        print(f"  {name}: n={m60['n']} pos={m60['n_pos']} base={m60['base_rate']:.2f} | "
              f"t=0.60 prec={m60['precision']:.2f} POD={m60['pod']:.2f} lift={m60['lift']:.2f} "
              f"[{m60['lift_lo']:.2f}, {m60['lift_hi']:.2f}] AUC={m60['auc']:.3f} | t*={t_star}")

    prim = iec[iec.date >= PRIMARY_START]
    cal = prim[prim.date <= CALIB_END]
    test = prim[prim.date > CALIB_END]
    onset = test[test.Chlorophyll <= BLOOM_THRESHOLD]
    onset_cal = cal[cal.Chlorophyll <= BLOOM_THRESHOLD]
    print("Scoring...")
    run("primary: 2020-2025 onset rows, >10 ug/L h21", onset, "bloom_fwd", onset_cal)
    run("primary-all: 2018-2025 onset rows (incl. calib years)",
        prim[prim.Chlorophyll <= BLOOM_THRESHOLD], "bloom_fwd", onset_cal)
    run("all rows 2020-2025, >10 ug/L h21", test, "bloom_fwd", cal)
    run("secondary: 2020-2025 onset rows, own-station p75 h21",
        test[test.Chlorophyll <= test.p75], "bloom_p75", cal[cal.Chlorophyll <= cal.p75])
    hist = iec[iec.date < PRIMARY_START]
    run("secondary: 1991-2017 summer-only onset rows, >10 ug/L h21",
        hist[hist.Chlorophyll <= BLOOM_THRESHOLD], "bloom_fwd", onset_cal)
    for st, grp in onset.groupby("station_name"):
        g = grp.dropna(subset=["bloom_fwd"]).copy(); g["bloom_fwd"] = g.bloom_fwd.astype(int)
        if len(g) >= 30 and g.bloom_fwd.sum() >= 5:
            add(f"station {st}: 2020-2025 onset", "LIS frozen", 0.60,
                point_metrics(g.bloom_fwd.values, g.p_lis.values, 0.60) | boot_ci(g, "p_lis", "bloom_fwd", 0.60))
    res = pd.DataFrame(results)
    res.to_csv(OUT_RES, index=False)

    # -----------------------------------------------------------------------
    # 5. Cross-lab check: DEEP vs IEC chlorophyll at paired stations
    # -----------------------------------------------------------------------
    print("Cross-lab check DEEP vs IEC...")
    deep = lis[["station_name", "date", "Chlorophyll"]].copy()
    deep["station_name"] = deep.station_name.astype(str)
    deep = deep[deep.station_name.isin(PAIRED)].rename(columns={"Chlorophyll": "chl_deep"})
    iec_p = iec[["station_name", "date", "Chlorophyll"]].copy()
    iec_p["station_name"] = iec_p.station_name.str.replace("M", "", regex=False)   # B3M -> B3
    iec_p = iec_p[iec_p.station_name.isin(PAIRED)].rename(columns={"Chlorophyll": "chl_iec"})
    pairs = []
    for st in PAIRED:
        a = deep[deep.station_name == st].sort_values("date").drop(columns="station_name")
        b = iec_p[iec_p.station_name == st].sort_values("date").drop(columns="station_name")
        if a.empty or b.empty:
            continue
        m = pd.merge_asof(a, b, on="date", tolerance=pd.Timedelta(days=DAY_TOL), direction="nearest")
        m = m.dropna(subset=["chl_iec"]); m["station_name"] = st
        pairs.append(m[["station_name", "date", "chl_deep", "chl_iec"]])
    pairs = (pd.concat(pairs) if pairs
             else pd.DataFrame(columns=["station_name", "date", "chl_deep", "chl_iec"]))
    pairs = pairs[(pairs.chl_deep > 0) & (pairs.chl_iec > 0)].copy()
    pairs["ratio"] = pairs.chl_iec / pairs.chl_deep
    pairs.to_csv(OUT_PAIRS, index=False)
    for lab_, pp in [("all years", pairs), ("2018-2025", pairs[pairs.date >= PRIMARY_START])]:
        if len(pp) >= 5:
            rho = spearmanr(pp.chl_deep, pp.chl_iec).correlation
            agree = ((pp.chl_deep > 10) == (pp.chl_iec > 10)).mean()
            print(f"  {lab_}: n={len(pp)} median IEC/DEEP ratio={pp.ratio.median():.2f} "
                  f"[IQR {pp.ratio.quantile(.25):.2f}-{pp.ratio.quantile(.75):.2f}] "
                  f"Spearman r={rho:.2f} >10 label agreement={agree:.2f}")
        else:
            print(f"  {lab_}: only {len(pp)} pairs within +/-{DAY_TOL} d")

    # -----------------------------------------------------------------------
    # 6. Figure
    # -----------------------------------------------------------------------
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    top = res[res.scenario.str.startswith("primary:")].reset_index(drop=True)
    labels = [f"{m} (t={t:g})" if pd.notna(t) else m for m, t in zip(top.model, top.threshold)]
    x = np.arange(len(top))
    ax[0].bar(x, top.lift, color=["#1f4e79" if "LIS" in m else "#9aa5b1" for m in top.model])
    lo = (top.lift - top.lift_lo).fillna(0).clip(lower=0); hi = (top.lift_hi - top.lift).fillna(0).clip(lower=0)
    ax[0].errorbar(x, top.lift, yerr=[lo, hi], fmt="none", ecolor="k", capsize=3)
    ax[0].axhline(1, color="k", lw=0.8, ls="--")
    ax[0].set_xticks(x); ax[0].set_xticklabels(labels, rotation=20, ha="right", fontsize=8)
    ax[0].set_ylabel("Onset lift over always-alert")
    ax[0].set_title("Frozen LIS model on IEC 2020-2025 (no retraining)")
    if len(pairs):
        ax[1].scatter(pairs.chl_deep, pairs.chl_iec, s=14, alpha=0.6)
        lim = [0.3, max(pairs.chl_deep.max(), pairs.chl_iec.max()) * 1.1]
        ax[1].plot(lim, lim, "k--", lw=0.8); ax[1].set_xscale("log"); ax[1].set_yscale("log")
        ax[1].axvline(10, color="grey", lw=0.6); ax[1].axhline(10, color="grey", lw=0.6)
        ax[1].set_xlabel("CT DEEP chlorophyll (ug/L)"); ax[1].set_ylabel("IEC chlorophyll (ug/L)")
        ax[1].set_title(f"Same-station pairs within +/-{DAY_TOL} d (n={len(pairs)})")
    fig.tight_layout(); fig.savefig(OUT_FIG, dpi=160)
    print(f"Saved {OUT_RES}, {OUT_PAIRS}, {OUT_FIG}")
    cols = ["scenario", "model", "threshold", "n", "n_pos", "base_rate", "precision", "pod",
            "lift", "lift_lo", "lift_hi", "auc", "auc_lo", "auc_hi"]
    print(res[cols].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
