# Critical Review: Phase 4a Inference (Expected Results)

**Reviewer:** Critical Reviewer (3-bot protocol)
**Date:** 2026-03-15
**Artifact:** `phase4_inference/exec/INFERENCE_EXPECTED.md`

---

## Summary Assessment

The Phase 4a artifact is well-structured and demonstrates a competent unfolded thrust measurement with a validated covariance matrix. The independent closure test is a genuine improvement over Phase 3. However, there are several significant issues that must be addressed before this phase can be considered complete.

---

## Category A Findings (Must Resolve)

### A1. No stress test performed

**Conventions requirement (Section "Regularization and iteration"):** The regularization selection criterion requires three checks: (1) closure test, (2) stress test (unfolding a reweighted truth through the response recovers the reweighted truth), and (3) stable plateau. The artifact reports closure and prior sensitivity but **no stress test is mentioned anywhere**. A grep of the entire `phase4_inference/` directory finds zero references to "stress test" or "reweighted truth."

The stress test is distinct from the prior sensitivity test. Prior sensitivity checks whether a flat prior changes the result. A stress test checks whether the unfolding can recover a *different* truth distribution (e.g., reweighted by a linear tilt or by alpha_s variation) when unfolded through the nominal response matrix. This probes regularization bias in the presence of genuine data-MC shape differences -- which is directly relevant here given the 15-20% data/MC normalization offset.

**Action required:** Implement a stress test. Reweight the half-B truth distribution (e.g., linear tilt in tau, or +/-20% variation in the 2-jet peak region), fold through the half-A response matrix, unfold, and verify recovery. Report chi2/ndf vs iterations.

### A2. Alpha_s extraction is fundamentally broken (acknowledged but incompletely handled)

The artifact acknowledges the LO shape chi2 approach is degenerate (Section 6.1: "the shape chi2 profile is flat ... chi2 = 47.69 for all r"). This is confirmed by the code: after normalizing both data and MC to unit fit-range integral, multiplying the MC by a constant r and renormalizing gives back the same shape. The chi2 is independent of r for a flat scale factor -- the `compute_chi2_for_scale` function in `extract_alphas.py` (line 108-114) confirms this: `theory = mc_norm * scale_r` followed by renormalization to unit integral.

The reported "optimal r = 0.896" and "alpha_s = 0.1066" therefore reflect numerical noise or a subtle shape effect from the renormalization boundary, not a genuine alpha_s constraint. The chi2/ndf = 3.97 at "minimum" is a bad fit by any standard.

The artifact correctly flags this as requiring NLO+NLL theory for Phase 4c, but the current presentation is misleading:
- The "1.1 sigma tension with LEP combination" computed in Section 6.3 is meaningless if the extraction method is degenerate.
- The uncertainty breakdown (stat/exp/hadr/theo) gives false precision to a non-result.
- The docstring in `extract_alphas.py` (lines 16-19) claims "chi2 at the minimum is ~1.3/12" and "optimal rescaling factor is r = 0.978" -- these numbers disagree with the actual output (chi2 = 47.7/12, r = 0.896), indicating the docstring was never updated after the code was modified.

**Action required:** (a) Clearly label the alpha_s result as "illustrative only -- not a valid extraction" in the artifact, not buried in caveats. The current Section 6.2 heading "Indicative Result" is too mild. (b) Fix the stale docstring in `extract_alphas.py`. (c) Remove or heavily caveat the "1.1 sigma tension" comparison -- comparing a degenerate LO extraction to NLO+NLL results is not informative.

### A3. Hadronization systematic is not adequately implemented

**Conventions requirement (Section "Generator model"):** "Compare generators with fundamentally different fragmentation models (e.g. string vs. cluster). This is typically the dominant systematic for event-shape measurements." The conventions further state: "Data-driven reweighting of a single generator's response matrix is not a substitute."

The artifact reports "Hadronization model: ~0%" (Section 3.1). The "Herwig-like reweighting" apparently produced a negligible shift. This is deeply suspicious for an event-shape measurement where hadronization is universally the dominant systematic. The ALEPH 2004 reference analysis quotes hadronization as a ~1-3% per-bin effect.

The Strategy (Section 6.1.3) planned a specific approach: "reweight the Pythia 6.1 particle-level distribution to match Herwig 7 generator-level distributions." Was this actually done? Was a Herwig 7 sample generated as planned? If the "Herwig-like reweighting" is just a generic pT-broadening applied to the prior (as suggested by the PARTIAL note in Section 3.2), this is far weaker than what was planned and what conventions require.

A ~0% hadronization systematic for thrust at the Z pole is not credible. Either the implementation is wrong, or the reweighting is so weak that it does not actually probe hadronization differences.

**Action required:** (a) Document exactly what the "Herwig-like reweighting" does -- what parameters were changed, what is the resulting particle-level thrust shift. (b) If a Herwig 7 generator-level sample was not produced as planned in the strategy, explain why. (c) If the hadronization systematic is genuinely ~0%, provide a detailed justification. Otherwise, implement a more realistic hadronization variation. The ALEPH 2004 analysis quotes ~1-2% from hadronization for thrust in the fit range; getting ~0% requires explanation.

### A4. Reference comparisons use diagonal-only chi2 despite full covariance being available

**Conventions requirement (Section "Comparison to reference measurements"):** "Use the full covariance matrix (not diagonal uncertainties only)." The comparisons to ALEPH 2004 and archived ALEPH (Section 6.4) use `diagonal_approx` method with chi2/ndf = 2.33 and 1.88 respectively. Both exceed chi2/ndf = 1.5, triggering the conventions requirement to investigate.

The artifact does investigate the Pythia 6.1 comparison (chi2/ndf = 5.22, done with full covariance), but the reference comparisons are dismissed with "the chi2 is inflated by the approximate nature of the reference (digitized from publication, not HEPData tables)." This may be true but is not demonstrated.

**Action required:** (a) For the ALEPH 2004 comparison with chi2/ndf = 2.33: even with diagonal-only uncertainties, this exceeds 1.5. The investigation must go beyond "the reference values are approximate." Show a bin-by-bin comparison identifying which bins drive the chi2. (b) Attempt to use HEPData tables for the ALEPH 2004 result rather than approximate digitized values.

---

## Category B Findings (Should Address)

### B1. Covariance matrix dominated by BBB systematic

The systematic covariance is dominated by the alternative-method (BBB) shift at 21%. This means the total covariance matrix is almost entirely determined by a single systematic source that is not a genuine uncertainty but a method comparison. The covariance matrix is essentially rank-1 (outer product of the BBB shift vector).

This has consequences:
- The condition number of 1.71 x 10^5 may be acceptable, but the effective number of constrained degrees of freedom is low.
- The alpha_s fit using this covariance will be dominated by the BBB systematic, not by the actual measurement uncertainties.

**Recommendation:** Separate the BBB systematic from the "core" systematics. Report results with and without BBB to show the impact. Consider whether the BBB systematic should be treated as an envelope (max shift) rather than included in the covariance as a fully-correlated source.

### B2. Response matrix properties not reported

**Conventions requirement (Section "Response matrix construction - Matrix properties to report"):** The artifact does not report: diagonal fraction, column normalization check, or efficiency as a function of tau. These are Phase 3 deliverables but should be summarized in Phase 4a for completeness. The conventions list these as required reporting items.

**Recommendation:** Add a brief summary of response matrix properties to the artifact, referencing the Phase 3 results.

### B3. Input validation (data/MC kinematic comparisons) not referenced

**Conventions requirement (Section "Response matrix construction - Input validation"):** "Produce data/MC comparisons for all kinematic variables that enter the observable calculation, resolved by reconstructed object category." The Phase 4a artifact does not reference whether this was done in Phase 2/3. The conventions require this before proceeding to unfolding.

**Recommendation:** Add a reference to the Phase 2/3 data/MC validation, confirming it was performed and summarizing the agreement level.

### B4. Year-to-year consistency check not performed

**Strategy Section 6.1.5:** "Compare corrected distributions from individual data-taking years (1992, 1993, 1994, 1995)" was planned as an additional systematic. There is no mention of this in the Phase 4a artifact, and no code or results files for it. This probes time-dependent detector effects and is standard practice at LEP.

**Recommendation:** Either implement the year-by-year comparison or document why it was dropped.

### B5. Selection cut systematics are mostly negligible -- insufficient variation?

Three systematics show ~0% shift: selection efficiency, MissP cut, and selection (TPC hits at 0.17%). The strategy planned to vary multiple event-level cuts: charged energy threshold, sphericity axis cut, track multiplicity, track pT, d0/z0. The artifact only reports three selection-related variations (TPC hits, MissP, selection efficiency).

Were all planned selection variations actually performed? The strategy noted that some variations might be precluded by pre-applied "aftercut" cuts. If so, this limitation should be documented.

**Recommendation:** Confirm that all planned selection variations from the strategy were either implemented or documented as precluded by the pre-selection.

### B6. Closure test chi2 values are suspiciously identical between Phase 3 and Phase 4a

The Phase 4a independent closure test at 3 iterations gives chi2/ndf = 0.924. But this is described in Section 5 as: "The Phase 3 closure chi2 was inflated by same-sample correlations." This implies Phase 3 gave higher values. However, the artifact also states "chi2/ndf = 0.924-2.55 at 3 iterations, depending on reporting convention" for Phase 3. The exact same value (0.924) appearing in both the Phase 3 and Phase 4a independent test is suspicious -- are these actually different tests?

**Recommendation:** Clarify whether the Phase 4a closure test uses genuinely independent half-samples. Show the half-A and half-B sample sizes and confirm no overlap.

---

## Category C Findings (Suggestions)

### C1. Correlation matrix visualization not shown

The conventions require "Correlation matrix visualization." The artifact mentions the covariance is PSD but does not reference a correlation matrix plot. This is a useful diagnostic that should be included in the figures.

### C2. Toy pseudo-experiment validation not performed

Conventions recommend: "For robust validation, generate toy pseudo-experiments from the reference measurement (sampling from its covariance) and compare the observed chi2 to the toy distribution." This is listed as a recommended validation for reference comparisons with chi2/ndf > 1.5.

### C3. Numerical values missing from artifact table

Section 2.1 has a table with "see thrust_distribution.csv" placeholders. The full numerical result should be in the artifact itself for self-containment, or at minimum the fit-range values should be listed.

### C4. Theory uncertainty floor is borrowed, not derived

The theory uncertainty of +/-0.005 is taken directly from the LEP combination rather than being derived from the actual scale variation in this analysis. The scale variation gives only +/-0.0012 (from the r * running calculation), so the analysis falls back to the "LEP floor." This is reasonable for an LO extraction but should be explicitly flagged as borrowed rather than computed.

---

## Systematic Completeness Table: Row-by-Row Verification

| Source | Conventions | This Analysis | Reference 1 (LEP comb.) | Reference 2 (ALEPH 2004) | Verdict |
|--------|-------------|---------------|--------------------------|---------------------------|---------|
| Statistical (data) | Required | PASS (500 toys) | Yes | Yes | OK |
| Response matrix (MC stat) | Required | PASS (200 replicas) | Implicit | Implicit | OK |
| Object-level response (tracking) | Required | PASS (2% smear) | Yes | Yes | OK |
| Object-level response (calorimeter) | Required | PASS (5% scale) | Yes | Yes | OK |
| Selection cuts | Required | PARTIAL -- only 3 of ~6 planned variations reported | Yes | Yes (extensive) | **NEEDS CLARIFICATION (B5)** |
| Background contamination | Required | PASS | Yes | Yes | OK |
| Regularization strength | Required | PASS (+/-1 iter) | N/A (BBB) | N/A (BBB) | OK |
| Prior dependence | Required | PASS (0.24%) | N/A | N/A | OK |
| Alternative method | Required | PASS (BBB) | N/A | N/A | OK |
| Hadronization model | Required | **~0% -- NOT CREDIBLE** | Pythia/Herwig/Ariadne | Pythia/Herwig/Ariadne | **CATEGORY A (A3)** |
| ISR treatment | Recommended | PASS | Yes | Yes | OK |
| Heavy flavor | Recommended | PASS | Not separately | Not separately | OK |
| QED radiative corrections | Optional | Not implemented (noted) | Yes | Yes | ACCEPTABLE |
| Stress test | Required | **NOT DONE** | N/A | N/A | **CATEGORY A (A1)** |
| Year-to-year consistency | Planned | **NOT DONE** | N/A | N/A | **CATEGORY B (B4)** |

---

## Answers to Concrete Operating Principles

**1. Are all systematic sources from conventions either implemented or justified?**
No. The stress test is missing entirely (A1). The hadronization model systematic is implemented but produces a non-credible ~0% shift (A3). Selection cut variations appear incomplete relative to the strategy plan (B5).

**2. Does this analysis match or exceed the reference analyses' systematic coverage?**
No. The reference analyses (ALEPH 2004, LEP combination) used three fully simulated generators for the hadronization systematic. This analysis has only one generator with a weak reweighting that gives ~0%. The reference analyses performed extensive selection cut variations; this analysis reports only three. The alpha_s extraction uses LO scaling rather than NLO+NLL theory, but this is planned for Phase 4c.

**3. What would a competing group have that we don't?**
- A genuine Herwig or Ariadne comparison (even at generator level with fast simulation, as the strategy proposed but was apparently not pursued).
- A stress test validating the unfolding under shape mismodeling.
- A credible hadronization uncertainty (1-3% per bin, not ~0%).
- NLO+NLL theory for the alpha_s extraction (planned for Phase 4c).
- HEPData-sourced reference values for validation comparisons.

---

## Disposition

**Phase 4a cannot advance to human review until A1 (stress test) and A3 (hadronization systematic) are resolved.** A2 (alpha_s labeling) and A4 (reference comparison investigation) should also be addressed but are less likely to change the physics result. The Category B items are important for completeness but do not block advancement.
