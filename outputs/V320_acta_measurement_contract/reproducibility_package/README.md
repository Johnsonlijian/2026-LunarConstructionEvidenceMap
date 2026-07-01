# Reproducibility package

Supporting data and code for the manuscript
**"Mission-scale decidability of directed-energy lunar-regolith construction claims:
a physics-grounded measurement contract."**

The top-level `reproduce.py` is self-contained (Python standard library only) and lets a reviewer
reproduce the census counts, worked-example margins, and wall-input capacity boundary without any
third-party downloads. Optional mechanism and figure scripts under `computation/` use NumPy/SciPy
and Matplotlib. No author-identifying material is included.

## Contents

| File | What it is |
| --- | --- |
| `census_directed_energy_n7.csv` | The open-access full-text census (n = 7). One row per source; one column per directed-energy closure coordinate. Each cell records the reporting status (`REPORTED` / `PARTIAL` / `ABSENT`) and the page-locked value where reported, with the DOI and PMCID for traceability. |
| `prisma_screening_log.csv` | The PRISMA-style screening log: the records returned by the search, the include/exclude decision, and the documented reason for each exclusion. |
| `worked_example_margins.csv` | Per-completion margins for the Section 7 worked example. |
| `cross_route_paywalled_extraction.csv` | Four additional cross-route engineering examples used as bounded stress checks, not as a prevalence estimate. |
| `v282_broader_source_coded_coordinate_audit.csv` | Broader 16-source registry with the nine in-basis route groups coordinate-coded. |
| `v282_broader_source_corpus_metadata.csv` | Metadata for the broader 16-source registry. |
| `reproduce.py` | Recomputes (1) the per-coordinate census counts, (2) the worked-example closure margins and boundary thresholds, and (3) the wall-input capacity boundary from the two reported Lim energy-per-mass values. It asserts the two decision-controlling coordinates are reported 0/7. |
| `computation/thermal_sintering/` | Solver verification, wall-input energy ledger, closure-boundary, field-profile, and main physics-figure scripts and outputs. |
| `computation/uq/` | 3000-sample conditional Monte Carlo sensitivity for the thermal-efficiency band. |
| `computation/06_figures_structural_uq.py` | Regenerates the supplementary structural/thermal sensitivity figure exports from bundled numerical outputs. |
| `computation/structural/*.npz` | Lightweight structural sandbox outputs used for Supplementary Figures S1-S3; these are illustrative sensitivity outputs, not a submission-package structural verification workflow. |
| `computation/gpu_thermal/out_U_eff.npz` | Thermal sensitivity output used by Supplementary Figure S2. |
| `figures/` | Public PDF/PNG exports of the physical-mechanism and supplementary sensitivity figures. |

## How to reproduce

```
python reproduce.py
```

Expected output: input power and dwell reported 7/7; processed-sample scale 6/7 (+1 partial);
energy-per-accepted-mass 2/7; wall-plug-to-cavity efficiency 0/7; deployed active source
capacity 0/7. Worked example: `N_req = 5`, closure boundary `eta >= 0.60` and
`P_cap >= 5 kW`; completion A (eta 0.50, cap 3 kW) does not close (margins 0.83 / 0.60);
completion B (eta 0.70, cap 6 kW) closes (margins 1.17 / 1.20). Physics-derived wall-input
boundary: `18 MJ/kg -> 2.08 kW` and `72 MJ/kg -> 8.33 kW` for the diagnostic
1000 kg / 100 day boundary; no efficiency divisor is applied to already wall-input energy.

## Search and inclusion (census)

The corpus was assembled by a reproducible PubMed Central open-access full-text query; the exact
search term, the twelve returned records, and the PRISMA-style screening are recorded in
`prisma_screening_log.csv`. A source was included if it (i) thermally consolidates lunar regolith
or a regolith simulant with a directed-energy source (microwave or laser) and (ii) has open-access
full text retrievable and quotable from PubMed Central. This is, by construction, an open-access
slice and not an exhaustive multi-database review; paywalled sources are out of scope.

## Closure predicate (worked example)

Directed-energy route-closure predicate, evaluated on the Lim (2021) reported projection
(`P_unit = 1 kW`, `t = 900 s`, `m_s = 0.05 kg`) under a declared illustrative mission boundary
(`e* = 30 MJ/kg`, required active modules `N_req = 5`):

```
energy condition:  q_D = P_unit * t / (1000 * eta * m_s)  <=  e*
source condition:  phi_D = P_cap / P_unit                 >=  N_req
```

The reported projection fixes neither `eta` (wall-plug-to-cavity efficiency) nor `P_cap` (deployed
source capacity); these are exactly the two coordinates the census finds reported 0/7. The
illustrative completions A and B differ only in those two coordinates and return opposite verdicts,
so the same published evidence is compatible with both a pass and a fail state. The mission boundary
and the A/B values are illustrative and assert no closure verdict for any real route.

## Optional figures and mechanism checks

From the package root:

```
python computation/thermal_sintering/01_heat_solver_validated.py
python computation/thermal_sintering/02_regolith_energy_balance.py
python computation/thermal_sintering/03_closure_boundary_physics.py
python computation/thermal_sintering/05_figures.py
python computation/06_figures_structural_uq.py
```

The first four commands reproduce the heat-solver verification, wall-input energy ledger, capacity
boundary, and main physical-mechanism figures. The final command regenerates the supplementary
structural/thermal sensitivity figures from bundled numerical outputs; it does not rerun OpenSees.

## Wall-input capacity boundary

The two Lim energy values are treated as reported wall-plug input energy per accepted mass. The
diagnostic capacity calculation therefore uses:

```
P_cap_wall = M_req * E_wall_per_mass / T_window
```

It does not divide those wall-input values by wall-plug-to-cavity efficiency again. The coupling
efficiency remains a separate reporting coordinate for interpreting the thermal ledger and for cases
that report delivered/cavity energy rather than wall input.
