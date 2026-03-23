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

### Analysis Philosophy

**Correctness above all else.** The single most important property of an
analysis is that it produces the right answer with honest uncertainties.
No amount of completeness, polish, or thoroughness compensates for a wrong
result. Agents should spend as much time as needed — hours, iterations,
multiple approaches — to be confident the result is correct. A slow,
correct analysis is infinitely more valuable than a fast, wrong one.

Concretely:
- When two approaches exist and one is faster but less rigorous, use the
  more rigorous one.
- When a validation test gives an unexpected result, investigate until you
  understand WHY — not just until you can rationalize it.
- When a systematic seems too small or too large, verify it independently
  before accepting it.
- When the result disagrees with a published value, assume you are wrong
  until you can prove otherwise.
- When you're unsure whether an approximation is valid, compute both the
  approximate and exact versions and compare.

The goal is not to pass all review gates. It is to produce the most
convincing and thorough physics result achievable with the available data
and computational resources. Review gates catch errors; they do not define
the ceiling of quality. An analysis that passes every gate but produces a
mediocre result has failed in spirit.

**The "nodding physicist" test.** At every phase — including Phase 4a —
ask: "Would a physicist reading this artifact find every step
well-motivated, every number well-supported, and every limitation
honestly assessed with evidence that improvement was attempted?" If the
answer is no, the artifact is not ready for submission. This test applies
to artifacts, to the AN at every stage, and to individual systematic
evaluations. A Phase 4a AN should already read like a draft physics
paper, not a technical checkpoint.

**Solve problems, don't accept limitations.** When you encounter a
limitation (poor tagger purity, single generator, uncalibrated variable,
missing published data, dominant systematic), your first response must
be to try to solve it:

- **Poor tagger purity** → try alternative tagging approaches: different
  variables, different thresholds, PID-based truth labels, contamination
  matrix correction. An AUC of 0.76 is workable with the right
  correction framework.
- **Single generator** → generate particle-level predictions from modern
  generators. Running PYTHIA 8 Monash or HERWIG 7 at particle level for
  e+e- → hadrons at the Z pole takes ~30 minutes (install, configure,
  generate 1M events, compute observable). This is expected at Phase 4a,
  not deferred to Phase 5. Downscoping this requires documented evidence
  that installation or generation actually failed — not just that it
  wasn't attempted.
- **Uncalibrated variable** → attempt data-driven calibration before
  assigning a flat systematic. Reweight, derive scale factors from
  control samples, or use published measurements. Calibration directly
  improves your result; a flat systematic just inflates your errors.
- **Missing published data** → digitize from thesis or paper figures,
  query the LEP corpus, extract from HEPData, read the actual paper.
  Every measurement should be compared to something.
- **Dominant systematic** → investigate whether a better evaluation
  method exists. Decompose into components (normalization vs shape).
  Check whether the variation is physically motivated or an artifact
  of the evaluation procedure. A 10x-larger-than-published systematic
  is almost always an evaluation problem, not a physics truth.
- **Data/MC disagreement** → this is a calibration opportunity, not just
  a "data quality finding." Identify the source, derive a correction,
  verify it reduces the disagreement. An uncalibrated systematic is
  always larger than a calibrated one.

Accept a limitation ONLY when: (a) you have tried at least one concrete
approach to solve it, (b) the approach failed for a documented, specific
reason (not "it's hard" or "it would take too long"), and (c) solving
it would genuinely require multi-day computation or external resources
you don't have. Document what you tried and why it didn't work. A
limitation with evidence of attempted improvement is honest. A
limitation without evidence of attempted improvement is lazy — and
reviewers should treat it as Category B.

**Every measurement needs context.** A number without comparison is not
a physics result. After presenting any measurement:

1. Compare to the published reference or expectation
2. State whether it is consistent, and if not, why
3. State what physics question the measurement helps answer
4. State what deviations the measurement could detect (resolving power)

Example of insufficient prose: "The tracking efficiency systematic is
0.95%." Example of adequate prose: "The tracking efficiency systematic
is 0.95%, evaluated by randomly dropping 1% of tracks (conservative
upper bound on ALEPH tracking inefficiency of ~0.3% per track, based on
tracking resolution studies in [ref]). This is consistent with the
0.5–1.5% range found in published ALEPH measurements [ref1, ref2]. The
impact on the EEC is largest in the forward region where low-momentum
tracks dominate."

**Cross-checks are not overhead — they are the physics content.** A
measurement with three independent cross-checks that all agree is far
more convincing than a measurement with tighter error bars but no
cross-checks. Proactively identify and implement:
- Alternative unfolding/correction method (IBU vs bin-by-bin)
- Alternative selection (tight vs loose cuts)
- Subperiod stability (year-by-year, run-by-run)
- Published result overlay with chi2
- Theory prediction comparison (not just the generator used for
  corrections)

**Published result overlay is mandatory.** If published results exist
for the same or similar observable, extract the numerical values and
overlay them on your measurement plot with a chi2. A measurement
presented in isolation — without comparison to any published result or
theory prediction — is incomplete. The comparison IS the physics content.
Phase 1 must extract published values; Phase 4a must overlay them.
Deferring the overlay to Phase 5 is Category B.

**Implement improvements, don't defer them.** When you identify a
feasible improvement during the analysis — a better tagging method,
a generator comparison, a calibration, a published overlay — the
question is: "Can this be done in < 2 hours?" If yes, do it now. "Future
Directions" is for genuinely infeasible items (new data, new algorithms,
multi-day computation). It is NOT for tasks like running PYTHIA 8 at
particle level (~30 min), trying a contamination matrix correction
(~1 hour), or decomposing a systematic into components (~1 hour). These
were all deferred to "Future Directions" in actual analyses and later
implemented in ~1 hour during regression, producing large improvements.
The analysis would have been stronger if they had been done originally.
See §12 for the full policy.

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
- Identify 2-3 reference analyses, tabulate their systematic programs.
  **Extract published numerical results** (central values and uncertainties
  at representative kinematic points) from the reference analyses and record
  them in the strategy artifact. These become binding comparison targets at
  Phase 4c review (per §6.8). Do not defer literature data extraction to
  Phase 5 — the comparison values must be available before Phase 4a so the
  executor can include quantitative comparison plots from the start.
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
- **Published yield cross-check (pre-selected data).** When the data has
  been pre-selected at ntuple production ("aftercut", "skimmed", or
  similar), the pre-selection efficiency is an unmeasured correction
  that will propagate to the cross-section. Characterize it in Phase 2:
  1. From cited references, obtain the published luminosity and
     cross-section at each energy point.
  2. Compute expected event counts: N_exp = L_pub × sigma_pub.
  3. Compare to observed event counts in the ntuples: N_obs.
  4. The ratio f_presel = N_obs / N_exp is the pre-selection efficiency.
  5. Tabulate f_presel per energy point and per year. Flag any
     energy dependence — if f_presel varies by more than 2% across
     energy points, it will bias lineshape/shape measurements unless
     corrected. This is a Phase 4 input, not a curiosity.
  6. If f_presel cannot be computed (no published luminosity), document
     this as a limitation and plan for Phase 4.

  This cross-check catches two problems early: (a) energy-dependent
  pre-selection that would distort the lineshape, and (b) mismatched
  data periods (archived files containing events from unpublished
  sub-periods for which no luminosity is available).

**Data discovery:** Metadata first → small slice (~1000 events) → identify
jagged structure → document schema.

**Data archaeology protocol (archived/open data).** When working with
archived data that was not produced by the analysis team, unexpected
properties can fundamentally change what is feasible. Phase 2 must
systematically discover these before Phase 3 begins:

1. **Check all weight/flag branches for non-triviality.** Print unique
   values, range, and mean for every branch that could be a weight,
   flag, or quality indicator. Non-trivial weights (not all 1.0) must
   be understood and documented — they affect every downstream
   computation. Example: per-track `weight` ranging 0.08-4.5 discovered
   in one analysis; ignoring it would bias the measurement.
2. **Check what processing has been applied.** Compare event counts to
   published cross-section × luminosity. If counts are significantly
   lower, the data has been pre-selected at ntuple production level.
   Determine what was cut (hadronic selection? quality flags? fiducial
   cuts?) and document the impact on feasibility of planned
   measurements. Example: one analysis discovered leptonic events were
   entirely absent from "aftercut" ntuples, making per-channel leptonic
   measurements impossible.
3. **Check MC generation parameters.** Verify the generator, tune, beam
   energy, and process match the data-taking conditions. If MC is limited
   to a single energy point or year, document the coverage gap and plan
   for Phase 4 uncertainty treatment.
4. **Check for truth-level information.** What generator-level quantities
   are available? What particle-level definition can be supported? Are
   truth-matching variables present? If truth labels needed for tagging
   or closure are absent, document alternatives.
5. **Strategy revision gate.** If any discovery materially changes the
   feasibility of a planned measurement (e.g., required branches absent,
   truth labels unavailable, dominant weight not understood, leptonic
   events pre-selected away), the exploration artifact must flag this as
   a **strategy revision input** with a clear statement of what changed
   and what the implications are. The orchestrator must then re-read the
   Phase 1 strategy and update it before Phase 3 begins — revising
   scope, adjusting the systematic plan, or formally downscoping
   measurements that are no longer feasible. This is not a regression —
   it is the normal flow when Phase 2 reveals that Phase 1 assumptions
   were incorrect. The strategy revision follows the same format as the
   original strategy (updated STRATEGY.md with a change log entry) and
   receives a lightweight re-review (1-bot) focusing on the changed
   sections.

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

  **When the majority of inputs fail the quality gate**, the MVA approach
  may still be viable if: (1) the BDT output data/MC disagreement is
  smaller than the input-level disagreement (classifiers compress
  mismodeled inputs), AND (2) data-driven scale factors can be derived
  for the BDT output in a control region with an appropriate systematic
  uncertainty. This calibrate-then-use approach is standard practice for
  b-tagging at the LHC and should be attempted before rejecting an MVA
  that provides better discrimination than simpler alternatives.
  Rejection of an MVA solely on the input quality gate — without
  evaluating the output data/MC agreement or attempting calibration — is
  Category B at review (limitation accepted without evidence of attempted
  improvement). The AN must document either the calibration attempt and
  its result, or a quantitative argument for why calibration is infeasible
  (e.g., no independent control sample, single MC generator prevents
  cross-check of calibration stability).

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

**Closure test alarm bands (mandatory, non-negotiable).** These apply at
Phase 3 AND Phase 4a. The executor must not rationalize away failures:

- **chi2/ndf < 0.1:** Category A — suspiciously good. Investigate
  uncertainty inflation (common: loop accumulating variance across bins),
  tautological test construction (applying correction back to derivation
  sample), or accidentally using the same sample for derivation and
  testing. A chi2/ndf of 0.01 is not "excellent closure" — it means
  your uncertainties are 10x too large or your test has no diagnostic
  power.
- **chi2/ndf > 3 OR any single pull > 5-sigma:** Category A — method
  failure. The method does not work on the sample it was derived from.
  Do not proceed. The ONLY acceptable responses are: (a) find and fix
  the bug, (b) redesign the method, (c) fix the test if it is flawed,
  or (d) formally abandon the measurement with documentation.
- **Closure `passes: false` in machine-readable output while artifact
  text claims the result is acceptable:** Category A —
  misrepresentation. If the closure test fails, say it fails. "Known
  limitation" and "acceptable bias" are not valid framings for a method
  that cannot reproduce the correct answer on its own training sample.
  The first hypothesis for a closure failure is always a code bug
  (wrong sign, wrong formula, wrong variable), not a physics effect.

These alarm bands exist because agents consistently rationalize
catastrophic closures: chi2/ndf = 0.01 called "good," -287 sigma called
"known limitation," -12.6 sigma framed as "acceptable." The spec does
not permit this. A closure test that fails is a method that doesn't work.

**Artifact:** `SELECTION.md`. **Review:** 1-bot (§6).

---

### Phase 4: Statistical Analysis

Three sub-phases. **Both measurements and searches follow 4a → 4b → 4c.**

#### Phase 4a: Expected Results

**Goal:** Systematics, statistical model, expected results on Asimov only.

- **Published input lookup protocol.** When the strategy commits to a
  published value from a cited paper (e.g., "luminosity from
  hep-ex/9904007" [D1]), the executor must obtain the actual published
  values — not derive them from the data. RAG passage retrieval may
  fail to surface specific tables; this does not mean the values are
  unavailable. Escalation order:
  1. Query RAG with specific terms (paper ID + "Table" + quantity name)
  2. Use `get_paper` to retrieve the paper's section structure, then
     search for the relevant section
  3. Fetch the actual PDF and read the relevant pages
  4. If still not found: escalate to the orchestrator as a **blocker**

  "I searched the corpus and didn't find it, so I derived the values
  from the data instead" is NOT an acceptable resolution of a binding
  commitment. The paper exists; the table is in it; read the paper.
  Substituting a data-derived value for a committed published value
  is a silent violation of the strategy and Category A at review.

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
- **No inflated uncertainties.** Uncertainty inflation is as harmful as
  underestimation — it makes pull checks pass trivially, masks method
  biases, and destroys resolving power. A measurement that is "consistent
  with everything" is not a measurement. Apply these checks:

  1. **Re-evaluate, don't transfer.** When a systematic was evaluated on
     MC in Phase 4a and a data-based evaluation is available in 4c, the
     data evaluation takes precedence. Using the MC value when it is >2x
     the data value is inflation unless the MC value is justified as more
     representative (e.g., the data spread is artificially small due to
     statistical fluctuation in a finite scan). Document the comparison.
  2. **No "conservative" rounding up.** A systematic of 0.006 evaluated
     on data does not become 0.017 because the MC gave 0.017. Use the
     value that corresponds to the actual dataset the result is quoted on.
  3. **Resolving power check.** If the total uncertainty means the result
     cannot distinguish the SM from a ±20% deviation at 2-sigma, state
     this explicitly. A result whose error bars span the entire
     physically interesting range is honest only if it says so.
  4. **Budget cross-check.** Compare the total uncertainty to the naive
     expectation from the data size and method. If the observed total is
     significantly larger than what a simple sqrt(N) scaling from a
     published result would predict (after accounting for differences in
     b-purity, acceptance, etc.), identify which systematic is responsible
     and verify it is not inflated.
  5. **Pull distribution sanity.** If the analysis reports multiple
     independent results or cross-checks, the distribution of pulls
     versus reference values should be roughly unit-Gaussian. If all
     pulls are < 0.5σ and the uncertainties are large, this is a sign
     of inflation — properly sized uncertainties produce ~32% of pulls
     above 1σ. (This check requires ≥5 independent quantities to be
     meaningful.)

  At review, the question is symmetric: "Is this uncertainty too small?"
  AND "Is this uncertainty too large?" A reviewer who only checks for
  missing systematics but never questions inflated ones is doing half the
  job.

- **Overcoverage investigation (mandatory when pull RMS < 0.7).** If the
  distribution of pulls (measured vs expected, or data vs MC) has RMS
  significantly below 1.0 (< 0.7), the uncertainties are overestimated.
  This is not automatically wrong, but it MUST be discussed:

  1. Identify which systematic source dominates the overcoverage (usually
     the largest one).
  2. Estimate what the pull RMS would be without that source. If it rises
     to ~1.0, that source is the culprit.
  3. State explicitly: "The total uncertainty is dominated by [source],
     which may be conservatively overestimated. The measurement's
     resolving power is limited by this conservative assignment rather
     than by the data."

  Overcoverage erodes resolving power — a measurement that "agrees with
  everything" because the error bars are enormous is not informative.
  This is Category B at review; it becomes Category A if the overcoverage
  is not discussed in the AN.

- **Known-underestimate protocol.** When an independent cross-check
  (generator comparison, alternative method, data-driven evaluation)
  reveals that the true variation is N× larger than the assigned
  systematic:

  1. If N ≥ 2: the independent cross-check MUST either replace or inflate
     the assigned systematic. "Lower bound" labeling is not sufficient —
     the measurement's total uncertainty is wrong if a known-larger
     variation is documented but not incorporated.
  2. If the independent variation uses a different evaluation level (e.g.,
     generator-level vs correction-factor-level), estimate the correction-
     factor-level equivalent. If estimation is infeasible, assign the
     generator-level difference as a conservative upper bound and document
     the approximation.
  3. The AN must state: "The [source] systematic of X% is a [lower bound /
     central estimate]. An independent comparison using [method] shows Y%
     variation. The total uncertainty [incorporates / does not incorporate]
     this larger variation because [reason]."

  This protocol exists because two pilot analyses documented generator
  variations 4-5× larger than their assigned MC model systematic but used
  the smaller value for the total uncertainty without inflating it.

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

- **Systematic implementation self-check (mandatory before submission).**
  For each systematic variation, verify these properties and document the
  verification in the artifact:
  1. **The varied quantity actually changes:** Print `nominal_value` vs
     `varied_value` for the underlying physics input. If identical → bug.
  2. **The impact is non-zero in at least some bins.** Exactly zero
     everywhere → bug or no-op variation (see zero-impact check above).
  3. **The impact has the expected sign/direction.** Increasing
     resolution should reduce correction factors. Dropping tracks should
     reduce multiplicity. A systematic that moves in the wrong direction
     likely has a sign error or is evaluating the wrong quantity.
  4. **The evaluation level is consistent.** Gen-level systematics must
     be evaluated at gen level; reco-level at reco level. Mixing levels
     (e.g., reco-based tag but gen-level bins) conflates detector effects
     with physics and produces uninterpretable shifts.
  5. **The variation was propagated, not borrowed.** A systematic
     assigned a flat percentage without running the varied input through
     the analysis chain is a borrowed systematic. Mark it explicitly as
     `[borrowed]` and justify per the no-borrowed-flat-systematics rule.

  This self-check exists because 4 of 8 systematics in one analysis had
  implementation bugs (flat assignment, missing entirely, no-op smearing,
  wrong evaluation level). These were caught by reviewers, but the
  executor should have caught them first.

- **Generator comparison as concrete default action.** For analyses
  measuring hadronic observables at the Z pole, generating standalone
  particle-level predictions from at least one modern generator (PYTHIA 8
  Monash, HERWIG 7, Sherpa) is an expected Phase 4a deliverable — not a
  Phase 5 "nice to have" or a commitment to be silently downscoped.
  Particle-level generation (no detector simulation) for 1M e+e- → Z →
  hadrons events takes ~30 minutes: install the generator, write a
  steering card, generate events, compute the observable at particle
  level, and overlay on the corrected measurement. If the archived MC
  is the only generator available for corrections, this standalone
  comparison provides the only genuine hadronization model dependence
  estimate. Downscoping to "literature-based hadronization systematic"
  is acceptable ONLY if generator installation genuinely fails — with
  documented error messages, not "it wasn't attempted."

- **COMMITMENTS.md (mandatory tracking artifact).** At Phase 1 completion,
  create `COMMITMENTS.md` listing every Phase 1 commitment — systematic
  sources, cross-checks, validation tests, comparison targets, planned
  figures — with a machine-readable status:
  ```
  - [x] D1: EEC self-pair convention (i<j) — resolved Phase 1
  - [D] D11: PYTHIA 8/HERWIG 7 standalone — downscoped Phase 4a
        (PYTHIA 8 installation failed: [error])
  - [ ] A1: Published ALEPH EEC overlay — NOT YET ADDRESSED
  ```
  Update COMMITMENTS.md at every phase boundary. At Phase 5 review, the
  reviewer MUST verify every line is either `[x]` (resolved) or `[D]`
  (formally downscoped with documented justification). Any `[ ]`
  remaining at Phase 5 is Category A. This prevents Phase 1 commitments
  from being silently dropped — a pattern observed in 3 of 4 analyses.

- **Phase 4a as draft physics result.** The Phase 4a artifact and AN
  are not a technical checkpoint — they are a draft physics result. A
  physicist picking up the Phase 4a AN should be able to understand:
  - What is being measured and why (with equations defining the
    observable and the extraction/correction procedure)
  - How it compares to published values (with overlaid comparison and
    chi2, not just a table of numbers)
  - What the dominant uncertainties are and whether they are
    well-motivated (with physical origin, not just "tracking: 0.95%")
  - What limitations exist and what was attempted to address them (with
    documentation of attempted improvements, not just acceptance)
  - Whether the measurement is competitive with published results (with
    explicit resolving-power statement)

  The Phase 4a AN must contain at minimum: equations defining the
  observable, the correction procedure, and the systematic evaluation;
  a comparison overlay with published measurements; a systematic
  completeness table with physical motivations; and a "money plot"
  showing the expected measurement with total uncertainty band. If the
  Phase 4a AN would not make a physicist nod along, it is not ready.

**Artifact:** `INFERENCE_EXPECTED.md` + `ANALYSIS_NOTE_4a_v1.md` (complete
AN with all detail using expected-only results; 4b/4c update numbers,
Phase 5 polishes prose and typesets).

**Number consistency gate (every AN compilation).** Before compiling any
AN version (4a, 4b, 4c, or 5), the note writer must verify that all
numerical values in the AN match the latest machine-readable outputs
from the current phase's inference artifacts or `results/` directory.
Systematic uncertainties, central values, event counts, selection
efficiencies — everything must be current. Any discrepancy > 1% relative
is Category A. This gate prevents stale numbers from earlier phases
propagating forward — a problem observed when a systematic was revised
from 9.3% to 1.7% but the AN abstract still quoted the old value.

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
- **Fit triviality gate (mandatory).** If the fit chi^2 is identically
  zero (or within numerical precision of zero), OR if the fitted
  parameters exactly equal the input assumptions used elsewhere in the
  analysis chain, the executor must STOP and investigate whether the
  methodology is algebraically circular. chi^2 = 0.000 is not
  "excellent fit quality" — it is an alarm that the measurement may
  be trivially self-consistent. Before proceeding:
  1. Trace every input to the cross-section formula: where does each
     luminosity, efficiency, and background fraction come from?
  2. If any input was derived using the same theoretical cross-section
     that the fit is trying to measure, the fit is circular.
  3. If circular: investigate whether independent inputs exist
     (published luminosities, external efficiency measurements).
     Check the cited reference papers for data tables.
  4. Only after exhausting alternatives may the analysis proceed with
     circular inputs, and in that case the results must be presented
     as "self-consistency check" values, not measurements.
  This gate applies even if the executor already acknowledges the
  circularity. Acknowledgment is not remediation. A measurement
  that is circular when non-circular inputs exist is Category A.

- **Poor GoF → investigate calibration (mandatory).** When a fit
  produces chi2/ndf >> 1 (e.g., > 10) after introducing a correction
  that was previously absent (switching from derived to published
  luminosities, adding an efficiency correction, changing the
  background model), the first hypothesis is a **missing calibration**
  — an energy-dependent, time-dependent, or sample-dependent detector
  effect that was previously absorbed by the derived quantity and is
  now exposed.

  Do NOT conclude "the correction doesn't work" or revert to the
  uncorrected (possibly circular) approach. Instead:
  1. Examine the residuals per data point. Which points drive the chi2?
  2. Check whether the problematic points share a common property
     (energy region, data-taking year, detector configuration).
  3. Compute the ratio of observed to expected yields at each point.
     A smooth, non-flat ratio indicates an unmeasured efficiency
     that varies with the relevant dimension.
  4. Calibrate the missing efficiency using published reference values
     (cross-sections, event counts) at each point. This is a standard
     detector calibration — using a known candle to measure response.
  5. Refit with the calibrated corrections. The chi2 should improve
     dramatically. If it doesn't, the problem is elsewhere.

  This pattern — "correct result appears only after calibrating an
  effect that was hidden by a circular derivation" — is common in
  precision measurements with archived or reprocessed data.

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

- **Competitiveness assessment (multi-observable analyses).** When an
  analysis extracts multiple quantities, each must be assessed not just
  for viability but for competitiveness. If total uncertainty (stat ⊕
  syst) exceeds the published reference precision by > 5×, the
  measurement is non-competitive. This is not automatically a problem,
  but it requires a decision:
  - If the dominant systematic is methodological (not fundamental) and
    an alternative method is feasible (< 2 hours of implementation),
    the executor SHOULD attempt the improvement before Phase 4c. A
    measurement that is non-competitive due to a methodological choice
    when a better method exists is a missed opportunity.
  - If the measurement is genuinely limited by the data or detector,
    label it as "non-competitive" in the AN and state what it would
    take to make it competitive (more data, better MC, different
    detector).
  - Non-competitive measurements may still be reported but must not be
    presented as if they are competitive. "Consistent with the SM" is
    vacuous when the error bars span the entire physically interesting
    range.
  This assessment exists because one analysis carried a 72% relative
  uncertainty measurement through to Phase 5 before anyone questioned
  whether improvement was feasible — and a 30-minute method change
  produced a 10× improvement.

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

**Interpretive quality.** The note writer must ensure every section passes
the "nodding physicist" test. Concrete requirements:
- **Minimum 4 equations:** observable definition, correction procedure,
  systematic evaluation formula, fit/extraction model. Zero equations
  is Category A.
- **Every result has context:** after each results table or key figure,
  2-3 sentences interpreting what the numbers mean physically. Compare
  to published values. State whether consistent and why.
- **Validation summary table:** tabulate every validation test (closure,
  stress, stability, cross-checks) with chi2/ndf, p-value, and verdict.
- **Resolving power statement:** after the final result, state what
  deviations the measurement can detect at 2-sigma.
- **Published overlay:** at least one figure overlaying measured values
  with published results and chi2 annotation.

**Number consistency gate.** Before PDF compilation, verify all numerical
values in the AN match the machine-readable JSON outputs in `results/`.
Systematic uncertainties, central values, event counts — everything must
be current. Any discrepancy > 1% relative is Category A.

**Figure composition annotations (mandatory).** The note writer knows
which figures are related — it is writing the prose around them. When
referencing a group of related figures (per-variable data/MC comparisons,
per-systematic impact maps, per-cut distributions, nominal + uncertainty
pairs), the note writer MUST annotate the grouping in the markdown using
HTML comments that the typesetter reads:

```markdown
<!-- COMPOSE: 2x3 grid -->
![Charged multiplicity...](figures/datamc_nch.pdf){#fig:datamc-a}
![Visible energy...](figures/datamc_evis.pdf){#fig:datamc-b}
![Thrust...](figures/datamc_thrust.pdf){#fig:datamc-c}
![Sphericity...](figures/datamc_spher.pdf){#fig:datamc-d}
![Aplanarity...](figures/datamc_aplan.pdf){#fig:datamc-e}
![cos θ_T...](figures/datamc_costheta.pdf){#fig:datamc-f}

Pre-selection data/MC comparisons for the six key kinematic variables.
Agreement is within 5% across all variables...
```

Annotation syntax:
- `<!-- COMPOSE: NxM grid -->` — merge the next N×M figures into a
  single multi-panel figure with one shared caption
- `<!-- COMPOSE: side-by-side -->` — merge the next 2 figures as
  (a)/(b) panels (e.g., nominal + uncertainty maps)
- `<!-- COMPOSE: 1xN row -->` — merge into a single-row layout
- `<!-- FLAGSHIP -->` — this figure gets full-page standalone treatment

The note writer has the physics context to decide what belongs together:
data/MC for the same selection stage, systematic shifts for related
sources, year-by-year stability comparisons. This grouping decision is
a physics judgment, not a typesetting judgment.

These annotations persist across AN versions (4a → 4b → 4c → 5) because
the note writer updates the existing AN rather than rewriting from
scratch. When new figures are added in later phases, the note writer
adds them with appropriate annotations. The typesetter reads the
annotations and converts them to side-by-side `\includegraphics` layouts
with `\hspace` gaps — its merge scan becomes a safety net (catching
ungrouped runs of 3+ sequential figures) rather than the primary grouping
mechanism.

**Typesetting.** Runs AFTER the AN is written. The typesetting concern:
- Runs `pandoc` to convert the markdown AN to `.tex` (not PDF):
  `pandoc ANALYSIS_NOTE_5_v1.md -o ANALYSIS_NOTE_5_v1.tex --standalone
  --include-in-header=../../conventions/preamble.tex
  --number-sections --toc --filter pandoc-crossref --citeproc`
- Runs `postprocess_tex.py` which handles all deterministic structural
  fixes automatically: title math (sqrt(s)→$\sqrt{s}$), escaped
  standalone math ($\pm$→proper LaTeX), margins, abstract→environment,
  references unnumbering, table spacing, short longtable→table
  conversion, FloatBarrier insertion, needspace, duplicate header/label
  removal, appendix insertion, clearpage placement, and stale phase
  label warnings.
- The typesetter then reads the `.tex` and does judgment-requiring work:
  - **Combine related figures** into `\begin{figure}` environments
    with side-by-side `\includegraphics` calls separated by
    `\hspace{0.01-0.02\linewidth}`. Do NOT use `\subfloat` — use
    unified captions with (a)/(b)/(c) labels instead.
    **Primary source: note writer annotations.** The note writer marks
    figure groups with `<!-- COMPOSE: ... -->` comments in the
    markdown. These annotations survive pandoc conversion as HTML
    comments in the `.tex` (`%` lines or stripped — the typesetter
    should search for `COMPOSE` in the markdown source). Convert each
    annotated group to side-by-side `\includegraphics` layouts with
    a shared caption.
    Figures marked `<!-- FLAGSHIP -->` get standalone full-page
    treatment. The typesetter's merge scan (below) is a safety net
    for ungrouped figures, not the primary grouping mechanism.
    **Mandatory merge candidates** (Category A if left standalone):
    - Per-variable distribution surveys (e.g., data/MC for 8 input
      variables → one 2x4 or 3x3 grid, not 8 separate figures)
    - Per-systematic shift/impact maps for similar sources
    - Per-cut before/after comparisons
    - Per-subperiod or per-category comparisons
    - Sequential figures of the same type differing only in one
      parameter (bin, region, category, angular range)
    - **Nominal + uncertainty pairs.** When a 2D map (migration
      matrix, response matrix, correction map, efficiency map) is
      followed by its associated uncertainty or relative-uncertainty
      map, these MUST be placed side-by-side as (a)/(b) panels
      within a single `\begin{figure}`. The nominal map is panel
      (a), the uncertainty map is panel (b). This applies to any
      quantity-plus-uncertainty pair sharing the same binning axes —
      the reader needs them adjacent for interpretation.
    The rule: if N consecutive figures share the same axes, layout,
    and differ only in a label or parameter, they MUST be merged
    into a single multi-panel figure. Scan the figure list for runs
    of 3+ sequential related figures — these are merge candidates.
    Additionally, scan for any figure immediately followed by its
    uncertainty counterpart (look for captions or filenames
    containing "uncertainty", "error", "sigma", "stat_unc",
    "rel_unc") — these are mandatory pairs.
    After merging, write one composite caption that describes the
    variation across panels.
  - **Convert longtable to table** — ensure no column overflow, use
    `\resizebox` or `\small` for wide tables.
  - **Verify every section has prose** — no bare headings before
    figures.
  - **Check caption quality** — flag any caption under 2 sentences.
- **Compile → read → fix loop.** The typesetter iterates:
  1. Compile the `.tex` to PDF via `tectonic` (or `pdflatex`). Fix
     any compilation errors.
  2. Read the compiled PDF and check for visual issues: broken
     figures, unresolved cross-references, content overflow,
     different-height panels in composites, unreadable text at
     rendered size, cut-off content, awkward page breaks.
  3. If issues found: fix the `.tex`, recompile, re-read.
  4. Iterate until the PDF passes all visual checks (max 3
     iterations before flagging to the orchestrator).
  A single compile-and-ship pass is not acceptable — the typesetter
  must visually verify the rendered output.
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
