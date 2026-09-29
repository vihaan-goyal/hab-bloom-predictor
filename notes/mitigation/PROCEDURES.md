# Step-by-step procedures, by hypothesis

Written 2026-09-28 from `EXECUTION_PLAN.md`, `00_CONTROL_LOOP.md`, the method files,
`WATER_RECIPE.md` and `MATERIALS_LIST.md`. **Nothing starts until the Direct Supervisor has signed
the forms.** Pre-register each hypothesis (commit it) before its experiment starts.

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
1. Grow each strain in f/2 under the light (12:12 or 16:8) at 15-18 °C.
2. Keep 2 backup flasks per strain at all times.
3. **For the last transfer before any experiment, grow the culture in f/20** (one-tenth strength), so it doesn't carry extra nutrients into the test water.
4. Count the cells (P4) before inoculating, so every vessel starts with the same number of cells.

### P3. Calibrate and read the fluorometer
**Materials:** alerter (Arduino + TSL2591 dark box), cuvettes, culture, seawater, pipette.
1. Make a dilution series of one culture (100%, 50%, 25%, 12.5%, 0%) and read each; send `blank` for the 0% sample.
2. Count the cells in the 100% sample (P4) and fit a chlorophyll-per-cell factor (`chlk`).
3. **Reading rules:** sample every vessel at the same time each day; keep each sample in the dark for 15 minutes; strain through fine mesh if seaweed is present; read 3 times and average.

### P4. Count cells
**Materials:** microscope, Sedgewick-Rafter slide, pipettes, phone camera.
1. Mix the sample, and fill the 1 mL slide.
2. Count 10 grid squares, or photograph them and count later in ImageJ.
3. Convert the count to cells per mL, and record it next to the fluorometer reading.

### P5. Non-target test (brine shrimp)
**Materials:** *Artemia* eggs, hatching cone, 6-well plates or small cups, light.
1. Hatch brine shrimp 24-48 h ahead.
2. Put 10 nauplii into 10 mL of test water (treated) and 10 into control water; 3 replicates each.
3. Count the survivors at 24 h (and at 96 h for peroxide). Survival more than 20 points below control is a **fail**.

---

## Part 1: Screens (small flasks, days)

### S1. Bubbles
**Hypothesis:** at 0.6 L/min per litre, the dinoflagellate's cell count after 48 h is ≥ 30% below the still control, and the diatom is not reduced.

**Materials:** 32 × 1 L flasks (500 mL culture each), 2 air pumps, manifold, needle valves, tubing, air stones, flow meter, dinoflagellate (*P. triestinum*) and diatom (*Phaeodactylum*) cultures, pH probe, thermometer, DO kit, microscope.

1. Fill the flasks with 500 mL of P1 water and inoculate the same number of cells in each (P2, P4).
2. Set up 4 arms × 2 species × n = 4 flasks:
   - **still:** no air;
   - **gentle:** a few bubbles per second, which gives CO₂ without stirring;
   - **low:** 25 mL/min;
   - **high:** 300 mL/min.
3. Set each flow with the valve and flow meter, and check it daily.
4. Bubble continuously for 48 h, then stop and watch the regrowth for 48 h more.
5. **Every day:** cell count (P4), pH and temperature in every flask. At dawn after day 2, measure DO in the high and still arms.
6. **Analysis:** percent change in cells, high vs still and high vs gentle, at 48 h (mean ± 95% t-interval).

### S2. Seaweed
**Hypothesis:** 2 g/L kelp cuts diatom cells ≥ 50% vs no seaweed at 72 h; the fake panel and pH-matched controls don't.

**Materials:** 22 × 250 mL flasks, live sugar kelp (or *Ulva*), salad spinner, scale, plastic aquarium plant, sodium carbonate, fine mesh, *Skeletonema* culture, pH probe, microscope, brine shrimp.

1. **The day before:** cut the kelp pieces, rinse them in filtered seawater, and keep them cold in the holding tank so the cut edges heal.
2. Fill the flasks with 200 mL of P1 water and inoculate the same number of *Skeletonema* cells.
3. Spin-dry and weigh the kelp. Set up 7 arms × n = 3:
   - kelp at 0, 0.5, 1 and 2 g/L;
   - a **fake panel** (plastic plant, same size);
   - **pH-matched** (no kelp; sodium carbonate raises pH to match the 2 g/L arm);
   - **filtrate** (water that held kelp for 24 h, then filtered, with no kelp inside).
4. Add a **seaweed-only** flask: kelp, no algae, to measure background chlorophyll.
5. **Every 24-48 h for 10 days:** cell count (the main result), fluorometer reading after straining, and pH.
6. **At the end:** brine shrimp test (P5) on the 2 g/L water.
7. **Analysis:** percent cut vs 0 g/L at 72 h and at day 10; compare the fake-panel, pH-matched and filtrate arms.

### S3. Peroxide
**Hypothesis:** 0.8 mg/L cuts the small-celled alga ≥ 50% in 24 h, while the diatom and *P. micans* drop < 20%.

**Materials:** 57 × 250 mL flasks, 3% hydrogen peroxide, sodium percarbonate (pure oxygen-bleach powder), sodium carbonate, low-range peroxide kit and strips, 5 µm syringe filters and syringes, small-celled alga, *T. weissflogii*, *P. micans*, fluorometer, brine shrimp, goggles and gloves (supervisor present).

1. **Check the percarbonate first:** dissolve a weighed amount in plain seawater (no algae) and measure peroxide at 0, 15 min, 1 h and 24 h. This confirms how much peroxide it really gives (0.8 mg/L H₂O₂ ≈ 2.5-2.9 mg/L percarbonate). Always dissolve it fresh on the day of use.
2. Fill the flasks with P1 water. Inoculate each species separately (3 species).
3. Dose with liquid 3% H₂O₂: 0, 0.8, 1.6, 3.2 and 6.4 mg/L × 3 species × n = 3. Add a **sodium percarbonate** arm at the same peroxide dose (0.8 mg/L H₂O₂, ~2.9 mg/L percarbonate) × 3 species × n = 3, and a **sodium carbonate** control (~2.0 mg/L, the carbonate that percarbonate adds) on the small-celled alga, n = 3.
4. Measure peroxide with the low-range kit at 0, 1, 4 and 24 h.
5. **At 24 h and 72 h:** size-fractionated chlorophyll (total, and after the 5 µm filter = small cells), plus cell counts for the diatom and *P. micans*.
6. Run brine shrimp tests (P5) at **24 h and 96 h** (peroxide can cause delayed deaths).
7. **Analysis:** percent cut per species at each dose; the lowest dose that kills small cells while sparing large ones; and whether percarbonate matches liquid H₂O₂ at the same peroxide dose.

### S4. Curcumin
**Hypothesis:** the lowest dose with ≥ 30% cell reduction at 24 h is ≤ 2.5 mg/L, and brine shrimp survival at that dose, in light, is within 20 points of control.

**Materials:** 28 × 250 mL flasks, curcumin (≥ 95%), food-grade ethanol, micropipette, aluminium foil, *P. micans* and diatom cultures, fluorometer, DO kit, microscope, brine shrimp.

1. Make a curcumin stock in ethanol, so ethanol in the flasks stays below 0.1%. Record the product and lot.
2. **Correction curve:** read one algae sample with 0, 0.5, 1 and 2.5 mg/L curcumin added (the dye lowers the fluorometer reading).
3. Set up the doses: 0, 0.5, 1, 2.5, 5 and 10 mg/L, plus **ethanol-only** and **2.5 mg/L in the dark** (flasks wrapped in foil), n = 3.
4. **At 0, 6 and 24 h:** colour (fading), DO, and cell counts (the main result).
5. Run brine shrimp tests (P5) **in light** at the lowest effective dose.
6. **Analysis:** the dose-response curve, the lowest effective dose, and the light vs dark difference.

### S5. Shellfish clearance
**Hypothesis:** the measured clearance rate (L per oyster per hour) at 18 °C is within 2× of the published planning rate.

**Materials:** 13 × 1 L beakers, 10 oysters (~40 mm), diatom culture, fluorometer, timer, air stones, gloves, holding tank.

1. Starve the oysters for 12-24 h in clean seawater.
2. Fill the beakers with 1 L of diatom culture at the same density: 10 with 1 oyster each, 3 with no oyster.
3. Read chlorophyll every 30 min for 4 h (gentle aeration keeps the water mixed).
4. Clearance = volume × (drop in log chlorophyll with the oyster − drop without it) ÷ time.
5. **Result:** L per oyster per hour. This number sets how many oysters go in each tank (enough to clear 2 tank volumes per day).

**Go rule after the screens:** a method goes to a full loop run only if its screen meets its
hypothesis **and** passes the brine shrimp test.

---

## Part 2: Full loop runs (tanks, weeks)

**Materials:**
- 24 tanks (4-10 L; 20 L for shellfish): arms A, B, C, D, plus 2 pilot tanks and 1 seaweed-only tank.
- The alerter (Arduino, fluorometer, temperature and pH sensors, relay, servo or pumps), laptop with `alerter_link.py`.
- Grow lights and timers, air pumps, P1 water and nutrient stocks, *Skeletonema* culture.
- The chosen treatment (kelp panels, or oyster bags, or a pump-dosed method).
- Microscope, DO kit, ammonia kit (shellfish), brine shrimp.

**Setup (one run per method; arm A is shared):**
1. **Days −7 to 0:** calibrate the fluorometer (P3), dry-run the controller, and pre-register the run in `LOOP_PREREG.md` (commit it).
2. **Day 0:** fill all tanks with P1 water, and inoculate the same number of *Skeletonema* cells in each.
3. **Days 0-21 (warm-up):** log readings daily, with no nutrients added. On about day 7, give the **2 pilot tanks** the bloom pulse early: they show that the culture blooms and set the expected peak.
4. **Day 21:** add the **bloom pulse** to arms A, B and C: per 10 L, nitrate 1.02 mL, phosphate 1.01 mL, silicate 4.98 mL. **Arm D gets none.**
5. **Days 21-40 (bloom phase):** the loop runs each tank's treatment by its own rule:
   - **A:** never treated.
   - **B:** switches ON by the forecast (or by the rule trigger if the model is still silent 2 days after it). It re-measures every X days and switches OFF when chlorophyll is below C_ok and not rising, when it falls 2 days below 80% of warm-up, or on a safety stop.
   - **C:** switches ON when chlorophyll reaches 50% of the expected peak (from the pilot), then follows the same OFF rule.
   - **D:** forced ON on day 21 with no bloom, for one full episode.
6. **Days 40-45 (cool-down):** keep logging, with no new ON switches.
7. **Throughout:** fluorometer daily (P3 rules); cell counts every 2 days, and daily around ON and OFF (P4); pH, temperature and DO daily; ammonia daily for shellfish; log every time a human has to step in.

**Hypotheses and what decides each one:**

| Hypothesis | What we compare | Pass if |
|---|---|---|
| **H1a** early loop works | peak chlorophyll and cells, arm B vs arm A | B's peak is ≥ 50% below A's (mean ± 95% t-interval, n = 3) |
| **H1b** early beats reactive | peak cut, arm B vs arm C | B's cut is larger than C's |
| **H2** false alarm is safe | brine shrimp survival (P5), arm D vs arm A, at each re-measure | D is within 20 points of A |
| **H3** regrowth after OFF (reported) | days from B's last OFF until chlorophyll is back above C_ok | no pass mark; it's measured and reported |
| **H4** trim, don't remove | arm B's lowest chlorophyll vs its warm-up level; daytime DO | B never falls below 80% of warm-up, and daytime DO stays at or above warm-up |

**Also reported:** treatment used (ON hours or dose) in B and C, treatment per percent of peak
cut, safety stops, and human interventions per week (autonomy).

**After each run:** analyse with `src/lab/analyze_lab.py`, dispose of everything per Form 3, and
update `SCIENTIFIC_METHOD.md`.
