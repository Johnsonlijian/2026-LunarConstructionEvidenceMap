#!/usr/bin/env python3
"""Figure 1 (lead mechanism figure): coordinate-projection collapse -> non-identifiability.

One left->right story. (a) A full route state carries five coordinates; two admissible latent
states are IDENTICAL on the three reported coordinates (input power, dwell, accepted mass) and
differ ONLY on the two decisive coordinates that no source reports (deployed source capacity,
wall-plug efficiency): one completion passes, one fails. (b) The reported-coordinate projection
keeps only the shared part, so both states collapse onto one observed point -- the real Lim
(2021) projection -- which is therefore compatible with both a pass and a fail verdict.

Illustrative schematic of the observation model (numbers from the worked example on the Lim
2021 reported projection); not empirical route data.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, r"R:\AcademicWorkspace\tools")
from pyplot_cjk import set_style, savefig, WIDTH_DOUBLE  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle  # noqa: E402

set_style(lang="en", base=8.5, family="serif")

C_PASS = "#2f8f4e"   # green
C_FAIL = "#c0392b"   # red
C_SHARE = "#222222"  # charcoal (shared/observed)
C_OMIT = "#e0871a"   # amber (omitted / decisive)
C_BOX = "#f7f7f5"
C_EDGE = "#9a9a9a"

fig, ax = plt.subplots(figsize=(WIDTH_DOUBLE, WIDTH_DOUBLE * 0.585))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")

YT, YB = 0.80, 0.46


def yv(v):
    return YB + v * (YT - YB)


def panel(x0, x1, tag, title, subtitle=""):
    ax.add_patch(FancyBboxPatch((x0, 0.150), x1 - x0, 0.815,
                 boxstyle="round,pad=0.006,rounding_size=0.012",
                 fc=C_BOX, ec=C_EDGE, lw=0.9, zorder=0))
    ax.text(x0 + 0.016, 0.932, tag, ha="left", va="center", fontsize=9.0,
            fontweight="bold", color="#222")
    cx = (x0 + x1) / 2
    ax.text(cx, 0.932, title, ha="center", va="center", fontsize=8.0,
            fontweight="bold", color="#222")
    if subtitle:
        ax.text(cx, 0.900, subtitle, ha="center", va="center", fontsize=6.0, color="#777")


def axis(x, name, top=YT, bot=YB):
    ax.plot([x, x], [bot - 0.02, top + 0.02], color="#c4c4c4", lw=0.8, zorder=1)
    ax.text(x, bot - 0.052, name, ha="center", va="top", fontsize=6.0, color="#444")


# ================= LEFT panel (a) =================
panel(0.02, 0.435, "(a)", "Full route state  $x\\in X$",
      "two admissible states, same reported coordinates")
xr = [0.085, 0.160, 0.235]
for x, n in zip(xr, ("input\npower", "process\ndwell", "accepted\nmass")):
    axis(x, n)
# omitted / decisive zone
ax.add_patch(Rectangle((0.288, YB - 0.025), 0.130, (YT - YB) + 0.055,
             fc=C_OMIT, ec="none", alpha=0.13, zorder=0))
xo = [0.325, 0.395]
for x, n in zip(xo, ("source\ncapacity", "wall-plug\nefficiency")):
    axis(x, n)
ax.text(0.353, 0.862, "not reported by any source", ha="center", va="center",
        fontsize=6.0, color=C_OMIT, fontweight="bold")
ax.text(0.353, 0.836, "(0 / 7)", ha="center", va="center",
        fontsize=6.0, color=C_OMIT, fontweight="bold")

# shared reported history (identical for both states)
shy = [yv(0.50), yv(0.68), yv(0.36)]
ax.plot(xr, shy, color=C_SHARE, lw=2.6, zorder=4, solid_capstyle="round")
for x, y in zip(xr, shy):
    ax.plot(x, y, "o", color=C_SHARE, ms=3.1, zorder=5)
# "identical" bracket over reported axes
ax.annotate("", xy=(xr[0] - 0.006, 0.815), xytext=(xr[2] + 0.006, 0.815),
            arrowprops=dict(arrowstyle="-", color="#9a9a9a", lw=0.8,
                            connectionstyle="bar,fraction=0.12"))
ax.text((xr[0] + xr[2]) / 2, 0.846, "identical reported coordinates", ha="center",
        va="center", fontsize=5.7, color="#777", style="italic")

bx, by = xr[2], yv(0.36)
pass_pts = [(bx, by), (xo[0], yv(0.90)), (xo[1], yv(0.84))]
fail_pts = [(bx, by), (xo[0], yv(0.12)), (xo[1], yv(0.20))]
ax.plot(*zip(*pass_pts), color=C_PASS, lw=2.2, zorder=4, solid_capstyle="round")
ax.plot(*zip(*fail_pts), color=C_FAIL, lw=2.2, zorder=4, solid_capstyle="round")
for x, y in pass_pts[1:]:
    ax.plot(x, y, "o", color=C_PASS, ms=3.0, zorder=5)
for x, y in fail_pts[1:]:
    ax.plot(x, y, "o", color=C_FAIL, ms=3.0, zorder=5)
# value annotations on the diverging endpoints (what actually differs)
ax.text(0.410, yv(0.90), "6 kW", ha="left", va="center", fontsize=5.6, color=C_PASS)
ax.text(0.410, yv(0.84), "0.70", ha="left", va="center", fontsize=5.6, color=C_PASS)
ax.text(0.410, yv(0.12), "3 kW", ha="left", va="center", fontsize=5.6, color=C_FAIL)
ax.text(0.410, yv(0.20), "0.50", ha="left", va="center", fontsize=5.6, color=C_FAIL)
ax.text(xo[0] - 0.030, yv(0.90) + 0.028, r"$x_{\rm pass}\;C{=}1$", ha="left", va="bottom",
        fontsize=6.4, color=C_PASS, fontweight="bold")
ax.text(xo[0] - 0.030, yv(0.12) - 0.028, r"$x_{\rm fail}\;C{=}0$", ha="left", va="top",
        fontsize=6.4, color=C_FAIL, fontweight="bold")

# ================= MIDDLE: projection map =================
ax.add_patch(FancyArrowPatch((0.448, 0.560), (0.560, 0.560), arrowstyle="-|>",
             mutation_scale=18, lw=2.4, color="#333"))
ax.text(0.504, 0.660, r"$\pi_S$", ha="center", va="center", fontsize=11, fontweight="bold")
ax.text(0.504, 0.612, "keep only the\nreported coordinates", ha="center", va="center",
        fontsize=5.9, color="#444")
ax.text(0.504, 0.500, "drops", ha="center", va="center", fontsize=5.6, color=C_OMIT,
        fontweight="bold")
for i, lab in enumerate(("source capacity", "wall-plug efficiency")):
    yy = 0.466 - i * 0.033
    ax.text(0.504, yy, lab, ha="center", va="center", fontsize=5.3, color=C_OMIT)
    ax.plot([0.455, 0.553], [yy + 0.001, yy + 0.001], color=C_OMIT, lw=0.7, zorder=6)

# ================= RIGHT panel (b) =================
panel(0.565, 0.98, "(b)", "Observed evidence  $O_S(x)=\\pi_S(x)$",
      "both states collapse to one observed point")
xr2 = [0.620, 0.690, 0.760]
for x, n in zip(xr2, ("input\npower", "process\ndwell", "accepted\nmass")):
    axis(x, n)
oy = [yv(0.50), yv(0.68), yv(0.36)]
# faint ghosts of the two states merging into the single observed line
for gy in (0.0,):
    pass
ax.plot(xr2, oy, color=C_SHARE, lw=2.8, zorder=4, solid_capstyle="round")
for x, y in zip(xr2, oy):
    ax.plot(x, y, "o", color=C_SHARE, ms=3.3, zorder=5)
ax.text(0.690, yv(0.36) - 0.066, "Lim 2021 reported projection",
        ha="center", va="top", fontsize=5.8, color="#666")
ax.text(0.690, yv(0.36) - 0.100, r"$1\,$kW $\cdot\;900\,$s $\cdot\;0.05\,$kg",
        ha="center", va="top", fontsize=6.4, color="#222", fontweight="bold")


def chip(x, y, color, title, line):
    ax.add_patch(FancyBboxPatch((x, y), 0.150, 0.115,
                 boxstyle="round,pad=0.005,rounding_size=0.01",
                 fc="white", ec=color, lw=1.1, zorder=6))
    ax.text(x + 0.010, y + 0.083, title, ha="left", va="center", fontsize=5.9,
            color=color, fontweight="bold", zorder=7)
    ax.text(x + 0.010, y + 0.049, line[0], ha="left", va="center", fontsize=5.2,
            color="#333", zorder=7)
    ax.text(x + 0.010, y + 0.020, line[1], ha="left", va="center", fontsize=5.2,
            color="#333", zorder=7)


ax.add_patch(FancyArrowPatch((0.805, yv(0.40)), (0.822, 0.700), arrowstyle="-|>",
             mutation_scale=9, lw=1.1, color=C_PASS, linestyle=(0, (3, 2)), zorder=3))
ax.add_patch(FancyArrowPatch((0.805, yv(0.34)), (0.822, 0.360), arrowstyle="-|>",
             mutation_scale=9, lw=1.1, color=C_FAIL, linestyle=(0, (3, 2)), zorder=3))
chip(0.820, 0.640, C_PASS, "compatible with PASS",
     [r"$\eta\,$0.70,  cap 6 kW", "margins 1.17 / 1.20"])
chip(0.820, 0.300, C_FAIL, "compatible with FAIL",
     [r"$\eta\,$0.50,  cap 3 kW", "margins 0.83 / 0.60"])

# ================= conclusion strip =================
ax.add_patch(FancyBboxPatch((0.05, 0.018), 0.90, 0.078,
             boxstyle="round,pad=0.004,rounding_size=0.012",
             fc="#fbf1df", ec=C_OMIT, lw=1.1, zorder=2))
ax.text(0.5, 0.057,
        "Identical reported evidence $\\;\\rightleftarrows\\;$ opposite closure verdicts "
        "$\\;\\Rightarrow\\;$ closure is not identifiable from the reported projection",
        ha="center", va="center", fontsize=7.4, color="#5a3d0a", fontweight="bold")

out = Path(r"W:\01_PROJECTS\NAS_DRIVE\IMUT\1-Research_Output\1-Papers"
           r"\1_In_Preparation\2026-LunarConstructionEvidenceMap\figures"
           r"\fig1_projection_collapse_observability")
out.parent.mkdir(parents=True, exist_ok=True)
savefig(fig, str(out), formats=("png", "pdf", "svg"), dpi=600)
# also write the canonical manuscript name
canon = out.parent / "Figure_1_mechanism"
savefig(fig, str(canon), formats=("png", "pdf"), dpi=600)
print("WROTE", out.with_suffix(".pdf"), "and", canon.with_suffix(".pdf"))
