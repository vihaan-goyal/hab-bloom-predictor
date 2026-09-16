"""
rake_field.py
-------------
Step 1 of the device simulation (notes/DEVICE_SIMULATION.md): magnetic field of the
v7-final magnet rake (notes/DEVICE_PROTOTYPE.md s3), computed with Magpylib.

Geometry (SI units, metres; origin at the pole face of stack 0, block 0):
  - 6 stacks, each 4 x N52 blocks 40 x 20 x 10 mm laid end to end along x (160 mm)
  - stacks side by side along y at PITCH (33 mm default) centre to centre
  - blocks magnetised through the 10 mm thickness, same pole down (polarisation -z)
  - pole face at z = 0; acrylic tube wall 3.2 mm -> capture surface at z = -3.2 mm
  - skids 3 mm -> tank floor at z = -6.2 mm

Outputs
  data/sim/rake_field_grid.csv        field on the capture plane and floor plane
  data/sim/rake_field_cube_p<pitch>.npz  3D field grid used by rake_capture.py
  figures/sim/fig_rake_field.png
Prints cross-checks against the reviewers' hand calculations.

Run from repo root:
    python src/sim/rake_field.py [--pitch-mm 33]
"""
import argparse
import os
import numpy as np
import magpylib as magpy

BR = 1.45             # T, N52 remanence (reviews 1 and 6)
BLOCK = (0.040, 0.020, 0.010)
N_BLOCKS, N_STACKS = 4, 6
WALL, SKID = 0.0032, 0.003


def cuboid(pos, pol=-1.0):
    return magpy.magnet.Cuboid(polarization=(0, 0, pol * BR), dimension=BLOCK, position=pos)


def stack_blocks(y, pol=-1.0):
    return [cuboid((BLOCK[0] * (b + 0.5), y, BLOCK[2] / 2), pol) for b in range(N_BLOCKS)]


def build_rake(pitch):
    return magpy.Collection(*[blk for s in range(N_STACKS) for blk in stack_blocks(pitch * s)])


def single_block_face_field():
    m = cuboid((0, 0, BLOCK[2] / 2), pol=1.0)
    zs = np.array([0.0032, 0.005, 0.010])
    B = m.getB(np.c_[np.zeros(3), np.zeros(3), -zs])
    return zs, np.linalg.norm(B, axis=1)


def force_on(targets, sources):
    for t in targets:
        t.meshing = 10
    F, _ = magpy.getFT(magpy.Collection(*sources), targets)
    return np.asarray(F).reshape(-1, 3).sum(axis=0)


def field_cube(rake, pitch, x_rng=(-0.03, 0.19), z_rng=(-0.0122, -0.0030), dxy=0.001, dz=0.0002):
    xs = np.arange(x_rng[0], x_rng[1] + 1e-9, dxy)
    ys = np.arange(-0.03, pitch * (N_STACKS - 1) + 0.03 + 1e-9, dxy)
    zs = np.arange(z_rng[0], z_rng[1] + 1e-9, dz)
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")
    B = rake.getB(np.c_[X.ravel(), Y.ravel(), Z.ravel()]).reshape(len(xs), len(ys), len(zs), 3)
    Bmag = np.linalg.norm(B, axis=-1)
    gx, gy, gz = np.gradient(Bmag, xs, ys, zs)
    return xs, ys, zs, Bmag, gx, gy, gz


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pitch-mm", type=float, default=33.0)
    ap.add_argument("--cube-only", action="store_true", help="only write the 3D grid (for sensitivity pitches)")
    args = ap.parse_args()
    pitch = args.pitch_mm / 1000
    os.makedirs("data/sim", exist_ok=True)
    os.makedirs("figures/sim", exist_ok=True)

    if not args.cube_only:
        zs_, Bf = single_block_face_field()
        print("Single block, field on the pole-face axis:")
        for z, bb, ref in zip(zs_, Bf, (0.32, 0.27, 0.17)):
            print(f"  {z*1000:4.1f} mm: {bb:.3f} T  (reviewers' block formula {ref:.2f} T, diff {100*(bb-ref)/ref:+.0f}%)")

    F = force_on(stack_blocks(pitch), stack_blocks(0.0))
    print(f"Adjacent-stack force at {pitch*1000:.0f} mm pitch: Fy = {F[1]:+.1f} N ({F[1]/9.81:+.1f} kgf), "
          f"Fz = {F[2]:+.1f} N  (reviewer 6 estimate ~116 N repulsion)")
    others = [blk for s in range(1, N_STACKS) for blk in stack_blocks(pitch * s)]
    Fe = force_on(stack_blocks(0.0), others)
    print(f"End stack net force from the other five: Fy = {Fe[1]:+.1f} N ({Fe[1]/9.81:+.1f} kgf)  (reviewer 6 ~130 N)")

    rake = build_rake(pitch)
    xs, ys, zs, Bmag, gx, gy, gz = field_cube(rake, pitch)
    tag = int(round(pitch * 1000))
    np.savez_compressed(f"data/sim/rake_field_cube_p{tag}.npz",
                        xs=xs, ys=ys, zs=zs, Bmag=Bmag, gx=gx, gy=gy, gz=gz, pitch=pitch)

    if args.cube_only:
        print(f"Saved data/sim/rake_field_cube_p{tag}.npz")
        return
    import pandas as pd
    rows = []
    for zname, zt in (("capture_surface", -WALL), ("floor_skid3", -(WALL + SKID))):
        k = int(np.argmin(abs(zs - zt)))
        g = np.sqrt(gx[:, :, k]**2 + gy[:, :, k]**2 + gz[:, :, k]**2)
        XX, YY = np.meshgrid(xs, ys, indexing="ij")
        rows.append(pd.DataFrame({"plane": zname, "x_mm": XX.ravel()*1000, "y_mm": YY.ravel()*1000,
                                  "z_mm": zs[k]*1000, "Bmag_T": Bmag[:, :, k].ravel(),
                                  "gradB_T_per_m": g.ravel(), "gradBz_T_per_m": gz[:, :, k].ravel()}))
    pd.concat(rows).to_csv("data/sim/rake_field_grid.csv", index=False, float_format="%.5g")

    ix = int(np.argmin(abs(xs - 0.08)))
    k_floor = int(np.argmin(abs(zs + (WALL + SKID))))
    k_cap = int(np.argmin(abs(zs + WALL)))
    j_face = [int(np.argmin(abs(ys - pitch * s))) for s in range(N_STACKS)]
    j_gap = [int(np.argmin(abs(ys - pitch * (s + 0.5)))) for s in range(N_STACKS - 1)]
    print("Mid-stack (x = 80 mm), capture surface z = -3.2 mm: "
          f"|B| under faces {Bmag[ix, j_face, k_cap].mean():.3f} T, between faces {Bmag[ix, j_gap, k_cap].mean():.3f} T")
    print("Mid-stack, floor z = -6.2 mm: "
          f"|B| under faces {Bmag[ix, j_face, k_floor].mean():.3f} T, between {Bmag[ix, j_gap, k_floor].mean():.3f} T; "
          f"|d|B|/dz| under faces {abs(gz[ix, j_face, k_floor]).mean():.1f} T/m, between {abs(gz[ix, j_gap, k_floor]).mean():.1f} T/m")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
    im = ax[0].imshow(Bmag[:, :, k_floor].T, origin="lower", aspect="equal",
                      extent=[xs[0]*1000, xs[-1]*1000, ys[0]*1000, ys[-1]*1000], cmap="viridis")
    cs = ax[0].contour(xs*1000, ys*1000, Bmag[:, :, k_floor].T, levels=[0.05, 0.1, 0.15], colors="w", linewidths=0.8)
    ax[0].clabel(cs, fmt="%.2f T", fontsize=7)
    for s in range(N_STACKS):
        ax[0].add_patch(plt.Rectangle((0, (pitch*s - 0.01)*1000), 160, 20, fill=False, ec="r", lw=0.6))
    ax[0].set_xlabel("x along stack (mm)"); ax[0].set_ylabel("y across frame (mm)")
    ax[0].set_title(f"|B| on the tank floor (3 mm skid), pitch {pitch*1000:.0f} mm; red = pole faces")
    fig.colorbar(im, ax=ax[0], label="T", shrink=0.8)
    im2 = ax[1].imshow(Bmag[ix, :, :].T, origin="lower", aspect="auto",
                       extent=[ys[0]*1000, ys[-1]*1000, zs[0]*1000, zs[-1]*1000], cmap="viridis")
    ax[1].axhline(-WALL*1000, color="w", ls="--", lw=0.8)
    ax[1].text(ys[0]*1000 + 2, -WALL*1000 - 0.5, "capture surface", color="w", fontsize=7)
    ax[1].axhline(-(WALL+SKID)*1000, color="orange", ls="--", lw=0.8)
    ax[1].text(ys[0]*1000 + 2, -(WALL+SKID)*1000 - 0.5, "floor (3 mm skid)", color="orange", fontsize=7)
    ax[1].set_xlabel("y across frame (mm)"); ax[1].set_ylabel("z below pole face (mm)")
    ax[1].set_title("|B| in a section across the six stacks, x = 80 mm")
    fig.colorbar(im2, ax=ax[1], label="T", shrink=0.8)
    fig.tight_layout(); fig.savefig("figures/sim/fig_rake_field.png", dpi=160)
    print(f"Saved data/sim/rake_field_grid.csv, data/sim/rake_field_cube_p{tag}.npz, figures/sim/fig_rake_field.png")


if __name__ == "__main__":
    main()
