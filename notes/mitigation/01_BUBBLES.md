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
  - Bubble size and flow rate weren't in the abstract. **Read the full paper before fixing the settings.**

## The loop for this method

| Loop step | What happens |
|---|---|
| **Trigger** | Narragansett model `p ≥ 0.50` on the column's daily sensor means (backup: the rule trigger in `00_CONTROL_LOOP.md`) → relay switches the air pump ON |
| **Treatment** | coarse bubbles (large-bore outlet, not a fine airstone) from the bottom of the column |
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

## Before building: verify in the full paper
- Bubble diameter, airflow per volume, and exposure durations in Sung & Gobler 2026.
- Whether the effect held after bubbling stopped (the rebound question, which matters for `Y`).
