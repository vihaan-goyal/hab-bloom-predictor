"""
point_of_no_return.py
---------------------
How late can a bloom still be averted?

Two independent answers, computed side by side, because they can disagree and
the disagreement is the interesting part.

1. MODEL COUNTERFACTUAL. The locked model is logistic regression on standardized
   features, so the question has a closed form rather than needing a search.
   The alert fires when

       decision(z) = w . z + b  >=  logit(t*)

   Define margin = w . z + b - logit(t*). Perturbing only the features in a
   modifiable set M, the largest achievable reduction in the decision value is

       box budget:  sum_{j in M} max( w_j (z_j - lo_j), w_j (z_j - hi_j) )
       ball budget: r * sqrt( w_M' Sigma_MM w_M )

   where lo_j/hi_j are that station-season's 5th/95th percentile for feature j
   (a physically observed extreme, not an arbitrary multiple of sigma) and
   Sigma_MM is the training covariance of the modifiable features. If
   margin > max reduction, no admissible perturbation flips the alert off: the
   row is past the model's point of no return.

2. EMPIRICAL, MODEL-FREE. For the same row, take its k nearest neighbours in
   standardized feature space -- drawn from other station-years, matched within
   +/- 30 days of year so season cannot do the work -- and measure how often those
   historical analogues went on to exceed the threshold within the horizon. When
   that fraction is at or above `--emp-threshold`, the state has historically led
   to a bloom regardless of what the subsequent forcing did.

What this is not
----------------
This is a point of no return IN THE MODEL. Logistic regression is correlational.
"No admissible perturbation flips the alert" is not "the bloom is physically
unstoppable", and the modifiable set is a modelling choice, not a fact about the
estuary -- which is why M is reported as a nested ladder rather than as one
number. All chlorophyll-derived features are excluded from M throughout: they
ARE the bloom, so perturbing them relabels the outcome instead of intervening
on it.

Lead time is coarsely quantized. The median gap between station visits is 21
days, the same as the forecast horizon, so a typical event offers three or four
chances to be evaluated across four months. Results are reported as bins.

Run from repo root:
    python src/models/point_of_no_return.py
    python src/models/point_of_no_return.py --verify
"""

import argparse
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bloom_precursor_events import (  # noqa: E402
    LOOKBACK_DAYS, build_episode_index)
from locked_pipeline import (  # noqa: E402
    BLOOM_THRESHOLD, FEATURES_ALL, HORIZON_DAYS, add_forward_label,
    fit_locked_model, load_locked_dataframe)

LABEL = "bloom_fwd"
T_STAR = 0.35            # README's frozen operating point
T_STAR_ALT = 0.30        # what the selection sweep CSVs mark as chosen
FIRST_TEST_YEAR = 2015
LAST_TEST_YEAR = 2025
PCT_LO, PCT_HI = 5, 95   # admissible move: the observed station-season extremes
MIN_PCT_ROWS = 20        # below this, fall back to network-wide percentiles
BALL_RADII = (1.0, 2.0, 3.0)
K_NEIGHBOURS = 50
EMP_THRESHOLD = 0.90
DOY_TOL = 30

OUT_SUMMARY = "data/point_of_no_return.csv"
OUT_ROWS = "data/ponr_rows.csv"

# Chlorophyll-derived state and fixed geography are never modifiable.
BLOCKS = {
    "chl_state": [
        "Chlorophyll", "chl_lag1", "chl_lag2", "chl_lag3", "chl_lag4",
        "chl_roll3_mean", "chl_roll6_mean", "chl_roll9_mean",
        "chl_roll14_mean", "chl_roll21_mean", "chl_trend",
        "chl_anomaly", "chl_climatology",
        "neighbor_chl3_mean", "neighbor_chl3_lag1",
    ],
    "geography": ["month", "latitude_x", "longitude_x"],
    "nutrients": ["nox_lag2", "dip_lag2", "dip_change", "dip_x_month"],
    "meteorology": ["max_gust_3d"],
    "physics": [
        "sea_water_temperature", "temp_lag1", "sea_water_salinity",
        "sal_lag1", "sal_lag2", "sal_lag3", "sal_lag4",
        "tidal_gt_anom", "tidal_msl_anom",
    ],
    "oxygen": [
        "oxygen_concentration_in_sea_water", "do_lag1", "percent_saturation",
    ],
}

# Nested ladder: each rung adds levers, so the point of no return can only move
# later (closer to onset). Monotonicity across these is a correctness check.
MODIFIABLE_SETS = {
    "M1 nutrients": ["nutrients"],
    "M2 +meteorology": ["nutrients", "meteorology"],
    "M3 +physics": ["nutrients", "meteorology", "physics"],
    "M4 +oxygen": ["nutrients", "meteorology", "physics", "oxygen"],
}


def logit(p):
    return float(np.log(p / (1.0 - p)))


def season_of(month):
    return "winter" if month in (1, 2, 3, 4) else (
        "summer" if month in (6, 7, 8, 9) else "other")


def station_season_bounds(z, stations, seasons, features, lo=PCT_LO, hi=PCT_HI,
                          min_rows=MIN_PCT_ROWS):
    """Admissible move limits per (station, season), in standardized units.

    Computed on TRAINING rows only. A station-season with too few rows inherits
    the network-wide percentiles for that season, so a thin station degrades to a
    weaker claim rather than to a nonsensical one.
    """
    n_feat = z.shape[1]
    net = {}
    for season in np.unique(seasons):
        sel = seasons == season
        net[season] = ((np.nanpercentile(z[sel], lo, axis=0),
                        np.nanpercentile(z[sel], hi, axis=0)) if sel.sum()
                       else (np.full(n_feat, -2.0), np.full(n_feat, 2.0)))

    bounds = {}
    keys = pd.Series(list(zip(stations, seasons)))
    for key, idx in keys.groupby(keys).groups.items():
        rows = np.asarray(idx)
        if len(rows) >= min_rows:
            bounds[key] = (np.nanpercentile(z[rows], lo, axis=0),
                           np.nanpercentile(z[rows], hi, axis=0))
        else:
            bounds[key] = net[key[1]]
    return bounds, net


def box_reduction(z_rows, w, bounds, net, stations, seasons, mod_idx):
    """Largest decrease in the decision value from moving only `mod_idx`
    features to their admissible station-season extremes.

    Exact for a linear model: each feature independently contributes its best
    endpoint, so the sum of per-feature bests is the constrained optimum.
    """
    out = np.zeros(len(z_rows))
    if not len(mod_idx):
        return out
    for i in range(len(z_rows)):
        pair = bounds.get((stations[i], seasons[i])) or net.get(seasons[i])
        if pair is None:
            continue
        lo, hi = pair
        zj = z_rows[i, mod_idx]
        wj = w[mod_idx]
        gain = np.maximum(wj * (zj - lo[mod_idx]), wj * (zj - hi[mod_idx]))
        out[i] = np.maximum(gain, 0.0).sum()
    return out


def ball_reduction(w, cov, mod_idx, radius):
    """Largest decrease over a Mahalanobis ball of the modifiable features.

    Respects the correlation structure, so it never credits a jointly impossible
    combination the way the independent box budget can.
    """
    if not len(mod_idx):
        return 0.0
    wm = w[mod_idx]
    quad = float(wm @ cov[np.ix_(mod_idx, mod_idx)] @ wm)
    return radius * np.sqrt(max(quad, 0.0))


def empirical_risk(z_query, doy_query, key_query, z_pool, doy_pool, key_pool,
                   y_pool, k=K_NEIGHBOURS, doy_tol=DOY_TOL):
    """Fraction of matched historical analogues that went on to bloom.

    Neighbours are restricted to other station-years and to a +/- doy_tol day-of-
    year window, so neither the event's own history nor the season can supply the
    answer.
    """
    out = np.full(len(z_query), np.nan)
    n_used = np.zeros(len(z_query), dtype=int)
    finite_y = np.isfinite(y_pool)
    for i in range(len(z_query)):
        dd = np.abs(doy_pool - doy_query[i])
        dd = np.minimum(dd, 366 - dd)
        ok = (dd <= doy_tol) & (key_pool != key_query[i]) & finite_y
        if ok.sum() < k:
            continue
        d = np.linalg.norm(z_pool[ok] - z_query[i], axis=1)
        take = np.argpartition(d, k - 1)[:k]
        out[i] = float(np.mean(y_pool[ok][take]))
        n_used[i] = k
    return out, n_used


def build_rows(t_star=T_STAR, first_year=FIRST_TEST_YEAR,
               last_year=LAST_TEST_YEAR, lookback=LOOKBACK_DAYS,
               emp_threshold=EMP_THRESHOLD, verbose=True):
    """Score every pre-onset observation for model and empirical irreversibility."""
    df = load_locked_dataframe(verbose=verbose)
    df = add_forward_label(df, horizon=HORIZON_DAYS, threshold=BLOOM_THRESHOLD,
                           col=LABEL)
    episodes = build_episode_index(df, lookback=lookback)
    clean = episodes[episodes["clean_onset"]
                     & episodes["regime"].isin(["winter", "summer"])]

    features = [f for f in FEATURES_ALL if f in df.columns]
    mod_index = {name: np.array(
        [features.index(f) for blk in blocks for f in BLOCKS[blk]
         if f in features], dtype=int)
        for name, blocks in MODIFIABLE_SETS.items()}
    if verbose:
        for name, idx in mod_index.items():
            print(f"  {name:<18} {len(idx):>2} modifiable of {len(features)}")

    df["season"] = df["date"].dt.month.map(season_of)
    df["doy"] = df["date"].dt.dayofyear
    df["sy"] = (df["station_name"].astype(str) + "_"
                + df["date"].dt.year.astype(str))

    # map each observation to the onset it precedes, if any
    onset_of, lead_of, regime_of = {}, {}, {}
    for _, ev in clean.iterrows():
        station, onset = str(ev["station_name"]), ev["onset"]
        win = df[(df["station_name"].astype(str) == station)
                 & (df["date"] < onset)
                 & (df["date"] >= onset - pd.Timedelta(days=lookback))]
        for i, d in zip(win.index, win["date"]):
            lead = int((onset - d).days)
            # if a row precedes two onsets, attribute it to the nearer one
            if i not in lead_of or lead < lead_of[i]:
                lead_of[i] = lead
                onset_of[i] = f"{station}_{onset.date()}"
                regime_of[i] = ev["regime"]

    records = []
    for T in range(first_year, last_year + 1):
        tr_end = pd.Timestamp(f"{T - 2}-12-31")
        tr = df[(df["date"] <= tr_end) & df[LABEL].notna()]
        te = df[(df["date"].dt.year == T) & df[LABEL].notna()]
        if len(tr) < 200 or te.empty:
            continue

        bundle = fit_locked_model(df, LABEL, train_end=tr_end, features=features)
        w = bundle["model"].coef_[0]
        b = float(bundle["model"].intercept_[0])
        med, scaler = bundle["medians"], bundle["scaler"]

        z_tr = scaler.transform(tr[features].fillna(med))
        z_te = scaler.transform(te[features].fillna(med))
        cov = np.cov(z_tr, rowvar=False)

        bounds, net = station_season_bounds(
            z_tr, tr["station_name"].astype(str).to_numpy(),
            tr["season"].to_numpy(), features)

        decision = z_te @ w + b
        margin = decision - logit(t_star)

        # only rows that actually precede an onset carry a lead time
        te_idx = te.index.to_numpy()
        is_pre = np.array([i in lead_of for i in te_idx])
        if not is_pre.any():
            continue

        st_te = te["station_name"].astype(str).to_numpy()
        se_te = te["season"].to_numpy()
        reductions = {}
        for name, idx in mod_index.items():
            reductions[(name, "box")] = box_reduction(
                z_te, w, bounds, net, st_te, se_te, idx)
            for r in BALL_RADII:
                reductions[(name, f"ball_r{r:g}")] = np.full(
                    len(z_te), ball_reduction(w, cov, idx, r))

        # empirical analogues: the pool is every labelled row up to the fold's
        # training cutoff, so nothing after the fold leaks in
        emp, n_emp = empirical_risk(
            z_te[is_pre], te["doy"].to_numpy()[is_pre],
            te["sy"].to_numpy()[is_pre],
            z_tr, tr["doy"].to_numpy(), tr["sy"].to_numpy(),
            tr[LABEL].to_numpy(dtype=float))

        pre_positions = np.flatnonzero(is_pre)
        for j, pos in enumerate(pre_positions):
            i = te_idx[pos]
            rec = {
                "fold": T, "row": int(i), "event": onset_of[i],
                "regime": regime_of[i], "lead_days": lead_of[i],
                "station_name": st_te[pos], "date": te["date"].iloc[pos],
                "decision": float(decision[pos]), "margin": float(margin[pos]),
                "alert": bool(decision[pos] >= logit(t_star)),
                "emp_risk": float(emp[j]) if np.isfinite(emp[j]) else np.nan,
                "emp_n": int(n_emp[j]),
            }
            for key, arr in reductions.items():
                rec[f"red_{key[0]}_{key[1]}"] = float(arr[pos])
                rec[f"irr_{key[0]}_{key[1]}"] = bool(margin[pos] > arr[pos])
            rec["irr_empirical"] = (bool(emp[j] >= emp_threshold)
                                    if np.isfinite(emp[j]) else None)
            records.append(rec)

        if verbose:
            print(f"  fold {T}: {len(tr):>5} train, {int(is_pre.sum()):>4} "
                  f"pre-onset rows, {int(np.isfinite(emp).sum()):>4} with analogues")

    return pd.DataFrame(records), list(mod_index)


def _first_run_lead(group, flags):
    """Largest lead over which irreversibility holds continuously from onset."""
    run = 0
    while run < len(flags) and flags[run]:
        run += 1
    return int(group["lead_days"].to_numpy()[run - 1]) if run else None


def summarize(rows, set_names, emp_threshold=EMP_THRESHOLD, t_star=T_STAR):
    """Per regime and modifiable set, the lead at which irreversibility sets in.

    An event's point of no return is the largest lead at which the alert is
    irreversible AND stays irreversible through every later observation. Events
    that are never irreversible are counted, not silently dropped.
    """
    out = []
    budgets = ["box"] + [f"ball_r{r:g}" for r in BALL_RADII]
    for regime in ("winter", "summer"):
        sub = rows[rows["regime"] == regime]
        if sub.empty:
            continue
        for name in set_names:
            for budget in budgets:
                col = f"irr_{name}_{budget}"
                leads, n_ev = [], 0
                for _, g in sub.groupby("event"):
                    g = g.sort_values("lead_days")   # nearest onset first
                    n_ev += 1
                    lead = _first_run_lead(g, g[col].to_numpy(dtype=bool))
                    if lead is not None:
                        leads.append(lead)
                leads = np.array(leads)
                out.append({
                    "regime": regime, "modifiable_set": name, "budget": budget,
                    "t_star": t_star, "n_events": n_ev,
                    "n_events_with_ponr": len(leads),
                    "frac_events_with_ponr": len(leads) / n_ev if n_ev else np.nan,
                    "ponr_lead_median": float(np.median(leads)) if len(leads) else np.nan,
                    "ponr_lead_p25": float(np.percentile(leads, 25)) if len(leads) else np.nan,
                    "ponr_lead_p75": float(np.percentile(leads, 75)) if len(leads) else np.nan,
                    "frac_rows_irreversible": float(sub[col].mean()),
                })
        # the model-free comparison, computed once per regime
        emp = sub.dropna(subset=["emp_risk"])
        leads, n_ev = [], 0
        for _, g in emp.groupby("event"):
            g = g.sort_values("lead_days")
            n_ev += 1
            lead = _first_run_lead(
                g, (g["emp_risk"].to_numpy() >= emp_threshold))
            if lead is not None:
                leads.append(lead)
        leads = np.array(leads)
        out.append({
            "regime": regime, "modifiable_set": "EMPIRICAL", "budget": "knn",
            "t_star": np.nan, "n_events": n_ev, "n_events_with_ponr": len(leads),
            "frac_events_with_ponr": len(leads) / n_ev if n_ev else np.nan,
            "ponr_lead_median": float(np.median(leads)) if len(leads) else np.nan,
            "ponr_lead_p25": float(np.percentile(leads, 25)) if len(leads) else np.nan,
            "ponr_lead_p75": float(np.percentile(leads, 75)) if len(leads) else np.nan,
            "frac_rows_irreversible": float(
                (emp["emp_risk"] >= emp_threshold).mean()) if len(emp) else np.nan,
        })
    return pd.DataFrame(out)


def cross_check(rows, set_names):
    """Where do the model and the analogues agree that a bloom is locked in?"""
    emp = rows.dropna(subset=["emp_risk"]).copy()
    if emp.empty:
        return pd.DataFrame()
    emp["emp_irr"] = emp["emp_risk"] >= EMP_THRESHOLD
    out = []
    for name in set_names:
        col = f"irr_{name}_box"
        both = int((emp[col] & emp["emp_irr"]).sum())
        model_only = int((emp[col] & ~emp["emp_irr"]).sum())
        emp_only = int((~emp[col] & emp["emp_irr"]).sum())
        neither = int((~emp[col] & ~emp["emp_irr"]).sum())
        n = len(emp)
        out.append({"modifiable_set": name, "n_rows": n,
                    "both_irreversible": both, "model_only": model_only,
                    "empirical_only": emp_only, "neither": neither,
                    "agreement": (both + neither) / n})
    return pd.DataFrame(out)


def check_nesting(rows, set_names):
    """Adding levers can only make a row easier to flip, never harder.

    The invariant is per row -- irreversible under M4 implies irreversible under
    M3, and so on down. Comparing median lead times across rungs would NOT test
    this, because each rung's median is taken over a different subset of events
    (only those that reach irreversibility at all), so the medians can move in
    either direction without anything being wrong.
    """
    print("\nNesting check (irreversible under a larger M implies smaller M):")
    ok_all = True
    for a, b in zip(set_names, set_names[1:]):
        viol = int((rows[f"irr_{b}_box"] & ~rows[f"irr_{a}_box"]).sum())
        ok_all &= viol == 0
        print(f"  {b} implies {a}: {'OK' if viol == 0 else f'{viol} VIOLATIONS'}")
    assert ok_all, "irreversibility is not nested in the modifiable set"


def describe_empirical(rows):
    """What the analogue-based risk actually reaches, since it never hits 0.90.

    Reporting only 'no event passed the threshold' would hide whether the
    analogues came close or were nowhere near it.
    """
    emp = rows["emp_risk"].dropna()
    if emp.empty:
        print("\nEmpirical analogues: none computed")
        return
    qs = [50, 75, 90, 95, 99, 100]
    vals = np.percentile(emp, qs)
    print(f"\nEmpirical analogue risk over {len(emp)} pre-onset rows "
          f"(fraction of {K_NEIGHBOURS} matched neighbours that bloomed):")
    print("  " + "  ".join(f"p{q}={v:.2f}" for q, v in zip(qs, vals)))
    for t in (0.5, 0.6, 0.7, 0.8, 0.9):
        print(f"  rows with analogue risk >= {t:.1f}: "
              f"{int((emp >= t).sum()):>4} ({100 * (emp >= t).mean():.1f} %)")


def verify_box_budget(n=10, seed=0):
    """The box optimum should equal a general LP solved over the same bounds."""
    from scipy.optimize import linprog
    rng = np.random.default_rng(seed)
    print("\nVerification: analytic box budget vs scipy linprog")
    worst = 0.0
    for _ in range(n):
        k = int(rng.integers(3, 12))
        w = rng.normal(size=k)
        z = rng.normal(size=k)
        lo = z - rng.uniform(0.2, 2.5, size=k)
        hi = z + rng.uniform(0.2, 2.5, size=k)
        analytic = np.maximum(np.maximum(w * (z - lo), w * (z - hi)), 0.0).sum()
        res = linprog(c=w, bounds=list(zip(lo - z, hi - z)), method="highs")
        worst = max(worst, abs(analytic - (-float(res.fun))))
    print(f"  max |analytic - LP| over {n} instances: {worst:.3e}")
    assert worst < 1e-6, "analytic box budget disagrees with the LP optimum"
    print("  PASS")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--t-star", type=float, default=T_STAR,
                    help="alert threshold (README freezes 0.35; the selection "
                         "sweep CSVs mark 0.30)")
    ap.add_argument("--also-t-star", type=float, default=T_STAR_ALT,
                    help="second threshold reported for sensitivity")
    ap.add_argument("--emp-threshold", type=float, default=EMP_THRESHOLD)
    ap.add_argument("--summary-out", default=OUT_SUMMARY)
    ap.add_argument("--rows-out", default=OUT_ROWS)
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()

    if args.verify:
        verify_box_budget()

    frames, summaries = [], []
    for t in [args.t_star, args.also_t_star]:
        print(f"\n{'=' * 72}\nt* = {t}\n{'=' * 72}")
        rows, set_names = build_rows(t_star=t, emp_threshold=args.emp_threshold)
        if rows.empty:
            print("  no pre-onset rows scored")
            continue
        rows["t_star"] = t
        frames.append(rows)
        s = summarize(rows, set_names, args.emp_threshold, t)
        summaries.append(s)

        print(f"\n{len(rows)} pre-onset observations across "
              f"{rows['event'].nunique()} events")
        show = ["regime", "modifiable_set", "budget", "n_events",
                "frac_events_with_ponr", "ponr_lead_median", "ponr_lead_p25",
                "ponr_lead_p75", "frac_rows_irreversible"]
        print(s[s["budget"].isin(["box", "knn"])][show]
              .to_string(index=False, float_format=lambda v: f"{v:7.3f}"))

        cc = cross_check(rows, set_names)
        if not cc.empty:
            print("\nModel vs analogues (box budget):")
            print(cc.to_string(index=False, float_format=lambda v: f"{v:7.3f}"))

        check_nesting(rows, set_names)
        describe_empirical(rows)

    if summaries:
        pd.concat(summaries).to_csv(args.summary_out, index=False)
        pd.concat(frames).to_csv(args.rows_out, index=False)
        print(f"\n-> {args.summary_out}\n-> {args.rows_out}")


if __name__ == "__main__":
    main()
