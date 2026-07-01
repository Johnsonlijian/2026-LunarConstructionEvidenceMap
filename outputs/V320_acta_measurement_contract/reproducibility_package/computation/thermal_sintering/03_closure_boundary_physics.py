#!/usr/bin/env python3
"""Physics-derived route-closure boundary (Component 3).

The two Lim energy values used here are already wall-plug input energy per accepted mass:
P_wall * dwell / mass. They must therefore not be divided by a wall-plug-to-cavity efficiency
again. The route-scale link is the wall-input mass balance:

    throughput  mdot [kg/s] = P_deployed_wall [W] / E_wall_per_mass [J/kg]
    closure:    mdot * build_window >= M_required
    => boundary: P_deployed_wall >= M_required * E_wall_per_mass / window

The boundary therefore shows, on real reported wall-energy numbers, why deployed source
capacity and wall-input energy per accepted mass must both be known to decide closure. The
wall-plug-to-cavity efficiency remains a separate reporting coordinate for interpreting the
thermal ledger and for cases that report delivered/cavity energy rather than wall input; it is
not applied as a second divisor to the Lim wall-input values.
"""
from __future__ import annotations
import numpy as np

# reported wall-input energy-per-accepted-mass band from the two Lim census values
E_PER_MASS_MJKG = {"Lim2021_JSC1A_900s": 18.0, "Lim2023_highland_3600s": 72.0}


def required_capacity_wall(M_req_kg, window_days, E_wall_per_mass_MJkg):
    """Deployed wall-plug capacity [kW] needed to close from wall-input energy."""
    window_s = window_days * 24 * 3600.0
    E_per_mass = E_wall_per_mass_MJkg * 1e6
    return M_req_kg * E_per_mass / window_s / 1000.0


def main():
    print("== Component 3: physics-derived route-closure boundary ==\n")
    # illustrative-but-declared mission (now the ONLY illustrative inputs; energy-per-mass is real)
    M_req, window = 1000.0, 100.0   # kg of sintered product in 100 days
    print(f"Declared mission: produce {M_req:.0f} kg sintered product in {window:.0f} days.")
    print(f"Reported wall-input energy-per-accepted-mass band: "
          f"{list(E_PER_MASS_MJKG.values())} MJ/kg.\n")

    throughput_needed = M_req / (window * 24)  # kg/h
    print(f"Required throughput = {throughput_needed:.3f} kg/h = {throughput_needed*1000/3600:.4f} g/s.\n")

    print("Deployed wall-plug capacity [kW] required to close, vs reported wall energy per mass:")
    print(f"{'E_wall [MJ/kg]':>16} {'P_cap [kW]':>14}")
    for name in E_PER_MASS_MJKG:
        E = E_PER_MASS_MJKG[name]
        print(f"{E:>16.1f} {required_capacity_wall(M_req, window, E):>14.2f}   {name}")

    # the decisive ambiguity: the two real wall-input energy values give a 4x spread
    cap_lo = required_capacity_wall(M_req, window, 18.0)
    cap_hi = required_capacity_wall(M_req, window, 72.0)
    print(f"\n=> The required deployed wall-plug capacity is {cap_lo:.1f} kW (18 MJ/kg) "
          f"vs {cap_hi:.1f} kW (72 MJ/kg) -- a {cap_hi/cap_lo:.0f}x spread")
    print(f"   driven by the reported wall-energy-per-mass band. Reported power+mass alone")
    print(f"   cannot place the mission on either side of a deployed-capacity budget.")

    # grid for the figure: closure region in (E_wall, P_cap)
    energy_grid = np.linspace(5.0, 85.0, 240)
    cap_grid = np.linspace(0.0, 12.0, 240)
    boundary_kW = required_capacity_wall(M_req, window, energy_grid)
    np.savez(__file__.replace("03_closure_boundary_physics.py", "out_03_closure.npz"),
             energy_grid_MJkg=energy_grid, cap_grid=cap_grid,
             boundary_kW=boundary_kW,
             M_req=M_req, window_days=window,
             E_lo_MJkg=18.0, E_hi_MJkg=72.0,
             cap_lo=cap_lo, cap_hi=cap_hi)
    print("\nsaved out_03_closure.npz (closure boundaries for the figure)")


if __name__ == "__main__":
    main()
