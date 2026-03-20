## 7. Tools and Paradigms

### 7.1 Preferred Tools

| Capability | Tool | Notes |
|-----------|------|-------|
| ROOT file I/O | uproot | Pythonic, no ROOT install. `uproot.open()` to explore, `arrays()` to load. |
| Arrays | awkward-array, numpy | Columnar — no event loops. awkward for jagged, numpy for flat. |
| Histogramming | hist, boost-histogram | ND axes for systematic variations — store as axis dimensions, not separate histograms. |
| Statistical model | pyhf, cabinetry | HistFactory JSON workspaces. cabinetry for ranking/pulls. |
| Unbinned fits | zfit | When binned HistFactory is insufficient. |
| MVA | xgboost, scikit-learn | BDTs via xgboost. sklearn for preprocessing, metrics. |
| Plotting | matplotlib, mplhep | See `appendix-plotting.md` for all figure standards. |
| Columnar model | coffea | `NanoEvents` for schema-driven access, `PackedSelection` for cutflows. Optional. |
| Jet clustering | fastjet | e+e−: Durham (`ee_genkt_algorithm`, p=−1). pp: anti-kt. |
| b-tagging | tiered (see below) | Agent builds taggers during Phase 2. |
| Logging | logging + rich | No bare `print()`. See §11. |
| Documents | pandoc (≥3.0) + pdflatex | Markdown → PDF. Never use LLM for conversion. |
| Dependencies | pixi | `pixi.toml` is single source of truth for environment. |
| Experiment knowledge | RAG (SciTreeRAG) | See §2.2. |

**Tiered tagging:** (1) Cut-based as cross-check — always exists.
(2) BDT as default primary. (3) NN only if input space justifies it.

### 7.2 Paradigms

- **Prototype on a slice (~1000 events), then scale.** Full dataset is for
  production, not debugging.
- **Read the API before working around it.** Check docstrings/docs before
  writing workarounds. Add idioms to `appendix-heuristics.md`.
- **Columnar analysis.** Arrays + boolean masks, not event loops.
- **Immutable cuts.** Named boolean masks, never modify arrays.
- **Workspace as artifact.** pyhf JSON written to disk, committed.
- **Fit reproducibility.** Each fit has a pixi task. Human can re-run.
- **Plots are evidence.** Every claim has a figure or table.
- **Pin random seeds.** Record software versions.
- **MC normalization:** weight = σ × L / Σw_generated (algebraic sum for NLO).
- **Systematic naming:** `{source}Up` / `{source}Down` (pyhf/cabinetry convention).
- **Binning:** No bin with < ~5 expected events. Variable binning when motivated.

### 7.3 Scale-Out

Estimate before running: input size, per-event cost on 1000-event slice,
peak memory.

| Estimated time | Mode |
|----------------|------|
| < 2 min | Single-core local |
| 2–15 min | `ProcessPoolExecutor` or multicore |
| > 15 min | SLURM: `sbatch --wait` (single) or `--array` (per-file) |

Prefer the simplest pattern that works. See `appendix-automation.md` for
SLURM job templates. Never wait >15 min on a login node when SLURM exists.

### 7.4 Multiprocessing Safety

When using `ProcessPoolExecutor` with libraries that use OpenMP or other
threading (fastjet, ROOT, numpy with MKL), always set the start method
to `forkserver` or `spawn`:

```python
import multiprocessing
multiprocessing.set_start_method("forkserver", force=True)
```

The default `fork` method copies the parent process's thread state into
child processes. Libraries with active thread pools (OpenMP in fastjet,
Intel MKL in numpy) can produce silently wrong results — child processes
may return cached data from the parent instead of computing fresh
results. This bug is insidious because the output looks plausible
(correct types, reasonable magnitudes) but is numerically wrong.

**Validation rule:** After any parallel processing step that produces N
independent outputs, verify they are not trivially identical. If N
inputs produce N bit-for-bit identical outputs, this is a
multiprocessing bug, not a physics result.

### 7.5 Resolution Estimation

When computing detector resolution from a residual distribution (e.g.,
impact parameter d0 from the negative-significance side, or pull
distributions), **use a robust core estimator** — Gaussian fit to the
central peak, MAD-based sigma (σ = 1.4826 × MAD), or IQR-based sigma
(σ = 0.7413 × IQR). **Never use the RMS** as the resolution estimate.
Tracking residual distributions have heavy non-Gaussian tails from V0
decays (K_S, Λ), nuclear interactions in detector material, and
δ-rays. These tails contain 10–40% of tracks and inflate the RMS by
factors of 10–20× relative to the core resolution. Report both the
RMS and the core sigma in the artifact to document the tail fraction,
but use the core sigma for significance calculations and tagging.

### 7.6 Calibration Verification

**Every calibration must have a before/after comparison.** When applying
any correction to a quantity (beam spot correction to d0, energy scale
to jet pT, tracking efficiency scale factor, MC reweighting), produce
a plot showing the distribution before and after the correction. The
correction must visibly improve the relevant distribution — narrower
residuals, better data/MC agreement, or reduced bias. If a correction
*widens* a distribution or *worsens* data/MC agreement, the correction
is wrong (e.g., the quantity is already corrected at reconstruction
level). Do not apply corrections without verifying their effect.

This is particularly important for archival data where the processing
chain is not fully documented. Track parameters (d0, z0) may already
be corrected for the beam spot or primary vertex position at the
reconstruction stage. Applying the correction again (double-correction)
produces unphysical results. The verification plot catches this
immediately.

---
