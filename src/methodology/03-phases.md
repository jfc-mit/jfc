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
- **Selection approach exploration plan.** Phase 1 defines which approaches
  to explore — not which single approach to use. The strategy must identify
  at least two candidate selection approaches and commit to trying both in
  Phase 3. For each candidate, state the expected advantages, known costs,
  and what a quantitative comparison would look like. Phase 3 performs the
  exploration and selects based on evidence. Declaring a single approach
  without a comparison plan is acceptable only when the strategy documents
  why alternatives are infeasible (not merely suboptimal) — and the Phase 1
  review must validate this justification.
- **Method parity with published analyses (binding).** When reference
  analyses are identified, the strategy must compare the proposed method
  to the method used in those publications — not just the systematics,
  but the statistical extraction method itself. If published analyses
  used a more sophisticated method (e.g., differential fit vs mean value,
  NLO+NLL vs NLO, profile likelihood vs chi2), the strategy must either:
  (a) commit to using the same or better method, or (b) justify why a
  simpler method is adequate AND commit to implementing the published
  method as a cross-check. "We use the simpler method because it's
  easier" is not a justification. "We use the simpler method because
  [specific technical limitation], with the published method as a
  planned cross-check" is acceptable.

  This is a binding commitment reviewed at Phase 4a. Silent downscoping
  to a simpler method than what published analyses used — without
  documenting the decision and implementing the published method as a
  cross-check — is Category A at review.
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

**Methodology diagrams.** Identify where conceptual diagrams would help
a reader understand the analysis flow. Apply the figure-scrolling test:
if a reader scrolling through the AN figures would encounter a non-trivial
method (correction chain, sample merging, region definitions) with no
visual explanation, plan a diagram. List planned diagrams with their
target AN sections. These are produced in Phase 5.

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
- **Data/MC agreement on candidate variables.** For every variable that
  may enter a classifier or selection, produce a data/MC comparison and
  report the chi^2/ndf. This survey is an input to Phase 3's variable
  quality gate — variables with poor data/MC agreement should be flagged
  here so Phase 3 can decide to discard or calibrate them before
  training any MVA.
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
- For multi-dimensional selection, use a method that exploits correlations
  between variables. Document why if using a simpler approach. Read how
  reference analyses handled the same selection.
- **Approach comparison (mandatory).** Phase 3 must try at least two
  selection approaches and compare them quantitatively before choosing one.
  The comparison must use a common figure of merit evaluated on the same
  sample. Document in the artifact: what was tried, the figure of merit for
  each, and why the chosen approach is preferred. The only acceptable
  exemption is when Phase 1 documented that alternatives are infeasible AND
  the Phase 1 review validated this.
- **Input variable quality gate (MVA analyses).** Before training any
  classifier, produce a variable survey table for all candidate input
  features:

  | Variable | Flavour discrimination | Data/MC chi^2/ndf | Decision |
  |----------|----------------------|----------------|----------|

  Each candidate input must pass both a discrimination check (contributes
  to signal/background separation) and a modelling check (data/MC
  agreement). Variables with data/MC chi^2/ndf > 5 should be discarded
  unless (a) they provide exceptional discrimination AND (b) a
  data-driven calibration (reweighting, scale factor) is applied and
  validated. A poorly-modelled input that enters the classifier will
  produce a biased result on data even if MC closure passes — the
  closure test cannot catch data/MC mismodelling by construction.

  Training alternative classifier architectures or feature combinations
  during exploration is expected — the experiment log records what was
  tried. But the AN documents the variable survey, the selection
  rationale, the final classifier, and the result — not every
  intermediate training attempt.
- If MVA: train, validate, optimize. Train >=1 alternative architecture.
  Try multiclass if >2 physics classes. Check data/MC on classifier output.
  Sub-delegate training to sub-agent (§3a.5). Diagnostic plots (ROC, score
  distributions, feature importance) are AN-bound — save as figures for
  Phase 5 aggregation.
- Every cut must be motivated by a plot. N-1 distributions preferred
  (apply all cuts except the one being shown). Document sensitivity to
  cut variation. Cutflows should be monotonically non-increasing.
  Unexplained increases warrant investigation.

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
  < 50%, investigate — read how published analyses of the same or
  similar observable constructed their response matrix. A low diagonal
  fraction may indicate a methodological choice (e.g., wrong matching
  strategy) rather than a fundamental limitation of the observable.
  Do not conclude that unfolding is impossible without checking how
  published analyses handled the same correction.
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

Attempt >=3 independent remediation approaches. Read how published analyses
of the same or similar observable solved the problem. Document all attempts
in the experiment log. Only after 3+ remediation attempts have been tried
and documented may the failure be accepted. Accepting a validation failure
without remediation attempts is Category A at review.

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
Systematically explore qualitatively different strategies. Document each
approach and its limiting factor. Stop when the goal is met or diminishing
returns are evident (3+ approaches, <10% relative improvement).

**Method health assessment (measurements).** The Phase 3 artifact must
include an explicit "Is the method working?" section answering:
1. Does the closure test converge to chi2/ndf ~ 1 with a stable plateau
   spanning >= 2 iterations/parameter values?
2. Does the stress test pass at the level of expected data/MC differences?
   (Not just at 50% tilt — characterize the resolving power.)
3. Does the flat-prior test leave > 50% of bins with < 20% shift?
4. Is the alternative method viable (closure chi2/ndf < 5)?
5. Are the validation tests non-tautological? A closure test that applies
   the correction to MC reco-level and compares to MC truth is legitimate
   (it should give chi2/ndf ~ 1). But a test where the result is
   *algebraically guaranteed* — e.g., applying BBB correction factors
   derived from sample X back to sample X (identity), or a linearity
   test whose residual is zero by construction — has no diagnostic power.
   If any validation gives chi2/ndf < 0.1 or residuals exactly zero,
   check whether the result follows from the algebra rather than from
   the data. The test must be capable of failing to be informative.

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
- **Extraction method hierarchy (parameter measurements).** When
  extracting a physical parameter (coupling constant, mass, width) from
  a measured distribution, the extraction method must use ALL available
  information. The hierarchy, from best to acceptable:

  1. **Differential fit** (default): fit the theory prediction to the
     binned corrected distribution using the full covariance matrix.
     This uses shape information and is less sensitive to power
     corrections and endpoint effects than scalar summaries.
  2. **Moment fit**: fit to one or more moments (mean, variance) of
     the distribution. Acceptable when the differential prediction
     is unavailable or when the moment has a cleaner theoretical
     interpretation.
  3. **Total rate / mean value**: extract from a single number
     (total cross-section, mean of a distribution). Acceptable only
     as a cross-check, or when the distribution is not corrected
     (e.g., integrated luminosity measurement).

  When a corrected differential distribution AND its covariance matrix
  are available, using only the mean value for the primary extraction
  discards information and is a downscoping that must be justified.
  The differential fit is the default; the mean-value extraction is
  the cross-check. If the strategy committed to a mean-value method
  but the corrected distributions are available by Phase 4a, the
  executor must implement both and use the differential fit as primary.

- Construct binned likelihood (Asimov data, systematic terms)
- Validate: NP pulls small, fit converges, results sensible
- Signal injection tests (searches) or closure tests (measurements)
- GoF: chi2/ndf AND toy-based p-value (saturated model)
- **Fit boundary check.** After every fit, verify that no fitted
  parameter sits at or within 1% of its allowed boundary. A parameter
  at a boundary means the fit wants to go further — the reported
  uncertainty is a lower bound, not the true uncertainty. Either widen
  the bounds and refit, or document the boundary saturation and flag the
  affected uncertainty as a lower bound. This applies to physics
  parameters (signal strength, coupling constants) and nuisance
  parameters alike.
- For measurements: expected result from MC pseudo-data, never real data.
  See `conventions/extraction.md` for extraction-specific protocol.
- For measurements: full covariance matrix (stat + per-syst + total) +
  comparison to >=1 theory prediction using full covariance
- **MC-derived quantities require matching conditions.** Do not apply
  MC-derived quantities (efficiencies, corrections, scale factors)
  beyond the conditions they were derived from — whether different
  data-taking periods, detector configurations, or kinematic regions —
  without an uncertainty that reflects the extrapolation. If MC covers
  only a subset of the data, either restrict the measurement to that
  subset or justify applicability and size the uncertainty accordingly.

- **Per-systematic documentation depth.** Each systematic source in the
  artifact must be described in running prose covering: the physical
  origin (what detector or physics effect causes it), the evaluation
  method (how the variation was determined and justified), the numerical
  impact on each result parameter, and interpretation (dominant,
  subdominant, conservative? any caveats?). If an alternative evaluation
  was tried and failed, document what was tried and why, to prevent
  future analysts from repeating the same dead end. Write this as
  natural prose — do NOT use bold-labeled paragraph headings like
  "**Origin:**", "**Method:**", "**Impact:**". These make the document
  read like a form rather than an analysis note.
- **Phase 1 traceability.** Before finalizing the systematic table,
  re-read STRATEGY.md and verify every committed systematic source and
  variation was either implemented or formally downscoped (with a [D]
  label in the experiment log). Systematics added beyond Phase 1 must
  also be documented with justification. A systematic that was committed
  in Phase 1 but silently absent in Phase 4 is Category A.
- **Zero-impact sanity check.** If any systematic variation produces
  an impact of exactly zero (or < 0.01% relative), verify that the
  variation input is actually non-trivial: does the varied sample
  differ from nominal? Does the relevant branch/weight exist? A
  zero-impact systematic more often indicates a broken evaluation
  (missing branch, identical files, no-op variation) than a genuinely
  negligible effect. Document the verification or assign a conservative
  literature-based value.

**Artifact:** `INFERENCE_EXPECTED.md` + `ANALYSIS_NOTE_4a_v1.md` (complete
AN with all detail using expected-only results; 4b/4c update numbers,
Phase 5 polishes prose and typesets).

**PDF compilation is mandatory at 4a.** The AN must be compiled to a
publication-quality PDF before review begins. Separate the concerns of
statistical analysis, prose writing, and typesetting. The typesetting
workflow converts markdown to `.tex` (via pandoc), runs
`postprocess_tex.py` for deterministic structural fixes (margins, abstract,
references, table spacing, FloatBarrier, needspace, duplicate headers,
appendix, clearpage), then the typesetter does figure composition and
longtable conversion before compiling the `.tex` to PDF. The compiled PDF
is a review input — the 4-bot+bib review panel reads the PDF, not the
markdown.

**Review:** 4-bot+bib (§6).

#### Phase 4b: 10% Data Validation

**Goal:** Reality-check with 10% subsample + update AN with 10% results.

- 10% data (fixed seed), MC normalized to 10% luminosity
- Run full chain, evaluate GoF, NP pulls, impact ranking
- Compare to Phase 4a expected (overlay, chi2). Discrepancies documented.
- For extraction: include diagnostics sensitive to data/MC differences
  (not just the final quantity). See `conventions/extraction.md` check #5.
- **Update AN:** Update the AN (established in 4a) with 10% data results.
  Phases 4c/5 update results and finalize.

**Artifact:** `INFERENCE_PARTIAL.md` + `ANALYSIS_NOTE_4b_v1.md`.

**Figure reference verification (mandatory before PDF compilation).**
Before compiling the AN draft to PDF, verify all figure references
resolve to existing files:
```bash
grep -oP 'figures/[^)]+\.pdf' ANALYSIS_NOTE_4b_v*.md | sort -u | \
  while read f; do [ -f "$f" ] || echo "MISSING: $f"; done
```
Copy or symlink any missing figures from earlier phases into the output
figures directory. A missing figure is Category A — do not compile until
all references resolve.

**PDF compilation is mandatory at 4b.** The human gate requires a
publication-quality draft AN as a compiled PDF. The typesetting
subagent converts the updated markdown to `.tex`, runs
`postprocess_tex.py`, does figure composition and longtable conversion,
and compiles to PDF before the review panel and before the human sees
it. The human reviews the PDF, not markdown.

**Review:** 4-bot (§6) → **human gate** (§4.2).

#### Phase 4c: Full Data

**Goal:** Final results on full dataset.

- Full chain, post-fit diagnostics
- Compare to **both** 10% and expected. Flag >2-sigma disagreement with expected
  or disagreement with 10% beyond statistical scaling.
- Investigate anomalies (large NP pulls, poor GoF)
- **Re-evaluate systematics on full data.** The MC-derived systematic
  budget from Phase 4a is a starting point, not the final answer. For each
  systematic source that involves a scan or comparison across configurations
  (e.g., kappa values, binning schemes, alternative methods), re-evaluate
  on the full data. If the data-evaluated systematic differs from the MC
  evaluation by more than a factor of 2, the artifact must document the
  discrepancy and justify which evaluation is used. Transferring the entire
  systematic budget from MC to data without validation is a form of
  borrowed flat systematic — the same prohibition applies.
- **Configuration selection must include GoF.** When multiple analysis
  configurations are evaluated (kappa values, working points, binning
  schemes, fit variants), the primary configuration must satisfy both
  statistical precision AND goodness-of-fit. A configuration with
  chi2/ndf > 3 (p < 0.01) must not be selected as primary without:
  (a) investigation of the source of poor GoF, (b) documented
  justification that the GoF failure does not invalidate the result,
  (c) explicit comparison to configurations with acceptable GoF.
  Selecting a configuration solely for its small statistical error while
  ignoring fit quality is Category A. If the best-precision configuration
  has poor GoF, either fix the model, choose a configuration with
  acceptable GoF, or quote the result from the acceptable-GoF
  configuration with the poor-GoF configuration as a cross-check.
- **Fit pathologies must be investigated.** Parameter degeneracies,
  near-singular Hessians, near-flat likelihood directions, or parameters
  hitting boundaries are anomalies — not configuration choices. If a fit
  that worked on MC pseudo-data develops a pathology on full data, the
  artifact must document: what changed, why (e.g., a degeneracy exposed
  by higher statistics), and whether the pathology could affect the chosen
  configuration at even higher statistics or under different conditions.
  Silently switching to a different configuration without investigation
  is Category B.
- **Viability check (every reported measurement).** Before quoting
  any result — primary observable, secondary observable, or derived
  quantity — verify the extraction is meaningful. This applies to ALL
  measurements reported in the AN, not just the primary one. If a
  secondary measurement fails a viability criterion, either: (a)
  investigate and explain, (b) explicitly label as non-competitive with
  the failed criterion noted in the results text, or (c) remove from
  the results if it adds no information. Silently omitting the viability
  check for a secondary measurement is Category B. Verify:
  - If the total uncertainty exceeds 50% of the central value, or
    exceeds 10x the world-average precision, the measurement may lack
    resolving power. Document whether it can distinguish the SM from
    alternatives at any meaningful confidence.
  - If the central value deviates from a well-measured reference by
    more than 30% in relative terms, this triggers mandatory
    investigation per §6.8. When MC closure passes but data deviates,
    the first hypothesis is a calibration mismatch — follow the
    calibration-first protocol in §6.8.
  - If intermediate steps produce unphysical values (negative widths,
    imaginary couplings), the quantity should be documented as "not
    reliably extractable" rather than quoted with an inflated uncertainty.
  Quoting a result with a > 3-sigma pull OR > 50% relative deviation from a
  well-measured value without a quantitative explanation is not
  acceptable (§6.8).

**Machine-readable results (mandatory).** The Phase 4c executor must create
`phase5_documentation/outputs/results/` and populate it with JSON files
containing all numerical results: fitted parameters with uncertainties,
derived quantities, systematic shifts per source, covariance matrices, and
per-energy-point cross-sections. These are the single source of truth for
numbers in the AN — the note writer reads from these files, not from
prose artifacts.

**Artifact:** `INFERENCE_OBSERVED.md` + `ANALYSIS_NOTE_4c_v1.md`.

**AN update is mandatory at 4c.** The AN writing subagent updates the
AN with full data results (replacing 10% numbers from 4b). **PDF
compilation is mandatory at 4c** — the AN must be compiled to PDF
before review, matching the pattern at 4a and 4b (pandoc →
`postprocess_tex.py` → typesetter → tectonic). Every AN-producing
phase (4a, 4b, 4c, 5) compiles to PDF.

**Review:** 1-bot (§6).

---

### Phase 5: Documentation

**Goal:** Final analysis note — publication-quality, self-contained, 50-100 pages.

Phase 5 requires figure production, AN prose writing, and PDF typesetting.
These are separate concerns that depend on each other (figures → prose →
PDF). They may be separate agents or combined as context pressure requires.

**Figure production.** Produces any remaining AN-specific figures not
already generated in Phases 2-4 (e.g., per-cut distributions, per-
systematic impact plots). Reads data files, runs plotting scripts,
saves to `phase5_documentation/outputs/figures/`. **Flagship figures**
(defined in Phase 1 strategy) receive extra attention: tighter axis
limits, careful legend placement, considered color choices. These are
the figures that would appear in a journal paper. **Methodology
diagrams** planned in Phase 1 (correction chains, region schematics,
analysis flow charts) are also produced here — see `appendix-plotting.md`
for production guidelines.

**AN writing.** Reads ALL phase artifacts (strategy, exploration,
selection, inference) and the figures directory. Writes the complete AN
text to `phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md`. This concern
does NOT involve reading data files or writing code — it reads artifacts
and writes prose. The document must meet the completeness test: a physicist
unfamiliar with the analysis can reproduce every number from the AN alone.

**Typesetting.** Runs AFTER the AN is written. The typesetting concern:
- Runs `pandoc` to convert the markdown AN to `.tex` (not PDF):
  `pandoc ANALYSIS_NOTE_5_v1.md -o ANALYSIS_NOTE_5_v1.tex --standalone
  --include-in-header=../../conventions/preamble.tex
  --number-sections --toc --filter pandoc-crossref --citeproc`
- Runs `postprocess_tex.py` which handles all deterministic structural
  fixes automatically: margins, abstract→environment, references
  unnumbering, table spacing, FloatBarrier insertion, needspace,
  duplicate header removal, duplicate label removal, appendix insertion,
  and clearpage placement.
- The typesetter then reads the `.tex` and does judgment-requiring work:
  - **Combine related figures** into `\begin{figure}` environments
    with `\subfloat` or side-by-side `\includegraphics` where
    applicable (e.g., data/MC comparisons for related variables,
    systematic shift maps for similar sources). Use `\begin{figure*}`
    for full-width composites.
  - **Convert longtable to table** — ensure no column overflow, use
    `\resizebox` or `\small` for wide tables.
  - **Verify every section has prose** — no bare headings before
    figures.
  - **Check caption quality** — flag any caption under 2 sentences.
- Compiles the `.tex` to PDF via `tectonic ANALYSIS_NOTE_5_v1.tex` (or
  `pdflatex`). Fixes any compilation errors.
- Reads the compiled PDF and verifies: no broken figures, no
  unresolved cross-references, no overflow, no cut-off content.
- The final PDF is the deliverable, not the pandoc output.

**Typesetting does NOT modify physics content.** It changes only layout,
formatting, and figure grouping. It never changes numbers, captions
(except to fix grammar), or section structure. If it finds a physics
issue (e.g., missing figure, inconsistent number), it flags it for the
AN writer rather than fixing it.

See `analysis-note.md` for full AN specification.

**Artifact:** `ANALYSIS_NOTE_5_v1.md` + compiled PDF + `results/` directory.
**Review:** 5-bot (§6).

---
