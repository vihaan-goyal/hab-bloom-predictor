# Tank water matched to the western Long Island Sound (2026-09-28)

Built by `src/lab/lis_water_recipe.py` from CT DEEP's own measurements: surface samples, 2014-2025,
with silicate through 2024. It uses medians over 195-1,357 station visits per season. The outputs
are `data/lab/lis_baseline.csv` and `data/lab/lis_water_recipe.csv`; `data/` is gitignored, so
re-run the script to rebuild them.

**The idea:** the tanks copy real western-Sound water. The bloom trigger is the nutrient
drawdown of a real spring bloom, not an arbitrary dose of fertilizer. In the data:
- winter nitrate and silicate build up;
- the spring diatom bloom uses up about 90% of them by March-April.

That difference is the pulse.

## Western Sound baseline (DEEP medians, 2014-2025; west of Bridgeport; all regions with ranges in `LIS_WATER_STATS.md`)

| | Dec-Feb (winter) | Mar-Apr (after the spring bloom) | Jun-Aug (summer) |
|---|---|---|---|
| Temperature | 3.6 °C | 4.2 °C | 20.4 °C |
| Salinity | 27.5 | 27.1 | 27.0 |
| pH | 8.02 | 8.07 | 7.67 |
| DO | 11.3 mg/L | 11.2 mg/L | 6.1 mg/L |
| Chlorophyll (lab) | 5.2 µg/L | 4.0 µg/L | 3.5 µg/L |
| Nitrate + nitrite (N) | 0.108 mg/L (7.7 µM) | **0.010** mg/L (0.7 µM) | 0.018 mg/L |
| Ammonium (N) | 0.014 mg/L | 0.007 mg/L | 0.021 mg/L |
| Phosphate (P) | 0.065 mg/L (2.1 µM) | 0.034 mg/L (1.1 µM) | 0.043 mg/L |
| Silicate (SiO₂) | 2.26 mg/L (38 µM) | **0.14** mg/L (2.2 µM) | 2.79 mg/L |

## Recipe per 10 L tank

**Water:**
- Use distilled, RO or dechlorinated water plus artificial sea salt, mixed to a refractometer reading of **27.5**. That's roughly 290 g of mix per 10 L; add the salt gradually and adjust by the refractometer, not by weight.
- Artificial sea salt has almost no N, P or Si, so the nutrients below set the levels.

**Stock solutions (make once, keep in the fridge, label them):**

| Stock | Recipe |
|---|---|
| Nitrate | 0.59 g NaNO₃ in 100 mL water |
| Phosphate | 0.138 g NaH₂PO₄·H₂O in 100 mL |
| Silicate | 2.02 g Na₂SiO₃·9H₂O in 100 mL (use a plastic bottle: silicate etches glass) |

**Doses per 10 L tank:**

| | Nitrate stock | Phosphate stock | Silicate stock | Gives |
|---|---|---|---|---|
| **Warm-up** (day 0) | 0.10 mL | 1.08 mL | 0.32 mL | 0.7 µM N, 1.1 µM P, 2.2 µM Si: post-bloom western Sound |
| **Bloom pulse** (day 21, arms A-C and the pilot) | 1.02 mL | 1.01 mL | 4.98 mL | +7.1 µM N, +1.0 µM P, +35 µM Si: winter minus post-bloom |
| Arm D (false alarm) | no pulse | | | |

- **Trace metals and vitamins:** add the f/2 trace-metal and vitamin mixes at the normal f/2 dose to every tank, pulse or not. DEEP doesn't measure these, and diatoms need them. This keeps N, P and Si as the only things that differ between tanks.
- **Temperature:** the real spring bloom happens at 2-5 °C, which the lab can't hold. Run at **12-15 °C** (a cool room; this also suits the kelp) and report it as a limitation.
- **Light:** 12:12 or 16:8, the same in every tank.

## Watch-outs
1. **Starter-culture carry-over can swamp the recipe.** Standard f/2 has ~880 µM nitrate, so a 1:100 inoculum from an f/2 culture adds ~9 µM, more than the whole pulse.
   - Fix: grow the starter culture in **f/20** (one-tenth strength) for its last transfer, or spin it down and rinse the cells in nutrient-free seawater before adding them.
2. **Tank blooms will be small.** A 7 µM nitrate pulse supports a peak of very roughly 5-15 µg/L chlorophyll above the warm-up level. The Layer 2 re-run (2026-09-28) uses this scale; its untreated bloom peaks near 9 µg/L.
   - The pilot bloom run checks that the fluorometer can see a bloom this size.
   - If it's too faint, scale the **whole pulse** up by a fixed factor (for example ×3, keeping the N:P:Si ratios) and report the factor.
   - Re-run the simulation with the real pilot peak (scale `n_pulse` in `src/sim/method_params.csv` by the same factor).
3. **N:P in the pulse is ~7:1,** below the 16:1 algae need, so nitrogen runs out first. That's typical of the Sound. It's also why nitrogen, not phosphorus, is what the Sound's cleanup plan (the LIS TMDL) targets.
4. **Silicate unit is inferred.** DEEP's data portal doesn't state it. The values only make sense as mg/L SiO₂: as Si they would be 80-100 µM, far above typical Sound values.
   - Confirm with DEEP (add it to the Matt Lyman follow-up).
   - If it's actually Si, double the silicate stock volumes.
5. **Check it against a real sample:** a bucket of western-Sound water, measured for salinity, pH and temperature (and chlorophyll on the fluorometer), should fall inside DEEP's interquartile range for the month (in `lis_baseline.csv`).
