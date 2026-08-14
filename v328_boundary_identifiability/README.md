# V328 Boundary-Identifiability Package

This directory is a self-contained, public reproduction package for the typed
boundary, comparability-graph, repair and numerical-case results in the V328
analysis.

## Run

From the repository root:

```powershell
python -m pip install -r requirements.txt
python v328_boundary_identifiability/data/build_v328_identifiability.py
```

Expected headline outputs:

- 16 typed records and 120 possible pairs;
- one identified comparison edge and 14 isolates;
- strict field counts `(2, 3, 10, 15)` for mass, energy, time and endpoint;
- strict mass--energy repair interaction of `+7`;
- nine numerical cases; and
- maximum formed-mass denominator correction `50/22 = 2.2727...`.

## Contents

- `data/inputs/`: derived source registry, coding and numerical-case inputs.
- `data/build_v328_identifiability.py`: deterministic analysis and figure build.
- `data/*_v328.csv` and `data/*_v328.json`: generated outputs.
- `figures/`: five figures in SVG, PDF and PNG.
- `reports/`: computation notes, figure design brief and accessibility text.
- `MANIFEST.sha256`: checksums for every released V328 file.

The package does not include source article PDFs. The graph and diagnostics
describe a purposive 16-record set and one declared target metric; they are not
field-wide prevalence estimates.
