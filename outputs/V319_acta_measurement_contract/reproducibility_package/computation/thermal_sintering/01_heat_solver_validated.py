#!/usr/bin/env python3
"""Transient 1-D heat-conduction solver + analytical validation (Component 1).

Engine: implicit (backward-Euler) finite-difference for u_t = a u_xx on [0,L],
sparse tridiagonal solve. This module's job is to PROVE the engine is correct before
any regolith physics is added: it reproduces the closed-form semi-infinite-solid
response to a constant surface-temperature step,

    T(x,t) = Ts * erfc( x / (2 sqrt(a t)) ),

and shows second-order spatial / first-order temporal convergence of the L2 error.
Nothing here is illustrative -- the numbers are computed and checked against analysis.
"""
from __future__ import annotations
import numpy as np
from scipy.special import erfc
from scipy.sparse import diags, identity
from scipy.sparse.linalg import splu


def solve_heat_1d(L, nx, t_end, nt, alpha, T_left, T_init=0.0, T_right=0.0):
    """Backward-Euler FD solution of u_t = alpha u_xx, Dirichlet BCs both ends."""
    dx = L / (nx - 1)
    dt = t_end / nt
    r = alpha * dt / dx**2
    u = np.full(nx, float(T_init))
    u[0] = T_left
    u[-1] = T_right
    # interior operator (I - r*D2); D2 = tridiag(1,-2,1)/1
    n = nx - 2
    main = (1 + 2 * r) * np.ones(n)
    off = -r * np.ones(n - 1)
    A = diags([off, main, off], [-1, 0, 1], format="csc")
    lu = splu(A)
    for _ in range(nt):
        rhs = u[1:-1].copy()
        rhs[0] += r * T_left
        rhs[-1] += r * T_right
        u[1:-1] = lu.solve(rhs)
    x = np.linspace(0, L, nx)
    return x, u


def analytical_semiinf(x, t_end, alpha, Ts):
    return Ts * erfc(x / (2.0 * np.sqrt(alpha * t_end)))


def l2_error(num, exact):
    return float(np.sqrt(np.mean((num - exact) ** 2)))


def main():
    # physical-ish benchmark params (units SI); domain long enough to stay semi-infinite
    alpha = 5e-7      # m^2/s (order of a ceramic/regolith diffusivity)
    Ts = 1000.0       # K surface step
    t_end = 600.0     # s
    L = 6.0 * np.sqrt(alpha * t_end)   # far boundary ~6 diffusion lengths -> stays ~0

    print("== Component 1: transient heat solver, analytical validation ==")
    print(f"alpha={alpha:.1e} m^2/s, Ts={Ts} K, t_end={t_end}s, L={L*1e3:.2f} mm\n")

    # --- spatial convergence (fix small dt) ---
    print("Spatial convergence (nt=4000 fixed):")
    print(f"{'nx':>6} {'dx[mm]':>9} {'L2 err[K]':>12} {'ratio':>7}")
    prev = None
    for nx in [21, 41, 81, 161, 321]:
        x, u = solve_heat_1d(L, nx, t_end, 4000, alpha, Ts)
        ex = analytical_semiinf(x, t_end, alpha, Ts)
        e = l2_error(u, ex)
        ratio = (prev / e) if prev else float("nan")
        print(f"{nx:>6} {L/(nx-1)*1e3:>9.3f} {e:>12.4e} {ratio:>7.2f}")
        prev = e

    # --- temporal convergence (fix fine mesh) ---
    print("\nTemporal convergence (nx=321 fixed):")
    print(f"{'nt':>6} {'dt[s]':>9} {'L2 err[K]':>12} {'ratio':>7}")
    prev = None
    for nt in [100, 200, 400, 800, 1600]:
        x, u = solve_heat_1d(L, 321, t_end, nt, alpha, Ts)
        ex = analytical_semiinf(x, t_end, alpha, Ts)
        e = l2_error(u, ex)
        ratio = (prev / e) if prev else float("nan")
        print(f"{nt:>6} {t_end/nt:>9.3f} {e:>12.4e} {ratio:>7.2f}")
        prev = e

    # --- final accuracy + pass/fail gate ---
    x, u = solve_heat_1d(L, 321, t_end, 4000, alpha, Ts)
    ex = analytical_semiinf(x, t_end, alpha, Ts)
    e = l2_error(u, ex)
    rel = e / Ts
    print(f"\nFinest grid (nx=321, nt=4000): L2 error = {e:.4e} K  (relative {rel:.2e})")
    assert rel < 1e-3, "validation FAILED: solver does not match analytical erfc"
    print("VALIDATION PASSED: solver reproduces the analytical erfc response to <0.1% (relative).")

    # save validation arrays for the figure
    out = {"x_mm": x * 1e3, "numerical_K": u, "analytical_K": ex,
           "l2_error_K": e, "relative_error": rel}
    np.savez(__file__.replace("01_heat_solver_validated.py", "out_01_validation.npz"), **out)
    print("saved out_01_validation.npz")


if __name__ == "__main__":
    main()
