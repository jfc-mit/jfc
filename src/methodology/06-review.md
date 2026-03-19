## 6. Review Protocol

Review is mandatory at every phase gate. Skipping review is a process failure.

### 6.1 Classification

- **(A) Must resolve** — blocks advancement.
- **(B) Should address** — weakens the analysis. Must fix before PASS.
- **(C) Suggestions** — style, clarity.

### 6.2 Review Tiers

| Phase | Type | Notes |
|-------|------|-------|
| 1: Strategy | 4-bot | Sets direction; physics errors propagate |
| 2: Exploration | Self-review | Mechanical; errors caught in Phase 3 |
| 3: Processing | 1-bot | External eye on closure/modeling |
| 4a: Expected | 4-bot | Gates 10% validation |
| 4b: 10% validation | 4-bot → human gate | Draft AN must be polished |
| 4c: Full data | 1-bot | Methodology already human-approved |
| 5: Documentation | 5-bot (4 + rendering) | Final product |

**4-bot:** Physics + critical + constructive + plot validator (parallel),
then arbiter. Physics reviewer receives ONLY physics prompt + artifact.
Plot validator performs programmatic code/data checks (red flags are
auto-Category A). See `agents/` for full definitions.

**5-bot:** Adds rendering reviewer who compiles and inspects the PDF.

**1-bot:** Critical reviewer + plot validator (parallel). Category A items
→ fixer agent → re-submit.

**No self-review fallback.** All phases except Phase 2 require independent
reviewer subagents.

### 6.3 Reviewer Framing

The key question: **"What would a knowledgeable referee ask for that isn't
here?"** Check external completeness, not just internal consistency.

Before concluding, the reviewer must answer:
1. Are all sources in the applicable `conventions/` document implemented
   or justified as inapplicable?
2. Do 2-3 reference analyses exist, and does this analysis match their
   systematic coverage?
3. If a competing group published next month, what would they have that
   we don't?

"No" or "non-empty" without justification → Category A.

### 6.4 Review Focus by Phase

| Phase | Focus |
|-------|-------|
| Strategy | Backgrounds complete? Systematic plan covers conventions? 2-3 reference analyses tabulated? |
| Exploration | Samples complete? Data quality OK? Distributions physical? |
| Processing | Background model closes? Every cut motivated by plot? Cutflow monotonic? **MVA:** data/MC on classifier OK? Alternative architecture tried? |
| 4a: Expected | Systematics complete vs. conventions + references? Signal injection/closure passes? Operating point stable (Category A if not)? MC coverage matches data periods? Validation target check (§6.8). |
| 4b: 10% | Draft AN publication-quality? Results consistent with expected? Diagnostics clean? Validation target check (§6.8). |
| 4c: Full data | Post-fit diagnostics healthy? Anomalies characterized? **Validation target check:** every result compared to PDG/reference values — any pull > 3σ is Category A unless quantitatively explained (see §6.8). |
| 5: Documentation | See §6.4.3. |

#### 6.4.1 Completeness Review (Phases 1 and 4a)

**Phase 1:** Verify systematic plan covers conventions sources. Reference
analysis table present. Omissions without justification → Category A.

**Phase 4a:** Executor must produce a **systematic completeness table:**

```
| Source | Conventions | Ref 1 | Ref 2 | This analysis | Status |
```

Reviewer verifies row-by-row. MISSING without justification → Category A.
Cross-check conventions "required validation checks" against the artifact.

#### 6.4.2 Figure Review

**Reviewers must read every plot** and verify it makes physical sense. See
`appendix-plotting.md` for the complete figure checklist and standards.
Key Category A items: wrong metadata (√s, experiment, luminosity), missing
axis labels, no figure titles, clipped content, inappropriate scales.

**Figure-by-figure verification.** The reviewer must enumerate every figure
and state whether it passes or fails the plotting checklist. Specifically
check: `sharex=True` on ratio plots (no redundant x-axis labels),
`make_square_add_cbar` on 2D plots (colorbar same height as main axes),
no off-page content, described uncertainty bands in ratio panels, tight
axis limits. A blanket "figures look fine" is not acceptable — list each
figure number with its status.

#### 6.4.3 Documentation Review (Phase 5)

Reviewer reads the AN as a standalone document — as a journal referee would.
Check: every systematic described with method + impact? Every comparison
quantitative? Reproducible from the note alone? Conventions covered?

**Tautological comparisons.** If the "comparison to theory/MC" is
mathematically identical to the "comparison to expected" (e.g., the
expected result was derived from the same MC that serves as the theory
comparison), the AN must not present them as independent evidence of
consistency. Either (a) remove the redundant comparison, or (b) explicitly
state the tautology and explain what independent information, if any, the
comparison provides. Presenting tautological agreement as validation is
Category A.

### 6.5 Iteration and Escalation

**4/5-bot:** Repeat until arbiter PASS. Warn at 3, strong warn at 5, hard
cap at 10. The arbiter should ESCALATE rather than loop indefinitely.

**1-bot:** Warn at 2, escalate to human after 3.

### 6.5.1 Arbiter Dismissal Rules

**The arbiter may NOT dismiss a reviewer finding as "out of scope" if the
fix requires less than ~1 hour of agent processing time.** Re-running a
Phase 4 script with modified parameters, producing additional figures, or
propagating a systematic through an existing chain are NOT out of scope —
they are exactly the kind of work that review iterations exist for.

When multiple reviewer findings independently require re-running an
earlier phase, this is **extra motivation** to address them together in
a single regression or fix iteration, not a reason to dismiss each one
individually.

**The arbiter must justify every dismissal** with:
1. A concrete cost estimate (agent-hours, not vague "significant effort")
2. An explanation of why the finding does not affect the physics
   conclusion
3. A commitment to address it in a future phase (if applicable)

Dismissals of the form "requires reprocessing" or "out of scope for this
phase" without a cost estimate are not acceptable. Phase regression (§6.7)
exists precisely for findings that require upstream work.

### 6.6 Human Gate

Between Phase 4b and 4c for both measurements and searches. The human
receives a publication-quality draft AN with 10% results. Approves,
requests changes, or halts.

### 6.7 Phase Regression

**Regression must be triggered, not avoided.** Do not paper over upstream
problems. Concrete triggers (must not be rationalized away):
- Data/MC disagreement on observable or MVA inputs
- Closure test failure (p < 0.05)
- Stress test failure without successful remediation (see §3 validation
  failure remediation)
- Operating point instability
- Unexplained dominant systematic (a single source exceeding 80% of
  total uncertainty warrants investigation, not acceptance)
- MC used for periods without corresponding simulation
- Result > 3σ from a well-measured reference value (see §6.8)
- GoF toy distribution inconsistent with observed chi2 (the observed
  chi2 falls outside the 95% interval of the toy distribution)
- Wholesale bin exclusion: flat-prior gate or similar criterion
  excluding > 50% of measurement bins (indicates binning or method
  problem, not a systematic effect — see §3 Phase 3)
- Two distributions that should be independent appear visually
  identical (indicates a bug or tautological comparison)

**Procedure:**
1. Document issue, identify origin phase
2. Classify as regression trigger in review artifact
3. Orchestrator spawns **Investigator**: reads trigger → reads origin
   artifact → traces forward to identify affected phases →
   produces `REGRESSION_TICKET.md`
4. Fix origin phase → re-review → re-run affected downstream phases

**Timing:** Regression only before the human gate. After human approval,
issues become Phase 5 iteration items.

**Not regression:** Presentation issues (labels, captions, formatting) →
Phase 5 iteration, not regression.

**Upstream feedback (non-blocking):** Any executor may produce
`UPSTREAM_FEEDBACK.md` for issues an earlier phase missed. Routed to the
next review gate.

### 6.8 Validation Target Rule

When the Phase 1 strategy defines validation targets (PDG values, published
reference measurements), these create binding review obligations:

**The rule:** Any extracted parameter with a pull > 3σ from a well-measured
reference value is **Category A** (blocks advancement) unless the reviewer
can verify **all three** of the following:

1. **Quantitative explanation.** A specific, identified cause (not a
   narrative list of possible factors) that accounts for the observed
   deviation. "Luminosity strategy limitations" is not sufficient;
   "the Tier 2 luminosity derivation biases Γ_Z low by X MeV because Y"
   is.

2. **Demonstrated magnitude.** A calculation, fit variant, or toy study
   showing the identified cause produces a bias of the right size and
   sign. A qualitative argument that "this could bias the result" does
   not satisfy this requirement.

3. **No simpler explanation.** The reviewer has checked for bugs, sign
   errors, unit mistakes, and wrong input values before accepting a
   physics explanation.

**If the > 3σ pull cannot be quantitatively explained**, the reviewer must
classify it as Category A and recommend one of:
- Phase regression to investigate the upstream cause
- A dedicated systematic study to bound the bias
- Downscoping the affected parameter (document as not reliably extracted)

**Rationale:** Accepting large discrepancies with well-known physics values
erodes the credibility of the entire analysis. A 3σ pull may be a
statistical fluctuation, but the burden of proof is on the analysis to
demonstrate this — not on the reviewer to accept it. An analysis that
reports N_ν = 2.88 ± 0.03 without rigorous investigation of the 3.9σ
tension has a gap that a referee would immediately flag.

**This rule applies to all review tiers** (1-bot, 4-bot, 5-bot) at Phases
4a, 4b, 4c, and 5. It does not apply to Phase 1 (where targets are
defined, not yet tested) or Phases 2–3 (where results are not yet
extracted).

---
