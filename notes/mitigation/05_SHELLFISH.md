# Method 5: deployable shellfish bags (clams or oysters)

Plugs into the shared loop in `00_CONTROL_LOOP.md`. Evidence: `notes/snowball/plants_grazers.md`
#26-#36.

## Why this method
- **Field result:** Gobler et al. 2022, *Frontiers in Marine Science* ([doi:10.3389/fmars.2022.911731](https://doi.org/10.3389/fmars.2022.911731), open access). **3.2 million hard clams** (~27 per m²) were planted in 64 sanctuary plots in Shinnecock Bay, NY, 2012-2019. The time for the bay's clams to filter its whole volume fell from up to ~3 months to as low as 10 days. **No brown tides from 2017 to 2021** (below 10,000 cells/mL), after peaks of 0.3-1.9 million cells/mL in 2007-2016. Chlorophyll fell and eelgrass expanded.
  - It's the strongest *field* result of any low-impact method, and it's next door to Long Island Sound.
  - It is correlational at the whole-bay scale.
- **Nutrient co-benefit:** oyster aquaculture already removes 1.3-2.7% of Long Island Sound's nutrient inputs (Bricker et al. 2018).

**Caveats:**
- Filter feeders act over **days to years**, not hours, which fits a slower loop.
- **They accumulate toxins.** Oysters stored microcystin, and shellfish take up saxitoxin and domoic acid. Animals used for treatment must **never be eaten** and should be removed if a toxic species is present.
- Zebra mussels can favour *Microcystis* in low-nutrient lakes (freshwater).
- Shellfish need permits to hold or move in Connecticut waters.

## The loop for this method

| Loop step | What happens |
|---|---|
| **Trigger** | Narragansett model `p ≥ 0.50` on daily sensor means (backup: the rule trigger in `00_CONTROL_LOOP.md`) → a winch **lowers mesh bags of clams or oysters** into the treatment zone (in the bench: moves bags from a holding tank into the test tank) |
| **Density** | start at **~27 clams/m²-equivalent** scaled to tank volume (the Shinnecock density); the bench converts it to animals per litre using measured clearance rates |
| **`X` (ON time)** | **7 days**, then re-measure. Filtration works over days; the whole-bay time was ~10 days at Shinnecock |
| **Re-measure** | chlorophyll, cell count, DO, **animal health** (gaping, not closing, mortality), ammonia (shellfish excrete it) |
| **OFF rule** | the shared rule → **lift the bags out** back to the holding tank |
| **`MAX_ON`** | 28 days (4 × X) |
| **Method safety limits** | any shellfish mortality over 10%; ammonia above 0.5 mg/L; DO below 4 mg/L (shellfish respiration plus decaying algae); a toxic bloom species detected → remove the animals and discard them, never eat them |

**A faster bench version:** a **clearance-rate test** in hours. Put a known number of animals in a
known volume, measure chlorophyll every 30 min for 4 h, and calculate litres filtered per animal
per hour. This gives the number needed to plan the 7-day loop without guessing.

## Bench setup
- **Animals:** small hard clams (*Mercenaria*) or oyster seed. Buy them from a Connecticut shellfish farm or hatchery, which can advise on legal sourcing and keeping them.
- **Tanks:** 3 per arm, 20-40 L, aerated artificial seawater at salinity 28-30, 16-20 °C; a separate holding tank fed with a non-toxic alga (e.g. *Isochrysis*) between deployments.
- **Culture to "bloom":** non-toxic diatom or dinoflagellate, as in the other methods.
- **Extra control:** **empty shells** in bags, which separates filtering from simply having a structure in the water.

## Measurements specific to shellfish
- Clearance rate (L/animal/h) from the 4-h test.
- Ammonia (aquarium test kit) at each re-measure.
- Animal health log: opening, feeding, mortality.
- Biodeposits (faeces and pseudofaeces) on the tank floor. That's where the algae go, so it has to be cleaned up; in the field it feeds the sediment.

## Materials (estimates)

| Item | Approx. cost |
|---|---|
| Clams or oyster seed (farm or hatchery) | $30-80 |
| 12-15 tanks (20-40 L) + air pumps | $150 |
| Mesh bags, line, small winch | $30 |
| ESP32, fluorometer, pH, temperature, DO kit, ammonia kit | $120 |
| Sea salt, f/2, cultures | $80-130 |

## Safety and forms
- **Live vertebrates** aren't involved (shellfish are invertebrates), so no vertebrate animal forms. Still, keep a humane-care log.
- **Never eat** the animals, even after the experiment, and dispose of them as directed by the supplier or sponsor.
- Moving shellfish in or out of Connecticut waters needs a permit. **Keep everything in tanks** unless a permitted farm hosts a field version.

## Environment
- Native animals, nothing added, fully retrievable, with a nitrogen-removal co-benefit.
- Risks: toxin accumulation (they can't be eaten), and biodeposits enriching the sediment.
- The most "natural" option of the five, but also the slowest.

## Before building: verify in the full papers
- The Shinnecock clearance-rate numbers and whether the brown-tide end is attributed to clams alone or to other factors too.
- Clearance rates of hard clams versus oysters for dinoflagellates and diatoms. Some species are rejected as food, which would make the method species-specific.
