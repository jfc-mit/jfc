"""
Phase 3 Script 2: build_response.py

Build the response matrix from the full MC sample (all 40 files).

The response matrix R[i,j] = P(reco bin i | gen bin j) is constructed
as a 2D histogram of (tau_reco, tau_gen) for matched events passing
the full event selection (passesAll).

Outputs (in phase3_selection/exec/):
  - response_matrix.npz: the normalized response matrix and supporting arrays
  - bbb_corrections.npz: bin-by-bin correction factors C(tau) = MC_gen / MC_reco

Also reports:
  - Matrix dimensions and bin edges
  - Diagonal fraction per bin
  - Column normalization (should sum to 1)
  - Efficiency vs tau_gen (fraction of gen events that are reconstructed)
  - Condition number (for reference)
"""

import logging
from pathlib import Path

import numpy as np
import uproot
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplhep as mh
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
log = logging.getLogger("build_response")
console = Console()

# ---------------------------------------------------------------------------
# Paths and binning
# ---------------------------------------------------------------------------
MC_DIR  = Path("/n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ALEPHMC")
OUT_DIR = Path("phase3_selection/exec")
OUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR = Path("phase3_selection/figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

MC_FILES = sorted(MC_DIR.glob("LEP1MC1994_recons_aftercut-[0-9][0-9][0-9].root"))

# Binning: 25 uniform bins in tau [0, 0.5]
N_BINS    = 25
TAU_MIN   = 0.0
TAU_MAX   = 0.5
TAU_EDGES   = np.linspace(TAU_MIN, TAU_MAX, N_BINS + 1)
TAU_CENTERS = 0.5 * (TAU_EDGES[:-1] + TAU_EDGES[1:])
BIN_WIDTH   = TAU_EDGES[1] - TAU_EDGES[0]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    log.info("=" * 70)
    log.info("Phase 3 Script 2: Build Response Matrix")
    log.info("=" * 70)
    log.info(f"MC files: {len(MC_FILES)}")
    log.info(f"Binning: {N_BINS} bins, tau in [{TAU_MIN}, {TAU_MAX}]")

    # -----------------------------------------------------------------------
    # Accumulate 2D histogram (tau_reco x tau_gen) over all MC files
    # -----------------------------------------------------------------------
    # H2[i_reco, j_gen] = number of events with reco in bin i and gen in bin j
    H2 = np.zeros((N_BINS, N_BINS), dtype=np.float64)
    # 1D gen histogram (for events that have RECO counterparts, i.e., are selected)
    h_gen_sel = np.zeros(N_BINS, dtype=np.float64)
    # 1D genbefore histogram (all gen events, for efficiency denominator)
    h_gen_before = np.zeros(N_BINS, dtype=np.float64)
    # 1D reco histogram (for bin-by-bin correction factors)
    h_reco_sel = np.zeros(N_BINS, dtype=np.float64)

    n_files_processed = 0
    for path in MC_FILES:
        log.info(f"  {path.name}")
        with uproot.open(str(path)) as f:
            # Reco tree
            reco = f["t"].arrays(["Thrust", "passesAll"], library="np")
            # Gen tree (matched 1:1 to reco)
            gen  = f["tgen"].arrays(["Thrust", "passesAll"], library="np")
            # tgenBefore (all gen events, before detector selection)
            genbefore = f["tgenBefore"].arrays(["Thrust"], library="np")

        sel = reco["passesAll"].astype(bool)
        tau_reco = 1.0 - reco["Thrust"][sel]
        tau_gen  = 1.0 - gen["Thrust"][sel]
        tau_gb   = 1.0 - genbefore["Thrust"]

        # 2D histogram
        h2, _, _ = np.histogram2d(
            tau_reco, tau_gen,
            bins=[TAU_EDGES, TAU_EDGES],
        )
        H2 += h2

        # 1D histograms
        hg, _ = np.histogram(tau_gen,  bins=TAU_EDGES)
        hr, _ = np.histogram(tau_reco, bins=TAU_EDGES)
        hgb, _ = np.histogram(tau_gb,  bins=TAU_EDGES)
        h_gen_sel   += hg
        h_reco_sel  += hr
        h_gen_before += hgb

        n_files_processed += 1

    log.info(f"\nProcessed {n_files_processed} MC files")
    log.info(f"Total matched (reco, gen) pairs in response matrix: {H2.sum():.0f}")
    log.info(f"Total tgenBefore events: {h_gen_before.sum():.0f}")

    # -----------------------------------------------------------------------
    # Normalize response matrix: R[i,j] = P(reco bin i | gen bin j)
    # Column sums = 1 for bins with any content.
    # -----------------------------------------------------------------------
    # col_sums[j] = sum_i H2[i,j] = number of gen-bin-j events that are reconstructed
    col_sums = H2.sum(axis=0)  # shape (N_BINS,)
    # Avoid division by zero
    safe_col = np.where(col_sums > 0, col_sums, 1.0)
    R = H2 / safe_col[np.newaxis, :]   # R[i,j] = H2[i,j] / col_sums[j]

    # Efficiency: fraction of all gen events (tgenBefore) that end up in reco
    efficiency = np.where(h_gen_before > 0, col_sums / h_gen_before, 0.0)

    # Diagonal fraction per bin
    diagonal_frac = np.where(col_sums > 0, np.diag(H2) / col_sums, 0.0)

    # Column normalization check
    col_norm = R.sum(axis=0)  # should be 1 where col_sums > 0

    # Bin-by-bin correction factors C(tau) = h_gen_sel / h_reco_sel
    # (applied as C * reco to get approximate gen)
    bbb_C = np.where(h_reco_sel > 0, h_gen_sel / h_reco_sel, 1.0)

    # -----------------------------------------------------------------------
    # Save
    # -----------------------------------------------------------------------
    np.savez(
        OUT_DIR / "response_matrix.npz",
        R=R,
        H2=H2,
        edges=TAU_EDGES,
        centers=TAU_CENTERS,
        col_sums=col_sums,
        efficiency=efficiency,
        diagonal_frac=diagonal_frac,
        h_gen_sel=h_gen_sel,
        h_reco_sel=h_reco_sel,
        h_gen_before=h_gen_before,
    )
    log.info("Saved response_matrix.npz")

    np.savez(
        OUT_DIR / "bbb_corrections.npz",
        C=bbb_C,
        h_gen_sel=h_gen_sel,
        h_reco_sel=h_reco_sel,
        edges=TAU_EDGES,
        centers=TAU_CENTERS,
    )
    log.info("Saved bbb_corrections.npz")

    # -----------------------------------------------------------------------
    # Report matrix properties
    # -----------------------------------------------------------------------
    table = Table(title="Response Matrix Properties", show_header=True)
    table.add_column("tau bin center", justify="right")
    table.add_column("H2 col sum",    justify="right")
    table.add_column("Diag frac",     justify="right")
    table.add_column("Col norm",      justify="right")
    table.add_column("Efficiency",    justify="right")
    table.add_column("BBB corr C",    justify="right")

    for j in range(N_BINS):
        table.add_row(
            f"{TAU_CENTERS[j]:.3f}",
            f"{col_sums[j]:.0f}",
            f"{diagonal_frac[j]:.3f}",
            f"{col_norm[j]:.4f}",
            f"{efficiency[j]:.3f}",
            f"{bbb_C[j]:.3f}",
        )
    console.print(table)

    # Condition number (for informational purposes; not used in IBU directly)
    # Use only populated rows/cols
    active = col_sums > 0
    if active.sum() > 1:
        R_sub = R[np.ix_(active, active)]
        cond = np.linalg.cond(R_sub)
        log.info(f"\nCondition number of R (active sub-matrix): {cond:.2e}")
    else:
        log.warning("Too few populated bins to compute condition number")

    log.info(f"Column normalization: min={col_norm[active].min():.4f}, "
             f"max={col_norm[active].max():.4f} (should be ~1.0 for active bins)")
    log.info(f"Diagonal fraction: min={diagonal_frac[active].min():.3f}, "
             f"max={diagonal_frac[active].max():.3f}")
    log.info(f"Efficiency (reco/genbefore): min={efficiency[active].min():.3f}, "
             f"max={efficiency[active].max():.3f}")

    # -----------------------------------------------------------------------
    # Figures
    # -----------------------------------------------------------------------
    mh.style.use("CMS")

    # 1. Response matrix as 2D colormap
    fig, ax = plt.subplots(figsize=(9, 8))
    im = ax.imshow(
        R.T,          # transpose so x=reco, y=gen visually
        origin="lower",
        aspect="auto",
        extent=[TAU_MIN, TAU_MAX, TAU_MIN, TAU_MAX],
        vmin=0, vmax=R.max(),
        cmap="Blues",
    )
    plt.colorbar(im, ax=ax, label=r"$P(\mathrm{reco\;bin}\,i\,|\,\mathrm{gen\;bin}\,j)$")
    ax.set_xlabel(r"$\tau_\mathrm{reco}$", fontsize=14)
    ax.set_ylabel(r"$\tau_\mathrm{gen}$", fontsize=14)
    mh.label.exp_label(exp="ALEPH", data=False, rlabel=r"Pythia 6.1 MC", ax=ax)
    fig.savefig(FIG_DIR / "response_matrix.pdf", bbox_inches="tight", dpi=200, transparent=True)
    fig.savefig(FIG_DIR / "response_matrix.png", bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)
    log.info("Saved response_matrix figure")

    # 2. Diagonal fraction vs tau_gen
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    ax2.step(TAU_EDGES[:-1], diagonal_frac, where="post", color="black", linewidth=1.5,
             label="Diagonal fraction")
    ax2.axhline(0.5, color="red", linestyle="--", linewidth=1.0, label="50% reference")
    ax2.axvline(0.05, color="gray", linestyle=":", linewidth=1.0, label="Fit range lower bound")
    ax2.axvline(0.30, color="gray", linestyle=":",  linewidth=1.0, label="Fit range upper bound")
    ax2.set_xlabel(r"$\tau_\mathrm{gen}$", fontsize=14)
    ax2.set_ylabel("Diagonal fraction", fontsize=14)
    ax2.set_xlim(TAU_MIN, TAU_MAX)
    ax2.set_ylim(0, 1)
    ax2.legend(fontsize="x-small")
    mh.label.exp_label(exp="ALEPH", data=False, rlabel=r"Pythia 6.1 MC", ax=ax2)
    fig2.savefig(FIG_DIR / "response_diagonal_frac.pdf", bbox_inches="tight", dpi=200, transparent=True)
    fig2.savefig(FIG_DIR / "response_diagonal_frac.png", bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig2)
    log.info("Saved response_diagonal_frac figure")

    # 3. Efficiency vs tau_gen
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    ax3.step(TAU_EDGES[:-1], efficiency, where="post", color="black", linewidth=1.5)
    ax3.set_xlabel(r"$\tau_\mathrm{gen}$", fontsize=14)
    ax3.set_ylabel(r"Reconstruction efficiency $\varepsilon(\tau_\mathrm{gen})$", fontsize=14)
    ax3.set_xlim(TAU_MIN, TAU_MAX)
    ax3.set_ylim(0, 1)
    mh.label.exp_label(exp="ALEPH", data=False, rlabel=r"Pythia 6.1 MC", ax=ax3)
    fig3.savefig(FIG_DIR / "response_efficiency.pdf", bbox_inches="tight", dpi=200, transparent=True)
    fig3.savefig(FIG_DIR / "response_efficiency.png", bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig3)
    log.info("Saved response_efficiency figure")

    # 4. Bin-by-bin correction factors
    fig4, ax4 = plt.subplots(figsize=(10, 6))
    ax4.step(TAU_EDGES[:-1], bbb_C, where="post", color="black", linewidth=1.5)
    ax4.axhline(1.0, color="gray", linewidth=1.0, linestyle="--")
    ax4.set_xlabel(r"$\tau$", fontsize=14)
    ax4.set_ylabel(r"Bin-by-bin correction $C(\tau)$", fontsize=14)
    ax4.set_xlim(TAU_MIN, TAU_MAX)
    mh.label.exp_label(exp="ALEPH", data=False, rlabel=r"Pythia 6.1 MC", ax=ax4)
    fig4.savefig(FIG_DIR / "bbb_corrections.pdf", bbox_inches="tight", dpi=200, transparent=True)
    fig4.savefig(FIG_DIR / "bbb_corrections.png", bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig4)
    log.info("Saved bbb_corrections figure")

    log.info("\n[bold green]build_response.py complete[/bold green]")
    log.info(f"Outputs in {OUT_DIR}/")


if __name__ == "__main__":
    main()
