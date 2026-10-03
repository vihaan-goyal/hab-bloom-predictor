# Step-by-step procedures, by hypothesis

Written 2026-09-28 from `EXECUTION_PLAN.md`, `00_CONTROL_LOOP.md`, the method files,
`WATER_RECIPE.md` and `MATERIALS_LIST.md`. **Nothing starts until the Direct Supervisor has signed
the forms.** Pre-register each hypothesis (commit it) before its experiment starts.

**Updated 2026-10-01:** the experiments are now **aeration and peroxide only** (screens on a
cell-size species panel, then both full loop runs). The seaweed, curcumin and shellfish procedures
are marked dropped, with the reason; aeration is judged on **delay** (days held below `C_ok`, hours
ON, ON episodes). See `EXECUTION_PLAN.md`, "Plan change 2026-10-01".

## Shared procedures (used by every experiment)

### P1. Make Sound-matched seawater
**Materials:** artificial sea salt, distilled/RO water, refractometer, nutrient stocks (NaNO₃,
NaH₂PO₄·H₂O, Na₂SiO₃·9H₂O), f/2 trace metals and vitamins, scale, pipette, goggles, gloves.
1. Mix sea salt into water, adding it gradually, until the refractometer reads **27.5**.
2. Add the warm-up nutrients per 10 L: nitrate stock 0.10 mL, phosphate stock 1.08 mL, silicate stock 0.32 mL (recipes in `WATER_RECIPE.md`).
3. Add f/2 trace metals and vitamins at the normal f/2 dose.
4. Label the container with the date, salinity and "warm-up".

### P2. Grow the algae cultures
**Materials:** NCMA cultures, f/2 and f/20 medium, flasks, grow light and timer, labels.
1. Grow each strain in f/2 under the light (12:12 or 16:8) at the **run temperature, 12-15 °C** (WATER_RECIPE.md); move stock cultures kept warmer (15-18 °C) to 12-15 °C at least one transfer before an experiment.
2. Keep 2 backup flasks per strain at all times.
3. **For the last transfer before any experiment, grow the culture in f/20** (one-tenth strength), so it doesn't carry extra nutrients into the test water.
4. Count the cells (P4) before inoculating, so every vessel starts with the same number of cells.

### P3. Calibrate and read the fluorometer
**Materials:** alerter (Arduino + TSL2591 dark box), cuvettes, culture, seawater, pipettes, a chlorophyll reference (acetone extraction with a borrowed spectrophotometer, or a borrowed calibrated fluorometer).
1. Set the gain first (`gain m`; `l` if it saturates). The gain is saved with the calibration, so a later gain change means redoing steps 2-3.
2. Make a dilution series of one culture (100%, 50%, 25%, 12.5%, 0%) and read each; send `blank` for the 0% sample.
3. Measure the **reference chlorophyll in µg/L** of the 100% sample (and ideally the 50%), and fit µg/L against the fluorometer signal `fl`: the slope is `chlk` (**µg/L per signal count**; type `chlk <slope>`). C_ok, the warm-up mean and the floor are then all in µg/L.
   - Also count cells in the 100% sample (P4) and record glow per cell. That is a check, not the calibration.
   - If no µg/L reference is available, fit **cells/mL** against `fl` instead, and give C_ok, `warm` and the floor in cells/mL too. Never mix the units.
3. **Reading rules:** sample every vessel at the same time each day; keep each sample in the dark for 15 minutes; read 3 times and average.

### P4. Count cells
**Materials:** microscope, Sedgewick-Rafter slide, hemocytometer, pipettes, phone camera.
1. Mix the sample, and fill the 1 mL slide.
2. Count 10 grid squares, or photograph them and count later in ImageJ.
3. Convert the count to cells per mL, and record it next to the fluorometer reading.
4. **Small cells (~2 µm *Micromonas*, *Nannochloropsis*; added 2026-10-01):** use the hemocytometer at **400×** (dilute if crowded; count the 4 corner squares and convert by the chamber volume). These counts are hard at school and are a check on the fluorometer, not the main measure; say so in the write-up.

### P5. Non-target test (brine shrimp)
**Materials:** *Artemia* eggs, hatching cone, 6-well plates or small cups, light.
1. Hatch brine shrimp 24-48 h ahead.
2. Put 10 nauplii into 10 mL of test water (treated) and 10 into control water; 3 replicates each.
3. Count the survivors at 24 h (and at 96 h for peroxide). Survival more than 20 points below control is a **fail**.

### P6. Working dilutions for small doses (make fresh each day; label with date)
**Materials:** 10-100 µL and 100-1000 µL micropipettes with tips, 0.01 g scale, 100 mL bottles, distilled water.

Flask volumes below are **200 mL** of culture in a 250 mL flask; tanks are **10 L**.

| Working solution | How to make it | Dose | Per 200 mL flask | Per 10 L tank |
|---|---|---|---|---|
| **H₂O₂ 0.1%** (1 mg/mL) | 1 mL of 3% H₂O₂ + 29 mL distilled water | 0.8 / 1.6 / 3.2 / 6.4 mg/L | 160 / 320 / 640 / 1280 µL | 8 mL (or 0.27 mL of 3%) at 0.8 mg/L |
| **Sodium percarbonate** (1 mg/mL) | 0.10 g in 100 mL distilled water, dissolved just before use | ~2.9 mg/L (≈ 0.8 mg/L H₂O₂) | 580 µL | 29 mL |
| **Sodium carbonate** (1 mg/mL) | 0.10 g in 100 mL distilled water | ~2.0 mg/L | 400 µL | 20 mL |

- *(Curcumin stocks in ethanol: dropped 2026-10-01 with the curcumin method.)*
- The loop's pump doses tanks through a **peristaltic dosing pump** (calibrated by weighing what it delivers). The 12 V diaphragm pump in the kit moves air or water, not microdoses.
- The 0.01 g scale can't weigh the 0.6 mg a flask needs, which is why every small dose goes through a 1 mg/mL working solution.

---

## Part 1: Screens (small flasks, days)

**Species panel (both screens, added 2026-10-01), smallest to largest:** *Micromonas pusilla*
(~2 µm, NCMA), *Nannochloropsis* (2-3 µm, live reef-aquarium food; check it under the microscope and
keep a clean sub-culture), the diatom *Skeletonema*, and each screen's dinoflagellate. **The ~2 µm
cells are hard to count at school:** measure them with the fluorometer (P3; one species per flask)
and check with hemocytometer counts at 400× (P4); say so in the write-up.

### S1. Bubbles
**Hypothesis:** at 0.6 L/min per litre, the dinoflagellate's cell count after 48 h is ≥ 30% below the still control, and *Skeletonema* is not reduced. The two small algae are reported with no pass mark.

**Materials:** 48 × 1 L flasks (500 mL culture each), 2 air pumps, manifold, needle valves, tubing, air stones, flow meter, panel cultures (*Micromonas pusilla*, *Nannochloropsis*, *Skeletonema*, dinoflagellate *Akashiwo sanguinea* or *P. triestinum*), fluorometer, hemocytometer, pH probe, thermometer, DO kit, microscope.

1. Fill the flasks with 500 mL of P1 water and inoculate the same number of cells in each (P2, P4).
2. Set up 4 arms × 4 species × n = 3 flasks:
   - **still:** no air;
   - **gentle:** a few bubbles per second, which gives CO₂ without stirring;
   - **low:** 25 mL/min;
   - **high:** 300 mL/min.
3. Set each flow with the valve and flow meter, and check it daily.
4. Bubble continuously for 48 h, then stop and watch the regrowth for 48 h more.
5. **Every day:** cell count (P4; hemocytometer at 400× for the small algae, Sedgewick-Rafter for the others), fluorometer reading (P3), pH and temperature in every flask. At dawn after day 2, measure DO in the high and still arms.
6. **Analysis:** percent change in cells, high vs still and high vs gentle, at 48 h, per species (mean ± 95% t-interval); **regrowth after OFF:** days for each bubbled arm to reach the still control's 48 h density (an early estimate of how often the loop has to re-run). The species with the largest growth pause becomes the aeration loop culture.

### S2. Seaweed: dropped 2026-10-01
Live stock in a cold holding tank, swapped weekly; sugar kelp dies back above ~18-20 °C (the
summer bloom season); can't run unattended. The old procedure is in git history and `02_SEAWEED.md`.

### S3. Peroxide
**Hypothesis (restated 2026-09-28 from the source, peroxide-03):** one 1.6 mg/L dose cuts the small-celled alga ≥ 50% in 24 h while the diatoms and *P. micans* drop < 20%; one 0.8 mg/L dose gives a smaller, transient cut; and **three daily 0.8 mg/L pulses** (the loop dose; re-dose only if the residual is ≤ 0.5 mg/L) cut the small-celled alga ≥ 50% by 72 h with brine shrimp survival within 20 points of control. Tested on both small algae.

**Secondary hypothesis H5 (added 2026-10-01): sensitivity falls with cell size.** At each dose the percent cut is largest in *Micromonas* and *Nannochloropsis* (~2-3 µm), smaller in *Skeletonema*, and smallest in *T. weissflogii* and *P. micans*; the larger cells are spared at 0.8 mg/L (Randhawa et al. 2012).

**Materials:** 93 × 250 mL flasks, 3% hydrogen peroxide (and its 0.1% working dilution, P6), sodium percarbonate (pure oxygen-bleach powder), sodium carbonate, low-range peroxide kit and strips, 5 µm syringe filters and syringes, panel cultures (*Micromonas pusilla*, *Nannochloropsis*, *Skeletonema*, *T. weissflogii*, *P. micans*), fluorometer, hemocytometer, brine shrimp, goggles and gloves (supervisor present).

1. **Check the percarbonate first:** dissolve a weighed amount in plain seawater (no algae) and measure peroxide at 0, 15 min, 1 h and 24 h. This confirms how much peroxide it really gives (0.8 mg/L H₂O₂ ≈ 2.5-2.9 mg/L percarbonate). Always dissolve it fresh on the day of use.
2. Fill the flasks with 200 mL of P1 water. Inoculate each species separately (5 species).
3. Dose with the 0.1% H₂O₂ working dilution (P6): 0, 0.8, 1.6, 3.2 and 6.4 mg/L × 5 species × n = 3 (75 flasks). Add a **3-pulse arm** on each small alga (n = 3 each): 0.8 mg/L on days 0, 1 and 2, each only if that flask's residual is ≤ 0.5 mg/L. Add a **sodium percarbonate** arm at the same peroxide dose (0.8 mg/L H₂O₂, ~2.9 mg/L percarbonate) on *Micromonas*, *Nannochloropsis* and *Skeletonema*, n = 3, and a **sodium carbonate** control (~2.0 mg/L, the carbonate that percarbonate adds) on *Micromonas*, n = 3.
4. Measure peroxide with the low-range kit at 0, 1, 4 and 24 h.
5. **At 24 h and 72 h:** fluorometer reading of every flask (P3); hemocytometer counts at 400× for the small algae; Sedgewick-Rafter counts for *Skeletonema*, *T. weissflogii* and *P. micans*.
6. Run brine shrimp tests (P5) at **24 h and 96 h** (peroxide can cause delayed deaths).
7. **Analysis:** percent cut per species at each dose; the lowest dose that kills small cells while sparing large ones; **H5:** percent cut against cell size at each dose (does the ranking hold?); whether three 0.8 mg/L pulses match one 1.6 mg/L dose; and whether percarbonate matches liquid H₂O₂ at the same peroxide dose. The small alga with the clearest cut becomes the peroxide loop culture.

### S4. Curcumin: dropped 2026-10-01
Its yellow colour absorbs the ~470 nm excitation light and blinds the fluorometer (false "bloom
gone", early OFF); the effective dose (≥ 3 mg/L) overlaps the zebrafish larval LD50 (1.8-2.8 mg/L);
one organism tested. See `04_CURCUMIN.md`.

### S5. Shellfish clearance: dropped 2026-10-01
Always filtering (not switchable), live animals, permits, and feeding stops in dense blooms. See
`05_SHELLFISH.md`.

**Go rule after the screens (changed 2026-10-01):** both methods go to a loop run. Each screen
chooses its loop's culture; a method whose screen fails the brine shrimp test does not go to a loop
run.

---

## Part 2: Full loop runs (tanks, weeks)

**Two runs at the same time (2026-10-01): aeration and peroxide.**

**Materials:**
- 28 tanks (4-10 L): for each method, arms A, B, C and D (3 tanks each) plus 2 pilot tanks. If both screens pick the same culture, arm A and the pilots are shared (23 tanks).
- The alerter (Arduino, fluorometer, temperature and pH sensors, relay), laptop with `alerter_link.py`.
- **Aeration:** relay-switched air pumps, airline, check valves and air stones for the 9 treated tanks (0.6 L/min per litre).
- **Peroxide:** 12 V peristaltic dosing pump (calibrated by weight), a 3% H₂O₂ reservoir bottle, low-range peroxide kit and strips, 5 µm syringe filters.
- Grow lights and timers, P1 water and nutrient stocks, the loop cultures chosen by the screens (aeration: the dinoflagellate; peroxide: the small alga mixed with *Skeletonema*).
- Microscope, hemocytometer, Sedgewick-Rafter slide, DO kit, brine shrimp.

**Setup (one run per method; both run on the same dates):**
1. **Days −7 to 0:** calibrate the fluorometer (P3) and the peristaltic pump (by weight), dry-run the controller, and pre-register both runs in `LOOP_PREREG.md` (commit it), including the aeration delay outcome.
2. **Day 0:** fill all tanks with P1 water, and inoculate the same number of cells of that method's culture in each.
3. **Days 0-21 (warm-up):** log readings daily, with no nutrients added. On about day 7, give the **2 pilot tanks** of each culture the bloom pulse early: they show that the culture blooms and set the expected peak.
4. **Day 21:** add the **bloom pulse** to arms A, B and C: per 10 L, nitrate 1.02 mL, phosphate 1.01 mL, silicate 4.98 mL. **Arm D gets none.**
5. **Days 21-40 (bloom phase):** the loop runs each tank's treatment by its own rule:
   - **A:** never treated.
   - **B:** switches ON by the forecast (or by the rule trigger if the model is still silent 2 days after it). It re-measures every X days and switches OFF when chlorophyll is below C_ok and not rising, when it falls 2 days below 80% of warm-up, or on a safety stop. A new alert after OFF starts a new episode (a rerun). Alerter settings: `mode H`, `warm <warm-up mean>`, `floor 0.8`, `cok <50% of the pilot peak>`, `x <X>` (aeration: `x 2`; peroxide: `x 1`, `maxon 3`).
   - **C:** switches ON when chlorophyll reaches 50% of the expected peak (from the pilot), then follows the same OFF rule.
   - **D:** forced ON on day 21 with no bloom, for one full episode, with the floor switched off (`floor 0`).
6. **Days 40-45 (cool-down):** keep logging, with no new ON switches.
7. **Throughout:** fluorometer daily (P3 rules); cell counts every 2 days, and daily around ON and OFF (P4); pH, temperature and DO daily; peroxide residual before each pulse (peroxide tanks); log every time a human has to step in.
8. **Aeration outcome log (added 2026-10-01), per tank:** each day, whether chlorophyll is below C_ok; the day it first exceeds C_ok; hours the air pump was ON (from the alerter log); the number of ON episodes; days from each OFF back to C_ok (H3).
9. **Peroxide reservoir:** check its strength weekly with the low-range kit and refill it if needed (the one allowed maintenance; log it).

**Hypotheses and what decides each one:**

| Hypothesis | Method | What we compare | Pass if |
|---|---|---|---|
| **H1-delay** bloom held back (primary for aeration, 2026-10-01) | aeration | days below C_ok from nutrients-in to day 40, arm B vs arm A (and vs C); with hours ON and ON episodes | B's mean days below C_ok is longer than A's (Welch 95% interval of B − A above 0, n = 3) |
| **H1a** early loop cuts the peak (primary for peroxide; secondary for aeration) | both | peak chlorophyll and cells, arm B vs arm A | B's peak is ≥ 50% below A's (mean ± 95% t-interval, n = 3) |
| **H1b** early beats reactive | both | peak cut (aeration: also days below C_ok), arm B vs arm C | B's cut is larger than C's |
| **H2** false alarm is safe | both | brine shrimp survival (P5), arm D vs arm A, at each re-measure | D is within 20 points of A |
| **H3** regrowth after OFF (reported) | both | days from each B OFF until chlorophyll is back above C_ok | no pass mark; for aeration it tells how often reruns are needed |
| **H4** trim, don't remove | both | arm B's lowest chlorophyll vs its warm-up level; daytime DO | B never falls below 80% of warm-up, and daytime DO stays at or above warm-up |
| **H5** size selectivity (screen; also checked in the mixed peroxide tanks) | peroxide | small-cell vs large-cell chlorophyll (5 µm filter) in arm B | the small alga falls more than *Skeletonema* |

**Also reported:** treatment used (ON hours or dose) in B and C, treatment per percent of peak
cut, safety stops, and human interventions per week (autonomy).

**After each run:** analyse with `src/lab/analyze_lab.py`, dispose of everything per Form 3, and
update `SCIENTIFIC_METHOD.md`.
