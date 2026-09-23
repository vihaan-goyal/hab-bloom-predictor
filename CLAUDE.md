# CLAUDE.md — HAB Bloom Predictor

## Run instructions

```bash
# Use the BASE conda env: ~/anaconda3/python.exe (or `conda activate base`).
# The `hab` env is BROKEN (exit 127 on np.linalg.lstsq / sklearn fits): its
# pip-installed scipy conflicts with conda-forge MKL. Three in-place repairs
# failed (2026-09-01); recreate it if you need it:
#   conda env remove -n hab && conda env create -f environment.yml
# (2026-09-05: the fork's environment.yml is re-pinned to the base env's real versions and
#  verified to build from scratch; this repo's yml still lists the torch/xgboost extras.)

# Final evaluation with threshold sweep (test set 2023–2025)
python src/models/final_evaluation_threshold_sweep.py

# Daily inference for a given date (generates data/daily_predictions.csv)
python src/deploy/daily_inference.py --date 2022-07-19
```

## Primary data file

`data/hab_features_tidal.csv` — 11,447 station-days, 50 CT DEEP LISICOS stations,
1993–2025, with tidal anomaly and salinity-lag features. This is the input to both
the evaluation script and the daily inference pipeline.

## Deployed model

Logistic Regression, `C=0.05`, `class_weight='balanced'`, 35 features:
BASE + tidal_gt_anom + tidal_msl_anom + chl_roll14_mean + chl_roll21_mean +
sal_lag2 + sal_lag3 + sal_lag4 + percent_saturation + max_gust_3d

Requires `data/gust_features_daily.csv` — generate with:
`python src/features/add_gust_features.py`

Test AUC: 0.815 | Precision @0.60: 0.500 | Recall @0.60: 0.486 | F1 @0.60: 0.493

**Superseded 2026-09-23 as the headline (label rebuild, notes/LABEL_REBUILD_PREREG.md).**
The numbers above use the raw CTD-fluorometer `Chlorophyll`, which read 2-3x DEEP's lab
values in 1994-1999 and 2009-2013. On the lab-consistent S1 series
(`data/hab_features_tidal_S1.csv`; run with `--input data/hab_features_tidal_S1.csv --tag _S1`):
Test AUC 0.804 [0.706, 0.878] | base rate 6.3% | Precision @0.60 0.316 | Recall 0.477 |
Lift 5.03 [3.50, 6.88]. The station table below is still on the old label until re-run.
CT DEEP (2026-09-23) advises against the in-situ fluorometer: "Use the lab data." The
lab-only series S4 (`--input data/hab_features_tidal_S4.csv --label-col bloom_28d_lab --tag _S4`)
gives AUC 0.782 [0.595, 0.921] on 161 test rows / 15 events (lab data end 2024-06-04):
consistent with S1, too small to stand alone. Report S1 as the skill estimate with S4 beside it.

**Station-specific best operating points (test 2023–2025):**

| Station | Rate | Strategy | Threshold | Prec | Rec | F1 | TP | FP | FN |
|---------|------|----------|-----------|------|-----|-----|-----|-----|-----|
| C1 | 17.5% | B (global) | 0.60 | 1.000 | 0.571 | 0.727 | 4 | 0 | 3 |
| 02 | 33.3% | B (global) | 0.60 | 0.625 | 0.833 | 0.714 | 5 | 3 | 1 |
| 01 | 16.7% | B (global) | 0.60 | 0.500 | 1.000 | 0.667 | 3 | 3 | 0 |
| A4 | 20.0% | A (station-only) | 0.60 | 0.625 | 0.625 | 0.625 | 5 | 3 | 3 |
| B3 | 27.5% | A (station-only) | 0.50 | 0.556 | 0.455 | 0.500 | 5 | 4 | 6 |

Note: C1 precision=1.000 is genuine (4 TP, 0 FP) but small sample (7 test positives).

## Key scripts

| Script | Purpose |
|--------|---------|
| `src/models/final_evaluation_threshold_sweep.py` | Final test-set evaluation; threshold sweep |
| `src/models/station_specific_models.py` | Per-station threshold tuning (Strategy B) |
| `src/models/ablation_study.py` | Feature ablation (useful for paper) |
| `src/deploy/daily_inference.py` | Daily inference pipeline + alert emails |
| `src/deploy/dashboard.html` | Browser-based monitoring dashboard |
| `src/sim/rake_field.py`, `floc_kinetics.py`, `rake_capture.py` | Device simulation: magnet field (Magpylib), floc growth, raster capture; see notes/DEVICE_SIMULATION.md |

## End of every session

Update  (question, hypotheses, variables, results,
conclusion) with what changed. It is the one-page truth of the project.

## Experiment scripts

One-off experiments that are not part of the main pipeline are archived in
`src/models/experiments/`. Do not import from them.
