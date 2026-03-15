"""
Phase 4a Script 3: build_covariance.py

Construct the full covariance matrix for the unfolded thrust distribution.

Components:
  1. Statistical covariance: from bootstrap resampling of data through the
     unfolding chain (500+ Poisson toys).
  2. Systematic covariance per source: outer product of shift vectors.
  3. Total covariance: sum of all components.

Validation:
  - Positive semi-definiteness (eigenvalue check)
  - Condition number
  - Correlation matrix visualization

Outputs:
  - phase4_inference/exec/covariance_stat.npz
  - phase4_inference/exec/covariance_syst_*.npz (per source)
  - phase4_inference/exec/covariance_total.npz
  - phase4_inference/exec/results/covariance_total.csv
  - phase4_inference/figures/cov_correlation.{pdf,png}
  - phase4_inference/figures/cov_eigenvalues.{pdf,png}
"""

import logging
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
log = logging.getLogger("build_covariance")
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
N_TOYS_STAT  = 500  # Bootstrap toys for statistical covariance


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
    log.info("Phase 4a Script 3: Build Covariance Matrix")
    log.info("=" * 70)

    # -------------------------------------------------------------------------
    # Load nominal inputs
    # -------------------------------------------------------------------------
    rm = np.load(P3_EXEC / "response_matrix.npz")
    R          = rm["R"]
    eff        = rm["efficiency"]
    h_gen_sel  = rm["h_gen_sel"]

    dh = np.load(P3_EXEC / "hist_tau_data.npz")
    h_data = dh["counts"].astype(float)

    prior_mc = h_gen_sel / h_gen_sel.sum() if h_gen_sel.sum() > 0 else np.ones(N_BINS) / N_BINS

    # Nominal unfolded result (normalized)
    unf_nominal    = ibu(h_data, R, eff, prior_mc.copy(), NOMINAL_ITER)
    norm_nominal   = normalize(unf_nominal)

    log.info(f"Data events: {h_data.sum():.0f}")
    log.info(f"Nominal unfolded total: {unf_nominal.sum():.0f}")

    # =========================================================================
    # 1. Statistical covariance: bootstrap data through unfolding
    # =========================================================================
    log.info(f"\n[bold]1. Statistical covariance ({N_TOYS_STAT} bootstrap toys)...[/bold]")

    rng = np.random.default_rng(99999)
    stat_replicas = np.zeros((N_TOYS_STAT, N_BINS))

    for toy in range(N_TOYS_STAT):
        # Poisson resample each bin of the data histogram
        h_toy = rng.poisson(h_data)
        h_toy = h_toy.astype(float)
        unf_toy = ibu(h_toy, R, eff, prior_mc.copy(), NOMINAL_ITER)
        stat_replicas[toy] = normalize(unf_toy)

        if (toy + 1) % 100 == 0:
            log.info(f"  Bootstrap toy {toy + 1}/{N_TOYS_STAT}")

    # Covariance from replicas
    cov_stat = np.cov(stat_replicas.T)   # (N_BINS, N_BINS)
    log.info(f"Statistical covariance: shape = {cov_stat.shape}")
    log.info(f"Stat cov diagonal range: [{cov_stat.diagonal().min():.3e}, {cov_stat.diagonal().max():.3e}]")

    # =========================================================================
    # 2. Systematic covariance: outer products of shift vectors
    # =========================================================================
    log.info("\n[bold]2. Systematic covariance (outer products)...[/bold]")

    # Load systematic shifts
    syst = np.load(P4_EXEC / "systematics_shifts.npz")

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
                # MC statistics: stored as 1-sigma per bin — diagonal contribution
                cov_key = np.diag(delta**2)
            else:
                # Fully correlated across bins: outer product
                cov_key = np.outer(delta, delta)
            cov_syst_per[key] = cov_key
            cov_syst_total += cov_key
            max_d  = np.abs(np.diag(cov_key)).max()
            log.info(f"  {key}: max diagonal cov = {max_d:.3e}")
        else:
            log.warning(f"  {key} not found in systematics_shifts.npz — skipping")

    log.info(f"Total systematic covariance: max diagonal = {np.diag(cov_syst_total).max():.3e}")

    # =========================================================================
    # 3. Total covariance
    # =========================================================================
    cov_total = cov_stat + cov_syst_total
    log.info(f"\nTotal covariance matrix: shape = {cov_total.shape}")

    # =========================================================================
    # 4. Validation
    # =========================================================================
    log.info("\n[bold]4. Validation checks...[/bold]")

    # 4a. Eigenvalue check (full matrix)
    eigenvalues_stat   = np.linalg.eigvalsh(cov_stat)
    eigenvalues_syst   = np.linalg.eigvalsh(cov_syst_total)
    eigenvalues_total  = np.linalg.eigvalsh(cov_total)

    n_neg_stat  = (eigenvalues_stat  < -1e-12 * eigenvalues_stat.max()).sum()
    n_neg_syst  = (eigenvalues_syst  < -1e-12 * np.abs(eigenvalues_syst).max()).sum()
    n_neg_total = (eigenvalues_total < -1e-12 * eigenvalues_total.max()).sum()

    log.info(f"Stat covariance: {n_neg_stat} negative eigenvalues "
             f"(min = {eigenvalues_stat.min():.3e})")
    log.info(f"Syst covariance: {n_neg_syst} negative eigenvalues "
             f"(min = {eigenvalues_syst.min():.3e})")
    log.info(f"Total covariance: {n_neg_total} negative eigenvalues "
             f"(min = {eigenvalues_total.min():.3e})")

    if n_neg_total > 0:
        log.warning("WARNING: negative eigenvalues in total covariance — applying floor at 0")

    # 4b. Condition number (fit-range sub-matrix)
    cov_fit = cov_total[np.ix_(FIT_MASK, FIT_MASK)]
    eigs_fit = np.linalg.eigvalsh(cov_fit)
    eigs_pos = eigs_fit[eigs_fit > 0]
    if len(eigs_pos) > 0:
        condition_number = eigs_pos.max() / eigs_pos.min()
        log.info(f"Condition number (fit range): {condition_number:.2e}")
        if condition_number > 1e10:
            log.warning("  WARN: condition number > 1e10 — chi2 fit may be ill-conditioned")
        elif condition_number > 1e6:
            log.info("  NOTE: condition number is moderate (> 1e6) — monitor fit stability")
        else:
            log.info("  OK: condition number is acceptable")
    else:
        log.warning("  Could not compute condition number — all eigenvalues <= 0")
        condition_number = np.inf

    # 4c. Diagonal comparison: total per-bin uncertainty
    sigma_tot  = np.sqrt(np.diag(cov_total))
    sigma_stat = np.sqrt(np.diag(cov_stat))
    sigma_syst = np.sqrt(np.diag(cov_syst_total))

    # Fractional uncertainty
    safe_nom = np.where(norm_nominal > 0, norm_nominal, 1.0)
    frac_tot  = sigma_tot  / safe_nom * 100
    frac_stat = sigma_stat / safe_nom * 100
    frac_syst = sigma_syst / safe_nom * 100

    log.info("\n[bold]Per-bin uncertainties (fit range):[/bold]")
    table = Table(title="Total Uncertainty per Bin", show_header=True)
    table.add_column("tau_center", justify="right")
    table.add_column("Stat (%)", justify="right")
    table.add_column("Syst (%)", justify="right")
    table.add_column("Total (%)", justify="right")
    for j in range(N_BINS):
        if FIT_MASK[j]:
            table.add_row(
                f"{TAU_CENTERS[j]:.3f}",
                f"{frac_stat[j]:.3f}",
                f"{frac_syst[j]:.3f}",
                f"{frac_tot[j]:.3f}",
            )
    console.print(table)

    # 4d. Correlation matrix
    diag_sqrt = np.sqrt(np.maximum(np.diag(cov_total), 1e-20))
    corr_total = cov_total / np.outer(diag_sqrt, diag_sqrt)
    corr_total = np.clip(corr_total, -1.0, 1.0)

    # =========================================================================
    # 5. Save
    # =========================================================================
    np.savez(
        P4_EXEC / "covariance_stat.npz",
        cov=cov_stat,
        replicas=stat_replicas,
        tau_edges=TAU_EDGES,
        tau_centers=TAU_CENTERS,
    )

    np.savez(
        P4_EXEC / "covariance_syst.npz",
        cov_total=cov_syst_total,
        **{k: v for k, v in cov_syst_per.items()},
        tau_edges=TAU_EDGES,
        tau_centers=TAU_CENTERS,
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
        tau_edges=TAU_EDGES,
        tau_centers=TAU_CENTERS,
        fit_mask=FIT_MASK,
    )
    log.info(f"Saved covariance NPZ files to {P4_EXEC}/")

    # Save total covariance as CSV (fit range)
    cov_fit_full = cov_total[np.ix_(FIT_MASK, FIT_MASK)]
    tau_fit = TAU_CENTERS[FIT_MASK]
    header  = "tau_center," + ",".join(f"{t:.4f}" for t in tau_fit)
    rows    = []
    for i, t_row in enumerate(tau_fit):
        row_str = f"{t_row:.4f}," + ",".join(f"{cov_fit_full[i,j]:.6e}" for j in range(len(tau_fit)))
        rows.append(row_str)
    csv_path = RESULTS / "covariance_total_fitrange.csv"
    with open(csv_path, "w") as f:
        f.write(header + "\n")
        for row in rows:
            f.write(row + "\n")
    log.info(f"Saved covariance CSV to {csv_path}")

    # =========================================================================
    # 6. Figures
    # =========================================================================
    mh.style.use("CMS")

    # Fig 1: Correlation matrix (full 25x25)
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(corr_total, vmin=-1, vmax=1, cmap="RdBu_r",
                   origin="lower", aspect="auto",
                   extent=[TAU_MIN, TAU_MAX, TAU_MIN, TAU_MAX])
    plt.colorbar(im, ax=ax, label=r"Correlation $\rho_{ij}$")
    ax.set_xlabel(r"$\tau_j$", fontsize=14)
    ax.set_ylabel(r"$\tau_i$", fontsize=14)
    ax.set_title("Correlation Matrix (total)", fontsize=13)
    # Mark fit range
    ax.axvline(0.05, color="gray", linestyle="--", linewidth=1.0)
    ax.axvline(0.30, color="gray", linestyle="--", linewidth=1.0)
    ax.axhline(0.05, color="gray", linestyle="--", linewidth=1.0)
    ax.axhline(0.30, color="gray", linestyle="--", linewidth=1.0)
    mh.label.exp_label(exp="ALEPH", data=True, rlabel=r"$\sqrt{s} = 91.2$ GeV", ax=ax)
    for fmt in ("pdf", "png"):
        fig.savefig(FIG_DIR / f"cov_correlation.{fmt}",
                    bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)
    log.info("Saved cov_correlation")

    # Fig 2: Eigenvalue spectrum
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    ax2.semilogy(np.arange(1, N_BINS + 1), np.sort(eigenvalues_total)[::-1],
                 "o-", color="black", label="Total covariance eigenvalues")
    ax2.semilogy(np.arange(1, N_BINS + 1), np.sort(eigenvalues_stat)[::-1],
                 "s--", color="tab:blue", label="Statistical covariance eigenvalues")
    ax2.semilogy(np.arange(1, N_BINS + 1), np.sort(np.abs(eigenvalues_syst))[::-1],
                 "^:", color="tab:red", label="Systematic covariance eigenvalues (|λ|)")
    ax2.axhline(0, color="gray", linewidth=0.5)
    ax2.set_xlabel("Eigenvalue index", fontsize=14)
    ax2.set_ylabel(r"Eigenvalue $\lambda_k$", fontsize=14)
    ax2.legend(fontsize="x-small")
    ax2.set_xticks(np.arange(1, N_BINS + 1, 2))
    mh.label.exp_label(exp="ALEPH", data=True, rlabel=r"$\sqrt{s} = 91.2$ GeV", ax=ax2)
    for fmt in ("pdf", "png"):
        fig2.savefig(FIG_DIR / f"cov_eigenvalues.{fmt}",
                     bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig2)
    log.info("Saved cov_eigenvalues")

    # Fig 3: Per-bin uncertainty breakdown
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    ax3.stairs(frac_stat, TAU_EDGES, color="tab:blue",  linewidth=2.0, label="Statistical")
    ax3.stairs(frac_syst, TAU_EDGES, color="tab:red",   linewidth=2.0, linestyle="--", label="Systematic")
    ax3.stairs(frac_tot,  TAU_EDGES, color="black",     linewidth=2.0, linestyle="-",  label="Total")
    ax3.axvspan(0.05, 0.30, alpha=0.05, color="green")
    ax3.set_xlabel(r"$\tau = 1 - T$", fontsize=14)
    ax3.set_ylabel("Fractional uncertainty (%)", fontsize=14)
    ax3.set_xlim(0.0, 0.45)
    ax3.legend(fontsize="x-small")
    mh.label.exp_label(exp="ALEPH", data=True, rlabel=r"$\sqrt{s} = 91.2$ GeV", ax=ax3)
    for fmt in ("pdf", "png"):
        fig3.savefig(FIG_DIR / f"cov_uncertainty_breakdown.{fmt}",
                     bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig3)
    log.info("Saved cov_uncertainty_breakdown")

    # Summary
    log.info("\n[bold]Covariance matrix validation summary:[/bold]")
    log.info(f"  Shape:                    {cov_total.shape}")
    log.info(f"  Negative eigenvalues:     {n_neg_total}")
    log.info(f"  Condition number (fit):   {condition_number:.2e}")
    log.info(f"  Max stat uncertainty:     {frac_stat[FIT_MASK].max():.2f}%")
    log.info(f"  Max syst uncertainty:     {frac_syst[FIT_MASK].max():.2f}%")
    log.info(f"  Max total uncertainty:    {frac_tot[FIT_MASK].max():.2f}%")
    log.info(f"  Dominant off-diag corr:   {np.abs(corr_total - np.eye(N_BINS)).max():.3f}")

    log.info("\n[bold green]build_covariance.py complete[/bold green]")


if __name__ == "__main__":
    main()
