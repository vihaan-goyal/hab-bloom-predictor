# Pre-registration: does the model beat the calendar? (written 2026-09-28, before running)

**Question.** Does the locked 21-day model rank bloom risk better than a calendar forecast built
only from past years?

**Why this test.** On the single 2023-25 test split (65 events), the 28-day model beat a
station-month calendar baseline by +0.039 AUC, one-sided p = 0.17: not significant, but that test
has little power. Walk-forward CV (`rolling_origin_cv.py --horizon 21`, test years 2016-2025,
121 events) is already run and its model is fixed. So comparing on it adds power without tuning
anything.

**Data.** `data/cv_predictions.csv` as written by `rolling_origin_cv.py --horizon 21` on
2026-09-28, after the leak fixes: out-of-fold `y_prob`, the 21-day label with unresolved windows
dropped, and `fold` = test year.

**Baseline (fixed now).** For each fold year T:
- The calendar forecast for a row is the bloom rate of its (station, month) over all rows dated
  before T - 21 days (the same purge as the model).
- With fewer than 5 such rows, the month rate across all stations is used; failing that, the
  overall past rate.
- The label is identical to the model's.

**Primary test.** Pooled out-of-fold AUC of the model minus pooled AUC of the calendar forecast,
with a paired station-year clustered bootstrap (2,000 resamples, seed 42).
- **The model beats the calendar if the one-sided p = P(difference ≤ 0) is < 0.05.**
- Also reported: the per-fold AUC difference, and the number of folds where the model wins.

**Secondary.**
- The same comparison restricted to 2023-25 folds.
- Lift at a matched alert rate: both forecasts alert on their top 10% of rows per fold.

**Whatever the result, it is reported as is.** No change to the model, label or baseline after
seeing it.

## Result (run 2026-09-28, after the rule above was written; `src/models/calendar_baseline_cv.py`, `data/rerun3_calendar_baseline_cv.log`)
- **Primary: PASS.** Pooled 2016-2025, 1,971 rows, 121 events: model AUC **0.693** vs calendar **0.616**, difference **+0.077 [+0.034, +0.121]**, one-sided p < 0.001.
- **Per fold:** the model wins 6 of 10 folds, including 2019 (52 events, +0.163). The calendar wins 2022-2025 (−0.04 to −0.10).
- **Secondary, 2023-25:** model 0.736 vs calendar 0.750, −0.013 [−0.101, +0.069], p = 0.64. A tie.
- **Lift at the top 10% of each fold:** model 2.56 vs calendar 2.81 (2023-25: 2.56 vs 3.02).

**Reading.** Over the decade the model ranks risk clearly better than a calendar built from past years. The edge is concentrated in the earlier folds and in the big 2019 bloom year. In recent years, with more calendar history to draw on, the calendar has caught up, and at the very top alerts it matches the model. Honest claim: *"better than the calendar across 2016-2025 (p < 0.001); about equal to it in 2023-25."*

---

# Pre-registration 2: calendar + conditions model (written 2026-09-28, before building or running)

**Idea.** Start from the season and adjust for this year's water. The same locked logistic
regression (C = 0.05, balanced, 35 features) gets one more input, `cal_logit`: the logit of the
station-month bloom rate (21-day label) over rows whose label had already resolved on the row's
date (date + 21 d ≤ t).
- Needs at least 5 rows; otherwise it falls back to the month-level rate, then the overall past rate.
- The rate is clipped to [0.01, 0.99].
- It is causal: known at forecast time.

**Protocol.**
- Identical to `rolling_origin_cv.py --horizon 21`: train ≤ T−2, test = T, for T = 2016-2025.
- Same label, with unresolved windows dropped.
- Development folds: 2016-2022. Held-out folds: 2023-2025. These years were already looked at
  (disclosed), so they are not a clean test; the clean test is the 2026 season.

**Decision rules, fixed now:**
1. **Adopt** the hybrid as the forecast model only if, on the 2016-2022 development folds, its
   pooled AUC is ≥ both the locked model's and the calendar's. Point estimates; the AUC of the raw
   `cal_logit` score is the calendar.
2. **Report 2023-25 once:** hybrid minus calendar, pooled AUC with a paired station-year bootstrap.
   Claim "beats the calendar in recent years" only if the one-sided p < 0.05; otherwise say "ties".
3. No other variants are tried (no extra features, no interactions, no tuning of C). If rule 1
   fails, the locked model stays and the result is reported.
4. If adopted, freeze the hybrid for the prospective 2026 season.

## Result 2 (run 2026-09-28; `src/models/calendar_hybrid_cv.py`, `data/rerun3_calendar_hybrid_cv.log`)
- **Development 2016-2022** (78 events): locked **0.676**, hybrid 0.668, calendar 0.545.
  - The hybrid is below the locked model: −0.008 [−0.011, −0.005].
  - **Rule 1 fails, so the hybrid is NOT adopted; the locked model stays.**
- **Held out 2023-25** (reported once): locked 0.736, hybrid 0.735, calendar 0.749. Hybrid minus calendar −0.014, p = 0.64: a tie.
- **Why it doesn't help:** the locked model already carries the seasonal and site information (`month`, station latitude/longitude, the causal `chl_climatology`). Adding the calendar rate again gives the regularized LR nothing new. The recent-years tie is a real limit of the current features, not a missing calendar input.
- Per the protocol, no other variants were tried.

## Rerun 2026-10-02 after the 2024 correction (data fix, rules unchanged; `data/rerun_2024fix_calendar.log`, `data/rerun_2024fix_hybrid.log`)
2024 chlorophyll is now on DEEP's corrected (lab) scale, so the 2024 bloom days fell from 13.3% to 4.1%, and pooled events from 121 to 94.
- **Primary: still PASS.** Model 0.660 vs calendar 0.573, **+0.088 [+0.042, +0.135], p < 0.001**. The model wins 6 of 10 folds.
- **Secondary, 2023-25:** model 0.602 vs calendar 0.706, −0.104 [−0.258, +0.046], p = 0.91, on 16 events. Not significant either way. The calendar is ahead.
- **Hybrid:** rule 1 still fails (development: hybrid 0.668 < locked 0.676), so it is not adopted.
- **Reading:** the decade-long edge over the calendar holds. In recent years the boat-sampled model does not beat the season. The clean check is the pre-registered 2026 season (`notes/PROSPECTIVE_2026_PREREG.md`).
