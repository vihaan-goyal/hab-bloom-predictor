# Lab protocol: forecast-triggered magnetic clay flocculation (design v8)

Standalone bench procedure at the current settings: design v7-final plus Amendment A1 (notes/DEVICE_PROTOTYPE.md). If this protocol and the design record disagree, the design record's Amendment A1 table governs; report the conflict. Pre-registered hypotheses and bands: notes/SCIENTIFIC_METHOD.md Phase 11. Simulation predictions: notes/DEVICE_SIMULATION.md.

**What the experiment answers.** When a forecast row alerts, does a magnetic clay dose remove a Long Island Sound diatom at pre-bloom density, and how much of the clay comes back out on a magnet instead of staying on the bottom?

**Headline numbers:** removal (% of cells gone at 5 h, control-corrected) and recovery (% of dosed magnetite back on the magnet). Predicted recovery about 95%, an upper bound.

---

## 1. Before any hands-on work

| By | Item |
|---|---|
| Sep 16-18 | Order CCMP1332 *Skeletonema marinoi* from NCMA (Bigelow); get the ship date in writing. Live cultures ship Wednesdays, at least two weeks out; earliest arrival Thu Oct 8. |
| Sep 16-18 | Order materials (section 10). Quote the N52 blocks first. |
| Sep 22 | Book the fume hood, water bath, spectrophotometer, 0.001 g balance, microscope, drying oven. Email the partner lab: ICP Al (5 samples), Sedgewick-Rafter loan, counting help. |
| Sep 25 | ISEF Forms 1A, 1, 3, 1B signed. Adult Sponsor; Designated Supervisor (school chemistry teacher) on Forms 1 and 3. Signed after-hours agreement (student, parent, Designated Supervisor, principal). Nothing hands-on before this. |
| Sep 28-Oct 2 | Build the rake, jar rig, controller, pull-test holder. Prepare two sterile 2 L carboys of f/2. |
| Oct 3-4 | Collect the first 40 L of seawater (driver needed). |

A second cell counter must be recruited and trained on chain diatoms before Nov 9.

---

## 2. Equipment

**Device tank.** 10 gal glass aquarium, 20 L working volume (16 cm deep, 50 x 25 cm floor).

**Magnet rake.**
- 5 stacks, each 4 N52 blocks 40 x 20 x 10 mm, **same pole down** on all stacks.
- Each stack epoxied to a carrier strip, fixed to a nylon end-block with an 8 mm nylon rod through a **removable top cap**, inside a capped 1-1/4 in square acrylic tube (1/8 in wall).
- One pole face flat against the bottom tube wall, foam shim above; PTFE tape on that wall and on the outer side walls of the two end tubes.
- Tubes held in slots in wooden end rails, 33 mm centre to centre (screwed, not glued); 3 mm skids; two handles.
- Neighbouring stacks repel at about 12 kgf; the end stacks press outward at about 13 kgf. Assemble one stack at a time in the locked frame.
- 30 x 25 cm release tray; wash bottle.

**Mixing.** Cordless drill with paint paddle (rapid mix, ~300 rpm). Tank paddle motor **48-50 rpm**, 15 cm paddle (G ~60). Jar rig: three identical **~100 rpm** 12 V gearmotors with 6 x 2 cm paddles, three 2 L jars at a time.

**Controller.** ESP32, 2-channel relay (pump, paddle), microSD logger, 10-minute timer relay in series with the pump, 12 V 5 A fused supply behind a GFCI outlet. Peristaltic pump ~60 mL/min.

**Measurement.** Sedgewick-Rafter 1 mL chamber, Lugol's iodine, microscope; 47 mm GF/F filters, 90% acetone, spectrophotometer (664/750 nm); DO meter (record whether optical or membrane); pH pen; salinity refractometer or meter; DRV5055A4 Hall sensor; 0.001 g balance with the pull-test rig; drying oven at 65 C; syringes (10, 50, 60 mL) on silicone tubing; 6 mm siphon tubing; 5 L carboy; trace-metal HDPE bottles and 0.45 um syringe filters; one spare N52 block for settling.

---

## 3. Materials and preparation

### 3.1 Seawater (~220 L over the project)
- Collect Long Island Sound water at Milford or Stratford, 40-50 L on alternate weekends. Store dark and cold (<= 10 C); use within two weeks. Record salinity and pH for each batch.
- **Diluent** (tank and jars): gravity-filter through a 5 um filter bag.
- **Culture water**: additionally pasteurise (2 L at 75 C for 30 min in the water bath) or 0.2 um filter.

### 3.2 Culture
1. On arrival (earliest Thu Oct 8) let the tube stabilise 12 h.
2. Next day move half the biomass into each of two 2 L f/2 carboys (A and B).
3. Grow at 18-20 C under a cool LED.
4. When carboy A reaches >= 1e6 cells/mL, scale it to 20 L; target >= 5e5 cells/mL.
5. Carboy B supplies the stock pilot (section 5.2) and is the backup.
6. Count with every transfer and log chain length. Bleach used culture before disposal.

### 3.3 Clay (dry blends, kept dry)
| Mix | Recipe per batch | Use |
|---|---|---|
| Magnetic blend | **8 g magnetite pigment + 25.3 g EPK kaolin + 6.7 g PAC powder** (28-30% Al2O3) = 40 g, 20% magnetite | all magnetic runs; make three batches |
| Plain clay | 25 g EPK kaolin + 5 g PAC powder | plain arm and plain blank |
| Un-PAC'd mix | kaolin + magnetite 35 : 15, 5 g | week-1 route P trial only |

Weigh powders in the hood with a dust mask. If the week-1 gate fails, re-blend at 37.5% magnetite from the third batch.

### 3.4 Stock (paste 24 h before each use, on a school day)
- Tank run: 4 g dry blend in 40 mL. Jar batch: 1.1 g in 11 mL. Both are 100 g/L.
- **Route S:** paste in filtered seawater. **Route D:** paste in DI water. The route is chosen on Oct 30 (section 5.2); until then both are tested.
- **Dose = total dry blend mass.** 0.2 g/L = 4 g per 20 L tank = 3.6 mL of stock per 1.8 L jar.

---

## 4. Calibrations (week 1, Oct 5-9)

### 4.1 Pull test (every day it is used)
- Glue the sample vial into a >= 100 g holder on a 10 cm plastic riser on the balance pan. Fix one N52 block on a stand 30-40 mm above the vial.
- Read magnet-only zero; then magnetite standards 5, 10, 20, 50, 100, 200 mg; fit a line.
- Accept the day only if r^2 >= 0.99 and the zero drifts <= 2 mg (read before and after each sample). Log date, slope, intercept, r^2, zeros to CSV. Repeat a failed day.
- Once: 0.5 g and 1.0 g magnetite mixed into kaolin at pad fill height, to check linearity at scale.
- Samples: grind the dried pad, pull-test **three 150 mg aliquots** (~30 mg magnetite each), report the mean as magnetite-equivalent.

### 4.2 Detachment test
1 g stock in 1 L filtered seawater, rig at ~100 rpm for 15 min, hold on a magnet 10 min, decant, dry and weigh the non-magnetic residue. Routes S and D, fresh and 24 h aged (4 g total).

**Gate Fri Oct 9:** > 30% pull loss or > 30% non-magnetic residue on a route -> re-blend at 37.5% and retest.

### 4.3 Hall check
DRV5055A4 readings at 10, 15, 20, 30 mm from a tube face, compared with the field model (the sensor saturates above ~170 mT).

### 4.4 Controller dry run
ESP32 reads a hand-written test ledger row. It doses only if `status = ok`, `alert = 1`, `onset_row = 1` and not locked out; it fires the pump relay 40 s and the paddle relay 10 min, logs every poll and action to SD. Endpoint unreachable or a parse error = hold, never dose from a cached row.

---

## 5. Experiments in order

### 5.1 Clay-only blanks (gate for everything else)
| Date | Run |
|---|---|
| Wed Oct 14 | Blank 1: route S (paste Tue Oct 13) |
| Thu Oct 15 | Blank 2: route D (paste Wed Oct 14) |
| Tue Oct 20 | Plain-clay blank (paste Mon Oct 19) |

Run the tank sequence (section 6) with filtered seawater and no culture; skip cell counts. Fraction (iii) is siphoned at T93 and at 07:30 the next school morning.

**Gate Fri Oct 23, each route on its own blank:** >= 70% of dosed solids and >= 80% of magnetite-equivalent recovered. The plain blank should recover almost nothing (it is described, not tested, n = 1).
If a route fails, **diagnose before changing hardware**: floc photo at T11 and a 10 mL column count at T20. Loss in the water column -> chemistry (other route, or dose 0.4 g/L). Loss on the floor -> add a centre pass. Loss in the tube rinse -> slow the withdrawal. A failing route leaves the pilot; if both fail, retry route S Fri Oct 30 after the fix.

### 5.2 Stock-route pilot (Wed Oct 28, carboy B)
- Six 1.8 L jars at 1e4 cells/mL, 0.2 g/L, the routes that passed Oct 23, n = 2, run as two rig rounds with one of each route per round.
- Pipette 3.6 mL stock into the vortex in the first 10 s of a 60 s rapid mix; then ~100 rpm for 10 min; settle.
- 5 h counts (19:30) plus one t0 count from the batch bottle. Raw removal = 1 - Ct/C0, route against route.
- **Decision Fri Oct 30:** a route that wins by > 15 removal points (mean of two) becomes the recipe; within 15 points, route S stays. Log the six counts and the decision as a dated commit before batch 1.
- **Design freeze Fri Nov 6** (Nov 13 if the culture arrived after Oct 8).

### 5.3 Jar experiments (three weekly batches: Thu Nov 12, Thu Nov 19, Tue Dec 1)
Each batch, from one batch bottle at 1e4 cells/mL:

| Rig round | Jars |
|---|---|
| 1: three-arm comparison | untreated, plain clay 0.2 g/L, magnetic blend 0.2 g/L |
| 2 and 3: dose screen | magnetic blend at 0.05, 0.1, 0.2, 0.4 g/L (one jar each per batch; the untreated jar from round 1 is the control) |

Per jar, in this order, 2 cm below the surface:
1. **Batch 2 only:** ICP aluminum, 50 mL, first draw at 5 h, through a 0.45 um syringe filter into a trace-metal HDPE bottle. Add a seawater blank and a filter blank (DI through the same filter). Acidification by the partner or teacher only.
2. 5 h count: 5 mL into a Lugol vial.
3. 5 h chlorophyll: 250 mL by 60 mL syringe in five draws.
4. 24 h count: 5 mL.

The t0 count and t0 chlorophyll come from the batch bottle. Read DO and pH in the jar.

### 5.4 Tank runs (Tue Dec 8, Thu Dec 10, Tue Dec 15)
Three full device runs at 1e4 cells/mL and 0.2 g/L, section 6. **Controller gate Fri Dec 4:** pump and paddle fire from a test row with the student mixing; if not, trigger manually from the printed row on video.

---

## 6. Tank run sequence (T = minutes from dosing; T0 = 14:30, or 10:45 in a booked research block)

**T-24 h:** paste 4 g stock in 40 mL (route per Oct 30 decision).

**T-1 h, set the conditions:**
1. Fill 20 L filtered seawater; add culture to 1e4 cells/mL (for a 5e5 cells/mL culture, 400 mL into 19.6 L).
2. Record **before**: t0 count, 250 mL chlorophyll filter, DO, pH, salinity, temperature.
3. Tape the floor-sample tube in one corner, tip 2 cm above the floor.
4. Controller armed with the test ledger row.

**T0-T1, dose:** controller fires the pump (40 mL in 40 s) and paddle relay; **start the drill mix at the same moment**, 60 s at ~300 rpm, stock entering the vortex.

**T1-T11, slow mix:** paddle at 48-50 rpm (G ~60). Photograph 1 mL on a ruler slide at T11 (floc size).

**T11-T21, settle:** paddle off, no disturbance.
- **T20:** 10 mL count (syringe on a 5 cm tube at an end-wall mark, 2 cm below surface, 10 s); 10 mL floor sample (750 nm); DO spot read with probe swirled.

**T21-T29, two floor passes** at 2 cm/s, all pole faces down:
- Pass 1: outer tube against long wall A, full length of the tank.
- Lift at < 1 cm/s, carry to the release tray, caps off, pull each stack up by its rod, pad drops, rinse tubes with 100 mL from the wash bottle into the tray (fraction i jar), reinsert stacks, caps on (~3.6 min per cycle).
- Pass 2: outer tube against long wall B; release the same way.

**T29-T33, one column pass:** stacks vertical, 2 cm/s through mid-depth; release.

**T33:** 10 mL count at the T20 spot; floor sample.
**T93:** floor sample; DO spot read.
**5 h (19:30 +/- 30 min):** count; 250 mL chlorophyll; siphon 5 L of supernatant for fraction (iii) (inlet 3 cm below the surface at an end wall, < 0.5 L/min, ~12 min, into a 5 L carboy standing on the spare N52 block).
**24 h (14:30 +/- 2 h next day):** count.
**After the 5 h draws:** photograph the floor on a 5 cm grid; siphon the tank to 1 cm at < 2 L/min; rinse the floor with 500 mL seawater and a squeegee into a tared beaker; settle on the block (fraction ii, including the corner patch shadowed by the sample tube).

---

## 7. Sample workup

| Sample | Procedure |
|---|---|
| **Pad** (release tray) | Settle in a tared beaker, decant the water over the magnet block; weigh wet (W); take a wet subsample by mass fraction for chlorophyll; dry the rest at 65 C and weigh (D); solids = (D - S x W) / (1 - S), with S the seawater salt mass fraction; grind; pull-test three 150 mg aliquots. |
| **Fraction i** (tube rinses) | Settle, decant over the block, dry, pull-test. |
| **Fraction ii** (floor rinse) | Settle on the block, decant, dry, pull-test. |
| **Fraction iii** (5 L supernatant) | Settle 24 h on the block; decant to 200 mL over the block; rinse the carboy floor with 50 mL DI; dry in a tared vial; pull-test. Detection floor 8 mg = 1.0% of the 0.8 g magnetite dosed; quantitative above 20 mg = 2.5%. Print both beside the number. |
| **Cell counts** | Lugol-fixed; 1 mL Sedgewick-Rafter; count >= 400 cells where density allows, otherwise up to 200 cells or 500 grids, with the Poisson interval; record mean chain length. Five samples counted by both counters. |
| **Chlorophyll** | 250 mL onto 47 mm GF/F; extract in 5 mL 90% acetone; read 664 and 750 nm; 87.67 L/g/cm. Reportable at 1e4 cells/mL only where removal <= ~70%; counts are the primary measure. |
| **Floor samples** | 10 mL, read at 750 nm as relative turbidity. |
| **ICP aluminum** | Delivered to the partner lab; report with its reporting limit and the 24 ug/L marine guideline. About 5 mg/L Al and 29 mg/L Fe are added per dose. |

---

## 8. Calculations and pass criteria

- **Removal (per batch):** RE = 1 - (Ct/C0) / (Ct,control / C0,control), at 5 h.
- **H11a:** mean RE over three batches with a t-interval (t = 4.30). Pass: mean >= 70%, lower bound > 50%, magnetic within 15 points of plain. Mean >= 70% with lower bound 40-50% reads **"consistent, underpowered"** (the pre-registered likely reading). Mean < 50%: rerun at 0.6 g/L and report both.
- **Recovery (per tank run):** magnetite-equivalent in pad / magnetite dosed; also total solids recovered / solids dosed.
- **Mass balance:** dosed magnetite = pad + fraction i + fraction ii + fraction iii + unaccounted.
- **H11b:** pass if mean magnetite-equivalent recovery >= 70% over three runs, each >= 60%, total solids >= 50%; plain blank described (expected <= 10%).
- **Resuspension index:** T33 count / T20 count (> 1 means the sweep stirred cells back up; about +/- 20% from counting).
- **H11c (dose screen):** three batch means per dose with t-intervals; monotonic by ordered means; D90 by log-linear interpolation only when bracketed by two adjacent means, otherwise "> 0.4 g/L" or "< 0.05 g/L" and "not testable".
- **Inter-counter agreement:** mean absolute relative difference and Lin's concordance coefficient on five duplicate counts.
- Compare measured recovery with the simulation's prediction (~95%, upper bound).

---

## 9. Records

One CSV row per sample: `date, batch, vessel, arm, dose_g_L, route, T_min, measure, value, unit, counter, notes` (dates as YYYY-MM-DD). Photograph count sheets the day they are counted. Copy the controller SD log after each run. Dated git commits at: Oct 9 gate, Oct 23 gate, Oct 30 route decision with pilot counts, Nov 6 freeze, each batch's counts, Dec 4 controller gate, Dec 15 last tank run, Jan 8 outcomes against the bands.

---

## 10. Materials and budget

| Item | $ |
|---|---|
| 22 N52 blocks 40 x 20 x 10 mm (20 in stacks, pull test, settling) at $8 | 176 |
| Square acrylic tube, slotted rails, skids, handles, rods, end-blocks, PTFE tape, release tray | 58 |
| Aquarium, 6 x 2 L jars, 2 x 20 L carboys, filter bag, sample bottles | 85 |
| Magnetite pigment 1 lb, EPK kaolin 5 lb, PAC powder 1 kg | 47 |
| ESP32, relays, SD, peristaltic pump, gearmotors (tank ~50 rpm, jar rig ~100 rpm), 12 V supply, Hall sensor | 85 |
| Sedgewick-Rafter chamber | 60 |
| GF/F filters | 40 |
| f/2 medium, LED, culture jug, Lugol's, pH pen, PPE, siphon, small parts | 149 |
| **Buy everything** | **700** |
| **With five borrows** (chamber, jars, medium, light, power supply) | **533** |

Conditional: commercial ICP aluminum if the partner cannot run it, ~$125-150.

---

## 11. Safety

- **PAC powder** is an acidic aluminium coagulant: gloves, goggles, dust mask; aluminium floc as lab solid waste; effluent bleached, diluted and disposed per school drain policy.
- **Route D paste** is pH ~3-4: gloves.
- **Magnets:** 25 kg pull to steel per block; stacks repel at ~12 kgf. They pinch and shatter. Assemble one at a time in the locked frame; keep phones and SD cards away.
- **Electrical:** everything touching water on 12 V behind a GFCI; drill and hot plate on a separate bench.
- **Acid** (sample preservation) handled only by the partner or teacher.
- **Cultures** are non-toxic; bleach before disposal.
- After-hours work only under the signed agreement with the Designated Supervisor present.

---

## 12. Calendar

| Dates | Work |
|---|---|
| Sep 16-25 | Orders, bookings, forms signed |
| Sep 28-Oct 4 | Build; sterile medium; first seawater |
| Oct 5-9 | Blends, pull-test calibration, detachment tests, Hall check; culture arrives; **gate Oct 9** |
| Oct 13-23 | Clay-only blanks S, D, plain; **gate Oct 23** |
| Oct 26-30 | Scale carboy A to 20 L; stock-route pilot Oct 28; **decision Oct 30** |
| Nov 6 | **Design freeze** |
| Nov 12, 19 | Jar batches 1 and 2 (ICP samples from batch 2); counting checkpoint Nov 20 |
| Nov 23-27 | Thanksgiving: no batch, no counting |
| Dec 1 | Jar batch 3; **controller gate Dec 4** |
| Dec 8, 10, 15 | Tank runs 1-3 |
| Dec 16-Jan 8 | Workups, calculations, board figures, outcomes in Phase 11 |
| Jan 11-15 | Demo dry run; buffer. CSEF deadline Feb 15, 2027 |
