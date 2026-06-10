from pathlib import Path
import pandas as pd

root = Path(__file__).resolve().parents[1]
routes = pd.read_csv(root / "data" / "lc_erl_route_assignments.csv")
param = pd.read_csv(root / "data" / "parametric_engineering_case.csv")

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
print(f"Mid-case SPS storage-equivalent power: {float(mid['storage_equivalent_power_kW'].iloc[0]):.1f} kW")
print("Reviewer-ready checks passed.")
