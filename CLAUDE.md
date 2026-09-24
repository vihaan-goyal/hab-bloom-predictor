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

# Default input is now the lab-consistent label, data/hab_features_tidal_S1.csv.
# Build it: python src/features/add_tidal_features.py   (writes data/hab_features_tidal.csv)
#           python src/models/label_rebuild.py build     (writes data/hab_features_tidal_S1.csv)
# Prefix HAB_FEATURES_CSV=data/hab_features_tidal.csv to reproduce the original sensor label.

# Final evaluation with threshold sweep (test set 2023–2025)
python src/models/final_evaluation_threshold_sweep.py

# Daily inference for a given date (generates data/daily_predictions.csv)
python src/deploy/daily_inference.py --date 2022-07-19
```

## Primary data files

`data/hab_features_tidal_S1.csv` — the default (S1, lab-consistent label): the label and
every chlorophyll feature rebuilt from DEEP's lab-corrected `Corrected_Chlorophyll`. It is
the input to the evaluation scripts and the daily inference pipeline.

`data/hab_features_tidal.csv` — 11,447 station-days, 50 CT DEEP LISICOS stations,
1993–2025, with tidal anomaly and salinity-lag features, labelled from the raw CTD
fluorometer `Chlorophyll` (the original sensor label). It is the source S1 is built from,
and `HAB_FEATURES_CSV=data/hab_features_tidal.csv` reproduces the sensor-label results.

## Deployed model

Logistic Regression, `C=0.05`, `class_weight='balanced'`, 35 features:
BASE + tidal_gt_anom + tidal_msl_anom + chl_roll14_mean + chl_roll21_mean +
sal_lag2 + sal_lag3 + sal_lag4 + percent_saturation + max_gust_3d

Requires `data/gust_features_daily.csv` — generate with:
`python src/features/add_gust_features.py`

Test (2023–2025, 28-day label, S1 default): AUC 0.804 [0.706, 0.878] | base rate 6.3% |
Precision @0.60 0.316 [0.179, 0.424] | Recall @0.60 0.477 | 31 TP / 67 FP / 34 FN |
Lift 5.03 [3.50, 6.88]. All seven pre-registered predictions were right.

Original sensor label (superseded 2026-09-23): Test AUC 0.815 | Precision @0.60 0.500 |
Recall @0.60 0.486 | F1 @0.60 0.493.

**Why the label changed (2026-09-23; notes/LABEL_REBUILD_PREREG.md, numbers in
notes/S1_NUMBERS_SHEET.md).** The raw CTD-fluorometer `Chlorophyll` read 2.1-4.8x DEEP's lab
values in 1994-1999 and 1.8-3.2x in 2009-2013. CT DEEP (2026-09-22/23) confirmed the CTD changed
from a SeaBird to a YSI EXO2 around 2009/2010, its lab is unchanged, and advised: "Use the lab
data." The lab-only check S4 (`--input data/hab_features_tidal_S4.csv --label-col bloom_28d_lab
--tag _S4`) gives AUC 0.782 [0.595, 0.921] on 161 test rows / 15 events (lab data end
2024-06-04): consistent with S1, too small to stand alone. Report S1 as the skill estimate with
S4 beside it.

**Per-station, western five, global t=0.60 (test 2023–2025, S1):**

| Station | Base rate | Precision | Recall | TP/FP/FN |
|---------|-----------|-----------|--------|----------|
| A4 | 20.0% | 0.333 | 0.875 | 7/14/1 |
| B3 | 20.0% | 0.333 | 0.625 | 5/10/3 |
| C1 | 12.5% | 0.444 | 0.800 | 4/5/1 |
| 01 | 16.7% | 0.500 | 0.667 | 2/2/1 |
| 02 | 27.8% | 0.429 | 0.600 | 3/4/2 |

No western station and strategy clears precision > 0.50 with recall > 0.40. The old C1
precision 1.000 (sensor label) is gone.

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
