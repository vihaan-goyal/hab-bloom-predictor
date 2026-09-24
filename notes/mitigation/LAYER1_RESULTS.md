# Layer 1 results: the control loop replayed on real history (2026-09-24)

Script: `src/models/control_loop_sim.py`. Outputs: `data/control_loop_sim.csv`,
`data/control_loop_episodes.csv`. The rules were copied unchanged from `00_CONTROL_LOOP.md`,
which was written before this was run.

**What this tests:** the *control logic* only (when the loop would switch on, whether that was
before a real bloom, and how much treatment time it would use). The water in these records was
never treated, so it **cannot** show whether bubbles or seaweed work. That's Layers 2-3.

## Results

| | Narragansett, bubbles (X = 2 d) | Narragansett, seaweed (X = 3 d) | Long Island Sound, boat visits (t = 0.35) | Long Island Sound, boat visits (t = 0.20) |
|---|---|---|---|---|
| Data | 15 sonde stations, daily, 2015-2023 (107 station-years) | same | 42 stations, 954 visits, 2023-2025 (median 17 days apart) | same |
| Bloom starts ("onsets") | 1,016 | 1,016 | 55 | 55 |
| **Loop was ON when the bloom started** | **79%** | **81%** | 27% | 35% |
| Switched on 1-H days ahead | 73% (median 3 days ahead) | 57% (median 3 days ahead) | 22% | 27% |
| **False-alarm episodes** (no bloom followed) | **29%** | **24%** | 91% | 93% |
| Treatment-days per station per year | 92 | 102 | 69 | 83 |
| **Treatment-days per bloom caught early** | **13** | **19** | 542 | 524 |
| Share of ON days that came just before a bloom | **39.7%** | **37.6%** | 6.4% | 4.9% |
| Same number of ON days placed at random (95% range) | 33.7% (33.1-34.2) | 30.9% (30.3-31.6) | 5.5% (4.3-6.7) | 4.4% (3.8-4.9) |
| Episodes that hit the time cap (`MAX_ON`) | 85% | 79% | 88% | 90% |

## What it means
1. **With continuous sensors, the loop works as a trigger.**
   - In Narragansett it was already running when about 80% of blooms started, switching on a median 3 days early.
   - About 3 in 4 treatment episodes were followed by a real bloom.
   - The forecast placed treatment days better than chance: 39.7% vs 33.7% just before a bloom for bubbles, and 37.6% vs 30.9% for seaweed, both outside the random range. The advantage is clear but modest (about 1.2×).
2. **With boat visits every ~17 days, it doesn't.**
   - In Long Island Sound the loop caught only 27-35% of bloom starts, and 91-93% of its episodes were false alarms.
   - It would need about 530 treatment-days per bloom caught.
   - Its timing was **no better than random**: 6.4% vs 5.5% (4.3-6.7).
   - A loop that can only re-check every 2-3 weeks can't decide when to switch off. **Any real deployment needs a continuous sensor at the site.** That makes the low-cost fluorometer a required part of the system, not an extra.
3. **Bubbles vs seaweed:** the shorter check interval (bubbles, 2 days) caught more blooms early and needed fewer treatment-days per bloom (13 vs 19). Seaweed had slightly fewer false alarms.
4. **The off rule almost never fired (79-90% hit the time cap).** In an untreated replay that's expected, because nothing lowered the chlorophyll. It also shows that `C_ok` = 5 µg/L is strict for a nutrient-rich bay like Narragansett, where chlorophyll often sits above 5. Whether the off rule works can only be judged when treatment actually lowers chlorophyll (Layer 3). If `C_ok` is changed, it must be written down first and justified.

## Caveats
- **Daily "onsets" include short wiggles.** A daily sonde crossing 10 µg/L counts as an onset (1,016 in 107 station-years, about 9.5 per station per year). Many are brief crossings, not full blooms.
- **The two bays use different models and horizons:** Narragansett gradient boosting at 7 days and t = 0.50; Long Island Sound logistic regression at 21 days on the lab-consistent label.
- **Treatment-days are an upper bound,** because the off rule couldn't fire on untreated water.
