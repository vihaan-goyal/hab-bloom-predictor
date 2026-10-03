# Execution plan: bloom-disruption experiments (aeration and peroxide)

Written 2026-09-25. Built from the five evidence reviews in `evidence/` (123 sources in total)
and the shared loop in `00_CONTROL_LOOP.md`. **Updated 2026-10-01: the treatments are now
aeration and peroxide only** (see "Plan change 2026-10-01" below). **Nothing hands-on starts until
the sponsor (Designated Supervisor) and forms are signed.**

## Plan change 2026-10-01

Decided by the student and the counselor on 2026-10-01, **before any tank data exists.**

**The rule behind it: the device has to sit on the water fully autonomously.** A treatment stays
only if the device can switch it (relay or pump), it needs no living stock, and it runs for weeks
with at most a refill. Aeration (relay → air pump) and peroxide (relay → peristaltic pump, 3% H₂O₂
reservoir) pass. The device targets **enclosed or semi-enclosed water** (harbors, shellfish beds,
aquaculture pens, coastal ponds), never the open Sound.

| Decision | Reason |
|---|---|
| **Seaweed (kelp) dropped** | Needs live stock kept alive in a cold holding tank and swapped weekly. Sugar kelp dies back above about 18-20 °C, which is the summer bloom season. It can't run unattended |
| **Shellfish dropped** | Always filtering, so it can't be switched off by the device. Live animals, and permits. Feeding stops in dense blooms |
| **Curcumin dropped** | Its yellow colour absorbs the ~470 nm excitation light, so it blinds the device's own fluorometer (a false "bloom gone" and an early OFF). Its effective dose (≥ 3 mg/L) overlaps the zebrafish larval LD50 (1.8-2.8 mg/L). Tested on one organism only, with no diatom or field data |
| Clay/flocculation and the other scoreboard methods | Already out (counselor, 2026-09-24) |
| **Two full loop runs: aeration and peroxide** (were seaweed and shellfish) | The two methods that meet the autonomy rule. Arms A-D, n = 3 per arm, the floor rule, the handover, `MAX_ON` (peroxide 3 pulses) and the pumped 0.8 mg/L peroxide pulses (3% H₂O₂ by peristaltic pump; sodium percarbonate only in the screen) all stay as they were |
| **Aeration is judged on delay, not peak cut** (written down now, before data) | Primary outcome for aeration: **days held below `C_ok`** in arm B vs untreated arm A, reported with **hours ON** and **number of ON episodes** (reruns). The ≥ 50% peak cut becomes secondary for aeration. In real water, tides flush nutrients and conditions change, so holding a bloom back lets its window pass, and the device simply re-runs when the forecast fires again. H3 (regrowth after OFF) stays and tells how often reruns are needed. Peroxide keeps H1 (≥ 50% peak cut) |
| **Cell-size species panel in both screens** | The freed time goes into a panel: *Nannochloropsis* (2-3 µm), *Micromonas pusilla* (~2 µm), the diatom *Skeletonema*, and the dinoflagellate already in each screen. New secondary hypothesis: **peroxide sensitivity falls with cell size** (Randhawa et al. 2012) |

The seaweed, shellfish and curcumin method files, evidence reviews and Layer 2 results are kept as
a record of what was considered and why it was dropped.

## 1. What the evidence says, method by method

| # | Method | Sources | Evidence strength | Will it work on *our* cultures? | Role in the project |
|---|---|---|---|---|---|
| 01 | Coarse bubbles (aeration) | 27 | Moderate (bench) | Only on sensitive dinoflagellates. It pauses division (23-55% less growth) and cells regrow once it stops. 3 of 10 dinoflagellates grew *faster* when stirred. Diatoms are unaffected or helped | **Full loop run #1** (2026-10-01), judged on **delay** (days held below `C_ok`), not peak cut. Layer 2: bubbles mostly delay the bloom (≥ 50% cut in 4% of runs), which is now the outcome being measured |
| 02 | Kelp panels | 20 | Moderate-strong (lab and mesocosm) | Likely on diatoms, but needs live, cold-held kelp | **Dropped 2026-10-01** (live stock, dies back above ~18-20 °C, not autonomous) |
| 03 | Peroxide (pumped H₂O₂; percarbonate comparison) | 27 | Strong for small cells only | Below the most sensitive non-target LC50s (krill 0.86, *Moina* 2 mg/L), only ~2 µm cells die, and one 0.8 mg/L dose is only transient (peroxide-03). *P. micans* was hit 11% even at 6.4 mg/L, *T. weissflogii* 2.6% | **Full loop run #2** (2026-10-01; was screen only), on a small-celled alga. Keeps H1 (≥ 50% peak cut). Layer 2: 74% median cut from up to 3 daily 0.8 mg/L pulses, 1% non-target harm |
| 04 | Curcumin | 25 | Weak-moderate (one organism, *K. brevis*) | Unknown; blinds the 470 nm fluorometer | **Dropped 2026-10-01** (fluorometer interference, dose overlaps zebrafish LD50, one organism) |
| 05 | Shellfish bags | 24 | Strong in tanks, weak at larger scale | Filters, but can't be switched off | **Dropped 2026-10-01** (not switchable, live animals, permits, stops feeding in dense blooms) |

**Evidence files:** `evidence/01_BUBBLES_EVIDENCE.md`, `02_SEAWEED_`, `03_PEROXIDE_`,
`04_CURCUMIN_`, `05_SHELLFISH_EVIDENCE.md`. Each file has a master table, per-source detail,
aggregated data, hypotheses, mechanisms, design numbers and gaps. The dropped methods' files are
kept as a record.

**Layer 2 simulation (2026-09-26, re-run 2026-09-28 to match the protocol; `LAYER2_SIM_RESULTS.md`):**
- Re-run (peroxide as pumped pulses, pilot-based C_ok, H4 floor, handover, recipe-scale nutrients,
  intervals that include arm A's spread): seaweed 72%, shellfish 81%, peroxide 74% median peak cut;
  curcumin 63% with 19% non-target harm; bubbles 25%. With 3 tanks per arm the honest interval clears
  50% in 64-80% of runs; with 4 tanks, 78-92%.
- At the time it chose seaweed and shellfish for the full runs. **Superseded 2026-10-01** by the
  autonomy rule above; the simulation results stand as a record.
- It lowered the peroxide target to 0.8 mg/L because of non-target harm (still in force).
- For bubbles, it predicts a small peak cut and arm B hitting `MAX_ON` in 99% of runs: bubbles hold
  the bloom back rather than cut it. That is why aeration is now judged on delay.

**Why only two full loop runs:** each run is 4 arms × 3 tanks for 6-7 weeks. The **screens**
(days, small flasks) test both methods on a cell-size panel; the **loop runs** (weeks, tanks) test
both methods in the full loop.

## 2. Design numbers (from the evidence files)

| | Bubbles (aeration) | Peroxide |
|---|---|---|
| Treatment | coarse bubbles, air stone, relay → air pump | liquid 3% H₂O₂ by peristaltic pump (loop); sodium percarbonate (screen comparison) |
| Dose | 0.05 and 0.6 L/min per litre (Sung & Gobler: 25 and 300 mL/min into 500 mL); loop at 0.6 | **0.8** mg/L H₂O₂ per pulse, up to 3 daily pulses; re-dose only if residual ≤ 0.5; stop if > 2.8 |
| `X` | 48 h | 24 h per pulse |
| `MAX_ON` | 192 h per episode; a new forecast alert after OFF starts a new episode (a rerun) | **3 pulses** |
| Screen species (2026-10-01 panel) | *Nannochloropsis*, *Micromonas pusilla*, *Skeletonema*, dinoflagellate *Akashiwo sanguinea* (backup *Prorocentrum triestinum*) | *Nannochloropsis*, *Micromonas pusilla*, *Skeletonema*, *T. weissflogii*, *P. micans* (larger cells as the "expected spared" controls) |
| Loop culture | the dinoflagellate the screen shows is slowed (fallback: the panel species with the largest growth pause) | the small alga the screen shows is cut, mixed with *Skeletonema* (tests size selectivity in the tank) |
| Extra controls | still, gentle bubbling (CO₂ control), pulsed | sodium percarbonate arm, sodium carbonate |
| Method safety limit | temp +2 °C, evaporation > 5% | residual > 2.8 mg/L, pH > 9.0 |
| Non-target check | *Artemia* 24 h | *Artemia* **24 h and 96 h** (delayed deaths) |
| Main endpoint | **days held below `C_ok`** (B vs A), with hours ON and ON episodes; cell count | peak chlorophyll and cell count (size classes) |

The shared safety limits apply to both methods: DO < 4 mg/L; pH outside 7.6-8.6 (or the method's
own limit); non-target survival more than 20 points below control.

## 3. Hypotheses we test

**Screens** (one per method, pre-registered before starting):
- **S1 bubbles:** at 0.6 L/min per litre, the dinoflagellate's cell count after 48 h is ≥ 30% below the still control, and *Skeletonema* is not reduced. The two small algae are reported (no pass mark). Regrowth after the 48 h OFF is measured in every species, because it sets how often the loop has to re-run.
- **S3 peroxide (restated 2026-09-28 from the source):** one 1.6 mg/L dose cuts the small-celled alga ≥ 50% in 24 h while the diatoms and *P. micans* drop < 20%; one 0.8 mg/L dose gives a smaller, transient cut (peroxide-03); and **three daily 0.8 mg/L pulses** (the loop dose) cut the small-celled alga ≥ 50% by 72 h with *Artemia* survival (24 h and 96 h) within 20 points of control. Tested on both small algae (*Micromonas* and *Nannochloropsis*).
- **H5 / S-size (secondary, new 2026-10-01; `00_CONTROL_LOOP.md`): peroxide sensitivity falls with cell size.** At each dose, the percent cut ranks *Micromonas* ≈ *Nannochloropsis* (2-3 µm) > *Skeletonema* > *T. weissflogii* > *P. micans*, and the larger cells (and the arm-D non-target check) are spared at 0.8 mg/L, as Randhawa et al. 2012 reported. *Micromonas* was eradicated by peroxide in Randhawa 2012 (peroxide-03); *Nannochloropsis*'s peroxide sensitivity is untested in our papers, so it is a real test.
- *S2 seaweed, S4 curcumin, S5 shellfish: dropped 2026-10-01 (see Plan change).*

**Counting 2 µm cells:** they are hard to count with a school microscope. The small algae are
measured by the **fluorometer** (each screen flask holds one species) plus **hemocytometer counts at
400×**, and that is said in the write-up. The 5 µm syringe filter splits small from large cells in
the mixed peroxide loop tanks.

**Go rule (changed 2026-10-01):** both methods go to a loop run. The screens choose each loop's
**species** (and confirm the dose), and a screen that fails its non-target check stops that loop
run.

**Loop runs** (from `00_CONTROL_LOOP.md`):
- **Aeration, primary (2026-10-01): H1-delay.** Arm B stays below `C_ok` for more days than arm A (from nutrients-in to the end of the bloom phase), reported with total hours ON and the number of ON episodes (reruns). Also B vs C on the same measure. The ≥ 50% peak cut (H1a) is reported as **secondary** for aeration.
- **Peroxide, primary: H1a:** arm B's peak chlorophyll (and cell count) is ≥ 50% below arm A's. **H1b:** arm B's peak cut beats arm C's (reactive treatment, started at 50% of the expected peak).
- Treatment used by B and C is reported, not tested. The original "less treatment than C" can't pass even when B works; see `LAYER2_SIM_RESULTS.md`.
- **H2:** arm D shows no non-target loss compared with arm A.
- **H4 (2026-09-28):** arm B trims the bloom without pushing algae below normal: its 3-tank mean chlorophyll never falls below 80% of the warm-up mean, and daytime DO stays at or above its warm-up level. A floor OFF rule (2 days below 80% of warm-up) enforces it; details in `00_CONTROL_LOOP.md`.
- **H3:** after OFF, arm B regrows. We record days until it's back above `C_ok`. The reviews say bubble effects stop when the treatment is removed, so this is expected; for aeration it tells how often the device has to re-run.

## 4. Timeline

The fixed points:
- The loop runs must finish before the February write-up.
- The 21-day warm-up can start before the screens finish, because warm-up is just logging with low nutrients.
- **Winter break (about Dec 22 - Jan 2):** the lab may be closed and cell counts need a person. **Plan the bloom phase to avoid it.**

| Dates (2026-27) | Phase | What happens | Blocking on |
|---|---|---|---|
| **Now - Oct 10** | 0. Admin | Find a sponsor or Designated Supervisor and a lab space. Forms 1, 1A, 1B, and Form 3 (sodium percarbonate oxidizer, 3% H₂O₂). Ask NCMA about the strains, including *Micromonas pusilla* (§5). Buy live *Nannochloropsis* (reef-aquarium phytoplankton). Optional: email Dr. Gobler for the bubble PDF | **You** |
| Oct 5 - Oct 24 | 1. Build and calibrate | Arduino Uno alerter with relay → air pump and peristaltic dosing pump; DIY fluorometer; calibrate to µg/L with a dilution series. Percarbonate peroxide-content check in seawater without algae (low-range kit at 0, 15 min, 1 h, 24 h). Calibrate the peristaltic pump by weight. Start the design log | parts ordered |
| Oct 15 - Oct 31 | Culture up | Grow the panel (*Nannochloropsis*, *Micromonas*, *Skeletonema*, *T. weissflogii*, the dinoflagellates) to working density; check the aquarium *Nannochloropsis* under the microscope and sub-culture it clean; hatch *Artemia* test batches | cultures arrive |
| **Oct 26 - Nov 14** | 2. Screens | Two screens on the species panel, in flasks, n = 3 each (§6). 4 and 3 days, run in parallel; repeat a failed flask set if time allows | cultures, forms |
| **Nov 10** | Warm-up start | 28 tanks start logging at low nutrients (the model's 21-day warm-up) | controller working |
| Nov 16 - Nov 25 | 3. Decide and pre-register | Apply the go rule; choose each loop's species; write `LOOP_PREREG.md` (arms, n, X, dose, endpoints, stats, the aeration delay outcome) and commit it **before** nutrients go in | screen results |
| **Dec 1** | Nutrients in | Arms A-C get nutrients; D doesn't. The loop runs on both triggers (model and rule) | prereg committed |
| Dec 1 - Dec 20 | 4. Loop runs | Both methods run at once (days 21-40). Bloom phase ~2-3 weeks; re-measure at every X; cell counts on school days | lab access |
| Dec 20 - Dec 25 | Cool-down | Days 40-45: 5 days of logging, overlapping the start of winter break (the controller runs unattended; one visit for counts and the peroxide reservoir) | |
| **Jan 4 - Feb 1** | 5. Analyse and write | `src/lab/analyze_lab.py` (mean ± 95% t, n = 3); figures; board; update `SCIENTIFIC_METHOD.md` | |
| Feb | Backup window | If a run fails, repeat the best method once (another 6-7 weeks is too long, so use a shortened warm-up and report it) | |

> **DECIDED 2026-10-03: option 1 (warm up all candidate cultures in parallel from Nov 10; keep only the tanks the screens choose after Nov 25).** Original note:
> **Warm-up Day 0 comes before the culture choice.** Warm-up Day 0
> (Nov 10, when every tank is inoculated with "that method's culture") and the pilot pulse (~Nov 17)
> both come before the screens choose each loop's culture (Nov 16-25). Decide before ordering tanks:
> 1. **Warm up all candidate cultures in parallel** (e.g. both small algae + *Skeletonema*, and the
>    dinoflagellate candidates) and keep only the chosen tanks after Nov 25; this needs extra tanks
>    and lab space, but keeps the timeline; or
> 2. **Shift Day 0 to after the decision** (about Nov 26), which moves nutrients-in to about Dec 17
>    and the bloom phase into winter break, so the loop runs would move to January (see §10, "No
>    sponsor by mid-October").

## 5. What you need to do (in order)

1. **Sponsor and forms.** This blocks everything.
   - Designated Supervisor: a science teacher, or a UConn/DEEP contact.
   - Form 3: sodium percarbonate is an oxidizer; 3% H₂O₂ is an irritant. (Ethanol is no longer used, 2026-10-01.)
   - No vertebrates are used: *Artemia* are invertebrates. No live shellfish or seaweed any more. Confirm with the SRC.
2. **Lab space:** room for 28 tanks plus flask racks, grow lights, a GFCI outlet and a microscope.
3. **Email NCMA (Bigelow)** to ask:
   - whether they have non-toxic strains of *Akashiwo sanguinea* and *Prorocentrum triestinum*;
   - whether they have *Skeletonema*, *Thalassiosira weissflogii*, *P. micans*, *Micromonas pusilla* and (as a backup to the aquarium culture) *Nannochloropsis*.

   *Akashiwo* has caused seabird deaths (a surfactant, not a toxin), so the sponsor must approve it. Otherwise use *P. triestinum*.
4. **Buy live *Nannochloropsis*** from a reef-aquarium supplier (sold as live coral and rotifer food). It is harmless; check it under the microscope and keep a clean sub-culture.
5. *(Dropped 2026-10-01: the kelp-farm and shellfish-hatchery emails and the aquaculture permit question.)*
6. **Order parts** (§8).
7. **Emails you send yourself**; I can draft each one (short, one ask).

## 6. The two screens (Phase 2)

| Screen | Vessels | Arms (n = 3 each) | Length | Measure |
|---|---|---|---|---|
| Bubbles | 500 mL cultures in 1 L flasks (the Sung & Gobler setup) | still; gentle (a few bubbles/s, CO₂ control); air stone at 25 mL/min; air stone at 300 mL/min; × 4 species (*Nannochloropsis*, *Micromonas*, *Skeletonema*, dinoflagellate); n = 3 (48 flasks) | 4 d (covers 48 h ON + 48 h regrowth) | cells daily (small algae: fluorometer + hemocytometer at 400×), pH, temperature, dawn DO |
| Peroxide | 250 mL flasks (93) | liquid H₂O₂ 0, 0.8, 1.6, 3.2, 6.4 mg/L × 5 species (*Nannochloropsis*, *Micromonas*, *Skeletonema*, *T. weissflogii*, *P. micans*); 3 daily 0.8 mg/L pulses (both small algae); percarbonate at 0.8 mg/L H₂O₂ × 3 species (both small algae, *Skeletonema*); Na₂CO₃ (*Micromonas*) | 72 h (+ *Artemia* to 96 h) | chlorophyll by fluorometer, hemocytometer (small cells, 400×) and Sedgewick-Rafter (large cells) counts, H₂O₂ kit and strips, *Artemia* 24 h + 96 h |
| *Seaweed, curcumin, shellfish* | | *dropped 2026-10-01* | | |

**Total:** about 141 vessels: 48 × 1 L flasks (bubbles) and 93 × 250 mL flasks (peroxide). They
are small and can share one shelf and light bank.

## 7. Loop run layout (Phase 4)

Two methods, **aeration and peroxide** (2026-10-01), run at the same time. They are likely to use
**different cultures** (a dinoflagellate for aeration; a small alga mixed with *Skeletonema* for
peroxide), so each method gets its own untreated arm A and its own pilot tanks:

| Arm | Tanks | Notes |
|---|---|---|
| A untreated, aeration culture | 3 | |
| B loop, aeration | 3 | relay → air pump, 0.6 L/min per litre |
| C reactive (starts at 50% of expected peak), aeration | 3 | |
| D false alarm, aeration | 3 | no nutrients |
| A, B, C, D, peroxide culture | 12 | peristaltic pump, 0.8 mg/L pulses |
| Pilot bloom (warm-up only), 2 per culture | 4 | pilot tanks can be reused as spares once the run starts |
| **Total** | **28 tanks (4-10 L)** | |

If the screens point both methods at the **same** culture, arm A and the pilots are shared (3 A +
2 × 9 + 2 pilots = 23 tanks), as in the earlier plan.

## 8. Shopping list (both methods, combined)

| Item | For | Approx. |
|---|---|---|
| Arduino Uno (+1 spare), relay, peristaltic dosing pump (12 V), wiring | controllers | $60 |
| DIY fluorometer parts × 3 (470 nm LED, photodiode, red filter, op-amp) | all | $90 |
| pH probe, DS18B20 × 6, DO kit, ammonia kit | all | $120 |
| 28 tanks (4-10 L) + ~141 flasks | all | $250 |
| 2 air pumps, manifold, needle valves, tubing (screen) | bubbles | $40 |
| Air pumps for the loop tanks (enough for the 9 aeration B, C and D tanks at 0.6 L/min per L), airline, check valves, air stones | bubbles | $60 |
| LED grow lights × 2 + timers | all | $60 |
| Sea salt, f/2 and f/4 medium, Sedgewick-Rafter chamber, hemocytometer | all | $100 |
| Cultures (NCMA, 5-6 strains incl. *Micromonas pusilla*) | all | $250-400 |
| Live *Nannochloropsis* (reef-aquarium supplier) | all | $15-25 |
| Sodium percarbonate, 3% H₂O₂, low-range kit and strips | peroxide | $60-90 |
| *Artemia* eggs | non-target | $10 |
| *(Curcumin, ethanol, kelp, mesh cages, oysters, mesh bags: dropped 2026-10-01)* | | |
| **Total** | | **about $1,100-1,300, assuming the sponsor lends the microscope, scale, micropipettes, glassware and meters** (about $1,575-1,865 without borrowing; `MATERIALS_LIST.md`) |

Much of this can be borrowed: ask the sponsor for the microscope, glassware and the pH/DO meters.

## 9. Changes this plan made to the method files (all applied by 2026-09-28; updated 2026-10-01)

- `00_CONTROL_LOOP.md` / `01_BUBBLES.md`: the main bubble test species becomes *Akashiwo sanguinea* (backup *P. triestinum*); bubbling may raise pH in dense cultures, so log pH in the still control too.
- `03_PEROXIDE_BAG.md`: a fixed per-pulse target replaces the freshwater dose-per-chlorophyll rule (now 0.8 mg/L per pulse, up to 3 pulses; was 1.6 in this list); `MAX_ON` 3 pulses; *Artemia* checked at 96 h.
- Add H3 (regrowth after OFF) to `00_CONTROL_LOOP.md` (done 2026-09-28).
- **2026-10-01:** `00_CONTROL_LOOP.md`, `01_BUBBLES.md`, `03_PEROXIDE_BAG.md`, `PROCEDURES.md` and `MATERIALS_LIST.md` updated for the two-method plan, the aeration delay outcome and the species panel; `02_SEAWEED.md`, `04_CURCUMIN.md` and `05_SHELLFISH.md` carry a "Dropped 2026-10-01" banner. (The 2026-09-28 changes to the curcumin and shellfish files stand in those files as a record.)

## 10. Risks

| Risk | Effect | Fallback |
|---|---|---|
| No sponsor by mid-October | the whole timeline slips | screens can shrink to 2 weeks; loop runs start mid-December and the bloom phase moves to January |
| Bubble screen: no panel species is slowed | aeration's delay result is likely negative (still reportable) | run the aeration loop on the dinoflagellate anyway and report the delay result honestly; or run a second peroxide dose level in those tanks, decided in `LOOP_PREREG.md` before nutrients go in |
| Peroxide screen: small algae not cut at 0.8 mg/L | H1a for peroxide likely fails | use the screen's lowest dose that cuts small cells and still passes the *Artemia* check (never above the 2.8 mg/L stop), decided before nutrients go in |
| Aquarium *Nannochloropsis* is mixed or contaminated | wrong species in the screen | clean sub-culture; NCMA *Nannochloropsis* as backup; *Micromonas* carries the size test alone |
| 2 µm cells can't be counted reliably | weak cell counts for the small algae | fluorometer is the main measure for the small algae, hemocytometer at 400× as a check, 5 µm size fraction in mixed tanks; say so in the write-up |
| Fluorometer disagrees with cell counts | the OFF rule is wrong | the OFF rule uses cell counts for peroxide; report glow per cell for both methods |
| Model never fires in a tank (month term, rescaling) | arm B has no model trigger | the rule trigger drives arm B; report the model's behaviour as a finding |
| Lab closed over break | missed counts | the bloom phase ends Dec 20 by design; the cool-down runs unattended |
| Arm A culture doesn't bloom in our tanks | every hypothesis fails | pilot bloom run during warm-up; backup culture flasks (§11) |
| Peroxide reservoir runs low or loses strength | doses drift | check the reservoir weekly with the low-range kit; refill (the one allowed maintenance) |

## 11. Make-or-break fixes (2026-09-28)

A review for holes that could sink a method. The details are in each method file; the shared
ones are in `00_CONTROL_LOOP.md`.

**Shared (all methods):**

| Hole | Fix | Where |
|---|---|---|
| Arm C ("after the peak") does 0-4% by construction, so it's a strawman | **Arm C now starts at 50% of the expected untreated peak** (a reactive manager). Re-run the Layer 2 simulation with it before writing `LOOP_PREREG.md` | `00_CONTROL_LOOP.md` |
| When the rule trigger takes over from the model is undefined | **Handover rule:** rule fired + model silent for 2 days → rule drives that tank; log which trigger fired. The model's skill is argued from Layer 1, not the tanks | `00_CONTROL_LOOP.md` |
| The fluorometer reads glow, not cells; treatments and time of day change glow per cell | Same sampling time daily, 15 min dark before reading, report glow per cell; counts decide OFF for peroxide | `00_CONTROL_LOOP.md` |
| Arm A may never bloom (culture crash), which fails every hypothesis | **Pilot bloom run** in 2 spare tanks per culture during warm-up; it also sets arm C's start and `C_ok`. Keep backup culture flasks | `00_CONTROL_LOOP.md` |
| Cell counting (28 tanks × ~10 min) is too much work | Phone photos through the microscope, count later in ImageJ; every 2 days, daily only around trigger and OFF; split between both team members | `00_CONTROL_LOOP.md` |
| *Phaeodactylum* is hardy and may under-respond | ***Skeletonema*** first (dominant Long Island Sound diatom) | `00_CONTROL_LOOP.md` |
| Nothing stopped the loop from pushing diatoms (oxygen makers) below normal | **H4** + a floor OFF rule: 2 days below 80% of the warm-up level → OFF; log daytime DO | `00_CONTROL_LOOP.md` |

**Per method:**

| Method | Hole | Fix |
|---|---|---|
| Bubbles | Bubbling adds CO₂, which helps growth and hides the stress effect | pH in every flask; gentle-bubbling control |
| Bubbles | A peak-cut test would fail by design (Layer 2: 25%) | **judged on delay** (days held below `C_ok`, hours ON, ON episodes), written down 2026-10-01 before data |
| Peroxide | Strips can't resolve 0.8 mg/L; bag overshoots | low-range peroxide kit; pump-dosed liquid 3% H₂O₂ as the main dose; **calcium peroxide bag dropped (2026-09-28)**, sodium percarbonate (registered-algaecide ingredient) is the comparison |
| Peroxide | ~2 µm cells can't be counted | fluorometer on single-species flasks + hemocytometer at 400×; size-fractionated chlorophyll with a 5 µm syringe filter in mixed tanks |
| *Seaweed, shellfish, curcumin* | *(fixes kept in their files as a record)* | *dropped 2026-10-01* |

**Added to the shopping list:** low-range peroxide test kit (~$30-60), 5 µm syringe filters and
syringes (~$20).

## Never claim
- That it prevents blooms in the open Sound; this is tanks only, aimed at enclosed or semi-enclosed water (harbors, shellfish beds, aquaculture pens, coastal ponds).
- That the device is field-ready.
- That it is safe without arm D's non-target data.
- Any result before it is measured; pre-register first.
