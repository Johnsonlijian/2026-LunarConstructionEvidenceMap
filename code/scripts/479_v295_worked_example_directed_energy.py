#!/usr/bin/env python3
"""V295 worked example: the measurement contract is operational.

Uses the FROZEN directed-energy predicate from 421_v266_proof_grade_witness_register.py
(e_star and evaluate_directed_energy copied verbatim) on the REAL reported coordinates of
Lim et al. (2021, PMC7822870) to show two things on real data:

  (1) Non-identifiability instantiated: holding the reported projection (unit power, dwell,
      sample mass) and a declared illustrative mission boundary fixed, two admissible
      completions that differ ONLY in the two census-absent coordinates
      (active_source_capacity, wall_to_cavity_efficiency) give OPPOSITE closure verdicts.
  (2) The contract resolves it: supplying those two coordinates makes the predicate decide
      with concrete margins.

The supplied efficiency/capacity values and the mission boundary are ILLUSTRATIVE; the
example demonstrates that the predicate is operational, NOT that any real route closes or
fails.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_CSV = ROOT / "source_tables" / "v295_worked_example_directed_energy.csv"
OUT_JSON = ROOT / "outputs" / "v295_worked_example_summary.json"


# --- Frozen predicate (verbatim arithmetic from 421_v266_proof_grade_witness_register.py) ---
def e_star(P_kW: float, tau_days: float, M_kg: float, L: float) -> float:
    return 86.4 * P_kW * tau_days / (L * M_kg)


def evaluate_directed_energy(unit_power, dwell, sample_mass, active_source, eta,
                             P_kW, tau_days, M_kg, L) -> dict:
    tau_s = tau_days * 86400.0
    mission_mass = M_kg
    q_bus = unit_power * dwell / sample_mass / 1000.0 / eta
    active_modules = active_source / unit_power
    required_modules = mission_mass * dwell / (sample_mass * tau_s)
    es = e_star(P_kW, tau_days, M_kg, L)
    energy_margin = es / q_bus
    source_margin = active_modules / required_modules
    return {
        "e_star_mj_kg": es,
        "bus_specific_energy_mj_kg": q_bus,
        "active_modules": active_modules,
        "required_modules": required_modules,
        "energy_margin": energy_margin,
        "source_margin": source_margin,
        "decision_margin": min(energy_margin, source_margin),
        "closed": bool(energy_margin >= 1.0 and source_margin >= 1.0),
    }


def main() -> None:
    # Reported projection: Lim et al. 2021 (PMC7822870), 1000 W run, 900 kJ over 50 g.
    # unit_power 1 kW; dwell 900 s (900 kJ at 1 kW); sample mass 0.05 kg. These three are
    # source-visible; the census records active_source_capacity and wall_to_cavity_efficiency
    # as ABSENT for this source.
    reported = {"unit_power_kw": 1.0, "process_time_s": 900.0, "sample_mass_kg": 0.05}

    # Declared illustrative mission boundary (NOT a certified requirement): 10 kW available
    # power, 100 d build window, 2400 kg target processed mass, loss multiplier 1.2.
    mission = {"P_kW": 10.0, "tau_days": 100.0, "M_kg": 2400.0, "L": 1.2}

    # Two admissible completions that differ ONLY in the two census-absent coordinates.
    completion_fail = {"active_source_kw": 3.0, "wall_to_cavity_eff": 0.50}
    completion_pass = {"active_source_kw": 6.0, "wall_to_cavity_eff": 0.70}

    ev_fail = evaluate_directed_energy(
        reported["unit_power_kw"], reported["process_time_s"], reported["sample_mass_kg"],
        completion_fail["active_source_kw"], completion_fail["wall_to_cavity_eff"], **mission)
    ev_pass = evaluate_directed_energy(
        reported["unit_power_kw"], reported["process_time_s"], reported["sample_mass_kg"],
        completion_pass["active_source_kw"], completion_pass["wall_to_cavity_eff"], **mission)

    # Observed projection (what a downstream reader actually sees) is identical for both
    # completions: same reported source coordinates + same declared mission boundary.
    observed = {**reported, **mission}

    non_identifiable = (ev_fail["closed"] is False) and (ev_pass["closed"] is True)

    rows = [
        {"scenario": "reported_projection_only", **observed,
         "active_source_kw": "ABSENT_IN_SOURCE", "wall_to_cavity_eff": "ABSENT_IN_SOURCE",
         "closure_decidable": "NO_NON_IDENTIFIABLE", "closed": "",
         "energy_margin": "", "source_margin": "", "decision_margin": ""},
        {"scenario": "admissible_completion_A_low_eff_low_capacity", **observed,
         "active_source_kw": completion_fail["active_source_kw"],
         "wall_to_cavity_eff": completion_fail["wall_to_cavity_eff"],
         "closure_decidable": "YES", "closed": ev_fail["closed"],
         "energy_margin": round(ev_fail["energy_margin"], 4),
         "source_margin": round(ev_fail["source_margin"], 4),
         "decision_margin": round(ev_fail["decision_margin"], 4)},
        {"scenario": "admissible_completion_B_higher_eff_higher_capacity", **observed,
         "active_source_kw": completion_pass["active_source_kw"],
         "wall_to_cavity_eff": completion_pass["wall_to_cavity_eff"],
         "closure_decidable": "YES", "closed": ev_pass["closed"],
         "energy_margin": round(ev_pass["energy_margin"], 4),
         "source_margin": round(ev_pass["source_margin"], 4),
         "decision_margin": round(ev_pass["decision_margin"], 4)},
    ]

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    summary = {
        "version": "V295",
        "source": "Lim et al. 2021 (PMC7822870), reported projection",
        "reported_projection": observed,
        "completion_fail": {**completion_fail, **{k: ev_fail[k] for k in
                            ("energy_margin", "source_margin", "decision_margin", "closed")}},
        "completion_pass": {**completion_pass, **{k: ev_pass[k] for k in
                            ("energy_margin", "source_margin", "decision_margin", "closed")}},
        "non_identifiable_from_reported_projection": non_identifiable,
        "required_modules": ev_fail["required_modules"],
        "e_star_mj_kg": ev_fail["e_star_mj_kg"],
        "contract_resolves_decidability": True,
        "boundary": ("Illustrative supplied efficiency/capacity and declared mission boundary; "
                     "demonstrates the predicate is operational, not that any real route closes or fails."),
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
