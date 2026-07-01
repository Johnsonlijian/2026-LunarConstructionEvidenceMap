# V320 Acta Measurement-Contract Reproducibility Package

Release date: 2026-07-01

This release supports the Acta Astronautica candidate manuscript:

**Mission-scale decidability of directed-energy lunar-regolith construction claims: a physics-grounded measurement contract**

## Scope

- Replaces the earlier broad route-feasibility framing with a directed-energy route-closure decidability frame.
- Corrects the physical capacity boundary to treat the Lim energy values as reported wall-input energy per accepted mass.
- Removes the extra wall-plug-to-cavity efficiency divisor from the wall-input capacity calculation.
- Updates the quick-check package so `reproduce.py` reports `18 MJ/kg -> 2.08 kW` and `72 MJ/kg -> 8.33 kW`.
- Adds refreshed physical-mechanism and supplementary figure exports.
- Adds bundled numerical outputs and a Matplotlib-only script for regenerating the supplementary structural/thermal sensitivity figures.
- Updates title, Zenodo metadata, citation metadata, and release README wording to the V320 manuscript scope.

## Public Boundary

This repository excludes the active submission manuscript, submission PDFs, LaTeX build package, cover letter, reviewer-response drafts, internal rounds/logs, raw third-party source material, credentials, and private author/funding files.

## Quick Reproduction

```powershell
python outputs/V320_acta_measurement_contract/reproducibility_package/reproduce.py
python outputs/V320_acta_measurement_contract/reproducibility_package/computation/06_figures_structural_uq.py
```

The first command uses only the Python standard library. The second command regenerates supplementary figure exports from bundled numerical outputs and does not rerun OpenSees.
