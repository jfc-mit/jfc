## 3. Analysis Phases

The analysis proceeds through five phases. Dependencies between phases are
sequential — each phase consumes artifacts from prior phases. Within a phase,
work may be parallelized at the agent's discretion.

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
- List anticipated systematic uncertainty categories (experimental, theoretical)
- Identify which collision data and simulation samples are needed

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

**Practical note:** The agent should expect to discover the data format at
runtime — branch naming conventions, tree structures, and storage formats vary
across experiments and analyses. The agent explores file contents
programmatically before attempting bulk data access. This discovery process is
itself documented in the artifact.

---

### Phase 3: Selection and Background Modeling

**Goal:** Define the complete analysis selection, design control and validation
regions, estimate backgrounds, and validate the background model.

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

*Regions:*
- Define control regions enriched in each major background. Document purity and
  the kinematic relationship to the signal region.
- Define validation regions kinematically between control and signal regions for
  closure testing. These must be statistically independent of both CR and SR.

*Background estimation:*
- Estimate background yields in SR using the chosen method per background
  (simulation-scaled-from-CR, data-driven, or pure simulation with justification)
- Perform closure tests in validation regions: compare predicted yields
  (extrapolated from CRs, not pure MC) to observation. Document agreement
  quantitatively.
- If closure fails, investigate and iterate on the region design or estimation
  method before proceeding.

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
- The most recent improvement was marginal (<10% relative), **and**
- The remaining ideas are increasingly speculative

The sensitivity log is included in the artifact and provides evidence to
reviewers that reasonable alternatives were explored. "We tried X, Y, and Z;
Y performed best because [reason]; further improvements are limited by
[factor]" is a valid and professional conclusion.

**Review:** See Section 6. Selection review focuses on background modeling
fidelity. Closure test failures are always Category A.

---

### Phase 4: Systematic Uncertainties and Statistical Inference

This is the longest phase, with three distinct sub-phases separated by
gates. Each sub-phase produces its own artifact.

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

**Review:** Rigorous multi-reviewer process (Section 4.2: critical reviewer,
constructive reviewer, arbiter). This cycle gates partial unblinding — it
repeats until the arbiter issues PASS.

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
near-complete analysis note including the 10% observed results. This must be
publication-quality: complete methodology, all figures, proper citations,
self-contained. Only the final (full-data) numbers are missing.

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

**Goal:** Produce the final publication-quality analysis note.

**Inputs:** All prior phase artifacts, including observed results.

**The agent must:**
- Update the draft note with observed results, final figures, and conclusions
- All quantitative results must be inline — the document must be self-contained
- Figures must be publication-quality
- All citations must reference published literature with proper identifiers
- The note should be suitable for submission as an internal collaboration
  analysis note

**Output artifact:** `ANALYSIS_NOTE.md` (or `.tex` + compiled PDF).

**Review:** See Section 6. Documentation review reads the note as a
collaboration editorial board reviewer would.

---
