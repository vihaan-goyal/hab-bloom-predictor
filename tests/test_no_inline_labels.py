"""
test_no_inline_labels.py
------------------------
Regression guard for the label defects found in the 2026-08 audit.

Three ways of building a forward label by hand were found across the repo, and
all three were wrong:

  inline_zero_init   df['bloom_28d'] = 0, then only ever written up to 1, so a
                     window that could never be resolved was scored as a clean
                     negative. At h=28 that mislabeled 33.4% of rows.
  positional_shift   groupby(...).shift(-7), or .shift(-LABEL_SHIFT_DAYS).
                     Shifts ROWS, not days. Station visits are a survey cadence
                     with a ~21-day median gap, so shift(-7) spans a median of
                     217 days and shift(-21) roughly 441.
  positional_iloc    iloc[idx + FORECAST_HORIZON], same defect as above.

This test does not try to fix the legacy scripts. It freezes the list of files
that already contain these patterns and fails when a NEW one appears, so the
class of defect cannot spread back into live code.

To fix a legacy file: use locked_pipeline.add_forward_label (or
label_utils.build_forward_label), delete its entry from ALLOWED below, and this
test will hold you to it.

To refresh the list after an intentional change:
    python tests/scan_labels.py

Run:  python -m pytest tests/test_no_inline_labels.py -q
      python tests/test_no_inline_labels.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scan_labels import scan                                   # noqa: E402

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

# Files on the live path. These must NEVER build a label by hand -- they are
# what produces every number that gets published.
LIVE = [
    "src/models/locked_pipeline.py",
    "src/models/label_utils.py",
    "src/models/emit_test_predictions.py",
    "src/models/basin_alert.py",
    "src/models/cadence_thinning.py",
    "src/models/station_specific_models.py",
    "src/models/rolling_origin_cv.py",
    "src/models/bootstrap_ci.py",
    "src/deploy/daily_inference.py",
    "warning_operating_point.py",
    "warning_threshold_selection.py",
    "warning_robustness.py",
    "warning_station_gate.py",
]

# Frozen 2026-08-26. Legacy scripts that still build a label inline. Their
# printed numbers are not trustworthy. Shrink this list; never grow it.
ALLOWED = {
    "src/archive/ablation_study.py",  # inline_zero_init
    "src/archive/aeration_intervention.py",  # positional_shift
    "src/archive/baseline.py",  # positional_shift
    "src/archive/build_conv_sequences.py",  # positional_shift
    "src/archive/build_sequences.py",  # positional_iloc
    "src/archive/conditional_satellite_eval.py",  # positional_shift
    "src/archive/failure_analysis.py",  # positional_shift
    "src/archive/final_evaluation.py",  # positional_shift
    "src/archive/final_evaluation_threshold_sweep.py",  # inline_zero_init
    "src/archive/prevention_analysis.py",  # positional_shift
    "src/archive/shap_analysis.py",  # positional_shift
    "src/data/download_uconn_nutrients.py",  # inline_zero_init
    "src/features/add_nutrient_ffill.py",  # inline_zero_init
    "src/features/add_stratification_features.py",  # inline_zero_init
    "src/features/add_tidal_features.py",  # inline_zero_init
    "src/features/add_wind_features.py",  # inline_zero_init
    "src/features/build_era5_features.py",  # inline_zero_init
    "src/features/merge_modis_features.py",  # inline_zero_init
    "src/models/acceleration_feature.py",  # inline_zero_init
    "src/models/baseline_final.py",  # inline_zero_init
    "src/models/baseline_v2.py",  # inline_zero_init
    "src/models/baselines_corrected.py",  # inline_zero_init
    "src/models/calibration.py",  # inline_zero_init
    "src/models/chl_correction_test.py",  # inline_zero_init
    "src/models/ensemble_aligned.py",  # inline_zero_init
    "src/models/ensemble_final.py",  # inline_zero_init
    "src/models/experiments/analyze_errors.py",  # inline_zero_init
    "src/models/experiments/anomaly_features_test.py",  # inline_zero_init
    "src/models/experiments/auc_optimization_test.py",  # inline_zero_init
    "src/models/experiments/combo_search.py",  # inline_zero_init
    "src/models/experiments/era_split_models.py",  # inline_zero_init
    "src/models/experiments/feature_combination_search.py",  # inline_zero_init
    "src/models/experiments/feature_strategy_search.py",  # inline_zero_init
    "src/models/experiments/full_model_comparison.py",  # inline_zero_init
    "src/models/experiments/gust_interaction_test.py",  # inline_zero_init
    "src/models/experiments/hourly_gust_test.py",  # inline_zero_init
    "src/models/experiments/interaction_features.py",  # inline_zero_init
    "src/models/experiments/longer_lags.py",  # inline_zero_init
    "src/models/experiments/mlp_tabular.py",  # inline_zero_init
    "src/models/experiments/narragansett_transfer_test.py",  # inline_zero_init
    "src/models/experiments/oracle_nutrient_experiment.py",  # inline_zero_init
    "src/models/experiments/precision_search.py",  # inline_zero_init
    "src/models/experiments/retrain_with_satellite.py",  # inline_zero_init
    "src/models/experiments/retrain_with_tidal.py",  # inline_zero_init
    "src/models/experiments/retrain_with_wind.py",  # inline_zero_init
    "src/models/experiments/self_training.py",  # inline_zero_init
    "src/models/experiments/t98_nutrient_test.py",  # inline_zero_init
    "src/models/experiments/test_calibration.py",  # inline_zero_init
    "src/models/experiments/test_chl_acceleration.py",  # inline_zero_init
    "src/models/experiments/test_kd490_features.py",  # inline_zero_init
    "src/models/experiments/test_neighbor_bloom_prob.py",  # inline_zero_init
    "src/models/experiments/test_station_month_rate.py",  # inline_zero_init
    "src/models/experiments/test_xgboost_precision.py",  # inline_zero_init
    "src/models/experiments/unused_features_search.py",  # inline_zero_init
    "src/models/experiments/usgs_nutrient_conc_test.py",  # inline_zero_init
    "src/models/experiments/wqp_nutrient_test.py",  # inline_zero_init
    "src/models/extended_train.py",  # inline_zero_init
    "src/models/false_positive_analysis.py",  # inline_zero_init
    "src/models/feature_selection.py",  # inline_zero_init
    "src/models/feature_weighting.py",  # inline_zero_init
    "src/models/lr_vs_ensemble.py",  # inline_zero_init
    "src/models/lstm_corrected.py",  # inline_zero_init
    "src/models/precision_boost.py",  # inline_zero_init
    "src/models/precision_features.py",  # inline_zero_init
    "src/models/regularization_sweep.py",  # inline_zero_init
    "src/models/shap_corrected.py",  # inline_zero_init
    "src/models/station_models.py",  # inline_zero_init
    "src/models/station_thresholds.py",  # inline_zero_init
    "src/models/threshold_tuning.py",  # inline_zero_init
    "src/models/tune_scale_pos_weight.py",  # inline_zero_init
    "src/models/tune_xgboost.py",  # inline_zero_init
    "src/models/two_stage_classifier.py",  # inline_zero_init
}

NEWLINE_INDENT = "\n  "


def test_live_path_has_no_inline_labels():
    hits = scan(REPO)
    offenders = {p: k for p, k in hits.items() if p in LIVE}
    assert not offenders, (
        "Live-path file builds a label by hand; use "
        f"locked_pipeline.add_forward_label instead: {offenders}")
    print(f"  live path clean ({len(LIVE)} files checked)")


def test_no_new_inline_labels():
    hits = scan(REPO)
    new = sorted(set(hits) - ALLOWED)
    assert not new, (
        "New file(s) build a forward label by hand. Use "
        "locked_pipeline.add_forward_label or label_utils.build_forward_label:"
        + NEWLINE_INDENT + NEWLINE_INDENT.join(new))
    print(f"  no new inline labels ({len(hits)} known legacy files)")


def test_allowlist_is_not_stale():
    """If a legacy file was fixed, its entry must be removed, so the list
    keeps shrinking and stays an accurate inventory."""
    hits = scan(REPO)
    fixed = sorted(ALLOWED - set(hits))
    assert not fixed, (
        "These no longer build a label inline -- delete them from ALLOWED:"
        + NEWLINE_INDENT + NEWLINE_INDENT.join(fixed))
    print(f"  allowlist accurate ({len(ALLOWED)} entries)")


if __name__ == "__main__":
    print("inline-label guard:")
    test_live_path_has_no_inline_labels()
    test_no_new_inline_labels()
    test_allowlist_is_not_stale()
    print("all inline-label guard checks passed")
