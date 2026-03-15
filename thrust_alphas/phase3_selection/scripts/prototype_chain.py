"""
Phase 3 Script 5: prototype_chain.py

Run the full unfolding chain on the actual data.

This is a working result — not the final measurement (systematic
uncertainties are deferred to Phase 4). It serves as a sanity check
and provides the uncorrected and corrected thrust distributions.

Steps:
  1. Load the pre-built response matrix and closure results (optimal iteration).
  2. Load the data tau histogram.
  3. Run IBU on data using the MC prior.
  4. Run IBU on data using the flat prior.
  5. Compute bin-by-bin corrected distribution as cross-check.
  6. Compare unfolded data to MC particle-level truth (tgenBefore).
  7. Produce figures.

Inputs:
  - phase3_selection/exec/response_matrix.npz
  - phase3_selection/exec/hist_tau_data.npz
  - phase3_selection/exec/hist_tau_mc_reco.npz
  - phase3_selection/exec/hist_tau_mc_gen.npz
  - phase3_selection/exec/bbb_corrections.npz
  - phase3_selection/exec/closure_results.npz

Outputs:
  - phase3_selection/exec/prototype_unfolded.npz
  - phase3_selection/figures/prototype_*.{pdf,png}
"""

import logging
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplhep as mh
from rich.logging import RichHandler

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger("prototype_chain")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
OUT_DIR = Path("phase3_selection/exec")
FIG_DIR = Path("phase3_selection/figures")
OUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

N_BINS    = 25
TAU_MIN   = 0.0
TAU_MAX   = 0.5
TAU_EDGES   = np.linspace(TAU_MIN, TAU_MAX, N_BINS + 1)
TAU_CENTERS = 0.5 * (TAU_EDGES[:-1] + TAU_EDGES[1:])
BIN_WIDTH   = TAU_EDGES[1] - TAU_EDGES[0]


# ---------------------------------------------------------------------------
# IBU (same as in run_closure.py)
# ---------------------------------------------------------------------------

def ibu(data_reco, R, efficiency, prior, n_iter):
    n_reco, n_gen = R.shape
    prior = prior / prior.sum() if prior.sum() > 0 else np.ones(n_gen) / n_gen
    for _ in range(n_iter):
        denom = R @ prior
        safe_denom = np.where(denom > 0, denom, 1.0)
        U = (R * prior[np.newaxis, :]).T / safe_denom[:, np.newaxis]
        U = U.T
        unfolded = U @ data_reco
        safe_eff = np.where(efficiency > 0, efficiency, 1.0)
        unfolded = unfolded / safe_eff
        if unfolded.sum() > 0:
            prior = unfolded / unfolded.sum()
        else:
            prior = np.ones(n_gen) / n_gen
    return unfolded


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    log.info("=" * 70)
    log.info("Phase 3 Script 5: Prototype Unfolding Chain")
    log.info("=" * 70)

    # Load inputs
    rm  = np.load(OUT_DIR / "response_matrix.npz")
    dh  = np.load(OUT_DIR / "hist_tau_data.npz")
    mhr = np.load(OUT_DIR / "hist_tau_mc_reco.npz")
    mhg = np.load(OUT_DIR / "hist_tau_mc_gen.npz")
    bbb = np.load(OUT_DIR / "bbb_corrections.npz")
    cl  = np.load(OUT_DIR / "closure_results.npz")

    R          = rm["R"]
    efficiency = rm["efficiency"]
    h_gen_before = rm["h_gen_before"]

    h_data    = dh["counts"].astype(float)
    h_mc_reco = mhr["counts"].astype(float)
    h_mc_gen  = mhg["counts"].astype(float)
    bbb_C     = bbb["C"]

    optimal_iter = int(cl["optimal_iter"])
    log.info(f"Optimal IBU iterations: {optimal_iter}")
    log.info(f"Data events: {h_data.sum():.0f}")
    log.info(f"MC reco events: {h_mc_reco.sum():.0f}")

    # ------------------------------------------------------------------
    # 1. IBU with MC prior
    # ------------------------------------------------------------------
    prior_mc = h_mc_gen / h_mc_gen.sum()
    unfolded_mc_prior = ibu(h_data, R, efficiency, prior_mc.copy(), optimal_iter)

    # ------------------------------------------------------------------
    # 2. IBU with flat prior
    # ------------------------------------------------------------------
    prior_flat = np.ones(N_BINS) / N_BINS
    unfolded_flat_prior = ibu(h_data, R, efficiency, prior_flat.copy(), optimal_iter)

    # ------------------------------------------------------------------
    # 3. Bin-by-bin correction (cross-check)
    # ------------------------------------------------------------------
    bbb_corrected = h_data * bbb_C

    # ------------------------------------------------------------------
    # Normalize all to (1/N) dN/dtau
    # ------------------------------------------------------------------
    def normalize(h):
        s = h.sum()
        if s > 0:
            return h / (s * BIN_WIDTH)
        return h

    # Unfolded data (MC prior), efficiency-corrected
    unf_norm       = normalize(unfolded_mc_prior)
    unf_flat_norm  = normalize(unfolded_flat_prior)
    bbb_norm       = normalize(bbb_corrected)
    # MC gen truth (tgenBefore) for comparison
    mc_truth_norm  = normalize(h_gen_before.astype(float))
    # Detector-level data (uncorrected)
    data_det_norm  = normalize(h_data)

    # Statistical uncertainties on normalized unfolded:
    # Approx by propagating sqrt(N_data) through the efficiency correction
    data_unc_raw = np.sqrt(np.maximum(h_data, 1.0))
    unf_stat_unc = ibu(data_unc_raw**2, R, efficiency, prior_mc.copy(), optimal_iter)
    unf_stat_unc = np.sqrt(np.maximum(unf_stat_unc, 0.0))
    scale = unfolded_mc_prior.sum() if unfolded_mc_prior.sum() > 0 else 1.0
    unf_stat_unc_norm = unf_stat_unc / (scale * BIN_WIDTH)

    log.info(f"Unfolded data (normalized) total integral: "
             f"{np.sum(unf_norm * BIN_WIDTH):.4f} (should be ~1)")

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------
    np.savez(
        OUT_DIR / "prototype_unfolded.npz",
        # Counts
        unfolded_mc_prior=unfolded_mc_prior,
        unfolded_flat_prior=unfolded_flat_prior,
        bbb_corrected=bbb_corrected,
        h_data=h_data,
        h_gen_before=h_gen_before,
        # Normalized
        unf_norm=unf_norm,
        unf_flat_norm=unf_flat_norm,
        bbb_norm=bbb_norm,
        mc_truth_norm=mc_truth_norm,
        data_det_norm=data_det_norm,
        unf_stat_unc_norm=unf_stat_unc_norm,
        # Metadata
        tau_edges=TAU_EDGES,
        tau_centers=TAU_CENTERS,
        optimal_iter=optimal_iter,
    )
    log.info("Saved prototype_unfolded.npz")

    # ------------------------------------------------------------------
    # Figures
    # ------------------------------------------------------------------
    mh.style.use("CMS")

    # Fig 1: Detector-level data vs MC reco
    mc_reco_norm = normalize(h_mc_reco)
    ratio_det = np.where(mc_reco_norm > 0, data_det_norm / mc_reco_norm, np.nan)

    fig1, (ax1, rax1) = plt.subplots(
        2, 1, figsize=(10, 10),
        gridspec_kw={"height_ratios": [3, 1]}, sharex=True,
    )
    fig1.subplots_adjust(hspace=0.0)
    ax1.stairs(data_det_norm, TAU_EDGES, color="black",   linewidth=1.5, label="Data (detector level)")
    ax1.stairs(mc_reco_norm,  TAU_EDGES, color="tab:red", linewidth=1.5, linestyle="--",
               label="MC Pythia 6.1 (detector level)")
    ax1.set_ylabel(r"$(1/N)\,dN/d\tau$", fontsize=14)
    ax1.set_yscale("log")
    ax1.legend(fontsize="x-small")
    mh.label.exp_label(exp="ALEPH", data=True, rlabel=r"$\sqrt{s} = 91.2$ GeV", ax=ax1)

    rax1.axhline(1.0, color="gray", linewidth=1.0)
    rax1.stairs(ratio_det, TAU_EDGES, color="black", linewidth=1.5)
    rax1.set_xlabel(r"$\tau = 1 - T$", fontsize=14)
    rax1.set_ylabel("Data / MC", fontsize=12)
    rax1.set_ylim(0.7, 1.3)
    rax1.set_xlim(TAU_MIN, TAU_MAX)

    for fmt in ("pdf", "png"):
        fig1.savefig(FIG_DIR / f"prototype_detector_level.{fmt}",
                     bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig1)
    log.info("Saved prototype_detector_level")

    # Fig 2: Unfolded data vs MC truth (main result plot)
    ratio_unf = np.where(mc_truth_norm > 0, unf_norm / mc_truth_norm, np.nan)

    fig2, (ax2, rax2) = plt.subplots(
        2, 1, figsize=(10, 10),
        gridspec_kw={"height_ratios": [3, 1]}, sharex=True,
    )
    fig2.subplots_adjust(hspace=0.0)
    ax2.stairs(unf_norm,      TAU_EDGES, color="black",   linewidth=1.5,
               label=f"Data unfolded (IBU, iter={optimal_iter})")
    ax2.stairs(mc_truth_norm, TAU_EDGES, color="tab:red", linewidth=1.5, linestyle="--",
               label="MC truth (particle level)")
    ax2.stairs(unf_flat_norm, TAU_EDGES, color="tab:blue", linewidth=1.0, linestyle=":",
               label="Data unfolded (flat prior)")
    ax2.stairs(bbb_norm,      TAU_EDGES, color="tab:green", linewidth=1.0, linestyle="-.",
               label="Data bin-by-bin corrected")
    ax2.set_ylabel(r"$(1/N)\,dN/d\tau$", fontsize=14)
    ax2.set_yscale("log")
    ax2.legend(fontsize="x-small")
    mh.label.exp_label(exp="ALEPH", data=True, rlabel=r"$\sqrt{s} = 91.2$ GeV", ax=ax2)

    rax2.axhline(1.0, color="gray", linewidth=1.0)
    rax2.stairs(ratio_unf, TAU_EDGES, color="black", linewidth=1.5)
    rax2.errorbar(TAU_CENTERS, ratio_unf, yerr=unf_stat_unc_norm / (mc_truth_norm + 1e-10),
                  fmt="none", color="black", capsize=2)
    rax2.set_xlabel(r"$\tau = 1 - T$", fontsize=14)
    rax2.set_ylabel("Data / MC truth", fontsize=12)
    rax2.set_ylim(0.7, 1.3)
    rax2.set_xlim(TAU_MIN, TAU_MAX)

    for fmt in ("pdf", "png"):
        fig2.savefig(FIG_DIR / f"prototype_unfolded.{fmt}",
                     bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig2)
    log.info("Saved prototype_unfolded")

    # Fig 3: Method comparison (IBU vs BBB vs flat prior), ratio to IBU MC prior
    ratio_flat = np.where(unf_norm > 0, unf_flat_norm / unf_norm, np.nan)
    ratio_bbb  = np.where(unf_norm > 0, bbb_norm / unf_norm, np.nan)

    fig3, ax3 = plt.subplots(figsize=(10, 6))
    ax3.axhline(1.0, color="gray", linewidth=1.0)
    ax3.stairs(ratio_flat, TAU_EDGES, color="tab:blue",  linewidth=1.5,
               label="Flat prior / MC prior (IBU)")
    ax3.stairs(ratio_bbb,  TAU_EDGES, color="tab:green", linewidth=1.5,
               label="Bin-by-bin / IBU (MC prior)")
    ax3.set_xlabel(r"$\tau = 1 - T$", fontsize=14)
    ax3.set_ylabel("Ratio to nominal IBU", fontsize=14)
    ax3.set_xlim(TAU_MIN, TAU_MAX)
    ax3.set_ylim(0.8, 1.2)
    ax3.legend(fontsize="x-small")
    mh.label.exp_label(exp="ALEPH", data=True, rlabel=r"$\sqrt{s} = 91.2$ GeV", ax=ax3)
    for fmt in ("pdf", "png"):
        fig3.savefig(FIG_DIR / f"prototype_method_comparison.{fmt}",
                     bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig3)
    log.info("Saved prototype_method_comparison")

    # Summary
    log.info("\n[bold]Unfolded vs. MC truth comparison (fit range only)[/bold]")
    fit_mask = (TAU_CENTERS >= 0.05) & (TAU_CENTERS <= 0.30)
    for j in range(N_BINS):
        if fit_mask[j]:
            ratio_val = ratio_unf[j] if not np.isnan(ratio_unf[j]) else 0.0
            log.info(f"  tau={TAU_CENTERS[j]:.3f}: unf/truth = {ratio_val:.3f}")

    log.info("\n[bold green]prototype_chain.py complete[/bold green]")
    log.info(f"Outputs in {OUT_DIR}/")


if __name__ == "__main__":
    main()
