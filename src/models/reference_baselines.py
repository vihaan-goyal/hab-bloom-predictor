"""
reference_baselines.py
----------------------
What does the alert beat?

Every skill number in this repo so far compares the locked model against another
MODEL (ablations, bakeoffs, challengers). Nothing compares it against a forecast
that requires no model at all. That is the first question anyone asks, and until
it is answered "POD 0.875" and "POD 1.00" cannot be interpreted.

Four reference forecasters, scored identically to the real alert:

  always      alert every decision unit. POD is 1.0 by construction and its FAR
              is exactly 1 - base_rate, so it is the floor any product must clear.
  climatology alert when the historical bloom rate for this station and month
              (computed on TRAIN years only) exceeds a threshold chosen on val.
              This is "just use the season", the forecast a domain expert makes
              for free.
  doyclim     same idea at finer resolution: day-of-year bins rather than months,
              reusing the 24-bin scheme from bloom_precursor_events.doy_bin.
  persistence alert if this station's most recent previous reading exceeded the
              bloom threshold. The cheapest forecast that uses data.

The headline metric is LIFT = precision / base_rate, because it is the only one
of POD/FAR/CSI that is defined relative to a reference rather than rewarding a
convenient base rate. Note the ceiling: lift can never exceed 1 / base_rate, so
on a set where half the units are events the best achievable lift is 2.0. That
bound is reported alongside every row, because a lift of 1.3 means something very
different at a 5 % base rate than at a 40 % one.

Differences are tested with a paired station-year clustered bootstrap, matching
the convention in bootstrap_ci.py (cluster="station_year", n_boot=2000, seed=42)
and the paired-lift-difference template in
src/models/experiments/label_refinement.py.

Run from repo root:
    python src/models/reference_baselines.py
"""

import argparse
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bloom_precursor_events import doy_bin  # noqa: E402
from locked_pipeline import (  # noqa: E402
    BLOOM_THRESHOLD, HORIZON_DAYS, add_forward_label, fit_locked_model,
    load_locked_dataframe, predict_proba)

TRAIN_END = pd.Timestamp("2019-12-31")
VAL_START, VAL_END = pd.Timestamp("2020-01-01"), pd.Timestamp("2022-12-31")
TEST_START = pd.Timestamp("2023-01-01")
LABEL = "bloom_fwd"
T_STAR = 0.35            # frozen station-day operating point (README)
WEST_LON = -73.4         # matches basin_alert.py default
GRID = np.round(np.arange(0.0, 1.001, 0.05), 3)
N_BOOT = 2000
SEED = 42
OUT_CSV = "data/reference_baselines.csv"


def contingency(y, a):
    """POD/FAR/CSI/precision. Same definitions as basin_alert.contingency."""
    y = np.asarray(y).astype(int)
    a = np.asarray(a).astype(bool)
    tp = int(((y == 1) & a).sum())
    fp = int(((y == 0) & a).sum())
    fn = int(((y == 1) & ~a).sum())
    pod = tp / (tp + fn) if (tp + fn) else np.nan
    far = fp / (tp + fp) if (tp + fp) else np.nan
    csi = tp / (tp + fp + fn) if (tp + fp + fn) else np.nan
    prec = (1 - far) if np.isfinite(far) else np.nan
    base = y.mean() if len(y) else np.nan
    return {"tp": tp, "fp": fp, "fn": fn, "pod": pod, "far": far, "csi": csi,
            "precision": prec, "base_rate": base,
            "lift": prec / base if (np.isfinite(prec) and base) else np.nan,
            "max_lift": 1 / base if base else np.nan,
            "alert_rate": float(a.mean()) if len(a) else np.nan}


def build_station_day(verbose=True):
    """Locked frame with the forward label, out-of-sample model probabilities,
    and every baseline's alert decision. Probabilities are walk-forward: the
    model scoring val+test is fit on train only, exactly as basin_alert does."""
    df = load_locked_dataframe(verbose=verbose)
    df = df.sort_values(["station_name", "date"]).reset_index(drop=True)
    df = add_forward_label(df, horizon=HORIZON_DAYS, threshold=BLOOM_THRESHOLD,
                           col=LABEL)

    bundle = fit_locked_model(df, label_col=LABEL, train_end=TRAIN_END)
    df["bloom_prob"] = predict_proba(bundle, df)

    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["doy_bin"] = doy_bin(df["date"])
    df["station_name"] = df["station_name"].astype(str)

    # --- climatology rates, TRAIN ROWS ONLY (no leakage into val/test) ------
    tr = df[(df["date"] <= TRAIN_END) & df[LABEL].notna()]
    global_rate = float(tr[LABEL].mean())

    for name, keys in [("clim_rate", ["station_name", "month"]),
                       ("doyclim_rate", ["station_name", "doy_bin"])]:
        rate = tr.groupby(keys)[LABEL].mean().rename(name).reset_index()
        df = df.merge(rate, on=keys, how="left")
        df[name] = df[name].fillna(global_rate)

    # --- persistence: did this station's PREVIOUS reading exceed? ----------
    df["persist"] = (df.groupby("station_name")["Chlorophyll"]
                       .shift(1) > BLOOM_THRESHOLD)
    df["persist"] = df["persist"].fillna(False)
    return df


def basin_frame(df):
    """Collapse western stations to one decision unit per sampled date.

    Mirrors basin_alert.basin_series (max aggregator, OR label, right-censored
    windows -> NaN) but additionally carries each baseline aggregated the same
    way, so the basin comparison is like-for-like.
    """
    w = df[df["longitude_x"] < WEST_LON].copy()
    days = (w.groupby("date")
             .agg(bloom_prob=("bloom_prob", "max"),
                  clim_rate=("clim_rate", "max"),
                  doyclim_rate=("doyclim_rate", "max"),
                  persist=("persist", "max"),
                  n_stations=("station_name", "nunique"))
             .reset_index().sort_values("date"))

    vis = w["date"].sort_values().unique()
    exc = w.loc[w["Chlorophyll"] > BLOOM_THRESHOLD, "date"].sort_values().unique()
    last = w["date"].max()
    lab = []
    for d in days["date"]:
        end = d + pd.Timedelta(days=HORIZON_DAYS)
        if ((exc > d) & (exc <= end)).any():
            lab.append(1.0)
        elif end <= last:
            lab.append(0.0)
        else:
            lab.append(np.nan)
    days[LABEL] = lab
    days["year"] = days["date"].dt.year
    # one cluster per year at basin level (no station dimension left)
    days["station_name"] = "BASIN"
    return days


def pick_threshold(val, col, floor=0.8):
    """Pre-registered rule, same as t*: highest threshold whose val POD >= floor.
    Returns NaN if no threshold reaches the floor."""
    best = np.nan
    for t in GRID:
        m = contingency(val[LABEL], val[col].to_numpy(dtype=float) >= t)
        if np.isfinite(m["pod"]) and m["pod"] >= floor:
            best = t
    return best


def forecasts(val, test, level):
    """Return (name, boolean alert array) for the model and each baseline.
    Thresholds for the continuous baselines are chosen on VAL only."""
    out = []

    t_model = T_STAR if level == "station-day" else pick_threshold(val, "bloom_prob")
    out.append((f"MODEL (locked LR, t={t_model:g})",
                test["bloom_prob"].to_numpy(dtype=float) >= t_model))

    out.append(("always alert", np.ones(len(test), dtype=bool)))

    for label, col in [("climatology (station x month)", "clim_rate"),
                       ("climatology (station x doy bin)", "doyclim_rate")]:
        t = pick_threshold(val, col)
        if np.isfinite(t):
            out.append((f"{label}, t={t:g}",
                        test[col].to_numpy(dtype=float) >= t))
        else:
            out.append((f"{label} (no threshold reached POD>=0.8)",
                        np.zeros(len(test), dtype=bool)))

    out.append(("persistence (last reading > 10)",
                test["persist"].to_numpy(dtype=bool)))
    return out


def paired_lift_bootstrap(test, a_model, a_ref, n_boot=N_BOOT, seed=SEED):
    """Station-year clustered bootstrap of lift(model) - lift(reference).

    Resamples whole clusters with replacement, same count as observed, and
    recomputes BOTH forecasters on the identical resample so the difference is
    paired. Matches bootstrap_ci.bootstrap conventions.
    """
    key = (test["station_name"].astype(str) + "_"
           + test["year"].astype(str)).to_numpy()
    pos = pd.Series(np.arange(len(test)))
    groups = [np.asarray(v) for v in pos.groupby(key).indices.values()]
    y = test[LABEL].to_numpy()
    rng = np.random.default_rng(seed)
    diffs = []
    for _ in range(n_boot):
        pick = rng.integers(0, len(groups), len(groups))
        idx = np.concatenate([groups[p] for p in pick])
        if len(np.unique(y[idx])) < 2:
            continue
        lm = contingency(y[idx], a_model[idx])["lift"]
        lr = contingency(y[idx], a_ref[idx])["lift"]
        if np.isfinite(lm) and np.isfinite(lr):
            diffs.append(lm - lr)
    if not diffs:
        return np.nan, np.nan, np.nan
    d = np.array(diffs)
    lo, hi = np.percentile(d, [2.5, 97.5])
    return float(d.mean()), float(lo), float(hi)


def evaluate(level, val, test, n_boot=N_BOOT, verbose=True):
    rows = []
    fc = forecasts(val, test, level)
    model_name, a_model = fc[0]
    for name, a in fc:
        m = contingency(test[LABEL], a)
        row = {"level": level, "forecaster": name, "n": len(test),
               "events": int(np.asarray(test[LABEL]).sum()), **m}
        if name != model_name:
            d, lo, hi = paired_lift_bootstrap(test, a_model, a, n_boot=n_boot)
            row.update({"lift_diff_vs_model": d, "ci_lo": lo, "ci_hi": hi,
                        "model_clearly_better": bool(np.isfinite(lo) and lo > 0)})
        rows.append(row)

    if verbose:
        base = float(np.asarray(test[LABEL]).mean())
        print(f"\n{'=' * 96}\n{level.upper()}  "
              f"(n={len(test)}, events={int(np.asarray(test[LABEL]).sum())}, "
              f"base rate={base:.3f}, max possible lift={1 / base:.2f}x)\n"
              f"{'=' * 96}")
        hdr = (f"{'forecaster':<44}{'POD':>6}{'FAR':>7}{'CSI':>7}"
               f"{'prec':>7}{'lift':>7}   model minus ref, lift [95% CI]")
        print(hdr + "\n" + "-" * len(hdr))
        for r in rows:
            tail = ""
            if np.isfinite(r.get("lift_diff_vs_model", np.nan)):
                flag = "  <-- model clearly better" if r.get(
                    "model_clearly_better") else "  (CI includes 0)"
                tail = (f"   {r['lift_diff_vs_model']:+.3f} "
                        f"[{r['ci_lo']:+.3f}, {r['ci_hi']:+.3f}]{flag}")
            print(f"{r['forecaster']:<44}{r['pod']:>6.3f}{r['far']:>7.3f}"
                  f"{r['csi']:>7.3f}{r['precision']:>7.3f}{r['lift']:>7.2f}{tail}")
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=OUT_CSV)
    ap.add_argument("--n-boot", type=int, default=N_BOOT)
    args = ap.parse_args()

    df = build_station_day()
    rows = []

    sd = df.dropna(subset=[LABEL])
    rows += evaluate("station-day",
                     sd[(sd["date"] >= VAL_START) & (sd["date"] <= VAL_END)],
                     sd[sd["date"] >= TEST_START], n_boot=args.n_boot)

    bd = basin_frame(df).dropna(subset=[LABEL])
    rows += evaluate("basin-day",
                     bd[(bd["date"] >= VAL_START) & (bd["date"] <= VAL_END)],
                     bd[bd["date"] >= TEST_START], n_boot=args.n_boot)

    out = pd.DataFrame(rows)
    out.to_csv(args.out, index=False)
    print(f"\n-> {args.out}")

    # The check that matters: always-alert must be exactly POD 1 and
    # FAR = 1 - base_rate. If not, the scoring is wrong, not the baseline.
    print()
    for lvl in out["level"].unique():
        a = out[(out["level"] == lvl)
                & (out["forecaster"] == "always alert")].iloc[0]
        ok = (abs(a["pod"] - 1.0) < 1e-9
              and abs(a["far"] - (1 - a["base_rate"])) < 1e-9)
        print(f"  sanity [{lvl}]: always-alert POD=1 and FAR=1-base_rate "
              f"-> {'PASS' if ok else 'FAIL'}")


if __name__ == "__main__":
    main()
