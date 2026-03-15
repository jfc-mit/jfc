"""
Phase 3 Script 3: run_closure.py

Implement iterative Bayesian unfolding (IBU / D'Agostini method).

Tests performed:
  1. Closure test: unfold MC reco through the response matrix, compare to MC gen truth.
  2. Stress test: reweight MC truth by a linear tilt, propagate through detector
     simulation (apply the response matrix forward), unfold, compare to reweighted truth.
  3. Iteration scan: chi2/ndf for closure and stress vs. number of iterations (1-10).
  4. Flat-prior sensitivity test: unfold data with flat prior vs. MC prior; flag bins
     where the shift exceeds 20% (per conventions).

Inputs (from build_response.py outputs):
  - phase3_selection/exec/response_matrix.npz
  - phase3_selection/exec/hist_tau_mc_reco.npz
  - phase3_selection/exec/hist_tau_mc_gen.npz
  - phase3_selection/exec/hist_tau_data.npz  (for flat-prior test)

Outputs:
  - phase3_selection/exec/closure_results.npz
  - phase3_selection/figures/closure_*.{pdf,png}
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
log = logging.getLogger("run_closure")
console = Console()

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
OUT_DIR = Path("phase3_selection/exec")
FIG_DIR = Path("phase3_selection/figures")
OUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Tau binning (must match apply_selection + build_response)
N_BINS    = 25
TAU_MIN   = 0.0
TAU_MAX   = 0.5
TAU_EDGES   = np.linspace(TAU_MIN, TAU_MAX, N_BINS + 1)
TAU_CENTERS = 0.5 * (TAU_EDGES[:-1] + TAU_EDGES[1:])

# Number of IBU iterations to scan
N_ITER_MAX = 10

# Fit range for chi2 evaluation: tau in [0.05, 0.30]
FIT_MASK = (TAU_CENTERS >= 0.05) & (TAU_CENTERS <= 0.30)


# ---------------------------------------------------------------------------
# IBU algorithm
# ---------------------------------------------------------------------------

def ibu(data_reco: np.ndarray,
        R: np.ndarray,
        efficiency: np.ndarray,
        prior: np.ndarray,
        n_iter: int) -> np.ndarray:
    """
    Iterative Bayesian Unfolding (D'Agostini method).

    Parameters
    ----------
    data_reco : (N_reco,) array — observed detector-level counts
    R         : (N_reco, N_gen) response matrix — P(reco bin i | gen bin j)
    efficiency: (N_gen,) array — reco efficiency per gen bin
    prior     : (N_gen,) normalized prior (sum to 1 or proportional)
    n_iter    : number of iterations

    Returns
    -------
    unfolded : (N_gen,) array — unfolded counts (NOT normalized, NOT efficiency-corrected)
    """
    n_reco, n_gen = R.shape
    # Normalize prior
    prior = prior / prior.sum() if prior.sum() > 0 else np.ones(n_gen) / n_gen

    for _ in range(n_iter):
        # E-step: U[j,i] = R[i,j] * prior[j] / sum_k( R[i,k]*prior[k] )
        # Denominator for each reco bin i
        denom = R @ prior           # (N_reco,) — sum_k R[i,k]*prior[k]
        safe_denom = np.where(denom > 0, denom, 1.0)
        # U[j,i] = R[i,j] * prior[j] / denom[i]   → shape (N_gen, N_reco)
        U = (R * prior[np.newaxis, :]).T / safe_denom[:, np.newaxis]
        # Transpose to (N_gen, N_reco)
        U = U.T    # shape (N_gen, N_reco)

        # M-step: unfolded[j] = sum_i U[j,i] * data[i] / efficiency[j]
        unfolded = U @ data_reco   # (N_gen,)
        safe_eff = np.where(efficiency > 0, efficiency, 1.0)
        unfolded = unfolded / safe_eff

        # Update prior (normalized)
        if unfolded.sum() > 0:
            prior = unfolded / unfolded.sum()
        else:
            prior = np.ones(n_gen) / n_gen

    return unfolded


def chi2_ndf(y_unfolded: np.ndarray,
             y_truth: np.ndarray,
             mask: np.ndarray) -> tuple[float, int]:
    """
    Compute chi2/ndf between unfolded and truth using Poisson-like uncertainties.
    Uncertainty on truth assumed from MC counting statistics (sqrt(N)).
    """
    y_u = y_unfolded[mask]
    y_t = y_truth[mask]
    # Normalize both to same total (shape comparison)
    if y_u.sum() > 0:
        y_u = y_u / y_u.sum() * y_t.sum()
    unc = np.sqrt(np.maximum(y_t, 1.0))
    chi2 = np.sum(((y_u - y_t) / unc) ** 2)
    ndf = int(mask.sum())
    return float(chi2), ndf


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    log.info("=" * 70)
    log.info("Phase 3 Script 3: Closure and Stress Tests (IBU)")
    log.info("=" * 70)

    # Load response matrix
    rm = np.load(OUT_DIR / "response_matrix.npz")
    R          = rm["R"]           # (N_reco, N_gen)
    efficiency = rm["efficiency"]  # per gen bin
    h_gen_before = rm["h_gen_before"]   # generator-level truth (tgenBefore)
    h_gen_sel    = rm["h_gen_sel"]      # generator-level matched to reco
    h_reco_sel   = rm["h_reco_sel"]     # reco level

    # Load data tau histogram
    dh = np.load(OUT_DIR / "hist_tau_data.npz")
    h_data = dh["counts"].astype(float)

    log.info(f"Response matrix shape: {R.shape}")
    log.info(f"Total MC reco events in matrix: {h_reco_sel.sum():.0f}")
    log.info(f"Total tgenBefore events: {h_gen_before.sum():.0f}")

    # ------------------------------------------------------------------
    # 1. CLOSURE TEST
    # ------------------------------------------------------------------
    log.info("\n[bold]--- Closure Test ---[/bold]")
    # Input: MC reco histogram. Truth: MC gen histogram (matched tgen).
    # Prior: uniform (flat).
    mc_reco_input = h_reco_sel.copy().astype(float)
    mc_truth      = h_gen_sel.copy().astype(float)   # matched gen (should close to this)
    prior_flat    = np.ones(N_BINS)

    closure_chi2  = []
    closure_ndf   = []
    closure_unfolded_iter = {}

    for n_iter in range(1, N_ITER_MAX + 1):
        unfolded = ibu(mc_reco_input, R, efficiency, prior_flat.copy(), n_iter)
        c2, ndf = chi2_ndf(unfolded, mc_truth, FIT_MASK)
        closure_chi2.append(c2)
        closure_ndf.append(ndf)
        closure_unfolded_iter[n_iter] = unfolded.copy()
        log.info(f"  Iter {n_iter:2d}: chi2/ndf = {c2/ndf:.3f} ({c2:.1f}/{ndf})")

    closure_chi2_per_ndf = [c / n for c, n in zip(closure_chi2, closure_ndf)]

    # ------------------------------------------------------------------
    # 2. STRESS TEST
    # ------------------------------------------------------------------
    log.info("\n[bold]--- Stress Test ---[/bold]")
    # Reweight truth by a linear function w(tau) = 1 + 2*tau (tilted toward large tau)
    weights = 1.0 + 2.0 * TAU_CENTERS
    mc_truth_reweighted = mc_truth * weights
    # Propagate reweighted truth through response matrix to get "alternative reco"
    # Forward fold: h_reco_alt[i] = sum_j R[i,j] * efficiency[j] * mc_truth_rw[j]
    mc_reco_alt = R @ (mc_truth_reweighted * efficiency)

    stress_chi2 = []
    stress_ndf  = []
    stress_unfolded_iter = {}

    for n_iter in range(1, N_ITER_MAX + 1):
        unfolded = ibu(mc_reco_alt, R, efficiency, prior_flat.copy(), n_iter)
        c2, ndf = chi2_ndf(unfolded, mc_truth_reweighted, FIT_MASK)
        stress_chi2.append(c2)
        stress_ndf.append(ndf)
        stress_unfolded_iter[n_iter] = unfolded.copy()
        log.info(f"  Iter {n_iter:2d}: chi2/ndf = {c2/ndf:.3f} ({c2:.1f}/{ndf})")

    stress_chi2_per_ndf = [c / n for c, n in zip(stress_chi2, stress_ndf)]

    # ------------------------------------------------------------------
    # Determine optimal number of iterations
    # ------------------------------------------------------------------
    # Select iteration where closure chi2/ndf stops improving significantly
    # (plateau criterion: less than 5% improvement from n-1 to n)
    optimal_iter = 1
    for n in range(2, N_ITER_MAX + 1):
        prev = closure_chi2_per_ndf[n - 2]
        curr = closure_chi2_per_ndf[n - 1]
        if prev > 0 and abs(prev - curr) / prev < 0.05:
            optimal_iter = n - 1
            break
        optimal_iter = n

    log.info(f"\n[bold]Optimal number of iterations: {optimal_iter}[/bold]")
    log.info(f"  Closure chi2/ndf at optimal: {closure_chi2_per_ndf[optimal_iter-1]:.3f}")
    log.info(f"  Stress  chi2/ndf at optimal: {stress_chi2_per_ndf[optimal_iter-1]:.3f}")

    # ------------------------------------------------------------------
    # 3. FLAT-PRIOR SENSITIVITY TEST (per conventions)
    # ------------------------------------------------------------------
    log.info("\n[bold]--- Flat-Prior Sensitivity Test ---[/bold]")
    # Unfold the data with the nominal prior (MC truth) and with a flat prior.
    # Flag bins where the shift exceeds 20% relative.
    prior_mc   = mc_truth / mc_truth.sum()
    prior_flat = np.ones(N_BINS) / N_BINS

    unfolded_nominal = ibu(h_data, R, efficiency, prior_mc.copy(),   optimal_iter)
    unfolded_flat    = ibu(h_data, R, efficiency, prior_flat.copy(), optimal_iter)

    # Relative shift per bin
    safe_nom = np.where(unfolded_nominal > 0, unfolded_nominal, 1.0)
    rel_shift = np.abs(unfolded_flat - unfolded_nominal) / safe_nom
    flagged = rel_shift > 0.20

    table = Table(title=f"Flat-Prior Sensitivity (iter={optimal_iter})", show_header=True)
    table.add_column("tau bin", justify="right")
    table.add_column("Nominal", justify="right")
    table.add_column("Flat prior", justify="right")
    table.add_column("Rel. shift", justify="right")
    table.add_column("Flag (>20%)", justify="center")
    for j in range(N_BINS):
        table.add_row(
            f"{TAU_CENTERS[j]:.3f}",
            f"{unfolded_nominal[j]:.1f}",
            f"{unfolded_flat[j]:.1f}",
            f"{rel_shift[j]*100:.1f}%",
            "[red]YES[/red]" if flagged[j] else "OK",
        )
    console.print(table)
    log.info(f"Bins flagged (>20% flat-prior shift): {flagged.sum()}")

    # ------------------------------------------------------------------
    # Save all results
    # ------------------------------------------------------------------
    np.savez(
        OUT_DIR / "closure_results.npz",
        # Iteration scan
        n_iters=np.arange(1, N_ITER_MAX + 1),
        closure_chi2=np.array(closure_chi2),
        closure_ndf=np.array(closure_ndf),
        closure_chi2_per_ndf=np.array(closure_chi2_per_ndf),
        stress_chi2=np.array(stress_chi2),
        stress_ndf=np.array(stress_ndf),
        stress_chi2_per_ndf=np.array(stress_chi2_per_ndf),
        optimal_iter=optimal_iter,
        # At optimal iteration
        closure_unfolded=closure_unfolded_iter[optimal_iter],
        stress_unfolded=stress_unfolded_iter[optimal_iter],
        mc_truth=mc_truth,
        mc_truth_reweighted=mc_truth_reweighted,
        mc_reco_input=mc_reco_input,
        # Flat-prior sensitivity
        unfolded_nominal=unfolded_nominal,
        unfolded_flat=unfolded_flat,
        rel_shift=rel_shift,
        flagged=flagged,
        # Metadata
        tau_centers=TAU_CENTERS,
        tau_edges=TAU_EDGES,
        fit_mask=FIT_MASK,
    )
    log.info("Saved closure_results.npz")

    # ------------------------------------------------------------------
    # Figures
    # ------------------------------------------------------------------
    mh.style.use("CMS")

    # Fig 1: chi2/ndf vs iterations (closure + stress)
    fig, ax = plt.subplots(figsize=(10, 6))
    iters = np.arange(1, N_ITER_MAX + 1)
    ax.plot(iters, closure_chi2_per_ndf, "o-", color="black",  label="Closure test")
    ax.plot(iters, stress_chi2_per_ndf,  "s--", color="tab:red", label="Stress test")
    ax.axvline(optimal_iter, color="gray", linestyle=":", linewidth=1.5,
               label=f"Optimal = {optimal_iter}")
    ax.axhline(1.0, color="green", linestyle="--", linewidth=1.0, label=r"$\chi^2/\mathrm{ndf}=1$")
    ax.set_xlabel("Number of IBU iterations", fontsize=14)
    ax.set_ylabel(r"$\chi^2/\mathrm{ndf}$", fontsize=14)
    ax.set_xticks(iters)
    ax.legend(fontsize="x-small")
    mh.label.exp_label(exp="ALEPH", data=False, rlabel=r"Pythia 6.1 MC", ax=ax)
    fig.savefig(FIG_DIR / "closure_chi2_vs_iter.pdf", bbox_inches="tight", dpi=200, transparent=True)
    fig.savefig(FIG_DIR / "closure_chi2_vs_iter.png", bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)
    log.info("Saved closure_chi2_vs_iter figure")

    # Fig 2: Closure test at optimal iteration (unfolded vs truth)
    unf_opt = closure_unfolded_iter[optimal_iter]
    # Normalize for shape comparison
    scale = mc_truth.sum() / unf_opt.sum() if unf_opt.sum() > 0 else 1.0
    unf_opt_norm = unf_opt * scale

    ratio_closure = np.where(mc_truth > 0, unf_opt_norm / mc_truth, np.nan)

    fig2, (ax2, rax2) = plt.subplots(
        2, 1, figsize=(10, 10),
        gridspec_kw={"height_ratios": [3, 1]}, sharex=True,
    )
    fig2.subplots_adjust(hspace=0.0)
    bw = TAU_EDGES[1] - TAU_EDGES[0]
    norm_truth = mc_truth / (mc_truth.sum() * bw)
    norm_unf   = unf_opt_norm / (mc_truth.sum() * bw)

    ax2.stairs(norm_truth, TAU_EDGES, color="black",   linewidth=1.5, label="MC truth (gen)")
    ax2.stairs(norm_unf,   TAU_EDGES, color="tab:red", linewidth=1.5, linestyle="--",
               label=f"Unfolded MC reco (iter={optimal_iter})")
    ax2.set_ylabel(r"$(1/N)\,dN/d\tau$", fontsize=14)
    ax2.set_yscale("log")
    ax2.legend(fontsize="x-small")
    mh.label.exp_label(exp="ALEPH", data=False, rlabel=r"Pythia 6.1 MC", ax=ax2)

    rax2.axhline(1.0, color="gray", linewidth=1.0)
    rax2.stairs(ratio_closure, TAU_EDGES, color="black", linewidth=1.5)
    rax2.set_xlabel(r"$\tau = 1 - T$", fontsize=14)
    rax2.set_ylabel("Unfolded / Truth", fontsize=12)
    rax2.set_ylim(0.8, 1.2)
    rax2.set_xlim(TAU_MIN, TAU_MAX)

    fig2.savefig(FIG_DIR / "closure_test.pdf", bbox_inches="tight", dpi=200, transparent=True)
    fig2.savefig(FIG_DIR / "closure_test.png", bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig2)
    log.info("Saved closure_test figure")

    # Fig 3: Stress test at optimal iteration
    unf_str = stress_unfolded_iter[optimal_iter]
    scale_s = mc_truth_reweighted.sum() / unf_str.sum() if unf_str.sum() > 0 else 1.0
    unf_str_norm = unf_str * scale_s

    ratio_stress = np.where(mc_truth_reweighted > 0, unf_str_norm / mc_truth_reweighted, np.nan)

    fig3, (ax3, rax3) = plt.subplots(
        2, 1, figsize=(10, 10),
        gridspec_kw={"height_ratios": [3, 1]}, sharex=True,
    )
    fig3.subplots_adjust(hspace=0.0)
    norm_rw  = mc_truth_reweighted / (mc_truth_reweighted.sum() * bw)
    norm_us  = unf_str_norm / (mc_truth_reweighted.sum() * bw)

    ax3.stairs(norm_rw, TAU_EDGES, color="black",   linewidth=1.5, label="Reweighted MC truth")
    ax3.stairs(norm_us, TAU_EDGES, color="tab:red", linewidth=1.5, linestyle="--",
               label=f"Unfolded reweighted reco (iter={optimal_iter})")
    ax3.set_ylabel(r"$(1/N)\,dN/d\tau$", fontsize=14)
    ax3.set_yscale("log")
    ax3.legend(fontsize="x-small")
    mh.label.exp_label(exp="ALEPH", data=False, rlabel=r"Pythia 6.1 MC", ax=ax3)

    rax3.axhline(1.0, color="gray", linewidth=1.0)
    rax3.stairs(ratio_stress, TAU_EDGES, color="black", linewidth=1.5)
    rax3.set_xlabel(r"$\tau = 1 - T$", fontsize=14)
    rax3.set_ylabel("Unfolded / Truth", fontsize=12)
    rax3.set_ylim(0.8, 1.2)
    rax3.set_xlim(TAU_MIN, TAU_MAX)

    fig3.savefig(FIG_DIR / "stress_test.pdf", bbox_inches="tight", dpi=200, transparent=True)
    fig3.savefig(FIG_DIR / "stress_test.png", bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig3)
    log.info("Saved stress_test figure")

    # Fig 4: Flat-prior sensitivity per bin
    fig4, ax4 = plt.subplots(figsize=(10, 6))
    ax4.step(TAU_EDGES[:-1], rel_shift * 100, where="post", color="black", linewidth=1.5)
    ax4.axhline(20.0, color="red", linestyle="--", linewidth=1.0, label="20% threshold (convention)")
    ax4.set_xlabel(r"$\tau = 1 - T$", fontsize=14)
    ax4.set_ylabel("Flat-prior shift (% relative)", fontsize=14)
    ax4.set_xlim(TAU_MIN, TAU_MAX)
    ax4.legend(fontsize="x-small")
    mh.label.exp_label(exp="ALEPH", data=True, rlabel=r"$\sqrt{s} = 91.2$ GeV", ax=ax4)
    fig4.savefig(FIG_DIR / "flatprior_sensitivity.pdf", bbox_inches="tight", dpi=200, transparent=True)
    fig4.savefig(FIG_DIR / "flatprior_sensitivity.png", bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig4)
    log.info("Saved flatprior_sensitivity figure")

    log.info("\n[bold green]run_closure.py complete[/bold green]")
    log.info(f"Optimal IBU iterations: {optimal_iter}")
    log.info(f"Closure chi2/ndf: {closure_chi2_per_ndf[optimal_iter-1]:.3f}")
    log.info(f"Stress  chi2/ndf: {stress_chi2_per_ndf[optimal_iter-1]:.3f}")


if __name__ == "__main__":
    main()
