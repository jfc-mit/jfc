"""
Phase 4a — Stress Test: unfold a reweighted MC truth through the response matrix
and verify recovery of the reweighted shape.

Convention requirement: unfold a reweighted MC truth through the NOMINAL response
matrix and check that the unfolded result recovers the reweighted truth. Tests
for regularization-induced bias and sensitivity to non-trivial input shapes.

Steps:
  1. Load response matrix (R), MC gen histogram, MC reco histogram from Phase 3.
  2. Define a reweighting function w(tau) = 1 + 2*(tau - 0.25) (makes high-tau
     region heavier).
  3. Reweighted truth = MC gen counts * w(tau).
  4. Reweighted reco = R @ reweighted_truth (fold through response).
  5. Unfold the reweighted reco using IBU with 3 iterations (nominal) through the
     NOMINAL (un-reweighted) response matrix.
  6. Compare unfolded result to reweighted truth. Compute chi2/ndf.
  7. Repeat for 2, 4, 5 iterations.
  8. Save results and produce figure with ratio panel.

Outputs:
  - phase4_inference/exec/stress_test_results.npz
  - phase4_inference/figures/stress_test.{pdf,png}
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
log = logging.getLogger("stress_test")
console = Console()

# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------
P3_EXEC = Path("phase3_selection/exec")
P4_EXEC = Path("phase4_inference/exec")
FIG_DIR = Path("phase4_inference/figures")
P4_EXEC.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

N_BINS    = 25
TAU_MIN   = 0.0
TAU_MAX   = 0.5
TAU_EDGES   = np.linspace(TAU_MIN, TAU_MAX, N_BINS + 1)
TAU_CENTERS = 0.5 * (TAU_EDGES[:-1] + TAU_EDGES[1:])
BIN_WIDTH   = TAU_EDGES[1] - TAU_EDGES[0]

ITER_SCAN     = [2, 3, 4, 5]
NOMINAL_ITER  = 3


# ---------------------------------------------------------------------------
# IBU algorithm (as specified in task brief)
# ---------------------------------------------------------------------------

def ibu_unfold(data_reco: np.ndarray, response_matrix: np.ndarray,
               efficiency: np.ndarray, n_iterations: int,
               prior: np.ndarray | None = None) -> np.ndarray:
    """Iterative Bayesian Unfolding (IBU)."""
    n_gen  = response_matrix.shape[1]
    n_reco = response_matrix.shape[0]
    if prior is None:
        prior = np.ones(n_gen) / n_gen
    result = prior.copy()
    for _ in range(n_iterations):
        # Fold prior through response
        folded = response_matrix @ result
        folded[folded == 0] = 1e-10
        # Unfolding weights
        unfolded = np.zeros(n_gen)
        for j in range(n_gen):
            s = 0.0
            for i in range(n_reco):
                if folded[i] > 0:
                    s += response_matrix[i, j] * result[j] / folded[i] * data_reco[i]
            unfolded[j] = s / max(efficiency[j], 1e-10)
        result = unfolded.copy()
    return result


def normalize(h: np.ndarray) -> np.ndarray:
    s = h.sum()
    return h / (s * BIN_WIDTH) if s > 0 else h.copy()


def chi2_ndf(unfolded_norm: np.ndarray, truth_norm: np.ndarray,
             mask: np.ndarray | None = None) -> tuple[float, int]:
    """Compute chi2/ndf using bin-by-bin Poisson approximation (diagonal)."""
    if mask is None:
        mask = np.ones(len(unfolded_norm), dtype=bool)
    delta = unfolded_norm[mask] - truth_norm[mask]
    # Use the truth as the variance estimate (Poisson-like)
    sigma2 = np.maximum(truth_norm[mask], 1e-30)
    chi2 = float(np.sum(delta**2 / sigma2))
    ndf  = int(mask.sum())
    return chi2, ndf


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    log.info("=" * 70)
    log.info("Phase 4a: IBU Stress Test (reweighted MC truth recovery)")
    log.info("=" * 70)

    # -------------------------------------------------------------------------
    # 1. Load inputs
    # -------------------------------------------------------------------------
    log.info("\n[bold]1. Loading Phase 3 outputs...[/bold]")

    rm_data  = np.load(P3_EXEC / "response_matrix.npz")
    R        = rm_data["R"]           # (25, 25) — R[i, j] = P(reco=i | gen=j)
    eff      = rm_data["efficiency"]  # (25,)
    h_gen_sel = rm_data["h_gen_sel"]  # (25,) — matched gen events (used for prior)

    gen_data = np.load(P3_EXEC / "hist_tau_mc_gen.npz")
    h_mc_gen = gen_data["counts"].astype(float)  # (25,)

    reco_data = np.load(P3_EXEC / "hist_tau_mc_reco.npz")
    h_mc_reco = reco_data["counts"].astype(float)  # (25,)

    log.info(f"Response matrix shape:    {R.shape}")
    log.info(f"MC gen total events:      {h_mc_gen.sum():.0f}")
    log.info(f"MC reco total events:     {h_mc_reco.sum():.0f}")
    log.info(f"Efficiency range:         [{eff.min():.3f}, {eff.max():.3f}]")

    # -------------------------------------------------------------------------
    # 2. Define reweighted truth
    # -------------------------------------------------------------------------
    log.info("\n[bold]2. Constructing reweighted truth...[/bold]")

    # w(tau) = 1 + 2*(tau - 0.25) — linearly heavier toward high tau
    weights = 1.0 + 2.0 * (TAU_CENTERS - 0.25)
    log.info(f"Weight range: [{weights.min():.3f}, {weights.max():.3f}]")
    log.info(f"  tau=0.00: w={weights[0]:.3f}, tau=0.25: w={weights[12]:.3f}, tau=0.50: w={weights[-1]:.3f}")

    h_gen_reweighted = h_mc_gen * weights
    # Ensure non-negative (weights can go negative at very low tau — clamp)
    h_gen_reweighted = np.maximum(h_gen_reweighted, 0.0)

    log.info(f"Reweighted gen total:     {h_gen_reweighted.sum():.0f}")

    # Normalized truth distributions
    norm_truth_nominal    = normalize(h_mc_gen)
    norm_truth_reweighted = normalize(h_gen_reweighted)

    log.info(f"Max ratio (reweighted/nominal truth): "
             f"{(norm_truth_reweighted / np.where(norm_truth_nominal > 0, norm_truth_nominal, 1.0)).max():.3f}")

    # -------------------------------------------------------------------------
    # 3. Create reweighted reco: fold reweighted truth through response matrix
    # -------------------------------------------------------------------------
    log.info("\n[bold]3. Folding reweighted truth through response matrix...[/bold]")

    # Forward fold: expected_reco[i] = sum_j R[i,j] * truth[j] * eff[j]
    # R already encodes the probability P(reco=i | gen=j & selected)
    # The reco histogram = R @ (truth * eff) ... but we need to be careful:
    # In IBU, the "data" fed in is the raw reco histogram (after selection).
    # The folded model is: reco_pred[i] = sum_j R[i,j] * gen_j
    # where gen_j is the number of selected gen events in bin j.
    # The selected gen events = h_gen_reweighted (already reweighted).
    # So: h_reco_reweighted = R @ h_gen_reweighted (before efficiency correction)

    h_reco_reweighted = R @ h_gen_reweighted

    log.info(f"Reweighted reco total (folded): {h_reco_reweighted.sum():.0f}")
    log.info(f"  Original reco total:          {h_mc_reco.sum():.0f}")

    # -------------------------------------------------------------------------
    # 4. Unfold the reweighted reco using nominal prior and NOMINAL response matrix
    # -------------------------------------------------------------------------
    log.info("\n[bold]4. Unfolding reweighted reco...[/bold]")

    # Prior: use MC gen distribution (un-reweighted, i.e. "wrong" prior)
    prior_mc = h_gen_sel / h_gen_sel.sum() if h_gen_sel.sum() > 0 else np.ones(N_BINS) / N_BINS

    results = {}
    for n_iter in ITER_SCAN:
        unfolded = ibu_unfold(h_reco_reweighted, R, eff,
                               n_iterations=n_iter,
                               prior=prior_mc.copy())
        norm_unfolded = normalize(unfolded)
        chi2, ndf = chi2_ndf(norm_unfolded, norm_truth_reweighted)
        results[n_iter] = {
            "unfolded_counts": unfolded,
            "norm_unfolded":   norm_unfolded,
            "chi2": chi2,
            "ndf":  ndf,
        }
        log.info(f"  Iterations = {n_iter}: chi2/ndf = {chi2:.2f}/{ndf} = {chi2/ndf:.3f}")

    nominal = results[NOMINAL_ITER]
    log.info(f"\nNominal ({NOMINAL_ITER} iterations): chi2/ndf = "
             f"{nominal['chi2']:.2f}/{nominal['ndf']} = "
             f"{nominal['chi2']/nominal['ndf']:.3f}")

    # Stress test passes if chi2/ndf < 2.0 at nominal iterations
    passed = nominal["chi2"] / nominal["ndf"] < 2.0
    log.info(f"Stress test PASS (chi2/ndf < 2.0): {passed}")

    # -------------------------------------------------------------------------
    # 5. Save results
    # -------------------------------------------------------------------------
    log.info("\n[bold]5. Saving results...[/bold]")

    save_dict = dict(
        tau_edges=TAU_EDGES,
        tau_centers=TAU_CENTERS,
        weights=weights,
        h_mc_gen=h_mc_gen,
        h_gen_reweighted=h_gen_reweighted,
        h_reco_reweighted=h_reco_reweighted,
        norm_truth_nominal=norm_truth_nominal,
        norm_truth_reweighted=norm_truth_reweighted,
        iter_scan=np.array(ITER_SCAN),
        nominal_iter=NOMINAL_ITER,
        stress_test_passed=passed,
    )
    for n_iter in ITER_SCAN:
        save_dict[f"norm_unfolded_iter{n_iter}"] = results[n_iter]["norm_unfolded"]
        save_dict[f"chi2_iter{n_iter}"]          = results[n_iter]["chi2"]
        save_dict[f"ndf_iter{n_iter}"]           = results[n_iter]["ndf"]

    np.savez(P4_EXEC / "stress_test_results.npz", **save_dict)
    log.info(f"Saved {P4_EXEC}/stress_test_results.npz")

    # -------------------------------------------------------------------------
    # 6. Figure: reweighted truth vs unfolded (with ratio panel)
    # -------------------------------------------------------------------------
    log.info("\n[bold]6. Producing figure...[/bold]")

    mh.style.use("CMS")

    fig, (ax, rax) = plt.subplots(
        2, 1, figsize=(10, 10),
        gridspec_kw={"height_ratios": [3, 1]}, sharex=True,
    )
    fig.subplots_adjust(hspace=0.0)

    mh.label.exp_label(exp="ALEPH", data=False, rlabel=r"$\sqrt{s} = 91.2$ GeV", ax=ax)

    # ---- Main panel ----

    # Nominal (un-reweighted) MC truth for reference
    ax.stairs(norm_truth_nominal, TAU_EDGES, color="tab:gray", linewidth=1.5,
              linestyle=":", label="Nominal MC truth (un-reweighted)")

    # Reweighted truth (target)
    ax.stairs(norm_truth_reweighted, TAU_EDGES, color="tab:red", linewidth=2.5,
              linestyle="-", label=r"Reweighted truth [$w(\tau) = 1 + 2(\tau - 0.25)$]")

    # Unfolded results for each iteration count
    iter_colors = {2: "tab:blue", 3: "black", 4: "tab:orange", 5: "tab:green"}
    iter_ls     = {2: "--", 3: "-", 4: "-.", 5: ":"}
    for n_iter in ITER_SCAN:
        lw = 2.5 if n_iter == NOMINAL_ITER else 1.5
        chi2 = results[n_iter]["chi2"]
        ndf  = results[n_iter]["ndf"]
        ax.stairs(
            results[n_iter]["norm_unfolded"], TAU_EDGES,
            color=iter_ls[n_iter] if False else iter_colors[n_iter],
            linewidth=lw,
            linestyle=iter_ls[n_iter],
            label=(rf"IBU {n_iter} iter "
                   rf"[$\chi^2/\mathrm{{ndf}} = {chi2:.1f}/{ndf}$]"
                   + (" [NOMINAL]" if n_iter == NOMINAL_ITER else "")),
        )

    ax.set_ylabel(r"$(1/N)\,dN/d\tau$", fontsize=14)
    ax.set_yscale("log")
    ax.set_xlim(TAU_MIN, 0.45)
    ax.legend(fontsize="x-small")

    # ---- Ratio panel: unfolded / reweighted truth ----
    rax.axhline(1.0, color="gray", linewidth=1.0)

    safe_truth = np.where(norm_truth_reweighted > 0, norm_truth_reweighted, 1.0)

    for n_iter in ITER_SCAN:
        ratio = results[n_iter]["norm_unfolded"] / safe_truth
        lw = 2.5 if n_iter == NOMINAL_ITER else 1.5
        rax.stairs(ratio, TAU_EDGES,
                   color=iter_colors[n_iter],
                   linewidth=lw,
                   linestyle=iter_ls[n_iter],
                   label=f"iter={n_iter}")

    rax.set_xlabel(r"$\tau = 1 - T$", fontsize=14)
    rax.set_ylabel("Unfolded / Reweighted truth", fontsize=11)
    rax.set_ylim(0.7, 1.3)
    rax.set_xlim(TAU_MIN, 0.45)
    rax.axvspan(0.05, 0.30, alpha=0.05, color="green")

    for fmt in ("pdf", "png"):
        fig.savefig(FIG_DIR / f"stress_test.{fmt}",
                    bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)
    log.info(f"Saved {FIG_DIR}/stress_test.pdf and .png")

    # -------------------------------------------------------------------------
    # 7. Summary table
    # -------------------------------------------------------------------------
    log.info("\n[bold]Stress test summary:[/bold]")
    table = Table(title="IBU Stress Test: Reweighted MC Truth Recovery", show_header=True)
    table.add_column("Iterations", justify="right")
    table.add_column("chi2", justify="right")
    table.add_column("ndf", justify="right")
    table.add_column("chi2/ndf", justify="right")
    table.add_column("Pass (< 2.0)?", justify="center")
    for n_iter in ITER_SCAN:
        chi2 = results[n_iter]["chi2"]
        ndf  = results[n_iter]["ndf"]
        ok   = "YES" if chi2 / ndf < 2.0 else "NO"
        nom  = " [NOMINAL]" if n_iter == NOMINAL_ITER else ""
        table.add_row(f"{n_iter}{nom}", f"{chi2:.2f}", f"{ndf}",
                      f"{chi2/ndf:.3f}", ok)
    console.print(table)

    log.info(f"\n[bold green]stress_test.py complete. "
             f"Nominal stress test PASSED = {passed}[/bold green]")


if __name__ == "__main__":
    main()
