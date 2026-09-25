# Method 2: retrievable seaweed panels (sugar kelp first, *Ulva* second)

Plugs into the shared loop in `00_CONTROL_LOOP.md`. Evidence: `notes/snowball/marine.md` #21-#24.
**Updated 2026-09-25 after reading the three Sylvers & Gobler papers in full** (2021, 2023, 2025;
open access, read through the browser). Tang & Gobler 2011 is paywalled and still abstract-only.

## Why this method (full-text numbers)

| Study | Target | Setup | Result |
|---|---|---|---|
| **Sylvers & Gobler 2025**, *Limnol. Oceanogr.* 70:2591 ([doi](https://doi.org/10.1002/lno.70127)) | ***Pseudo-nitzschia*, a diatom** (Long Island Sound blooms are mostly diatoms) | 250 mL flasks, f/4 medium, 15 °C, ~100 µmol photons m⁻² s⁻¹, 16:8 light; start 1-4 × 10³ cells/mL; kelp or *Ulva* at 0.5-3 g/L wet weight; counts every 24-48 h | 13-47% fewer cells at 24-48 h, **74-94% at ≥72 h**. **In the controls, exponential growth started at about 72 h; seaweed stopped the treated flasks from ever entering it.** Kelp 0.5 g/L worked on *P. multiseries* by day 7 (83%); *P. australis* needed 2 g/L. Wild bloom water: **2 g/L kelp −69 to −81%; 1 g/L not significant**. *Gracilaria* did nothing |
| **Sylvers & Gobler 2021**, *Harmful Algae* 105:102056 ([doi](https://doi.org/10.1016/j.hal.2021.102056)) | *Alexandrium catenella* (dinoflagellate) | 250 mL flasks, f/2, 15-21 °C, 100 µmol, 16:8; start 2-10 × 10² cells/mL; *Ulva*, kelp or Irish moss at 0.7-3.8 g/L | 17-74% at 2-3 d, 42-96% at about 1 week. Low densities only significant after about 6 d; at 15 °C only high *Ulva* worked by day 3. Bloom bottles (3-6 g/L): up to 95%. 300 L mesocosms at 1 g/L: kelp −73% in 48 h, *Ulva* −54% in 96 h |
| **Sylvers & Gobler 2023**, *Aquaculture* 574:739676 ([doi](https://doi.org/10.1016/j.aquaculture.2023.739676)) | *Margalefidinium* (fish-killer) | well plates with larval fish; 300 L mesocosm, 7 d | 0.17 g/L *Ulva* on ropes: **no effect until day 5**, then −68%, −90% and −92% on days 5-7. Over 24 h, *Ulva* protected fish **without** reducing cell numbers (antioxidants at the seaweed surface), and only with **direct contact**. Live beat frozen. *Gracilaria* was weak |

**What these papers settle for the design:**
- **Density:**
  - Real Long Island kelp farms measure **0.6-4.4 g/L** wet weight around the lines.
  - The papers use **1 g/L** for a moderate farm and **3 g/L** for a dense one.
  - For diatoms, **2 g/L kelp** was the level that worked on wild bloom water.
- **Timing:**
  - At 1-3 g/L, most of the effect appears by **72 h**.
  - At low density (~0.2 g/L) it takes **5-7 days**.
- **Kelp is safer than *Ulva* for pH:**
  - *Ulva* pushed closed vessels to **pH 9.0-9.5, sometimes above 10**.
  - Kelp stayed at **8.1-8.9** with about the same effect on diatoms.
  - pH isn't what does the killing: kelp worked without raising it.
- **Mechanism:** mainly allelopathy (likely phenolic compounds; the diatoms lost photosynthetic efficiency and turned pale). It's not just nutrient competition: seaweed still worked in nutrient-rich water.
- **Preparation:** cut discs or pieces from healthy blades, rinse with filtered seawater, wipe off grazers and film, **spin dry in a salad spinner**, then weigh wet mass. Live seaweed only: frozen worked much worse.
- **Important for the sensor:** in the 2021 mesocosms, **total chlorophyll did not drop** even while the target species fell 54-73%, because other algae grew in its place.
  - A bench tank with one species avoids this.
  - In mixed field water, the fluorometer can't confirm success on its own; the OFF rule must also use **cell counts of the target species**.

## The loop for this method

| Loop step | What happens |
|---|---|
| **Trigger** | Narragansett model `p ≥ 0.50` on the tank's daily sensor means (backup: the rule trigger in `00_CONTROL_LOOP.md`) → a servo or winch **lowers the seaweed panel** into the water |
| **Treatment** | fresh **sugar kelp at 2 g/L wet weight** for a diatom culture, or **1 g/L** for a dinoflagellate. *Ulva* at 1 g/L is the fallback if kelp is unavailable |
| **`X` (ON time)** | **72 h**, then re-measure (74-94% of the effect is seen at ≥72 h at these densities) |
| **Re-measure** | chlorophyll, **cell counts** (the OFF rule uses these whenever the water holds more than one species), DO day **and** night, pH, non-target survival |
| **OFF rule** | the shared rule → **lift the panel out** into the aerated holding tank |
| **`MAX_ON`** | 12 days (4 × X); the 2023 mesocosm needed 5-7 days at low density |
| **Method safety limits** | **pH above 9.0** (kelp should stay below it; *Ulva* may not, so switch to kelp, or lower the *Ulva* density); night-time DO below 4 mg/L; seaweed pale or decaying → replace it |

**Density arms for the Layer-2 pilot:** kelp 0.5, 1, 2 g/L plus a no-seaweed control, which
repeats the 2025 design on our stand-in culture.

## Bench setup
- **Vessels:** follow the papers first. **250 mL flasks** for the Layer-2 dose pilot (3-4 per arm), then 4-10 L tanks for the Layer-3 loop.
- **Conditions from the papers:** 15-18 °C, ~100 µmol photons m⁻² s⁻¹ (a small LED grow light), 16:8 light:dark, f/4 medium (half-strength f/2) at salinity ~32, starting at 1-4 × 10³ cells/mL.
- **Culture:** a non-toxic **diatom** first (*Phaeodactylum tricornutum* or *Thalassiosira*), because diatoms are the Long Island Sound bloom type and the 2025 paper shows diatoms respond. A non-toxic dinoflagellate is the second series.
- **Seaweed sourcing and timing (a real constraint):**
  - **Sugar kelp** grows over winter and is harvested April-June, so for a November-December bench, ask a **Connecticut kelp farm** for young blades or hatchery kelp.
  - ***Ulva*** is abundant in summer but scarce in winter, so collect it early if needed, and hold it in f/2 under light (the papers kept it up to a month).
- **Panel:** a mesh cage holding the weighed seaweed, lowered and lifted by a servo arm.
- **Extra control arm:** a plastic "fake seaweed" panel of the same area, which separates chemistry from shading and contact.

## Measurements specific to seaweed
- Seaweed wet weight before and after each deployment (salad-spun).
- pH at every re-measure (the key safety variable).
- Nitrate and phosphate strips (nutrient competition).
- Day and night DO.
- Cell counts by Sedgewick-Rafter every 24-48 h, as in the papers.
- Optional: photos of the cells. The papers report shrunken, pale cells before they burst, which is a nice visual for the board.

## Materials (estimates)

| Item | Approx. cost |
|---|---|
| 250 mL flasks (15) + 12-15 tanks (4-10 L) | $90 |
| Mesh cages, servo arm | $25 |
| ESP32 + servo driver | $20 |
| DIY fluorometer, pH, temperature, DO kit | $90 |
| LED grow light + timer | $30 |
| Holding tank + air pump for seaweed | $30 |
| Sea salt, f/2 medium, nitrate and phosphate strips | $45 |
| Diatom culture (NCMA) | $50-100 |
| Kelp from a CT farm (ask) or *Ulva* (collected) | $0-30 |
| Brine shrimp eggs | $10 |

## Safety and forms
- No hazardous chemicals.
- Check Connecticut DEEP rules before collecting *Ulva*.
- Never release lab seaweed or cultures into the Sound. Dispose of them by drying or bleaching.

## Environment
- Native species, nothing added, fully retrievable.
- Kelp farms also take up nitrogen, a known co-benefit in Long Island Sound.
- Risks: decaying seaweed releasing nutrients, night-time oxygen use, and high pH with *Ulva* in small volumes.

## Still unverified
- Tang & Gobler 2011 (paywalled): fresh vs dried *Ulva*, and the 7-species results.
- How far the effect reaches from a panel in open water. The papers show the fish-protection effect needs contact; cell reduction happened in 300 L mesocosms with seaweed on ropes across the surface.
