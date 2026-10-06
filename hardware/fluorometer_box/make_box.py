"""
make_box.py -- 3D-printable dark box for the alerter's fluorometer (build stage 5)
==================================================================================
A light-tight block that holds one standard 4.5 mL cuvette (12.5 x 12.5 x 45 mm):

  - LED bore on the -X face: a 5 mm blue LED pushes in from outside and shines at the cuvette.
  - Sensor at 90 deg on the +Y face: a 5 mm deep pocket for the Adafruit TSL2591 STEMMA QT board
    (25.4 x 17.8 mm, chip facing in) with a notch for the cable plug, a 6 mm window to the cuvette,
    and a thin slot in between for a strip of red gel filter (13 x 40 mm).
    The 90 deg angle means the sensor sees the chlorophyll's red glow, not the LED.
  - A cap with a skirt covers the cuvette well and the filter slot.
The LED and the window are both at the cuvette's standard beam height (15 mm above its bottom).

Print in BLACK filament (light leaks through white/clear plastic), 3+ walls, 20%+ infill, no supports:
body upside-up, cap skirt-up. Tolerances assume a normal FDM printer; if the cuvette is tight,
scale X/Y by 101% in the slicer.

Run from repo root:  python hardware/fluorometer_box/make_box.py
Writes fluorometer_box.stl, fluorometer_cap.stl and preview.png next to this script.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- dimensions (mm)
W = D = 50.0                  # body footprint
H = 51.0                      # body height
FLOOR = 5.0                   # material under the cuvette
WELL = 13.2                   # cuvette well: standard cuvette 12.5 x 12.5 x 45; printed holes come out ~0.2 small
BEAM_Z = FLOOR + 15.0         # beam height: 15 mm above the cuvette bottom (standard spectrophotometer z-height)
LED_R = 5.3 / 2               # 5 mm LED body (5.0-5.1 mm)
LED_FLANGE_R, LED_FLANGE_DEPTH = 6.2 / 2, 1.5     # LED rim is ~5.8 mm across, ~1 mm thick
WINDOW_R = 3.0                # 6 mm window: tolerates the sensor chip being ~1 mm off the board centre
# Adafruit TSL2591 STEMMA QT (#1980, 2020+): standard 1.0 x 0.7 in (25.4 x 17.8 mm) board with a JST SH
# connector on each short edge, ~3 mm tall on the chip side. (The older non-STEMMA board is 19 x 16 mm
# and also fits.) Pocket = board + 1 mm, deep enough for the connectors, plus a notch for the cable plug.
BOARD_W, BOARD_H, BOARD_DEPTH = 26.4, 18.8, 5.0
NOTCH_H = 8.0                 # cable notch: from the pocket's +X edge out to the side of the block
SLOT_W, SLOT_T, SLOT_BOTTOM = 14.0, 1.0, 8.0      # red gel slot (cut the gel 13 x 40 mm)
SLOT_Y = WELL / 2 + 3.5       # slot sits 3.5 mm from the well wall
CAP_T, SKIRT_H, SKIRT_T, CLEAR = 3.0, 6.0, 1.4, 0.4


def box(sx, sy, sz, cx=0, cy=0, cz=0):
    m = trimesh.creation.box(extents=(sx, sy, sz))
    m.apply_translation((cx, cy, cz))
    return m


def cyl(r, length, axis, center):
    m = trimesh.creation.cylinder(radius=r, height=length, sections=64)
    if axis == "x":
        m.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, (0, 1, 0)))
    elif axis == "y":
        m.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, (1, 0, 0)))
    m.apply_translation(center)
    return m


def body():
    b = box(W, D, H, cz=H / 2)
    well_wall = WELL / 2
    cuts = [
        box(WELL, WELL, H - FLOOR + 1, cz=FLOOR + (H - FLOOR + 1) / 2),                       # cuvette well
        cyl(LED_R, W / 2 - well_wall + 1, "x", (-(W / 2 + well_wall) / 2, 0, BEAM_Z)),     # LED bore
        cyl(LED_FLANGE_R, LED_FLANGE_DEPTH + 1, "x", (-W / 2 + (LED_FLANGE_DEPTH - 1) / 2, 0, BEAM_Z)),
        cyl(WINDOW_R, D / 2 - well_wall, "y", (0, (D / 2 + well_wall) / 2, BEAM_Z)),        # sensor window
        box(BOARD_W, BOARD_DEPTH + 1, BOARD_H, cy=D / 2 - (BOARD_DEPTH - 1) / 2, cz=BEAM_Z),  # board pocket
        box(W / 2 - BOARD_W / 2 + 1, BOARD_DEPTH + 1, NOTCH_H, cx=(W / 2 + BOARD_W / 2) / 2,   # cable notch
            cy=D / 2 - (BOARD_DEPTH - 1) / 2, cz=BEAM_Z),
        box(SLOT_W, SLOT_T, H - SLOT_BOTTOM + 1, cy=SLOT_Y, cz=SLOT_BOTTOM + (H - SLOT_BOTTOM + 1) / 2),  # gel slot
    ]
    # Subtract one at a time: concatenating overlapping cutters into one mesh leaves their overlap uncut
    # (a thin skin over the LED hole, in the sensor pocket and across the gel slot).
    for cut in cuts:
        b = b.difference(cut, engine="manifold")
    return b


def cap():
    outer = W + 2 * (CLEAR + SKIRT_T)
    plate = box(outer, outer, CAP_T, cz=CAP_T / 2)
    ring = box(outer, outer, SKIRT_H, cz=CAP_T + SKIRT_H / 2).difference(
        box(W + 2 * CLEAR, W + 2 * CLEAR, SKIRT_H + 1, cz=CAP_T + SKIRT_H / 2), engine="manifold")
    return plate.union(ring, engine="manifold")


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


def main():
    b, c = body(), cap()
    assert b.is_watertight, "body mesh not watertight"
    b.export(os.path.join(HERE, "fluorometer_box.stl"))
    c.export(os.path.join(HERE, "fluorometer_cap.stl"))

    fig = plt.figure(figsize=(13, 4.6))
    draw(fig.add_subplot(131, projection="3d"), b, "#9aa4ad", "LED side (-X): 5 mm LED bore", 22, -140)
    draw(fig.add_subplot(132, projection="3d"), b, "#9aa4ad", "Sensor side (+Y): board pocket + window", 22, 60)
    draw(fig.add_subplot(133, projection="3d"), c, "#6d7780", "Cap (print skirt-up)", 35, -60)
    fig.suptitle("Fluorometer dark box: cuvette in the top, blue LED left, TSL2591 at 90° behind red gel",
                 fontsize=12, fontweight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "preview.png"), dpi=130, facecolor="white")
    print(f"body {b.extents.round(1)} mm, volume {b.volume / 1000:.1f} cm3, watertight {b.is_watertight}")
    print(f"cap  {c.extents.round(1)} mm")
    print("wrote fluorometer_box.stl, fluorometer_cap.stl, preview.png")


if __name__ == "__main__":
    main()
