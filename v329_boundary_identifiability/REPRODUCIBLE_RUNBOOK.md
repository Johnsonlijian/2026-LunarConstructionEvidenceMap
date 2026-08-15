# Reproducible Runbook

## Environment

The package was verified with Python 3.11.15, Matplotlib 3.11.0, NumPy 2.2.6
and pandas 2.3.3 on Windows. The code uses relative paths and the non-interactive
Matplotlib `Agg` backend.

## Run order

1. Create and activate a clean Python environment.
2. Install `requirements.txt`.
3. Run `python data/build_v329_identifiability.py` from the package root.
4. Confirm that the process exits with code 0.
5. Compare the regenerated files under `data/`, `figures/` and `reports/` with
   the packaged outputs or their SHA-256 hashes.

## Expected outputs

The script writes 15 V329 CSV/JSON outputs, five figures in SVG/PDF/PNG, and a
computation-verification report. Assertions enforce the core numerical claims.
No random sampling is used and no network connection or private path is needed.

## Inputs and provenance

The `data/inputs/` directory contains Crossref metadata, a candidate map,
selection and coding ledgers, a 16-record source audit and two numerical-case
input tables. These are metadata or author-derived coding records, not copies
of published articles. Source locators are included; article PDFs are excluded.

## Known limits

A successful rerun establishes computational reproducibility of the declared
transformations. It does not independently validate source coding, external
validity, population prevalence or the performance of any construction route.
