# HAB Bloom Predictor

**Predictability and its limits: a 21-day early warning system for chlorophyll exceedances in Long Island Sound**

Vihaan Goyal, Westhill High School, Stamford, Connecticut

---

## What this project shows

A regularized logistic regression forecasts chlorophyll-a exceedances (>10 ug/L within 21 days of a station visit) across Long Island Sound with strong ranking skill (pooled out-of-sample AUC 0.818, single-split test AUC 0.856), but alert precision is capped near 0.12 regardless of model class, feature set, threshold, era, or spatial alerting policy. Thirteen pre-registered improvement attempts were rejected. The central finding is that this precision ceiling is mechanistic, not a modeling failure:

1. **Ecology.** After the Clean Water Act nitrogen TMDL was met (~2014), western stations became nitrogen limited, decoupling elevated chlorophyll from realized blooms.
2. **Sampling.** The median gap between chlorophyll measurements is 21 days, equal to the forecast horizon. 48% of inter-sample gaps exceed the horizon, so many predicted events cannot even be verified.

Across eras and label definitions the system delivers a roughly constant 2 to 3x precision lift over the base rate, and no intervention has moved that multiplier.

## The early warning system

Operating point frozen by a pre-registered rule (highest threshold with out-of-sample 2020 to 2022 POD >= 0.8), evaluated once on out-of-sample 2023 to 2025:

| Metric | Value | 95% CI (clustered bootstrap) |
|---|---|---|
| POD (recall) | 0.896 (43 of 48 events) | [0.781, 0.977] |
| FAR (1 - precision) | 0.886 | -- |
| Precision | 0.114 (2.3x over 5.0% base rate) | [0.071, 0.158] |
| CSI | 0.113 | -- |
| F1 | 0.202 | [0.130, 0.270] |

Alert threshold **t\* = 0.30**, selected on 2020-2022 and evaluated once on 2023-2025 (956 rows, 48 events; TP 43 / FP 334 / FN 5).

**Restricted to verifiable windows** -- the 58.8% of windows that contained a station visit, so a negative means an observation showed no exceedance rather than that nothing was looked at -- precision is **0.146** and FAR **0.854** at the same POD. Note the lift is *lower* there (1.7x), because the base rate rises to 8.5% too. Both framings are reported because they answer different questions; neither is flattering.

A station-gated alert policy was tested and rejected: gating to the 21 recurring-bloom stations moves FAR only 0.884 -> 0.869 while costing POD 0.896 -> 0.833, so the ceiling is temporal, not spatial.

The framing rationale: a missed bloom carries ecological and shellfish-industry costs, while a false alarm prompts a water sample at a station where, half the time, no sample would otherwise occur in the window.

## Locked pipeline

- Model: LogisticRegression, C=0.05, L2, balanced class weights, 35 features
- Label: any chlorophyll-a exceedance >10 ug/L within 21 days of a station visit
- Evaluation: rolling-origin cross-validation (train <= T-2, test = T), folds 2015 to 2025, station-year clustered bootstrap for all interval claims
- Canonical data file: `data/hab_features_tidal_v2.csv` (plus in-script merges of percent saturation and gust features). The non-v2 file leaks test-period data through full-record climatologies; see `CLAUDE.md`.
- Label: `locked_pipeline.add_forward_label`, right-censored. Never built inline; `tests/test_label_equivalence.py` pins the shared builder to it.
- Dominant signal: chlorophyll history (~42% grouped feature importance)

Complexity does not help: XGBoost cost 33 points of precision against this baseline. Nutrient forward-fill, ERA5 wind, Kd490, neighbor bloom probability, station-month rates, and chlorophyll acceleration were all tested and rejected.

## Key ecological context

- Long-term chlorophyll decline since 1993, sharp inflection at the ~2014 TMDL achievement
- Post-TMDL biomass-bloom decoupling at western stations (A4, B3), confirmed by near-zero NOx observations
- Bloom frequency peaks February to March at 0 to 5 C, driven by cold-water diatoms, not summer cyanobacteria
- Chlorophyll biomass (this project's target) skews west and tracks eutrophication; toxin-producing HAB species monitored by the state concentrate in eastern LIS. This system is a eutrophication early warning tool, not a direct toxin predictor.

## Repository structure

```
src/
  models/
    locked_pipeline.py              features, label and model spec (source of truth)
    label_utils.py                  shared label builder
    emit_test_predictions.py        produces data/test_predictions.csv
    rolling_origin_cv.py            evaluation harness (canonical instrument)
    basin_alert.py                  western-basin alert product
    cadence_thinning.py             sampling-cadence decomposition of FAR
    threshold_robustness.py         label-definition robustness (10 vs 12 ug/L)
    experiments/                    rejected improvement attempts (13)
  archive/                          superseded label pipelines -- DO NOT USE,
                                    see src/archive/README.md
  deploy/                           daily inference + dashboard
tests/                              label-equivalence tests
data/                               gitignored; see Data sources
figures/
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
python src/features/rebuild_climatology.py               # leak-free features
python src/features/rebuild_tidal_anomalies.py
python src/models/rolling_origin_cv.py --horizon 21      # pooled AUC 0.818
python src/models/emit_test_predictions.py               # test AUC 0.856
python warning_operating_point.py --target-pod 0.8       # freezes t* = 0.30
python src/models/bootstrap_ci.py --preds data/test_predictions.csv --mode global
```

## Status notes

- Horizon is standardized at 21 days throughout. Older 28-day single-split numbers are superseded; those scripts now live in `src/archive/`.
- Six pipeline defects were found by systematic self-audit and fixed: a positional row-shift label, an uncensored 28-day label, a shared label builder that never emitted NaN, full-record climatology leakage in 4 of the locked 35 features, a threshold swept on the test set, and a per-station strategy chosen on test F1. `src/archive/README.md` documents which scripts carry which.
- A seventh is documented but deliberately unchanged: 47.7% of windows close with no station visit and are still scored 0. This *depresses* precision rather than flattering it; see `CLAUDE.md`.
- Numbers not yet rerun on the corrected pipeline and so **not quotable**: the sustained-exceedance secondary label, the XGBoost comparison, grouped feature importances, and the 13 rejected-attempt results in `src/models/experiments/`.
- Aeration intervention results were computed against a ~7-month label (`src/archive/`) and must not be quoted.