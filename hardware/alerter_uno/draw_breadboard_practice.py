"""
draw_breadboard_practice.py -- Fritzing / circuito.io style breadboard picture: alerter + NEW practice light sensor
=================================================================================================================
Builds breadboard_practice.svg / .png in the same style as draw_breadboard_fritzing.py (stage 2), from real
Fritzing part art (CC-BY-SA, fritzing-parts repo, branch `develop`). The stage 1 + stage 2 alerter is drawn
exactly as in breadboard_stage2.png (same part and wire positions); only its "NEW" highlight is dropped.

Run (base env):
    ~/anaconda3/python.exe hardware/alerter_uno/draw_breadboard_practice.py

Practice light sensor (pins match fluoro_practice/fluoro_practice.ino):
  D7 -> blue LED long leg (anode, f22); short leg (cathode, e22) -> 220 ohm (d22-d26) -> GND rail
  +5V rail -> photoresistor (f28 / e28) -> node (bottom col 28) -> A1, and node -10k (b28-b24)-> GND rail
  (the Uno's analog header is missing: the A1 jumper is held pressed into the bare A1 hole)
  The LED and the photoresistor both straddle the centre channel and face each other along it;
  the clear cup of water sits in the channel between them.
Units inside the SVG: 1 unit = 1/90 inch (breadboard hole pitch = 9 units).
"""
import math
import os
import re
import subprocess
import sys
import urllib.request

from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
PARTS = os.path.join(HERE, "fritzing_parts")
OUT_SVG = os.path.join(HERE, "breadboard_practice.svg")
OUT_PNG = os.path.join(HERE, "breadboard_practice.png")
RAW = "https://raw.githubusercontent.com/fritzing/fritzing-parts/develop/svg/core/breadboard/"
FILES = {
    "bb": "Half_breadboard56a.svg",
    "uno": "arduino_Uno_Rev3_breadboard.svg",
    "led": "LED-5mm-red-leg.svg",
    "res": "resistor_220.svg",
    "npn": "transistor_npn.svg",
    "diode": "diode.svg",
    "buzzer": "sparkfun-electromechanical_buzzer-12mm-ns_breadboard.svg",
    "relay": "sparkfun-electromechanical_relay-jzc_breadboard.svg",
    "ldr": "ldr.svg",
}
SVGNS = "http://www.w3.org/2000/svg"
UPI = 90.0                      # global units per inch
PNG_W = 1600
CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"
NUM = r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?"


# ---------------------------------------------------------------- affine helpers
def mul(A, B):      # A o B  (apply B first)
    a, b, c, d, e, f = A
    g, h, i, j, k, l = B
    return (a * g + c * h, b * g + d * h, a * i + c * j, b * i + d * j, a * k + c * l + e, b * k + d * l + f)


def T(x, y):
    return (1, 0, 0, 1, x, y)


def S(sx, sy=None):
    return (sx, 0, 0, sx if sy is None else sy, 0, 0)


def R(deg):
    r = math.radians(deg)
    return (math.cos(r), math.sin(r), -math.sin(r), math.cos(r), 0, 0)


def ap(M, p):
    a, b, c, d, e, f = M
    return (a * p[0] + c * p[1] + e, b * p[0] + d * p[1] + f)


def parse_tf(s):
    M = (1, 0, 0, 1, 0, 0)
    for name, args in re.findall(r"(\w+)\s*\(([^)]*)\)", s or ""):
        v = [float(x) for x in re.findall(NUM, args)]
        if name == "translate":
            m = T(v[0], v[1] if len(v) > 1 else 0)
        elif name == "scale":
            m = S(v[0], v[1] if len(v) > 1 else v[0])
        elif name == "rotate":
            m = R(v[0])
            if len(v) == 3:
                m = mul(T(v[1], v[2]), mul(m, T(-v[1], -v[2])))
        elif name == "matrix":
            m = tuple(v)
        else:
            continue
        M = mul(M, m)
    return M


def fmt(M):
    return "matrix(%s)" % ",".join("%.5f" % v for v in M)


# ---------------------------------------------------------------- part loading
def fetch(fname):
    path = os.path.join(PARTS, fname)
    if not os.path.exists(path):
        os.makedirs(PARTS, exist_ok=True)
        urllib.request.urlretrieve(RAW + urllib.request.quote(fname), path)
    return path


class Part:
    def __init__(self, key, viewbox=None):
        self.tree = etree.parse(fetch(FILES[key]))
        self.root = self.tree.getroot()
        vb = [float(v) for v in re.findall(NUM, self.root.get("viewBox"))]
        w, h = self.root.get("width"), self.root.get("height")
        wu = self._len(w)
        self.vb_full = vb
        self.k = wu / vb[2]                      # global units per viewBox unit
        self.vb = viewbox or vb

    @staticmethod
    def _len(s):
        v = float(re.findall(NUM, s)[0])
        return v * UPI if s.strip().endswith("in") else v   # unitless/px only for the 90-dpi breadboard

    def el(self, id_):
        r = self.root.xpath('//*[@id="%s"]' % id_)
        return r[0] if r else None

    def remove(self, pred):
        for e in list(self.root.iter()):
            if e.getparent() is not None and pred(e):
                e.getparent().remove(e)

    def recolor(self, old, new):
        for e in self.root.iter():
            for att in ("fill", "stroke"):
                if (e.get(att) or "").lower() == old.lower():
                    e.set(att, new)

    def local(self, e):
        """element anchor in viewBox coords (all ancestor transforms applied)"""
        M = (1, 0, 0, 1, 0, 0)
        chain = [e] + list(e.iterancestors())
        for a in reversed(chain):
            if a.get("transform"):
                M = mul(M, parse_tf(a.get("transform")))
        tag = etree.QName(e).localname
        g = lambda k: float(e.get(k, 0))
        if tag == "rect":
            p = (g("x") + g("width") / 2, g("y") + g("height") / 2)
        elif tag in ("circle", "ellipse"):
            p = (g("cx"), g("cy"))
        elif tag == "line":
            p = (g("x1"), g("y1"))
        else:
            raise ValueError(tag)
        return ap(M, p)

    def base(self):
        """viewBox -> global units (before placement)"""
        return mul(S(self.k), T(-self.vb[0], -self.vb[1]))

    def render(self, M, clip=False):
        inner = "".join(etree.tostring(c, encoding="unicode") for c in self.root
                        if isinstance(c.tag, str) and etree.QName(c).localname not in ("desc", "title", "metadata"))
        inner = re.sub(r'\s(id|gorn)="[^"]*"', "", inner)
        inner = inner.replace('xmlns="%s"' % SVGNS, "").replace('xmlns:svg="%s"' % SVGNS, "")
        return '<g transform="%s">%s</g>\n' % (fmt(mul(M, self.base())), inner)


def fixed_place(M_place, part, anchor_vb, target):
    """shift M_place so that part-local anchor lands on target"""
    p = ap(mul(M_place, part.base()), anchor_vb)
    return mul(T(target[0] - p[0], target[1] - p[1]), M_place)


def two_pin_place(part, a_vb, b_vb, pa, pb):
    """similarity transform taking anchors a,b (viewBox) onto global points pa,pb"""
    B = part.base()
    qa, qb = ap(B, a_vb), ap(B, b_vb)
    ang = math.atan2(pb[1] - pa[1], pb[0] - pa[0]) - math.atan2(qb[1] - qa[1], qb[0] - qa[0])
    sc = math.dist(pa, pb) / math.dist(qa, qb)
    M = mul(R(math.degrees(ang)), S(sc))
    q = ap(M, qa)
    return mul(T(pa[0] - q[0], pa[1] - q[1]), M)


# ---------------------------------------------------------------- scene
out = []          # svg fragments in paint order
labels = []       # drawn last


def add(s):
    out.append(s)


def text(x, y, s, size=5.2, color="#222", anchor="middle", weight="normal", layer=None, **kw):
    extra = "".join(' %s="%s"' % (k.replace("_", "-"), v) for k, v in kw.items())
    light = color.lower() in ("#fff", "#ffffff") or color.lower()[1] in "de"
    halo = "" if light else ' stroke="#fff" stroke-width="1.1" stroke-linejoin="round" paint-order="stroke"'
    frag = ('<text x="%.2f" y="%.2f" font-family="Arial, Helvetica, sans-serif" font-size="%.2f" fill="%s" '
            'text-anchor="%s" font-weight="%s"%s%s>%s</text>\n' % (x, y, size, color, anchor, weight, extra, halo, s))
    (layer if layer is not None else labels).append(frag)


def tag(x, y, s, bg, fg="#fff", size=4.6, layer=None):
    w = 0.58 * size * len(s) + 3.2
    frag = ('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="1.6" fill="%s" stroke="#fff" stroke-width="0.6"/>\n'
            % (x - w / 2, y - size * 0.82, w, size * 1.2, bg))
    (layer if layer is not None else labels).append(frag)
    text(x, y + size * 0.1, s, size, fg, weight="bold", layer=layer)


def shade(hexcol, f):
    h = hexcol.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(v * f))) for v in (r, g, b))


def rounded(points, r=3.5):
    d = "M%.2f,%.2f" % points[0]
    for i in range(1, len(points) - 1):
        p0, p1, p2 = points[i - 1], points[i], points[i + 1]
        l1, l2 = math.dist(p0, p1), math.dist(p1, p2)
        rr = min(r, l1 / 2, l2 / 2)
        a = (p1[0] + (p0[0] - p1[0]) * rr / l1, p1[1] + (p0[1] - p1[1]) * rr / l1)
        b = (p1[0] + (p2[0] - p1[0]) * rr / l2, p1[1] + (p2[1] - p1[1]) * rr / l2)
        d += " L%.2f,%.2f Q%.2f,%.2f %.2f,%.2f" % (a + p1 + b)
    d += " L%.2f,%.2f" % points[-1]
    return d


WIRES = []


def wire(points, color):
    d = rounded(points)
    s = ('<path d="%s" fill="none" stroke="%s" stroke-width="4.4" stroke-linecap="round" stroke-linejoin="round"/>'
         '<path d="%s" fill="none" stroke="%s" stroke-width="3.0" stroke-linecap="round" stroke-linejoin="round"/>'
         '<path d="%s" fill="none" stroke="#fff" stroke-opacity="0.28" stroke-width="0.8" stroke-linecap="round" '
         'stroke-linejoin="round" transform="translate(-0.5,-0.5)"/>\n' % (d, shade(color, 0.55), d, color, d))
    for p in (points[0], points[-1]):
        s += ('<circle cx="%.2f" cy="%.2f" r="2.3" fill="%s" stroke="%s" stroke-width="0.6"/>'
              '<circle cx="%.2f" cy="%.2f" r="0.9" fill="#222"/>\n' % (p[0], p[1], shade(color, 0.8), shade(color, 0.45), p[0], p[1]))
    WIRES.append(s)


LEG = '<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="#8C8C8C" stroke-width="2.4" stroke-linecap="round"/>\n'

# ---------------- breadboard (at origin)
bb = Part("bb")
bb.remove(lambda e: etree.QName(e).localname == "text")
HOLE, RAIL = {}, {}
for e in bb.root.iter("{%s}g" % SVGNS):
    m = re.fullmatch(r"pin(\d+)([A-Z])", e.get("id") or "")
    if m:
        c = e.find("{%s}circle" % SVGNS)
        p = ap(bb.base(), bb.local(c))
        if m.group(2) in "WXYZ":
            RAIL.setdefault(m.group(2), []).append(p)
        else:
            HOLE[(int(m.group(1)), m.group(2))] = p
BBW, BBH = bb.vb[2] * bb.k, bb.vb[3] * bb.k


def H(col, row):
    return HOLE[(col, row.upper())]


def X(col):
    return H(col, "A")[0]


def rail(r, x):     # nearest rail hole to x on rail r (Z/Y top -,+ ; X/W bottom -,+)
    return min(RAIL[r], key=lambda p: abs(p[0] - x))


add(bb.render(T(0, 0)))
# upright row letters / column numbers (Fritzing's are rotated)
for i, r in enumerate("JIHGFEDCBA"):
    y = H(1, r)[1] + 1.9
    text(6.5, y, r.lower(), 5.0, "#8a8686", layer=out)
    text(BBW - 6.2, y, r.lower(), 5.0, "#8a8686", layer=out)
for c in (1, 5, 10, 15, 20, 25, 30):
    text(X(c), 38.4 - 0.5, str(c), 4.6, "#8a8686", layer=out)
    text(X(c), 155.5, str(c), 4.6, "#8a8686", layer=out)
text(BBW + 3.5, 11, "\u2212", 7, "#2257c9", "start", "bold", layer=out)
text(BBW + 3.5, 20.5, "+", 7, "#d42020", "start", "bold", layer=out)
text(BBW + 3.5, 173.5, "\u2212", 7, "#2257c9", "start", "bold", layer=out)
text(BBW + 3.5, 182.5, "+", 7, "#d42020", "start", "bold", layer=out)

# ---------------- NEW highlight (under parts): inserted here once the practice parts are placed
HL_AT = len(out)

# ---------------- Arduino Uno below the board
UX, UY = -118, 234
uno = Part("uno")
M_uno = T(UX, UY)
add(uno.render(M_uno))
UNO = {name: ap(mul(M_uno, uno.base()), uno.local(uno.el(cid + "pin")))
       for name, cid in [("D2", "connector63"), ("D5", "connector66"), ("D6", "connector67"), ("D9", "connector52"),
                         ("D10", "connector53"), ("5V", "connector87"), ("GND", "connector88"), ("GNDtop", "connector57"),
                         ("D7", "connector68"), ("A1", "connector1")]}
UNO_W, UNO_H = uno.vb[2] * uno.k, uno.vb[3] * uno.k


# ---------------- parts
def led(cath_col, row, color, mirror=False):
    p = Part("led")
    p.remove(lambda e: (e.get("id") or "").endswith("leg"))
    p.recolor("#E60000", color)
    if color == "#FFFFFF":      # white LED: pale lens with a visible edge
        p.recolor("#FFFFFF", "#FFFFFF")
        for e in p.root.iter():
            if (e.get("id") or "") == "color_path32":
                e.set("fill", "#F4F4F4"); e.set("opacity", "0.9"); e.set("stroke", "#A8A8A8"); e.set("stroke-width", "0.8")
    anchor = (6.287, 40.565) if not mirror else (16.29, 40.565)      # cathode leg bottom
    M0 = S(-1, 1) if mirror else T(0, 0)
    M = fixed_place(M0, p, anchor, H(cath_col, row))
    add(p.render(M))
    return ap(mul(M, p.base()), (9.84, 0))                            # lens top


def resistor(pa, pb, bands):
    p = Part("res")
    p.remove(lambda e: etree.QName(e).localname == "use")
    for bid, col in zip(("band_1_st", "band_2_nd", "band_rd_multiplier"), bands):
        p.el(bid).set("fill", col)
    add(p.render(two_pin_place(p, (1.455, 5.045), (41.462, 5.045), pa, pb)))


def npn(e_col, row, name):
    p = Part("npn")
    p.remove(lambda e: (e.get("id") or "").endswith("leg"))
    M = fixed_place(T(0, 0), p, (1.08, 24.081), H(e_col, row))
    add(p.render(M))
    g = lambda q: ap(mul(M, p.base()), q)
    for q, s in (((1.9, 17.6), "E"), ((8.26, 17.6), "B"), ((14.6, 17.6), "C")):
        x, y = g(q)
        text(x, y + 1.6, s, 4.6, "#ffffff", weight="bold")
    x, y = g((8.26, 0))
    return x, y


RED, ORANGE, BROWN = "#C40808", "#E8750A", "#8A3D06"
R220, R330 = (RED, RED, BROWN), (ORANGE, ORANGE, BROWN)

# stage 1 (top half: parts in row j, resistors bridge the centre channel d -> f)
LEDS1 = [(3, "#FFFFFF", R220, "D9", "WHITE", "220 \u03a9"), (7, "#22C422", R330, "D6", "GREEN", "330 \u03a9"),
         (11, "#1E6EFF", R220, "D5", "BLUE", "220 \u03a9")]
for k, col, rb, pin, nm, rv in LEDS1:
    top = led(k, "J", col)
    resistor(H(k + 1, "D"), H(k + 1, "F"), rb)
    text(top[0], -3.5, "%s (%s)" % (nm, pin), 4.6, "#333", weight="bold")
    text(X(k + 1) + 5.8, 100.5, rv, 3.9, "#444", "start")
q1 = npn(14, "J", "Q1")
resistor(H(15, "D"), H(15, "F"), R330)
text(X(15) + 5.8, 100.5, "330 \u03a9", 3.9, "#444", "start")

# buzzer (12 mm, legs 0.3 in apart): (-) at j18, (+) at j21
bz = Part("buzzer", viewbox=[95, 142, 475, 718])
bz.remove(lambda e: (e.get("fill") or "").upper() == "#1F7A34")
bz.remove(lambda e: etree.QName(e).localname == "g" and (e.get("transform") or "").startswith("translate(316.319"))
bz_cx = (X(18) + X(21)) / 2
bz_bottom = H(18, "J")[1] - 7.5
bzw, bzh = bz.vb[2] * bz.k, bz.vb[3] * bz.k
M_bz = T(bz_cx - bzw / 2, bz_bottom - bzh)
for c in (18, 21):
    add(LEG % (X(c), bz_bottom - 3, X(c), H(c, "J")[1]))
add(bz.render(M_bz))
text(bz_cx - 11.5, bz_bottom - bzh + 21.5, "\u2212", 7, "#fff", weight="bold")
text(bz_cx + 11.5, bz_bottom - bzh + 21.5, "+", 7, "#fff", weight="bold")
text(bz_cx, bz_bottom - bzh - 3, "BUZZER (passive)", 4.6, "#333", weight="bold")

# stage 2 (bottom half: parts in row e, bodies over the centre channel)
q2 = npn(19, "E", "Q2")
resistor(H(16, "B"), H(20, "B"), R330)
dio = Part("diode")
add(dio.render(two_pin_place(dio, (0.52, 3.63), (29.36, 3.63), H(17, "D"), H(21, "D"))))   # cathode(stripe)=d17
resistor(H(25, "C"), H(29, "C"), R220)
ptop = led(30, "E", "#E60000", mirror=True)          # anode e29 (bent/long leg), cathode e30

# relay (bare 5-pin, blue cube), off-board below the right half, 3-pin end up
rl = Part("relay")
rl.remove(lambda e: (e.get("fill") or "").upper() in ("#1F7A34", "#808080"))
rl.recolor("#333333", "#2F6FD3")
rl.recolor("#1A1A1A", "#1F55AE")
RW, RH = rl.vb[2] * rl.k, rl.vb[3] * rl.k
pads = {}
M_rl0 = mul(T(RW, RH), R(180))
for i in range(5):
    pads[i] = ap(mul(M_rl0, rl.base()), rl.local(rl.el("connector%dpin" % i)))
top_pads = sorted([p for p in pads.values() if p[1] < RH / 2], key=lambda p: p[0])
bot_pads = sorted([p for p in pads.values() if p[1] > RH / 2], key=lambda p: p[0])
RX = X(21) - top_pads[0][0]
RY = 226
M_rl = mul(T(RX, RY), M_rl0)
top_pads = [(RX + x, RY + y) for x, y in top_pads]
bot_pads = [(RX + x, RY + y) for x, y in bot_pads]
for x, y in top_pads:
    add(LEG % (x, y, x, RY + 11))
for x, y in bot_pads:
    add(LEG % (x, y, x, RY + RH - 11))
add(rl.render(M_rl))
COIL1, COM, COIL2 = top_pads
NC, NO = bot_pads
text(RX + RW / 2, RY + 42, "RELAY", 6.2, "#fff", weight="bold")
text(RX + RW / 2, RY + 48, "SRD-05VDC", 4.3, "#e8f0ff")
text(RX + RW / 2, RY + 54, "-SL-C", 4.3, "#e8f0ff")


# ---------------------------------------------------------------- wires
C = dict(red="#E0231C", black="#2B2B2B", D9="#F2C200", D6="#1FA84F", D5="#1E6EE8", D2="#F07A12", D10="#8E3FC0",
         brown="#8B5A2B", coil="#E83E8C", no="#10A5B5")

# power: Uno 5V/GND -> top rails, looping round the left of the Uno
v5, g0 = UNO["5V"], UNO["GND"]
yp, zp = rail("Y", 17), rail("Z", 17)
wire([v5, (v5[0], UY + UNO_H + 9), (UX - 16, UY + UNO_H + 9), (UX - 16, yp[1]), yp], C["red"])
wire([g0, (g0[0], UY + UNO_H + 18), (UX - 26, UY + UNO_H + 18), (UX - 26, zp[1]), zp], C["black"])

# stage 1 signal wires: Uno -> bottom-half end of each centre-channel resistor (row a)
JOG = {"D9": 205, "D6": 205, "D5": 213, "D2": 221}
for pin, col in (("D9", 4), ("D6", 8), ("D5", 12), ("D2", 15)):
    p, t = UNO[pin], H(col, "A")
    wire([p, (p[0], JOG[pin]), (t[0], JOG[pin]), t], C[pin])

# stage 1 GND / 5V links
def to_z(start_col, via_col, zx):
    s = H(start_col, "I")
    z = rail("Z", zx)
    wire([s, (X(via_col), s[1]), (X(via_col), 14), z], C["black"])


to_z(3, 2, X(2) + 3.35)            # white LED cathode
to_z(7, 6, X(6) - 5.65)            # green LED cathode
to_z(11, 10, X(10) + 3.35)         # blue LED cathode
to_z(14, 13, X(13) + 3.35)         # Q1 emitter
wire([H(16, "H"), H(18, "H")], C["brown"])                                  # Q1 collector -> buzzer (-)
yb = rail("Y", X(23) + 3.35)
wire([H(21, "I"), (X(23), H(21, "I")[1]), (X(23), 26), yb], C["red"])       # buzzer (+) -> 5V

# stage 2 wires
d10 = UNO["D10"]
wire([d10, (d10[0], 229), (X(16), 229), H(16, "A")], C["D10"])
gt = UNO["GNDtop"]
xg = rail("X", 17)
wire([gt, (gt[0], 200), (xg[0], 200), xg], C["black"])                     # Uno GND -> bottom (-) rail
yr, wr = rail("Y", X(30)), rail("W", X(30))
wire([yr, (BBW + 10, yr[1]), (BBW + 10, wr[1]), wr], C["red"])              # top (+) -> bottom (+)
w17 = rail("W", X(17) + 3.35)
wire([H(17, "A"), (X(17), 160), (w17[0], 166), w17], C["red"])              # diode stripe node -> 5V
x19 = rail("X", X(19) + 3.35)
wire([H(19, "A"), (X(19), 158), x19], C["black"])                          # Q2 emitter -> GND
x30 = rail("X", X(30) - 5.65)
wire([H(30, "A"), (X(30), 158), x30], C["black"])                          # pump LED cathode -> GND
wire([COIL1, H(21, "A")], C["coil"])                                        # relay COIL 1 -> collector
wcom = rail("W", COM[0] + 3.35)
wire([COM, (COM[0], 196), (wcom[0], 190), wcom], C["red"])                   # COM -> 5V
wc2 = rail("W", COIL2[0] + 3.35)
wire([COIL2, (COIL2[0], 196), (wc2[0], 190), wc2], C["red"])                 # COIL 2 -> 5V
wire([NO, (NO[0], RY + RH + 9), (RX + RW + 8, RY + RH + 9), (RX + RW + 8, 200), (X(25), 200), H(25, "A")], C["no"])

# ---------------------------------------------------------------- NEW: practice light sensor
BLACK = "#1A1A1A"
R10K = (BROWN, BLACK, ORANGE)                        # brown-black-orange = 10 kOhm
C.update(D7="#35B5EE", A1="#9CCB19")
CHAN_Y = (H(22, "E")[1] + H(22, "F")[1]) / 2         # centre line of the breadboard's middle channel
GLOW = []                                            # yellow glow painted under the new wires


def new_wire(points, color):
    GLOW.append('<path d="%s" fill="none" stroke="#ffd83a" stroke-opacity="0.55" stroke-width="10" '
                'stroke-linecap="round" stroke-linejoin="round"/>\n' % rounded(points))
    wire(points, color)


# 1. blue LED lying in the channel, pointing right at the photoresistor; legs straddle the channel:
#    anode (long leg) in f22 (top half), cathode (short leg) in e22 (bottom half)
bl = Part("led")
bl.remove(lambda e: (e.get("id") or "").endswith("leg") or (e.get("fill") or "").upper() == "#8C8C8C")
bl.recolor("#E60000", "#1E6EFF")
FLANGE = (9.844, 32.6)                               # lens-base centre in the LED art
M_bl = fixed_place(mul(S(1, -1), R(90)), bl, FLANGE, (X(22) + 4.5, CHAN_Y))   # lens -> +x, anode on top
g_bl = lambda q: ap(mul(M_bl, bl.base()), q)
an_base, ca_base = g_bl((16.29, 32.6)), g_bl((6.287, 32.6))
for base_pt, hole in ((an_base, H(22, "F")), (ca_base, H(22, "E"))):
    add('<path d="M%.2f,%.2f L%.2f,%.2f L%.2f,%.2f" fill="none" stroke="#8C8C8C" stroke-width="2.4" '
        'stroke-linecap="round" stroke-linejoin="round"/>\n' % (base_pt + (hole[0], base_pt[1]) + hole))
LENS_TIP = g_bl((9.844, 0))

# 2. photoresistor straddling the channel at column 28, face towards the LED:
#    f28 (top half) -> +5V ; e28 (bottom half) = sensor node -> A1, and -> 10k -> GND
ldr = Part("ldr")
ldr.remove(lambda e: (e.get("id") or "").endswith("leg"))
M_ldr = two_pin_place(ldr, (0.784, 4.784), (22.385, 4.784), H(28, "E"), H(28, "F"))
LDR_LEFT = min(ap(mul(M_ldr, ldr.base()), q)[0] for q in ((4.864, 0), (4.864, 10.932), (19.466, 0), (19.466, 10.932)))

# 3. the cup of water (side view) in the channel between the LED and the photoresistor
cx0, cx1 = LENS_TIP[0] + 1.6, LDR_LEFT - 1.6
cy0, cy1 = CHAN_Y - 11.5, CHAN_Y + 11.5
add('<path d="M%.2f,%.2f L%.2f,%.2f L%.2f,%.2f L%.2f,%.2f Z" fill="#1E6EFF" fill-opacity="0.22"/>\n'
    % (LENS_TIP[0] - 1, CHAN_Y - 1.2, LDR_LEFT + 2, CHAN_Y - 4.5, LDR_LEFT + 2, CHAN_Y + 4.5, LENS_TIP[0] - 1, CHAN_Y + 1.2))
add('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="1.8" fill="#dff1ff" fill-opacity="0.85" '
    'stroke="#3d7fb3" stroke-width="0.9"/>\n' % (cx0, cy0, cx1 - cx0, cy1 - cy0))
add('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="1.2" fill="#9fd3ff" fill-opacity="0.75"/>\n'
    % (cx0 + 0.9, cy0 + 5, cx1 - cx0 - 1.8, cy1 - cy0 - 5.9))
add('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="#3d7fb3" stroke-width="0.6" stroke-dasharray="1.2,0.8"/>\n'
    % (cx0 + 0.9, cy0 + 5, cx1 - 0.9, cy0 + 5))
add(bl.render(M_bl))
add(ldr.render(M_ldr))

# 4. 220 ohm: LED cathode (short leg, bottom col 22) d22 -> d26, col 26 -> GND.  10k: node b28 -> b24, col 24 -> GND
resistor(H(22, "D"), H(26, "D"), R220)
resistor(H(24, "B"), H(28, "B"), R10K)

# ---- new wires
d7, a1 = UNO["D7"], UNO["A1"]
XL = (X(6) + X(7)) / 2                               # run between columns 6 and 7 (never over a hole)
YL = (H(7, "F")[1] + H(7, "G")[1]) / 2               # run between rows f and g
new_wire([d7, (d7[0], 215), (XL, 215), (XL, YL), (X(22), YL), H(22, "G")], C["D7"])   # D7 -> LED long leg (col 22 top)
ya = UY + UNO_H + 12
new_wire([a1, (a1[0], ya), (X(28), ya), H(28, "A")], C["A1"])                        # A1 <- sensor node
xg24, xg26 = min(RAIL["X"], key=lambda p: abs(p[0] - 215)), min(RAIL["X"], key=lambda p: abs(p[0] - 242))
new_wire([H(24, "A"), (X(24), 158), xg24], C["black"])                              # 10k -> GND
new_wire([H(26, "A"), (X(26), 158), xg26], C["black"])                              # 220 -> GND
new_wire([H(28, "H"), (X(28), 26), rail("Y", X(28) + 3.35)], C["red"])             # photoresistor -> +5V

# ---- NEW highlight boxes (under the parts): the LED / cup / photoresistor channel, the 220 ohm, the 10k
hl = [(X(21) + 4.5, YL + 1.5), (X(28) + 10, YL + 1.5), (X(28) + 10, H(1, "E")[1] + 3), (X(21) + 4.5, H(1, "E")[1] + 3)]
out.insert(HL_AT, '<path d="%s Z" fill="#ffe45c" fill-opacity="0.38" stroke="#e8a200" stroke-width="1.3" '
           'stroke-dasharray="4,2.5"/>\n' % rounded(hl, 4))
for c0, c1, row in ((24, 28, "B"), (22, 26, "D")):
    g = (X(c0) - 2.5, H(c0, row)[1] - 5.6, X(c1) - X(c0) + 5, 11.2)
    out.insert(HL_AT, '<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="4" fill="#ffe45c" fill-opacity="0.38" '
               'stroke="#e8a200" stroke-width="1.0" stroke-dasharray="4,2.5"/>\n' % g)
WIRES[:0] = GLOW

# ---------------------------------------------------------------- labels
for pin in ("D10", "D9", "D6", "D5", "D2"):
    p = UNO[pin]
    tag(p[0], UY + {"D10": 17, "D9": 25.5, "D6": 17, "D5": 25.5, "D2": 17}[pin], pin, C[pin])
tag(d7[0], UY + 25.5, "D7", C["D7"])
tag(gt[0], UY + 17, "GND", "#333")
tag(v5[0] - 2, UY + UNO_H - 14, "5V", C["red"])
tag(g0[0] + 5, UY + UNO_H - 14, "GND", "#333")
tag(a1[0] - 1, UY + UNO_H - 14, "A1", "#5f8a00")
tag(a1[0] + 37, ya + 10.5, "A1 (hold wire in hole)", "#5f8a00")

text(q1[0], q1[1] - 2.2, "PN2222A", 4.0, "#333", weight="bold")
text(X(19) - 4.8, CHAN_Y - 3, "PN2222A #2", 3.8, "#333", "end", weight="bold")
text(X(19), 125.5, "330 Ω", 3.9, "#444")
text(X(29) + 3.5, H(29, "C")[1] + 1.4, "220 Ω", 3.9, "#444", "start")
text(BBW + 16, 150, "red LED = pretend pump", 4.2, "#333", "start", weight="bold")
text(BBW + 16, 156, "(on relay NO)", 3.8, "#555", "start")
# relay pin names beside the relay
for nm, p in (("COIL1", COIL1), ("COM", COM), ("COIL2", COIL2)):
    text(p[0] + 1.3, RY + 13.5, nm, 3.5, "#fff", "end", "bold", transform="rotate(-90 %.2f %.2f)" % (p[0] + 1.3, RY + 13.5))
for nm, p in (("NC", NC), ("NO", NO)):
    text(p[0] + 1.3, RY + RH - 13, nm, 3.5, "#fff", "start", "bold", transform="rotate(-90 %.2f %.2f)" % (p[0] + 1.3, RY + RH - 13))
text(NC[0], RY + RH + 17, "NC: leave empty", 3.8, "#555", weight="bold")
text(RX + RW + 12, RY + RH + 2, "NO", 4, "#0b7c88", "start", weight="bold")
text(BBW + 16, 128, "5V jumper:", 4.2, "#b01010", "start", weight="bold")
text(BBW + 16, 133, "top + rail to", 4.2, "#b01010", "start")
text(BBW + 16, 138, "bottom + rail", 4.2, "#b01010", "start")
text(-6, 197, "GND jumper", 4.2, "#333", "end", weight="bold")

# practice-sensor labels
text(X(22) + 4.5, (H(1, "G")[1] + H(1, "H")[1]) / 2 + 1.4, "BLUE LED (D7)", 4.0, "#1a4fb8", "start", weight="bold")
text(X(22) + 4.5, YL + 1.2, "long leg (+) in f22", 3.4, "#333", "start")
text((cx0 + cx1) / 2, cy1 - 2.2, "cup", 3.3, "#12476f", weight="bold")
text(X(28) + 1, (H(1, "E")[1] + H(1, "D")[1]) / 2 + 1.7, "PHOTORESISTOR", 3.6, "#6a3b00", weight="bold")
text(X(24), (H(1, "C")[1] + H(1, "D")[1]) / 2 + 1.4, "220 Ω", 3.9, "#444")
text(X(24) - 3, (H(1, "B")[1] + H(1, "C")[1]) / 2 + 1.4, "10 kΩ", 3.9, "#444", "end")

text(BBW + 16, 62, "NEW (practice light sensor)", 7.0, "#b36b00", "start", "bold")
for i, s_ in enumerate(["A clear cup of water goes between the",
                        "blue LED and the photoresistor. The LED",
                        "shines THROUGH the water at the sensor.",
                        "Cover LED + cup + sensor with a box."]):
    text(BBW + 16, 71 + 6 * i, s_, 4.4, "#5a3d00", "start")
text(BBW + 16, 99, "D7 lights the LED; A1 reads the light (10k to GND).", 4.4, "#5a3d00", "start", weight="bold")

text(156, -55, "Practice light sensor: blue LED on D7 shines through a cup of water onto a photoresistor read on A1",
     8.2, "#111", weight="bold")
text(156, -44, "The stage 1 + stage 2 alerter is unchanged. The yellow boxes and yellow-glow wires are NEW.", 5.6, "#444")

NOTES = [
    ("CHECKLIST (practice sensor)", True),
    ("1. LDR (photoresistor) has no polarity: either way round.", False),
    ("2. 10 kΩ = brown-black-orange.", False),
    ("3. A1 header is missing: press the jumper into the", False),
    ("    A1 hole while reading.", False),
    ("4. Re-upload alerter_uno.ino afterwards.", False),
]
yy = 250
for s_, bold in NOTES:
    text(270, yy, s_, 5.0 if not bold else 5.8, "#222", "start", "bold" if bold else "normal")
    yy += 8.2 if bold else 7.0
text(470, 458, "Part art: Fritzing (CC-BY-SA)", 4.2, "#888", "end")

# ---------------------------------------------------------------- write svg + png
VX, VY, VW, VH = -168, -68, 648, 532
svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="%g %g %g %g">\n'
       '<rect x="%g" y="%g" width="%g" height="%g" fill="#ffffff"/>\n'
       % (PNG_W, round(PNG_W * VH / VW), VX, VY, VW, VH, VX, VY, VW, VH))
svg += "".join(out) + "".join(WIRES) + "".join(labels) + "</svg>\n"
with open(OUT_SVG, "w", encoding="utf-8") as f:
    f.write(svg)
print("wrote", OUT_SVG)

if os.path.exists(CHROME):
    ph = round(PNG_W * VH / VW)
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    "--default-background-color=ffffffff", "--screenshot=" + OUT_PNG,
                    "--window-size=%d,%d" % (PNG_W, ph), "file:///" + OUT_SVG.replace("\\", "/")],
                   check=True, capture_output=True)
    print("wrote", OUT_PNG)
else:
    sys.exit("Chrome not found; open the SVG in a browser to view it")
