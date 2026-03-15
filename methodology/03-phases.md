## 3. Analysis Phases

The analysis proceeds through five phases. Dependencies between phases are
sequential — each phase consumes artifacts from prior phases. Within a phase,
work may be parallelized at the agent's discretion.

### 3.0 Artifact and Review Gates

**Every phase boundary is a hard gate.** The agent must not begin Phase N+1
until Phase N has produced its required artifact AND the required review has
been performed. This applies regardless of execution mode (orchestrated
multi-agent or single-session).

**The gate protocol:**
1. Phase executor produces the phase artifact (written to disk as markdown)
2. Phase executor updates the experiment log with what was done
3. The required review is performed (see Section 6)
4. Review findings are addressed (Category A items resolved)
5. Only then does the next phase begin

**Artifact existence is a precondition.** If Phase 2 has no `EXPLORATION.md`
on disk, Phase 3 must not start. If Phase 4 has no `INFERENCE_EXPECTED.md`,
Phase 4b must not start. The artifact is both the handoff document and the
proof that the phase was completed with appropriate rigor.

**Why this is a hard rule:** Without artifact gates, agents compress or skip
phases to reach results faster. The result is an analysis with no audit trail,
no intermediate review, and gaps that compound. The artifacts exist to force
the agent to consolidate what it knows before moving on — the act of writing
the artifact surfaces gaps that coding alone does not.

Skipping a phase artifact is never acceptable, even under context pressure.
If context limits are approaching, the agent should write the artifact for the
current phase, commit, and stop — not rush through remaining phases without
artifacts.

### 3.0.1 Single-Session Execution via Subagent Delegation

When a single agent session runs the full analysis, it operates as a **thin
orchestrator** that delegates work to subagents. The orchestrator's context
stays small; the heavy work happens in subagent contexts that are discarded
after each phase. This is the primary defense against context exhaustion.

**Architecture:** The main session (orchestrator) never writes analysis code
or produces figures itself. It spawns subagents for execution and review,
reads their summaries, makes phase-transition decisions, and commits. Each
subagent reads upstream artifacts from disk — not from the parent's context.

**The orchestrator loop for each phase:**

```
for each phase in [1, 2, 3, 4a, 4b, 4c, 5]:

  1. EXECUTE — spawn a phase executor subagent with:
     - The physics prompt
     - The phase CLAUDE.md (read from disk, pass in prompt)
     - Paths to upstream artifacts (the subagent reads them from disk)
     - The experiment log path (subagent appends to it)
     - The conventions document path (for phases that need it)
     - Explicit instruction to write the phase artifact to disk

  2. REVIEW — spawn a reviewer subagent with:
     - Path to the phase artifact just written
     - The review criteria for this phase (from Section 6.4)
     - The conventions document path
     - Instruction to write REVIEW_NOTES.md in the phase directory

  3. CHECK — orchestrator reads the review findings (short).
     If Category A issues exist:
       - Spawn a fix agent with the artifact + findings
       - Re-review after fix
     If no Category A issues: proceed.

  4. COMMIT — orchestrator commits the phase's work.

  5. ADVANCE — proceed to next phase.
```

**Why subagents solve context exhaustion:**
- The Phase 2 executor agent processes 40 MC files, debugs ROOT branch
  names, produces 12 figures. This consumes 50k+ tokens of context. When it
  finishes and returns a 500-token summary, all that bulk is gone. The
  orchestrator's context grows by 500 tokens, not 50k.
- By Phase 5, the orchestrator has accumulated only ~5k tokens of phase
  summaries. It has full context budget to spawn the AN-writing agent with a
  detailed prompt.
- If the orchestrator itself hits context limits despite staying thin, the
  committed artifacts + experiment log on disk are a complete checkpoint.
  A new session can read them and resume from the last committed phase.

**Subagent prompt templates:**

*Phase executor prompt (adapt per phase):*
```
You are executing Phase N of a HEP analysis. Read the methodology and
follow it exactly.

Analysis directory: analyses/<name>/
Phase CLAUDE.md: <path> (read this first)
Upstream artifacts to read from disk: <list of paths>
Experiment log: <path> (append your findings as you work)
Conventions: <path> (consult for systematic requirements)

Your deliverables:
1. Scripts in phase*/scripts/ that produce all required figures and results
2. The phase artifact: phase*/exec/<ARTIFACT_NAME>.md
3. Updated experiment_log.md with material decisions and discoveries
4. Updated pixi.toml tasks for any new scripts

Write the artifact LAST, after all scripts run and results are on disk.
The artifact summarizes and references the results — it is not a plan.

[Insert physics prompt here]
```

*Reviewer prompt (adapt per phase):*
```
You are reviewing Phase N of a HEP analysis. You are a critical reviewer —
your job is to find what is MISSING, not just check what is present.

Read the artifact: <path>
Read the conventions: <path>
Read the reference analyses in the strategy: <path to STRATEGY.md>

Apply the review focus from methodology Section 6.4 for this phase.
Check the artifact against the checklist in methodology Appendix B.

For each finding, classify as:
  (A) Must resolve — blocks advancement
  (B) Should address — weakens but doesn't invalidate
  (C) Suggestion — style, clarity

Write your findings to: phase*/review/REVIEW_NOTES.md

The key question: "What would a knowledgeable referee ask for that
isn't here?"
```

*3-bot review (for phases requiring it):*
Spawn three reviewer agents in parallel:
1. Critical reviewer — "find everything wrong or missing"
2. Constructive reviewer — "what would make this stronger"
3. Arbiter — reads both reviews, issues PASS / ITERATE / ESCALATE

The arbiter's verdict determines whether the phase advances.

**What the orchestrator does NOT do:**
- Read full scripts or data files (subagents do this)
- Debug code (subagents do this)
- Produce figures (subagents do this)
- Write analysis prose (subagents do this)

The orchestrator reads: CLAUDE.md files, phase summaries returned by
subagents, review findings, and the experiment log when deciding next steps.
It writes: commit messages and (if needed) the physics prompt passed to
subagents.

**Fallback: self-review.** If agent spawning is unavailable or impractical,
the orchestrator may perform review itself. In this case it must still:
- Read the artifact from disk (not from conversation memory)
- Apply the review criteria explicitly (Section 6.4)
- Write findings to REVIEW_NOTES.md
- This is strictly weaker than subagent review and should be a last resort

**Anti-pattern:** Running straight from Phase 1 to Phase 5 in a single pass,
producing only the strategy document and the final analysis note, with no
intermediate artifacts, no experiment log entries, and no reviews. This is
the failure mode the orchestrator pattern exists to prevent.

**Anti-pattern:** The orchestrator doing the phase work itself instead of
delegating. If the orchestrator is writing analysis scripts, it is not
orchestrating — it is executing, and its context will fill up.

---

### Analysis Types

The spec supports two analysis types. The physics prompt must declare which
type applies; the agent confirms this during Phase 1.

- **Search / limit-setting:** Signal vs. background discrimination, signal
  region / control region structure, blinding protocol (Section 4), expected
  limits or significance as the primary deliverable.
- **Measurement:** Corrected differential or inclusive cross-sections, event
  shape distributions, or extracted physical parameters (e.g., αs). No
  signal/background separation per se — the "signal" is the process being
  measured. Blinding may not apply (the observable is the result). The primary
  deliverable is a corrected spectrum or extracted parameter with full
  uncertainties.

Where phase descriptions below reference search-specific concepts (signal
region, control regions, S/B optimization), measurement analyses substitute
the analogous concepts: fiducial region, sideband/validation regions,
purity optimization. The review criteria adapt accordingly — e.g., "closure
test in VR" becomes "correction validation via cross-checks."

---

### Phase 1: Strategy

**Goal:** Produce a written analysis strategy that a collaboration reviewer
could approve.

**Inputs:** Physics prompt, experiment context (via retrieval).

**The agent must:**
- Query the experiment corpus to understand the detector capabilities, available
  datasets, and any prior work in the same or related channels
- Identify the signal process, production mechanism, and final state
- Enumerate principal backgrounds and classify them (irreducible, reducible,
  instrumental) with expected relative importance
- Propose an event selection approach with justification for the choice
- Define the discriminating variable(s) for the final statistical interpretation
- Specify the blinding variable and signal region boundaries (see Section 4)
- Outline the background estimation strategy per background and identify
  control regions needed
- List anticipated systematic uncertainty categories (experimental, theoretical).
  **Before finalizing the systematic plan,** read the applicable `conventions/`
  document and enumerate every required source. For each source, state whether
  it will be implemented and, if not, why not. This enumeration becomes the
  baseline that Phase 4a reviews against — sources omitted here without
  justification are Category A findings downstream.
- Identify which collision data and simulation samples are needed

**For measurement analyses,** the agent must additionally:
- Define the observable(s) to be measured and their physical interpretation
- Identify the correction/unfolding strategy (bin-by-bin, matrix inversion,
  iterative Bayesian, OmniFold) and what inputs it requires (response matrix,
  MC truth, etc.)
- Survey prior measurements of the same observable — identify published data
  points that will serve as the primary validation target
- Identify what theory predictions or MC generators can be compared to the
  corrected result

**Output artifact:** `STRATEGY.md` — a document covering the above points,
written at the level of an internal analysis note introduction. Quantitative
estimates (cross-sections, expected yields) should cite sources from the
retrieval corpus; order-of-magnitude estimates are acceptable where precision
is unavailable.

**Review:** See Section 6. Strategy review evaluates physics soundness,
completeness of background enumeration, and adequacy of the blinding plan.

---

### Phase 2: Exploration

**Goal:** Characterize the available data, validate the detector model, and
establish the foundation for event selection.

**Inputs:** Strategy, experiment context (via retrieval), data/MC samples.

**The agent must:**
- Inventory available samples (data and simulation): discover file locations,
  tree/branch structure, number of events, cross-sections, luminosity
- Validate data quality: check for pathologies (empty branches, outliers,
  discontinuities in distributions) and document findings
- Apply standard object definitions (retrieved from the experiment corpus) and
  verify agreement between data and simulation in inclusive distributions
- Survey discriminating variables: produce distributions of kinematic observables
  for signal and principal backgrounds, rank by separation power
- Establish baseline event yields after preselection

**Output artifact:** `EXPLORATION.md` — sample inventory, data quality summary,
variable ranking with distributions, preselection cutflow, and data/MC
comparison observations.

**Review:** See Section 6. Exploration review checks sample inventory
completeness, flags data quality issues, and assesses variable survey
thoroughness.

**Data discovery.** The agent should expect to discover the data format at
runtime — branch naming conventions, tree structures, and storage formats vary
across experiments and analyses. To avoid wasting time and memory:

1. **Metadata first.** Inspect tree names, branch names, and types before
   loading any event data (e.g., `uproot.open(f).keys()`, branch dtypes).
2. **Small slice of scalars.** Load ~1000 events of scalar branches first.
   Do not attempt to load all branches (especially jagged/variable-length)
   until you know the schema.
3. **Identify jagged structure.** Determine which branches are variable-length
   before bulk loading — these require awkward-array handling and consume
   more memory.
4. **Document the schema.** The discovered tree/branch structure, event counts,
   and any format quirks are themselves artifact content.

This discovery process is documented in the artifact.

---

### Phase 3: Selection and Modeling

**Goal:** Implement the analysis approach defined in the Phase 1 strategy.
For searches: define the selection, design control and validation regions,
estimate backgrounds, and validate the background model. For measurements:
define the selection and build the validated correction chain (response
matrix, unfolding, closure tests). The strategy determines which track
applies and what specific deliverables Phase 3 must produce — Phase 3
executes the plan, it does not redesign it.

**Inputs:** Strategy, exploration report, data/MC samples.

**The agent must:**

*Selection:*
- Implement event selection (preselection + final selection or MVA, as
  determined by the strategy and what the data supports)
- If using multivariate techniques: train, validate (overtraining checks), and
  optimize the classifier. Document feature importance and working point choice.
- If cut-based: optimize cut values with a figure of merit and document N-1
  distributions.
- Produce the final signal region definition and cutflow with efficiencies
- **Every cut must be motivated by a plot.** The artifact must include, for
  each selection cut, the distribution of the cut variable showing signal and
  background. The plot should make visually clear why this cut value was chosen
  — typically one of: "signal only exists above/below this threshold," "data
  quality degrades beyond this point," "this value maximizes purity while
  retaining sufficient statistics," or "this removes a specific background
  while preserving signal efficiency." A cut without a motivating plot is an
  unjustified cut.

*Regions (search analyses):*
- Define control regions enriched in each major background. Document purity and
  the kinematic relationship to the signal region.
- Define validation regions kinematically between control and signal regions for
  closure testing. These must be statistically independent of both CR and SR.

*Background estimation (search analyses):*
- Estimate background yields in SR using the chosen method per background
  (simulation-scaled-from-CR, data-driven, or pure simulation with justification)
- Perform closure tests in validation regions: compare predicted yields
  (extrapolated from CRs, not pure MC) to observation. Document agreement
  quantitatively. A closure test passes when agreement is consistent with
  statistical fluctuations (p-value > 0.05 under the relevant test statistic,
  typically chi2). A test that fails at p < 0.05 is Category A — investigate
  and iterate on the region design or estimation method before proceeding.

*Correction infrastructure (measurement analyses):*

For measurements, Phase 3 builds the correction chain rather than a
background model. The primary deliverable is a working, validated correction
pipeline — not yet the final measurement (systematic evaluation is Phase 4a).

- Produce data/MC comparisons for **all** kinematic variables entering the
  observable, resolved by reconstructed object category. Observable-level
  agreement can mask compensating category-level mismodeling. These plots are
  required evidence that the MC response model is adequate — missing
  category-level validation is Category A for unfolded measurements.
- Construct the response matrix from MC (matched reco/gen events). Report
  matrix properties: dimensions, diagonal fraction, condition number,
  efficiency as a function of the particle-level observable.
- Implement the correction/unfolding chain end-to-end on MC. Run closure
  tests: unfold MC truth through the response and verify recovery within
  statistical precision. Run stress tests: unfold a reweighted truth through
  the nominal response and verify recovery of the reweighted shape.
- Closure test failure (chi2 p-value < 0.05) is Category A — the correction
  chain must close before proceeding.
- Prototype the full chain on data to verify it runs without errors. The
  corrected spectrum at this stage is a working result, not the final
  measurement.
- Prepare inputs for Phase 4a systematic evaluation: nominal response matrix,
  selection machinery that can be re-run with varied cuts, alternative MC
  samples if available.

If backgrounds are present (e.g., non-hadronic contamination in an event
shape measurement), estimate and subtract them. But the primary Phase 3
deliverable for measurements is the validated correction chain, not a
background model. Control regions and validation regions (as described for
searches above) are typically not needed for inclusive measurements where the
signal is the process being measured.

**Workflow pattern.** Phase 3 is iteration-heavy. Follow this progression:

1. **Setup & prototype.** Build the processing pipeline on a small slice
   (~1 file or ~1000 events). Verify it runs end-to-end and produces
   sensible distributions. Register each script as a pixi task.
2. **Full processing.** Run on the full dataset. Produce data/MC comparisons
   for every variable entering the observable or selection. For measurements:
   build the response matrix and correction machinery at this stage.
3. **Inspect & validate.** Systematically review all produced plots — data/MC
   agreement per variable, cutflow yields, closure tests. This is where
   modeling issues must be caught before they propagate to Phase 4.

**Output artifact:** `SELECTION.md` — selection definition, cutflow, MVA
details if applicable, region definitions with purity, background estimates with
uncertainties, closure test results, data/MC comparisons in all regions.

**Sensitivity optimization.** If the expected sensitivity after the initial
selection is insufficient for the physics goal, the agent must systematically
explore alternative approaches before concluding. The agent maintains a
**sensitivity log** (`sensitivity_log.md`) tracking each approach tried, the
figure of merit achieved, and the limiting factor (statistical, systematic,
background modeling).

The exploration should progress through qualitatively different strategies,
not just parameter tuning within one approach:

1. *Optimize the current approach* — tune cuts for S/√B or equivalent
2. *Try a more powerful discriminant* — move from cut-based to BDT, or from
   BDT to a more expressive model (GNN for high-dimensional inputs, etc.)
3. *Try different extraction strategies* — shape fit vs counting experiment,
   mass fit vs classifier score fit, different discriminant variables
4. *Try different signal extraction techniques* — rebinned histograms,
   classifier output reshaping (e.g., flat signal transform), categorization
   by S/B ratio
5. *Revisit region design* — tighter signal region, different background
   decomposition, additional categories

The agent should stop optimizing when:
- The sensitivity meets the physics goal, **or**
- At least 3 materially different approaches have been tried, **and**
- The most recent improvement was marginal (<10% relative to the best
  achieved so far), **and**
- The remaining ideas are increasingly speculative

The sensitivity log is included in the artifact and provides evidence to
reviewers that reasonable alternatives were explored. "We tried X, Y, and Z;
Y performed best because [reason]; further improvements are limited by
[factor]" is a valid and professional conclusion.

**Review:** See Section 6. For searches, selection review focuses on
background modeling fidelity. For measurements, it focuses on correction
chain closure and data/MC validation. Closure test failures are always
Category A.

---

### Phase 4: Systematic Uncertainties and Statistical Inference

This is the longest phase, with three distinct sub-phases separated by
gates. Each sub-phase produces its own artifact.

**Measurement vs. search flow.** The sub-phase structure below is designed
for searches with blinding. For **measurements** (corrected spectra, event
shapes, extracted parameters) where the observable is the result and there
is nothing to blind:

- **Phase 4a (Expected Results)** is the primary inference phase. It includes
  systematic evaluation, correction/unfolding, covariance construction, and
  comparison to references. This is where the measurement is made.
- **Phase 4b and 4c are skipped** unless the measurement involves a quantity
  that could bias the analyst (e.g., an anomalous coupling fit where the
  analyst might tune to a preferred value). For standard corrected spectra,
  the result is visible throughout — there is nothing to unblind.
- The **3-bot review gate** still applies at Phase 4a for measurements. The
  review evaluates systematic completeness, correction validation, and
  result quality — the same scrutiny, just without the blinding ceremony.
- For measurements, Phase 4a must also produce `ANALYSIS_NOTE_DRAFT.md` —
  a near-complete analysis note (same structure as the search-flow draft
  described in Phase 4b below). The result is already final; only Phase 5
  polishing remains. A non-blocking subagent (lowest tier) should compile
  the draft to LaTeX/PDF in parallel with the review cycle, so the human
  gate receives a rendered document.
- The **human gate** applies after Phase 4a review passes: the human sees
  the draft analysis note (as PDF) and measurement result before proceeding
  to Phase 5.

#### Phase 4a: Expected Results

**Goal:** Evaluate systematic uncertainties, construct the statistical model,
and compute expected results using Asimov data only.

**Inputs:** Selection report, background estimates, data/MC samples.

**The agent must:**

*Systematics:*
- Evaluate experimental systematic uncertainties as rate and/or shape variations.
  The relevant sources depend on the experiment and analysis — the agent
  determines these from the experiment corpus and the analysis design.
- Evaluate theory systematic uncertainties as rate and/or shape variations
- Quantify the impact of each source on signal and background yields
- Prune negligible sources and document the pruning criterion

*Statistical model:*
- Construct a binned likelihood model with all signal and background samples,
  Asimov data, and systematic uncertainty terms
- Validate the model: verify nuisance parameter pulls are small, the fit
  converges, and the expected results are physically sensible
- Perform signal injection tests: inject signal at known strengths and verify
  the fit recovers them

*Expected results:*
- Compute expected results (limits, significance, or measurement precision)
- Produce pre-unblinding fit diagnostics

**Output artifact:** `INFERENCE_EXPECTED.md` — systematic uncertainty table with
impacts, statistical model description, expected results, fit diagnostics, and
signal injection test outcomes.

**For measurement analyses:** the artifact must additionally include:
- The full bin-to-bin covariance matrix (statistical + each systematic source
  separately + total). This is essential for any downstream use of the result
  (theory fits, combinations, reinterpretation). Provide the matrices in both
  the artifact (as tables or heatmap figures) and as machine-readable files
  (NumPy `.npy`, JSON, or CSV).
- Comparison of the corrected result to at least one theory prediction or MC
  generator (e.g., Pythia, Herwig, Sherpa at particle level, or fixed-order
  pQCD where available). Compute a chi2 or p-value using the full covariance
  matrix. If no theory prediction is available, justify why and compare to
  published measurements instead.

**Review:** 3-bot review (Section 6.2). For searches, this gates partial
unblinding. For measurements, this gates the human review before Phase 5.
The cycle repeats until the arbiter issues PASS.

#### Phase 4b: Partial Unblinding (10% Data)

**Goal:** Reality-check the analysis with a small data subsample.

**Inputs:** Phase 4a artifact, statistical model, 10% SR data subsample.

**The agent must:**
- Select 10% of SR data using a fixed random seed
- Run the full fit on this subsample
- Evaluate goodness-of-fit, nuisance parameter pulls, impact ranking
- Compare observed and expected results (should be compatible within the large
  statistical uncertainties)
- Document any discrepancies and their explanations
- If problems are found, fix them and re-run (without seeing additional data)

**Output artifact:** `INFERENCE_PARTIAL.md` — 10% observed results, post-fit
diagnostics, comparison to expected, and assessment of analysis health.

**Draft analysis note:** The agent produces `ANALYSIS_NOTE_DRAFT.md` — a
near-complete analysis note following the full AN structure described in
Phase 5. This is not a summary — it is the comprehensive AN with all
sections, cross-checks, systematic descriptions, and appendices, using 10%
observed results as placeholders for the final numbers. Only the full-data
results and their interpretation are missing. The Phase 5 step then updates
numbers, not structure. A non-blocking subagent (lowest tier) should compile
the draft to LaTeX/PDF in parallel with the review cycle, so the human gate
receives a rendered document.

**Review:** 3-bot review (Section 6.2) on the draft analysis note. The
critical and constructive reviewers evaluate the note as collaboration
reviewers would. The arbiter must PASS before the note goes to a human.
The point: the human should receive a polished product, not a rough draft.

**Human gate:** After the arbiter passes, the draft note, unblinding
checklist, and all phase artifacts are presented for human review (Section
4.3). The analysis pauses until the human approves full unblinding.

#### Phase 4c: Full Unblinding

**Goal:** Compute final observed results on the full dataset.

**Inputs:** Phase 4a+4b artifacts, statistical model, full SR data, human
approval.

**The agent must:**
- Run the full fit on the complete dataset
- Produce post-fit diagnostics: nuisance parameter pulls, impact ranking,
  correlation matrix, goodness-of-fit
- Compare to 10% results (consistency check) and expected results
- If results show anomalies (large NP pulls, poor GoF, unexpected signal),
  investigate and document whether these indicate a modeling problem or a
  genuine feature of the data

**Output artifact:** `INFERENCE_OBSERVED.md` — full observed results, post-fit
diagnostics, interpretation, and comparison to partial and expected results.

**Review:** Standard results + writeup review (Section 6).

---

### Phase 5: Documentation

**Goal:** Produce a comprehensive internal analysis note (AN).

**Inputs:** All prior phase artifacts, including observed results.

**What an analysis note is.** The AN is the complete, permanent record of the
analysis — not a journal paper. A journal publication is a distilled summary;
the AN is the full story. It must contain every detail a physicist needs to
reproduce the analysis from scratch using only the note and the data: every
selection cut and its motivation, every systematic variation and how it was
evaluated, every cross-check and its outcome, every correction and how it was
derived. ANs in real collaborations routinely reach 100–200+ pages. Length is
not a goal in itself, but completeness is — and completeness at this level of
detail requires substantial length. **Err on the side of too much detail, not
too little.** A reviewer who has to ask "but how exactly did you do X?" has
found a gap.

**The agent must produce a note containing at minimum the following sections:**

1. **Introduction** — Physics motivation, observable definition, theoretical
   context (perturbative order, resummation, non-perturbative effects where
   relevant). Prior measurements of the same or related observables with
   citations.

2. **Data samples** — Complete inventory: experiment, √s, integrated luminosity
   or event counts, data-taking periods, file-level details. For MC: generator,
   tune, cross-section, number of generated events, filter efficiency.

3. **Event selection** — Every cut listed with:
   - The physical motivation (why this cut exists)
   - The distribution of the cut variable, showing the effect of the cut
   - The numerical efficiency (per-cut and cumulative)
   - Sensitivity studies: what happens when the cut is varied or removed

4. **Corrections / unfolding** (for measurements) — Full description of the
   correction procedure: what is being corrected for, how corrections are
   derived, validation of the correction method (closure tests, stress tests).
   For unfolding: response matrix, regularization, number of iterations,
   convergence checks.

5. **Systematic uncertainties** — One subsection per source, each containing:
   - What the source is and why it affects the result
   - How the variation was evaluated (up/down shifts, alternative samples,
     reweighting, etc.)
   - The impact on the final result (table + figure showing the variation)
   - For literature-derived systematics: the source, its applicability, and
     any inflation applied
   - Summary table of all sources with per-bin or integrated impacts
   - Correlation information: which sources are correlated across bins,
     regions, or processes

6. **Cross-checks** — Every cross-check performed, each as its own subsection:
   - What is being tested and what a failure would indicate
   - The quantitative result (ratio plots, chi2, p-values)
   - Interpretation: does it pass? If marginal, why?
   - Examples: year-by-year or run-period stability, subdetector comparisons,
     charged-only vs. full, alternative selections, alternative correction
     methods, kinematic subsamples, generator comparisons

7. **Statistical method** — For searches: likelihood construction, nuisance
   parameter treatment, test statistic, CLs or frequentist/Bayesian
   procedure. For measurements: bin-by-bin vs. unfolded, normalization,
   uncertainty propagation. In either case: fit validation, signal injection
   or closure tests, goodness-of-fit.

8. **Results** — The primary result with full uncertainties (stat + syst
   breakdown). Tables with per-bin values. Summary figures. For measurements:
   the corrected spectrum, moments or extracted parameters. For searches:
   observed and expected limits/significance.

9. **Comparison to prior results and theory** — If published measurements
   exist: overlay plots with ratio panels, chi2/p-value using the full
   covariance matrix. If theory predictions exist: overlay and quantitative
   comparison. **"Qualitative consistency" is insufficient when data points
   are available.** If no prior measurement exists, state this explicitly.

10. **Conclusions** — Summary of the result, its precision, the dominant
    limitations, and the physics interpretation.

11. **Future directions** — Concrete roadmap per Section 12.6.

12. **Appendices** — Supporting material that would interrupt the main flow:
    full systematic tables per bin, auxiliary distributions, extended cutflow
    tables, full correlation/covariance matrices, additional cross-checks.
    Appendices are not optional padding — they are where the bulk of the
    detail lives. A 10-page main text with 150 pages of appendices is a
    normal AN structure.

**Additional requirements:**
- All quantitative results must be inline — the document must be
  self-contained
- Figures must be publication-quality (see Section 5 for figure standards)
- All citations must reference published literature with proper identifiers
- **Machine-readable results:** All tabulated results (spectra, uncertainties,
  covariance matrices) must also be provided in a machine-readable format
  (CSV, JSON, or YAML) in a `results/` directory alongside the note. Results
  that exist only inside a PDF are not reusable.

**Completeness test:** A physicist unfamiliar with the analysis should be able
to read the AN alone — without access to code, experiment logs, or phase
artifacts — and understand every choice that was made, reproduce every number
in the results, and evaluate whether the conclusions are supported. If a
choice requires reading the code to understand, the AN has a gap.

**Depth calibration:** The AN is not a summary — it is the complete record.
Concrete minimum expectations:

- **Systematics section:** One subsection per source. A summary table alone
  is insufficient. Each source gets: description, method, impact figure,
  per-bin table. If the analysis has 5 systematic sources, there are 5
  subsections plus a summary.
- **Cross-checks section:** One subsection per cross-check. "Bin-by-bin
  cross-check confirms the result" is a one-liner, not a subsection. A
  subsection shows the comparison plot, states the chi2, and interprets
  the level of agreement.
- **Event selection:** Every cut gets its own paragraph with a figure
  reference showing the distribution before and after the cut. A two-row
  cutflow table ("before" and "after all cuts") is not a cutflow — it
  must show each cut individually with per-cut and cumulative efficiencies.
- **Appendices:** Full per-bin systematic tables, covariance/correlation
  matrices (as tables, not just figures), extended cutflow, auxiliary
  distributions. The appendices will typically be longer than the main
  text.

As a rough calibration: a measurement analysis with 5 systematic sources,
3 cross-checks, 6 selection cuts, and 18 result bins should produce an AN
of approximately 50–100 pages when rendered. If the AN is under 30 rendered
pages, it is almost certainly missing required detail.

**LaTeX compilation.** The working format during development is markdown.
The Phase 5 executor (or a dedicated lower-tier subagent) converts the
final note to LaTeX, compiles to PDF, and verifies that all figures render
correctly. The LaTeX source and compiled PDF are both deliverables.

**Output artifact:** `ANALYSIS_NOTE.md` (or `.tex` + compiled PDF) plus
`results/` directory containing machine-readable data tables.

**Review:** See Section 6. Documentation review reads the note as a
collaboration editorial board reviewer would. Reviewers should specifically
check for completeness — are all cross-checks documented? Are all systematics
described in sufficient detail? Could a reader reproduce the analysis?

---
