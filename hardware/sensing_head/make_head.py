"""
make_head.py -- 3D-printable submerged sensing head (plan §13), v1
===================================================================
Replaces the cardboard-and-tape prototype that first saw chlorophyll (2026-10-14/15: plain water
322 counts, dark spinach extract 685; dilutions halve from 1/16 down). That prototype's limit was
mechanical: every time the jar was handled the zero jumped ~10 counts. Here nothing can move.

Parts, all in BLACK PETG (light passes through white/clear plastic):

  head    A cylinder that looks DOWN through a round glass window set into its underside.
          The thick floor above the glass holds:
            - the 5 mm blue LED in a bore, tip touching the glass;
            - the light sensor (Adafruit TSL2591 STEMMA QT, 25.4 x 17.8 mm) chip-down over its own
              window, with a 2.1 mm recess under it for the red filter: a 12 mm HB650 long-pass glass disc
              (or 2 squares of red gel cut 12 x 12 mm).
          The solid plastic between the two bores is the divider: the sensor can only see light
          that went down through the glass into the water and came back.
          Two optics layouts are written; print both and compare them with spinach dilutions:
            head.stl           CONVERGING: bores tilted TILT deg toward each other, 12 mm apart at the
                               glass, so the blue beam and the sensor's view cross inside the water gap
                               (how commercial in-water fluorometers are built).
            head_straight.stl  STRAIGHT: both bores vertical, 20 mm apart, as the cardboard prototype.
                               Their cones only start to overlap ~20 mm down, below the 12 mm gap.
  lid     Closes the top; the centre hole takes a PG7 cable gland (12.5 mm thread) for the 6 wires.
  shroud  A sleeve the head drops into. An inner ledge holds the glass exactly GAP mm above
          whatever the shroud stands on, and four side windows let water flow under the glass.
          On the bench it stands on a black floor; on the buoy it shades the window from sunlight.

Window: a borosilicate glass disc GLASS_D x GLASS_T. Order it, measure it with calipers, set the two
numbers below and rerun. It goes in from below and is sealed with aquarium silicone, so water
pressure pushes it ONTO the plastic, not off it.

Printing (black PETG, 0.2 mm layers, 4+ walls):
  head    floor-down on the bed, 100% infill. Turn supports on for the glass recess only (a 3 mm deep
          pocket, easy to clear); the tilted bores print without them.
  lid     flat face down.      shroud  bottom (feet) down.
FDM prints can weep water between layers: coat the outside of the head with epoxy or silicone and
soak-test it for an hour before any electronics go in.

Run from repo root:  python hardware/sensing_head/make_head.py
Writes head.stl, head_straight.stl, lid.stl, shroud.stl and preview.png next to this script.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- window (measure the disc you buy and set these)
GLASS_D, GLASS_T = 50.8, 3.0          # Plymor 2 in x 3 mm clear circle (B0BS1KZG6J); re-measure
GLASS_CLR = 0.4                   # radial gap for the silicone; printed holes come out ~0.2 small

# ---- head (mm). z = 0 is the underside; the glass recess opens downward.
OD, WALL, H = 62.0, 4.0, 45.0
RECESS_D, RECESS_H = GLASS_D + 2 * GLASS_CLR, GLASS_T + 0.2
LED_LEN = 7.6                     # 5 mm LED: body length below the flange (8.6 total - 1.0 flange)
FLOOR_EXTRA = 3.0                 # extra floor so the sensor pocket is deep enough (LED sits in a counterbore)
FLOOR_TOP = RECESS_H + LED_LEN + FLOOR_EXTRA
LED_R = 5.3 / 2                   # 5.0-5.1 mm body
LED_FLANGE_R = 6.4 / 2
LED_DOME_R = 2.5
# Screws that hold the head in the shroud (sealed, the head floats with ~85 g of lift). M3 self-tapping
# into blind pilot holes in the SOLID floor, so they cannot leak. Shroud gets clearance holes.
SCREW_Z = 7.0                     # height on the head (inside the solid floor)
PILOT_R, PILOT_DEPTH, CLEAR_R = 1.25, 6.0, 1.7
WIN_R = 3.5                       # 7 mm sensor window
GEL, GEL_H = 12.6, 2.1            # filter recess: HB650 650 nm long-pass glass, 12 mm round x 2.0 mm (B0H8F41D8D); 12 x 12 gel squares also fit
BOARD_X, BOARD_Y = 18.8, 26.4     # TSL2591 pocket (board + 1 mm), long side along y
# The STEMMA QT board has its chip AND both JST plugs on the same side (~3 mm tall). Mounted chip-down,
# it rests on its plugs: pocket = board 1.6 + parts 3.0 deep, with notches at both ends for the cables.
POCKET_D = 4.6
NOTCH_W, NOTCH_L = 8.0, 8.0
VARIANTS = {"head": dict(half=6.0, tilt=25.0), "head_straight": dict(half=10.0, tilt=0.0)}
LID_T, SKIRT_H, SKIRT_T, CLR = 4.0, 8.0, 2.4, 0.3
GLAND_D = 12.8                    # PG7 cable gland thread (12.5 mm)

# ---- shroud
GAP = 12.0                        # water under the glass (the prototype's Lego stilt was ~10)
S_WALL, S_OVERLAP = 3.0, 18.0
S_ID = OD + 2 * CLR
LEDGE_ID = RECESS_D + 3.0         # the ledge carries the head's rim, never the glass
LEDGE_T = 2.0
FLOW_W, FLOW_H = 22.0, GAP - 3.0  # four side windows below the ledge, 3 mm feet left at the bottom


def box(sx, sy, sz, cx=0, cy=0, cz=0):
    m = trimesh.creation.box(extents=(sx, sy, sz))
    m.apply_translation((cx, cy, cz))
    return m


def cyl(r, h, cx=0, cy=0, z0=0, sections=96):
    m = trimesh.creation.cylinder(radius=r, height=h, sections=sections)
    m.apply_translation((cx, cy, z0 + h / 2))
    return m


def bore(r, x0, lean, a0, a1):
    """Cylinder of radius r on an axis through (x0, 0, glass top), leaning `lean` deg from vertical
    (positive: its top leans toward +x), spanning axial distances a0..a1 from that point.
    Cutters start well below the glass seat so their tilted end never notches the seat (it lies in the empty recess)."""
    m = trimesh.creation.cylinder(radius=r, height=a1 - a0, sections=64)
    m.apply_translation((0, 0, (a0 + a1) / 2))
    m.apply_transform(trimesh.transformations.rotation_matrix(np.radians(lean), (0, 1, 0)))
    m.apply_translation((x0, 0, RECESS_H))
    return m


def cut_all(m, cutters):
    # One at a time: a concatenated cutter leaves overlaps uncut (trimesh/manifold).
    for c in cutters:
        m = m.difference(c, engine="manifold")
    return m


FILTER_Z = FLOOR_TOP - POCKET_D - GEL_H / 2   # middle of the filter recess, under the board pocket


def window_top_x(half, tilt):
    """x of the sensor bore at the filter's height (the filter and the board are centred there)."""
    return half + (FILTER_Z - RECESS_H) * np.tan(np.radians(tilt))


def led_lift(tilt):
    """A tilted LED's round tip would touch the glass before its axis point does: raise its seat."""
    return LED_DOME_R / np.cos(np.radians(tilt)) - LED_DOME_R + 0.05 if tilt else 0.0


def head(half, tilt):
    wx = window_top_x(half, tilt)
    reach = (FLOOR_TOP - RECESS_H) / np.cos(np.radians(tilt)) + 6     # long enough to clear the floor
    lift = led_lift(tilt)
    pilots = []
    for sgn in (1, -1):              # two blind pilot holes, radial along +/- y, into the solid floor
        c = trimesh.creation.cylinder(radius=PILOT_R, height=PILOT_DEPTH + 1, sections=24)
        c.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, (1, 0, 0)))
        c.apply_translation((0, sgn * (OD / 2 - PILOT_DEPTH / 2 + 0.5), SCREW_Z))
        pilots.append(c)
    return cut_all(cyl(OD / 2, H), pilots + [
        cyl(OD / 2 - WALL, H - FLOOR_TOP + 1, z0=FLOOR_TOP),                        # electronics cavity
        cyl(RECESS_D / 2, RECESS_H + 0.01, z0=-0.01),                                # glass recess
        bore(LED_R, -half, -tilt, -RECESS_H - 2, LED_LEN + lift + 0.01),                      # LED body, tip on glass
        bore(LED_FLANGE_R, -half, -tilt, LED_LEN + lift, reach),                     # flange seat and above
        bore(WIN_R, half, tilt, -RECESS_H - 2, reach),                                        # sensor window
        box(BOARD_X, BOARD_Y, POCKET_D + 0.01, cx=wx, cz=FLOOR_TOP - POCKET_D / 2 + 0.005),  # board pocket
        box(NOTCH_W, NOTCH_L, POCKET_D + 0.01, cx=wx, cy=(BOARD_Y + NOTCH_L) / 2 - 0.5,
            cz=FLOOR_TOP - POCKET_D / 2 + 0.005),                                    # cable plug notches
        box(NOTCH_W, NOTCH_L, POCKET_D + 0.01, cx=wx, cy=-(BOARD_Y + NOTCH_L) / 2 + 0.5,
            cz=FLOOR_TOP - POCKET_D / 2 + 0.005),
        box(GEL, GEL, GEL_H + 0.02, cx=wx, cz=FILTER_Z),                            # filter recess
    ])


def lid():
    plate = cyl(OD / 2, LID_T)
    skirt_r = OD / 2 - WALL - CLR
    skirt = cyl(skirt_r, SKIRT_H, z0=LID_T - 0.01).difference(
        cyl(skirt_r - SKIRT_T, SKIRT_H + 1, z0=LID_T - 0.5), engine="manifold")
    return plate.union(skirt, engine="manifold").difference(
        cyl(GLAND_D / 2, LID_T + SKIRT_H + 2, z0=-1), engine="manifold")


def shroud():
    h = GAP + LEDGE_T + S_OVERLAP
    s = cyl(S_ID / 2 + S_WALL, h).difference(cyl(S_ID / 2, h + 2, z0=-1), engine="manifold")
    ledge = cyl(S_ID / 2 + 0.1, LEDGE_T, z0=GAP).difference(
        cyl(LEDGE_ID / 2, LEDGE_T + 2, z0=GAP - 1), engine="manifold")
    s = s.union(ledge, engine="manifold")
    for sgn in (1, -1):                  # M3 clearance holes, lined up with the head's pilot holes
        c = trimesh.creation.cylinder(radius=CLEAR_R, height=S_WALL * 3, sections=24)
        c.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, (1, 0, 0)))
        c.apply_translation((0, sgn * (S_ID / 2 + S_WALL / 2), GAP + LEDGE_T + SCREW_Z))
        s = s.difference(c, engine="manifold")
    for a in (0, 90, 180, 270):          # flow windows through the wall, below the ledge
        w = box(FLOW_W, S_WALL * 3 + 2, FLOW_H, cy=S_ID / 2 + S_WALL / 2, cz=3.0 + FLOW_H / 2)
        w.apply_transform(trimesh.transformations.rotation_matrix(np.radians(a), (0, 0, 1)))
        s = s.difference(w, engine="manifold")
    return s


def draw(ax, mesh, color, title, elev, azim):
    light = np.array([0.4, -0.5, 0.8]) / np.linalg.norm([0.4, -0.5, 0.8])
    base = np.array(matplotlib.colors.to_rgb(color))
    shade = 0.45 + 0.55 * np.clip(mesh.face_normals @ light, 0, 1)
    ax.add_collection3d(Poly3DCollection(mesh.vertices[mesh.faces], facecolors=base * shade[:, None],
                                         edgecolor="none"))
    lo, hi = mesh.bounds
    span = (hi - lo).max() / 2
    mid = (hi + lo) / 2
    for setlim, c in zip((ax.set_xlim, ax.set_ylim, ax.set_zlim), mid):
        setlim(c - span, c + span)
    ax.view_init(elev=elev, azim=azim)
    ax.set_title(title, fontsize=10)
    ax.set_axis_off()


def section(ax, hd, half, tilt, title):
    """Side cut through the LED and the sensor window (y = 0), to scale, with the glass, the water and
    the two optical axes (dashed) so you can see where they cross."""
    sec = hd.section(plane_origin=(0, 0, 0), plane_normal=(0, 1, 0))
    for seg in sec.discrete:                       # outline loops in 3D; plot x against z
        ax.fill(seg[:, 0], seg[:, 2], color="#30363b", lw=0)
    ax.add_patch(plt.Rectangle((-GLASS_D / 2, 0.1), GLASS_D, GLASS_T, color="#a9d6e5", alpha=0.9))
    ax.add_patch(plt.Rectangle((-OD / 2 - 6, -GAP), OD + 12, GAP, color="#cfe8d0", alpha=0.6))
    wx, t = window_top_x(half, tilt), np.tan(np.radians(tilt))
    zs = np.array([FLOOR_TOP + 2, -GAP])
    ax.plot(-half - (zs - RECESS_H) * t, zs, "--", color="#2f7de1", lw=1.4)
    ax.plot(half + (zs - RECESS_H) * t, zs, "--", color="#c62828", lw=1.4)
    ax.add_patch(plt.Rectangle((wx - BOARD_X / 2 + 0.5, FLOOR_TOP - 1.6), BOARD_X - 1, 1.6, color="#7b3fb5"))
    ax.add_patch(plt.Rectangle((wx - 6, FLOOR_TOP - POCKET_D - GEL_H), 12, 2.0, color="#c62828"))
    ax.annotate("blue LED axis", (-half - 9, FLOOR_TOP + 4), ha="center", fontsize=8, color="#2f7de1")
    ax.annotate("TSL2591 over red gel", (wx + 2, FLOOR_TOP + 4), ha="center", fontsize=8)
    ax.annotate("glass window", (0, -3.5), ha="center", fontsize=8)
    ax.annotate(f"water, {GAP:.0f} mm gap", (0, -GAP + 1.5), ha="center", fontsize=8)
    ax.set_aspect("equal")
    ax.set_xlim(-OD / 2 - 6, OD / 2 + 6)
    ax.set_ylim(-GAP - 2, H + 2)
    ax.set_title(title, fontsize=10)
    ax.set_xlabel("mm")


def main():
    parts = {name: head(**v) for name, v in VARIANTS.items()}
    parts.update(lid=lid(), shroud=shroud())
    for name, m in parts.items():
        assert m.is_watertight, f"{name} mesh not watertight"
        m.export(os.path.join(HERE, f"{name}.stl"))
        print(f"{name:<14} {m.extents.round(1)} mm, volume {m.volume / 1000:.1f} cm3")

    fig = plt.figure(figsize=(16, 8.6))
    draw(fig.add_subplot(231, projection="3d"), parts["head"], "#7d8790", "Head from above (lid off)", 55, -60)
    draw(fig.add_subplot(232, projection="3d"), parts["head"], "#7d8790", "Head from below (glass recess)", -50, -60)
    draw(fig.add_subplot(233, projection="3d"), parts["shroud"], "#5c656d", "Shroud (flow windows)", 20, -60)
    for k, (name, v) in enumerate(VARIANTS.items()):
        cross = v["half"] / np.tan(np.radians(v["tilt"])) - GLASS_T if v["tilt"] else None
        where = f"axes cross {cross:.0f} mm below the glass" if cross else "axes never cross"
        section(fig.add_subplot(2, 2, 3 + k), parts[name], v["half"], v["tilt"],
                f"{name}.stl: {where} (to scale)")
    fig.suptitle("Submerged sensing head v1: LED and sensor look down through one glass window",
                 fontsize=12, fontweight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "preview.png"), dpi=130, facecolor="white")
    print("wrote " + ", ".join(f"{n}.stl" for n in parts) + ", preview.png")


if __name__ == "__main__":
    main()
