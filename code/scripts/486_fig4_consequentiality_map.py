#!/usr/bin/env python3
"""Figure 4: consequentiality map — route-scale framing vs missing decisive coordinates.

Each of the seven census sources attaches its own verbatim route-scale framing (left) to a
result that omits the two decision-controlling coordinates (right, absent in all seven). Two
sources tie the framing to a named exploration programme/roadmap. Quotes are verbatim and
page-locked (V294 audit + V296 census); the figure is source framing, not evidence of author
error.
"""
from __future__ import annotations
from pathlib import Path

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

try:
    from pyplot_cjk import set_style, savefig, WIDTH_DOUBLE  # type: ignore
except ImportError:
    WIDTH_DOUBLE = 7.2

    def set_style(lang="en", base=8.5, family="serif"):
        plt.rcParams.update({"font.size": base, "font.family": family})

    def savefig(fig, path, formats=("png", "pdf"), dpi=300):
        base = Path(path)
        base.parent.mkdir(parents=True, exist_ok=True)
        for fmt in formats:
            fig.savefig(base.with_suffix(f".{fmt}"), bbox_inches="tight", dpi=dpi)

set_style(lang="en", base=8.5, family="serif")

C_STRONG = "#b5400a"   # industrial-scale / large-scale / roadmap-tied
C_MED = "#d9730a"      # scalability / viability / infrastructure / production
C_ABSENT = "#c0392b"
C_DIV = "#888888"

# (label, verbatim framing snippet, class_color, roadmap_badge)
# Snippets are verbatim sub-phrases; rows carrying a badge use a shorter snippet to leave room.
SRC = [
    ("Kato 2024", "“towards lunar base construction”", C_STRONG, "JP STARDUST"),
    ("Lim 2023", "“industrial-scale lunar construction”", C_STRONG, "ESA Terrae Novae 2030+"),
    ("Linke 2022", "“… very scalable” technology", C_MED, "MOONRISE mission"),
    ("Gines 2023", "“proved the viability … for paving applications”", C_MED, ""),
    ("Lim 2021", "directed at “… spacecraft landing pads”", C_MED, ""),
    ("Zhu 2026", "“in situ construction of lunar infrastructure”", C_MED, ""),
    ("Tsubaki 2024", "“Self-Sufficient Production … on the Moon”", C_MED, ""),
]

fig, ax = plt.subplots(figsize=(WIDTH_DOUBLE, WIDTH_DOUBLE * 0.56))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")

DIV = 0.625
capx, effx = 0.71, 0.875

# headers
ax.text(0.02, 0.93, "Route-scale framing asserted (verbatim, page-locked)", ha="left",
        va="center", fontsize=7.6, fontweight="bold", color="#2b2b2b")
ax.text((DIV + 1) / 2 + 0.02, 0.965, "Decision-controlling", ha="center", va="center",
        fontsize=7.4, fontweight="bold", color="#2b2b2b")
ax.text((DIV + 1) / 2 + 0.02, 0.935, "coordinates reported", ha="center", va="center",
        fontsize=7.4, fontweight="bold", color="#2b2b2b")
ax.text(capx, 0.895, "deployed\nsource capacity", ha="center", va="center", fontsize=5.8,
        color="#444")
ax.text(effx, 0.895, "wall-plug\nefficiency", ha="center", va="center", fontsize=5.8,
        color="#444")
ax.plot([DIV, DIV], [0.07, 0.91], color=C_DIV, lw=1.0, zorder=1)

y0, dy = 0.83, 0.097
for i, (lab, snip, col, badge) in enumerate(SRC):
    y = y0 - i * dy
    if i % 2 == 0:
        ax.add_patch(Rectangle((0.01, y - dy / 2 + 0.006), 0.98, dy - 0.012,
                     fc="#f4f4f4", ec="none", zorder=0))
    # source label + class tick
    ax.add_patch(Rectangle((0.015, y - 0.018), 0.006, 0.036, fc=col, ec="none", zorder=3))
    ax.text(0.03, y, lab, ha="left", va="center", fontsize=6.8, fontweight="bold",
            color="#222")
    # framing snippet
    ax.text(0.135, y, snip, ha="left", va="center", fontsize=6.3, color=col, style="italic")
    # roadmap / mission badge
    if badge:
        ax.add_patch(FancyBboxPatch((0.45, y - 0.016), 0.165, 0.032,
                     boxstyle="round,pad=0.002,rounding_size=0.008",
                     fc="#fff4e8", ec=col, lw=0.7, zorder=2))
        ax.plot(0.468, y, marker="*", color=col, ms=5, zorder=3)
        ax.text(0.5425, y, badge, ha="center", va="center", fontsize=5.2,
                color=col, zorder=3)
    # two absent cells
    for cx in (capx, effx):
        ax.add_patch(FancyBboxPatch((cx - 0.05, y - 0.02), 0.10, 0.04,
                     boxstyle="round,pad=0.002,rounding_size=0.006",
                     fc="#fbeae8", ec=C_ABSENT, lw=0.8, zorder=2))
        ax.text(cx, y, "absent", ha="center", va="center", fontsize=6.0,
                color=C_ABSENT, fontweight="bold", zorder=3)

# conclusion strip
ax.add_patch(FancyBboxPatch((0.05, 0.008), 0.90, 0.052,
             boxstyle="round,pad=0.004,rounding_size=0.012",
             fc="#fbf0df", ec=C_STRONG, lw=1.0, zorder=2))
ax.text(0.5, 0.034, "All seven sources assert route-scale feasibility / scalability; "
        "neither decisive coordinate is reported by any — the framing outruns the "
        "reported coordinates", ha="center", va="center", fontsize=6.6,
        color="#5a3d0a", fontweight="bold")

ax.set_title("Consequentiality: route-scale framing is attached to coordinate-incomplete results",
             fontsize=8.6, fontweight="bold", pad=6)

ROOT = Path(__file__).resolve().parents[2]
out = ROOT / "figures" / "fig4_consequentiality_map"
savefig(fig, str(out), formats=("png", "pdf", "svg"), dpi=600)
print("WROTE", out.with_suffix(".pdf"))
