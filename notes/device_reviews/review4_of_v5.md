# Reviewer 4 report on design v5 (first review of the second loop)

Lens: do the v5 changes actually resolve V1-V8 and R3, and what did they break. Every number below was recomputed from v5's own values (script this session: 2026 calendar, BOM, counts, clay, seawater, Version A/B arithmetic). Web checks: 8 calls (SEN0189 DFRobot product page and wiki, EPA 200.8, ICP-OES Al limits, DO-probe flow dependence, S. marinoi growth rate; 40 CFR 136 Table II blocked at two hosts, so the preservation footnote is cited from EPA method practice, not fetched).

## A. Resolution audit

| Finding | v5 text | Status |
|---|---|---|
| V1 seawater-aged stock | s3 stock pilot: routes S/D/P, n = 2, 6 jars, >15-point rule, decide Oct 30 | **Partly.** Pilot has no untreated jar and the "control-normalised against the untreated clay-only week" sentence is meaningless (no cells in week 1); as a route-vs-route comparison it is valid. Pilot consumes ~1.1 L of the 2 L inoculum on the day of scale-up (B4). The clay-only blanks (Oct 12, 19) run on a route chosen *before* the pilot decides (B2). Stock age 3-10 weeks is a new, untested variable (B3). |
| V2 raster resuspension | s3 floor DO/SEN0189 logging; 750 nm samples; resuspension index | **Partly.** Index mixes T51 (51 min) with jar 5 h and requires a "same batch" jar that does not exist in the Dec 7-18 tank weeks (B1). Probes at the tank centre sit inside the raster envelope (B5). DO signal at bench scale is ~0 (B7). |
| V2 miss attribution | s3 four fractions (i)-(iv), mass balance | **Resolved in structure**; detection floor of fraction (iii) not stated (B6). |
| V2 natural magnetite baseline | s5 sled baseline, 63 um sieve | Resolved as concept; s13 item 8 honest. |
| V3 dissolved Al, kit unsupported | s3 ICP-OES on 4 samples, 0.45 um, HNO3, guideline cited | **Resolved**, with two caveats: ICP-OES in a diluted seawater matrix may not resolve 24 ug/L (ask for ICP-MS if available); the ICP draw should precede the 250 mL Chl draw (B8). 5 h single point is meaningful as "residual at end of the removal window", not as a time course; s13 item 6 says so. |
| V3 "retrieved better" unsupported | s1 paragraph, weakness 8, board sentence 3 | Resolved. |
| V4 mass balance / Milford N | s5 table scaled to 160 m3; s13 item 13 | Resolved; arithmetic correct. |
| V5 field sequence | s5 Versions A and B, bed-vacuum dropped | **Partly.** Version A "mix by recirculating 2 m3/h for 15 min" turns over 5% of 9.4 m3, not a mix (B9). Version B "one drum pass in 1 h" gives at most 63% capture if the effluent returns to the cell (B9). Pump energy "~4 kWh" disagrees with V5's 10-15 kW (10-15 kWh at 1 h); both defensible at different heads, basis not stated. |
| V6 permits | s5, s13 item 11 | Resolved. |
| V7 trigger | s4 wasted-dose arithmetic, "p75-exceedance trigger" | Resolved; numbers match V7. |
| V8 pull-test drift | s3 daily calibration, r^2, 2 mg zero | Resolved. |
| V8 risk 3 reading | s10 amendment | Resolved; note H11a is "entered before Oct 19" but the route is decided Oct 30, so the entry is an amendment by design (say so in SCIENTIFIC_METHOD). |
| V8 board sentences | s9 split, "no HAB clay study", reject list | Resolved, except V% (plain clay) has no tank run to produce it (B2 of this review, carried from R3). |
| Self-audit rows | BOM 696/449/533/616; counts 60; clay 30.9 g; seawater 198 L; dates | **All re-sum correctly.** Count table omits the three tank 7 d regrowth counts (s3 protocol lists them): 63, not 60. "Thanksgiving week, no batch; catch-up counting" contradicts "less the Thanksgiving week" in the hours budget; pick one. |
| s13 Open issues | 13 items | Honest; missing items listed in D/E below. |

## B. Findings

### Blocking

**B1. The resuspension index as written cannot be computed and mixes time points.** "Tank count at T51 / mean jar count at 5 h for the same batch and dose": T is minutes (T16-T31 settle), so T51 is 51 min after dosing, not 5 h; the count table's "5 h (T51)" conflates them; and no jar batch runs in the same week as any tank run (batches Nov 9, 16, 30; tanks Dec 7-18), so "same batch" does not exist. Fix: measure resuspension *within the tank*: a 10 mL count 2 cm below the surface at T30 (settled, pre-raster) and at T51 (post-raster) at the same depth, index = T51/T30; add a true 5 h tank count for comparability with jars. No extra vessel, one extra count per run.

**B2. Route decision lands after the recovery gate, and there is no plain-clay tank run.** Clay-only blanks #1 and #2 (Oct 12, 19; gate Oct 23) must run on route S because the pilot decides Oct 30; if D or P wins, every tank run uses a stock whose recovery was never gated, and the "loser for clay-only work" sentence makes this explicit. Separately, board sentence 2 ("under V% of the plain clay") and H11b's "<= 10% of plain PAC-kaolinite" have no run behind them: all five tank fills are blend (2 blanks + 3 runs), plain clay is jars only (~3 g). Fix: blank #1 on route S, blank #2 on route D (each 4 g, 20 L; gate on whichever route wins, one blank each is the honest n); add one plain-clay tank blank (4 g plain, 20 L, total-solids recovery only, no counts) or delete the V clause and the H11b plain criterion. Cost: +20 L seawater, +4 g plain, one afternoon.

### Major

**B3. Stock age is an uncontrolled variable v5 introduced.** Both 40 g half-blends are pasted in week 1 (Oct 5-9) and "held" as 100 g/L stocks through Dec 18: 3 weeks old at the pilot, 10 weeks old at the tank runs. Yu 2016's mechanism is clay-clay aggregation *in the stock*; route S will keep aggregating for ten weeks, and route D sits at pH 3-4 on magnetite for ten weeks with a pull test that covers only the first 24 h. Fix (simpler, and it is the IOCAS practice): keep the blends dry; paste 4-5 g 24 h before each use in 15-20 mL of the chosen water. Every run then sees a 24 h-aged stock, and "T-24 h age or check stock" becomes one instruction.

**B4. The pilot eats the inoculum.** Six jars x 1.8 L x 1e4 cells/mL = 1.1e8 cells = 1.08 L of the 2 L culture at 1e5, on the same Monday the 2 L is scaled to 20 L (Oct 26). The 20 L then starts at ~5e3 cells/mL and needs ~6.8 doublings by Nov 6 at ~1 division/day for S. marinoi (NCMA): marginal. Fix: run the pilot from the second staggered carboy, or defer the scale-up two days after re-growth, and say which.

**B5. Probes inside the raster envelope.** The DO tip and SEN0189 fixed "2 cm above the floor at the tank centre" sit in the path of a 198 mm-wide frame (6 x 33 mm) rastering a 250 x 500 mm floor; the frame must detour, leaving an unswept patch that becomes a "left on floor" miss caused by the instrument. DFRobot states "the top of probe is not waterproof" and the SEN0189 gives "relative turbidity (no NTU value)"; in 16 cm of seawater the top is submerged. Fix: mount both probes at an end wall outside the raster lanes, SEN0189 top above the waterline (it is 16 cm deep; the probe is longer), or drop SEN0189 and keep the four 750 nm syringe samples, which are the quantitative measure anyway.

**B6. Detection floor of fraction (iii) is not stated.** 1 L of a 20 L supernatant carries 5% of any free magnetite; 2 mg balance drift x 20 = 40 mg = 2.7% of the 1.48 g dosed, and the 20 mg low calibration point x 20 = 27% of dose. So "never in floc" is quantitative only above ~3% and calibrated only above ~27%. Fix: settle 5 L (floor 0.5%/5%), add 5 and 10 mg standards, and print the floor beside fraction (iii) so "unaccounted" is honest.

**B7. Floor DO is a null measurement at bench scale.** 0.01 g algal dry mass in 20 L is 0.7 mg O2/L if fully mineralised, over days; over the 1 h raster window the expected DO change is <0.01 mg/L, below any school meter. A galvanic or polarographic school probe held static 2 cm above the floor is also flow-dependent (Fondriest/YSI) and reads low without stirring, which the raster then "cures", giving an artefact in the direction of a real effect. Fix: spot-read DO at T30 and T111 with the probe swirled; log turbidity only; state that DO at bench scale is a control for the mesocosm protocol, not a result.

**B8. ICP details.** 0.45 um filtration, HNO3 to pH < 2, trace-metal HDPE is the standard dissolved-metals prep (EPA 200.7/200.8 s8; 40 CFR 136 Table II: filter on site, 6 months acidified; unacidified samples are acidified on receipt and held 16 h before analysis). Two gaps: the 50 mL ICP draw must be the first draw at 5 h (before the 250 mL Chl draw disturbs the jar); and ICP-OES on a 5-10x diluted seawater matrix has an Al reporting limit of roughly 5-20 ug/L, at or near the 24 ug/L guideline (Thermo comparison; OES DL ~0.9 ug/L in clean water). Ask the partner for ICP-MS if they have it; otherwise state the reporting limit with the number. Include a filter blank (DI through the same syringe filter): nylon and cellulose filters leach Al.

**B9. Field arithmetic that does not hold.** Version A: 2 m3/h x 15 min = 0.5 m3 = 5% of 9.4 m3; that is not mixing. Say a submersible pump sized for one turnover in 15 min (~40 m3/h) or a paddle/air lift. Version B: a 160 m3 cell pumped at 160 m3/h for 1 h captures 1 - e^-1 = 63% at perfect drum efficiency if the effluent returns inside the curtain; only a once-through discharge outside the cell approaches one full pass, and that is the discharge the permit paragraph says needs an individual permit. State which, and cap the claimed capture accordingly. Pump energy: 700 gpm at ~5 m head is ~3.6 kW (v5's ~4 kWh); V5's 10-15 kW assumed the IRL barge genset; give the basis.

### Minor

**B10.** Pilot design: the rig holds 3 jars, so 6 jars are two rounds ~16 min apart; block one replicate of each route per round and say so. **B11.** Route P material (plain kaolin + magnetite 35:15, no PAC) is not in either half-blend; add 5 g of the un-PAC'd dry mix to the week-1 list. **B12.** Dose during the drill, for every route and vessel: a 100 g/L DI stock hitting pH 8 seawater at 0.7 M forms the EPA "baseball" aggregates at the injection point unless it enters a running rapid mix; the tank sequence implies this (pump inside T0-T1) but the jar protocol never says how the 3.6 mL is added. **B13.** Detachment tests: "1 g, before and after ageing, both routes" is 4 g, not the 2 g budgeted; still inside the 40 g. **B14.** "Regrowth at 7 d" for the third tank run lands Dec 25; move run 3 to Dec 14 or drop tank regrowth. **B15.** If the week-1 gate forces 50 wt% magnetite, the two 40 g half-blends are already made; budget a third 40 g dry mix (pigment 500 g and kaolin 5 lb cover it).

## C. What v5 gets right

The changelog is honest and every V1-V8 item has a concrete edit with a date. The four-fraction mass balance is the right structure for the headline and forces the two recovery numbers to agree or explain. The pull-test drift protocol is exactly what V8 asked for. Demoting the LaMotte kit and sending Al to ICP is the single most valuable environmental change. Section 5 now has two physically consistent field versions, the Version A mesocosm is the correct student-reachable path, and the wasted-dose arithmetic and "p75-exceedance trigger" language remove the board's biggest overclaim. All BOM, count, clay, seawater, calendar and 160 m3 arithmetic re-sums (696/449/533/616; 60; 30.9 g; 198 L; Oct 5 Mon, Nov 26 Thu, Dec 18 Fri, Feb 15 2027 Mon; 32 kg, 0.8 kg Al, 8.6 kg Fe, 0.4 t wet). Section 13 is a real open-issues list, not a fig leaf.

## D. Simplicity check

v5 is ~7,700 tokens and a judge will read section 3 only. Cut or demote: (1) SEN0189 and 10 s DO logging (B5, B7): replace with four 750 nm samples and two DO spot reads; saves a probe, ESP32 code, and a false result. (2) LaMotte Al kit ($80) and API Fe kit: already "indicative only"; drop and take the $616 baseline. (3) ImageJ floor-area fraction: the floor rinse gives the number; keep the photo as a photo. (4) 7 d regrowth counts (9 jar + 3 tank = 12 counts, ~7 h): regrowth suppression is a beaker result the design itself says is untestable in a flushed slip; cutting it takes the count budget from 63 to 51 (~30 h) and restores the margin one counter lacks. (5) Route P in the culture pilot: keep it in the week-1 clay-only floc-size trial, and only promote it to the six-jar pilot if its floc photo beats S and D; it cannot be automated (s13 item 5) and is bench-only either way. (6) Collapse the Version B paragraph to five lines; it is agency-led and not on the board.

Open issues missing from s13: stock age (B3); no plain-clay tank run (B2); whether the school DO meter is optical or membrane (B7); ICP-OES reporting limit vs 24 ug/L in a seawater matrix (B8); the pilot-inoculum conflict (B4); H11a pre-registration (Oct 19) preceding the route decision (Oct 30).

## E. Three highest-value changes for v6

1. Keep the blends dry and paste 24 h before each use, run blank #1 on route S and blank #2 on route D before Oct 23, and add one plain-clay tank blank, so the gate covers the recipe actually used and V% exists.
2. Replace the cross-vessel resuspension index with a within-tank T30/T51 count pair plus a 5 h tank count, and move the probes (or drop SEN0189) out of the raster envelope.
3. Cut DO logging, the Al/Fe kits, ImageJ and the 7 d regrowth counts, and print the detection floor of fraction (iii) and the ICP reporting limit next to their numbers.

## Sources

- v5.md, verification.md, review3.md (scratchpad); notes/CLAY_RETRIEVAL_RESEARCH.md s1, s2, s5, s9; notes/CLAY_FLOCCULATION_RESEARCH.md s1, s2, s7.
- https://www.dfrobot.com/product-1394.html ("the top of probe is not waterproof"; "relative turbidity (no NTU value)"; 5-90 C); https://wiki.dfrobot.com/Turbidity_sensor_SKU__SEN0189
- https://www.epa.gov/sites/default/files/2015-08/documents/method_200-8_rev_5-4_1994.pdf (dissolved metals: 0.45 um, HNO3 pH < 2, 6 months; acidify on receipt and hold 16 h; PDF not text-extractable this session, cited from the method's s8 as recalled)
- https://www.thermofisher.com/us/en/home/industrial/environmental/environmental-learning-center/contaminant-analysis-information/metal-analysis/comparison-icp-oes-icp-ms-trace-element-analysis.html ; https://www.spectroscopyonline.com/view/icp-oes-capabilities-developments-limitations-and-any-potential-challengers (ICP-OES TDS tolerance, dilution degrades detection limits; OES Al DL ~0.9 ug/L clean water)
- https://www.fondriest.com/environmental-measurements/measurements/measuring-water-quality/dissolved-oxygen-sensors-and-methods/ ; https://www.fondriest.com/pdf/ysi_do_handbook.pdf (galvanic and polarographic probes are flow-dependent; optical are not)
- https://ncma.bigelow.org/Skeletonema-marinoi (~1 division per day)
- Computations this session: 2026-27 weekdays; BOM sums; 6 x 1.8 L x 1e4 cells; log2(5e5/5e3) = 6.8 doublings; 2 mg and 20 mg x 20 L / 1.48 g; 0.01 g x 1.4 g O2/g / 20 L; 6 x 33 mm; pi x 1 m^2 x 3 m; 2 m3/h x 0.25 h / 9.42 m3; 1 - e^-1; 700 gpm x 5 m x 9.81 / 0.6.
