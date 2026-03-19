## 3. Analysis Phases

Five sequential phases. Within a phase, **parallelize where possible** —
sub-delegate independent tasks (MVA training, systematics, plotting). See
§3a.5.

### 3.0 Artifact and Review Gates

**Every phase boundary is a hard gate.** Phase N+1 cannot begin until
Phase N has produced its artifact AND passed review (§6).

Gate protocol: (1) produce artifact → (2) update experiment log → (3)
review (§6) → (4) resolve Category A items → (5) advance.

Artifact existence is a precondition. Never skip an artifact, even under
context pressure — write the artifact and stop cleanly.

See §3a for orchestrator architecture. Phase CLAUDE.md templates (from
`templates/`) are the operational entry points agents read at runtime.

---

### Analysis Types

- **Search:** Signal/background, SR/CR structure, blinding (§4), limits or
  significance.
- **Measurement:** Corrected spectra, event shapes, extracted parameters.
  No S/B per se. Staged validation replaces blinding (§4).

Where phase descriptions reference search concepts (SR, CR, S/B),
measurements substitute: fiducial region, sidebands, purity optimization.

---

### Phase 1: Strategy

**Goal:** Written analysis strategy a collaboration reviewer could approve.

**The agent must:**
- Query experiment corpus for detector capabilities, prior work, datasets
- Identify signal process, backgrounds (classified: irreducible, reducible,
  instrumental), discriminating variables
- Propose selection approach, background estimation strategy, control regions
- **Technique justification:** Explicitly defend the chosen technique against
  alternatives (e.g., "double-tag vs single-tag because...", "bin-by-bin
  correction vs full unfolding because..."). A reader should understand not
  just what will be done, but why it was chosen over the alternatives.
- **Systematic plan:** read applicable `conventions/` document, enumerate
  every required source with "Will implement" or "Not applicable because
  [reason]." This is binding — Phase 4a reviews against it.
- Identify 2-3 reference analyses, tabulate their systematic programs
- **Constraint and limitation labels.** Throughout the strategy, label
  known constraints [A1], [A2], ..., known limitations [L1], [L2], ...,
  and key design decisions [D1], [D2], .... These labels propagate to
  later phases and the final AN. A constraint is a data/MC property that
  restricts what can be done; a limitation is a feature that weakens the
  result; a decision is a deliberate choice with alternatives.

**For measurements additionally:** Define observable(s), correction strategy,
prior measurements (validation target), theory predictions for comparison.
**Theory comparison independence:** The MC generators listed for comparison
must include at least one that is INDEPENDENT of the MC used to derive
the correction (response matrix, efficiency). Comparing the corrected
result to the same MC used for the correction is a closure check, not a
theory comparison. If no independent generator is available, document this
as a limitation and plan particle-level-only comparisons.

**Flagship figures.** Identify ~6 figures that would represent the
measurement in a journal paper — the "money plots." Examples: the final
spectrum with uncertainties, the response matrix, the key data/MC
comparison, the systematic breakdown, the theory overlay. These are
defined here in the strategy and produced at the highest quality in
Phase 5. The list propagates to the AN writing subagent.

**Artifact:** `STRATEGY.md`. **Review:** 4-bot (§6).

---

### Phase 2: Exploration

**Goal:** Characterize data, validate detector model, establish selection
foundation.

**The agent must:**
- Inventory samples (files, trees, branches, events, cross-sections)
- Validate data quality (pathologies, outliers, unphysical values)
- Apply standard object definitions (from corpus), verify data/MC agreement
- Survey discriminating variables, rank by separation power
- Establish baseline yields after preselection

**Data discovery:** Metadata first → small slice (~1000 events) → identify
jagged structure → document schema.

**PDF build test (independent):** Stub `pixi run build-pdf` to verify
toolchain. Can run in parallel.

**Artifact:** `EXPLORATION.md`. **Review:** Self-review (§6).

---

### Phase 3: Processing

**Goal:** Implement the strategy. Searches: selection, regions, background
estimation. Measurements: selection, correction chain. Phase 3 executes
the plan; it does not redesign it.

**Selection:**
- Default to MVA (BDT, NN) for multi-dimensional classification. Cuts
  acceptable only for preselection, single-variable, or tiny samples (<1000).
- If MVA: train, validate, optimize. Train ≥1 alternative architecture.
  Try multiclass if >2 physics classes. Check data/MC on classifier output.
  Sub-delegate training to sub-agent (§3a.5).
- Every cut must be motivated by a plot. Cutflow must be monotonically
  non-increasing (Category A if violated).

**Regions (searches):** Define CRs (enriched in backgrounds) and VRs
(between CR and SR, statistically independent).

**Background estimation (searches):** Estimate SR yields from CRs. Closure
test in VRs (p > 0.05 or Category A).

**Correction infrastructure (measurements):**
- Data/MC comparisons for all variables entering the observable, resolved
  by object category (Category A if missing for unfolded measurements)
- Response matrix: dimensions, diagonal fraction, condition number, efficiency
- **Early diagonal fraction check (gate).** Before building the full
  correction chain, compute the response matrix on a small MC subset
  (~10K events) and report the diagonal fraction. If diagonal fraction
  < 50%, trigger an immediate strategy reassessment: consider coarser
  binning, SVD unfolding, or dimensionality reduction BEFORE investing
  in full-scale processing. Do not build a complete BBB chain and
  discover at the end that the method is invalid.
- Closure + stress tests on MC. Failure (p < 0.05) is Category A.
- Prototype full chain on data.
- Binning must be justified (resolution, statistics, physics features).

**Validation failure remediation (measurements).** When a required
validation test fails (stress test, flat-prior test, alternative method
closure), the failure must NOT be accepted at face value. The executor
must attempt **at least 3 independent remediation approaches** before
documenting the failure as a limitation. At least one attempt should use
a **minimal-context subagent** — a fresh agent given only the problem
statement and data, without the prior failed attempts in context, to get
an unbiased perspective.

Remediation hierarchy for unfolding:
1. Adjust regularization (more/fewer iterations, different parameter)
2. Modify binning (coarser, variable-width, restrict range to
   well-populated region)
3. Try a data-driven prior (use reco-level data shape as IBU starting
   point instead of MC truth)
4. Try an entirely different unfolding method
5. Reduce dimensionality (2D → 1D projections)

Only after 3+ remediation attempts have been tried and documented in the
experiment log may the failure be accepted. Accepting a validation
failure without remediation attempts is Category A at review.

**Wholesale bin exclusion is a red flag.** If a flat-prior gate or
similar criterion excludes more than 50% of the measurement bins, this
indicates a fundamental problem with the binning, regularization, or
method — not a legitimate systematic effect. This triggers mandatory
re-evaluation of the binning choice and/or method before proceeding.
Exclusion is appropriate for edge bins with genuine kinematic boundary
effects (e.g., the upper corner of a Dalitz plot), not for central bins
that are simply poorly constrained.

**Background estimation flow:** Phase 1 defines approach → Phase 2
validates feasibility → Phase 3 builds estimation inputs for Phase 4.

**Sensitivity optimization (when insufficient):** Maintain `sensitivity_log.md`.
Progress through qualitatively different strategies (optimize current → more
powerful discriminant → different inference strategy → revisit regions).
Stop when goal met OR 3+ approaches tried with marginal improvement.

**Method health assessment (measurements).** The Phase 3 artifact must
include an explicit "Is the method working?" section answering:
1. Does the closure test converge to chi2/ndf ≈ 1 with a stable plateau
   spanning ≥ 2 iterations/parameter values?
2. Does the stress test pass at the level of expected data/MC differences?
   (Not just at 50% tilt — characterize the resolving power.)
3. Does the flat-prior test leave > 50% of bins with < 20% shift?
4. Is the alternative method viable (closure chi2/ndf < 5)?

If ANY of these fail, the method needs redesign or the binning needs
adjustment before proceeding to Phase 4. Document what was tried
(minimum 3 remediation attempts per failure) and what the resolution was.

**Artifact:** `SELECTION.md`. **Review:** 1-bot (§6).

---

### Phase 4: Statistical Analysis

Three sub-phases. **Both measurements and searches follow 4a → 4b → 4c.**

#### Phase 4a: Expected Results

**Goal:** Systematics, statistical model, expected results on Asimov only.

- Evaluate experimental + theory systematics as rate/shape variations.
  **Variation sizing:** every systematic variation must be motivated by
  a measurement, calibration, or published uncertainty — not an arbitrary
  round number. "±50% on the background" is not acceptable unless 50% is
  the measured uncertainty on the background estimate. If the background
  is estimated from a sideband fit with 12% uncertainty, use ±12%. If
  from MC with a 20% normalization uncertainty, use ±20%. Arbitrary
  inflations ("conservative ±50%") mask the analysis's actual sensitivity
  and are Category A at review.
- **No borrowed flat systematics.** Borrowing systematic values from a
  different analysis as flat percentages is NOT a propagation. Every
  systematic must be evaluated by varying the source and re-running
  the affected part of the analysis chain to produce bin-dependent
  shifts. Flat estimates are acceptable ONLY when (a) the source is
  confirmed subdominant AND (b) a proper propagation is infeasible
  AND (c) the flat value is justified by a cited measurement — with
  all three conditions documented in the artifact. A perfectly flat
  relative shift across all bins of a shape measurement is physically
  suspect and likely indicates the systematic was not propagated.
- Construct binned likelihood (Asimov data, systematic terms)
- Validate: NP pulls small, fit converges, results sensible
- Signal injection tests (searches) or closure tests (measurements)
- GoF: chi2/ndf AND toy-based p-value (saturated model)
- For measurements: expected result from MC pseudo-data, never real data.
  See `conventions/extraction.md` for extraction-specific protocol.
- For measurements: full covariance matrix (stat + per-syst + total) +
  comparison to ≥1 theory prediction using full covariance

- **Per-systematic documentation depth.** Each systematic source in the
  artifact must include: (a) physical origin — what detector or physics
  effect causes this, (b) evaluation method — how the variation was
  determined and justified, (c) numerical impact on each result parameter,
  (d) interpretation — is this dominant, subdominant, conservative? Any
  caveats or capping? (e) failed attempts — if an alternative evaluation
  was tried and failed, document what was tried, why it failed, and how
  the fallback was chosen. Failed attempts are valuable because they
  prevent future analysts from repeating the same dead end.

**Artifact:** `INFERENCE_EXPECTED.md`. **Review:** 4-bot (§6).

#### Phase 4b: 10% Data Validation

**Goal:** Reality-check with 10% subsample + produce draft AN.

- 10% data (fixed seed), MC normalized to 10% luminosity
- Run full chain, evaluate GoF, NP pulls, impact ranking
- Compare to Phase 4a expected (overlay, chi2). Discrepancies documented.
- For extraction: include diagnostics sensitive to data/MC differences
  (not just the final quantity). See `conventions/extraction.md` check #5.
- **Draft AN:** Complete AN per `analysis-note.md`. Structure written here;
  Phases 4c/5 update results only.

**Artifact:** `INFERENCE_PARTIAL.md` + `ANALYSIS_NOTE_DRAFT.md`.
**Review:** 4-bot (§6) → **human gate** (§4.2).

#### Phase 4c: Full Data

**Goal:** Final results on full dataset.

- Full chain, post-fit diagnostics
- Compare to **both** 10% and expected. Flag >2σ disagreement with expected
  or disagreement with 10% beyond statistical scaling.
- Investigate anomalies (large NP pulls, poor GoF)
- **Derived quantity viability check.** Before quoting a derived quantity
  (e.g., α_s from Γ_had, N_ν from Γ_inv), verify the extraction is
  meaningful: does the primary measurement have sufficient precision to
  constrain the derived quantity? If the propagated uncertainty exceeds
  10× the world-average precision, or if intermediate steps produce
  unphysical values (negative widths, imaginary couplings), the derived
  quantity should be documented as "not reliably extractable from this
  measurement" rather than quoted with an inflated uncertainty. Quoting
  a result with a > 3σ pull from a well-measured value without a
  quantitative explanation of the tension is not acceptable (§6.8).

**Artifact:** `INFERENCE_OBSERVED.md`. **Review:** 1-bot (§6).

---

### Phase 5: Documentation

**Goal:** Final analysis note — publication-quality, self-contained, 50-100 pages.

Phase 5 has three distinct sub-tasks that should be handled by **separate
subagents** (the AN is context-intensive and must not compete for context
with figure generation or data processing):

1. **Figures subagent.** Produces any remaining AN-specific figures not
   already generated in Phases 2-4 (e.g., per-cut distributions, per-
   systematic impact plots). Reads data files, runs plotting scripts,
   saves to `phase5_documentation/exec/figures/`. This is a code-writing
   agent. **Flagship figures** (defined in Phase 1 strategy) receive
   extra attention: tighter axis limits, careful legend placement,
   considered color choices. These are the figures that would appear in
   a journal paper.

2. **AN writing subagent.** Reads ALL phase artifacts (strategy, exploration,
   selection, inference) and the figures directory. Writes the complete AN
   text to `phase5_documentation/exec/ANALYSIS_NOTE.md`. This agent does
   NOT read data files or write code — it reads artifacts and writes prose.
   It must produce a document that meets the completeness test: a physicist
   unfamiliar with the analysis can reproduce every number from the AN alone.

3. **Typesetting subagent.** Runs AFTER the AN writing subagent. This agent
   is a LaTeX typesetting expert. It:
   - Runs `pandoc` to convert the markdown AN to `.tex` (not PDF):
     `pandoc ANALYSIS_NOTE.md -o ANALYSIS_NOTE.tex --standalone
     --include-in-header=../../conventions/preamble.tex
     --number-sections --toc --filter pandoc-crossref --citeproc`
   - Reads the generated `.tex` file and improves the typesetting:
     - **Combine related figures** into `\begin{figure}` environments
       with `\subfloat` or side-by-side `\includegraphics` where
       applicable (e.g., data/MC comparisons for related variables,
       systematic shift maps for similar sources, reco vs gen Lund
       plane). Use `\begin{figure*}` for full-width composites.
     - **Fix float placement** — ensure no figure overflows the page,
       add `\clearpage` before dense figure sequences if needed.
     - **Adjust table formatting** — ensure no column overflow, use
       `\resizebox` or `\small` for wide tables, add `\toprule`,
       `\midrule`, `\bottomrule` from booktabs if pandoc didn't.
     - **Verify every section has prose** — no bare headings before
       figures.
     - **Check caption quality** — flag any caption under 2 sentences.
     - **Optimize page breaks** — prevent awkward orphaned section
       headings at the bottom of pages.
     - **Add `\FloatBarrier`** at section boundaries to prevent figures
       from drifting too far from their text.
   - Compiles the `.tex` to PDF via `tectonic ANALYSIS_NOTE.tex` (or
     `pdflatex`). Fixes any compilation errors.
   - Reads the compiled PDF and verifies: no broken figures, no
     unresolved cross-references, no overflow, no cut-off content.
   - The final PDF is the deliverable, not the pandoc output.

   **The typesetting agent does NOT modify physics content.** It changes
   only layout, formatting, and figure grouping. It never changes
   numbers, captions (except to fix grammar), or section structure. If
   it finds a physics issue (e.g., missing figure, inconsistent number),
   it flags it for the AN writing agent rather than fixing it.

The execution order is: figures → AN writing → typesetting → 5-bot review.
The orchestrator should spawn each in sequence since each depends on the
previous output.

See `analysis-note.md` for full AN specification.

**Artifact:** `ANALYSIS_NOTE.md` + compiled PDF + `results/` directory.
**Review:** 5-bot (§6).

---
