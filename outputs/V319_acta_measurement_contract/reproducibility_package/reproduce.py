#!/usr/bin/env python3
"""Reproduce the quantitative claims of the manuscript from the bundled data.

Self-contained: standard library only, relative paths only. Run from this directory:
    python reproduce.py

It reproduces (1) the per-coordinate reporting counts of the open-access directed-energy
census (Figure 2 / Section 5), and (2) the worked-example directed-energy closure margins
for completions A and B and the closure-boundary thresholds (Section 7 / Figure 1b).
"""
import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent


def status(cell: str) -> str:
    return cell.strip().upper().split(":")[0].split()[0]


def reproduce_census() -> None:
    rows = list(csv.DictReader((HERE / "census_directed_energy_n7.csv").read_text(encoding="utf-8").splitlines()))
    coords = ["c_input_power", "c_process_time_dwell", "c_processed_sample_mass",
              "c_energy_per_accepted_mass", "c_wall_to_cavity_efficiency", "c_active_source_capacity"]
    n = len(rows)
    print(f"== Open-access directed-energy census (n = {n}) - per-coordinate reporting ==")
    for c in coords:
        rep = sum(1 for r in rows if status(r[c]) == "REPORTED")
        par = sum(1 for r in rows if status(r[c]) == "PARTIAL")
        ab = sum(1 for r in rows if status(r[c]) == "ABSENT")
        print(f"  {c:32s} reported {rep}/{n}  partial {par}  absent {ab}")
    dec = ["c_wall_to_cavity_efficiency", "c_active_source_capacity"]
    assert all(sum(1 for r in rows if status(r[c]) == "ABSENT") == n for c in dec), "decisive coords must be 0/n"
    print("  -> the two decision-controlling coordinates are reported 0/%d (assertion passed)\n" % n)


def reproduce_worked_example() -> None:
    # directed-energy predicate; Lim 2021 reported projection + declared illustrative mission
    P_unit, t_s, m_s = 1.0, 900.0, 0.05          # kW, s, kg  (reported)
    e_star, N_req = 30.0, 5.0                     # MJ/kg, modules (declared illustrative mission)
    eta_thr = (P_unit * t_s) / (1000.0 * m_s * e_star)
    cap_thr = N_req * P_unit
    print("== Worked example (directed-energy predicate on Lim-2021 projection) ==")
    print(f"  closure boundary:  eta >= {eta_thr:.2f}  and  P_cap >= {cap_thr:.1f} kW")
    for name, eta, cap in [("A", 0.50, 3.0), ("B", 0.70, 6.0)]:
        q = (P_unit * t_s) / (1000.0 * eta * m_s)       # MJ/kg
        energy_margin = e_star / q
        source_margin = cap / cap_thr
        closes = (q <= e_star) and (cap >= cap_thr)
        print(f"  completion {name}: eta={eta:.2f}, cap={cap:.0f} kW  ->  "
              f"energy margin {energy_margin:.2f}, source margin {source_margin:.2f}  ->  "
              f"{'CLOSES' if closes else 'does not close'}")
    print("  -> identical reported projection, opposite verdicts (non-identifiable).")


if __name__ == "__main__":
    reproduce_census()
    reproduce_worked_example()
