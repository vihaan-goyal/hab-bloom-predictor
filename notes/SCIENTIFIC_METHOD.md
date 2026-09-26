# The project as one experiment — scientific-method summary

**Update this file at the end of every work session.** It is the single place
where the project's question, hypotheses, variables, controls, results, and
conclusion are kept current. Last updated: 2026-09-23 (label rebuilt on the lab scale).

## Overarching question

Can chlorophyll-a blooms in Long Island Sound be forecast far enough ahead to
be useful to a monitoring program, using the water-quality data the state
already collects?

## Phase 1 — Build and test the forecast (2025-06 → 2026-08)

- **Hypothesis:** bloom exceedances (chlorophyll > 10 µg/L) can be predicted
  21 days ahead from routine in-situ measurements.
- **Independent variables:** the predictors — chlorophyll history, temperature,
  salinity, dissolved oxygen, nutrients, tidal anomalies, wind, season, station.
- **Dependent variable:** forecast skill on held-out years — AUC, precision,
  recall (POD), lift over climatology.
- **Controls:** trivial reference forecasts — always-alert, persistence
  ("was it blooming last visit?"), station × season climatology.
- **Constants:** 21-day horizon, 10 µg/L threshold, train ≤2019 / val 2020–22 /
  test 2023–25 (and rolling-origin CV 2015–2025), threshold chosen on
  validation only, station-year clustered bootstrap (n=2000, seed 42) for every
  interval claim.
- **Result — partly supported.** Ranking skill is real (AUC 0.875; beats
  always-alert decisively) but precision caps at 0.14 and the model is not
  clearly better than climatology. Thirteen pre-registered improvements
  (nutrients, wind, satellite chl, calibration, XGBoost, station gating, a
  912-config basin search at the 52nd percentile of chance, …) were rejected.
  Side findings: low DO raises bloom odds (0.19 → 0.30); temperature is
  uninformative; no point of no return; the 2016 rust tide was invisible to
  the data.

## Phase 2 — Explain the ceiling (2026-08-31 → 09-01)

- **Hypothesis (pre-registered):** the precision ceiling is caused by sampling
  cadence — 21-day gaps vs blooms that develop faster than that.
- **Independent variable:** sampling interval (15 min → 1, 3, 7, 14, 21, 28 d),
  varied by subsampling Narragansett Bay's continuous sonde record.
- **Control:** Narragansett Bay at full cadence — same recipe, same features,
  same bloom definition, same evaluation. 4.52M readings, 18 stations,
  2005–2023.
- **Pre-registered criterion:** precision at 21-day cadence < 0.30 confirms.
- **Result — rejected.** Dense data: onset precision 0.66 [0.62, 0.69] over
  nine test years, beats every trivial rule. Thinned to 21 days: 0.52, not
  0.14. LIS's own 15-minute buoys: 0.16–0.18 (boat level). Cadence costs
  ~0.3 precision but is not the primary cause.
- Also measured, newly possible with dense data: median bloom lasts 4 days,
  ramps in ~3; DO conditioning and no-PONR replicate across bays;
  temperature dependence does not (flat in LIS, strong in Narragansett).

## Phase 3 — The revised explanation (2026-09-01)

- **Hypothesis:** precision is bounded by event rarity.
- **Tests:** (a) make Narragansett's bloom definition as rare as LIS's (5% of
  days → chl > 52.5 µg/L sonde) and rerun; (b) examine LIS bloom frequency by
  year, with Narragansett as the untreated control.
- **Result — supported.** (a) At matched rarity precision falls to LIS level
  (0.14 single-year; 0.29–0.48 pooled). (b) LIS station-days > 10 µg/L:
  42–59% in 2009–2013 → 9% in 2014 → 3–11% every year since; Narragansett
  held at ~30–40% throughout. (Attribution to the nitrogen TMDL was withdrawn
  2026-09-05: see the satellite cross-check below.)
- **Secondary finding:** at matched rarity, dense sampling still gives
  7–8× lift [lower CI 5.3–6.0] vs the boat network's 2.7× — sensors improve
  *where to look*, not *how often alerts are right*.
- **Tuning search (360 configs, pre-registered):** the reference model is
  already the optimum at its bloom definition; a lift-maximising rule merely
  chases rarer labels.

**Satellite cross-check (2026-09-05).** The 2014 cliff in the lab record
could be a lab/method change, so it was tested against an instrument with no
2014 change: MODIS-Aqua L3m daily chlor_a, 4 km grid, 5×5-pixel patch (~20 km)
around each of the 50 stations (`data/modis_station_daily.csv`; script
`src/models/experiments/cliff_satellite_check.py`, criterion fixed in the
docstring before the run). *Criterion:* station-days with valid_frac ≥ 0.5;
threshold = 75th percentile of satellite chl over 2005–2013 pooled
(= 10.6 satellite units, n = 40,241); R = share(2015–2023) / share(2009–2013),
station-year clustered bootstrap (n = 2000, seed 42); step confirmed if
R < 0.5 with CI upper < 0.7, no step if CI lower > 0.8. *Result:* satellite
share above threshold 0.240 (2009–2013, n = 22,547) → 0.202 (2014, n = 4,225)
→ 0.260 (2015–2023, n = 41,212); **R = 1.08 [1.01, 1.16] — NO STEP.**
Sensitivity at an absolute 10: R = 1.08 [1.01, 1.16]. Annual mean satellite chl
7.4–11.1 throughout (8.9 pre, 9.3 post). The lab record over the same years:
0.469 (n = 1,877) → 0.092 (n = 401) → 0.060 (n = 3,361), R = 0.13 [0.10, 0.15];
restricted to the same station-days on which the satellite is valid (so not a
coverage artefact): lab 0.395 (n = 408) → 0.037 (n = 107) → 0.040 (n = 891),
R = 0.10 [0.07, 0.14], while the satellite on those very days is 0.348 → 0.421
→ 0.339, R = 0.97 [0.83, 1.16]. Matched-day 2×2: pre-2014 (n = 810) lab and
satellite exceed together 104 times vs 74 expected by chance, kappa 0.18; from
2014 on (n = 1,147) 16 vs 17 expected, kappa 0.00 — the weak day-level
agreement that existed vanishes exactly in 2014. Satellite valid-day fraction
is flat (0.21–0.28 per year; 0.23 in 2014), so the satellite population did
not change. *Meaning for the thesis:* an independent instrument sees no change
in LIS surface chlorophyll across 2014, so the cliff most likely lives in the
lab record (method, lab, or protocol change), not in the Sound. The "LIS is
bloom-rare because the TMDL worked" reading (Phase 3 result (b), §15 of the
fork) is therefore not supported and must be softened to: the *label* became
rare in 2014 for reasons not yet established, and that label rarity — whatever
its cause — is what caps precision. The rarity mechanism (Phase 3 (a), matched-
rarity test) stands; the ecological attribution does not. *Limits:* MODIS
chlor_a is biased in optically complex estuarine water and averages a 20 km
patch around a point sample, and even before 2014 it agreed with the lab only
weakly (kappa 0.18–0.25), so it is a coarse witness; but a 5–8× fall in
exceedance frequency would move a 20 km surface mean, and the satellite moved
by +8 % [+1, +16]. Only 24 % of station-days are satellite-valid (cloud, land
adjacency), so matched-day n is modest (43–155 per year). Written to
`data/cliff_satellite_check.csv` and `figures/fig_cliff_satellite.png`; the
draft email to CT DEEP / UConn (`notes/EMAIL_DRAFT_2014_CLIFF.md`) should now
ask specifically about a 2014 chlorophyll method change.

**The cliff is in the sensor, not the lab (2026-09-23).** CT DEEP replied on
2026-09-22: same sampling procedures, analysis methods and analytical laboratory
for 30+ years; they recall a region-wide change in chlorophyll and blooms
"around 2011". That ruled out the lab-change reading above, so the label source
was checked. `bloom_28d` is built from `Chlorophyll`, the CTD fluorometer, not
lab CHLA. Matched to surface lab CHLA on the same station-date
(`src/models/experiments/sensor_vs_lab_chl.py`, `data/sensor_vs_lab_chl.csv`),
sensor ÷ lab (median per year) is 2.08-4.79 in 1994-1999, 0.96-1.37 in
2003-2008, 1.77-3.22 in 2009-2013, 0.80-1.05 in 2016-2021 and 0.86-1.31 in
2022-2024. `Corrected_Chlorophyll` is 0.82-1.35 of lab in every year 1995-2021,
and empty for 2022-2024. Lab exceedance share (>10 µg/L) has no 2014 step: it is
0.10-0.23 in 2008-2011, 0.03-0.07 in 2012-2017 and 0.10-0.19 in 2018-2021, a
real temporary low that fits DEEP's recollection (lab n is low in 2012-2013).
*Meaning:* the 2014 label cliff is mostly a sensor scale change on top of a
smaller real dip. Training labels are inflated in 1994-1999 and 2009-2013; the
test years are near lab scale. The "cliff lives in the lab record" sentence
above is withdrawn. *Next:* the label rebuild is pre-registered in
`notes/LABEL_REBUILD_PREREG.md` (primary S1 = Corrected_Chlorophyll with a
documented gap fill; S1 becomes the headline whichever way it moves). All LIS
headline numbers stand as "original sensor-scale label" until it runs. The user
replied to the whole thread on 2026-09-23, asking whether the fluorometer or its
calibration changed around 2014 and whether the corrected field is the one to use;
the 2022-2024 gap question is held for the next reply.

**Label rebuilt on the lab scale (2026-09-23), per `notes/LABEL_REBUILD_PREREG.md`.**
`src/models/label_rebuild.py` rebuilds `Chlorophyll` and every chlorophyll-derived
feature for each series. Gate G1 passed: rebuilding the original sensor series (S0)
reproduced all 14 columns to 2e-13, and test AUC 0.8150 / precision 0.500 exactly.
The headline, S1 (DEEP's `Corrected_Chlorophyll`, gap-filled), gives test AUC
**0.804 [0.706, 0.878]**, base rate 6.3%, and at t=0.60 precision **0.316
[0.179, 0.424]**, recall 0.477, lift **5.03 [3.50, 6.88]**. The original label gave
0.815, 7.2%, 0.500, 0.486 and 6.99. The training positive rate falls from 22.7% to
5.5%. S2 (sensor divided by the yearly sensor/lab ratio) agrees: AUC 0.799, lift 4.05
[3.17, 5.32]. S3 (label from lab samples only, 161 test rows, 15 events): AUC 0.760
[0.52, 0.92]. All five pre-registered predictions were right. *Meaning:* ranking
skill survives the correction almost unchanged, but alert precision at the old 0.60
threshold drops from one in two to about one in three. Lift stays around 4-5×
because the base rate barely moves. The old precision was partly the model learning
the sensor's inflated scale. S1 now replaces S0 as the headline. Still to re-run on
S1: per-station operating points, the 21-day operating point, decision value, IEC
zero-shot, the rarity/overlap comparison, then KEY_NUMBERS, CLAUDE.md, the README,
the deck and the board.

**DEEP: use the lab data (2026-09-23, 11:52).** O'Brien-Clayton: "I would not use
the in situ fluorometer data at this point. Use the lab data." The CTD changed from a
SeaBird to a YSI EXO2 around 2009/2010, which fits sensor ÷ lab rising from 1.37 in
2008 to 1.84-2.25 in 2009-2010. A DEEP seasonal is comparing lab and in-situ values. So
Amendment A1 added S4 before it was run: chlorophyll features and label both from lab
surface CHLA only. Its result is test AUC **0.782 [0.595, 0.921]**, lift 5.0
[0.0, 9.9], on 161 rows with 15 events. ERDDAP lab data end 2024-06-04, so the test
covers only 2023 to May 2024. Both predictions were right (P6, P7). The interval is
wider than 0.30, so under the pre-registered rule S4 is "consistent with S1, not yet
measurable on its own". **Reporting from now on:** the label definition is the lab
(S4). The skill estimate is S1's, AUC 0.804 [0.706, 0.878] and lift 5.0 [3.5, 6.9], on
the full 2023-2025 test, with S4's interval beside it. S4 becomes final when DEEP
releases lab chlorophyll after June 2024. *Open design question:* lab chlorophyll
arrives months after sampling, so a real-time forecast can't use lab-based
chlorophyll features. The label should be lab. Real-time features will have to come
from sensors (LISICOS buoys for the prospective season), which is a separate question
from the one settled here. M. Lyman (DEEP) then confirmed that the corrected
chlorophyll "has been corrected against the lab data", which supports using S1 as the
full-coverage skill estimate. The one gap still open is 2022-2024, where the corrected
field is empty.

### Session addenda (2026-09-01, evening)
- Pre-registered 360-config tuning search: the reference model is the
  optimum at its bloom definition; lift-maximising selection chases rarity.
- Lift at LIS rarity over nine CV years: 7–8× vs 2.7× (dense sampling
  triples ranking skill; precision still rarity-capped).
- The 2014 cliff: LIS bloom-days 42–59% (2009–13) → 9% (2014) → 3–11%
  since; Narragansett flat — awaiting DEEP/UConn confirmation (email drafted).
- Probability 21 d before onset: LIS median 0.46, Narragansett 0.85; most
  of the 3-week signal is seasonal; Narragansett curve flat −21→−1.
- Calibration: LIS days scored ≥0.9 bloomed 58% of the time (7/12) — ranking
  monotonic, confidence inflated; report lift/ranking, not raw probabilities.
- Positioning vs CyFi / Mermer 2024 / NOAA: different question (forecast vs
  nowcast), stricter evaluation; never "better".

## Phase 4 — Does the model transfer? (2026-09-03)

**Question.** Is the bloom-precursor signature learned in Narragansett specific
to that bay, or general?

**Test 1, export (fork findings §19).** The frozen Narragansett model, applied
with no retraining to six other systems (Chesapeake Bay, six NERRS reserves,
UK shelf via Cefas SmartBuoys, Australian IMOS moorings, western Lake Erie,
SF Bay/Suisun Delta; 124k–144k station-days), after quantile-rescaling each
site's chlorophyll. IV: training site. DV: onset-only lift over always-alert,
AUC, station-year bootstrap CIs. Control: a model refit on each site's own
data, a chl>c rule, climatology. Result: exported model within CI of the local
refit at NERRS, UK, Australia and Lake Erie; clearly below it at Chesapeake and
SF Delta (both tidal-fresh). Raw transfer without rescaling never alerts
anywhere; rescaling is the whole trick. No method beats the simple rule by much
at any estuary; the model's edge is ranking (AUC 0.86 vs 0.73 in the UK).

**Test 2, import (§20).** A model trained on all six foreign sites, never shown
Narragansett, tested on Narragansett 2023: lift 1.64 [1.31, 2.10], AUC 0.76 vs
the local model's 2.00, 0.84. Transfer is asymmetric: exports well, does not
replace local data where blooms are strong.

**Test 3, water-type models (§22, pre-registered).** Hypothesis: models per
salinity regime (fresh / estuarine / marine) would fix the tidal-fresh
failures. Leave-one-site-out across 12 site×regime holdouts. Regime model
pooled lift 1.36 [1.32, 1.40] vs single Narragansett model 1.45 [1.37, 1.54]
vs all-sites-pooled 1.37. **Rejected.** Water type carries no information
beyond data volume; the run-up shape is universal, only its strength varies.

**Deliverable.** `predict_anywhere.py` + a 122 kB frozen model: anyone with
sub-daily chlorophyll (plus optional temp/sal/DO) can score their site.
Verified to reproduce the harness to three decimals (Lake Erie, SF Bay); does
not reproduce LIS (a 7-day daily-sonde model asked a 21-day question on
boat visits: AUC 0.77 vs 0.875 for the LIS-trained model).

**Also this session.** Narragansett's nitrogen load fell >50% after 2006 with
no exceedance cliff, which weakens the pure-TMDL reading of the LIS 2014 step;
reply drafted to the existing June thread with CT DEEP (O'Brien-Clayton) and
UConn (O'Donnell, Fake) asking whether 2014 was a method change.

## Phase 5 - Can the model go global on satellite data? (2026-09-04)

**Question.** Sub-daily sondes exist at a few hundred stations; satellites see
every coast daily. Does a satellite-chlorophyll-driven version of the model
keep useful 7-day onset skill?

**Design (pre-registered).** 89 sonde stations across seven systems; daily
satellite chlorophyll at each from four products (OLCI 300 m, gap-filled 2 km,
VIIRS 4 km, OLCI 4 km) plus 1 km SST; features from the satellite series only;
truth from the sondes. GO if satellite-refit onset lift >= 1.3 (CI > 1), beating
a satellite threshold rule, with >= 60% of onsets observable in the prior week.

**Result.** NO-GO at every resolution. Satellite refit lift 1.07-1.26 (CIs
above 1 but below the bar); climatology with no satellite data beats it
everywhere but the open shelf; the exported Narragansett model gets nothing
from satellite input (lift ~1.0). Satellite chlorophyll agrees weakly with the
sondes inside estuaries (Spearman 0.1-0.2; 0.4-0.8 offshore) and is visible
only 20-40% of days. Scored against its own label the satellite model reports
lift 1.75, i.e. it predicts itself, not the water: the key caveat for any
satellite HAB product validated without in-situ truth. Fork findings 23, fig 10.

**Also this session.** A pre-registered test of water-type ("regime") models
also failed (fork 22): regime lift 1.36 vs the single Narragansett model 1.45.
Coverage roadmap therefore stands at: exported Narragansett model at any site
with sub-daily sondes (predict_anywhere.py), local refit where >= 3 years of
local data exist, satellites for nowcast screening only.

## Phase 6 - How many sites can the model run on today? (2026-09-05)

**Question.** With satellites ruled out (Phase 5), coverage is the set of public
sub-daily chlorophyll sondes. How many exist, and does the exported model work
on them blind?

**Method.** Crawled the 48 public fixed-platform ERDDAP servers for datasets
with a chlorophyll variable and a measured cadence of 1-60 min; 325 found,
172 eligible fixed sondes (~1,400 station-years) after removing cruise,
glider and duplicate records. Ran the frozen Narragansett model on the 100
longest, scoring each with the section-19 protocol (own-site p75 label,
onset rows, one calibration slice for the threshold, station-year bootstrap).

**Result.** 87 new sites with predictions, 74 scored: median onset lift
1.58, 67 of 74 with a CI above 1.0, none below, median AUC 0.74.
Gulf of Mexico, Florida, Carolinas, California, Great Lakes, Alaska, British
Columbia, New Hampshire, Hawaii and six other Pacific islands. Same skill band
as the seven-network test. Fork findings 24, fig 11, data/registry/.

**Where the project now stands.** One model, trained on one bay, produces a
useful 7-day bloom-onset probability at every public sub-daily chlorophyll
sonde tested (80 systems), with skill set by each site's bloom
statistics rather than by the model; it cannot be driven by satellites.
Retraining on a site's own data was tested three ways (seven-network refits,
regime models, refits at the 11 best ERDDAP sites) and never beat the exported
model on marine or open-coast sites (median delta lift -0.06 at the ERDDAP
sites); it helps only in tidal-fresh and estuarine water with 3+ local years.

## Phase 7 - Is every result documented and reproducible? (2026-09-05)

**Question.** Could a stranger regenerate every number in both repos from the
notes, the scripts and the public data, without asking us anything?

**Method.** Audited both repos: git status, every findings section checked
for a named script, every referenced script checked for existence, every
data source checked for a fetch script or download URL, then the committed
`environment.yml` built from scratch into a fresh conda env and used to run
the pipeline.

**Result.** Code was fully committed and every data source had a documented
route, but four gaps would have stopped a stranger. (1) Fork findings §7-13
and §15 named no script; §15 (the 2014 cliff) was an inline calculation with
no script at all. (2) §6 and §17 cited scripts that live in this repo without
saying so. (3) The Cefas download is a manual, login-gated portal export and
the notes did not say what was requested. (4) `environment.yml` had never been
built and did not describe the environment that produced the results: it
pinned Python 3.11, pandas 3.0 and scikit-learn 1.8, while every run used
Python 3.13, pandas 2.3.3 and scikit-learn 1.7.2, and the released model
file unpickles with version warnings under 1.8.

**Fixes.** A Reproducibility map (section, script, inputs, output) now heads
the fork findings note; `src/models/experiments/bloom_rate_by_period.py`
regenerates the §15 table exactly; cross-repo references are labelled; §19
records the exact Cefas export request; `environment.yml` is re-pinned to
the real versions with torch/xgboost/shap moved to an optional block, and a
clean `conda env create` was verified to build and run inference, a model
fit and a warning-free load of the released model. The "hab env is broken"
note described one damaged local env, not the recipe.

**Not covered.** This repo's older LIS chapter was not re-audited beyond
confirming its evidence map; this repo's own `environment.yml` still lists
the deep-learning extras unpinned to the base env.

## Phase 8 - Does the skill hold prospectively? (built 2026-09-05; not started)

**Question.** Do forecasts issued before the outcome is known show the same
onset lift as the retrospective tests?

**Method (pre-registered, fork notes/PROSPECTIVE_PROTOCOL.md v1.0, amended 1.1 and 1.2 on 2026-09-06 before any issuance).** Frozen
model (sha 5c0f7a17), threshold 0.50, 20 live sonde stations in four groups
(LIS buoys WLIS/EXRX via UConn ERDDAP; two Kachemak Bay NERRS; six Maryland
Eyes on the Bay; ten IOOS ERDDAP sites chosen by a written rule), each
station's own p75 frozen from its history. Weekly issuance appended to a
tracked ledger; outcomes scored 9+ days later; station-week clustered
bootstrap; nothing reported below n >= 30 rows and 5 positives. Expected
bands: LIS buoys 1.1-2.5x (revised 2026-09-06 from a retrospective zero-shot
run of the frozen model on WLIS/EXRX: EXRX lift 1.9-2.5, AUC 0.81-0.84; WLIS
1.1-1.5, AUC 0.63, its fluorometer gain drifts 7x; fork findings 25.1),
NERRS/Chesapeake 1.3-2.0x, ERDDAP 1.5-2.5x. This is also the first time the
exported Narragansett model was applied to any LIS data; section 12 had only
retrained the recipe. Narragansett cannot be included: RIDEM has no live feed.

**Pre-start health check (2026-09-06).** 11 of 20 stations current. Dead at
source: both Kachemak NERRS sondes (no chlorophyll channel in 2026) and Indian
River Lagoon Banana River (sonde out since July). Caught before issuance:
Scripps pier's catalogued chlorophyll channel had read a constant zero flagged
QARTOD 4 since April; amendment 1.1 switches it to the pier's live ECO channel
(fresh site, p75 1.33 on 21 months, site threshold withdrawn), drops readings
flagged 4/9 at all ERDDAP sites, and documents the NERRS NaN-flag rule.
Amendment 1.2 revises the LIS-buoy expectation band (above). Dry run under
1.1: 10 ok, 3 stale, 4 warm-up, 3 feed_down.

**Positioning (notes/BENCHMARKS.md, 2026-09-06).** Eight operational HAB
products tabulated with sources: every one forecasts a species or toxin for
one region with a locally trained model, none states a base rate, one (Gulf
HAB-OFS) tests against chance. This work forecasts chlorophyll onset at any
sonde with no retraining and always shows base rate and a trivial baseline.
Framing stays "different question, stricter evaluation", never "better".

**Status.** Code built, protocol frozen at 1.2, dry-run verified; no forecast
issued. Formal start after the ISEF Form 1A adult-sponsor signature. Results
will be added here.

### Decision value (2026-09-06)

**Question.** What is the forecast worth in the unit a monitoring manager
budgets in: station-visits per confirmed bloom, under a fixed monthly budget?

**Method (`src/models/decision_value.py`).** Per bay, per calendar month of
the out-of-sample period, per budget V in {4, 8, 12} station-visits a month,
five ways of choosing which station-days to visit: calendar (even spacing,
fixed station rotation), random-uniform (= always-alert / base rate, 200
seeds), climatology (station x month bloom rate from training years only),
alert-directed top-V by out-of-sample probability within the month, and a
causal alert variant that spends budget day by day on rows above the shipped
t* (LIS 0.35, Narragansett 0.50; unspent budget stays unspent). A visit
confirms a bloom if the station-day's label is 1. Totals over months; 95 %
CI by resampling months (n = 2000, seed 42). Inputs: LIS = the locked
walk-forward frame (LR fit <= 2019, test 2023-25, 956 station-days, 48
blooms, 28 months); Narragansett = pooled rolling-origin out-of-fold GB
tier-A probabilities, onset rows only (chl <= 10), 2015-23 (15,118
station-days, 3,964 blooms, 108 months). Sanity check reproduced exactly:
at the full budget the alert precision equals the published lift x base rate
(LIS 0.132 = 2.63 x 0.050; Narragansett 2023 single split 0.696 = 2.00 x
0.347).

**Results at V = 8 (data/decision_value.csv, figures/fig_decision_value.png).**

| Strategy | LIS visits/bloom [95% CI] | LIS share caught | Narragansett visits/bloom [95% CI] | Narragansett share caught |
|---|---|---|---|---|
| Calendar (fixed rotation) | 15.4 [8.4, 44.0] | 0.29 | 3.81 [3.36, 4.41] | 0.057 |
| Random / always-alert | 18.7 [10.0, 51.9] | 0.24 | 3.51 [3.13, 4.00] | 0.062 |
| Climatology | 9.3 [5.3, 24.4] | 0.48 | 1.76 [1.58, 2.01] | 0.124 |
| Alert-directed (top-V per month) | 8.3 [4.9, 21.6] | 0.54 | 1.45 [1.34, 1.58] | 0.151 |
| Alert-directed (causal, t*) | 6.9 [3.5, 38.6] | 0.31 | 1.60 [1.45, 1.78] | 0.113 |

- LIS: With 8 station-visits a month, calendar sampling confirms 4.7 blooms
  per season (15.4 visits per bloom [8.4, 44.0]); alert-directed sampling
  confirms 8.7 (8.3 visits per bloom [4.9, 21.6]). Season = test year (3
  years, 2025 partial).
- Narragansett: With 8 station-visits a month, calendar sampling confirms
  25.2 blooms per season (3.8 visits per bloom [3.4, 4.4]); alert-directed
  sampling confirms 66.3 (1.4 visits per bloom [1.3, 1.6]). Season = test
  year (9 years).

**Conclusion.** The alert roughly halves the cost of a confirmed bloom in
LIS (1.9x, wide CI: 48 blooms) and cuts it 2.6x in Narragansett; the ordering
is the same at V = 4 and 12. Two caveats the lift numbers hid: (i) in LIS the
free climatology forecast gets most of the way there (9.3 visits per bloom
vs 8.3 for the alert; CIs overlap), so the model's marginal value over "use
the season" is small in the bloom-rare Sound and clear only in Narragansett
(1.76 vs 1.45, CIs disjoint); (ii) the causal t* variant spends only about
half its LIS budget (104 of 215 visits) because alerts are sparse, which
makes its visits-per-bloom look best while it catches fewer blooms (0.31 vs
0.54 of the season's). The earlier "2.5-3x better than the calendar" claim
is now replaced by these scripted numbers.

## Phase 9 - Would a neural network do better? (2026-09-10)

**Question.** The LIS chapter chose logistic regression because every neural and
tree alternative lost on 11k station-days and 74 test blooms. Narragansett has
4.5M raw 15-minute sonde rows, 42k labelled station-days and 380 bloom events,
and §11 showed skill falling when cadence is thinned below daily. Does (a) a
sequence model on the raw 15-minute record beat the daily-feature GB, and (b) a
pooled multi-site network with a learned site embedding close the
reverse-transfer gap (§20: pooled GB blind on Narragansett AUC 0.76 / lift 1.64
vs local 0.839 / 2.00)?

**Method (both pre-registered in fork findings §26-27 before any run; env
`hab-nn` = base pins + CPU torch, `environment-nn.yml`; `src/nn/`).** (a) A 2x2
on identical rows: input (23 daily tier-A features vs a 7-day window of 672
15-minute steps of chl, temperature, salinity, DO with missingness masks) x
model (GB vs neural), plus a hybrid; train <= 2020, val 2021-22, test 2023 onset
rows (1,697 after a >= 50 % window-coverage rule; base 0.347; 13 station-year
clusters); 5 seeds per network, 5-seed mean-probability ensemble as the primary
object; *paired* station-year clustered bootstrap (same resamples for every
model, verified to reproduce the fork's marginal `boot_ci` to 4 dp). GO if
paired dAUC(CNN - GB) CI excludes 0 and point >= +0.02. (b) The §20 pooled rows
(six foreign systems, 144k station-days, Narragansett never in training), MLP
with a 4-d site embedding and an UNK token used for the unseen bay, early
stopping on a 15 % foreign holdout, Narragansett 2021-22 for the threshold only.
GO if AUC >= 0.80 and paired dLift vs pooled GB CI excludes 0 and lift >= 1.82.

**Result (a): NO, and reliably so.** GB-daily 0.839, MLP-daily 0.829, CNN-15min
0.822, Hybrid 0.827 on the same 1,697 rows; paired dAUC(CNN - GB) -0.017
[-0.027, -0.002], 0 of 5 CNN seeds above GB, all four cells at lift 1.83-1.85
with overlapping CIs. The architecture control (MLP ~ GB) says model class is
not the lever; the hybrid (~ MLP) says the 15-minute structure adds nothing on
top of the daily aggregates. The daily-mean contract is the right resolution;
the 15-minute record's value is in building dense daily rows (§11-13), not in
feeding a sequence model. Fig 12.

**Result (b):** NO-GO on every bar, and in the wrong direction. Pooled GB
(re-run) 0.762 / lift 1.57; pooled MLP without embedding 0.719; with the UNK site
embedding 0.700 / lift 1.36, paired dLift vs pooled GB -0.21 [-0.45, -0.05]; mean-of-sites
embedding 0.723. The networks fit the *foreign* holdout as well as the GB (AUC
0.84-0.85) and transfer worse, so the §20 gap is not site identity that an
embedding can absorb; it is the weak-event problem named there (foreign "blooms"
are 75th-percentile wiggles), and a more flexible model learns those wiggles
without learning anything that carries to a strong-bloom bay. Fig 13.

**The ceiling as geometry (2026-09-11, fork findings §28; `src/models/lr_geometry.py`,
`figures/fig_lr_geometry.png`).** Because LR matches every other model, the decision
surface is close to a plane; projecting test-period onset rows onto the LR
log-odds axis draws the ceiling. Reading rule fixed first: if the class overlap
(OVL, integral of the smaller of the two class densities) differs by < 0.10
between bays while the bloom share differs ~7x, the precision gap is rarity.
Result: OVL 0.44 in LIS vs 0.52 in Narragansett (LIS separates *better*, AUC
0.855 vs 0.810), bloom share 0.036 vs 0.347, precision at t* 0.11 vs 0.64.
About three quarters of blooms in both bays sit inside the no-bloom central
band, which is why every model family lands at the same AUC. The first
number on the figure is the one to put beside the precision-vs-base-rate
result on the board.

**What this settles.** Across both bays and four model families (LR, GB, MLP,
1-D CNN) plus tree ensembles, the ranking skill of the precursor signature is
~0.82-0.84 AUC on onset rows and does not move with model class, input
resolution or training-set size. Rarity, not modelling, sets alert precision
(Phase 3). No further architecture work is planned; any new one needs its own
pre-registered section with the prior that it must overcome a reliably
negative ~0.02 rather than a null.

## Phase 10 - Does the LIS model hold on a second agency's record of the same water? (pre-registered 2026-09-14, before any run)

**Question.** The LIS model has only ever been scored on CT DEEP's own
cruises. The Interstate Environmental Commission (IEC) samples the western
Narrows with its own boat, crew and lab: 22 stations, weekly late June to
mid-September and monthly the rest of the year since 2018, lab chlorophyll a,
DO, temperature, salinity (EPA Water Quality Portal, org 31ISC2RS_WQX, records
to 2025-12-09; raw pull `data/iec_wqp_raw.csv`). Does the frozen LIS model
beat always-alert on IEC station-days with no retraining?

**Why this is a real test.** Same instrument class as training (bottle
chlorophyll from boat visits, so no sonde rescaling), but a different agency,
lab method (Standard Methods 10200 H and EPA 445.0 vs DEEP's), a bloom rate
about ten times LIS's (41% of IEC samples since 2018 exceed 10 ug/L), and
winter coverage DEEP never had. IEC stations A4, B3, C1 and C2 sit within
~1 km of DEEP stations of the same names, which allows a same-week
cross-lab check.

**Hypotheses.** H10a: onset-only lift of the frozen LIS model on IEC
2018-2025 has a station-year bootstrap CI entirely above 1.0. H10b: AUC on
the same rows is within 0.70-0.85. H10c: same-week DEEP vs IEC chlorophyll at
the four paired stations agree within a factor of two (median ratio in
0.5-2.0), so the 10 ug/L label means the same thing in both records.

**Method (fixed before running).** `src/transfer/iec_zero_shot.py`.
- Model: locked spec from `src/models/locked_pipeline.py` fit on LIS rows
  to 2019-12-31 with the 21-day, >10 ug/L label; scaler and imputation
  medians from LIS training only. IEC data never touches the fit.
- IEC rows: Sound stations only (Byram River sites BR1-BR10 dropped);
  surface = shallowest depth <= 1.5 m per station-date parsed from the
  activity ID; one row per station-date; 2018-01-01 to 2025-12-09 primary
  (year-round period); 1991-2017 summer-only rows reported as secondary.
- Features: the 35 locked features built by the LIS recipe (visit-based
  lags and rolling means, station-month climatology from the IEC record,
  three-nearest-station neighbour mean on the same survey date, monthly
  tidal anomalies by date, ERA5 gust by date). Nutrient lags and
  percent_saturation are unavailable for 2018+ and take the LIS training
  median, as half of LIS rows already do.
- Label: any chlorophyll > 10 ug/L within 21 days after the visit at the
  same station; right-censored windows excluded (locked rule).
- Scoring: onset rows (today <= 10 ug/L). Two operating points: the LIS
  global threshold 0.60, and a threshold chosen on IEC 2018-2019 rows for
  POD >= 0.6 then applied to 2020-2025. Metrics: precision, POD, lift =
  precision / base rate, AUC; 2000-draw station-year clustered bootstrap
  (seed 42). Baselines: always-alert, station-month climatology, chl > c
  rule with c chosen on 2018-2019. Secondary label: own-station p75.
- Cross-lab check: DEEP and IEC chlorophyll at A4/B3/C1/C2 paired within
  +/-3 days, 2018-2025; report n, median ratio, Spearman r.

**Expected bands (written before the run).** Base rate on onset rows
0.30-0.55, so the ceiling on lift is about 2-3. Expect lift 1.2-1.8, AUC
0.70-0.85, precision 0.45-0.70. A lift CI including 1.0 rejects H10a. If
H10c fails (ratio outside 0.5-2.0) the p75 label becomes primary and the
10 ug/L result is reported as method-confounded.

**What it is not.** Not a prospective test (IEC posts with a lag of
months); not a refit (a fourth model would add nothing to the claim). It
is the outside-agency confirmation (workstream C1) using data already
public.

**Result (run 2026-09-14, same day, `src/transfer/iec_zero_shot.py`;
`data/iec_zero_shot_results.csv`, `figures/fig_iec_zero_shot.png`).**
5,204 IEC station-days, 34 stations, 1991-2025. Primary rows: 949 onset
station-days 2020-2025, base rate 0.13 (below the 0.30-0.55 band: the
monthly winter cadence leaves most 21-day windows with one or no visit, so
onset-row positives are rarer than the 41% sample share suggested).

| Model (2020-2025 onset rows, h21, >10 ug/L) | Prec | POD | Lift [95% CI] | AUC [CI] |
|---|---|---|---|---|
| LIS frozen, t=0.60 (LIS global threshold) | 0.24 | 0.62 | **1.84 [1.59, 2.11]** | 0.73 [0.68, 0.78] |
| LIS frozen, t=0.82 (chosen on IEC 2018-19 for POD>=0.6) | 0.34 | 0.44 | 2.53 [2.08, 3.00] | same |
| Station-month climatology (2018-19) | 0.20 | 0.80 | 1.50 [1.37, 1.65] | 0.73 [0.68, 0.78] |
| chl > 3 rule (2018-19) | 0.17 | 0.90 | 1.26 [1.17, 1.35] | 0.61 |
| Always-alert | 0.13 | 1.00 | 1.00 | 0.50 |

- **H10a holds**: lift CI entirely above 1.0 at both thresholds; lift 1.84 is
  at the top of the pre-registered 1.2-1.8 band. Precision 0.24 is below
  the 0.45-0.70 band only because the base rate came in at 0.13, not 0.4.
- **H10b holds**: AUC 0.73 [0.68, 0.78], inside 0.70-0.85. But
  station-month climatology reaches the same AUC (0.73); the model's edge
  over climatology is in lift at a fixed operating point (1.84 vs 1.50, CIs
  touching; 2.53 vs 1.50 at t*), not in ranking. Same pattern as the
  Narragansett trivial-rule comparison (fork findings 8): the model wins,
  modestly.
- Secondary: own-station p75 label lift 1.73 [1.52, 1.94], AUC 0.72;
  1991-2017 summer-only rows lift 1.20 [1.15, 1.25], AUC 0.71 (weekly
  summer cadence, higher base rate 0.27, so less headroom). All rows
  2020-2025 (not onset-only) AUC 0.79 [0.76, 0.81]. 13 stations have >=30
  onset rows; every per-station lift point estimate is above 1 (1.4-3.2),
  five with CI above 1.
- **H10c holds on the ratio, weakly on agreement**: 60 same-station pairs
  within +/-3 days 2018-2025, median IEC/DEEP ratio 1.25 [IQR 0.75-1.95],
  Spearman r = 0.38, bloom/no-bloom agreement 0.68. Across all 243 pairs
  since 1991, r = 0.07. Two labs sampling the same station in the same
  week agree on the 10 ug/L label about two times in three. The label is
  noisy at the visit level; the model's skill survives that noise.

**The 2014 step, second witness (unplanned, run after the above).** Summer
(Jun-Sep) share of samples > 10 ug/L at the four paired stations:

| Network, paired A4/B3/C1/C2 | 2005-2013 | 2014-2025 |
|---|---|---|
| CT DEEP | 0.50 (n=271) | **0.07** (n=344) |
| IEC | 0.66 (n=107) | **0.47** (n=136) |

DEEP's paired-station share is 0.00 in each of 2014-2017; IEC's is 0.55,
0.50, 1.00, 0.25 in the same years, at the same stations. All-station
figures: DEEP 0.44 -> 0.04, IEC 0.61 -> 0.54. An independent agency's lab
saw no cliff in the same water. With the MODIS null (Phase 3), the 2014
step now has two witnesses against it being ecology. This is the
strongest evidence yet that the LIS label rarity after 2014 is a property
of the DEEP chlorophyll record.

**Conclusion of Phase 10.** The LIS precursor signature is a property of
the western Sound, not of DEEP's dataset: it transfers to a second
agency's record with no retraining (lift 1.84 [1.59, 2.11]). Its margin
over climatology is real but modest. And the same record shows the 2014
cliff is not in the water.


## Phase 11 - Can the forecast trigger a mitigation that leaves nothing on the bottom? (designed 2026-09-15; bench work not started)

**Question.** Aeration cannot prevent a bloom (notes/AERATION_RESEARCH.md); the
only in-water mitigation with an operational record is modified-clay
flocculation, which sinks the floc onto the bed (notes/CLAY_FLOCCULATION_RESEARCH.md).
No study has combined clay flocculation with retrieval of the floc in seawater,
and none has dosed on a forecast (notes/CLAY_RETRIEVAL_RESEARCH.md s9). Does a
magnetite-kaolin-PAC clay, dosed when a test ledger row alerts (bench: ledger-triggered,
controller-timed, student-mixed), remove a
Long Island Sound diatom at pre-bloom density and come back out on a magnet?

**How the design was reached.** A builder agent drafted the device; three
independent reviewers critiqued v1, v2 and v3 in turn (notes/device_reviews/);
a scientist verifier then graded every component WORKS / PLAUSIBLE /
UNSUPPORTED (notes/DEVICE_VERIFICATION.md). Frozen design: notes/DEVICE_PROTOTYPE.md
(v7-final; a second loop of three reviewers and a freeze audit,
notes/device_reviews/review4-6, took v4 to v7; frozen Fri Nov 6, 2026, or
Nov 13 if the culture arrives after Oct 8). Decisions that survived review: no flotation (the one brackish DAF trial
fell to 21% chlorophyll removal at 19-20 ppt); a physical blend of magnetite
pigment, EPK kaolin and PAC powder rather than co-precipitated magnetic clay
(same material once PAC bridges it in seawater, no hot iron chemistry for a
school lab); capture by settling first, then a floor raster of square-tube
NdFeB stacks with release after every pass; a minimum viable January program
with recovery fraction as the headline number and the two-density dose study
deferred to summer 2027. The field concept is documented but marked "concept,
not performed"; the verifier rates it UNSUPPORTED (tidal timing inconsistent,
bed shear 0.06-0.09 Pa resuspends fresh PAC floc, natural magnetite in LIS
sediment confounds a bed survey, permits are agency-led).

**Pre-registered hypotheses (bench, MVP; bands written before any run).**
- **H11a (removal).** Magnetic PAC-kaolin at 0.2 g/L (product basis; stock route S or D
  per the Oct 30 amendment) removes *Skeletonema marinoi* (CCMP1332, Milford CT isolate) at
  1e4 cells/mL by 70-95% at 5 h (control-normalised Sedgewick-Rafter counts,
  n = 3 batches), and within +/-15 points of plain PAC-kaolin at the same dose.
  Pass: mean RE >= 70% with the n = 3 CI lower bound > 50% and
  |magnetic - plain| <= 15 points. Mean >= 70% with a lower bound of 40-50%
  reads "consistent, underpowered", not failed (verifier risk 3); the
  interval is a t-interval on three batch REs (t = 4.30), and "consistent,
  underpowered" is the pre-registered likely reading. The stock route (S or
  D) is logged as a dated amendment on Fri Oct 30 from the six pilot counts,
  before batch 1; decision rule: a route that wins by > 15 RE points (mean of
  two) becomes the recipe, a tie within 15 points keeps route S, route P
  enters the pilot only if its week-1 floc photo beats S and D. Below 50%:
  rerun at 0.6 g/L and report both.
- **H11b (recovery).** The settle-raster-column sequence recovers 75-95% of
  dosed magnetite-equivalent by pull test on homogenised pad aliquots and >= 70% of total dry product in the winning route's
  blank, 60-90% / 50-85% with culture, and <= 10% of plain PAC-kaolin
  (one plain tank blank, n = 1, reported as a description with its ~2-3%
  solids floor). Pass: mean magnetite-equivalent >= 70% over
  n = 3 tank runs, each >= 60%; total >= 50%; plain <= 10%. A blank below
  70/80 is a design failure (gate), not a hypothesis failure.
- **H11c (dose-density), MVP version.** RE at 1e4 cells/mL rises
  monotonically by ordered means over 0.05, 0.1, 0.2 g/L (three means with
  t-intervals); D90 by log-linear interpolation only when bracketed by two
  adjacent means, otherwise reported as "> 0.2 g/L" or "< 0.05 g/L". Pass:
  ordered means non-decreasing and, when bracketed, D90 in 0.05-0.2 g/L; an
  unbracketed D90 reads "not testable". Full version
  (summer 2027): D90(1e5)/D90(1e4) in 1.5-4x, bootstrap CI lower bound > 1.0.

**Two edits the verifier requires before the build (adopted).** (1) Week-1
clay-only trial of routes S, D and P (floc photo, detachment test): the two
best sources on PAC-clay in seawater (Yu et al. 2016; EPA/WHOI ECOHAB report)
show that ageing and storing the stock in seawater costs floc size and dose;
culture pilot on the first Tue-Thu after carboy B reaches 1e5 cells/mL
(target Wed Oct 28) with the routes that passed the Oct 23 recovery gate,
n = 2, six jars in two blocked rig rounds; decision Fri Oct 30 by the rule in
H11a. (2) Tank runs take DO spot reads at T30 and T111 (protocol
control), four 750 nm floor samples in the long-wall margin, T30 and T51
counts for a within-tank resuspension index (+/-20%), and every recovery miss
is attributed by tube rinse, floor rinse and a 5 L supernatant pull test with
its 0.5% detection floor, so raster resuspension is a measured quantity.

**What is not claimed.** Not bloom prevention (a p75 exceedance is a
top-quartile day, not a harmful bloom, and pre-emption is only coherent in an
enclosed volume); not nutrient removal (one 600 m3 treatment would export
~0.1 kg N while adding ~3 kg Al and ~32 kg Fe); not "no habitat impact"
(dissolved Al from PAC is likely above the 24 ug/L marine guideline for hours
regardless of retrieval, and the documented clay harm to clams is
resuspension, which a raster causes); not field-ready. Board sentences and
the reject list are in DEVICE_PROTOTYPE.md s9 with the verifier's two
qualifications (split jar removal from the tank trigger; "no HAB clay study",
not "no study"), and reviewer 5's three ("ledger-triggered (test row)",
"magnetite-equivalent by pull test", "were not tested").

**Gates.** Forms 1/1A/1B/3 signed by Sep 25; week-1 chemistry by Oct 9;
route blanks S (Oct 14) and D (Oct 15) and a plain blank (Oct 20), each route
passing or failing on its own blank Oct 23, retry Oct 30 on S with a rebuilt
8-tube frame; culture >= 5e5 cells/mL in 20 L by Nov 6; freeze Nov 6 (Nov 13
if the culture arrives after Oct 8); counting checkpoint Nov 20; controller
gate Dec 4 (pump and paddle from a test row, student mixing); three tank runs
by Dec 15. Fallbacks and what the board shows at each
failure: DEVICE_PROTOTYPE.md s11.

**Addendum 2026-09-16.** Capture before settling (pumping the vessel through a
magnetic trap during the slow mix) is the mechanism that separates magnetic
clay from plain clay in tidal water; it is deferred to summer 2027 as a
pre-registered comparison against the January settle-and-raster result
(DEVICE_PROTOTYPE.md s12a). Not in the January build.

**Predicted before measurement (2026-09-16; notes/DEVICE_SIMULATION.md).**
Magpylib field model reproduces the reviewers' hand numbers (single block 0.32 T
at 3.2 mm, stack repulsion 116 N) and shows the six-stack array gives 0.22 T at
the capture surface. A Smoluchowski floc model says floc size at 15 min depends
almost entirely on collision efficiency (D50 2-22 um at low efficiency, ~140 um
at full charge neutralisation or with a pre-aggregated stock). A Monte-Carlo
raster model predicts magnetite-equivalent floor-raster recovery of about
94-96% if flocculation is good and 54-72% if poor, insensitive to rake speed
(0.5-2 cm/s), skid height (0-6 mm) and Ms (60-80); the no-magnetite control
recovers 0%. These are upper bounds: pad stranding, resuspension and floc
stripping are not modelled. H11b bands unchanged. The model also shows the
8-tube 30 mm contingency frame does not fit 1-1/4 in tubes on a 250 mm floor.

**Amendment A1, 2026-09-16 (before any bench work; DEVICE_PROTOTYPE.md A1).**
Settings changed to the simulation optimum: magnetite 20% of the dry blend
(was 37.5%); slow mix G ~60 for 10 min and settle 10 min (were G ~30, 15 and
15); 5 magnet stacks (was 6); 2 floor passes with the frame against each long
wall (was 3 at 11/41/11 mm) at 2 cm/s (was 1) and one column cycle; the
recovery-gate contingency is a diagnosis (column count, floc photo, tube
rinse) instead of an 8-tube frame, which does not fit the floor. Run clock
becomes T1-T11 paddle, T11-T21 settle, T21-T33 raster and column, resuspension
index T33/T20. H11c's MVP dose screen adds 0.4 g/L (12 jars). H11a, H11b and
H11c bands do not move. Predicted recovery under A1: ~95%
magnetite-equivalent, upper bound.

**Analysis frozen before the data exists (2026-09-18/19).** The whole of the
Phase 11 analysis is now code, written and verified months before the first
measurement: `src/lab/lab_schema.py` (the s9 row contract and a validator),
`src/lab/synth_lab_data.py` (a synthetic season generated under a known planted
truth) and `src/lab/analyze_lab.py` (control-corrected removal, the t-interval at
t = 4.30, H11a including the "consistent, underpowered" reading, recovery and the
H11b three-part test, the magnetite mass balance with the s7 8 mg / 20 mg floors,
the resuspension index, H11c with D90 interpolated only when bracketed, and
counter agreement by MARD and Lin's concordance). No band was touched.

Verified on four synthetic seasons whose truth was planted in advance, so the
code's answers can be scored rather than trusted: with a planted removal of 92.0%
and recovery of 88.0% it returned 92.1% and 91.9%; the `underpowered` scenario
(seeds 99 and 101) returned "consistent, underpowered"; the `fail` scenario
returned the pre-registered rerun at 0.6 g/L; the `unbracketed` scenario refused
to report a D90 and printed "not testable". Six deliberately corrupted rows each
drew a readable complaint from the validator and nothing raised. Figure:
`figures/lab/fig_lab_results.png`. What this buys is narrow and worth stating
plainly: in December the numbers go into a pipeline fixed before anyone knew what
they would be, so no choice in the analysis can be made to flatter the result.

**Result.** _pending_

### Session log, 2026-09-18/19 (desk work, no lab access)

UConn replied: J. O'Donnell is interested in the work and offered a slot to
present to his group once he is back from a conference; availability was sent the
same day. A 15-slide talk and a spoken script were built for it
(`notes/TALK_UCONN.md`), with two constraints carried from the thread: results
stop at 2025, and nothing is claimed about 2026 observations until his student
publishes.

Two errors in the record were found and fixed while building it. First, the
research plan that attaches to ISEF Form 1A still claimed "no hazardous
materials" and "no fieldwork", which stopped being true when the bench
workstream was added; sections B, C, D, E, F and G were rewritten so a sponsor
asked to sign Form 3 reads an accurate hazard list
(`notes/ISEF_RESEARCH_PLAN.md`). Second, `notes/COMPETITION_CHECKLIST.md` said
Form 3 was "not needed - no hazards" and dated the forms to Oct 5; both are
corrected, and the Sep 25 hard stop is now a row of its own. Also written:
`notes/SPONSOR_ASK.md` (the sponsor is still unnamed and is the critical path)
and `notes/ORDER_LIST.md`.

One inconsistency is recorded and not resolved: the repository carries two
operating points for the same model, a 28-day label at threshold 0.60 with
precision 0.500, and a 21-day label at t* = 0.35 with precision 0.125 and POD
0.875. Both are correct for their own label and neither file mentions the other.
The talk uses the first and states the second out loud. Which one is the headline
needs deciding before February.

## Conclusion (current)

Blooms can be forecast; the model's ranking skill is genuine in both bays.
Alert precision is set by bloom rarity — not model class, features, training
data volume, or sampling frequency — and the LIS bloom *label* became rare
in 2014. Whether that is ecology or a change in the lab chlorophyll record is
unresolved: MODIS satellite chlorophyll over the same stations shows no 2014
step (ratio 1.08 [1.01, 1.16]) while the lab record falls to 0.13 [0.10,
0.15], and lab–satellite agreement drops to zero from 2014, so the evidence
currently points to the record, not the Sound (Phase 3 cross-check; CT DEEP
asked 2026-09-05; confirmed by the IEC record in Phase 10: an independent lab at
the same four stations shows 0.66 -> 0.47, not 0.50 -> 0.07). In a bloom-rare system the forecast's value
is triage (at 8 station-visits a month one confirmed bloom costs 15.4 calendar
visits vs 8.3 alert-directed in LIS, 3.8 vs 1.4 in Narragansett;
src/models/decision_value.py), and
continuous sensors would roughly triple that.

## Variables that turned out not to matter (a finding in itself)

Model class (LR ≈ GB in LIS; GB slightly ahead in Narragansett; a 15-minute
sequence CNN and a tabular MLP both at or slightly below GB, Phase 9), input
resolution finer than daily (Phase 9), extra
features (13 LIS attempts; stratification, pH, diel DO, chl acceleration in
Narragansett), more training data (14k → 34k station-days: no change),
temperature in LIS.

## Limitations

Sonde fluorescence reads ~1.3–1.6× above lab chlorophyll (n=734 pairs; lab 10
≈ sonde 13–16); LIS buoy tests rest on two buoys (§12: 78 positives; zero-shot
§25.1: WLIS transfers weakly, AUC 0.63, with a fluorometer gain that drifts 7×);
the 2014 step is now more likely a lab-record change than ecology and awaits
DEEP/UConn's answer (email drafted, to be sent 2026-09-08); the LIS decision-value
numbers rest on 48 blooms and carry wide CIs; nothing has yet been tested
prospectively; all findings are correlational — low DO marks bloom-prone water,
it does not cause blooms.

## Where the evidence lives

Parent repo: README.md Findings, notes/KEY_NUMBERS.md, notes/BENCHMARKS.md (incl.
operational-products table), src/models/decision_value.py + figures/fig_decision_value.png,
src/models/lr_geometry.py + figures/fig_lr_geometry.png + data/lr_geometry_*.csv (Phase 9 geometry),
src/models/experiments/cliff_satellite_check.py + figures/fig_cliff_satellite.png,
notes/ISEF_RESEARCH_PLAN.md, notes/COMPETITION_CHECKLIST.md.
Fork (../hab-bloom-predictor-narragansett): notes/NARRAGANSETT_FINDINGS.md
§1–28, figures/nar_fig1–14, predict_anywhere.py + release/, data/registry/, src/nn/ + environment-nn.yml (Phase 9),
notes/PROSPECTIVE_PROTOCOL.md + src/deploy/prospective_*.py + data/prospective/ (ledger, tracked). Every number has a script under src/;
the **Reproducibility map** at the top of the fork's findings note lists, per section, the script, inputs and
output (added 2026-09-05 after an audit found §7–13 and §15 named none; §15 was an inline calculation and now has
`src/models/experiments/bloom_rate_by_period.py`, which reproduces the 2014-cliff table exactly). Cross-repo
dependencies: fork §12 and §17 read this repo's `src/models/experiments/{lis_buoy_recipe,prob_before_onset_lis}.py`
outputs; fork §15 reads this repo's `data/hab_features_tidal.csv`. Cefas is the one manual download.

**Downstream results on the rebuilt label (2026-09-23; `notes/LABEL_REBUILD_PREREG.md`
§14).**
- **21-day operating point** (t*=0.35): precision 0.117, POD 0.744, lift 2.59, against
  0.132, 0.917 and 2.63 on the old label. Still clearly better than always-alert. Against
  climatology it was not tested fairly: climatology's own threshold degenerated to t=0.
- **Decision value** (8 visits/month): 17.8 → 9.7 visits per confirmed bloom, against
  15.4 → 8.3.
- **Per-station:** no western station clears P>0.5 with R>0.4. The C1 precision of 1.000
  no longer holds.
- **IEC transfer:** lift 1.57 [1.41, 1.75], against 1.84; AUC 0.707, against 0.732.
  Better than chance, level with climatology.
- **Rarity/overlap flips.** The Sound's OVL is now 0.620 against Narragansett's 0.516
  (it was 0.445). Lower precision in the Sound is rarity **and** weaker separation, so
  "not skill" is withdrawn.

*Overall:* the Sound model is a modest forecaster. Its ranking survives (AUC about 0.80)
and it roughly halves the visits per bloom. Its alerts are right about one time in three
at 0.60, and it does not beat a calendar climatology on another agency's data. That is
what the evidence supports. Narragansett and the 74-site transfer are unaffected.

**Migration completed (2026-09-23, later).** S1 is now the default input for every locked
script. `HAB_FEATURES_CSV=data/hab_features_tidal.csv` reproduces the sensor label, and the old
outputs are archived in `data/archive_sensor_label/`. Gate: the default run gives 0.8036, the
env-var run 0.8150.

Re-runs on S1:
- Pooled 21-day rolling CV: AUC 0.772 (was 0.852).
- Frozen t*=0.35: POD 0.791, precision 0.114. The pre-registered POD ≥ 0.8 rule now selects
  t*=0.20. **Open decision for the user**; deploy keeps 0.35.
- Basin search: validation lift 2.05× at the 70.5th percentile of the null. Still noise, conclusion
  unchanged.
- Point of no return: analogue risk peak 0.42. Still no point of no return.
- The fork's matched-rarity tests are unchanged on the Narragansett side. At 5% rarity precision is
  0.09-0.14, and the Sound's 0.117 sits inside.
- IEC's chlorophyll method switched from 10200H to EPA 445.0 in 2017-18, before the 2020-25
  transfer window, so no re-score was needed.
- Live-season rule written down (prereg §15): lab label, sensor inputs, prospective buoy scoring
  unchanged, and a secondary lab cross-check.

All documents in both repos now take current LIS numbers from `notes/S1_NUMBERS_SHEET.md`. History
files keep their old numbers under a dated pointer.

**Mitigation pivot and Layer 1 (2026-09-24).** The counselor rejected clay flocculation: it changes
the environment and can't be retrieved in open water. The literature review in
`notes/HAB_MITIGATION_LITERATURE.md` has 245 agent-read entries and a 3,352-paper citation
snowball. From it, the forecast-triggered process is specified for five low-impact methods in
`notes/mitigation/` (a shared on/off control loop, rules fixed before any run); bubbles and
seaweed are the leads. Layer 1 (`src/models/control_loop_sim.py`) replayed the loop on untreated
history:
- **Narragansett, daily sensors:** the loop was ON at 79-81% of bloom starts (a median 3 days
  early). 24-29% of episodes were false alarms, at 13 (bubbles) to 19 (seaweed) treatment-days per
  bloom caught. Its ON days were better placed than random (39.7% vs 33.7% [33.1, 34.2] pre-bloom).
- **Long Island Sound, boat visits every ~17 days:** ON at 27-35% of bloom starts, with 91-93%
  false-alarm episodes, and no better than random (6.4% vs 5.5% [4.3, 6.7]).
- **Conclusion:** the loop needs a continuous sensor at the site. The off rule can't be judged
  on untreated water (79-90% of episodes hit the time cap). Details in
  `notes/mitigation/LAYER1_RESULTS.md`.

**Evidence reviews, scoreboard and full texts (2026-09-25/26).**
- **Evidence reviews:** each of the five loop methods now has 20-27 sourced papers in `notes/mitigation/evidence/`, and `notes/mitigation/EXECUTION_PLAN.md` sets out five short screens followed by two full loop runs.
- **Scoreboard:** 256 papers across 15 methods (`notes/mitigation/scores/`, built by `src/lit/build_scoreboard.py`). Separate agents rated each paper 1-5 on reproducibility, effectiveness, cost, time and environment. A method's score uses only papers that test it on algae; safety, mechanism, feeding and misfiled papers are listed but not counted.
  - Scorer agreement on 6 shared papers: 87% of scores within 1 point.
  - A Crossref check found 20 of 20 DOIs real.
- **Full texts:** 197 of 256 papers were read in full (open-access copies, plus paywalled papers through Columbia Libraries), merged by `src/lit/merge_fulltext.py` and re-scored.
- **Ranking:** unchanged at the top. Seaweed 3.55, peroxide 3.25 (equal weights); phosphorus inactivation is last at 1.63.
- **What the full texts corrected:**
  - Abstracts often overstated effects: some reported the share remaining as if it were the reduction, and some headline "%" figures came from highlights or single tanks.
  - Sung & Gobler 2026 (bubbles): 21-58% and 34-63% cuts at 300 mL/min into 500 mL (0.6 L/min per L). The bubble screen now copies that setup.
  - Seaweed stimulated the target alga at low dose in one study.
  - Curcumin's 99% kill fell to 47% when the trial was repeated.
