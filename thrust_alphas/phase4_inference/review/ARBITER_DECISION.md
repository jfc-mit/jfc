# Arbiter Decision: Phase 4a Inference Review

**Arbiter:** Phase 4a Arbiter (3-bot protocol)
**Date:** 2026-03-15
**Artifact:** `phase4_inference/exec/INFERENCE_EXPECTED.md`
**Reviews adjudicated:** Critical Review, Constructive Review

---

## Reviewer Agreement Summary

| Finding | Critical Reviewer | Constructive Reviewer | Agreement |
|---------|-------------------|----------------------|-----------|
| A1: Missing stress test | Category A | Category B | Both identify; disagree on severity |
| A2: Alpha_s degeneracy labeling | Category A | Not raised (implicitly accepted) | Partial |
| A3: Hadronization ~0% | Category A | Category B (B7) | Both identify; disagree on severity |
| A4: Diagonal-only chi2 | Category A | Category B (B4) | Both identify; disagree on severity |

---

## Adjudication of Category A Findings

### A1: Missing stress test — UPHELD as Category A

Both reviewers correctly identify that the stress test is absent. The conventions (`unfolding.md`, Section "Regularization and iteration") list three criteria for choosing regularization: closure test, stress test, and stable plateau. Two of three are present; one is missing entirely.

The critical reviewer is right that this is distinct from the prior sensitivity test. The stress test validates that the unfolding can recover a *different* truth shape when passed through the nominal response matrix. This is directly relevant here: the data is 15-20% below Pythia 6.1, meaning the unfolding must handle a genuine data/MC shape difference. Without a stress test, we have no evidence that the 3-iteration choice is adequate for this level of mismodeling.

This is a straightforward conventions requirement with a clear implementation path. It remains Category A.

**Required action:** Implement a stress test. Reweight the half-B truth distribution (e.g., apply a linear tilt in tau of +/-20%, or scale the 2-jet peak region) and unfold through the half-A response matrix. Report stress-test chi2/ndf vs. iterations. Verify that 3 iterations recovers the reweighted truth within statistical precision.

### A2: Alpha_s extraction labeling — DOWNGRADED to Category B

The critical reviewer raises three sub-issues: (a) the extraction is degenerate and misleadingly presented, (b) the `extract_alphas.py` docstring is stale, (c) the tension comparison is meaningless.

On examination, the artifact *does* flag the degeneracy prominently. Section 6.1 contains a bold-face caveat paragraph explaining the flat chi2 profile and the normalization degeneracy. Section 6.2 is titled "Indicative Result." Section 6.3 repeats the caveat. The artifact is not hiding the problem.

However, the critical reviewer has valid sub-points:
- The stale docstring in `extract_alphas.py` (claiming chi2 ~ 1.3/12 and r = 0.978 when the actual output is chi2 = 47.7/12 and r = 0.896) is a code hygiene issue that should be fixed.
- The "1.1 sigma tension" comparison is indeed not very informative when the extraction method is degenerate. A stronger caveat is warranted.

These are presentation and code quality issues, not physics blockers. The analysis correctly identifies that NLO+NLL theory is needed for Phase 4c. The alpha_s result is explicitly marked as indicative. A referee would want clearer labeling but would not reject the measurement itself over this.

**Required action (B-level):** (a) Fix the stale docstring in `extract_alphas.py`. (b) Add a sentence to Section 6.3 stating that the tension comparison is not meaningful given the degenerate LO method.

### A3: Hadronization systematic ~0% — UPHELD as Category A, but with modified remediation

Both reviewers flag this. The critical reviewer calls it Category A; the constructive reviewer puts it at B with a recommendation to add a quantitative bound from published analyses.

The conventions are explicit: "Compare generators with fundamentally different fragmentation models (e.g. string vs. cluster). This is typically the dominant systematic for event-shape measurements." They also state: "If alternative generators with full detector simulation are unavailable, reweighting at particle level is acceptable but must be documented as a limitation."

The analysis acknowledges the limitation but reports ~0% as the hadronization systematic. This is the core problem: reporting ~0% implies the systematic has been evaluated and found negligible, when in fact the method used (Herwig-like pT-broadening reweighting) is too weak to probe the actual hadronization model dependence. Published LEP analyses consistently find 1-3% per-bin effects from hadronization for thrust at the Z pole.

I uphold this as Category A because a ~0% hadronization systematic for an event-shape measurement is not defensible at journal review. However, I recognize the constraint: no alternative generator with full detector simulation is available for this archived dataset. The remediation must be realistic.

**Required action (choose one or both):**

1. **Strengthen the reweighting.** The current "Herwig-like reweighting" apparently applies only a pT-broadening to the Pythia prior, which is too mild. A more physics-motivated approach: generate a standalone Herwig 7 (or Sherpa) particle-level thrust distribution at sqrt(s) = 91.2 GeV (no detector simulation needed — just the generator). Reweight the Pythia 6.1 particle-level distribution bin-by-bin to match this Herwig shape. Rebuild the response matrix with the reweighted particle-level weights. Unfold data with the reweighted response. The difference vs. nominal is the hadronization systematic. This was the approach outlined in the Phase 1 strategy (Section 6.1.3).

2. **Assign a conservative floor.** If generating Herwig particle-level events is not feasible within the agent's tool constraints, assign a hadronization systematic floor based on published LEP analyses. The ALEPH 2004 analysis and LEP combination both quote ~2% per-bin (correlated) from hadronization model dependence. Add this as a flat 2% fully-correlated systematic to the covariance matrix, documented as "assigned from published LEP analyses due to the absence of an alternative generator."

Option 1 is preferred because it produces a data-driven estimate specific to this analysis. Option 2 is acceptable as a fallback. Either way, the reported hadronization systematic must not be ~0%.

### A4: Diagonal-only chi2 for reference comparisons — DOWNGRADED to Category B

The conventions state "Use the full covariance matrix (not diagonal uncertainties only)." Both reviewers flag this.

However, the practical situation matters. The reference values (ALEPH 2004, archived ALEPH) are approximate — digitized from publications, not from HEPData. The published covariance matrices for these references are not available to the agent. Computing a chi2 with the analysis's own full covariance against approximate central values would give a formally correct but practically misleading result: the dominant uncertainty (21% BBB) would trivially absorb any data-reference tension, making all chi2 values << 1 and providing no discriminating power.

The diagonal chi2 is actually more informative here as a quick compatibility check. The values (2.33, 1.88) are borderline but not alarming, and the investigation correctly identifies the Pythia 6.1 offset as the cause.

That said, the critical reviewer's sub-point about HEPData is valid: if official tabulated values exist, they should be used instead of digitized approximations.

**Required action (B-level):** (a) Check whether ALEPH 2004 thrust data is available on HEPData; if so, use those values. (b) Add a brief bin-by-bin breakdown showing which bins drive the chi2 vs. ALEPH 2004. (c) Add a sentence justifying the diagonal-only approach (published covariance unavailable).

---

## Summary of Disposition

| Finding | Original Category | Arbiter Decision | Blocking? |
|---------|-------------------|------------------|-----------|
| A1: Missing stress test | A (critical), B (constructive) | **A — Upheld** | Yes |
| A2: Alpha_s labeling | A (critical) | **B — Downgraded** | No |
| A3: Hadronization ~0% | A (critical), B (constructive) | **A — Upheld** | Yes |
| A4: Diagonal chi2 | A (critical), B (constructive) | **B — Downgraded** | No |

---

## Additional B-level Items (from both reviewers, not adjudicated as A)

The following B-level items from both reviewers are endorsed and should be addressed before Phase 5, but do not block Phase 4b progression:

- **Response matrix properties** (B2 in both reviews): Add diagonal fraction, column normalization, efficiency vs. tau.
- **Year-to-year consistency** (Critical B4): Either implement or document why dropped.
- **Selection cut completeness** (Critical B5): Confirm all planned variations were run or explain which were precluded.
- **Closure test independence** (Critical B6): Clarify that Phase 4a uses genuinely independent half-samples.
- **Full-range CSV** (Constructive B5): Produce the 25-bin result file.
- **Figures in analysis note** (Constructive B6): Add figure references to the draft note.
- **Correlation structure discussion** (Constructive B3): Discuss the near-rank-1 systematic covariance.

---

## Verdict

**ITERATE**

Two Category A findings must be resolved before Phase 4a can pass the gate:

1. **Stress test (A1).** Implement and report. This is a mechanical task with a clear specification.

2. **Hadronization systematic (A3).** The reported ~0% must be replaced with either (a) a reweighting-based estimate using an alternative generator's particle-level shape, or (b) a conservative floor from published LEP analyses. The current value is not credible and would not survive journal review.

**Scope of iteration:** These two items only. The B-level findings (A2 downgraded, A4 downgraded, and the various B items from both reviewers) should be addressed but do not need to be resolved before re-review. The executor should focus on A1 and A3, then resubmit the artifact for a follow-up review pass.

**Estimated effort:** Both fixes are bounded. The stress test requires running the existing unfolding code with a reweighted input — no new infrastructure. The hadronization systematic requires either generating ~100k Herwig particle-level events (if the tool environment supports it) or assigning a floor value with a paragraph of justification. Neither should require more than one executor session.
