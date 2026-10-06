"""
rake_capture.py
---------------
Step 3 of the device simulation (notes/DEVICE_SIMULATION.md): settling plus the floor
raster of the v7-final magnet rake (notes/DEVICE_PROTOTYPE.md s3), as a Monte-Carlo
particle model driven by the Step 1 field grid and the Step 2 floc size distribution.

Model
  - N flocs, each representing an equal share of the dosed clay mass, sizes drawn from
    data/sim/floc_size_dist.csv for one flocculation case (alpha, seed).
  - Floc solids mass = n primaries x m0 (floc_kinetics.py); magnetite = 37.5 wt% of the
    dry blend (15 : 18.5 : 6.5 magnetite : kaolin : PAC). Magnetisation M(B) = Ms tanh(B / 0.08 T)
    (pigment-grade magnetite is near saturation above ~0.2 T; stated assumption).
  - Settle 15 min from a uniform start height in 160 mm of water; flocs still in the column
    at T31 are not reachable by the floor raster (column passes are not modelled).
  - Floor positions uniform over the 500 x 250 mm floor. The rake translates along x at
    speed u; each floc moves at  F_mag / (3 pi mu d)  +  buoyant weight / (3 pi mu d)  (down),
    F_mag = m_mag M(B) grad|B|, with the floor (and tank walls) as hard constraints.
  - Capture when the floc top reaches the tube wall surface (z = -3.2 mm) under a tube
    (31.75 mm OD square tubes centred on each stack). Flocs pulled up in the 1.25 mm gaps
    between tubes are not captured.
  - Pass 1 and 3 on lane A (first tube edge 11 mm from the long wall); pass 2 offset +30 mm.
    Captured flocs are removed after each pass (release into the tray).
  - Not modelled: stranding at release, resuspension of the floor by the frame and wake,
    floc breakup under magnetic or drag stress, floc-floc interaction, the skids pushing flocs.

Outputs
  data/sim/rake_capture.csv          one row per case x pass
  figures/sim/fig_rake_capture.png

Run from repo root (after rake_field.py and floc_kinetics.py):
    python src/sim/rake_capture.py
"""
import os
import numpy as np
import pandas as pd

MU, RHO_W, RHO_S = 1.08e-3, 1025.0, 3000.0
D0, DF = 2.0e-6, 2.2
M0 = RHO_S * np.pi / 6 * D0 ** 3
MAG_FRAC = 15 / 40
WALL = 0.0032
TUBE_HALF = 0.03175 / 2
STACK_LEN = 0.160
FLOOR_X, FLOOR_Y, DEPTH = 0.500, 0.250, 0.160
LANE_A_EDGE = 0.011
SETTLE_S = 900.0
DT = 0.004
N_FLOCS = 4000
SEED = 42

BASE = dict(speed=0.010, skid=0.003, pitch=33, Ms=70.0, alpha=0.35, seed_case="pre-aggregated")
CASES = [
    ("base", {}),
    ("speed 0.5 cm/s", dict(speed=0.005)),
    ("speed 2 cm/s", dict(speed=0.020)),
    ("skid 0 mm", dict(skid=0.0)),
    ("skid 6 mm", dict(skid=0.006)),
    ("pitch 30 mm", dict(pitch=30)),
    ("Ms 60", dict(Ms=60.0)),
    ("Ms 80", dict(Ms=80.0)),
    ("flocs: dispersed, alpha 0.35", dict(seed_case="dispersed", alpha=0.35)),
    ("flocs: dispersed, alpha 1.0", dict(seed_case="dispersed", alpha=1.0)),
    ("flocs: pre-aggregated, alpha 0.1", dict(seed_case="pre-aggregated", alpha=0.1)),
    ("control: no magnetite", dict(Ms=0.0)),
]

_cubes = {}


def load_cube(pitch):
    if pitch not in _cubes:
        z = np.load(f"data/sim/rake_field_cube_p{pitch}.npz")
        _cubes[pitch] = {k: z[k] for k in z.files}
    return _cubes[pitch]


def sample_flocs(dist, alpha, seed_case, rng, n):
    d = dist[(np.isclose(dist.alpha, alpha)) & (dist.seed == seed_case)].sort_values("bin")
    p = d.mass_frac.to_numpy(); p = p / p.sum()
    k = rng.choice(len(d), size=n, p=p)
    n_prim = d.n_primaries.to_numpy()[k]
    diam = D0 * n_prim ** (1 / DF)
    solids = n_prim * M0
    v_set = d.v_settle_mm_s.to_numpy()[k] / 1000
    return diam, solids, v_set


def simulate(cfg, dist, rng):
    diam, solids, v_set = sample_flocs(dist, cfg["alpha"], cfg["seed_case"], rng, N_FLOCS)
    h0 = rng.uniform(0, DEPTH, N_FLOCS)
    on_floor = v_set * SETTLE_S >= h0
    frac_column = 1 - on_floor.mean()

    cube = load_cube(cfg["pitch"])
    xs, ys, zs = cube["xs"], cube["ys"], cube["zs"]
    Bm, gx, gy, gz = cube["Bmag"], cube["gx"], cube["gy"], cube["gz"]
    pitch = float(cube["pitch"])
    floor_z = -(WALL + cfg["skid"])

    idx = np.where(on_floor)[0]
    x = rng.uniform(0, FLOOR_X, len(idx))
    y = rng.uniform(0, FLOOR_Y, len(idx))
    d = diam[idx]; r = d / 2
    z = floor_z + r
    m_mag = MAG_FRAC * solids[idx]
    weight = (RHO_S - RHO_W) / RHO_S * solids[idx] * 9.81
    drag = 3 * np.pi * MU * d
    alive = np.ones(len(idx), bool)

    out = []
    lanes = [LANE_A_EDGE + TUBE_HALF, LANE_A_EDGE + TUBE_HALF + 0.030, LANE_A_EDGE + TUBE_HALF]
    captured_total = 0
    for p, y_off in enumerate(lanes, start=1):
        x_r = -0.20
        x_end = FLOOR_X + 0.03
        cap_pass = 0
        while x_r < x_end:
            lx = x - x_r
            ly = y - y_off
            act = alive & (lx > xs[0]) & (lx < xs[-1]) & (ly > ys[0]) & (ly < ys[-1])
            if act.any():
                a = np.where(act)[0]
                ii = np.clip(np.rint((lx[a] - xs[0]) / (xs[1] - xs[0])).astype(int), 0, len(xs) - 1)
                jj = np.clip(np.rint((ly[a] - ys[0]) / (ys[1] - ys[0])).astype(int), 0, len(ys) - 1)
                kk = np.clip(np.rint((z[a] - zs[0]) / (zs[1] - zs[0])).astype(int), 0, len(zs) - 1)
                below = z[a] < zs[0]
                B = Bm[ii, jj, kk]
                Mf = cfg["Ms"] * np.tanh(B / 0.08) * m_mag[a]
                Fx, Fy, Fz = Mf * gx[ii, jj, kk], Mf * gy[ii, jj, kk], Mf * gz[ii, jj, kk]
                Fx[below] = 0.0; Fy[below] = 0.0; Fz[below] = 0.0
                x[a] = np.clip(x[a] + DT * Fx / drag[a], 0, FLOOR_X)
                y[a] = np.clip(y[a] + DT * Fy / drag[a], 0, FLOOR_Y)
                z[a] = np.maximum(z[a] + DT * (Fz - weight[a]) / drag[a], floor_z + r[a])
                top = z[a] + r[a] >= -WALL
                if top.any():
                    at = a[top]
                    lyt = y[at] - y_off
                    s = np.rint(lyt / pitch)
                    under = (np.abs(lyt - s * pitch) <= TUBE_HALF) & (s >= 0) & (s <= 5) \
                        & (x[at] - x_r >= -0.002) & (x[at] - x_r <= STACK_LEN + 0.002)
                    hit = at[under]
                    alive[hit] = False
                    cap_pass += len(hit)
                    gap = at[~under]
                    z[gap] = -WALL - r[gap]
            x_r += cfg["speed"] * DT
        captured_total += cap_pass
        z[alive] = floor_z + r[alive]          # uncaptured flocs fall back before the next pass
        out.append(dict(pass_no=p, recovery=captured_total / N_FLOCS, captured_this_pass=cap_pass / N_FLOCS))
    left_floor = alive.sum() / N_FLOCS
    lane_lo = LANE_A_EDGE
    lane_hi = LANE_A_EDGE + 0.030 + 5 * pitch + 2 * TUBE_HALF
    outside = (alive & ((y < lane_lo) | (y > lane_hi))).sum() / N_FLOCS
    for o in out:
        o.update(frac_column=frac_column, left_on_floor=left_floor, left_outside_lanes=outside)
    return out


def main():
    os.makedirs("data/sim", exist_ok=True); os.makedirs("figures/sim", exist_ok=True)
    dist = pd.read_csv("data/sim/floc_size_dist.csv")
    rows = []
    for name, over in CASES:
        cfg = dict(BASE, **over)
        if not os.path.exists(f"data/sim/rake_field_cube_p{cfg['pitch']}.npz"):
            print(f"skip {name}: no field grid for pitch {cfg['pitch']} "
                  f"(run rake_field.py --pitch-mm {cfg['pitch']} --cube-only)")
            continue
        res = simulate(cfg, dist, np.random.default_rng(SEED))
        for r in res:
            rows.append(dict(case=name, speed_cm_s=cfg["speed"] * 100, skid_mm=cfg["skid"] * 1000, pitch_mm=cfg["pitch"],
                             Ms=cfg["Ms"], alpha=cfg["alpha"], floc_seed=cfg["seed_case"], **r))
        r3 = res[-1]
        print(f"{name:>34}: recovery after passes 1/2/3 = "
              f"{100*res[0]['recovery']:.0f} / {100*res[1]['recovery']:.0f} / {100*r3['recovery']:.0f}%; "
              f"still in column {100*r3['frac_column']:.0f}%; left on floor {100*r3['left_on_floor']:.0f}% "
              f"(outside lanes {100*r3['left_outside_lanes']:.0f}%)", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv("data/sim/rake_capture.csv", index=False, float_format="%.4g")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    last = df[df.pass_no == 3].reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(10, 5))
    yy = np.arange(len(last))[::-1]
    ax.barh(yy, 100 * last.recovery, color=["#8a3b1f" if c == "base" else "#c9b99b" for c in last.case],
            label="captured on the tubes")
    ax.barh(yy, 100 * last.frac_column, left=100 * last.recovery, color="#9fc7cf", label="still in water column at T31")
    ax.barh(yy, 100 * last.left_on_floor, left=100 * (last.recovery + last.frac_column), color="#d9d9d9",
            label="left on floor")
    ax.set_yticks(yy); ax.set_yticklabels(last.case, fontsize=8)
    ax.axvline(70, color="k", lw=0.8, ls="--"); ax.text(70.5, len(last) - 0.4, "H11b pass (70%)", fontsize=7)
    ax.set_xlim(0, 100); ax.set_xlabel("% of dosed magnetite (equal-mass flocs), after three floor passes")
    ax.set_title("Predicted floor-raster recovery, one-at-a-time sensitivity around the base case")
    ax.legend(fontsize=8, loc="lower right"); fig.tight_layout(); fig.savefig("figures/sim/fig_rake_capture.png", dpi=160)
    print("Saved data/sim/rake_capture.csv, figures/sim/fig_rake_capture.png")


if __name__ == "__main__":
    main()
