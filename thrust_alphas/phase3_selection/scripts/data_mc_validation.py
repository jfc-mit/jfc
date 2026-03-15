"""
Phase 3 Script 4: data_mc_validation.py

Produce data/MC comparison plots for ALL kinematic variables entering
the thrust calculation, resolved by reconstructed object category.

Required by conventions/unfolding.md (Section: Response matrix construction,
Input validation). These plots are evidence that the MC response model is
adequate. They are required — not optional.

Categories:
  - Charged tracks (pwflag = 0): primary charged tracks used in thrust
  - Neutral objects (pwflag = 4): calorimeter clusters

Variables per category:
  - Track/cluster multiplicity per event
  - Momentum magnitude |p|
  - Polar angle cos(theta)
  - Transverse momentum p_T  (charged only)
  - Impact parameters d0, z0  (charged only)
  - TPC hit count ntpc         (charged only)
  - Cluster energy E = |p|     (neutral objects, same |p| array)

Event-level variables:
  - Total charged energy sum
  - Total neutral energy sum
  - Total visible energy
  - Number of charged + neutral particles
  - Missing momentum magnitude

All plots use ratio panels. Data = all 6 years combined (passesAll).
MC = all 40 files combined (passesAll).

Scale: process file-by-file to avoid memory overflow.
"""

import logging
from pathlib import Path
from typing import Optional

import numpy as np
import awkward as ak
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
log = logging.getLogger("data_mc_validation")
console = Console()

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DATA_DIR = Path("/n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ALEPH")
MC_DIR   = Path("/n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ALEPHMC")
FIG_DIR  = Path("phase3_selection/figures")
OUT_DIR  = Path("phase3_selection/exec")
FIG_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

DATA_FILES = [
    DATA_DIR / "LEP1Data1992_recons_aftercut-MERGED.root",
    DATA_DIR / "LEP1Data1993_recons_aftercut-MERGED.root",
    DATA_DIR / "LEP1Data1994P1_recons_aftercut-MERGED.root",
    DATA_DIR / "LEP1Data1994P2_recons_aftercut-MERGED.root",
    DATA_DIR / "LEP1Data1994P3_recons_aftercut-MERGED.root",
    DATA_DIR / "LEP1Data1995_recons_aftercut-MERGED.root",
]
MC_FILES = sorted(MC_DIR.glob("LEP1MC1994_recons_aftercut-[0-9][0-9][0-9].root"))

# Branches we need for kinematic validation
KINEMATIC_BRANCHES = [
    "passesAll",
    "nParticle", "nChargedHadrons",
    "missP",
    # Per-particle arrays
    "px", "py", "pz", "pmag", "pt", "theta", "phi",
    "charge", "pwflag",
    "d0", "z0", "ntpc",
]


# ---------------------------------------------------------------------------
# Histogram accumulator helper
# ---------------------------------------------------------------------------

class HistAccum:
    """Accumulate a 1-D histogram across many files."""

    def __init__(self, edges: np.ndarray):
        self.edges  = edges
        self.counts = np.zeros(len(edges) - 1, dtype=np.float64)

    def fill(self, values: np.ndarray, weights: Optional[np.ndarray] = None):
        h, _ = np.histogram(values, bins=self.edges, weights=weights)
        self.counts += h

    @property
    def centers(self):
        return 0.5 * (self.edges[:-1] + self.edges[1:])


# ---------------------------------------------------------------------------
# Define histogram binning for each variable
# ---------------------------------------------------------------------------

HIST_DEFS = {
    # --- Multiplicity ---
    "n_charged_per_event": {
        "edges": np.arange(0, 55, 1),
        "xlabel": r"Charged tracks per event ($N_\mathrm{ch}$)",
        "yscale": "linear",
    },
    "n_neutral_per_event": {
        "edges": np.arange(0, 40, 1),
        "xlabel": r"Neutral clusters per event ($N_\mathrm{neu}$)",
        "yscale": "linear",
    },
    # --- Charged track variables ---
    "chg_pmag": {
        "edges": np.concatenate([np.linspace(0, 2, 21), np.linspace(2, 10, 17), np.linspace(10, 50, 9)]),
        "xlabel": r"Charged track $|p|$ (GeV)",
        "yscale": "log",
    },
    "chg_pt": {
        "edges": np.concatenate([np.linspace(0, 2, 21), np.linspace(2, 10, 17)]),
        "xlabel": r"Charged track $p_T$ (GeV)",
        "yscale": "log",
    },
    "chg_costheta": {
        "edges": np.linspace(-1, 1, 41),
        "xlabel": r"Charged track $\cos\theta$",
        "yscale": "linear",
    },
    "chg_d0": {
        "edges": np.linspace(-2.5, 2.5, 51),
        "xlabel": r"Charged track $d_0$ (cm)",
        "yscale": "log",
    },
    "chg_z0": {
        "edges": np.linspace(-12, 12, 61),
        "xlabel": r"Charged track $z_0$ (cm)",
        "yscale": "log",
    },
    "chg_ntpc": {
        "edges": np.arange(0, 40, 1),
        "xlabel": r"Charged track TPC hit count ($n_\mathrm{TPC}$)",
        "yscale": "linear",
    },
    # --- Neutral cluster variables ---
    "neu_pmag": {
        "edges": np.concatenate([np.linspace(0, 5, 26), np.linspace(5, 30, 13)]),
        "xlabel": r"Neutral cluster $|p|$ (GeV)",
        "yscale": "log",
    },
    "neu_costheta": {
        "edges": np.linspace(-1, 1, 41),
        "xlabel": r"Neutral cluster $\cos\theta$",
        "yscale": "linear",
    },
    # --- Event-level ---
    "e_charged": {
        "edges": np.linspace(0, 100, 51),
        "xlabel": r"$\sum |p|_\mathrm{ch}$ (GeV)",
        "yscale": "linear",
    },
    "e_neutral": {
        "edges": np.linspace(0, 60, 31),
        "xlabel": r"$\sum |p|_\mathrm{neu}$ (GeV)",
        "yscale": "linear",
    },
    "e_total": {
        "edges": np.linspace(0, 120, 61),
        "xlabel": r"$E_\mathrm{vis} = \sum |p|_\mathrm{all}$ (GeV)",
        "yscale": "linear",
    },
    "missp": {
        "edges": np.linspace(0, 25, 51),
        "xlabel": r"Missing momentum $|\vec{p}_\mathrm{miss}|$ (GeV)",
        "yscale": "log",
    },
    "n_total_per_event": {
        "edges": np.arange(0, 80, 1),
        "xlabel": r"Total particles per event ($N_\mathrm{ch} + N_\mathrm{neu}$)",
        "yscale": "linear",
    },
}

# Initialize accumulators: data + MC for each variable
data_hists = {k: HistAccum(v["edges"]) for k, v in HIST_DEFS.items()}
mc_hists   = {k: HistAccum(v["edges"]) for k, v in HIST_DEFS.items()}


# ---------------------------------------------------------------------------
# Processing function
# ---------------------------------------------------------------------------

def fill_hists(path: Path, hists: dict, is_mc: bool = False):
    """Read one file and fill all histograms."""
    label = path.name
    log.info(f"  Processing: {label}")
    with uproot.open(str(path)) as f:
        arrays = f["t"].arrays(KINEMATIC_BRANCHES, library="ak")

    # Apply passesAll
    sel = ak.to_numpy(arrays["passesAll"])
    arrays = arrays[sel]

    # ---- Per-particle ----
    pwflag = arrays["pwflag"]
    pmag   = arrays["pmag"]
    pt_arr = arrays["pt"]
    theta  = arrays["theta"]
    d0_arr = arrays["d0"]
    z0_arr = arrays["z0"]
    ntpc   = arrays["ntpc"]

    # Charged (pwflag = 0)
    mask_chg = pwflag == 0
    # Neutral (pwflag = 4)
    mask_neu = pwflag == 4

    # Flatten per-track arrays for track-level histograms
    chg_pmag    = ak.to_numpy(ak.flatten(pmag[mask_chg]))
    chg_pt_flat = ak.to_numpy(ak.flatten(pt_arr[mask_chg]))
    chg_cos     = np.cos(ak.to_numpy(ak.flatten(theta[mask_chg])))
    chg_d0      = ak.to_numpy(ak.flatten(d0_arr[mask_chg]))
    chg_z0      = ak.to_numpy(ak.flatten(z0_arr[mask_chg]))
    chg_ntpc    = ak.to_numpy(ak.flatten(ntpc[mask_chg]))

    neu_pmag    = ak.to_numpy(ak.flatten(pmag[mask_neu]))
    neu_cos     = np.cos(ak.to_numpy(ak.flatten(theta[mask_neu])))

    # Per-event variables
    n_charged    = ak.to_numpy(ak.sum(mask_chg, axis=1))
    n_neutral    = ak.to_numpy(ak.sum(mask_neu, axis=1))
    n_total      = ak.to_numpy(ak.num(pwflag))   # all particles (any pwflag)
    e_chg        = ak.to_numpy(ak.sum(pmag[mask_chg], axis=1))
    e_neu        = ak.to_numpy(ak.sum(pmag[mask_neu], axis=1))
    e_tot        = ak.to_numpy(ak.sum(pmag, axis=1))
    missp        = ak.to_numpy(arrays["missP"])

    # Fill
    hists["n_charged_per_event"].fill(n_charged)
    hists["n_neutral_per_event"].fill(n_neutral)
    hists["chg_pmag"].fill(chg_pmag)
    hists["chg_pt"].fill(chg_pt_flat)
    hists["chg_costheta"].fill(chg_cos)
    hists["chg_d0"].fill(chg_d0)
    hists["chg_z0"].fill(chg_z0)
    hists["chg_ntpc"].fill(chg_ntpc.astype(float))
    hists["neu_pmag"].fill(neu_pmag)
    hists["neu_costheta"].fill(neu_cos)
    hists["e_charged"].fill(e_chg)
    hists["e_neutral"].fill(e_neu)
    hists["e_total"].fill(e_tot)
    hists["missp"].fill(missp)
    hists["n_total_per_event"].fill(n_total)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    log.info("=" * 70)
    log.info("Phase 3 Script 4: Data/MC Kinematic Validation")
    log.info("=" * 70)

    # ------------------------------------------------------------------
    # Process DATA
    # ------------------------------------------------------------------
    log.info("\n[bold]Processing DATA files[/bold]")
    for path in DATA_FILES:
        fill_hists(path, data_hists, is_mc=False)
    log.info(f"Data total events (n_charged_per_event sum): "
             f"{data_hists['n_charged_per_event'].counts.sum():.0f}")

    # ------------------------------------------------------------------
    # Process MC
    # ------------------------------------------------------------------
    log.info("\n[bold]Processing MC files[/bold]")
    for path in MC_FILES:
        fill_hists(path, mc_hists, is_mc=True)
    log.info(f"MC total events (n_charged_per_event sum): "
             f"{mc_hists['n_charged_per_event'].counts.sum():.0f}")

    # ------------------------------------------------------------------
    # Produce comparison plots
    # ------------------------------------------------------------------
    mh.style.use("CMS")

    # Group labels for titles/output filenames
    variable_groups = {
        "charged_multiplicity":  ["n_charged_per_event"],
        "neutral_multiplicity":  ["n_neutral_per_event"],
        "total_multiplicity":    ["n_total_per_event"],
        "charged_momentum":      ["chg_pmag", "chg_pt"],
        "charged_angle":         ["chg_costheta"],
        "charged_impact_param":  ["chg_d0", "chg_z0"],
        "charged_tpc_hits":      ["chg_ntpc"],
        "neutral_energy":        ["neu_pmag"],
        "neutral_angle":         ["neu_costheta"],
        "event_energy":          ["e_charged", "e_neutral", "e_total"],
        "missp":                 ["missp"],
    }

    agreement_table = Table(title="Data/MC Agreement Summary", show_header=True)
    agreement_table.add_column("Variable", style="cyan")
    agreement_table.add_column("Max |ratio - 1| (in range)", justify="right")
    agreement_table.add_column("Status", justify="center")

    for var_key, hdef in HIST_DEFS.items():
        d_counts = data_hists[var_key].counts
        m_counts = mc_hists[var_key].counts
        edges    = hdef["edges"]
        centers  = 0.5 * (edges[:-1] + edges[1:])
        bwidths  = np.diff(edges)

        # Normalize to density
        d_norm = d_counts / (d_counts.sum() * bwidths) if d_counts.sum() > 0 else d_counts
        m_norm = m_counts / (m_counts.sum() * bwidths) if m_counts.sum() > 0 else m_counts

        # Statistical uncertainties
        d_unc = np.sqrt(np.maximum(d_counts, 1)) / (d_counts.sum() * bwidths) if d_counts.sum() > 0 else np.zeros_like(d_counts)
        m_unc = np.sqrt(np.maximum(m_counts, 1)) / (m_counts.sum() * bwidths) if m_counts.sum() > 0 else np.zeros_like(m_counts)

        # Ratio
        ratio     = np.where(m_norm > 0, d_norm / m_norm, np.nan)
        ratio_unc = np.where(
            m_norm > 0,
            np.sqrt((d_unc / m_norm)**2 + (d_norm * m_unc / m_norm**2)**2),
            np.nan,
        )

        # Agreement: max |ratio - 1| in bins with enough data (> 1% of peak)
        threshold = 0.01 * d_norm.max() if d_norm.max() > 0 else 0.0
        in_range  = (d_norm > threshold) & (m_norm > 0)
        max_dev   = np.nanmax(np.abs(ratio[in_range] - 1.0)) if in_range.any() else np.nan

        status = "OK" if (np.isnan(max_dev) or max_dev < 0.15) else "CHECK"
        if not np.isnan(max_dev):
            agreement_table.add_row(var_key, f"{max_dev*100:.1f}%",
                                    "[green]OK[/green]" if status == "OK" else "[yellow]CHECK[/yellow]")

        # ------ Plot ------
        fig, (ax, rax) = plt.subplots(
            2, 1, figsize=(10, 10),
            gridspec_kw={"height_ratios": [3, 1]},
            sharex=True,
        )
        fig.subplots_adjust(hspace=0.0)

        ax.stairs(d_norm, edges, color="black",   linewidth=1.5, label="Data 1992–1995")
        ax.stairs(m_norm, edges, color="tab:red", linewidth=1.5, linestyle="--",
                  label="MC Pythia 6.1")
        ax.set_ylabel(r"$\frac{1}{N}\frac{dN}{dx}$ (a.u.)", fontsize=14)
        ax.set_yscale(hdef.get("yscale", "linear"))
        ax.legend(fontsize="x-small")
        mh.label.exp_label(exp="ALEPH", data=True, rlabel=r"$\sqrt{s} = 91.2$ GeV", ax=ax)

        rax.axhline(1.0, color="gray", linewidth=1.0)
        rax.stairs(ratio, edges, color="black", linewidth=1.5)
        rax.errorbar(
            centers, ratio, yerr=ratio_unc,
            fmt="none", color="black", capsize=2,
        )
        rax.set_xlabel(hdef["xlabel"], fontsize=14)
        rax.set_ylabel("Data / MC", fontsize=12)
        rax.set_ylim(0.7, 1.3)
        rax.set_xlim(edges[0], edges[-1])

        for fmt in ("pdf", "png"):
            fig.savefig(FIG_DIR / f"datamc_{var_key}.{fmt}", bbox_inches="tight",
                        dpi=200, transparent=True)
        plt.close(fig)
        log.info(f"  Saved datamc_{var_key}")

    console.print(agreement_table)

    # Save agreement summary
    np.savez(
        OUT_DIR / "datamc_agreement.npz",
        variables=np.array(list(HIST_DEFS.keys())),
    )
    log.info("Saved datamc_agreement.npz")

    log.info("\n[bold green]data_mc_validation.py complete[/bold green]")
    log.info(f"Figures in {FIG_DIR}/")


if __name__ == "__main__":
    main()
