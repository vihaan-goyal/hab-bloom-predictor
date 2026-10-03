# Layer 2 results: simulated bench runs of the treatment loop (2026-09-26; re-run 2026-09-28)

> **2026-10-01:** the plan changed for autonomy reasons: the full loop runs are now aeration and peroxide (seaweed, shellfish and curcumin dropped; `EXECUTION_PLAN.md`, "Plan change 2026-10-01"). The seaweed and shellfish results below are kept as a record.

> **Read the 2026-09-28 re-run first. It supersedes every table further down, which is kept as
> history.** An audit found that the earlier runs did not match the protocol. Every number in the
> re-run section comes from `data/sim/method_summary.csv` and `data/sim/method_design_*.csv`
> (`python src/sim/method_mc.py`, 2,000 draws per method, seed 42).

## Re-run, 2026-09-28: the protocol as planned

**What changed:**
- **Peroxide is a pumped liquid pulse.** The dose is added once per ON day, only when the residual is at
  or below 0.5 mg/L, and decays with the H2O2 half-life. Before, the level was held at the target all
  day, which does not match a single pump pulse.
  - The back-test now uses direct spikes, as in the source (peroxide-03): 1.6 mg/L must cut the
    small-celled alga at least 80% at 24 h, and 0.8 mg/L must stay at or below 60% ("transient"
    inhibition at 0.8 mg/L; 24-h EC50 0.91 mg/L).
  - The fabric-bag release parameters are removed.
- **C_ok** is 50% of the expected untreated peak from the **pilot run**, pulsed on day 7 as in
  PROCEDURES. It was arm A's running peak.
- **H4 floor OFF** as planned: 2 readings in a row below 80% of warm-up, not applied to arm D.
- **The handover** is simulated: forecast arm, rule fires, model silent for 2 days, then the rule
  starts the tank.
- **MAX_ON per method:** peroxide 3 pulses, curcumin 4 pulses, the rest 4 × X.
- **The H1a interval** includes arm A's tank-to-tank spread (Welch t on log peaks). Before, A was
  treated as exact, which made the "95% interval clears 50%" chance too high.
- **Peak cuts** are measured on cell-count-like readings, so curcumin's fluorometer under-reading no
  longer inflates its cut. The loop still sees the biased fluorometer.
- **Nutrients are on the WATER_RECIPE scale:** warm-up about 1, pulse 5-16 µg chl-equivalent, so
  the untreated bloom peaks near 9 µg/L (was 88). If the bench scales the pulse up, scale `n_pulse`
  by the same factor.
- **Doses are the planned ones:** peroxide 0.8 mg/L per pulse, curcumin ladder capped at 2.5,
  shellfish stocked for 2 tank volumes a day with X = 3 d.

**Checks:**
- The controller still matches Layer 1's `run_loop` on 77,958 station-days with 0 mismatches.
- The hourly step matches `solve_ivp` within 0.30%.
- Back-test acceptance: seaweed 34%, bubbles 11%, peroxide 14%, curcumin 49%.

**Results** (n = 3 tanks per arm, forecast trigger with the handover):

| | Seaweed 2 g/L | Shellfish 2 vol/day | Peroxide 0.8 mg/L pulses | Curcumin (cap 2.5) | Bubbles, responsive sp. | Bubbles, unscreened |
|---|---|---|---|---|---|---|
| B peak cut vs A, median [5-95%] | **72%** [52, 84] | **81%** [63, 92] | **74%** [57, 83] | 63% [33, 79] | 25% [9, 48] | 10% [-16, 39] |
| ≥ 50% cut (mean), n = 3 | 97% | 100% | 99% | 78% | 4% | 1% |
| ≥ 50% cut (95% CI incl. A spread), n = 3 / 4 / 5 | 64% / 78% / 84% | 79% / 92% / 96% | 80% / 92% / 95% | 47% / 60% / 65% | 1% / 1% / 1% | 0% / 0% / 0% |
| Reactive C peak cut (starts at 50% of expected peak) | 14% | 22% | 24% | 21% | 6% | 1% |
| C starts after B (median days) | 3.0 | 3.0 | 2.7 | 6.7 | 7.3 | 7.3 |
| B beats C / by 20+ points | 100% / 100% | 100% / 100% | 100% / 100% | 100% / 92% | 99% / 48% | 70% / 22% |
| ON days B / C / D | 12 / 4 / 4 | 24 / 4 / 4 | 11 / 3 / 2 | 23 / 4 / 2 | 30 / 9 / 3 | 30 / 9 / 3 |
| Non-target harm in B | 0% | 0% | 1% | 19% | 0% | 0% |
| False-alarm arm D safe (H2) | 100% | 100% | 100% | 94% | 100% | 100% |
| B ended by the H4 floor | 39% | 93% | 0% | 0% | 0% | 0% |
| Rule trigger instead: peak cut | 55% | 65% | 62% | 50% | 22% | 7% |

**Design sweeps** (400 draws per cell):

| Method | ≥ 50% cut, mean (95%-CI version) | Non-target harm |
|---|---|---|
| **Peroxide, X = 1** | 0.8 mg/L: 99% (80%). 1.6 mg/L: 100% (91%). 3.2 mg/L: 100% (95%) | 0.8: 1%. 1.6: 62%. 3.2: 100% |
| **Curcumin, X = 1** | cap 2.5: 79% (49%). cap 5: 100% (78%) | cap 2.5: 26%. cap 5: 86% |
| **Seaweed, X = 3** | 1 g/L: 55%. 2 g/L: 96% (63%). 3 g/L: 99% (67%) | none |
| **Shellfish, X = 3** | 1 vol/day: 84% (53%). 2 vol/day: 100% (80%) | none |
| **Bubbles** | best 16% (X = 4, 0.6 L/min per L) | none |

**What it means:**
1. **Seaweed, shellfish and peroxide cut the simulated peak by about three-quarters.**
   - Seaweed 72%, shellfish 81%, peroxide 74%. With the honest interval, 3 tanks per arm gives a
     64-80% chance the CI clears 50%; **4 tanks per arm gives 78-92%.**
   - Treating early beats the reactive start in essentially every run.
2. **Peroxide at 0.8 mg/L works through repeated pulses, not one dose.**
   - One 0.8 mg/L dose gives a transient cut (back-test median 48% at 24 h), which is what the source
     paper says.
   - Up to 3 daily 0.8 mg/L pulses cut the simulated peak 74%, with 1% non-target harm. 1.6 mg/L
     harms non-targets in 62% of runs.
   - The screen is restated accordingly (EXECUTION_PLAN S3, PROCEDURES S3).
3. **Curcumin's earlier 92% was inflated** by its fluorometer artefact. Measured on cell-like
   readings it is 63%, and it still harms non-targets in 19% of runs at the 2.5 mg/L cap. It stays a
   comparison screen.
4. **Bubbles still mostly delay the bloom** (25% cut), and B hits MAX_ON in 99% of runs.
5. **The H4 floor matters for shellfish:** the oysters push chlorophyll below 80% of warm-up in 93%
   of runs, so the floor, not the C_ok rule, ends most shellfish episodes. That is the "trim, don't
   remove" rule working as intended, and a bench prediction to check.

**Caveats (in addition to those below):**
- The recipe-scale bloom peaks near 9 µg/L. The pilot run must confirm the fluorometer resolves it.
- The rule-trigger arm is always weaker than the forecast arm with the handover (for example
  seaweed 55% vs 72%).

---

## History: 2026-09-26 runs (superseded by the re-run above)


Scripts:
- `src/sim/tank_model.py`: the tank.
- `src/sim/loop_controller.py`: the ON/OFF loop.
- `src/sim/method_mc.py`: the Monte Carlo.

Parameters are in `src/sim/method_params.csv`, each with source paper ids from `notes/mitigation/scores/`. Outputs are `data/sim/method_summary.csv`, `method_mc_*.csv`, `method_design_*.csv` and `figures/sim/fig_method_*.png`.

**Status:** all five methods simulated (phase 1: seaweed and bubbles; phase 2: peroxide, curcumin and shellfish). The phase 2 summary is at the end.

**What this tests.** Layer 1 replayed the loop on water nobody treated. Layer 2 closes the loop:
- A simulated tank grows a bloom after nutrients go in on day 21.
- The treatment changes the algae, and the controller reacts to noisy daily readings.
- Each of 2,000 draws is a full simulated bench run: arms A (untreated), B (loop), C (late, in these historical runs; now reactive), D (false alarm), n = 3 tanks each, plus 2 spare tanks per arm for a power check.
- The parameters are drawn from the literature ranges and **kept only if they reproduce the paper they came from**:
  - seaweed: 13-47% at 48 h and 74-94% at 72 h (seaweed-03);
  - bubbles: 21-63% over 10 days (mixing-01);
  - both ranges widened by 10 points.

These are predictions to test on the bench, not evidence that a method works.

## Checks passed
- **Integration accuracy:** the hourly exponential step matches scipy's `solve_ivp` within 0.06% over 20 days.
- **Untreated bloom shape:** with mid values, warm-up sits at 1.4 µg/L, the peak is 88 µg/L on day 26, and chlorophyll falls to 12 µg/L by day 55.
- **Controller:** it matches Layer 1's `run_loop` on 77,958 Narragansett station-days with **0 mismatches**.
- **Back-test acceptance:** 34% of seaweed draws and 12% of bubble draws reproduce their calibration paper. The rest are rejected.

## Results (2,000 draws each, forecast trigger, n = 3)

| | Seaweed (kelp 2 g/L, X = 3 d, diatom) | Bubbles, species that responds (0.6 L/min per L, X = 2 d) | Bubbles, species not yet screened |
|---|---|---|---|
| Peak cut, B vs A (median [5-95%]) | **75% [58, 84]** | 20% [5, 41] | 7% [-13, 33] |
| Late arm C peak cut | 0% | 3% | 1% |
| **≥ 50% peak cut (mean), n = 3** | **99%** | 3% | 1% |
| ≥ 50% peak cut (95% CI lower bound), n = 3 / 4 / 5 | **81% / 92% / 95%** | 1% / 1% / 1% | 0% / 1% / 1% |
| B beats late C by 20+ points | 100% | 38% | 15% |
| H1 as written (also fewer ON days than C) | 0% | 0% | 0% |
| ON days: B / C / D | 12 / 4 / 4 | 32 / 9 / 4 | 32 / 9 / 4 |
| False-alarm arm D safe (no pH stop) | 100% | 100% | 100% |
| Rule trigger instead of the forecast: peak cut | 70% | 18% | 7% |

**Design sweep** (400 draws per cell; `fig_method_design_*.png`):

| Method | Result |
|---|---|
| **Seaweed** | The dose matters far more than X. At 2 g/L, X = 2-4 d gives a ≥ 50% cut in 99-100% of runs (CI version 78-85%). At 1 g/L it's only about 50% (CI ~22%); at 0.5 g/L never. |
| **Bubbles** | Best case X = 4 d at 0.6 L/min per L: 11% (median cut 29%). The low rate is slightly worse. |

**What drives the result** (`fig_method_tornado_*.png`):
- **Seaweed:** the diatom's growth rate matters most (faster growth = smaller cut), then the kelp's maximum strength.
- **Bubbles:** the dinoflagellate's growth rate and the late-mortality term.

## What it means
1. **Seaweed is the strongest candidate, if its lab effect carries over to our culture.**
   - At 2 g/L it cuts the simulated peak by about three-quarters, and 3 tanks are nearly always enough (81% chance the CI clears 50%; 92% with 4 tanks).
   - 1 g/L is borderline, so **keep 2 g/L**.
   - X barely matters, so X = 3 d is fine, and X = 2 d is equally good.
2. **Bubbles mostly delay the bloom instead of stopping it.**
   - The calibrated effect is a partial pause in division (a growth multiplier around 0.83), so the bloom peaks about 8 days later and about 20% lower (see `fig_method_curves.png`).
   - The loop can't switch off because chlorophyll never falls below C_ok, so B stays ON for about 32 days.
   - A ≥ 50% cut is unlikely (3%) even with a responsive species.
   - Bubbles look like the weaker full-run candidate. The second full run should probably go to shellfish (to be simulated next), with bubbles kept as a short screen.
3. **H1 as written can't pass for either method.**
   - Late treatment (arm C) starts after the peak, when the bloom is already crashing, so it is short (about 4 days) and does almost nothing (0-3% cut).
   - "B uses less treatment than C" therefore fails even when B works.
   - **Suggested wording for LOOP_PREREG.md** (the student's decision): H1a, a ≥ 50% peak cut vs A, and H1b, B's cut beats C's.
   - Reporting treatment per percent of peak cut is also more meaningful than raw ON days.
4. **The forecast trigger helps a little over the simple rule** (75% vs 70% for seaweed).
5. **Seaweed's pH safety limit wasn't reached at 2 g/L,** using the levelling-off pH rise that matches Sylvers & Gobler's 8.1-8.9. A linear pH rise, used in an earlier draft, made pH the dominant risk. Measuring pH on the bench matters for this reason.

## Caveats
- **Transfer from the calibration papers:** the seaweed result inherits the lab effect of Sylvers & Gobler on *Pseudo-nitzschia*. Two full-text records show the effect shrinking in field water (seaweed-12: over 97% in the lab vs 13-44% in field water) and species-specific responses. Our *Phaeodactylum* or *Thalassiosira* may respond less, which is why the seaweed screen comes first.
- **Model simplifications:**
  - one algal population, well mixed;
  - no nutrient uptake by the seaweed and no bacteria;
  - chlorophyll stands in for cell counts;
  - the forecast is an emulator (a persistence projection with noise), not the Narragansett model.
- **Bubble parameters** come mostly from shaker and shear studies. Only Sung & Gobler used bubbles.
- **The "B beats C by 20 points" margin** is our choice, not pre-registered.

## Phase 2: peroxide, curcumin, shellfish (2,000 draws each, forecast trigger, n = 3)

**Calibration (back-tests):**
- **Peroxide:** a single 1.6 mg/L bag on a small-celled alga must cut it ≥ 80% in 24 h (peroxide-03: > 90%, EC50 0.91 mg/L). 87% of draws accepted.
- **Curcumin:** 5 mg/L → 22-99% at 24 h, 3 mg/L → 20-70%, 1 mg/L → no effect (curcumin-01, and curcumin-02's 2022 and 2024 runs). 48% of draws accepted.
- **Shellfish:** no single calibration experiment, so all draws are used. The biggest unknown is how much of the planned clearance the animals actually deliver (20-120%, since lab maxima overestimate by up to 10×; shellfish-04, -07, -12).

**Non-target harm** = the highest peroxide or curcumin level in a tank passes a harm threshold drawn from the literature:
- peroxide 0.86-3 mg/L (krill 48-h LC50 0.86; *Moina* no-effect 1.5; *Daphnia* no-effect 3);
- curcumin 1.8-6 mg/L (zebrafish larval LD50 1.8-2.8; no harm to adult clams, crabs or urchins at 5 mg/L).

| | Peroxide bag, 1.6 mg/L (small-celled alga) | Curcumin ladder 1 → 2.5 → 5 mg/L (dinoflagellate) | Shellfish, 1 tank volume/day (diatom) |
|---|---|---|---|
| Peak cut, B vs A (median [5-95%]) | **95% [91, 98]** | **92% [78, 96]** | 31% [10, 61] |
| ≥ 50% cut (mean / 95% CI), n = 3 | 100% / 100% | 100% / 98% | 16% / 5% |
| B beats late C by 20+ points | 100% | 99% | 76% |
| ON days: B / C / D | 19 / 2 / 2 | 19 / 4 / 3 | 19 / 5 / 2 |
| **Non-target harm in B tanks** | **38%** | **91%** | 0% |
| False-alarm arm D safe | 67% | 87% | 100% |

**Design sweeps** (400 draws per cell):

| Method | Result |
|---|---|
| **Peroxide** | **0.8 mg/L** still gives a ≥ 50% cut in 100% of runs (CI version 89-99%) with **0% non-target harm**. 1.6 mg/L harms in about 36% of runs; 3.2 mg/L harms in 98% and hits the 2.8 mg/L pull limit in 78%. |
| **Curcumin** | Capping the ladder at **2.5 mg/L** keeps 76-94% of runs passing (more with a longer X) and cuts harm to about 26%. A 5 mg/L cap harms in about 90%. |
| **Shellfish** | The stocking decides it. At 1 volume/day only 19-46% pass; at **2 volumes/day** with X = 3-4 d, 94-95% (CI version 67-79%). The biggest unknown is the real clearance vs planned (Spearman +0.75), which the 4-hour clearance test measures directly. |

## What the full set means
1. **Seaweed stays the lead full run.** It gives a large cut, no non-target harm, and it's retrievable.
2. **Shellfish is the better second full run, not bubbles, if the animals are stocked for 2 tank volumes per day.**
   - The 4-hour clearance test must come first: it measures the number that decides success.
   - Bubbles mostly delay the bloom.
3. **Peroxide works only on small cells, and the dose matters for safety.**
   - Lower the target from 1.6 to **0.8 mg/L**: the simulated cut is the same and the non-target harm disappears.
   - It stays a short screen on a small-celled alga, as planned.
4. **Curcumin cuts strongly but mostly at doses that harm other organisms.** It's a comparison screen only; if it's run at all, cap the ladder at 2.5 mg/L and run the brine shrimp check in light.
5. **In every method, the late arm C does almost nothing (0-4%).** That confirms the timing claim the loop rests on: acting early matters.

**Planned changes to the method files (not applied yet):**
- `03_PEROXIDE_BAG.md`: target 1.6 → 0.8 mg/L.
- `05_SHELLFISH.md`: stock for 2 tank volumes per day, X = 3-4 d.
- `04_CURCUMIN.md`: ladder cap 5 → 2.5 mg/L.
- `EXECUTION_PLAN.md`: second full run = shellfish.

**Added caveats:**
- **Peroxide:** the model follows one small-celled population, so it can't show the cell-size selectivity the screen tests.
- **Curcumin:** its fluorometer artefact (0-30% under-reading) can make the loop think chlorophyll fell; the bench uses cell counts for this reason.
- **Shellfish:**
  - the model has no pseudofaeces and no toxin;
  - regrowth is fed by excreted ammonia;
  - "clearance" stands in for all of the animals' behaviour.

## Re-run with the reactive arm C (2026-09-28)

**What changed:**
- Arm C now starts the first day chlorophyll passes **50% of the expected untreated peak**. The expected peak comes from a simulated pilot bloom run: 2 untreated tanks per draw with the draw's parameters.
- The old "after the peak" arm is kept as `Cl` for comparison.
- H1b is now "B's cut beats C's", also reported with a 20-point margin.
- The code is in `src/sim/method_mc.py` (`pilot_run`, `C_REACT_FRAC`). Results are 2,000 draws per method, forecast trigger, n = 3; the method rows use their summary dose; shellfish is at 1 tank volume/day.

| | Seaweed | Shellfish (1 vol/day) | Peroxide | Curcumin | Bubbles (responsive sp.) |
|---|---|---|---|---|---|
| B peak cut (median) | 75% | 30% | 96% | 92% | 19% |
| **Reactive C peak cut** | **11%** | **6%** | **25%** | **21%** | **3%** |
| Old late arm (after the peak) | 1% | 0% | 1% | 4% | 3% |
| C starts after B by (median) | 4.0 d | 4.0 d | 3.0 d | 8.7 d | 9.7 d |
| B beats C | 100% | 99% | 100% | 100% | 98% |
| B beats C by 20+ points | 100% | 62% | 100% | 100% | 39% |

The other numbers (H1a, ON days, harm, H2) match the earlier run within 1-2 points.

**Sensitivity: how early does "reactive" have to be before it catches up?** (300 draws; shellfish stocked at the planned 2 volumes/day)

| C starts at … of the expected peak | 50% | 20% | 10% |
|---|---|---|---|
| Seaweed: C cut / B beats C / by 20+ | 10% / 100% / 100% | 33% / 100% / 99% | 52% / 100% / 56% |
| Shellfish: C cut / B beats C / by 20+ | 9% / 100% / 93% | 34% / 100% / 63% | 29% / 93% / 58% |

**What it means:**
- The simulated tank bloom goes from warm-up level to peak in about 5 days. A treatment started when the bloom is "visible" (50% of peak) is only ~1 day before the peak, so it can do little. B wins because it starts about 4 days earlier.
- Even a reactive manager watching closely (starting at 10-20% of peak, 2-3 days after B) gets a smaller cut than B. The gap shrinks as C gets earlier: every day of lead time counts.
- This is the bench version of the project's claim, and it is no longer a strawman comparison.
- **The bench test depends on the real bloom speed,** which the pilot bloom run measures. A slower bloom gives the reactive arm more time. Pre-register the 50% start and report the sensitivity.

**Overshoot check (H4, 2026-09-28).**
- **What the simulation shows:** seaweed and peroxide B tanks fall below 80% of their warm-up level in 91-95% of runs (low point 0.35-0.42× normal). The low comes **weeks after the treatment is OFF** (median day 54-55), never while it's ON.
- **Why it isn't a real prediction:** the model has no nutrient recycling from dead cells. Treated tanks use up their nutrients, then drift down.
- **The floor rule:** a "switch OFF below 80% of warm-up" rule (`FLOOR_ON` in `method_mc.py`) was tested. It never fired during treatment, and it only cut the false-alarm arm D short on noise, so it is off by default in the simulation.
- **Decision:** overshoot is measured on the bench instead (H4 in `00_CONTROL_LOOP.md`).
- **New caveat:** no nutrient recycling means the model can't predict late regrowth or overshoot.
