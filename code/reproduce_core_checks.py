from pathlib import Path
import pandas as pd

root = Path(__file__).resolve().parents[1]
routes = pd.read_csv(root / "data" / "lc_erl_route_assignments.csv")
param = pd.read_csv(root / "data" / "parametric_engineering_case.csv")
stress = pd.read_csv(root / "data" / "parametric_stress_test_summary.csv")

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

print(f"SPS energy ratio vs lowest nominal: {float(sps):.2f}x")
cs_10 = stress[(stress["available_power_cap_kW"] == 10) & (stress["route"] == "Cold sinter")]["cases_below_or_equal_cap"].iloc[0]
sps_5 = stress[(stress["available_power_cap_kW"] == 5) & (stress["route"] == "SPS")]["cases_below_or_equal_cap"].iloc[0]
assert int(cs_10) == 41
assert int(sps_5) == 0

print(f"Mid-case SPS storage-equivalent power: {float(mid['storage_equivalent_power_kW'].iloc[0]):.1f} kW")
print(f"Stress-test cold-sinter cases below 10 kW cap: {int(cs_10)}/81")
print("Reviewer-ready checks passed.")
