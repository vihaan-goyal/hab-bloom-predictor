# Method 4: curcumin dosing

Plugs into the shared loop in `00_CONTROL_LOOP.md`. Evidence: `notes/snowball/marine.md` #9-#10,
`notes/snowball/natural_compounds.md`; Part 1 #3.

## Why this method
- **Lab:** Hall et al. 2024, *Water* 16:1458 ([doi:10.3390/w16101458](https://doi.org/10.3390/w16101458)), Mote Marine Laboratory, on *Karenia brevis* at about 1 × 10⁶ cells/L:
  - **5 mg/L: 89% fewer cells and 60% less toxin in 24 h.**
  - 0.1-3 mg/L: 2-45% fewer cells.
  - 30-40 mg/L: 100% of cells gone by 6 h.
- **Mesocosm:** Devillier et al. 2025, *Limnol. Oceanogr. Methods* ([doi:10.1002/lom3.10731](https://doi.org/10.1002/lom3.10731)). 5 mg/L in 1,400 L tanks cut cells and toxins significantly within 24 h. **No significant effect on hard clams, sea urchins or blue crabs over 72 h**, and no change in dissolved N or P. **Turbidity rose.**
- **Status:** Mote reports curcumin as "the most effective" compound tested; it's in permitting for field trials.

**Caveats:**
- **It can't be retrieved:** curcumin is dosed into the water.
- Its breakdown products have only been assessed by computer prediction, not in animals.
- It dissolves poorly in water, so it needs a carrier (a small amount of ethanol, or a food-grade emulsifier) **and a carrier-only control**.
- It was tested on a dinoflagellate (*K. brevis*). Effects on diatoms, which dominate Long Island Sound, are untested here.
- Some natural compounds *raise* toxin release at low doses (gallic and tannic acid; `natural_compounds.md`).

## The loop for this method

| Loop step | What happens |
|---|---|
| **Trigger** | Narragansett model `p ≥ 0.50` on daily sensor means (backup: the rule trigger in `00_CONTROL_LOOP.md`) → a peristaltic pump doses curcumin stock |
| **Dose** | **1 mg/L** first pulse, a **low** dose because we treat early at low density. If the OFF rule isn't met at re-measure, the next pulse steps up to **2.5 mg/L, and stays there** (updated 2026-09-26). The Layer 2 simulation found a 5 mg/L top step harmed non-targets in about 90% of runs, vs about 26% at 2.5, while 76-94% of runs still cut the peak ≥ 50% (`LAYER2_SIM_RESULTS.md`). Never above 5 mg/L (the mesocosm-tested level) |
| **`X` (ON time)** | **24 h** after each pulse (the 89% effect was measured at 24 h), then re-measure |
| **Re-measure** | chlorophyll, cell count, **turbidity** (curcumin clouds the water), colour, DO, pH, non-target survival |
| **OFF rule** | the shared rule → stop dosing. There's nothing to retrieve, so "OFF" means no further pulses |
| **`MAX_ON`** | 4 pulses (cumulative ≤ 1 + 2.5 + 2.5 + 2.5 = 8.5 mg/L per event) |
| **Method safety limits** | non-target survival more than 20 points below control; DO below 4 mg/L (dying cells use oxygen); turbidity more than 3× control |

**Why step the dose up:** the forecast gives you a head start. The question is whether the smallest
early dose that works is well below the 5 mg/L needed against an established bloom. That's H1 in
dose form: arm B total dose < arm C total dose.

## Bench setup
- **Jars:** 3 per arm, 1.5 L, following Mote's beaker scale, artificial seawater at salinity 30, 12:12 light.
- **Culture:** non-toxic dinoflagellate (*Prorocentrum micans*) plus a diatom (*Phaeodactylum*) arm, to test whether curcumin works on diatoms at all.
- **Stock:** food-grade curcumin (≥ 95%, not turmeric powder), dissolved in a small volume of ethanol. Keep ethanol in the jar below 0.1% and match it exactly in a **carrier-only control jar**.
- **Dosing:** peristaltic pump driven by the ESP32, calibrated by weighing the delivered volume.

## Measurements specific to curcumin
- Turbidity (a DIY nephelometer: LED at 90° to a photodiode, or a Secchi-tube reading).
- Colour; curcumin is yellow and **interferes with fluorescence**. Calibrate the fluorometer against curcumin-spiked, algae-free water, and confirm with cell counts.
- Curcumin fading over time (absorbance near 425 nm if a cheap spectrometer is available).

## Materials (estimates)

| Item | Approx. cost |
|---|---|
| Curcumin ≥ 95% (food or supplement grade) | $20 |
| Ethanol (food grade) | $10 |
| Peristaltic pump + driver | $25 |
| Jars, ESP32, fluorometer, turbidity LED/photodiode, pH, temperature, DO kit | $140 |
| Sea salt, f/2, cultures (NCMA) | $80-130 |
| Brine shrimp eggs | $10 |

## Safety and forms
- Curcumin is a food supplement. Ethanol is flammable in small amounts; handle it with supervision. It's a low-risk chemical list, but record it on Form 3 if the sponsor requires.
- Dispose of treated water down the drain, not into the Sound.

## Environment
- A natural product, and a mesocosm found no harm to clams, crabs or urchins over 72 h.
- But it's **not retrievable**, it clouds the water, and its breakdown products are unstudied in animals.
- Of the five methods, this is the least aligned with the counselor's "don't change the environment" point, so treat it as a **comparison arm** rather than the lead method.

## Before building: verify in the full papers
- Hall 2024 and Devillier 2025: the carrier or solvent used, how long curcumin persists, and what exactly caused the turbidity.
- Whether any study tested curcumin on diatoms.
