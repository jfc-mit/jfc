"""
Phase 3 Supplementary: validate_pwflag_categories.py

Category A review fix: verify that pwflag categories 1, 2, 3, and 5 contribute
negligible momentum to the thrust sum, or produce data/MC comparison plots for
any category that contributes >= 1% of total momentum.

The stored `Thrust` branch uses ALL particles (pwflag 0-5). The existing
data_mc_validation.py only covers pwflag=0 (charged tracks) and pwflag=4
(neutral clusters). This script closes that gap.

Method:
  For each pwflag in {0, 1, 2, 3, 4, 5}:
    - count events containing at least one particle of this type
    - count total particles of this type
    - compute fraction of total event momentum (sum|p|) contributed by this type
  If any type contributes >= 1% of total momentum -> produce data/MC comparison
  plots (|p| and cos(theta)) for that type.

Inputs: 1 data file (1994P1) + 1 MC file (001) for a quick representative check.
Outputs:
  - phase3_selection/figures/pwflag_momentum_fractions.{pdf,png}
  - phase3_selection/figures/datamc_pwflag{N}_*.{pdf,png}  (only if >= 1%)
  - phase3_selection/exec/pwflag_coverage_summary.txt
"""

import logging
from pathlib import Path

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
log = logging.getLogger("validate_pwflag")
console = Console()

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DATA_FILE = Path("/n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ALEPH/"
                 "LEP1Data1994P1_recons_aftercut-MERGED.root")
MC_FILE   = Path("/n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ALEPHMC/"
                 "LEP1MC1994_recons_aftercut-001.root")
FIG_DIR   = Path("phase3_selection/figures")
OUT_DIR   = Path("phase3_selection/exec")
FIG_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

PWFLAG_LABELS = {
    0: "Good charged tracks (primary)",
    1: "Charged tracks (reduced quality)",
    2: "Charged tracks (further reduced quality)",
    3: "Charged tracks (pathological / very few)",
    4: "Neutral calorimeter clusters",
    5: "Additional neutral objects",
}

# 1% threshold: if a category contributes >= this fraction -> make plots
PLOT_THRESHOLD = 0.01


# ---------------------------------------------------------------------------
# Load one file, apply passesAll, return relevant arrays
# ---------------------------------------------------------------------------

def load_file(path: Path, label: str):
    log.info(f"Loading {label}: {path.name}")
    branches = ["passesAll", "pwflag", "pmag", "theta"]
    with uproot.open(str(path)) as f:
        arrays = f["t"].arrays(branches, library="ak")
    sel = ak.to_numpy(arrays["passesAll"])
    arrays = arrays[sel]
    n_events = len(arrays)
    log.info(f"  {n_events:,} events after passesAll")
    return arrays, n_events


# ---------------------------------------------------------------------------
# Compute per-pwflag statistics
# ---------------------------------------------------------------------------

def compute_pwflag_stats(arrays, n_events, label):
    """Return dict keyed by pwflag with momentum fraction and particle counts."""
    pwflag = arrays["pwflag"]
    pmag   = arrays["pmag"]

    # Total momentum sum over all particles in all events
    total_pmag_sum = float(ak.sum(pmag))

    stats = {}
    for flag in range(6):  # 0..5
        mask         = (pwflag == flag)
        n_particles  = int(ak.sum(mask))
        n_events_w   = int(ak.sum(ak.any(mask, axis=1)))
        pmag_sum     = float(ak.sum(pmag[mask]))
        frac         = pmag_sum / total_pmag_sum if total_pmag_sum > 0 else 0.0
        stats[flag]  = {
            "n_particles":   n_particles,
            "n_events_with": n_events_w,
            "pmag_sum":      pmag_sum,
            "frac":          frac,
        }
        log.info(
            f"  [{label}] pwflag={flag}: {n_particles:>10,} particles, "
            f"{n_events_w:>9,} events, momentum fraction = {frac*100:.4f}%"
        )
    return stats, total_pmag_sum


# ---------------------------------------------------------------------------
# Plot bar chart of momentum fractions
# ---------------------------------------------------------------------------

def plot_momentum_fractions(data_stats, mc_stats):
    flags  = list(range(6))
    d_frac = np.array([data_stats[f]["frac"] for f in flags]) * 100.0
    m_frac = np.array([mc_stats[f]["frac"]   for f in flags]) * 100.0

    x = np.arange(len(flags))
    width = 0.35

    mh.style.use("CMS")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width/2, d_frac, width, label="Data 1994 P1",   color="black", alpha=0.7)
    ax.bar(x + width/2, m_frac, width, label="MC Pythia 6.1",  color="tab:red", alpha=0.7)
    ax.axhline(1.0, color="orange", linewidth=1.2, linestyle="--",
               label="1% threshold")
    ax.set_xticks(x)
    ax.set_xticklabels([f"pwflag={f}" for f in flags], rotation=15, ha="right")
    ax.set_ylabel("Momentum fraction (% of total)", fontsize=12)
    ax.set_yscale("log")
    ax.legend(fontsize="x-small")
    mh.label.exp_label(exp="ALEPH", data=True, rlabel=r"$\sqrt{s} = 91.2$ GeV", ax=ax)

    for fmt in ("pdf", "png"):
        fig.savefig(FIG_DIR / f"pwflag_momentum_fractions.{fmt}",
                    bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)
    log.info("Saved pwflag_momentum_fractions")


# ---------------------------------------------------------------------------
# Data/MC comparison for a single pwflag category
# ---------------------------------------------------------------------------

def plot_datamc_for_flag(flag, data_arrays, mc_arrays, data_stats, mc_stats):
    """Produce |p| and cos(theta) comparison plots for a given pwflag."""
    label = PWFLAG_LABELS.get(flag, f"pwflag={flag}")

    for dataset_name, arrays_dict in [("data", data_arrays), ("mc", mc_arrays)]:
        pass  # just to satisfy linter — we build combined below

    d_pw = data_arrays["pwflag"]
    d_pm = data_arrays["pmag"]
    d_th = data_arrays["theta"]
    m_pw = mc_arrays["pwflag"]
    m_pm = mc_arrays["pmag"]
    m_th = mc_arrays["theta"]

    d_mask = (d_pw == flag)
    m_mask = (m_pw == flag)

    d_pmag_flat = ak.to_numpy(ak.flatten(d_pm[d_mask]))
    m_pmag_flat = ak.to_numpy(ak.flatten(m_pm[m_mask]))
    d_cos_flat  = np.cos(ak.to_numpy(ak.flatten(d_th[d_mask])))
    m_cos_flat  = np.cos(ak.to_numpy(ak.flatten(m_th[m_mask])))

    if len(d_pmag_flat) == 0 or len(m_pmag_flat) == 0:
        log.warning(f"  pwflag={flag}: empty array for data or MC — skipping plots")
        return

    mh.style.use("CMS")

    for var_key, d_vals, m_vals, xlabel, edges, yscale in [
        (
            f"pwflag{flag}_pmag",
            d_pmag_flat, m_pmag_flat,
            rf"pwflag={flag} $|p|$ (GeV)",
            np.concatenate([np.linspace(0, 2, 21), np.linspace(2, 10, 17), np.linspace(10, 50, 9)]),
            "log",
        ),
        (
            f"pwflag{flag}_costheta",
            d_cos_flat, m_cos_flat,
            rf"pwflag={flag} $\cos\theta$",
            np.linspace(-1, 1, 41),
            "linear",
        ),
    ]:
        d_counts, _ = np.histogram(d_vals, bins=edges)
        m_counts, _ = np.histogram(m_vals, bins=edges)
        bwidths = np.diff(edges)
        centers = 0.5 * (edges[:-1] + edges[1:])

        d_norm = d_counts / (d_counts.sum() * bwidths) if d_counts.sum() > 0 else d_counts * 0.0
        m_norm = m_counts / (m_counts.sum() * bwidths) if m_counts.sum() > 0 else m_counts * 0.0

        d_unc = np.sqrt(np.maximum(d_counts, 1)) / (d_counts.sum() * bwidths) if d_counts.sum() > 0 else np.zeros_like(d_counts, dtype=float)
        m_unc = np.sqrt(np.maximum(m_counts, 1)) / (m_counts.sum() * bwidths) if m_counts.sum() > 0 else np.zeros_like(m_counts, dtype=float)

        ratio     = np.where(m_norm > 0, d_norm / m_norm, np.nan)
        ratio_unc = np.where(
            m_norm > 0,
            np.sqrt((d_unc / m_norm)**2 + (d_norm * m_unc / m_norm**2)**2),
            np.nan,
        )

        fig, (ax, rax) = plt.subplots(
            2, 1, figsize=(10, 10),
            gridspec_kw={"height_ratios": [3, 1]},
            sharex=True,
        )
        fig.subplots_adjust(hspace=0.0)

        ax.stairs(d_norm, edges, color="black",   linewidth=1.5, label="Data 1994 P1")
        ax.stairs(m_norm, edges, color="tab:red", linewidth=1.5, linestyle="--",
                  label="MC Pythia 6.1")
        ax.set_ylabel(r"$\frac{1}{N}\frac{dN}{dx}$ (a.u.)", fontsize=14)
        ax.set_yscale(yscale)
        ax.legend(fontsize="x-small")
        mh.label.exp_label(exp="ALEPH", data=True, rlabel=r"$\sqrt{s} = 91.2$ GeV", ax=ax)

        rax.axhline(1.0, color="gray", linewidth=1.0)
        rax.stairs(ratio, edges, color="black", linewidth=1.5)
        rax.errorbar(centers, ratio, yerr=ratio_unc, fmt="none", color="black", capsize=2)
        rax.set_xlabel(xlabel, fontsize=14)
        rax.set_ylabel("Data / MC", fontsize=12)
        rax.set_ylim(0.5, 1.5)
        rax.set_xlim(edges[0], edges[-1])

        for fmt in ("pdf", "png"):
            fig.savefig(FIG_DIR / f"datamc_{var_key}.{fmt}",
                        bbox_inches="tight", dpi=200, transparent=True)
        plt.close(fig)
        log.info(f"  Saved datamc_{var_key}")


# ---------------------------------------------------------------------------
# Write text summary
# ---------------------------------------------------------------------------

def write_summary(data_stats, mc_stats, flags_above_threshold):
    lines = []
    lines.append("pwflag Category Coverage Summary")
    lines.append("=" * 60)
    lines.append("Input: 1 data file (1994P1) + 1 MC file (001), passesAll applied.")
    lines.append("")
    lines.append(f"{'Flag':<6} {'Description':<42} {'Data frac%':>10} {'MC frac%':>10}")
    lines.append("-" * 70)
    for flag in range(6):
        desc   = PWFLAG_LABELS.get(flag, "?")[:41]
        d_frac = data_stats[flag]["frac"] * 100.0
        m_frac = mc_stats[flag]["frac"]   * 100.0
        lines.append(f"{flag:<6} {desc:<42} {d_frac:>10.4f} {m_frac:>10.4f}")
    lines.append("")
    lines.append(f"1% threshold for mandatory plotting: {PLOT_THRESHOLD*100:.0f}%")
    lines.append("")
    if flags_above_threshold:
        lines.append(f"Flags above threshold (plots produced): {flags_above_threshold}")
    else:
        lines.append("No flags above 1% threshold.")
        lines.append("Flags 1, 2, 3, and 5 each contribute < 1% of total event momentum.")
        lines.append("Their contribution to the thrust sum is negligible.")
        lines.append("Validation for these categories is not required beyond this")
        lines.append("quantitative demonstration.")
    lines.append("")
    lines.append("Particle counts per category (data / MC):")
    for flag in range(6):
        d_n = data_stats[flag]["n_particles"]
        m_n = mc_stats[flag]["n_particles"]
        d_e = data_stats[flag]["n_events_with"]
        m_e = mc_stats[flag]["n_events_with"]
        lines.append(
            f"  pwflag={flag}: data {d_n:>10,} particles in {d_e:>9,} events | "
            f"MC {m_n:>8,} particles in {m_e:>8,} events"
        )

    summary_path = OUT_DIR / "pwflag_coverage_summary.txt"
    summary_path.write_text("\n".join(lines) + "\n")
    log.info(f"Saved {summary_path}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    log.info("=" * 70)
    log.info("Phase 3 Supplementary: pwflag category coverage validation")
    log.info("=" * 70)

    # Load data
    data_arrays, data_n = load_file(DATA_FILE, "Data 1994P1")
    mc_arrays,   mc_n   = load_file(MC_FILE,   "MC 001")

    # Compute statistics per pwflag
    log.info("\n[bold]Data pwflag statistics:[/bold]")
    data_stats, data_total = compute_pwflag_stats(data_arrays, data_n, "Data")

    log.info("\n[bold]MC pwflag statistics:[/bold]")
    mc_stats, mc_total = compute_pwflag_stats(mc_arrays, mc_n, "MC")

    # Summary table via rich
    tbl = Table(title="pwflag Momentum Fractions", show_header=True)
    tbl.add_column("pwflag", style="cyan")
    tbl.add_column("Description")
    tbl.add_column("Data %", justify="right")
    tbl.add_column("MC %", justify="right")
    tbl.add_column("Action", justify="center")
    for flag in range(6):
        d_f = data_stats[flag]["frac"] * 100.0
        m_f = mc_stats[flag]["frac"]   * 100.0
        above = (d_f >= PLOT_THRESHOLD * 100) or (m_f >= PLOT_THRESHOLD * 100)
        action = "[yellow]PLOT[/yellow]" if above else "[green]negligible[/green]"
        tbl.add_row(
            str(flag),
            PWFLAG_LABELS.get(flag, "?"),
            f"{d_f:.4f}",
            f"{m_f:.4f}",
            action,
        )
    console.print(tbl)

    # Determine which flags need plots
    flags_above = [
        f for f in range(6)
        if (data_stats[f]["frac"] >= PLOT_THRESHOLD or
            mc_stats[f]["frac"]   >= PLOT_THRESHOLD)
    ]
    log.info(f"\nFlags above {PLOT_THRESHOLD*100:.0f}% threshold: {flags_above}")

    # Always produce the momentum-fraction overview plot
    plot_momentum_fractions(data_stats, mc_stats)

    # Produce per-category plots only for flags above threshold
    for flag in flags_above:
        log.info(f"\nProducing data/MC comparison plots for pwflag={flag}")
        plot_datamc_for_flag(flag, data_arrays, mc_arrays, data_stats, mc_stats)

    # Write text summary
    summary = write_summary(data_stats, mc_stats, flags_above)
    console.print("\n[bold]Summary:[/bold]")
    console.print(summary)

    log.info("\n[bold green]validate_pwflag_categories.py complete[/bold green]")
    log.info(f"Figures in {FIG_DIR}/")
    log.info(f"Summary in {OUT_DIR}/pwflag_coverage_summary.txt")


if __name__ == "__main__":
    main()
