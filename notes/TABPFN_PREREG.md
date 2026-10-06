# Pre-registration: TabPFN vs the locked logistic regression on LIS (written 2026-10-05, before any run)

**Question.** TabPFN is a pretrained transformer built for small tabular datasets. LIS is limited by too
few, sparse samples. Does TabPFN rank LIS bloom risk better than the locked logistic regression?

**Prior evidence (disclosed).** GB lost to LR on the development folds (−0.028, `MODEL_CLASS_PREREG.md`);
the neural networks were NO-GO (fork §26-27). That pre-registration said "no other model classes"; this is
a separate, new pre-registration. Our expectation is "no difference": the limit is the ~3-week sampling.

## Fixed now
- **Models.**
  - LR: the locked logistic regression (C = 0.05, balanced, 35 features), as in `model_class_cv.py`.
  - TabPFN: `tabpfn==2.2.1` `TabPFNClassifier(random_state=42, device="cpu")`, default settings, the
    same 35 features with training-fold median imputation. No tuning, no feature changes.
- **Protocol.** Identical to `model_class_cv.py`: walk-forward as `rolling_origin_cv.py --horizon 21`
  (train ≤ T−2, test T, 2016-2025), label from `label_utils.forward_window_label`, unresolved windows
  dropped.
- **Development folds 2016-2022** decide adoption; 2023-2025 have been looked at, so they are reported
  only.
- **Adoption rule:** TabPFN replaces LR only if, on pooled 2016-2022 out-of-fold rows,
  AUC(TabPFN) − AUC(LR) ≥ +0.02 **and** the paired station-year bootstrap (2,000 resamples, seed 42)
  gives one-sided p < 0.05. Otherwise LR stays.
- TabPFN runs in a separate environment (it needs PyTorch); the base environment builds the folds and
  computes all statistics with the same `paired()` bootstrap.

**Whatever the result, it is reported as is.**

## Result (run 2026-10-05/06, after this rule was committed and pushed; `src/models/tabpfn_cv.py`, `data/tabpfn_cv.log`)
- **Development 2016-2022** (1,411 rows, 78 events): LR **0.676**, TabPFN **0.529**.
  TabPFN − LR **−0.147 [−0.184, −0.116]**, one-sided p = 1.000. **The rule fails, so LR stays.**
  The LR numbers reproduce the locked walk-forward exactly (0.676 dev, 0.660 all).
- **Held out 2023-25** (reported only; 560 rows, 16 events): LR 0.602, TabPFN 0.693, +0.091 [−0.066, +0.254],
  p = 0.13. Not significant; 2025 (3 events) drives it (0.292 vs 0.885).
- **All 2016-2025:** LR 0.660, TabPFN 0.551, −0.109 [−0.148, −0.067].
- **Per fold:** TabPFN collapses where the big events are: 2019 (52 events) 0.527 vs 0.629, and 2020-21
  (0.33 / 0.23 vs 0.71 / 0.46), the same folds where GB failed.
- **Reading:** a model built for small tables does worse, not better. With three tests now (GB, the
  neural networks, TabPFN), more flexible models consistently lose to the regularized LR on sparse
  boat data. The limit is the ~3-week sampling, not the model class.
- Run note: TabPFN 2.2.1 on CPU (`TABPFN_ALLOW_CPU_LARGE_DATASET=1`, a speed guard only); folds
  2016-2019 on the laptop, 2020-2025 on a home desktop after the laptop ran out of memory. Same
  package version, settings and input file.
