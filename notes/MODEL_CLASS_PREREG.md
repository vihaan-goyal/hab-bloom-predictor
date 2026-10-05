# Pre-registration: logistic regression vs gradient boosting on LIS (written 2026-10-02, before any run)

**Question.** Now that chlorophyll is on one lab-consistent scale (S1, 2024 corrected 2026-10-02), does a
gradient-boosted tree model rank LIS bloom risk better than the locked logistic regression?

**Prior evidence (disclosed).**
- XGBoost was one of 13 rejected LIS improvement attempts on the sensor-scale label (XGBoost, not this HistGradientBoosting model).
- The neural networks (fork findings §26-27) were NO-GO.
- Our expectation is "no difference": the limit is the ~3-week sampling, not the model class.

## Fixed now
- **Models.**
  - LR: the locked logistic regression (C = 0.05, balanced, 35 features).
  - GB: `HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=300,
    min_samples_leaf=50, l2_regularization=1.0, class_weight="balanced", random_state=42)`, the same 35
    features. These are the Narragansett settings, copied, not tuned.
- **Protocol.**
  - Identical to `rolling_origin_cv.py --horizon 21`: train ≤ T−2, test T.
  - Label from `label_utils.forward_window_label`; unresolved windows dropped.
  - Median imputation from the training fold.
- **Development folds 2016-2022** decide adoption. Folds 2023-2025 have already been looked at, so they
  are reported but cannot decide.
- **Adoption rule:**
  - GB replaces LR only if, on the pooled 2016-2022 out-of-fold rows, AUC(GB) − AUC(LR) ≥ +0.02;
  - **and** the paired station-year bootstrap (2,000 resamples, seed 42) gives a one-sided p < 0.05.
  - Otherwise LR stays.
- **Clean confirmation:** whichever model the rule selects is scored once on the 2026 season under
  `notes/PROSPECTIVE_2026_PREREG.md`. LR stays the primary model there; GB is reported alongside it as
  secondary, with the same label, rows and calendar baseline.
- **No other variants:** no feature changes, no hyperparameter search, no other model classes.

**Whatever the result, it is reported as is.**

## Result (run 2026-10-05, after the rule above was written and pushed; `src/models/model_class_cv.py`, `data/model_class_cv.log`)
- **Development 2016-2022** (1,411 rows, 78 events): LR **0.676**, GB **0.648**.
  - GB − LR **−0.028 [−0.068, +0.011]**, one-sided p = 0.93.
  - **The rule fails, so LR stays.** The LR numbers reproduce the locked walk-forward exactly (0.676 dev, 0.660 all).
- **Held out 2023-25** (reported only; 560 rows, 16 events): LR 0.602, GB 0.622, +0.020 [−0.105, +0.150], p = 0.39. A tie.
- **All 2016-2025:** LR 0.660, GB 0.644, −0.016 [−0.053, +0.023].
- **Per fold:** GB wins 3 of 10 (2017, 2024, 2025, all with 7 or fewer events) and loses badly in 2020-21 (0.26 / 0.18 vs 0.71 / 0.46).
- **Reading:** on the consistent lab-scale label, a more flexible model does not help. The tree model overfits small, sparse folds. As expected, the limit is the ~3-week sampling, not the model class.
