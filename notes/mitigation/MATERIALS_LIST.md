# Materials list, by experiment

Written 2026-09-26 from `EXECUTION_PLAN.md` §6-8 and the method docs. **Updated 2026-09-28:**
- every item now says what it does and why we need it;
- the make-or-break fixes (`EXECUTION_PLAN.md` §11) are added;
- the electronics match the Arduino alerter actually being built.

Prices are estimates. **Borrow first:** ask the sponsor for the microscope, scale, glassware and
pH/DO meters before buying.

Current plan:
- five **screens** (small flasks, days);
- two **full loop runs** (tanks, weeks): **seaweed** and **shellfish**.

## 0. Shared kit (buy once, used by every experiment)

**Electronics: the alerter** (details and links in `hardware/alerter_uno/README.md`)

| Item | Qty | Approx. | What it does | Why we need it |
|---|---|---|---|---|
| Arduino Uno + breadboard, LEDs, buzzer, wires | 1 (have; a 2nd Uno planned) | $0-25 | The "brain": runs the ON/OFF rules, lights the status LEDs, beeps | It *is* the control loop: it decides when a treatment goes in and comes out, the same way every time |
| Relay + PN2222A transistor + 1N4007 diode | 1 (have) | $0 | An electrically controlled switch; the transistor lets the Arduino drive it, and the diode protects the Arduino from the relay's voltage kick | Lets a 5 V Arduino switch a 12 V pump (or other device) on and off automatically |
| 12 V pump + tubing + 12 V 2 A adapter | 2 pumps / 1 kit / 1 (ordered) | $27 | A diaphragm pump: moves air or water when the relay closes | Circulates tank water (e.g. through the sensor) and runs aeration; it can't meter microdoses |
| **Peristaltic dosing pump** (12 V, with silicone tubing) | 1 | $15-25 | Pushes a measured volume each time it runs; calibrated by weighing what it delivers | Doses the peroxide and curcumin working solutions in the loop runs (a few mL per 10 L tank) |
| Servo motor | 1 | $5 | Motor that rotates to a set angle | Lowers and lifts the seaweed panel or shellfish bag on ON and OFF |
| DS18B20 waterproof temperature sensor + 4.7 kΩ resistor | 1+ (ordered) | $10 | Measures water temperature | Temperature is a model input, and a safety check: pump heat, and kelp must stay cool |
| pH module (probe + board) + pH 6.86 / 9.18 buffer powder | 1 / 12-pack (ordered) | $25 | Measures how acidic or basic the water is; the buffers calibrate it | Seaweed and percarbonate raise pH, and the loop must stop above pH 9.0 or outside 7.6-8.6 |
| **DIY fluorometer:** TSL2591 light sensor + blue LED + red gel filter + 3D-printed dark box + cuvettes | 1 set (ordered; box printed at school) | $45 | The blue LED makes chlorophyll glow red; the gel blocks the blue; the sensor measures the red glow in the dark box | **The main measurement.** Chlorophyll glow is how the loop "sees" the algae every day, without a lab machine |

**Water, algae and counting**

| Item | Qty | Approx. | What it does | Why we need it |
|---|---|---|---|---|
| Artificial sea salt + refractometer | 1 bag / 1 | $45 | Salt makes seawater; the refractometer measures salinity | The tanks copy the western Sound at salinity 27.5 (WATER_RECIPE.md); evaporation raises it, so we check and top up |
| f/2 medium (make f/4 by halving) | 1 kit | $30 | Algae "fertilizer": nitrogen, phosphorus, vitamins, trace metals | Grows the cultures, and the nutrient pulse on day 21 is what starts the bloom |
| **Cultures from NCMA:** *Skeletonema* (lead diatom), *Thalassiosira*, *Phaeodactylum* (backup), dinoflagellate *Akashiwo* / *P. triestinum*, *P. micans*, a small-celled alga | 4-6 strains | $250-400 | Living, non-toxic stand-ins for bloom algae | The "bloom" we try to stop. *Skeletonema* is the dominant diatom of Long Island Sound blooms, so results are more relevant |
| Backup culture flasks | 2 per strain | (from the flasks below) | Spare copies of every culture | If a culture crashes or gets contaminated, we restart instead of losing the run |
| Sedgewick-Rafter counting chamber + transfer pipettes | 1 / 200 | $30 | A slide with a 1 mL grid for counting cells under a microscope | Cell counts are the ground truth: the fluorometer measures glow, which treatments can distort |
| Microscope (borrow) + phone adapter | 1 / 1 | $0-15 | Magnifies the cells; the adapter lets a phone photograph them | Counting; photos are counted later in ImageJ, which cuts the daily counting time |
| Scale, 0.01 g (borrow if possible) | 1 | $20 | Weighs small amounts | Seaweed dose (grams per litre), percarbonate, curcumin, salt |
| LED grow lights + outlet timers | 2 | $60 | Light on a fixed 16:8 or 12:12 day | Algae need steady light to grow the same in every tank |
| GFCI power strip | 1 | $20 | Cuts power instantly if current leaks to water | Safety: pumps and lights near water |
| *Artemia* (brine shrimp) eggs + hatching cone | 1 | $15 | Tiny animals hatched on demand | The non-target check: if a treatment kills brine shrimp, it isn't safe |
| DO (dissolved oxygen) test kit | 1 | $30 | Measures oxygen in the water | Safety: dying algae, shellfish and seaweed at night use oxygen; the loop stops below 4 mg/L |
| **Chlorophyll reference**: 90% acetone + borrowed spectrophotometer (or a borrowed calibrated fluorometer) | 1 | $0-20 | Measures true chlorophyll in µg/L | Calibrates the DIY fluorometer (`chlk`) so C_ok and the floor are in µg/L (PROCEDURES P3) |
| Goggles, nitrile gloves, lab notebook, labels | 1 set | $20 | Protection and records | Required for chemicals, and the notebook is the official record for ISEF |

**Tanks shared by both loop runs**

| Item | Qty | Approx. | What it does | Why we need it |
|---|---|---|---|---|
| Arm A tanks (untreated) | 3 | $40 | Algae bloom with no treatment | The baseline: the treatment's effect is measured against these |
| **Pilot bloom tanks** | 2 | $25 | Get nutrients early, during warm-up, with no treatment | Prove the culture actually blooms in our tanks before the real run, and give the expected peak that arm C's start is set from. Reused as spares afterwards |

## 1. Bubbles (screen only, 4 days)

| Item | Qty | Approx. | What it does | Why we need it |
|---|---|---|---|---|
| 1 L flasks (500 mL culture each): still, low, high, **gentle** × 2 species × n = 4 | 32 | $65 | Holds each culture | Copies the Sung & Gobler setup so our result is comparable |
| Aquarium air pumps + gang manifold + needle valves + tubing | 2 | $40 | Pumps air; the valves set each flask's flow | Airflow is the "dose", and every flask in an arm must get the same flow |
| Air stones | 24 | $15 | Break the air into bubbles at the bottom | What the paper used to make the bubbles |
| Flow meter (rotameter, 0-500 mL/min) | 1 | $20 | Measures airflow | Sets 25 and 300 mL/min exactly (0.05 and 0.6 L/min per litre) |

The **gentle-bubbling control** (a few bubbles per second) adds CO₂ without stirring. Bubbling
supplies CO₂, which *helps* growth and can hide the stress effect; this arm separates the two.

## 2. Seaweed (screen + full loop run #1)

**Screen (10 days):**

| Item | Qty | Approx. | What it does | Why we need it |
|---|---|---|---|---|
| 250 mL flasks: 0, 0.5, 1, 2 g/L kelp, fake panel, pH-matched, filtrate × n = 3, + 1 seaweed-only | 22 | $40 | Small test cultures | Finds the dose that works on *our* diatom before committing tanks |
| Plastic aquarium plant (fake seaweed) | 1 | $5 | Same shape and shade as seaweed, no chemistry | Shows whether the effect is the seaweed's chemicals or just shade and structure |

**Loop run:**

| Item | Qty | Approx. | What it does | Why we need it |
|---|---|---|---|---|
| Tanks, 4-10 L (arms B, C, D) | 9 | $80 | The treated tanks | Arm B = early loop, C = reactive start, D = false alarm |
| **Seaweed-only control tank** | 1 | $10 | Kelp in medium with **no algae** | Measures chlorophyll from seaweed bits and hitchhiking microalgae, so it can be subtracted |
| Mesh cages for the kelp + servo arm | 9 / 1 | $25 | Holds the seaweed; the servo lowers and lifts it | Makes the treatment removable, so the loop can switch it ON and OFF |
| Holding tank + air pump | 1 | $30 | Keeps kelp alive between deployments | Only live seaweed works; frozen or dead seaweed worked much worse in the papers |
| **Mini fridge or cool spot** for the holding tank (borrow) + small LED | 1 | $0-60 | Keeps the kelp near 10-15 °C | Sugar kelp is a cold-water plant and starts to rot near room temperature |
| Fine nylon mesh (~50-100 µm) | 1 piece | $10 | Strains samples before the cuvette | Keeps seaweed fragments out of the fluorometer reading |
| Nitrate and phosphate test strips | 1 pack each | $15 | Measure nutrients in the water | Shows whether the seaweed also competes for food with the algae |
| Salad spinner | 1 | $10 | Spins off surface water | Gives a consistent wet weight, as the papers did, so the dose (g/L) is accurate |
| **Sugar kelp** (Yarish lab or Stonington Kelp), ~150 g; backup *Ulva* collected | ~150 g | $0-30 | The treatment itself | ~100 g for the run plus extra for the weekly blade swaps |

## 3. Peroxide (screen only, 72 h)

| Item | Qty | Approx. | What it does | Why we need it |
|---|---|---|---|---|
| 250 mL flasks: 0, 0.8, 1.6, 3.2, 6.4 mg/L × 3 species, + 3-pulse 0.8 arm, + percarbonate × 3 species, + Na₂CO₃, × n = 3 | 60 | $80 | Test cultures | A dose ladder on small and large cells tests the "only kills small cells" idea |
| Drugstore 3% H₂O₂ | 1 bottle | $3 | Liquid peroxide | **Main dosing method**: diluted to 0.1% for flasks (160 µL per 200 mL = 0.8 mg/L) and pumped in tanks (8 mL of 0.1% or 0.27 mL of 3% per 10 L) |
| Sodium percarbonate, pure (oxygen-bleach powder, no fragrance or surfactant) | 1 small tub | $10 | Dissolves into hydrogen peroxide plus washing soda | The active ingredient of registered pond algaecides; tested as the "real-world product" version at the same peroxide dose |
| **Low-range peroxide test kit** (steps below 1 mg/L) | 1 | $30-60 | Measures peroxide at low levels | Strips can't tell 0.8 from 0.5 mg/L; this confirms the dose |
| H₂O₂ test strips, 0.5-25 mg/L | 1 pack | $20 | Rough peroxide reading | The fast check for the 2.8 mg/L safety cutoff |
| **5 µm syringe filters + syringes** | 30 + 5 | $20 | Let only small cells through | Size-fractionated chlorophyll: small vs large cells, since ~2 µm cells can't be counted under a school microscope |
| Washing soda (Na₂CO₃) | 1 | $5 | The carbonate part of percarbonate, without the peroxide | Control: shows whether the effect is peroxide or just the carbonate and pH rise |

⚠ Sodium percarbonate is an oxidizer: it needs Form 3 and the supervisor present.

## 4. Curcumin (screen only, 72 h)

| Item | Qty | Approx. | What it does | Why we need it |
|---|---|---|---|---|
| 250 mL flasks: 0, 0.5, 1, 2.5, 5, 10 mg/L, ethanol-only, 2.5 mg/L in dark × n = 3, + 4 correction-curve flasks | 28 | $40 | Test cultures | Finds the lowest dose that works; the dark arm tests whether light makes it toxic |
| Curcumin ≥ 95% (supplement grade, not turmeric); record product and lot | 1 bottle | $20 | The treatment | Turmeric is mostly not curcumin; "95%" is really a mix of 3 compounds, so the lot is recorded |
| Food-grade ethanol (e.g. Everclear) | small bottle | $10 | Dissolves the curcumin | Curcumin won't dissolve in water; the ethanol-only flask checks the ethanol does nothing by itself |
| Adjustable micropipettes (10-100 µL and 100-1000 µL) + tips | 2 | $50 | Measure tiny volumes exactly | Flask doses of 50-1280 µL of working solutions (PROCEDURES P6) |
| Aluminium foil | 1 roll | $3 | Blocks light | The dark arm |

The **correction curve** (the same algae sample spiked with 0-2.5 mg/L curcumin) is needed
because yellow curcumin absorbs the blue LED light, which makes the fluorometer under-read.

## 5. Shellfish (clearance test + full loop run #2)

**Clearance test (4 hours):**

| Item | Qty | Approx. | What it does | Why we need it |
|---|---|---|---|---|
| 1 L beakers: 1 oyster each + 3 no-animal controls | 13 | $30 | One animal in a known volume | Measures litres filtered per oyster per hour. The simulation says this number decides success, and it sets how many oysters go in each tank |

**Loop run:**

| Item | Qty | Approx. | What it does | Why we need it |
|---|---|---|---|---|
| **Oyster seed ~40 mm** (Copps Island); backup: **live oysters from a seafood market** | ~50 | $30-80 | The filter feeders that remove algae | The treatment. Market oysters are the backup if seed or permits are late (never eaten, never released) |
| Tanks, 20 L (arms B, C, D) + air pumps | 9 | $120 | The treated tanks | Oysters need more water and aeration than the seaweed tanks |
| Holding tank, 20-40 L, aerated | 1 | $30 | Keeps oysters alive between deployments | Oysters go in only while the loop is ON |
| Mesh bags (oysters) + extra bags of **empty shells** | 9 + 3 | $20 | Hold the oysters; the empty-shell bags are the control | Removable treatment; the empty shells show the effect is filtering, not just shells in the water |
| Ammonia test kit (tested **daily** while oysters are in) | 1 | $15 | Measures ammonia | Oysters excrete ammonia: toxic above 0.5 mg/L, and it feeds regrowth after OFF |
| Food culture for the holding tank (*Isochrysis*, or a commercial shellfish feed) | 1 | $0-40 | Feeds oysters between uses | Starving oysters filter less and may die |

## Totals

| | Approx. |
|---|---|
| Shared kit + cultures + arm A and pilot tanks (much of the electronics already bought) | $795-1,045 |
| Bubbles | $140 |
| Seaweed | $225-325 |
| Peroxide | $180-210 |
| Curcumin | $125 |
| Shellfish | $245-335 |
| **All five** | **about $1,700-2,200 before borrowing; ~$1,200-1,500 if the sponsor lends the microscope, scale, glassware, meters and a mini fridge** |

## Open points
- **Tank size mismatch:** arm A is shared, but seaweed tanks are 4-10 L and shellfish tanks 20 L. Either make every tank 20 L (then seaweed needs ~40 g kelp per tank, ~360 g total) or give seaweed its own 3 untreated tanks. The plan now counts 24 tanks including the pilot and seaweed-only tanks.
- **Holding-tank food:** *Isochrysis* isn't on the NCMA request yet. Either add it or buy a commercial shellfish feed.
- **Cold holding for kelp:** ask the school for a spare mini fridge or a cool room before buying one.
