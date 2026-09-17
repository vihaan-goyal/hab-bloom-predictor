# Device simulation: magnet field, floc growth, floor-raster capture

Written 2026-09-16, before any bench work. Scripts in `src/sim/`, figures in `figures/sim/`, CSVs in `data/sim/` (gitignored, regenerable). Parameters are the v7-final design in notes/DEVICE_PROTOTYPE.md s3. Base conda env; one added dependency, `magpylib` 5.2.3.

```
python src/sim/rake_field.py                          # ~5 min (3D field grid)
python src/sim/rake_field.py --pitch-mm 30 --cube-only
python src/sim/floc_kinetics.py                       # ~2 s
python src/sim/rake_capture.py                        # ~10 min (12 cases x 3 passes)
```

Purpose: turn the reviewers' hand calculations into models, and log a **predicted** recovery and floc size in SCIENTIFIC_METHOD.md Phase 11 before the October blanks, so January is scored as prediction versus measurement.

## 1. Magnet field (`rake_field.py`, Magpylib)

Six stacks of four N52 40 x 20 x 10 mm blocks (Br 1.45 T), same pole down, 33 mm centres; 3.2 mm acrylic wall; 3 mm skids.

**Cross-checks against the reviews (all agree):**

| Quantity | Magpylib | Reviewers' hand value |
|---|---|---|
| Single block, 3.2 mm from face | 0.321 T | 0.32 T |
| Single block, 5 mm | 0.273 T | 0.27 T |
| Single block, 10 mm | 0.168 T | 0.17 T |
| Adjacent-stack repulsion, 33 mm pitch | 116.5 N (11.9 kgf) | ~116 N (reviewer 6) |
| End stack net outward force | 130.7 N (13.3 kgf) | ~130 N (reviewer 6) |

**New finding.** In the six-stack array the neighbours partly cancel: at the capture surface under a face, mid-stack, |B| is **0.22 T**, not the single-block 0.32 T; between faces 0.17 T. On the floor (3 mm skid) 0.16 T under faces and 0.07 T between, with |d|B|/dz| 17 T/m under faces and 24 T/m between. The two end stacks carry the strongest field. Reviewer 2's force budget assumed ~25 T/m; the array gives 17-24 T/m, which does not change any capture conclusion below.

Figure: `figures/sim/fig_rake_field.png`.

## 2. Floc growth (`floc_kinetics.py`, Smoluchowski population balance)

Hounslow doubling-grid sectional model. Primaries: dry blend at 0.2 g/L as 2 um equivalent spheres (3.0 g/cm3), fractal aggregates (Df 2.2), orthokinetic + perikinetic kernel, 60 s at G 300 then 15 min at G 30. Breakup represented by a size cap at the Kolmogorov microscale (59 um at G 300, 187 um at G 30); without it the fractal kernel gels in finite time. Mass conserved to 100.00% in every case. Collision efficiency alpha swept 0.1-1.0; seed either dispersed primaries or a pre-aggregated stock (~10 um aggregates).

| Seed | alpha | D50 at 16 min | Time to D50 >= 50 um | Clay mass in flocs >= 30 um | D50 settling |
|---|---|---|---|---|---|
| dispersed | 0.10 | 2 um | never | 0% | 0.00 mm/s |
| dispersed | 0.35 | 22 um | never | 48% | 0.07 mm/s |
| dispersed | 1.00 | 140 um | 110 s | 93% | 0.65 mm/s |
| pre-aggregated | 0.10 | 48 um | never | 66% | 0.18 mm/s |
| pre-aggregated | 0.35 | 139 um | 135 s | 96% | 0.65 mm/s |
| pre-aggregated | 1.00 | 142 um | 80 s | 99% | 0.66 mm/s |

**Reading.** Whether the design's 65-70 um flocs form in 15 min depends almost entirely on the collision efficiency, which is what PAC charge neutralisation sets and what seawater-aged stock degrades (Yu 2016). At full charge neutralisation, or with a pre-aggregated stock at moderate efficiency, flocs reach the turbulence cap (~140 um) within about two minutes and settle at ~0.65 mm/s, inside the design's 0.3-1 mm/s. At low efficiency most clay never forms settleable flocs. The plateau near 140 um is set by the cap assumption, not predicted independently. Cell attachment is fast in every case; what limits removal is whether the clay carrying the cells grows big enough to settle. This makes the October stock-preparation pilot the most consequential test in the program.

Figure: `figures/sim/fig_floc_kinetics.png`.

## 3. Settling and floor-raster capture (`rake_capture.py`, Monte-Carlo)

4,000 equal-mass flocs sampled from step 2; 15 min settle from uniform heights in 160 mm; the step 1 field translated over a 500 x 250 mm floor; each floc moves at magnetic force plus buoyant weight over Stokes drag, with floor and walls as hard limits; M(B) = Ms tanh(B / 0.08 T); captured when it touches a tube wall; pass 2 offset 30 mm; captured flocs removed each pass. Seed 42.

**Predicted magnetite-equivalent recovery after three floor passes:**

| Case | Pass 1 | Pass 2 | Pass 3 | Still in water column at T31 | Left on floor |
|---|---|---|---|---|---|
| **Base** (1 cm/s, 3 mm skid, 33 mm, Ms 70, pre-aggregated alpha 0.35) | 86% | 96% | **96%** | 4% | 0% |
| Speed 0.5 or 2 cm/s | 86% | 96% | 96% | 4% | 0% |
| Skid 0 or 6 mm | 86% | 96% | 96% | 4% | 0% |
| Ms 60 or 80 A m2/kg | 86% | 96% | 96% | 4% | 0% |
| Pitch 30 mm (narrower frame) | 80% | 92% | 92% | 4% | 5% |
| Flocs: dispersed, alpha 1.0 | 84% | 94% | 94% | 6% | 0% |
| Flocs: pre-aggregated, alpha 0.1 | 65% | 72% | 72% | 28% | 0% |
| Flocs: dispersed, alpha 0.35 | 48% | 54% | 54% | 46% | 0% |
| Control: no magnetite | 0% | 0% | 0% | 4% | 96% |

**Reading.**

1. **The magnets are not the limit.** Near a tube the magnetic pull on a settled floc is roughly 100 times its weight and moves it centimetres per second. Every floc that reaches the floor inside the frame's sweep is captured, at any tested speed (0.5-2 cm/s), skid height (0-6 mm) or magnetite strength.
2. **Recovery is set by two things:** how much floc settled by T31 (step 2's collision efficiency), and how much of the floor the frame covers (pass 1 ~86%; the 30 mm offset lane brings it to ~96%).
3. **Pass 3 adds nothing** in the model, because it repeats lane A. A third pass on a new offset, or dropping it, would save about 5 min per run.
4. **The no-magnetite control recovers exactly 0%**, the sanity check.
5. **The 8-tube contingency frame cannot be built as specified.** Review 6 proposed eight tubes at 30 mm centres if the blanks fail; 1-1/4 in tubes are 31.75 mm wide, so 30 mm centres overlap and eight tubes need 254 mm on a 250 mm floor. It would also fix the wrong failure: the model says a failed blank points to poor flocculation or to unmodelled losses, not to magnet reach.

**Prediction logged for H11b:** if flocculation is good (pre-aggregated stock, or full charge neutralisation), floor-raster recovery of magnetite-equivalent is **about 94-96%, an upper bound**. If flocculation is poor, **54-72%**, with the shortfall in the water column rather than on the floor. H11b's pass bands (>= 70%, each run >= 60%) are unchanged.

Figure: `figures/sim/fig_rake_capture.png`.


## 4. Optimisation sweep (2026-09-16, `optimize.py`)

`python src/sim/optimize.py` (~5 min). Stage A: 1,728 floc settings (dose x rapid mix x slow-mix G x slow-mix time x settle time x 6 chemistry scenarios); target settled clay >= 90% and cells removed >= 90%. Stage B1: 4-7 stacks x three pass plans; Stage B2: speed 1-8 cm/s x skid 3-10 mm x magnetite fraction 10-37.5%; target >= 95% of settled flocs captured. Figure `figures/sim/fig_opt.png`; CSVs `data/sim/opt_*.csv`.

**Findings.**
- Chemistry dominates. At the v7 dose (0.2 g/L) a pre-aggregated stock with moderate stickiness settles 95-96% of the clay; a dispersed stock at the same stickiness settles 54-63%; no mixing setting rescues a poorly neutralised dispersed stock (best 64% even at 0.4 g/L). The robust setting across 5 of 6 scenarios needs 0.4 g/L, twice the aluminium.
- Faster slow mix wins in the model: G 60 for 10 min plus 10 min settling matches v7's G 30 for 15 min plus 15 min settling (95% vs 96% settled, pre-aggregated alpha 0.35) in 21 min instead of 31. Breakup is represented only by the Kolmogorov size cap (132 um at G 60), so real floc breakup at G 60 is a risk.
- Pass plan matters more than magnet count. Two passes aligned to each long wall capture 100% of settled flocs with any 4-7 stacks; the v7 plan (11/41/11 mm) needs 6 stacks and its third pass adds nothing.
- Magnet margins are large: >= 99% capture at speeds to 8 cm/s with 3-6 mm skids and magnetite down to 10% of the blend; capture only fails with a 10 mm skid at 4-8 cm/s and low magnetite.

**Recommended settings (applied 2026-09-16 as DEVICE_PROTOTYPE.md Amendment A1):**

| Setting | v7-final | Recommended | Why |
|---|---|---|---|
| Stock | pilot decides S or D | pre-aggregated paste, pilot still decides | 54% vs 96% settled at 0.2 g/L |
| Dose | 0.2 g/L | 0.2 g/L; pilot also runs 0.1 and 0.4 | 0.1 works only with good chemistry; 0.4 doubles aluminium |
| Rapid mix | 60 s, G ~300 | 60 s, G ~300 | unchanged |
| Slow mix | G 30, 15 min | G 60, 10 min | same settling, 5 min faster; breakup risk flagged |
| Settle | 15 min | 10 min | same settled fraction at G 60 |
| Stacks | 6 (24 blocks) | 5 (20 blocks) | 4 is the model minimum; 5 keeps the per-pass pad <= 2.5 mm on 160 cm2 of face at 0.2 g/L |
| Pass plan | 3 passes at 11/41/11 mm | 2 passes, tube edge against each long wall | 100% of settled flocs; drops the redundant pass |
| Speed | 1 cm/s | 2 cm/s | magnetic capture unchanged; faster speeds excluded because resuspension is unmodelled |
| Skid | 3 mm | 3 mm | 10 mm starts losing flocs at speed |
| Magnetite in blend | 37.5% | 20% (about 8 : 25.3 : 6.7 magnetite : kaolin : PAC) | 10% still captures >= 99%; 20% keeps margin for flocs that incorporate little magnetite; iron added ~29 mg/L instead of 54 |

**Predicted result at the recommended settings** (pre-aggregated stock, moderate stickiness): about 95% of clay settled x ~100% of settled flocs captured = **~95% magnetite-equivalent recovery, upper bound**; one run about 28 min (21 min flocculate and settle, ~7 min rastering) instead of ~44 min; 4 fewer magnet blocks.

**What the sweep cannot decide:** the chemistry (collision efficiency) is swept, not predicted, so dose and stock route stay with the October pilot; pad capacity, stranding, resuspension and floc stripping remain unmodelled; a lower magnetite fraction raises the chance that some kaolin carries no magnetite, which only the detachment test measures.

## What the models cannot see

These are the reasons the measured recovery should come in below the prediction, and the attribution fractions in DEVICE_PROTOTYPE.md s3 are designed to catch each one:

- **Pad capacity and stranding at release.** Captured flocs are simply removed; the 2 mm per-pass pad limit and material left on the tube when the stack is pulled are not modelled (fraction i).
- **Resuspension.** The frame, skids and wake stir the settled layer; the model has no fluid flow (the T30/T51 resuspension index).
- **Floc strength.** A magnetic pull of ~100x weight may strip kaolin and cells from the magnetite, so total-solids recovery can fall below magnetite-equivalent recovery (the detachment test; total solids beside magnetite on the board).
- **Floor friction and the skids pushing flocs ahead.**
- **Magnetisation curve** of the pigment actually bought (tanh with 0.08 T is assumed).
- **Column passes**, which could recover some of the suspended fraction.
- **Flocculation chemistry**: alpha is a swept parameter, not predicted; the seawater versus DI stock question is only answerable by the pilot.

## Design implications (applied 2026-09-16 as DEVICE_PROTOTYPE.md Amendment A1)

1. The October stock-route pilot and the clay-only blanks measure exactly the variables the model says control recovery. No change needed; their priority rises.
2. Replace the "+2 stacks at 30 mm" contingency with: if a blank fails, run a floc-size photo and a T31 column sample first. If the loss is in the water column, the fix is chemistry; if it is on the floor, add a third lane offset; if it is in the tube rinse, slow the withdrawal.
3. Pass 3 should use a new offset (for example -15 mm) or be dropped.
4. Rake speed could rise toward 2 cm/s without losing magnetic capture, but resuspension is unmodelled; test before changing.
