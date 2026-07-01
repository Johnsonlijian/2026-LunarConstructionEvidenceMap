#!/usr/bin/env python3
"""Figures from the illustrative structural + thermal sensitivity checks."""
from __future__ import annotations
from pathlib import Path
import numpy as np

import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.patches as mp  # noqa: E402

WIDTH_DOUBLE = 7.08


def set_style(base=8.5, family="serif"):
    plt.rcParams.update({
        "font.family": family,
        "font.size": base,
        "axes.linewidth": 0.7,
        "axes.labelsize": base,
        "xtick.labelsize": base - 1,
        "ytick.labelsize": base - 1,
        "legend.fontsize": base - 1,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })


def savefig(fig, stem, formats=("png", "pdf"), dpi=600):
    path = Path(stem)
    path.parent.mkdir(parents=True, exist_ok=True)
    for fmt in formats:
        fig.savefig(path.with_suffix(f".{fmt}"), dpi=dpi, bbox_inches="tight")
    plt.close(fig)


set_style(base=8.5, family="serif")
HERE = Path(__file__).parent
FIG = HERE.parent / "figures"
REP = {"REPORTED": "#9e9e9e", "design": "#5b8bd0", "partial": "#5b8bd0",
       "rare": "#bdbdbd", "unreported": "#d9730a"}


def fig_structural():
    cur = np.load(HERE / "structural/out_S2_curve.npz")
    par = np.load(HERE / "structural/out_S2_pushover.npz")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(WIDTH_DOUBLE, WIDTH_DOUBLE*0.42))
    Pu_a = float(cur["P_kN"].max())
    a1.plot(cur["d_mm"], cur["P_kN"]/Pu_a, color="#b5400a", lw=1.8)
    a1.set_xlabel("mid-span deflection (mm)", fontsize=7.6)
    a1.set_ylabel("normalized load  $P/P_u$", fontsize=7.6)
    a1.set_title("(a)  Nonlinear pushover (OpenSees)\nsintered-regolith pad strip, $f_c$=50 MPa",
                 fontsize=7.8, fontweight="bold", loc="left")
    a1.grid(alpha=0.25)
    for s in ("top", "right"):
        a1.spines[s].set_visible(False)
    Pu_min = float(par["Pu_kN"].min())
    a2.plot(par["ft"], par["Pu_kN"]/Pu_min, "o-", color="#2c7fb8", lw=1.6, ms=5)
    a2.set_xlabel("tensile strength $f_t$ (MPa)  [unreported]", fontsize=7.6)
    a2.set_ylabel("normalized capacity  $P_u/P_{u,\\mathrm{min}}$", fontsize=7.6)
    sp = par["Pu_kN"].max()/par["Pu_kN"].min()
    a2.set_title(f"(b)  At fixed reported $f_c$=50 MPa, capacity\nspans {sp:.1f}x with the unreported tensile strength",
                 fontsize=7.8, fontweight="bold", loc="left")
    a2.grid(alpha=0.25)
    for s in ("top", "right"):
        a2.spines[s].set_visible(False)
    fig.subplots_adjust(top=0.92, wspace=0.32)
    savefig(fig, str(FIG / "Figure_S1_structural"), formats=("png", "pdf"), dpi=600)
    print("WROTE Figure_S1_structural")


LABEL_MAP = {
    "fc_MPa": "$f_c$ (reported)",
    "ft_ratio": "$f_t/f_c$ (unreported)",
    "h_m": "thickness $h$ (design)",
    "L_m": "span $L$ (design)",
    "Ets_ratio": "tension-soften (unreported)",
    "E_GPa": "modulus $E$ (rare)",
    "dwell_s": "dwell (reported)",
    "m_kg": "specimen mass (reported)",
    "eta_couple": "coupling $\\eta$ (unreported)",
    "shape": "radiating geometry (unreported)",
    "Ts": "sinter $T$ (unreported)",
    "eps": "emissivity (unreported)",
}


def tornado(ax, npz, rep_map, title, xlabel):
    d = np.load(npz, allow_pickle=True)
    names = list(d["names"]); ST = np.array(d["ST"], dtype=float)
    order = np.argsort(ST)
    names = [names[i] for i in order]; ST = ST[order]
    colors = [REP.get(rep_map.get(n, "unreported"), "#d9730a") for n in names]
    ax.barh(range(len(names)), ST, color=colors, edgecolor="white")
    ax.set_yticks(range(len(names)))
    display_names = [LABEL_MAP.get(n, n.replace("_", " ")) for n in names]
    ax.set_yticklabels(display_names, fontsize=6.3)
    ax.set_xlabel(xlabel, fontsize=7.6)
    ax.set_title(title, fontsize=7.6, fontweight="bold", loc="left")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def fig_sobol():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(WIDTH_DOUBLE, WIDTH_DOUBLE*0.40))
    tornado(a1, HERE/"structural/out_S3_sobol.npz",
            {"fc_MPa": "REPORTED", "ft_ratio": "unreported", "E_GPa": "rare",
             "h_m": "design", "L_m": "design", "Ets_ratio": "unreported"},
            "(a)  Structural capacity (illustrative sensitivity runs)", "Sobol total-effect index")
    tornado(a2, HERE/"gpu_thermal/out_U_eff.npz",
            {"m_kg": "REPORTED", "dwell_s": "REPORTED", "eta_couple": "unreported",
             "eps": "unreported", "shape": "unreported", "Ts": "unreported"},
            "(b)  Thermal efficiency (3000 conditional MC samples)", "Sobol total-effect index")
    handles = [mp.Patch(color="#9e9e9e", label="reported by census"),
               mp.Patch(color="#5b8bd0", label="design / sometimes reported"),
               mp.Patch(color="#d9730a", label="unreported")]
    fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=6.6, frameon=False,
               bbox_to_anchor=(0.5, -0.02))
    fig.subplots_adjust(bottom=0.22, wspace=0.58, top=0.92, left=0.13, right=0.97)
    savefig(fig, str(FIG / "Figure_S2_sobol"), formats=("png", "pdf"), dpi=600)
    print("WROTE Figure_S2_sobol")


def fig_fragility():
    d = np.load(HERE / "structural/out_S4_fragility.npz")
    mbar = float(d["Pf"].mean())
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(WIDTH_DOUBLE, WIDTH_DOUBLE*0.42))
    a1.hist(d["Pf"]/mbar, bins=50, density=True, color="#d9730a", alpha=0.55,
            label=f"nothing known (COV {d['Pf'].std()/d['Pf'].mean():.2f})")
    a1.hist(d["Pc"]/mbar, bins=50, density=True, color="#2c7fb8", alpha=0.7,
            label=f"reported fc+geometry known (COV {d['Pc'].std()/d['Pc'].mean():.2f})")
    a1.set_xlabel("normalized capacity  $P_u/\\bar{P}_u$", fontsize=7.6)
    a1.set_ylabel("probability density", fontsize=7.6)
    a1.set_xlim(0, 950/mbar)
    a1.set_title("(a)  Capacity stays uncertain even after\nknowing every reported coordinate",
                 fontsize=7.6, fontweight="bold", loc="left")
    a1.legend(fontsize=6.2, frameon=False)
    for s in ("top", "right"):
        a1.spines[s].set_visible(False)
    a2.plot(d["demand"]/mbar, d["frag_full"], color="#d9730a", lw=1.8, label="nothing known")
    a2.plot(d["demand"]/mbar, d["frag_cond"], color="#2c7fb8", lw=1.8, label="reported fc+geometry known")
    a2.fill_between(d["demand"]/mbar, d["frag_cond"], d["frag_full"], color="#bbb", alpha=0.4)
    a2.set_xlabel("normalized demand  $D/\\bar{P}_u$", fontsize=7.6)
    a2.set_ylabel("P(structural failure)", fontsize=7.6)
    a2.set_xlim(0, 900/mbar)
    a2.set_title("(b)  Fragility: the reliability gap that the\nunreported coordinates leave open",
                 fontsize=7.6, fontweight="bold", loc="left")
    a2.legend(fontsize=6.4, frameon=False, loc="lower right")
    a2.grid(alpha=0.25)
    for s in ("top", "right"):
        a2.spines[s].set_visible(False)
    fig.subplots_adjust(top=0.92, wspace=0.30)
    savefig(fig, str(FIG / "Figure_S3_fragility"), formats=("png", "pdf"), dpi=600)
    print("WROTE Figure_S3_fragility")


if __name__ == "__main__":
    fig_structural()
    fig_sobol()
    fig_fragility()
    print("done")
