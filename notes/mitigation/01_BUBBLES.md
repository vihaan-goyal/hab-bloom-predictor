# Method 1: coarse-bubble aeration ("macrobubbles")

Plugs into the shared loop in `00_CONTROL_LOOP.md`. Evidence: `notes/snowball/physical.md` #22,
`notes/snowball/marine.md` #33.

## Why this method
- **Evidence:** Sung & Gobler (2026), *Journal of Environmental Management*, [doi:10.1016/j.jenvman.2026.129015](https://doi.org/10.1016/j.jenvman.2026.129015). Coarse bubbles cut *Margalefidinium polykrikoides* cell density **by more than 60%**, against under 20% for nanobubbles, and lowered its photosynthetic efficiency. Fish survived **100%** where unbubbled controls had **100% mortality**.
- ***Margalefidinium* matters locally:** it's the fish-killing "rust tide" dinoflagellate of Long Island's bays.
- **No chemicals, and switching it off removes it completely.** That answers the counselor's objection most cleanly of any method.
- **Caveats:**
  - Bench-scale only; no field trial.
  - The bubbling shifted the community toward *Prorocentrum cordatum*.
  - Gentle turbulence can *help* some algae: weak turbulence raised *Microcystis* growth by 241% in one study (`physical.md`).

**What the paper page shows (2026-09-25; it's paywalled, so only the introduction and section snippets were visible):**
- **"Macrobubbles" are bubbles > 100 µm.** Microbubbles are 0.2-100 µm and nanobubbles < 200 nm, so an aquarium air pump with an open tube or coarse stone makes macrobubbles.
- **Airflow is the dose:** "higher macrobubble flow rates more strongly inhibited cell proliferation and reduced fish kills". Test at least two flow rates.
- **Culture conditions:** strains from Flanders Bay and Shinnecock Bay, NY; GSe medium, salinity ~32, 21 °C, ~100 µmol photons, 12:12 light.
- **Two warnings that change the design:**
  1. **Diatoms may be *helped* by bubbling.** The paper's introduction notes that moderate turbulence can promote diatom growth, with damage only above a threshold. Long Island Sound blooms are mostly diatoms, so bubbles are a **dinoflagellate** method, and the bench must include a diatom check arm.
  2. **Bubbling promoted *Prorocentrum*** in bloom water. So *Prorocentrum micans*, the stand-in suggested in `00_CONTROL_LOOP.md`, is the **wrong test organism** for this method: it may grow *better*. Use it only as an "expected to resist" comparison. Pick the main stand-in dinoflagellate after asking the Gobler lab or NCMA which non-toxic species responds most like *Margalefidinium*.
- **Still unknown from this paper:** flow rates, vessel volumes, bubbling duration. The sources below cover most of this, so the Gobler PDF is **optional**, not blocking.

## Other sources (added 2026-09-25, in place of the paywalled PDF)

| Source | What it did | What it tells the design |
|---|---|---|
| Llaveria et al. 2009, *J. Phycol.* ([doi](https://doi.org/10.1111/j.1529-8817.2009.00740.x)) | Shaken cultures of the toxic dinoflagellate *Alexandrium minutum* | Turbulence **immediately paused cell division** (G2/M arrest) but killed nothing at first; **mortality appeared only after > 4 days** of continuous shaking |
| Berdalet 1992, *J. Phycol.* ([doi](https://doi.org/10.1111/j.0022-3646.1992.00267.x)) | Shaken *Gymnodinium nelsonii* | Stopping after 10 days → cells **resumed dividing at once** at ~2/3 of the normal rate; shaking > 20 days → total death |
| Sullivan & Swift 2003, *J. Phycol.* ([doi](https://doi.org/10.1046/j.1529-8817.2003.02094.x)) | 10 dinoflagellate species, 20 L tanks, quantified turbulence | **Species-specific:** *Ceratium fusus* slowed; *Alexandrium catenella*, *A. tamarense* unaffected; *Lingulodinium*, *Gymnodinium catenatum*, *A. fundyense* grew *faster* |
| Juhl & Latz, *Mechanisms of fluid shear-induced inhibition...* ([ResearchGate](https://www.researchgate.net/publication/229946931)) | *Lingulodinium polyedrum* in Couette shear chambers | Shear cuts net growth through fewer divisions and more deaths, at stresses like real ocean turbulence |
| *P. micans* turbulence result (same search set; primary source still to pin down) | *Prorocentrum micans* under turbulence | Negative growth **only at high light (332-451 µmol)**, not at 162-209. At bench light (~100) expect no effect: confirms it's the wrong main stand-in |
| Barbosa et al. 2003, *Biotechnol. Bioeng.* ([doi](https://doi.org/10.1002/bit.10657)) | Bubble columns, gas velocity vs cell death | Rising bubbles did **no damage** up to 0.076-0.085 m/s superficial gas velocity; cell death comes from **bubble formation at the outlet**, above ~30-50 m/s gas entrance velocity |
| Hu et al. 2007, *Biotechnol. Prog.* ([doi](https://doi.org/10.1021/bp070306a)) | Dinoflagellate *Crypthecodinium* in a flow-contraction device + bubble rupture | Flagella lost at 1.6 × 10⁷ W/m³; lysis only above 5.8 × 10⁷ W/m³. Dinoflagellates are damaged sub-lethally well before they burst |
| Huang et al. 2022, *Sci. Total Environ.* ([doi](https://doi.org/10.1016/j.scitotenv.2022.157400)) | Water-lifting aerators in a stratified reservoir (field) | Dinoflagellates **removed 95-97%**; chl-a < 10 µg/L; community **shifted to diatoms**. Field mechanism was mixing (deeper mixed layer, less light, cooler surface), not shear |

**What these settle:**
- **At bench scale the mechanism is a pause, not a kill.** Short bubbling stops division; death needs days. So `X` = 48 h tests suppression, and a **rebound after OFF is likely** (Berdalet: division resumed at once). The re-measure and cool-down `Y` must catch it. `MAX_ON` 192 h (8 d) is long enough to reach the > 4 d mortality window.
- **Dose can be stated in physical units without the Gobler numbers:**
  - superficial gas velocity = airflow ÷ column cross-section;
  - entrance velocity = airflow ÷ outlet area.
  - Example: 2 L/min through a 4 mm tube into an 8 cm column gives an entrance velocity of ~2.7 m/s and a superficial velocity of ~0.007 m/s. Both are far below the lethal levels in Barbosa, so an aquarium pump won't shred cells, and any effect is turbulence stress on division. Log both numbers for every column.
- **Pilot flow rates:** 0.5 and 2 L/min per column (a 4× contrast, both within a cheap pump's range).
- **The choice of species matters more than the flow rate.** Several dinoflagellates grow *faster* when stirred, so the stand-in must be screened in the pilot. The first candidate is a species published as "inhibited" (*Ceratium fusus*-type, or a *Lingulodinium* strain from NCMA).
- **Diatom warning confirmed in the field** (Huang 2022): mixing swapped dinoflagellates for diatoms. Keep the diatom check arm.

## The loop for this method

| Loop step | What happens |
|---|---|
| **Trigger** | Narragansett model `p ≥ 0.50` on the column's daily sensor means (backup: the rule trigger in `00_CONTROL_LOOP.md`) → relay switches the air pump ON |
| **Treatment** | coarse bubbles (> 100 µm; large-bore outlet, not a fine airstone) from the bottom of the column, at the **higher** of the two pilot flow rates (the paper: higher flow = stronger effect) |
| **`X` (ON time)** | **48 h**, then re-measure. This is a starting value; the bench's arm-B pilot also tests 24 h and 96 h |
| **Re-measure** | chlorophyll, cell count, DO, pH, temperature, non-target survival |
| **OFF rule** | the shared rule (`p < T_off`, `chl < C_ok`, not rising) → relay OFF |
| **`MAX_ON`** | 192 h (4 × X) |
| **Method safety limits** | water temperature rising more than 2 °C above control (pump heat); evaporation over 5% of volume (top up with fresh water to hold salinity) |

**Why 48 h:** it matches the 2-3 day timescale over which the seaweed and peroxide studies saw most
of their effect, and it's long enough to separate a real effect from a 1-day artefact. The bench tunes it.

## Bench setup
- **Columns:** 3 clear tubes per arm, about 1 m tall × 7-10 cm wide (acrylic or 2 L soda bottles stacked), artificial seawater at salinity 30, 12:12 light, 18-20 °C.
- **Culture:** non-toxic dinoflagellate (*Prorocentrum micans*); optional second series with a diatom (*Phaeodactylum*).
- **Air:** one aquarium pump per arm via a manifold, with an **open tube end or wide-bore outlet** (coarse) at the bottom and a needle valve so every column gets the same flow. Measure flow with a bubble-counter or a rotameter.
- **Extra arm worth adding:** a fine airstone at the same airflow, which replicates the paper's coarse-versus-fine contrast.
- **Controller:** ESP32 + relay module → pump; fluorometer + DO/pH/temperature sensors → state machine.

## Measurements specific to bubbles
- Airflow (L/min) per column, logged.
- Water temperature (pump heat), plus salinity by refractometer at each re-measure.
- Cell integrity under the microscope: are cells broken (shear) or intact but suppressed?

## Materials (estimates)

| Item | Approx. cost |
|---|---|
| 2 aquarium air pumps + manifold, needle valves, tubing | $40 |
| 12 clear columns (or soda bottles) + stands | $40 |
| ESP32 + relay module + wiring | $20 |
| DIY fluorometer parts (LED, photodiode, filter, op-amp) | $30 |
| pH probe + DS18B20 temperature sensor; DO test kit | $60 |
| Artificial sea salt, culture medium (f/2) | $30 |
| Culture (NCMA) | $50-100 |
| Brine shrimp eggs for the non-target test | $10 |

## Safety and forms
- No hazardous chemicals, so Form 3 probably isn't needed; check with the sponsor.
- Mains-powered pumps near water: use a GFCI outlet.
- Non-toxic culture only.

## Environment
- **Adds nothing to the water.** Side effects are community shifts (seen in the paper) and energy use.
- In a real enclosed site: noise, and stirring up sediment if bubblers sit too close to the bottom.

## Before building
- Answered from other sources: dose units, pilot flow rates, rebound risk (see "Other sources").
- Settle in the pilot, not from papers: which stand-in species is inhibited at 0.5 and 2 L/min.
- Nice to have: the Sung & Gobler 2026 numbers, to compare our flow per litre with theirs.
