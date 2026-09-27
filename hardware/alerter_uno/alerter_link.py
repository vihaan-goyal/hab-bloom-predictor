"""
alerter_link.py -- the laptop side of the Uno alerter (build stage 7)
=====================================================================
Sends one `<day> <p> <chl>` line per day to hardware/alerter_uno/alerter_uno.ino over USB,
reads the Uno's decision back, and logs everything to a CSV. Every Uno reply is also checked
against the Python controller (src/sim/loop_controller.py), so a mismatch shows up at once.

Opening the USB port resets an Uno and wipes its ON/OFF state. --today therefore replays the
earlier days from the log (buzzer muted) before sending today's line.

--sim runs a stand-in Uno made from the Python controller, so everything can be tried with
no board plugged in.

Run from repo root (needs `pip install pyserial` for a real Uno):
    python hardware/alerter_uno/alerter_link.py --ports
    python hardware/alerter_uno/alerter_link.py --demo [--sim]
    python hardware/alerter_uno/alerter_link.py --replay narragansett:<station> [--days 150] [--sim]
    python hardware/alerter_uno/alerter_link.py --replay my_days.csv [--sim]      # columns day,p,chl
    python hardware/alerter_uno/alerter_link.py --today --p 0.62 --chl 7.4 [--start 2026-11-10]
Options: --port COM4, --x 3 (days between re-measures), --cok 5 (C_ok, ug/L).
Log: hardware/alerter_uno/logs/alerter_log.csv
"""
import argparse
import csv
import datetime as dt
import json
import math
import os
import re
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src", "sim"))
from loop_controller import Controller, T_ON  # noqa: E402

LOG_DIR = os.path.join(HERE, "logs")
LOG = os.path.join(LOG_DIR, "alerter_log.csv")
STATE = os.path.join(LOG_DIR, "state.json")
LOG_COLS = ["timestamp", "mode", "source", "day", "p", "chl", "uno_state", "next_check",
            "episodes", "py_state", "match"]
BAUD = 115200
REPLY = re.compile(r"day=(-?\d+) p=(\S+) chl=(\S+) -> (\w+)(?: next_check=(\d+))? episodes=(\d+)")
DEMO = [(1, 0.2, 3), (2, 0.6, 4), (3, 0.7, 6), (4, 0.7, 8), (5, 0.5, 9), (8, 0.3, 4), (9, 0.3, 3)]


def fmt(v):
    """Value as sent to the Uno ('-' = missing)."""
    return "-" if v is None or (isinstance(v, float) and math.isnan(v)) else f"{v:.4g}"


def fmt2(v):
    """Value as the sketch prints it."""
    return "nan" if v is None else f"{v:.2f}"


class Reference:
    """The Python controller, labelled the way the sketch labels its decisions."""

    def __init__(self, x, c_ok):
        self.c, self.c_ok = Controller(1, x), c_ok

    def step(self, day, p, chl):
        was = bool(self.c.on[0])
        maxed_before = int(self.c.maxed[0])
        p_ = np.nan if p is None else p
        chl_ = np.nan if chl is None else chl
        trig = np.array([not math.isnan(p_) and p_ >= T_ON])
        self.c.step(int(day), trig, np.array([p_]), np.array([chl_]), self.c_ok)
        on = bool(self.c.on[0])
        if not was and on:
            label = "START"
        elif was and not on:
            label = "STOP_MAX_ON" if self.c.maxed[0] > maxed_before else "OFF"
        else:
            label = "ON" if on else "idle"
        nxt = int(self.c.check[0]) if on else None
        return label, nxt, int(self.c.episodes[0])


class SimUno:
    """Stand-in for the board: answers like the sketch, using the Python controller."""

    def __init__(self):
        self.x, self.c_ok, self.ref = 3, 5.0, None
        self.out = ["alerter_uno ready. Send: <day> <p> <chl>   or: status"]

    def write(self, data):
        parts = data.decode().split()
        if not parts:
            return
        if parts[0].lstrip("-").isdigit():
            if self.ref is None:
                self.ref = Reference(self.x, self.c_ok)
            val = lambda s: None if s in ("-", "nan") else float(s)  # noqa: E731
            day, p, chl = int(parts[0]), val(parts[1]), val(parts[2])
            label, nxt, eps = self.ref.step(day, p, chl)
            nc = f" next_check={nxt}" if nxt is not None else ""
            self.out.append(f"day={day} p={fmt2(p)} chl={fmt2(chl)} -> {label}{nc} episodes={eps}")
            return
        if parts[0] == "x":
            self.x = int(parts[1])
        elif parts[0] == "cok":
            self.c_ok = float(parts[1])
        elif parts[0] == "reset":
            self.ref = None
        if parts[0] != "mute":
            self.out.append(f"mode=F X={self.x} C_ok={self.c_ok:.2f} state=sim")

    def readline(self):
        return (self.out.pop(0) + "\r\n").encode() if self.out else b""

    def close(self):
        pass


def find_port():
    from serial.tools import list_ports
    for p in list_ports.comports():
        desc = f"{p.description} {p.manufacturer or ''}".lower()
        if p.vid in (0x2341, 0x2A03, 0x1A86, 0x0403) or "arduino" in desc or "ch340" in desc:
            return p.device
    return None


class Link:
    def __init__(self, port, sim):
        self.sim = sim
        if sim:
            self.dev = SimUno()
        else:
            import serial
            port = port or find_port()
            if not port:
                sys.exit("No Arduino found. Plug it in, close the Arduino IDE Serial Monitor, or pass --port COM4.")
            self.dev = serial.Serial(port, BAUD, timeout=0.2)
            time.sleep(2.2)                   # the Uno restarts when the port opens
        self.send("status", expect=r"^mode=")

    def send(self, text, expect=None, timeout=3.0):
        """Send one line; return the first reply line matching `expect` (None: don't wait)."""
        self.dev.write((text + "\n").encode())
        if expect is None:
            time.sleep(0 if self.sim else 0.05)
            return None
        end = time.time() + timeout
        while time.time() < end:
            line = self.dev.readline().decode(errors="replace").strip()
            if not line:
                if self.sim:
                    return None
                continue
            if re.search(expect, line):
                return line
        return None

    def day(self, day, p, chl):
        line = self.send(f"{day} {fmt(p)} {fmt(chl)}", expect=r"^day=")
        m = REPLY.search(line or "")
        if not m:
            return None, None, None, line
        return m.group(4), (int(m.group(5)) if m.group(5) else None), int(m.group(6)), line

    def setup(self, x, c_ok):
        for cmd in (f"x {x}", f"cok {c_ok}", "mode F", "reset"):
            self.send(cmd, expect=r"^mode=")


def log_rows(rows):
    os.makedirs(LOG_DIR, exist_ok=True)
    new = not os.path.exists(LOG)
    with open(LOG, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LOG_COLS)
        if new:
            w.writeheader()
        w.writerows(rows)


def row(mode, link, day, p, chl, state, nxt, eps, raw, py):
    return dict(timestamp=dt.datetime.now().isoformat(timespec="seconds"), mode=mode,
                source="sim" if link.sim else "uno", day=day, p=fmt(p), chl=fmt(chl),
                uno_state=state or f"NO REPLY: {raw}", next_check="" if nxt is None else nxt,
                episodes="" if eps is None else eps, py_state=py, match=state == py)


def run_days(link, days, x, c_ok, mode):
    """Send (day, p, chl) rows, compare with the Python controller, log, print the active days."""
    link.setup(x, c_ok)
    ref = Reference(x, c_ok)
    rows = []
    for day, p, chl in days:
        state, nxt, eps, raw = link.day(day, p, chl)
        py, _, _ = ref.step(day, p, chl)
        rows.append(row(mode, link, day, p, chl, state, nxt, eps, raw, py))
        if state != "idle" or state != py:
            flag = "" if state == py else f"   <-- MISMATCH (Python says {py})"
            print(f"  day {day:>6}  p={fmt(p):>6}  chl={fmt(chl):>6}  -> {state}{flag}")
    log_rows(rows)
    return rows


def load_replay(spec, ndays):
    if spec.startswith("narragansett:"):
        sys.path.insert(0, os.path.join(ROOT, "src", "models"))
        import control_loop_sim as L1
        station = spec.split(":", 1)[1]
        df = L1.load_narragansett()
        g = df[df.station == station].sort_values("day")
        if g.empty:
            sys.exit(f"station {station!r} not found; stations: {sorted(df.station.unique())}")
        days = [(int(d), None if math.isnan(p) else float(p), None if math.isnan(c) else float(c))
                for d, p, c in zip(g.day, g.p, g.chl)]
    else:
        num = lambda s: None if s in ("", "-", "nan") else float(s)  # noqa: E731
        with open(spec) as f:
            days = [(int(r["day"]), num(r["p"]), num(r["chl"])) for r in csv.DictReader(f)]
    return days[:ndays] if ndays else days


def today(link, a):
    os.makedirs(LOG_DIR, exist_ok=True)
    state = json.load(open(STATE)) if os.path.exists(STATE) else {}
    start = a.start or state.get("start") or dt.date.today().isoformat()
    state.update(start=start, x=a.x, c_ok=a.cok)
    with open(STATE, "w") as f:
        json.dump(state, f, indent=1)
    day = (dt.date.today() - dt.date.fromisoformat(start)).days + 1
    history = {}
    if os.path.exists(LOG):
        num = lambda s: None if s in ("", "-") else float(s)  # noqa: E731
        with open(LOG) as f:
            for r in csv.DictReader(f):
                if r["mode"] == "today" and int(r["day"]) < day:
                    history[int(r["day"])] = (int(r["day"]), num(r["p"]), num(r["chl"]))
    print(f"Day {day} (run started {start}); restoring {len(history)} earlier day(s) on the Uno, buzzer muted")
    link.send("mute 1")
    link.setup(a.x, a.cok)
    ref = Reference(a.x, a.cok)
    for d, p, c in sorted(history.values()):
        link.day(d, p, c)
        ref.step(d, p, c)
    link.send("mute 0")
    state_, nxt, eps, raw = link.day(day, a.p, a.chl)
    py, _, _ = ref.step(day, a.p, a.chl)
    log_rows([row("today", link, day, a.p, a.chl, state_, nxt, eps, raw, py)])
    print(f"Today: p={fmt(a.p)} chl={fmt(a.chl)} -> {state_}"
          + (f" (next re-measure: day {nxt})" if nxt else "")
          + ("" if state_ == py else f"   <-- MISMATCH (Python says {py})"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ports", action="store_true", help="list serial ports and exit")
    ap.add_argument("--demo", action="store_true", help="send Test A")
    ap.add_argument("--replay", help="narragansett:<station> or a CSV with day,p,chl")
    ap.add_argument("--days", type=int, default=0, help="only the first N days of a replay")
    ap.add_argument("--today", action="store_true", help="send today's line (restores history first)")
    ap.add_argument("--p", type=float, help="today's forecast probability")
    ap.add_argument("--chl", type=float, help="today's chlorophyll (ug/L)")
    ap.add_argument("--start", help="first day of the run, YYYY-MM-DD (--today)")
    ap.add_argument("--x", type=int, default=3)
    ap.add_argument("--cok", type=float, default=5.0)
    ap.add_argument("--port")
    ap.add_argument("--sim", action="store_true", help="no board: use a simulated Uno")
    a = ap.parse_args()

    if a.ports:
        from serial.tools import list_ports
        for p in list_ports.comports():
            print(p.device, "|", p.description, "| VID", p.vid)
        print("Arduino guess:", find_port())
        return
    if not (a.demo or a.replay or a.today):
        ap.error("choose --demo, --replay, --today or --ports")
    if a.today and a.p is None and a.chl is None:
        ap.error("--today needs --p and/or --chl")

    link = Link(a.port, a.sim)
    if a.today:
        today(link, a)
        link.dev.close()
        return
    days = DEMO if a.demo else load_replay(a.replay, a.days)
    t0 = time.time()
    rows = run_days(link, days, a.x, a.cok, "demo" if a.demo else "replay")
    on = sum(r["uno_state"] in ("START", "ON", "OFF", "STOP_MAX_ON") for r in rows)
    eps = max([int(r["episodes"]) for r in rows if r["episodes"] != ""] or [0])
    mism = sum(not r["match"] for r in rows)
    print(f"{len(rows)} days sent in {time.time() - t0:.1f} s | treatment-ON days {on} | episodes {eps} | "
          f"mismatches with the Python controller: {mism}")
    print(f"log: {os.path.relpath(LOG, ROOT)}")
    link.dev.close()


if __name__ == "__main__":
    main()
