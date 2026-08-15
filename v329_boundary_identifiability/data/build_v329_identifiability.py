"""Build the V329 boundary-identifiability analysis and publication figures."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
import itertools
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedFormatter, FixedLocator, NullFormatter
import numpy as np
import pandas as pd


PACKAGE = Path(__file__).resolve().parents[1]
DATA = PACKAGE / "data"
INPUTS = DATA / "inputs"
FIGURES = PACKAGE / "figures"
REPORTS = PACKAGE / "reports"

COORDINATES = ["mass", "energy", "time", "endpoint"]
ROUTE_ORDER = [
    "Binder composite",
    "Cold sintering",
    "Geopolymer",
    "Laser",
    "Microwave",
    "Solar sintering",
    "SPS/ECAS",
    "Thermal",
]
ROUTE_COLORS = {
    "Binder composite": "#8C6BB1",
    "Cold sintering": "#2A9D8F",
    "Geopolymer": "#4C78A8",
    "Laser": "#D1495B",
    "Microwave": "#E9A23B",
    "Solar sintering": "#6A994E",
    "SPS/ECAS": "#7F7F7F",
    "Thermal": "#9C6644",
}


# Typed labels are direct summaries of source-locked fields in the V326 ledger.
# Only B08 and B09 enter the point-identified target-metric comparison class.
TYPE_INFO = {
    "B01": ("unavailable", "feed_paste_only", "multistage_fabrication_schedule", "property_tested", "not_audited", ""),
    "B02": ("equipment_cycle", "mass_unavailable", "equipment_cycle", "property_tested", "not_audited", ""),
    "B03": ("unavailable", "mixture_feed_only", "cure_schedule", "property_tested", "not_audited", ""),
    "B04": ("nominal_optical_setting_partial", "drying_batch_only", "irradiation_duration", "property_tested", "not_audited", ""),
    "B05": ("unavailable", "specimen_mass_not_accepted_yield", "scan_speed_only", "formed_specimen", "not_audited", ""),
    "B06": ("unavailable", "mass_unavailable", "unquantified", "qualitative_formation", "not_audited", ""),
    "B07": ("magnetron_rating_partial", "green_compact_only", "hold_plus_ramp", "formed_specimen", "not_audited", ""),
    "B08": ("nominal_magnetron_input", "accepted_formed_mass", "complete_nominal_input_exposure", "formation_yield", "reporting_resolution_only", "nominal_magnetron_input_per_formed_mass"),
    "B09": ("nominal_magnetron_input", "accepted_formed_mass", "complete_nominal_input_exposure", "formation_yield", "reporting_resolution_only", "nominal_magnetron_input_per_formed_mass"),
    "B10": ("microwave_setting_partial", "green_body_only", "partial_dwell", "property_tested", "not_audited", ""),
    "B11": ("active_microwave_segment_partial", "packed_feed_only", "single_mode_exposure", "property_tested", "not_audited", ""),
    "B12": ("rated_microwave_output_partial", "geometry_only", "preset_unreported", "crack_transition", "not_audited", ""),
    "B13": ("xenon_system_rating_partial", "layer_additions_only", "brick_run", "property_tested", "not_audited", ""),
    "B14": ("unavailable", "charge_mass_unavailable", "hold_only", "property_tested", "not_audited", ""),
    "B15": ("unavailable", "feed_specimen_only", "no_hold", "property_tested", "not_audited", ""),
    "B16": ("unavailable", "tablet_mass_unavailable", "programmed_thermal_cycle", "property_tested", "not_audited", ""),
}


def style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8.5,
            "axes.titlesize": 10.5,
            "axes.labelsize": 9,
            "axes.linewidth": 0.8,
            "xtick.labelsize": 7.5,
            "ytick.labelsize": 7.5,
            "legend.fontsize": 7.5,
            "svg.hashsalt": "lunar-boundary-identifiability-v329",
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def save_figure(fig: plt.Figure, stem: str) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    fixed_date = datetime(2026, 8, 15, tzinfo=timezone.utc)
    for suffix, kwargs in {
        "svg": {
            "metadata": {
                "Date": "2026-08-15",
                "Creator": "V329 deterministic figure build",
            }
        },
        "pdf": {
            "metadata": {
                "Creator": "V329 deterministic figure build",
                "CreationDate": fixed_date,
                "ModDate": fixed_date,
            }
        },
        "png": {
            "dpi": 360,
            "metadata": {"Software": "V329 deterministic figure build"},
        },
    }.items():
        path = FIGURES / f"{stem}.{suffix}"
        fig.savefig(path, bbox_inches="tight", **kwargs)
        if suffix == "svg":
            text = path.read_text(encoding="utf-8")
            normalized = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
            path.write_text(normalized, encoding="utf-8", newline="\n")
    plt.close(fig)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"No rows for {path}")
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def build_typed_audit(audit: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for _, source in audit.iterrows():
        source_plane, denominator, time_support, endpoint, uncertainty, metric_class = TYPE_INFO[source.record_id]
        reported = [
            coordinate
            for coordinate in COORDINATES
            if source[f"strict_{coordinate}_coordinate"] == "reported"
        ]
        rows.append(
            {
                "record_id": source.record_id,
                "short_cite": source.short_cite,
                "route_family": source.route_family,
                "doi": source.doi,
                "strict_reported_coordinates": ";".join(reported),
                "strict_formation_closed": source.strict_formation_closure,
                "source_plane_basis": source_plane,
                "denominator_basis": denominator,
                "time_support_basis": time_support,
                "endpoint_basis": endpoint,
                "uncertainty_basis": uncertainty,
                "target_metric_compatibility_class": metric_class,
                "source_locator": source.source_locator,
                "inference_boundary": (
                    "Typed label summarizes a source-locked V326 field; it does not "
                    "supply a missing measurement or conversion."
                ),
            }
        )
    typed = pd.DataFrame(rows)
    typed.to_csv(DATA / "typed_audit_16_v329.csv", index=False, encoding="utf-8-sig")
    return typed


def build_comparability_graph(typed: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    edges: list[dict[str, object]] = []
    for left, right in itertools.combinations(typed.to_dict("records"), 2):
        same_class = (
            left["target_metric_compatibility_class"]
            and left["target_metric_compatibility_class"] == right["target_metric_compatibility_class"]
        )
        if (
            left["strict_formation_closed"] == "yes"
            and right["strict_formation_closed"] == "yes"
            and same_class
        ):
            edges.append(
                {
                    "record_i": left["record_id"],
                    "record_j": right["record_id"],
                    "compatibility_class": left["target_metric_compatibility_class"],
                    "identified_comparison": "yes",
                    "reason": (
                        "Both records report nominal magnetron input, complete exposure, "
                        "accepted formed mass and a source-defined formation-yield endpoint."
                    ),
                }
            )
    write_csv(DATA / "comparability_edges_v329.csv", edges)

    n = len(typed)
    adjacency = {node: set() for node in typed.record_id}
    for edge in edges:
        adjacency[edge["record_i"]].add(edge["record_j"])
        adjacency[edge["record_j"]].add(edge["record_i"])
    seen: set[str] = set()
    components: list[list[str]] = []
    for node in adjacency:
        if node in seen:
            continue
        stack = [node]
        component: list[str] = []
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            component.append(current)
            stack.extend(adjacency[current] - seen)
        components.append(sorted(component))
    metrics = {
        "records": n,
        "possible_pairs": n * (n - 1) // 2,
        "identified_edges": len(edges),
        "graph_density": 2 * len(edges) / (n * (n - 1)),
        "isolated_records": sum(len(neighbors) == 0 for neighbors in adjacency.values()),
        "connected_components": len(components),
        "largest_component_size": max(map(len, components)),
        "components": sorted(components, key=lambda x: (-len(x), x)),
        "inference_boundary": (
            "Metrics describe the purposive 16-record audit set and one declared "
            "target metric; they are not field-wide prevalence estimates."
        ),
    }
    (DATA / "comparability_graph_metrics_v329.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )
    return pd.DataFrame(edges), metrics


def build_boundary_diagnostic_ladder(
    audit: pd.DataFrame, typed: pd.DataFrame
) -> pd.DataFrame:
    """Separate missingness-only candidate pairs from typed-boundary edges."""

    typed_by_id = typed.set_index("record_id")

    def eligible_ids(rule: str, fields: tuple[str, ...]) -> list[str]:
        mask = pd.Series(True, index=audit.index)
        for field in fields:
            mask &= audit[f"{rule}_{field}_coordinate"].eq("reported")
        return audit.loc[mask, "record_id"].tolist()

    def typed_pairs(ids: list[str], include_denominator: bool) -> list[str]:
        axes = ["source_plane_basis", "time_support_basis", "endpoint_basis"]
        if include_denominator:
            axes.insert(1, "denominator_basis")
        groups: dict[tuple[str, ...], list[str]] = {}
        for record_id in ids:
            key = tuple(str(typed_by_id.loc[record_id, axis]) for axis in axes)
            groups.setdefault(key, []).append(record_id)
        pairs: list[str] = []
        for group in groups.values():
            for left, right in itertools.combinations(sorted(group), 2):
                pairs.append(f"{left}-{right}")
        return sorted(pairs)

    specifications = [
        (
            "strict_energy_time_endpoint",
            "strict",
            ("energy", "time", "endpoint"),
            False,
            "Lower-tier energy record: field presence compared with exact source, time and endpoint labels.",
        ),
        (
            "permissive_energy_time_endpoint",
            "permissive",
            ("energy", "time", "endpoint"),
            False,
            "Sensitivity tier allowing the declared permissive field rules before exact label matching.",
        ),
        (
            "strict_endpoint_product",
            "strict",
            ("mass", "energy", "time", "endpoint"),
            True,
            "Decision tier requiring endpoint-product mass as well as energy, time and endpoint.",
        ),
        (
            "permissive_endpoint_product",
            "permissive",
            ("mass", "energy", "time", "endpoint"),
            True,
            "Decision-tier sensitivity under the declared permissive field rules.",
        ),
    ]

    rows: list[dict[str, object]] = []
    for name, rule, fields, include_denominator, interpretation in specifications:
        ids = eligible_ids(rule, fields)
        pairs = typed_pairs(ids, include_denominator)
        rows.append(
            {
                "diagnostic_tier": name,
                "coding_rule": rule,
                "required_fields": ";".join(fields),
                "eligible_record_count": len(ids),
                "eligible_record_ids": ";".join(ids),
                "missingness_only_candidate_pairs": len(ids) * (len(ids) - 1) // 2,
                "typed_boundary_edges": len(pairs),
                "typed_edge_ids": ";".join(pairs),
                "interpretation": interpretation,
                "inference_boundary": (
                    "The missingness-only count is a candidate-pair baseline. "
                    "A typed edge additionally requires exact observed boundary labels; "
                    "neither count estimates literature prevalence."
                ),
            }
        )
    ladder = pd.DataFrame(rows)
    ladder.to_csv(
        DATA / "boundary_diagnostic_ladder_v329.csv",
        index=False,
        encoding="utf-8-sig",
    )
    return ladder


def closure_count(audit: pd.DataFrame, repair: frozenset[str]) -> tuple[int, list[str]]:
    return closure_count_for_rule(audit, repair, "strict")


def closure_count_for_rule(
    audit: pd.DataFrame, repair: frozenset[str], rule: str
) -> tuple[int, list[str]]:
    if rule not in {"strict", "permissive"}:
        raise ValueError(f"Unsupported coding rule: {rule}")
    closed: list[str] = []
    for _, row in audit.iterrows():
        if all(
            coordinate in repair
            or row[f"{rule}_{coordinate}_coordinate"] == "reported"
            for coordinate in COORDINATES
        ):
            closed.append(row.record_id)
    return len(closed), closed


def shapley_for_rule(audit: pd.DataFrame, rule: str) -> tuple[dict[str, float], int]:
    def value(fields: set[str]) -> int:
        return closure_count_for_rule(audit, frozenset(fields), rule)[0]

    n_fields = len(COORDINATES)
    gains: dict[str, float] = {}
    for coordinate in COORDINATES:
        others = [item for item in COORDINATES if item != coordinate]
        phi = 0.0
        for size in range(len(others) + 1):
            for subset in itertools.combinations(others, size):
                base = set(subset)
                weight = (
                    math.factorial(size)
                    * math.factorial(n_fields - size - 1)
                    / math.factorial(n_fields)
                )
                phi += weight * (value(base | {coordinate}) - value(base))
        gains[coordinate] = phi

    interaction = (
        value({"mass", "energy"})
        - value({"mass"})
        - value({"energy"})
        + value(set())
    )
    return gains, interaction


def build_repair_analysis(audit: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, int]:
    coalitions: list[dict[str, object]] = []
    for size in range(len(COORDINATES) + 1):
        for subset in itertools.combinations(COORDINATES, size):
            repair = frozenset(subset)
            count, ids = closure_count(audit, repair)
            route_sizes = audit[audit.record_id.isin(ids)].groupby("route_family").size()
            within_route_pairs = int(sum(n * (n - 1) // 2 for n in route_sizes))
            coalitions.append(
                {
                    "repair_fields": ";".join(subset) if subset else "none",
                    "field_count": size,
                    "formation_closed_records_upper_bound": count,
                    "all_pairs_upper_bound": count * (count - 1) // 2,
                    "within_route_pairs_upper_bound": within_route_pairs,
                    "closed_record_ids": ";".join(ids),
                    "inference_boundary": (
                        "Optimistic reporting-availability upper bound. A supplied field "
                        "is not assumed to be numerically compatible across source planes."
                    ),
                }
            )
    coalition_df = pd.DataFrame(coalitions)
    coalition_df.to_csv(DATA / "repair_coalitions_v329.csv", index=False, encoding="utf-8-sig")

    def value(fields: set[str]) -> int:
        return closure_count(audit, frozenset(fields))[0]

    shapley_rows: list[dict[str, object]] = []
    n_fields = len(COORDINATES)
    for coordinate in COORDINATES:
        others = [item for item in COORDINATES if item != coordinate]
        phi = 0.0
        for size in range(len(others) + 1):
            for subset in itertools.combinations(others, size):
                base = set(subset)
                weight = (
                    math.factorial(size)
                    * math.factorial(n_fields - size - 1)
                    / math.factorial(n_fields)
                )
                phi += weight * (value(base | {coordinate}) - value(base))
        shapley_rows.append(
            {
                "coordinate": coordinate,
                "shapley_closure_gain": round(phi, 6),
                "share_of_14_recoverable_closures": round(phi / 14, 6),
                "interpretation": (
                    "Order-averaged marginal contribution to the optimistic closure "
                    "upper bound; not a causal value or measurement cost."
                ),
            }
        )
    shapley_df = pd.DataFrame(shapley_rows)
    shapley_df.to_csv(DATA / "repair_shapley_v329.csv", index=False, encoding="utf-8-sig")

    mass_energy_interaction = (
        value({"mass", "energy"})
        - value({"mass"})
        - value({"energy"})
        + value(set())
    )
    return coalition_df, shapley_df, mass_energy_interaction


def build_rule_and_deletion_sensitivity(audit: pd.DataFrame) -> dict[str, object]:
    rule_rows: list[dict[str, object]] = []
    shapley_rows: list[dict[str, object]] = []
    deletion_rows: list[dict[str, object]] = []

    for rule in ("strict", "permissive"):
        reported_counts = {
            coordinate: int(
                (audit[f"{rule}_{coordinate}_coordinate"] == "reported").sum()
            )
            for coordinate in COORDINATES
        }
        closed_count, closed_ids = closure_count_for_rule(audit, frozenset(), rule)
        gains, interaction = shapley_for_rule(audit, rule)
        rule_rows.append(
            {
                "coding_rule": rule,
                **{f"reported_{coordinate}": reported_counts[coordinate] for coordinate in COORDINATES},
                "formation_closed_records": closed_count,
                "closed_record_ids": ";".join(closed_ids),
                "mass_energy_interaction": interaction,
                "inference_boundary": (
                    "Counts describe the purposive audit set; rule sensitivity is not "
                    "an inter-rater reliability estimate."
                ),
            }
        )
        for coordinate in COORDINATES:
            shapley_rows.append(
                {
                    "coding_rule": rule,
                    "coordinate": coordinate,
                    "shapley_closure_gain": round(gains[coordinate], 6),
                    "interpretation": (
                        "Order-averaged marginal contribution to the optimistic closure "
                        "upper bound under the stated coding rule."
                    ),
                }
            )

        for held_out in audit.record_id:
            reduced = audit[audit.record_id != held_out].copy()
            reduced_gains, reduced_interaction = shapley_for_rule(reduced, rule)
            reduced_closed, _ = closure_count_for_rule(reduced, frozenset(), rule)
            ordered = sorted(
                COORDINATES, key=lambda coordinate: (-reduced_gains[coordinate], coordinate)
            )
            for coordinate in COORDINATES:
                deletion_rows.append(
                    {
                        "coding_rule": rule,
                        "held_out_record": held_out,
                        "coordinate": coordinate,
                        "shapley_closure_gain": round(reduced_gains[coordinate], 6),
                        "coordinate_rank": ordered.index(coordinate) + 1,
                        "formation_closed_records_after_deletion": reduced_closed,
                        "mass_energy_interaction_after_deletion": reduced_interaction,
                    }
                )

    rule_df = pd.DataFrame(rule_rows)
    rule_df.to_csv(DATA / "coding_rule_sensitivity_v329.csv", index=False, encoding="utf-8-sig")
    shapley_df = pd.DataFrame(shapley_rows)
    shapley_df.to_csv(
        DATA / "repair_shapley_rule_sensitivity_v329.csv", index=False, encoding="utf-8-sig"
    )
    deletion_df = pd.DataFrame(deletion_rows)
    deletion_df.to_csv(
        DATA / "leave_one_record_out_shapley_v329.csv", index=False, encoding="utf-8-sig"
    )

    loo_summary: list[dict[str, object]] = []
    for rule in ("strict", "permissive"):
        subset = deletion_df[deletion_df.coding_rule == rule]
        for coordinate in COORDINATES:
            values = subset[subset.coordinate == coordinate].shapley_closure_gain
            ranks = subset[subset.coordinate == coordinate].coordinate_rank
            loo_summary.append(
                {
                    "coding_rule": rule,
                    "coordinate": coordinate,
                    "leave_one_out_gain_min": float(values.min()),
                    "leave_one_out_gain_max": float(values.max()),
                    "leave_one_out_rank_min": int(ranks.min()),
                    "leave_one_out_rank_max": int(ranks.max()),
                }
            )
    pd.DataFrame(loo_summary).to_csv(
        DATA / "leave_one_record_out_summary_v329.csv", index=False, encoding="utf-8-sig"
    )

    strict_counts = [
        int((audit[f"strict_{coordinate}_coordinate"] == "reported").sum())
        for coordinate in COORDINATES
    ]
    n_records = len(audit)
    limiting_count = min(strict_counts)
    limiting_index = strict_counts.index(limiting_count)
    expected_closed = n_records * math.prod(count / n_records for count in strict_counts)
    probability_of_maximum_overlap = math.prod(
        math.comb(count, limiting_count) / math.comb(n_records, limiting_count)
        for index, count in enumerate(strict_counts)
        if index != limiting_index
    )
    observed_closed, _ = closure_count_for_rule(audit, frozenset(), "strict")
    null_diagnostic = {
        "records": n_records,
        "strict_reported_field_counts": dict(zip(COORDINATES, strict_counts)),
        "observed_fully_closed_records": observed_closed,
        "maximum_possible_fully_closed_records_given_margins": limiting_count,
        "expected_fully_closed_records_under_independent_field_allocation": expected_closed,
        "observed_to_independent_expectation_ratio": observed_closed / expected_closed,
        "conditional_probability_of_maximum_overlap_given_independent_fixed_margins": probability_of_maximum_overlap,
        "interpretation": (
            "Finite-configuration diagnostic only. It shows that the same two records "
            "concentrate all four reported coordinates more strongly than independent "
            "field allocation with the observed margins; it is not a population p-value."
        ),
    }
    (DATA / "boundary_clustering_null_diagnostic_v329.json").write_text(
        json.dumps(null_diagnostic, indent=2), encoding="utf-8"
    )

    summary = {
        "strict_closed_records": int(rule_df.loc[rule_df.coding_rule == "strict", "formation_closed_records"].iloc[0]),
        "permissive_closed_records": int(rule_df.loc[rule_df.coding_rule == "permissive", "formation_closed_records"].iloc[0]),
        "strict_mass_energy_interaction": int(rule_df.loc[rule_df.coding_rule == "strict", "mass_energy_interaction"].iloc[0]),
        "permissive_mass_energy_interaction": int(rule_df.loc[rule_df.coding_rule == "permissive", "mass_energy_interaction"].iloc[0]),
        "strict_expected_closed_under_independent_field_allocation": expected_closed,
        "strict_probability_of_maximum_overlap": probability_of_maximum_overlap,
    }
    (DATA / "rule_and_deletion_sensitivity_summary_v329.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary


def build_numeric_cases() -> tuple[pd.DataFrame, dict[str, object]]:
    b08 = pd.read_csv(INPUTS / "lim2021_best_case_nominal_input_v326.csv")
    b09 = pd.read_csv(INPUTS / "lim2023_vacuum_nominal_input_v326.csv")
    rows: list[dict[str, object]] = []
    for _, row in b08.iterrows():
        feed = float(row.source_reported_starting_mass_g)
        formed = float(row.source_selected_maximum_hardened_mass_g)
        energy = float(row.source_reported_nominal_input_kJ)
        rows.append(
            {
                "case_id": f"B08_{int(row.nominal_magnetron_input_setting_W)}W",
                "record_id": "B08",
                "year": 2021,
                "simulant": "JSC-1A",
                "nominal_input_setting_W": row.nominal_magnetron_input_setting_W,
                "nominal_input_energy_kJ": energy,
                "feed_mass_g": feed,
                "formed_mass_g": formed,
                "yield_fraction": formed / feed,
                "feed_normalized_input_MJ_kg": energy / feed,
                "formed_normalized_input_MJ_kg": energy / formed,
                "denominator_correction_factor": feed / formed,
                "formed_intensity_lower_resolution_MJ_kg": row.one_gram_reporting_resolution_lower_MJ_per_kg,
                "formed_intensity_upper_resolution_MJ_kg": row.one_gram_reporting_resolution_upper_MJ_per_kg,
                "selection_boundary": row.selection_boundary,
            }
        )
    for _, row in b09.iterrows():
        feed = float(row.source_reported_starting_mass_g)
        formed = float(row.source_reported_sintered_or_molten_mass_g)
        energy = float(row.source_reported_nominal_input_kJ)
        rows.append(
            {
                "case_id": f"B09_{row.simulant}_{int(row.nominal_magnetron_input_setting_W)}W",
                "record_id": "B09",
                "year": 2023,
                "simulant": row.simulant,
                "nominal_input_setting_W": row.nominal_magnetron_input_setting_W,
                "nominal_input_energy_kJ": energy,
                "feed_mass_g": feed,
                "formed_mass_g": formed,
                "yield_fraction": formed / feed,
                "feed_normalized_input_MJ_kg": energy / feed,
                "formed_normalized_input_MJ_kg": energy / formed,
                "denominator_correction_factor": feed / formed,
                "formed_intensity_lower_resolution_MJ_kg": row.one_gram_reporting_resolution_lower_MJ_per_kg,
                "formed_intensity_upper_resolution_MJ_kg": row.one_gram_reporting_resolution_upper_MJ_per_kg,
                "selection_boundary": row.selection_boundary,
            }
        )
    cases = pd.DataFrame(rows).sort_values(["record_id", "nominal_input_setting_W"])
    cases.to_csv(DATA / "numeric_cases_9_v329.csv", index=False, encoding="utf-8-sig")

    jsc = cases[(cases.simulant == "JSC-1A") & (cases.nominal_input_energy_kJ == 900)]
    correction_max = float(cases.denominator_correction_factor.max())
    summary = {
        "numeric_cases": len(cases),
        "jsc_900kJ_50g_cases": len(jsc),
        "jsc_feed_normalized_unique_MJ_kg": sorted(jsc.feed_normalized_input_MJ_kg.unique().tolist()),
        "jsc_formed_normalized_range_MJ_kg": [
            float(jsc.formed_normalized_input_MJ_kg.min()),
            float(jsc.formed_normalized_input_MJ_kg.max()),
        ],
        "observed_yield_range": [float(cases.yield_fraction.min()), float(cases.yield_fraction.max())],
        "observed_denominator_correction_range": [
            float(cases.denominator_correction_factor.min()),
            correction_max,
        ],
        "sample_observed_rank_ambiguity_nominal_ratio": [1 / correction_max, correction_max],
        "inference_boundary": (
            "The ambiguity interval uses only the correction-factor range observed in "
            "these nine source-selected microwave cases; it is not a cross-route bound."
        ),
    }
    (DATA / "numeric_case_summary_v329.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return cases, summary


def build_partial_identification_rules() -> None:
    rows = [
        {
            "case": "point_yield_and_native_energy",
            "available_information": "E_n, F and y are source-visible at aligned boundaries",
            "formed_product_intensity_set": "{E_n/(y F)}",
            "identification_state": "point at the declared native source plane",
        },
        {
            "case": "bounded_yield",
            "available_information": "E_n, F and y in [y_L,y_U], with 0<y_L<=y_U<=1",
            "formed_product_intensity_set": "[E_n/(y_U F), E_n/(y_L F)]",
            "identification_state": "partially identified",
        },
        {
            "case": "feed_only",
            "available_information": "E_n and F; only 0<y<=1 is known",
            "formed_product_intensity_set": "[E_n/F, infinity)",
            "identification_state": "lower-bounded, not point identified",
        },
        {
            "case": "wall_plug_product_boundary",
            "available_information": "E_w=E_n/eta_g+E_anc, 0<eta_g<=1, E_anc>=0, 0<y<=1",
            "formed_product_intensity_set": "[E_n/F, infinity) unless finite bounds are measured",
            "identification_state": "nonidentified for cross-plane route ranking",
        },
    ]
    write_csv(DATA / "partial_identification_rules_v329.csv", rows)


def figure_1_boundary_mechanism() -> None:
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.5)
    ax.axis("off")

    def box(x: float, y: float, w: float, h: float, title: str, detail: str, color: str) -> None:
        ax.add_patch(Rectangle((x, y), w, h, facecolor=color, edgecolor="#303030", linewidth=0.9))
        ax.text(x + w / 2, y + h * 0.65, title, ha="center", va="center", fontweight="bold", fontsize=7.4, linespacing=0.95)
        ax.text(x + w / 2, y + h * 0.24, detail, ha="center", va="center", fontsize=6.6, color="#303030")

    def arrow(x1: float, y1: float, x2: float, y2: float, label: str) -> None:
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=10, linewidth=1.1, color="#333333"))
        label_y = 5.48 if y1 > 3 else 2.55
        ax.text((x1 + x2) / 2, label_y, label, ha="center", va="center", fontsize=6.6)

    box(0.35, 4.05, 2.05, 1.05, "Wall-plug\nenergy", r"$E_w$", "#E8F1F2")
    box(3.25, 4.05, 2.15, 1.05, "Native source\nplane", r"reported $E_n$", "#F2E8CF")
    box(6.20, 4.05, 2.35, 1.05, "Process/material\nplane", "absorbed or delivered", "#F8E1DF")
    arrow(2.40, 4.58, 3.25, 4.58, r"conversion $\eta_g$ + ancillaries")
    arrow(5.40, 4.58, 6.20, 4.58, "route coupling")

    box(0.35, 1.05, 2.05, 1.05, "Feed mass", r"$F$", "#E8F1F2")
    box(3.25, 1.05, 2.15, 1.05, "Formed mass", r"$M_f=y_fF$", "#DDEEDB")
    box(6.20, 1.05, 2.35, 1.05, "Endpoint-qualified\nmass", r"$M_q=a_qM_f=y_qF$", "#E6E0F0")
    arrow(2.40, 1.58, 3.25, 1.58, r"formation yield $y_f$")
    arrow(5.40, 1.58, 6.20, 1.58, r"endpoint acceptance $a_q$")

    ax.text(9.85, 4.85, "Point identified", ha="center", fontweight="bold", color="#1B6F68")
    ax.text(8.80, 4.30, r"$y_q,\eta_g,E_{anc}$ measured", ha="left", fontsize=7.1)
    ax.text(9.85, 3.25, "Partially identified", ha="center", fontweight="bold", color="#9C6B12")
    ax.text(8.80, 2.70, "finite source-visible bounds", ha="left", fontsize=7.1)
    ax.text(9.85, 1.65, "Nonidentified", ha="center", fontweight="bold", color="#B23A48")
    ax.text(8.80, 1.10, "conversion or yield unbounded", ha="left", fontsize=6.7)
    ax.text(
        5.25,
        0.22,
        r"$e_{w,q}=\dfrac{E_w}{M_q}=\dfrac{E_n/\eta_g+E_{anc}}{y_qF}$, only when all terms share the declared time and endpoint boundary.",
        ha="center",
        va="center",
        fontsize=8.2,
    )
    ax.set_title("Boundary factors determine whether an energy-per-product comparison is identified", loc="left", fontweight="bold")
    save_figure(fig, "Figure_1_boundary_identifiability_mechanism")


def figure_2_graph(
    typed: pd.DataFrame,
    edges: pd.DataFrame,
    metrics: dict[str, object],
    ladder: pd.DataFrame,
) -> None:
    fig, axes = plt.subplots(
        1,
        2,
        figsize=(7.2, 4.35),
        gridspec_kw={"width_ratios": [0.9, 1.55]},
    )

    ordered = typed.sort_values("record_id").reset_index(drop=True)
    ax = axes[0]
    for row_index, row in ordered.iterrows():
        reported = set(filter(None, str(row.strict_reported_coordinates).split(";")))
        ax.add_patch(
            Rectangle(
                (-0.72, row_index - 0.42),
                0.24,
                0.84,
                facecolor=ROUTE_COLORS[row.route_family],
                edgecolor="none",
            )
        )
        for column_index, coordinate in enumerate(COORDINATES):
            present = coordinate in reported
            ax.add_patch(
                Rectangle(
                    (column_index - 0.42, row_index - 0.42),
                    0.84,
                    0.84,
                    facecolor="#1F6F78" if present else "#F3F3F3",
                    edgecolor="white",
                    linewidth=0.8,
                )
            )
            if present:
                ax.text(column_index, row_index, "●", ha="center", va="center", color="white", fontsize=5.8)
    ax.set_xlim(-0.82, len(COORDINATES) - 0.5)
    ax.set_ylim(len(ordered) - 0.45, -0.55)
    ax.set_xticks(range(len(COORDINATES)), ["mass", "energy", "time", "endpoint"], rotation=35, ha="right")
    ax.set_yticks(range(len(ordered)), ordered.record_id)
    ax.tick_params(axis="both", length=0, labelsize=6.1)
    ax.set_title("a  Strict coordinate availability", loc="left", fontweight="bold", pad=12)
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax = axes[1]
    nonclosed = ordered.loc[ordered.strict_formation_closed.ne("yes"), "record_id"].tolist()
    angles = np.linspace(0, 2 * np.pi, len(nonclosed), endpoint=False)
    positions = {
        record_id: (2.2 * np.cos(angle), 1.35 * np.sin(angle))
        for record_id, angle in zip(nonclosed, angles)
    }
    positions["B08"] = (-0.62, 0.0)
    positions["B09"] = (0.62, 0.0)

    for _, edge in edges.iterrows():
        x1, y1 = positions[edge.record_i]
        x2, y2 = positions[edge.record_j]
        ax.plot([x1, x2], [y1, y2], color="#1F6F78", linewidth=2.6, zorder=1)

    for _, row in ordered.iterrows():
        x, y = positions[row.record_id]
        closed = row.strict_formation_closed == "yes"
        ax.scatter(
            x,
            y,
            s=145 if closed else 72,
            color=ROUTE_COLORS[row.route_family] if closed else "#F7F7F7",
            edgecolor=ROUTE_COLORS[row.route_family],
            linewidth=1.3 if closed else 1.0,
            zorder=2,
        )
        ax.text(
            x,
            y,
            row.record_id,
            ha="center",
            va="center",
            fontsize=5.8,
            fontweight="bold" if closed else "normal",
        )

    ladder_by_name = ladder.set_index("diagnostic_tier")
    strict_etq = ladder_by_name.loc["strict_energy_time_endpoint"]
    permissive_etq = ladder_by_name.loc["permissive_energy_time_endpoint"]
    ax.text(
        0.5,
        0.985,
        f"1 typed edge / {metrics['possible_pairs']} audit-frame pairs | 14 isolates",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=7.0,
        fontweight="bold",
    )
    ax.text(
        0.5,
        0.91,
        "fixed claim: nominal magnetron input per accepted formed mass",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=5.9,
        color="#444444",
    )
    ax.text(
        0.5,
        0.035,
        (
            "Lower-tier E+T+Q field presence flags "
            f"{strict_etq.missingness_only_candidate_pairs} strict / "
            f"{permissive_etq.missingness_only_candidate_pairs} permissive pairs; "
            "exact typed boundaries retain 1 / 1."
        ),
        transform=ax.transAxes,
        ha="center",
        va="bottom",
        fontsize=5.7,
        color="#333333",
    )
    ax.set_xlim(-2.65, 2.65)
    ax.set_ylim(-2.15, 2.15)
    ax.axis("off")
    ax.set_title("b  Claim-indexed compatibility", loc="left", fontweight="bold")

    legend_handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="none",
            markerfacecolor="white",
            markeredgecolor=ROUTE_COLORS[route],
            markersize=4.5,
            label=route,
        )
        for route in ROUTE_ORDER
    ]
    fig.legend(
        handles=legend_handles,
        loc="lower center",
        ncol=4,
        frameon=False,
        fontsize=5.4,
        bbox_to_anchor=(0.5, 0.0),
        handletextpad=0.25,
        columnspacing=0.8,
    )
    fig.suptitle(
        "Field co-occurrence and boundary typing leave one admissible pair",
        x=0.01,
        ha="left",
        fontweight="bold",
        fontsize=10.5,
    )
    fig.subplots_adjust(left=0.09, right=0.99, bottom=0.16, top=0.83, wspace=0.26)
    save_figure(fig, "Figure_2_comparability_graph")


def figure_3_repair(coalitions: pd.DataFrame, shapley: pd.DataFrame, interaction: int) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.7), gridspec_kw={"width_ratios": [1.25, 1]})
    ax = axes[0]
    ax.scatter(
        coalitions.field_count,
        coalitions.formation_closed_records_upper_bound,
        color="#A9A9A9",
        s=30,
        alpha=0.8,
    )
    best = coalitions.loc[
        coalitions.groupby("field_count").formation_closed_records_upper_bound.idxmax()
    ].sort_values("field_count")
    ax.plot(best.field_count, best.formation_closed_records_upper_bound, color="#1F6F78", marker="o", linewidth=1.8)
    short_labels = {
        "none": "none",
        "mass": "mass",
        "mass;energy": "mass+energy",
        "mass;energy;time": "mass+energy+time",
        "mass;energy;time;endpoint": "all 4 fields",
    }
    for _, row in coalitions.iterrows():
        if row.repair_fields in {"none", "mass", "mass;energy", "mass;energy;time", "mass;energy;time;endpoint"}:
            label = short_labels[row.repair_fields]
            offset = (-4, -16) if row.repair_fields == "mass;energy;time;endpoint" else (4, 5)
            align = "right" if row.repair_fields == "mass;energy;time;endpoint" else "left"
            ax.annotate(
                label,
                (row.field_count, row.formation_closed_records_upper_bound),
                xytext=offset,
                textcoords="offset points",
                fontsize=6.5,
                ha=align,
            )
    ax.set_xticks(range(5))
    ax.set_xlabel("Fields supplied to every record (counterfactual)")
    ax.set_ylabel("Eligible records (optimistic upper bound)")
    ax.set_ylim(0, 17)
    ax.grid(axis="y", color="#DDDDDD", linewidth=0.6)
    ax.set_title("a  Eligibility requires field coalitions", loc="left", fontweight="bold")

    ax = axes[1]
    ordered = shapley.set_index("coordinate").loc[COORDINATES].reset_index()
    colors = ["#4C78A8", "#D1495B", "#E9A23B", "#7F7F7F"]
    bars = ax.barh(ordered.coordinate, ordered.shapley_closure_gain, color=colors)
    ax.invert_yaxis()
    ax.set_xlabel("Shapley eligibility gain (records)")
    ax.set_xlim(0, 7)
    ax.grid(axis="x", color="#DDDDDD", linewidth=0.6)
    for bar, value in zip(bars, ordered.shapley_closure_gain):
        ax.text(value + 0.12, bar.get_y() + bar.get_height() / 2, f"{value:.2f}", va="center", fontsize=7)
    ax.set_title(f"b  Allocation; mass-energy interaction = +{interaction}", loc="left", fontweight="bold")
    fig.suptitle("Mass and energy are complementary eligibility fields in this audit", x=0.01, ha="left", fontweight="bold", fontsize=10.5)
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.17, top=0.78, wspace=0.48)
    save_figure(fig, "Figure_3_repair_complementarity")


def figure_4_denominator(cases: pd.DataFrame) -> None:
    ordered = cases.sort_values("formed_normalized_input_MJ_kg").reset_index(drop=True)
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.65), gridspec_kw={"width_ratios": [1.45, 1]})
    ax = axes[0]
    y = np.arange(len(ordered))
    for index, row in ordered.iterrows():
        color = "#4C78A8" if row.record_id == "B08" else ("#2A9D8F" if row.simulant == "JSC-1A" else "#D1495B")
        ax.plot(
            [row.feed_normalized_input_MJ_kg, row.formed_normalized_input_MJ_kg],
            [index, index],
            color=color,
            linewidth=1.5,
        )
        ax.scatter(row.feed_normalized_input_MJ_kg, index, facecolor="white", edgecolor=color, s=34, zorder=3)
        ax.scatter(row.formed_normalized_input_MJ_kg, index, color=color, s=34, zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels(ordered.case_id.str.replace("_", " ", regex=False), fontsize=6.7)
    ax.set_xscale("log")
    ax.set_xlim(15, 90)
    ax.set_xticks([18, 20, 30, 40, 60, 80], labels=["18", "20", "30", "40", "60", "80"])
    ax.set_xlabel("Nominal input intensity (MJ kg$^{-1}$)")
    ax.grid(axis="x", color="#DDDDDD", linewidth=0.6)
    ax.text(0.02, 0.98, "open: feed mass   filled: formed mass", transform=ax.transAxes, va="top", fontsize=6.9)
    ax.set_title("a  Formed mass changes the denominator", loc="left", fontweight="bold")

    ax = axes[1]
    x = np.linspace(0.4, 1.0, 200)
    ax.plot(x, 1 / x, color="#333333", linewidth=1.4, label=r"$e_{formed}/e_{feed}=1/y$")
    for _, row in cases.iterrows():
        color = "#4C78A8" if row.record_id == "B08" else ("#2A9D8F" if row.simulant == "JSC-1A" else "#D1495B")
        ax.scatter(row.yield_fraction, row.denominator_correction_factor, color=color, s=37, edgecolor="white", linewidth=0.5, zorder=3)
    ax.set_xlim(0.4, 1.02)
    ax.set_ylim(0.9, 2.45)
    ax.set_xlabel("Source-defined formed-mass yield y")
    ax.set_ylabel("Denominator correction factor 1/y")
    ax.grid(color="#DDDDDD", linewidth=0.6)
    ax.legend(frameon=False, loc="upper right")
    ax.set_title("b  Observed correction spans 1.00-2.27", loc="left", fontweight="bold")
    fig.suptitle("Within one microwave lineage, feed-normalized equality does not fix product burden", x=0.01, ha="left", fontweight="bold", fontsize=10.5)
    fig.tight_layout()
    save_figure(fig, "Figure_4_denominator_effect")


def figure_5_rank_ambiguity(summary: dict[str, object]) -> None:
    cmax = float(summary["observed_denominator_correction_range"][1])
    ratio = np.geomspace(0.2, 5.0, 400)
    lower = ratio / cmax
    upper = ratio * cmax
    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    ax.fill_between(ratio, lower, upper, color="#D8E4E8", alpha=1.0, label="product-ratio set under observed correction range")
    ax.plot(ratio, lower, color="#4C78A8", linewidth=1.2)
    ax.plot(ratio, upper, color="#D1495B", linewidth=1.2)
    ax.axhline(1, color="#222222", linewidth=1.0)
    ax.axvline(1 / cmax, color="#7F7F7F", linestyle="--", linewidth=0.9)
    ax.axvline(cmax, color="#7F7F7F", linestyle="--", linewidth=0.9)
    ax.axvspan(
        1 / cmax,
        cmax,
        facecolor="#F2C14E",
        edgecolor="#8A6D1D",
        linewidth=0.0,
        alpha=0.22,
        hatch="///",
        label="rank not fixed by nominal ratio",
    )
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.2, 5)
    ax.set_ylim(0.08, 12)
    ax.xaxis.set_major_locator(FixedLocator([0.2, 0.44, 1, 2.27, 5]))
    ax.xaxis.set_major_formatter(FixedFormatter(["0.2", "0.44", "1", "2.27", "5"]))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.yaxis.set_major_locator(FixedLocator([0.1, 0.2, 0.5, 1, 2, 5, 10]))
    ax.yaxis.set_major_formatter(FixedFormatter(["0.1", "0.2", "0.5", "1", "2", "5", "10"]))
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.set_xlabel("Nominal feed-normalized intensity ratio, route i / route j (unitless)")
    ax.set_ylabel("Admissible formed-product intensity ratio (unitless)")
    ax.grid(which="both", color="#DDDDDD", linewidth=0.55)
    ax.legend(frameon=False, loc="upper left")
    ax.text(
        0.98,
        0.04,
        "Sensitivity envelope from nine source-selected microwave cases only;\nnot a universal yield bound or a cross-route performance estimate.",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=6.8,
        color="#444444",
    )
    ax.set_title("Nine-case correction envelope leaves nominal ratios from 0.44 to 2.27 rank-ambiguous", loc="left", fontweight="bold")
    save_figure(fig, "Figure_5_sample_observed_rank_ambiguity")


def write_reports(
    metrics: dict[str, object],
    interaction: int,
    summary: dict[str, object],
    sensitivity: dict[str, object],
    ladder: pd.DataFrame,
) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    report = f"""# V329 computation verification

- Records in typed audit: {metrics['records']}
- Identified target-metric edges: {metrics['identified_edges']} of {metrics['possible_pairs']}
- Graph density: {metrics['graph_density']:.6f}
- Isolated records: {metrics['isolated_records']}
- Mass-energy discrete interaction: +{interaction} optimistic eligibility units
- Numeric source-visible cases: {summary['numeric_cases']}
- JSC-1A cases at 900 kJ and 50 g feed: {summary['jsc_900kJ_50g_cases']}
- Feed-normalized intensity for those cases: 18 MJ/kg
- Formed-product range for those cases: {summary['jsc_formed_normalized_range_MJ_kg'][0]:.3f}-{summary['jsc_formed_normalized_range_MJ_kg'][1]:.3f} MJ/kg
- Observed denominator correction range: {summary['observed_denominator_correction_range'][0]:.3f}-{summary['observed_denominator_correction_range'][1]:.3f}
- Strict/permissive closed records: {sensitivity['strict_closed_records']}/{sensitivity['permissive_closed_records']}
- Strict/permissive mass-energy interaction: +{sensitivity['strict_mass_energy_interaction']}/+{sensitivity['permissive_mass_energy_interaction']}
- Expected closed records under independent fixed-margin allocation: {sensitivity['strict_expected_closed_under_independent_field_allocation']:.6f}
- Conditional probability of the observed maximum two-record overlap: {sensitivity['strict_probability_of_maximum_overlap']:.6f}
- Strict E+T+Q missingness-only candidate pairs: {int(ladder.set_index('diagnostic_tier').loc['strict_energy_time_endpoint', 'missingness_only_candidate_pairs'])}
- Permissive E+T+Q missingness-only candidate pairs: {int(ladder.set_index('diagnostic_tier').loc['permissive_energy_time_endpoint', 'missingness_only_candidate_pairs'])}
- Exact typed E+T+Q edges under strict/permissive coding: 1/1

All graph results are audit-set and target-metric specific. Repair results are
optimistic reporting-availability upper bounds. The rank-ambiguity envelope uses
only the observed correction-factor range in nine selected microwave cases. The
fixed-margin overlap calculation is a finite-configuration diagnostic, not a
population p-value.
"""
    (REPORTS / "computation_verification.md").write_text(report, encoding="utf-8")

    alt = """# Figure accessibility descriptions

## Figure 1
Two parallel chains show energy moving from wall-plug to native source and
process planes, and mass moving from feed to formed and endpoint-qualified
product. Conversion efficiency, ancillary energy and yield determine whether
energy per endpoint-qualified product is point identified, bounded or
nonidentified.

## Figure 2
The left panel shows strict mass, energy, time and endpoint availability for
all 16 records, with route family encoded by a colour strip. The right panel
shows the claim-indexed graph: only B08 and B09 are connected and 14 records
are isolated for the declared nominal-source-input per formed-mass comparison.
A lower-tier sensitivity notes that field presence alone flags 3 strict or 15
permissive energy-time-endpoint pairs, whereas exact typed boundaries retain
one edge under either coding rule.

## Figure 3
The left panel shows all combinations of universally supplied mass, energy,
time and endpoint fields. Mass plus energy increases the optimistic count of
closed records from two to ten, while either alone has little effect. The right
panel shows order-averaged Shapley closure gains dominated by mass and energy.

## Figure 4
Nine microwave cases compare feed-normalized and formed-mass-normalized nominal
input. Eight JSC-1A cases share 18 MJ per feed kilogram, but formed-product
normalization spans 18 to 40.9 MJ per kilogram as yield changes. The second
panel shows the exact correction factor 1 divided by yield.

## Figure 5
A log-log sensitivity envelope maps a nominal feed-normalized intensity ratio
to admissible formed-product ratios using only the observed correction-factor
range of 1 to 2.27. Nominal ratios between 0.44 and 2.27 cross unity and are
therefore rank-ambiguous under this sample-specific yield sensitivity.
"""
    (REPORTS / "figure_alt_text.md").write_text(alt, encoding="utf-8")


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    style()
    audit = pd.read_csv(INPUTS / "source_audit_16_v326.csv")
    typed = build_typed_audit(audit)
    edges, metrics = build_comparability_graph(typed)
    ladder = build_boundary_diagnostic_ladder(audit, typed)
    coalitions, shapley, interaction = build_repair_analysis(audit)
    sensitivity = build_rule_and_deletion_sensitivity(audit)
    cases, summary = build_numeric_cases()
    build_partial_identification_rules()

    assert len(typed) == 16
    assert len(edges) == 1
    assert set(edges.iloc[0][["record_i", "record_j"]]) == {"B08", "B09"}
    assert metrics["isolated_records"] == 14
    assert interaction == 7
    assert math.isclose(shapley.shapley_closure_gain.sum(), 14.0, abs_tol=2e-6)
    ladder_by_name = ladder.set_index("diagnostic_tier")
    assert int(ladder_by_name.loc["strict_energy_time_endpoint", "missingness_only_candidate_pairs"]) == 3
    assert int(ladder_by_name.loc["permissive_energy_time_endpoint", "missingness_only_candidate_pairs"]) == 15
    assert int(ladder_by_name.loc["strict_energy_time_endpoint", "typed_boundary_edges"]) == 1
    assert int(ladder_by_name.loc["permissive_energy_time_endpoint", "typed_boundary_edges"]) == 1
    assert int(ladder_by_name.loc["strict_endpoint_product", "missingness_only_candidate_pairs"]) == 1
    assert int(ladder_by_name.loc["permissive_endpoint_product", "missingness_only_candidate_pairs"]) == 1
    assert sensitivity["strict_closed_records"] == 2
    assert sensitivity["permissive_closed_records"] == 2
    assert math.isclose(
        sensitivity["strict_expected_closed_under_independent_field_allocation"],
        0.2197265625,
        rel_tol=1e-12,
    )
    assert math.isclose(
        sensitivity["strict_probability_of_maximum_overlap"],
        0.008203125,
        rel_tol=1e-12,
    )
    assert len(cases) == 9
    assert math.isclose(summary["observed_denominator_correction_range"][1], 50 / 22, rel_tol=1e-9)

    figure_1_boundary_mechanism()
    figure_2_graph(typed, edges, metrics, ladder)
    figure_3_repair(coalitions, shapley, interaction)
    figure_4_denominator(cases)
    figure_5_rank_ambiguity(summary)
    write_reports(metrics, interaction, summary, sensitivity, ladder)


if __name__ == "__main__":
    main()
