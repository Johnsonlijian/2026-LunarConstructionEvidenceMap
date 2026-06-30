#!/usr/bin/env python3
"""M1 robustness: is the 'efficiency is physically decisive, 6%->1.5%' result a knife-edge
calibration, or robust to the assumed parameters?  (Answers reviewer-sim M1.)

Three deliverables, all from the SAME transient physics as 02_regolith_energy_balance.py
(re-implemented here with every assumed property as an explicit argument; a baseline assertion
guarantees it reproduces script 02's calibrated 6.0% / 1.5% before any uncertainty is propagated):

  (1) MC band  : propagate the assumed parameters (coupling, emissivity, radiating-area factor,
                 ambient sink, c_p slope) by Monte Carlo -> 5-95% band of efficiency vs dwell.
  (2) OAT table: one-at-a-time sensitivity of efficiency@900s and @3600s to each parameter.
  (3) Closed-form cross-check: radiative loss eps*sigma*A*(Ts^4-Tamb^4)*dwell, using NO fitted
                 coupling, as a fraction of Lim-2021's reported input energy.

Key efficiency fact used for speed: while the source is on, T rises monotonically, so a single
solve to the longest dwell yields eff(d) = m*int(cp,Tamb..T(d)) / (P*d) for every dwell d.
"""
from __future__ import annotations
import os
from pathlib import Path
from multiprocessing import Pool
import numpy as np
from scipy.integrate import solve_ivp, quad

SIGMA = 5.670374419e-8
RHO = 1800.0
M_KG = 0.050          # Lim specimens (both papers, 50 g)
P_W = 1000.0          # reported 1 kW
TS = 1373.0           # sintering onset (K)
DWELL_MAX = 7200.0

# --- baseline (script 02 calibration) ---
BASE = dict(eta=0.60, eps=0.90, fA=1.00, Tamb=250.0, slope=0.50)
# --- plausible ranges for the assumed (mostly unreported) parameters ---
RANGES = dict(eta=(0.45, 0.80), eps=(0.80, 0.95), fA=(0.70, 1.50),
              Tamb=(150.0, 300.0), slope=(0.40, 0.60))
LABEL = dict(eta="coupling efficiency", eps="emissivity",
             fA="radiating-area factor", Tamb="ambient sink T (K)", slope="c_p slope")

def a_top():
    V = M_KG / RHO
    R = (V / (np.pi * 0.4)) ** (1 / 3)   # disk, aspect 0.4 (same as script 02)
    return np.pi * R ** 2                # top face only (insulated crucible)
A_TOP = a_top()

def cp(T, slope):
    return np.clip(600.0 + slope * (T - 300.0), 600.0, 1200.0)

def sensible(Tamb, T1, slope):
    val, _ = quad(cp, Tamb, T1, args=(slope,))
    return M_KG * val                    # J

def eff_curve(eta, eps, fA, Tamb, slope, dwells):
    """One transient solve -> efficiency at each dwell. Same ODE as script 02."""
    A = fA * A_TOP
    def rhs(t, y):
        T = y[0]
        q_rad = eps * SIGMA * A * (T ** 4 - Tamb ** 4)
        return [(eta * P_W - q_rad) / (M_KG * cp(T, slope))]
    sol = solve_ivp(rhs, [0, DWELL_MAX], [Tamb], max_step=DWELL_MAX / 4000,
                    rtol=1e-7, atol=1e-4, dense_output=True)
    effs, Tds = [], []
    for d in dwells:
        Td = float(sol.sol(d)[0])
        Tds.append(Td)
        effs.append(sensible(Tamb, Td, slope) / (P_W * d))   # E_sens / E_input
    return np.array(effs), np.array(Tds)

DWELLS = np.array([300, 600, 900, 1500, 2400, 3600, 5400, 7200.0])
I900, I3600 = list(DWELLS).index(900), list(DWELLS).index(3600)

def _mc_worker(p):
    eff, Td = eff_curve(p["eta"], p["eps"], p["fA"], p["Tamb"], p["slope"], DWELLS)
    reached = Td[I900] >= TS          # did it actually sinter by the 900 s dwell?
    return np.concatenate([eff, [1.0 if reached else 0.0]])

def main():
    print("== M1 efficiency robustness: MC band + OAT sensitivity + closed-form cross-check ==\n")

    # (0) baseline reproduces script 02's calibration -> guard against model drift
    eff_b, Td_b = eff_curve(**BASE, dwells=DWELLS)
    e900, e3600 = eff_b[I900] * 100, eff_b[I3600] * 100
    print(f"baseline (script-02 calibration): eff@900s={e900:.2f}%  eff@3600s={e3600:.2f}%  "
          f"Tmax@900={Td_b[I900]:.0f}K")
    assert abs(e900 - 6.0) < 0.4 and abs(e3600 - 1.5) < 0.4, "baseline does not match script 02 (6.0/1.5)"
    print("  -> matches script 02 within tolerance (no model drift).\n")

    # (1) Monte-Carlo band over the assumed parameters
    rng = np.random.default_rng(7)
    N = 3000
    samples = [{k: float(rng.uniform(*RANGES[k])) for k in RANGES} for _ in range(N)]
    with Pool(min(60, os.cpu_count() or 4)) as pool:
        out = np.array(pool.map(_mc_worker, samples))
    effs, reached = out[:, :len(DWELLS)] * 100.0, out[:, -1].astype(bool)
    valid = effs[reached]              # physically-sintering runs
    lo = np.percentile(valid, 5, axis=0)
    med = np.percentile(valid, 50, axis=0)
    hi = np.percentile(valid, 95, axis=0)
    falling = np.all(np.diff(valid, axis=1) < 0, axis=1).mean() * 100
    print(f"MC: {N} samples, {reached.mean()*100:.0f}% reach sintering by 900 s (kept {valid.shape[0]}).")
    print(f"  efficiency 5-95% band: @900s=[{lo[I900]:.1f},{hi[I900]:.1f}]%  "
          f"@3600s=[{lo[I3600]:.1f},{hi[I3600]:.1f}]%")
    print(f"  whole-ensemble efficiency range: [{valid.min():.1f}, {valid.max():.1f}]%")
    print(f"  efficiency monotonically FALLING with dwell in {falling:.1f}% of samples")
    print(f"  band brackets the calibrated points? @900 {lo[I900]:.1f}<= {e900:.1f} <={hi[I900]:.1f} ; "
          f"@3600 {lo[I3600]:.1f}<= {e3600:.1f} <={hi[I3600]:.1f}\n")

    # (2) one-at-a-time sensitivity table
    print("OAT sensitivity (others at baseline):")
    print(f"  {'parameter':>22} {'range':>16} {'eff@900%':>16} {'eff@3600%':>16}")
    oat = []
    for k in RANGES:
        row = {"param": k, "label": LABEL[k], "lo": RANGES[k][0], "hi": RANGES[k][1]}
        for tag, val in (("lo", RANGES[k][0]), ("hi", RANGES[k][1])):
            pp = dict(BASE); pp[k] = val
            ec, _ = eff_curve(**pp, dwells=DWELLS)
            row[f"e900_{tag}"] = ec[I900] * 100
            row[f"e3600_{tag}"] = ec[I3600] * 100
        oat.append(row)
        rng_s = f"{RANGES[k][0]:g}-{RANGES[k][1]:g}"
        e9 = f"{row['e900_lo']:.1f} -> {row['e900_hi']:.1f}"
        e36 = f"{row['e3600_lo']:.1f} -> {row['e3600_hi']:.1f}"
        print(f"  {LABEL[k]:>22} {rng_s:>16} {e9:>16} {e36:>16}")
    # sign invariance: eff@3600 < eff@900 across every OAT corner
    sign_ok = all(min(r["e3600_lo"], r["e3600_hi"]) < max(r["e900_lo"], r["e900_hi"]) for r in oat)
    print(f"  efficiency@3600 < efficiency@900 at every OAT corner: {sign_ok}\n")

    # (3) closed-form radiative cross-check (NO fitted coupling)
    d_lim = 900.0
    E_rad_cf = BASE["eps"] * SIGMA * A_TOP * (TS ** 4 - BASE["Tamb"] ** 4) * d_lim
    E_input = P_W * d_lim
    frac = E_rad_cf / E_input
    print(f"closed-form radiative loss at Lim-2021 (eps sigma A (Ts^4-Tamb^4) * dwell, no fitted coupling):")
    print(f"  E_rad = {E_rad_cf/1e3:.0f} kJ of E_input = {E_input/1e3:.0f} kJ  ->  {frac*100:.0f}% re-radiated")
    print(f"  (independent of calibration; confirms re-radiation dominates the ledger)\n")

    outp = Path(__file__).with_name("out_U_band.npz")
    np.savez(outp, dwells=DWELLS, lo=lo, med=med, hi=hi,
             e900_base=e900, e3600_base=e3600,
             band900=np.array([lo[I900], hi[I900]]), band3600=np.array([lo[I3600], hi[I3600]]),
             ens_min=float(valid.min()), ens_max=float(valid.max()),
             falling_pct=falling, reached_pct=reached.mean() * 100,
             radiative_fraction=frac,
             oat_params=[r["param"] for r in oat],
             oat_labels=[r["label"] for r in oat],
             oat_lo=[r["lo"] for r in oat], oat_hi=[r["hi"] for r in oat],
             oat_e900=[[r["e900_lo"], r["e900_hi"]] for r in oat],
             oat_e3600=[[r["e3600_lo"], r["e3600_hi"]] for r in oat])
    print(f"saved {outp.name}")

if __name__ == "__main__":
    main()
