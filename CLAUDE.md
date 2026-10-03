# CLAUDE.md — HAB Bloom Predictor

## Run instructions

```bash
# Use the BASE conda env: ~/anaconda3/python.exe (or `conda activate base`).
# The `hab` env is broken (scipy/MKL conflict). To rebuild it:
#   conda env remove -n hab && conda env create -f environment.yml

# Default input: the lab-consistent label, data/hab_features_tidal_S1.csv. Build it:
python src/features/add_tidal_features.py   # writes data/hab_features_tidal.csv
python src/models/label_rebuild.py build     # writes data/hab_features_tidal_S1.csv
# Prefix HAB_FEATURES_CSV=data/hab_features_tidal.csv to reproduce the original sensor label.

# Final evaluation (test 2023–2025); add --no-censor to reproduce the old label
python src/models/final_evaluation_threshold_sweep.py --tag _S1

# Daily inference for a given date (writes data/daily_predictions.csv)
python src/deploy/daily_inference.py --date 2022-07-19
```

## Primary data files

- `data/hab_features_tidal_S1.csv`: the default. The label and every chlorophyll feature are rebuilt from DEEP's lab-corrected `Corrected_Chlorophyll`. It feeds evaluation and daily inference.
- `data/hab_features_tidal.csv`: 11,447 station-days, 50 CT DEEP LISICOS stations, 1993–2025, with tidal-anomaly and salinity-lag features, labelled from the raw CTD fluorometer (the original sensor label). S1 is built from it.

## Deployed model

Logistic Regression, `C=0.05`, `class_weight='balanced'`, 35 features:
BASE + tidal_gt_anom + tidal_msl_anom + chl_roll14_mean + chl_roll21_mean +
sal_lag2 + sal_lag3 + sal_lag4 + percent_saturation + max_gust_3d.
Requires `data/gust_features_daily.csv` (`python src/features/add_gust_features.py`).

Current numbers live ONLY in `notes/S1_NUMBERS_SHEET.md` (updated 2026-10-02: 2024 is now on DEEP's corrected scale). In short:
- **28-day test 2023-25** (683 rows, 25 events, base 3.7%): AUC 0.590 [0.427, 0.757].
  - Per year: 2023 0.433 (12 events), 2024 0.952 (9), 2025 0.537 (4). The old 0.767 rested on raw-sensor 2024 events.
  - At t = 0.47: precision 0.163, lift 4.45. At t* = 0.25: precision 0.045, recall 0.520.
- **21-day walk-forward CV:** AUC 0.660. It beats a past-years calendar over 2016-2025 (+0.088, p < 0.001, pre-registered); in 2023-25 the calendar is ahead (not significant).
- The 21-day operating threshold is `locked_pipeline.T_STAR_21` (0.20, validation rule); import it, never hard-code.
- 2022-2023 are still raw-sensor scale. The clean test is the 2026 season (`notes/PROSPECTIVE_2026_PREREG.md`).

Rules learned the hard way (2026-09-28 audit):
- Any climatology, anomaly or monthly feature must use only data dated before the row (and, for monthly series, only completed months).
- Forward labels come only from `label_utils.forward_window_label`: an unobserved or unfinished window is NaN, not 0.
- Thresholds are chosen on validation only; purge training rows whose label window reaches the next split.
- The forecast is issued at the end of sampling day t from that day's measurements.
- Disclose that the 35 features were chosen partly on 2023-25, and that 2022-23 S1 is raw-sensor scale (2024 corrected 2026-10-02).

## Key scripts

| Script | Purpose |
|--------|---------|
| `src/models/final_evaluation_threshold_sweep.py` | 28-day evaluation; validation-chosen threshold; test sweep for display only |
| `tests/check_dependencies.py` | Lists imports missing from `environment.yml` |
| `src/models/significance_checks.py`, `calendar_baseline_cv.py`, `calendar_hybrid_cv.py` | Significance and calendar comparisons (pre-registered in `notes/CALENDAR_BASELINE_PREREG.md`) |
| `src/models/station_specific_models.py` | Per-station threshold tuning (Strategy B) |
| `src/models/ablation_study.py` | Feature ablation |
| `src/deploy/daily_inference.py` | Daily inference pipeline + alert emails |
| `src/sim/method_mc.py` (+ `tank_model.py`, `loop_controller.py`) | Layer 2 tank simulation of the treatment loop; see `notes/mitigation/LAYER2_SIM_RESULTS.md` |
| `src/lab/lis_water_recipe.py` | DEEP-based Sound water stats and tank water recipe |
| `hardware/alerter_uno/` | Arduino alerter firmware (`alerter_uno.ino`), laptop link (`alerter_link.py`), build guide (`README.md`) |
| `src/sim/rake_field.py`, `floc_kinetics.py`, `rake_capture.py` | Earlier clay-device simulation; see `notes/DEVICE_SIMULATION.md` |

## Bench experiments

The current plan is in `notes/mitigation/`:
- `EXECUTION_PLAN.md`: the overall plan;
- `00_CONTROL_LOOP.md`: shared loop rules and hypotheses H1-H4;
- `PROCEDURES.md`, `MATERIALS_LIST.md`, `WATER_RECIPE.md`;
- one file per method.

## End of every session

Update `notes/SCIENTIFIC_METHOD.md` (question, hypotheses, variables, results, conclusion)
with what changed. It is the one-page truth of the project.

## Experiment scripts

One-off experiments that are not part of the main pipeline are archived in
`src/models/experiments/`. Do not import from them.
