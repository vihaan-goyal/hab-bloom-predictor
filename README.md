# HAB Bloom Predictor

**Predictability and its limits: a 21-day early warning system for chlorophyll exceedances in Long Island Sound**

Vihaan Goyal, Westhill High School, Stamford, Connecticut

---

## What this project shows

A regularized logistic regression forecasts chlorophyll-a exceedances (>10 ug/L within 21 days of a station visit) across Long Island Sound with strong ranking skill (pooled out-of-sample AUC 0.852), but alert precision is capped near 0.13 regardless of model class, feature set, threshold, era, or spatial alerting policy. Thirteen pre-registered improvement attempts were rejected. The central finding is that this precision ceiling is mechanistic, not a modeling failure:

1. **Ecology.** After the Clean Water Act nitrogen TMDL was met (~2014), western stations became nitrogen limited, decoupling elevated chlorophyll from realized blooms.
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

- Long-term chlorophyll decline since 1993, sharp inflection at the ~2014 TMDL achievement
- Post-TMDL biomass-bloom decoupling at western stations (A4, B3), confirmed by near-zero NOx observations
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
  deploy/                           daily inference + dashboard (being migrated
                                    to the locked model; see DASHBOARD.md)
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
- `src/deploy/` still runs a superseded XGBoost model and is being migrated to the locked pipeline.
- Aeration intervention results are pending a rerun on corrected data and should not be quoted yet.