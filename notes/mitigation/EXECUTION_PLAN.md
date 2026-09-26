# Execution plan: five bloom-disruption experiments

Written 2026-09-25. Built from the five evidence reviews in `evidence/` (123 sources in total)
and the shared loop in `00_CONTROL_LOOP.md`. **Nothing hands-on starts until the sponsor
(Designated Supervisor) and forms are signed.**

## 1. What the evidence says, method by method

| # | Method | Sources | Evidence strength | Will it work on *our* cultures? | Role in the project |
|---|---|---|---|---|---|
| 01 | Coarse bubbles | 27 | Moderate (bench) | Only on sensitive dinoflagellates. It pauses division (23-55% less growth) and cells regrow once it stops. 3 of 10 dinoflagellates grew *faster* when stirred. Diatoms are unaffected or helped | **Screen only** (Layer 2: bubbles mostly delay the bloom; ≥ 50% cut in 3% of runs) |
| 02 | Kelp panels | 20 | Moderate-strong (lab and mesocosm) | Likely: diatom −74-94% at ≥ 72 h (2 g/L); dinoflagellates need ~2 g/L for ~10 days. Untested on *Phaeodactylum* or *Thalassiosira* | **Full loop run** (lead method) |
| 03 | Peroxide bag | 27 | Strong for small cells only | At a dose that is safe for non-targets (≤ 2.8 mg/L), only ~2 µm cells die. *P. micans* was hit 11% even at 6.4 mg/L, *T. weissflogii* 2.6% | **Screen only**, on a small-celled alga; shows the "selective" idea |
| 04 | Curcumin | 25 | Weak-moderate (one organism, *K. brevis*) | Unknown: no diatom or *Prorocentrum* data. Works at ≥ 3 mg/L, but zebrafish larval LD50 is 1.8-2.8 mg/L. It also interferes with the 470 nm fluorometer | **Screen only**, as a comparison arm |
| 05 | Shellfish bags | 24 | Strong in tanks, weak at larger scale | Yes for filtration (oysters ~1 L/h per 60 mm animal), but feeding stops at high HAB density, and every success had the animals in place *before* the bloom | **Full loop run #2** (Layer 2: 94-95% chance of a ≥ 50% cut when stocked for 2 tank volumes/day), after the clearance test; needs permits and animals |

**Evidence files:** `evidence/01_BUBBLES_EVIDENCE.md`, `02_SEAWEED_`, `03_PEROXIDE_`,
`04_CURCUMIN_`, `05_SHELLFISH_EVIDENCE.md`. Each file has a master table, per-source detail,
aggregated data, hypotheses, mechanisms, design numbers and gaps.

**Layer 2 simulation (2026-09-26, `LAYER2_SIM_RESULTS.md`):**
- It confirmed seaweed as full run #1.
- It moved shellfish into full run #2 in place of bubbles, which mostly delay the bloom.
- It lowered the peroxide target to 0.8 mg/L and capped curcumin at 2.5 mg/L, both because of non-target harm.

**Why only two full loop runs:** each run is 4 arms × 3 tanks for 6-7 weeks. Five methods would
need about 60 tanks and a lab we don't have. The **screens** (days, small flasks) test all five;
the **loop runs** (weeks, tanks) go to the two methods most likely to work on our cultures.

## 2. Design numbers (from the evidence files)

| | Bubbles | Seaweed | Peroxide | Curcumin | Shellfish |
|---|---|---|---|---|---|
| Treatment | coarse bubbles, open tube | live sugar kelp panel | CaO₂ in fabric bag | ethanol stock, peristaltic dose | oysters or clams in mesh bag |
| Dose | 0.05 and 0.6 L/min per litre (Sung & Gobler: 25 and 300 mL/min into 500 mL) | 2 g/L wet (dose arms 0, 0.5, 1, 2) | target **0.8** mg/L H₂O₂; pull above 2.8 | ladder 1 → 2.5 mg/L (cap 2.5) | clear **2** tank volumes/day ≈ 4 oysters (40 mm) per 20 L, sized from the measured clearance; cap 1 per 2 L |
| `X` | 48 h | 72 h | 24 h, then bag out | 24 h per pulse | **3 d** (Layer 2 sweep) |
| `MAX_ON` | 192 h | 12 d (≥ 10 d for dinoflagellate) | **3 bags** (was 4) | 4 pulses | 4 × X |
| Main culture | *Akashiwo sanguinea* (backup *Prorocentrum triestinum*) + *Phaeodactylum* check | *Phaeodactylum* or *Thalassiosira*; dinoflagellate second | small-celled alga (*Micromonas*/*Nannochloropsis*-type) + *T. weissflogii*, *P. micans* as resistant controls | *P. micans* + diatom | diatom |
| Extra controls | still column, fine airstone, pulsed | fake plastic panel, pH-matched, nutrient top-up, filtrate | empty bag, sodium carbonate, liquid H₂O₂ | ethanol-only, light vs dark, curcumin-spiked blank | empty-shell bag, animals without algae |
| Method safety limit | temp +2 °C, evaporation > 5% | pH > 9.0 | residual > 2.8 mg/L, pH > 9.0 | DO drop > 2 mg/L in 24 h | ammonia-N > 0.5 mg/L, mortality > 10% |
| Non-target check | *Artemia* 24 h | *Artemia* 24 h | *Artemia* **24 h and 96 h** (delayed deaths) | *Artemia* in **light** | animal health log |
| Main endpoint | cell count | cell count | size-class cell count | cell count (fluorometer unreliable) | chl + cell count |

The shared safety limits apply to all methods: DO < 4 mg/L; pH outside 7.6-8.6 (or the method's
own limit); non-target survival more than 20 points below control.

## 3. Hypotheses we test

**Screens** (one per method, pre-registered before starting):
- **S1 bubbles:** at 0.6 L/min per litre, the screened dinoflagellate's cell count after 48 h is ≥ 30% below the still control, and *Phaeodactylum* is not reduced.
- **S2 seaweed:** 2 g/L kelp cuts diatom cells ≥ 50% vs no-seaweed at 72 h. The fake panel and pH-matched control don't.
- **S3 peroxide:** 0.8 mg/L cuts the small-celled alga ≥ 50% in 24 h, while the diatom and *P. micans* drop < 20%.
- **S4 curcumin:** the lowest dose with ≥ 30% cell reduction at 24 h is ≤ 2.5 mg/L, and *Artemia* survival at that dose in light is within 20 points of control.
- **S5 shellfish:** measured clearance rate (L/animal/h) at 18 °C is within 2× of the published planning rate.

**Go rule for a loop run:** the screen meets its hypothesis *and* passes the non-target check.

**Loop runs** (from `00_CONTROL_LOOP.md`):
- **H1a:** arm B's peak chlorophyll (and cell count) is ≥ 50% below arm A's.
- **H1b:** arm B's peak cut beats arm C's (late treatment).
- Treatment used by B and C is reported, not tested. The original "less treatment than C" can't pass even when B works; see `LAYER2_SIM_RESULTS.md`.
- **H2:** arm D shows no non-target loss compared with arm A.
- **H3 (new, from the reviews):** after OFF, arm B regrows. We record days until it's back above `C_ok`. The reviews say bubbles and seaweed effects stop when the treatment is removed, so this is expected, and measuring it is part of the result.

## 4. Timeline

The fixed points:
- The loop run must finish before the February write-up.
- The 21-day warm-up can start before the screens finish, because warm-up is just logging with low nutrients.
- **Winter break (about Dec 22 - Jan 2):** the lab may be closed and cell counts need a person. **Plan the bloom phase to avoid it.**

| Dates (2026-27) | Phase | What happens | Blocking on |
|---|---|---|---|
| **Now - Oct 10** | 0. Admin | Find a sponsor or Designated Supervisor and a lab space. Forms 1, 1A, 1B, and Form 3 (CaO₂ oxidizer, ethanol). Ask NCMA about the strains (§5). Email a CT kelp farm and a shellfish hatchery. Optional: email Dr. Gobler for the bubble PDF | **You** |
| Oct 5 - Oct 24 | 1. Build and calibrate | ESP32 controller and relay/servo/pump; DIY fluorometer; calibrate to µg/L with a dilution series. Curcumin-spiked blank test for fluorometer interference. CaO₂ release curve in seawater without algae (strips at 1, 4, 12, 24 h). Start the design log | parts ordered |
| Oct 15 - Oct 31 | Culture up | Grow NCMA cultures to working density; hatch *Artemia* test batches | cultures arrive |
| **Oct 26 - Nov 14** | 2. Screens | Five screens in 250 mL flasks or 5 L columns, n = 3 each (§6). Each is 1-10 days, run in parallel | cultures, forms |
| **Nov 10** | Warm-up start | 21 tanks start logging at low nutrients (the model's 21-day warm-up) | controller working |
| Nov 16 - Nov 25 | 3. Decide and pre-register | Apply the go rule; choose the two loop methods; write `LOOP_PREREG.md` (arms, n, X, dose, endpoints, stats) and commit it **before** nutrients go in | screen results |
| **Dec 1** | Nutrients in | Arms A-C get nutrients; D doesn't. The loop runs on both triggers (model and rule) | prereg committed |
| Dec 1 - Dec 19 | 4. Loop run | Bloom phase ~2-3 weeks; re-measure at every X; cell counts on school days | lab access |
| Dec 19 - Dec 24 | Cool-down | 5 days of logging (the controller runs unattended; one visit for counts) | |
| **Jan 4 - Feb 1** | 5. Analyse and write | `src/lab/analyze_lab.py` (mean ± 95% t, n = 3); figures; board; update `SCIENTIFIC_METHOD.md` | |
| Feb | Backup window | If a run fails, repeat the best method once (another 6-7 weeks is too long, so use a shortened warm-up and report it) | |

## 5. What you need to do (in order)

1. **Sponsor and forms.** This blocks everything.
   - Designated Supervisor: a science teacher, or a UConn/DEEP contact.
   - Form 3: CaO₂ is an oxidizer and ethanol is flammable.
   - No vertebrates are used: *Artemia* and shellfish are invertebrates. Confirm with the SRC.
2. **Lab space:** room for 21 tanks plus flask racks, grow lights, a GFCI outlet and a microscope.
3. **Email NCMA (Bigelow)** to ask:
   - whether they have non-toxic strains of *Akashiwo sanguinea* and *Prorocentrum triestinum*;
   - whether they have *Phaeodactylum*, *Thalassiosira weissflogii*, *P. micans* and a small-celled alga (*Micromonas* or *Nannochloropsis*).

   *Akashiwo* has caused seabird deaths (a surfactant, not a toxin), so the sponsor must approve it. Otherwise use *P. triestinum*.
4. **Email a Connecticut kelp farm** for young sugar kelp blades in November (kelp is grown over winter, but the blades are small in autumn). Backup: collect *Ulva* now and hold it in f/2.
5. **Email a shellfish hatchery** for 40 mm oyster or clam seed, and ask about the CT Department of Agriculture (Bureau of Aquaculture) permits. If it's slow, drop shellfish to "clearance test only".
6. **Order parts** (§8).
7. **Emails you send yourself**; I can draft each one (short, one ask).

## 6. The five screens (Phase 2)

| Screen | Vessels | Arms (n = 3 each) | Length | Measure |
|---|---|---|---|---|
| Bubbles | 500 mL cultures in 1 L flasks (the Sung & Gobler setup) | still; air stone at 25 mL/min; air stone at 300 mL/min; × 2 species (dinoflagellate, *Phaeodactylum*); n = 4 | 4 d (covers 48 h ON + 48 h regrowth) | cells daily, pH, temperature |
| Seaweed | 250 mL flasks | kelp 0, 0.5, 1, 2 g/L; fake panel; pH-matched; filtrate | 10 d | cells every 24-48 h, pH, *Artemia* at end |
| Peroxide | 250 mL flasks | 0, 0.8, 1.6, 3.2, 6.4 mg/L × 3 species; empty bag; Na₂CO₃ | 72 h | size-class counts, H₂O₂ strips, *Artemia* 24 h + 96 h |
| Curcumin | 250 mL flasks | 0, 0.5, 1, 2.5, 5, 10 mg/L; ethanol-only; 2.5 mg/L dark | 72 h | cells, A425, DO, *Artemia* in light |
| Shellfish | 1 L beakers | 1 animal each (10 per species) + 3 no-animal | 4 h | chl every 30 min → L/animal/h |

**Total:** about 110 flasks or beakers plus 15 columns. These are small and can share one shelf
and light bank.

## 7. Loop run layout (Phase 4)

For two methods on the same culture (**planned: seaweed and shellfish**, both on the diatom; chosen by the Layer 2 simulation, `LAYER2_SIM_RESULTS.md`):

| Arm | Tanks | Notes |
|---|---|---|
| A untreated | 3 | **shared** by both methods (same culture, same dates) |
| B loop, method 1 | 3 | |
| C late, method 1 | 3 | |
| D false alarm, method 1 | 3 | no nutrients |
| B, C, D, method 2 | 9 | |
| **Total** | **21 tanks (4-10 L)** | |

If the shellfish clearance test shows too little filtering, or the animals or permits don't come
through, method 2 falls back to seaweed at a second density.

## 8. Shopping list (all methods, combined)

| Item | For | Approx. |
|---|---|---|
| ESP32 × 3, relays, servo, peristaltic pump, wiring | controllers | $60 |
| DIY fluorometer parts × 3 (470 nm LED, photodiode, red filter, op-amp) | all | $90 |
| pH probe, DS18B20 × 6, DO kit, ammonia kit | all | $120 |
| 21 tanks (4-10 L) + 15 columns (5 L) + ~110 flasks/beakers | all | $220 |
| 2 air pumps, manifold, needle valves, tubing | bubbles | $40 |
| LED grow lights × 2 + timers | all | $60 |
| Sea salt, f/2 and f/4 medium, Sedgewick-Rafter chamber | all | $80 |
| Cultures (NCMA, 4-5 strains) | all | $250-400 |
| Calcium peroxide, H₂O₂ strips, fabric | peroxide | $60 |
| Curcumin ≥ 95%, food-grade ethanol | curcumin | $30 |
| Kelp (farm) / *Ulva* (collect), mesh cages | seaweed | $0-50 |
| Oyster or clam seed, mesh bags | shellfish | $30-80 |
| *Artemia* eggs | non-target | $10 |
| **Total** | | **about $1,100-1,300** |

Much of this can be borrowed: ask the sponsor for the microscope, glassware and the pH/DO meters.

## 9. Changes this plan makes to the method files (not yet applied)

- `00_CONTROL_LOOP.md` / `01_BUBBLES.md`: the main bubble test species becomes *Akashiwo sanguinea* (backup *P. triestinum*); bubbling may raise pH in dense cultures, so log pH in the still control too.
- `03_PEROXIDE_BAG.md`: a fixed 1.6 mg/L target replaces the freshwater dose-per-chlorophyll rule; `MAX_ON` 3 bags; *Artemia* checked at 96 h.
- `04_CURCUMIN.md`: add the DO-drop safety rule; cell counts are the primary endpoint; add a light vs dark arm.
- `05_SHELLFISH.md`: bench `X` = 24 h (the 7 days was for a whole bay); dose computed from measured clearance.
- Add H3 (regrowth after OFF) to `00_CONTROL_LOOP.md`.

## 10. Risks

| Risk | Effect | Fallback |
|---|---|---|
| No sponsor by mid-October | the whole timeline slips | screens can shrink to 2 weeks; loop run starts mid-December and the bloom phase moves to January |
| Bubble screen: dinoflagellate unaffected | bubbles drop to a negative result (still reportable) | shellfish or a second seaweed density in the loop |
| Kelp unavailable in November | seaweed arm has no material | *Ulva* collected now and held in culture |
| Fluorometer disagrees with cell counts | the OFF rule is wrong | the OFF rule uses cell counts (already the plan for seaweed and curcumin) |
| Model never fires in a tank (month term, rescaling) | arm B has no model trigger | the rule trigger drives arm B; report the model's behaviour as a finding |
| Lab closed over break | missed counts | the bloom phase ends Dec 19 by design |

## Never claim
- That it prevents blooms in the open Sound; this is tanks only.
- That it is safe without arm D's non-target data.
- Any result before it is measured; pre-register first.
