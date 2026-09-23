"""
label_rebuild.py -- put the LIS chlorophyll label on a lab-consistent scale
===========================================================================
Implements notes/LABEL_REBUILD_PREREG.md. The locked label is built from the CTD
fluorometer (`Chlorophyll`), which read 2-3x DEEP's lab chlorophyll in 1994-1999 and
2009-2013 and ~1x from 2016 on (src/models/experiments/sensor_vs_lab_chl.py). This
writes one feature file per series, with `Chlorophyll` replaced and every
chlorophyll-derived column recomputed, so the locked evaluation script can be run on
each one unchanged except for --input.

Series (defined in the pre-registration, section 3):
    S0  raw sensor, rebuilt through this code          gate G1: must equal the original
    S1  Corrected_Chlorophyll, gap-filled               primary
    S2  sensor / that year's median sensor-to-lab ratio sensitivity
    S3  S1 features, label from lab surface CHLA only   sensitivity (adds bloom_28d_lab)
    S4  lab CHLA features and label only (Amendment A1) headline label definition

Subcommands
    build     write data/hab_features_tidal_S{0,1,2,3,4}.csv, run gates G1 and G2
    compare   read data/test_predictions_S*.csv, bootstrap AUC / precision / lift,
              write data/label_rebuild_results.csv

Run from repo root:
    python src/models/label_rebuild.py build
    python src/models/final_evaluation_threshold_sweep.py --input data/hab_features_tidal_S1.csv --tag _S1
    (same for S0, S2; S3 adds --label-col bloom_28d_lab)
    python src/models/label_rebuild.py compare
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

FEATURES_CSV = "data/hab_features_tidal.csv"
PROFILE_CSV = "data/hab_labels_final.csv"      # profile rows; source of chl_climatology
LAB_CSV = "data/uconn_nutrients_raw.csv"
RATIO_CSV = "data/sensor_vs_lab_chl.csv"
OUT_TMPL = "data/hab_features_tidal_{}.csv"
PREDS_TMPL = "data/test_predictions_{}.csv"
RESULTS_CSV = "data/label_rebuild_results.csv"

BLOOM = 10.0
HORIZON_D = 28
MIN_FILL_ROWS = 30                  # S1: rows with both values needed for a year factor
KM_PER_DEG_LAT = 111.0
KM_PER_DEG_LON = 111.0 * np.cos(np.radians(41.1))   # reproduces neighbor_chl3_mean exactly
G1_TOL = 1e-9
G2_BAND = (0.75, 1.35)
G2_MIN_PAIRS = 50
T_LOCKED = 0.60
N_BOOT, SEED = 2000, 42

# columns rebuilt from the series; everything else in the file is carried over untouched
REBUILT = ["Chlorophyll", "chl_lag1", "chl_lag2", "chl_lag3", "chl_lag4",
           "chl_climatology", "chl_anomaly", "chl_anomaly_pct",
           "chl_roll3_mean", "chl_roll6_mean", "chl_roll9_mean", "chl_trend",
           "neighbor_chl3_mean", "neighbor_chl3_lag1"]
# chlorophyll-derived but not used by the model and not reproducible from station-day
# rows: dropped from the rebuilt files so no stale sensor-scale value survives. (`bloom`
# was aggregated from profile rows; it agrees with Chlorophyll > 10 on 93.5% of rows.
# The model's label is bloom_28d, recomputed from Chlorophyll by the evaluation script.)
DROPPED = ["bloom", "chl_roll3_std", "neighbor_chl3_lag2", "neighbor_chl5_mean"]


# ---------------------------------------------------------------------------
# Series
# ---------------------------------------------------------------------------
def s1_year_factors(df):
    """Median Corrected/raw per year over station-day rows that have both."""
    both = df[df.Chlorophyll.gt(0) & df.Corrected_Chlorophyll.notna()]
    ratio = (both.Corrected_Chlorophyll / both.Chlorophyll).groupby(both.year)
    fac = ratio.median().where(ratio.size() >= MIN_FILL_ROWS)
    return fac.reindex(sorted(df.year.unique())).fillna(1.0)


def s2_year_ratios():
    r = pd.read_csv(RATIO_CSV).set_index("year").sensor_over_lab
    fallback = r.loc[2016:2024].median()
    return r, fallback


def series(frame, name, s1_fac, s2_ratio, s2_fallback):
    raw, corr, yr = frame.Chlorophyll, frame.Corrected_Chlorophyll, frame.year
    if name == "S0":
        return raw.copy()
    if name in ("S1", "S3"):
        return corr.where(corr.notna(), raw * yr.map(s1_fac).fillna(1.0))
    if name == "S2":
        return raw / yr.map(s2_ratio).fillna(s2_fallback)
    raise ValueError(name)


# ---------------------------------------------------------------------------
# Feature recipe (reproduces the columns in hab_features_tidal.csv; gate G1 checks it)
# ---------------------------------------------------------------------------
def slope(v):
    """Least-squares slope over the window's positions, skipping missing values.
    Identical to np.polyfit on a window with no gaps (only S4 has gaps)."""
    m = np.isfinite(v)
    return np.polyfit(np.arange(len(v))[m], v[m], 1)[0] if m.sum() >= 2 else np.nan


def neighbour_mean(df):
    """Mean chlorophyll of each station's three nearest stations on the same date."""
    st = df.groupby("station_name")[["latitude_x", "longitude_x"]].first()
    la, lo, names = st.latitude_x.values, st.longitude_x.values, st.index.values
    nbrs = {}
    for i, s in enumerate(names):
        d = np.hypot((la - la[i]) * KM_PER_DEG_LAT, (lo - lo[i]) * KM_PER_DEG_LON)
        d[i] = np.inf
        nbrs[s] = names[np.argsort(d)[:3]]
    piv = df.pivot(index="date", columns="station_name", values="Chlorophyll")
    out = np.full(len(df), np.nan)
    for j, (s, dt) in enumerate(zip(df.station_name.values, df.date.values)):
        v = piv.loc[dt, nbrs[s]].values
        if np.isfinite(v).any():
            out[j] = np.nanmean(v)
    return pd.Series(out, index=df.index)


def rebuild(df, prof, name, s1_fac, s2_ratio, s2_fallback, lab=None):
    d = df.copy()
    if name == "S4":        # lab surface CHLA only (Amendment A1); empty where no sample
        d["Chlorophyll"] = d[["station_name", "date"]].merge(
            lab, on=["station_name", "date"], how="left").lab.values
    else:
        d["Chlorophyll"] = series(d, name, s1_fac, s2_ratio, s2_fallback)
    g = d.groupby("station_name")["Chlorophyll"]
    for k in range(1, 5):
        d[f"chl_lag{k}"] = g.shift(k)
    for n, mp in [(3, 2), (6, 3), (9, 5)]:
        d[f"chl_roll{n}_mean"] = g.transform(lambda x: x.rolling(n, min_periods=mp).mean())
    d["chl_trend"] = g.transform(lambda x: x.rolling(4, min_periods=3).apply(slope, raw=True))

    # climatology: station x month mean over every profile reading, all years, as in
    # notebooks/eda_labels.ipynb cell 11
    if name == "S4":        # lab analogue: every lab surface sample, all years
        clim = lab.groupby([lab.station_name, lab.date.dt.month.rename("month")]).lab.mean()
        clim = clim.rename("clim").astype(float)
        clim.index = clim.index.set_levels(clim.index.levels[1].astype(float), level=1)
    else:
        p = prof.copy()
        p["Chlorophyll"] = series(p, name, s1_fac, s2_ratio, s2_fallback)
        clim = p.groupby(["station_name", "month"]).Chlorophyll.mean().rename("clim")
    d = d.drop(columns="chl_climatology").merge(clim.reset_index(), on=["station_name", "month"],
                                                how="left").rename(columns={"clim": "chl_climatology"})
    d.index = df.index
    d["chl_anomaly"] = d.Chlorophyll - d.chl_climatology
    d["chl_anomaly_pct"] = d.chl_anomaly / d.chl_climatology * 100

    d["neighbor_chl3_mean"] = neighbour_mean(d)
    d["neighbor_chl3_lag1"] = d.groupby("station_name")["neighbor_chl3_mean"].shift(1)
    return d[df.columns]


# ---------------------------------------------------------------------------
# Lab label for S3
# ---------------------------------------------------------------------------
def load_lab():
    raw = pd.read_csv(LAB_CSV, low_memory=False)
    lab = raw[(raw.Parameter == "CHLA") & (raw.Depth_Code == "S")].copy()
    lab["date"] = pd.to_datetime(lab.time).dt.tz_localize(None).dt.normalize()
    lab["lab"] = pd.to_numeric(lab.Result, errors="coerce")
    lab["station_name"] = lab.Station_Name.astype(str).str.strip()
    return lab.dropna(subset=["lab"]).groupby(["station_name", "date"]).lab.mean().reset_index()


def lab_label(df, lab):
    """1 if any lab sample in (date, date+28d] exceeds 10; NaN if the window holds none
    or runs past the last lab date."""
    last = lab.date.max()
    by_st = {s: g.sort_values("date") for s, g in lab.groupby("station_name")}
    out = np.full(len(df), np.nan)
    h = np.timedelta64(HORIZON_D, "D")
    for j, (s, dt) in enumerate(zip(df.station_name.values, df.date.values)):
        if s not in by_st or dt + h > last:
            continue
        g = by_st[s]
        w = g.lab.values[(g.date.values > dt) & (g.date.values <= dt + h)]
        if len(w):
            out[j] = float((w > BLOOM).any())
    return pd.Series(out, index=df.index), last


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------
def build():
    df = pd.read_csv(FEATURES_CSV, dtype={"station_name": str})
    df["date"] = pd.to_datetime(df.date)
    df["year"] = df.date.dt.year
    keep_cols = [c for c in df.columns if c not in DROPPED]
    prof = pd.read_csv(PROFILE_CSV, usecols=["station_name", "month", "year", "Chlorophyll",
                                             "Corrected_Chlorophyll"],
                       dtype={"station_name": str}, low_memory=False)
    s1_fac = s1_year_factors(df)
    s2_ratio, s2_fallback = s2_year_ratios()
    print("S1 gap-fill factor (Corrected/raw) for years not fully covered:")
    cov = df.groupby("year").Corrected_Chlorophyll.apply(lambda s: s.notna().mean())
    for y in cov.index[cov < 1]:
        print(f"  {y}: coverage {cov[y]:.2f}, factor {s1_fac[y]:.3f}")
    print(f"S2 ratio for 2025 (no lab yet): 2016-2024 median = {s2_fallback:.3f}")

    # ---- gate G1 -------------------------------------------------------------
    s0 = rebuild(df, prof, "S0", s1_fac, s2_ratio, s2_fallback)
    print("\nGate G1: S0 rebuilt through this code vs the original columns")
    ok = True
    for c in REBUILT:
        a, b = df[c], s0[c]
        nn = int((a.notna() != b.notna()).sum())
        both = a.notna() & b.notna()
        diff = float(np.abs(a[both] - b[both]).max()) if both.any() else 0.0
        good = nn == 0 and diff <= G1_TOL
        ok &= good
        print(f"  {c:<20} max diff {diff:.2e}  null mismatches {nn:>4}  {'ok' if good else 'FAIL'}")
    if not ok:
        sys.exit("Gate G1 FAILED: the rebuild does not reproduce the original features. "
                 "Nothing else was written.")
    print("  G1 passed at the feature level. Still to check: the default run must reproduce "
          "test AUC 0.8150.")

    # ---- series + gate G2 ------------------------------------------------------
    lab = load_lab()
    out = {"S0": s0}
    for name in ("S1", "S2", "S3", "S4"):
        out[name] = rebuild(df, prof, name, s1_fac, s2_ratio, s2_fallback, lab)
    lab_y, last = lab_label(df, lab)
    out["S3"]["bloom_28d_lab"] = lab_y
    out["S4"]["bloom_28d_lab"] = lab_y
    print(f"S4 lab chlorophyll present on {out['S4'].Chlorophyll.notna().mean():.1%} "
          f"of station-days")

    print(f"\nGate G2: median series / lab per year, band {G2_BAND}, years with >= "
          f"{G2_MIN_PAIRS} pairs")
    ok2 = True
    for name in ("S1", "S2"):
        m = out[name][["station_name", "date", "year", "Chlorophyll"]].merge(
            lab, on=["station_name", "date"])
        m = m[m.lab >= 0.5]
        r = (m.Chlorophyll / m.lab).groupby(m.year).agg(["median", "size"])
        r = r[r["size"] >= G2_MIN_PAIRS]
        bad = r[(r["median"] < G2_BAND[0]) | (r["median"] > G2_BAND[1])]
        ok2 &= bad.empty
        print(f"  {name}: {len(r)} years, ratio {r['median'].min():.2f}-{r['median'].max():.2f}"
              f"  {'ok' if bad.empty else 'FAIL in ' + ', '.join(map(str, bad.index))}")
    if not ok2:
        sys.exit("Gate G2 FAILED: a series is off lab scale. Files were not written.")

    for name, d in out.items():
        cols = keep_cols + (["bloom_28d_lab"] if name in ("S3", "S4") else [])
        d = d.drop(columns="year", errors="ignore")
        d[[c for c in cols if c in d.columns and c != "year"]].to_csv(
            OUT_TMPL.format(name), index=False)
        print(f"Wrote {OUT_TMPL.format(name)}")

    print(f"\nS3 lab label: last lab date {last.date()}, "
          f"{int(lab_y.notna().sum()):,} of {len(df):,} rows labelled, "
          f"positive share {np.nanmean(lab_y):.3f}")
    print("\nOne-day share of station-days above 10 ug/L, by period:")
    for name in ("S0", "S1", "S2", "S4"):
        d = out[name]
        s = [f"{a}-{b}: {(d.Chlorophyll[(d.year >= a) & (d.year <= b)].dropna() > BLOOM).mean():.3f}"
             for a, b in [(1994, 1999), (2009, 2013), (2014, 2019), (2023, 2025)]]
        print(f"  {name}  " + "   ".join(s))


# ---------------------------------------------------------------------------
# compare
# ---------------------------------------------------------------------------
def auc(y, p):
    from sklearn.metrics import roc_auc_score
    return roc_auc_score(y, p) if 0 < y.sum() < len(y) else np.nan


def point(d, t):
    y, p = d.y_true.values, d.y_prob.values
    pred = p >= t
    base = y.mean()
    prec = y[pred].mean() if pred.any() else np.nan
    rec = pred[y == 1].mean() if y.any() else np.nan
    return dict(auc=auc(y, p), base_rate=base, precision=prec, recall=rec,
                lift=prec / base if base > 0 else np.nan, n=len(y), positives=int(y.sum()),
                alerts=int(pred.sum()))


def boot(d, t):
    d = d.assign(cl=d.station_name.astype(str) + "_" + pd.to_datetime(d.date).dt.year.astype(str))
    groups = {k: g for k, g in d.groupby("cl")}
    keys = np.array(list(groups))
    rng = np.random.default_rng(SEED)
    draws = []
    for _ in range(N_BOOT):
        s = pd.concat([groups[k] for k in rng.choice(keys, len(keys), replace=True)])
        draws.append(point(s, t))
    b = pd.DataFrame(draws)
    return {f"{k}_{q}": b[k].quantile(v) for k in ("auc", "precision", "lift", "base_rate")
            for q, v in (("lo", 0.025), ("hi", 0.975))}


def compare(val_thresholds):
    rows = []
    for name in ("S0", "S1", "S2", "S3", "S4"):
        f = PREDS_TMPL.format(name)
        if not os.path.exists(f):
            print(f"  {name}: {f} missing, skipped")
            continue
        d = pd.read_csv(f)
        for label, t in (("locked 0.60", T_LOCKED), ("validation F1", val_thresholds.get(name))):
            if t is None:
                continue
            r = dict(series=name, operating_point=label, threshold=t, **point(d, t), **boot(d, t))
            rows.append(r)
    res = pd.DataFrame(rows)
    res.to_csv(RESULTS_CSV, index=False, float_format="%.4f")
    pd.set_option("display.width", 200)
    show = res[["series", "operating_point", "threshold", "n", "positives", "base_rate", "auc",
                "auc_lo", "auc_hi", "precision", "precision_lo", "precision_hi", "recall",
                "lift", "lift_lo", "lift_hi"]]
    print(show.round(3).to_string(index=False))
    print(f"\nWrote {RESULTS_CSV} ({N_BOOT} station-year cluster resamples, seed {SEED})")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build")
    c = sub.add_parser("compare")
    c.add_argument("--val-thresholds", default="",
                   help="validation-chosen thresholds, e.g. S0=0.55,S1=0.60,S2=0.55,S3=0.50")
    a = ap.parse_args()
    if a.cmd == "build":
        build()
    else:
        vt = dict((k, float(v)) for k, v in (x.split("=") for x in a.val_thresholds.split(",") if x))
        compare(vt)


if __name__ == "__main__":
    main()
