# Talk: Prof. James O'Donnell's group, UConn Marine Sciences / CIRCA

**Length:** ~15 minutes, 15 slides, one beat per slide. Audience is technical and
does ML in other domains, so the methods beats (6, 8, 12) carry the weight.

**Hard constraint from the email thread (2026-09-17):** O'Donnell asked that his
student publish the 2026 observations first. Every number in this talk stops at
2025. Say nothing about 2026 data, not even "we've started looking at it."

**Before the deck is final:** reconcile the two LIS operating points (28-day
threshold-0.60 vs 21-day locked pipeline). See the fact sheet note. Put ONE of
them on the headline slide and keep the other for Q&A.

| Beat | Slide | Time | Running |
|---|---|---|---|
| 1 | Title | 0:30 | 0:30 |
| 2 | The question and the unit | 1:00 | 1:30 |
| 3 | The data | 1:00 | 2:30 |
| 4 | The label and the base rate | 1:00 | 3:30 |
| 5 | The model | 1:00 | 4:30 |
| 6 | Splits and leakage | 1:00 | 5:30 |
| 7 | Headline test performance | 1:00 | 6:30 |
| 8 | Precision-recall and geometry | 1:15 | 7:45 |
| 9 | Decision value | 1:30 | 9:15 |
| 10 | Benchmarks | 1:00 | 10:15 |
| 11 | Zero-shot transfer to IEC | 1:15 | 11:30 |
| 12 | Pre-registered negatives and limits | 1:15 | 12:45 |
| 13 | The device | 1:00 | 13:45 |
| 14 | Simulation predictions | 0:45 | 14:30 |
| 15 | The ask | 0:30 | 15:00 |

---

## 1. Title and one line (0:30)

Thank you for the time. My name is Vihaan Goyal, I'm a junior at Westhill High
School in Stamford, and for about fifteen months I've been trying to answer one
question: can you forecast a chlorophyll exceedance in Long Island Sound three
weeks ahead using only the water-quality data the state already collects? The
short version of the answer is that you can rank the risk, you cannot make the
alerts mostly-right, and I think I can show you exactly why not. Everything I
show today stops at the end of 2025.

## 2. The question, and why the unit is station-visits per confirmed bloom (1:00)

I want to start with the unit, because I think the unit is where most machine
learning on environmental data goes wrong, including mine for the first year.
The natural instinct is to report AUC, or accuracy, or precision, and those are
real numbers, but nobody at a monitoring agency budgets in AUC. They budget in
boat days. A monitoring program has some fixed number of station-visits it can
afford in a month, and the thing it wants at the end of the season is confirmed
observations of the events it cares about. So the honest question is not "how
good is the model," it is: for a fixed budget of station-visits per month, does
using the model to choose where to go get you more confirmed blooms per visit
than the calendar rotation you already run? That is a number a manager can act
on, it is invariant to how you define the event, and it forces you to compare
against the thing the program actually does today rather than against a
strawman. I'll come back to it in beat nine, and I'll show you that it changes
the story.

## 3. The data (1:00)

The data is the CT DEEP LISICOS long-term water-quality record: boat cruises to
about fifty stations across the Sound, from 1993 through 2025. The raw record is
depth profiles, a hundred and twenty to two hundred rows per station visit, one
row per depth bin, and the first thing I had to fix in this project was that my
own early pipeline never aggregated those. It treated every depth bin as an
independent sample, which inflated the dataset to over a million rows and leaked
same-visit chlorophyll into both the features and the label. The corrected
dataset is one row per station-date: eleven thousand four hundred and
forty-seven station-days. That aggregation dropped my headline AUC from 0.936 to
0.815, and I mention it because the 0.936 is still sitting in some of my older
figures and I'd rather tell you about it than have you find it. The other thing
to know about this record is the cadence: the median gap between visits at a
station is twenty-one days. That number governs everything downstream.

## 4. The label and the base rate (1:00)

The label is a forward exceedance. For each station-visit, I ask whether any
chlorophyll-a reading at that same station within the next twenty-eight days
exceeds ten micrograms per litre. Ten is CT DEEP's own working threshold, not
mine — I did not tune it, and I want to be clear that it is a biomass proxy, not
a toxin and not a species. A p75 exceedance or a ten-microgram day is a
top-quartile day; it is not automatically a harmful bloom. The base rate on the
2023 to 2025 test years is about seven percent of station-days. One thing I have
to flag up front: the chlorophyll behind that label is the CTD fluorometer, not
DEEP's lab chlorophyll. Before 2014 the fluorometer read about two to three times
the lab value on the same samples; from 2016 on it matches. So my older training
years have inflated exceedances. The numbers in this talk use the original label,
and I've written down exactly how I'll rebuild it before re-running anything.
I'll come back to how I found this, because it's the most useful thing I learned
this month.

## 5. The model, and why logistic regression (1:00)

The deployed model is a regularized logistic regression: L2, C equals 0.05,
balanced class weights, thirty-five features. The features are chlorophyll
history — lags and three-, six-, nine-, fourteen- and twenty-one-visit rolling
means — temperature, salinity, dissolved oxygen, two nutrient lags, a
three-nearest-neighbour station chlorophyll mean, month and station climatology,
two tidal anomaly terms, salinity lags two through four, percent saturation, and
a three-day maximum wind gust. I did not choose logistic regression because it
was easy. I chose it because everything else lost. XGBoost, random forest, an
LSTM, and later a one-dimensional CNN on fifteen-minute sonde data and a tabular
MLP all landed at or below it on held-out years, and I'll give you the numbers
in beat twelve. When four model families with very different inductive biases
converge on the same AUC, that is information about the problem, not about the
models.

## 6. How the years were split, and what I did about leakage (1:00)

The split is strictly temporal, never random: train on 1993 through 2019,
validate on 2020 through 2022, test on 2023 through 2025, and the test years
were scored once. Every threshold, including the per-station ones, was chosen on
the validation years only. The scaler and the median imputation values are fit
on the training rows alone and then applied to validation and test. On leakage
specifically, because this is the question I'd ask: the rolling chlorophyll
means and the salinity lags are strictly backward-looking within a station — a
pandas rolling mean over prior visits, and shifts of prior observations — and
the label window is strictly forward, dates strictly greater than the visit date.
So no future measurement enters a feature, and no feature enters its own label.
The one thing I want to flag honestly is that features are computed over the
whole time series before the split, which is safe only because every one of them
is causal; if any had been centred or standardised globally it would not be, and
that is the mistake I would look for first in somebody else's pipeline.

## 7. Headline test performance (1:00)

On the 2023 to 2025 test years: AUC 0.815. At the operating threshold of 0.60,
precision 0.500, recall 0.486, F1 0.493 — thirty-six true positives,
thirty-six false alarms, thirty-eight misses out of seventy-four test blooms in
just over a thousand station-days. If I tune a threshold per station on the
validation years, the best five stations run from F1 0.50 to F1 0.73. One
station, C1, has perfect precision, four for four, and I put that on the slide
only so I can tell you not to believe it: seven test positives is not a sample,
it's an anecdote. The number I'd defend is the global one.

## 8. Precision-recall and the geometry of the problem (1:15)

Here is the part I actually find interesting. Precision around one half looks
mediocre until you put the base rate next to it: the event happens on about
seven percent of station-days, so one alert in two being right is a large
multiple of what you get by guessing. But I could not push it further, and I
spent a year trying. What finally explained it was projecting the test rows onto
the logistic regression's log-odds axis and looking at the class overlap
directly. Because every model family lands at the same AUC, the decision surface
is effectively a plane, so that one-dimensional projection is the whole problem.
In Long Island Sound the overlap between the bloom and no-bloom densities is
0.44; in Narragansett Bay, where I have continuous sonde data, it's 0.52 — so
the Sound actually separates the classes slightly better. But the bloom share is
3.6 percent in the Sound against 34.7 percent in Narragansett, and precision at
the operating point is 0.11 against 0.64. About three quarters of blooms in both
bays sit inside the central band where the no-bloom days live. Rarity sets
precision. Model class does not.

## 9. Decision value (1:30)

So let me put that back into boat days. I took a fixed budget — four, eight or
twelve station-visits a month — and compared five ways of spending it over the
out-of-sample period: an even calendar rotation, random-uniform, which is the
same as always-alert, station-by-month climatology from training years only,
alert-directed top-V within the month, and a causal variant that spends day by
day above the shipped threshold. A visit counts as confirming a bloom if the
station-day's label is one, and the intervals come from resampling months,
two thousand draws. At eight visits a month in Long Island Sound, calendar
rotation costs 15.4 station-visits per confirmed bloom, with a wide interval,
8.4 to 44. Alert-directed costs 8.3, interval 4.9 to 21.6. So the forecast
roughly halves the cost of a confirmed bloom. In Narragansett the same
comparison is 3.8 against 1.4, a factor of 2.6, and the intervals are tight.
Two caveats I want to state rather than bury. First, in Long Island Sound
station-by-month climatology — which is free, and needs no model at all — gets
you to 9.3 visits per bloom, and its interval overlaps the model's. The model's
marginal value over "just use the season" is small in the bloom-rare Sound and
only clearly positive in Narragansett, where the intervals are disjoint. Second,
the causal variant looks best on cost per bloom precisely because alerts are
sparse and it leaves about half its budget unspent, so it catches fewer blooms
overall. These numbers rest on forty-eight blooms, and that is why the interval
is as wide as it is.

## 10. Benchmarks against operational systems (1:00)

I tabulated eight operational HAB products against primary sources — NOAA's Lake
Erie forecast, the Gulf of Mexico HAB-OFS, C-HARM in California, EPA CyAN, the
Chesapeake systems, SAMS HABreports in Scotland, CSIRO's Australian tools. I
want to frame this the way I think it should be framed: different question,
stricter evaluation, never "better." Every one of those products forecasts a
species or a toxin for one region with a locally trained model, and that is a
harder and more useful target than a chlorophyll exceedance. What I can say is
this: not one of the eight states its event base rate, so none of their published
POD-FAR pairs can be compared against its own climatology; exactly one, the Gulf
HAB-OFS, tests against chance at all, using a Heidke skill score. Also worth
knowing: the Gulf of Mexico Texas assessment could only verify about five
percent of issued transport forecasts and under nine percent of respiratory
forecasts, because the observations did not exist — which is the same verification
problem I have, and it's reassuring that operational practice handles it the
same way, by excluding unverifiable forecasts rather than counting them wrong.
For scale, C-HARM's nowcast AUCs against pier observations run 0.33 to 0.77.

## 11. Zero-shot transfer to a second agency's record (1:15)

The obvious objection to everything so far is that the model has only ever been
scored on DEEP's own cruises, so it might be learning DEEP's dataset rather than
the Sound. So I pre-registered a test before running it. The Interstate
Environmental Commission samples the western Narrows with its own boat, its own
crew and its own lab — different lab methods, Standard Methods 10200H and EPA
445.0 — and posts to the EPA Water Quality Portal. I froze the LIS model, trained
on DEEP rows through 2019, and scored it on 949 IEC onset station-days from 2020
to 2025 with no retraining at all. Lift 1.84, interval 1.59 to 2.11, entirely
above one; AUC 0.73, interval 0.68 to 0.78. Both pre-registered hypotheses hold.
The honest caveat is that station-by-month climatology reaches the same AUC of
0.73 on those rows, so the model's edge is in lift at a fixed operating point,
not in ranking. And then the unplanned part. My label's exceedance share fell
from forty-two to fifty-nine percent of station-days in 2009 to 2013 to three to
eleven percent from 2014 on. IEC's lab at the same four stations fell far less,
and MODIS saw no step at all, ratio 1.08. I assumed DEEP's lab had changed. DEEP
told me it hasn't, in thirty years, so I went back to my own data and found my
label comes from the CTD fluorometer. On matched surface samples it read 1.8 to
3.2 times the lab value in 2009 to 2013 and 0.8 to 1.05 from 2016 on. DEEP's lab
record has no 2014 cliff. It does have a real low period: exceedances around 3 to
7 percent in 2012 to 2017, against 10 to 23 before and after, which matches what
DEEP remembers. So a scale change in the sensor turned a real, temporary dip into
what looked like a permanent cliff. The rebuild of the label is pre-registered,
and the question I'd most like this room's help with is whether
Corrected_Chlorophyll is the right field to rebuild it from.

## 12. Pre-registered negatives and limitations (1:15)

I want to spend real time on what failed, because the negatives are most of the
evidence. Thirteen pre-registered improvement attempts on the LIS model were
rejected — nutrients, wind, satellite chlorophyll, calibration, XGBoost, station
gating, a nine-hundred-config basin search. On neural networks specifically,
since I understand your group works on ML: I pre-registered two tests with GO
criteria written before any run. A one-dimensional CNN on seven-day windows of
fifteen-minute sonde data against gradient boosting on daily features, with a
paired station-year clustered bootstrap so every model sees the same resamples:
GB 0.839, MLP 0.829, CNN 0.822, hybrid 0.827, and paired delta-AUC for CNN minus
GB was minus 0.017, interval minus 0.027 to minus 0.002, with zero of five seeds
above GB. Reliably negative, not null. The architecture control says model class
isn't the lever; the hybrid says the fifteen-minute structure adds nothing on top
of daily aggregates. Second, a pooled multi-site MLP with a learned site
embedding to close a transfer gap: AUC 0.700 against gradient boosting's 0.762,
paired delta-lift minus 0.21, interval minus 0.45 to minus 0.05 — wrong direction
on every bar. Limitations, briefly: sonde fluorescence reads 1.3 to 1.6 times
above lab chlorophyll across 734 paired samples; the buoy work rests on two
buoys, one of which has a fluorometer gain that drifts by a factor of seven; the
decision-value numbers rest on forty-eight blooms; nothing has been tested
prospectively yet; and every finding here is correlational — low dissolved oxygen
marks bloom-prone water, it does not cause blooms.

## 13. The device: what it is and what it is not (1:00)

Last piece, briefly, because it's the part that isn't done. If a forecast is
going to be worth anything operationally, something has to happen when it fires.
Aeration cannot prevent a bloom. The one in-water mitigation with an operational
record is modified-clay flocculation, used in Korea and China, and its standing
objection is that it sinks the floc onto the seabed and leaves it there. So the
question I pre-registered is narrow: can a magnetite-kaolin-PAC clay, dosed when
a test ledger row alerts, remove a Long Island Sound diatom at pre-bloom density
in filtered seawater, and then come back out on a magnet? The headline number is
recovery fraction. Let me be explicit about what this is not, because the failure
mode of a project like this is overclaiming. It is not bloom prevention. It is
not nutrient removal — one six-hundred-cubic-metre treatment would export about
0.1 kilograms of nitrogen while adding roughly 3 kilograms of aluminium and 32 of
iron. It is not a claim of no habitat impact; dissolved aluminium from PAC is
likely above the marine guideline for hours regardless of retrieval, and the
documented clay harm to clams is resuspension, which a magnet raster causes. And
it is not field-ready. It's a bench result for one non-toxic diatom, and no
bench work has started.

## 14. Predictions logged before the bench work (0:45)

What I did do, before touching any hardware, was build three simulations and
log their predictions, so that January is scored as prediction against
measurement rather than as a story told afterwards. A Magpylib field model
reproduces the reviewers' hand calculations — 0.32 tesla at 3.2 millimetres from
a single block, 116 newtons of stack repulsion — and then tells me something the
hand calculation didn't: in the array, neighbouring stacks partly cancel, so the
field at the capture surface is 0.22 tesla, not 0.32. A Smoluchowski population
balance says floc size at fifteen minutes depends almost entirely on collision
efficiency — median diameter 2 to 22 microns if the chemistry is poor, about 140
microns if it's good — which makes the October stock-preparation pilot the most
consequential test in the program. And a Monte-Carlo raster model predicts
magnetite-equivalent recovery of about 94 to 96 percent if flocculation is good
and 54 to 72 percent if it isn't, insensitive to rake speed, skid height and
magnet strength, with the no-magnetite control at exactly zero. Those are upper
bounds: stranding, resuspension and floc stripping are not modelled, which is
precisely why I expect the measurement to come in below them.

## 15. The ask (0:30)

**Primary ask, one sentence:** Would one person in your group be willing to act
as a methods reviewer for the prospective season — roughly thirty minutes a
month from October through March — so that the frozen forecast protocol gets
scored against LISICOS buoy feeds with someone outside the project checking the
evaluation?

**Fallback ask if that's too much:** If a standing commitment isn't possible,
could you point me to whoever handles the DEEP CTD data on ERDDAP, to confirm
whether the fluorometer or its calibration changed around 2014, and why
Corrected_Chlorophyll is empty for 2022 to 2024? (Skip this if DEEP has already
answered by the talk date; then say what they said.)

Thank you. I'm happy to take methods questions.

---

# Questions they will ask

**How were train and test split, and could anything leak through the rolling
chlorophyll means or the lagged salinity?**
Strictly temporal: train 1993-2019, validate 2020-2022, test 2023-2025, scored
once. Thresholds, including per-station ones, are chosen on validation only.
Scaler and median imputation are fit on training rows and applied forward. On
the rolling means: they are backward-looking rolling windows within a station,
and the salinity lags are shifts of prior observations, so no future value enters
a feature. The label window is strictly forward — dates strictly greater than the
visit date — so no feature can enter its own label. The one thing I'll concede is
that features are computed over the full series before the split; that is safe
here only because every transform is causal, and if any had been globally
centred or quantile-normalised it would not be. The earlier version of this
pipeline *did* leak, in a different way: it never aggregated the depth profiles,
so the same visit's chlorophyll appeared in both feature and label rows. That
leak is what produced AUC 0.936, and fixing it gave 0.815.

**Why is precision around 0.5 not the same as guessing?**
Because the base rate is about seven percent. If you alerted at random you'd be
right seven percent of the time; the model is right half the time, which is a
lift of roughly seven over chance on these rows. I always report the base rate
next to the precision for exactly this reason, and I'd note that none of the
eight operational products I tabulated reports theirs, so their POD-FAR pairs
cannot be compared against their own climatology. What I will not claim is that
0.5 is good in an absolute sense. It means one alert in two sends a boat
somewhere nothing happens.

**Why logistic regression rather than gradient boosting or a neural net, and
what did the neural network experiments actually show?**
Because they all lose or tie, and I have the paired tests. On Long Island Sound,
XGBoost validates higher and tests lower — 0.850 validation, 0.774 test against
LR's 0.824 and 0.815 — which is overfitting to eleven thousand rows with
seventy-four test events. On Narragansett, where there's far more data, I ran a
pre-registered two-by-two: input, daily features versus a seven-day window of 672
fifteen-minute steps, crossed with model, GB versus neural, plus a hybrid. Five
seeds each, the five-seed mean-probability ensemble as the primary object, and a
paired station-year clustered bootstrap so every model saw identical resamples.
GB 0.839, MLP 0.829, CNN 0.822, hybrid 0.827; paired delta-AUC for CNN minus GB
was minus 0.017 with interval minus 0.027 to minus 0.002, and zero of five CNN
seeds beat GB. The MLP-versus-GB comparison is the architecture control and it
says model class isn't the lever; the hybrid sitting on the MLP says the
fifteen-minute structure adds nothing on top of daily aggregates. The second
experiment, a pooled multi-site MLP with a four-dimensional site embedding meant
to close a reverse-transfer gap, failed in the wrong direction: 0.700 against
0.762 for pooled GB, paired delta-lift minus 0.21 with interval minus 0.45 to
minus 0.05. Interestingly the networks fit the *foreign* holdout as well as GB,
AUC 0.84 to 0.85, and transferred worse — so the gap isn't site identity that an
embedding can absorb, it's that the foreign "blooms" are 75th-percentile wiggles
and a more flexible model learns the wiggles. I treat neural network work as
closed: any new attempt has to overcome a reliably negative 0.02, not a null.

**What is the label and who defines the exceedance threshold?**
Any chlorophyll-a reading above ten micrograms per litre at the same station
within the forward window. Ten is CT DEEP's working threshold, not something I
tuned. It is a biomass proxy — no species, no cell counts, no toxin — and I'd
rather say that plainly than let it be read as a harmful-bloom forecast. For
sites without a natural threshold I use that site's own 75th percentile instead,
which is explicitly a top-quartile day, not a bloom. One detail worth stating:
station-days where no observation falls inside the forward window are labelled
zero in this pipeline rather than excluded, which is conservative for precision.
The 21-day locked pipeline excludes them instead, and reports a verifiable-window
false-alarm rate alongside the all-window one; that's the same convention NOAA
uses in the Gulf HAB-OFS skill assessments.

**Your label comes from a sensor. How do you know it's right, and what happens to
your numbers when you fix it?**
It wasn't right, and I found that out this month. The model's chlorophyll column is
the CTD fluorometer. Matched to DEEP's lab chlorophyll on the same station and day,
it read 1.8 to 3.2 times high in 2009 to 2013, 2 to 5 times high in the late
nineties, and about 1 from 2016 on. The test years sit near 1 (0.86 to 1.31), so
the test labels are close to lab scale; the training labels are not. Before
re-running anything I wrote down the fix: rebuild the label and every chlorophyll
feature from DEEP's Corrected_Chlorophyll, which tracks the lab at 0.82 to 1.35
in every year it exists, with two sensitivity versions, one calibrated directly
to the lab and one labelled from lab samples only. The corrected version becomes
the headline whichever way the numbers move, and I wrote predictions down first:
the training base rate should fall by at least 40 percent, and AUC should stay
within 0.05. Every LIS number in this talk will be re-reported after that run.
The script is `src/models/experiments/sensor_vs_lab_chl.py`, and the plan is
`notes/LABEL_REBUILD_PREREG.md`.

**How does this compare to NOAA's operational products?**
Different question, stricter evaluation — I won't say better. NOAA's Lake Erie
bulletins and the Gulf HAB-OFS both track a bloom that satellite imagery or cell
counts have already found, three to four days ahead; C-HARM produces a
probability field for one species in one region; CyAN is a nowcast. Tracking is a
much easier target than initiation, which is why their false-alarm rates are
lower, and they forecast the harmful organism or the toxin, which is the more
useful target. Where I think I'm ahead is on evaluation discipline: base rate
stated on every site, always-alert and persistence as reference forecasts,
station-year clustered bootstrap intervals, and pre-registered negatives. Of
those eight products, none states a base rate and one compares against chance.
Where I'm behind: no agency runs this, no bulletin is issued, no agency has
validated any of my numbers, and I can't map a bloom's spatial extent because I
need an instrument in the water.

**What does the zero-shot transfer really demonstrate?**
That the precursor signature is a property of the western Sound rather than of
DEEP's dataset. Same instrument class — bottle chlorophyll from boat visits, so
no sonde rescaling is involved — but a different agency, different crew,
different lab methods, and winter coverage DEEP never had. Lift 1.84, interval
1.59 to 2.11, entirely above one, pre-registered band 1.2 to 1.8, so it came in
at the top of the band. What it does *not* demonstrate is that the model is the
best available tool on those rows: station-month climatology reaches the same
AUC, 0.73, and the model's margin is in lift at a fixed operating point, 1.84
against 1.50 with intervals that touch. It also isn't prospective — IEC posts
with a lag of months. And there's a sobering detail in the cross-lab check: at
paired stations within three days, the two labs agree on the ten-microgram label
about two times in three, with Spearman 0.38. The label is noisy at the visit
level, and the skill survives that noise, which is either reassuring or a warning
depending on your temperament.

**What would falsify the device hypothesis?**
Each band was written before any run. H11a fails if mean removal is below 70
percent, or if the magnetic blend is more than fifteen points from plain
PAC-kaolin at the same dose — if magnetic clay doesn't remove cells as well as
plain clay, the whole idea is pointless. Below 50 percent I rerun at 0.6 grams
per litre and report both. H11b fails if mean magnetite-equivalent recovery over
three tank runs is below 70 percent, or any single run below 60, or total solids
below 50 — and critically, if the plain-clay control recovers more than about ten
percent, then the magnet isn't doing the work and the result is an artefact. The
no-magnetite simulation control recovers exactly zero, which is the sanity check
that the model isn't cheating. H11c fails if removal doesn't rise monotonically
across the dose screen. There's also a gate before any of this: if the clay-only
blanks in October don't hit 70 percent solids and 80 percent
magnetite-equivalent, the design has failed on its own terms and the board shows
the measured recovery however low it is. And I should say the pre-registered
likely reading of H11a with three batches is "consistent but underpowered" — a
t-interval on three replicates has a multiplier of 4.30.

**What's the sample size, and are the intervals honest?**
The uncomfortable numbers, in order. Seventy-four bloom events in the LIS test
years across just over a thousand station-days; forty-eight events underlying the
decision-value work, which is why that interval runs 4.9 to 21.6. Seven test
positives at station C1, which is why I tell people not to believe the
precision-1.000 cell. Twelve events in the basin-level test, where the advantage
over always-alert has an interval that touches zero and I report it that way. For
the device, n equals three batches and three tank runs, with one plain-clay blank
at n equals one, reported as a description rather than a test. On the method: all
intervals are station-year clustered bootstrap, two thousand draws, seed 42, so
that repeat visits to the same station in the same year aren't treated as
independent; the neural network comparisons use *paired* resamples so every model
is scored on identical draws; and the decision-value intervals resample months
rather than rows. I've tried to report the interval rather than the point
estimate wherever the point estimate would flatter me.

**(If asked) Your README says precision 0.125 and lift 2.7. Which is it?**
Two operating points on the same model spec. The headline here is the 28-day
label at threshold 0.60, where precision is 0.500 on a 7.2 percent base rate. The
README reports a 21-day label at threshold 0.35, chosen by a pre-registered
high-recall rule, which excludes right-censored windows and gives POD 0.875 at
precision 0.125 on a 4.6 percent base rate. Different horizon, different
threshold, different row set — the 21-day version is the one the decision-value
and benchmark work uses. I should give you both rather than pick the flattering
one.

---

# Do not say

Drawn from `notes/DEVICE_PROTOTYPE.md` section 9 reject list, plus the email
constraint.

- **Nothing about 2026 observations.** Not results, not trends, not "we've
  started looking." O'Donnell asked that his student publish first. All numbers
  stop at 2025.
- **Not** "prevents blooms" or "pre-empts blooms." Pre-emption is only coherent
  in an enclosed volume.
- **Not** "removes nutrients" / "removes nitrogen" / any nutrient-credit number.
  One 600 m³ treatment exports ~0.1 kg N while adding ~3 kg Al and ~32 kg Fe.
- **Not** "removes aluminium" — it *adds* about 5 mg/L.
- **Not** "no habitat impact." Dissolved Al is likely above the 24 µg/L marine
  guideline for hours regardless of retrieval, and the documented clay harm to
  clams is resuspension, which the raster causes.
- **Not** "field-ready" or "scalable to Long Island Sound." Both field versions
  are concepts, explicitly not performed, and the verifier rates the field
  concept UNSUPPORTED.
- **Not** "toxin-free." Not tested.
- **No efficiency number without n and an interval.** Never "90% efficient" —
  always "X% [95% t-interval a–b, n = 3 batches]."
- **Not** "predicts blooms" — it is a p75/10 µg·L⁻¹ *exceedance* forecast.
- **Not** "forecast-triggered" without "(test row)" — the bench trigger is a test
  ledger row, and the device is ledger-triggered, controller-timed,
  student-mixed.
- **Not** "no study has done this" — say "no HAB clay study has measured the
  recovered fraction in seawater."
- **Not** "better than NOAA / C-HARM." Say "different question, stricter
  evaluation."
- **Not** the old numbers: AUC 0.936, 1.36 M rows, 7-day horizon, r = 0.707.
  All from the pre-aggregation pipeline.
- **Not** "the TMDL caused the 2014 drop." Withdrawn 2026-09-05; the satellite
  and IEC records both contradict it.
- **Not** "the 2014 cliff is in DEEP's lab record." Withdrawn 2026-09-23: DEEP
  says its lab and methods haven't changed, and the lab record has no 2014 step.
  The step is in the CTD fluorometer's ratio to the lab.
- **Not** "Long Island Sound chlorophyll crashed in 2014." The lab shows a
  temporary low period, 2012 to 2017, then a recovery.
- **Not** any rebuilt-label number until `notes/LABEL_REBUILD_PREREG.md` has run.
