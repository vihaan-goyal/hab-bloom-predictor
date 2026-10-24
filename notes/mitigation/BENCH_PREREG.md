# Pre-registration: the bench treatment experiments (aeration and peroxide)

**Written 2026-10-24. Status: written before any tank data. No flask or tank has been inoculated,
and no culture has been counted for an experiment.**

This file fixes, before any data exist, how every bench treatment experiment is judged: the
hypothesis, the one primary endpoint and its formula, the secondary endpoints, the design, the
exclusions, and what counts as PASS, FAIL or INCONCLUSIVE. It uses the same approach as the forecast
tests (`notes/CALENDAR_BASELINE_PREREG.md`, `notes/PROSPECTIVE_2026_PREREG.md`): rules first, data
second, and the result is reported as it comes out.

- **Code:** `src/lab/bench_analysis.py` computes every endpoint and decision below, exactly as
  written here. It was written and tested on made-up data before any real data exist
  (`tests/test_bench_analysis.py`). Data sheets: `src/lab/templates/tank_log.csv` and `counts.csv`.
- **Sources:** `EXECUTION_PLAN.md` (§2, §3, §6, §7, §14), `00_CONTROL_LOOP.md`, `01_BUBBLES.md`,
  `03_PEROXIDE_BAG.md`, `PROCEDURES.md`, `LAYER2_SIM_RESULTS.md`. Where they disagree, this file
  follows the newest dated decision and lists the disagreement under "Open questions for Vihaan".
- **`LOOP_PREREG.md`** (planned for Nov 16-25, after the screens) may only fill in the items the
  screens choose by the rules below: the loop culture, the loop dose, `C_ok` from the pilot tanks and
  the tank volume. It cannot change an endpoint, a mark or a decision rule in this file.
- **Changing anything here** after the first flask is inoculated is a protocol change. It is added
  as a dated amendment at the bottom, says why, and the original rule is still reported.

**What this tests and what it does not.** This is a tank-scale test of a warning-and-treatment loop
on non-toxic algae. It does not show that blooms can be prevented in open water. The target setting
is enclosed or semi-enclosed water (harbors, shellfish beds, aquaculture pens, coastal ponds).
Aeration is expected to be the main treatment (Dr. P. Vlahos, UConn, 2026-10-15); peroxide is tested
as a short, acute response only.

---

## Part A. Rules that apply to every experiment

### A1. What is measured

**Primary measure: cell counts, as percent change against each vessel's own start.** Treatments are
judged on the percent change in cells/mL of each flask or tank against its own starting count,
confirmed by microscope counts (Dr. P. Vlahos, 2026-10-15; `EXECUTION_PLAN.md` §14). No µg/L
chlorophyll is needed for any treatment result. Peroxide can dim the chlorophyll glow without
killing cells, so the counts are the proof of a reduction.

**How a count becomes cells/mL** (done in the code, never by hand):

    cells/mL = cells counted ÷ (squares counted × volume of one square in mL) × dilution factor

| Chamber | One square | Used for |
|---|---|---|
| Hemocytometer (Neubauer), large corner square, 400× | 0.1 µL = 1 × 10⁻⁴ mL | *Nannochloropsis* (2-3 µm) |
| Hemocytometer, small central square | 0.004 µL = 4 × 10⁻⁶ mL | *Nannochloropsis* when very dense |
| Sedgewick-Rafter, 1 mm square | 1 µL = 1 × 10⁻³ mL | *Thalassiosira*, *Akashiwo* |

- The dilution factor is (sample + diluent + fixative) ÷ sample; 1 if undiluted.
- **At least 50 cells per sample:** keep counting squares (or the whole chamber) until 50 cells are
  counted. Samples with fewer are kept but flagged in the output (their counting error is above 14%).
- A zero count stays 0 cells/mL. For logarithms, it is replaced by half a cell in the counted volume.
- Two chambers counted for the same vessel and time are averaged.
- Large cells are counted for the mixed peroxide tanks by size: "small" (< 5 µm, *Nannochloropsis*)
  and "large" (*Thalassiosira*).

**Secondary measure: the DIY fluorometer** (LED on − off counts, minus that day's clean-seawater
blank). Every primary endpoint is also computed on fluorometer counts and reported as secondary.
It does not decide anything until the sensor is calibrated (`EXECUTION_PLAN.md` §14). Glow per
cell is reported at each count.

### A2. Effect sizes

- **Percent cut** (screens and peaks). For each vessel, `r = ln(N_t ÷ N_start)`. For a treated arm
  against its control: `cut = 1 − exp(mean r_treated − mean r_control)`. A 50% cut means the treated
  vessels grew to half of what the control vessels grew to, each measured against its own start.
- **The 95% interval** comes from a Welch t-interval on the r values (it does not assume both arms
  have the same spread), converted to the percent scale.
- **Days** (aeration delay) and **survival points** (*Artemia*) use the Welch interval on the raw
  difference in means.
- **Exact permutation p** (one-sided) is printed next to each comparison as a check. With 3 vs 3
  vessels there are only 20 ways to split them, so the smallest possible p is 0.05; it does not
  decide anything.

### A3. How every test is decided

Each effect hypothesis has a **mark** (the effect it claims, e.g. a 50% cut).

| Decision | Rule |
|---|---|
| **PASS** | the estimate reaches the mark **and** the lower end of the 95% interval is above zero (the effect is real) |
| **FAIL** | the upper end of the 95% interval is below the mark (the data rule out an effect as large as claimed) |
| **INCONCLUSIVE** | anything else (with 3 vessels per arm the interval is often too wide to decide) |

Also printed for every PASS: whether the whole interval clears the mark (lower end ≥ mark). That is
the stricter reading the Layer 2 simulation called "the honest interval". With n = 3, a result can be
"consistent but underpowered", and it is reported that way.

**Safety checks (non-inferiority).** For *Artemia* survival, treated minus control, in percentage
points, with a margin of −20 points (`PROCEDURES.md` P5):
- **PASS (safe):** the lower end of the 95% interval is above −20;
- **FAIL:** the estimate is below −20;
- **INCONCLUSIVE:** otherwise. Safety is then **not** claimed.

The screens' go/no-go *Artemia* gates use the point estimate only (survival more than 20 points below
control fails), as `PROCEDURES.md` P5 already says.

### A4. Multiplicity: one primary per experiment

- There are **four primary hypotheses**, one per experiment: S1 (aeration screen), S3 (peroxide
  screen), H1-delay (aeration loop) and H1a (peroxide loop). Each answers a different question and
  decides a different thing. Each is tested once at the 95% level. A PASS needs the interval to
  exclude zero, which is a one-sided 2.5% test. If all four treatments truly did nothing, the chance
  that at least one passes by luck is at most about 10%. That is stated in the write-up.
- **Fixed sequence:** the key secondary of each loop run (H1b for peroxide; H1-delay B vs C for
  aeration) is tested only if that run's primary PASSES. Otherwise it is reported as "NOT TESTED".
- **Every other secondary** is printed with its unadjusted interval, labelled "secondary", and
  cannot turn a failed or inconclusive primary into a claim.
- **Safety (H2 and the gates) is not adjusted:** any FAIL counts.

### A5. Randomisation

- `python src/lab/bench_analysis.py layout --experiment <name> --seed <setup date as YYYYMMDD>` gives
  every vessel a neutral code (e.g. `AL07`) and a random shelf position. The seed is the setup date,
  written in the design log, so anyone can re-create the layout.
- Arms are mixed across the shelf and the light bank, so no arm sits in the brightest or warmest spot.
- The inoculum for each experiment comes from one mixed culture, split into all vessels, with the
  same starting count (P2, P4).

### A6. Blinding (where it can be done)

- **The person who counts cells does not know the arms.** Vessels carry only their neutral code. The
  code → arm key is kept by the other team member (or the Direct Supervisor). Counting is done from
  phone photos in ImageJ, by sample code, where possible.
- **The treatments themselves cannot be hidden:** bubbles are visible, and the pump is audible. The
  fluorometer and the alerter log are automatic, so they need no blinding.
- **Exclusions are decided before the arms are revealed** whenever the cause is visible without the
  key (contamination, a broken vessel).

### A7. Exclusions (fixed now; never based on the result)

A vessel is excluded from the main ("per-protocol") analysis only for one of these reasons. Each is
logged with its reason in the `excluded` and `exclusion_reason` columns.

| Reason | Rule | Checked by |
|---|---|---|
| Contamination | foreign cells > 10% of the cells seen, or grazers (ciliates, rotifers) seen, in **2 counts in a row** | code (from `foreign_cells`, `grazers_seen`) |
| Crash before treatment (loop runs) | any count before nutrients-in (day 21) below 10% of the vessel's day-0 count | code |
| Dose error (peroxide screen) | the first peroxide reading after dosing is outside 50-150% of the planned dose | code |
| Airflow error (aeration screen, low and high arms) | measured airflow > 25% off target on 2 checks in a row during the 48 h ON | code |
| Equipment failure | the vessel did not get its assigned treatment for > 12 h (pump, relay, air line), or the wrong dose went in | logged by hand |
| Lost vessel | spilled, broken, more than 10% of the volume lost, or wrong culture inoculated | logged by hand |

- **Not exclusions:** a safety stop, the floor OFF rule, `MAX_ON`, a crash *after* treatment starts,
  or a tank that does not bloom. These are outcomes, and the tank stays in its arm (like
  "intention to treat").
- **Both analyses are reported:** per-protocol (exclusions applied; this is the main one) and
  all-vessels (nothing excluded). The code prints every primary or safety decision that changes
  between the two.
- **Too few vessels:** if exclusions leave fewer than 2 vessels in an arm, that comparison is
  INCONCLUSIVE.

### A8. Validity checks (they exclude nobody, but can make a result INCONCLUSIVE)

- **Screen control crashed:** if the control arm's geometric-mean N_t ÷ N_start at the endpoint time
  is below 0.5, that species' comparison is INCONCLUSIVE.
- **No bloom in the loop:** if arm A's geometric-mean peak ÷ warm-up level is below 2, there was no
  bloom to treat, and H1a, H1b and H1-delay are INCONCLUSIVE for that run.
- **Pilot:** `C_ok` comes from the 2 pilot tanks. With no pilot data, the loop endpoints that need
  `C_ok` cannot be computed.

### A9. Stopping and safety rules (already in the plan; repeated here so they cannot drift)

- **Emergency OFF in that tank at any time:** DO < 4 mg/L; pH below 7.6 or above the pH ceiling (rule below); H₂O₂ residual
  > 2.8 mg/L (no more pulses this episode); *Artemia* survival more than 20 points below control.
- **Aeration's own limits:** water more than 2 °C above the untreated control (pump heat);
  evaporation over 5% of the volume (top up with fresh water).
- **Peroxide:** a new pulse only if the residual is ≤ 0.5 mg/L; at most 3 pulses per episode.
- **Floor OFF (H4):** a treated tank reading below 80% of its warm-up mean on 2 days in a row is
  switched OFF (not used in arm D).
- **Go rule:** a screen that fails its *Artemia* gate stops that method's loop run.
- Every stop is logged as an event and reported. The tank stays in the analysis.

### A10. Reported whatever the outcome

- Every vessel's raw counts, fluorometer readings, pH, temperature, DO and peroxide.
- Every exclusion with its reason, and both analysis sets.
- Every hypothesis, including the ones that FAIL or are INCONCLUSIVE, with its interval.
- Every safety stop, floor OFF, `MAX_ON`, skipped pulse, refill and human intervention.
- Treatment used (hours ON, ON episodes, mg of H₂O₂) and which trigger switched each tank ON
  (model, rule, reactive, forced).
- The fluorometer version of every primary endpoint, and glow per cell.

---

## Part B. The experiments

### B1. Aeration screen (S1)

| | |
|---|---|
| **Hypothesis S1** | At 0.6 L/min per litre (300 mL/min into 500 mL), the dinoflagellate *Akashiwo sanguinea* has ≥ 30% fewer cells after 48 h than the still control, and the diatom *Thalassiosira* is not reduced |
| **Design** | 500 mL cultures in 1 L flasks. 4 arms (still; gentle, a few bubbles per second as the CO₂ control; low 25 mL/min; high 300 mL/min) × 3 species (*Nannochloropsis*, *Thalassiosira*, *Akashiwo*) × n = 3 = **36 flasks**. Bubbling for 48 h, then OFF and 48 h of regrowth |
| **Counts** | 0, 24, 48, 72 and 96 h (± 4 h). pH and temperature in every flask daily; airflow checked daily; dawn DO in the high and still arms after 48 h |
| **Primary endpoint** | S1a: % cut in *Akashiwo* cells at 48 h, high vs still, `1 − exp(mean r_high − mean r_still)` with `r = ln(N_48h ÷ N_0h)`. Mark **30%**. S1b: the same for *Thalassiosira*; "not reduced" = point estimate of the cut **< 20%** |
| **Decision** | **S1 PASS** = S1a PASSES and S1b is below 20%. **S1 FAIL** = S1a FAILS, or the *Thalassiosira* cut is ≥ 20%. Otherwise INCONCLUSIVE |
| **Secondary** | high vs gentle (separates stirring from CO₂), and low vs still, for every species; *Nannochloropsis* high vs still (no mark); regrowth after OFF (days for each bubbled arm to reach the still arm's 48 h count, "> 2 days" if not reached by 96 h); pH and dawn-DO differences, high minus still; the fluorometer version of S1a; *Artemia* 24 h in high vs still water (gate, if run); cell shape under the microscope (broken or intact) |
| **What it decides** | The aeration loop culture is *Akashiwo* unless S1a FAILS. If it fails, the culture is the species with the largest point-estimate cut at 48 h (high vs still), and if no species shows any cut, *Akashiwo* anyway (`EXECUTION_PLAN.md` §10: run it and report the delay result honestly) |
| **Expected** | Unknown, which is why it is a screen. Sung & Gobler (2026) saw 21-63% cuts in a different dinoflagellate (*Margalefidinium*). Sullivan & Swift (2003) found some dinoflagellates unaffected or helped by stirring. Diatoms may be helped |

### B2. Peroxide screen (S3), including the size test (H5)

| | |
|---|---|
| **Hypothesis S3 (primary)** | Three daily 0.8 mg/L H₂O₂ pulses (the loop dose, each only if the residual is ≤ 0.5 mg/L) cut *Nannochloropsis* cells by ≥ 50% at 72 h against the untreated control, **and** *Artemia* survival in that water is within 20 points of control at both 24 h and 96 h |
| **Design** | 200 mL in 250 mL flasks. H₂O₂ 0, 0.8, 1.6, 3.2, 6.4 mg/L × 3 species × n = 3 (45); 3-pulse arm, *Nannochloropsis* (3); sodium percarbonate at 0.8 mg/L H₂O₂ × 3 species (9); sodium carbonate ~2.0 mg/L, *Nannochloropsis* (3). **60 flasks.** Doses through the 0.1% working solution (P6) |
| **Counts and readings** | Cells at 0, 24 and 72 h (hemocytometer at 400× for *Nannochloropsis*, Sedgewick-Rafter for the others). H₂O₂ with the low-range kit at 0 (15 min after dosing), 1, 4 and 24 h, and before each pulse |
| **Artemia** | Water drawn 1 h after the last dose (3-pulse arm: after the third pulse at 48 h; single-dose arms and control: 1 h after dosing), 10 nauplii per 10 mL, 3 wells per flask; survivors at 24 h and 96 h |
| **Primary endpoint** | % cut at 72 h, 3-pulse vs control, *Nannochloropsis*: `1 − exp(mean r_pulse − mean r_ctrl)`, `r = ln(N_72h ÷ N_0h)`. Mark **50%**. Gate: survival (3-pulse minus control) ≥ −20 points at 24 h and at 96 h |
| **Decision** | **S3 PASS** = the cut PASSES and both gates pass. **S3 FAIL** = the cut FAILS, or a gate fails. Otherwise INCONCLUSIVE |
| **Secondary** | (a) replication of the source: one 1.6 mg/L dose, *Nannochloropsis* cut at 24 h, mark 50%, with *Thalassiosira* and *Akashiwo* "spared" (point cut < 20%); (b) a single 0.8 mg/L dose at 24 h and 72 h ("transient" if the 72 h cut is smaller than the 24 h cut); (c) 3 × 0.8 against a single 1.6 at 72 h; (d) percarbonate against liquid H₂O₂ at 0.8 mg/L, each species, 72 h; (e) sodium carbonate against control: a cut ≥ 20% means part of percarbonate's effect is from carbonate and pH; (f) the fluorometer version of the primary (expected to over-state the cut, because peroxide dims the glow) |
| **H5 (secondary): sensitivity falls with cell size** | At 24 h, the % cut ranks *Nannochloropsis* > *Thalassiosira* > *Akashiwo*. **PASS:** the ranking holds at ≥ 3 of the 4 doses (0.8, 1.6, 3.2, 6.4) **and** both larger species have a point cut < 20% at 0.8 mg/L. **FAIL:** it holds at ≤ 1 dose. Otherwise INCONCLUSIVE. Stated limit: with one species per size, cell size and taxon cannot be separated |
| **What it decides** | Loop dose: 3 × 0.8 mg/L if S3 PASSES. Otherwise the lowest dose ≤ 2.8 mg/L that cuts *Nannochloropsis* ≥ 50% at 72 h and passes both *Artemia* gates, which can only be the single 1.6 mg/L dose. If none qualifies, the loop runs at 0.8 mg/L anyway and is reported (H1a is then expected to fail). A failed *Artemia* gate at the loop dose stops the peroxide loop run (go rule) |
| **Expected** | Randhawa et al. 2012: 24 h EC50 0.91 mg/L for ~2 µm cells, which suggests ≥ 50% at 1.6 mg/L and a smaller, transient cut at 0.8 mg/L. *Nannochloropsis* was never tested in our sources, so a miss is a real result about that species |

### B3. Peroxide half-life (added from the Vlahos call, 2026-10-15)

| | |
|---|---|
| **Question** | How fast does H₂O₂ disappear in our seawater, with and without algae? (Reported; no pass mark) |
| **Design** | Plain Sound-matched seawater with no algae: liquid H₂O₂ at 0.8 mg/L (3 flasks) and sodium percarbonate at the same H₂O₂ dose (3 flasks; this is also the percarbonate content check in `PROCEDURES.md` S3 step 1). Also every dosed screen flask (B2), from its 0, 1, 4 and 24 h readings |
| **Endpoint** | Per flask, a straight-line fit of ln(residual) against time over 0-24 h, using readings above the kit's lowest step (0.1 mg/L, see open questions) and at least 3 of them: half-life = ln 2 ÷ decay rate. Per group: geometric mean with a 95% t-interval |
| **Design check** | A 0.8 mg/L pulse falls to ≤ 0.5 mg/L within 24 h only if the half-life is ≤ 35.4 h. If it is longer, daily pulses would be skipped by the re-dose rule. That is reported as a design finding |
| **Expected** | 2.4-14.4 h, the range used in the Layer 2 simulation (`src/sim/method_params.csv`, < 10 h in coastal water); faster with algae and bacteria than in plain seawater |

### B4. Aeration loop run

| | |
|---|---|
| **Hypothesis H1-delay (primary)** | Forecast-triggered aeration (arm B) holds the bloom below `C_ok` for more days than untreated tanks (arm A) |
| **Design** | Tanks (4-10 L, volume fixed in `LOOP_PREREG.md`), the culture chosen by S1. Arms A untreated, B forecast loop, C reactive (ON when the count passes 50% of the expected peak), D false alarm (no nutrients, forced ON on day 21, floor off), **n = 4 each** (decided 2026-10-24), plus 2 pilot tanks: 18 tanks per loop experiment. Warm-up days 0-21, nutrients-in on day 21 (A-C), bloom phase days 21-40, cool-down days 40-45. Air at 0.6 L/min per litre, X = 48 h, `MAX_ON` 192 h per episode, bench trigger p ≥ 0.45 with the rule trigger and handover (`00_CONTROL_LOOP.md`) |
| **Counts** | Every 2 days, and daily around each ON and OFF. Fluorometer, pH, temperature and DO daily |
| **`C_ok`** | 50% of the mean pilot peak, in cells/mL (each pilot tank's highest count, averaged). Fixed from the pilots before nutrients-in |
| **Primary endpoint** | For each tank, the number of days from day 21 to day 40 (20 days) on which its count is below `C_ok`. Counts between count days are filled in by straight-line interpolation of ln(count). A tank with more than 2 uncovered days gets no value. Effect: mean days(B) − mean days(A), Welch 95% interval. Mark **2 days** (one X) |
| **Decision** | A3 rule with mark 2 days. INCONCLUSIVE if arm A did not bloom (A8) |
| **Key secondary** | H1-delay B vs C, same rule, tested only if the primary PASSES |
| **Secondary** | H1a (peak ÷ warm-up level, B vs A, % cut, mark 50%); H1b (B vs C on the peak, mark 0); the day of the peak in each arm; H2-B (*Artemia* in B vs A); the fluorometer versions of H1a and H1-delay |
| **H2 (safety)** | *Artemia* 24 h survival in tank water at each re-measure. Per tank, the worst assay between day 21 and day 45. D minus A in points, A3 safety rule (margin −20) |
| **H3 (reported)** | For each B tank, days from its last OFF until the count is back above `C_ok` ("more than N days" if not by day 45). For aeration it sets how often the device would re-run |
| **H4 (secondary)** | The warm-up mean is each tank's mean count from day 14 to day 21. **PASS** if arm B's 3-tank mean count ÷ warm-up mean never falls below 0.80 on any count day from 21 to 45, **and** arm B's mean daytime DO on each day stays at or above its warm-up mean minus 0.5 mg/L (kit resolution). Otherwise FAIL |
| **Reported** | Hours ON and ON episodes (reruns) per tank in B, C and D; safety stops; human interventions per tank per week; which trigger switched each tank ON |
| **Expected (Layer 2, chlorophyll not cells)** | Aeration mostly delays the bloom: a 25% peak cut [9, 48], B reaching `MAX_ON` in 99% of runs, the peak about 8 days later in the earlier run. H1-delay itself was not simulated for aeration, so there is no numeric expectation |

### B5. Peroxide loop run

| | |
|---|---|
| **Hypothesis H1a (primary)** | Forecast-triggered 0.8 mg/L peroxide pulses (arm B) cut the small-cell bloom peak by ≥ 50% compared with untreated tanks (arm A) |
| **Design** | As B4, with *Nannochloropsis* mixed with *Thalassiosira* (or the culture S3 points to), the dose chosen by S3, X = 24 h per pulse, `MAX_ON` 3 pulses, re-dose only if the residual is ≤ 0.5 mg/L. Residual measured before each pulse |
| **Counts** | As B4, counted by size: small (*Nannochloropsis*) and large (*Thalassiosira*) |
| **Primary endpoint** | Per tank, `r = ln(highest small-cell count from day 21 to day 45 ÷ warm-up mean (days 14-21))`. Effect: `1 − exp(mean r_B − mean r_A)`, Welch 95% interval. Mark **50%** |
| **Decision** | A3 rule with mark 50%. INCONCLUSIVE if arm A did not bloom |
| **Key secondary** | H1b: B's peak lower than reactive C's, `1 − exp(mean r_B − mean r_C)`, mark 0 (B simply better). Tested only if H1a PASSES |
| **Secondary** | H1-delay (days below `C_ok`, B − A); H5 in the tank (the large-cell peak cut, B vs A, set beside the small-cell cut: H5 expects small ≫ large); the fluorometer versions; H2-B |
| **H2 (safety)** | As B4, but at both 24 h **and** 96 h (delayed deaths); both must PASS to claim the false alarm was safe |
| **H3, H4, reported** | As B4, plus mg of H₂O₂ dosed per tank and skipped pulses |
| **Expected (Layer 2, chlorophyll not cells)** | B cuts the peak 74% [57, 83]; the 95% interval clears 50% in 80% of simulated runs with 3 tanks per arm (92% with 4). Reactive C cuts 24%. B − A days below `C_ok` +9.7 [6.7, 15]. False-alarm harm 0% |

---

## Part C. Summary

| Experiment | Hypothesis | Role | Endpoint (cells) | Mark | PASS / FAIL |
|---|---|---|---|---|---|
| Aeration screen | S1 | **primary** | *Akashiwo* % cut at 48 h, high vs still; *Thalassiosira* cut < 20% | 30% | A3 on *Akashiwo* and the diatom spared / A3 FAIL or diatom cut ≥ 20% |
| Peroxide screen | S3 | **primary** | *Nannochloropsis* % cut at 72 h, 3 × 0.8 vs control; *Artemia* gate at 24 h and 96 h | 50%; −20 points | A3 on the cut and both gates / A3 FAIL or a gate fails |
| Peroxide screen | H5 | secondary | ranking of % cuts by size at 24 h | ranking at ≥ 3 of 4 doses | ≥ 3 doses and both large species spared at 0.8 / ≤ 1 dose |
| Half-life | (none) | reported | H₂O₂ half-life, h | none | reported; > 35.4 h flagged |
| Aeration loop | H1-delay | **primary** | days below `C_ok`, days 21-40, B − A | 2 days | A3 |
| Aeration loop | H1-delay B vs C | key secondary | same, B − C | 2 days | A3, only if the primary PASSES |
| Peroxide loop | H1a | **primary** | small-cell peak ÷ warm-up, B vs A, % cut | 50% | A3 |
| Peroxide loop | H1b | key secondary | same, B vs C | 0 | A3, only if H1a PASSES |
| Both loops | H2 | safety | *Artemia* survival, D − A, worst assay | −20 points | lower end > −20 / estimate < −20 |
| Both loops | H4 | secondary | B lowest mean count ÷ warm-up; daytime DO | 0.80; −0.5 mg/L | both hold / either fails |
| Both loops | H3 | reported | days from last OFF back above `C_ok` | none | reported |

---

## Open questions for Vihaan

These are places where the existing notes disagree, or where a number had to be chosen for this
file. Each is decided as written above unless you change it **before the first flask is
inoculated** (then add a dated amendment).

1. **How strict is PASS?** Here PASS = the estimate reaches the mark and the interval excludes zero.
   The stricter reading (the whole interval clears the mark, Layer 2's "honest interval") is printed
   too. Which one is the headline? With n = 3, the strict one passes only ~80% of the time even if
   peroxide works as simulated.
2. **H1-delay mark of 2 days.** The plan only says "interval of B − A above 0". I added a 2-day mark
   (one X) so that a no-effect result can FAIL instead of always being INCONCLUSIVE. Keep it?
3. **H1b mark of 0.** As written ("B's cut is larger than C's"). Layer 2 also showed a 20-point margin
   (not pre-registered). Keep 0?
4. **pH limit: DECIDED 2026-10-24 (Vihaan) — measure it, by a rule fixed now.** A dense bloom raises pH
   by itself (photosynthesis uses up CO₂), so a fixed 8.6 could stop treatment because of the bloom, not
   the treatment. The rule:
   - **Measure:** log pH daily in the untreated pilot tanks through warm-up and bloom, and before and after
     every treatment in the flask screens (aeration, peroxide, percarbonate, carbonate control). Reported,
     not tested.
   - **Set:** pH ceiling = highest pH reached by the untreated pilot tanks + 0.2, **never below 8.6 and
     never above 9.0** (above 9, pH alone inhibits algae and would confound the result). The lower limit
     stays 7.6.
   - **When:** fixed from the pilots before the first loop tank gets nutrients (day 21), written in
     `LOOP_PREREG.md`, and used as the controller's `--ph-max` for both methods. Until then 8.6.
     `bench_analysis.py` computes it (`ph_ceiling`) and applies it to the safety checks.
   - This replaces both the 7.6-8.6 rule and the 9.0 in `03_PEROXIDE_BAG.md` / `PROCEDURES.md` for the
     loop runs.
5. **Cells, not chlorophyll, as the primary measure.** This follows the newest decision (Vlahos,
   2026-10-15, written 2026-10-18). The older files (`EXECUTION_PLAN.md` §2 and §3,
   `00_CONTROL_LOOP.md`) still say "peak chlorophyll (and cell count)" with `C_ok` in µg/L. The
   controller still switches on the fluorometer in its own units; the analysis's `C_ok` is in
   cells/mL, set from the same pilot tanks. OK?
6. **Peroxide loop primary = small cells only** (*Nannochloropsis*), not the total, because the large
   diatom is meant to be spared. OK?
7. **Your research plan (`forms/RESEARCH_PLAN_REGISTRATION.md`)** still lists the old species
   (*Skeletonema*, *T. weissflogii*, *Phaeodactylum*, *P. micans*, *P. triestinum*, *Micromonas*), "4
   species" in the aeration screen, and peroxide counts at 24, 48 and 72 h. The panel became the three
   bought cultures on 2026-10-11. You may want to update it yourself (and check whether the SRC needs
   to know).
8. **H₂O₂ reading times.** `03_PEROXIDE_BAG.md` says 1, 4, 12 and 24 h; `PROCEDURES.md` S3 and the
   Vlahos advice say 0, 1, 4 and 24 h. I followed 0, 1, 4, 24 h (a 12 h reading, if taken, is used in
   the fit).
9. **The kit's lowest step.** The half-life fit ignores readings ≤ 0.1 mg/L. That is a placeholder:
   replace it with your kit's real lowest step before the screen.
10. **Half-life flasks.** Liquid H₂O₂ in plain seawater (3 flasks) is new. The percarbonate check
    (3 flasks) was already planned. Are 6 extra flasks OK?
11. ***Artemia* in the aeration screen.** `EXECUTION_PLAN.md` §2 lists a 24 h *Artemia* check for
    bubbles, but `PROCEDURES.md` S1 does not include it. It is a gate here only if it is run. Run it?
12. **Warm-up window.** "Warm-up mean" is fixed here as days 14-21. The alerter's `warm` setting
    should use the same window.
13. **Script name.** `EXECUTION_PLAN.md` §4 and `PROCEDURES.md` say the loop runs are analysed with
    `src/lab/analyze_lab.py`. That is the Phase 11 clay script. The bench uses `bench_analysis.py`.
14. **Tanks per arm: DECIDED 2026-10-24, 4 per arm** for both loop experiments (Vihaan). With 4, the simulated peroxide effect clears the 50% mark in 92% of runs instead of 80%.
    The flask screens stay at n = 3.
15. **Counting at tank densities.** At about 10⁴ cells/mL, 4 hemocytometer squares hold only about
    4 cells. The 50-cell minimum means counting many more squares, using the Sedgewick-Rafter slide
    for large cells, or concentrating the sample (letting it settle). Try this on the pilot tanks.

## Amendments

None yet.
