# V329 Boundary-Identifiability Release

Release date: 2026-08-15

Tag: `v329-boundary-identifiability`

This release adds the self-contained `v329_boundary_identifiability/` package
supporting the boundary-identifiability framework for lunar-regolith
construction experiments.

## Added or corrected

- A diagnostic ladder that distinguishes missingness-only candidate pairs from
  exact typed comparison edges.
- Explicit separation of point identification, bounded identification,
  reporting eligibility and pairwise compatibility.
- Eligibility-coalition and Shapley terminology that does not imply that
  supplying fields automatically creates graph edges.
- Per-axis strict/permissive coding tests and leave-one-record-out sensitivity.
- A bounded, post hoc fixed-margin configuration diagnostic.
- Nine source-visible microwave cases explicitly limited to two records in one
  research lineage.
- Five SVG/PDF/PNG figure sets with fixed metadata and byte-deterministic output.
- Pinned environment metadata, source/redistribution boundaries and SHA-256
  manifests that pass before and after a clean rerun.

## Reproduce

```powershell
python -m pip install -r v329_boundary_identifiability/requirements.txt
python v329_boundary_identifiability/data/build_v329_identifiability.py
```

The release excludes active manuscripts, submission PDFs and LaTeX packages,
cover letters, editorial correspondence, internal review rounds, credentials
and copyrighted source PDFs. A successful rerun establishes computational
reproducibility of the declared transformations, not external validation or
population representativeness.
