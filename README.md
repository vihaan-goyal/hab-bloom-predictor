# HAB Bloom Predictor

**Predictability and its limits: a 21-day early warning system for chlorophyll exceedances in Long Island Sound**

Vihaan Goyal, Westhill High School, Stamford, Connecticut

---

## What this project shows

A regularized logistic regression forecasts chlorophyll-a exceedances (>10 ug/L within 21 days of a station visit) across Long Island Sound with strong ranking skill (pooled out-of-sample AUC 0.852), but alert precision is capped near 0.13 regardless of model class, feature set, threshold, era, or spatial alerting policy. Thirteen pre-registered improvement attempts were rejected. The central finding is that this precision ceiling is mechanistic, not a modeling failure:

1. **Rarity.** Chlorophyll exceedances in the DEEP lab record fall from 42–59% of station-days (2009–2013) to 3–11% from 2014 on, and rare events cap precision regardless of model. Whether the 2014 step is ecological (nitrogen TMDL) or a change in the lab record is unresolved: MODIS satellite chlorophyll over the same stations shows no step, and lab–satellite agreement drops to zero from 2014 (`src/models/experiments/cliff_satellite_check.py`, `figures/fig_cliff_satellite.png`). CT DEEP has been asked.
2. **Sampling.** The median gap between chlorophyll measurements is 21 days, equal to the forecast horizon. 48% of inter-sample gaps exceed the horizon, so many predicted events cannot even be verified.

Across eras and label definitions the system delivers a roughly constant 2.5 to 3.4x precision lift over the base rate, and no intervention has moved that multiplier.

## The early warning system

Operating point frozen by a pre-registered rule (highest threshold with out-of-sample 2020 to 2022 POD >= 0.8), evaluated once on out-of-sample 2023 to 2025:

| Metric | Value | 95% CI (clustered bootstrap) |
|---|---|---|
| POD (recall) | 0.875 (42 of 48 events) | [0.750, 0.962] |
| FAR (1 - precision) | 0.875 | [0.828, 0.923] |
| Precision | 0.125 (2.7x over 4.6% base rate) | [0.077, 0.172] |
| CSI | 0.122 | [0.075, 0.169] |

Alert threshold t* = 0.35. Selection-to-test transfer was near exact (POD 0.864 -> 0.875). At the 21 recurring-bloom stations (defined on pre-test data), detection is 91% at precision 0.137. A station-gated alert policy was tested and rejected: false alarms arise at bloom-prone stations during non-bloom periods, so the ceiling is temporal, not spatial. A sustained-exceedance secondary label raises the lift to 3.4x but leaves precision near 0.10.

The framing rationale: a missed bloom carries ecological and shellfish-industry costs, while a false alarm prompts a water sample at a station where, half the time, no sample would otherwise occur in the window.

## Locked pipeline

- Model: LogisticRegression, C=0.05, L2, balanced class weights, 35 features
- Label: any chlorophyll-a exceedance >10 ug/L within 21 days of a station visit
- Evaluation: rolling-origin cross-validation (train <= T-2, test = T), folds 2015 to 2025, station-year clustered bootstrap for all interval claims
- Canonical data file: `data/hab_features_tidal.csv` (plus in-script merges of percent saturation and gust features)
- Dominant signal: chlorophyll history (~42% grouped feature importance)

Complexity does not help: XGBoost cost 33 points of precision against this baseline. Nutrient forward-fill, ERA5 wind, Kd490, neighbor bloom probability, station-month rates, and chlorophyll acceleration were all tested and rejected.

## Key ecological context

- Long-term chlorophyll decline since 1993 in the lab record, with a sharp 2014 step that the satellite record does not show (cause under inquiry with CT DEEP; do not cite as TMDL effect)
- Biomass-bloom decoupling at western stations (A4, B3) after 2014, with near-zero NOx observations; the decoupling stands, its cause does not
- Bloom frequency peaks February to March at 0 to 5 C, driven by cold-water diatoms, not summer cyanobacteria
- Chlorophyll biomass (this project's target) skews west and tracks eutrophication; toxin-producing HAB species monitored by the state concentrate in eastern LIS. This system is a eutrophication early warning tool, not a direct toxin predictor.

## Repository structure

```
src/
  models/
    rolling_origin_cv.py            evaluation harness (canonical instrument)
    final_evaluation_threshold_sweep.py   single-split evaluation
    threshold_robustness.py         label-definition robustness (10 vs 12 ug/L)
    experiments/                    rejected improvement attempts (13)
  deploy/                           daily inference on the locked model;
                                    dashboard.html is stale (see DASHBOARD.md)
data/                               gitignored; see Data sources
figures/
paper/                              LaTeX (Overleaf)
```

Warning-system scripts (repo root): `warning_operating_point.py` (threshold selection), `warning_robustness.py` (CIs, extra years, per-station), `warning_station_gate.py` (rejected gate experiment), `grouped_station_report.py`.

## Data sources

| Source | Content | Access |
|---|---|---|
| CT DEEP / LISICOS via UConn ERDDAP | In-situ water quality, 1993 to 2025, ~monthly per station | public, merlin.dms.uconn.edu:8080 |
| UConn ERDDAP DEEP_Nutrient | Nutrient observations (NOx, DIP) | public |
| USGS stream gauges | Connecticut, Thames, Housatonic discharge | public |

The `data/` folder is not in git. Reproduce it from the public sources above; the raw water quality export is a single ERDDAP CSV query.

## Reproducing the headline numbers

```
conda activate hab
python src/models/rolling_origin_cv.py --horizon 21      # pooled AUC 0.852
python warning_operating_point.py --target-pod 0.8 --test-from-cv
python warning_robustness.py --t-star 0.35
```

## Status notes

- Horizon is standardized at 21 days throughout. An earlier single-split evaluation used a 28-day label; where its numbers appear in older notes they are superseded.
- `src/deploy/daily_inference.py` runs the locked pipeline (v2): it imports `locked_pipeline`, fits the LR walk-forward in-process, and loads no serialized model. The residual stale artifact is `src/deploy/dashboard.html`, whose sidebar still reads "Model: XGBoost / AUC 0.827" and which parses `aeration_score`/`do`/`temp`/`intervene` columns the current script no longer emits.
- Aeration intervention results are pending a rerun on corrected data and should not be quoted yet.

---

## Findings

Five results, each with the number that supports it. The negatives are the substance,
not the leftovers.

### 1. The alert beats "always alert", and nothing else

Until August 2026 this repo contained no trivial reference forecast, so "POD 0.875"
had nothing to be measured against. `src/models/reference_baselines.py` adds four
(always-alert, station x month climatology, station x day-of-year climatology,
persistence) with a paired station-year clustered bootstrap of the lift difference.

| Level | base rate | model lift | clearly beats |
|---|---|---|---|
| Station-day (n=956, 48 events) | 0.050 | **2.63x** | always-alert only, +1.651 [+1.197, +2.228] |
| Basin-day (n=41, 12 events) | 0.293 | 1.37x | nothing; +0.390 [+0.000, +0.909] vs always-alert |

At station-day level the model is decisively better than no information. Against
climatology (+0.331 [-0.009, +0.712]) and persistence the CIs include zero, so it is
not demonstrably better than a lookup table. At basin level a day-of-year table
(1.52x) and "was the last reading above 10?" (1.81x) both score numerically higher
than the model.

**Mechanism:** basin aggregation raises the base rate from 0.05 to 0.29, and
lift = precision / base_rate. The aggregation that buys verification coverage spends
the model's entire advantage. Report the station-day product, not the basin one.

### 2. Searching 912 operating points finds exactly chance

`src/models/basin_search.py` pre-registers a 912-cell grid (threshold x west-lon cut x
season gate x min-stations x aggregator), selects on validation only by a fixed rule,
and scores one configuration on test once. A permutation null re-runs the entire
search on shuffled labels.

- best real validation lift: **1.84x**
- permutation null best-lift: median **1.83x**, 95th percentile 3.01x
- the real result sits at the **52nd percentile of noise**

At 8 validation events, any search over this space returns ~1.8x whether or not the
labels carry information. The selected configuration scores POD 1.000 / FAR 0.583 /
lift 1.62x on test; that number is the output of selecting on noise and is not
reported as an improvement. This is a direct quantitative demonstration of the failure
mode recorded in `notes/PRECISION_CEILING_INVESTIGATION.md` Finding 1.

### 3. The detector cannot see the HAB it is named for

`notes/BENCHMARKS.md` and Hattenrath-Lehmann & Gobler (2016) record that CTDEEP -- the
provider of this dataset -- reported *Cochlodinium* (rust tide) patches in Long Island
Sound in 2012 and 2016, plus an extensive bloom in Port Jefferson Harbor in 2016.

Our Jul-Oct chlorophyll for 2016 is **0.6 sd below** the multi-year average (mean 4.21
vs 2012's 11.18), and across all 11,447 station-days exactly **one** reading reaches
the 100 ug/L rust-tide dense-patch level. Rust tide forms localised surface
aggregations that a station-day mean over multiple casts dilutes away.

Consequence for framing: chl-a > 10 ug/L is a **biomass** threshold, not a harm
threshold. Benign winter diatom blooms are counted; genuine HABs are missed. What this
model predicts is phytoplankton biomass exceedance. See `notes/LITERATURE_NOTES.md`.

### 4. Temperature is nearly uninformative here

Bloom rate below 15 C is **22.4%** versus **25.5%** at or above it (n=2,787
exceedances with paired temperature). A third of exceedances fall below the 15 C
threshold Reinl et al. (2023) use to define a cold-water bloom, and 20% below 5 C.
This cuts against the warming-drives-blooms framing that dominates the HAB
literature, and is consistent with the Feb-Mar cold-water diatom peak.

### 5. No point of no return exists

`src/models/point_of_no_return.py` tests, over 617 pre-onset observations, whether a
bloom ever becomes unavoidable. Two independent methods share **zero** rows. The
model-free test (50 matched historical analogues per state) peaks at **0.62**, median
0.04. The model counterfactual's apparent answer -- 65% of summer events locked in
~29 days out -- collapses to **0%** once temperature, salinity and tides are allowed
to move within their own observed station-season range, so it measures lever
restriction rather than inevitability.

### The rejected-attempts ledger, enumerated

This README previously said "thirteen pre-registered improvement attempts were
rejected" but named only seven and quantified one. The full ledger, with deltas where
they were logged (sources: `notes/PRECISION_OPTIMIZATION_LOG.md`,
`notes/PRECISION_PUSH_TRACKER.md`, `src/models/experiments/`):

| # | Attempt | Outcome |
|---|---|---|
| 1 | Nutrient forward-fill | **-10.4pp** precision (stale monthly samples) |
| 2 | NOAA ASOS wind (land-based) | **-4pp** |
| 3 | MODIS satellite CHL | **-7.8pp** (4 km too coarse) |
| 4 | ERA5 wind stress | **-6.3pp** (corr -0.003; wind is noise for LIS blooms) |
| 5 | Kd490 water clarity | **-2.2pp** (78.8% null in the merge) |
| 6 | UConn nutrients | **-4.9pp** (still monthly cadence) |
| 7 | River discharge lags | no signal, corr < 0.03 at every lag; screened out |
| 8 | Isotonic/Platt calibration | breaks the probability scale; val too small (~67 positives) |
| 9 | XGBoost | **-33pp** precision |
| 10 | Station-month bloom rate | rejected; delta not logged (`experiments/test_station_month_rate.py`) |
| 11 | Chlorophyll acceleration | rejected; delta not logged (`experiments/test_chl_acceleration.py`) |
| 12 | Neighbor bloom probability | rejected; delta not logged (`experiments/test_neighbor_bloom_prob.py`) |
| 13 | Station-gated alert policy | rejected; false alarms arise at bloom-prone stations in non-bloom periods, so the ceiling is temporal, not spatial |

Rejected since, under rolling-origin CV and this session's baselines: selective
prediction / station abstention (CI [-0.024, +0.037] straddles zero); stratification
features (paired AUC -0.014 [-0.021, -0.007] — real physics, no marginal signal);
label refinement (raises raw precision 0.175 to 0.380 while lift *falls* 5.72 to 2.91 —
a base-rate illusion); the ensemble (+0.0038 AUC vs LR, CI [-0.0100, +0.0201]); and the
912-configuration basin operating-point search (52nd percentile of its own permutation
null). The consistency of these failures across mechanism, model class, and alerting
policy is the precision-ceiling finding.

### Also worth knowing

- **Model class does not matter.** Ensemble vs locked LR on the same test split:
  +0.0038 AUC, 95% CI [-0.0100, +0.0201]. Every tree ensemble in
  `data/full_model_comparison_results.csv` scores clearly worse (VotingEnsemble 0.7918,
  StackedLR 0.7697) than LR (0.8139-0.8157).
- **A typical bloom onset carries one in-situ reading in the preceding month**
  (median 3 in 90 days; median inter-visit gap 21 days = the forecast horizon).
- **There is no spare data.** The raw ERDDAP export holds 106 real stations and 11,508
  station-days with usable chlorophyll; the model already uses 11,447 (~99.5%).