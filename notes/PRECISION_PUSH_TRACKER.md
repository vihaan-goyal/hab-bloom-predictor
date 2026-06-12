# Precision Push Tracker

Working list of every remaining avenue to push precision on the HAB predictor.
Knock these off top to bottom. Update the Status column as we go.

Status key: TODO / IN PROGRESS / DONE / REJECTED

Locked baseline to beat: LR, C=0.05, balanced, 35 features, rolling split.
Global t=0.60: Prec=0.500, Rec=0.486, F1=0.493, AUC=0.815.
Powered (rolling-origin CV): AUC 0.852 @ 21d, honest pooled precision ~0.26.

---

## Reframe (why this list exists)

The mechanistic ceiling we confirmed is an F1/recall ceiling under the constraint
"catch the blooms." Precision specifically is a different lever. The three real
questions: (1) is the plateau even statistically real, (2) can we honestly scope
out the bad regime, (3) is the target/label even correct. Most of the gains below
attack those, not the nitrogen-regime problem.

---

## Tier 1 - Do first (cheap, sets the terrain)

| # | Idea | Why | Effort | Status |
|---|------|-----|--------|--------|
| 1 | Bootstrap CI on precision + PR curve figure | Tells us if Prec=0.500 vs 0.600 is even distinguishable (likely +/- 10-15pp at our positive counts). Shows the high-precision end of the curve. Do before anything else. | Low | TODO |
| 2 | Bloom label audit | Highest-potential precision gain, free. Some FPs may be label noise (single-sample exceedances or missed short blooms). Redefine bloom as a sustained crossing and re-score. Fixing labels removes FPs from the denominator with zero model change. | Low | TODO |
| 3 | Move up the PR curve | Reframe precision as the goal: push threshold to t=0.75-0.80 and report that operating point. Trivial once #1 shows the curve shape. | Trivial | TODO |

---

## Tier 2 - Honest scoping + new data (medium effort, real ceiling)

| # | Idea | Why | Effort | Status |
|---|------|-----|--------|--------|
| 4 | Selective prediction / abstention | Detect the post-TMDL decoupled regime (where ~23 of 38 FPs live) and let the model abstain. Report precision at coverage < 1.0. Clean, not fudged. Converts the mechanistic finding into a usable operating mode. | Medium | TODO |
| 5 | USGS daily river discharge | The source that beats the monthly-nutrient problem. Daily resolution proxy for stratification + nutrient flux. Gages: Connecticut 01184000, Housatonic 01205500, Quinnipiac 01196500, Naugatuck 01208500. Free via `dataretrieval` (Python). Also WRTDS modeled daily N flux exists for these rivers. | Medium | TODO |
| 6 | Target swap to cyanobacteria-specific signal | FP cluster is "high CHL, no harmful bloom." Total CHL includes non-harmful diatoms, and Vaudrey confirmed species shift post-TMDL means CHL is a worse proxy now. Check LISICOS ERDDAP variable list for phycocyanin / total-algae channel; ask O'Donnell or Vaudrey directly. Highest ceiling on the target side IF data exists. Standard LISICOS params are temp/sal/DO/PAR/chl, so not guaranteed. | Medium | TODO |
| 7 | Stratification index from existing depth data | Did we keep surface-minus-bottom temp/density difference when aggregating depth profiles? Stratification is the physical switch that enables blooms. Free, in-house, daily, no download. Close the gap if only surface values were kept. | Low | TODO |
| 8 | PAR / photoperiod feature | LISICOS records PAR; day length is deterministic from date. Light is a first-order bloom driver we may not have. | Low | TODO |
| 9 | Two-stage decomposition | Stage 1 predicts high CHL; stage 2 (conditional on high CHL) predicts bloom-vs-no-bloom using regime/nutrient context. Isolates the precision-killing step so the decoupling signal goes exactly where it matters. Pairs with #4. | Medium | TODO |
| 10 | Decoupling-regime feature, strict t-28 window | Trailing CHL/N decoupling ratio, window ending at t-28 (no leakage). Lower priority but legitimate. | Medium | TODO |

---

## Tier 3 - ML frameworks worth a bake-off

The XGBoost failure (-33pp from bloom-rate shift) says the bottleneck is data
quantity + distribution shift, not model capacity. So most of the model zoo is a
trap. Only these are built for our regime:

| # | Idea | Why | Effort | Status |
|---|------|-----|--------|--------|
| 11 | TabPFN v2 | Transformer pre-trained for SMALL tabular data. Our dataset size is its home turf. Near-zero tuning, runs in seconds. Most likely thing to beat LR precisely because it does not over-extract capacity. | Low | TODO |
| 12 | Explainable Boosting Machine (EBM, InterpretML) | Glassbox additive model between LR and XGBoost. Per-feature nonlinearity + controlled pairwise interactions, far more regularizable than a GBM. Native interpretability (shape functions) is strong for SJWP. If it ties LR, that proves the relationship is ~linear (a real finding). | Low | TODO |
| 13 | LightGBM + monotonic constraints + heavy reg | Only disciplined way to retry a GBM. Force monotonic sign on physically-signed features so it cannot learn spurious wiggles in the decoupled A4 regime. Shallow depth (<=3), high min_child_samples, lambda_l2. | Medium | TODO |
| 14 | Temporal importance weighting / per-period threshold recalibration | Attacks the ROOT cause of the XGBoost failure (bloom-rate shift between splits) directly, instead of hoping a new architecture is robust to it. Higher value than any new classifier. | Medium | TODO |

---

## Dead / Do NOT revisit

- More nutrient CONCENTRATION data: oracle experiment settled it at +1.5pp max.
- More complex models generally: XGBoost was -33pp.
- Satellite: 4km MODIS resolution too coarse for LIS.
- Deep tabular nets (TabNet, FT-Transformer, SAINT): data-starved, will overfit.
- More LSTM/RNN variants: same data starvation, invalidated regime.
- SVM: no edge over regularized LR, harder to calibrate.
- Plain stacking/ensembling: marginal, adds complexity, weakens interpretability story.
- Already rejected (12 experiments): nutrient forward-fill, ERA5 wind, Kd490,
  UConn monthly nutrients, station-month bloom rate, CHL acceleration,
  neighbor bloom prob, isotonic/Platt calibration, discharge lags (old attempt).

---

## Suggested two-day plan

1. Bootstrap CI + PR curve (#1) - tells us the terrain
2. Bloom label audit (#2)
3. USGS discharge pull (#5)
4. In parallel, quick TabPFN + EBM bake-off (#11, #12) against locked LR

Any one of #1, #2, #5 could move the number, or prove the plateau is real with a
tight CI, which is itself a strong methods result.