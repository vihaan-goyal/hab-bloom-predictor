"""
decision_value.py
-----------------
The forecast's value in the unit a monitoring manager actually budgets in:
STATION-VISITS PER CONFIRMED BLOOM under a fixed monthly sampling budget.

Every skill number so far (precision, lift, POD) is a property of the alert.
A manager does not buy alerts; they buy visits. This script asks: if I can
afford V station-visits a month, how many blooms do I confirm, and how many
visits does each confirmed bloom cost me, depending on how I choose where to
send the sampler?

Units. A "visit" is one station-day drawn from the out-of-sample universe:
  LIS          one station sampled on one CT DEEP cruise day (test 2023-2025).
  Narragansett one station-day of the RIDEM sonde record, ONSET rows only
               (today's chl <= 10 ug/L), pooled out-of-fold 2015-2023.
A visit "confirms a bloom" if that station-day's label is 1, i.e. an
exceedance (> 10 ug/L) follows within the horizon (LIS 21 d, Narragansett 7 d).
Read it as: the sampler was sent to a place and time that a bloom followed.

Strategies (per bay, per calendar month in the test period, per budget V):
  calendar_fixed   V visits spread evenly over the month's sampled dates,
                   stations in a fixed rotation (deterministic).
  random_uniform   V station-days drawn uniformly; averaged over 200 seeds.
                   This is ALSO the always-alert / base-rate strategy: with no
                   ranking information every station-day is equally likely,
                   so its visits-per-bloom is 1 / base rate. Reported once.
  climatology      rank station-days by the station x month bloom rate
                   computed on TRAINING years only; take the top V.
  alert_greedy     rank the month's station-days by out-of-sample bloom_prob
                   and take the top V (non-causal within the month: the
                   ranking uses the whole month's scores at once).
  alert_causal     spend the budget as days arrive: each day, visit that
                   day's station-days with bloom_prob >= t* (shipped t*:
                   LIS 0.35, Narragansett 0.50) in descending order until the
                   month's budget is gone. Unspent budget stays unspent, so
                   the `visits` column is what was actually used.
If a month has fewer station-days than V, every strategy visits them all.

Aggregation: totals over months. Visits-per-bloom = sum(visits) /
sum(blooms confirmed); share caught = sum(confirmed) / sum(month blooms).
95 % CI: bootstrap over months (n=2000, seed=42).

Sanity check printed at the end: at the FULL budget (every station-day
visited, alert_causal with V = infinity) the alert-directed precision must
equal the published lift x base rate: LIS lift ~2.6-2.7 at t*=0.35,
precision ~0.13 (data/reference_baselines.csv); Narragansett onset lift 2.00,
precision 0.696 at 2023 (fork data/narragansett_model_results.csv, GB tier A
single split). Both are reproduced as a by-product and printed side by side.

Inputs.
  LIS: the locked walk-forward frame from reference_baselines.build_station_day
       (locked LR fit on <= 2019, scoring 2020-2025; columns station_name,
       date, bloom_fwd, bloom_prob, clim_rate). No CSV of these rows existed;
       they are re-derived here (~20 s) and cached to data/decision_value_rows.csv.
  Narragansett: rolling_origin_cv_nar.py writes only fold summaries, so its
       9-fold loop (train <= T-2, test == T, GB tier A, T in 2015..2023) is
       re-run here verbatim to obtain per-row out-of-fold probabilities.

Outputs: data/decision_value.csv, figures/fig_decision_value.png.

Run from the LIS repo root with the BASE anaconda python:
    python src/models/decision_value.py [--nar-root ../hab-bloom-predictor-narragansett]
"""

import argparse
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.ensemble import HistGradientBoostingClassifier  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reference_baselines import build_station_day, TEST_START, TRAIN_END  # noqa: E402
from reference_baselines import T_STAR as T_STAR_LIS  # noqa: E402

BUDGETS = (4, 8, 12)
N_RANDOM_SEEDS = 200
N_BOOT = 2000
SEED = 42
T_STAR_NAR = 0.50
BLOOM_NAR = 10.0
NAR_TEST_YEARS = range(2015, 2024)
NAR_MIN_VAL_POS = 5
# Tier-A feature list, copied verbatim from the fork's train_narragansett.py
NAR_TIER_A = ['chl', 'chl_lag1', 'chl_lag2', 'chl_lag3', 'chl_lag4',
              'chl_roll3_mean', 'chl_roll6_mean', 'chl_roll9_mean',
              'chl_roll14_mean', 'chl_roll21_mean', 'chl_trend',
              'chl_anomaly', 'chl_climatology',
              'do', 'do_lag1', 'temp', 'temp_lag1',
              'sal', 'sal_lag1', 'sal_lag2', 'sal_lag3', 'sal_lag4', 'month']
STRATEGIES = ["calendar_fixed", "random_uniform", "climatology",
              "alert_greedy", "alert_causal"]
STRATEGY_LABEL = {"calendar_fixed": "Calendar (fixed rotation)",
                  "random_uniform": "Random / always-alert",
                  "climatology": "Climatology",
                  "alert_greedy": "Alert-directed (top-V per month)",
                  "alert_causal": "Alert-directed (causal, t*)"}
# Fixed categorical order (dataviz palette slots 1,2,3,4,7)
STRATEGY_COLOR = {"calendar_fixed": "#2a78d6", "random_uniform": "#eb6834",
                  "climatology": "#1baf7a", "alert_greedy": "#eda100",
                  "alert_causal": "#4a3aa7"}
OUT_CSV = "data/decision_value.csv"
OUT_ROWS = "data/decision_value_rows.csv"
OUT_FIG = "figures/fig_decision_value.png"


# --------------------------------------------------------------------------
# Universes: one row per out-of-sample station-day
# --------------------------------------------------------------------------
def lis_universe(verbose=True):
    """Locked LIS frame, test rows 2023-2025 with a finished label."""
    df = build_station_day(verbose=False)
    t = df[(df["date"] >= TEST_START) & df["bloom_fwd"].notna()].copy()
    out = pd.DataFrame({"bay": "LIS", "station": t["station_name"].astype(str),
                        "date": t["date"], "y": t["bloom_fwd"].astype(int),
                        "prob": t["bloom_prob"].astype(float),
                        "clim_rate": t["clim_rate"].astype(float)})
    if verbose:
        print(f"LIS universe: {len(out)} station-days, {out.y.sum()} blooms, "
              f"{out.station.nunique()} stations, {out.date.min().date()} .. "
              f"{out.date.max().date()}; climatology from train <= "
              f"{TRAIN_END.year}")
    return out.sort_values(["date", "station"]).reset_index(drop=True)


def _fit_gb(Xtr, ytr):
    m = HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05,
                                       max_iter=300, min_samples_leaf=50,
                                       l2_regularization=1.0, random_state=42,
                                       class_weight="balanced").fit(Xtr, ytr)
    return m


def nar_universe(nar_root, verbose=True):
    """Pooled out-of-fold GB tier-A probabilities, onset rows (chl <= 10),
    reproducing the fold loop of the fork's rolling_origin_cv_nar.py.
    Climatology rate per fold from that fold's training years only.
    Also returns the single-split (train <= 2020, test 2023) onset precision
    at t*=0.50 to reproduce the published number."""
    path = os.path.join(nar_root, "data", "narragansett_daily_features.csv")
    df = pd.read_csv(path, parse_dates=["date"])
    df["year"] = df.date.dt.year
    lab = df.dropna(subset=["bloom_fwd"]).copy()
    lab["bloom_fwd"] = lab.bloom_fwd.astype(int)
    lab["onset"] = lab.chl <= BLOOM_NAR
    lab["month"] = lab.date.dt.month

    parts = []
    for T in NAR_TEST_YEARS:
        train = lab[lab.year <= T - 2]
        val = lab[lab.year == T - 1]
        test = lab[lab.year == T]
        if (len(train) == 0 or test.bloom_fwd.sum() == 0
                or val.bloom_fwd.sum() < NAR_MIN_VAL_POS):
            print(f"  skip T={T}")
            continue
        med = train[NAR_TIER_A].median(numeric_only=True)
        prep = lambda d: d[NAR_TIER_A].fillna(med).values  # noqa: E731
        model = _fit_gb(prep(train), train.bloom_fwd.values)
        pt = model.predict_proba(prep(test))[:, 1]
        rate = (train.groupby(["station", "month"])["bloom_fwd"].mean()
                .rename("clim_rate").reset_index())
        te = test[["station", "date", "bloom_fwd", "onset", "month"]].copy()
        te["prob"] = pt
        te = te.merge(rate, on=["station", "month"], how="left")
        te["clim_rate"] = te["clim_rate"].fillna(float(train.bloom_fwd.mean()))
        te = te[te.onset]
        parts.append(te)
        if verbose:
            a = te.prob >= T_STAR_NAR
            print(f"  fold T={T}: train<= {T-2}, onset n={len(te)}, "
                  f"pos={int(te.bloom_fwd.sum())}, prec@0.50={te.bloom_fwd[a].mean():.3f}")
    oof = pd.concat(parts, ignore_index=True)
    out = pd.DataFrame({"bay": "Narragansett", "station": oof["station"].astype(str),
                        "date": oof["date"], "y": oof["bloom_fwd"].astype(int),
                        "prob": oof["prob"].astype(float),
                        "clim_rate": oof["clim_rate"].astype(float)})
    if verbose:
        print(f"Narragansett universe: {len(out)} onset station-days, "
              f"{out.y.sum()} blooms, {out.station.nunique()} stations, "
              f"{out.date.min().date()} .. {out.date.max().date()}")

    # single-split reproduction of the published 2023 number
    train = lab[lab.year <= 2020]
    test = lab[lab.year == 2023]
    med = train[NAR_TIER_A].median(numeric_only=True)
    prep = lambda d: d[NAR_TIER_A].fillna(med).values  # noqa: E731
    model = _fit_gb(prep(train), train.bloom_fwd.values)
    pt = model.predict_proba(prep(test))[:, 1]
    om = test.onset.values
    yt = test.bloom_fwd.values
    a = pt[om] >= T_STAR_NAR
    single = {"precision": float(yt[om][a].mean()), "base_rate": float(yt[om].mean()),
              "n": int(om.sum()), "n_alert": int(a.sum())}
    single["lift"] = single["precision"] / single["base_rate"]
    return out.sort_values(["date", "station"]).reset_index(drop=True), single


# --------------------------------------------------------------------------
# Strategies: each returns the boolean mask of visited rows for ONE month
# --------------------------------------------------------------------------
def _evenly_spaced(n_items, k):
    """k indices spread evenly over range(n_items) (may repeat if k > n)."""
    if n_items == 0 or k == 0:
        return np.array([], dtype=int)
    return np.round(np.linspace(0, n_items - 1, k)).astype(int)


def pick_calendar_fixed(m, V, rot_state, stations):
    """Evenly spaced dates; at each date the next station in a fixed rotation
    that is sampled that day and not yet chosen. If the target date has no
    unused station, the nearest-in-date unused row is taken."""
    n = min(V, len(m))
    chosen = np.zeros(len(m), dtype=bool)
    dates = np.sort(m["date"].unique())
    targets = _evenly_spaced(len(dates), n)
    idx_by_date = {d: np.where(m["date"].values == d)[0] for d in dates}
    for ti in targets:
        d = dates[ti]
        picked = None
        for k in range(len(stations)):
            st = stations[(rot_state["ptr"] + k) % len(stations)]
            cand = [i for i in idx_by_date[d] if m["station"].values[i] == st and not chosen[i]]
            if cand:
                picked = cand[0]
                rot_state["ptr"] = (rot_state["ptr"] + k + 1) % len(stations)
                break
        if picked is None:
            unused = np.where(~chosen)[0]
            if len(unused) == 0:
                break
            gap = np.abs((m["date"].values[unused] - d).astype("timedelta64[D]").astype(int))
            picked = unused[int(np.argmin(gap))]
            rot_state["ptr"] = (rot_state["ptr"] + 1) % len(stations)
        chosen[picked] = True
    return chosen


def pick_random(m, V, rng):
    n = min(V, len(m))
    chosen = np.zeros(len(m), dtype=bool)
    chosen[rng.choice(len(m), size=n, replace=False)] = True
    return chosen


def pick_climatology(m, V):
    """Stations in descending station x month training bloom rate; within a
    station, dates spread evenly; ties broken by station name."""
    n = min(V, len(m))
    chosen = np.zeros(len(m), dtype=bool)
    order = (m.groupby("station")["clim_rate"].first()
             .reset_index().sort_values(["clim_rate", "station"],
                                        ascending=[False, True]))
    left = n
    for st in order["station"]:
        if left == 0:
            break
        rows = np.where(m["station"].values == st)[0]
        rows = rows[np.argsort(m["date"].values[rows])]
        take = rows[np.unique(_evenly_spaced(len(rows), min(left, len(rows))))]
        chosen[take] = True
        left -= len(take)
    return chosen


def pick_alert_greedy(m, V):
    n = min(V, len(m))
    chosen = np.zeros(len(m), dtype=bool)
    order = np.lexsort((m["station"].values, m["date"].values, -m["prob"].values))
    chosen[order[:n]] = True
    return chosen


def pick_alert_causal(m, V, t_star):
    chosen = np.zeros(len(m), dtype=bool)
    left = V
    for d in np.sort(m["date"].unique()):
        if left == 0:
            break
        rows = np.where((m["date"].values == d) & (m["prob"].values >= t_star))[0]
        rows = rows[np.argsort(-m["prob"].values[rows], kind="stable")]
        take = rows[:left]
        chosen[take] = True
        left -= len(take)
    return chosen


# --------------------------------------------------------------------------
# Simulation
# --------------------------------------------------------------------------
def simulate(u, t_star, verbose=True):
    """Per-month (visits, blooms confirmed, month blooms) for every strategy
    and budget. Returns a long dataframe of month-level results."""
    u = u.copy()
    u["ym"] = u["date"].dt.to_period("M")
    months = sorted(u["ym"].unique())
    stations = sorted(u["station"].unique())
    rows = []
    for V in BUDGETS:
        rot_state = {"ptr": 0}
        for ym in months:
            m = u[u["ym"] == ym].sort_values(["date", "station"]).reset_index(drop=True)
            y = m["y"].values
            total = int(y.sum())
            res = {}
            c = pick_calendar_fixed(m, V, rot_state, stations)
            res["calendar_fixed"] = (int(c.sum()), int(y[c].sum()))
            vis, bl = [], []
            for s in range(N_RANDOM_SEEDS):
                c = pick_random(m, V, np.random.default_rng(SEED + s))
                vis.append(c.sum()); bl.append(y[c].sum())
            res["random_uniform"] = (float(np.mean(vis)), float(np.mean(bl)))
            c = pick_climatology(m, V)
            res["climatology"] = (int(c.sum()), int(y[c].sum()))
            c = pick_alert_greedy(m, V)
            res["alert_greedy"] = (int(c.sum()), int(y[c].sum()))
            c = pick_alert_causal(m, V, t_star)
            res["alert_causal"] = (int(c.sum()), int(y[c].sum()))
            for s, (v, b) in res.items():
                rows.append(dict(strategy=s, V=V, ym=str(ym), n_rows=len(m),
                                 visits=v, confirmed=b, blooms=total))
    out = pd.DataFrame(rows)
    if verbose:
        print(f"  {len(months)} months, {len(stations)} stations, "
              f"{len(u)} station-days, {int(u.y.sum())} blooms")
    return out


def aggregate(month_df, n_boot=N_BOOT, seed=SEED):
    """Totals over months + month-resampled bootstrap CIs."""
    rng = np.random.default_rng(seed)
    out = []
    for (s, V), g in month_df.groupby(["strategy", "V"], sort=False):
        vis, con, blo = g["visits"].values, g["confirmed"].values, g["blooms"].values
        n = len(g)
        idx = rng.integers(0, n, size=(n_boot, n))
        bv, bc, bb = vis[idx].sum(1), con[idx].sum(1), blo[idx].sum(1)
        with np.errstate(divide="ignore", invalid="ignore"):
            vpb = np.where(bc > 0, bv / bc, np.nan)
            share = np.where(bb > 0, bc / bb, np.nan)
        years = pd.PeriodIndex(g["ym"], freq="M").year
        out.append(dict(
            strategy=s, V=V, n_months=n, n_years=int(pd.Series(years).nunique()),
            visits=float(vis.sum()), blooms_confirmed=float(con.sum()),
            blooms_total=int(blo.sum()),
            visits_per_bloom=float(vis.sum() / con.sum()) if con.sum() > 0 else np.nan,
            share_caught=float(con.sum() / blo.sum()) if blo.sum() > 0 else np.nan,
            ci_lo=float(np.nanpercentile(vpb, 2.5)), ci_hi=float(np.nanpercentile(vpb, 97.5)),
            share_ci_lo=float(np.nanpercentile(share, 2.5)),
            share_ci_hi=float(np.nanpercentile(share, 97.5))))
    return pd.DataFrame(out)


def full_budget_precision(u, t_star):
    a = u["prob"].values >= t_star
    prec = float(u["y"].values[a].mean())
    base = float(u["y"].mean())
    return dict(precision=prec, base_rate=base, lift=prec / base,
                n=len(u), n_alert=int(a.sum()))


# --------------------------------------------------------------------------
def plot(summary, path):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), dpi=150)
    for ax, bay in zip(axes, ["LIS", "Narragansett"]):
        d = summary[summary["bay"] == bay]
        for s in STRATEGIES:
            g = d[d["strategy"] == s].sort_values("V")
            col = STRATEGY_COLOR[s]
            ax.fill_between(g["V"], g["ci_lo"], g["ci_hi"], color=col, alpha=0.12, lw=0)
            ax.plot(g["V"], g["visits_per_bloom"], color=col, lw=2, marker="o", ms=5,
                    label=STRATEGY_LABEL[s])
        ax.set_xticks(list(BUDGETS))
        ax.set_xlabel("Budget V (station-visits per month)")
        ax.set_title(bay, loc="left", fontsize=11)
        ax.grid(axis="y", color="#e5e5e2", lw=0.8)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        # clip the axis to the point estimates' neighbourhood so the wide
        # upper CIs of the few-bloom LIS test set do not flatten the lines
        top = 1.3 * max(d["visits_per_bloom"].max(), d["ci_hi"].median())
        ax.set_ylim(0, top)
        clipped = d[d["ci_hi"] > top]
        if len(clipped):
            ax.text(0.02, 0.97, f"upper CI bands clipped (max {clipped['ci_hi'].max():.0f})",
                    transform=ax.transAxes, fontsize=7, color="#52514e", va="top")
    axes[0].set_ylabel("Station-visits per confirmed bloom")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, fontsize=8, loc="lower center",
               ncol=3, bbox_to_anchor=(0.5, -0.01))
    fig.suptitle("Cost of a confirmed bloom under a fixed monthly budget "
                 "(bands: 95% CI, months resampled)", fontsize=10, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def notes_snippet(summary, V=8):
    """Markdown for notes/SCIENTIFIC_METHOD.md (numbers straight from the CSV)."""
    lines = [f"| Strategy | LIS visits/bloom [95% CI] | LIS share caught | "
             f"Narragansett visits/bloom [95% CI] | Narragansett share caught |",
             "|---|---|---|---|---|"]
    sub = summary[summary["V"] == V].set_index(["bay", "strategy"])
    for s in STRATEGIES:
        l, n = sub.loc[("LIS", s)], sub.loc[("Narragansett", s)]
        lines.append(f"| {STRATEGY_LABEL[s]} | {l.visits_per_bloom:.1f} "
                     f"[{l.ci_lo:.1f}, {l.ci_hi:.1f}] | {l.share_caught:.2f} | "
                     f"{n.visits_per_bloom:.2f} [{n.ci_lo:.2f}, {n.ci_hi:.2f}] | "
                     f"{n.share_caught:.3f} |")
    sent = []
    for bay in ("LIS", "Narragansett"):
        c, a = sub.loc[(bay, "calendar_fixed")], sub.loc[(bay, "alert_greedy")]
        sent.append(
            f"{bay}: With {V} station-visits a month, calendar sampling confirms "
            f"{c.blooms_confirmed / c.n_years:.1f} blooms per season "
            f"({c.visits_per_bloom:.1f} visits per bloom [{c.ci_lo:.1f}, {c.ci_hi:.1f}]); "
            f"alert-directed sampling confirms {a.blooms_confirmed / a.n_years:.1f} "
            f"({a.visits_per_bloom:.1f} visits per bloom [{a.ci_lo:.1f}, {a.ci_hi:.1f}]) "
            f"(season = test year, {int(c.n_years)} years, {int(c.n_months)} months).")
    return "\n".join(lines), sent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nar-root", default=os.path.join("..", "hab-bloom-predictor-narragansett"))
    ap.add_argument("--n-boot", type=int, default=N_BOOT)
    ap.add_argument("--out", default=OUT_CSV)
    ap.add_argument("--fig", default=OUT_FIG)
    a = ap.parse_args()

    print("=== LIS: locked walk-forward frame (reference_baselines.build_station_day)")
    lis = lis_universe()
    print("=== Narragansett: rolling-origin out-of-fold GB tier A, onset rows")
    nar, nar_single = nar_universe(a.nar_root)
    pd.concat([lis, nar]).to_csv(OUT_ROWS, index=False)
    print(f"row-level inputs cached -> {OUT_ROWS}")

    parts = []
    for bay, u, t in (("LIS", lis, T_STAR_LIS), ("Narragansett", nar, T_STAR_NAR)):
        print(f"=== simulate {bay} (t* = {t})")
        md = simulate(u, t)
        sm = aggregate(md, n_boot=a.n_boot)
        sm.insert(0, "bay", bay)
        parts.append(sm)
    summary = pd.concat(parts, ignore_index=True)
    cols = ["bay", "strategy", "V", "visits", "blooms_confirmed", "visits_per_bloom",
            "share_caught", "ci_lo", "ci_hi", "share_ci_lo", "share_ci_hi",
            "blooms_total", "n_months", "n_years"]
    summary = summary[cols]
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    summary.to_csv(a.out, index=False)
    plot(summary, a.fig)
    print(f"wrote {a.out} and {a.fig}\n")

    pd.set_option("display.width", 200)
    for bay in ("LIS", "Narragansett"):
        d = summary[summary.bay == bay]
        print(f"--- {bay} ---")
        print(d[["strategy", "V", "visits", "blooms_confirmed", "visits_per_bloom",
                 "ci_lo", "ci_hi", "share_caught", "share_ci_lo", "share_ci_hi"]]
              .to_string(index=False, float_format=lambda x: f"{x:.3f}"))
        print()

    # --- sanity check: full budget == published lift x base rate --------------
    print("=== SANITY: alert-directed precision at the FULL budget vs published")
    print(f"{'bay':<13}{'set':<38}{'n':>6}{'alerts':>8}{'base':>8}{'prec':>8}{'lift':>7}")
    f = full_budget_precision(lis, T_STAR_LIS)
    print(f"{'LIS':<13}{'this script, test 2023-25, t*=0.35':<38}{f['n']:>6}{f['n_alert']:>8}"
          f"{f['base_rate']:>8.3f}{f['precision']:>8.3f}{f['lift']:>7.2f}")
    ref_path = "data/reference_baselines.csv"
    if os.path.exists(ref_path):
        r = pd.read_csv(ref_path)
        r = r[(r.level == "station-day") & r.forecaster.str.startswith("MODEL")].iloc[0]
        print(f"{'LIS':<13}{'published reference_baselines.csv':<38}{int(r.n):>6}"
              f"{int(r.tp + r.fp):>8}{r.base_rate:>8.3f}{r.precision:>8.3f}{r.lift:>7.2f}")
    print(f"{'LIS':<13}{'published daily_inference.py docstring':<38}{'':>6}{'':>8}"
          f"{'':>8}{'~0.125':>8}{'~2.7':>7}")
    f = full_budget_precision(nar[nar.date.dt.year == 2023], T_STAR_NAR)
    print(f"{'Narragansett':<13}{'this script, OOF fold 2023 (train<=21)':<38}{f['n']:>6}"
          f"{f['n_alert']:>8}{f['base_rate']:>8.3f}{f['precision']:>8.3f}{f['lift']:>7.2f}")
    s = nar_single
    print(f"{'Narragansett':<13}{'this script, single split train<=2020':<38}{s['n']:>6}"
          f"{s['n_alert']:>8}{s['base_rate']:>8.3f}{s['precision']:>8.3f}{s['lift']:>7.2f}")
    print(f"{'Narragansett':<13}{'published GB_onset A_LIS_analog (2023)':<38}{1727:>6}{517:>8}"
          f"{0.347:>8.3f}{0.696:>8.3f}{2.00:>7.2f}")
    f = full_budget_precision(nar, T_STAR_NAR)
    print(f"{'Narragansett':<13}{'this script, pooled OOF 2015-23, t=0.50':<38}{f['n']:>6}"
          f"{f['n_alert']:>8}{f['base_rate']:>8.3f}{f['precision']:>8.3f}{f['lift']:>7.2f}")
    print("(random_uniform visits-per-bloom at any V ~= 1 / base rate; "
          "alert_causal at V=inf has precision = published)\n")

    table, sentences = notes_snippet(summary, V=8)
    print("=== notes snippet (V=8)")
    print(table)
    for s in sentences:
        print(s)


if __name__ == "__main__":
    main()
