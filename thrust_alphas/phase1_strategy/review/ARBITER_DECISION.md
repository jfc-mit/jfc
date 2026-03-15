# Arbiter Decision: Phase 1 Strategy Review

**Arbiter:** Phase 1 Review Arbiter
**Date:** 2026-03-15
**Artifact:** `phase1_strategy/exec/STRATEGY.md`
**Reviews adjudicated:** Critical Review, Constructive Review

---

## Verdict: ITERATE (minor)

Resolve the items marked "Required" below, then advance. No second review cycle needed -- the resolutions are straightforward additions to the existing document.

---

## Adjudication of Critical Review Category A Findings

### A1. Hadronization systematic structurally weaker than references

**Critical reviewer:** Category A. Strategy must add explicit acknowledgment, quantitative reasoning for why reweighting is conservative, and discussion of fast-sim alternatives.

**Constructive reviewer:** Raised as B-2 (only two generators instead of three). Did not classify as blocking.

**Arbiter ruling: Downgrade to Category B (with a required documentation addition).**

Rationale: The conventions file explicitly states that "reweighting at particle level is acceptable but must be documented as a limitation." The strategy already acknowledges this constraint and identifies particle-level reweighting as a fallback. The critical reviewer is correct that the strategy should be more explicit about the severity of this limitation, but the conventions themselves establish that this approach is *acceptable*, not disqualifying.

**Required action:** Add 2-3 sentences to Section 6.1.3 that:
1. State explicitly that particle-level reweighting is the dominant methodological limitation relative to the original ALEPH publications.
2. Note that the reweighting approach is expected to be conservative for thrust because the dominant detector effect (tracking efficiency and resolution) is largely independent of the fragmentation model -- the detector response to individual tracks does not depend strongly on whether they came from string or cluster fragmentation.
3. State that the feasibility of parametric fast-sim as a cross-check will be evaluated in Phase 2.

This is sufficient. A full fast-sim study is a Phase 4 deliverable if warranted, not a strategy requirement.

### A2. Primary ALEPH event shapes paper not tabulated as a reference analysis

**Critical reviewer:** Category A. Replace DELPHI oriented-shapes (Ref 2) with the primary ALEPH paper (Eur.Phys.J.C35:457-486, 2004).

**Constructive reviewer:** Did not raise this issue. Found the three references "well-chosen."

**Arbiter ruling: Agree -- Category A. Must resolve.**

The critical reviewer is correct. The primary ALEPH event shapes publication is the single most relevant reference for this analysis (same detector, same observable, same dataset era). It is currently cited only in passing for the particle-level definition. The DELPHI oriented event shapes paper measures a fundamentally different quantity (event shapes as functions of thrust-axis polar angle). While informative, it is less relevant than the direct ALEPH measurement.

**Required action:** Either (a) replace Reference Analysis 2 with the primary ALEPH event shapes paper and tabulate its systematic program, or (b) add it as a fourth reference with its own row in the comparison table. Option (a) is preferred for conciseness.

### A3. "Aftercut" pre-selection interaction with systematic program

**Critical reviewer:** Category A. Strategy must identify the risk that pre-applied cuts may constrain planned systematic variations.

**Constructive reviewer:** Did not raise this issue.

**Arbiter ruling: Downgrade to Category B. Add a risk note, but do not block advancement.**

Rationale: The strategy already acknowledges the "aftercut" issue (Section 4.1, final note) and correctly defers the investigation to Phase 2 -- which is exactly where data exploration belongs. The strategy *cannot* resolve this issue because the file contents are not yet known. However, the critical reviewer makes a valid point that the *risk* should be flagged.

**Required action:** Add a single paragraph to Section 4.1 (or as a Phase 2 gate condition in Section 11) stating: "If Phase 2 reveals that any planned cut variation (Section 6.1.1) is precluded by the pre-applied selection, the systematic plan will be updated to document the limitation and substitute alternative probes of the same detector effect."

This is a contingency note, not a blocking issue. Phase 2 is the correct place to discover what cuts are pre-applied.

---

## Adjudication of Category B Findings

Both reviewers independently identified the covariance matrix construction gap (Critical B1 / Constructive B-1). This convergence confirms it should be addressed.

| Finding | Critical | Constructive | Arbiter ruling |
|---------|----------|-------------|----------------|
| Covariance matrix construction | B1 | B-1 | **B -- Required.** Add a brief subsection specifying bootstrap for stat covariance, outer-product for syst covariance, and validation checks. |
| Fit range sensitivity | B2 | B-3 | **B -- Recommended.** Add criteria for fit range selection (stability, hadronization correction thresholds). Can be brief. |
| Multiple event shapes | B3 | Not raised | **B -- Noted.** Add one sentence justifying single-observable focus. Not required to add C-parameter. |
| Stat correlation in alpha_s fit | B4 | Not raised | **B -- Recommended.** Add a note that the alpha_s fit uses the full unfolded covariance. One sentence suffices. |
| Generator sample details | B5 | Not raised | **B -- Recommended.** Specify tunes and target statistics for Pythia 8 and Herwig 7 samples. |
| Calorimeter systematics | B6 | Not raised | **B -- Recommended.** Expand object-level response to address calorimeter objects with equal specificity to tracking. |
| Third generator (Ariadne/Sherpa) | Not raised | B-2 | **B -- Noted.** A third generator-level comparison would strengthen the result but is not required at strategy phase. Can be decided in Phase 4. |
| Power corrections ambiguity | Not raised | B-4 | **B -- Recommended.** Clarify which non-perturbative approach is primary vs. cross-check. |

---

## Category C Findings

All Category C items from both reviewers are accepted as suggestions. None require action before advancing. The most valuable ones to incorporate when convenient:

- **C2/C-1 (normalization/response matrix validation):** Clarify whether efficiency is folded into the response matrix or applied separately. One sentence.
- **C-2 (toy pseudo-experiments):** Add as a planned validation step if the published covariance is available. Good practice.
- **C-4 (expected statistical precision):** Useful context. One line of arithmetic.

---

## Summary of Required Actions Before Advancing

These are the items that must be resolved. All are documentation additions, not structural changes to the analysis plan.

1. **[From A2]** Add the primary ALEPH event shapes paper (Eur.Phys.J.C35:457-486, 2004) as a tabulated reference analysis with its systematic program.
2. **[From A1, downgraded]** Expand Section 6.1.3 to explicitly document the particle-level reweighting limitation, explain why it is expected to be adequate for thrust, and note that fast-sim alternatives will be evaluated in Phase 2.
3. **[From A3, downgraded]** Add a contingency note about the "aftercut" pre-selection potentially constraining systematic variations, with a Phase 2 gate condition.
4. **[From B1/B-1]** Add a subsection on covariance matrix construction (method, validation).

Items 1-4 are concise additions (a few paragraphs total). Once incorporated, the strategy is ready for Phase 2 advancement without a second review cycle.

---

## Assessment of Strategy Quality

The strategy is strong. It demonstrates thorough knowledge of the physics, a comprehensive systematic plan that maps every convention requirement, and a well-structured analysis chain. The issues identified are gaps in documentation and specificity, not flaws in the analysis design. The measurement approach (IBU with bin-by-bin cross-check, particle-level reweighting for hadronization, alpha_s extraction with scale variation) is sound and well-motivated by the reference analyses.

The critical reviewer's concern about the hadronization systematic being "structurally weaker" is valid in absolute terms but must be evaluated against the constraints of the available data: there is one reconstructed MC sample, and the conventions explicitly permit particle-level reweighting as a fallback. Demanding full detector simulation with alternative generators would effectively block the analysis, which is not the intent of the conventions.

**Final verdict: ITERATE (minor).** Resolve the four required actions above. No re-review needed.
