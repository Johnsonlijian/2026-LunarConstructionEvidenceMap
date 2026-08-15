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

## V329 Boundary-Identifiability Scope

The current release adds a self-contained package under
`v329_boundary_identifiability/` with:

- typed source, time, denominator, endpoint and uncertainty states;
- a diagnostic ladder separating field-presence pairs from exact typed edges;
- a claim-indexed comparability graph and graph diagnostics;
- point, partial and nonidentification rules;
- eligibility-repair coalitions, Shapley gains and mass--energy interaction;
- strict/permissive and leave-one-record-out sensitivity analyses;
- a bounded, post hoc fixed-margin configuration diagnostic;
- nine source-visible numerical cases and a denominator rank-ambiguity envelope;
- five byte-deterministic figures in SVG, PDF and PNG; and
- the inputs and assertions needed to regenerate every V329 table and figure.

## Quick Check

```powershell
python -m pip install -r v329_boundary_identifiability/requirements.txt
python v329_boundary_identifiability/data/build_v329_identifiability.py
```

The script contains assertions for the record count, diagnostic-ladder pair
counts, graph edge, isolate count, eligibility interaction, numerical-case count
and maximum denominator correction. It requires no private path, network access
or copyrighted source PDF.

## Historical V328 Scope

V328 introduced the typed boundary state, claim-indexed graph, repair-game and
partial-identification implementation. V329 retains that provenance while
correcting the distinction between reporting eligibility and returned graph
edges, adding the lower-tier diagnostic ladder, bounding the numerical evidence
to one microwave lineage and making all figure exports byte-deterministic.

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

Current reproducibility scope: V329 boundary-identifiability package, updated on
2026-08-15.
