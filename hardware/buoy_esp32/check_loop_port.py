"""
check_loop_port.py -- prove loop_control.h (the ESP32's treatment rules) matches the Python controller
----------------------------------------------------------------------------------------------------
Builds loop_test.cpp with g++, runs random multi-week scenarios through it and through the Python
reference (alerter_link.Reference -> src/sim/loop_controller.Controller, the same reference the Uno
alerter was checked against), and compares the decision, next check day and episode count per day.

    python check_loop_port.py            2,000 scenarios (all three modes, gaps, missing readings, stops)

Values are sent with 3 decimals on both sides. The firmware computes in 32-bit floats and Python in
64-bit, so a value landing exactly on a threshold could differ; the generator keeps clear of them.
Also checks the calendar-day conversion against Python's datetime.
"""
import datetime as dt
import math
import os
import random
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "alerter_uno"))
from alerter_link import Reference, T_ON  # noqa: E402

N_SCENARIOS = 2000


def fmt(v):
    return "nan" if v is None else f"{v:.3f}"


def clear_of(v, edges, eps=1e-3):
    """Nudge v away from any threshold so float and double agree."""
    while any(abs(v - e) < eps for e in edges if e is not None):
        v += 2 * eps
    return v


def scenario(rng):
    mode = rng.choice("FFFRH")
    x = rng.choice([1, 2, 3, 4])
    max_on = rng.choice([0, 0, 3, 6])
    warm = None if rng.random() < 0.2 else round(rng.uniform(1.5, 4.0), 3)
    floor = rng.choice([0.0, 0.8, 0.8, 0.6])
    c_ok = round(rng.uniform(3.0, 7.0), 3)
    edges = [c_ok, T_ON, 0.8 * T_ON, None if warm is None else floor * warm, None if warm is None else 2 * warm]
    days, day, chl = [], rng.randint(1, 400), rng.uniform(1, 6)
    for _ in range(rng.randint(8, 45)):
        day += 1 if rng.random() < 0.85 else rng.randint(2, 5)
        chl = max(0.2, chl + rng.gauss(0.3, 1.6))
        p = None if rng.random() < 0.05 else clear_of(round(min(0.99, max(0.01, rng.gauss(0.45, 0.25))), 3), edges)
        c = None if rng.random() < 0.08 else clear_of(round(chl, 3), edges)
        days.append((day, p, c, rng.random() < 0.03))
    return dict(mode=mode, x=x, max_on=max_on, warm=warm, floor=floor, c_ok=c_ok, days=days)


def main():
    exe = os.path.join(tempfile.gettempdir(), "loop_test_port.exe")
    subprocess.run(["g++", "-O1", "-std=c++11", "-o", exe, os.path.join(HERE, "loop_test.cpp")], check=True)
    rng = random.Random(42)
    scen = [scenario(rng) for _ in range(N_SCENARIOS)]
    lines, expect = [], []
    for s in scen:
        lines.append(f"c {T_ON} {fmt(s['c_ok'])} {fmt(s['warm'])} {s['floor']} {s['x']} {s['max_on']} {s['mode']}")
        ref = Reference(s["x"], float(fmt(s["c_ok"])), s["mode"], s["warm"], s["floor"], s["max_on"])
        prev_chl = {}
        for day, p, c, stop in s["days"]:
            lines.append(f"d {day} {fmt(p)} {fmt(c)} {int(stop)}")
            label, nxt, eps = ref.step(day, p, c, force_off=stop)
            expect.append(f"{label} {'-' if nxt is None else nxt} {eps}")
    out = subprocess.run([exe], input="\n".join(lines) + "\n", capture_output=True, text=True, check=True).stdout.split("\n")
    out = [o.strip() for o in out if o.strip()]
    bad = [(i, e, o) for i, (e, o) in enumerate(zip(expect, out)) if e != o]
    labels = {}
    for e in expect:
        labels[e.split()[0]] = labels.get(e.split()[0], 0) + 1
    print(f"{N_SCENARIOS} scenarios, {len(expect)} days; C++ returned {len(out)} lines")
    print("decisions in the reference:", dict(sorted(labels.items())))
    print(f"mismatches: {len(bad)}" + ("" if len(out) == len(expect) else "  (LINE COUNT DIFFERS)"))
    for i, e, o in bad[:10]:
        print(f"  day #{i}: python '{e}'  c++ '{o}'")

    # calendar-day numbers: loop_day_number / loop_date_of vs datetime, every day 1999-2040
    src = ('#include <cstdio>\n#include "loop_control.h"\nint main(){long y;while(scanf("%ld",&y)==1){'
           'long n=loop_day_number((int32_t)y);printf("%ld %ld%c",n,(long)loop_date_of((int32_t)n),10);}return 0;}\n')
    cpp = os.path.join(tempfile.gettempdir(), "loop_days_port.cpp")
    exe2 = os.path.join(tempfile.gettempdir(), "loop_days_port.exe")
    open(cpp, "w").write(src)
    subprocess.run(["g++", "-O1", "-std=c++11", f"-I{HERE}", "-o", exe2, cpp], check=True)
    d0, n = dt.date(1999, 1, 1), (dt.date(2040, 12, 31) - dt.date(1999, 1, 1)).days + 1
    dates = [d0 + dt.timedelta(days=i) for i in range(n)]
    got = subprocess.run([exe2], input="\n".join(d.strftime("%Y%m%d") for d in dates), capture_output=True, text=True, check=True).stdout.split("\n")
    wrong = sum(1 for d, g in zip(dates, got)
                if g.split() != [str((d - dt.date(1970, 1, 1)).days), d.strftime("%Y%m%d")])
    print(f"calendar days 1999-2040: {n} dates, {wrong} wrong")
    ok = not bad and len(out) == len(expect) and wrong == 0
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
