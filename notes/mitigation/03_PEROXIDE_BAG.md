# Method 3: retrievable peroxide "tea bag" (calcium peroxide in fabric)

Plugs into the shared loop in `00_CONTROL_LOOP.md`. Evidence: `notes/snowball/peroxides.md` #3,
#5, #6, #15, #18, #34, #39; Part 1 #1.

## Why this method
- **The bag:** Keliri et al. 2022 ([doi:10.1016/j.ceja.2022.100318](https://doi.org/10.1016/j.ceja.2022.100318), open access) sealed calcium peroxide (CaO₂) granules in fabric. 2 g/L released **up to 12 mg/L H₂O₂ within 24 h** and cut *Microcystis* fluorescence from 8,000 to under 1,000 RFU. The granules stay inside the bag, so it **can be pulled out**.
- **Why treating early is the whole point** (Chen 2020; Buley 2023, [doi](https://doi.org/10.1007/s11356-023-25301-4)):
  - The effective dose is about **0.03-0.12 mg/L H₂O₂ per µg/L of chlorophyll**.
  - Dense blooms needed 20 mg/L; sparse ones 5 mg/L.
  - Dense treatment also released nutrients and toxins.
  - So treating at the forecast trigger, while chlorophyll is still low, needs a fraction of the dose.
- **The selectivity lever:** 1.6 mg/L H₂O₂ wiped out Long Island–type brown tide (*Aureococcus*, about 2 µm) within 24 h, but cells larger than about 2-3 µm (diatoms, most dinoflagellates) were largely unaffected (Randhawa 2012, *PLOS ONE*, [doi](https://doi.org/10.1371/journal.pone.0047844)).

**Serious caveats:**
- **Short-lived:** blooms rebounded within 2 weeks or less in whole-pond dosing (Lusty & Gobler 2022).
- **Pollution swapping:** repeated pond dosing **increased fecal-indicator bacteria** (Lusty & Gobler 2022).
- **Marine dinoflagellates need 10-50+ mg/L**, which harms zooplankton. Treating even non-toxic dinoflagellates made the water **more toxic to fish gill cells** (Mardones 2023).
- **Non-target limits:**
  - *Daphnia* LC50 5.6 mg/L, no-effect level 3 mg/L; *Moina* LC50 2 mg/L (Reichwaldt 2011).
  - Proposed safe level: below 2.8 mg/L H₂O₂ (Thoo 2020).
- **Best fit:** small-celled blooms (brown tide, cyanobacteria) in enclosed ponds and basins, **not** dinoflagellate blooms.

## The loop for this method

| Loop step | What happens |
|---|---|
| **Trigger** | Narragansett model `p ≥ 0.50` on daily sensor means (backup: the rule trigger in `00_CONTROL_LOOP.md`) → a servo or winch **lowers the peroxide bag** |
| **Dose** | **fixed target 0.8 mg/L H₂O₂** (updated 2026-09-26). The Layer 2 simulation gave the same ≥ 50% cut on a small-celled alga at 0.8 as at 1.6 mg/L, with no non-target harm; 1.6 mg/L harmed non-targets in about 36% of runs (`LAYER2_SIM_RESULTS.md`). The earlier dose-per-chlorophyll rule came from freshwater work at 82-371 µg/L. The bag is still pulled if the residual exceeds 2.8 mg/L. The CaO₂ mass in the bag is sized from the Keliri release curve; the bench calibrates it |
| **`X` (ON time)** | **24 h** (release peaks by 24 h; brown-tide kill within 24 h), then **lift the bag out** and re-measure |
| **Re-measure** | chlorophyll, cell count, **H₂O₂ residual** (test strips, 0.5-25 mg/L range), pH (CaO₂ raises pH), DO, non-target survival |
| **OFF rule** | the shared rule. **Because the bag comes out after every X, "ON again" means a fresh bag** |
| **`MAX_ON`** | 3 bags per event (evidence review, 2026-09-25) |
| **Method safety limits** | H₂O₂ residual above 2.8 mg/L → pull the bag early; pH above 9.0; non-target survival more than 20 points below control |

**Important difference from the other methods:** the bag is **pulled out after every 24 h
pulse** whatever happens, then the OFF rule decides whether to send in a new bag. This keeps
exposure short and retrievable by design.

## Bench setup
- **Jars:** 3 per arm, 1-4 L (Lusty & Gobler used 4 L bottles; Randhawa 250 mL).
- **Best-fit culture:** a **small-celled non-toxic alga** (e.g. a *Micromonas*- or *Nannochloropsis*-type picoplankton) mixed with a **diatom**. That tests the size selectivity: does the small alga crash while the diatom survives?
- **Bag:** 2-4 layers of polyester or nonwoven fabric, heat-sealed or sewn, holding the weighed CaO₂. Keliri tested four fabric types; start with the one they found released like loose granules.
- **Dose-response pilot first:** 0, 0.5, 1, 2 g/L CaO₂ in plain seawater without algae. Measure H₂O₂ at 1, 4, 12 and 24 h with strips to build your own release curve before the main run.
- **Extra arm worth adding:** liquid 3% H₂O₂ dosed to the same target, which compares the bag with direct dosing.

## Measurements specific to peroxide
- H₂O₂ residual (strips) at 1, 4, 12 and 24 h in the first cycle.
- pH (CaO₂ forms calcium hydroxide).
- Size-class cell counts (small vs large cells).
- Optional, with sponsor approval and BSL review: coliform plates, to check the "pollution swapping" finding.

## Materials (estimates)

| Item | Approx. cost |
|---|---|
| Calcium peroxide (garden, pond or soil grade) | $25 |
| Peroxide test strips (0.5-25 mg/L) | $20 |
| Fabric + heat sealer or thread | $15 |
| Jars (12-15) | $40 |
| ESP32 + servo; fluorometer, pH, temperature, DO kit | $110 |
| Sea salt, f/2, cultures (NCMA) | $80-130 |
| Brine shrimp eggs | $10 |

## Safety and forms
- **Calcium peroxide is an oxidizer:** goggles and gloves, keep it away from organics and heat, and store it dry. That means a **Form 3 risk assessment**, with the Designated Supervisor present.
- Keep drugstore 3% H₂O₂ for comparison only.
- Dispose of treated water after the peroxide has decayed (check with strips).

## Environment
- Short-lived: it breaks down to water and oxygen, and the bag is retrieved.
- Real risks from the literature: zooplankton harm above about 2-3 mg/L, more toxic water after killing dinoflagellates, fecal-bacteria increases with repeated use, and fast rebound.
- The cap at 2.8 mg/L and the one-bag-at-a-time design limit these, but **arm D (false alarm) must show no non-target harm** before any claim of safety.

## Before building: verify in the full papers
- The Keliri 2022 fabric types and release curves (open access, so read it fully).
- The Buley 2023 dose-per-chlorophyll values and the chlorophyll range they apply to (82-371 µg/L). **Our trigger chlorophyll will be lower.** Extrapolating below that range is itself a testable question.
