# Materials list, by experiment

Written 2026-09-26 from `EXECUTION_PLAN.md` §6-8 and the method docs. **Updated 2026-09-28:**
- every item now says what it does and why we need it;
- the make-or-break fixes (`EXECUTION_PLAN.md` §11) are added;
- the electronics match the Arduino alerter actually being built.

**Updated 2026-10-01:** the plan is now **aeration and peroxide only** (the device must run fully
autonomously; `EXECUTION_PLAN.md`, "Plan change 2026-10-01"). Kelp, shellfish and curcumin/ethanol
items are removed (listed at the end as dropped). Added: *Micromonas pusilla* and *Nannochloropsis*
cultures for the cell-size panel, a hemocytometer, the loop-run air supply, and the peristaltic pump
and 3% H₂O₂ reservoir for the peroxide loop run.

Prices are estimates. **Borrow first:** ask the sponsor for the microscope, scale, glassware and
pH/DO meters before buying.

Current plan:
- two **screens** (small flasks, days) on a cell-size species panel;
- two **full loop runs** (tanks, weeks): **aeration** and **peroxide**.

## 0. Shared kit (buy once, used by every experiment)

**Electronics: the alerter** (details and links in `hardware/alerter_uno/README.md`)

| Item | Qty | Approx. | What it does | Why we need it |
|---|---|---|---|---|
| Arduino Uno + breadboard, LEDs, buzzer, wires | 1 (have; a 2nd Uno planned) | $0-25 | The "brain": runs the ON/OFF rules, lights the status LEDs, beeps | It *is* the control loop: it decides when a treatment switches on and off, the same way every time |
| Relay + PN2222A transistor + 1N4007 diode | 1 (have) | $0 | An electrically controlled switch; the transistor lets the Arduino drive it, and the diode protects the Arduino from the relay's voltage kick | Lets a 5 V Arduino switch a 12 V pump (air or dosing) on and off automatically |
| 12 V pump + tubing + 12 V 2 A adapter | 2 pumps / 1 kit / 1 (ordered) | $27 | A diaphragm pump: moves air or water when the relay closes | Runs aeration and circulates tank water (e.g. through the sensor); it can't meter microdoses |
| **Peristaltic dosing pump** (12 V, with silicone tubing) | 1 (+1 spare) | $15-25 each | Pushes a measured volume each time it runs; calibrated by weighing what it delivers | **Now needed for the peroxide loop run (2026-10-01):** doses 3% H₂O₂ from the reservoir in 0.8 mg/L pulses (0.27 mL per 10 L tank) |
| DS18B20 waterproof temperature sensor + 4.7 kΩ resistor | 1+ (ordered) | $10 | Measures water temperature | Temperature is a model input, and a safety check: pump heat must not warm the tank more than 2 °C |
| pH module (probe + board) + pH 6.86 / 9.18 buffer powder | 1 / 12-pack (ordered) | $25 | Measures how acidic or basic the water is; the buffers calibrate it | Bubbling (CO₂) and percarbonate change pH, and the loop must stop above pH 9.0 or outside 7.6-8.6 |
| **DIY fluorometer:** TSL2591 light sensor + blue LED + red gel filter + 3D-printed dark box + cuvettes | 1 set (ordered; box printed at school) | $45 | The blue LED makes chlorophyll glow red; the gel blocks the blue; the sensor measures the red glow in the dark box | **The main measurement.** Chlorophyll glow is how the loop "sees" the algae every day, without a lab machine; it is also the main measure for the ~2 µm algae |

**Water, algae and counting**

| Item | Qty | Approx. | What it does | Why we need it |
|---|---|---|---|---|
| Artificial sea salt + refractometer | 1 bag / 1 | $45 | Salt makes seawater; the refractometer measures salinity | The tanks copy the western Sound at salinity 27.5 (WATER_RECIPE.md); evaporation (worse with bubbling) raises it, so we check and top up |
| f/2 medium (make f/4 by halving) | 1 kit | $30 | Algae "fertilizer": nitrogen, phosphorus, vitamins, trace metals | Grows the cultures, and the nutrient pulse on day 21 is what starts the bloom |
| **Cultures from NCMA:** *Skeletonema* (lead diatom), *Thalassiosira weissflogii*, *Phaeodactylum* (backup), dinoflagellate *Akashiwo* / *P. triestinum*, *P. micans*, ***Micromonas pusilla*** | 5-6 strains | $250-400 | Living, non-toxic stand-ins for bloom algae, from ~2 µm to ~50 µm | The "bloom" we try to stop, and the cell-size panel. *Micromonas* (~2 µm) was wiped out by peroxide in Randhawa et al. 2012; *Skeletonema* is the dominant diatom of Long Island Sound blooms |
| **Live *Nannochloropsis*** (reef-aquarium phytoplankton, sold as coral and rotifer food) | 1 bottle | $15-25 | A harmless 2-3 µm alga, bought live | Second small-celled alga for the size panel; its peroxide sensitivity is untested in our papers, so it is a real test. Check it under the microscope and keep a clean sub-culture (NCMA *Nannochloropsis* as backup) |
| Backup culture flasks | 2 per strain | (from the flasks below) | Spare copies of every culture | If a culture crashes or gets contaminated, we restart instead of losing the run |
| Sedgewick-Rafter counting chamber + transfer pipettes | 1 / 200 | $30 | A slide with a 1 mL grid for counting cells under a microscope | Cell counts are the ground truth for the larger cells: the fluorometer measures glow, which treatments can distort |
| **Hemocytometer** (Neubauer) + cover slips | 1 | $20 | A fine-grid counting slide for very small cells at 400× | Counts the ~2 µm *Micromonas* and *Nannochloropsis*, which are too small for the Sedgewick-Rafter slide; hard at school, so it checks the fluorometer rather than replacing it |
| Microscope with 40× objective (400×) (borrow) + phone adapter | 1 / 1 | $0-15 | Magnifies the cells; the adapter lets a phone photograph them | Counting; photos are counted later in ImageJ, which cuts the daily counting time |
| Scale, 0.01 g (borrow if possible) | 1 | $20 | Weighs small amounts | Percarbonate, sodium carbonate, salt, nutrient salts |
| Adjustable micropipettes (10-100 µL and 100-1000 µL) + tips | 2 | $50 | Measure tiny volumes exactly | Flask doses of 160-1280 µL of the peroxide working solutions (PROCEDURES P6) |
| LED grow lights + outlet timers | 2 | $60 | Light on a fixed 16:8 or 12:12 day | Algae need steady light to grow the same in every tank |
| GFCI power strip | 1 | $20 | Cuts power instantly if current leaks to water | Safety: pumps and lights near water |
| *Artemia* (brine shrimp) eggs + hatching cone | 1 | $15 | Tiny animals hatched on demand | The non-target check: if a treatment kills brine shrimp, it isn't safe |
| DO (dissolved oxygen) test kit | 1 | $30 | Measures oxygen in the water | Safety: dying algae use oxygen at night; the loop stops below 4 mg/L. Also the dawn-DO test for aeration |
| **Chlorophyll reference**: 90% acetone + borrowed spectrophotometer (or a borrowed calibrated fluorometer) | 1 | $0-20 | Measures true chlorophyll in µg/L | Calibrates the DIY fluorometer (`chlk`) so C_ok and the floor are in µg/L (PROCEDURES P3) |
| Goggles, nitrile gloves, lab notebook, labels | 1 set | $20 | Protection and records | Required for chemicals, and the notebook is the official record for ISEF |

**Untreated and pilot tanks** (one set per loop culture; shared if both screens pick the same culture)

| Item | Qty | Approx. | What it does | Why we need it |
|---|---|---|---|---|
| Arm A tanks (untreated) | 3 per culture (6) | $80 | Algae bloom with no treatment | The baseline: the treatment's effect (peak cut, or days held below `C_ok` for aeration) is measured against these |
| **Pilot bloom tanks** | 2 per culture (4) | $50 | Get nutrients early, during warm-up, with no treatment | Prove the culture actually blooms in our tanks before the real run, and give the expected peak that arm C's start and `C_ok` are set from. Reused as spares afterwards |

## 1. Aeration (screen, 4 days + full loop run #1)

**Screen (4 days):**

| Item | Qty | Approx. | What it does | Why we need it |
|---|---|---|---|---|
| 1 L flasks (500 mL culture each): still, low, high, **gentle** × 4 species (*Micromonas*, *Nannochloropsis*, *Skeletonema*, dinoflagellate) × n = 3 | 48 | $95 | Holds each culture | Copies the Sung & Gobler setup so our result is comparable; the panel shows which cell sizes aeration slows |
| Aquarium air pumps + gang manifold + needle valves + tubing | 2 | $40 | Pumps air; the valves set each flask's flow | Airflow is the "dose", and every flask in an arm must get the same flow |
| Air stones | 36 | $20 | Break the air into bubbles at the bottom | What the paper used to make the bubbles |
| Flow meter (rotameter, 0-500 mL/min) | 1 | $20 | Measures airflow | Sets 25 and 300 mL/min exactly (0.05 and 0.6 L/min per litre) |

The **gentle-bubbling control** (a few bubbles per second) adds CO₂ without stirring. Bubbling
supplies CO₂, which *helps* growth and can hide the stress effect; this arm separates the two.

**Loop run:**

| Item | Qty | Approx. | What it does | Why we need it |
|---|---|---|---|---|
| Tanks, 4-10 L (arms B, C, D) | 9 | $80 | The treated tanks | Arm B = forecast loop, C = reactive start, D = false alarm |
| Air pumps for the treated tanks (each tank's air switched by the relay), airline, check valves, air stones | 9 outlets | $60 | Bubbles each tank at 0.6 L/min per litre when the loop says ON | The treatment itself; check valves stop tank water siphoning back into the pump when it switches OFF |

The aeration outcome (days below `C_ok`, hours ON, ON episodes) comes from the alerter's CSV log and
the daily fluorometer readings; it needs no extra kit.

## 2. Peroxide (screen, 72 h + full loop run #2)

**Screen (72 h, *Artemia* to 96 h):**

| Item | Qty | Approx. | What it does | Why we need it |
|---|---|---|---|---|
| 250 mL flasks: 0, 0.8, 1.6, 3.2, 6.4 mg/L × 5 species, + 3-pulse 0.8 arm × 2 small algae, + percarbonate × 3 species, + Na₂CO₃, × n = 3 | 93 | $125 | Test cultures | A dose ladder from ~2 µm to ~50 µm cells tests the "only kills small cells" idea (H5) |
| Drugstore 3% H₂O₂ | 2 bottles | $6 | Liquid peroxide | **Main dosing method**: diluted to 0.1% for flasks (160 µL per 200 mL = 0.8 mg/L) and pumped in tanks (0.27 mL of 3% per 10 L) |
| Sodium percarbonate, pure (oxygen-bleach powder, no fragrance or surfactant) | 1 small tub | $10 | Dissolves into hydrogen peroxide plus washing soda | The active ingredient of registered pond algaecides; tested in the screen only, as the "real-world product" version at the same peroxide dose |
| **Low-range peroxide test kit** (steps below 1 mg/L) | 1 | $30-60 | Measures peroxide at low levels | Strips can't tell 0.8 from 0.5 mg/L; this confirms the dose and the ≤ 0.5 mg/L re-dose rule |
| H₂O₂ test strips, 0.5-25 mg/L | 1 pack | $20 | Rough peroxide reading | The fast check for the 2.8 mg/L safety cutoff |
| **5 µm syringe filters + syringes** | 60 + 5 | $30 | Let only small cells through | Size-fractionated chlorophyll in the mixed loop tanks: small vs large cells |
| Washing soda (Na₂CO₃) | 1 | $5 | The carbonate part of percarbonate, without the peroxide | Control: shows whether the effect is peroxide or just the carbonate and pH rise |

**Loop run:**

| Item | Qty | Approx. | What it does | Why we need it |
|---|---|---|---|---|
| Tanks, 4-10 L (arms B, C, D) | 9 | $80 | The treated tanks | Arm B = forecast loop, C = reactive start, D = false alarm |
| 3% H₂O₂ reservoir bottle (dark, capped) feeding the peristaltic pump | 1 | $5 | Holds the peroxide the pump draws from | Stable for weeks, so the device runs with at most a refill; strength checked weekly with the low-range kit |

**Dosing module, inline dilution (added 2026-10-03; `hardware/alerter_uno/README.md` stage 9).** The
bench module doses the 0.1% working dilution; the 7% stock is for the field design (one bottle to
show and test the parts with, not dosed into tanks).

| Item | Qty | Approx. | What it does | Why we need it |
|---|---|---|---|---|
| 7% H₂O₂, plain (no surfactant, fragrance or stabiliser blend) | 1 L | $15 | The field-design stock | 2.4× less volume than 3% for a 2-week service interval, and below the ~8% corrosive line; surfactants would harm non-targets |
| Opaque HDPE jug with vented cap | 1 | $10 | Holds the stock in the dark | Light and heat break peroxide down; HDPE resists it; the vent stops gas building up |
| 12 V circulation pump (bench: small aquarium pump; field: 10-20 L/min) | 1 | $15 | Draws water in and pushes it through the mixing hose | Dilutes the peroxide inline so there is no concentrated jet at the outlet |
| Intake screen (2-5 mm mesh) | 1 | $3 | Covers the circulation pump's intake | Keeps debris and animals out of the pump and the flow switch |
| Check valve (peroxide-compatible) | 1 | $4 | One-way valve between the dosing pump and the tee | Stops water pushing back into the dosing line or siphoning stock |
| Tee + 1 m mixing hose (or an inline static mixer) | 1 | $6 | Joins the dose into the water stream and mixes it | Blends the dose before the outlet (~1:150 in the field) |
| Flow switch (inline, closes on flow) | 1 | $8 | Tells the Uno that water is moving (D8) | The no-flow interlock: never dose into a dead line |
| Float switch | 1 | $4 | Closes when the jug runs low (D4) | Prints `REFILL` so the service visit is not missed |
| 2-channel 5 V relay module | 1 | $8 | Switches the dosing pump (D10) and the circulation pump (D12) | Two pumps, two independent switches |
| Peroxide-compatible tubing (silicone in the pump head; PE or PVC elsewhere) | 2 m | $6 | Carries the stock and the mix | Some rubbers and metals break peroxide down or corrode |

⚠ Sodium percarbonate is an oxidizer: it needs Form 3 and the supervisor present.

## Dropped 2026-10-01 (do not buy)

| Item | Was for | Why dropped |
|---|---|---|
| Sugar kelp / *Ulva*, mesh cages, holding tank, mini fridge, salad spinner, plastic plant, fine nylon mesh, nitrate/phosphate strips, seaweed-only tank, 22 seaweed flasks | seaweed | live stock kept cold and swapped; kelp dies back above ~18-20 °C; not autonomous |
| Oyster seed, mesh bags, empty-shell bags, 20 L tanks, oyster holding tank, ammonia kit (for oysters), *Isochrysis* / shellfish feed, 13 clearance beakers | shellfish | always filtering (not switchable), live animals, permits, stops feeding in dense blooms |
| Curcumin ≥ 95%, food-grade ethanol, aluminium foil, 28 curcumin flasks | curcumin | blinds the 470 nm fluorometer; dose overlaps zebrafish LD50; one organism tested |
| Servo motor | lowering seaweed panel / shellfish bag | nothing to lower any more (keep it if already bought) |

## Totals

| | Approx. |
|---|---|
| Shared kit + cultures (incl. *Micromonas*, *Nannochloropsis*) + arm A and pilot tanks for two cultures (much of the electronics already bought) | $945-1,205 |
| Aeration (screen + loop run) | $315 |
| Peroxide (screen + loop run) | $315-345 |
| **Both methods** | **about $1,575-1,865 before borrowing; ~$1,100-1,350 if the sponsor lends the microscope, scale, micropipettes, glassware and meters** |

## Open points
- **One dosing pump or nine?** The alerter drives one relay. Each B, C and D tank runs its own schedule, so either each treated tank gets its own relay channel and pump (an 8-channel relay module, ~$10, plus more pumps), or one alerter-driven tank is the full demonstration and the others are switched by hand at the logged times. Decide before `LOOP_PREREG.md`, and report it under autonomy.
- **Air supply for the aeration tanks:** 0.6 L/min per litre is 2.4-6 L/min per tank. Check the pumps reach that through the stones; if not, run the aeration tanks at 4 L.
- ***Nannochloropsis* purity:** aquarium cultures may carry other algae or bacteria. Check under the microscope and sub-culture before the screen.
