"""
Phase 4a — Fix Systematics (Category A issue resolution)

This script fixes two Category A issues identified in the Phase 4a review:

  Issue 1 (STRESS TEST):
    The conventions require a stress test: unfold a reweighted MC truth through
    the response matrix and verify recovery of the reweighted shape. This test
    was absent. It is now performed by calling stress_test.py's main() function.

  Issue 2 (HADRONIZATION SYSTEMATIC):
    The hadronization systematic was estimated at ~0%, which is not credible
    for thrust at LEP. Published ALEPH/LEP analyses quote 1-3%. A 2% per-bin
    conservative floor (below the 1-3% LEP combination range) is assigned.

Steps:
  1. Run the stress test (imports and calls stress_test.main()).
  2. Assign a 2% per-bin floor to the hadronization systematic.
  3. Rebuild the covariance matrix using the updated shifts.
  4. Rerun final_result.py to update the final result files.
  5. Produce all needed figures.

Outputs:
  - phase4_inference/exec/systematics_shifts.npz  (updated: shift_hadronization)
  - phase4_inference/exec/covariance_{stat,syst,total}.npz  (rebuilt)
  - phase4_inference/exec/results/thrust_distribution.{npz,csv}  (updated)
  - phase4_inference/figures/stress_test.{pdf,png}
  - phase4_inference/figures/syst_hadronization_floor.{pdf,png}
"""

import logging
import sys
from pathlib import Path

import numpy as np
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
log = logging.getLogger("fix_systematics")
console = Console()

# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------
P3_EXEC = Path("phase3_selection/exec")
P4_EXEC = Path("phase4_inference/exec")
FIG_DIR = Path("phase4_inference/figures")
RESULTS = Path("phase4_inference/exec/results")
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
N_TOYS_STAT  = 500

# Conservative hadronization floor (below the 1–3% from LEP combination)
HADRONIZATION_FLOOR_FRACTION = 0.02  # 2% per bin


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
    log.info("Phase 4a: Fix Systematics (Category A Issues)")
    log.info("=" * 70)

    # =========================================================================
    # PART 1: Run the stress test
    # =========================================================================
    log.info("\n" + "=" * 70)
    log.info("PART 1: Running IBU Stress Test")
    log.info("=" * 70)

    # Import and run stress_test.main()
    # Add the scripts directory to the path so stress_test can be imported
    scripts_dir = Path(__file__).parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))

    import stress_test as st_module
    st_module.main()
    log.info("Stress test complete.")

    # Load stress test results for reporting
    st_results = np.load(P4_EXEC / "stress_test_results.npz")
    stress_passed = bool(st_results["stress_test_passed"])
    nominal_chi2  = float(st_results[f"chi2_iter{NOMINAL_ITER}"])
    nominal_ndf   = int(st_results[f"ndf_iter{NOMINAL_ITER}"])
    log.info(f"Stress test PASSED = {stress_passed}, "
             f"chi2/ndf = {nominal_chi2:.2f}/{nominal_ndf} = {nominal_chi2/nominal_ndf:.3f}")

    # =========================================================================
    # PART 2: Fix hadronization systematic
    # =========================================================================
    log.info("\n" + "=" * 70)
    log.info("PART 2: Fix Hadronization Systematic")
    log.info("=" * 70)

    # Load current nominal unfolded result (normalized)
    rm_data   = np.load(P3_EXEC / "response_matrix.npz")
    R         = rm_data["R"]
    eff       = rm_data["efficiency"]
    h_gen_sel = rm_data["h_gen_sel"]

    h_data = np.load(P3_EXEC / "hist_tau_data.npz")["counts"].astype(float)
    prior_mc = h_gen_sel / h_gen_sel.sum() if h_gen_sel.sum() > 0 else np.ones(N_BINS) / N_BINS

    unfolded_nominal  = ibu(h_data, R, eff, prior_mc.copy(), NOMINAL_ITER)
    norm_nominal      = normalize(unfolded_nominal)

    # 2% per-bin floor on hadronization systematic
    # Applied to the normalized distribution: shift = 2% * |nominal|
    hadronization_floor = HADRONIZATION_FLOOR_FRACTION * np.abs(norm_nominal)

    log.info(f"Hadronization floor: {HADRONIZATION_FLOOR_FRACTION*100:.0f}% per bin")
    log.info(f"Max floor value (fit range): {hadronization_floor[FIT_MASK].max():.4e}")
    log.info(f"Max frac uncertainty from floor (fit range): "
             f"{(hadronization_floor[FIT_MASK] / np.where(norm_nominal[FIT_MASK] > 0, norm_nominal[FIT_MASK], 1.0)).max()*100:.2f}%")

    # Load existing systematics_shifts.npz and replace hadronization shift
    syst_file = P4_EXEC / "systematics_shifts.npz"
    existing  = dict(np.load(syst_file, allow_pickle=False))

    # Report old hadronization shift for comparison
    old_hadr_shift = existing.get("shift_hadronization", np.zeros(N_BINS))
    log.info(f"\nOld hadronization shift (max abs, fit range): "
             f"{np.abs(old_hadr_shift[FIT_MASK]).max()*100:.4f}%  (<-- was ~0%)")
    log.info(f"New hadronization shift (max abs, fit range): "
             f"{hadronization_floor[FIT_MASK].max()*100:.2f}%  (2% floor)")

    # Replace hadronization shift: use +floor as a conservative one-sided systematic.
    # We assign it symmetrically as the ±1σ shift in normalized units.
    existing["shift_hadronization"] = hadronization_floor

    # Resave with updated hadronization
    np.savez(syst_file, **existing)
    log.info(f"Updated {syst_file} with hadronization floor.")

    # =========================================================================
    # PART 3: Rebuild covariance matrix
    # =========================================================================
    log.info("\n" + "=" * 70)
    log.info("PART 3: Rebuild Covariance Matrix")
    log.info("=" * 70)

    # --- Statistical covariance: bootstrap (same as build_covariance.py) ---
    log.info(f"  Statistical covariance ({N_TOYS_STAT} bootstrap toys)...")
    rng = np.random.default_rng(99999)
    stat_replicas = np.zeros((N_TOYS_STAT, N_BINS))

    for toy in range(N_TOYS_STAT):
        h_toy = rng.poisson(h_data).astype(float)
        unf_toy = ibu(h_toy, R, eff, prior_mc.copy(), NOMINAL_ITER)
        stat_replicas[toy] = normalize(unf_toy)
        if (toy + 1) % 100 == 0:
            log.info(f"    Bootstrap toy {toy + 1}/{N_TOYS_STAT}")

    cov_stat = np.cov(stat_replicas.T)
    log.info(f"  Stat cov diagonal range: "
             f"[{cov_stat.diagonal().min():.3e}, {cov_stat.diagonal().max():.3e}]")

    # --- Systematic covariance: outer products ---
    log.info("  Systematic covariance (outer products)...")
    syst = np.load(syst_file)

    syst_sources = [
        "shift_mom_smear",
        "shift_sel_missp",
        "shift_sel_eff",
        "shift_sel_tpc",
        "shift_calorimeter",
        "shift_background",
        "shift_regularization",
        "shift_prior_flat",
        "shift_alt_method",
        "shift_hadronization",
        "shift_isr",
        "shift_heavy_flavor",
        "shift_mc_statistics",
    ]

    cov_syst_total = np.zeros((N_BINS, N_BINS))
    cov_syst_per   = {}

    for key in syst_sources:
        if key in syst:
            delta = syst[key]
            if key == "shift_mc_statistics":
                cov_key = np.diag(delta**2)
            else:
                cov_key = np.outer(delta, delta)
            cov_syst_per[key] = cov_key
            cov_syst_total   += cov_key
            max_d = np.abs(np.diag(cov_key)).max()
            log.info(f"    {key}: max diagonal cov = {max_d:.3e}")
        else:
            log.warning(f"    {key} not found in systematics_shifts.npz — skipping")

    # --- Total covariance ---
    cov_total = cov_stat + cov_syst_total
    log.info(f"  Total covariance: max diagonal = {np.diag(cov_total).max():.3e}")

    # Validation
    eigenvalues_stat  = np.linalg.eigvalsh(cov_stat)
    eigenvalues_syst  = np.linalg.eigvalsh(cov_syst_total)
    eigenvalues_total = np.linalg.eigvalsh(cov_total)

    n_neg_total = (eigenvalues_total < -1e-12 * eigenvalues_total.max()).sum()
    log.info(f"  Total covariance negative eigenvalues: {n_neg_total}")
    if n_neg_total > 0:
        log.warning("  WARNING: negative eigenvalues — matrix may not be PSD")

    # Condition number (fit range)
    cov_fit = cov_total[np.ix_(FIT_MASK, FIT_MASK)]
    eigs_fit = np.linalg.eigvalsh(cov_fit)
    eigs_pos = eigs_fit[eigs_fit > 0]
    condition_number = eigs_pos.max() / eigs_pos.min() if len(eigs_pos) > 0 else np.inf
    log.info(f"  Condition number (fit range): {condition_number:.2e}")

    # Per-bin uncertainties
    sigma_tot  = np.sqrt(np.diag(cov_total))
    sigma_stat = np.sqrt(np.diag(cov_stat))
    sigma_syst = np.sqrt(np.diag(cov_syst_total))

    safe_nom = np.where(norm_nominal > 0, norm_nominal, 1.0)
    frac_tot  = sigma_tot  / safe_nom * 100
    frac_stat = sigma_stat / safe_nom * 100
    frac_syst = sigma_syst / safe_nom * 100

    log.info(f"  Max stat uncertainty (fit): {frac_stat[FIT_MASK].max():.2f}%")
    log.info(f"  Max syst uncertainty (fit): {frac_syst[FIT_MASK].max():.2f}%")
    log.info(f"  Max total uncertainty (fit): {frac_tot[FIT_MASK].max():.2f}%")

    # Correlation matrix
    diag_sqrt  = np.sqrt(np.maximum(np.diag(cov_total), 1e-20))
    corr_total = cov_total / np.outer(diag_sqrt, diag_sqrt)
    corr_total = np.clip(corr_total, -1.0, 1.0)

    # Save updated covariance matrices
    np.savez(
        P4_EXEC / "covariance_stat.npz",
        cov=cov_stat, replicas=stat_replicas,
        tau_edges=TAU_EDGES, tau_centers=TAU_CENTERS,
    )
    np.savez(
        P4_EXEC / "covariance_syst.npz",
        cov_total=cov_syst_total,
        **{k: v for k, v in cov_syst_per.items()},
        tau_edges=TAU_EDGES, tau_centers=TAU_CENTERS,
    )
    np.savez(
        P4_EXEC / "covariance_total.npz",
        cov=cov_total,
        cov_stat=cov_stat,
        cov_syst=cov_syst_total,
        corr=corr_total,
        eigenvalues=eigenvalues_total,
        condition_number=condition_number,
        sigma_tot=sigma_tot,
        sigma_stat=sigma_stat,
        sigma_syst=sigma_syst,
        tau_edges=TAU_EDGES, tau_centers=TAU_CENTERS,
        fit_mask=FIT_MASK,
    )
    log.info("  Saved updated covariance_stat.npz, covariance_syst.npz, covariance_total.npz")

    # Save fit-range covariance as CSV
    tau_fit   = TAU_CENTERS[FIT_MASK]
    header    = "tau_center," + ",".join(f"{t:.4f}" for t in tau_fit)
    rows      = []
    for i, t_row in enumerate(tau_fit):
        row_str = f"{t_row:.4f}," + ",".join(f"{cov_fit[i, j]:.6e}" for j in range(len(tau_fit)))
        rows.append(row_str)
    csv_path = P4_EXEC / "covariance_total_fitrange.csv"
    with open(csv_path, "w") as f:
        f.write(header + "\n")
        for row in rows:
            f.write(row + "\n")
    log.info(f"  Saved {csv_path}")

    # =========================================================================
    # PART 4: Update final result
    # =========================================================================
    log.info("\n" + "=" * 70)
    log.info("PART 4: Update Final Result")
    log.info("=" * 70)

    from scipy import stats as scipy_stats

    # MC truth
    h_gen_before = rm_data["h_gen_before"]
    mc_truth_norm = normalize(h_gen_before.astype(float))

    # Chi2 vs MC truth using updated covariance
    try:
        cov_fit_inv = np.linalg.inv(cov_fit)
    except np.linalg.LinAlgError:
        log.warning("  Covariance inversion failed; using diagonal-only")
        cov_fit_inv = np.diag(1.0 / np.diag(cov_fit))

    delta_fit   = norm_nominal[FIT_MASK] - mc_truth_norm[FIT_MASK]
    chi2_vs_mc  = float(delta_fit @ cov_fit_inv @ delta_fit)
    ndf_vs_mc   = N_FIT_BINS
    pval_vs_mc  = float(scipy_stats.chi2.sf(chi2_vs_mc, df=ndf_vs_mc))

    log.info(f"  Updated chi2 vs MC truth: {chi2_vs_mc:.1f}/{ndf_vs_mc} = {chi2_vs_mc/ndf_vs_mc:.3f}")
    log.info(f"  p-value: {pval_vs_mc:.4f}")

    # Save updated thrust_distribution.npz
    np.savez(
        RESULTS / "thrust_distribution.npz",
        tau_edges=TAU_EDGES,
        tau_centers=TAU_CENTERS,
        tau_bin_width=BIN_WIDTH,
        unfolded_norm=norm_nominal,
        unfolded_counts=unfolded_nominal,
        sigma_stat=sigma_stat,
        sigma_syst=sigma_syst,
        sigma_tot=sigma_tot,
        mc_truth_norm=mc_truth_norm,
        fit_mask=FIT_MASK,
        n_data_events=h_data.sum(),
        chi2_vs_mc=chi2_vs_mc,
        ndf_vs_mc=ndf_vs_mc,
        pval_vs_mc=pval_vs_mc,
        n_iterations=NOMINAL_ITER,
    )
    log.info(f"  Saved {RESULTS}/thrust_distribution.npz")

    # Save updated CSV
    csv_lines = [
        "# ALEPH Thrust Distribution -- (1/N)dN/dtau -- corrected for detector effects",
        "# Analysis: thrust_alphas, Phase 4a (updated after Category A fix)",
        "# tau_center, tau_lo, tau_hi, dNdtau, stat_unc, syst_unc, total_unc",
    ]
    for j in range(N_BINS):
        if FIT_MASK[j]:
            csv_lines.append(
                f"{TAU_CENTERS[j]:.4f},"
                f"{TAU_EDGES[j]:.4f},"
                f"{TAU_EDGES[j+1]:.4f},"
                f"{norm_nominal[j]:.6e},"
                f"{sigma_stat[j]:.6e},"
                f"{sigma_syst[j]:.6e},"
                f"{sigma_tot[j]:.6e}"
            )
    with open(RESULTS / "thrust_distribution.csv", "w") as f:
        f.write("\n".join(csv_lines) + "\n")
    log.info(f"  Saved {RESULTS}/thrust_distribution.csv")

    # =========================================================================
    # PART 5: Figures
    # =========================================================================
    log.info("\n" + "=" * 70)
    log.info("PART 5: Producing Figures")
    log.info("=" * 70)

    mh.style.use("CMS")

    # Fig 1: Hadronization systematic — old vs new
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    ax1.stairs(np.abs(old_hadr_shift) * 100, TAU_EDGES,
               color="tab:blue", linewidth=2.0, linestyle="--",
               label="Hadronization (old: prior-change, ~0%)")
    ax1.stairs(hadronization_floor * 100, TAU_EDGES,
               color="tab:red", linewidth=2.5, linestyle="-",
               label=r"Hadronization (new: 2% floor, conservative)")
    ax1.axvspan(0.05, 0.30, alpha=0.05, color="green")
    ax1.set_xlabel(r"$\tau = 1 - T$", fontsize=14)
    ax1.set_ylabel(r"$|\Delta(1/N\,dN/d\tau)|$ (%)", fontsize=14)
    ax1.set_xlim(0.0, 0.45)
    ax1.legend(fontsize="x-small")
    mh.label.exp_label(exp="ALEPH", data=False, rlabel=r"$\sqrt{s} = 91.2$ GeV", ax=ax1)
    for fmt in ("pdf", "png"):
        fig1.savefig(FIG_DIR / f"syst_hadronization_floor.{fmt}",
                     bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig1)
    log.info("  Saved syst_hadronization_floor.{pdf,png}")

    # Fig 2: Updated uncertainty breakdown
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    ax2.stairs(frac_stat, TAU_EDGES, color="tab:blue", linewidth=2.0, label="Statistical")
    ax2.stairs(frac_syst, TAU_EDGES, color="tab:red",  linewidth=2.0,
               linestyle="--", label="Systematic (updated)")
    ax2.stairs(frac_tot,  TAU_EDGES, color="black",    linewidth=2.0, label="Total (updated)")
    ax2.axvspan(0.05, 0.30, alpha=0.05, color="green")
    ax2.set_xlabel(r"$\tau = 1 - T$", fontsize=14)
    ax2.set_ylabel("Fractional uncertainty (%)", fontsize=14)
    ax2.set_xlim(0.0, 0.45)
    ax2.legend(fontsize="x-small")
    mh.label.exp_label(exp="ALEPH", data=False, rlabel=r"$\sqrt{s} = 91.2$ GeV", ax=ax2)
    for fmt in ("pdf", "png"):
        fig2.savefig(FIG_DIR / f"cov_uncertainty_breakdown_updated.{fmt}",
                     bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig2)
    log.info("  Saved cov_uncertainty_breakdown_updated.{pdf,png}")

    # Fig 3: Updated correlation matrix
    fig3, ax3 = plt.subplots(figsize=(10, 8))
    im = ax3.imshow(corr_total, vmin=-1, vmax=1, cmap="RdBu_r",
                    origin="lower", aspect="auto",
                    extent=[TAU_MIN, TAU_MAX, TAU_MIN, TAU_MAX])
    plt.colorbar(im, ax=ax3, label=r"Correlation $\rho_{ij}$")
    ax3.set_xlabel(r"$\tau_j$", fontsize=14)
    ax3.set_ylabel(r"$\tau_i$", fontsize=14)
    for line_val in [0.05, 0.30]:
        ax3.axvline(line_val, color="gray", linestyle="--", linewidth=1.0)
        ax3.axhline(line_val, color="gray", linestyle="--", linewidth=1.0)
    mh.label.exp_label(exp="ALEPH", data=False, rlabel=r"$\sqrt{s} = 91.2$ GeV", ax=ax3)
    for fmt in ("pdf", "png"):
        fig3.savefig(FIG_DIR / f"cov_correlation_updated.{fmt}",
                     bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig3)
    log.info("  Saved cov_correlation_updated.{pdf,png}")

    # =========================================================================
    # Summary
    # =========================================================================
    log.info("\n" + "=" * 70)
    log.info("SUMMARY")
    log.info("=" * 70)

    table = Table(title="Category A Fix Summary", show_header=True)
    table.add_column("Issue", max_width=35)
    table.add_column("Status", justify="center")
    table.add_column("Details")

    stress_status = "FIXED" if stress_passed else "FAILED"
    table.add_row(
        "Stress test (missing)",
        stress_status,
        f"chi2/ndf = {nominal_chi2:.2f}/{nominal_ndf} = {nominal_chi2/nominal_ndf:.3f}",
    )
    table.add_row(
        "Hadronization syst (~0%)",
        "FIXED",
        f"Old: ~0%, New: {HADRONIZATION_FLOOR_FRACTION*100:.0f}% per bin (conservative floor)",
    )
    table.add_row(
        "Covariance matrix",
        "REBUILT",
        f"Max syst unc (fit): {frac_syst[FIT_MASK].max():.2f}%",
    )
    table.add_row(
        "Final result",
        "UPDATED",
        f"chi2 vs MC: {chi2_vs_mc:.1f}/{ndf_vs_mc}, max total unc: {frac_tot[FIT_MASK].max():.2f}%",
    )
    console.print(table)

    log.info("\n[bold green]fix_systematics.py complete[/bold green]")


if __name__ == "__main__":
    main()
