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
| 2: Exploration | Self-review + plot validator | Mechanical; figures validated programmatically |
| 3: Processing | 1-bot | External eye on closure/modeling |
| 4a: Expected | 4-bot+bib | Gates 10% validation; AN v1 has citations |
| 4b: 10% validation | 4-bot+bib → human gate | Draft AN must be polished; bibtex validated |
| 4c: Full data | 1-bot | Methodology already human-approved |
| 5: Documentation | 5-bot (4 + rendering + bibtex) | Final product |

**4-bot:** Physics + critical + constructive (parallel), then arbiter.
The plot validator joins 4-bot and 1-bot reviews at phases that produce
figures (Phases 2–5); it is skipped at Phase 1 (strategy has no figures).
Physics reviewer receives ONLY physics prompt + artifact.
Plot validator performs programmatic code/data checks (red flags are
auto-Category A). See `agents/` for full definitions.

**4-bot+bib (Phases 4a, 4b):** Same as 4-bot but adds BibTeX validator — the
draft AN has citations that must be verified against DOI/arXiv/INSPIRE.

**5-bot (Phase 5):** Adds rendering reviewer (compiles and inspects the
PDF) and BibTeX validator. Full panel: physics + critical + constructive +
plot validator + rendering + bibtex → arbiter.

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
4. **Are uncertainties honest in BOTH directions?** Check for inflation
   as well as underestimation:
   - Is any systematic evaluated on MC when a data-based evaluation
     exists and gives a smaller value? (Inflation.)
   - Does the total uncertainty make every validation check pass
     trivially? If all pulls are < 0.5σ, is this because the
     measurement is genuinely compatible, or because the uncertainties
     are large enough to accommodate anything?
   - Could the quoted precision be improved by re-evaluating a dominant
     systematic more carefully (e.g., on the actual data rather than
     borrowing from MC)?
   - Does the measurement have resolving power — can it distinguish
     the SM from a ±20% deviation at 2σ? If not, is this stated?

"No" or "non-empty" without justification → Category A.

5. **Were limitations accepted without evidence of attempted
   improvement?** For each documented limitation or downscoped
   commitment, check: did the executor try to solve the problem before
   accepting it? "Single generator" without evidence of attempting
   PYTHIA 8 installation is Category B. "Uncalibrated variable" without
   evidence of attempting data-driven calibration is Category B.
   "Dominant systematic" without evidence of investigating decomposition
   or alternative evaluation is Category B. The analysis should
   demonstrate ambition — the best achievable result, not the minimum
   passing result.
6. **Does every result have context?** A number without comparison to
   published values, theory predictions, or cross-checks is incomplete.
   Check that every extracted parameter is compared to at least one
   independent reference with a quantitative pull or chi2. Check that
   the AN states the measurement's resolving power: "this precision can
   distinguish X from Y at N-sigma." A measurement that is "consistent
   with everything" is not informative.

### 6.3.1 Evidence-Based Review (mandatory)

Every verification claim in a review must cite specific evidence.
The following patterns are NOT acceptable in any review output:

- "Verified" / "Confirmed" / "Checks out" — without a number or reference
- "Looks reasonable" / "Appears correct" — without stating what was checked
- "Consistent with expectations" — without stating the expectation and
  the comparison metric

Acceptable patterns:
- "Closure chi2/ndf = 1.3/36 (p = 0.24) from results/closure.json — PASS"
- "Tracking systematic: 0.95% (artifact Table 7) matches 0.95%
  (results/systematics.json) — consistent"
- "Figure 12 ratio panel: all bins within [0.85, 1.15] — acceptable
  data/MC agreement"

This requirement applies to ALL reviewer roles (physics, critical,
constructive, rendering, plot validator). A review that says "everything
looks fine" without evidence is a failed review — it provides no
information to the arbiter and no audit trail for future reference.

Reviewers who find themselves unable to cite evidence for a "verified"
claim should recognize this as a signal that they have not actually
verified the claim, and should go back and check.

### 6.3.2 Reviewer Investigation Subagents

Reviewers may spawn focused investigation subagents when a concern
requires deeper analysis than reading the artifact allows. Use cases:

- Tracing a computed value through multiple scripts to verify correctness
- Checking whether a systematic variation is correctly propagated through
  the analysis chain (reading code, not just the artifact's claim)
- Verifying that intermediate outputs are consistent (e.g., same efficiency
  used across scripts)
- Cross-referencing a published paper's methodology against the
  implementation

**When to spawn:** The concern requires reading >3 files, tracing a
computation through code, or cross-referencing intermediate outputs. Most
review work should NOT need subagents — this is for substantive
investigations where the artifact alone is insufficient.

**Contract:**
- Provide the subagent with: specific question, relevant file paths, what
  evidence to look for
- The subagent reads and reports — it does NOT fix or modify anything
- Integrate the subagent's findings as evidence in the review (cite file
  paths and line numbers)

**Scope control:** Subagent spawning is for substantive concerns, not
routine checks. The reviewer should document in their review why the
investigation was needed and what it found.

### 6.4 Review Focus by Phase

Summary table (see subsections below for detailed checklists):

| Phase | Primary Focus |
|-------|---------------|
| Strategy | Backgrounds, systematic plan, selection exploration, reference analyses |
| Exploration | Samples, data quality, data archaeology findings |
| Processing | Closure, approach comparison, cut motivation, MVA input modelling |
| 4a: Expected | Systematic completeness + implementation audit, closure alarm bands, formula audit, Phase 1 traceability, published overlay |
| 4b: 10% | Draft AN quality, consistency with expected, diagnostics, number consistency |
| 4c: Full data | GoF, viability, competitiveness, fit pathologies, number consistency |
| 5: Documentation | See §6.4.3 |

#### Phase 1 (Strategy) review focus

Backgrounds complete? Systematic plan covers conventions? 2-3 reference
analyses tabulated? Selection exploration plan identifies >=2 approaches to
try in Phase 3 (or documents why alternatives are infeasible)?

#### Phase 2 (Exploration) review focus

Samples complete? Data quality OK? Distributions physical? **Data
archaeology** (archived data): were all weight/flag branches checked for
non-triviality? Was pre-selection efficiency characterized? Are any
strategy revision inputs flagged?

#### Phase 3 (Processing) review focus

Background model closes? Every cut motivated by plot? Cutflow monotonic?

**Approach comparison:** Did the executor try >=2 selection approaches and
report a quantitative comparison? If not, is the Phase 1 infeasibility
exemption satisfied? Implementing a single approach without comparison is
Category A unless the exemption applies.

**MVA:** data/MC on classifier OK? Alternative architecture tried?

**MVA input modelling check:** Did the executor check data/MC agreement on
all classifier inputs before training? Any input with data/MC chi^2/ndf > 5
that enters the classifier without documented justification or calibration
is Category A. A classifier that passes MC closure but fails on data due to
a mismodelled input is a preventable error, not a discovery.

**Closure alarm bands:** chi2/ndf < 0.1 is Category A (suspicious);
chi2/ndf > 3 or any pull > 5-sigma is Category A (failure).

#### Phase 4a (Expected Results) review focus

**Systematic completeness:** Every source from conventions + references
implemented or formally downscoped? Signal injection/closure passes?
Operating point stable (Category A if not)? MC coverage matches data periods?

**Phase 1 traceability:** Every Phase 1 commitment implemented or formally
downscoped. Cross-check COMMITMENTS.md if it exists.

**Closure test alarm bands:** chi2/ndf < 0.1 is Category A (suspicious);
chi2/ndf > 3 or any pull > 5-sigma is Category A (failure); `passes: false`
in JSON while text claims acceptable is Category A (misrepresentation).

**Systematic implementation audit:** For each systematic, verify the
variation input actually changes, the impact is non-zero and has the
expected sign, and the evaluation level is consistent (gen vs reco). A
systematic with exactly zero impact in every bin without documented
verification is Category A.

**Formula audit:** For every formula that transforms measured quantities
into physics results, verify dimensional consistency, limiting cases (100%
purity → no correction), and cross-check against the published reference
method. The first hypothesis for a closure failure is a formula bug, not a
physics effect.

**Generator comparison:** If the analysis committed to independent generator
comparison and downscoped it, verify the downscope justification includes
evidence of attempted installation/generation — "not attempted" is not a
justification.

**Published overlay:** If reference analyses published numerical results,
verify they are overlaid on the measurement with chi2 — a measurement
without comparison is incomplete.

**Statistical methodology audit (Category A if violated):**
- All chi2 values computed with full covariance matrix (not diagonal)?
  Diagonal chi2 with all p-values = 1.000 is a red flag for missing
  off-diagonal correlations.
- Closure test uses independent MC sample (not the correction-derivation
  sample)? Pull = 0.000 at all operating points indicates self-consistency,
  not independent closure.
- Every systematic variation justified by a measurement or published value
  (not arbitrary "±50%")?
- Per-systematic impact figures present (not just summary table)?
- Extraction uses differential fit when differential distribution +
  covariance are available?

**Validation target check (§6.8).**

#### Phase 4b (10% Validation) review focus

Draft AN publication-quality? Results consistent with expected? Diagnostics
clean? **Number consistency:** do AN text/table values match the latest
machine-readable outputs? Any discrepancy > 1% relative is Category A
(stale numbers). Validation target check (§6.8).

#### Phase 4c (Full Data) review focus

Post-fit diagnostics healthy? Anomalies characterized?

**GoF of primary configuration:** chi2/ndf < 3 (p > 0.01) — selecting the
smallest-error configuration while ignoring poor GoF is Category A.

**Systematics re-evaluated on full data** (not just transferred from MC)?
If a systematic evaluated on data differs by >2x from MC, is the
discrepancy discussed?

**Viability check on ALL reported measurements** (primary and secondary) —
any failing the 50%/30% criteria must be explicitly noted.

**Competitiveness check** for multi-observable analyses: any measurement
with total uncertainty > 5× published precision flagged as non-competitive —
is improvement feasible?

**Fit pathologies:** any near-degeneracies, boundary hits, or flat likelihood
directions investigated (not silently worked around)?

**Validation target check:** every result compared to PDG/reference values —
any pull > 3-sigma is Category A unless quantitatively explained (§6.8).

**Number consistency:** do numerical values in the AN text/tables match the
machine-readable JSON outputs? Any discrepancy > 1% relative is Category A
(stale numbers).

**Operating-point consistency:** If the primary configuration changed since
Phase 4a (different kappa, different working point, different binning),
verify: (a) the change is stated in the results section (not just the
Change Log), (b) systematics are re-evaluated at the new operating point
or quantitative transfer justification is provided, (c) the "primary"
label is consistent throughout the AN. Pulls between results at different
operating points must be flagged as approximate.

**Known-underestimate check:** For each systematic, compare the assigned
value to any independent cross-check value (e.g., generator comparison).
If the cross-check variation is > 2× the assigned systematic, is the
discrepancy discussed and the total uncertainty appropriately adjusted?
See §3 known-underestimate protocol.

**Conditional escalation to 4-bot.** Phase 4c normally gets 1-bot review
(methodology already human-approved at 4b). However, if ANY of the
following occur, the orchestrator MUST escalate to a full 4-bot review:
- Any result deviates from Phase 4a expected by > 2-sigma
- Any new regression trigger fires (§6.7)
- Any systematic evaluated on full data differs from MC by > 3×
- GoF is pathological (chi2/ndf > 5 or chi2/ndf < 0.05)

The most important result in the analysis deserves adequate review. The
1-bot is sufficient when full data is consistent with expectations; it is
insufficient when surprises appear.

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

Figure review has two components that catch different failure modes:

**Code linter (batch, automated).** A script or pixi task that greps all
plotting scripts for mechanical violations of `appendix-plotting.md`.
Catches: absolute `fontsize=N` values, wrong colorbar patterns, missing
`hspace=0`, `figsize` violations, `ax.set_title()`, `data=False` +
`llabel`/`text` stacking. This runs before the review agent and
produces a machine-readable report. Any violation is auto-Category A.
The linter does NOT read rendered figures — it reads code.

**Visual validator (agent, reads rendered PNGs).** The plot validator
agent must **read every rendered figure image** (PNG) and assess visual
quality as a human referee would. This is NOT a code review — the agent
looks at the picture. The visual checklist:

- [ ] All text (labels, legends, tick marks, annotations) legible at
  the rendered size in the AN? Text that is technically present but
  unreadable at 0.45\linewidth is Category A.
- [ ] Legend overlaps with data points, fit curves, or other content?
  Category A.
- [ ] Any text elements collide with each other (e.g., experiment label
  stacking "ALEPHSimulation Expected")? Category A.
- [ ] Axis labels and legend entries use publication-quality names, not
  code variable names ("efficiency_energy_dep" → Category A)?
- [ ] Subplot layout suits the content? (Horizontal bar charts need
  width; narrow panels with long labels are unreadable.)
- [ ] Axis ranges appropriate? (No excessive whitespace, no clipped
  content, data fills the plot area.)
- [ ] Ratio panel gap? (Any visible gap between main and ratio panels
  is Category A.)
- [ ] **Physics content check (Category A if failed).** The visual
  validator and ALL prose reviewers must look at every figure and
  check whether the physics makes sense — not just whether the
  formatting is correct. Concrete red flags:
  - Data/MC normalization mismatch: MC visibly above or below data
    by more than ~20% across the bulk of the distribution. This
    likely indicates a normalization bug, wrong cross-section, or
    missing background — investigate before attributing to systematics.
  - Postfit data/MC worse than prefit: if the fit is supposed to
    improve agreement but the postfit plot shows larger residuals,
    the fit is broken.
  - Empty bins where events are expected, or vice versa.
  - Ratio panel systematically above or below 1.0 across all bins
    (global offset, not a shape effect).
  - Efficiency or purity outside [0, 1] in any bin.
  - Unphysical distribution shapes: negative yields, rising spectrum
    where it should fall, sharp features with no physics explanation.
  - Two distributions that should differ (e.g., signal vs background)
    appearing identical.
  - **Insane uncertainties.** Error bars visibly larger than the
    signal itself, or uncertainties that span the entire y-axis range.
    Common cause: plotting derived quantities (normalized spectra,
    EEC values, correction factors, ratios) without explicit `yerr`,
    so mplhep auto-computes sqrt(bin content) — which is meaningless
    for non-count values (e.g., sqrt(0.03) = 0.17 on an EEC value
    known to 4%). Any figure where error bars are obviously
    unphysical — relative uncertainties of 100%+ on quantities that
    should be well-measured — is Category A. The reviewer must check
    whether the error bar magnitude is consistent with the stated
    statistical precision of the measurement.
  Any of these visible in a figure that the AN presents without
  comment is Category A. The reviewer must state what the figure
  shows and whether it is consistent with the accompanying text.

A blanket "figures look fine" is not acceptable — list each figure
number with its status. The visual validator runs during each phase's
review, not just at Phase 5.

#### 6.4.3 Documentation Review (Phase 5)

Reviewer reads the AN as a standalone document — as a journal referee would.
Check: every systematic described with method + impact? Every comparison
quantitative? Reproducible from the note alone? Conventions covered?

**Physics narrative quality (Category B if weak).** The reviewer must assess
not just completeness but whether the AN tells a convincing physics story —
the "nodding physicist" test:

- **Motivation:** Does the introduction clearly state why this measurement
  matters beyond "it hasn't been done with this data"? Is there a physics
  question being addressed?
- **Logical flow:** Does each section follow from the previous? Selection
  motivated by physics, corrections motivated by selection, systematics
  motivated by corrections?
- **Evidence of thoroughness:** Are cross-checks well-chosen and interpreted
  (not random)? Do limitations show evidence of attempted improvement?
- **Interpretation:** After results, does the AN explain what the numbers
  mean physically? Not just "M_Z = 91.188 ± 0.004" but "consistent with
  the world average, with precision limited by the 4-point energy scan"?
- **Context:** Is the result placed in the broader landscape of existing
  measurements? Does the reader understand what this measurement adds?
- **Equations:** Does the AN contain equations defining the observable, the
  correction procedure, the systematic evaluation, and the fit/extraction?
  Zero equations is Category A — it means the reader cannot verify the
  mathematics independently.
- **Resolving power:** After the final result, does the AN state what
  deviations the measurement can detect at 2-sigma? A measurement without
  a resolving power statement is incomplete.

**Rendering mechanical checks (Category A if failed).** The rendering
reviewer must verify each of these on the compiled PDF — not the markdown:

- Zero unresolved cross-references ("??" in the PDF text). Run
  `grep '??' ANALYSIS_NOTE.log` and visually scan the PDF for "??" or
  "Figure ??". The most common cause is lost `\label{}` entries when
  the typesetter merged figures into composites.
- **TOC page numbers match actual PDF pages.** Spot-check 3 entries
  (one early section, one late section, one appendix). If any is off
  by more than 1 page, the compilation did not run enough passes.
- **No raw LaTeX or markdown visible** in rendered text (e.g., literal
  `$\sqrt{s}$` with dollar signs, `\textbf{...}`, `@fig:name`).
- **Title renders mathematical symbols correctly.** Check page 1 for
  literal `sqrt(s)` or `$\sqrt{s}$` with visible dollar signs.
- **No `$\pm$` with visible dollar signs** in body text or captions.
  The postprocessor fixes these automatically, but verify in the PDF.
- **All composite figure panels have legible axis labels** at the
  rendered size. If zooming is required to read any text, the panel
  is too small — Category A.

**Consistency sweep (Category A if failed).** The physics reviewer must:

- Verify the "primary" configuration label is consistent throughout
  the AN. If Section 10 calls κ = 0.5 "primary" and Section 13 calls
  κ = 0.3 "primary", this is Category A — the reader cannot determine
  what the actual primary result is. Search the PDF for "primary" and
  verify every occurrence refers to the same configuration.
- Check that abstract numbers match conclusion numbers match results
  table numbers to at least 2 significant figures. If the abstract
  says "±0.018 (syst)" and a table says "±0.0180", that is acceptable.
  If the abstract says "±0.01" and a table says "±0.011", flag it.
- Verify event counts are consistent across cutflow table, body text,
  and summary tables. For the same dataset, event counts must match
  exactly (not approximately). If 2,889,000 appears in one place and
  2,889,543 in another, the discrepancy must be explained.
- Verify the chi-squared / covariance treatment is stated and
  consistent. If chi-squared values use diagonal-only covariance,
  this must be stated. If full covariance is available but not used,
  flag as Category B — all chi-squared values should use the full
  covariance matrix when it exists.

**Figure-scrolling test (Category B if fails).** The rendering reviewer
or physics reviewer must verify: can the complete physics story be
understood by scrolling through the figures alone? Every major analysis
step (data quality, selection, corrections, validation, results,
comparison) should have at least one figure. Non-trivial methods without
a visual explanation (diagram, flowchart, schematic) are gaps. A "yes"
requires that the figure sequence tells a coherent narrative without
reading the text. A "no" requires identifying which steps lack visual
representation.

**Tautological comparisons.** If the "comparison to theory/MC" is
mathematically identical to the "comparison to expected" (e.g., the
expected result was derived from the same MC that serves as the theory
comparison), the AN must not present them as independent evidence of
consistency. Either (a) remove the redundant comparison, or (b) explicitly
state the tautology and explain what independent information, if any, the
comparison provides. Presenting tautological agreement as validation is
Category A.

**Tautology detection — concrete alarm criteria.** Reviewers must verify
algebraic independence for every validation comparison. Specific alarms:
- **chi2/ndf < 0.1 between corrected data and MC truth:** Almost
  certainly tautological. If the correction was derived from that MC,
  corrected_data = reco_data × (gen_truth / reco_MC), so
  corrected_data / gen_truth ≈ reco_data / reco_MC — this is a
  data/MC closure check, not an independent validation. Label it as
  such; do not present chi2 = 0.19 as evidence of physics agreement.
- **chi2 identically zero (not just small):** Diagnostic of algebraic
  circularity. All three fitted parameters may be determined by input
  assumptions, not data. Investigate immediately (see §3 Phase 4c
  fit triviality gate).
- **Per-subset fits returning identical central values:** If splitting
  the data by year, run period, or subsample produces central values
  that agree to 5+ decimal places, the fit is not using the data —
  the result is determined by construction.
- **True validation requires comparison to:** (a) an independent
  dataset, (b) published results from a different analysis, (c) a
  different method applied to the same data, or (d) theory predictions
  not used in the analysis chain. Comparison to the MC used for
  corrections is a closure check, not a validation. Both are useful
  but they are different things, and the AN must not conflate them.

### 6.5 Iteration and Escalation

**4/5-bot:** Repeat until arbiter PASS. Warn at 3, strong warn at 5, hard
cap at 10. The arbiter should ESCALATE rather than loop indefinitely.

**1-bot:** Warn at 2, escalate to human after 3.

**Re-review documentation (mandatory).** When a review verdict is ITERATE,
the fix agent produces fixes and the phase is re-reviewed. The re-review
MUST produce a written re-review artifact (`{PHASE}_REREVIEW.md` or
`{PHASE}_REVIEW_v2.md`) that explicitly verifies each Category A/B finding
from the original review. "ITERATE → fix → advance without re-review" is
a process failure — the orchestrator must not advance the phase without
a documented re-review PASS. If the re-review identifies new issues, the
cycle continues (fix → re-review) until PASS. Every cycle produces a
numbered review artifact on disk for the audit trail.

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
receives a publication-quality compiled PDF (not markdown) with 10%
validation results and the unblinding checklist.

**Response options:**

| Response | Meaning | Orchestrator action |
|----------|---------|---------------------|
| **APPROVE** | Analysis is sound; proceed to full data | Continue to Phase 4c |
| **ITERATE** | Issues within 4b scope | Fix, re-review 4b, re-present to human |
| **REGRESS(N)** | Fundamental issue traced to Phase N | Non-destructive regression (see below) |
| **PAUSE** | External input needed (data, MC, theory) | Wait for human to provide input |

**APPROVE** means the human is satisfied that the methodology is correct
and the 10% validation is clean. It does NOT mean the final result is
approved — that comes after Phase 5 review.

**Human review checklist.** The human should concretely verify:

- [ ] **Event selection yields**: do cutflow numbers match expectations
      from the published reference analysis (within ~10%)? Large
      discrepancies indicate a selection bug, not a physics effect.
- [ ] **Data/MC agreement**: are the key data/MC comparisons (selection
      variables, observable inputs) acceptable? Is there any
      distribution where MC is visibly 2× the data?
- [ ] **Validation tests**: do closure/stress tests pass? If any fail,
      is the failure understood and is the remediation adequate?
- [ ] **Systematic completeness**: does the systematic table cover the
      sources from the reference analyses? Any surprising omissions?
- [ ] **Comparison to published result**: does the 10% result (or
      expected result) agree with the reference within uncertainties?
      If not, is the discrepancy understood?
- [ ] **Figure quality**: are all figures interpretable? Do captions
      accurately describe what is shown? Would you approve these
      figures for a conference talk?
- [ ] **Uncertainty honesty**: do the total uncertainties seem
      reasonable? Are they comparable to (not vastly larger or smaller
      than) published results? If much larger, is the source identified?
- [ ] **"Where I wasn't sure" items**: did the agent flag any physics
      decisions as uncertain? Review these explicitly — any analysis
      step where the agent expressed doubt or tried multiple approaches
      should be highlighted for human judgment.

The last item is critical: agents should flag uncertainty rather than
hide it. A flag that says "I chose κ = 0.5 based on GoF, but κ = 0.3
gives 40% better statistical precision with worse GoF — this is a
physics judgment I'm not confident about" is more valuable than a
silent choice. The human gate exists precisely for these moments.

**ITERATE** is for issues the executor can fix without changing the
analysis approach: missing systematics, inadequate validation, prose
quality, figure problems. The fix-review-present cycle repeats until
the human approves.

**REGRESS(N)** is for fundamental issues that trace to an earlier phase.
The human specifies: which phase, what the issue is, and what needs to
change. Examples:
- REGRESS(1): Strategy missed a dominant background → Phase 1 must
  revise the background model → cascade forward
- REGRESS(3): Selection is suboptimal, published analyses use a better
  discriminant → Phase 3 must implement and compare → cascade forward
- REGRESS(4a): Systematic treatment is incomplete or wrong → Phase 4a
  must revise → re-run 4b

**Regression at the human gate follows the non-destructive protocol:**

1. Orchestrator spawns Investigator to assess cascade scope
2. Investigator produces `REGRESSION_TICKET.md` identifying:
   - What must change in Phase N
   - Which downstream artifacts are invalidated vs reusable
   - Estimated rework scope
3. Executor creates new artifact versions (e.g., `STRATEGY_v2.md`),
   does NOT overwrite originals
4. Each downstream phase re-evaluates:
   - If Phase N change doesn't affect Phase M → Phase M artifacts
     reused as-is
   - If Phase N change invalidates Phase M → Phase M re-executes,
     reusing code and infrastructure where still valid
5. Note writer produces new AN version with updated narrative (see
   post-regression cohesion below)
6. Affected phases re-reviewed with same panel
7. Re-present to human

**Post-regression AN cohesion.** After any regression, the AN must tell
a cohesive physics story reflecting the CURRENT analysis. The body text
should read as if the current approach was the plan from the start — the
reader should not need to know the analysis was restructured. The Change
Log provides the full audit trail (what changed, when, and why). This
means: if Phase 1 strategy changed, the Introduction motivates the
current strategy; if Phase 3 selection changed, the Event Selection
describes the current approach. The AN is a physics argument, not a
process diary.

**PAUSE** is for situations where the analysis needs something the
system cannot provide: additional MC samples, a theoretical calculation,
expert consultation, or access to data not yet available. The human
specifies what is needed and provides it when ready.

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
- Result > 3-sigma from a well-measured reference value (see §6.8)
- Result with relative deviation > 30% from a well-measured reference
  value, regardless of pull (see §6.8 — triggers calibration-first
  investigation)
- GoF toy distribution inconsistent with observed chi2 (the observed
  chi2 falls outside the 95% interval of the toy distribution)
- Wholesale bin exclusion: flat-prior gate or similar criterion
  excluding > 50% of measurement bins (indicates binning or method
  problem, not a systematic effect — see §3 Phase 3)
- Two distributions that should be independent appear visually
  identical (indicates a bug or tautological comparison)
- Systematic double-counting: two or more systematic sources produce
  numerically identical per-bin shifts (indicates they are the same
  underlying effect with different names — merge and document)
- Correlated combination error: when combining results from multiple
  observables or methods, shared systematic sources (e.g., scale
  variation, generator choice) must be treated as correlated. Treating
  correlated uncertainties as uncorrelated artificially reduces the
  combined uncertainty.

**Procedure:**
1. Document issue, identify origin phase
2. Classify as regression trigger in review artifact
3. Orchestrator spawns **Investigator**: reads trigger → reads origin
   artifact → traces forward to identify affected phases →
   produces `REGRESSION_TICKET.md`
4. Fix origin phase → re-review → re-run affected downstream phases

**Upstream improvement cascade (applies to all fixes, not just regression).**
When any component is improved — a better truth labeling method, a refined
calibration, an updated selection — the executor must trace all downstream
consumers of that component and re-evaluate them. This is not optional.
Concretely:
- Identify every script, figure, table, and AN section that used the old
  component's output
- Re-run each with the improved input, or document why the improvement
  does not affect the downstream result (e.g., the BDT was rejected for
  data/MC disagreement on inputs, which is independent of training labels)
- Update the AN with the improved numbers/figures
- If a downstream result changes materially (>1σ shift or qualitative
  change in ranking/selection), the change propagates further downstream

The cost of re-running a script is low; the cost of leaving stale results
that contradict the improved methodology is high. A variable survey
computed with approximate labels while the analysis uses high-purity
neutrino labels is internally inconsistent — a referee will notice. When
in doubt, re-run.

**Timing:** Regression may be triggered at any phase gate or by the
human gate. After human approval and entry into Phase 4c, new issues
discovered during 4c or Phase 5 review are addressed as Phase 5
iteration unless the arbiter classifies them as regression triggers
(§6.7 list), in which case they still trigger regression.

**Not regression:** Presentation issues (labels, captions, formatting) →
Phase 5 iteration, not regression.

**Upstream feedback (non-blocking):** Any executor may produce
`UPSTREAM_FEEDBACK.md` for issues an earlier phase missed. Routed to the
next review gate.

### 6.8 Validation Target Rule

When the Phase 1 strategy defines validation targets (PDG values, published
reference measurements), these create binding review obligations:

**The rule has two tiers:**

**Tier 1 — Mandatory investigation (Category A).** Any extracted
parameter that meets **either** of the following triggers a mandatory
investigation that blocks advancement until resolved:

- **Pull threshold:** pull > 3-sigma from a well-measured reference value, OR
- **Gross deviation threshold:** relative deviation > 30% from a
  well-measured reference value (i.e., |result − reference| / reference
  > 0.3), regardless of the pull.

There is no single number that cleanly separates "method problem" from
"new physics" — a 40% deviation could be either. The 30% threshold is
guidance, not gospel. The point is to trigger investigation, not to
render a verdict. A deviation of 25% with a clean calibration story
may need no further work; a 15% deviation with no explanation may need
deep investigation. Reviewers should use physics judgment, with 30% as
the default trigger for mandatory formal investigation.

**Tier 1b — Method-improvement investigation (Category B, upgradable to A).**
When the result deviates from a well-measured reference by 1–3-sigma (or 10–30%
relative) and the deviation has a **known directional bias from the choice
of method** (e.g., NLO vs NNLO, mean value vs differential fit, leading-order
vs resummed), the reviewer must check:

1. **Is a better method feasible with the available data and tools?** If
   the analysis has corrected differential distributions but only used the
   mean value, the differential fit is feasible. If NLO+NLL predictions
   exist in the literature and the analysis used NLO only, implementing
   NLL is feasible if the coefficients are published.

2. **Did the reference analyses use a better method?** Compare the
   extraction method (not just systematics) to the Phase 1 reference
   table. If every published analysis used method X and this analysis
   used a simpler method Y without attempting X, this is a **method
   parity failure** (see §3 Phase 1) — Category A if it was committed
   to in the strategy, Category B if it was not discussed.

3. **Would the better method plausibly resolve the deviation?** Estimate
   the expected shift from published comparisons (e.g., "NLO→NNLO shifts
   alpha_s by -0.007 in published analyses").

If all three answers are yes, the reviewer must require the executor to
implement the better method as the primary result (or at minimum as a
documented cross-check) before advancing. "The deviation is a known
limitation of our method" is not sufficient when the better method is
feasible — the analysis should use the best feasible method, not explain
why the suboptimal method gives a biased answer.

This tier exists because a 1.7-sigma deviation with a known directional
cause is qualitatively different from a 1.7-sigma statistical fluctuation.
The former can be reduced by improving the method; the latter cannot.
Accepting a known-biased result without attempting the unbiased method
wastes the data.

**Tier 2 — Calibration-first investigation.** When the method passes
MC closure (correct result on MC) but produces a deviant result on
data, this is the classic signature of a calibration mismatch — not
new physics, not a bug, but MC-derived corrections that don't match
the data. The investigation protocol is:

1. **Diagnose what needs calibrating.** Back-substitute: given the
   observed data rates and the known reference value, solve for the
   implied MC-derived parameters (efficiencies, corrections, scale
   factors). Compare implied vs. nominal MC values. The shifts tell
   you which parameters are miscalibrated and by how much.

   Back-substitution is a **diagnostic tool**, not a calibration. It
   answers "what would need to change?" — it does not provide the
   correction itself. Using back-substituted values (derived by
   assuming the answer) as the calibration is circular and is
   forbidden as the primary correction. See step 3.

2. **Check physical plausibility.** Are the implied shifts consistent
   with known data/MC differences (resolution, tracking efficiency,
   alignment)? A 5% efficiency shift consistent with a 5% resolution
   difference is plausible. A 50% shift with no known mechanism is a
   red flag.

3. **Calibrate from independent observables.** For each miscalibrated
   parameter identified in step 1, find an independent data-driven
   measurement that constrains it — one that does NOT depend on
   (or has minimal dependence on) the primary result.

   **Independence classification (must be stated for each parameter):**

   - **Independent** (gold standard): calibration from a control
     sample, auxiliary measurement, or sideband that has no dependence
     on the primary observable. Examples: d0 resolution from the
     negative-side d0 distribution; tracking efficiency from
     tag-and-probe on a known resonance; energy scale from the Z mass
     peak. The calibration observable is measured in data AND MC, and
     the data/MC ratio is the scale factor.

   - **Weakly dependent** (acceptable with documentation): calibration
     from an anti-signal region or a variable correlated with but not
     identical to the primary result. Example: non-b hemisphere
     correlation from anti-b-tagged events, or background efficiency
     from a sideband. The circular dependence is second-order and
     must be quantified (e.g., by varying the primary result within
     its uncertainty and checking the calibration stability).

   - **Circular** (forbidden as primary calibration): any method that
     assumes the value of the primary result to derive the correction.
     Back-substitution falls in this category. These values may be
     used for diagnostics, cross-checks, and informing systematic
     ranges, but NOT as the central correction.

   Apply the independent calibration (scale factors, reweighting, or
   corrected parameter values) and re-run the extraction. The
   calibrated result is the measurement; the uncalibrated-vs-calibrated
   difference quantifies the calibration systematic.

4. **Handle parameters that cannot be independently calibrated.** When
   no independent observable constrains a parameter (e.g., a correction
   factor that cannot be measured in a control sample):

   - Use the MC value as the central value (not the back-substituted
     value)
   - Inflate the systematic uncertainty to cover the range between the
     MC value and the back-substituted (data-implied) value
   - Document explicitly: "parameter X cannot be independently
     calibrated; the MC value is used with a systematic covering the
     data-implied range"
   - The back-substitution informs the systematic range — this is its
     legitimate role

   This is honest: the result uses the best available (MC) estimate
   with an uncertainty that reflects what the data are telling you.
   It will be less precise than a circular calibration but it is not
   wrong.

5. **Verify magnitude closure.** The combination of independent
   calibrations (step 3) and inflated systematics (step 4) must
   account for the full observed deviation. "Correcting the efficiency
   explains 40% of the bias" is acceptable IF the remaining 60% is
   covered by the inflated systematic on the uncalibrated parameters.
   The total uncertainty on the calibrated result must be large enough
   that the uncalibrated result falls within ~2-sigma — otherwise some
   bias source is missing.

6. **Document the calibration chain.** The analysis note must contain:
   the uncalibrated result, the identified miscalibrations, the
   calibration procedure (stating the independence level for each
   parameter), the calibrated result, the residual calibration
   systematic, and what the result would be with no calibration.
   A reader should understand exactly what was corrected, from what
   source, and what the analysis cannot independently constrain.

If the investigation reveals the deviation **cannot** be explained by
calibration (the implied parameter shifts are unphysical, or the
calibrated result still deviates significantly), then:
- Check for bugs, sign errors, unit mistakes, wrong input values
- If no mundane explanation, document as a genuine tension and
  consider downscoping the affected parameter
- Do not claim new physics without exhausting mundane explanations

**Rationale:** Accepting large discrepancies with well-known physics values
erodes the credibility of the entire analysis. A 3-sigma pull may be a
statistical fluctuation, but the burden of proof is on the analysis to
demonstrate this — not on the reviewer to accept it. An analysis that
reports N_nu = 2.88 ± 0.03 without rigorous investigation of the 3.9-sigma
tension has a gap that a referee would immediately flag. Conversely,
a measurement where MC closure works perfectly but data deviates is
almost always a calibration issue — the standard HEP response is to
calibrate, not to panic or to shrug.

**This rule applies to all review tiers** (1-bot, 4-bot, 5-bot) at Phases
4a, 4b, 4c, and 5. It does not apply to Phase 1 (where targets are
defined, not yet tested) or Phases 2–3 (where results are not yet
extracted).

---
