# Lunar Construction Boundary Identifiability

Public reproducibility package supporting the research article candidate:

**A boundary-identifiability framework for energy comparisons in
lunar-regolith construction experiments**

This repository contains code, derived tables, figure sources, source registries
and runbook material for testing whether heterogeneous engineering records
identify a common energy-per-product quantity.

It intentionally excludes raw third-party data, active submission manuscripts,
submission PDFs, LaTeX submission packages, cover letters, reviewer-response
drafts, internal rounds/logs, credentials and private author/funding files.

## V328 Boundary-Identifiability Scope

The current release adds a self-contained package under
`v328_boundary_identifiability/` with:

- typed source, time, denominator, endpoint and uncertainty states;
- a claim-indexed comparability graph and graph diagnostics;
- point, partial and nonidentification rules;
- reporting-repair coalitions, Shapley gains and mass--energy interaction;
- strict/permissive and leave-one-record-out sensitivity analyses;
- a fixed-margin boundary-clustering diagnostic;
- nine source-visible numerical cases and a denominator rank-ambiguity envelope;
- five figures in SVG, PDF and PNG; and
- the derived inputs needed to regenerate every V328 table and figure.

## Quick Check

```powershell
python -m pip install -r requirements.txt
python v328_boundary_identifiability/data/build_v328_identifiability.py
```

The script contains assertions for the record count, graph edge, isolate count,
repair interaction, numerical-case count and maximum denominator correction.
It requires no private path or copyrighted source PDF.

## Historical V320 Scope

The V320 release updates the public reproducibility assets for the Acta-facing
measurement-contract manuscript after the full-scope cold-read and consistency
repair round:

- active coordinate contract table;
- open-access directed-energy census and PRISMA-style screening log;
- consequentiality framing audit;
- directed-energy worked example;
- constructed witness-register summary and proof-grade state-pair register;
- transient heat-balance, wall-input closure-boundary and efficiency-sensitivity scripts;
- corrected wall-input capacity boundary (`18 MJ/kg -> 2.08 kW`, `72 MJ/kg -> 8.33 kW`)
  without an additional efficiency divisor;
- final exported main and supplementary figure PDFs/PNGs, including normalized
  structural supplementary figures;
- broader sixteen-source-group corpus metadata used in the Supplementary Material;
- DOI-verified bibliography metadata used by the manuscript.

Historical V320 material is retained for provenance. It is not the active
methodological release.

## Repository Boundary

This repository is for reproducibility and source traceability only. It does not
certify a construction route, release raw third-party data, or contain the active
submission manuscript.

Repository URL: https://github.com/Johnsonlijian/2026-LunarConstructionEvidenceMap

Zenodo concept DOI: https://doi.org/10.5281/zenodo.20962960

Current reproducibility scope: V328 boundary-identifiability package, updated on
2026-08-14.
