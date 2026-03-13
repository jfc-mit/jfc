#!/usr/bin/env python3
"""Phase 2 Exploration — Script 02: Comprehensive data characterization.

Produces all key distributions, data/MC comparisons, resolution studies,
thrust validation, cut boundary studies, and response matrix preview.
"""

import logging
import time
from pathlib import Path

import numpy as np
import uproot
import awkward as ak
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplhep as hep
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger("exploration")

plt.style.use(hep.style.CMS)
plt.rcParams.update({"figure.figsize": (8, 6), "font.size": 14})

# ---- Paths ----
DATA_DIR = Path("/n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ALEPH")
MC_DIR = Path("/n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ALEPHMC")
FIG_DIR = Path("/n/home07/anovak/work/reslop/analyses/thrust_measurement/phase2_exploration/figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

DATA_FILES = sorted(DATA_DIR.glob("LEP1Data*_recons_aftercut-MERGED.root"))
MC_FILES = sorted(MC_DIR.glob("LEP1MC1994_recons_aftercut-*.root"))

# ---- Branches ----
SCALAR_BRANCHES = [
    "Thrust", "Thrust_charged", "Thrust_neutral",
    "ThrustCorr", "ThrustCorrInverse", "ThrustWithMissP",
    "Sphericity", "STheta", "SPhi", "Energy",
    "nParticle", "nChargedHadrons", "nChargedHadronsHP",
    "missP", "missChargedP",
    "passesAll", "passesNTupleAfterCut", "passesTotalChgEnergyMin",
    "passesNTrkMin", "passesSTheta", "passesMissP",
    "passesISR", "passesWW", "passesNeuNch", "passesLEP1TwoPC",
    "particleWeight",
]

def save_fig(fig, name):
    path = FIG_DIR / f"{name}.pdf"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    log.info(f"  Saved: {path.name}")

def ratio_plot(ax, bc, h_num, h_den, **kwargs):
    r = np.divide(h_num, h_den, out=np.ones_like(h_num, dtype=float), where=h_den > 0)
    ax.plot(bc, r, "k.", markersize=3, **kwargs)
    ax.axhline(1.0, color="gray", ls="--", lw=0.8)
    ax.set_ylabel("Data / MC")

# ============================================================
# LOAD DATA — event-level scalars only (fast)
# ============================================================
t0 = time.time()
log.info("Loading data scalar branches (first file)...")
with uproot.open(DATA_FILES[0]) as f:
    data_evt = f["t"].arrays(SCALAR_BRANCHES, library="np")
n_data = len(data_evt["Thrust"])
log.info(f"  Data loaded: {n_data} events in {time.time()-t0:.1f}s")

t0 = time.time()
log.info("Loading MC scalar branches (first file)...")
with uproot.open(MC_FILES[0]) as f:
    mc_evt = f["t"].arrays(SCALAR_BRANCHES, library="np")

    mc_gen_branches = [
        "Thrust", "Thrust_charged", "Thrust_neutral",
        "ThrustCorr", "ThrustWithMissP",
        "Sphericity", "STheta", "Energy",
        "nParticle", "nChargedHadrons",
        "missP", "passesAll",
        "ThrustWithReco", "ThrustWithGenIneff",
        "ThrustWithRecoCorr",
        "particleWeight",
    ]
    mc_gen = f["tgen"].arrays(mc_gen_branches, library="np")

    mc_genBefore_branches = [
        "Thrust", "Thrust_charged", "Thrust_neutral",
        "Sphericity", "STheta", "Energy",
        "nParticle", "nChargedHadrons",
        "missP", "passesAll", "particleWeight",
    ]
    mc_genBefore = f["tgenBefore"].arrays(mc_genBefore_branches, library="np")

n_mc = len(mc_evt["Thrust"])
n_mcgen = len(mc_gen["Thrust"])
n_mcgenB = len(mc_genBefore["Thrust"])
log.info(f"  MC loaded: reco={n_mc}, gen={n_mcgen}, genBefore={n_mcgenB} in {time.time()-t0:.1f}s")

# ============================================================
# FIGURE 1: Thrust (tau = 1-T) distribution
# ============================================================
log.info("=== Figure 1: Thrust distribution ===")

tau_data = 1.0 - data_evt["Thrust"]
tau_mc = 1.0 - mc_evt["Thrust"]

fig, (ax1, ax2) = plt.subplots(2, 1, height_ratios=[3, 1], sharex=True,
                                gridspec_kw={"hspace": 0.05})
bins = np.linspace(0, 0.5, 51)
bc = 0.5 * (bins[:-1] + bins[1:])
bw = bins[1:] - bins[:-1]

h_d, _ = np.histogram(tau_data, bins=bins)
h_m, _ = np.histogram(tau_mc, bins=bins)
h_dn = h_d / (np.sum(h_d) * bw)
h_mn = h_m / (np.sum(h_m) * bw)
h_de = np.sqrt(h_d) / (np.sum(h_d) * bw)

ax1.errorbar(bc, h_dn, yerr=h_de, fmt="k.", label="ALEPH 1992 Data", ms=4)
ax1.stairs(h_mn, bins, color="tab:blue", lw=1.5, label="MC (reco)")
ax1.set_ylabel(r"$(1/N)\, \mathrm{d}N/\mathrm{d}\tau$")
ax1.set_yscale("log")
ax1.set_ylim(0.01, 100)
ax1.legend(fontsize=11)

r = np.divide(h_dn, h_mn, out=np.ones_like(h_dn), where=h_mn > 0)
re = np.divide(h_de, h_mn, out=np.zeros_like(h_de), where=h_mn > 0)
ax2.errorbar(bc, r, yerr=re, fmt="k.", ms=4)
ax2.axhline(1.0, color="gray", ls="--", lw=0.8)
ax2.set_xlabel(r"$\tau = 1 - T$")
ax2.set_ylabel("Data / MC")
ax2.set_ylim(0.8, 1.2)
save_fig(fig, "01_thrust_tau_data_mc")

# ============================================================
# FIGURE 2: Charged track multiplicity
# ============================================================
log.info("=== Figure 2: Charged track multiplicity ===")
nch_d = data_evt["nChargedHadrons"]
nch_m = mc_evt["nChargedHadrons"]

fig, (ax1, ax2) = plt.subplots(2, 1, height_ratios=[3, 1], sharex=True,
                                gridspec_kw={"hspace": 0.05})
bins_nch = np.arange(0, 61, 1) - 0.5
bc_n = 0.5 * (bins_nch[:-1] + bins_nch[1:])
h_d_n, _ = np.histogram(nch_d, bins=bins_nch)
h_m_n, _ = np.histogram(nch_m, bins=bins_nch)
h_dn2 = h_d_n / np.sum(h_d_n)
h_mn2 = h_m_n / np.sum(h_m_n)

ax1.errorbar(bc_n, h_dn2, yerr=np.sqrt(h_d_n)/np.sum(h_d_n), fmt="k.", ms=3, label="Data")
ax1.stairs(h_mn2, bins_nch, color="tab:blue", label="MC")
ax1.set_ylabel("Fraction of events")
ax1.set_yscale("log")
ax1.set_ylim(1e-5, 0.2)
ax1.legend()

ratio_plot(ax2, bc_n, h_dn2, h_mn2)
ax2.set_xlabel(r"$N_\mathrm{ch}$")
ax2.set_ylim(0.6, 1.4)
ax2.set_xlim(-0.5, 55)
save_fig(fig, "02_nch_data_mc")

# ============================================================
# FIGURE 3: Total visible energy
# ============================================================
log.info("=== Figure 3: Total visible energy ===")
e_d = data_evt["Energy"]
e_m = mc_evt["Energy"]

fig, (ax1, ax2) = plt.subplots(2, 1, height_ratios=[3, 1], sharex=True,
                                gridspec_kw={"hspace": 0.05})
bins_e = np.linspace(0, 150, 76)
bc_e = 0.5 * (bins_e[:-1] + bins_e[1:])
bw_e = bins_e[1:] - bins_e[:-1]
h_de, _ = np.histogram(e_d, bins=bins_e)
h_me, _ = np.histogram(e_m, bins=bins_e)
h_den = h_de / (np.sum(h_de) * bw_e)
h_men = h_me / (np.sum(h_me) * bw_e)

ax1.errorbar(bc_e, h_den, yerr=np.sqrt(h_de)/(np.sum(h_de)*bw_e), fmt="k.", ms=3, label="Data")
ax1.stairs(h_men, bins_e, color="tab:blue", label="MC")
ax1.set_ylabel(r"$(1/N)\, \mathrm{d}N/\mathrm{d}E$ [GeV$^{-1}$]")
ax1.set_yscale("log")
ax1.legend()

ratio_plot(ax2, bc_e, h_den, h_men)
ax2.set_xlabel("Total visible energy [GeV]")
ax2.set_ylim(0.5, 1.5)
save_fig(fig, "03_energy_data_mc")

# ============================================================
# FIGURE 4: cos(theta_sph)
# ============================================================
log.info("=== Figure 4: cos(theta_sph) ===")
ct_d = np.cos(data_evt["STheta"])
ct_m = np.cos(mc_evt["STheta"])

fig, (ax1, ax2) = plt.subplots(2, 1, height_ratios=[3, 1], sharex=True,
                                gridspec_kw={"hspace": 0.05})
bins_ct = np.linspace(-1, 1, 51)
bc_ct = 0.5 * (bins_ct[:-1] + bins_ct[1:])
bw_ct = bins_ct[1:] - bins_ct[:-1]
h_dc, _ = np.histogram(ct_d, bins=bins_ct)
h_mc_, _ = np.histogram(ct_m, bins=bins_ct)
h_dcn = h_dc / (np.sum(h_dc) * bw_ct)
h_mcn = h_mc_ / (np.sum(h_mc_) * bw_ct)

ax1.errorbar(bc_ct, h_dcn, yerr=np.sqrt(h_dc)/(np.sum(h_dc)*bw_ct), fmt="k.", ms=3, label="Data")
ax1.stairs(h_mcn, bins_ct, color="tab:blue", label="MC")
ax1.set_ylabel(r"$(1/N)\, \mathrm{d}N/\mathrm{d}\cos\theta_\mathrm{sph}$")
ax1.legend()

ratio_plot(ax2, bc_ct, h_dcn, h_mcn)
ax2.set_xlabel(r"$\cos\theta_\mathrm{sph}$")
ax2.set_ylim(0.8, 1.2)
save_fig(fig, "04_costheta_sph_data_mc")

# ============================================================
# FIGURE 5: Track pT and |p| (load particles for subset)
# ============================================================
log.info("=== Figure 5: Track pT and momentum ===")

# Load particle branches for 50k events only
NTRACK = 50000
with uproot.open(DATA_FILES[0]) as f:
    dp = f["t"].arrays(["pt", "pmag", "theta"], library="ak", entry_stop=NTRACK)
with uproot.open(MC_FILES[0]) as f:
    mp = f["t"].arrays(["pt", "pmag", "theta"], library="ak", entry_stop=NTRACK)

pt_d = ak.to_numpy(ak.flatten(dp["pt"]))
pt_m = ak.to_numpy(ak.flatten(mp["pt"]))
pmag_d = ak.to_numpy(ak.flatten(dp["pmag"]))
pmag_m = ak.to_numpy(ak.flatten(mp["pmag"]))

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# pT
bins_pt = np.linspace(0, 20, 101)
bc_pt = 0.5 * (bins_pt[:-1] + bins_pt[1:])
bw_pt = bins_pt[1:] - bins_pt[:-1]
h_dpt, _ = np.histogram(pt_d, bins=bins_pt)
h_mpt, _ = np.histogram(pt_m, bins=bins_pt)
axes[0].errorbar(bc_pt, h_dpt/(np.sum(h_dpt)*bw_pt),
                 yerr=np.sqrt(h_dpt)/(np.sum(h_dpt)*bw_pt), fmt="k.", ms=2, label="Data")
axes[0].stairs(h_mpt/(np.sum(h_mpt)*bw_pt), bins_pt, color="tab:blue", label="MC")
axes[0].set_xlabel(r"Track $p_\mathrm{T}$ [GeV]")
axes[0].set_ylabel(r"$(1/N)\, \mathrm{d}N/\mathrm{d}p_\mathrm{T}$")
axes[0].set_yscale("log")
axes[0].legend(fontsize=10)

# |p|
bins_p = np.linspace(0, 50, 101)
bc_p = 0.5 * (bins_p[:-1] + bins_p[1:])
bw_p = bins_p[1:] - bins_p[:-1]
h_dp, _ = np.histogram(pmag_d, bins=bins_p)
h_mp, _ = np.histogram(pmag_m, bins=bins_p)
axes[1].errorbar(bc_p, h_dp/(np.sum(h_dp)*bw_p),
                 yerr=np.sqrt(h_dp)/(np.sum(h_dp)*bw_p), fmt="k.", ms=2, label="Data")
axes[1].stairs(h_mp/(np.sum(h_mp)*bw_p), bins_p, color="tab:blue", label="MC")
axes[1].set_xlabel(r"Track $|p|$ [GeV]")
axes[1].set_ylabel(r"$(1/N)\, \mathrm{d}N/\mathrm{d}|p|$")
axes[1].set_yscale("log")
axes[1].legend(fontsize=10)

save_fig(fig, "05_track_pt_pmag_data_mc")

# ============================================================
# FIGURE 6: Track polar angle
# ============================================================
log.info("=== Figure 6: Track polar angle ===")

theta_d = ak.to_numpy(ak.flatten(dp["theta"]))
theta_m = ak.to_numpy(ak.flatten(mp["theta"]))

fig, ax = plt.subplots()
bins_th = np.linspace(0, np.pi, 51)
bc_th = 0.5 * (bins_th[:-1] + bins_th[1:])
bw_th = bins_th[1:] - bins_th[:-1]
h_dth, _ = np.histogram(theta_d, bins=bins_th)
h_mth, _ = np.histogram(theta_m, bins=bins_th)
ax.errorbar(bc_th, h_dth/(np.sum(h_dth)*bw_th),
            yerr=np.sqrt(h_dth)/(np.sum(h_dth)*bw_th), fmt="k.", ms=3, label="Data")
ax.stairs(h_mth/(np.sum(h_mth)*bw_th), bins_th, color="tab:blue", label="MC")
ax.set_xlabel(r"Track $\theta$ [rad]")
ax.set_ylabel(r"$(1/N)\, \mathrm{d}N/\mathrm{d}\theta$")
ax.legend()
save_fig(fig, "06_track_theta_data_mc")

# Clean up particle arrays
del dp, mp, pt_d, pt_m, pmag_d, pmag_m, theta_d, theta_m

# ============================================================
# FIGURE 7: Thrust recomputation check
# ============================================================
log.info("=== Figure 7: Thrust recomputation from 4-vectors ===")

# Load px, py, pz for 500 events
N_CHECK = 500
with uproot.open(DATA_FILES[0]) as f:
    check_ptcl = f["t"].arrays(["px", "py", "pz"], library="ak", entry_stop=N_CHECK)

stored_T = data_evt["Thrust"][:N_CHECK]
recomp_T = np.zeros(N_CHECK)

for i in range(N_CHECK):
    px = ak.to_numpy(check_ptcl["px"][i])
    py = ak.to_numpy(check_ptcl["py"][i])
    pz = ak.to_numpy(check_ptcl["pz"][i])
    pmag = np.sqrt(px**2 + py**2 + pz**2)
    total_p = np.sum(pmag)
    if total_p == 0:
        continue
    best = 0.0
    for j in range(len(px)):
        if pmag[j] == 0:
            continue
        nx, ny, nz = px[j]/pmag[j], py[j]/pmag[j], pz[j]/pmag[j]
        proj = np.abs(px*nx + py*ny + pz*nz)
        t = np.sum(proj) / total_p
        if t > best:
            best = t
    recomp_T[i] = best

diff = stored_T - recomp_T

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
axes[0].scatter(stored_T, recomp_T, s=1, alpha=0.5, color="tab:blue")
axes[0].plot([0.5, 1.0], [0.5, 1.0], "r--", lw=1)
axes[0].set_xlabel("Stored Thrust $T$")
axes[0].set_ylabel("Recomputed Thrust $T$")
axes[0].set_xlim(0.5, 1.0)
axes[0].set_ylim(0.5, 1.0)

axes[1].hist(diff, bins=50, range=(-0.05, 0.05), histtype="step", color="tab:blue")
axes[1].set_xlabel("Stored $T$ - Recomputed $T$")
axes[1].set_ylabel("Events")
axes[1].axvline(0, color="red", ls="--", lw=0.8)
mean_d = np.mean(diff)
std_d = np.std(diff)
axes[1].text(0.95, 0.95, f"mean = {mean_d:.5f}\nstd = {std_d:.5f}",
             transform=axes[1].transAxes, ha="right", va="top", fontsize=10)
save_fig(fig, "07_thrust_recomputation_check")
log.info(f"  Thrust recomputation: mean diff = {mean_d:.6f}, std = {std_d:.6f}")
del check_ptcl

# ============================================================
# FIGURE 8: Cut boundary distributions
# ============================================================
log.info("=== Figure 8: Cut boundaries ===")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 8a: |cos(theta_sph)| near 0.82
abs_ct_d = np.abs(ct_d)
abs_ct_m = np.abs(ct_m)
bins8a = np.linspace(0, 1.0, 101)
bc8a = 0.5 * (bins8a[:-1] + bins8a[1:])
h8ad, _ = np.histogram(abs_ct_d, bins=bins8a)
h8am, _ = np.histogram(abs_ct_m, bins=bins8a)
axes[0,0].errorbar(bc8a, h8ad/np.sum(h8ad), yerr=np.sqrt(h8ad)/np.sum(h8ad), fmt="k.", ms=2, label="Data")
axes[0,0].stairs(h8am/np.sum(h8am), bins8a, color="tab:blue", label="MC")
axes[0,0].axvline(0.82, color="red", ls="--", lw=1, label=r"$|\cos\theta|=0.82$")
axes[0,0].set_xlabel(r"$|\cos\theta_\mathrm{sph}|$")
axes[0,0].set_ylabel("Fraction")
axes[0,0].legend(fontsize=9)

# 8b: nChargedHadrons near 5
bins8b = np.arange(0, 30, 1) - 0.5
bc8b = 0.5 * (bins8b[:-1] + bins8b[1:])
h8bd, _ = np.histogram(nch_d, bins=bins8b)
h8bm, _ = np.histogram(nch_m, bins=bins8b)
axes[0,1].errorbar(bc8b, h8bd/np.sum(h8bd), yerr=np.sqrt(h8bd)/np.sum(h8bd), fmt="k.", ms=2, label="Data")
axes[0,1].stairs(h8bm/np.sum(h8bm), bins8b, color="tab:blue", label="MC")
axes[0,1].axvline(5, color="red", ls="--", lw=1, label="$N_{ch} = 5$")
axes[0,1].set_xlabel(r"$N_\mathrm{ch}$")
axes[0,1].set_ylabel("Fraction")
axes[0,1].set_xlim(-0.5, 25)
axes[0,1].set_yscale("log")
axes[0,1].legend(fontsize=9)

# 8c: missP near 20
mp_d = data_evt["missP"]
mp_m = mc_evt["missP"]
bins8c = np.linspace(0, 40, 81)
bc8c = 0.5 * (bins8c[:-1] + bins8c[1:])
h8cd, _ = np.histogram(mp_d, bins=bins8c)
h8cm, _ = np.histogram(mp_m, bins=bins8c)
axes[1,0].errorbar(bc8c, h8cd/np.sum(h8cd), yerr=np.sqrt(h8cd)/np.sum(h8cd), fmt="k.", ms=2, label="Data")
axes[1,0].stairs(h8cm/np.sum(h8cm), bins8c, color="tab:blue", label="MC")
axes[1,0].axvline(20, color="red", ls="--", lw=1, label="missP = 20 GeV")
axes[1,0].set_xlabel("Missing momentum [GeV]")
axes[1,0].set_ylabel("Fraction")
axes[1,0].set_yscale("log")
axes[1,0].legend(fontsize=9)

# 8d: Energy near 15 GeV
bins8d = np.linspace(0, 120, 121)
bc8d = 0.5 * (bins8d[:-1] + bins8d[1:])
h8dd, _ = np.histogram(e_d, bins=bins8d)
h8dm, _ = np.histogram(e_m, bins=bins8d)
axes[1,1].errorbar(bc8d, h8dd/np.sum(h8dd), yerr=np.sqrt(h8dd)/np.sum(h8dd), fmt="k.", ms=2, label="Data")
axes[1,1].stairs(h8dm/np.sum(h8dm), bins8d, color="tab:blue", label="MC")
axes[1,1].axvline(15, color="red", ls="--", lw=1, label="E > 15 GeV")
axes[1,1].set_xlabel("Visible energy [GeV]")
axes[1,1].set_ylabel("Fraction")
axes[1,1].set_yscale("log")
axes[1,1].legend(fontsize=9)

fig.tight_layout()
save_fig(fig, "08_cut_boundaries")

# Also report what fraction is below cut boundaries
log.info(f"  Data events with |cos_sph| > 0.82: {np.sum(abs_ct_d > 0.82)}/{n_data} = {np.mean(abs_ct_d > 0.82):.4f}")
log.info(f"  Data events with nCh < 5: {np.sum(nch_d < 5)}/{n_data} = {np.mean(nch_d < 5):.6f}")
log.info(f"  Data events with missP > 20: {np.sum(mp_d > 20)}/{n_data} = {np.mean(mp_d > 20):.4f}")
log.info(f"  Data events with E < 15: {np.sum(e_d < 15)}/{n_data} = {np.mean(e_d < 15):.6f}")

# ============================================================
# FIGURE 9: Resolution study (reco vs gen thrust)
# ============================================================
log.info("=== Figure 9: Resolution study ===")

tau_reco = 1.0 - mc_evt["Thrust"]
tau_gen = 1.0 - mc_gen["Thrust"]
delta_tau = tau_reco - tau_gen

fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))

# 9a: 2D response matrix preview
h2d, xe, ye = np.histogram2d(tau_reco, tau_gen,
                              bins=[np.linspace(0, 0.5, 51), np.linspace(0, 0.5, 51)])
im = axes[0].pcolormesh(ye, xe, h2d, cmap="Blues",
                        norm=matplotlib.colors.LogNorm(vmin=0.5))
axes[0].plot([0, 0.5], [0, 0.5], "r--", lw=0.8)
axes[0].set_xlabel(r"$\tau_\mathrm{gen}$")
axes[0].set_ylabel(r"$\tau_\mathrm{reco}$")
fig.colorbar(im, ax=axes[0], label="Events")

# 9b: Delta tau
axes[1].hist(delta_tau, bins=100, range=(-0.1, 0.1), histtype="step", color="tab:blue")
axes[1].set_xlabel(r"$\tau_\mathrm{reco} - \tau_\mathrm{gen}$")
axes[1].set_ylabel("Events")
axes[1].axvline(0, color="red", ls="--", lw=0.8)
axes[1].text(0.95, 0.95, f"mean={np.mean(delta_tau):.4f}\nRMS={np.std(delta_tau):.4f}",
             transform=axes[1].transAxes, ha="right", va="top", fontsize=10)

# 9c: RMS vs tau_gen
tg_bins = np.linspace(0, 0.45, 19)
bc_tg = 0.5 * (tg_bins[:-1] + tg_bins[1:])
rms_v = []
mean_v = []
for i in range(len(tg_bins)-1):
    mask = (tau_gen >= tg_bins[i]) & (tau_gen < tg_bins[i+1])
    if np.sum(mask) > 10:
        rms_v.append(np.std(delta_tau[mask]))
        mean_v.append(np.mean(delta_tau[mask]))
    else:
        rms_v.append(np.nan)
        mean_v.append(np.nan)

axes[2].plot(bc_tg, rms_v, "bo-", ms=4, label="RMS")
axes[2].plot(bc_tg, np.abs(mean_v), "rs--", ms=4, label="|Mean bias|")
axes[2].set_xlabel(r"$\tau_\mathrm{gen}$")
axes[2].set_ylabel(r"$\sigma(\tau_\mathrm{reco} - \tau_\mathrm{gen})$")
axes[2].legend(fontsize=10)

fig.tight_layout()
save_fig(fig, "09_resolution_study")
log.info(f"  Resolution: mean={np.mean(delta_tau):.5f}, RMS={np.std(delta_tau):.5f}")

# ============================================================
# FIGURE 10: Cutflow
# ============================================================
log.info("=== Figure 10: Cutflow ===")

cut_names = ["passesNTupleAfterCut", "passesTotalChgEnergyMin", "passesNTrkMin",
             "passesSTheta", "passesMissP", "passesISR", "passesWW",
             "passesNeuNch", "passesLEP1TwoPC", "passesAll"]
cut_labels = ["NTuple\nAfterCut", "ChgE\n>15", "NTrk\n>=5", "STheta", "MissP\n<20",
              "ISR", "WW", "NeuNch", "LEP1\n2PC", "All"]

d_yields = [np.sum(data_evt[c]) for c in cut_names]
m_yields = [np.sum(mc_evt[c]) for c in cut_names]
d_eff = np.array(d_yields) / n_data
m_eff = np.array(m_yields) / n_mc

fig, ax = plt.subplots(figsize=(12, 6))
x = np.arange(len(cut_names))
w = 0.35
ax.bar(x - w/2, d_eff, w, label="Data", color="black", alpha=0.7)
ax.bar(x + w/2, m_eff, w, label="MC", color="tab:blue", alpha=0.7)
ax.set_ylabel("Fraction passing")
ax.set_xticks(x)
ax.set_xticklabels(cut_labels, fontsize=9)
ax.legend()
ax.set_ylim(0.9, 1.01)
save_fig(fig, "10_cutflow")

log.info("  CUTFLOW TABLE:")
log.info(f"  {'Cut':<30s} {'Data':>12s} {'Eff':>8s} {'MC':>12s} {'Eff':>8s}")
log.info(f"  {'Total':<30s} {n_data:>12d} {'1.0000':>8s} {n_mc:>12d} {'1.0000':>8s}")
for i, c in enumerate(cut_names):
    log.info(f"  {c:<30s} {d_yields[i]:>12.0f} {d_eff[i]:>8.4f} {m_yields[i]:>12.0f} {m_eff[i]:>8.4f}")

# ============================================================
# FIGURE 11: Weight distributions
# ============================================================
log.info("=== Figure 11: Weights ===")

pw_d = data_evt["particleWeight"]
pw_m = mc_evt["particleWeight"]

fig, ax = plt.subplots()
ax.hist(pw_d, bins=50, range=(pw_d.min()-0.01, pw_d.max()+0.01), histtype="step", color="black", label="Data")
ax.hist(pw_m, bins=50, range=(pw_m.min()-0.01, pw_m.max()+0.01), histtype="step", color="tab:blue", label="MC")
ax.set_xlabel("particleWeight")
ax.set_ylabel("Events")
ax.legend()
ax.set_yscale("log")
save_fig(fig, "11_weight_distributions")

log.info(f"  Data particleWeight: unique values = {np.unique(pw_d)}")
log.info(f"  MC particleWeight: unique values (first 10) = {np.unique(pw_m)[:10]}")
log.info(f"  Data particleWeight range: [{pw_d.min():.4f}, {pw_d.max():.4f}], mean={pw_d.mean():.4f}")
log.info(f"  MC particleWeight range: [{pw_m.min():.4f}, {pw_m.max():.4f}], mean={pw_m.mean():.4f}")

# ============================================================
# FIGURE 12: Thrust variants comparison
# ============================================================
log.info("=== Figure 12: Thrust variants ===")

variants = {
    "Thrust": data_evt["Thrust"],
    "ThrustCorr": data_evt["ThrustCorr"],
    "ThrustCorrInverse": data_evt["ThrustCorrInverse"],
    "Thrust_charged": data_evt["Thrust_charged"],
    "Thrust_neutral": data_evt["Thrust_neutral"],
    "ThrustWithMissP": data_evt["ThrustWithMissP"],
}

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
for ax, (name, vals) in zip(axes.flat, variants.items()):
    tau_v = 1.0 - vals
    ax.hist(tau_v, bins=50, range=(0, 0.5), histtype="step", color="tab:blue")
    ax.set_xlabel(f"$\\tau$ from {name}")
    ax.set_ylabel("Events")
    ax.set_yscale("log")
    ax.text(0.95, 0.95, f"mean={np.mean(tau_v):.4f}\nstd={np.std(tau_v):.4f}",
            transform=ax.transAxes, ha="right", va="top", fontsize=9)
fig.tight_layout()
save_fig(fig, "12_thrust_variants")

# ============================================================
# FIGURE 13: Efficiency vs tau_gen
# ============================================================
log.info("=== Figure 13: Efficiency ===")

tau_tgen = 1.0 - mc_gen["Thrust"]
tau_tgenB = 1.0 - mc_genBefore["Thrust"]

eff_bins = np.linspace(0, 0.5, 26)
h_tg, _ = np.histogram(tau_tgen, bins=eff_bins)
h_tgB, _ = np.histogram(tau_tgenB, bins=eff_bins)
eff = np.divide(h_tg.astype(float), h_tgB.astype(float),
                out=np.zeros(len(h_tg), dtype=float), where=h_tgB > 0)
eff_err = np.sqrt(eff * (1-eff) / np.maximum(h_tgB, 1))
bc_eff = 0.5 * (eff_bins[:-1] + eff_bins[1:])

fig, ax = plt.subplots()
ax.errorbar(bc_eff, eff, yerr=eff_err, fmt="bo-", ms=4)
ax.set_xlabel(r"$\tau_\mathrm{gen}$")
ax.set_ylabel(r"Efficiency $\varepsilon(\tau_\mathrm{gen})$")
ax.set_ylim(0, 1.1)
ax.axhline(1.0, color="gray", ls="--", lw=0.5)
save_fig(fig, "13_efficiency_vs_tau_gen")
log.info(f"  Mean efficiency: {np.mean(eff[eff > 0]):.4f}")

# ============================================================
# FIGURE 14: MC event matching verification
# ============================================================
log.info("=== Figure 14: MC event matching ===")

T_reco = mc_evt["Thrust"]
T_gen_matched = mc_gen["Thrust"]
T_withReco = mc_gen["ThrustWithReco"]

fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))

axes[0].scatter(T_gen_matched, T_reco, s=0.5, alpha=0.3, color="tab:blue")
axes[0].plot([0.5, 1], [0.5, 1], "r--", lw=0.8)
axes[0].set_xlabel("Gen Thrust (tgen)")
axes[0].set_ylabel("Reco Thrust (t)")

diff_rc = T_reco - T_withReco
axes[1].hist(diff_rc, bins=100, range=(-0.01, 0.01), histtype="step", color="tab:blue")
axes[1].set_xlabel("t.Thrust - tgen.ThrustWithReco")
axes[1].set_ylabel("Events")
axes[1].axvline(0, color="red", ls="--", lw=0.8)
axes[1].text(0.05, 0.95, f"mean={np.mean(diff_rc):.6f}\nstd={np.std(diff_rc):.6f}",
             transform=axes[1].transAxes, ha="left", va="top", fontsize=10)

# Gen spectra comparison
bins14 = np.linspace(0, 0.5, 51)
bc14 = 0.5 * (bins14[:-1] + bins14[1:])
bw14 = bins14[1:] - bins14[:-1]
h_tg14, _ = np.histogram(tau_tgen, bins=bins14)
h_tgB14, _ = np.histogram(tau_tgenB, bins=bins14)
axes[2].stairs(h_tg14/(np.sum(h_tg14)*bw14), bins14, color="tab:blue", label="tgen (reco-matched)")
axes[2].stairs(h_tgB14/(np.sum(h_tgB14)*bw14), bins14, color="tab:orange", label="tgenBefore (all gen)")
axes[2].set_xlabel(r"$\tau_\mathrm{gen}$")
axes[2].set_ylabel(r"$(1/N)\, \mathrm{d}N/\mathrm{d}\tau$")
axes[2].set_yscale("log")
axes[2].legend(fontsize=10)

fig.tight_layout()
save_fig(fig, "14_mc_event_matching")

# ============================================================
# FIGURE 15: nParticle
# ============================================================
log.info("=== Figure 15: nParticle ===")

np_d = data_evt["nParticle"]
np_m = mc_evt["nParticle"]

fig, ax = plt.subplots()
bins15 = np.arange(0, 80, 1) - 0.5
bc15 = 0.5 * (bins15[:-1] + bins15[1:])
h15d, _ = np.histogram(np_d, bins=bins15)
h15m, _ = np.histogram(np_m, bins=bins15)
ax.errorbar(bc15, h15d/np.sum(h15d), yerr=np.sqrt(h15d)/np.sum(h15d), fmt="k.", ms=2, label="Data")
ax.stairs(h15m/np.sum(h15m), bins15, color="tab:blue", label="MC")
ax.set_xlabel("nParticle (charged + neutral)")
ax.set_ylabel("Fraction")
ax.set_yscale("log")
ax.axvline(13, color="red", ls="--", lw=1, label="Cut: nParticle >= 13")
ax.legend(fontsize=10)
ax.set_xlim(-0.5, 75)
save_fig(fig, "15_nparticle_data_mc")

# ============================================================
# FIGURE 16: Sphericity
# ============================================================
log.info("=== Figure 16: Sphericity ===")

sph_d = data_evt["Sphericity"]
sph_m = mc_evt["Sphericity"]

fig, ax = plt.subplots()
bins16 = np.linspace(0, 1, 51)
bc16 = 0.5 * (bins16[:-1] + bins16[1:])
bw16 = bins16[1:] - bins16[:-1]
h16d, _ = np.histogram(sph_d, bins=bins16)
h16m, _ = np.histogram(sph_m, bins=bins16)
ax.errorbar(bc16, h16d/(np.sum(h16d)*bw16), yerr=np.sqrt(h16d)/(np.sum(h16d)*bw16),
            fmt="k.", ms=3, label="Data")
ax.stairs(h16m/(np.sum(h16m)*bw16), bins16, color="tab:blue", label="MC")
ax.set_xlabel("Sphericity")
ax.set_ylabel(r"$(1/N)\, \mathrm{d}N/\mathrm{d}S$")
ax.set_yscale("log")
ax.legend()
save_fig(fig, "16_sphericity_data_mc")

# ============================================================
# Summary statistics
# ============================================================
log.info("\n" + "="*60)
log.info("SUMMARY")
log.info("="*60)
log.info(f"Data file: {DATA_FILES[0].name}, {n_data} events")
log.info(f"MC file: {MC_FILES[0].name}, reco={n_mc}, gen={n_mcgen}, genBefore={n_mcgenB}")
log.info(f"passesAll fraction — Data: {np.mean(data_evt['passesAll']):.4f}, MC: {np.mean(mc_evt['passesAll']):.4f}")
log.info(f"Thrust resolution (reco-gen): mean={np.mean(delta_tau):.5f}, RMS={np.std(delta_tau):.5f}")
log.info(f"Mean efficiency: {np.mean(eff[eff>0]):.4f}")
log.info(f"t.Thrust - tgen.ThrustWithReco: mean={np.mean(diff_rc):.7f}, std={np.std(diff_rc):.7f}")
log.info(f"Data events below nCh=5: {np.sum(nch_d < 5)}")
log.info(f"Data events above |cos_sph|=0.82: {np.sum(abs_ct_d > 0.82)}")
log.info(f"Data events with missP > 20: {np.sum(mp_d > 20)}")
log.info(f"Data events with E < 15: {np.sum(e_d < 15)}")

log.info("\nDone.")
