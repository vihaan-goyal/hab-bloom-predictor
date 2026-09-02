"""W9: out-of-sample bloom probability ~21 days before each LIS bloom onset.

Locked LR pipeline (src/models/locked_pipeline.py), 21-day forward label,
trained on visits dated <= 2019-12-31; every visit dated 2020-2025 is scored
out of sample.

Onset = station visit with Chlorophyll > 10 whose previous visit at that
station had Chlorophyll <= 10 and occurred within 60 days. LIS visits are
~2-3 weeks apart, so "21 days before" = the prior visit whose date lies in
[onset-35, onset-10] d, choosing the one closest to -21 (offset recorded).
The visit before that one is recorded too (offset and p) when present.

Matched null = visits 2020-2025 with Chlorophyll <= 10, at least one later
visit at the station within 35 d, and no Chlorophyll > 10 in those 35 d.
Reported as the full null distribution and as a station+month matched
resample (one null visit per onset, 500 draws).

Output: data/prob_before_onset_lis.csv (+ null CSV, printed summary)
Run from repo root with the BASE conda python (not the hab env).
"""
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from src.models.locked_pipeline import (load_locked_dataframe, add_forward_label,
                                        fit_locked_model, predict_proba)

BLOOM = 10.0
T_STAR = 0.35
TRAIN_END = "2019-12-31"
SCORE_YEARS = range(2020, 2026)
GAP_MAX = 60           # prior visit must be within 60 d for an onset
WIN = (10, 35)         # "-21 d" visit must lie in [onset-35, onset-10]
NULL_FWD = 35

df = load_locked_dataframe()
df = add_forward_label(df, horizon=21, col="bloom_fwd")
df = df.sort_values(["station_name", "date"]).reset_index(drop=True)
df["year"] = df.date.dt.year
bundle = fit_locked_model(df, "bloom_fwd", train_end=TRAIN_END)
print(f"trained on {bundle['n_train']} visits <= {TRAIN_END}, "
      f"bloom rate {bundle['train_bloom_rate']:.3f}")
df["p"] = np.nan
sc_mask = df.year.isin(SCORE_YEARS)
df.loc[sc_mask, "p"] = predict_proba(bundle, df[sc_mask])
sc = df[sc_mask].copy()
lab = sc.bloom_fwd.notna()
print(f"scored visits 2020-2025: {len(sc)}  AUC p vs bloom_fwd (all rows) = "
      f"{roc_auc_score(sc.bloom_fwd[lab].astype(int), sc.p[lab]):.3f}")

# ---- onsets ------------------------------------------------------------------
recs = []
for st, g in df.groupby("station_name"):
    g = g.reset_index(drop=True)
    for i in range(1, len(g)):
        if g.Chlorophyll[i] <= BLOOM or g.year[i] not in SCORE_YEARS:
            continue
        gap = (g.date[i] - g.date[i - 1]).days
        if g.Chlorophyll[i - 1] > BLOOM or gap > GAP_MAX:
            continue
        od = g.date[i]
        prior = g.iloc[:i].copy()
        prior["off"] = (prior.date - od).dt.days
        cand = prior[(prior.off >= -WIN[1]) & (prior.off <= -WIN[0])]
        rec = dict(station_name=st, onset_date=od.date(), prev_visit_gap=gap,
                   chl_at_onset=g.Chlorophyll[i], visit_offset_days=np.nan,
                   chl_at_visit=np.nan, p_at_visit=np.nan,
                   prev_offset_days=np.nan, p_prev=np.nan)
        if not cand.empty:
            k = (cand.off + 21).abs().idxmin()
            v = cand.loc[k]
            rec.update(visit_offset_days=int(v.off), chl_at_visit=v.Chlorophyll,
                       p_at_visit=v.p)
            before = prior[prior.index < k]
            if not before.empty:
                b = before.iloc[-1]
                rec.update(prev_offset_days=int(b.off), p_prev=b.p)
        recs.append(rec)
res = pd.DataFrame(recs)
res.to_csv("data/prob_before_onset_lis.csv", index=False)
print(f"onsets 2020-2025: {len(res)}  with a visit in [-35,-10]: "
      f"{res.p_at_visit.notna().sum()}  with a visit before that: {res.p_prev.notna().sum()}")
print(f"wrote data/prob_before_onset_lis.csv")

# ---- matched null --------------------------------------------------------------
null_rows = []
for st, g in sc.groupby("station_name"):
    full = df[df.station_name == st]
    dates = full.date.values; chl = full.Chlorophyll.values
    for _, r in g.iterrows():
        if r.Chlorophyll > BLOOM:
            continue
        m = (dates > np.datetime64(r.date)) & \
            (dates <= np.datetime64(r.date + pd.Timedelta(days=NULL_FWD)))
        if m.any() and not (chl[m] > BLOOM).any():
            null_rows.append((st, r.date, r.Chlorophyll, r.p))
null = pd.DataFrame(null_rows, columns=["station_name", "date", "Chlorophyll", "p"])
null.to_csv("data/prob_before_onset_lis_null.csv", index=False)


def summ(p, thr=T_STAR):
    p = pd.Series(p).dropna()
    q = p.quantile([.25, .5, .75])
    return dict(n=len(p), median=q[.5], q25=q[.25], q75=q[.75],
                frac_ge=(p >= thr).mean())


ons = res.dropna(subset=["p_at_visit"])
S_on, S_null = summ(ons.p_at_visit), summ(null.p)
S_prev = summ(res.p_prev)

rng = np.random.default_rng(42)
null["month"] = null.date.dt.month
key = {k: g.p.values for k, g in null.groupby(["station_name", "month"])}
ons_key = [(s, pd.Timestamp(d).month) for s, d in zip(ons.station_name, ons.onset_date)]
draws = []
for _ in range(500):
    samp = [rng.choice(key[k]) for k in ons_key if k in key]
    s = summ(samp); draws.append([s["median"], s["q25"], s["q75"], s["frac_ge"]])
mm = np.median(np.array(draws), axis=0)
n_matched = sum(k in key for k in ons_key)
auc = roc_auc_score(np.r_[np.ones(len(ons)), np.zeros(len(null))],
                    np.r_[ons.p_at_visit.values, null.p.values])

print("\n=== LIS: p at the ~-21 d visit (locked LR h21, out of sample 2020-2025) ===")
print(f"onsets with a -21 visit     : {S_on['n']} / {len(res)}  "
      f"offset median {ons.visit_offset_days.median():.0f} d  "
      f"IQR [{ons.visit_offset_days.quantile(.25):.0f}, {ons.visit_offset_days.quantile(.75):.0f}]")
print(f"p at ~-21   onsets          : median {S_on['median']:.3f}  IQR [{S_on['q25']:.3f}, {S_on['q75']:.3f}]  frac>={T_STAR} {S_on['frac_ge']:.3f}")
print(f"p           null (all)      : n={S_null['n']}  median {S_null['median']:.3f}  IQR [{S_null['q25']:.3f}, {S_null['q75']:.3f}]  frac>={T_STAR} {S_null['frac_ge']:.3f}")
print(f"p           null (st+month) : n={n_matched}/draw  median {mm[0]:.3f}  IQR [{mm[1]:.3f}, {mm[2]:.3f}]  frac>={T_STAR} {mm[3]:.3f}  (median over 500 draws)")
print(f"p at visit before that      : n={S_prev['n']}  median {S_prev['median']:.3f}  IQR [{S_prev['q25']:.3f}, {S_prev['q75']:.3f}]  frac>={T_STAR} {S_prev['frac_ge']:.3f}  "
      f"offset median {res.prev_offset_days.median():.0f} d")
print(f"AUC onset-21 vs null        : {auc:.3f}")
print(f"chl at -21 visit onsets     : median {ons.chl_at_visit.median():.2f}  "
      f"frac chl>10: {(ons.chl_at_visit > BLOOM).mean():.3f}  "
      f"(is the immediately-previous visit: {(ons.visit_offset_days == -ons.prev_visit_gap).mean():.3f})")
print("\nby station (count, median p):")
print(res.groupby("station_name").p_at_visit.agg(["count", "median"]).round(3)
      .sort_values("count", ascending=False).head(15).to_string())
