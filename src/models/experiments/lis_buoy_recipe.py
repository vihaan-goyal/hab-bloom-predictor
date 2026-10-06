"""
W6 LIS buoy recipe test
=======================

Question: does the "sampling cadence" thesis hold INSIDE Long Island Sound?
LIS boat sampling (~21-day gaps) caps bloom-forecast precision at ~0.14
(lift 2.7 at base rate 0.046).  In Narragansett Bay, 15-min sondes + the same
recipe give onset precision ~0.70 (lift 2.0 at base 0.35).  Here we apply the
same Tier-A recipe to UConn LISICOS buoy fluorescence (15-min ECO-FL).

Input : data/buoy_eco_fl/all_buoys_eco_fl.parquet
Output: data/lis_buoy_recipe.csv  (one row per split x threshold-def x horizon
        x subset x model/baseline)

Calibration of Avg_FL to lab chl-a failed (R^2 0.13 / 0.02), so everything is
done in fluorescence space (raw ECO-FL counts).

Run from repo root:
    ~/anaconda3/python.exe src/models/experiments/lis_buoy_recipe.py
"""

from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[3]
PARQUET = ROOT / "data" / "buoy_eco_fl" / "all_buoys_eco_fl.parquet"
OUT_CSV = ROOT / "data" / "lis_buoy_recipe.csv"

NIGHT_HOURS = [21, 22, 23, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]  # UTC, de-quench
MIN_READINGS_PER_DAY = 12
MAX_STUCK_FRAC = 0.5          # drop a day if >50% of night readings are one value
FL_MIN, FL_MAX = 0.0, 5000.0  # drop zero/negative and spike readings
MIN_YEARS_PER_BUOY = 3
MIN_TRAIN_DAYS_PER_BUOY = 60
HORIZONS = [7, 21]
THRESH_DEFS = {"p75": 0.75, "p95_5pct": 0.95}  # 5% exceedance == p95 of daily means

SPLITS = {
    # prescribed by the task; stated as-is even though train is tiny
    "prescribed_tr<=2019_va20-22_te23-25": dict(train=(1900, 2019), val=(2020, 2022), test=(2023, 2025)),
    # feasible split given actual buoy coverage (2019-2026)
    "feasible_tr<=2022_va23-24_te25-26": dict(train=(1900, 2022), val=(2023, 2024), test=(2025, 2026)),
}

# Reference numbers for the pre-registered read
LIS_BOAT = dict(precision=0.14, lift=2.7, base=0.046)
NARR = dict(precision=0.70, lift=2.0, base=0.35)


# --------------------------------------------------------------------------- #
# 1. Load + inventory + de-quench + daily aggregation
# --------------------------------------------------------------------------- #
def load_daily() -> tuple[pd.DataFrame, dict]:
    raw = pd.read_parquet(PARQUET)
    raw["time"] = pd.to_datetime(raw["time"], utc=True)
    raw["buoy"] = raw["station"].str.replace("_WQ_SFC", "", regex=False)
    raw["year"] = raw["time"].dt.year
    raw["hour"] = raw["time"].dt.hour

    inv = {}
    print("=" * 78)
    print("DATA INVENTORY  (raw 15-min ECO-FL readings)")
    print("=" * 78)
    print(raw.groupby(["buoy", "year"]).size().unstack(0).fillna(0).astype(int).to_string())
    extra = [c for c in raw.columns if any(k in c.lower() for k in ("temp", "sal", "do_", "oxy", "cond"))]
    print(f"\nExtra temp/sal/DO columns present: {extra if extra else 'NONE'}")
    print("\nMean Avg_FL by UTC hour (quenching check):")
    print(raw.groupby(["buoy", "hour"])["Avg_FL"].mean().unstack(0).round(1).to_string())

    yrs = raw.groupby("buoy")["year"].nunique()
    keep = yrs[yrs >= MIN_YEARS_PER_BUOY].index.tolist()
    print(f"\nYears of data per buoy: {yrs.to_dict()}  -> keeping {keep} (>= {MIN_YEARS_PER_BUOY} yrs)")
    inv["buoys"] = keep

    df = raw[raw["buoy"].isin(keep)].copy()
    n0 = len(df)
    df = df[(df["Avg_FL"] > FL_MIN) & (df["Avg_FL"] < FL_MAX)]
    print(f"QC: dropped {n0 - len(df)} readings outside ({FL_MIN}, {FL_MAX})")
    n1 = len(df)
    df = df[df["hour"].isin(NIGHT_HOURS)]
    print(f"De-quench: kept {len(df)} / {n1} readings in night hours {NIGHT_HOURS}")

    df["date"] = df["time"].dt.floor("D").dt.tz_localize(None)
    grp = df.groupby(["buoy", "date"])["Avg_FL"]
    daily = grp.agg(value="mean", n="count").reset_index()
    stuck = grp.agg(lambda s: s.value_counts(normalize=True).iloc[0]).rename("stuck_frac").reset_index()
    daily = daily.merge(stuck, on=["buoy", "date"])

    n_days0 = len(daily)
    bad_n = daily["n"] < MIN_READINGS_PER_DAY
    bad_stuck = daily["stuck_frac"] > MAX_STUCK_FRAC
    print(f"Daily: {n_days0} buoy-days; drop {bad_n.sum()} with <{MIN_READINGS_PER_DAY} night readings, "
          f"{(bad_stuck & ~bad_n).sum()} more with stuck sensor (>{MAX_STUCK_FRAC:.0%} identical)")
    daily = daily[~bad_n & ~bad_stuck].copy()

    # Reindex to full calendar per buoy so gaps stay as NaN (lags/rolls honour gaps)
    parts = []
    for b, g in daily.groupby("buoy"):
        idx = pd.date_range(g["date"].min(), g["date"].max(), freq="D")
        gg = g.set_index("date").reindex(idx)
        gg["buoy"] = b
        gg.index.name = "date"
        parts.append(gg.reset_index())
    daily = pd.concat(parts, ignore_index=True)
    daily["year"] = daily["date"].dt.year
    daily["month"] = daily["date"].dt.month
    daily["doy"] = daily["date"].dt.dayofyear

    print("\nValid daily night-means per buoy-year (after QC):")
    valid = daily.dropna(subset=["value"])
    print(valid.groupby(["buoy", "year"]).size().unstack(0).fillna(0).astype(int).to_string())
    gaps = daily.groupby("buoy")["value"].apply(lambda s: s.isna().sum())
    print(f"\nCalendar gaps (missing days inside each buoy's span): {gaps.to_dict()}")
    print("\nDaily night-mean Avg_FL distribution:")
    print(valid.groupby("buoy")["value"].describe().round(1).to_string())
    inv["daily_valid"] = valid.groupby("buoy").size().to_dict()
    return daily, inv


# --------------------------------------------------------------------------- #
# 2. Features
# --------------------------------------------------------------------------- #
def build_features(daily: pd.DataFrame, train_years: tuple[int, int]) -> pd.DataFrame:
    out = []
    for b, g in daily.groupby("buoy"):
        g = g.sort_values("date").copy()
        v = g["value"]
        for k in range(1, 5):
            g[f"lag{k}"] = v.shift(k)
        for w in (3, 6, 9, 14, 21):
            g[f"roll{w}"] = v.rolling(w, min_periods=max(2, int(0.6 * w))).mean()
        g["trend"] = v - g["roll6"]
        # buoy x 15-day DOY climatology on TRAIN years only
        g["doy_bin"] = ((g["doy"] - 1) // 15).clip(upper=23)
        tr = g[(g["year"] >= train_years[0]) & (g["year"] <= train_years[1])]
        clim = tr.groupby("doy_bin")["value"].mean()
        g["clim"] = g["doy_bin"].map(clim)
        g["anom"] = v - g["clim"]
        g["is_EXRX"] = int(b == "EXRX")
        out.append(g)
    return pd.concat(out, ignore_index=True)


FEATURES = ["value", "lag1", "lag2", "lag3", "lag4", "roll3", "roll6", "roll9", "roll14", "roll21",
            "trend", "clim", "anom", "month", "is_EXRX"]


# --------------------------------------------------------------------------- #
# 3. Labels (forward, right-censored)
# --------------------------------------------------------------------------- #
def forward_label(g: pd.DataFrame, thr: float, H: int) -> pd.Series:
    """1 if any observed daily mean in t+1..t+H exceeds thr; 0 if all H forward
    days are observed and none exceed; NaN otherwise (gap / right-censored)."""
    v = g["value"].to_numpy()
    n = len(v)
    lab = np.full(n, np.nan)
    for i in range(n):
        fwd = v[i + 1:i + 1 + H]
        if len(fwd) < H:
            if np.nanmax(fwd, initial=-np.inf) > thr:
                lab[i] = 1.0
            continue  # right-censored
        if np.any(fwd > thr):
            lab[i] = 1.0
        elif not np.isnan(fwd).any():
            lab[i] = 0.0
    return pd.Series(lab, index=g.index)


# --------------------------------------------------------------------------- #
# 4. Models / evaluation
# --------------------------------------------------------------------------- #
def make_lr():
    return Pipeline([
        ("imp", SimpleImputer(strategy="median")),
        ("sc", StandardScaler()),
        ("lr", LogisticRegression(C=0.05, class_weight="balanced", max_iter=5000)),
    ])


def make_hgb():
    return HistGradientBoostingClassifier(
        max_depth=3, learning_rate=0.05, max_iter=300, min_samples_leaf=50,
        l2_regularization=1.0, class_weight="balanced", random_state=42)


def best_f1_threshold(y, p, grid=None):
    if grid is None:
        grid = np.unique(np.round(p, 3))
        if len(grid) > 400:
            grid = np.quantile(p, np.linspace(0.01, 0.99, 400))
    best_t, best_f = 0.5, -1.0
    for t in grid:
        f = f1_score(y, (p >= t).astype(int), zero_division=0)
        if f > best_f:
            best_f, best_t = f, t
    return best_t


def metrics(y, p, t, n_train, n_val):
    y = np.asarray(y).astype(int)
    a = (p >= t).astype(int)
    base = y.mean() if len(y) else np.nan
    prec = precision_score(y, a, zero_division=np.nan) if a.sum() > 0 else np.nan
    pod = recall_score(y, a, zero_division=0)
    auc = roc_auc_score(y, p) if (len(np.unique(y)) == 2 and len(np.unique(p)) > 1) else np.nan
    return dict(t_star=float(t), auc=auc, precision=prec, pod=pod, base_rate=base,
                lift=(prec / base if (base and not np.isnan(prec)) else np.nan),
                n_test=int(len(y)), n_pos=int(y.sum()), n_alerts=int(a.sum()),
                n_train=int(n_train), n_val=int(n_val))


def run_config(feat: pd.DataFrame, split_name: str, split: dict, thr_name: str, q: float, H: int, rows: list):
    tr_y, va_y, te_y = split["train"], split["val"], split["test"]
    in_rng = lambda s, r: (s >= r[0]) & (s <= r[1])
    d = feat.copy()

    # thresholds per buoy on train years only
    thr = {}
    for b, g in d.groupby("buoy"):
        tr = g[in_rng(g["year"], tr_y)]["value"].dropna()
        if len(tr) < MIN_TRAIN_DAYS_PER_BUOY:
            continue
        thr[b] = float(tr.quantile(q))
    if not thr:
        print(f"[{split_name} | {thr_name} | H={H}] no buoy has >= {MIN_TRAIN_DAYS_PER_BUOY} train days; skipped")
        return
    d = d[d["buoy"].isin(thr)].copy()
    d["thr"] = d["buoy"].map(thr)
    d["y"] = np.nan
    for b, g in d.groupby("buoy"):
        d.loc[g.index, "y"] = forward_label(g, thr[b], H)
    d["above_today"] = d["value"] > d["thr"]
    d = d.dropna(subset=["value", "y"])

    tr = d[in_rng(d["year"], tr_y)]
    va = d[in_rng(d["year"], va_y)]
    te = d[in_rng(d["year"], te_y)]
    print(f"\n[{split_name} | thr={thr_name} | H={H}]  thresholds={ {k: round(v, 1) for k, v in thr.items()} }")
    print(f"   n_train={len(tr)} (pos {int(tr.y.sum())})  n_val={len(va)} (pos {int(va.y.sum())})  "
          f"n_test={len(te)} (pos {int(te.y.sum())})   test buoys: {te.groupby('buoy').size().to_dict()}")
    if len(tr) < 30 or tr["y"].nunique() < 2 or len(te) == 0 or len(va) == 0:
        print("   -> too thin to fit/evaluate; recording NaNs")
        for subset in ("all", "onset"):
            for m in ("LR", "HistGB", "always_alert", "persistence", "threshold_rule"):
                rows.append(dict(split=split_name, thr_def=thr_name, horizon=H, subset=subset, model=m,
                                 t_star=np.nan, auc=np.nan, precision=np.nan, pod=np.nan, base_rate=np.nan,
                                 lift=np.nan, n_test=len(te), n_pos=int(te.y.sum()) if len(te) else 0,
                                 n_alerts=0, n_train=len(tr), n_val=len(va), thresholds=str(thr)))
        return

    Xtr, ytr = tr[FEATURES], tr["y"].astype(int)
    preds = {}
    for name, mk in (("LR", make_lr), ("HistGB", make_hgb)):
        mdl = mk().fit(Xtr, ytr)
        preds[name] = (mdl.predict_proba(va[FEATURES])[:, 1], mdl.predict_proba(te[FEATURES])[:, 1])

    for subset in ("all", "onset"):
        if subset == "all":
            vm, tm = np.ones(len(va), bool), np.ones(len(te), bool)
        else:
            vm, tm = (~va["above_today"]).to_numpy(), (~te["above_today"]).to_numpy()
        yv, yt = va["y"].to_numpy()[vm].astype(int), te["y"].to_numpy()[tm].astype(int)
        if len(yt) == 0:
            continue
        common = dict(split=split_name, thr_def=thr_name, horizon=H, subset=subset, thresholds=str(thr))

        for name, (pv, pt) in preds.items():
            if yv.sum() == 0:
                t = 0.5
            else:
                t = best_f1_threshold(yv, pv[vm])
            rows.append(dict(**common, model=name, **metrics(yt, pt[tm], t, len(tr), len(va))))
            if subset == "onset" and H == 7 and split_name.startswith("feasible"):
                buoys_t = te["buoy"].to_numpy()[tm]
                lines = []
                for b in sorted(set(buoys_t)):
                    mb = buoys_t == b
                    m = metrics(yt[mb], pt[tm][mb], t, len(tr), len(va))
                    lines.append(f"  {name:7s} {b}: precision={m['precision']:.3f} POD={m['pod']:.2f} "
                                 f"base={m['base_rate']:.3f} lift={m['lift']:.2f} n={m['n_test']} "
                                 f"n_pos={m['n_pos']} alerts={m['n_alerts']}")
                PER_BUOY[thr_name] = PER_BUOY.get(thr_name, "") + "\n".join(lines) + "\n"

        # baselines
        rows.append(dict(**common, model="always_alert",
                         **metrics(yt, np.ones(len(yt)), 0.5, len(tr), len(va))))
        pers_t = te["above_today"].to_numpy()[tm].astype(float)
        rows.append(dict(**common, model="persistence",
                         **metrics(yt, pers_t, 0.5, len(tr), len(va))))
        # threshold rule: value > c, c tuned on val (grid = val quantiles of value)
        vv, vt = va["value"].to_numpy()[vm], te["value"].to_numpy()[tm]
        grid = np.quantile(vv, np.linspace(0.05, 0.99, 95)) if yv.sum() > 0 else [np.median(vv)]
        c = best_f1_threshold(yv, vv, grid=grid) if yv.sum() > 0 else grid[0]
        rows.append(dict(**common, model="threshold_rule",
                         **metrics(yt, vt, c, len(tr), len(va))))


# --------------------------------------------------------------------------- #
def main():
    daily, inv = load_daily()
    rows: list[dict] = []
    for split_name, split in SPLITS.items():
        feat = build_features(daily, split["train"])
        for thr_name, q in THRESH_DEFS.items():
            for H in HORIZONS:
                run_config(feat, split_name, split, thr_name, q, H, rows)

    res = pd.DataFrame(rows)
    col_order = ["split", "thr_def", "horizon", "subset", "model", "t_star", "auc", "precision", "pod",
                 "base_rate", "lift", "n_test", "n_pos", "n_alerts", "n_train", "n_val", "thresholds"]
    res = res[col_order]
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    res.to_csv(OUT_CSV, index=False)

    pd.set_option("display.width", 220)
    pd.set_option("display.max_rows", 500)
    print("\n" + "=" * 78)
    print("RESULTS  (pooled WLIS+EXRX; t* = val max-F1 within the evaluated subset)")
    print("=" * 78)
    show = res.drop(columns=["thresholds", "n_train", "n_val"]).copy()
    for c in ("t_star", "auc", "precision", "pod", "base_rate", "lift"):
        show[c] = show[c].astype(float).round(3)
    print(show.to_string(index=False))
    print(f"\nWrote {OUT_CSV}  ({len(res)} rows)")

    # ---------------- pre-registered read ----------------
    print("\n" + "=" * 78)
    print("PRE-REGISTERED READ  (onset-only, feasible split, H=7)")
    print("=" * 78)
    key = res[(res.split.str.startswith("feasible")) & (res.subset == "onset") & (res.horizon == 7)]
    print(f"Reference: LIS boat precision {LIS_BOAT['precision']}, lift {LIS_BOAT['lift']} at base {LIS_BOAT['base']}; "
          f"Narragansett {NARR['precision']} / {NARR['lift']} at base {NARR['base']}")
    for _, r in key[key.model != "persistence"].iterrows():
        print(f"  {r.thr_def:9s} {r.model:14s} precision={r.precision:.3f} lift={r.lift:.2f} base={r.base_rate:.3f} "
              f"POD={r.pod:.2f} AUC={r.auc if not np.isnan(r.auc) else float('nan'):.3f} "
              f"n_test={r.n_test} n_pos={r.n_pos} n_alerts={r.n_alerts}")
    # Judge on the threshold definition whose onset base rate is closest to the LIS boat base rate
    # (base rates differ, so lift is the primary comparator; precision secondary).
    models = key[key.model.isin(["LR", "HistGB"])]
    if len(models) == 0:
        print("VERDICT: nothing to judge.")
        return
    closest_def = (models.groupby("thr_def")["base_rate"].first() - LIS_BOAT["base"]).abs().idxmin()
    cand = models[models.thr_def == closest_def].sort_values("lift", ascending=False).iloc[0]
    rule = key[(key.thr_def == closest_def) & (key.model == "threshold_rule")].iloc[0]
    print(f"\nJudged on thr_def={closest_def} (onset base {cand.base_rate:.3f}): best model {cand.model} "
          f"precision={cand.precision:.3f} lift={cand.lift:.2f} (n_pos={cand.n_pos}); "
          f"threshold rule precision={rule.precision:.3f} lift={rule.lift:.2f}")
    if cand.n_pos < 20:
        print("VERDICT: data too thin (test positives < 20) -- no call.")
    elif cand.lift > LIS_BOAT["lift"] and cand.precision >= 0.3:
        print("VERDICT: onset precision/lift clearly above LIS boat level and toward Narragansett -> "
              "cadence thesis HOLDS within LIS.")
    elif cand.lift <= LIS_BOAT["lift"] and cand.precision <= 0.2:
        print("VERDICT: model skill stays at LIS boat level (lift <= 2.7, precision <= 0.2) despite 15-min "
              "cadence -> bay biology / sensor limits may be binding, not cadence alone.")
    else:
        print("VERDICT: intermediate -- above boat level on one axis only; partial support.")

    # per-buoy breakdown of the judged config for transparency
    print("\nPer-buoy onset test breakdown (feasible split, H=7, thr_def=%s):" % closest_def)
    print(PER_BUOY.get(closest_def, "n/a"))


PER_BUOY: dict = {}


if __name__ == "__main__":
    main()
