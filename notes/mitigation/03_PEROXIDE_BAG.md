# Method 3: peroxide (liquid H₂O₂ pumped by the loop; sodium percarbonate as the off-the-shelf comparison)

**Changed 2026-09-28:** calcium peroxide and the fabric "tea bag" are dropped.
- **The loop doses liquid 3% H₂O₂ with the pump.** It is stable in a reservoir for weeks, so it suits the autonomy goal.
- **The screen adds sodium percarbonate** (pure oxygen-bleach powder, Na₂CO₃·1.5H₂O₂), the active ingredient of registered pond algaecides (PAK 27, GreenClean, Phycomycin SCP). It shows the loop can trigger a product already approved and used at lake scale.
- **Why:** percarbonate dissolves in minutes, so a bag of it wouldn't be retrievable. Peroxide breaks down to water and oxygen within 1-2 days anyway, so the loop controls exposure by **dose and timing**, not by retrieval. Percarbonate also raises pH less than CaO₂ (washing soda vs calcium hydroxide), its own non-target data exist (Thoo 2020: below 10 mg/L percarbonate ≈ 2.8 mg/L H₂O₂), and there is one less oxidizer to store.
- The CaO₂ bag notes below are kept as background only.

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

- **Already a commercial pond treatment:** sodium carbonate peroxyhydrate (a solid peroxide) is a registered algaecide.
  - Texas A&M rates it "good" control (75-89%) of **planktonic** algae, best on blue-greens (Sink et al. 2022, AgriLife RWFM-PU-154).
  - The Army Corps of Engineers trials, as reported by AquaPlant, rate it "good" too.
  - Our version differs in three ways: it's triggered by the forecast loop, dosed early and low, and used in marine water.

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
| **Trigger** | Narragansett model `p ≥ 0.50` on daily sensor means (backup: the rule trigger in `00_CONTROL_LOOP.md`) → the relay runs the **pump**, which doses liquid 3% H₂O₂ from a reservoir |
| **Dose** | **fixed target 0.8 mg/L H₂O₂** (updated 2026-09-26). The Layer 2 simulation gave the same ≥ 50% cut on a small-celled alga at 0.8 as at 1.6 mg/L, with no non-target harm; 1.6 mg/L harmed non-targets in about 36% of runs (`LAYER2_SIM_RESULTS.md`). The earlier dose-per-chlorophyll rule came from freshwater work at 82-371 µg/L. No new pulse is sent while the residual exceeds 2.8 mg/L. Liquid 3% H₂O₂: 0.27 mL per 10 L gives 0.8 mg/L. Percarbonate (screen comparison only): ~2.9 mg/L, dissolved fresh, content confirmed with the low-range kit |
| **`X` (ON time)** | **24 h** per pulse (brown-tide kill within 24 h; H₂O₂ half-life in seawater is hours), then re-measure |
| **Re-measure** | chlorophyll, cell count, **H₂O₂ residual** (test strips, 0.5-25 mg/L range), pH, DO, non-target survival |
| **OFF rule** | the shared rule. **Each ON is one pulse; "ON again" means a new pulse** |
| **`MAX_ON`** | 3 pulses per event (evidence review, 2026-09-25) |
| **Method safety limits** | H₂O₂ residual above 2.8 mg/L → no further pulse until it decays below 0.5 mg/L; pH above 9.0; non-target survival more than 20 points below control |

**Important difference from the other methods:** each ON is a **single 24 h pulse** whatever
happens, then the OFF rule decides whether to send another. This keeps exposure short by design.

## Bench setup
- **Jars:** 3 per arm, 1-4 L (Lusty & Gobler used 4 L bottles; Randhawa 250 mL).
- **Best-fit culture:** a **small-celled non-toxic alga** (e.g. a *Micromonas*- or *Nannochloropsis*-type picoplankton) mixed with a **diatom**. That tests the size selectivity: does the small alga crash while the diatom survives?
- *(Dropped 2026-09-28)* **Bag:** 2-4 layers of polyester or nonwoven fabric, heat-sealed or sewn, holding the weighed CaO₂. Keliri tested four fabric types; start with the one they found released like loose granules.
- **Percarbonate check first (replaces the CaO₂ release curve):** dissolve a weighed amount of sodium percarbonate in plain seawater and measure H₂O₂ at 0, 15 min, 1 h and 24 h with the low-range kit. That confirms its real peroxide content (theoretical 32.5% H₂O₂ by weight; commercial powder is often less), so 0.8 mg/L H₂O₂ ≈ **2.5-2.9 mg/L percarbonate (~25-29 mg per 10 L)**. Always dissolve it fresh on the day of dosing. *(Old CaO₂ pilot, dropped:)* run.
- **Comparison arm:** sodium percarbonate at the same H₂O₂ dose, plus a **sodium carbonate control** matched to the carbonate it adds (~2.0 mg/L Na₂CO₃ per 2.9 mg/L percarbonate), which separates peroxide from carbonate and pH.
- **Measuring 0.8 mg/L (added 2026-09-28; can break the method).** 0.5-25 mg/L strips are too coarse at the bottom of their range to confirm a 0.8 mg/L dose.
  - Buy a **low-range peroxide test kit** (colorimetric, with steps below 1 mg/L), and keep the strips only for the 2.8 mg/L safety cutoff.
  - Make **liquid 3% H₂O₂, dosed by the pump,** the main dosing method for the screen: the dose is then known from the arithmetic (0.8 mg/L in 10 L = 8 mg = 0.27 mL of 3%). The percarbonate arm becomes the comparison arm.
- *(Dropped with CaO₂)* **The bag overshoots:** Keliri's 2 g/L released up to 12 mg/L, 15× the target. Build the release curve in plain seawater first (below) and **start with a very small CaO₂ mass**.
- **Counting ~2 µm cells:** they're nearly impossible to count on a school microscope. Use **size-fractionated chlorophyll** instead: push a sample through a **5 µm syringe filter**. What passes through is small cells, and total minus filtrate is large cells. It's a standard oceanography method and cheap. Hemocytometer counts at 400× are a cross-check only.

## Measurements specific to peroxide
- H₂O₂ residual (strips) at 1, 4, 12 and 24 h in the first cycle.
- pH (percarbonate adds washing soda, a small rise).
- Size-class cell counts (small vs large cells).
- Optional, with sponsor approval and BSL review: coliform plates, to check the "pollution swapping" finding.

## Materials (estimates)

| Item | Approx. cost |
|---|---|
| Sodium percarbonate, pure (oxygen-bleach powder, no fragrance or surfactant) | $10 |
| Peroxide test strips (0.5-25 mg/L) | $20 |
| Jars (12-15) | $40 |
| ESP32 + servo; fluorometer, pH, temperature, DO kit | $110 |
| Sea salt, f/2, cultures (NCMA) | $80-130 |
| Brine shrimp eggs | $10 |

## Safety and forms
- **Sodium percarbonate is an oxidizer** (milder than CaO₂, but still): goggles and gloves, keep it away from organics and heat, and store it dry. That means a **Form 3 risk assessment**, with the Designated Supervisor present.
- Keep drugstore 3% H₂O₂ for comparison only.
- Dispose of treated water after the peroxide has decayed (check with strips).

## Environment
- Short-lived: it breaks down to water and oxygen within 1-2 days.
- Real risks from the literature: zooplankton harm above about 2-3 mg/L, more toxic water after killing dinoflagellates, fecal-bacteria increases with repeated use, and fast rebound.
- The cap at 2.8 mg/L and one-pulse-at-a-time dosing limit these, but **arm D (false alarm) must show no non-target harm** before any claim of safety.

## Before building: verify in the full papers
- The Keliri 2022 fabric types and release curves (open access, so read it fully).
- The Buley 2023 dose-per-chlorophyll values and the chlorophyll range they apply to (82-371 µg/L). **Our trigger chlorophyll will be lower.** Extrapolating below that range is itself a testable question.
