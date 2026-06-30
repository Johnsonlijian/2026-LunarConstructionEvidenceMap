# Physics computation (Section 5 + Supplementary Section S4)

Reproduces the physical-mechanism results of the main text and the thermal-efficiency
robustness of the Supplementary Material. Requires Python 3 with NumPy and SciPy.

thermal_sintering/
  01_heat_solver_validated.py   implicit FD transient heat solver, validated vs analytical erfc (L2 ~1.7e-5)
  02_regolith_energy_balance.py calibrated transient energy balance; reproduces both reported energy values
                                (18 & 72 MJ/kg) and the energy ledger (re-radiation dominates)
  03_closure_boundary_physics.py physics-derived deployed-capacity closure boundary on the calibrated band
  04_transient_field.py         1-D nonlinear field; sintering confined to a ~2 mm near-surface layer
  05_figures.py                 regenerates Figures P1-P3 (needs matplotlib + the project style helper)
  out_*.npz                     numerical outputs consumed by the figures/verifiers

uq/
  01_efficiency_uq_sensitivity.py  M1 robustness: MC 5-95% efficiency band + one-at-a-time sensitivity
                                   + closed-form (no-fitted-coupling) radiative cross-check
  out_U_band.npz                  band + sensitivity outputs (Supplementary Table S1)

Run from this directory, e.g.:  python thermal_sintering/02_regolith_energy_balance.py
