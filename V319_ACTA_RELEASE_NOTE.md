# V319 Acta Measurement-Contract Reproducibility Package

Release date: 2026-06-30

This release supports the Acta Astronautica candidate manuscript:

**Hidden coordinates decide lunar-regolith route feasibility: a physics-grounded measurement contract for decidable claims**

## Scope

- Updates the public reproducibility package after the V315-V319 acceptance-maximization rounds.
- Adds the self-contained directed-energy census and worked-example package under `outputs/V319_acta_measurement_contract/reproducibility_package/`.
- Adds transient heat-balance, closure-boundary, and efficiency-sensitivity scripts and computed outputs.
- Adds the broader sixteen-source-group metadata table used in the Supplementary Material.
- Adds final public figure exports for the main and supplementary figure set, including normalized structural supplementary figures.

## Public Boundary

This repository excludes the active submission manuscript, submission PDFs, LaTeX build package, cover letter, reviewer-response drafts, internal rounds/logs, raw third-party source material, credentials, and private author/funding files.

## Quick Reproduction

```powershell
python outputs/V319_acta_measurement_contract/reproducibility_package/reproduce.py
```

The quick check uses only the Python standard library and recomputes the open-access directed-energy census counts and worked-example closure margins from bundled derived CSV files.
