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

For **3-bot reviews:** the cycle repeats until the arbiter issues PASS. There
is no hard iteration cap — correctness is the termination condition. In
practice, the orchestrator emits warnings after 3 iterations as a signal that
the issues may require human input. The arbiter should ESCALATE rather than
continue indefinitely.

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
| Phase 4 executor (fits, systematics) | Mid | Statistical modeling is well-scoped; mid tier iterates faster |
| 1-bot reviewer | Mid | Single-reviewer phases; physics context carried by the artifact |
| Plot regeneration, reformatting | Lowest (e.g., Haiku) | Mechanical tasks with clear specifications |
| Smoke tests, linting | Lowest | Boilerplate with clear pass/fail |

A **top-level configuration switch** controls whether tiering is active:
- `model_tier: uniform_high` — all sessions use the highest model (for
  benchmarking or when cost is not a constraint)
- `model_tier: auto` — use the tiering above (default, cost-efficient):
  Opus for strategy + reviewers + arbiter, Sonnet for executors + 1-bot
  review, Haiku for plots/tests
- `model_tier: uniform_mid` — all sessions use mid tier (budget mode)

This switch exists at the orchestration level, not in the methodology spec,
so the same spec can be used for cost comparisons across configurations.

### 6.7 Cost Controls

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

### 6.8 Phase Regression

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

Regression only triggers before Phase 4c (full unblinding). Once the human
gate approves full unblinding, discovered issues become documented observations
in the final note, not regression triggers. The analysis is past the point
where re-running earlier phases is meaningful — the observed result exists.

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
