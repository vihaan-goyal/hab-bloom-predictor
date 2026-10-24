"""Tests for src/lab/chl_calibration.py on synthetic data with a known answer.
Run:  python -m pytest tests/test_chl_calibration.py -q"""
import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "lab"))
import chl_calibration as cc  # noqa: E402


def test_jeffrey_humphrey_hand_value():
    # by hand: 11.85*0.400 - 1.54*0.100 - 0.08*0.050 = 4.740 - 0.154 - 0.004 = 4.582 ug/mL
    assert cc.jeffrey_humphrey(0.002, 0.402, 0.102, 0.052) == pytest.approx(4.582, abs=1e-9)
    # 4.582 ug/mL x 10 mL / 0.050 L / 1 cm = 916.4 ug/L
    assert cc.culture_chl(4.582, 10, 50, 1) == pytest.approx(916.4)
    # a 2 cm cell halves it
    assert cc.culture_chl(4.582, 10, 50, 2) == pytest.approx(458.2)


def test_spectro_warnings():
    df = pd.DataFrame([["ok", 50, 10, 1, 0.002, 0.402, 0.102, 0.052],
                       ["turbid", 50, 10, 1, 0.020, 0.420, 0.120, 0.070],
                       ["weak", 50, 10, 1, 0.001, 0.051, 0.012, 0.006]], columns=cc.SPECTRO_COLS)
    t = cc.spectro_table(df)
    assert t.warning[0] == ""
    assert "turbid" in t.warning[1]
    assert "outside" in t.warning[2]
    assert cc.stock_from_spectro(t, "ok") == pytest.approx(916.4)


def synthetic(slope=0.6, blank=310.0, sd=1.0, stock=200.0, reps=4, saturate=False, seed=0):
    """Readings at 0, 1/64 ... 1 of the stock. saturate=True: exactly linear up to 1/8 of the
    stock, then the inner filter keeps only 75%, 45% and 20% of the signal at 1/4, 1/2 and 1."""
    rng = np.random.default_rng(seed)
    fr = np.array([0, 1 / 64, 1 / 32, 1 / 16, 1 / 8, 1 / 4, 1 / 2, 1])
    keep = np.array([1, 1, 1, 1, 1, 0.75, 0.45, 0.20]) if saturate else np.ones(fr.size)
    true = blank + slope * fr * stock * keep
    cols = {"dilution_fraction": fr}
    for r in range(reps):
        cols["fl" if r == 0 else f"fl_{r + 1}"] = true + rng.normal(0, sd, fr.size)
    return pd.DataFrame(cols)


def test_recovers_slope_and_blank_from_noisy_linear_data():
    long = cc.tidy_dilution(synthetic(), stock_ugL=200.0)
    fit = cc.fit_calibration(long)
    assert len(long) == 32                       # 8 levels x 4 repeats, fl and fl_2..fl_4 melted
    assert fit["levels_dropped"] == []           # straight line: nothing is dropped
    assert fit["slope"] == pytest.approx(0.6, rel=0.02)
    assert fit["intercept"] == pytest.approx(310.0, abs=1.0)
    assert fit["blank_mean"] == pytest.approx(310.0, abs=1.5)
    assert fit["r2"] > 0.99
    k = cc.firmware_constants(fit)
    assert k["chlk_lab"] == pytest.approx(1 / 0.6, rel=0.02)
    assert k["chlk_sonde"] == pytest.approx(1.28 / 0.6, rel=0.02)


def test_drops_saturating_high_points():
    long = cc.tidy_dilution(synthetic(saturate=True), stock_ugL=200.0)
    fit = cc.fit_calibration(long)
    assert fit["levels_dropped"] == [50.0, 100.0, 200.0]   # 1/4, 1/2 and full stock
    assert fit["top_linear_ugL"] == 25.0                     # 1/8 of the stock
    assert fit["slope"] == pytest.approx(0.6, rel=0.05)      # the true low-end slope
    # fitting everything instead would badly underestimate the slope
    a, b, _ = cc.ols(long.chl_ugL, long.fl)
    assert b < 0.4
    # points above the line are never dropped
    up = synthetic(sd=0.5)
    up.loc[7, ["fl", "fl_2", "fl_3", "fl_4"]] += 30
    assert cc.fit_calibration(cc.tidy_dilution(up, 200.0))["levels_dropped"] == []


def test_lod_formula():
    assert cc.lod(2.0, 0.5) == pytest.approx(12.0)       # 3 x 2 / 0.5
    df = pd.DataFrame({"chl_ugL": [0, 0, 0, 0, 10, 20, 40], "fl": [309, 311, 310, 310, 316, 322, 334]})
    fit = cc.fit_calibration(cc.tidy_dilution(df))
    sd = np.std([309, 311, 310, 310], ddof=1)
    assert fit["lod_ugL"] == pytest.approx(3 * sd / fit["slope"])


def test_commands_use_firmware_names():
    fit = cc.fit_calibration(cc.tidy_dilution(synthetic(), 200.0))
    cmds = [c for c in cc.firmware_commands(fit) if not c.startswith("#")]
    assert cmds[0] == "blank" and cmds[1].startswith("chlk ") and cmds[2] == "cal"
    assert float(cmds[1].split()[1]) == pytest.approx(1.28 / fit["slope"], rel=1e-4)


def test_needs_blank_and_stock():
    with pytest.raises(ValueError):
        cc.tidy_dilution(pd.DataFrame({"dilution_fraction": [0, 0.5], "fl": [310, 330]}))
    with pytest.raises(ValueError):
        cc.fit_calibration(pd.DataFrame({"chl_ugL": [5.0, 10, 20], "fl": [313.0, 316, 322]}))
