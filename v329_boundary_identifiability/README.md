# Lunar Construction Boundary Identifiability - V329

Public-safe reproducibility package for the local research-article candidate:

**A boundary-identifiability framework for energy comparisons in
lunar-regolith construction experiments**

The package tests whether heterogeneous engineering records identify a common
energy-per-product quantity. It contains the source registry and coding ledgers,
deterministic analysis code, derived tables, vector figure sources, previews,
environment record and verification notes.

## Scientific boundary

The 16-record audit is purposive and source-locked. It is not a prevalence
estimate, a route ranking or cross-route performance validation. The nine
numerical cases come from two microwave records in one research lineage and
define a sample-observed sensitivity envelope only.

## Quick reproduction

```powershell
python -m pip install -r requirements.txt
python data/build_v329_identifiability.py
```

The script regenerates the V329 derived tables and all five figure sets and
checks the record count, diagnostic-ladder pair counts, the single B08-B09
edge, isolate count, Shapley efficiency, mass-energy interaction, nine-case
count and maximum denominator correction.

## Repository boundary

Source PDFs, active submission files, cover letters, internal review rounds,
credentials and private author records are excluded. DOI and official-source
locators are retained so readers can retrieve the original publications under
their applicable access terms.

Repository: https://github.com/Johnsonlijian/2026-LunarConstructionEvidenceMap

Zenodo concept DOI: https://doi.org/10.5281/zenodo.20962960

Release tag: `v329-boundary-identifiability`

The version DOI is assigned by Zenodo after the GitHub release is published;
the concept DOI above remains the stable package-family identifier.
