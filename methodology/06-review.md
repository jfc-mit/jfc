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

### 6.3 Reviewer Framing

The critical reviewer's job is not to check whether the artifact meets its
own stated criteria. It is to evaluate whether the artifact would survive
**external scrutiny** — a journal referee, a collaboration review committee,
or a competing group doing the same measurement independently.

The key question is not "does this pass its tests?" but "what would a
knowledgeable referee ask for that isn't here?" This requires the reviewer
to bring external standards to the evaluation:

- **Conventions:** What does the applicable `conventions/` document require
  for this analysis technique? Is anything missing?
- **Reference analyses:** What did published measurements of the same or
  similar observables do? Is anything they did missing here?
- **Literature:** Would a query to the RAG corpus surface a standard
  practice that this analysis omits?

A reviewer that only checks internal consistency will miss the most
dangerous class of errors: things that are absent. Closure tests passing,
fits converging, and chi2 values below threshold are necessary but not
sufficient. The reviewer must also check that the *right things* are being
tested.

**Concrete operating principle:** Before concluding the review, the reviewer
must answer: "If a competing group published a measurement of the same
quantity next month, what would they have that we don't?" If the answer is
non-empty and unjustified, those are Category A findings.

### 6.4 Review Focus by Phase

| Phase | Review focus |
|-------|-------------|
| Strategy | Are backgrounds complete? Is the approach motivated by the literature? Does the systematic plan cover the standard sources for this analysis type (consult `conventions/`)? Are 2-3 reference analyses identified with their systematic programs tabulated? |
| Exploration | (Self-review) Are samples complete? Any data quality issues? Do distributions look physical? |
| Selection & Modeling | Does the background model close? Is every cut motivated by a plot? Is signal contamination controlled? Are particle-level inputs to the observable validated with data/MC comparisons per object category? |
| 4a: Expected | Is the fit healthy? Are systematics complete — both internally consistent AND complete relative to conventions and reference analyses? Do signal injection tests pass? |
| 4b: Partial unblinding | Is the draft note publication-quality? Are 10% results consistent with expectations? Are diagnostics clean? |
| 4c: Full unblinding | Are post-fit diagnostics healthy? Are anomalies properly characterized? |
| Documentation | See 6.4.3 below. |

#### 6.4.1 Completeness Review (Phases 1 and 4a)

Reviews at Phase 1 (Strategy) and Phase 4a (Expected Results) must include an
explicit **completeness check** in addition to the standard correctness review.
The completeness check asks what is *missing*, not just whether what is
*present* is correct.

**At Phase 1:**
- Consult the applicable `conventions/` document for the analysis technique
  (e.g., `conventions/unfolding.md` for an unfolded measurement). Verify that
  the planned systematic program covers the standard sources listed there.
  Flag any omission as Category A unless the strategy explicitly justifies
  the omission.
- Verify that the strategy identifies 2-3 published reference analyses and
  tabulates their systematic programs. If this table is missing, flag as
  Category A.

**At Phase 4a:**
- Re-check the conventions document against the *implemented* systematic
  program, not just the planned one. Sources that were planned but dropped
  during execution must be justified.
- Produce or verify a **systematic completeness table** comparing this
  analysis to the reference analyses identified in Phase 1:

  ```
  | Source           | This analysis | Ref 1 | Ref 2 | Status  |
  |------------------|---------------|-------|-------|---------|
  | Hadronization    | Pythia only   | P+H   | P+H+S | MISSING |
  | ...              |               |       |       |         |
  ```

  Any row with status MISSING or PARTIAL is Category A unless explicitly
  justified (e.g., resource unavailable — documented as a limitation, not
  silently omitted).

- Cross-check the conventions document's "required validation checks"
  against the artifact. For unfolded measurements, this includes the
  prior-sensitivity test and the particle-level validation plots.

This completeness review is the primary defense against the failure mode
where an analysis passes all *internal* consistency checks but omits a
standard systematic source. Internal consistency (closure tests pass, fits
converge) is necessary but not sufficient — the review must also check
external completeness (are we evaluating what the field considers standard?).

#### 6.4.2 Figure and Label Review (all phases producing figures)

Every review that evaluates figures — whether self-review, 1-bot, or 3-bot —
must include a mechanical pass over all figures checking the following (see
Appendix D for the plotting template that prevents most of these). These
are Category A if wrong:

- [ ] **√s and energy labels** match the actual dataset (not copied from a
  template for a different collider or energy)
- [ ] **Experiment name** is correct in all figure text and annotations
- [ ] **No figure titles** — captions in the note replace `ax.set_title()`
- [ ] **Axis labels** include units in brackets; y-axis label matches the
  normalization actually applied
- [ ] **Luminosity / event count** annotations match the data sample used
- [ ] **Legend entries** match what is actually plotted (no stale labels from
  earlier iterations)
- [ ] **Aspect ratios and font sizes** are consistent across all figures in
  the note
- [ ] **Bin widths** are noted on the y-axis label for variable-width binning

This is a cheap check — it can be delegated to a lowest-tier model as a
mechanical pass before or during review. Metadata errors in figures destroy
reviewer trust disproportionate to their severity, because they signal that
the author did not look at their own plots.

**Known limitation: LLM visual inspection is unreliable.** Current models
are poor at catching text overlaps, alignment issues, clipped labels, and
figure sizing problems. To mitigate this:

- **Programmatic checks in plotting scripts.** Where possible, plotting code
  should validate properties that are hard to see: `assert not ax.get_title()`
  (no titles), check that axis labels are set, verify figure dimensions match
  a standard template. These run as part of the plot task and catch issues
  before review.
- **Standardized figure function.** Analyses should define a common plotting
  setup function (figure size, font sizes, axis formatting) used by all
  scripts, rather than configuring each plot independently. This prevents
  inconsistency by construction rather than by review.
- **Human spot-check.** Visual quality (overlaps, readability, aesthetics)
  should be verified by a human at Phase 5 review rather than relying on
  LLM visual inspection. The human gate at Phase 4b is a natural checkpoint
  for this.

#### 6.4.3 Documentation Review (Phase 5)

The Phase 5 review is the last line of defense. It operates on the analysis
note as a **standalone document** — the reviewer should evaluate it as a
journal referee would, not as someone who has followed the analysis from
Phase 1.

**Framing:** The reviewer reads only the analysis note (not experiment logs,
not phase artifacts, not code). The question is: "Based solely on what is
written here, am I convinced that this result is correct and complete?"

**What this catches that earlier reviews may not:**
- A systematic source that was planned in Phase 1 but quietly dropped and
  never made it into the note
- Validation evidence that exists in phase artifacts but was not included
  in the note (e.g., particle-level data/MC plots were made but not shown)
- Logical gaps: a claim is made (e.g., "the MC accurately models the
  detector response") without the evidence to support it in the document
- Quantitative results that don't add up (e.g., efficiencies or event
  counts that are inconsistent between tables)

**Required checks:**
- For every systematic source in the uncertainty table: is the method
  described, is the magnitude reported, and is validation evidence shown?
- For every comparison to a reference (published data, MC prediction):
  is a quantitative compatibility metric given, and is the level of
  agreement or tension interpreted?
- Does the note contain enough information that an independent analyst
  could reproduce the measurement? (Selection criteria, binning, unfolding
  parameters, MC samples, correction procedures.)
- Consult the applicable `conventions/` document one final time. Is
  anything required there that is absent from the note?
- Figures pass the cosmetic checklist (6.4.2).

The cost of this review is additional iteration loops if it finds gaps that
should have been caught earlier. That cost is acceptable — it is better to
iterate at Phase 5 than to publish an incomplete result.

### 6.5 Iteration and Escalation

For **3-bot reviews:** the cycle repeats until the arbiter issues PASS. There
is no hard iteration cap — correctness is the termination condition. In
practice, the orchestrator emits warnings after 3 iterations as a signal that
the issues may require human input. The arbiter should ESCALATE rather than
continue indefinitely.

For **1-bot reviews:** the executor addresses Category A items and re-submits.
Up to 2 iterations before escalation.

For **self-review:** no formal iteration — the agent corrects issues as it
finds them during execution.

### 6.6 The Human Gate

After Phase 4b's 3-bot review passes, the draft analysis note (including 10%
observed results, post-fit diagnostics, and goodness-of-fit) is presented to a
human. The human sees the complete package and either approves full unblinding,
requests changes, or halts the analysis.

This is equivalent to a collaboration internal review before unblinding. The
human should receive a professional, publication-quality document — not a
work-in-progress.

### 6.7 Model Tiering

Not every agent session requires the most capable (and expensive) model.
The principle: use the highest tier for physics reasoning and adversarial
review, mid tier for code-heavy execution, lowest tier for mechanical tasks.

| Task | Model tier |
|------|-----------|
| Strategy execution (Phase 1), 3-bot reviewers, arbiter, investigator | Highest (Opus) |
| Phase 2–4 executors, 1-bot reviewer, calibrations | Mid (Sonnet) |
| Plot generation, smoke tests, linting | Lowest (Haiku) |

A top-level switch (`model_tier: auto | uniform_high | uniform_mid`)
controls whether tiering is active. See `orchestration/reviews.md` for the
operational configuration and YAML schema.

### 6.8 Cost Controls

To prevent runaway costs from pathological iteration:

**Review iteration warnings:** The orchestrator emits a warning after **3**
review iterations and a strong warning after **5**. These are soft thresholds,
not hard caps — correctness remains the termination condition. If the arbiter
cannot reach PASS, it should ESCALATE rather than loop indefinitely. In
interactive mode, the orchestrator surfaces the warning to the human for
guidance. In batch mode, the warning is logged and the arbiter is prompted to
consider ESCALATE.

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

### 6.9 Phase Regression

The pipeline is normally forward-only, but a reviewer or executor may discover
that a fundamental assumption from an earlier phase is wrong — a major
background was missed, the selection approach is unworkable, or the data
contradicts the strategy.

When this happens:

1. The agent (or reviewer) documents the issue and identifies which earlier
   phase it originates from
2. The issue is classified as a **regression trigger** in the review artifact
3. The orchestrator spawns an **Investigator** (see below) to assess the
   impact before any re-execution begins
4. Fixes are dispatched based on the Investigator's ticket

#### The Investigator

The Investigator is a dedicated agent role (Opus-tier) spawned when a
regression trigger is flagged. It does *not* read all artifacts end-to-end.
Instead it follows a structured, minimal-read process:

1. **Read the trigger description** from the review artifact that flagged the
   regression.
2. **Read the origin phase artifact** to identify the specific wrong
   conclusion(s).
3. **Trace forward phase by phase:** for each downstream artifact, read only
   the Summary and Method sections. If the artifact depends on the wrong
   conclusion, read the full affected sections and add them to the impact list.
   If it does not, mark the phase unaffected and stop tracing that branch.
4. **Produce `REGRESSION_TICKET.md`** containing:
   - Root cause and origin phase
   - Affected phases with specific sections that must change
   - Unaffected phases with reasoning for why they are safe
   - Fix scope per affected phase (what the executor must redo)

#### The fix cycle

The orchestrator dispatches fixes automatically — no human gate for regression.

- **Origin phase:** the executor re-runs with the previous artifact, the
  regression ticket, and the experiment log as inputs. The arbiter reviews the
  before/after to confirm the root cause is resolved.
- **Affected downstream phases:** each receives the same treatment (previous
  artifact + ticket + updated upstream artifact). Fixes proceed in phase order.
- **Unaffected phases:** skipped entirely, per the Investigator's assessment.

#### Timing

Regression only triggers before the **human gate** — Phase 4c for searches,
Phase 4a for measurements. Once the human approves proceeding to final
documentation, discovered issues become Phase 5 iteration items or
documented observations, not regression triggers.

**Regression vs. documentation fix.** Not every issue found in review
requires regression. The distinction:
- **Physics issue** (wrong systematic treatment, missing background, flawed
  correction) → regression trigger. Re-run earlier phases.
- **Presentation issue** (axis label wrong, figure unclear, caption sparse,
  missing cross-reference) → Phase 5 iteration. Fix in the documentation
  without re-running earlier phases.

#### Upstream feedback (non-blocking)

Any executor may proactively produce an `UPSTREAM_FEEDBACK.md` artifact when
it encounters something an earlier phase did not consider — an unexpected
background shape, a missing systematic, a data feature not mentioned upstream.
This is *not* a regression trigger and does not block execution. The
orchestrator routes it to the next review gate for the affected upstream phase.
If the reviewers agree the issue is material, they may flag a regression
trigger through the normal mechanism.

Phase regression is expensive and should be rare. The strategy and exploration
phases exist to prevent it. But when it happens, it is better to go back and
fix the foundation than to build on a known-faulty premise.

Regression is logged in a `regression_log.md` at the analysis root, tracking
what triggered the regression, the Investigator's ticket, which phases were
re-run, and what changed.

---
