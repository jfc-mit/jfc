# LLM-Driven HEP Analysis: A Minimal Methodology Specification

## 1. Scope and Principles

This document specifies a methodology for conducting a complete High Energy
Physics (HEP) collider analysis using LLM-based agents. The specification is
intentionally minimal: it defines *what* must happen and *what* each phase must
produce, not *how* the agent should implement it. The agent selects tools,
writes code, and makes physics judgments within the constraints described here.

**Design principles:**

- **Prose over code.** The methodology is expressed in natural language. No
  bespoke library is required — agents use standard, community-maintained HEP
  software directly.
- **Artifacts over memory.** Each phase produces a self-contained written
  report. Subsequent phases read these reports, not prior conversation history.
  This bounds context consumption and makes the analysis auditable.
- **Review at every level.** Plans are reviewed before execution. Code is
  reviewed before results are trusted. Results are reviewed before they are
  written up. The final writeup is reviewed before the analysis is considered
  complete. Review artifacts are first-class outputs.
- **The agent adapts to the analysis.** Not every analysis needs multivariate
  techniques, multiple signal regions, or data-driven background estimates. The
  agent evaluates what is appropriate and documents its reasoning. Omitting an
  unnecessary step is correct; performing it without justification is not.
- **No encoded physics.** This specification describes methodology, not physics.
  The agent derives its physics approach from the literature (via retrieval from
  the experiment's publication corpus) and first principles, not from templates
  or recipes. HEP is an evolving field; hardcoded physics guidance goes stale.
- **Cost-aware execution.** Not every task requires the most capable model.
  The orchestrator assigns model tiers based on task complexity (see Section
  6.6). This is configurable — a top-level switch controls whether to use
  tiered models or a uniform model (useful for benchmarking).

---

## 2. Inputs

An analysis begins with two inputs:

### 2.1 Physics Prompt

A brief natural-language description of the physics goal. Examples:

> Search for the Higgs boson produced in association with a Z boson, where the
> Higgs decays to a pair of b quarks, using ALEPH data at sqrt(s) = 200–209 GeV.

> Measure the inclusive W+W- production cross-section at LEP2 energies using
> fully hadronic final states.

The prompt need not specify methodology. It states the physics target and any
constraints (dataset, final state, energy range).

### 2.2 Experiment Context (Retrieval-Based)

The agent has access to a retrieval system (e.g., RAG over a corpus of
collaboration publications, theses, and internal notes) for the relevant
experiment(s). This replaces hand-curated configuration files.

The agent queries this corpus to obtain:
- Detector specifications (subsystem resolutions, angular coverage, material
  budgets)
- Standard object definitions (tracking, lepton ID, jet reconstruction) as
  published in collaboration papers
- Available MC generators, simulation samples, and their known limitations
- Measured performance (efficiencies, fake rates, energy scale uncertainties)
- Prior analyses in the same or related channels (for context, not for copying)

**Why retrieval over static files:** Experiment knowledge is vast, evolving, and
distributed across hundreds of publications. No static configuration captures it
adequately. A retrieval system over the actual literature (a) scales to any
experiment with a publication corpus, (b) provides citations naturally, (c) lets
the agent discover relevant information it wouldn't know to ask for, and (d)
stays current as new publications are indexed.

The agent must cite the source for any experiment-specific information it uses
(detector parameters, object selections, performance numbers). "Retrieved from
[reference]" is the minimum; direct quotation with section numbers is preferred.

**Retrieve, then verify.** Information from the retrieval corpus may be
incomplete, out of context, or wrong. Where the analysis has access to the
underlying data (as is the case for completed experiments like ALEPH or DELPHI
where full datasets are available), the agent must verify retrieved claims
against the data itself. If the corpus says "good tracks require ntpc >= 4",
the agent should confirm this produces the expected efficiency by applying the
cut to data and comparing. The data is the ground truth; the corpus provides
starting points and context. Discrepancies between retrieved information and
observed data behavior must be documented and resolved — typically by trusting
the data and noting the corpus inconsistency.

**When retrieval fails.** The corpus may be sparse, the query poorly matched,
or the relevant information simply not indexed. The agent should:
1. Log the failed query and what it was looking for in a retrieval log
   (`retrieval_log.md` in the phase directory)
2. Try rephrased queries or broader searches
3. If retrieval remains unhelpful, proceed using the agent's training knowledge
   and clearly mark any claim that is not corpus-backed as "unverified — based
   on general knowledge, to be confirmed"
4. Flag the gap in the artifact's open issues section

The RAG corpus is an aid, not a requirement. The agent should never block on a
failed retrieval — it does its best and documents the uncertainty.

---

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

## 4. Blinding Protocol

Blinding prevents the analyst (human or agent) from tuning the analysis to
produce a desired result in the signal region. The protocol is procedural,
with staged unblinding.

**What is blinded:** The distribution of the final discriminant variable (the
variable used for statistical inference — e.g., invariant mass, BDT output
score) in the signal region. Other distributions in the signal region (control
variables, event counts in sidebands) may be examined for debugging and
validation purposes.

### 4.1 Blinding Stages

**Fully blinded (Phases 1–3):** The signal region discriminant distribution in
data is not examined. Background estimates in the SR rely on extrapolation from
control regions or simulation.

**Asimov-only (Phase 4, expected results):** Expected limits and sensitivity
use Asimov data (background-only pseudo-data). Signal injection tests use
pseudo-data at known signal strengths.

**Partial unblinding — 10% data (Phase 4, agent-gated):** After the expected
results and fit validation pass rigorous agent review (see Section 4.2), the
agent performs a partial unblinding using a 10% random subsample of the SR data.
This is a standard HEP practice that provides a meaningful but low-stakes
reality check — the results will have large statistical uncertainties but will
expose any gross modeling failures (wrong background normalization, misshapen
discriminant, fit pathologies) that Asimov data cannot reveal.

The agent:
- Selects 10% of SR data events using a fixed random seed for reproducibility
- Runs the full fit on this subsample
- Evaluates goodness-of-fit, nuisance parameter pulls, and impact ranking
- Compares observed and expected results — they should be statistically
  compatible given the large uncertainties
- Documents any discrepancies and their likely explanations
- If problems are found, fixes them *before* seeing more data, then re-runs
  the partial unblinding

**Full unblinding (Phase 4, human-gated):** After partial unblinding succeeds,
the agent produces a near-final analysis note including the 10% observed
results and presents it to a human reviewer. The human sees an essentially
complete product — methodology, validation, and weak but real results — and
decides whether to proceed to full unblinding. See Section 4.3.

**Post-unblinding:** The full observed result is computed. Post-unblinding
modifications must be explicitly documented and justified.

### 4.2 Agent Gate: Earning Partial Unblinding

The agent does not proceed to partial unblinding until the analysis passes a
rigorous multi-reviewer process. This is the agent's internal quality bar —
it must be high enough that a senior physicist would be comfortable with the
analysis as presented.

The review structure for the pre-unblinding assessment:

1. **Critical reviewer ("bad cop"):** Reviews the analysis artifacts with the
   goal of finding flaws. Looks for incomplete background estimates, missing
   systematics, unjustified assumptions, potential biases, and any way the
   analysis could produce a misleading result. Every issue is a potential
   Category A.

2. **Constructive reviewer ("good cop"):** Reviews the analysis with the goal
   of strengthening it. Identifies areas where the argument could be clearer,
   where additional validation would build confidence, and where the
   presentation could be improved. Focuses on Category B and C issues but
   escalates to A if warranted.

3. **Arbiter:** Reads both reviews and the original artifacts. Adjudicates
   disagreements between reviewers. Produces a final assessment with a clear
   PASS / ITERATE / ESCALATE decision.

This cycle repeats until the arbiter issues a PASS with no unresolved Category A
items. There is no iteration limit on this cycle — it runs until the analysis
is right. (In practice, if it hasn't converged after 3-4 rounds, the issues are
likely fundamental enough to require human input, and the arbiter should
escalate.)

Only after PASS does the agent proceed to partial unblinding.

### 4.3 Human Gate: Approving Full Unblinding

After partial unblinding, the agent produces and presents to a human:

- The draft analysis note, now including 10% observed results, post-fit
  diagnostics, and goodness-of-fit assessment
- The unblinding checklist:
  1. Background model validated (closure tests pass in all VRs)
  2. Systematic uncertainties evaluated and fit model stable
  3. Expected results physically sensible
  4. Signal injection tests confirm fit recovers injected signals
  5. 10% partial unblinding shows no unexpected pathologies
  6. All agent review cycles resolved (arbiter PASS)
  7. Draft analysis note reviewed and considered publication-ready modulo
     full observed results

The human reviews the complete package and either approves full unblinding,
requests changes, or halts the analysis. The agent does not fully unblind
autonomously.

---

## 5. Artifact Format

Every phase produces three types of written output, at different levels of
formality:

### 5.1 The Experiment Log

Each phase maintains an **experiment log** (`experiment_log.md`) — a persistent,
append-only record of what was tried and what happened. This is the analysis
lab notebook.

```markdown
## 2026-03-13 — Exploring jet clustering

Tried Durham algorithm with ycut=0.005 on the signal sample.
- Result: dijet mass resolution ~4 GeV, reasonable
- But: 8% of events have 3+ jets, losing signal efficiency

Tried ycut=0.008 (looser).
- Result: mass resolution ~5 GeV (slightly worse), but only 3% of events
  have 3+ jets. Better signal efficiency.
- Going with ycut=0.008 for now.

## 2026-03-13 — b-tag working point study

Tried tight WP (80% efficiency, 1% mistag).
- S/B = 2.3 in signal region, but only 45 signal events survive.

Tried medium WP (70% efficiency, 2% mistag).
- S/B = 1.1, but 62 signal events. Better expected limit.
- Medium WP gives ~15% better expected significance. Going with medium.
```

The experiment log is:
- **Not a formal artifact** — it does not follow the standard artifact
  structure and is not the handoff document
- **Readable by both agents and humans** — it provides context that the
  formal artifact compresses away
- **Append-only** — entries are never deleted or modified. Failed approaches
  are as valuable as successful ones.
- **Referenced by the formal artifact** — the artifact says "we chose Durham
  with ycut=0.008 (see experiment log for alternatives explored)"
- **Persists across agent sessions within a phase** — if the executor iterates
  10 times, all 10 sessions append to the same log

The experiment log is especially valuable for Phases 2–3 where iteration is
high. It prevents agents from re-trying failed approaches and gives humans
visibility into the agent's decision-making without reading full session
transcripts.

### 5.2 The Primary Artifact

Every phase produces a primary artifact (markdown or LaTeX) that serves as the
handoff to subsequent phases and the permanent analysis record.

Artifacts must be **self-contained**: a reader with access only to the artifact
and the experiment corpus should understand what was done, why, and what the
results are.

### Standard artifact sections:

1. **Summary** — What was accomplished (1 paragraph)
2. **Method** — How it was done, in enough detail to reproduce
3. **Results** — Key findings: tables, figures (by path), numbers with
   uncertainties
4. **Validation** — Checks performed and their quantitative outcomes
5. **Open issues** — What subsequent phases should be aware of
6. **Code reference** — Where scripts live and how to re-execute

### Presentation requirements:

Artifacts are markdown documents with embedded figure references (paths to
PDF/PNG files in the phase's `figures/` directory). Every quantitative claim
must be supported by a figure or table:

- **Data/MC comparisons:** overlaid distributions with ratio panels
- **Cutflows:** tables with per-cut yields, efficiencies, and S/B ratios
- **Selection cuts:** each cut accompanied by the distribution that motivates
  it, showing where signal and background separate
- **Background estimates:** yield tables with stat + syst uncertainties per
  region
- **Fit results:** post-fit pull distributions, impact ranking plots,
  correlation matrices, GoF summaries
- **Limits/measurements:** Brazil band plots, observed vs expected comparisons

Figures are referenced inline: `![description](figures/filename.pdf)`. All
figures use consistent styling (mplhep or equivalent). Axis labels include
units. Legends are readable.

The artifact + its `figures/` directory must be self-contained — a reader
should be able to evaluate the analysis from these alone.

### Supplementary artifacts:

Phases also produce data files, figures, and scripts in phase-specific
subdirectories. Scripts are referenced from the artifact's code reference
section for reproducibility.

---

## 6. Review Protocol

Review intensity is proportional to stakes. Heavyweight review is reserved for
gate points where errors are costly. Phases with high execution iteration
(data exploration, selection) use lightweight review to avoid bottlenecking
the natural trial-and-error of data analysis.

### 6.1 Review Classification

All reviews — regardless of intensity — use the same classification:

- **(A) Must resolve:** Errors or missing elements that would cause a
  collaboration reviewer to reject the analysis. Work cannot proceed until
  addressed.
- **(B) Should address:** Issues that weaken the analysis but don't invalidate
  it. Tracked and resolved before the analysis is finalized.
- **(C) Suggestions:** Style, clarity, or minor improvements.

### 6.2 Tiered Review Structure

| Phase | Review type | Rationale |
|-------|------------|-----------|
| Phase 1: Strategy | **3-bot** (critical + constructive + arbiter) | Sets direction for everything. Physics errors propagate. Cheap phase, so review cost is well spent. |
| Phase 2: Exploration | **Self-review** | Mostly mechanical (sample inventory, distributions). High execution iteration as the agent discovers data formats. Errors caught downstream in Phase 3. |
| Phase 3: Selection & Modeling | **1-bot** (single critical reviewer) | Physics mistakes become quantitative here. One external eye on closure tests and background modeling. High execution iteration — don't bottleneck it. |
| Phase 4a: Expected results | **3-bot** | Gates partial unblinding. The fit model, systematics, and expected results must be bulletproof. Full tribunal. |
| Phase 4b: Partial unblinding | **3-bot** | The draft analysis note and 10% results must be polished before presenting to a human. The human should see a professional product, not a rough draft. |
| Phase 4c: Full unblinding | **1-bot** | Sanity check on post-fit diagnostics. Methodology already human-approved. |
| Phase 5: Documentation | **3-bot** | The final product submitted for collaboration review. Worth the full treatment. |

**3-bot review** = critical reviewer ("bad cop") + constructive reviewer
("good cop") + arbiter, as described in Section 4.2. Reviewers run in
parallel; arbiter reads both and issues PASS / ITERATE / ESCALATE.

**1-bot review** = single critical reviewer. Issues classified A/B/C.
Executor addresses Category A items and re-submits. No arbiter needed.

**Self-review** = the executing agent explicitly reviews its own work before
producing the artifact. Plan review and code review happen within the session.
No separate agent invocation.

### 6.3 Review Focus by Phase

| Phase | Review focus |
|-------|-------------|
| Strategy | Are backgrounds complete? Is the approach motivated by the literature? |
| Exploration | (Self-review) Are samples complete? Any data quality issues? Do distributions look physical? |
| Selection & Modeling | Does the background model close? Is every cut motivated by a plot? Is signal contamination controlled? |
| 4a: Expected | Is the fit healthy? Are systematics complete? Do signal injection tests pass? |
| 4b: Partial unblinding | Is the draft note publication-quality? Are 10% results consistent with expectations? Are diagnostics clean? |
| 4c: Full unblinding | Are post-fit diagnostics healthy? Are anomalies properly characterized? |
| Documentation | Is the note self-contained, correct, and publication-ready? |

### 6.4 Iteration and Escalation

For **3-bot reviews:** the cycle repeats until the arbiter issues PASS. No
fixed iteration limit — the analysis must be right. If not converged after 3-4
rounds, the arbiter should ESCALATE to human review.

For **1-bot reviews:** the executor addresses Category A items and re-submits.
Up to 2 iterations before escalation.

For **self-review:** no formal iteration — the agent corrects issues as it
finds them during execution.

### 6.5 The Human Gate

After Phase 4b's 3-bot review passes, the draft analysis note (including 10%
observed results, post-fit diagnostics, and goodness-of-fit) is presented to a
human. The human sees the complete package and either approves full unblinding,
requests changes, or halts the analysis.

This is equivalent to a collaboration internal review before unblinding. The
human should receive a professional, publication-quality document — not a
work-in-progress.

### 6.6 Model Tiering

Not every agent session requires the most capable (and expensive) model.
The orchestrator assigns model tiers based on task type:

| Task | Model tier | Rationale |
|------|-----------|-----------|
| Strategy execution (Phase 1) | Highest (e.g., Opus) | Physics reasoning, literature synthesis |
| 3-bot reviewers + arbiter | Highest | Adversarial critique, catching subtle errors |
| Phase 3 executor (selection iteration) | Mid (e.g., Sonnet) | Code writing, debugging, iterating fast |
| Phase 2 executor (data exploration) | Mid | I/O plumbing, plotting, mechanical inventory |
| Phase 4 executor (fits, systematics) | Mid-High | Needs to get statistical model right |
| 1-bot reviewer | Mid-High | Single-reviewer phases still need physics judgment |
| Plot regeneration, reformatting | Lowest (e.g., Haiku) | Mechanical tasks with clear specifications |
| Smoke tests, linting | Lowest | Boilerplate with clear pass/fail |

A **top-level configuration switch** controls whether tiering is active:
- `model_tier: auto` — use the tiering above (default, cost-efficient)
- `model_tier: uniform_high` — all sessions use the highest model (for
  benchmarking or when cost is not a constraint)
- `model_tier: uniform_mid` — all sessions use mid tier (budget mode)

This switch exists at the orchestration level, not in the methodology spec,
so the same spec can be used for cost comparisons across configurations.

### 6.7 Cost Controls

To prevent runaway costs from pathological iteration:

**Review iteration cap:** 3-bot review cycles are capped at **3 iterations**
per phase. If the arbiter has not issued PASS after 3 cycles:
- In interactive mode: pause and present the unresolved issues to the human
- In batch mode: emit a warning, log the unresolved Category A items, and
  proceed to the next phase with the issues documented as open

**Execution iteration budget:** Phases 2 and 3 (high iteration) should have a
configurable execution budget (e.g., maximum N executor iterations or M tokens).
When the budget is approached:
- The agent produces the best artifact it can with current results
- Open issues are documented in the artifact
- The phase proceeds to review with a note that the iteration budget was
  reached

**Total analysis budget:** The orchestrator tracks cumulative cost across all
phases. If the total exceeds a configured threshold, the analysis pauses for
human review of cost vs. progress.

These controls are configurable — aggressive budgets for exploratory runs,
relaxed budgets for production analyses.

### 6.8 Phase Regression

The pipeline is normally forward-only, but a reviewer or executor may discover
that a fundamental assumption from an earlier phase is wrong — a major
background was missed, the selection approach is unworkable, or the data
contradicts the strategy.

When this happens:

1. The agent (or reviewer) documents the issue and identifies which earlier
   phase it originates from
2. The issue is classified as a **regression trigger** in the review artifact
3. The orchestrator re-runs the identified phase with the new information
   injected as an additional input (e.g., "Phase 3 discovered that the WW
   background dominates after selection — revise the strategy to address this")
4. All downstream phases are invalidated and re-run from the regressed phase

Phase regression is expensive and should be rare. The strategy and exploration
phases exist to prevent it. But when it happens, it is better to go back and
fix the foundation than to build on a known-faulty premise.

Regression is logged in a `regression_log.md` at the analysis root, tracking
what triggered the regression, which phase was re-run, and what changed.

---

## 7. Tools and Paradigms

The agent uses standard HEP software. No bespoke analysis framework is
required, but the following tools and paradigms are preferred. This section
is maintained by the analysis team and reflects operational knowledge about
what works well in practice.

<!--
  TODO: Fill in with your preferred tool stack and paradigms.
  This is the place for things like:
  - Preferred I/O library (uproot vs ROOT vs coffea)
  - Statistical framework (pyhf vs RooFit vs Combine)
  - Plotting conventions (mplhep with experiment style)
  - Jet algorithms relevant to your experiment
  - Specific packages with version pins if needed
  - Coding paradigms (columnar analysis, event loops, etc.)
  - Any "use X not Y" preferences
-->

### 7.1 Preferred Tools

| Capability | Tool | Notes |
|-----------|------|-------|
| ROOT file I/O | uproot | Pythonic, no ROOT install required. Use `uproot.open()` to explore, `arrays()` to load. |
| Array operations | awkward-array, numpy | Columnar analysis — no event loops. awkward for jagged structure, numpy for flat. |
| Histogramming | hist, boost-histogram | Use `hist` for building and plotting; `boost-histogram` for performance-critical fills. |
| Statistical model | pyhf | HistFactory JSON workspaces. Portable, text-based, version-controllable. |
| Fitting / limits | pyhf, cabinetry | cabinetry for convenience wrappers (ranking, pulls). pyhf directly for custom fits. |
| MVA | xgboost, scikit-learn | BDTs via xgboost. scikit-learn for preprocessing, train/test split, metrics. |
| Hyperparameter opt | optuna | Bayesian optimization. Pin `random_state=42` for reproducibility. |
| Plotting | matplotlib, mplhep | mplhep for experiment-specific styling (`mplhep.style.ALEPH` etc.). All figures as PDF. |
| Jet clustering | — | *Specify: e.g., fastjet with Durham algorithm for LEP, anti-kt for LHC* |
| b-tagging | — | *Specify: experiment-specific algorithm and working points* |
| Document preparation | LaTeX | pdflatex + bibtex. Markdown acceptable for intermediate artifacts. |
| Experiment knowledge | RAG (SciTreeRAG) | Retrieval over publication/thesis corpus. See Section 2.2. |

### 7.2 Paradigms

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

<!-- Add or modify paradigms as needed. Examples of things to specify:
  - Event weighting conventions (how to handle negative weights, normalization)
  - Luminosity handling (where the number comes from, how it enters the analysis)
  - Naming conventions for systematic variations (e.g., {source}Up / {source}Down)
  - Signal normalization (to cross-section × lumi, or to unity for shapes)
  - Binning strategy preferences (uniform, variable, algorithm-driven)
  - Correlation model for systematics (what is correlated across processes/regions)
-->

### 7.3 Retrieval

The agent has access to a RAG system over the experiment's publication corpus
for retrieving detector specifications, object definitions, prior analysis
results, and other experiment-specific knowledge. See Section 2.2.

---

## 8. Context Management

### 8.1 Artifacts as Handoffs

The only information that crosses phase boundaries is the written artifact. No
conversation history, no shared variables, no implicit state. Each agent session
starts with:

1. This methodology spec (~4 pages)
2. Upstream phase artifacts (~2-5 pages each)
3. The physics prompt (~1 paragraph)
4. Access to the experiment retrieval corpus

Even at Phase 5, the total input is bounded at ~20-25 pages. Context does not
accumulate unboundedly.

### 8.2 What Goes Where

- **Artifact:** Decisions, results, reasoning, key figures (by path), validation
  outcomes. Everything a reader needs to evaluate the analysis.
- **Scripts directory:** Code that produced the results. Referenced from the
  artifact for reproducibility, but not read by downstream phases.
- **Supplementary files:** Full tables, workspaces, trained models. Referenced
  from the artifact, consulted only when needed.

### 8.3 Handling Large Outputs

If a phase produces extensive tabular data, the artifact includes a summary
table with the most impactful entries, references the full table as a
supplementary file, and states conclusions in prose.

---

## 9. Multi-Channel Analyses

Many HEP analyses involve multiple channels with different final states (e.g.,
ttH with 0-lepton, 1-lepton, 2-lepton channels, or Zh with νν̄bb̄, ℓ⁺ℓ⁻bb̄,
qq̄bb̄ channels). The methodology handles this as follows:

**Phase 1 (Strategy)** defines the channel decomposition:
- Which channels are included, with physics motivation
- How channels are defined to ensure no event overlap (orthogonal selections)
- Which calibrations and systematic uncertainties are shared across channels
  (e.g., jet energy corrections, b-tagging, luminosity)
- Which are channel-specific (e.g., lepton ID for leptonic channel only)

**Phases 2–3** may proceed per-channel, potentially in parallel:
- Each channel has its own exploration, selection, and background modeling
- Shared calibrations (b-tagging efficiency, energy scales) are developed once
  and referenced by all channels
- Each channel produces its own artifact (e.g., `SELECTION_nunu.md`,
  `SELECTION_llbb.md`)
- A consolidation artifact documents the overlap check (no events shared
  between channels) and summarizes cross-channel consistency

**Shared sub-analyses (calibrations):** Some analysis components are not
channel-specific — they are mini-analyses in their own right that produce
calibration artifacts consumed by all channels. Examples:

- **Jet energy corrections:** derive correction factors from data, measure
  residual uncertainty → produces correction functions + systematic variations
- **b-tag calibration:** measure b-tagging efficiency in data using a tag-and-
  probe or similar method → produces scale factors + uncertainties per working
  point
- **Trigger efficiency:** measure turn-on curves in data → produces efficiency
  maps + uncertainties
- **Luminosity:** typically provided by the experiment, but may need validation

Each shared sub-analysis:
- Has its own experiment log and artifact (e.g., `CALIBRATION_BTAG.md`)
- Follows the same structure as a phase (method, results, validation, code)
- Produces a calibration artifact with **central values + uncertainties** that
  channels consume as inputs
- The uncertainties propagate into Phase 4 as systematic terms in the fit model

Shared sub-analyses are identified in Phase 1 (strategy) or Phase 2
(exploration, when the agent discovers what calibrations are needed). They run
in parallel with or before the channel-specific Phase 2–3 work. They may be
assigned to dedicated agent sessions.

**Phase 4** combines channels in a single statistical model:
- The fit model includes all channels simultaneously
- Correlated systematic uncertainties (including shared calibrations) use
  shared nuisance parameters across channels
- The combined expected sensitivity is the primary figure of merit
- Per-channel results are also reported for diagnostic purposes

The channel structure is a strategy decision — the agent proposes it in Phase 1
and the strategy review evaluates whether it makes sense.

---

## 10. Scaling to Multiple Agents

This specification is written for a single agent executing phases sequentially.
For parallel execution:

- **Within a phase:** Multiple agents may work in parallel provided they write
  to separate sub-artifacts and a consolidation step merges outputs before
  review.
- **Across phases:** Sequential by design. An agent beginning Phase N reads the
  completed artifact from Phase N-1.
- **Review as a separate agent:** Results and writeup reviews should be distinct
  agent invocations. This provides adversarial review that self-review cannot.
- **Per-channel parallelism:** In multi-channel analyses, channel-specific work
  in Phases 2–3 can proceed in parallel as separate agent teams, merging in
  Phase 4.

---

## 11. Version Control and Coding Practices

Analysis code is exploratory by nature, but it must be correct and
reproducible. The engineering bar is **"would this pass review from a physicist
colleague"** — not enterprise software standards.

### 11.1 Git Discipline

All analysis work is tracked in git. This serves as the checkpointing mechanism
within and across phases.

**Conventional commits.** Every commit uses a structured message format:

```
<type>(phase): <description>

Types:
  feat     — new analysis capability (selection, training, fit)
  fix      — bug fix in analysis code
  data     — data exploration, sample inventory
  plot     — figure generation or update
  doc      — artifact writing, note updates
  refactor — restructuring without changing results
  test     — adding or updating tests
  chore    — housekeeping (formatting, dependencies)
```

**Commit frequency:** After every meaningful step — completing a cut study,
producing a set of plots, finishing a closure test, updating the artifact.
Commits within a phase are the checkpoints; if the agent crashes at step 12 of
15, it can resume from the last commit.

**Branch strategy:** Each phase works on a branch (`phase1_strategy`,
`phase2_exploration`, etc.). The branch is merged to main when the phase's
review passes. This keeps main clean — it always reflects reviewed work.

### 11.2 Code Quality

**Formatting and linting:** Use `ruff` (or equivalent) with a pre-commit hook.
Every commit is automatically formatted and checked for common errors (undefined
variables, unused imports, shadowed names). This is cheap and catches real bugs.

**Code style:**
- **KISS.** Obvious numpy/awkward operations over clever metaprogramming. A
  physicist reading the code should be able to follow the analysis flow.
- **DRY.** If multiple channels share the same calibration logic, factor it out.
  But do not prematurely abstract for hypothetical future needs.
- **YAGNI.** Do not build CLIs, config systems, or plugin architectures. Write
  scripts. Refactor when (not before) reuse is actually needed.

**What NOT to do:**
- Do not write unit tests for every function
- Do not create mock data fixtures when real data is available
- Do not add type annotations to exploratory scripts
- Do not write docstrings for functions that run once
- Do not build frameworks when scripts work
- Do not use dependency injection, abstract base classes, or enterprise patterns

### 11.3 Testing

Testing effort should focus on **structural bugs** — errors in the plumbing
that silently propagate through everything downstream. A bug in the final fit
is cheap to fix (re-run the fit). But cutting on the wrong lepton pT branch,
reconstructing a nonsensical 4-lepton mass, or applying a weight meant for
signal to background — these are catastrophic because they require re-running
the entire analysis and are hard to track down (the numbers look plausible
but are wrong).

**Always:** One **smoke test** per phase — does the full pipeline run on ~100
events without crashing? This catches import errors, broken paths, shape
mismatches, and API changes. Fast to run, high value.

**Always:** One **integration test** for the processing chain — does it produce
output files with the expected structure? Not checking physics values — checking
that the machinery works (correct number of bins, files exist, no NaN yields).

**Focus on structural correctness:**
- Test that variable names map to the right physical quantities (is this
  actually lepton pT, not jet pT?)
- Test that cut inversions actually invert (CR selection is complement of SR)
- Test that object definitions produce yields consistent with published
  efficiencies (if the experiment says 99% tracking efficiency and you get 60%,
  something is structurally wrong)
- Test that systematic variations go in the expected direction
- Test that event counts are monotonically decreasing through the cutflow
  (if a cut increases yield, something is wrong)

These structural tests are cheap to write and catch the bugs that are most
expensive to debug later.

**Never:** Full test suites, 100% coverage targets, TDD. The analysis result
is the product, not the code. The physics validation (closure tests, signal
injection, post-fit diagnostics) IS the test suite for correctness.

### 11.4 Pre-commit Configuration

A minimal `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

This is installed once and runs automatically on every commit. No agent
attention required after setup.

---

## Appendix A: Phase Dependency Graph

```
                         Experiment Corpus
                              (RAG)
                                │
                                │  queried throughout
                                ▼
Physics Prompt ──────► Phase 1: Strategy ◄──────────────────────┐
                                │                               │
                                ▼                               │
                       Phase 2: Exploration ◄───────────────┐   │
                                │                           │   │
                     ┌──────────┼──────────┐                │   │
                     │     (per channel)   │                │   │
                     ▼                     ▼                │   │
                  Phase 3a            Phase 3b ...          │   │
                  Channel A           Channel B             │   │
                     │                     │                │   │
                     └──────────┬──────────┘         phase regression
                                │                    (if fundamental
                                ▼                     issue found)
                       Phase 4a: Expected Results           │   │
                                │                           │   │
                        ★ AGENT GATE ★ (3-bot) ─────────────┘   │
                                │                               │
                       Phase 4b: Partial Unblinding (10%)       │
                                │                               │
                        ★ 3-BOT REVIEW ★ ──────────────────────┘
                                │
                        ★ HUMAN GATE ★
                        (draft note + 10% results → human)
                                │
                       Phase 4c: Full Unblinding
                                │
                                ▼
                       Phase 5: Documentation
```

---

## Appendix B: Minimal Artifact Checklist

| Phase | Must contain |
|-------|-------------|
| Strategy | Signal/background enumeration, selection approach, blinding plan, systematics categories, literature citations |
| Exploration | Sample inventory, data quality assessment, variable ranking, preselection cutflow |
| Selection & Modeling | Selection definition, region definitions, background estimates, closure tests |
| 4a: Expected | Systematic table, fit model, expected results, signal injection tests |
| 4b: Partial (10%) | 10% observed results, post-fit diagnostics, GoF, draft analysis note |
| 4c: Full observed | Full observed results, post-fit diagnostics, anomaly assessment |
| Documentation | Complete analysis note with all sections, figures, citations |
