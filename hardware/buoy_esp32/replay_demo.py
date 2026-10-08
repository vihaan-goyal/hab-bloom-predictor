"""
replay_demo.py -- stream one Narragansett station's real daily rows to the buoy and check its forecasts
======================================================================================================
Reads the fork's data/narragansett_daily_features.csv, takes one station's daily rows in date
order, and for each day:
  * sends   day <yyyy-mm-dd> <chl> <temp> <sal> <do> [clim]   to the ESP32 (buoy_esp32.ino),
  * reads back the board's 23 features (F line) and probability (P line),
  * computes the SAME day in Python: same daily history, same feature rules (features() below mirrors
    features.h line for line), same model (release/narragansett_bloom_model_v2.joblib, NaN filled with
    the training medians as in export_c_model.py),
  * prints board p next to Python p and flags any mismatch (|dp| >= 2e-3 or a different alert).

Without a board (--sim), only the Python path runs, and it is compared with the fork's PRECOMPUTED
feature columns (the training table): this checks that the streaming feature code reproduces training.

Climatology (--clim): "row" (default) sends the fork's chl_climatology for each day as the optional
6th value, so the whole feature vector is comparable. "none" sends nothing: the board uses its `clim`
table (empty -> NaN -> training median), as a new buoy would; --sim then reports how much that
changes the forecasts.

Usage (BASE env):
  ~/anaconda3/python.exe hardware/buoy_esp32/replay_demo.py --sim --station B3
  ~/anaconda3/python.exe hardware/buoy_esp32/replay_demo.py --port COM5 --station B3 --start 2023-07-01 --days 60
"""
import argparse
import math
import os
import sys
import time
from collections import deque

import joblib
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FORK = os.path.normpath(os.path.join(HERE, "..", "..", "..", "hab-bloom-predictor-narragansett"))
HIST_MAX, WARMUP = 30, 21           # features.h HIST_MAX; the longest rolling window
P_TOL = 2e-3
FEATS = ["chl", "chl_lag1", "chl_lag2", "chl_lag3", "chl_lag4", "chl_roll3_mean", "chl_roll6_mean",
         "chl_roll9_mean", "chl_roll14_mean", "chl_roll21_mean", "chl_trend", "chl_anomaly",
         "chl_climatology", "do", "do_lag1", "temp", "temp_lag1", "sal", "sal_lag1", "sal_lag2",
         "sal_lag3", "sal_lag4", "month"]


# ---------------------------------------------------------------- the device's feature rules, in Python
def roll_mean(hist, w):
    """pandas rolling(w, min_periods=max(2, w//3)).mean() at the newest row (rows, not calendar days)."""
    vals = [r["chl"] for r in list(hist)[-w:] if not math.isnan(r["chl"])]
    return sum(vals) / len(vals) if len(vals) >= max(2, w // 3) else math.nan


def back(hist, k, key):
    return hist[-1 - k][key] if len(hist) > k else math.nan


def features(hist, clim_table):
    """23 features for the newest row of `hist` (deque of dicts, oldest first). Mirrors features.h."""
    d = hist[-1]
    x = {"chl": d["chl"]}
    for k in (1, 2, 3, 4):
        x[f"chl_lag{k}"] = back(hist, k, "chl")
        x[f"sal_lag{k}"] = back(hist, k, "sal")
    for w in (3, 6, 9, 14, 21):
        x[f"chl_roll{w}_mean"] = roll_mean(hist, w)
    x["chl_trend"] = d["chl"] - x["chl_roll6_mean"]
    m = d["date"].month
    clim = d["clim"] if not math.isnan(d["clim"]) else clim_table.get(m, math.nan)
    x["chl_climatology"] = clim
    x["chl_anomaly"] = d["chl"] - clim
    x["do"], x["do_lag1"] = d["do"], back(hist, 1, "do")
    x["temp"], x["temp_lag1"] = d["temp"], back(hist, 1, "temp")
    x["sal"] = d["sal"]
    x["month"] = float(m)
    return [x[f] for f in FEATS]


def push(hist, rec):
    """features.h hist_push: same date replaces, older is rejected, otherwise append (keep HIST_MAX)."""
    if hist and rec["date"] == hist[-1]["date"]:
        hist[-1] = rec
        return 1
    if hist and rec["date"] < hist[-1]["date"]:
        return -1
    hist.append(rec)
    return 0


class Model:
    def __init__(self, fork):
        pack = joblib.load(os.path.join(fork, "release", "narragansett_bloom_model_v2.joblib"))
        assert pack["features"] == FEATS, "feature order changed in the release pack"
        self.m, self.med, self.thr = pack["model"], pd.Series(pack["medians"]), pack["threshold"]

    def prob(self, X):
        X = pd.DataFrame(np.asarray(X, dtype=float), columns=FEATS)
        return self.m.predict_proba(X.fillna(self.med).values)[:, 1]   # same call as export_c_model.py


# ---------------------------------------------------------------- data
def station_rows(fork, station):
    df = pd.read_csv(os.path.join(fork, "data", "narragansett_daily_features.csv"), parse_dates=["date"])
    st = df[df.station == station].sort_values("date").reset_index(drop=True)
    if st.empty:
        sys.exit(f"no rows for station {station!r}; stations: {sorted(df.station.unique())}")
    return st


def fmt(v):
    return "nan" if v is None or (isinstance(v, float) and math.isnan(v)) else f"{v:.9g}"


def day_line(r, send_clim):
    vals = [r["chl"], r["temp"], r["sal"], r["do"]] + ([r["chl_climatology"]] if send_clim else [])
    return f"day {r['date']:%Y-%m-%d} " + " ".join(fmt(float(v)) for v in vals)


def to_rec(r, send_clim):
    f = lambda v: float(v) if pd.notna(v) else math.nan
    return {"date": r["date"], "chl": f(r["chl"]), "temp": f(r["temp"]), "sal": f(r["sal"]),
            "do": f(r["do"]), "clim": f(r["chl_climatology"]) if send_clim else math.nan}


# ---------------------------------------------------------------- board link
class Board:
    def __init__(self, port, baud=115200):
        import serial                      # pyserial
        self.s = serial.Serial(port, baud, timeout=0.2)
        t0 = time.time()                   # opening the port resets the ESP32: wait for the self-test
        while time.time() - t0 < 12:
            ln = self.readline()
            if ln:
                print("  board>", ln)
            if ln.startswith("READY"):
                break
        else:
            print("  (no READY seen; continuing)")
        self.cmd("reset")

    def readline(self):
        return self.s.readline().decode(errors="replace").strip()

    def cmd(self, line, until=None, timeout=5.0):
        self.s.write((line + "\n").encode())
        out, t0 = [], time.time()
        while time.time() - t0 < timeout:
            ln = self.readline()
            if not ln:
                if until is None and out:
                    break
                continue
            out.append(ln)
            if until and ln.startswith(until):
                break
        return out

    def day(self, line):
        lines = self.cmd(line, until="P ")
        feats, p, state = None, math.nan, "?"
        for ln in lines:
            if ln.startswith("F "):
                kv = dict(t.split("=", 1) for t in ln.split()[2:])
                feats = [float(kv.get(f, "nan")) for f in FEATS]
            elif ln.startswith("P "):
                parts = ln.split()
                p = float(parts[2].split("=", 1)[1])
                state = parts[3]
            elif not ln.startswith("note"):
                print("  board>", ln)
        return feats, p, state


# ---------------------------------------------------------------- main
def compare_cols(py, ref, cols):
    """per-column max |diff| and the number of rows that differ (NaN vs number counts as different)."""
    out = {}
    for j, c in enumerate(cols):
        a, b = py[:, j], ref[:, j]
        nan_mis = np.isnan(a) != np.isnan(b)
        both = ~np.isnan(a) & ~np.isnan(b)
        d = np.abs(a[both] - b[both])
        bad = nan_mis.sum() + (d > 1e-6 * (1 + np.abs(b[both]))).sum()
        out[c] = (float(d.max()) if d.size else 0.0, int(bad))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1], formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", help="serial port of the ESP32, e.g. COM5 or /dev/ttyUSB0")
    ap.add_argument("--sim", action="store_true", help="no board: Python path only, checked against the fork's columns")
    ap.add_argument("--station", default="B3")
    ap.add_argument("--start", help="first reported day yyyy-mm-dd (the 21 days before it are streamed as warm-up)")
    ap.add_argument("--days", type=int, default=0, help="days to report after --start (0 = all)")
    ap.add_argument("--clim", choices=["row", "none"], default="row")
    ap.add_argument("--fork", default=DEFAULT_FORK)
    ap.add_argument("--verbose", action="store_true", help="--sim: print every day")
    ap.add_argument("--bulletins", action="store_true", help="--sim: print the harbor bulletin timeline")
    a = ap.parse_args()
    if not a.sim and not a.port:
        ap.error("give --port COMx (board) or --sim (no board)")

    st = station_rows(a.fork, a.station)
    i0 = 0
    if a.start:
        i0 = int(st["date"].searchsorted(pd.Timestamp(a.start)))
    feed0 = max(0, i0 - WARMUP)
    i1 = len(st) if a.days <= 0 else min(len(st), i0 + a.days)
    rows = st.iloc[feed0:i1]
    send_clim = a.clim == "row"
    model = Model(a.fork)
    print(f"station {a.station}: streaming {len(rows)} days {rows.date.iloc[0]:%Y-%m-%d}..{rows.date.iloc[-1]:%Y-%m-%d}"
          f" ({i0 - feed0} warm-up), clim={a.clim}, threshold {model.thr}")

    board = None if a.sim else Board(a.port)
    hist, X, BX, BP = deque(maxlen=HIST_MAX), [], [], []
    for _, r in rows.iterrows():
        push(hist, to_rec(r, send_clim))
        X.append(features(hist, {}))
        if board:
            bf, bp, _ = board.day(day_line(r, send_clim))
            BX.append(bf if bf else [math.nan] * len(FEATS))
            BP.append(bp)
    X = np.array(X, dtype=float)
    p_py = model.prob(X)
    dates = rows["date"].dt.strftime("%Y-%m-%d").values
    rep = slice(i0 - feed0, None)      # reported rows (after warm-up)

    if board:
        BP, BX = np.array(BP), np.array(BX, dtype=float)
        print(f"\n{'date':10s} {'chl':>7s} {'p_board':>9s} {'p_python':>9s} {'diff':>9s}  board   python")
        mism = 0
        for k in range(len(rows))[rep]:
            d = BP[k] - p_py[k]
            ab, apy = BP[k] >= model.thr, p_py[k] >= model.thr
            bad = not (abs(d) < P_TOL) or ab != apy
            mism += bad
            print(f"{dates[k]} {X[k, 0]:7.2f} {BP[k]:9.6f} {p_py[k]:9.6f} {d:+9.2e}  "
                  f"{'ALERT' if ab else 'idle ':5s}   {'ALERT' if apy else 'idle ':5s}{'  <-- MISMATCH' if bad else ''}")
        fd = np.nanmax(np.abs(BX[rep] - X[rep])) if len(BX) else math.nan
        print(f"\nboard vs Python: {len(BP[rep])} days, {mism} mismatches; max |dp| {np.nanmax(np.abs(BP[rep] - p_py[rep])):.2e}; "
              f"max |feature diff| {fd:.2e}")
        return

    # --sim: Python streaming features vs the fork's precomputed training columns
    # from the station's first row every row is exact; otherwise the 21 warm-up rows give the
    # reported rows their full window (roll21 = the row + 20 before it)
    cmp_rows = slice(0, None) if feed0 == 0 else rep
    ref = rows[FEATS].astype(float).values
    cols = FEATS if send_clim else [f for f in FEATS if f not in ("chl_climatology", "chl_anomaly")]
    idx = [FEATS.index(c) for c in cols]
    res = compare_cols(X[cmp_rows][:, idx], ref[cmp_rows][:, idx], cols)
    n_cmp = len(X[cmp_rows])
    p_ref = model.prob(ref)
    if a.verbose:
        for k in range(len(rows))[rep]:
            print(f"{dates[k]} chl={X[k, 0]:6.2f} p_stream={p_py[k]:.6f} p_fork_cols={p_ref[k]:.6f}")
    bad_cols = {c: v for c, v in res.items() if v[1]}
    worst = max(res.values(), key=lambda v: v[0])[0]
    print(f"\nfeatures, streaming Python vs fork columns, {n_cmp} days x {len(cols)} features: "
          f"max |diff| {worst:.2e}; columns with differing rows: {bad_cols if bad_cols else 'none'}")
    dp = np.abs(p_py[cmp_rows] - p_ref[cmp_rows])
    flips = int(((p_py[cmp_rows] >= model.thr) != (p_ref[cmp_rows] >= model.thr)).sum())
    print(f"forecast, streaming vs fork columns: max |dp| {dp.max():.2e}, alert disagreements {flips} "
          f"(alerts: stream {int((p_py[cmp_rows] >= model.thr).sum())}, fork {int((p_ref[cmp_rows] >= model.thr).sum())})")
    if not send_clim:
        print("  (clim=none: chl_climatology/chl_anomaly are NaN -> training median on the device, so differences "
              "above are the cost of not having a climatology table)")
    if a.bulletins:
        # same rules as applyForecast() in buoy_esp32.ino: WARNING when the alert turns on, All clear when it
        # turns off, Bloom detected when chl > 10 after 5 stored days at or below 10 (an onset)
        print(f"\nharbor bulletins, station {a.station} (same rules as the firmware):")
        on = False
        for k in range(len(rows)):
            chl, p = X[k, 0], p_py[k]
            now = p >= model.thr
            if k >= rep.start:
                if chl > 10 and k >= 5 and all(X[k - j, 0] <= 10 for j in range(1, 6)):
                    print(f"  {dates[k]}  Bloom detected   chl {chl:5.1f}")
                if now and not on:
                    print(f"  {dates[k]}  Bloom WARNING    risk {p:.2f}, chl {chl:5.1f}  (bloom likely within 7 days)")
                elif on and not now:
                    print(f"  {dates[k]}  All clear        risk {p:.2f}, chl {chl:5.1f}")
            on = now
    if not a.verbose:
        print("\nlast 10 reported days:")
        for k in range(len(rows))[rep][-10:]:
            print(f"  {dates[k]} chl={X[k, 0]:6.2f}  p={p_py[k]:.4f} {'ALERT' if p_py[k] >= model.thr else 'idle'}")


if __name__ == "__main__":
    main()
