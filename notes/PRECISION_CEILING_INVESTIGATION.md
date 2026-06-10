# Precision Ceiling Investigation: Unexamined Holes

Companion to `notes/PRECISION_LOG.md`. Where `PRECISION_LOG.md` records features and
model classes that were tested and rejected, this document lists the holes that sit
*outside* that space: the label, the evaluation statistics, and the framing of the
A4-2024 drift problem. None of these are on the rejected list.

Locked pipeline reference: LR, C=0.05, class_weight='balanced', 35 features,
train <= 2019 / val 2020-2022 / test 2023-2025. Global test at t=0.60:
Prec=0.500, Rec=0.486, F1=0.493, AUC=0.815. Combined western stations:
Prec=0.464, Rec=0.743, F1=0.571.

Ranked by expected payoff against effort.

---

## 1. The plateau may not be statistically real (run first, lowest effort)

The test set (2023-2025) has a small positive count. If global Prec=0.500 comes from
roughly TP=18, FP=18, the Wilson 95% interval on 18/36 is approximately:

    0.50 +/- 1.96 * sqrt( (0.5 * 0.5) / 36 )  ~=  [0.34, 0.66]

Implications:
- The "ceiling at 0.500" and the western-station F1 of 0.571 may not be
  statistically distinguishable.
- The 12 rejected experiments at -2 to -5 pp are almost certainly inside the noise
  band, so "rejected" may mean "indistinguishable from baseline," not "worse."

Action:
- Pull exact TP/FP/FN counts from `data/threshold_sweep_results.csv`.
- Bootstrap the test set: resample station-days with replacement, recompute
  Prec/Rec/F1, 2000 iterations, report 2.5 / 97.5 percentiles.
- If the CI is +/- 0.15, the plateau is partly a sample-size statement and the
  paper framing must change accordingly.

This is the single most important thing to run before accepting any ceiling as
mechanistic. Roughly an afternoon.

---

## 2. Label definition audit (foundational, most likely real gain)

Every feature experiment assumes the target is clean. Check the label builder:

- Definition: is a positive `max(chl over next 28d) > 10`, or sustained exceedance?
  A single-sample max means one noisy in-situ reading flips a label to positive,
  manufacturing both unlearnable false positives and false negatives.
- Quantify: what fraction of positive labels are single-sample (one day above 10
  with neighbors below)? If high, redefine a bloom as >= 2 readings above threshold
  within a short window, or use a rolling-mean exceedance.
- Threshold cliff: 9.8 vs 10.2 ug/L are physically near-identical but opposite
  labels. Test 8 and 12 as a sensitivity check. Large metric swings mean the label
  boundary is doing the work, not the model.

Cleaner labels raise apparent precision directly by removing the penalty for
chasing instrument noise.

---

## 3. Reframe A4-2024: detect the regime, do not predict the nutrient

Current conclusion: A4 false positives are post-TMDL nitrogen depletion, and no
feature fixes it without fresh nutrient data (oracle only +1.5 pp). That conclusion
is about *predicting nutrients*. The signal actually needed is *the regime has
shifted*, which is observable from the project's own CHL and bloom history with no
nutrient sample.

Two causal features:

- Trailing decoupling ratio: at station s, the fraction of high-CHL days in a
  trailing 90-day window that did NOT produce a bloom. As N depletes, this ratio
  climbs at A4 specifically. Distinct from the rejected station-month bloom rate
  (-20.8 pp), which is a static seasonal climatology; this is dynamic and tracks
  drift.
  LEAKAGE CAVEAT (given prior bug history): the window must end at t - 28d so the
  forward label horizon is fully resolved. Otherwise this reintroduces the same bug
  class already fixed in the May 26-27 correction.

- Continuous time trend interacted with CHL and station: not era-split models
  (coarse), but a `years_since_2014` term plus a
  `chl_roll14 x years_since_2014 x is_A4` interaction. This lets a linear model
  learn that the same CHL anomaly means progressively less bloom risk at A4 over
  time. The -0.63%/yr secular decline says this signal exists; the LR has never been
  given the term to fit it.

If neither moves precision, that is the strong mechanistic-ceiling result, stated
with a regime feature in hand rather than only by ruling out nutrients.

---

## 4. The untested middle between global and per-station (partial pooling)

Two extremes were tested: one global model, and fully per-station thresholds. The
gap is partial pooling.

- Add station fixed effects (one-hot station, or western/central/eastern regime
  clusters) to the LR features. Data-rich western stations then inform offsets
  without 50 independent fits.
- Per-station thresholds are fit on val 2020-2022 and applied to test 2023-2025.
  Check threshold stability across years before trusting them. A small-sample
  per-station threshold overfits easily; if C1's optimal threshold jumps year to
  year, the 1.000 precision is luck.

---

## 5. Nonlinearity without tree overfitting

XGBoost at -33 pp is a red flag that the tree overfit a tiny positive class, not
evidence that interactions are absent. The skipped middle path: keep LR but add a
spline basis on `chl_roll14/21` (the CHL-to-bloom response is threshold-like, not
linear) plus a few hand-built interactions (`chl x month`, `salinity x temperature`).
This buys curvature with controlled degrees of freedom, the regime where the heavily
regularized LR (C=0.05) is already winning.

---

## 6. Decompose the 28-day horizon

A single binary "bloom within 28 days" lumps high-confidence near-term cases with
hard far-term ones. Predict 7 / 14 / 21 / 28 day horizons separately, then report
precision on the near-term head. This will likely show performance is already past
the plateau where the forecast is actionable, and reframes evaluation: for an
aeration alert, precision on the 7-to-14 day actionable window matters more than the
pooled 28-day number.

---

## Recommended order

1. Bootstrap CIs (Section 1) - tells you whether anything else is worth chasing.
2. Label audit (Section 2) - most likely real gain.
3. Trailing decoupling feature for A4 (Section 3).
4. Then partial pooling / splines / multi-horizon as time allows.