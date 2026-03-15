"""
Phase 3 Script 1: apply_selection.py

Apply the full hadronic event selection to all data and MC files.
Produce cutflow table and save selected events to NPZ files for downstream use.

Selection applied:
  - passesAll (= passesNTupleAfterCut & passesTotalChgEnergyMin & passesNTrkMin
               & passesSTheta & passesMissP & passesISR)
  Note: the first three flags are pre-applied in the files (100% pass),
        but we apply passesAll to also enforce STheta, MissP, and ISR cuts.

Output files (in phase3_selection/exec/):
  - selected_data.npz: tau, year per event for selected data
  - selected_mc_reco.npz: tau per selected MC reco event
  - selected_mc_gen.npz:  tau (generator level) for matched reco events
  - selected_mc_genbefore.npz: tau (generator level, all events before selection)
  - cutflow_data.npz, cutflow_mc.npz: per-cut yield tables
  - hist_tau_data.npz: summed tau histogram over all data years
  - hist_tau_mc_reco.npz, hist_tau_mc_gen.npz: tau histograms from full MC

Scale approach: process files one at a time, accumulate histograms and
  selected-event arrays. Total MC is ~33 GB; DO NOT load all at once.
"""

import logging
import os
import sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np
import uproot
import awkward as ak
from rich.logging import RichHandler
from rich.console import Console
from rich.table import Table

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger("apply_selection")
console = Console()

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DATA_DIR = Path("/n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ALEPH")
MC_DIR   = Path("/n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ALEPHMC")
OUT_DIR  = Path("phase3_selection/exec")
OUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR  = Path("phase3_selection/figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Data file list (year label, filename)
DATA_FILES = [
    (1992, DATA_DIR / "LEP1Data1992_recons_aftercut-MERGED.root"),
    (1993, DATA_DIR / "LEP1Data1993_recons_aftercut-MERGED.root"),
    (1994, DATA_DIR / "LEP1Data1994P1_recons_aftercut-MERGED.root"),
    (1994, DATA_DIR / "LEP1Data1994P2_recons_aftercut-MERGED.root"),
    (1994, DATA_DIR / "LEP1Data1994P3_recons_aftercut-MERGED.root"),
    (1995, DATA_DIR / "LEP1Data1995_recons_aftercut-MERGED.root"),
]

MC_FILES = sorted(MC_DIR.glob("LEP1MC1994_recons_aftercut-[0-9][0-9][0-9].root"))

# Observable binning: 25 uniform bins in tau [0, 0.5]
N_BINS   = 25
TAU_MIN  = 0.0
TAU_MAX  = 0.5
TAU_EDGES = np.linspace(TAU_MIN, TAU_MAX, N_BINS + 1)
TAU_CENTERS = 0.5 * (TAU_EDGES[:-1] + TAU_EDGES[1:])

# Selection flag names for cutflow
CUT_FLAGS = [
    "passesNTupleAfterCut",
    "passesTotalChgEnergyMin",
    "passesNTrkMin",
    "passesSTheta",
    "passesMissP",
    "passesISR",
]

# ---------------------------------------------------------------------------
# Helper: read one file and compute cutflow + tau arrays
# ---------------------------------------------------------------------------

def process_data_file(year: int, path: Path) -> dict:
    """Read one data file; return cutflow and selected tau, year arrays."""
    log.info(f"  Processing data: {path.name}")
    branches = CUT_FLAGS + ["Thrust", "passesAll"]
    with uproot.open(str(path)) as f:
        tree = f["t"]
        arrays = tree.arrays(branches, library="np")

    n_total = len(arrays["Thrust"])
    tau_all = 1.0 - arrays["Thrust"]

    # Build per-cut yields (cumulative)
    cutflow = {"total": n_total}
    mask = np.ones(n_total, dtype=bool)
    for flag in CUT_FLAGS:
        mask = mask & arrays[flag].astype(bool)
        cutflow[flag] = int(np.sum(mask))

    # Final mask = passesAll (should match cumulative above)
    final_mask = arrays["passesAll"].astype(bool)
    tau_sel = tau_all[final_mask]
    year_sel = np.full(len(tau_sel), year, dtype=np.int32)

    return {
        "cutflow": cutflow,
        "tau": tau_sel,
        "year": year_sel,
    }


def process_mc_file(path: Path) -> dict:
    """Read one MC file; return cutflow, reco tau, gen tau arrays."""
    log.info(f"  Processing MC: {path.name}")
    reco_branches = CUT_FLAGS + ["Thrust", "passesAll"]
    gen_branches  = ["Thrust", "passesAll"]

    with uproot.open(str(path)) as f:
        # Reco tree
        t_reco = f["t"]
        reco   = t_reco.arrays(reco_branches, library="np")
        n_reco = len(reco["Thrust"])

        # Generator-matched tree (same events as reco, same length)
        t_gen = f["tgen"]
        gen   = t_gen.arrays(gen_branches, library="np")

        # tgenBefore: all generated events (different length)
        t_genbefore = f["tgenBefore"]
        genbefore   = t_genbefore.arrays(["Thrust"], library="np")

    tau_reco_all = 1.0 - reco["Thrust"]
    tau_gen_all  = 1.0 - gen["Thrust"]
    tau_genbefore_all = 1.0 - genbefore["Thrust"]

    # Cutflow (reco)
    cutflow = {"total": n_reco}
    mask = np.ones(n_reco, dtype=bool)
    for flag in CUT_FLAGS:
        mask = mask & reco[flag].astype(bool)
        cutflow[flag] = int(np.sum(mask))

    # Apply passesAll to both reco and matched gen
    sel = reco["passesAll"].astype(bool)
    tau_reco_sel = tau_reco_all[sel]
    tau_gen_sel  = tau_gen_all[sel]

    # tgenBefore: no selection applied — this is the full particle-level sample
    # (used for efficiency calculation; the detector selection efficiency is
    #  the ratio of tgen[passesAll] to tgenBefore)
    tau_genbefore_sel = tau_genbefore_all

    return {
        "cutflow": cutflow,
        "tau_reco": tau_reco_sel,
        "tau_gen":  tau_gen_sel,
        "tau_genbefore": tau_genbefore_sel,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    log.info("=" * 70)
    log.info("Phase 3 Script 1: Apply Selection")
    log.info("=" * 70)

    # ------------------------------------------------------------------
    # Process DATA files
    # ------------------------------------------------------------------
    log.info("\n[bold]Processing DATA files[/bold]")
    all_tau_data  = []
    all_year_data = []
    # Per-file cutflow for data: list of dicts
    data_cutflows = []

    for year, path in DATA_FILES:
        result = process_data_file(year, path)
        all_tau_data.append(result["tau"])
        all_year_data.append(result["year"])
        data_cutflows.append({"file": path.name, "year": year, **result["cutflow"]})

    tau_data_all  = np.concatenate(all_tau_data)
    year_data_all = np.concatenate(all_year_data)
    log.info(f"\nTotal selected data events: {len(tau_data_all):,}")

    # Save selected data arrays
    np.savez(
        OUT_DIR / "selected_data.npz",
        tau=tau_data_all,
        year=year_data_all,
    )
    log.info(f"Saved selected_data.npz")

    # Data tau histogram (summed over all years)
    hist_tau_data, _ = np.histogram(tau_data_all, bins=TAU_EDGES)
    np.savez(
        OUT_DIR / "hist_tau_data.npz",
        counts=hist_tau_data,
        edges=TAU_EDGES,
        centers=TAU_CENTERS,
    )

    # ------------------------------------------------------------------
    # Process MC files
    # ------------------------------------------------------------------
    log.info("\n[bold]Processing MC files[/bold]")
    all_tau_reco     = []
    all_tau_gen      = []
    all_tau_genbefore = []
    mc_cutflows = []

    for path in MC_FILES:
        result = process_mc_file(path)
        all_tau_reco.append(result["tau_reco"])
        all_tau_gen.append(result["tau_gen"])
        all_tau_genbefore.append(result["tau_genbefore"])
        mc_cutflows.append({"file": path.name, **result["cutflow"]})

    tau_reco_all      = np.concatenate(all_tau_reco)
    tau_gen_all       = np.concatenate(all_tau_gen)
    tau_genbefore_all = np.concatenate(all_tau_genbefore)

    log.info(f"\nTotal selected MC reco events:       {len(tau_reco_all):,}")
    log.info(f"Total matched MC gen events:         {len(tau_gen_all):,}")
    log.info(f"Total tgenBefore events:             {len(tau_genbefore_all):,}")

    # Save MC arrays
    np.savez(OUT_DIR / "selected_mc_reco.npz", tau=tau_reco_all)
    np.savez(OUT_DIR / "selected_mc_gen.npz",  tau=tau_gen_all)
    np.savez(OUT_DIR / "selected_mc_genbefore.npz", tau=tau_genbefore_all)
    log.info("Saved MC NPZ files")

    # MC histograms
    hist_tau_mc_reco, _ = np.histogram(tau_reco_all, bins=TAU_EDGES)
    hist_tau_mc_gen,  _ = np.histogram(tau_gen_all,  bins=TAU_EDGES)
    hist_tau_mc_genbefore, _ = np.histogram(tau_genbefore_all, bins=TAU_EDGES)
    np.savez(
        OUT_DIR / "hist_tau_mc_reco.npz",
        counts=hist_tau_mc_reco,
        edges=TAU_EDGES,
        centers=TAU_CENTERS,
    )
    np.savez(
        OUT_DIR / "hist_tau_mc_gen.npz",
        counts=hist_tau_mc_gen,
        edges=TAU_EDGES,
        centers=TAU_CENTERS,
    )
    np.savez(
        OUT_DIR / "hist_tau_mc_genbefore.npz",
        counts=hist_tau_mc_genbefore,
        edges=TAU_EDGES,
        centers=TAU_CENTERS,
    )

    # ------------------------------------------------------------------
    # Cutflow tables
    # ------------------------------------------------------------------
    log.info("\n[bold]Computing aggregate cutflow tables[/bold]")

    # Data cutflow: sum over all files
    data_total = sum(cf["total"] for cf in data_cutflows)
    data_per_cut = {}
    for flag in CUT_FLAGS:
        data_per_cut[flag] = sum(cf.get(flag, 0) for cf in data_cutflows)
    data_selected = len(tau_data_all)

    # MC cutflow: sum over all files
    mc_total = sum(cf["total"] for cf in mc_cutflows)
    mc_per_cut = {}
    for flag in CUT_FLAGS:
        mc_per_cut[flag] = sum(cf.get(flag, 0) for cf in mc_cutflows)
    mc_selected = len(tau_reco_all)

    # Save cutflow arrays
    np.savez(
        OUT_DIR / "cutflow_data.npz",
        total=data_total,
        flags=CUT_FLAGS,
        yields=np.array([data_per_cut[f] for f in CUT_FLAGS], dtype=np.int64),
    )
    np.savez(
        OUT_DIR / "cutflow_mc.npz",
        total=mc_total,
        flags=CUT_FLAGS,
        yields=np.array([mc_per_cut[f] for f in CUT_FLAGS], dtype=np.int64),
    )

    # Print cutflow table to console
    table = Table(title="Cutflow Table", show_header=True)
    table.add_column("Cut", style="cyan")
    table.add_column("Data Events", justify="right")
    table.add_column("Data Eff.", justify="right")
    table.add_column("MC Events", justify="right")
    table.add_column("MC Eff.", justify="right")

    prev_data = data_total
    prev_mc   = mc_total
    table.add_row(
        "Total (aftercut)",
        f"{data_total:,}",
        "100.0%",
        f"{mc_total:,}",
        "100.0%",
    )
    label_map = {
        "passesNTupleAfterCut":    "NTuple aftercut (pre-applied)",
        "passesTotalChgEnergyMin": "E_ch > 15 GeV (pre-applied)",
        "passesNTrkMin":           "N_trk >= 5 (pre-applied)",
        "passesSTheta":            "|cos(theta_sph)| < 0.82",
        "passesMissP":             "missP < 20 GeV",
        "passesISR":               "No hard ISR",
    }
    for flag in CUT_FLAGS:
        d_n = data_per_cut[flag]
        m_n = mc_per_cut[flag]
        d_eff = 100.0 * d_n / data_total if data_total > 0 else 0.0
        m_eff = 100.0 * m_n / mc_total   if mc_total   > 0 else 0.0
        table.add_row(
            label_map.get(flag, flag),
            f"{d_n:,}",
            f"{d_eff:.1f}%",
            f"{m_n:,}",
            f"{m_eff:.1f}%",
        )
    console.print(table)

    log.info(f"\nFinal selected: data={data_selected:,} ({100.*data_selected/data_total:.1f}%), "
             f"MC reco={mc_selected:,} ({100.*mc_selected/mc_total:.1f}%)")

    # ------------------------------------------------------------------
    # Basic tau distribution plots (data and MC reco overlaid)
    # ------------------------------------------------------------------
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import mplhep as mh
    mh.style.use("CMS")

    # Normalize histograms for shape comparison
    bin_width = TAU_EDGES[1] - TAU_EDGES[0]

    norm_data = hist_tau_data / (hist_tau_data.sum() * bin_width)
    norm_mc   = hist_tau_mc_reco / (hist_tau_mc_reco.sum() * bin_width)

    # Compute statistical uncertainties
    data_unc = np.sqrt(hist_tau_data) / (hist_tau_data.sum() * bin_width)
    mc_unc   = np.sqrt(hist_tau_mc_reco) / (hist_tau_mc_reco.sum() * bin_width)

    # Ratio: data / MC
    ratio = np.where(norm_mc > 0, norm_data / norm_mc, np.nan)
    ratio_unc = np.where(
        norm_mc > 0,
        np.sqrt((data_unc / norm_mc)**2 + (norm_data * mc_unc / norm_mc**2)**2),
        np.nan,
    )

    fig, (ax, rax) = plt.subplots(
        2, 1, figsize=(10, 10),
        gridspec_kw={"height_ratios": [3, 1]},
        sharex=True,
    )
    fig.subplots_adjust(hspace=0.0)

    ax.stairs(norm_data, TAU_EDGES, color="black", linewidth=1.5, label="Data 1992–1995")
    ax.stairs(norm_mc,   TAU_EDGES, color="tab:red", linewidth=1.5, linestyle="--",
              label="MC Pythia 6.1 (reco)")
    ax.set_ylabel(r"$(1/N)\,dN/d\tau$", fontsize=14)
    ax.set_yscale("log")
    ax.legend(fontsize="x-small")
    mh.label.exp_label(exp="ALEPH", data=True, rlabel=r"$\sqrt{s} = 91.2$ GeV", ax=ax)

    rax.axhline(1.0, color="gray", linewidth=1.0)
    rax.stairs(ratio, TAU_EDGES, color="black", linewidth=1.5)
    rax.errorbar(
        TAU_CENTERS, ratio,
        yerr=ratio_unc,
        fmt="none", color="black", capsize=2,
    )
    rax.set_xlabel(r"$\tau = 1 - T$", fontsize=14)
    rax.set_ylabel("Data / MC", fontsize=12)
    rax.set_ylim(0.7, 1.3)
    rax.set_xlim(TAU_MIN, TAU_MAX)

    fig.savefig(FIG_DIR / "tau_data_mc_phase3.pdf", bbox_inches="tight", dpi=200, transparent=True)
    fig.savefig(FIG_DIR / "tau_data_mc_phase3.png", bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)
    log.info("Saved tau_data_mc_phase3 figure")

    # Year-by-year cutflow plot (bar chart of per-year selected events)
    year_labels = ["1992", "1993", "1994 P1", "1994 P2", "1994 P3", "1995"]
    per_year_total    = [cf["total"] for cf in data_cutflows]
    per_year_selected = [int(cf[CUT_FLAGS[-1]]) for cf in data_cutflows]
    per_year_eff      = [s / t * 100 for s, t in zip(per_year_selected, per_year_total)]

    fig2, ax2 = plt.subplots(figsize=(10, 6))
    x = np.arange(len(year_labels))
    ax2.bar(x - 0.2, per_year_total,    0.35, label="Aftercut total",  color="steelblue", alpha=0.8)
    ax2.bar(x + 0.2, per_year_selected, 0.35, label="After passesAll", color="darkorange", alpha=0.8)
    ax2.set_xticks(x)
    ax2.set_xticklabels(year_labels)
    ax2.set_ylabel("Events", fontsize=14)
    ax2.legend(fontsize="x-small")
    for i, (eff, sel) in enumerate(zip(per_year_eff, per_year_selected)):
        ax2.text(i + 0.2, sel + 2000, f"{eff:.1f}%", ha="center", fontsize=9)
    mh.label.exp_label(exp="ALEPH", data=True, rlabel=r"$\sqrt{s} = 91.2$ GeV", ax=ax2)
    fig2.savefig(FIG_DIR / "cutflow_by_year.pdf", bbox_inches="tight", dpi=200, transparent=True)
    fig2.savefig(FIG_DIR / "cutflow_by_year.png", bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig2)
    log.info("Saved cutflow_by_year figure")

    log.info("\n[bold green]apply_selection.py complete[/bold green]")
    log.info(f"Outputs in {OUT_DIR}/")


if __name__ == "__main__":
    main()
