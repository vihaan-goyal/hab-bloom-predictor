# Method 2: retrievable seaweed panels (*Ulva*, sugar kelp)

Plugs into the shared loop in `00_CONTROL_LOOP.md`. Evidence: `notes/snowball/marine.md` #21-#24,
`notes/snowball/natural_compounds.md`.

## Why this method
Seaweeds release compounds (allelopathy) and compete for nutrients. They suppress bloom species, and
they're native, removable, and already grown on Long Island Sound shellfish and kelp farms.

| Study | Seaweed vs species | Result |
|---|---|---|
| Tang & Gobler 2011, *Harmful Algae* ([doi](https://doi.org/10.1016/j.hal.2011.03.003)) | *Ulva lactuca* vs 7 HAB species, incl. Long Island brown tide | lysed or inhibited all 7; often more than 50% fewer *Aureococcus* in about 48 h in field bottles |
| Sylvers & Gobler 2021, *Harmful Algae* ([doi](https://doi.org/10.1016/j.hal.2021.102056)) | sugar kelp, *Ulva*, Irish moss vs *Alexandrium catenella* | 17-74% in 2-3 d, 42-96% in about a week; mesocosm: kelp −73% in 48 h, *Ulva* −54% in 96 h; kept mussel saxitoxin below the closure limit (71.8 vs 93.5 µg/100 g) |
| Sylvers & Gobler 2023, *Aquaculture* ([doi](https://doi.org/10.1016/j.aquaculture.2023.739676)) | *Ulva* and others vs *Margalefidinium* | 0.2 g/L *Ulva* cut wild *Margalefidinium* 68-92%; protected larval fish, **but only in close proximity** |
| Sylvers & Gobler 2025, *Limnol. Oceanogr.* ([doi](https://doi.org/10.1002/lno.70127)) | kelp, *Ulva*, *Gracilaria* vs *Pseudo-nitzschia* (a diatom) | 13-47% at 24-48 h, 74-94% at ≥72 h; kelp at 2 g/L −69-81% in field bottles; *Gracilaria* not effective |

**Caveats:**
- The studies were read at abstract level. The 2011 study came via a search summary.
- One invasive red seaweed *raised* *Alexandrium* toxin per cell (Barriuso 2026, `marine.md`).
- The protective effect needs the seaweed **close to** the bloom.
- *Ulva* itself can bloom as a nuisance ("green tides"), so remove it after use.

## The loop for this method

| Loop step | What happens |
|---|---|
| **Trigger** | Narragansett model `p ≥ 0.50` on the tank's daily sensor means (backup: the rule trigger in `00_CONTROL_LOOP.md`) → a servo or winch **lowers the seaweed panel** into the water |
| **Treatment** | fresh seaweed held in a mesh cage or on lines, at a set density |
| **`X` (ON time)** | **72 h**, then re-measure. Most studies show the large reductions at 72 h or later (74-94% for *Pseudo-nitzschia*) |
| **Re-measure** | chlorophyll, cell count, DO (day **and** night: seaweed makes oxygen by day and uses it at night), pH (seaweed raises pH), non-target survival |
| **OFF rule** | the shared rule → **lift the panel out** and let it drain back into a holding tank |
| **`MAX_ON`** | 12 days (4 × X) |
| **Method safety limits** | pH above 8.8; night-time DO below 4 mg/L; seaweed turning pale or decaying (dying seaweed releases nutrients, which feed blooms): swap it for fresh |

**Density:** start at **1 g/L fresh weight** (between the 0.2 g/L *Ulva* result and the 2 g/L kelp
result). The bench also runs 0.2 g/L and 2 g/L as a dose-response.

## Bench setup
- **Tanks:** 3 per arm, 4-10 L, artificial seawater at salinity 30, 12:12 light, 16-18 °C.
- **Culture:** non-toxic dinoflagellate (*Prorocentrum micans*) and/or diatom (*Phaeodactylum*, the stand-in for *Pseudo-nitzschia*).
- **Seaweed:**
  - *Ulva* collected from a Connecticut beach. Rinse it, sort out attached animals, and hold it in a separate aerated tank.
  - Sugar kelp is seasonal. Local kelp farms may give or sell it; *Ulva* is the easy default.
  - Weigh it blotted dry for "fresh weight".
- **Panel:** a plastic mesh cage holding the seaweed, hung from a servo arm or a small winch so the controller can lower and lift it.
- **Extra control arm:** a **plastic "fake seaweed" panel** at the same size. It separates chemistry and nutrient competition from simple shading and physical contact.

## Measurements specific to seaweed
- Seaweed fresh weight before and after each deployment (did it grow, or decay?).
- Nitrate and phosphate test strips at re-measure: is part of the effect just nutrient competition?
- Day and night DO.

## Materials (estimates)

| Item | Approx. cost |
|---|---|
| 12-15 tanks (4-10 L) + lids | $60 |
| Mesh cages, line, servo or small winch | $30 |
| ESP32 + servo driver | $20 |
| DIY fluorometer, pH, temperature, DO kit | $90 |
| Holding tank + air pump for the seaweed | $30 |
| Sea salt, f/2 medium, nitrate and phosphate strips | $45 |
| Culture (NCMA) | $50-100 |
| Brine shrimp eggs | $10 |

## Safety and forms
- No hazardous chemicals.
- Collecting *Ulva*: check Connecticut DEEP rules on collecting seaweed at the chosen beach. It's usually fine in small amounts, but confirm.
- Don't release lab seaweed or culture back into the Sound. Dispose of it by drying or bleaching.

## Environment
- Native species, nothing added, fully retrievable.
- Seaweed farms also take up nitrogen, a known co-benefit in Long Island Sound.
- Risks: decaying seaweed releasing nutrients if left in too long, and night-time oxygen use.

## Before building: verify in the full papers
- Seaweed densities and exposure times in Sylvers & Gobler 2021/2023/2025.
- Whether fresh, living seaweed or dried powder was more effective (Tang & Gobler 2011 tested both).
- The "close proximity" requirement: how far from the panel does the effect reach? It sets how many panels a real site needs.
