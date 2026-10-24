"""Tests for src/lab/bench_analysis.py on synthetic data with known answers.
Run:  python -m pytest tests/test_bench_analysis.py -q"""
import os
import sys

import numpy as np
import pandas as pd
import pytest
from scipy import stats

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "lab"))
import bench_analysis as B  # noqa: E402

REP = (0.9, 1.0, 1.1)          # replicate spread so intervals are not degenerate
SQ = 4                          # hemocytometer large squares counted (0.4 uL)


def count_row(exp, tank, cells_ml, day=np.nan, t_h=np.nan, size="all", foreign=0, grazers=0):
    return dict(experiment=exp, tank_id=tank, day=day, timepoint_h=t_h, size_class=size,
                count_method="hemo_large", cells_counted=cells_ml * SQ * 1e-4, squares_counted=SQ,
                dilution_factor=1.0, foreign_cells=foreign, grazers_seen=grazers)


def get(res, hyp, analysis_set="per-protocol", endpoint=None):
    r = res[(res.hypothesis == hyp) & (res.analysis_set == analysis_set)]
    if endpoint:
        r = r[r.endpoint.str.contains(endpoint, regex=False)]
    assert len(r) >= 1, (hyp, endpoint)
    return r.iloc[0]


# --- arithmetic -----------------------------------------------------------------------------
def test_hemocytometer_arithmetic():
    # 200 cells in 4 large squares (4 x 0.1 uL = 0.4 uL), diluted 1:1 -> 200 / 0.0004 mL x 2
    assert B.cells_per_ml([200], [4], ["hemo_large"], [2.0])[0] == pytest.approx(1.0e6)
    # 150 cells in 10 Sedgewick-Rafter squares (10 uL), undiluted -> 15,000 /mL
    assert B.cells_per_ml([150], [10], ["sr"], [1.0])[0] == pytest.approx(1.5e4)
    # 80 cells in 5 small central squares (5 x 0.004 uL = 0.02 uL) -> 4.0e6 /mL
    assert B.cells_per_ml([80], [5], ["hemo_small"], [np.nan])[0] == pytest.approx(4.0e6)
    # a zero count stays 0 cells/mL, but its log uses half a cell in the counted volume
    assert B.cells_per_ml([0], [4], ["hemo_large"])[0] == 0
    assert np.exp(B.log_floor([0.0], [0], [4], ["hemo_large"])[0]) == pytest.approx(0.5 / 4e-4)
    with pytest.raises(ValueError):
        B.cells_per_ml([10], [1], ["bad_slide"])


def test_welch_matches_scipy_and_permutation_floor():
    x, y = np.array([1.0, 1.4, 2.1]), np.array([3.0, 3.2, 4.4])
    d, lo, hi, _ = B.welch(x, y)
    ci = stats.ttest_ind(x, y, equal_var=False).confidence_interval(0.95)
    assert (lo, hi) == pytest.approx((ci.low, ci.high))
    assert d == pytest.approx(x.mean() - y.mean())
    # 3 v 3, complete separation: 1 of 20 relabellings, the smallest p possible
    assert B.perm_p(x, y, "less") == pytest.approx(0.05)
    assert B.perm_p(y, x, "greater") == pytest.approx(0.05)


def test_decision_rules():
    assert B.decide(0.6, 0.1, 0.9, 0.5) == "PASS"
    assert B.decide(0.6, -0.1, 0.9, 0.5) == "INCONCLUSIVE"    # big estimate, CI includes 0
    assert B.decide(0.05, -0.1, 0.2, 0.5) == "FAIL"           # CI rules out the mark
    assert B.decide(0.3, 0.1, 0.7, 0.5) == "INCONCLUSIVE"     # real but maybe smaller than mark
    assert B.decide_safety(-5, -15) == "PASS"
    assert B.decide_safety(-25, -40) == "FAIL"
    assert B.decide_safety(-10, -30) == "INCONCLUSIVE"


# --- screens --------------------------------------------------------------------------------
def aeration_screen_data(akashiwo_cut=0.5, thal_cut=0.0):
    log, counts, k = [], [], 0
    growth48 = {"nanno": 2.0, "thal": 2.0, "akashiwo": 1.8}
    for arm in ("still", "gentle", "low", "high"):
        for sp in ("nanno", "thal", "akashiwo"):
            for i, f in enumerate(REP):
                k += 1
                t = f"AS{k:02d}"
                cut = {"akashiwo": akashiwo_cut, "thal": thal_cut}.get(sp, 0.0) if arm == "high" else 0.0
                n0 = 2.0e4
                g48 = growth48[sp] * (1 - cut) * (1 + (f - 1) / 5)   # +/- 2% between flasks
                series = {0: n0, 24: n0 * np.sqrt(g48), 48: n0 * g48,
                          72: n0 * g48 * 1.3, 96: n0 * g48 * 1.7}
                for th, v in series.items():
                    counts.append(count_row("aeration_screen", t, v, t_h=th))
                    log.append(dict(experiment="aeration_screen", arm=arm, species=sp, tank_id=t,
                                    replicate=i + 1, volume_L=0.5, timepoint_h=th, ph=8.1,
                                    fl_counts=20 + v / 1e3, fl_blank_counts=0,
                                    airflow_mL_min=B.S1_FLOW.get(arm) if th <= 48 else 0))
    return pd.DataFrame(log), pd.DataFrame(counts)


def test_aeration_screen_clear_effect_passes():
    res = B.run(*aeration_screen_data(akashiwo_cut=0.5))
    s1a = get(res, "S1a")
    assert s1a.estimate == pytest.approx(0.5, abs=0.03)
    assert s1a.decision == "PASS"
    assert get(res, "S1b").decision == "PASS"
    assert get(res, "S1").decision == "PASS"
    assert "akashiwo" in get(res, "S1-choice").endpoint


def test_aeration_screen_no_effect_fails():
    res = B.run(*aeration_screen_data(akashiwo_cut=0.0))
    assert get(res, "S1a").decision == "FAIL"      # tight CI around 0 rules out a 30% cut
    assert get(res, "S1").decision == "FAIL"


def test_aeration_screen_diatom_harmed_fails_joint():
    res = B.run(*aeration_screen_data(akashiwo_cut=0.5, thal_cut=0.4))
    assert get(res, "S1a").decision == "PASS"
    assert get(res, "S1b").decision == "FAIL"
    assert get(res, "S1").decision == "FAIL"


def peroxide_screen_data(pulse_cut=0.8, artemia_ctrl=27, artemia_pulse=26):
    log, counts, k = [], [], 0
    arms = [(a, s) for a in ("ctrl", "h2o2_0.8", "h2o2_1.6", "h2o2_3.2", "h2o2_6.4", "percarb_0.8")
            for s in ("nanno", "thal", "akashiwo")] + [("pulse3_0.8", "nanno"), ("carbonate", "nanno")]
    size_rank = {"nanno": 1.0, "thal": 0.3, "akashiwo": 0.1}
    for arm, sp in arms:
        dose = B._nominal_dose(arm) or 0.0
        for i, f in enumerate(REP):
            k += 1
            t = f"PS{k:02d}"
            if arm == "pulse3_0.8":
                c24, c72 = 0.4, pulse_cut
            else:
                c = min(0.95, size_rank[sp] * dose / 2.0)   # bigger dose, smaller cell -> bigger cut
                c24, c72 = c, c
            n0 = 5.0e4
            for th, cut in ((0, 0.0), (24, c24), (72, c72)):
                g = (1.5 if th else 1.0) * (1 - cut) * (1 + (f - 1) / 5)
                counts.append(count_row("peroxide_screen", t, n0 * g, t_h=th))
            for th in (0, 1, 4, 24, 72):
                h = dose * np.exp(-np.log(2) * th / 6.0) if dose else 0.0
                r = dict(experiment="peroxide_screen", arm=arm, species=sp, tank_id=t, replicate=i + 1,
                         volume_L=0.2, timepoint_h=th, h2o2_mgL=round(h, 3), ph=8.1)
                if th == 24 and arm in ("ctrl", "pulse3_0.8", "h2o2_1.6") and sp == "nanno":
                    alive = {"ctrl": artemia_ctrl, "pulse3_0.8": artemia_pulse}.get(arm, 26)
                    r.update(artemia_start=30, artemia_alive_24h=alive + (i - 1), artemia_alive_96h=alive - 1 + (i - 1))
                log.append(r)
    return pd.DataFrame(log), pd.DataFrame(counts)


def test_peroxide_screen_pass_and_half_life():
    res = B.run(*peroxide_screen_data())
    assert get(res, "S3-cut").estimate == pytest.approx(0.8, abs=0.02)
    assert get(res, "S3").decision == "PASS"
    assert get(res, "H5").decision == "PASS"      # ranking nanno > thal > akashiwo at every dose
    hl = get(res, "half-life", endpoint="h2o2_0.8 nanno")
    assert hl.estimate == pytest.approx(6.0, rel=0.01)   # planted 6 h half-life


def test_peroxide_screen_artemia_harm_fails():
    res = B.run(*peroxide_screen_data(artemia_ctrl=27, artemia_pulse=15))   # 40 points below control
    assert get(res, "S3-cut").decision == "PASS"
    assert get(res, "S3-artemia").decision == "FAIL"
    assert get(res, "S3").decision == "FAIL"


def test_peroxide_screen_no_effect_fails():
    res = B.run(*peroxide_screen_data(pulse_cut=0.0))
    assert get(res, "S3-cut").decision == "FAIL"
    assert get(res, "S3").decision == "FAIL"


# --- loop runs ------------------------------------------------------------------------------
BASE = 1.0e4


def bloom(day, start, peak_day, amp):
    """warm-up level until `start`, then a Gaussian bloom of height amp x warm-up."""
    return BASE * (1 + (amp if day >= start else 0) * np.exp(-((day - peak_day) / 3.0) ** 2))


def loop_data(exp="peroxide_loop", b_amp=2.0, c_amp=6.0, d_alive=27, b3_amp=None, contam_tank=None):
    log, counts, k = [], [], 0
    shapes = {"A": (21, 27, 9.0), "B": (21, 27, b_amp), "C": (21, 27, c_amp), "D": (999, 0, 0.0),
              "P": (7, 13, 9.0)}
    for arm, (start, pk, amp) in shapes.items():
        for i, f in enumerate(REP[: 2 if arm == "P" else 3]):
            k += 1
            t = f"PL{k:02d}"
            a = (b3_amp if (arm == "B" and i == 2 and b3_amp is not None) else amp) * f
            for d in range(0, 46):
                v = bloom(d, start, pk, a)
                if d % 2 == 0:
                    foreign = int(0.3 * v * SQ * 1e-4) if (t == contam_tank and d in (30, 32)) else 0
                    counts.append(count_row(exp, t, v, day=d, size=B.LOOP_SIZE[exp], foreign=foreign))
                    if exp == "peroxide_loop":
                        counts.append(count_row(exp, t, 2.0e3, day=d, size="large"))
                r = dict(experiment=exp, arm=arm, species="mix", tank_id=t, replicate=i + 1, volume_L=10,
                         day=d, fl_counts=10 + v / 500, fl_blank_counts=0, ph=8.1, do_mgL=8.0, do_dawn=0,
                         temp_c=14.0)
                if arm in "BCD" and d == (23 if arm != "C" else 26):
                    r.update(event="ON", trigger={"B": "model", "C": "reactive", "D": "forced"}[arm],
                             treatment_on_h=0)
                if arm in "BCD" and d == 30:
                    r.update(event="OFF", treatment_on_h=24 * 7)
                if arm in "AD" and d in (23, 25):
                    alive = 27 if arm == "A" else d_alive
                    r.update(artemia_start=30, artemia_alive_24h=alive + (i - 1),
                             artemia_alive_96h=alive - 1 + (i - 1))
                log.append(r)
    return pd.DataFrame(log), pd.DataFrame(counts)


def test_peroxide_loop_clear_effect():
    res = B.run(*loop_data())
    cok = get(res, "C_ok")
    # pilots (amp 8.1 and 9.0, peak day 13) are counted on even days: peak = 1 + amp x exp(-1/9)
    pilot_peaks = [BASE * (1 + a * np.exp(-1 / 9)) for a in (8.1, 9.0)]
    assert cok.estimate == pytest.approx(0.5 * np.mean(pilot_peaks), rel=1e-9)   # 50% of the pilot peak
    h1a = get(res, "H1a")
    # B peaks at 1 + 2f, A at 1 + 9f: geometric-mean cut ~ 70%
    assert 0.6 < h1a.estimate < 0.75 and h1a.decision == "PASS" and h1a.role == "PRIMARY"
    assert get(res, "H1b").decision == "PASS"
    assert get(res, "H2", endpoint="24h").decision == "PASS"
    assert get(res, "H2", endpoint="96h").decision == "PASS"
    assert get(res, "H4").decision == "PASS"


def test_peroxide_loop_no_effect_fails_and_gates_h1b():
    res = B.run(*loop_data(b_amp=9.0))
    assert get(res, "H1a").decision == "FAIL"
    assert get(res, "H1b").decision == "NOT TESTED"


def test_false_alarm_harm_fails_h2():
    res = B.run(*loop_data(d_alive=12))
    assert get(res, "H2", endpoint="24h").decision == "FAIL"


def test_no_bloom_is_inconclusive():
    log, counts = loop_data()
    a_tanks = log[log.arm == "A"].tank_id.unique()
    counts.loc[counts.tank_id.isin(a_tanks), "cells_counted"] = BASE * SQ * 1e-4    # A stays flat
    res = B.run(log, counts)
    assert get(res, "H1a").decision == "INCONCLUSIVE"
    assert "did not bloom" in get(res, "H1a").note


def test_aeration_loop_delay():
    # B held below C_ok the whole bloom phase (peak 3x < C_ok 5x); A above it for ~5 days
    res = B.run(*loop_data(exp="aeration_loop", b_amp=2.0))
    d = get(res, "H1-delay")
    assert d.role == "PRIMARY" and d.decision == "PASS" and d.estimate >= 4
    res0 = B.run(*loop_data(exp="aeration_loop", b_amp=9.0))
    d0 = get(res0, "H1-delay")
    assert d0.estimate == pytest.approx(0.0) and d0.decision in ("FAIL", "INCONCLUSIVE")   # n = 3 spread
    assert get(res0, "H1-delay B v C").decision == "NOT TESTED"


def test_excluded_tank_is_dropped_only_from_per_protocol():
    log, counts = loop_data(b3_amp=20.0)        # third B tank blooms hugely ...
    bad = log[(log.arm == "B") & (log.replicate == 3)].tank_id.iloc[0]
    log.loc[log.tank_id == bad, ["excluded", "exclusion_reason"]] = [1, "equipment: dosing pump failed day 22"]
    res = B.run(log, counts)
    pp, allv = get(res, "H1a"), get(res, "H1a", "all-vessels")
    assert pp.n == "2 v 3" and allv.n == "3 v 3"
    assert pp.decision == "PASS"
    assert allv.estimate < pp.estimate
    ex = res[(res.hypothesis == "exclusion") & (res.analysis_set == "per-protocol")]
    assert bad in ex.endpoint.iloc[0] and "pump" in ex.note.iloc[0]


def test_contamination_rule_needs_two_consecutive_counts():
    log, counts = loop_data(contam_tank="PL01")      # foreign cells 30% on days 30 and 32
    excl = B.exclusions(*B.prepare(log, counts)[:2])
    assert ("peroxide_loop", "PL01") in excl and "contamination" in excl[("peroxide_loop", "PL01")]
    counts2 = counts.copy()
    counts2.loc[(counts2.tank_id == "PL01") & (counts2.day == 32), "foreign_cells"] = 0   # one count only
    excl2 = B.exclusions(*B.prepare(log, counts2)[:2])
    assert ("peroxide_loop", "PL01") not in excl2


def test_too_few_tanks_is_inconclusive():
    log, counts = loop_data()
    b = log[log.arm == "B"].tank_id.unique()
    log.loc[log.tank_id.isin(b[:2]), ["excluded", "exclusion_reason"]] = [1, "lost"]
    res = B.run(log, counts)
    assert get(res, "H1a").decision == "INCONCLUSIVE"


def test_layout_is_reproducible_and_complete():
    a, b = B.layout("peroxide_screen", 20261026), B.layout("peroxide_screen", 20261026)
    assert a.equals(b) and len(a) == 60
    assert sorted(a.position) == list(range(1, 61))
    assert len(B.layout("aeration_screen", 1)) == 36
    assert len(B.layout("aeration_loop", 1)) + len(B.layout("peroxide_loop", 1)) == 28


def test_templates_match_schema():
    here = os.path.join(os.path.dirname(__file__), "..", "src", "lab", "templates")
    assert list(pd.read_csv(os.path.join(here, "tank_log.csv")).columns) == B.LOG_COLUMNS
    assert list(pd.read_csv(os.path.join(here, "counts.csv")).columns) == B.COUNT_COLUMNS


def test_ph_ceiling_rule():
    """Pilot max + 0.2, kept within 8.6-9.0; 8.6 with no pilot readings (BENCH_PREREG open question 4)."""
    ph_ceiling = B.ph_ceiling
    assert ph_ceiling([]) == 8.6
    assert ph_ceiling([8.0, 8.2]) == 8.6          # low pilots: floor of 8.6
    assert ph_ceiling([8.1, 8.55]) == 8.75        # pilot max + 0.2
    assert ph_ceiling([8.4, 9.3]) == 9.0          # never above 9.0
