#!/usr/bin/env python3
"""Physics-derived route-closure boundary (Component 3).

Replaces the manuscript's illustrative worked example (made-up efficiency/capacity) with one
grounded in the calibrated energy balance of Component 2. The route-scale link is a mass balance:

    throughput  mdot [kg/s] = P_deployed [W] * eta_wallplug / E_per_mass [J/kg]
    closure:    mdot * build_window >= M_required
    => boundary in (eta, P_deployed):  P_deployed * eta  >=  M_required * E_per_mass / window

E_per_mass is NOT invented here: it is the calibrated, radiation-dominated value reproduced
against the two census sources that report energy (Lim 2021 ~18 MJ/kg at 900 s dwell;
Lim 2023 ~72 MJ/kg at 3600 s dwell). The boundary therefore shows, on real energy numbers, why
deployed capacity AND wall-plug efficiency must both be known to decide closure -- and why the
reported lab coordinates (which fix neither) leave the required capacity ambiguous by ~4x.
"""
from __future__ import annotations
import numpy as np

# calibrated energy-per-accepted-mass band from Component 2 (real census-reproducing values)
E_PER_MASS_MJKG = {"Lim2021_JSC1A_900s": 18.0, "Lim2023_highland_3600s": 72.0}


def required_capacity(M_req_kg, window_days, E_per_mass_MJkg, eta):
    """Deployed wall-plug capacity [kW] needed to close, at efficiency eta."""
    window_s = window_days * 24 * 3600.0
    E_per_mass = E_per_mass_MJkg * 1e6
    P_delivered = M_req_kg * E_per_mass / window_s      # W, useful power into process
    return P_delivered / eta / 1000.0                    # kW wall-plug


def main():
    print("== Component 3: physics-derived route-closure boundary ==\n")
    # illustrative-but-declared mission (now the ONLY illustrative inputs; energy-per-mass is real)
    M_req, window = 1000.0, 100.0   # kg of sintered product in 100 days
    print(f"Declared mission: produce {M_req:.0f} kg sintered product in {window:.0f} days.")
    print(f"Energy-per-accepted-mass band (calibrated to real census data): "
          f"{list(E_PER_MASS_MJKG.values())} MJ/kg.\n")

    throughput_needed = M_req / (window * 24)  # kg/h
    print(f"Required throughput = {throughput_needed:.3f} kg/h = {throughput_needed*1000/3600:.4f} g/s.\n")

    print("Deployed wall-plug capacity [kW] required to close, vs efficiency and energy-per-mass:")
    print(f"{'eta':>6}", end="")
    for name in E_PER_MASS_MJKG:
        print(f" {name[:18]:>20}", end="")
    print()
    for eta in [0.05, 0.10, 0.20, 0.40, 0.60]:
        print(f"{eta:>6.2f}", end="")
        for E in E_PER_MASS_MJKG.values():
            print(f" {required_capacity(M_req, window, E, eta):>20.2f}", end="")
        print()

    # the decisive ambiguity: at a plausible efficiency, the two real energy values give a 4x spread
    eta_ref = 0.10
    cap_lo = required_capacity(M_req, window, 18.0, eta_ref)
    cap_hi = required_capacity(M_req, window, 72.0, eta_ref)
    print(f"\n=> At eta={eta_ref:.2f}, the required deployed capacity is {cap_lo:.1f} kW (18 MJ/kg) "
          f"vs {cap_hi:.1f} kW (72 MJ/kg) -- a {cap_hi/cap_lo:.0f}x spread")
    print(f"   driven entirely by the (unreported) dwell/efficiency. Reported power+mass alone")
    print(f"   cannot place the mission on either side of a deployed-capacity budget.")

    # grid for the figure: closure region in (eta, P_cap) for the mid energy value
    eta_grid = np.linspace(0.02, 0.7, 240)
    cap_grid = np.linspace(0.0, 30.0, 240)
    E, C = np.meshgrid(eta_grid, cap_grid)
    boundary_lo = required_capacity(M_req, window, 18.0, eta_grid)  # kW needed vs eta (18 MJ/kg)
    boundary_hi = required_capacity(M_req, window, 72.0, eta_grid)  # (72 MJ/kg)
    np.savez(__file__.replace("03_closure_boundary_physics.py", "out_03_closure.npz"),
             eta_grid=eta_grid, cap_grid=cap_grid,
             boundary_lo_kW=boundary_lo, boundary_hi_kW=boundary_hi,
             M_req=M_req, window_days=window,
             E_lo_MJkg=18.0, E_hi_MJkg=72.0, eta_ref=eta_ref,
             cap_lo=cap_lo, cap_hi=cap_hi)
    print("\nsaved out_03_closure.npz (closure boundaries for the figure)")


if __name__ == "__main__":
    main()
