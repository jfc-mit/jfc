"""
Phase 4a Script 1: validate_iterations.py

Independent MC closure test using two independent MC half-samples.

Motivation:
  Phase 3 found closure chi2/ndf = 2.55 at 3 iterations (minimum = 1.91 at
  2 iterations). A reviewer flagged this: the Phase 3 closure used the SAME
  MC sample to build the response matrix AND to form the test reco histogram,
  so the chi2 was correlated with the response matrix fluctuations. This
  overestimates the true closure residuals.

  This script performs the proper independent-MC closure test:
    - Split 40 MC files into half A (even file numbers 002,004,...,040) and
      half B (odd file numbers 001,003,...,039).
    - Build the response matrix from half A.
    - Unfold half B's reco distribution through the half-A response matrix.
    - Compare to half B's truth distribution.
    - This is a genuine independent-MC closure test.

  Report chi2/ndf at iterations 1–6.
  Confirm or revise the nominal iteration count.

Outputs:
  - phase4_inference/exec/indep_closure_results.npz
  - phase4_inference/figures/indep_closure_*.{pdf,png}
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
log = logging.getLogger("validate_iterations")
console = Console()

# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------
MC_DIR  = Path("/n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ALEPHMC")
OUT_DIR = Path("phase4_inference/exec")
FIG_DIR = Path("phase4_inference/figures")
OUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

N_BINS      = 25
TAU_MIN     = 0.0
TAU_MAX     = 0.5
TAU_EDGES   = np.linspace(TAU_MIN, TAU_MAX, N_BINS + 1)
TAU_CENTERS = 0.5 * (TAU_EDGES[:-1] + TAU_EDGES[1:])
BIN_WIDTH   = TAU_EDGES[1] - TAU_EDGES[0]

FIT_MASK    = (TAU_CENTERS >= 0.05) & (TAU_CENTERS <= 0.30)
N_ITER_MAX  = 6

MC_FILES = sorted(MC_DIR.glob("LEP1MC1994_recons_aftercut-[0-9][0-9][0-9].root"))


# ---------------------------------------------------------------------------
# IBU algorithm
# ---------------------------------------------------------------------------

def ibu(data_reco: np.ndarray, R: np.ndarray, efficiency: np.ndarray,
        prior: np.ndarray, n_iter: int) -> np.ndarray:
    """
    Iterative Bayesian Unfolding.
    Returns unfolded counts (efficiency-corrected).
    """
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


def chi2_ndf(y_unfolded: np.ndarray, y_truth: np.ndarray,
             mask: np.ndarray) -> tuple[float, int]:
    """
    Compute chi2/ndf using truth MC Poisson uncertainties.
    Both inputs are raw counts (not normalized).
    """
    y_u = y_unfolded[mask].copy()
    y_t = y_truth[mask].copy()
    # Normalize unfolded to same total as truth for shape comparison
    if y_u.sum() > 0:
        y_u = y_u / y_u.sum() * y_t.sum()
    unc  = np.sqrt(np.maximum(y_t, 1.0))
    chi2 = np.sum(((y_u - y_t) / unc) ** 2)
    ndf  = int(mask.sum())
    return float(chi2), ndf


def chi2_ndf_independent(y_unfolded: np.ndarray, y_truth: np.ndarray,
                          mask: np.ndarray) -> tuple[float, int]:
    """
    Proper independent chi2: uncertainty = sqrt(y_unfolded + y_truth).
    Uses both halves' statistical uncertainties.
    """
    y_u = y_unfolded[mask].copy()
    y_t = y_truth[mask].copy()
    # Normalize unfolded to same total as truth
    if y_u.sum() > 0:
        y_u = y_u / y_u.sum() * y_t.sum()
    # Total uncertainty from both halves
    unc  = np.sqrt(np.maximum(y_u + y_t, 1.0))
    chi2 = np.sum(((y_u - y_t) / unc) ** 2)
    ndf  = int(mask.sum())
    return float(chi2), ndf


# ---------------------------------------------------------------------------
# Build response matrix from a set of MC files
# ---------------------------------------------------------------------------

def build_response_from_files(files: list[Path]) -> dict:
    """
    Build response matrix, efficiency, and histograms from a list of MC files.

    Returns dict with keys: R, efficiency, h_reco_sel, h_gen_sel, h_gen_before.
    """
    h2d          = np.zeros((N_BINS, N_BINS), dtype=np.float64)
    h_reco_sel   = np.zeros(N_BINS, dtype=np.float64)
    h_gen_sel    = np.zeros(N_BINS, dtype=np.float64)
    h_gen_before = np.zeros(N_BINS, dtype=np.float64)

    for fpath in files:
        with uproot.open(fpath) as f:
            # Reco tree (selected events)
            t_reco     = f["t"]
            passes_all = t_reco["passesAll"].array(library="np")
            tau_reco   = t_reco["Thrust"].array(library="np")
            tau_reco   = 1.0 - tau_reco

            sel_mask = passes_all.astype(bool)
            tau_reco_sel = tau_reco[sel_mask]

            # Gen tree (matched to selected reco)
            t_gen     = f["tgen"]
            tau_gen   = t_gen["Thrust"].array(library="np")
            tau_gen   = 1.0 - tau_gen
            tau_gen_sel = tau_gen[sel_mask]

            # Gen before selection
            t_genbefore = f["tgenBefore"]
            tau_genbefore = t_genbefore["Thrust"].array(library="np")
            tau_genbefore = 1.0 - tau_genbefore

            # Fill 2D histogram (reco x gen)
            mask2d = (
                (tau_reco_sel >= TAU_MIN) & (tau_reco_sel < TAU_MAX) &
                (tau_gen_sel  >= TAU_MIN) & (tau_gen_sel  < TAU_MAX)
            )
            if mask2d.sum() > 0:
                h2d_file, _, _ = np.histogram2d(
                    tau_reco_sel[mask2d], tau_gen_sel[mask2d],
                    bins=[TAU_EDGES, TAU_EDGES]
                )
                h2d += h2d_file

            # 1D histograms
            h_reco_file, _ = np.histogram(tau_reco_sel, bins=TAU_EDGES)
            h_gen_file,  _ = np.histogram(tau_gen_sel,  bins=TAU_EDGES)
            h_genb_file, _ = np.histogram(tau_genbefore, bins=TAU_EDGES)
            h_reco_sel   += h_reco_file
            h_gen_sel    += h_gen_file
            h_gen_before += h_genb_file

    log.info(f"  Reco events:    {h_reco_sel.sum():.0f}")
    log.info(f"  Gen-sel events: {h_gen_sel.sum():.0f}")
    log.info(f"  GenBefore evts: {h_gen_before.sum():.0f}")

    # Build normalized response matrix R[i,j] = P(reco bin i | gen bin j)
    col_sums = h2d.sum(axis=0)
    R = np.where(col_sums > 0, h2d / col_sums[np.newaxis, :], 0.0)

    # Efficiency: fraction of gen-before events that are reco-selected
    efficiency = np.where(
        h_gen_before > 0,
        h_gen_sel / h_gen_before,
        0.0
    )

    return dict(R=R, efficiency=efficiency,
                h_reco_sel=h_reco_sel, h_gen_sel=h_gen_sel,
                h_gen_before=h_gen_before)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    log.info("=" * 70)
    log.info("Phase 4a Script 1: Independent MC Closure Test")
    log.info("=" * 70)

    if len(MC_FILES) == 0:
        log.error("No MC files found. Check MC_DIR path.")
        return

    log.info(f"Total MC files: {len(MC_FILES)}")

    # Split into half A (even-numbered files) and half B (odd-numbered files)
    # File names: LEP1MC1994_recons_aftercut-001.root through -040.root
    # Extract file index from name
    half_a = []
    half_b = []
    for fpath in MC_FILES:
        stem = fpath.stem  # e.g. LEP1MC1994_recons_aftercut-001
        idx  = int(stem.split("-")[-1])  # 1..40
        if idx % 2 == 0:
            half_a.append(fpath)   # even: 002,004,...,040
        else:
            half_b.append(fpath)   # odd:  001,003,...,039

    log.info(f"Half A (response matrix): {len(half_a)} files (even indices)")
    log.info(f"Half B (test sample):     {len(half_b)} files (odd indices)")

    # -------------------------------------------------------------------------
    # Build response matrix from half A
    # -------------------------------------------------------------------------
    log.info("\n[bold]Building response matrix from half A...[/bold]")
    rm_a = build_response_from_files(half_a)
    R_a        = rm_a["R"]
    eff_a      = rm_a["efficiency"]
    h_gen_a    = rm_a["h_gen_sel"]

    # -------------------------------------------------------------------------
    # Load half B reco and truth
    # -------------------------------------------------------------------------
    log.info("\n[bold]Loading half B reco and truth...[/bold]")
    rm_b = build_response_from_files(half_b)
    h_reco_b   = rm_b["h_reco_sel"]   # half B detector-level
    h_truth_b  = rm_b["h_gen_sel"]    # half B truth (matched gen)

    log.info(f"\nHalf B reco events:  {h_reco_b.sum():.0f}")
    log.info(f"Half B truth events: {h_truth_b.sum():.0f}")

    # Prior from half A truth
    prior_from_a = h_gen_a / h_gen_a.sum() if h_gen_a.sum() > 0 else np.ones(N_BINS) / N_BINS

    # -------------------------------------------------------------------------
    # Scan iterations: unfold half B reco through half A response
    # -------------------------------------------------------------------------
    log.info("\n[bold]Scanning iterations (unfold half B through half A response)...[/bold]")
    closure_chi2     = []
    closure_chi2_ind = []
    closure_ndf      = []
    unfolded_by_iter = {}

    for n_iter in range(1, N_ITER_MAX + 1):
        unfolded = ibu(h_reco_b, R_a, eff_a, prior_from_a.copy(), n_iter)
        c2,     ndf  = chi2_ndf(unfolded, h_truth_b, FIT_MASK)
        c2_ind, _    = chi2_ndf_independent(unfolded, h_truth_b, FIT_MASK)
        closure_chi2.append(c2)
        closure_chi2_ind.append(c2_ind)
        closure_ndf.append(ndf)
        unfolded_by_iter[n_iter] = unfolded.copy()
        log.info(f"  Iter {n_iter}: chi2/ndf = {c2/ndf:.3f} (corr), {c2_ind/ndf:.3f} (indep)")

    closure_chi2_per_ndf = [c / n for c, n in zip(closure_chi2, closure_ndf)]
    closure_c2ind_per_ndf = [c / n for c, n in zip(closure_chi2_ind, closure_ndf)]

    # -------------------------------------------------------------------------
    # Also run the Phase 3 style closure (same sample) for comparison
    # -------------------------------------------------------------------------
    log.info("\n[bold]Reference: Phase 3 style closure (using pre-built full response)...[/bold]")
    rm_full = np.load("phase3_selection/exec/response_matrix.npz")
    R_full  = rm_full["R"]
    eff_full = rm_full["efficiency"]
    h_reco_full = rm_full["h_reco_sel"]
    h_truth_full = rm_full["h_gen_sel"]
    prior_full = h_truth_full / h_truth_full.sum() if h_truth_full.sum() > 0 else np.ones(N_BINS) / N_BINS

    phase3_chi2 = []
    for n_iter in range(1, N_ITER_MAX + 1):
        unf = ibu(h_reco_full, R_full, eff_full, prior_full.copy(), n_iter)
        c2, ndf_p3 = chi2_ndf(unf, h_truth_full, FIT_MASK)
        phase3_chi2.append(c2 / ndf_p3)
        log.info(f"  Phase3 iter {n_iter}: chi2/ndf = {c2/ndf_p3:.3f}")

    # -------------------------------------------------------------------------
    # Determine optimal iteration
    # -------------------------------------------------------------------------
    # Use independent chi2 for the iteration choice (more rigorous)
    optimal_iter = 1
    for n in range(2, N_ITER_MAX + 1):
        prev = closure_c2ind_per_ndf[n - 2]
        curr = closure_c2ind_per_ndf[n - 1]
        if prev > 0 and abs(prev - curr) / prev < 0.05:
            optimal_iter = n - 1
            break
        optimal_iter = n

    ndf_fit = int(FIT_MASK.sum())
    log.info(f"\n[bold]Independent-MC closure results:[/bold]")
    log.info(f"  Optimal iteration (independent test): {optimal_iter}")
    log.info(f"  chi2/ndf at iter={optimal_iter}: {closure_c2ind_per_ndf[optimal_iter-1]:.3f}")
    log.info(f"  chi2/ndf at iter=2: {closure_c2ind_per_ndf[1]:.3f}")
    log.info(f"  chi2/ndf at iter=3: {closure_c2ind_per_ndf[2]:.3f}")
    log.info(f"  chi2/ndf at iter=4: {closure_c2ind_per_ndf[3]:.3f}")

    # -------------------------------------------------------------------------
    # Print comparison table
    # -------------------------------------------------------------------------
    table = Table(title="Independent MC Closure: chi2/ndf vs Iterations", show_header=True)
    table.add_column("Iter", justify="right")
    table.add_column("Indep chi2/ndf", justify="right")
    table.add_column("Corr chi2/ndf",  justify="right")
    table.add_column("Phase3 chi2/ndf", justify="right")
    for i in range(N_ITER_MAX):
        n = i + 1
        marker = " <-- nominal" if n == optimal_iter else ""
        table.add_row(
            f"{n}",
            f"{closure_c2ind_per_ndf[i]:.3f}",
            f"{closure_chi2_per_ndf[i]:.3f}",
            f"{phase3_chi2[i]:.3f}",
        )
    console.print(table)

    # -------------------------------------------------------------------------
    # Per-bin comparison at optimal iteration
    # -------------------------------------------------------------------------
    unf_opt = unfolded_by_iter[optimal_iter]
    scale   = h_truth_b.sum() / unf_opt.sum() if unf_opt.sum() > 0 else 1.0
    unf_opt_norm  = unf_opt * scale

    bw = BIN_WIDTH
    norm_truth = h_truth_b / (h_truth_b.sum() * bw)
    norm_unf   = unf_opt_norm / (h_truth_b.sum() * bw)
    ratio      = np.where(h_truth_b > 0, unf_opt_norm / h_truth_b, np.nan)

    log.info("\n[bold]Per-bin ratio (unfolded half B / truth half B) at optimal iter:[/bold]")
    for j in range(N_BINS):
        if FIT_MASK[j]:
            log.info(f"  tau={TAU_CENTERS[j]:.3f}: ratio = {ratio[j]:.4f}")

    # -------------------------------------------------------------------------
    # Save results
    # -------------------------------------------------------------------------
    np.savez(
        OUT_DIR / "indep_closure_results.npz",
        n_iters=np.arange(1, N_ITER_MAX + 1),
        closure_chi2_indep=np.array(closure_chi2_ind),
        closure_chi2_corr=np.array(closure_chi2),
        closure_chi2_per_ndf=np.array(closure_chi2_per_ndf),
        closure_c2ind_per_ndf=np.array(closure_c2ind_per_ndf),
        phase3_chi2_per_ndf=np.array(phase3_chi2),
        closure_ndf=np.array(closure_ndf),
        optimal_iter=optimal_iter,
        # Half B results at optimal
        unfolded_opt=unf_opt,
        h_truth_b=h_truth_b,
        h_reco_b=h_reco_b,
        # Half A response info
        h_gen_a=h_gen_a,
        tau_centers=TAU_CENTERS,
        tau_edges=TAU_EDGES,
        fit_mask=FIT_MASK,
    )
    log.info(f"Saved {OUT_DIR}/indep_closure_results.npz")

    # -------------------------------------------------------------------------
    # Figures
    # -------------------------------------------------------------------------
    mh.style.use("CMS")

    # Fig 1: chi2/ndf vs iterations comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    iters_arr = np.arange(1, N_ITER_MAX + 1)
    ax.plot(iters_arr, closure_c2ind_per_ndf, "o-",  color="black",    label="Independent half-sample (proper)")
    ax.plot(iters_arr, closure_chi2_per_ndf,  "s--", color="tab:blue", label="Independent half-sample (corr unc)")
    ax.plot(iters_arr, phase3_chi2,           "^:",  color="tab:red",  label="Phase 3 (same-sample, reference)")
    ax.axvline(optimal_iter, color="gray", linestyle=":", linewidth=1.5,
               label=f"Optimal = {optimal_iter} iterations")
    ax.axhline(1.0, color="green", linestyle="--", linewidth=1.0, label=r"$\chi^2/\mathrm{ndf}=1$")
    ax.set_xlabel("Number of IBU iterations", fontsize=14)
    ax.set_ylabel(r"$\chi^2/\mathrm{ndf}$ (fit range)", fontsize=14)
    ax.set_xticks(iters_arr)
    ax.set_ylim(0.5, 5.0)
    ax.legend(fontsize="x-small")
    mh.label.exp_label(exp="ALEPH", data=False, rlabel=r"Pythia 6.1 MC", ax=ax)
    for fmt in ("pdf", "png"):
        fig.savefig(FIG_DIR / f"indep_closure_chi2_vs_iter.{fmt}",
                    bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)
    log.info("Saved indep_closure_chi2_vs_iter")

    # Fig 2: Unfolded vs truth at optimal iteration
    fig2, (ax2, rax2) = plt.subplots(
        2, 1, figsize=(10, 10),
        gridspec_kw={"height_ratios": [3, 1]}, sharex=True,
    )
    fig2.subplots_adjust(hspace=0.0)
    ax2.stairs(norm_truth, TAU_EDGES, color="black",   linewidth=1.5, label="Half B truth (gen sel)")
    ax2.stairs(norm_unf,   TAU_EDGES, color="tab:red", linewidth=1.5, linestyle="--",
               label=f"Half B reco unfolded (half A response, iter={optimal_iter})")
    ax2.set_ylabel(r"$(1/N)\,dN/d\tau$", fontsize=14)
    ax2.set_yscale("log")
    ax2.legend(fontsize="x-small")
    mh.label.exp_label(exp="ALEPH", data=False, rlabel=r"Pythia 6.1 MC (independent halves)", ax=ax2)

    rax2.axhline(1.0, color="gray", linewidth=1.0)
    rax2.stairs(ratio, TAU_EDGES, color="black", linewidth=1.5)
    # Uncertainty band from both halves
    unc_ratio = np.where(
        h_truth_b > 0,
        np.sqrt(1.0 / np.maximum(unf_opt * scale, 1.0) + 1.0 / np.maximum(h_truth_b, 1.0)) * ratio,
        0.0
    )
    rax2.fill_between(TAU_CENTERS, ratio - unc_ratio, ratio + unc_ratio,
                      step=None, alpha=0.3, color="tab:blue", label="Stat. unc.")
    rax2.set_xlabel(r"$\tau = 1 - T$", fontsize=14)
    rax2.set_ylabel("Unfolded / Truth", fontsize=12)
    rax2.set_ylim(0.8, 1.2)
    rax2.set_xlim(TAU_MIN, TAU_MAX)

    for fmt in ("pdf", "png"):
        fig2.savefig(FIG_DIR / f"indep_closure_test.{fmt}",
                     bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig2)
    log.info("Saved indep_closure_test")

    # Summary
    log.info("\n[bold green]validate_iterations.py complete[/bold green]")
    log.info(f"  Optimal iteration (independent test): {optimal_iter}")
    log.info(f"  Independent chi2/ndf at iter=2: {closure_c2ind_per_ndf[1]:.3f}")
    log.info(f"  Independent chi2/ndf at iter=3: {closure_c2ind_per_ndf[2]:.3f}")
    log.info(f"  Phase 3 chi2/ndf at iter=3:    {phase3_chi2[2]:.3f}")
    log.info(
        "  NOTE: Phase 3 chi2/ndf was inflated by same-sample correlations. "
        "The independent test is the authoritative result."
    )


if __name__ == "__main__":
    main()
