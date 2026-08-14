# V328 Boundary-Identifiability Release

Release date: 2026-08-14

Tag: `v328-boundary-identifiability`

This release adds the self-contained
`v328_boundary_identifiability/` package supporting the formal comparison
framework for lunar-regolith construction experiments.

## Added

- Typed 16-record boundary audit and claim-indexed comparison graph.
- Fixed-margin structure, strict/permissive coding and deletion sensitivity.
- Repair coalitions, Shapley gains and mass--energy interaction.
- Nine source-visible microwave cases and partial-identification rules.
- Five editable SVG/PDF figures with PNG previews and alt text.
- Nine derived input/metadata files needed by the executable build.
- SHA-256 manifest covering every file in the V328 subpackage.

## Reproduce

```powershell
python -m pip install -r requirements.txt
python v328_boundary_identifiability/data/build_v328_identifiability.py
```

The release excludes active manuscripts, submission files, editorial
correspondence, internal review rounds and copyrighted source PDFs.
