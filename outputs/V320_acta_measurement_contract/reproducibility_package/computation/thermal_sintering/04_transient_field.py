#!/usr/bin/env python3
"""1-D nonlinear transient temperature field in a regolith column (Component 4).

Extends the verified implicit engine (Component 1) to the real nonlinear problem: temperature-
dependent conductivity k(T) and heat capacity c_p(T), an absorbed directed-energy surface flux,
and a nonlinear radiative surface loss eps*sigma*(T^4 - T_amb^4). Backward-Euler in time with
Picard iteration on the nonlinearity each step. Gives the temperature-depth-time field and the
sintered depth (where T exceeds T_sinter), i.e. the spatial picture behind the lumped ledger.

Property model (compacted lunar simulant, literature ranges):
  rho = 1800 kg/m^3 ; c_p(T) = 600..1200 J/kg/K (Hemingway-type) ;
  k(T) = k0 + krad*T^3 (solid + in-pore radiative conduction), ~0.1 -> ~0.4 W/m/K at 1373 K ;
  eps = 0.9 ; T_sinter = 1373 K.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import solve_banded

SIGMA = 5.670374419e-8
T_AMB = 250.0
T_SINTER = 1373.0
EPS = 0.9
RHO = 1800.0


def cp(T):
    return np.clip(600.0 + 0.5 * (T - 300.0), 600.0, 1200.0)


def kcond(T):
    return 0.10 + 1.0e-10 * T**3      # W/m/K: solid + in-pore radiative conduction


def solve_field(L=0.05, nx=201, t_end=900.0, nt=1800,
                P=1000.0, eta_couple=0.60, spot_d=0.056, picard=8):
    """Transient T(x,t); top gets absorbed flux minus radiation, bottom insulated."""
    dx = L / (nx - 1)
    dt = t_end / nt
    x = np.linspace(0, L, nx)
    T = np.full(nx, T_AMB)
    A_spot = np.pi * (spot_d / 2) ** 2
    q_abs = eta_couple * P / A_spot              # W/m^2 absorbed at surface while on
    snapshots, snap_t = [], [0, 60, 180, 450, 900]
    sint_depth = []
    times = np.linspace(0, t_end, nt + 1)

    for n in range(nt):
        Told = T.copy()
        on = (n * dt) <= t_end
        for _ in range(picard):                  # Picard on k(T) and radiation
            k = kcond(T)
            kf = 0.5 * (k[:-1] + k[1:])           # face conductivities
            a = RHO * cp(T) * dx / dt             # capacity per node
            # tridiagonal (banded) assembly for interior + flux BCs
            ab = np.zeros((3, nx))
            rhs = np.zeros(nx)
            # interior
            for i in range(1, nx - 1):
                ab[0, i + 1] = -kf[i] / dx
                ab[2, i - 1] = -kf[i - 1] / dx
                ab[1, i] = a[i] + kf[i] / dx + kf[i - 1] / dx
                rhs[i] = a[i] * Told[i]
            # top (i=0): absorbed flux - radiation (linearized about current T)
            hr = EPS * SIGMA * (T[0] ** 2 + T_AMB ** 2) * (T[0] + T_AMB)  # radiative h
            ab[1, 0] = a[0] / 2 + kf[0] / dx + hr
            ab[0, 1] = -kf[0] / dx
            rhs[0] = a[0] / 2 * Told[0] + (q_abs if on else 0.0) + hr * T_AMB
            # bottom (i=nx-1): insulated
            ab[1, -1] = a[-1] / 2 + kf[-1] / dx
            ab[2, -2] = -kf[-1] / dx
            rhs[-1] = a[-1] / 2 * Told[-1]
            Tnew = solve_banded((1, 1), ab, rhs)
            if np.max(np.abs(Tnew - T)) < 1e-3:
                T = Tnew
                break
            T = Tnew
        # record sintered depth (interpolate the T = T_sinter crossing for a smooth front)
        if T[0] < T_SINTER:
            sint_depth.append(0.0)
        else:
            i = np.where(T >= T_SINTER)[0][-1]
            if i >= nx - 1:
                sint_depth.append(x[-1])
            else:
                frac = (T[i] - T_SINTER) / (T[i] - T[i + 1])
                sint_depth.append(x[i] + frac * dx)
        tnow = (n + 1) * dt
        for st in snap_t:
            if abs(tnow - st) < dt / 2:
                snapshots.append((tnow, T.copy()))
    return x, np.array(times[1:]), np.array(sint_depth), snapshots, q_abs, A_spot


def main():
    print("== Component 4: 1-D nonlinear transient temperature field ==\n")
    x, t, sdepth, snaps, q_abs, A_spot = solve_field()
    print(f"Absorbed surface flux q_abs = {q_abs/1e3:.1f} kW/m^2 (spot area {A_spot*1e4:.1f} cm^2).")
    print(f"Peak surface T = {max(s[1][0] for s in snaps):.0f} K (sinter at {T_SINTER:.0f} K).")
    print(f"Final sintered depth = {sdepth[-1]*1e3:.1f} mm.\n")
    print("Temperature-depth snapshots:")
    print(f"{'t[s]':>6} " + " ".join(f"{d:>6.0f}mm" for d in [0,2,5,10,20]))
    xq = [0, 0.002, 0.005, 0.010, 0.020]
    for tt, Tprof in snaps:
        vals = np.interp(xq, x, Tprof)
        print(f"{tt:>6.0f} " + " ".join(f"{v:>8.0f}" for v in vals))
    print("\n=> Heat does not penetrate: regolith's low conductivity confines sintering to a thin")
    print("   near-surface layer; the deep material stays cold. Throughput is set by how fast this")
    print("   thin layer can be advanced -- i.e. by source power and dwell, not by the coupon alone.")
    np.savez(__file__.replace("04_transient_field.py", "out_04_field.npz"),
             x_mm=x*1e3, t=t, sint_depth_mm=sdepth*1e3,
             snap_t=np.array([s[0] for s in snaps]),
             snap_T=np.array([s[1] for s in snaps]),
             T_sinter=T_SINTER, q_abs_kWm2=q_abs/1e3)
    print("saved out_04_field.npz")


if __name__ == "__main__":
    main()
