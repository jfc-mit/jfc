"""
Phase 4a Script 4: final_result.py

Run the nominal unfolding on actual data with the validated iteration count.
Produce the final corrected thrust distribution with full uncertainties.

Steps:
  1. Run nominal IBU on data (3 iterations, MC prior)
  2. Apply efficiency correction
  3. Normalize: (1/N) dN/dtau
  4. Assign per-bin uncertainties from covariance matrix
  5. Compare to MC truth (Pythia 6.1 particle level) with chi2/p-value
  6. Save machine-readable results

Outputs:
  - phase4_inference/exec/results/thrust_distribution.npz
  - phase4_inference/exec/results/thrust_distribution.csv
  - phase4_inference/figures/final_result_*.{pdf,png}
"""

import logging
from pathlib import Path

import numpy as np
from scipy import stats
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
log = logging.getLogger("final_result")
console = Console()

# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------
P3_EXEC  = Path("phase3_selection/exec")
P4_EXEC  = Path("phase4_inference/exec")
FIG_DIR  = Path("phase4_inference/figures")
RESULTS  = Path("phase4_inference/exec/results")
P4_EXEC.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)
RESULTS.mkdir(parents=True, exist_ok=True)

N_BINS      = 25
TAU_MIN     = 0.0
TAU_MAX     = 0.5
TAU_EDGES   = np.linspace(TAU_MIN, TAU_MAX, N_BINS + 1)
TAU_CENTERS = 0.5 * (TAU_EDGES[:-1] + TAU_EDGES[1:])
BIN_WIDTH   = TAU_EDGES[1] - TAU_EDGES[0]
FIT_MASK    = (TAU_CENTERS >= 0.05) & (TAU_CENTERS <= 0.30)
N_FIT_BINS  = int(FIT_MASK.sum())
NOMINAL_ITER = 3


# ---------------------------------------------------------------------------
# IBU algorithm
# ---------------------------------------------------------------------------

def ibu(data_reco: np.ndarray, R: np.ndarray, efficiency: np.ndarray,
        prior: np.ndarray, n_iter: int) -> np.ndarray:
    n_reco, n_gen = R.shape
    prior = prior / prior.sum() if prior.sum() > 0 else np.ones(n_gen) / n_gen
    for _ in range(n_iter):
        denom      = R @ prior
        safe_denom = np.where(denom > 0, denom, 1.0)
        U          = (R * prior[np.newaxis, :]).T / safe_denom[:, np.newaxis]
        unfolded   = U.T @ data_reco
        safe_eff   = np.where(efficiency > 0, efficiency, 1.0)
        unfolded   = unfolded / safe_eff
        if unfolded.sum() > 0:
            prior = unfolded / unfolded.sum()
        else:
            prior = np.ones(n_gen) / n_gen
    return unfolded


def normalize(h: np.ndarray) -> np.ndarray:
    s = h.sum()
    return h / (s * BIN_WIDTH) if s > 0 else h.copy()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    log.info("=" * 70)
    log.info("Phase 4a Script 4: Final Result")
    log.info("=" * 70)

    # -------------------------------------------------------------------------
    # Load nominal inputs
    # -------------------------------------------------------------------------
    rm = np.load(P3_EXEC / "response_matrix.npz")
    R          = rm["R"]
    eff        = rm["efficiency"]
    h_gen_sel  = rm["h_gen_sel"]
    h_gen_before = rm["h_gen_before"]

    dh = np.load(P3_EXEC / "hist_tau_data.npz")
    h_data = dh["counts"].astype(float)

    # Load covariance matrices
    cov_data = np.load(P4_EXEC / "covariance_total.npz")
    cov_total  = cov_data["cov"]
    sigma_tot  = cov_data["sigma_tot"]
    sigma_stat = cov_data["sigma_stat"]
    sigma_syst = cov_data["sigma_syst"]

    # Check if independent closure test revised the iteration count
    try:
        indep = np.load(P4_EXEC / "indep_closure_results.npz")
        indep_optimal = int(indep["optimal_iter"])
        log.info(f"Independent MC closure test optimal iter: {indep_optimal}")
        if indep_optimal != NOMINAL_ITER:
            log.info(f"  Phase 3 nominal was {NOMINAL_ITER}; independent test says {indep_optimal}")
            log.info(f"  Using {NOMINAL_ITER} (nominal) as analysis choice — see INFERENCE_EXPECTED.md")
    except FileNotFoundError:
        log.warning("indep_closure_results.npz not found — using Phase 3 nominal = 3")
        indep_optimal = NOMINAL_ITER

    prior_mc = h_gen_sel / h_gen_sel.sum() if h_gen_sel.sum() > 0 else np.ones(N_BINS) / N_BINS

    # -------------------------------------------------------------------------
    # Nominal unfolding
    # -------------------------------------------------------------------------
    log.info(f"\nRunning IBU on data ({NOMINAL_ITER} iterations, MC prior)...")
    unfolded_counts = ibu(h_data, R, eff, prior_mc.copy(), NOMINAL_ITER)
    unfolded_norm   = normalize(unfolded_counts)

    log.info(f"Data events: {h_data.sum():.0f}")
    log.info(f"Unfolded counts total: {unfolded_counts.sum():.0f}")
    log.info(f"Normalized integral: {np.sum(unfolded_norm * BIN_WIDTH):.4f} (should be ~1)")

    # MC truth (tgenBefore) for comparison
    mc_truth_norm = normalize(h_gen_before.astype(float))

    # -------------------------------------------------------------------------
    # Chi2 comparison to MC truth (using full covariance)
    # -------------------------------------------------------------------------
    log.info("\n[bold]Chi2 comparison to MC truth (Pythia 6.1)...[/bold]")

    # Sub-matrix for fit range
    cov_fit = cov_total[np.ix_(FIT_MASK, FIT_MASK)]

    # Invert fit-range covariance
    try:
        cov_fit_inv = np.linalg.inv(cov_fit)
        is_inv_ok = True
    except np.linalg.LinAlgError:
        log.warning("  Covariance inversion failed; using diagonal-only chi2")
        cov_fit_inv = np.diag(1.0 / np.diag(cov_fit))
        is_inv_ok = False

    delta_fit = unfolded_norm[FIT_MASK] - mc_truth_norm[FIT_MASK]
    chi2_full = float(delta_fit @ cov_fit_inv @ delta_fit)
    ndf_full  = N_FIT_BINS
    pval_full = float(stats.chi2.sf(chi2_full, df=ndf_full))

    log.info(f"  chi2/ndf = {chi2_full:.1f} / {ndf_full} = {chi2_full/ndf_full:.3f}")
    log.info(f"  p-value  = {pval_full:.4f}")
    if chi2_full / ndf_full > 1.5:
        log.warning("  chi2/ndf > 1.5 — requires investigation per conventions")

    # Also compute with diagonal uncertainties only for comparison
    diag_unc2 = np.diag(cov_fit)
    chi2_diag = float(np.sum(delta_fit**2 / np.maximum(diag_unc2, 1e-30)))
    log.info(f"  chi2/ndf (diagonal only) = {chi2_diag:.1f} / {ndf_full} = {chi2_diag/ndf_full:.3f}")

    # -------------------------------------------------------------------------
    # Per-bin table
    # -------------------------------------------------------------------------
    log.info("\n[bold]Final result per bin (fit range):[/bold]")
    table = Table(title="Corrected Thrust Distribution", show_header=True)
    table.add_column("tau_center",  justify="right")
    table.add_column("(1/N)dN/dtau", justify="right")
    table.add_column("Stat unc",    justify="right")
    table.add_column("Syst unc",    justify="right")
    table.add_column("Total unc",   justify="right")
    table.add_column("MC truth",    justify="right")
    table.add_column("Data/MC",     justify="right")

    for j in range(N_BINS):
        if FIT_MASK[j]:
            ratio = unfolded_norm[j] / mc_truth_norm[j] if mc_truth_norm[j] > 0 else np.nan
            table.add_row(
                f"{TAU_CENTERS[j]:.3f}",
                f"{unfolded_norm[j]:.4f}",
                f"{sigma_stat[j]:.4f}",
                f"{sigma_syst[j]:.4f}",
                f"{sigma_tot[j]:.4f}",
                f"{mc_truth_norm[j]:.4f}",
                f"{ratio:.4f}",
            )
    console.print(table)

    # -------------------------------------------------------------------------
    # Save machine-readable results
    # -------------------------------------------------------------------------
    np.savez(
        RESULTS / "thrust_distribution.npz",
        tau_edges=TAU_EDGES,
        tau_centers=TAU_CENTERS,
        tau_bin_width=BIN_WIDTH,
        unfolded_norm=unfolded_norm,
        unfolded_counts=unfolded_counts,
        sigma_stat=sigma_stat,
        sigma_syst=sigma_syst,
        sigma_tot=sigma_tot,
        mc_truth_norm=mc_truth_norm,
        fit_mask=FIT_MASK,
        n_data_events=h_data.sum(),
        chi2_vs_mc=chi2_full,
        ndf_vs_mc=ndf_full,
        pval_vs_mc=pval_full,
        n_iterations=NOMINAL_ITER,
    )
    log.info(f"Saved {RESULTS}/thrust_distribution.npz")

    # Save CSV (fit range, human-readable)
    csv_lines = [
        "# ALEPH Thrust Distribution -- (1/N)dN/dtau -- corrected for detector effects",
        "# Analysis: thrust_alphas, Phase 4a",
        "# tau_center, tau_lo, tau_hi, dNdtau, stat_unc, syst_unc, total_unc",
    ]
    for j in range(N_BINS):
        if FIT_MASK[j]:
            csv_lines.append(
                f"{TAU_CENTERS[j]:.4f},"
                f"{TAU_EDGES[j]:.4f},"
                f"{TAU_EDGES[j+1]:.4f},"
                f"{unfolded_norm[j]:.6e},"
                f"{sigma_stat[j]:.6e},"
                f"{sigma_syst[j]:.6e},"
                f"{sigma_tot[j]:.6e}"
            )
    csv_path = RESULTS / "thrust_distribution.csv"
    with open(csv_path, "w") as f:
        f.write("\n".join(csv_lines) + "\n")
    log.info(f"Saved {csv_path}")

    # =========================================================================
    # Figures
    # =========================================================================
    mh.style.use("CMS")

    # Fig 1: Final unfolded distribution with uncertainties
    fig1, (ax1, rax1) = plt.subplots(
        2, 1, figsize=(10, 10),
        gridspec_kw={"height_ratios": [3, 1]}, sharex=True,
    )
    fig1.subplots_adjust(hspace=0.0)

    # Main panel
    ax1.errorbar(
        TAU_CENTERS, unfolded_norm,
        yerr=sigma_tot,
        fmt="o", color="black", markersize=4, linewidth=1.5,
        label=f"Data (IBU, {NOMINAL_ITER} iter) [total unc.]",
        capsize=3,
    )
    ax1.errorbar(
        TAU_CENTERS, unfolded_norm,
        yerr=sigma_stat,
        fmt="none", color="black", linewidth=3.0,
        label="Statistical uncertainty",
        capsize=0,
    )
    ax1.stairs(mc_truth_norm, TAU_EDGES, color="tab:red", linewidth=2.0,
               linestyle="--", label="Pythia 6.1 (particle level)")

    ax1.set_ylabel(r"$(1/N)\,dN/d\tau$", fontsize=14)
    ax1.set_yscale("log")
    ax1.set_xlim(TAU_MIN, 0.45)
    ax1.legend(fontsize="x-small")
    mh.label.exp_label(exp="ALEPH", data=True, rlabel=r"$\sqrt{s} = 91.2$ GeV", ax=ax1)

    # Add chi2 annotation
    ax1.text(0.60, 0.75,
             rf"$\chi^2/\mathrm{{ndf}} = {chi2_full:.1f}/{ndf_full}$"
             f"\n$p = {pval_full:.3f}$",
             transform=ax1.transAxes, fontsize=11,
             bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))

    # Ratio panel
    ratio = np.where(mc_truth_norm > 0, unfolded_norm / mc_truth_norm, np.nan)
    ratio_unc = np.where(mc_truth_norm > 0, sigma_tot / mc_truth_norm, 0.0)
    ratio_stat_unc = np.where(mc_truth_norm > 0, sigma_stat / mc_truth_norm, 0.0)

    rax1.axhline(1.0, color="gray", linewidth=1.0)
    rax1.fill_between(
        TAU_CENTERS, ratio - ratio_unc, ratio + ratio_unc,
        alpha=0.3, color="black", step=None,
    )
    rax1.errorbar(TAU_CENTERS, ratio, yerr=ratio_stat_unc,
                  fmt="o", color="black", markersize=4, capsize=2)
    rax1.set_xlabel(r"$\tau = 1 - T$", fontsize=14)
    rax1.set_ylabel("Data / MC truth", fontsize=12)
    rax1.set_ylim(0.7, 1.3)
    rax1.set_xlim(TAU_MIN, 0.45)
    # Mark fit range
    rax1.axvspan(0.05, 0.30, alpha=0.05, color="green")

    for fmt in ("pdf", "png"):
        fig1.savefig(FIG_DIR / f"final_result_with_unc.{fmt}",
                     bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig1)
    log.info("Saved final_result_with_unc")

    # Fig 2: Uncertainty breakdown (absolute)
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    ax2.stairs(sigma_stat * 100 / np.where(unfolded_norm > 0, unfolded_norm, 1.0),
               TAU_EDGES, color="tab:blue", linewidth=2.0, label="Statistical (%)")
    ax2.stairs(sigma_syst * 100 / np.where(unfolded_norm > 0, unfolded_norm, 1.0),
               TAU_EDGES, color="tab:red", linewidth=2.0, linestyle="--", label="Systematic (%)")
    ax2.stairs(sigma_tot  * 100 / np.where(unfolded_norm > 0, unfolded_norm, 1.0),
               TAU_EDGES, color="black", linewidth=2.0, label="Total (%)")
    ax2.axvspan(0.05, 0.30, alpha=0.05, color="green")
    ax2.set_xlabel(r"$\tau = 1 - T$", fontsize=14)
    ax2.set_ylabel("Fractional uncertainty (%)", fontsize=14)
    ax2.set_xlim(0.0, 0.45)
    ax2.set_ylim(0, 15)
    ax2.legend(fontsize="x-small")
    mh.label.exp_label(exp="ALEPH", data=True, rlabel=r"$\sqrt{s} = 91.2$ GeV", ax=ax2)
    for fmt in ("pdf", "png"):
        fig2.savefig(FIG_DIR / f"final_result_unc_breakdown.{fmt}",
                     bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig2)
    log.info("Saved final_result_unc_breakdown")

    # Fig 3: Comparison data vs MC in fit range, zoomed in
    fig3, (ax3, rax3) = plt.subplots(
        2, 1, figsize=(10, 10),
        gridspec_kw={"height_ratios": [3, 1]}, sharex=True,
    )
    fig3.subplots_adjust(hspace=0.0)

    fit_centers = TAU_CENTERS[FIT_MASK]
    fit_data    = unfolded_norm[FIT_MASK]
    fit_mc      = mc_truth_norm[FIT_MASK]
    fit_stat    = sigma_stat[FIT_MASK]
    fit_tot     = sigma_tot[FIT_MASK]

    ax3.errorbar(fit_centers, fit_data, yerr=fit_tot,
                 fmt="o", color="black", markersize=5, capsize=3,
                 label=f"Data IBU (iter={NOMINAL_ITER}) [total unc.]")
    ax3.errorbar(fit_centers, fit_data, yerr=fit_stat,
                 fmt="none", color="black", linewidth=4.0)
    ax3.stairs(fit_mc, TAU_EDGES[FIT_MASK.argmax():FIT_MASK.argmax() + N_FIT_BINS + 1],
               color="tab:red", linewidth=2.0, linestyle="--",
               label="Pythia 6.1 particle level")
    ax3.set_ylabel(r"$(1/N)\,dN/d\tau$", fontsize=14)
    ax3.set_yscale("log")
    ax3.legend(fontsize="x-small")
    mh.label.exp_label(exp="ALEPH", data=True, rlabel=r"$\sqrt{s} = 91.2$ GeV", ax=ax3)

    fit_ratio     = np.where(fit_mc > 0, fit_data / fit_mc, np.nan)
    fit_ratio_unc = np.where(fit_mc > 0, fit_tot / fit_mc, 0.0)
    rax3.axhline(1.0, color="gray", linewidth=1.0)
    rax3.fill_between(fit_centers, fit_ratio - fit_ratio_unc, fit_ratio + fit_ratio_unc,
                      alpha=0.3, color="black")
    rax3.errorbar(fit_centers, fit_ratio,
                  yerr=fit_stat / np.where(fit_mc > 0, fit_mc, 1.0),
                  fmt="o", color="black", markersize=5, capsize=2)
    rax3.set_xlabel(r"$\tau = 1 - T$", fontsize=14)
    rax3.set_ylabel("Data / Pythia 6.1", fontsize=12)
    rax3.set_ylim(0.6, 1.4)
    rax3.set_xlim(0.04, 0.32)

    for fmt in ("pdf", "png"):
        fig3.savefig(FIG_DIR / f"final_result_fitrange.{fmt}",
                     bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig3)
    log.info("Saved final_result_fitrange")

    # Summary
    log.info("\n[bold]Final result summary:[/bold]")
    log.info(f"  Measurement range:   tau in [0.00, 0.40] (25 bins)")
    log.info(f"  Fit range:           tau in [0.05, 0.30] ({N_FIT_BINS} bins)")
    log.info(f"  IBU iterations:      {NOMINAL_ITER}")
    log.info(f"  Data events:         {h_data.sum():.0f}")
    log.info(f"  Chi2 vs Pythia 6.1:  {chi2_full:.1f} / {ndf_full} = {chi2_full/ndf_full:.3f}")
    log.info(f"  p-value vs Pythia:   {pval_full:.4f}")
    log.info(f"  Max stat unc (fit):  {sigma_stat[FIT_MASK].max() / unfolded_norm[FIT_MASK][np.argmax(sigma_stat[FIT_MASK])] * 100:.2f}%")
    log.info(f"  Max total unc (fit): {(sigma_tot[FIT_MASK] / np.where(unfolded_norm[FIT_MASK] > 0, unfolded_norm[FIT_MASK], 1.0)).max() * 100:.2f}%")

    log.info("\n[bold green]final_result.py complete[/bold green]")


if __name__ == "__main__":
    main()
