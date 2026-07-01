# Physics computation (Section 5 + Supplementary Section S4)

Reproduces the physical-mechanism results of the main text and the thermal-efficiency
robustness of the Supplementary Material. Requires Python 3 with NumPy and SciPy.

thermal_sintering/
  01_heat_solver_validated.py   legacy filename; implicit FD transient heat solver verified vs analytical erfc (L2 ~1.7e-5)
  02_regolith_energy_balance.py declared-geometry transient energy ledger using the two reported wall-input
                                energy values (18 & 72 MJ/kg)
  03_closure_boundary_physics.py physics-derived deployed-capacity boundary on the reported wall-energy band
  04_transient_field.py         1-D nonlinear field; sintering confined to a ~2 mm near-surface layer
  05_figures.py                 regenerates Figures P1-P3 (needs matplotlib)
  out_*.npz                     numerical outputs consumed by the figures/verifiers

uq/
  01_efficiency_uq_sensitivity.py  M1 robustness: MC 5-95% efficiency band + one-at-a-time sensitivity
                                   + closed-form (no-fitted-coupling) radiative cross-check
  out_U_band.npz                  band + sensitivity outputs (Supplementary Table S1)

Run from this directory, e.g.:  python thermal_sintering/02_regolith_energy_balance.py
