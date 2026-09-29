# Risk Assessment Form (3): attached pages

**Student:** Vihaan Goyal
**Project:** An Autonomous Forecast-Triggered System for Early Algal Bloom Disruption

Drafted 2026-09-28. To be reviewed with the Direct Supervisor before signing. Update this form if
any chemical, organism or activity changes (for example, if *Akashiwo sanguinea* is added).

## 1a. Hazardous chemicals, activities and devices

**Chemicals** (small, lab-scale quantities; each has a Safety Data Sheet on file):

| Chemical | Use | Hazard |
|---|---|---|
| Sodium percarbonate (pure oxygen-bleach powder, Na₂CO₃·1.5H₂O₂), ≤ 100 g | peroxide comparison arm (same active ingredient as registered pond algaecides) | oxidizer; eye irritant (can cause serious eye damage); can intensify fire with organic materials; releases washing soda (raises pH slightly) |
| Hydrogen peroxide, 3% (drugstore) | main peroxide treatment, dosed by pump (target 0.8 mg/L in tanks) | eye and skin irritant at 3% |
| Curcumin (≥ 95% curcuminoids), ≤ 25 g | natural algicide screen | low hazard; stains; dust irritant |
| Ethanol, food grade (e.g. Everclear), ≤ 100 mL | dissolves curcumin (≤ 0.1% in tanks) | flammable |
| Sodium metasilicate nonahydrate (Na₂SiO₃·9H₂O) | silicate nutrient stock | corrosive to eyes and skin (alkaline) |
| Sodium nitrate (NaNO₃) | nitrate nutrient stock | oxidizer; irritant |
| Sodium phosphate monobasic (NaH₂PO₄·H₂O) | phosphate nutrient stock | mild irritant |
| Sodium carbonate (washing soda) | carbonate/pH control arm | eye irritant |
| f/2 algae medium (trace metals, vitamins) and artificial sea salt | culture medium, seawater | low hazard at the concentrations used |
| Household bleach (sodium hypochlorite) | disinfecting cultures before disposal | corrosive; toxic gas (chloramine or chlorine) if mixed with ammonia or acids; with peroxide it releases oxygen, so keep them apart too |
| Acetone, 90% (≤ 250 mL) | extracting chlorophyll to calibrate the fluorometer | highly flammable; eye irritant; use with ventilation, no flames |
| Test-kit reagents (dissolved-oxygen, ammonia, nitrate/phosphate and low-range peroxide kits) | water tests | as each kit's SDS (some contain corrosive or toxic reagents); used as the kit directs |

**Devices and activities:**
- Mains-powered aquarium air pumps and LED grow lights, and 12 V pumps, near salt water (electrical).
- Arduino electronics with a relay and servo; soldering (burns, fumes).
- 3D printing of the sensor box (at school, under school rules).
- Heating collected seawater to ~80 °C to kill wild organisms (burns).
- Collecting seawater (and possibly *Ulva* seaweed) from the Long Island Sound shoreline (field work).
- Handling live oysters (cuts from shells).

## 1b. Microorganisms

All are **non-toxic marine microalgae** bought as identified cultures from the National Center for
Marine Algae and Microbiota (NCMA, Bigelow Laboratory). No bacteria, cyanobacteria, fungi or toxic
strains are cultured.

| Organism | Type | Use |
|---|---|---|
| *Skeletonema* sp. | diatom | main "bloom" culture (dominant Long Island Sound diatom) |
| *Thalassiosira weissflogii* | diatom | second diatom; peroxide size-selectivity control |
| *Phaeodactylum tricornutum* | diatom | backup diatom |
| *Prorocentrum micans* and *P. triestinum* | dinoflagellates | bubble and curcumin screens |
| *Nannochloropsis* or *Micromonas* sp. | small-celled alga | peroxide screen |
| *Isochrysis* sp. | microalga | food for the oyster holding tank |

**Other organisms (not microorganisms; listed for completeness):**
- brine shrimp (*Artemia*) for non-target toxicity tests;
- eastern oysters (*Crassostrea virginica*), from a licensed hatchery or seafood seller;
- sugar kelp (*Saccharina latissima*) or sea lettuce (*Ulva*).

All are invertebrates or seaweeds; **no vertebrates** are used. Collected seawater is heat-treated
before use, so wild microorganisms are not cultured.

## 2. Risks and hazards

| Hazard | Risk | Level |
|---|---|---|
| Peroxides (sodium percarbonate, 3% H₂O₂) | eye and skin irritation; percarbonate can feed a fire if mixed with organics or heated | moderate, controlled |
| Sodium metasilicate stock | eye and skin burns (strong base) | moderate, controlled |
| Ethanol | fire if near flame or heat | low (≤ 100 mL) |
| Sodium nitrate, phosphate, carbonate, curcumin | irritation; ingestion | low |
| Bleach | eye and skin burns; toxic gas if mixed with ammonia (oyster tanks) or acids; with peroxide it releases oxygen gas | moderate, controlled |
| Acetone | fire; vapour irritation | low (≤ 250 mL, ventilated, no flames) |
| Electricity near salt water | electric shock | moderate, controlled |
| Soldering; heating seawater | burns; solder fumes | low |
| Microalgae cultures | non-pathogenic; minor irritation if splashed in eyes | low |
| Oysters | cuts from shells; they can carry bacteria or toxins if eaten | low |
| Shoreline collection | slips, falls, cold water, weather | low, controlled |
| Environmental release | cultured algae, treated water, seaweed or animals entering the Sound; harm to non-target organisms | low, controlled |

**Overall: low to moderate,** and acceptable with the precautions in item 3.

## 3. Safety precautions and procedures
- **Supervision:** the Direct Supervisor is present for all chemical preparation and all work with sodium percarbonate, bleach and ethanol.
- **Protective equipment:** splash goggles, nitrile gloves and a lab coat or apron whenever chemicals, cultures or treated water are handled. Wash hands after every session. No food or drink in the work area.
- **Chemicals:**
  - Buy and use small quantities only, and review each SDS before first use.
  - Store sodium percarbonate dry in a closed, labeled container, away from heat, organics and acids; dissolve it fresh on the day of use.
  - Keep ethanol away from flames and heat sources.
  - Keep stock solutions labeled with contents, concentration and date, refrigerated and out of reach.
  - Weigh powders slowly to avoid dust.
  - Never mix bleach with ammonia-containing water (oyster tanks), acids or peroxide; disinfect each separately.
- **Dose limits used** (these are planning limits, not proof of safety; the brine shrimp tests measure harm directly):
  - peroxide: 0.8 mg/L per pulse in the tanks, at most 3 pulses, a new pulse only if the residual is ≤ 0.5 mg/L, emergency stop above 2.8 mg/L. Published non-target values: krill LC50 0.86 mg/L, *Moina* LC50 2 mg/L, *Daphnia* no-effect 3 mg/L. The **screen** doses go up to **6.4 mg/L** in 200 mL flasks, to map the dose-response;
  - curcumin: tank ladder 1 → 2.5 mg/L (cap 2.5; zebrafish larval LD50 1.8-2.8 mg/L, so 2.5 is not assumed safe). The **screen** doses go up to **10 mg/L** in flasks;
  - the control system automatically stops treatment if pH leaves 7.6-8.6 (9.0 for seaweed) or dissolved oxygen drops below 4 mg/L.
- **Electrical:**
  - Every mains device is plugged into a GFCI outlet or power strip, with drip loops on all cords.
  - Electronics are mounted above and away from water; sensors are low-voltage (5 V).
  - Power is unplugged before hands go into a tank.
- **Soldering and heating:** lead-free solder in a ventilated area; heat-resistant gloves and a stable hot plate for heating seawater, which is left to cool before handling.
- **Cultures:** clean technique, labeled flasks, and spills wiped with 10% bleach.
- **Animals:**
  - Oysters come from a licensed hatchery or seafood seller; there is no wild harvest.
  - Gloves are worn when handling shells, and a humane-care log is kept.
  - Animals are never eaten and never released.
- **Field work (seawater collection):**
  - From a public shoreline, with an adult present, in calm weather and daylight.
  - No wading beyond knee depth, no boats; water shoes are worn.
  - No permit is required to collect seawater. *Ulva* is collected only where CT DEEP rules allow, or bought instead. Shellfish are purchased, not collected.

## 4. Disposal
- **Cultures and treated tank water:**
  - Peroxide-treated water is held until test strips read below 0.5 mg/L.
  - All algae-containing water is then disinfected with household bleach: **1 part bleach to 9 parts culture water** (10% bleach by volume), 30 min, and flushed down a lab sink with plenty of running water. Oyster-tank water is disinfected separately and never mixed with other waste (ammonia + bleach).
  - **Nothing goes into the Sound, a storm drain or the ground.**
- **Chemicals:** leftovers go back to the school's chemical storage or are disposed of under the school's chemical hygiene plan, as the supervisor directs. Small amounts of dilute curcumin/ethanol solution are handled the same way.
- **Seaweed, brine shrimp and oysters:** frozen or bleached, then bagged in the trash, or as the supplier or supervisor directs. None are released or eaten.
- **Filters, pipette tips and gloves:** bagged in the regular trash after contact with bleach.

## 5. Sources of safety information
- Safety Data Sheets from the manufacturer or supplier for every chemical in item 1a.
- Society for Science, *International Rules: Guidelines for Science and Engineering Fairs 2026-2027*.
- NCMA (Bigelow Laboratory) culture-handling guidance, supplied with the strains.
- The school's chemical hygiene plan, and guidance from the Direct Supervisor.
- Published non-target thresholds used to set the safe doses:
  - hydrogen peroxide: Reichwaldt et al. 2011; Thoo et al. 2020;
  - curcumin: Devillier et al. 2025; zebrafish larval data.
- CT DEEP and CT Department of Agriculture (Bureau of Aquaculture) rules on seaweed and shellfish collection.
