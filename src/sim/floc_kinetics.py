"""
floc_kinetics.py
----------------
Step 2 of the device simulation (notes/DEVICE_SIMULATION.md): floc growth during the
v7-final mixing sequence (notes/DEVICE_PROTOTYPE.md s3), as a sectional Smoluchowski
population balance (Hounslow et al. 1988 doubling-grid discretisation).

Model
  - Primary particles: dry blend at 0.2 g/L treated as 2 um equivalent spheres of mean
    solid density 3.0 g/cm3 (kaolin 2.6, magnetite 5.2 at 37.5 wt% of the blend, PAC
    hydroxide lighter); magnetite 0.2 um assumed hetero-coagulated onto kaolin within the
    first minute (verification.md s2), so it is not tracked separately.
  - Aggregates are fractal: collision diameter d = d0 * n^(1/Df), Df = 2.2.
  - Kernel: alpha * [ (G/6)(di + dj)^3  +  (2 kT / 3 mu)(di + dj)^2 / (di dj) ].
    With a fractal collision diameter the kernel grows faster than n, so an unbounded
    Smoluchowski system gels in finite time. Breakup is represented by a size cap: pairs
    whose product would exceed the Kolmogorov microscale eta = (nu^3 / (nu G^2))^(1/4)
    (58 um at G 300, 183 um at G 30) do not coalesce. Mass is conserved exactly.
  - Mixing: 60 s at G = 300 s-1, then 15 min at G = 30 s-1; alpha swept 0.1-1.0
    (the collision efficiency is what PAC charge neutralisation and seawater versus fresh
    stock preparation change); seed either dispersed 2 um primaries or a pre-aggregated
    stock of ~10 um aggregates (32 primaries).
  - Diatom cells (8 um, 1e4 cells/mL) are a trace population: first-order attachment to
    aggregates with the same kernel; once attached a cell rides with the clay mass, so the
    fraction of cells in settling-size flocs = attached fraction x clay mass fraction in
    flocs >= 30 um.
  - Settling of an aggregate: Stokes with fractal excess density
    (rho_s - rho_w)(d/d0)^(Df-3); printed so the 0.3-1 mm/s design assumption can be checked.

Outputs
  data/sim/floc_kinetics.csv       time series per alpha
  data/sim/floc_size_dist.csv      mass fraction by size bin at 16 min per alpha (used by rake_capture.py)
  figures/sim/fig_floc_kinetics.png

Run from repo root:
    python src/sim/floc_kinetics.py
"""
import os
import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

KB, T, MU = 1.380649e-23, 293.15, 1.08e-3      # seawater ~20 C
RHO_S, RHO_W = 3000.0, 1025.0
D0, DF = 2.0e-6, 2.2
DOSE = 0.2                                      # kg/m3
NB = 30                                         # bins: n = 2^i primaries
D_CELL, N_CELL = 8.0e-6, 1.0e10                 # 1e4 cells/mL, per m3
ALPHAS = [0.1, 0.35, 1.0]
SEEDS = {"dispersed": 0, "pre-aggregated": 5}
NU = MU / RHO_W
D_SETTLE_MIN = 30e-6
STAGES = [(60.0, 300.0), (900.0, 30.0)]

m0 = RHO_S * np.pi / 6 * D0**3
N0 = DOSE / m0
n_i = 2.0 ** np.arange(NB)
d_i = D0 * n_i ** (1 / DF)

# Hounslow weights on a doubling grid (0-indexed)
W_BIRTH = np.array([[2.0 ** (j - i + 1) if j <= i - 2 else 0.0 for j in range(NB)] for i in range(NB)])
W_LOSS_SMALL = np.array([[2.0 ** (j - i) if j <= i - 1 else 0.0 for j in range(NB)] for i in range(NB)])
UPPER = np.triu(np.ones((NB, NB)))


def eta(G):
    return (NU ** 3 / (NU * G ** 2)) ** 0.25


def kernel(G, alpha):
    di, dj = np.meshgrid(d_i, d_i, indexing="ij")
    ortho = G / 6 * (di + dj) ** 3
    peri = 2 * KB * T / (3 * MU) * (di + dj) ** 2 / (di * dj)
    beta = alpha * (ortho + peri)
    i_max = int(np.searchsorted(d_i, eta(G), side="right")) - 1
    I, J = np.meshgrid(np.arange(NB), np.arange(NB), indexing="ij")
    beta[np.maximum(I, J) + 1 > i_max] = 0.0
    return beta


def rhs_factory(beta):
    diag = np.diag(beta)

    def rhs(t, N):
        N = np.maximum(N, 0)
        BN = beta * N[None, :]
        out = np.zeros(NB)
        # i-1 meets a smaller j: the pair is placed in bin i with weight 2^(j-i+1)
        out[1:] += N[:-1] * (W_BIRTH[1:, :] * BN[:-1, :]).sum(axis=1)
        # i-1 meets i-1: goes to bin i
        out[1:] += 0.5 * diag[:-1] * N[:-1] ** 2
        # i meets a smaller j: loses weight 2^(j-i) from bin i
        out -= N * (W_LOSS_SMALL * BN).sum(axis=1)
        # i meets j >= i: leaves bin i
        out -= N * (UPPER * BN).sum(axis=1)
        return out
    return rhs


def settling_velocity(d):
    drho = (RHO_S - RHO_W) * (d / D0) ** (DF - 3)
    return 9.81 * drho * d ** 2 / (18 * MU)


def mass_quantiles(N):
    mass = N * n_i
    c = np.cumsum(mass) / mass.sum()
    return float(np.interp(0.5, c, d_i)), float(np.interp(0.9, c, d_i))


def run(alpha, seed_bin=0, seed_name="dispersed"):
    N = np.zeros(NB); N[seed_bin] = N0 / n_i[seed_bin]
    t0, rows, cells_free, prevNt = 0.0, [], N_CELL, None
    for dur, G in STAGES:
        sol = solve_ivp(rhs_factory(kernel(G, alpha)), (0, dur), N, method="LSODA",
                        rtol=1e-6, atol=1e-2, dense_output=True, max_step=2.0)
        ts = np.linspace(0, dur, int(dur // 5) + 1)
        bc = alpha * (G / 6 * (D_CELL + d_i) ** 3 + 2 * KB * T / (3 * MU) * (D_CELL + d_i) ** 2 / (D_CELL * d_i))
        for k, t in enumerate(ts):
            Nt = np.maximum(sol.sol(t), 0)
            if k > 0:
                cells_free *= np.exp(-(bc * Nt).sum() * (ts[k] - ts[k - 1]))
            d50, d90 = mass_quantiles(Nt)
            big = (Nt * n_i)[d_i >= D_SETTLE_MIN].sum() / max((Nt * n_i).sum(), 1e-30)
            rows.append(dict(alpha=alpha, seed=seed_name, stage_G=G, t_s=t0 + t, D50_um=d50 * 1e6, D90_um=d90 * 1e6,
                             cells_attached_frac=1 - cells_free / N_CELL,
                             clay_mass_ge30um_frac=big,
                             cells_in_flocs_frac=(1 - cells_free / N_CELL) * big,
                             mass_conserved=(Nt * n_i).sum() / N0,
                             v_settle_D50_mm_s=settling_velocity(d50) * 1000))
        N = np.maximum(sol.sol(dur), 0)
        t0 += dur
    mass = N * n_i
    dist = pd.DataFrame(dict(alpha=alpha, seed=seed_name, bin=np.arange(NB), n_primaries=n_i, d_um=d_i * 1e6,
                             mass_frac=mass / mass.sum(), v_settle_mm_s=settling_velocity(d_i) * 1000))
    return pd.DataFrame(rows), dist


def main():
    os.makedirs("data/sim", exist_ok=True); os.makedirs("figures/sim", exist_ok=True)
    print(f"Primary particles: {N0/1e6:.2e} per mL at {DOSE*1000:.0f} mg/L; cells {N_CELL/1e6:.0e} per mL")
    print(f"Size cap (Kolmogorov eta): {eta(300)*1e6:.0f} um at G 300, {eta(30)*1e6:.0f} um at G 30")
    series, dists = [], []
    for seed_name, seed_bin in SEEDS.items():
        for a in ALPHAS:
            s, d = run(a, seed_bin, seed_name)
            series.append(s); dists.append(d)
            end = s.iloc[-1]
            t50 = s.loc[s.D50_um >= 50, "t_s"]
            print(f"{seed_name:>14} alpha {a:.2f}: D50 {end.D50_um:6.1f} um, D90 {end.D90_um:6.1f} um at 16 min; "
                  f"D50 >= 50 um at {('%.0f s' % t50.iloc[0]) if len(t50) else 'never'}; "
                  f"clay mass in flocs >= 30 um {100*end.clay_mass_ge30um_frac:.0f}%; "
                  f"cells in those flocs {100*end.cells_in_flocs_frac:.0f}%; D50 settles {end.v_settle_D50_mm_s:.2f} mm/s; "
                  f"mass conserved {100*end.mass_conserved:.2f}%")
    S = pd.concat(series); D = pd.concat(dists)
    S.to_csv("data/sim/floc_kinetics.csv", index=False, float_format="%.5g")
    D.to_csv("data/sim/floc_size_dist.csv", index=False, float_format="%.5g")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    for seed_name, ls in (("dispersed", "-"), ("pre-aggregated", "--")):
        for a, c in zip(ALPHAS, ("C0", "C1", "C2")):
            s = S[(S.alpha == a) & (S.seed == seed_name)]
            ax[0].plot(s.t_s / 60, s.D50_um, ls=ls, color=c, label=f"alpha {a}, {seed_name}")
            ax[1].plot(s.t_s / 60, 100 * s.cells_in_flocs_frac, ls=ls, color=c)
    ax[0].axhspan(65, 70, color="0.85", zorder=0); ax[0].text(0.3, 74, "design assumption 65-70 um", fontsize=8)
    for a_ in ax:
        a_.axvline(1, color="0.6", lw=0.8, ls=":")
    ax[0].set_yscale("log"); ax[0].set_xlabel("minutes from dosing"); ax[0].set_ylabel("mass-median floc diameter (um)")
    ax[0].set_title("Floc growth: 60 s at G 300, then G 30")
    ax[1].set_xlabel("minutes from dosing"); ax[1].set_ylabel("% of diatom cells in flocs >= 30 um")
    ax[1].set_title("Cell capture by flocs (1e4 cells/mL)")
    ax[0].legend(fontsize=7); fig.tight_layout(); fig.savefig("figures/sim/fig_floc_kinetics.png", dpi=160)
    print("Saved data/sim/floc_kinetics.csv, data/sim/floc_size_dist.csv, figures/sim/fig_floc_kinetics.png")


if __name__ == "__main__":
    main()
