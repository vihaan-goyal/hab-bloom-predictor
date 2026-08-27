# CLAUDE.md — HAB Bloom Predictor

## Run instructions

```bash
conda activate hab

# Regenerate the leak-free feature file (only needed if data/ is rebuilt)
python src/features/rebuild_climatology.py
python src/features/rebuild_tidal_anomalies.py

# Emit test-set predictions from the locked pipeline
python src/models/emit_test_predictions.py

# Confidence intervals on the operating point
python src/models/bootstrap_ci.py --preds data/test_predictions.csv --mode global

# Daily inference for a given date (generates data/daily_predictions.csv)
python src/deploy/daily_inference.py --date 2025-07-15

# Label semantics are pinned by tests — run both after touching any label code
python tests/test_label_equivalence.py
python tests/test_no_inline_labels.py

# environment.yml must cover every import in the repo
python tests/check_dependencies.py
```

## Primary data file

`data/hab_features_tidal_v2.csv` — 11,447 station-days, 50 CT DEEP LISICOS
stations, 1993–2025.

**Use v2, not `hab_features_tidal.csv`.** The original computes
`chl_climatology`, `chl_anomaly`, `tidal_gt_anom` and `tidal_msl_anom` against
climatologies averaged over the whole 1993–2025 record, which folds test-period
data into features on every training row. All four are in the locked 35.
`locked_pipeline.BASE_CSV` points at v2.

## Labels

`locked_pipeline.add_forward_label` — positive if any Chlorophyll > 10 µg/L
occurs within **21 days** strictly after a station visit, at that station.
Windows extending past the station's last observation are NaN and excluded.

Never build a label inline. `label_utils.build_forward_label` is the same
function plus a `sustained_only` option and an `unverifiable` policy;
`tests/test_label_equivalence.py` pins them together row for row.

**Known limitation, deliberately not changed.** Right-censoring excludes only 87
rows (0.8%). A further **47.7% of windows close with no station visit inside
them** and are still scored 0 — the survey cadence is ~21 days, so most windows
contain no observation. Such a row means "no exceedance was observed", not "no
exceedance occurred". Keeping them holds the positive rate at **0.146** instead
of **0.280**. This inflates the negative class, so it *depresses* precision and
FAR rather than flattering them. Metrics are reported both ways; use
`build_forward_label(..., unverifiable='exclude')` or the `verifiable` column in
`data/test_predictions.csv` for verification-style numbers.

## Deployed model

Logistic Regression, `C=0.05`, `class_weight='balanced'`, 35 features:
BASE + tidal_gt_anom + tidal_msl_anom + chl_roll14_mean + chl_roll21_mean +
sal_lag2 + sal_lag3 + sal_lag4 + percent_saturation + max_gust_3d

Requires `data/gust_features_daily.csv` — generate with:
`python src/features/add_gust_features.py`

**Operating point: t\* = 0.30**, selected on validation (2020–2022) by
`warning_operating_point.py` under the rule "highest threshold with selection
POD ≥ 0.8". Never tuned on test.

Test 2023–2025 (n=956, 48 positives, base rate 5.0%), AUC **0.856**:

| | POD | FAR | Precision | F1 | CSI | TP | FP | FN |
|---|---|---|---|---|---|---|---|---|
| all windows | 0.896 | 0.886 | 0.114 | 0.202 | 0.113 | 43 | 334 | 5 |
| verifiable windows | 0.896 | 0.854 | 0.146 | — | 0.144 | 43 | 251 | 5 |

Bootstrap 95% CI (2000 resamples, clustered by station-year):
precision [0.071, 0.158] · recall [0.781, 0.977] · F1 [0.130, 0.270].

**Station-specific operating points (test 2023–2025).** Strategy winner picked
on validation; the test column is read out once.

| Station | Rate | Winner | Threshold | Prec | Rec | F1 |
|---------|------|--------|-----------|------|-----|-----|
| B3 | 15.4% | A (station-only) | 0.30 (global) | 0.240 | 1.000 | 0.387 |
| 02 | 23.5% | A (station-only) | 0.12 (tuned) | 0.235 | 1.000 | 0.381 |
| A4 | 13.2% | A (station-only) | 0.30 (global) | 0.200 | 1.000 | 0.333 |
| C1 | 10.3% | A (station-only) | 0.30 (global) | 0.176 | 0.750 | 0.286 |
| 01 | — | — | — | skipped: fewer than 3 test positives | | |

**Per-station threshold tuning is not supported by this dataset, and is not
used.** Only **1 of 42 stations** (02, with 5) has ≥5 validation positives;
most have 0–2. `best_f1_threshold` therefore falls back to the global t\* unless
`MIN_VAL_POS` is met — matching the `--min-val-pos` rule already in
`rolling_origin_cv.py`. Without that guard A4 tuned to 0.92 on two validation
positives and caught **none** of its five test events (F1 0.000 vs 0.294 at the
global threshold).

The apparent gain from per-station thresholds was an artifact. Pooled, they gave
precision 0.176 at recall 0.667; a *single* global threshold of 0.45 reaches
precision **0.185** at the same recall. Per-station tuning was strictly worse
than one number — the same conclusion the station-gate experiment reached, and
further evidence the ceiling is temporal rather than spatial.

**No station reaches precision > 0.50.** Each rests on 3–6 test positives.
An earlier version of this table reported precision 0.500–1.000 and F1 up to
0.727; those came from Family B labels, a leaked climatology, and thresholds
selected on test. They are void.

## Headline results

- **Western-basin alert** (`basin_alert.py`): POD **1.000**, FAR **0.625**,
  CSI **0.375** on test, at a basin threshold pre-registered on val (12 TP,
  20 FP, 0 FN across 41 decision days). The strongest result in the project.

  **Report it with its confound.** `basin_prob` is a max over the stations
  sampled that day, and the label is "any western station exceeds in the
  window" — both scale with how many stations were looked at. On test,
  `n_stations` **alone** reaches AUC 0.713 against AUC 0.865 for the model
  (corr with the label +0.351). The model is genuinely +0.152 AUC above that
  null, but a reader who is not shown the null will overrate the result.
  `basin_alert.py` now prints this check on every run. 41 decision days with
  12 positives is also a small sample.
- **Cadence decomposition** (`cadence_thinning.py`): as sampling is thinned,
  raw FAR climbs 0.886 → 0.974 while FAR over *verifiable* windows stays flat
  near 0.85 and POD holds near 0.89. Apparent false alarms are substantially an
  artifact of unobserved windows, not of the model.

## Key scripts

| Script | Purpose |
|--------|---------|
| `src/models/locked_pipeline.py` | Single source of truth: features, label, model spec |
| `src/models/label_utils.py` | Shared label builder (`sustained_only`, `unverifiable`) |
| `warning_threshold_selection.py` | Independent re-derivation of t\* (agrees exactly) |
| `src/models/emit_test_predictions.py` | Produces `data/test_predictions.csv` |
| `src/models/bootstrap_ci.py` | Confidence intervals on the operating point |
| `src/models/basin_alert.py` | Western-basin alert product |
| `src/models/cadence_thinning.py` | Sampling-cadence decomposition of FAR |
| `src/models/station_specific_models.py` | Per-station thresholds (winner picked on val) |
| `src/models/rolling_origin_cv.py` | Rolling-origin CV; feeds threshold selection |
| `warning_operating_point.py` | Selects and freezes t\* on validation |
| `src/features/rebuild_climatology.py` | Expanding-window chl climatology |
| `src/features/rebuild_tidal_anomalies.py` | Expanding-window tidal anomalies |
| `tests/audit_station_thresholds.py` | Flags per-station thresholds with too little evidence (`--fix` resets them) |
| `src/deploy/daily_inference.py` | Daily inference pipeline + alert emails |
| `src/deploy/dashboard.html` | Browser-based monitoring dashboard |

## Archived code — do not use

`src/archive/` holds 13 scripts whose targets are built on discredited labels.
See `src/archive/README.md` for which defect each one carries. Two matter most:

- **Family B** (28-day horizon, no right-censoring) — includes
  `final_evaluation_threshold_sweep.py`, formerly the primary evaluation script.
  It also swept its threshold on the test set, which is where the retired 0.60
  operating point came from.
- **Family C** (positional row-shift) — `shift(-7)` on a survey cadence with a
  21-day median gap spans a **median of 217 days**. `bloom_7d_ahead` is a
  ~7-month-ahead label. The published SHAP rankings and the whole aeration /
  intervention framework were computed against it.

`src/models/experiments/` holds one-off experiments. Do not import from either
directory.

## Outstanding

- 72 legacy scripts still build a label inline (30 of them in
  `src/models/experiments/`). They are off the live path, but their printed
  numbers are not trustworthy. `tests/test_no_inline_labels.py` freezes that
  list, asserts the live path stays clean, and fails if a new one appears —
  shrink the list, never grow it. `python tests/scan_labels.py` refreshes it.
- The four nutrient features (`nox_lag2`, `dip_lag2`, `dip_change`,
  `dip_x_month`) are close to inert: dropping all four moves test AUC by
  −0.0012 (0.8562 → 0.8550), though POD does fall 0.896 → 0.854. They are
  50–62% missing, and the *missingness itself* tracks the label hard
  (`dip_change` missing → bloom rate 0.201 vs 0.054 present), so train-median
  imputation hands the model a readable "was this measured?" channel. Their
  missingness rate also shifts between eras (`nox_lag2`: 49.8% in train vs
  70.0% in test). `dip_x_month` was cited as a top-7 SHAP feature; that ranking
  is likely reading the missingness pattern, not nutrient chemistry.
- `neighbor_chl3_mean` / `neighbor_chl3_lag1` are in the locked 35 but arrive
  pre-baked from `hab_features_daily.csv`, whose producer does not exist in the
  repo. Their construction cannot be verified.
- `environment.yml` was missing 9 packages that scripts import, `polars` among
  them (9 files, including `audit_flagged_windows.py` and
  `check_label_integrity.py`). Now declared, but **not yet installed here** —
  run `conda env update -f environment.yml` before trusting those two scripts.
- **Reproducibility gap:** nothing in the repo builds `hab_features_daily.csv`
  (77 columns, 54 of them with no producer), and the raw NOAA CO-OPS tidal and
  ASOS wind inputs are no longer on disk. `data/` is entirely gitignored.
