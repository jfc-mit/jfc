#!/usr/bin/env python3
"""Phase 2 — Script 03: Full-statistics event counts and data/MC thrust comparison.

Loads ALL data files and ALL MC files to get definitive event counts
and produce the full-statistics tau distribution comparison.
"""

import logging
import time
from pathlib import Path

import numpy as np
import uproot
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
log = logging.getLogger("full_stats")

plt.style.use(hep.style.CMS)
plt.rcParams.update({"figure.figsize": (8, 6), "font.size": 14})

DATA_DIR = Path("/n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ALEPH")
MC_DIR = Path("/n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ALEPHMC")
FIG_DIR = Path("/n/home07/anovak/work/reslop/analyses/thrust_measurement/phase2_exploration/figures")

DATA_FILES = sorted(DATA_DIR.glob("LEP1Data*_recons_aftercut-MERGED.root"))
MC_FILES = sorted(MC_DIR.glob("LEP1MC1994_recons_aftercut-*.root"))

BRANCHES = ["Thrust", "nChargedHadrons", "Energy", "STheta", "missP",
            "passesAll", "nParticle", "Sphericity", "passesNTupleAfterCut",
            "passesTotalChgEnergyMin", "passesNTrkMin", "passesSTheta",
            "passesMissP", "passesISR", "passesWW", "passesNeuNch",
            "passesLEP1TwoPC"]

# ============================================================
# Load all data
# ============================================================
t0 = time.time()
log.info("Loading all data files...")
data_arrays = {b: [] for b in BRANCHES}
data_counts = {}

for fpath in DATA_FILES:
    with uproot.open(fpath) as f:
        arr = f["t"].arrays(BRANCHES, library="np")
        n = len(arr["Thrust"])
        data_counts[fpath.name] = n
        for b in BRANCHES:
            data_arrays[b].append(arr[b])
    log.info(f"  {fpath.name}: {n} events")

for b in BRANCHES:
    data_arrays[b] = np.concatenate(data_arrays[b])

n_data_total = len(data_arrays["Thrust"])
log.info(f"Total data events: {n_data_total:,} in {time.time()-t0:.1f}s")

# ============================================================
# Load all MC (reco + gen + genBefore)
# ============================================================
t0 = time.time()
log.info("Loading all MC files...")

mc_reco_thrust = []
mc_gen_thrust = []
mc_genB_thrust = []
mc_reco_counts = []
mc_gen_counts = []
mc_genB_counts = []

for fpath in MC_FILES:
    with uproot.open(fpath) as f:
        t_arr = f["t"].arrays(["Thrust"], library="np")
        tg_arr = f["tgen"].arrays(["Thrust"], library="np")
        tgB_arr = f["tgenBefore"].arrays(["Thrust"], library="np")

        mc_reco_thrust.append(t_arr["Thrust"])
        mc_gen_thrust.append(tg_arr["Thrust"])
        mc_genB_thrust.append(tgB_arr["Thrust"])

        mc_reco_counts.append(len(t_arr["Thrust"]))
        mc_gen_counts.append(len(tg_arr["Thrust"]))
        mc_genB_counts.append(len(tgB_arr["Thrust"]))

mc_reco_thrust = np.concatenate(mc_reco_thrust)
mc_gen_thrust = np.concatenate(mc_gen_thrust)
mc_genB_thrust = np.concatenate(mc_genB_thrust)

n_mc_reco = len(mc_reco_thrust)
n_mc_gen = len(mc_gen_thrust)
n_mc_genB = len(mc_genB_thrust)

log.info(f"MC total: reco={n_mc_reco:,}, gen={n_mc_gen:,}, genBefore={n_mc_genB:,} in {time.time()-t0:.1f}s")

# Verify event matching across ALL files
log.info(f"reco == gen count for all files: {all(r == g for r, g in zip(mc_reco_counts, mc_gen_counts))}")

# ============================================================
# Full cutflow
# ============================================================
log.info("\nFULL CUTFLOW (all data):")
cut_names = ["passesNTupleAfterCut", "passesTotalChgEnergyMin", "passesNTrkMin",
             "passesSTheta", "passesMissP", "passesISR", "passesWW",
             "passesNeuNch", "passesLEP1TwoPC", "passesAll"]

log.info(f"  {'Cut':<30s} {'Yield':>12s} {'Eff':>8s}")
log.info(f"  {'Total':<30s} {n_data_total:>12,d} {'1.0000':>8s}")
for c in cut_names:
    s = np.sum(data_arrays[c])
    log.info(f"  {c:<30s} {s:>12,.0f} {s/n_data_total:>8.4f}")

# Sequential (cumulative) cutflow
log.info("\nCUMULATIVE CUTFLOW:")
mask = np.ones(n_data_total, dtype=bool)
log.info(f"  {'Cut':<30s} {'Remaining':>12s} {'CumEff':>8s}")
log.info(f"  {'Initial':<30s} {n_data_total:>12,d} {'1.0000':>8s}")
for c in cut_names:
    if c == "passesAll":
        continue  # passesAll is the product of the others
    mask = mask & data_arrays[c].astype(bool)
    log.info(f"  {c:<30s} {np.sum(mask):>12,d} {np.mean(mask):>8.4f}")

n_selected = np.sum(data_arrays["passesAll"])
log.info(f"\n  passesAll selected: {n_selected:,} / {n_data_total:,} = {n_selected/n_data_total:.4f}")

# ============================================================
# FIGURE 17: Full-stats tau distribution
# ============================================================
log.info("=== Figure 17: Full-stats tau distribution ===")

tau_data_all = 1.0 - data_arrays["Thrust"]
tau_mc_all = 1.0 - mc_reco_thrust

bins = np.linspace(0, 0.5, 51)
bc = 0.5 * (bins[:-1] + bins[1:])
bw = bins[1:] - bins[:-1]

h_d, _ = np.histogram(tau_data_all, bins=bins)
h_m, _ = np.histogram(tau_mc_all, bins=bins)
h_dn = h_d / (np.sum(h_d) * bw)
h_mn = h_m / (np.sum(h_m) * bw)
h_de = np.sqrt(h_d) / (np.sum(h_d) * bw)

fig, (ax1, ax2) = plt.subplots(2, 1, height_ratios=[3, 1], sharex=True,
                                gridspec_kw={"hspace": 0.05})

ax1.errorbar(bc, h_dn, yerr=h_de, fmt="k.", ms=4, label=f"ALEPH Data ({n_data_total/1e6:.2f}M)")
ax1.stairs(h_mn, bins, color="tab:blue", lw=1.5, label=f"MC reco ({n_mc_reco/1e3:.0f}k)")
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

fig.savefig(FIG_DIR / "17_thrust_tau_fullstats.pdf", bbox_inches="tight")
plt.close(fig)
log.info("  Saved: 17_thrust_tau_fullstats.pdf")

# ============================================================
# FIGURE 18: Full-stats resolution and efficiency (all MC)
# ============================================================
log.info("=== Figure 18: Full-stats resolution and efficiency ===")

tau_reco_all = 1.0 - mc_reco_thrust
tau_gen_all = 1.0 - mc_gen_thrust
tau_genB_all = 1.0 - mc_genB_thrust
delta_tau_all = tau_reco_all - tau_gen_all

fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))

# 18a: Response matrix
h2d, xe, ye = np.histogram2d(tau_reco_all, tau_gen_all,
                              bins=[np.linspace(0, 0.5, 51), np.linspace(0, 0.5, 51)])
im = axes[0].pcolormesh(ye, xe, h2d, cmap="Blues",
                        norm=matplotlib.colors.LogNorm(vmin=0.5))
axes[0].plot([0, 0.5], [0, 0.5], "r--", lw=0.8)
axes[0].set_xlabel(r"$\tau_\mathrm{gen}$")
axes[0].set_ylabel(r"$\tau_\mathrm{reco}$")
fig.colorbar(im, ax=axes[0], label="Events")

# 18b: RMS vs tau_gen
tg_bins = np.linspace(0, 0.45, 19)
bc_tg = 0.5 * (tg_bins[:-1] + tg_bins[1:])
rms_all = []
for i in range(len(tg_bins)-1):
    mask = (tau_gen_all >= tg_bins[i]) & (tau_gen_all < tg_bins[i+1])
    if np.sum(mask) > 10:
        rms_all.append(np.std(delta_tau_all[mask]))
    else:
        rms_all.append(np.nan)
axes[1].plot(bc_tg, rms_all, "bo-", ms=4)
axes[1].set_xlabel(r"$\tau_\mathrm{gen}$")
axes[1].set_ylabel(r"RMS$(\tau_\mathrm{reco} - \tau_\mathrm{gen})$")

# 18c: Efficiency
eff_bins = np.linspace(0, 0.5, 26)
bc_eff = 0.5 * (eff_bins[:-1] + eff_bins[1:])
h_tg, _ = np.histogram(tau_gen_all, bins=eff_bins)
h_tgB, _ = np.histogram(tau_genB_all, bins=eff_bins)
eff = np.divide(h_tg.astype(float), h_tgB.astype(float),
                out=np.zeros(len(h_tg), dtype=float), where=h_tgB > 0)
eff_err = np.sqrt(eff*(1-eff)/np.maximum(h_tgB, 1))
axes[2].errorbar(bc_eff, eff, yerr=eff_err, fmt="bo-", ms=4)
axes[2].set_xlabel(r"$\tau_\mathrm{gen}$")
axes[2].set_ylabel(r"Efficiency $\varepsilon$")
axes[2].set_ylim(0, 1.1)
axes[2].axhline(1.0, color="gray", ls="--", lw=0.5)

fig.tight_layout()
fig.savefig(FIG_DIR / "18_resolution_efficiency_fullstats.pdf", bbox_inches="tight")
plt.close(fig)
log.info("  Saved: 18_resolution_efficiency_fullstats.pdf")

log.info(f"  Full-stats resolution: mean={np.mean(delta_tau_all):.5f}, RMS={np.std(delta_tau_all):.5f}")
log.info(f"  Full-stats mean efficiency: {np.mean(eff[eff>0]):.4f}")

# ============================================================
# FIGURE 19: Year-by-year data stability
# ============================================================
log.info("=== Figure 19: Year-by-year stability ===")

fig, ax = plt.subplots()
bins19 = np.linspace(0, 0.5, 26)
bc19 = 0.5 * (bins19[:-1] + bins19[1:])
bw19 = bins19[1:] - bins19[:-1]

colors = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple", "tab:brown"]
offset = 0
for i, fpath in enumerate(DATA_FILES):
    n = data_counts[fpath.name]
    tau_yr = 1.0 - data_arrays["Thrust"][offset:offset+n]
    h, _ = np.histogram(tau_yr, bins=bins19)
    hn = h / (np.sum(h) * bw19)
    label = fpath.name.replace("LEP1Data", "").replace("_recons_aftercut-MERGED.root", "")
    ax.stairs(hn, bins19, color=colors[i], label=label, lw=1.2)
    offset += n

ax.set_xlabel(r"$\tau = 1 - T$")
ax.set_ylabel(r"$(1/N)\, \mathrm{d}N/\mathrm{d}\tau$")
ax.set_yscale("log")
ax.set_ylim(0.01, 100)
ax.legend(fontsize=9, ncol=2)
fig.savefig(FIG_DIR / "19_year_stability.pdf", bbox_inches="tight")
plt.close(fig)
log.info("  Saved: 19_year_stability.pdf")

# ============================================================
# Binning proposal
# ============================================================
log.info("\n=== BINNING PROPOSAL ===")
log.info(f"Resolution (RMS) ranges from ~{min(r for r in rms_all if not np.isnan(r)):.4f} to ~{max(r for r in rms_all if not np.isnan(r)):.4f}")

# Proposed binning: finer near peak, coarser in tails
# Based on resolution ~0.005-0.02 and statistics
proposed_bins = np.array([
    0.00, 0.01, 0.02, 0.03, 0.04, 0.05,
    0.06, 0.07, 0.08, 0.09, 0.10,
    0.12, 0.14, 0.16, 0.18, 0.20,
    0.23, 0.26, 0.30, 0.35, 0.40, 0.50
])
log.info(f"Proposed binning ({len(proposed_bins)-1} bins): {proposed_bins}")

# Check bin populations
h_prop, _ = np.histogram(tau_data_all, bins=proposed_bins)
log.info("Bin populations:")
for i in range(len(proposed_bins)-1):
    log.info(f"  [{proposed_bins[i]:.2f}, {proposed_bins[i+1]:.2f}): {h_prop[i]:>8,d} events, width={proposed_bins[i+1]-proposed_bins[i]:.2f}")

# Published ALEPH binning (from hep-ex/0406111 Table 9)
aleph_bins = np.array([
    0.00, 0.01, 0.02, 0.03, 0.04, 0.05,
    0.06, 0.07, 0.08, 0.09, 0.10,
    0.12, 0.14, 0.16, 0.20, 0.25,
    0.30, 0.35, 0.40, 0.50
])
log.info(f"\nPublished ALEPH binning ({len(aleph_bins)-1} bins): {aleph_bins}")

h_aleph, _ = np.histogram(tau_data_all, bins=aleph_bins)
log.info("Bin populations with ALEPH binning:")
for i in range(len(aleph_bins)-1):
    log.info(f"  [{aleph_bins[i]:.2f}, {aleph_bins[i+1]:.2f}): {h_aleph[i]:>8,d} events")

# ============================================================
# Data/MC event count summary
# ============================================================
log.info("\n=== EVENT COUNT SUMMARY ===")
log.info(f"Data files: {len(DATA_FILES)}")
for name, count in data_counts.items():
    log.info(f"  {name}: {count:,}")
log.info(f"  TOTAL: {n_data_total:,}")

log.info(f"\nMC files: {len(MC_FILES)}")
log.info(f"  Total reco (t): {n_mc_reco:,}")
log.info(f"  Total gen matched (tgen): {n_mc_gen:,}")
log.info(f"  Total gen before (tgenBefore): {n_mc_genB:,}")
log.info(f"  Data/MC ratio: {n_data_total/n_mc_reco:.1f}")

log.info("\nDone.")
