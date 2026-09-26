"""
draw_relay_breadboard.py -- circuito-style breadboard picture of the stage 2 relay driver
=======================================================================================
circuito.io can't draw a bare 5-pin relay with its transistor and flyback diode, so this draws
it by hand: PN2222A on D10, 1N4007 across the coil, and an optional LED as a pretend pump on
the relay's COM -> NO contacts. Only what connects to what matters; any free columns work.

Run from repo root:
    python hardware/alerter_uno/draw_relay_breadboard.py
Writes hardware/alerter_uno/relay_breadboard.png
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle, Wedge

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "relay_breadboard.png")

NCOL = 30
Y = {r: 10 - i for i, r in enumerate("abcde")}           # a=10 ... e=6
Y.update({r: 4 - i for i, r in enumerate("fghij")})      # f=4 ... j=0
Y_PLUS, Y_MINUS = 12.6, 11.9                             # top power rails


def hole(col, row):
    return (col, Y[row])


fig, ax = plt.subplots(figsize=(15, 11))
ax.set_aspect("equal")
ax.axis("off")

# --- breadboard -------------------------------------------------------------------------
ax.add_patch(FancyBboxPatch((-0.2, -0.9), NCOL + 1.4, 14.2, boxstyle="round,pad=0.2",
                            fc="#f2f2f2", ec="#bbbbbb", lw=1.5))
ax.add_patch(Rectangle((0.3, 4.7), NCOL + 0.4, 0.6, fc="#dddddd", ec="none"))  # centre gap
for c in range(1, NCOL + 1):
    for r in "abcdefghij":
        ax.add_patch(Rectangle((c - 0.13, Y[r] - 0.13), 0.26, 0.26, fc="#555555", ec="none"))
    for y in (Y_PLUS, Y_MINUS):
        ax.add_patch(Rectangle((c - 0.13, y - 0.13), 0.26, 0.26, fc="#555555", ec="none"))
    if c % 5 == 0 or c == 1:
        ax.text(c, 10.75, str(c), ha="center", va="center", fontsize=7, color="#888888")
for r in "abcdefghij":
    ax.text(0.35, Y[r], r, ha="center", va="center", fontsize=7, color="#888888")
ax.plot([0.5, NCOL + 0.5], [Y_PLUS + 0.35] * 2, color="#d62728", lw=1.5)
ax.plot([0.5, NCOL + 0.5], [Y_MINUS - 0.35] * 2, color="#1f77b4", lw=1.5)
ax.text(NCOL + 0.9, Y_PLUS, "+ 5V", color="#d62728", va="center", fontsize=10, fontweight="bold")
ax.text(NCOL + 0.9, Y_MINUS, "− GND", color="#1f77b4", va="center", fontsize=10, fontweight="bold")
ax.text(NCOL / 2, 13.55, "Use any free columns on your breadboard: only what connects to what matters. "
        "Each column's a-e holes are joined; so are its f-j holes.", ha="center", fontsize=9, color="#555555")


def wire(points, colour, lw=4):
    xs, ys = zip(*points)
    ax.plot(xs, ys, color="black", lw=lw + 1.6, solid_capstyle="round", zorder=4)
    ax.plot(xs, ys, color=colour, lw=lw, solid_capstyle="round", zorder=5)
    for x, y in (points[0], points[-1]):
        ax.add_patch(Circle((x, y), 0.17, fc=colour, ec="black", lw=1, zorder=6))


def resistor(c1, c2, row, bands, label):
    x1, x2, y = c1, c2, Y[row]
    ax.plot([x1, x2], [y, y], color="#999999", lw=2, zorder=6)
    ax.add_patch(FancyBboxPatch((x1 + 0.9, y - 0.28), (x2 - x1) - 1.8, 0.56, boxstyle="round,pad=0.08",
                                fc="#e8d3a8", ec="#8a7650", lw=1, zorder=7))
    bx = x1 + 1.2
    for b in bands:
        ax.add_patch(Rectangle((bx, y - 0.3), 0.18, 0.6, fc=b, ec="none", zorder=8))
        bx += 0.35
    ax.text((x1 + x2) / 2, y + 0.55, label, ha="center", fontsize=9, zorder=9)


# --- Arduino (below the breadboard) -----------------------------------------------------
ax.add_patch(FancyBboxPatch((0, -9.5), 12, 6, boxstyle="round,pad=0.2", fc="#1f7a8c", ec="#0f4c57", lw=2))
ax.text(6, -7.2, "Arduino Uno", color="white", ha="center", fontsize=14, fontweight="bold")
ax.text(6, -8.3, "(the stage 1 wiring stays as it is)", color="white", ha="center", fontsize=9)
PIN = {"5V": (2, -3.6), "GND": (4, -3.6), "D10": (9, -3.6)}
for name, (x, y) in PIN.items():
    ax.add_patch(Rectangle((x - 0.3, y - 0.3), 0.6, 0.6, fc="#222222", ec="white", zorder=3))
    ax.text(x, y - 0.8, name, color="white", ha="center", fontsize=10, fontweight="bold", zorder=3)
ax.text(12.8, -8.6, "If 5V and GND already go to the rails from\nstage 1, skip the red and black wires here.",
        fontsize=9, color="#555555", va="center")

# --- columns used ----------------------------------------------------------------------
C_IN, C_E, C_B, C_C, C_5V = 2, 5, 6, 7, 11          # D10 in, transistor E B C, coil 5V node
C_PUMP_IN, C_LED_A, C_LED_K = 18, 22, 23             # pretend-pump LED

# Arduino → breadboard
wire([PIN["5V"], (2, -2.2), (0.0, -2.2), (0.0, Y_PLUS), (1, Y_PLUS)], "#d62728")
wire([PIN["GND"], (4, -1.6), (-0.6, -1.6), (-0.6, Y_MINUS), (2, Y_MINUS)], "#222222")
wire([PIN["D10"], (9, -2.6), (C_IN, -2.6), (C_IN, -1.2), hole(C_IN, "j")], "#ff7f0e")
ax.text(9.5, -2.25, "D10 → column 2", fontsize=9, color="#b35900")
# bottom-half column 2 joined to the top half with a short jumper across the gap
wire([hole(C_IN, "f"), hole(C_IN, "e")], "#ff7f0e", lw=3)

# resistor 330 Ω: column 2 → base column 6
resistor(C_IN, C_B, "c", ["#ff7f0e", "#ff7f0e", "#8b4513"], "330 Ω")

# transistor PN2222A, legs in row e, columns 5 6 7
for c, lab in [(C_E, "E"), (C_B, "B"), (C_C, "C")]:
    ax.plot([c, c], [Y["e"], Y["e"] - 0.9], color="#999999", lw=2, zorder=6)
    ax.text(c, Y["e"] - 1.35, lab, ha="center", fontsize=11, fontweight="bold", zorder=9)
ax.add_patch(Wedge((C_B, Y["e"] - 0.9), 1.25, 180, 360, fc="#222222", ec="black", zorder=7))
ax.plot([C_B - 1.25, C_B + 1.25], [Y["e"] - 0.9] * 2, color="#dddddd", lw=2, zorder=8)
ax.text(C_C + 1.6, 4.95, "PN2222A", fontsize=9, va="center", color="#333333", zorder=9)
# emitter → GND rail
wire([hole(C_E, "a"), (C_E, Y_MINUS)], "#222222")

# diode 1N4007 across the coil: anode column 7 (collector), cathode (stripe) column 11 (5V)
y = Y["b"]
ax.plot([C_C, C_5V], [y, y], color="#999999", lw=2, zorder=6)
ax.add_patch(Rectangle((C_C + 1.2, y - 0.3), C_5V - C_C - 2.4, 0.6, fc="#222222", ec="black", zorder=7))
ax.add_patch(Rectangle((C_5V - 1.55, y - 0.3), 0.3, 0.6, fc="#cccccc", ec="none", zorder=8))
ax.text((C_C + C_5V) / 2, y + 0.55, "1N4007 (stripe →)", ha="center", fontsize=9,
        fontweight="bold", color="#7a0000", zorder=9)

# column 11 → 5V rail
wire([hole(C_5V, "a"), (C_5V, Y_PLUS)], "#d62728")

# --- relay (off the board: its pins don't fit the breadboard grid) ----------------------
RX, RY = 33.5, 2.0
ax.add_patch(FancyBboxPatch((RX, RY), 5.5, 8.5, boxstyle="round,pad=0.2", fc="#1d4fd8", ec="#0b2a80", lw=2))
ax.text(RX + 2.75, RY + 7.8, "RELAY\nSRD-05VDC", color="white", ha="center", va="center",
        fontsize=11, fontweight="bold")
ax.text(RX + 2.75, RY + 6.9, "(pin names printed on top)", color="white", ha="center", fontsize=8)
RP = {"COIL 1": (RX, RY + 6.0), "COIL 2": (RX, RY + 5.0), "COM": (RX, RY + 4.0),
      "NO": (RX, RY + 3.0), "NC": (RX, RY + 2.0)}
for name, (x, yy) in RP.items():
    ax.add_patch(Circle((x, yy), 0.22, fc="#cccccc", ec="black", zorder=6))
    ax.text(x + 0.45, yy, name + ("  (empty)" if name == "NC" else ""), color="white", va="center",
            fontsize=10, fontweight="bold", zorder=6)

# collector (column 7) → COIL 1 ; column 11 (5V) → COIL 2
wire([hole(C_C, "a"), (C_C, 11.0), (31.8, 11.0), (31.8, RP["COIL 1"][1]), RP["COIL 1"]], "#2ca02c")
wire([hole(C_5V, "c"), (12.5, Y["c"]), (12.5, 10.5), (31.2, 10.5), (31.2, RP["COIL 2"][1]), RP["COIL 2"]],
     "#9467bd")

# --- pretend pump: 5V → COM, NO → 220 Ω → LED → GND --------------------------------------
wire([(29, Y_PLUS), (29, 12.2), (32.4, 12.2), (32.4, RP["COM"][1]), RP["COM"]], "#d62728")
wire([RP["NO"], (30.6, RP["NO"][1]), (30.6, Y["g"]), hole(C_PUMP_IN, "g")], "#e6c200")
resistor(C_PUMP_IN, C_LED_A, "i", ["#d62728", "#d62728", "#8b4513"], "220 Ω")
ax.plot([C_LED_A, C_LED_A], [Y["h"], Y["f"] - 0.2], color="#999999", lw=2, zorder=6)
ax.plot([C_LED_K, C_LED_K], [Y["h"], Y["f"] - 0.2], color="#999999", lw=2, zorder=6)
ax.add_patch(Circle((C_LED_A + 0.5, Y["f"] - 0.1), 0.55, fc="#9ecae1", ec="black", zorder=7))
ax.text(C_LED_A + 0.5, 4.95, "spare LED (pretend pump): long leg col 22", ha="center", va="center",
        fontsize=9, zorder=9)
wire([hole(C_LED_K, "j"), (C_LED_K, -0.6), (27, -0.6), (27, Y_MINUS)], "#222222")

ax.text(14.5, -3.4, "CHECKLIST\n"
        "1. PN2222A: flat side with the writing faces YOU (legs E, B, C left to right).\n"
        "2. 1N4007 diode: grey stripe on the 5V side (column 11). Backwards = short circuit.\n"
        "3. Relay pins: connect with M-F jumper wires (or solder short wires on). NC stays empty.\n"
        "4. The spare LED is optional: without it, just listen for the relay CLICK.\n"
        "5. Later the 12 V pump goes on COM → NO instead, on its own 12 V adapter (never mains).",
        fontsize=10, color="#333333", va="top", linespacing=1.6)

ax.set_xlim(-1.5, 41)
ax.set_ylim(-10.2, 14.2)
ax.set_title("Stage 2: bare relay on D10 (PN2222A + 1N4007)", fontsize=15, fontweight="bold")
fig.savefig(OUT, dpi=140, bbox_inches="tight", facecolor="white")
print("wrote", OUT)
