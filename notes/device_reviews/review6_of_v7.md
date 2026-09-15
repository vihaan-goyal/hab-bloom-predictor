# Reviewer 6 report on design v7 (freeze audit)

Lens: did reviews 4 and 5 land, does v7 still meet every verifier condition, does the section 10 diff apply to notes/SCIENTIFIC_METHOD.md Phase 11 (lines 536-600) as written, and does the new release mechanics hold up. Checks this pass: every "from" string grepped against the file; BOM, counts, 7a hours, cycle budget, calendar (2026-27) and (iii) floor recomputed; a Coulomb surface-charge model of the stack repulsion (Br 1.45 T, 160 x 20 x 10 mm bars); two web lookups (40x20x10 block pull rating; DRV5055 datasheet).

## A. Landing table (review 5 items)

| # | Item | Status |
|---|---|---|
| 1 | Calendar off Mondays, clock times, blanks (iii) at T111/morning | Landed; one residue: blank #2 (Fri) "next morning" is Mon Oct 19 (finding 6) |
| 2 | Culture order, ship date, medium ready, L1/f-2 range | Landed |
| 3 | Gate inverted, survivors only, +2 stacks retry | Landed; +2 stacks do not fit the floor (finding 4c) |
| 4 | Pull test in range: aliquots + pad-height standards | Landed |
| 5 | Release mechanics: polarity, rod, tray, budget | Landed, but the 25 kg / 5 kg figures are wrong physics (finding 4) |
| 6 | Draws and siphons with tool/position/rate/time | Landed; drain/rinse order vs second siphon unstated (finding 6) |
| 7 | Culture water pasteurised; bag filter | Landed |
| 8 | t-interval, bracketed D90, plain n = 1, index +/-20%, Lin's CCC | Landed |
| 9 | Controller-timed, student-mixed | Landed |
| 10 | $8 blocks, re-summed BOM | Landed; two loose blocks missing (finding 5) |
| 11 | Forms Sep 25, order from home, book Sep 22 | Landed |
| 12 | Margins to fraction (ii), long-wall sample spot | Landed |
| 13 | First seawater Oct 3-4 with driver | Landed |
| 14 | Pre-registration as a diff with commit log | Partly: four of nine replacements do not apply verbatim (B) |
| 15 | Three overclaim edits | Landed |
| 16 | R4 errors (gate dating, end-wall spot) | Landed |

Review 4 items B1-B15 and D1-D6 were confirmed by review 5 and remain in v7. Verifier table: every "to reach WORKS" condition is still met (three-route week 1 + culture pilot; detachment < 30%; drift <= 2 mg daily; ICP Al; closed mesocosm; DO/turbidity/index), with one acknowledged shortfall: "clay-only blank >= 70/80 twice" is now n = 1 per route (s8 item 1), and "unattended dose" became "controller-timed, student-mixed" for a reason the verifier would accept (R4 B12).

## B. Diff validity (Phase 11 is hard-wrapped at ~78 columns; "wrap" = matches only across a line break)

| # | From string | Verbatim? | Correction |
|---|---|---|---|
| 1 | "Frozen design: notes/DEVICE_PROTOTYPE.md (v4)" | wrap (l.549-550) | Apply across the break; add the second-loop clause (C2) |
| 2 | "dosed when the forecast ledger alerts" | yes (l.543) | none |
| 3 | "reads 'consistent, underpowered', not failed (verifier risk 3)" | no: file uses double quotes | from: `reads "consistent, underpowered", not failed (verifier risk 3)` (l.567) |
| 4 | "<= 10% of plain PAC-kaolin (magnetic-specificity control)"; "recovers 75-95% of dosed magnetite-equivalent" | wrap (l.572-573; l.570-571) | apply across the breaks |
| 5 | H11c "rises monotonically ... reads 'not testable'" | no: double quotes in file + wrap (l.575-578) | from ends `H11c reads "not testable"`; and the "to" text has no pass criterion (C3) |
| 6 | "Week-1 stock-preparation pilot ... before the Nov 6 freeze" | no: ellipsis is not a string | from = whole item (1), l.583-589, "Week-1\nstock-preparation pilot: the two best sources ... before the Nov 6 freeze."; keep the Yu 2016 rationale in the "to" text (C3) |
| 7 | "Tank runs log DO and turbidity ... a pull test of the tank rinse" | wrap (l.589-592) | apply across the breaks; the tail ", so raster resuspension is a measured quantity." stays and reads correctly |
| 8 | Gates "culture >= 5e5 ... three tank runs by Dec 18" | wrap (l.605-608), but the "to" text re-states "Forms ... week-1 chemistry by Oct 9;" which the untouched lead-in already carries | Blocking: from must start at "Forms 1/1A/1B/3 signed by Oct 5;" (C1) |
| 9 | "board sentences ... with the verifier's two qualifications" | wrap (l.601-602); insertion point unstated | exact text in C1 |

## C. Findings (ranked)

**1. (Blocking) Replacement 8 produces a contradictory gate line.** Applied as written, Phase 11 reads "Forms 1/1A/1B/3 signed by Oct 5; week-1 chemistry by Oct 9; Forms 1B/3 signed by Sep 25; week-1 chemistry by Oct 9; route blanks ...". Edit s10 item 8 to: from `Forms 1/1A/1B/3 signed by Oct 5; week-1 chemistry by Oct 9; culture >= 5e5 cells/mL in 20 L by Oct 26; clay-only blank >= 70% solids and >= 80% magnetite-equivalent by Oct 23 (retry Oct 30), design frozen Nov 6 whatever the number; counting checkpoint Nov 20; controller unattended dose Dec 4; three tank runs by Dec 18` -> `Forms 1/1A/1B/3 signed by Sep 25; week-1 chemistry by Oct 9; route blanks S (Oct 14) and D (Oct 16) and a plain blank (Oct 20), each route passing or failing on its own blank Oct 23, retry Oct 30 on S with two contingency stacks; culture >= 5e5 cells/mL in 20 L by Nov 6; freeze Nov 6 (Nov 13 if the culture arrives after Oct 8); counting checkpoint Nov 20; controller gate Dec 4 (pump and paddle from a test row, student mixing); three tank runs by Dec 15`. Item 9: replace `not "no study").` with `not "no study"), and reviewer 5's three ("ledger-triggered (test row)", "magnetite-equivalent by pull test", "were not tested").`

**2. (Blocking) Replacement 1 leaves "How the design was reached" incoherent** ("three independent reviewers critiqued v1, v2 and v3 ... Frozen design: v7"). Extend item 1's "to" text: `... (v7; a second loop of three reviewers and a freeze audit, notes/device_reviews/review4-6, took v4 to v7; frozen Fri Nov 6, 2026, or Nov 13 if the culture arrives after Oct 8)`. When v7 is written into notes/DEVICE_PROTOTYPE.md, its header comment ("Frozen 2026-09-15 as v4") must change too.

**3. (Blocking for the claim) H11c loses its pass criterion; "bands do not move" is untrue.** Item 5's "to" text ends without a pass. Append: `Pass: ordered means non-decreasing and, when bracketed, D90 in 0.05-0.2 g/L; an unbracketed D90 reads "not testable".` Change s10's preamble "bands do not move" to "the H11a and H11b recovery bands do not move; H11b's plain criterion becomes a description and H11c's D90 test changes method, both before any data". Item 6: keep the rationale clause (`the two best sources ... costs floc size and dose;`) and replace only from `compare DI-aged-then-seawater-dispersed` to `before the Nov 6 freeze.` Items 3 and 5: use double quotes in the from strings. Also in H11a: `(product basis, seawater make-up)` -> `(product basis; stock route S or D per the Oct 30 amendment)` and `n = 3 jars` -> `n = 3 batches`; H11b `in the clay-only blank` -> `in the winning route's blank`.

**4. (Major) Release-mechanics physics.** (a) The "~25 kg of pull" is the vendor pull-to-steel rating of one 40x20x10 block (N42 ~25 kg, Magnetpartner; Unimagnet 20 kg); there is no steel in the frame, so it does not press anything onto the PTFE. The real loads: same-pole-down stacks at 33 mm centres repel at ~116 N (~12 kgf) per adjacent pair; the end stacks carry ~130 N (~13 kgf) net outward against the outer side wall of their tube [my model]; the pad itself pulls only ~0.3 kgf (1.5 g magnetite, Ms 90 A m2/kg, 25 T/m). Inner stacks see near-cancelling side loads, so their rod force is gravity + shim + pad, under 1 kgf; the two end stacks need 0.2-0.4 x 13 = 2.6-5 kgf on bare acrylic. A hand-pulled T-handle is realistic; no lever. Edit s3: `(~5 kg at mu ~0.2 on PTFE under ~25 kg of pull)` -> `(under 1 kgf for the inner stacks; 3-5 kgf for the two end stacks, which the neighbour repulsion (~13 kgf) presses against their outer side wall: PTFE-line that wall too)`. s6: `Magnets: 25 kg pull per stack` -> `Magnets: ~25 kg pull-to-steel per block; adjacent stacks repel at ~12 kgf`. (b) The frame carries ~13 kgf in tension; wood is fine, but nylon bonds poorly to epoxy. Edit: tubes captured in through-slots in the wooden end rails (or end-blocks screwed, not glued). The four blocks in a row also repel each other end-to-end (parallel moments, side by side): each block must be epoxied to a carrier strip, not only the end block; add that sentence. (c) Contingency: 8 stacks x 33 mm = 264 mm > 250 mm floor. Edit s3 and s11: `+2 stacks` -> `a rebuilt 8-tube frame at 30 mm centres (240 mm; repulsion ~17 kgf per pair)`, blocks ordered Oct 23 for delivery by Oct 27.

**5. (Major) BOM misses two loose blocks** (pull-test block; settling block under the 5 L carboy and rinse beakers). 26 x $8: add a line `2 loose N52 blocks (pull test, settling) | 16`; totals become **$796 / $629 / $565 / $513** (at $6, 26 blocks). Update s3, s8 item 12 and s13 item 19.

**6. (Major) Blank timing and drain order.** Blank #2 runs Fri Oct 16; "07:30 next morning" is Saturday, and 7a correctly puts the second siphon on Mon Oct 19: 64 h of settling versus 17 h for blanks #1 and plain, so fraction (iii) is not comparable across routes. And 7a Oct 14 "tube and floor rinses settle" reads as if the tank is drained on the run day, which would leave nothing to siphon at 07:30. Edits: s3 Draws, `blanks at T111 and 07:30 next morning` -> `blanks at T111 and 07:30 the next school morning (hours logged); drain and floor rinse follow the second siphon`; 7a Oct 14 and 20, `tube and floor rinses settle` -> `tube rinse settles; drain and floor rinse next morning after the second siphon`. Preferably move blank #2 to Thu Oct 15 (paste D Wed Oct 14) so all three blanks get 17 h.

**7. (Minor) DRV5055A4 range is +/-169 mT at 5 V, +/-176 mT at 3.3 V** (TI SBAS640C). The face field of a 40x20x10 N52 block is ~270 mT at 5 mm and ~168 mT at 10 mm (block formula, Br 1.45 T), so the 5 mm point saturates and 10 mm is marginal. Edit s3 Instruments: `spot map at 5, 10, 20 mm` -> `spot map at 10, 15, 20, 30 mm (the A4 saturates above ~170 mT)`.

**8. (Minor) Arithmetic that rechecks and two nits.** BOM 780/613/549/501 sums as printed (before finding 5); counts 7+3+18+9+15+5 = 57, 33.3 h; 7a hours 32; run days all Tue-Fri; T111 = 16:21; 5 h = 19:30, 24 h = 14:30; (iii) floor 8/1480 = 0.54%, 20/1480 = 1.35%; raster cycle 280 s ~ 5 min, three in 15 min. Nits: the column cycle also sums to 280 s (~4.7 min, not "~4"), so two cycles use 9.3 of the 10 min T46-T56; the aliquot line says "45 wt%" where the blend is 37.5 wt% (50 after re-blend): write `(56-75 mg magnetite at 37.5-50 wt%)`. Run days: 14:30 + 3 h = 17:30 against "lab 14:30-17:00"; add "setup 14:15-14:30; run days to 17:30 under the same agreement".

Nothing new in the title, s1, s4 or s9 overclaims: "ledger-triggered (test row)", "magnetite-equivalent by pull test", "(one blank; solids floor ~2-3%)" and "were not tested" are all present and the reject list is intact.

## D. Verdict

Not yet freeze: apply C1-C3 (the diff as written would corrupt Phase 11 and drop the H11c pass), C4 (replace the 25 kg / 5 kg figures, line the end-tube outer walls, fasten rather than glue, rebuild rather than add stacks), C5 (26 blocks, $796/$629/$565/$513) and C6 (drain order, "next school morning"), plus the C7-C8 one-liners. None changes a band, a date beyond the optional blank #2 move, or the board text. With those edits applied, freeze as v7-final.

## Sources

- v7.md, review5.md, review4.md, verification.md (scratchpad); notes/SCIENTIFIC_METHOD.md lines 536-608; notes/DEVICE_PROTOTYPE.md header; notes/device_reviews/.
- https://www.ti.com/lit/ds/symlink/drv5055.pdf (SBAS640C, table 5.6: A4 sensitivity 12.5 mV/mT, linear range +/-169 mT at 5 V, +/-176 mT at 3.3 V)
- https://www.magnetpartner.com/products/power-magnet-block-40x20x10-mm (40x20x10 N42, ~25 kg tractive); https://www.unimagnet.com/neodymium-block-magnet-40-20-10-mm-2-holes-for-m4-screw-pull-force-20-kg_z739/ (20 kg)
- Computations this session (scratchpad/magcheck.py): Coulomb sheet-charge model, Br 1.45 T, 160x20x10 mm bars at 33 and 30 mm centres (116 N, 166 N; end stack 130 N); block face field 0.32 T at 3.2 mm, 0.27 T at 5 mm, 0.17 T at 10 mm; BOM, counts, hours, cycle seconds, calendar.
