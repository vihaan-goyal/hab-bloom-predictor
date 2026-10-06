"""
optimize.py
-----------
Parameter sweep over the device simulation (notes/DEVICE_SIMULATION.md) to find the
lowest-cost settings that still meet the targets.

Stage A (floc_kinetics model, exhaustive):
  dose {0.05, 0.1, 0.2, 0.4} g/L x rapid mix {30, 60} s at G 300 x slow-mix G {15, 30, 60}
  x slow-mix time {5, 10, 15, 20} min x settle time {5, 10, 15} min
  x chemistry scenario: alpha {0.1, 0.35, 1.0} x stock {dispersed, pre-aggregated}.
  Metrics: settled clay fraction (mass reaching the floor of 160 mm water by end of settle),
  cells removed (cells attached x settled mass fraction; cells ride with the clay mass).
  Target: settled >= 0.90 and cells removed >= 0.90. Cost order: dose (aluminium, clay), then time.

Stage B (rake_capture model, capture efficiency of settled flocs):
  B1 geometry: stacks {4, 5, 6, 7} at 33 mm x pass plan {1 pass wall-aligned; 2 passes
     wall-aligned left then right; current v7 plan 3 passes at 11/41/11 mm} at 1 cm/s, 3 mm skid.
  B2 margins at the chosen geometry: speed {1, 2, 4, 8} cm/s x skid {3, 6, 10} mm
     x magnetite fraction of blend {0.10, 0.20, 0.375}.
  Target: capture of settled flocs >= 0.95. Cost order: magnets, passes, magnetite, time.

Outputs: data/sim/opt_floc.csv, data/sim/opt_capture_geometry.csv, data/sim/opt_capture_margins.csv,
         figures/sim/fig_opt.png; printed recommendation.

Run from repo root:  python src/sim/optimize.py
"""
import os
import sys
import time
import itertools
import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
import magpylib as magpy

sys.path.insert(0, os.path.dirname(__file__))
import floc_kinetics as fk  # noqa: E402

H_WATER = 0.160
FLOOR_X, FLOOR_Y = 0.500, 0.250
WALL, TUBE_HALF, PITCH = 0.0032, 0.03175 / 2, 0.033
BR, BLOCK, N_BLOCKS = 1.45, (0.040, 0.020, 0.010), 4
MU, RHO_W, RHO_S = 1.08e-3, 1025.0, 3000.0
DT, N_FLOCS, SEED = 0.004, 2000, 42
RELEASE_S = 180.0          # per-pass lift, release, rinse, reinsert (v7 cycle budget)


# ---------------------------------------------------------------- Stage A
def floc_run(dose, t_rapid, G_slow, alpha, seed_bin):
    N0 = dose / fk.m0
    N = np.zeros(fk.NB); N[seed_bin] = N0 / fk.n_i[seed_bin]
    cells_free, snaps = 1.0, {}
    for dur, G in ((t_rapid, 300.0), (1200.0, G_slow)):
        sol = solve_ivp(fk.rhs_factory(fk.kernel(G, alpha)), (0, dur), N, method="LSODA",
                        rtol=1e-6, atol=1e-2 * dose / 0.2, dense_output=True, max_step=2.0)
        ts = np.arange(0, dur + 1e-9, 5.0)
        bc = alpha * (G / 6 * (fk.D_CELL + fk.d_i) ** 3
                      + 2 * fk.KB * fk.T / (3 * fk.MU) * (fk.D_CELL + fk.d_i) ** 2 / (fk.D_CELL * fk.d_i))
        is_slow = dur == 1200.0
        for k in range(1, len(ts)):
            Nt = np.maximum(sol.sol(ts[k]), 0)
            cells_free *= np.exp(-(bc * Nt).sum() * 5.0)
            if is_slow and int(round(ts[k])) in (300, 600, 900, 1200):
                snaps[int(round(ts[k])) // 60] = (Nt.copy(), 1 - cells_free)
        N = np.maximum(sol.sol(dur), 0)
    return snaps


def stage_a():
    v = fk.settling_velocity(fk.d_i)
    rows = []
    grid = itertools.product([0.05, 0.1, 0.2, 0.4], [30.0, 60.0], [15.0, 30.0, 60.0],
                             [0.1, 0.35, 1.0], [("dispersed", 0), ("pre-aggregated", 5)])
    for dose, t_rapid, G_slow, alpha, (seed_name, seed_bin) in grid:
        snaps = floc_run(dose, t_rapid, G_slow, alpha, seed_bin)
        for t_slow_min, (Nt, attached) in snaps.items():
            mass = Nt * fk.n_i; mass = mass / mass.sum()
            for t_settle_min in (5, 10, 15):
                settled = float((mass * np.minimum(1.0, v * t_settle_min * 60 / H_WATER)).sum())
                rows.append(dict(dose_g_L=dose, t_rapid_s=t_rapid, G_slow=G_slow, t_slow_min=t_slow_min,
                                 t_settle_min=t_settle_min, alpha=alpha, stock=seed_name,
                                 settled_frac=settled, cells_attached=attached, cells_removed=attached * settled,
                                 total_min=t_rapid / 60 + t_slow_min + t_settle_min))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- Stage B
_cubes = {}


def cube(n_stacks, zmin=-0.0140):
    if n_stacks in _cubes:
        return _cubes[n_stacks]
    rake = magpy.Collection(*[magpy.magnet.Cuboid(polarization=(0, 0, -BR), dimension=BLOCK,
                                                  position=(BLOCK[0] * (b + 0.5), PITCH * s, BLOCK[2] / 2))
                              for s in range(n_stacks) for b in range(N_BLOCKS)])
    xs = np.arange(-0.03, 0.19 + 1e-9, 0.001)
    ys = np.arange(-0.03, PITCH * (n_stacks - 1) + 0.03 + 1e-9, 0.001)
    zs = np.arange(zmin, -0.0030 + 1e-9, 0.0005)
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")
    B = rake.getB(np.c_[X.ravel(), Y.ravel(), Z.ravel()]).reshape(len(xs), len(ys), len(zs), 3)
    Bm = np.linalg.norm(B, axis=-1)
    gx, gy, gz = np.gradient(Bm, xs, ys, zs)
    _cubes[n_stacks] = dict(xs=xs, ys=ys, zs=zs, Bm=Bm, gx=gx, gy=gy, gz=gz)
    return _cubes[n_stacks]


_pop = {}


def settled_population(rng):
    if "d" not in _pop:
        dist = pd.read_csv("data/sim/floc_size_dist.csv")
        _pop["d"] = dist[(np.isclose(dist.alpha, 0.35)) & (dist.seed == "pre-aggregated")].sort_values("bin")
    d = _pop["d"]
    p = d.mass_frac.to_numpy() / d.mass_frac.sum()
    v = d.v_settle_mm_s.to_numpy() / 1000
    diam, solids = [], []
    while len(diam) < N_FLOCS:
        k = rng.choice(len(d), size=N_FLOCS, p=p)
        keep = v[k] * 900 >= rng.uniform(0, H_WATER, N_FLOCS)
        n = d.n_primaries.to_numpy()[k][keep]
        diam.extend(fk.D0 * n ** (1 / fk.DF)); solids.extend(n * fk.m0)
    return np.array(diam[:N_FLOCS]), np.array(solids[:N_FLOCS])


def lane_edges(plan, n_stacks):
    span = (n_stacks - 1) * PITCH + 2 * TUBE_HALF
    left, right = 0.0005, FLOOR_Y - 0.0005 - span
    return {"1 pass": [left], "2 pass wall-to-wall": [left, right],
            "v7: 3 pass 11/41/11 mm": [0.011, 0.041, 0.011]}[plan]


def capture(n_stacks, plan, speed, skid, mag_frac, Ms=70.0, rng_seed=SEED):
    rng = np.random.default_rng(rng_seed)
    diam, solids = settled_population(rng)
    C = cube(n_stacks)
    xs, ys, zs = C["xs"], C["ys"], C["zs"]
    floor_z = -(WALL + skid)
    x = rng.uniform(0, FLOOR_X, N_FLOCS); y = rng.uniform(0, FLOOR_Y, N_FLOCS)
    r = diam / 2; z = floor_z + r
    m_mag = mag_frac * solids
    weight = (RHO_S - RHO_W) / RHO_S * solids * 9.81
    drag = 3 * np.pi * MU * diam
    alive = np.ones(N_FLOCS, bool)
    per_pass = []
    edges = lane_edges(plan, n_stacks)
    for edge in edges:
        y_off = edge + TUBE_HALF
        x_r = -0.20
        while x_r < FLOOR_X + 0.03:
            lx, ly = x - x_r, y - y_off
            act = alive & (lx > xs[0]) & (lx < xs[-1]) & (ly > ys[0]) & (ly < ys[-1])
            if act.any():
                a = np.where(act)[0]
                ii = np.clip(np.rint((lx[a] - xs[0]) / 0.001).astype(int), 0, len(xs) - 1)
                jj = np.clip(np.rint((ly[a] - ys[0]) / 0.001).astype(int), 0, len(ys) - 1)
                kk = np.clip(np.rint((z[a] - zs[0]) / 0.0005).astype(int), 0, len(zs) - 1)
                Mf = Ms * np.tanh(C["Bm"][ii, jj, kk] / 0.08) * m_mag[a]
                x[a] = np.clip(x[a] + DT * Mf * C["gx"][ii, jj, kk] / drag[a], 0, FLOOR_X)
                y[a] = np.clip(y[a] + DT * Mf * C["gy"][ii, jj, kk] / drag[a], 0, FLOOR_Y)
                z[a] = np.maximum(z[a] + DT * (Mf * C["gz"][ii, jj, kk] - weight[a]) / drag[a], floor_z + r[a])
                top = z[a] + r[a] >= -WALL
                if top.any():
                    at = a[top]
                    lyt = y[at] - y_off
                    s = np.rint(lyt / PITCH)
                    under = (np.abs(lyt - s * PITCH) <= TUBE_HALF) & (s >= 0) & (s <= n_stacks - 1) \
                        & (x[at] - x_r >= -0.002) & (x[at] - x_r <= 0.162)
                    alive[at[under]] = False
                    gap = at[~under]; z[gap] = -WALL - r[gap]
            x_r += speed * DT
        z[alive] = floor_z + r[alive]
        per_pass.append(1 - alive.mean())
    pass_s = (FLOOR_X + 0.23) / speed + RELEASE_S
    return per_pass, len(edges) * pass_s / 60


def main():
    os.makedirs("data/sim", exist_ok=True); os.makedirs("figures/sim", exist_ok=True)
    t0 = time.time()

    A = stage_a()
    A.to_csv("data/sim/opt_floc.csv", index=False, float_format="%.4g")
    print(f"Stage A: {len(A)} rows in {time.time()-t0:.0f} s", flush=True)
    ok = A[(A.settled_frac >= 0.90) & (A.cells_removed >= 0.90)]
    print("\nStage A, cheapest setting meeting settled >= 90% and cells removed >= 90%, per chemistry scenario:")
    for (alpha, stock), g in A.groupby(["alpha", "stock"]):
        f = ok[(ok.alpha == alpha) & (ok.stock == stock)].sort_values(["dose_g_L", "total_min", "G_slow"])
        if len(f):
            b = f.iloc[0]
            print(f"  alpha {alpha:<4} {stock:>14}: dose {b.dose_g_L} g/L, rapid {b.t_rapid_s:.0f} s, slow G {b.G_slow:.0f} "
                  f"for {b.t_slow_min} min, settle {b.t_settle_min} min -> total {b.total_min:.1f} min; "
                  f"settled {100*b.settled_frac:.0f}%, cells removed {100*b.cells_removed:.0f}%")
        else:
            best = g.sort_values("cells_removed").iloc[-1]
            print(f"  alpha {alpha:<4} {stock:>14}: no setting reaches the target; best is dose {best.dose_g_L}, "
                  f"slow G {best.G_slow:.0f} {best.t_slow_min} min, settle {best.t_settle_min} min -> "
                  f"settled {100*best.settled_frac:.0f}%, cells {100*best.cells_removed:.0f}%")
    keys = ["dose_g_L", "t_rapid_s", "G_slow", "t_slow_min", "t_settle_min"]
    cover = ok.groupby(keys).size().rename("scenarios_met").reset_index()
    cover = cover.merge(A.groupby(keys).total_min.first().reset_index(), on=keys)
    cover = cover.sort_values(["scenarios_met", "dose_g_L", "total_min"], ascending=[False, True, True])
    cover.to_csv("data/sim/opt_floc_robust.csv", index=False)
    print("\nStage A, most robust settings (target met in the most of 6 chemistry scenarios), top 8:")
    print(cover.head(8).to_string(index=False), flush=True)

    t1 = time.time()
    geo = []
    for n in (4, 5, 6, 7):
        cube(n)
        for plan in ("1 pass", "2 pass wall-to-wall", "v7: 3 pass 11/41/11 mm"):
            pp, minutes = capture(n, plan, 0.01, 0.003, 0.375)
            geo.append(dict(stacks=n, plan=plan, capture_final=pp[-1], capture_by_pass=";".join(f"{v:.3f}" for v in pp),
                            raster_min=minutes, magnets=n * N_BLOCKS))
            print(f"  B1 stacks {n}, {plan:>24}: capture by pass {[round(v, 3) for v in pp]}, raster {minutes:.1f} min", flush=True)
    G = pd.DataFrame(geo); G.to_csv("data/sim/opt_capture_geometry.csv", index=False, float_format="%.4g")
    okg = G[G.capture_final >= 0.95].sort_values(["magnets", "raster_min"])
    best_geo = okg.iloc[0] if len(okg) else G.sort_values("capture_final").iloc[-1]
    print(f"\nStage B1 chosen geometry: {best_geo.stacks} stacks ({best_geo.magnets} blocks), {best_geo.plan}, "
          f"capture {100*best_geo.capture_final:.1f}% ({time.time()-t1:.0f} s)", flush=True)

    mar = []
    for speed, skid, mf in itertools.product((0.01, 0.02, 0.04, 0.08), (0.003, 0.006, 0.010), (0.10, 0.20, 0.375)):
        pp, minutes = capture(int(best_geo.stacks), best_geo.plan, speed, skid, mf)
        mar.append(dict(speed_cm_s=speed * 100, skid_mm=skid * 1000, magnetite_frac=mf, capture_final=pp[-1], raster_min=minutes))
        print(f"  B2 speed {speed*100:.0f} cm/s, skid {skid*1000:.0f} mm, magnetite {mf:.3f}: capture {100*pp[-1]:.1f}%, "
              f"raster {minutes:.1f} min", flush=True)
    M = pd.DataFrame(mar); M.to_csv("data/sim/opt_capture_margins.csv", index=False, float_format="%.4g")

    safe = M[(M.skid_mm == 6) & (M.speed_cm_s <= 2) & (M.capture_final >= 0.95)]
    rec_mf = safe.magnetite_frac.min() if len(safe) else 0.375
    rec_speed = safe[safe.magnetite_frac == rec_mf].speed_cm_s.max() if len(safe) else 1
    print(f"\nStage B2 recommendation: magnetite fraction {rec_mf}, speed {rec_speed:.0f} cm/s "
          f"(capture holds >= 95% at 6 mm skid; speeds above 2 cm/s excluded because resuspension is not modelled)")
    print(f"Total runtime {time.time()-t0:.0f} s")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.3))
    sub = A[(A.t_rapid_s == 60) & (A.G_slow == 30) & (A.t_slow_min == 10) & (A.t_settle_min == 10)]
    for (alpha, stock), g in sub.groupby(["alpha", "stock"]):
        ax[0].plot(g.dose_g_L, 100 * g.cells_removed, marker="o", ls="-" if stock == "pre-aggregated" else "--",
                   label=f"alpha {alpha}, {stock}")
    ax[0].axhline(90, color="k", lw=0.7, ls=":"); ax[0].set_xscale("log")
    ax[0].set_xlabel("dose (g/L)"); ax[0].set_ylabel("% cells removed (settled with clay)")
    ax[0].set_title("Dose response: 60 s rapid, G 30 for 10 min, settle 10 min"); ax[0].legend(fontsize=7)
    for plan, mk in zip(G.plan.unique(), "osd"):
        g = G[G.plan == plan]
        ax[1].plot(g.stacks, 100 * g.capture_final, marker=mk, label=plan)
    ax[1].axhline(95, color="k", lw=0.7, ls=":"); ax[1].set_xlabel("magnet stacks"); ax[1].set_ylabel("% of settled flocs captured")
    ax[1].set_title("Rake geometry and pass plan (1 cm/s, 3 mm skid)"); ax[1].legend(fontsize=7)
    for skid, ls in zip((3, 6, 10), ("-", "--", ":")):
        for mf, c in zip((0.10, 0.20, 0.375), ("C0", "C1", "C2")):
            g = M[(M.skid_mm == skid) & (np.isclose(M.magnetite_frac, mf))]
            ax[2].plot(g.speed_cm_s, 100 * g.capture_final, ls=ls, color=c, marker=".", label=f"skid {skid} mm, magnetite {mf}")
    ax[2].axhline(95, color="k", lw=0.7, ls=":"); ax[2].set_xscale("log", base=2)
    ax[2].set_xlabel("rake speed (cm/s)"); ax[2].set_ylabel("% of settled flocs captured")
    ax[2].set_title(f"Margins at {int(best_geo.stacks)} stacks, {best_geo.plan}"); ax[2].legend(fontsize=6, ncol=1)
    fig.tight_layout(); fig.savefig("figures/sim/fig_opt.png", dpi=160)
    print("Saved data/sim/opt_*.csv, figures/sim/fig_opt.png")


if __name__ == "__main__":
    main()
