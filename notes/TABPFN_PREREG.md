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
