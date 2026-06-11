from pathlib import Path
import pandas as pd

root = Path(__file__).resolve().parents[1]
routes = pd.read_csv(root / "data" / "lc_erl_route_assignments.csv")
param = pd.read_csv(root / "data" / "parametric_engineering_case.csv")
stress = pd.read_csv(root / "data" / "parametric_stress_test_summary.csv")
multi = pd.read_csv(root / "data" / "multisite_temporal_index.csv")

sps = routes.loc[routes["short_label"] == "SPS", "energy_ratio_vs_lowest_nominal"].iloc[0]
assert 12.8 < float(sps) < 13.0

mid = param[
    (param["route"] == "SPS")
    & (param["thickness_m"].round(3) == 0.05)
    & (param["bulk_density_kg_m3"] == 1800)
    & (param["loss_multiplier"] == 3)
    & (param["dark_gap_days"] == 8)
]
assert len(mid) == 1
assert float(mid["processed_mass_kg"].iloc[0]) == 1350.0
assert float(mid["storage_equivalent_power_kW"].iloc[0]) > 100.0

cs_10 = stress[(stress["available_power_cap_kW"] == 10) & (stress["route"] == "Cold sinter")]["cases_below_or_equal_cap"].iloc[0]
sps_5 = stress[(stress["available_power_cap_kW"] == 5) & (stress["route"] == "SPS")]["cases_below_or_equal_cap"].iloc[0]
assert int(cs_10) == 41
assert int(sps_5) == 0

assert set(multi["site"]) == {"Shackleton rim", "Connecting Ridge C1", "Connecting Ridge C2", "Barker Site-1"}
assert int(multi.loc[multi["site"].eq("Connecting Ridge C1"), "longest_shadow_h"].iloc[0]) == 112
assert int(multi.loc[multi["site"].eq("Connecting Ridge C2"), "longest_shadow_h"].iloc[0]) == 165
assert int(multi.loc[multi["site"].eq("Shackleton rim"), "longest_shadow_h"].iloc[0]) == 66
site1_cs = multi[(multi["site"] == "Barker Site-1") & (multi["route"] == "Cold sinter")]["temporal_storage_sensitivity_MJ_d_per_kg"].iloc[0]
assert abs(float(site1_cs) - 16.13) < 0.02

print(f"SPS energy ratio vs lowest nominal: {float(sps):.2f}x")
print(f"Mid-case SPS storage-equivalent power: {float(mid['storage_equivalent_power_kW'].iloc[0]):.1f} kW")
print(f"Stress-test cold-sinter cases below 10 kW cap: {int(cs_10)}/81")
print(f"Multi-site temporal sites: {multi['site'].nunique()}")
print("Reviewer-ready checks passed.")
