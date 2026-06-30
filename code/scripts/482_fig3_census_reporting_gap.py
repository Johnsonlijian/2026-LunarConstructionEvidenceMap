#!/usr/bin/env python3
"""Figure 3: open-access directed-energy census reporting gap.

Reads the bundled V319 directed-energy census CSV and counts, per closure
coordinate, how many sources REPORT it. The two coordinates the directed-energy
predicate makes decisive (deployed active source capacity, wall-plug-to-cavity efficiency)
are reported in 0/n, exactly the ones the framework flags as decision-controlling.
"""
from __future__ import annotations
import csv
from pathlib import Path

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

try:
    from pyplot_cjk import set_style, savefig, WIDTH_SINGLE  # type: ignore
except ImportError:
    WIDTH_SINGLE = 3.5

    def set_style(lang="en", base=8.5, family="serif"):
        plt.rcParams.update({"font.size": base, "font.family": family})

    def savefig(fig, path, formats=("png", "pdf"), dpi=300):
        base = Path(path)
        base.parent.mkdir(parents=True, exist_ok=True)
        for fmt in formats:
            fig.savefig(base.with_suffix(f".{fmt}"), bbox_inches="tight", dpi=dpi)

set_style(lang="en", base=8.5, family="serif")

ROOT = Path(__file__).resolve().parents[2]
census_path = ROOT / "outputs" / "V319_acta_measurement_contract" / "reproducibility_package" / "census_directed_energy_n7.csv"
rows = list(csv.DictReader(census_path.read_text(encoding="utf-8").splitlines()))
N = len(rows)


def counts(col):
    rep = sum(1 for r in rows if r[col].strip().upper().startswith("REPORTED"))
    par = sum(1 for r in rows if r[col].strip().upper().startswith("PARTIAL"))
    return rep, par


# coordinate, column, decisive?
COORDS = [
    ("input power", "c_input_power", False),
    ("process time / dwell", "c_process_time_dwell", False),
    ("processed sample mass", "c_processed_sample_mass", False),
    ("energy per accepted mass", "c_energy_per_accepted_mass", False),
    ("wall-plug-to-cavity efficiency", "c_wall_to_cavity_efficiency", True),
    ("deployed active source capacity", "c_active_source_capacity", True),
]

labels, rep_vals, par_vals, decisive = [], [], [], []
for name, col, dec in COORDS:
    rep, par = counts(col)
    labels.append(name)
    rep_vals.append(rep)
    par_vals.append(par)
    decisive.append(dec)

fig, ax = plt.subplots(figsize=(WIDTH_SINGLE * 2.0, WIDTH_SINGLE * 1.35))
y = range(len(labels))
C_OK = "#2c7fb8"
C_PARTIAL = "#9ecae1"
C_DEC = "#d9730a"

for i, (rep, par, dec) in enumerate(zip(rep_vals, par_vals, decisive)):
    base = C_DEC if dec else C_OK
    # reported (solid) + partial (light) stacked
    ax.barh(i, rep, color=base, edgecolor="white", height=0.62, zorder=3)
    if par:
        ax.barh(i, par, left=rep, color=C_PARTIAL, edgecolor="white", height=0.62, zorder=3)
    total = rep + par
    txt = f"{rep}/{N}" + (f"  (+{par} partial)" if par else "")
    ax.text(total + 0.12, i, txt, va="center", ha="left", fontsize=7.0,
            color=base if total else C_DEC, fontweight="bold")

ax.set_yticks(list(y))
ax.set_yticklabels(labels, fontsize=7.6)
for tick, dec in zip(ax.get_yticklabels(), decisive):
    if dec:
        tick.set_color(C_DEC)
        tick.set_fontweight("bold")
ax.invert_yaxis()
ax.set_xlim(0, N + 1.4)
ax.set_xticks(range(0, N + 1))
ax.set_xlabel(f"number of sources reporting the coordinate  (n = {N} open-access full texts)",
              fontsize=7.6)
ax.axvline(0, color="#888", lw=0.8)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.tick_params(axis="both", which="both", top=False, right=False, length=3)

# decisive-coordinate annotation band
ax.axhspan(3.5, 5.5, color=C_DEC, alpha=0.07, zorder=0)
ax.text(N + 1.32, 4.5, "decisive for the\nclosure predicate", rotation=0, ha="right",
        va="center", fontsize=6.4, color=C_DEC, style="italic")

ax.legend(handles=[
    Patch(fc=C_OK, label="reported"),
    Patch(fc=C_PARTIAL, label="partial (geometry/batch, not a per-sample number)"),
    Patch(fc=C_DEC, label=f"decision-controlling coordinate (reported 0/{N})"),
], loc="lower right", fontsize=6.2, frameon=False, bbox_to_anchor=(1.0, -0.02))

ax.set_title("Open-access directed-energy census: the two decision-controlling\n"
             "coordinates are exactly the ones never reported",
             fontsize=8.4, fontweight="bold", pad=8)

out = ROOT / "figures" / "fig3_census_reporting_gap"
savefig(fig, str(out), formats=("png", "pdf", "svg"), dpi=600)
print("WROTE", out.with_suffix(".pdf"))
print("counts:", dict(zip(labels, [f"{r}/{N}(+{p})" for r, p in zip(rep_vals, par_vals)])))
