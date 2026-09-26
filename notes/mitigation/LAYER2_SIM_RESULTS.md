# Layer 2 results: simulated bench runs of the treatment loop (2026-09-26)

Scripts:
- `src/sim/tank_model.py`: the tank.
- `src/sim/loop_controller.py`: the ON/OFF loop.
- `src/sim/method_mc.py`: the Monte Carlo.

Parameters are in `src/sim/method_params.csv`, each with source paper ids from `notes/mitigation/scores/`. Outputs are `data/sim/method_summary.csv`, `method_mc_*.csv`, `method_design_*.csv` and `figures/sim/fig_method_*.png`.

**Status:** all five methods simulated (phase 1: seaweed and bubbles; phase 2: peroxide, curcumin and shellfish). The phase 2 summary is at the end.

**What this tests.** Layer 1 replayed the loop on water nobody treated. Layer 2 closes the loop:
- A simulated tank grows a bloom after nutrients go in on day 21.
- The treatment changes the algae, and the controller reacts to noisy daily readings.
- Each of 2,000 draws is a full simulated bench run: arms A (untreated), B (loop), C (late), D (false alarm), n = 3 tanks each, plus 2 spare tanks per arm for a power check.
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
