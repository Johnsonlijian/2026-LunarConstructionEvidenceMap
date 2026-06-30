# Reproducibility package

Supporting data and code for the manuscript
**"A measurement contract for decidable route-closure claims in lunar regolith construction."**

This package is self-contained (Python standard library only) and lets a reviewer reproduce the
paper's two quantitative claims without any third-party downloads. No author-identifying material
is included.

## Contents

| File | What it is |
| --- | --- |
| `census_directed_energy_n7.csv` | The open-access full-text census (n = 7). One row per source; one column per directed-energy closure coordinate. Each cell records the reporting status (`REPORTED` / `PARTIAL` / `ABSENT`) and the page-locked value where reported, with the DOI and PMCID for traceability. |
| `prisma_screening_log.csv` | The PRISMA-style screening log: the records returned by the search, the include/exclude decision, and the documented reason for each exclusion. |
| `worked_example_margins.csv` | Per-completion margins for the Section 7 worked example. |
| `reproduce.py` | Recomputes (1) the per-coordinate census counts and (2) the worked-example closure margins and boundary thresholds, and asserts the two decision-controlling coordinates are reported 0/7. |

## How to reproduce

```
python reproduce.py
```

Expected output: input power and dwell reported 7/7; processed-sample scale 6/7 (+1 partial);
energy-per-accepted-mass 2/7; wall-plug-to-cavity efficiency 0/7; deployed active source
capacity 0/7. Worked example: closure boundary `eta >= 0.60` and `P_cap >= 5 kW`; completion A
(eta 0.50, cap 3 kW) does not close (margins 0.83 / 0.60); completion B (eta 0.70, cap 6 kW)
closes (margins 1.17 / 1.20).

## Search and inclusion (census)

The corpus was assembled by a reproducible PubMed Central open-access full-text query; the exact
search term, the twelve returned records, and the PRISMA-style screening are recorded in
`prisma_screening_log.csv`. A source was included if it (i) thermally consolidates lunar regolith
or a regolith simulant with a directed-energy source (microwave or laser) and (ii) has open-access
full text retrievable and quotable from PubMed Central. This is, by construction, an open-access
slice and not an exhaustive multi-database review; paywalled sources are out of scope.

## Closure predicate (worked example)

Directed-energy route-closure predicate, evaluated on the Lim (2021) reported projection
(`P_unit = 1 kW`, `t = 900 s`, `m_s = 0.05 kg`) under a declared illustrative mission boundary
(`e* = 30 MJ/kg`, required active modules `N_req = 5`):

```
energy condition:  q_D = P_unit * t / (1000 * eta * m_s)  <=  e*
source condition:  phi_D = P_cap / P_unit                 >=  N_req
```

The reported projection fixes neither `eta` (wall-plug-to-cavity efficiency) nor `P_cap` (deployed
source capacity); these are exactly the two coordinates the census finds reported 0/7. The
illustrative completions A and B differ only in those two coordinates and return opposite verdicts,
so the same published evidence is compatible with both a pass and a fail state. The mission boundary
and the A/B values are illustrative and assert no closure verdict for any real route.
