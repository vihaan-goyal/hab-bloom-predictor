"""
draw_schematic.py -- wiring schematic for the Uno alerter (hardware/alerter_uno)
==============================================================================
Draws the circuit for the parts actually on hand (green/blue/white LEDs, passive buzzer,
bare 5-pin relay with 1N4007 flyback diode, DS18B20) with the pins used in alerter_uno.ino.

Run from repo root (needs `pip install schemdraw`):
    python hardware/alerter_uno/draw_schematic.py
Writes hardware/alerter_uno/schematic.png
"""
import os

import matplotlib
matplotlib.use("Agg")
import schemdraw
import schemdraw.elements as elm

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schematic.png")


def pin(d, xy, name):
    d.add(elm.Dot(open=True).at(xy).label(name, loc="left", fontsize=13))


def title(d, xy, text):
    d.add(elm.Label().at(xy).label(text, fontsize=13, halign="left", color="#1f4e79"))


with schemdraw.Drawing(file=OUT, show=False, dpi=160) as d:
    d.config(fontsize=11, unit=2.5)

    # --- 1. Status LEDs -------------------------------------------------------------
    title(d, (0, 1.6), "1. Status LEDs (stage 1)")
    for y, p, r, colour, role in [(0, "D6", "330 Ω", "green", "idle"),
                                  (-2, "D5", "100-220 Ω", "blue", "treatment ON"),
                                  (-4, "D9", "220 Ω", "white", "warning")]:
        pin(d, (0, y), p)
        d.add(elm.Resistor().right().at((0, y)).label(r))
        d.add(elm.LED().right().label(f"{colour} LED\n{role}", loc="bottom"))
        d.add(elm.Line().right(0.6))
        d.add(elm.Ground())

    # --- 2. Passive buzzer ------------------------------------------------------------
    title(d, (0, -6.4), "2. Passive buzzer (stage 1)")
    pin(d, (0, -12), "D2")
    rb = d.add(elm.Resistor().right().at((0, -12)).label("330 Ω–1 kΩ"))
    q1 = d.add(elm.BjtNpn(circle=True).anchor("base").at(rb.end).label("NPN\nPN2222", loc="right"))
    d.add(elm.Ground().at(q1.emitter))
    d.add(elm.Line().up(0.4).at(q1.collector))
    d.add(elm.RBox().up().label("passive buzzer\n(+ leg to 5V)", loc="bottom", ofst=0.4))
    d.add(elm.Vdd().label("5V"))

    # --- 3. Bare relay + pump ---------------------------------------------------------
    title(d, (0, -15.4), "3. Bare 5-pin relay → 12 V pump (stage 2)")
    pin(d, (0, -22), "D10")
    rr = d.add(elm.Resistor().right().at((0, -22)).label("330 Ω–1 kΩ"))
    q2 = d.add(elm.BjtNpn(circle=True).anchor("base").at(rr.end).label("NPN\nPN2222", loc="right"))
    d.add(elm.Ground().at(q2.emitter))
    d.add(elm.Line().up(0.8).at(q2.collector))
    coil = d.add(elm.Inductor2(loops=3).up())
    d.add(elm.Label().at((coil.center[0] - 0.5, coil.center[1])).label("relay coil\n(2 coil pins)", halign="right"))
    d.add(elm.Vdd().label("5V"))
    # flyback diode across the coil, cathode (stripe) to the 5V side
    d.add(elm.Line().right(2.2).at(coil.start))
    d.add(elm.Diode().up().toy(coil.end[1]).label("1N4007\nstripe → 5V", loc="bottom", ofst=0.3))
    d.add(elm.Line().left(2.2))
    # contacts on a separate 12 V loop
    x0 = q2.collector[0] + 5.5
    src = d.add(elm.SourceV().up().at((x0, -22.6)).label("12 V\nadapter", loc="left"))
    d.add(elm.Line().right(0.8))
    d.add(elm.Switch().right().label("relay COM → NO", loc="top"))
    d.add(elm.Motor().down().label("air pump", loc="right"))
    d.add(elm.Line().left().tox(src.start[0]))

    # --- 4. DS18B20 temperature probe ------------------------------------------------
    title(d, (0, -26.4), "4. DS18B20 waterproof probe (stage 3)")
    y = -31
    pin(d, (0, y), "D3")
    d.add(elm.Line().at((0, y)).right(7))
    d.add(elm.Dot(open=True).label("yellow wire (DQ)", loc="right"))
    d.add(elm.Dot().at((2.5, y)))
    d.add(elm.Resistor().up().at((2.5, y)).label("4.7 kΩ (or 2 × 10 kΩ\nside by side)", loc="bottom", ofst=0.2))
    d.add(elm.Vdd().label("5V"))
    d.add(elm.Dot(open=True).at((7, y + 2.2)).label("red wire → 5V", loc="right"))
    d.add(elm.Line().at((7, y + 2.2)).left(1))
    d.add(elm.Vdd().label("5V"))
    d.add(elm.Dot(open=True).at((7, y - 1.6)).label("black wire → GND", loc="right"))
    d.add(elm.Line().at((7, y - 1.6)).left(1))
    d.add(elm.Ground())
    d.add(elm.Label().at((7.3, y - 2.6)).label("(the 3 wires of the DS18B20 probe)", fontsize=10, halign="left", color="#555555"))

    d.add(elm.Label().at((0, -36.5)).label(
        "All GNDs connect to the Uno GND; all 5V to the Uno 5V.  The 12 V pump loop is separate: never mains on the breadboard.",
        fontsize=10, halign="left", color="#555555"))
print("wrote", OUT)
