# Lunar Construction Evidence Map

Public reproducibility package for the Acta Astronautica candidate manuscript:

**Hidden coordinates decide lunar-regolith route feasibility: a physics-grounded measurement contract for decidable claims**

This repository contains code, derived tables, figure exports, source registries,
dataset/source links and runbook material supporting a measurement-contract and
evidence-readiness analysis for lunar regolith construction route-closure claims.

It intentionally excludes raw third-party data, active submission manuscripts,
submission PDFs, LaTeX submission packages, cover letters, reviewer-response
drafts, internal rounds/logs, credentials and private author/funding files.

## V319 Acta Scope

The V319 release updates the public reproducibility assets for the Acta-facing
measurement-contract manuscript after the acceptance-maximization and final
kill-path closure rounds:

- active coordinate contract table;
- open-access directed-energy census and PRISMA-style screening log;
- consequentiality framing audit;
- directed-energy worked example;
- constructed witness-register summary and proof-grade state-pair register;
- transient heat-balance, closure-boundary and efficiency-sensitivity scripts;
- final exported main and supplementary figure PDFs/PNGs, including normalized
  structural supplementary figures;
- broader sixteen-source-group corpus metadata used in the Supplementary Material;
- DOI-verified bibliography metadata used by the manuscript.

## Quick Check

```powershell
python outputs/V319_acta_measurement_contract/reproducibility_package/reproduce.py
python code/scripts/479_v295_worked_example_directed_energy.py
python code/scripts/481_fig1_projection_collapse.py
python code/scripts/482_fig3_census_reporting_gap.py
python code/scripts/486_fig4_consequentiality_map.py
```

The first command is self-contained and uses only the Python standard library.
The figure scripts regenerate the worked example and public figure exports from
derived/non-sensitive inputs. Raw third-party source material is not redistributed.

## Repository Boundary

This repository is for reproducibility and source traceability only. It does not
certify a construction route, release raw third-party data, or contain the active
submission manuscript.

Repository URL: https://github.com/Johnsonlijian/2026-LunarConstructionEvidenceMap

Zenodo concept DOI: https://doi.org/10.5281/zenodo.20962960

Current reproducibility scope: V319 Acta Astronautica measurement-contract
candidate package, updated on 2026-06-30.
