# Reviewer 3 report on device design v3 (final review before freeze)

Lens: did the review-1 and review-2 fixes land and agree with each other; is the whole thing buildable by one student with a chemistry teacher as Designated Supervisor between Oct 5 and Jan 15; and what can the board say. Every number below was recomputed from v3's own values (script run this session; block-field formula from R1 with Br 1.45 T).

## A. Consistency audit

| Item | v3 evidence | Status |
|---|---|---|
| R2#1 settle, floor raster, column last; 1 in sleeve | s3 Capture: T16-31 settle, T31-41 raster x3, T41-46 column; ID 26.6 mm | Landed, but see B3 (sagitta, scraping) |
| R2#1 capacity on pole-face area | 6 x 4 x 8 cm2 = 192 cm2, two cycles at 12 g | Landed; arithmetic correct (12 g at 5-10% = 6-12 mm; 100 mL = 5.2 mm) |
| R2#1 clay-only blank gates culture | s3 Gating test, Oct 19 | Landed |
| R2#2 matched vessels, draw table | Three 2 L jars on one rig; table | Landed; table sums to **515**, not 510 (B7) |
| R2#3 half-log series, n = 3, logistic, bootstrap | s3 Dose series; 78 jars | Landed; 6x2x3x2+6 = 78 correct |
| R2#4 NaOH titrated; detachment test; pull vs magnetite; acid digest | s3 Clay prep and Characterisation | Landed; stoichiometry correct (1.54 mol OH-, 61.6 g NaOH, 42.0 g Fe3O4, 45.6 wt%) |
| R2#5 riser pull test; Hall 10-40 mm | s3 Characterisation (1); Hall map | **Partly**: pull-test gap lifts the sample (B1); SS49E still saturates at 10-15 mm (B4) |
| R2#6 PAC powder, solids basis | s3 PAC modification | Landed |
| R2#7 bands dropped; lockout by issue_date; VERIFY criterion; enclosed-cell paragraph | s4 | Landed |
| R2#8 one-slack 600 m3 cell; bed sled; recovered-magnetite metric; Rhodamine with DEEP sign-off | s5 | Landed; but 600 m3 at 160 m3/h = 3.75 h, not one slack window (B11) |
| R2#9 counting budget, two counters, cut order | s3 Counting budget | Landed; 126 x 35 min = 73.5 h vs 84 h; margin gone once Thanksgiving week is removed (B6) |
| R2#10-13 ISEF forms; Chl limit; raster first; borosilicate/HDPE | s6, s3 | Landed; ISEF sequence wording slightly off (B15); synthesis vessel undersized (B2) |
| R1#1 tray fallback; R1#4 instruments; R1#5 NaOH; R1#7 G; R1#8 arms; R1#9e lockout; R1#12 dose basis; R1#14 DS + 1B | s1 Fallbacks; s3; s4; s6 | Landed. G: at the fixed 60 rpm the jar P/V is 0.86x the tank's (G ~33 vs ~35 s-1), fine; "~65 rpm" is unreachable on a 60 rpm motor (B10) |
| Arithmetic: BOM | 27 lines sum to 744; six borrows 259 -> 485 | Correct |
| Arithmetic: counts | 78 + 27 + 8 + 13 = 126 | Sum correct; the 27 and 8 do not match the protocol's own time points (B9) |
| Arithmetic: clay demand | "~75 g (20 + 4 x 12 + 12)" | Sums to 80 g product; ~67 g magnetic kaolinite once PAC is 1/6 of dose (B8) |
| Arithmetic: 600 m3 mass balance | 120 kg product; 0.3 kg algae; 1.5 t wet at 8%; 0.01-0.04 kg N | Correct |
| Arithmetic: NaOH | 62 g stoichiometric | Correct; but 62 g into 154 mL is a 68 kJ exotherm (B2) |

## B. Findings

### Blocking

**1. The pull test as specified cannot be read.** At the stated 10 mm gap the block field is 0.17 T with a gradient of ~16 T/m; 0.1 g of magnetite (Ms ~70 A m2/kg, near saturation) feels ~0.11 N = 12 gf, and the 0.5 g calibration mass ~59 gf. A 5 g vial on a riser lifts off the pan; a 12 g pad would slam into the magnet. This instrument gates Plan B (week 1) and reports the headline magnetite fraction, so it must work first time. Fix: set the gap at 30-40 mm (B 0.02-0.03 T, gradient ~1.5 T/m: 0.2 gf on 0.1 g, ~3 gf on 2 g, all inside a 0.001 g balance's range), glue the vial into a >= 100 g holder so nothing can move, calibrate with 20, 50, 100, 200 mg of magnetite powder, and record the magnet-only zero before and after each reading (drift <= 2 mg). The alternative Evans-style layout (magnet on the pan on the riser, sample clamped above) reads the same force and cannot lift.

**2. The synthesis as written will not pass a chemistry teacher.** (i) A 5 L beaker cannot hold 5 L of slurry plus 154 mL of NaOH under a stirrer, and no school water bath takes a 5 L beaker. (ii) "10 M NaOH" means dissolving 62 g of pellets in 154 mL: 68 kJ, enough to boil the water; school stock tops out at 6 M (Flinn's solution SDS covers 0.3-6.0 M). (iii) 3 h at 60 C with FeCl3 in an open hood is a supervised afternoon the teacher may not have. Fix: two 25 g half-batches in 4 L beakers on hot-plate stirrers with a thermometer (no bath); NaOH as 2 M (770 mL total), prepared by the teacher the day before in an ice bath; titrate to pH 11.0 as v3 says. Better for the MVP (section C): skip the co-precipitation entirely. R2 showed the product is a kaolinite-magnetite mixture bridged by PAC either way, so pigment-grade Fe3O4 (0.2-1 um, Pigment Black 11, already in the BOM as Plan B) blended with EPK kaolin and PAC powder is the same material with an exactly known magnetite mass, no FeCl3, no hot NaOH, and no hood time. Keep the synthesis as a stretch comparison if the DS signs off.

### Major

**3. Round sleeve geometry is worse than v3 states, and the floor raster scrapes its own pad.** A 20 mm flat pole face inside a 26.6 mm bore touches the wall only at its edges; the sagitta is 4.5 mm, so the face centre is 3.4 + 4.5 = 7.9 mm from the outer surface (B ~0.20 T there, 0.32 T at the edges), not 3.4 mm. Settled floc under a sleeve lying on the floor is therefore 8-13 mm from the pole, the outer edge of R2's 8-14 mm holding shell, and the pad that does form sits on the underside where the floor rubs it off in the next lane. Fix: 1-1/4 in square acrylic tube, 1/8 in wall (ID 25.4 mm; flat face 3.2 mm from the block, ~0.32 T), 3 mm skids on the frame, and release into the jar after every raster pass so each pass carries <= 2 mm of pad; keep the tray (R1#1) as the fallback. The frame must lock six stacks 33 mm apart; they attract hard sideways.

**4. The Hall map still saturates.** The block formula gives 0.17 T at 10 mm and 0.10 T at 15 mm; the SS49E is linear only to +/-1000 G (0.1 T), so the 10 and 15 mm points are unreadable and the fit to the face rests on 20-40 mm (0.07-0.017 T). Fix: DRV5055A4 (+/-169 mT at 5 V, ~$2), or state the map as 20-40 mm.

**5. Pad workup loses clay and destroys Chl.** 120-240 mL of pad water carries 3.4-6.7 g of salt; a single 50 mL DI rinse cannot remove it, and DI water deflocculates kaolinite, so the non-magnetic fraction leaves with the decant and "total recovery" is biased low in exactly the way weakness 2 warns about. Drying at 65 C degrades chlorophyll, so "Chl in pad" from a dried subsample is phaeopigment. Fix: weigh the wet pad (W), dry it (D), and report solids = (D - 0.028 W)/0.972 using the batch salinity; take the Chl subsample from the wet pad by mass fraction before drying.

**6. Counting is over budget once the calendar is real.** Nov 2-Dec 18 is seven weeks, one of them Thanksgiving, so two counters at 6 h/week give ~72 h against 73.5 h; the partner-lab counter is not confirmed (DEEP/UConn reply pending); a classmate must be trained on Skeletonema chains; and the two counters share one $60 chamber. Any culture crash or blank failure lands on this path. This is the reason for section C.

### Minor

**7.** Draw table: 5 + 5 + 250 + 50 + 5 + 200 = 515. Either drop the t0 row (it is from the batch bottle) or write 510 as the per-vessel draw. **8.** Clay demand sums to 80 g of product, ~67 g of magnetic kaolinite; against a ~92 g theoretical yield and three washes, say the margin (< 20%) and that the 1 g pilot is separate. **9.** "27 three-arm counts" implies t0 per jar, contradicting the batch-bottle rule (18 + 3 = 21); "8 tank counts" omits the protocol's 24 h count (12). Fix the table; total stays ~126. **10.** Write "60 rpm" for the jar rig. **11.** 600 m3 at 160 m3/h is 3.75 h; say two or three slack windows or a 250 m3 cell, and mark all of s5 "concept, not performed" on the board. **12.** Seawater: 87 jars x 1.8 L + 5 tank fills + culture make-up is ~260 L of 5 um-filtered LIS water, 13 carboy trips, with no stated storage; plan 40-50 L per week and a dark cold shelf. **13.** Counting unit: cells, with mean chain length logged per sample, since flocculation biases chain length. **14.** Fe/Al kits: Al by ECR is Fe-interfered and the API kit is a freshwater kit; call both "indicative" on the board. **15.** ISEF wording: hazardous chemicals and devices need Form 3 signed by the DS before experimentation and no SRC pre-approval (Society for Science rules); CSEF is an ISEF affiliate and takes the forms as uploads at registration, so replace "the SRC reviews the packet at the fair" with "uploaded at CSEF registration; SRC may query". Protists: Form 3 only, as stated.

## C. MVP recommendation

v3 is a good summer-2027 program compressed into ten weeks. Trim to what yields one defensible headline number plus its necessary companion:

**Build.** Blended magnetic PAC-kaolinite (pigment Fe3O4 : EPK : PAC by mass ~40 : 50 : 18, i.e. ~45 wt% magnetite and PAC 5:1 on the mineral solids, pasted in seawater and aged 24 h); square-tube stacks with skids; the jar rig; the ESP32 reading a test ledger row. Characterisation: pull test (fixed per B1) and the seawater detachment test only; acid digest to the partner lab or dropped.

**Run.** (i) Clay-only blank x2 (gate). (ii) Three-arm comparison at 0.2 g/L, 1e4 cells/mL, n = 3, one replicate per weekly batch. (iii) Tank runs x3 at 1e4 and 0.2 g/L: removal, recovery, video. (iv) Dose screen at 1e4 only, magnetic arm, 0.05/0.1/0.2 g/L, n = 3 (9 jars), sharing the three-arm untreated jars, to pick the controller dose. Counts: ~45-50, ~28 h; jars: 18 + tank; clay: ~25 g.

**Headline.** Number 2, recovery fraction (magnetite-equivalent, with total dry product beside it), which no HAB study has measured in seawater, paired with number 1, removal at the same dose. Drop number 3, the D90 ratio, from the January board: 78 jars and 126 counts buy a test with power 0.8 only for a 2x ratio and a real chance of a lower bound (D90 < 0.025 g/L). The forecast link on the panel is the trigger and the chosen dose, with the density-dose claim cited from the literature and the ratio test pre-registered for summer 2027.

**Defer to summer 2027.** Two-density half-log series and D90 ratio; co-precipitated clay vs blend; Heterosigma; 30 d regrowth; full Hall map; 1e5 Chl series; anything in s5.

## D. Board sentences

1. "In 20 L of filtered Long Island Sound seawater, a magnetite-kaolinite-PAC clay dosed at 0.2 g/L when a test forecast row alerted removed X% [95% CI a-b] of *Skeletonema marinoi* cells within 5 h (n = 3 jars, control-normalised), against Y% for plain PAC-kaolinite."
2. "A magnet sweep of the tank floor then recovered Z% [range over n = 3 runs] of the dosed magnetite and W% of the total dry clay; the same sweep recovered under V% of the plain clay. Korean and Chinese practice leaves the floc on the seabed; no published study had measured the recovered fraction in seawater."
3. "This is a bench result for one non-toxic diatom. It does not show that blooms are prevented, that nitrogen or phosphorus are removed from the Sound, or that bottom habitat is unaffected; those need a permitted mesocosm."

Phrasing a judge should reject: "prevents blooms", "removes nutrients/nitrogen", "no habitat impact", "90% efficient" without n and CI, "field-ready", "scalable to LIS", "toxin-free", any nutrient-credit number from s5.

## E. Proposed H11a-c (pre-register before Oct 19)

**H11a (removal).** Magnetic PAC-kaolinite at 0.2 g/L (product basis, seawater make-up) removes *S. marinoi* at 1e4 cells/mL by **70-95%** at 5 h (control-normalised Sedgewick-Rafter counts), and within **+/-15 points** of plain PAC-kaolinite at the same dose. Basis: kaolinite-PAC 100% at 0.1-0.3 g/L on *A. minutum* at 1e4 [CLAY s2]; MCII 91% on *Karenia* at 0.2 g/L, 5 h [RET s5]; seawater make-up needs ~3x dose and ionic strength cuts magnetic-flocculant efficiency [CLAY s2; RET s1]. Pass: mean RE >= 70% with the n = 3 CI lower bound > 50%, and |magnetic - plain| <= 15 points. Fail below 50%: rerun at 0.6 g/L and report both.

**H11b (recovery).** The settle-raster-column sequence recovers **75-95%** of dosed magnetite-equivalent and **>= 70%** of total dry product in the clay-only blank, **60-90% / 50-85%** with culture, and **<= 10%** of plain PAC-kaolinite (magnetic specificity control). Basis: freshwater magnetic-flocculant particle recovery 84-97.5% [RET s1]; composite Ms as low as 6 emu/g and free-magnetite detachment [R2#4]. Pass: mean magnetite-equivalent >= 70% over n = 3 runs, each >= 60%; total >= 50%; plain <= 10%. A blank below 70/80 is a design failure, not a hypothesis failure (F).

**H11c (dose-density).** Full version (summer 2027): D90(1e5)/D90(1e4) in **1.5-4x**; pass if the bootstrap 95% CI lower bound > 1.0 with D90(1e4) resolved inside the series (>= 0.025 g/L); if D90(1e4) is below the series, report a lower bound and record H11c as "not testable", not failed. MVP version (January): RE at 1e4 rises monotonically over 0.05-0.2 g/L and D90 lies in **0.05-0.2 g/L**; pass if the fitted D90 CI sits within 0.025-0.4 g/L. Basis: removal falls with initial density [CLAY s2, Yu 2017]; *A. pacificum* ~75% at 0.2 to ~99% at 1 g/L.

## F. Failure tree

| Gate | Decide by | Pass | Fallback | Board shows if it fails there |
|---|---|---|---|---|
| Forms 1/1A/1B/3 signed; DS accepts chemistry | Oct 5 | Signed | DS refuses synthesis: blend route (C); refuses hot Fe/NaOH only: teacher prepares reagents | Unchanged |
| Week-1 chemistry (PAC pilot, pull, detachment) | Oct 9 | < 30% pull loss, < 30% non-magnetic residue | Blend route becomes the only route | Unchanged |
| Batch yield (if synthesis run) | Oct 16 | >= 60 g product, pull >= 50% of magnetite-limited expectation | Blend route | "Blend used; synthesis result as a side panel" |
| Culture scale-up | Oct 26 (>= 5e5 cells/mL in 20 L) | Density met | Re-order (2 wk) or partner culture; if none by Nov 16, run clay-only work | Recovery number only; removal cited from literature and labelled "not measured here" |
| Clay-only blank | Oct 23; retry Oct 30 | >= 70% total, >= 80% magnetite-eq | Square tube, skids, +2 stacks, then tray; freeze design Nov 6 whatever the number | The measured recovery, however low, as the finding ("magnetic retrieval recovered X% under these conditions") |
| Counting checkpoint | Nov 20 | >= 40% of planned counts done | Apply cut order; MVP already cut | Fewer n, CIs wider, stated |
| Tank runs | Dec 18 | 3 runs complete | Report n = 2 | n on the panel |
| Controller | Dec 4 | Doses from a test ledger row unattended | Manual trigger from the printed row; video shows the row | "Trigger demonstrated manually" |

## G. Verdict

**Needs a v4, short.** The v2 fixes landed and are mutually consistent; what remains is two instrument-and-chemistry errors that would fail on the bench in week 1 (B1, B2), three geometry and workup errors that bias the headline number (B3-B5), and a schedule that has no slack (B6). None changes the concept. v4 should: fix B1-B5 as written; adopt the MVP (C) with the full program listed as "summer 2027"; correct the minor arithmetic (B7-B10); add H11a-c to SCIENTIFIC_METHOD.md as Phase 11 with the bands above before Oct 19; and carry the board sentences (D) verbatim into the board layout. After that the design can be frozen and sent to the scientist.

## Sources

- v3.md, review2.md, review1.md (this scratchpad); notes/CLAY_RETRIEVAL_RESEARCH.md s1, s5, s6, s9; notes/CLAY_FLOCCULATION_RESEARCH.md s2, s7, s8; notes/SCIENTIFIC_METHOD.md Phases 8, 10, Conclusion (pre-registration format, expected bands, "not testable" vs "failed").
- https://www.societyforscience.org/isef/international-rules/hazardous-chemicals-activities-or-devices/ ; https://www.societyforscience.org/isef/checklist-for-src-review/ ; https://www.societyforscience.org/isef/overview-of-forms-and-dates/ (Form 3 signed by the DS before experimentation; no SRC pre-approval for hazardous chemicals/devices)
- https://www.societyforscience.org/isef/international-rules/potentially-hazardous-biological-agents/ (protists: Form 3 only)
- http://ctsciencefair.org/document-library (CSEF is an ISEF affiliate; forms uploaded at registration; 2027 Fall Mailing dated 9/9/26)
- https://prod-edam.honeywell.com/content/dam/honeywell-edam/sps/siot/ja/products/sensors/magnetic-sensors/linear-and-angle-sensor-ics/common/documents/sps-siot-ss39et-ss49e-ss59et-product-sheet-005850-3-en-ciid-50359.pdf (SS49E: 1.4 mV/G, +/-1000 G)
- https://www.ti.com/lit/gpn/DRV5055 (DRV5055A4: 12.5 mV/mT, +/-169 mT at 5 V)
- https://www.flinnsci.com/sds_735-sodium-hydroxide-solution-0.3-m---6.0-m/sds_735 (school NaOH solutions 0.3-6.0 M)
- https://digitalfire.com/material/iron+oxide+black ; https://micronmetals.com/product/iron-oxide-powder-black-magnetite/ (synthetic magnetite pigment 0.2-1 um, Pigment Black 11)
- Computations this session: block field B(z) per R1 (Br 1.45 T, 40x20x10); sagitta r - sqrt(r^2 - 10^2) for r = 13.3 mm; NaOH dissolution 44.5 kJ/mol; magnetic force m x dB/dz with Ms 70 A m2/kg; jar/tank P/V with C_D 1.2 and 0.75 slip; salt correction at 28 g/L.
