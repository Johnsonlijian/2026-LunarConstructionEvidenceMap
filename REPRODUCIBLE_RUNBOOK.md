# Reproducible Runbook

1. Install Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

2. Run the core reproducibility check:

```powershell
python code/reproduce_core_checks.py
```

3. Inspect derived data:

- `data/lc_erl_route_assignments.csv`
- `data/parametric_engineering_case.csv`
- `data/processed_mass_envelope.csv`
- `data/lc_erl_codebook_protocol.csv`
- `supplementary_data/Supplementary_Data_6_parametric_case_and_lc_erl_codebook.xlsx`

Raw third-party lunar products are not redistributed. Source URLs are
listed in `DATASETS_AND_LINKS.csv`.
