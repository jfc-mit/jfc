## 7. Tools and Paradigms

The agent uses standard HEP software. No bespoke analysis framework is
required, but the following tools and paradigms are preferred. This section
is maintained by the analysis team and reflects operational knowledge about
what works well in practice.

### 7.1 Preferred Tools

| Capability | Tool | Notes |
|-----------|------|-------|
| ROOT file I/O | uproot | Pythonic, no ROOT install required. Use `uproot.open()` to explore, `arrays()` to load. |
| Array operations | awkward-array, numpy | Columnar analysis — no event loops. awkward for jagged structure, numpy for flat. |
| Histogramming | hist, boost-histogram | Use `hist` for building and plotting; `boost-histogram` for performance-critical fills. Leverage ND histogram axes for systematic variations and cut categories — store variations as axis dimensions rather than separate histograms. |
| Statistical model | pyhf | HistFactory JSON workspaces. Portable, text-based, version-controllable. |
| Fitting / limits | pyhf, cabinetry | cabinetry for convenience wrappers (ranking, pulls). pyhf directly for custom fits. |
| MVA | xgboost, scikit-learn | BDTs via xgboost. scikit-learn for preprocessing, train/test split, metrics. |
| Hyperparameter opt | optuna | Bayesian optimization. Pin `random_state=42` for reproducibility. |
| Plotting | matplotlib, mplhep (≥1.1) | Use a built-in `mplhep.style` if one exists for the experiment. If not, build a custom style using mplhep's generic style primitives (e.g., `mplhep.style.CMS` as a base, overriding experiment name, logo, fonts). mplhep ≥1.1 exposes the building blocks for constructing experiment styles programmatically. **Never use another experiment's style unmodified.** No figure titles — use captions. See Section 5 for full figure standards. All figures as PDF. |
| Event processing | coffea | Standard workhorse for columnar analysis. Handles chunked I/O, accumulation, and scale-out. Use `PackedSelection` for cutflow management. Preferred over hand-rolled event loops. |
| Scale-out | coffea + parsl/slurm | coffea with parsl or dask-jobqueue for slurm submission. This is the standard production path for large-scale processing. Local execution is fine for development and small datasets. |
| Jet clustering | fastjet | Python bindings via `fastjet`. For e+e− (LEP): Durham algorithm (`ee_genkt_algorithm`, p=−1). For pp (LHC): anti-kt. Use e+e− algorithms for e+e− data — pp-era algorithms assume beam remnants. |
| b-tagging | tiered (see below) | No pre-built tagger for ALEPH. Agent builds taggers during Phase 2 — see tiered tagging guidance below. |
| Dependency mgmt | pixi | All dependencies managed via pixi (conda-forge + pypi). `pixi.toml` / `pyproject.toml` is the single source of truth for the environment. |
| Logging | logging + rich | Python `logging` with `rich.logging.RichHandler`. No bare `print()`. See Section 11 for setup and enforcement. |
| Document preparation | LaTeX | pdflatex + bibtex. Markdown acceptable for intermediate artifacts. |
| Experiment knowledge | RAG (SciTreeRAG) | Retrieval over publication/thesis corpus. See Section 2.2. |

**Tiered tagging and classification.** When building taggers or classifiers
(b-tagging, tau-ID, quark/gluon, etc.), follow a tiered approach:

1. **Cut-based (cross-check).** Always build a simple cut-based version first
   using the most discriminating variables (e.g., impact parameter significance,
   secondary vertex mass for b-tagging). This serves as the baseline and
   independent cross-check — it should always exist even if a more powerful
   method is used as the primary.
2. **BDT (default primary).** A shallow BDT via xgboost on a handful of
   well-understood inputs is typically the right primary tagger. Fast to train,
   easy to interpret, robust with limited MC statistics. This is the expected
   choice for ALEPH/LEP-scale analyses.
3. **Neural networks (only if justified).** FCNs or GNNs are warranted only
   when the input space is large enough to benefit (many correlated low-level
   inputs) and sufficient MC is available for training. At LHC scale with
   millions of training events and dozens of inputs, this can be transformative.
   For ALEPH-scale analyses, a BDT will almost always suffice.

The agent defines working points during Phase 2 exploration based on the
efficiency vs. rejection trade-off in MC, then validates on data in Phase 3.

### 7.2 Paradigms

**Prototype on a slice, scale up when it works.** Never run on the full
dataset first. Every new script, selection, or processing step should be
developed and validated on a small subset (~1000 events or a single file)
before scaling to the full sample. This applies at every phase:
- **Exploration:** Load one file, check branches and distributions. Do not
  process 22GB of ROOT files to "see what's there."
- **Selection development:** Optimize cuts on a small slice. Only run the
  full cutflow once the logic is validated.
- **MVA training:** Prototype the feature pipeline on a subset. Only train
  on the full sample once the pipeline runs clean.
- **Fit development:** Build and test the workspace on a few bins / one
  region before scaling to the full model.

The pattern is: get the code right on a small sample where iteration is
cheap (seconds, not hours), then run once at scale. If a step takes more
than a few minutes, ask whether a subset would answer the same question.
The full dataset is for production runs, not for debugging.

**Read the API before working around it.** When a tool or library behaves
unexpectedly, the first action is ALWAYS to read the function's docstring or
documentation — not to hack around the behavior. Most "unexpected" behavior
is a documented feature with a documented parameter to control it. The
pattern of seeing unwanted output → wrapping it in post-hoc fixups →
creating brittle code that breaks on the next call is a common agent
failure mode. Concretely:
- Before calling a function with workarounds, run `help(function)` or read
  the source to check if there's a kwarg that does what you want.
- Before writing code to undo a library's default behavior, check if there's
  a configuration option or style parameter.
- If the tool is listed in Appendix C (Tool Heuristics), check there first.
  If it's not, query the docs, solve the problem correctly, and add the
  idiom to Appendix C so the next session doesn't repeat the mistake.

The 30 seconds spent reading a docstring saves minutes of debugging
cargo-culted workarounds.

**Columnar analysis.** Operate on arrays of events, not event-by-event loops.
Selections are boolean masks applied to arrays. This is faster, more readable,
and less error-prone than loop-based code.

**Immutable cuts.** Express selections as a sequence of named boolean masks.
Never modify the underlying arrays — apply masks to produce filtered views.
This makes cutflows trivial (count `True` values at each stage) and cuts
composable (AND masks for combined selections).

**Workspace as artifact.** The statistical model (pyhf JSON workspace) is a
version-controlled artifact, not ephemeral in-memory state. Write it to disk.
Validate it. Commit it. Downstream steps read the workspace file.

**Plots are evidence.** Every claim in an artifact should have a corresponding
figure or table. Plots are not decoration — they are the primary evidence that
the analysis is correct. Label axes with units. Include ratio panels for
data/MC comparisons. Use consistent styling throughout.

**Reproducibility by default.** Pin random seeds. Record software versions in
artifact code-reference sections. Scripts should be re-runnable from a clean
state and produce identical outputs.

**Event weighting and MC normalization.** During event processing, the
processor tracks the sum of MC generator weights (Σw) for each sample. After
processing, templates are normalized to the target luminosity:
weight_per_event = σ × L / Σw_generated. This reweighting step is cheap and
happens after the event loop, not inside it. The resulting yields are a nominal
estimate — the real process normalizations are calibrated in-situ by fits in
control regions during Phase 4. For generators with negative weights (NLO), Σw
is the algebraic sum (positives minus negatives), not the count.

**Systematic variation naming.** Use the convention `{source}Up` /
`{source}Down` for systematic variation branches or histogram suffixes (e.g.,
`JES_Up`, `JES_Down`). This is the standard expected by pyhf and cabinetry
for automatic workspace construction.

**Binning.** Start with uniform binning during exploration. Before fitting,
rebin to ensure adequate statistics — no bin should have fewer than ~5 expected
events (summed over all processes) to avoid fit instabilities. Variable binning
is fine when physically motivated (e.g., finer bins near a mass peak, coarser
in tails).

### 7.3 Retrieval

The agent has access to a SciTreeRAG system over the experiment's publication
corpus (~2,400 ALEPH and DELPHI papers) via MCP tools. The primary tool is
`search_lep_corpus` for hybrid dense + BM25 retrieval; use
`compare_measurements` when cross-checking between experiments. See Section 2.2
for retrieval expectations and `.mcp.json` for server configuration.

---
