# Precision Push Tracker

Status key: TODO / IN PROGRESS / DONE / REJECTED

Powered backbone (use this for all inference): rolling-origin CV, original label,
21-day horizon, 156 pooled positives, 11 folds. File: data/cv_pred_orig_h21.csv.

---

## Locked honest numbers (h21 original, fold-clustered bootstrap)

PR-AUC = 0.221, CI [0.165, 0.286]   (no-skill baseline 0.039, so ~5.7x chance)
ROC-AUC = 0.852, CI [0.827, 0.875]
At deployed t=0.60: precision 0.175, recall 0.468.
Low-false-alarm mode t~0.80: precision ~0.40, recall ~0.11.

The 0.500 precision headline is DEAD (it came from maximizing F1 on the test set).
Honest operating-point precision is 0.175 (h21) / 0.220 (h28). Report this as a
methods contribution: naive test-set threshold selection inflated precision ~3x.

Do NOT quote t>=0.85 rows as achievements (npos < 30, pure noise).

---

## Tier 1 - terrain (DONE)

| # | Idea | Status | Result |
|---|------|--------|--------|
| 1 | Bootstrap CI + PR curve | DONE | Plateau is NOISE: precision CIs at t=0.50/0.55/0.60/0.65 overlap heavily. No plateau, just a clean monotone PR tradeoff that is base-rate-limited. Confirmed across h28-orig, h21-orig, and the sweep. Ceiling is mechanistic, settled three ways. |
| 3 | Move up PR curve | DONE | Folded into #1. High-precision operating point t~0.80 is a legit deliverable. |

---

## VERIFY before paper (two unpaired claims)

These two canonical claims reproduce on point estimate but the on-disk evidence is
NOT the paired comparison the logged CI describes (different positive sets, different
skipped folds). Find how each was originally computed (must be on a common row set)
or recompute properly. Until then, treat the CIs as unsupported.

- [ ] "sustained AUC 0.882 vs 0.815, paired CI [0.027, 0.110]" -- h28: 0.884 vs 0.815
      reproduces, but 235 vs 51 positives = not paired. Also: sustained has LOWER
      operating-point precision (0.139 vs 0.220 at t=0.60). "Better" = ranking only.
- [ ] "21d beats 28d, paired AUC +0.037, CI [0.016, 0.059]" -- pooled AUC 0.852 vs
      0.815 = +0.037 reproduces, but 156 vs 235 positives = not paired. Also: h21 has
      LOWER operating-point precision than h28 (0.175 vs 0.220 at t=0.60).

Framing fix: wherever 21d or sustained is the headline, justify on AUC / lead-time,
NOT precision. They trade precision for ranking. A sharp judge catches the conflation.

---

## Tier 1.5 - NEXT

| # | Idea | Status | Why |
|---|------|--------|-----|
| 2 | False-positive label audit | IN PROGRESS | Split the ~390 FPs at t=0.60 into fixable (unobserved window / near-miss) vs genuine_low model error. At a 3.9% base rate this is where proportional precision leverage is. Script: fp_audit.py. Decides the whole downstream path. |

---

## Tier 2 - honest scoping + new data (after audit)

| # | Idea | Status |
|---|------|--------|
| 4 | Selective prediction / abstention (report precision at coverage < 1) | TODO |
| 5 | USGS daily river discharge (Connecticut 01184000, Housatonic 01205500, Quinnipiac 01196500, Naugatuck 01208500) + WRTDS daily N flux | TODO |
| 6 | Target swap to phycocyanin / cyanobacteria-specific (check LISICOS ERDDAP vars; ask O'Donnell/Vaudrey) | TODO |
| 7 | Stratification index (surface-bottom temp/density) from existing depth data | TODO |
| 8 | PAR / photoperiod feature (LISICOS has PAR) | TODO |
| 9 | Two-stage model (high-CHL then bloom-vs-no-bloom) | TODO |
| 10 | Decoupling-regime feature, strict t-28 window | TODO |

## Tier 3 - model bake-off (cheap, low priority)

| # | Idea | Status |
|---|------|--------|
| 11 | TabPFN v2 | TODO |
| 12 | EBM (InterpretML) | TODO |
| 13 | LightGBM + monotonic constraints | TODO |
| 14 | Temporal importance weighting / per-period threshold recalibration | TODO |

---

## Pipeline hygiene fixed this round

- --clean-labels no-op was a STALE-FILE artifact, not a code bug. Label logic is
  sound (sustained = real 34% subset; big forward-label differences at h21 and h28).
- Added --horizon flag to rolling_origin_cv.py (paper headline is 21d).
- build_dataset now strips any baked bloom_28d/is_sustained/is_exceedance before
  labeling. Also stripped baked bloom_28d from hab_features_tidal.csv.

## Dead / do NOT revisit

More nutrient concentration data (oracle +1.5pp). Complex models (XGBoost -33pp).
Satellite (4km too coarse). Deep tabular nets. More RNNs. SVM. Plain stacking.
The 12 previously-rejected feature experiments.