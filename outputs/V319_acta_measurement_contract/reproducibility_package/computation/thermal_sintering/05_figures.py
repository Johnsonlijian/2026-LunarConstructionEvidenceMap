#!/usr/bin/env python3
"""Publication figures from the REAL simulation outputs (Components 1-4)."""
from __future__ import annotations
from pathlib import Path
import numpy as np

import matplotlib.pyplot as plt  # noqa: E402
from importlib import import_module

try:
    from pyplot_cjk import set_style, savefig, WIDTH_DOUBLE, WIDTH_SINGLE  # type: ignore
except ImportError:
    WIDTH_DOUBLE = 7.2
    WIDTH_SINGLE = 3.5

    def set_style(lang="en", base=8.5, family="serif"):
        plt.rcParams.update({"font.size": base, "font.family": family})

    def savefig(fig, path, formats=("png", "pdf"), dpi=300):
        base = Path(path)
        base.parent.mkdir(parents=True, exist_ok=True)
        for fmt in formats:
            fig.savefig(base.with_suffix(f".{fmt}"), bbox_inches="tight", dpi=dpi)

sim = import_module("02_regolith_energy_balance")

set_style(lang="en", base=8.5, family="serif")
HERE = Path(__file__).parent
FIGDIR = HERE.parent.parent / "figures"


# ---------- FIG A: mechanism (energy ledger + efficiency vs dwell) ----------
def fig_mechanism():
    m, A_top = 0.050, None
    V, _, R, h = sim.specimen_geometry(m)
    A_top = np.pi * R**2
    cases = [("Lim 2021\n(JSC-1A, 900 s)", 1000.0, 900.0, 18.0, "#2c7fb8"),
             ("Lim 2023\n(highland, 3600 s)", 1000.0, 3600.0, 72.0, "#b5400a")]
    ledg = []
    for name, P, dwell, rep, c in cases:
        r = sim.simulate(m, P, 0.60, dwell, A_rad=A_top)
        Ein = r["E_input_J"]; Eabs = r["E_abs_J"]; Erad = r["E_rad_J"]; Esens = r["E_sens_J"]
        ledg.append((name, Ein, Eabs, Erad, Esens, c, r["eff_overall"]))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(WIDTH_DOUBLE, WIDTH_DOUBLE * 0.44))

    # (a) energy ledger stacked (% of input)
    labels = [l[0] for l in ledg]
    xs = np.arange(len(ledg))
    coupling = [(L[1]-L[2])/L[1]*100 for L in ledg]   # reflected / not coupled
    rad = [L[3]/L[1]*100 for L in ledg]
    sens = [L[4]/L[1]*100 for L in ledg]
    hold = [100 - c - rr - ss for c, rr, ss in zip(coupling, rad, sens)]
    b = np.zeros(len(ledg))
    for vals, col, lab in [(coupling, "#bdbdbd", "not coupled (reflected)"),
                           (rad, "#e0871a", "re-radiated over dwell"),
                           (hold, "#9ecae1", "stored in hot mass (lost on cool-down)"),
                           (sens, "#2f8f4e", "sensible heat in product")]:
        ax1.bar(xs, vals, bottom=b, color=col, width=0.55, label=lab, edgecolor="white", lw=0.6)
        b = b + np.array(vals)
    for i, L in enumerate(ledg):
        ax1.text(i, 101, f"input {L[1]/1e3:.0f} kJ\n{L[1]/0.05/1e6:.0f} MJ/kg",
                 ha="center", va="bottom", fontsize=6.2, color="#333")
        ax1.text(i, sens[i]/2+1, f"{sens[i]:.0f}%", ha="center", va="center",
                 fontsize=6.0, color="white", fontweight="bold")
    ax1.set_xticks(xs); ax1.set_xticklabels(labels, fontsize=6.8)
    ax1.set_ylabel("share of wall-plug input energy (%)", fontsize=7.6)
    ax1.set_ylim(0, 116)
    ax1.set_title("(a)  Energy ledger: re-radiation dominates", fontsize=8.2, fontweight="bold", loc="left")
    ax1.legend(fontsize=5.3, loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, -0.20))
    for s in ("top", "right"):
        ax1.spines[s].set_visible(False)

    # (b) efficiency vs dwell (real points marked)
    d = np.array([200, 400, 600, 900, 1500, 2400, 3600, 5400, 7200.0])
    eff = [sim.simulate(m, 1000.0, 0.60, dd, A_rad=A_top)["eff_overall"]*100 for dd in d]
    try:
        bd = np.load(HERE.parent / "uq" / "out_U_band.npz")
        ax2.fill_between(bd["dwells"], bd["lo"], bd["hi"], color="#9e9e9e", alpha=0.22, lw=0,
                         zorder=1, label="5–95% under parameter uncertainty")
    except FileNotFoundError:
        pass
    ax2.plot(d, eff, "-", color="#444", lw=1.6, zorder=2, label="calibrated model")
    for name, P, dwell, rep, c in cases:
        e = sim.simulate(m, P, 0.60, dwell, A_rad=A_top)["eff_overall"]*100
        ax2.plot(dwell, e, "o", color=c, ms=7, zorder=4, markeredgecolor="white", mew=1.0)
        ax2.annotate(f"{name.split(chr(10))[0]}\n{rep:.0f} MJ/kg, {e:.1f}%",
                     (dwell, e), xytext=(dwell, e+1.6), fontsize=6.0, color=c, ha="center")
    ax2.set_xlabel("process dwell (s)  [unreported]", fontsize=7.6)
    ax2.set_ylabel("wall-plug-to-product efficiency (%)", fontsize=7.6)
    ax2.set_title("(b)  Efficiency falls with dwell (robust to assumptions)", fontsize=8.2, fontweight="bold", loc="left")
    ax2.set_ylim(0, 9)
    ax2.legend(fontsize=5.6, loc="upper right", frameon=False)
    ax2.grid(alpha=0.25)
    for s in ("top", "right"):
        ax2.spines[s].set_visible(False)
    fig.suptitle("Calibrated regolith-sintering energy balance reproduces the two reported "
                 "energy values from one physics", fontsize=8.6, fontweight="bold", y=1.02)
    fig.subplots_adjust(bottom=0.26, top=0.85, wspace=0.30)
    savefig(fig, str(FIGDIR / "Figure_P1_mechanism"), formats=("png", "pdf"), dpi=600)
    print("WROTE Figure_P1_mechanism")


# ---------- FIG B: temperature field ----------
def fig_field():
    d = np.load(HERE / "out_04_field.npz")
    x = d["x_mm"]; snap_t = d["snap_t"]; snap_T = d["snap_T"]; Ts = float(d["T_sinter"])
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(WIDTH_DOUBLE, WIDTH_DOUBLE * 0.42))
    cmap = plt.cm.inferno(np.linspace(0.15, 0.85, len(snap_t)))
    for (tt, Tp, col) in zip(snap_t, snap_T, cmap):
        ax1.plot(x, Tp, color=col, lw=1.6, label=f"{tt:.0f} s")
    ax1.axhline(Ts, color="#c0392b", ls="--", lw=1.0)
    ax1.text(x[-1], Ts+25, f"sintering onset {Ts:.0f} K", ha="right", va="bottom",
             fontsize=6.2, color="#c0392b")
    ax1.set_xlim(0, 25); ax1.set_xlabel("depth (mm)", fontsize=7.6)
    ax1.set_ylabel("temperature (K)", fontsize=7.6)
    ax1.set_title("(a)  Sintering is confined to a thin near-surface layer",
                  fontsize=8.0, fontweight="bold", loc="left")
    ax1.legend(fontsize=6.0, title="dwell", title_fontsize=6.2, frameon=False)
    for s in ("top", "right"):
        ax1.spines[s].set_visible(False)
    ax2.plot(d["t"], d["sint_depth_mm"], "-", color="#b5400a", lw=1.8)
    ax2.set_xlabel("time (s)", fontsize=7.6); ax2.set_ylabel("sintered depth (mm)", fontsize=7.6)
    ax2.set_title("(b)  Sintered depth grows slowly", fontsize=8.0, fontweight="bold", loc="left")
    ax2.grid(alpha=0.25)
    ax2.text(0.96, 0.08, f"q$_{{abs}}$ = {float(d['q_abs_kWm2']):.0f} kW/m$^2$",
             transform=ax2.transAxes, ha="right", fontsize=6.4, color="#555")
    for s in ("top", "right"):
        ax2.spines[s].set_visible(False)
    fig.suptitle("Regolith's low conductivity confines the sintering front: throughput is set by "
                 "source power and dwell, not the coupon", fontsize=8.4, fontweight="bold", y=1.02)
    savefig(fig, str(FIGDIR / "Figure_P2_field"), formats=("png", "pdf"), dpi=600)
    print("WROTE Figure_P2_field")


# ---------- FIG C: physics closure boundary ----------
def fig_closure():
    d = np.load(HERE / "out_03_closure.npz")
    eta = d["eta_grid"]; cap = d["cap_grid"]
    blo = d["boundary_lo_kW"]; bhi = d["boundary_hi_kW"]
    YMAX = 90.0
    fig, ax = plt.subplots(figsize=(WIDTH_SINGLE*1.9, WIDTH_SINGLE*1.5))
    ax.fill_between(eta, blo, YMAX, color="#e3f1e7", alpha=0.7, zorder=0)
    ax.fill_between(eta, 0, bhi, color="#f7ece4", alpha=0.5, zorder=0)
    ax.plot(eta, blo, color="#2f8f4e", lw=1.8, label="closure boundary at 18 MJ/kg (Lim 2021)")
    ax.plot(eta, bhi, color="#b5400a", lw=1.8, label="closure boundary at 72 MJ/kg (Lim 2023)")
    ax.axvspan(eta[0], eta[-1], color="none")
    eref = float(d["eta_ref"])
    ax.plot([eref, eref], [float(d["cap_lo"]), float(d["cap_hi"])], color="#555", lw=1.0, ls=(0,(4,3)))
    ax.scatter([eref, eref], [float(d["cap_lo"]), float(d["cap_hi"])], color=["#2f8f4e","#b5400a"], s=40, zorder=5)
    ax.annotate(f"{float(d['cap_lo']):.0f} kW", (eref, float(d['cap_lo'])), xytext=(eref+0.03, float(d['cap_lo'])),
                fontsize=6.6, color="#2f8f4e", va="center")
    ax.annotate(f"{float(d['cap_hi']):.0f} kW", (eref, float(d['cap_hi'])), xytext=(eref+0.03, float(d['cap_hi'])),
                fontsize=6.6, color="#b5400a", va="center")
    ax.text(0.50, 70, "CLOSES\n(capacity above the boundary\nfor the operating energy/mass)",
            fontsize=6.6, color="#1f6e3a", ha="center", va="top")
    ax.text(0.13, 9, "does not close", fontsize=7.5, color="#a23b2b", fontweight="bold")
    ax.annotate(f"4x spread at $\\eta$=0.1:\n{float(d['cap_lo']):.0f}-{float(d['cap_hi']):.0f} kW",
                (0.10, float(d['cap_hi'])), xytext=(0.20, 78), fontsize=6.4, color="#333",
                ha="left", arrowprops=dict(arrowstyle="->", color="#555", lw=0.8))
    ax.text(0.40, 87, f"mission: {int(d['M_req'])} kg in {int(d['window_days'])} d; "
            "energy/mass calibrated to real census data", fontsize=6.2, color="#666",
            ha="center", style="italic", bbox=dict(boxstyle="round,pad=0.3", fc="#fbf1df", ec="#e0871a", lw=0.8))
    ax.set_xlim(eta[0], eta[-1]); ax.set_ylim(0, YMAX)
    ax.set_xlabel("wall-plug-to-process efficiency  $\\eta$  (unreported, 0/7)", fontsize=8.0)
    ax.set_ylabel("deployed source capacity (kW)  (unreported, 0/7)", fontsize=8.0)
    ax.set_title("Physics-derived closure boundary on the two unreported coordinates\n"
                 "(the required capacity spans ~4x with the calibrated energy/mass band)",
                 fontsize=8.2, fontweight="bold")
    ax.legend(fontsize=6.4, loc="upper right", frameon=True, framealpha=0.9)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    savefig(fig, str(FIGDIR / "Figure_P3_closure"), formats=("png", "pdf"), dpi=600)
    print("WROTE Figure_P3_closure")


if __name__ == "__main__":
    fig_mechanism()
    fig_field()
    fig_closure()
    print("all physics figures written to", FIGDIR)
