# The project as one experiment — scientific-method summary

**Update this file at the end of every work session.** It is the single place
where the project's question, hypotheses, variables, controls, results, and
conclusion are kept current. Last updated: 2026-09-05 (end of session).

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
  42–59% in 2009–2013 → 9% in 2014 → 3–11% every year since, coinciding with
  the nitrogen TMDL being met; Narragansett held at ~30–40% throughout.
- **Secondary finding:** at matched rarity, dense sampling still gives
  7–8× lift [lower CI 5.3–6.0] vs the boat network's 2.7× — sensors improve
  *where to look*, not *how often alerts are right*.
- **Tuning search (360 configs, pre-registered):** the reference model is
  already the optimum at its bloom definition; a lift-maximising rule merely
  chases rarer labels.

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

## Conclusion (current)

Blooms can be forecast; the model's ranking skill is genuine in both bays.
Alert precision is set by bloom rarity — not model class, features, training
data volume, or sampling frequency — and LIS blooms became rare in 2014
because pollution control worked. In a bloom-rare system the forecast's value
is triage (2.5–3× better than the calendar at choosing where to sample), and
continuous sensors would roughly triple that.

## Variables that turned out not to matter (a finding in itself)

Model class (LR ≈ GB in LIS; GB slightly ahead in Narragansett), extra
features (13 LIS attempts; stratification, pH, diel DO, chl acceleration in
Narragansett), more training data (14k → 34k station-days: no change),
temperature in LIS.

## Limitations

Sonde fluorescence reads ~1.3–1.6× above lab chlorophyll (n=734 pairs; lab 10
≈ sonde 13–16); LIS buoy test rests on two buoys and 78 positives; the 2014
step change awaits confirmation from DEEP/UConn that it is not a method
change (see EMAIL_DRAFT_2014_CLIFF.md); all findings are correlational — low
DO marks bloom-prone water, it does not cause blooms.

## Where the evidence lives

Parent repo: README.md Findings, notes/KEY_NUMBERS.md, notes/BENCHMARKS.md.
Fork (../hab-bloom-predictor-narragansett): notes/NARRAGANSETT_FINDINGS.md
§1–24, figures/nar_fig1–11, predict_anywhere.py + release/, data/registry/. Every number has a script under src/.
