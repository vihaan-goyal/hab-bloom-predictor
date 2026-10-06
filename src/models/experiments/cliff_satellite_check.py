"""
cliff_satellite_check.py -- pre-registered satellite cross-check of the 2014
chlorophyll cliff (fork findings section 15; parent SCIENTIFIC_METHOD Phase 3).
================================================================================

BACKGROUND
CT DEEP lab-bottle chlorophyll at the 50 LIS stations shows the share of
station-days with chl > 10 ug/L falling from 0.42-0.59 (2009-2013) to 0.09 in
2014 and 0.03-0.11 every year since (fork script bloom_rate_by_period.py).
The worry is a lab / method change in 2014 rather than an ecological step.
An instrument with no 2014 method change -- MODIS-Aqua ocean-colour
chlorophyll -- is available at the same stations and dates.

SATELLITE PRODUCT (from src/features/extract_modis_features.py)
AQUA_MODIS L3m DAY CHL chlor_a, 4 km mapped grid (files
AQUA_MODIS.YYYYMMDD.L3m.DAY.CHL.chlor_a.4km.nc). For each station and day the
extractor takes the 5x5-pixel patch (~20 x 20 km) centred on the nearest pixel;
sat_chl_mean is the mean of the valid pixels in that patch and
sat_chl_valid_frac is the share of the 25 pixels that are valid (unmasked,
0 < chl <= 1000). Standard NASA chlor_a (OCI/OC3M blend), which is known to be
biased in optically complex estuaries -- so the satellite is a proxy with its own
unknown but TIME-STABLE relation to the lab value. Time-stability, not accuracy,
is what this check needs. Single-sensor product (Aqua only), so no 2014 sensor
change either; Aqua's radiometric degradation is corrected in the reprocessing.

PRE-REGISTERED CRITERION (fixed before any result below was computed)
  Population : station-days at the 50 LIS stations with sat_chl_valid_frac
               >= 0.5, years 2003-2025.
  Threshold  : the 75th percentile of sat_chl_mean over the 2005-2013 reference
               period, pooled across stations (the satellite has its own units;
               10 ug/L lab is not 10 ug/L satellite, so the threshold is set by
               rank, not by value).
  Statistic  : yearly share of valid station-days above that threshold; the
               ratio R = share(2015-2023) / share(2009-2013).
  Uncertainty: station-year clustered bootstrap, n = 2000 resamples, seed 42,
               resampling station-year clusters with replacement within each
               period; percentile 95% CI for R.
  Decision   : STEP CONFIRMED  if R < 0.5 and CI upper bound < 0.7
               NO STEP         if CI lower bound > 0.8
               INCONCLUSIVE    otherwise.

SECONDARY REPORTS (descriptive, not part of the decision)
  (a) the same ratio for the LAB record (Chlorophyll > 10) restricted to the
      same station-days on which the satellite is valid (matched-day comparison,
      rules out a coverage artefact), plus the full lab record for reference;
  (b) annual mean sat_chl_mean on valid days;
  (c) share above an absolute 10 ug/L in satellite units (sensitivity);
  (d) 2x2 of lab-exceedance vs satellite-exceedance on matched days, pre-2014
      (2003-2013) and post-2014 (2014-2025), with agreement and Cohen's kappa
      by year -- if the lab-satellite agreement itself drops sharply in 2014
      that points to a lab change.

OUTPUTS
  data/cliff_satellite_check.csv      per-year rows + period rows
  figures/fig_cliff_satellite.png     two panels (lab share and satellite share,
                                      each on its own axis; matched-day
                                      agreement by year)
  a printed verdict line that quotes the criterion.

Run from the parent repo root with the BASE conda env:
  python src/models/experiments/cliff_satellite_check.py
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------------------------------------------------------- constants
MODIS_CSV = "data/modis_station_daily.csv"
LAB_CSV = "data/hab_features_tidal.csv"
OUT_CSV = "data/cliff_satellite_check.csv"
OUT_FIG = "figures/fig_cliff_satellite.png"

VALID_MIN = 0.5
REF_YEARS = (2005, 2013)           # threshold reference period
PRE_YEARS = (2009, 2013)           # ratio numerator baseline
POST_YEARS = (2015, 2023)          # ratio numerator
YEARS = (2003, 2025)
LAB_THRESH = 10.0
SAT_ABS_THRESH = 10.0
N_BOOT = 2000
SEED = 42

CRITERION = ("Criterion: valid (sat_chl_valid_frac >= 0.5) LIS station-days; threshold = P75 of "
             "sat_chl_mean over 2005-2013 pooled; R = share(2015-2023)/share(2009-2013); "
             "station-year clustered bootstrap n=2000 seed=42. STEP if R < 0.5 and CI_hi < 0.7; "
             "NO STEP if CI_lo > 0.8; else INCONCLUSIVE.")


# ---------------------------------------------------------------- helpers
def in_years(df, lo_hi):
    return df[(df.year >= lo_hi[0]) & (df.year <= lo_hi[1])]


def cluster_boot_ratio(df, flag, rng, n_boot=N_BOOT):
    """Ratio share(POST)/share(PRE) with a station-year clustered bootstrap.

    Clusters are resampled with replacement within each period separately, so
    each period keeps its own number of clusters.  Returns (ratio, lo, hi).
    """
    def cluster_sums(sub):
        g = sub.groupby(["station_name", "year"])[flag].agg(["sum", "size"])
        return g["sum"].to_numpy(float), g["size"].to_numpy(float)

    pre_s, pre_n = cluster_sums(in_years(df, PRE_YEARS))
    post_s, post_n = cluster_sums(in_years(df, POST_YEARS))
    point = (post_s.sum() / post_n.sum()) / (pre_s.sum() / pre_n.sum())
    boots = np.empty(n_boot)
    for b in range(n_boot):
        ip = rng.integers(0, len(pre_s), len(pre_s))
        iq = rng.integers(0, len(post_s), len(post_s))
        pre_share = pre_s[ip].sum() / pre_n[ip].sum()
        post_share = post_s[iq].sum() / post_n[iq].sum()
        boots[b] = post_share / pre_share if pre_share > 0 else np.nan
    lo, hi = np.nanpercentile(boots, [2.5, 97.5])
    return point, lo, hi


def kappa(a, b):
    a = np.asarray(a, bool); b = np.asarray(b, bool)
    n = len(a)
    if n == 0:
        return np.nan
    po = (a == b).mean()
    pe = a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean())
    return (po - pe) / (1 - pe) if pe < 1 else np.nan


def two_by_two(sub):
    lab, sat = sub.lab_exc.astype(bool), sub.sat_exc.astype(bool)
    return dict(both=int((lab & sat).sum()), lab_only=int((lab & ~sat).sum()),
                sat_only=int((~lab & sat).sum()), neither=int((~lab & ~sat).sum()),
                n=int(len(sub)), agree=float((lab == sat).mean()) if len(sub) else np.nan,
                kappa=kappa(lab, sat))


# ---------------------------------------------------------------- load
sat = pd.read_csv(MODIS_CSV, dtype={"station_name": str}, parse_dates=["date"])
sat["year"] = sat.date.dt.year
sat = in_years(sat, YEARS)
n_all = len(sat)
valid = sat[sat.sat_chl_valid_frac >= VALID_MIN].copy()
print(f"MODIS rows {n_all:,}; valid_frac >= {VALID_MIN}: {len(valid):,} "
      f"({len(valid)/n_all:.3f}); stations {sat.station_name.nunique()}")

lab = pd.read_csv(LAB_CSV, usecols=["station_name", "date", "Chlorophyll"],
                  dtype={"station_name": str}, parse_dates=["date"]).dropna(subset=["Chlorophyll"])
lab["year"] = lab.date.dt.year
lab = in_years(lab, YEARS)
lab["lab_exc"] = lab.Chlorophyll > LAB_THRESH

# ---------------------------------------------------------------- threshold (fixed by criterion)
ref = in_years(valid, REF_YEARS)
SAT_THRESH = float(np.percentile(ref.sat_chl_mean, 75))
print(f"Satellite threshold: P75 of sat_chl_mean, {REF_YEARS[0]}-{REF_YEARS[1]} pooled, "
      f"n={len(ref):,} valid station-days -> {SAT_THRESH:.2f} (satellite units)")
valid["sat_exc"] = valid.sat_chl_mean > SAT_THRESH
valid["sat_exc10"] = valid.sat_chl_mean > SAT_ABS_THRESH

# matched days: lab sample AND valid satellite same station, same date
matched = lab.merge(valid[["station_name", "date", "sat_chl_mean", "sat_exc", "sat_exc10"]],
                    on=["station_name", "date"], how="inner")
print(f"Matched station-days (lab sample + valid satellite): {len(matched):,} of {len(lab):,} lab days")

# ---------------------------------------------------------------- per-year table
rng = np.random.default_rng(SEED)
yrs = list(range(YEARS[0], YEARS[1] + 1))
rows = []
for y in yrs:
    v = valid[valid.year == y]; l = lab[lab.year == y]; m = matched[matched.year == y]
    tt = two_by_two(m)
    rows.append(dict(
        kind="year", period=str(y),
        sat_n=len(v), sat_valid_frac_of_all=float((sat.year == y).sum() and len(v) / (sat.year == y).sum()),
        sat_share_p75=v.sat_exc.mean() if len(v) else np.nan,
        sat_share_gt10=v.sat_exc10.mean() if len(v) else np.nan,
        sat_mean=v.sat_chl_mean.mean() if len(v) else np.nan,
        lab_n=len(l), lab_share_gt10=l.lab_exc.mean() if len(l) else np.nan,
        matched_n=len(m), lab_matched_share_gt10=m.lab_exc.mean() if len(m) else np.nan,
        sat_matched_share_p75=m.sat_exc.mean() if len(m) else np.nan,
        agree_frac=tt["agree"], kappa=tt["kappa"],
        both=tt["both"], lab_only=tt["lab_only"], sat_only=tt["sat_only"], neither=tt["neither"],
    ))
yr = pd.DataFrame(rows)

# ---------------------------------------------------------------- period rows + ratios
def period_row(lo_hi, label):
    v = in_years(valid, lo_hi); l = in_years(lab, lo_hi); m = in_years(matched, lo_hi)
    tt = two_by_two(m)
    return dict(kind="period", period=label,
                sat_n=len(v), sat_valid_frac_of_all=len(v) / max(1, len(in_years(sat, lo_hi))),
                sat_share_p75=v.sat_exc.mean(), sat_share_gt10=v.sat_exc10.mean(), sat_mean=v.sat_chl_mean.mean(),
                lab_n=len(l), lab_share_gt10=l.lab_exc.mean(),
                matched_n=len(m), lab_matched_share_gt10=m.lab_exc.mean(), sat_matched_share_p75=m.sat_exc.mean(),
                agree_frac=tt["agree"], kappa=tt["kappa"],
                both=tt["both"], lab_only=tt["lab_only"], sat_only=tt["sat_only"], neither=tt["neither"])

periods = [((2003, 2013), "2003-2013 (pre)"), (REF_YEARS, "2005-2013 (ref)"), (PRE_YEARS, "2009-2013"),
           ((2014, 2014), "2014"), (POST_YEARS, "2015-2023"), ((2014, 2025), "2014-2025 (post)")]
per = pd.DataFrame([period_row(p, lbl) for p, lbl in periods])

# Ratios (POST/PRE) with clustered bootstrap CIs. Primary first, seeded once.
R_sat, R_sat_lo, R_sat_hi = cluster_boot_ratio(valid, "sat_exc", rng)
R_sat10, R_sat10_lo, R_sat10_hi = cluster_boot_ratio(valid, "sat_exc10", rng)
R_labm, R_labm_lo, R_labm_hi = cluster_boot_ratio(matched, "lab_exc", rng)
R_satm, R_satm_lo, R_satm_hi = cluster_boot_ratio(matched, "sat_exc", rng)
R_lab, R_lab_lo, R_lab_hi = cluster_boot_ratio(lab, "lab_exc", rng)

ratio_rows = pd.DataFrame([
    dict(kind="ratio", period="sat_share_p75 (PRIMARY)", ratio=R_sat, ci_lo=R_sat_lo, ci_hi=R_sat_hi),
    dict(kind="ratio", period="sat_share_gt10 (sensitivity)", ratio=R_sat10, ci_lo=R_sat10_lo, ci_hi=R_sat10_hi),
    dict(kind="ratio", period="lab_share_gt10 matched days", ratio=R_labm, ci_lo=R_labm_lo, ci_hi=R_labm_hi),
    dict(kind="ratio", period="sat_share_p75 matched days", ratio=R_satm, ci_lo=R_satm_lo, ci_hi=R_satm_hi),
    dict(kind="ratio", period="lab_share_gt10 full record", ratio=R_lab, ci_lo=R_lab_lo, ci_hi=R_lab_hi),
])

# ---------------------------------------------------------------- verdict (rule fixed above)
if R_sat < 0.5 and R_sat_hi < 0.7:
    verdict = "STEP CONFIRMED"
elif R_sat_lo > 0.8:
    verdict = "NO STEP"
else:
    verdict = "INCONCLUSIVE"

# ---------------------------------------------------------------- save
os.makedirs("data", exist_ok=True); os.makedirs("figures", exist_ok=True)
out = pd.concat([yr, per, ratio_rows], ignore_index=True)
out.attrs["sat_threshold"] = SAT_THRESH
out.insert(2, "sat_threshold", SAT_THRESH)
out.to_csv(OUT_CSV, index=False)

# ---------------------------------------------------------------- print
pd.set_option("display.width", 220); pd.set_option("display.float_format", lambda v: f"{v:.3f}")
print("\nPer year (shares with n beside them):")
print(yr[["period", "sat_n", "sat_valid_frac_of_all", "sat_share_p75", "sat_share_gt10", "sat_mean",
          "lab_n", "lab_share_gt10", "matched_n", "lab_matched_share_gt10", "sat_matched_share_p75",
          "agree_frac", "kappa"]].to_string(index=False))
print("\nPer period:")
print(per[["period", "sat_n", "sat_share_p75", "sat_share_gt10", "sat_mean", "lab_n", "lab_share_gt10",
           "matched_n", "lab_matched_share_gt10", "sat_matched_share_p75", "agree_frac", "kappa"]].to_string(index=False))
print("\n2x2 lab-exceedance (>10 ug/L) vs satellite-exceedance (> P75) on matched days:")
for lbl in ["2003-2013 (pre)", "2014-2025 (post)"]:
    r = per[per.period == lbl].iloc[0]
    print(f"  {lbl:18s} n={int(r.matched_n):4d}  both={int(r.both):3d}  lab_only={int(r.lab_only):3d}  "
          f"sat_only={int(r.sat_only):3d}  neither={int(r.neither):3d}  agree={r.agree_frac:.2f}  kappa={r.kappa:.2f}")
print("\nRatios share(2015-2023)/share(2009-2013), 95% station-year clustered bootstrap CI:")
print(ratio_rows.to_string(index=False))

print("\n" + CRITERION)
print(f"RESULT: satellite R = {R_sat:.2f} [95% CI {R_sat_lo:.2f}, {R_sat_hi:.2f}]  "
      f"(share {PRE_YEARS[0]}-{PRE_YEARS[1]} = {per.loc[per.period=='2009-2013','sat_share_p75'].iloc[0]:.3f}, "
      f"n={int(per.loc[per.period=='2009-2013','sat_n'].iloc[0])}; "
      f"share {POST_YEARS[0]}-{POST_YEARS[1]} = {per.loc[per.period=='2015-2023','sat_share_p75'].iloc[0]:.3f}, "
      f"n={int(per.loc[per.period=='2015-2023','sat_n'].iloc[0])}); "
      f"lab full record R = {R_lab:.2f} [{R_lab_lo:.2f}, {R_lab_hi:.2f}]; "
      f"lab on matched days R = {R_labm:.2f} [{R_labm_lo:.2f}, {R_labm_hi:.2f}]")
print(f"VERDICT: {verdict}")

# ---------------------------------------------------------------- figure
BLUE, ORANGE, GRAY, INK = "#2a78d6", "#eb6834", "#9a9893", "#52514e"
fig = plt.figure(figsize=(12, 4.6), dpi=150)
gs = fig.add_gridspec(2, 2, width_ratios=[1.15, 1], hspace=0.08, wspace=0.28)
ax_lab = fig.add_subplot(gs[0, 0])
ax_sat = fig.add_subplot(gs[1, 0], sharex=ax_lab)
ax_ag = fig.add_subplot(gs[:, 1])

x = yr.period.astype(int)
ax_lab.plot(x, yr.lab_share_gt10, color=BLUE, lw=2, marker="o", ms=4, label="lab, all sampled days")
ax_lab.plot(x, yr.lab_matched_share_gt10, color=BLUE, lw=1.2, ls="--", marker="o", ms=3, mfc="white",
            label="lab, satellite-valid days only")
ax_lab.set_ylabel("lab share > 10 ug/L", color=INK)
ax_lab.set_ylim(0, 0.7)
ax_lab.legend(frameon=False, fontsize=8, loc="upper left")
ax_lab.set_title("Yearly exceedance share: lab bottle (top) vs MODIS-Aqua 4 km (bottom)", fontsize=10, loc="left")
plt.setp(ax_lab.get_xticklabels(), visible=False)

ax_sat.plot(x, yr.sat_share_p75, color=ORANGE, lw=2, marker="o", ms=4, label=f"satellite > P75 ref ({SAT_THRESH:.1f})")
ax_sat.plot(x, yr.sat_share_gt10, color=ORANGE, lw=1.2, ls="--", marker="o", ms=3, mfc="white",
            label="satellite > 10 (absolute)")
ax_sat.set_ylabel("satellite share > threshold", color=INK)
ax_sat.set_ylim(0, 0.7)
ax_sat.legend(frameon=False, fontsize=8, loc="upper right")
ax_sat.set_xlabel("year", color=INK)

for ax in (ax_lab, ax_sat):
    ax.axvline(2013.5, color=GRAY, lw=1, ls=":")
    ax.text(2013.7, 0.66, "2014", color=GRAY, fontsize=8, va="top")

ax_ag.bar(x, yr.agree_frac, color=GRAY, width=0.8, edgecolor="white", lw=1, label="agreement (lab>10 vs sat>P75)")
ax_ag.plot(x, yr.kappa, color=BLUE, lw=2, marker="o", ms=4, label="Cohen's kappa")
for xi, n, a in zip(x, yr.matched_n, yr.agree_frac):
    ax_ag.text(xi, a + 0.01, str(int(n)), ha="center", va="bottom", fontsize=6, color=INK)
ax_ag.axvline(2013.5, color=GRAY, lw=1, ls=":")
ax_ag.axhline(0, color=GRAY, lw=0.8)
ax_ag.set_ylim(-0.3, 1.05)
ax_ag.set_xlabel("year", color=INK)
ax_ag.set_ylabel("matched-day agreement / kappa", color=INK)
ax_ag.set_title("Do lab and satellite agree on the same station-day? (n above bars)", fontsize=10, loc="left")
ax_ag.legend(frameon=False, fontsize=8, loc="upper right")

for ax in (ax_lab, ax_sat, ax_ag):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#e6e5e1", lw=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(colors=INK, labelsize=8)

fig.text(0.01, 0.01, f"{verdict}: satellite R = {R_sat:.2f} [{R_sat_lo:.2f}, {R_sat_hi:.2f}]; "
         f"lab R = {R_lab:.2f} [{R_lab_lo:.2f}, {R_lab_hi:.2f}]  (share 2015-2023 / share 2009-2013, "
         f"station-year clustered bootstrap, n=2000)", fontsize=8, color=INK)
fig.savefig(OUT_FIG, bbox_inches="tight")
print(f"\nWrote {OUT_CSV} and {OUT_FIG}")
