# Reviewer 5 report on design v6 (second review of the second loop)

Lens: can one student run v6 on a school calendar, can a second student reproduce a tank run from s3 alone, and can the analysis deliver every board number with an interval. Web checks: 11 calls (NCMA ordering FAQ and CCMP1332 page; ISEF PHBA exemption; Yom Kippur 2026; N52 40x20x10 pricing, two hosts 403; acrylic square tube; magnetite pigment in 1 lb lots). Calendar, CI and pull-test arithmetic recomputed.

## A. Landing check (R4 items)

- B1 landed: within-tank T30/T51 index, true 5 h tank count.
- B2 landed in substance (blanks S, D, plain), but the gate sentence is now self-contradictory (finding 3).
- B3 landed: dry blends, T-24 h paste; it creates the Sunday problem (finding 1).
- B4 landed: carboys A/B, pilot from B.
- B5 landed: SEN0189 dropped, four 750 nm syringe samples; the spot is still in the lane path (finding 12).
- B6, B7, B8, B9 landed: 5 L with floors printed; DO spot reads as protocol control; ICP first draw, filter blank, reporting limit; 40 m3/h, 63% cap, 3.6 kW.
- B10-B15 landed: blocked rig rounds; 5 g un-PAC'd mix; stock into the vortex everywhere; 4 g detachment; run 3 by Dec 14; third dry mix.
- D1-D6 landed: DO logging, kits, ImageJ, regrowth cut; route P demoted; Version B five lines; s13 carries the six missing issues.

## B. Findings

### Blocking

**1. The calendar does not fit a school day.** (a) "T-24 h paste" plus Monday runs (Oct 12, 19, Nov 9, 16, 30, Dec 7) means pasting PAC at school on six Sundays. (b) Every 5 h read (blank supernatant draw, jar count and Chl, tank count) dosed after school at ~14:30 lands at ~19:30, and the 24 h read falls in last period. (c) Mon Oct 12 is Columbus Day (most CT districts closed): blank #1 sits on a holiday. Fix: run days Tue-Fri; a clock time for T0 in s3/s7 with a signed after-hours agreement, or T0 in a free block; blanks take fraction (iii) at T111 and next morning (no cells, so 5 h has no meaning); 24 h read defined as 24 +/- 2 h.

**2. The culture cannot arrive Tue Oct 6.** NCMA: non-aquaculture strains "take at least two weeks from a ... Wednesday (for domestic orders)", live cultures ship domestic on Wednesdays, overnight. A Sep 21 order ships Wed Oct 7 at the earliest (arrives Thu Oct 8); CCMP1332 is grown to order with ~32 d regrowth noted, so Oct 21+ is the honest planning date. NCMA also says stabilise 12 h then move half the biomass into fresh medium at once, so sterile 2 L medium must exist on arrival day, not Oct 13. Fix: order Sep 16-18, get the ship date in writing, "split" becomes "arrival + 1 d". CCMP1332 is axenic (2026-06-03); recommended L1 at 14 C, known range 11-30 C, so f/2 at 18-20 C is inside range: say so.

**3. The recovery gate is dated before the fact it depends on.** s3 and s11: gate Fri Oct 23 "on the route the pilot later picks" (Oct 30); the Oct 30 retry collides with the route decision. R4 B2 proposed this without checking the dates. Fix: invert it: each route passes or fails on its own blank on Oct 23; a failing route leaves the Oct 28 pilot; if both fail, +2 stacks (8 blocks, not in the BOM), retry Oct 30 on S only.

### Major

**4. Pull test calibrated 5-200 mg; the pad holds ~1,480 mg magnetite.** The headline sample is 7x above the top standard, and a 3 g cake has a different centre-of-mass gap and self-field than 5 mg on the vial floor. Fix: standards at 0.5-2.0 g magnetite in kaolin at pad fill height, or homogenise the dried pad and pull-test three 150 mg aliquots. Say which.

**5. Release mechanics are not reproducible from s3.** Missing: stack polarity (same pole down repels across 13 mm gaps; alternating closes the field between neighbours and shortens reach); how a 240 g stack held to the wall by ~25 kg of pull leaves a capped tube (removable end cap, nylon push rod); handles for a ~1.4 kg frame lifted through 16 cm at < 1 cm/s; and the release vessel ("over jar": a jar mouth is ~10 cm, the frame 198 mm). Fix: a 30 x 25 cm tray, two handles, stated polarity, push-rod release, a per-cycle time budget checked against the 20 min window.

**6. Draws and siphons lack tool, position, rate, time.** 10 mL "2 cm below the surface": 10 mL syringe on a 5 cm tube at a wall mark, 10 s. 5 L supernatant: inlet fixed 3 cm below the surface, < 0.5 L/min (~12 min), which magnet (a spare block, not the pull-test block), and how 5 L becomes a vial (decant to 200 mL over the magnet, DI rinse, dry). Draining before the floor rinse: siphon to 1 cm, then 500 mL and a squeegee. Tube rinse: 100 mL x ~5 cycles into one jar. Floor sample: syringe on a fixed wall tube.

**7. Culture water.** A 5 um cartridge is not medium; wild < 5 um cells grow over the four-week scale-up and appear in Chl and the untreated jar. Chain counts are morphologically specific so H11a survives; Chl and the pilot do not. Fix: pasteurise (2 L at 70-80 C) or 0.2 um filter the culture water; jar diluent can stay 5 um. The cartridge has no housing or pump in the BOM.

**8. Statistics.** (a) Name the CI method: three batch REs give a t-interval, t = 4.30, half-width 25 points at SD 10 (12 at SD 5), so "lower bound > 50" at mean 70 needs SD < 8; pre-register that the likely reading is "consistent, underpowered". (b) The 3-dose logistic (two parameters, three log-doses, asymptote fixed at 100) is identifiable only when no mean sits at the asymptote and the response is not flat; D90 is an extrapolation unless bracketed; a bootstrap of 9 points fails on non-monotone resamples. Honest alternative: three means with t-CIs, monotonicity by ordered means, D90 by log-linear interpolation only when bracketed, otherwise "> 0.2" or "< 0.05 g/L"; delete "fitted D90 CI within 0.025-0.4" from H11c before data. (c) Plain blank n = 1: no interval; print the solids floor (~2-3% of dose from the salinity correction) and treat "<= 10%" as a description. (d) The resuspension index is a ratio of two capped Poisson counts (~+/-20%); say so. (e) Name the inter-counter statistic.

**9. "Unattended dose" contradicts "every dose enters a running rapid mix".** The controller fires the pump; the drill is hand-held; an unattended dose enters a paddle-only tank at G ~30 and forms the EPA "baseball" aggregates (R4 B12). Fix: "controller-timed, student-mixed"; the Dec 4 gate shows pump + paddle relay from a test row with the student starting the drill on DOSE; the board says so.

**10. Magnet price.** $4 per 40x20x10 N52 block is below anything found (UK single GBP 14.60; US singles $6-12). At $8 the line is $192 and buy-everything ~$690. Quote before ordering.

### Minor

**11.** Sep 28 hands-on (stacks, frame, magnetite calibration) precedes Form 1B/3 on Oct 5; ISEF requires 1B before experimentation: sign by Sep 25. Sep 21 is Yom Kippur (many CT districts closed): order from home, book instruments Sep 22.
**12.** The frame covers 228 of 250 mm; the 11 mm long-wall margins are unswept by design and belong to fraction (ii); the end-wall sample spot is in the lane path: use the long-wall margin.
**13.** ~32 L of seawater is needed before Oct 12 but s7 says "from Oct 12"; the first collection is Oct 3-4 and needs a driver.
**14. Pre-registration.** Phase 11 differs from v6 s10 in: "Frozen design: v4" (v6, freeze Nov 6); "week-1 pilot on one 1e4 culture" (clay-only week 1, culture pilot Oct 28); the decision rule (> 15 points, tie keeps S, P only if its photo wins) absent; "log DO and turbidity before, during, after" (spot DO, four 750 nm, T30/T51, 5 L fraction with floor); gates "culture by Oct 26" (Nov 6), "clay-only blank" (two route blanks plus plain), "tank runs by Dec 18" (Dec 14); "fitted D90" (8b); plain "<= 10%" (n = 1); v6 "entered before Oct 19" (already entered 2026-09-15). The amendment-by-design is acceptable, not a loophole, if the decision rule is in Phase 11 now, the pilot counts and route are logged Oct 30 before batch 1, and no band moves after. Dated log, each a git commit: 2026-09-15 pre-registration; Oct 9 gate; Oct 23 blanks; Oct 30 route amendment with six pilot counts; Nov 6 freeze; count sheets photographed the day counted; Dec 4 controller gate.
**15. Overclaims.** Title and s1 "forecast-triggered": the tanks were triggered by a test row; board: "ledger-triggered (test row)". Sentence 2 "of the dosed magnetite": "magnetite-equivalent by pull test". Sentence 3 "those need a permitted mesocosm" implies the mesocosm would show them: "were not tested". Nothing else in s1, s4 or s9 implies prevention, nutrient removal or field-readiness.
**16. R4 errors applied:** gate-on-winner dating (3); end-wall spot (12). R4's arithmetic otherwise rechecks.

## C. Day-by-day, Oct 5-23 (school 7:30-14:15; lab 14:30-17:00 with the DS)

| Day | Planned | h | Needs | Conflict |
|---|---|---|---|---|
| Mon Oct 5 | Forms; three 40 g mixes + plain; paste S, D | 2.5 | DS, hood | Seawater unscheduled (F13); Sep 28 hands-on before forms (F11) |
| Tue Oct 6 | Clay-only S/D/P round, photos; "culture arrives" | 1.5 | rig | NCMA cannot deliver Tue (F2) |
| Wed Oct 7 | Detachment S, D fresh; pull calibration; residues to oven; paste for aged test | 2.5 | oven overnight | Oven unattended |
| Thu Oct 8 | Earliest culture arrival; aged detachment; weigh | 2.5 | sterile medium | Medium not planned until Oct 13 (F2, F7) |
| Fri Oct 9 | Week-1 gate; NCMA transfer | 2 | DS | Fail means re-blend, week 2 slips |
| Sat-Sun Oct 10-11 | Seawater 40 L; **paste S Sunday** | 2 | driver, school | School closed (F1a) |
| Mon Oct 12 | Blank #1: T0 14:30, raster to 15:21, T111 16:21, **5 h draw 19:30** | 6 | DS to 19:45 | Holiday; evening (F1b, c) |
| Tue Oct 13 | Split culture; pad W, dry; rinses settle | 2.5 | | Split already due Oct 9 |
| Wed Oct 14 | D weigh; four pull tests | 1.5 | | none |
| Thu Oct 15 | ESP32 endpoint; Hall map | 2 | | none |
| Fri Oct 16 | Buffer; weekend seawater 40 L | 1 | driver | none |
| Sun Oct 18 | **Paste D** | 0.5 | school | Closed (F1a) |
| Mon Oct 19 | Blank #2, same clock | 6 | DS to 19:45 | Evening (F1b) |
| Tue Oct 20 | #2 workup; paste plain | 2.5 | | none |
| Wed Oct 21 | Plain blank T0 14:30, sweep, drain, rinse; #2 pull tests | 3.5 | | Tight, fits |
| Thu Oct 22 | Plain pad weigh | 1.5 | | none |
| Fri Oct 23 | Recovery gate | 1 | | Route unknown until Oct 30 (F3); +2 stacks not in BOM |

Load is 1.5-2.5 h per weekday plus two 6 h Mondays: feasible only with evening access and runs moved off Mondays.

## D. What v6 gets right

The within-tank T30/T51 index is the correct resuspension measure at the cost of one count. Dry blends pasted at T-24 h remove stock age cleanly. Two route blanks plus a plain blank put a run behind V%. Detection floors printed beside fraction (iii) and the ICP number are how limits should appear. Cutting DO logging, kits, ImageJ and regrowth made s3 shorter and truer. BOM, count table (57), clay (~32 of 120 g) and seawater (~220 L) re-sum. s13 is honest and the s9 reject list is the board's best text. Protist handling (Form 3, no SRC pre-review) matches ISEF rules.

## E. Three highest-value changes for v7

1. Move every run off Mondays, write T0 and the 5 h/24 h clock times into s3 with a signed after-hours agreement, and take the blanks' fraction (iii) at T111/next morning.
2. Order CCMP1332 this week with a written ship date (Wed Oct 7 earliest), have sterile medium ready on arrival, and invert the recovery gate so each route passes or fails on Oct 23 and only survivors enter the Oct 28 pilot.
3. Extend pull-test standards to the pad's mass range, replace the fitted D90 with bracketed interpolation in H11c, and specify release mechanics (polarity, push-rod, tray) and every draw and siphon with tool, position, rate and time.

## Sources

- v6.md, review4.md, verification.md (scratchpad); notes/SCIENTIFIC_METHOD.md Phase 11 (lines 536-600).
- https://ncma.bigelow.org/ordering-shipping-FAQ (two weeks from a Wednesday, domestic; ships Wednesdays; overnight; stabilise 12 h then transfer)
- https://ncma.bigelow.org/CCMP1332 (S. marinoi, Milford CT; L1 at 14 C, range 11-30 C; grown to order, ~32 d regrowth; axenic 2026-06-03)
- https://ncma.bigelow.org/Skeletonema-marinoi (species page lists CCMP3694 only)
- https://www.societyforscience.org/isef/international-rules/faq/ ; https://sspcdn.blob.core.windows.net/files/Documents/SEP/ISEF/2026/Forms/3-Risk-Assessment.pdf ; https://www.sciencebuddies.org/science-fair-projects/competitions/biological-agents-regulations (protists exempt from PHBA pre-review; Form 3 required)
- https://www.hebcal.com/holidays/yom-kippur-2026 (sundown Sep 20 to nightfall Sep 21)
- https://www.ebay.co.uk/itm/223550007247 (40x20x10 N52 from GBP 14.60; pack page 403); https://www.magnet4sale.com/ (403)
- https://www.tapplastics.com/product/plastics/plastic_rods_tubes_shapes/clear_acrylic_tubes/141 ; https://www.usplastic.com/catalog/item.aspx?itemid=39820 (1-1/4 in OD x 1/8 wall square acrylic, 6 ft ~$29, stock)
- https://www.walmart.com/ip/Black-Iron-Oxide-Fe3O4-Synthetic-1-Pound/355495810 ; https://digitalfire.com/material/iron+oxide+black (synthetic Fe3O4 ~0.3 um, 1 lb, stock)
- Computations: 2026 calendar (Oct 12 second Monday); 4 g x 15/40 = 1.5 g vs 200 mg; t(2) = 4.30 half-widths 12/25/37 at SD 5/10/15; 24 x 60 g = 1.44 kg; 198 + 30 = 228 of 250 mm; pre-Oct 12 seawater 31.9 L.
