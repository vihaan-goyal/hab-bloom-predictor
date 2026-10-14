"""
prospective_2026.py -- the pre-registered 2026 test (notes/PROSPECTIVE_2026_PREREG.md, Amendment A1)
====================================================================================================
build  2026 station-days from DEEP's EXO profiles (M. Lyman, 2026-10-13), with every feature made
       by the same recipe as the S1 file, appended to the S1 history:
         data/hab_features_tidal_S1_2026.csv, data/gust_features_daily_2026.csv
       History rows are left exactly as they are; only 2026 rows are new.
score  fit the locked 28-day model (train <= 2020-01-01 - 28 d), check it reproduces the 2023-25
       test predictions, then score the resolved 2026 rows against the station-month calendar.
       Writes data/prospective_2026_predictions.csv.

Inputs fetched 2026-10-14 (public):
  data/raw/tidal/CO-OPS__<station>__ml_2025_2026.csv   NOAA CO-OPS monthly means, MLLW datum
  data/raw/iem_gust/iem_gust_2025_2026.csv              Iowa Environmental Mesonet, BDR/GON/HVN gusts
      (knots, local standard time), https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py

Run from repo root, base env:
    python src/models/prospective_2026.py build
    python src/models/prospective_2026.py score
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import label_rebuild as LR  # noqa: E402
import locked_pipeline as LP  # noqa: E402

EXO_XLSX = "data/raw/deep_lab_chla/Jan_Jul 2026_EXO Full Profile Data.xlsx"
S1_CSV = "data/hab_features_tidal_S1.csv"
GUST_CSV = "data/gust_features_daily.csv"
TIDE_OLD = "data/raw/tidal/CO-OPS__{}__ml.csv"
TIDE_NEW = "data/raw/tidal/CO-OPS__{}__ml_2025_2026.csv"
TIDE_STATIONS = ("8465705", "8467150", "8461490")
IEM_CSV = "data/raw/iem_gust/iem_gust_2025_2026.csv"
OUT_FEAT = "data/hab_features_tidal_S1_2026.csv"
OUT_GUST = "data/gust_features_daily_2026.csv"
OUT_PREDS = "data/prospective_2026_predictions.csv"
TEST_PREDS = "data/test_predictions_S1.csv"

START = pd.Timestamp("2026-01-01")
KT_TO_MS = 0.514444
MAX_GUST_KT = 75             # Amendment A1.5: the stored record maximum is 72 kt
MIN_PRIOR_YEARS = 3          # as add_tidal_features.py
HORIZON = 28                 # the pre-registered 28-day label (LP defaults to 21)
H = pd.Timedelta(days=HORIZON)
THRESHOLDS = {"budget, fixed": 0.47, "POD, fixed": 0.25, "budget, recomputed": 0.40, "POD, recomputed": 0.20}
N_BOOT, SEED, MIN_POS = 2000, 42, 5
NAN_2026 = ["nox_lag1", "nox_lag2", "nox_lag3", "nox_lag4", "dip_lag1", "dip_lag2", "dip_lag3", "dip_lag4",
            "nox_x_month", "dip_x_month", "nox_change", "dip_change"]


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------
def exo_rows():
    """Depth rows of the 2026 casts, dated from the cruise sheet."""
    x = pd.read_excel(EXO_XLSX, sheet_name=None, dtype={"station name": str, "stationName": str})
    e, c = x["Full Profile data"], x["LIS Cruise Info_0"]
    e = e.merge(c[["survey", "stationName", "surveyDate", "latDD", "longDD"]],
                left_on=["cruise name", "station name"], right_on=["survey", "stationName"],
                how="left", validate="many_to_one")
    assert e.surveyDate.notna().all(), "a cast has no date in the cruise sheet"
    return e.rename(columns={"station name": "station_name", "Chlorophyll ug/L": "raw_chl",
                             "Corrected Chlorophyll ug/L": "Corrected_Chlorophyll",
                             "temperature": "sea_water_temperature", "salinity": "sea_water_salinity",
                             "Dissolved Oxygen": "oxygen_concentration_in_sea_water",
                             "% saturation": "percent_saturation", "latDD": "latitude_x",
                             "longDD": "longitude_x"}).assign(
        date=lambda d: pd.to_datetime(d.surveyDate).dt.normalize())


def station_days(e):
    """One row per station and date: the mean over every depth row (as the 2025 rows);
    percent_saturation from the depth-code S row (as the deep_wq_S extracts)."""
    cols = ["raw_chl", "Corrected_Chlorophyll", "sea_water_temperature", "sea_water_salinity",
            "oxygen_concentration_in_sea_water", "latitude_x", "longitude_x"]
    d = e.groupby(["station_name", "date"], as_index=False)[cols].mean()
    ps = (e[e["depth code"] == "S"].groupby(["station_name", "date"], as_index=False)
            .percent_saturation.mean())
    d = d.merge(ps, on=["station_name", "date"], how="left")
    d["Chlorophyll"] = d.Corrected_Chlorophyll          # S1 scale: DEEP's corrected value
    d["month"] = d.date.dt.month.astype(float)
    return d


def s1_profile_obs():
    """S1 chlorophyll on every historical profile row, exactly as label_rebuild.build() makes it."""
    df = pd.read_csv(LR.FEATURES_CSV, dtype={"station_name": str})
    df["date"] = pd.to_datetime(df.date)
    df["year"] = df.date.dt.year
    prof = pd.read_csv(LR.PROFILE_CSV, usecols=["station_name", "month", "year", "time", "Chlorophyll",
                                                "Corrected_Chlorophyll"],
                       dtype={"station_name": str}, low_memory=False)
    prof["date"] = pd.to_datetime(prof.time, utc=True).dt.tz_localize(None).dt.normalize()
    corr = LR.deep_cruise_correction()
    df["Corrected_Chlorophyll"] = LR.fill_corrected(df, corr)
    prof["Corrected_Chlorophyll"] = LR.fill_corrected(prof, corr)
    s2_ratio, s2_fallback = LR.s2_year_ratios()
    v = LR.series(prof, "S1", LR.s1_year_factors(df), s2_ratio, s2_fallback)
    return pd.DataFrame({"station_name": prof.station_name, "date": prof.date, "v": v})


def tidal_monthly():
    """add_tidal_features.py's monthly table, with the 2025-26 downloads appended."""
    frames = []
    for st in TIDE_STATIONS:
        for path in (TIDE_OLD.format(st), TIDE_NEW.format(st)):
            t = pd.read_csv(path)
            t.columns = [c.strip() for c in t.columns]
            t["date"] = pd.to_datetime(t.Year.astype(str) + "-" + t.Month.astype(str).str.zfill(2) + "-01")
            t["station"] = st
            frames.append(t[["date", "station", "GT", "MSL"]])
    a = pd.concat(frames).drop_duplicates(["date", "station"], keep="first")   # stored file wins
    m = a.groupby("date").agg(tidal_gt=("GT", "mean"), tidal_msl=("MSL", "mean")).reset_index()
    m = m.sort_values("date").reset_index(drop=True)
    m["month_num"] = m.date.dt.month
    for col in ("tidal_gt", "tidal_msl"):
        g = m.groupby("month_num")[col]
        mean = g.transform(lambda s: s.expanding().mean().shift(1))
        n = g.transform(lambda s: s.expanding().count().shift(1))
        m[f"{col}_anom"] = m[col] - mean.where(n >= MIN_PRIOR_YEARS)
    m["month_start"] = m.date + pd.offsets.MonthBegin(1)      # join the PREVIOUS month's values
    return m[["month_start", "tidal_gt", "tidal_msl", "tidal_gt_anom", "tidal_msl_anom"]]


def gust_daily():
    """Stored daily gusts, plus mesonet days from 2026 on (Amendment A1.5); history unchanged."""
    old = pd.read_csv(GUST_CSV, parse_dates=["date"])
    g = pd.read_csv(IEM_CSV, na_values=["M", "T"])
    g["gust"] = pd.to_numeric(g.gust, errors="coerce")
    g = g[g.gust.le(MAX_GUST_KT)]
    g["date"] = pd.to_datetime(g.valid).dt.normalize()
    new = (g.assign(max_gust_ms=g.gust * KT_TO_MS).groupby("date", as_index=False).max_gust_ms.max())
    new = new[new.date > old.date.max()]
    both = pd.concat([old[["date", "max_gust_ms"]], new], ignore_index=True).sort_values("date")
    both["max_gust_3d"] = both.max_gust_ms.rolling(3, min_periods=2).max()
    add = both[both.date >= START]
    return pd.concat([old, add], ignore_index=True), new


def build():
    hist = pd.read_csv(S1_CSV, dtype={"station_name": str})
    hist["date"] = pd.to_datetime(hist.date)
    hist = hist.merge(LP._load_percent_saturation(), on=["date", "station_name"], how="left")
    e = exo_rows()
    new = station_days(e)
    unknown = sorted(set(new.station_name) - set(hist.station_name))
    print(f"2026 casts: {len(new)} station-days, {new.station_name.nunique()} stations, "
          f"{new.date.min().date()} to {new.date.max().date()}; stations not in history: {unknown}")
    new = new[new.station_name.isin(set(hist.station_name))]

    comb = pd.concat([hist, new.drop(columns="raw_chl")], ignore_index=True)
    comb = comb.sort_values(["station_name", "date"]).reset_index(drop=True)
    assert not comb.duplicated(["station_name", "date"]).any()
    is_new = (comb.date >= START).values
    g = comb.groupby("station_name")

    calc = pd.DataFrame(index=comb.index)
    for k in range(1, 5):
        calc[f"chl_lag{k}"] = g.Chlorophyll.shift(k)
        calc[f"temp_lag{k}"] = g.sea_water_temperature.shift(k)
        calc[f"do_lag{k}"] = g.oxygen_concentration_in_sea_water.shift(k)
        calc[f"sal_lag{k}"] = g.sea_water_salinity.shift(k)
    for n, mp in [(3, 2), (6, 3), (9, 5)]:
        calc[f"chl_roll{n}_mean"] = g.Chlorophyll.transform(lambda x: x.rolling(n, min_periods=mp).mean())
    calc["chl_trend"] = g.Chlorophyll.transform(lambda x: x.rolling(4, min_periods=3).apply(LR.slope, raw=True))

    obs = pd.concat([s1_profile_obs(),
                     e[["station_name", "date"]].assign(v=e.Corrected_Chlorophyll.values)], ignore_index=True)
    calc["chl_climatology"] = LR.causal_climatology(comb, obs)
    calc["chl_anomaly"] = comb.Chlorophyll - calc.chl_climatology
    calc["chl_anomaly_pct"] = calc.chl_anomaly / calc.chl_climatology * 100
    calc["neighbor_chl3_mean"] = LR.neighbour_mean(comb).values
    calc["neighbor_chl3_lag1"] = calc.groupby(comb.station_name).neighbor_chl3_mean.shift(1)

    tide = tidal_monthly()
    t = comb[["date"]].assign(month_start=comb.date.values.astype("datetime64[M]")).merge(
        tide, on="month_start", how="left")
    for c in ("tidal_gt", "tidal_msl", "tidal_gt_anom", "tidal_msl_anom"):
        calc[c] = t[c].values

    # gate: the recipe must reproduce the stored S1 history (2025 rows, where every input exists)
    chk = (comb.date.dt.year == 2025).values
    print("\nGate: recipe vs stored 2025 rows")
    bad = []
    for c in calc.columns:
        a, b = calc.loc[chk, c].values.astype(float), comb.loc[chk, c].values.astype(float)
        same_nan = np.isnan(a) == np.isnan(b)
        diff = np.nanmax(np.abs(a - b)) if (np.isfinite(a) & np.isfinite(b)).any() else 0.0
        ok = same_nan.all() and diff < 1e-9
        bad += [] if ok else [c]
        print(f"  {c:<20} max diff {diff:.1e}  null mismatches {(~same_nan).sum():>3}  {'ok' if ok else 'FAIL'}")
    if bad:
        sys.exit(f"Gate FAILED on {bad}. Nothing written.")

    for c in calc.columns:
        comb.loc[is_new, c] = calc.loc[is_new, c].values
    comb.loc[is_new, [c for c in NAN_2026 if c in comb.columns]] = np.nan
    comb.to_csv(OUT_FEAT, index=False)

    gust, mesonet = gust_daily()
    gust.to_csv(OUT_GUST, index=False)
    n26 = comb[is_new]
    print(f"\nWrote {OUT_FEAT}: {is_new.sum()} new 2026 rows (history {len(hist)} rows unchanged)")
    print(f"Wrote {OUT_GUST}: mesonet days {mesonet.date.min().date()} to {mesonet.date.max().date()}")
    print("2026 coverage: " + ", ".join(f"{c} {n26[c].notna().mean():.0%}" for c in
                                        ["Chlorophyll", "percent_saturation", "tidal_gt_anom", "chl_lag1"]))


# ---------------------------------------------------------------------------
# score
# ---------------------------------------------------------------------------
def calendar(rows, hist):
    """Station-month bloom rate over labelled rows dated before 2026-01-01 - 28 d (>= 5 rows),
    else the month rate across stations, else the overall rate."""
    past = hist[hist.date < START - H]
    sm = past.groupby(["station_name", "month"]).y.agg(["mean", "size"])
    mo = past.groupby("month").y.agg(["mean", "size"])
    out = []
    for s, m in zip(rows.station_name, rows.date.dt.month):
        if (s, m) in sm.index and sm.loc[(s, m), "size"] >= MIN_POS:
            out.append(sm.loc[(s, m), "mean"])
        elif m in mo.index and mo.loc[m, "size"] >= MIN_POS:
            out.append(mo.loc[m, "mean"])
        else:
            out.append(past.y.mean())
    return np.array(out)


def at_threshold(y, alerts_mask, months):
    tp = int((alerts_mask & (y == 1)).sum())
    return dict(alerts=int(alerts_mask.sum()), tp=tp,
                precision=tp / alerts_mask.sum() if alerts_mask.any() else np.nan,
                recall=tp / y.sum() if y.sum() else np.nan,
                alerts_per_month=alerts_mask.sum() / months)


def score():
    df = LP.load_locked_dataframe(base_csv=OUT_FEAT, gust_csv=OUT_GUST)
    df["station_name"] = df.station_name.astype(str)
    df = LP.add_forward_label(df, horizon=HORIZON)
    bundle = LP.fit_locked_model(df, "bloom_fwd", train_end="2020-01-01", purge_days=HORIZON)
    print(f"Locked model: {bundle['n_train']} training rows, train bloom rate {bundle['train_bloom_rate']:.3f}")

    # gate: identical to the 2023-25 test predictions
    ref = pd.read_csv(TEST_PREDS, dtype={"station_name": str}, parse_dates=["date"])
    t = df.merge(ref, on=["station_name", "date"], how="inner")
    diff = np.abs(LP.predict_proba(bundle, t) - t.y_prob.values).max()
    lab = (t.bloom_fwd.values == t.y_true.values).all()
    print(f"Gate: {len(t)} of {len(ref)} test rows matched, max |p diff| {diff:.2e}, labels equal: {lab}")
    if len(t) != len(ref) or diff > 1e-9 or not lab:
        sys.exit("Gate FAILED: the model does not reproduce the 2023-25 test. Not scoring 2026.")

    rows = df[(df.date >= START)].copy()
    n_all = len(rows)
    rows = rows.dropna(subset=["bloom_fwd"]).reset_index(drop=True)
    rows["p"] = LP.predict_proba(bundle, rows)
    hist = df.dropna(subset=["bloom_fwd"]).assign(y=lambda d: d.bloom_fwd, month=lambda d: d.date.dt.month)
    rows["cal"] = calendar(rows, hist)
    y = rows.bloom_fwd.values.astype(int)
    rows[["station_name", "date", "Chlorophyll", "bloom_fwd", "p", "cal"]].to_csv(OUT_PREDS, index=False)

    print(f"\n2026 rows: {n_all} station-days, {len(rows)} with a resolved 28-day window "
          f"({rows.date.min().date()} to {rows.date.max().date()}), events {y.sum()}, "
          f"base rate {y.mean():.3f}")
    if y.sum() == 0:
        print("No positive rows: AUC undefined. Test UNDERPOWERED; descriptive only.")
        return
    am, ac = roc_auc_score(y, rows.p), roc_auc_score(y, rows.cal)
    rng = np.random.default_rng(SEED)
    keys = rows.station_name.values
    groups = [np.where(keys == k)[0] for k in pd.unique(keys)]
    diffs = []
    for _ in range(N_BOOT):
        b = np.concatenate([groups[i] for i in rng.integers(0, len(groups), len(groups))])
        if 0 < y[b].sum() < len(b):
            diffs.append(roc_auc_score(y[b], rows.p.values[b]) - roc_auc_score(y[b], rows.cal.values[b]))
    diffs = np.array(diffs)
    verdict = ("UNDERPOWERED (< 5 positive rows): descriptive only" if y.sum() < MIN_POS else
               "beats the calendar" if (diffs <= 0).mean() < 0.05 else "does not beat the calendar")
    print(f"PRIMARY: model AUC {am:.3f}, calendar AUC {ac:.3f}, difference {am - ac:+.3f} "
          f"[{np.percentile(diffs, 2.5):+.3f}, {np.percentile(diffs, 97.5):+.3f}], "
          f"one-sided p = {(diffs <= 0).mean():.3f}  -> {verdict}")

    months = rows.date.dt.to_period("M").nunique()
    print(f"\nSECONDARY (descriptive; {months} sampled months)")
    for name, thr in THRESHOLDS.items():
        m = at_threshold(y, rows.p.values >= thr, months)
        k = m["alerts"]
        top = np.zeros(len(rows), bool)
        top[np.argsort(-rows.cal.values, kind="stable")[:k]] = True
        c = at_threshold(y, top, months)
        print(f"  t = {thr:.2f} ({name}): model {m['alerts']} alerts ({m['alerts_per_month']:.1f}/month), "
              f"TP {m['tp']}, precision {m['precision']:.3f}, recall {m['recall']:.3f} | "
              f"calendar top-{k}: TP {c['tp']}, precision {c['precision']:.3f}, recall {c['recall']:.3f}")
    print(f"\nWrote {OUT_PREDS}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["build", "score"])
    {"build": build, "score": score}[ap.parse_args().cmd]()


if __name__ == "__main__":
    main()
