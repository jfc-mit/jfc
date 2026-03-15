# Constructive Review: Phase 4a Inference (Expected Results)

**Reviewer:** Constructive Reviewer (presentation, validation, clarity)
**Date:** 2026-03-15
**Artifacts reviewed:**
- `phase4_inference/exec/INFERENCE_EXPECTED.md`
- `phase4_inference/exec/ANALYSIS_NOTE_DRAFT.md`
- `conventions/unfolding.md`
- Result CSVs and figures in `phase4_inference/exec/results/` and `phase4_inference/figures/`

---

## Summary Assessment

The Phase 4a inference artifact and draft analysis note are thorough and well-structured. The unfolded thrust distribution is produced with a complete systematic budget, validated covariance matrix, and independent closure test. The alpha_s extraction is correctly flagged as indicative only. The analysis is honest about its limitations. There are no Category A blockers, but several items would strengthen the work for journal submission.

---

## Category A: Must Resolve

None identified. The analysis meets all hard gate requirements.

---

## Category B: Should Address

### B1. Missing stress test (conventions requirement)

`conventions/unfolding.md` Section "Regularization and iteration" lists three criteria for choosing the regularization strength: (1) closure test, (2) stress test (unfolding a reweighted truth through the response), and (3) stable plateau. The closure test and plateau stability are demonstrated, but no stress test is reported anywhere in the INFERENCE_EXPECTED.md or the analysis note draft. The conventions state the stress test "should" pass, and the reporting section says to "show closure chi2/ndf and stress chi2/ndf vs. regularization strength."

**Action:** Run a stress test by reweighting the particle-level MC (e.g., linearly tilting the thrust distribution by +/-20%) and unfolding this reweighted detector-level spectrum through the nominal response matrix. Report the stress-test chi2/ndf vs. iterations. This validates that the unfolding can recover a distribution that differs from the prior, which is exactly the situation with data (15-20% below Pythia 6.1).

### B2. Response matrix properties not reported

`conventions/unfolding.md` under "Matrix properties to report" requires: dimension, diagonal fraction, column normalization, condition number, and efficiency as a function of the particle-level observable. The INFERENCE_EXPECTED.md states the matrix is 25x25 (dimension) but does not report diagonal fraction, column normalization check, or efficiency vs. tau. The analysis note draft (Section 4.2) mentions the matrix dimension but omits the other properties.

**Action:** Add a table or paragraph reporting the diagonal fraction (what fraction of events stay in the same bin), verification that columns sum to 1, and a plot or table of selection efficiency vs. tau at particle level. These are standard deliverables for an unfolding measurement.

### B3. Correlation matrix structure warrants discussion

The correlation matrix plot (`cov_correlation.png`) shows a striking pattern: nearly 100% correlation across the entire fit range block (tau = 0.05 to 0.30). This is dominated by the BBB systematic, which enters as a single outer product and therefore produces near-perfect correlation. While the matrix is technically valid (PSD, reasonable condition number), the near-rank-1 structure of the systematic covariance in the fit range means the chi2 is effectively driven by a single mode.

**Action:** Add a brief discussion in the analysis note acknowledging this correlation structure. Decompose the covariance into statistical-only and systematic-only components and show the chi2 vs. reference measurements computed with each separately. This would clarify whether the data-reference tension is driven by a shape disagreement (stat covariance) or absorbed by the large correlated systematic (total covariance). This is important for interpreting the chi2 values in Table 6.4 of the INFERENCE_EXPECTED.md.

### B4. Reference comparisons use diagonal-only chi2

The comparison_chi2.csv shows that the ALEPH 2004 and archived ALEPH comparisons use `diagonal_approx` while only the Pythia 6.1 comparison uses the full covariance. `conventions/unfolding.md` states: "Use the full covariance matrix (not diagonal uncertainties only)" for reference comparisons. This is understandable when the reference covariance is unavailable, but it should be explicitly justified in the note.

**Action:** State in the analysis note that the ALEPH 2004 and archived comparisons use diagonal uncertainties because the published covariance is not available (no HEPData entry with full covariance). Note that the diagonal chi2 values are upper bounds on the true chi2 when correlations are positive (which they are here).

### B5. Thrust distribution CSV only covers fit range

The `thrust_distribution.csv` file contains 13 bins (tau = 0.05 to 0.30), which is just the fit range. The full 25-bin result should also be provided in machine-readable form for completeness, since the analysis measures the distribution over tau in [0, 0.5].

**Action:** Produce a full 25-bin CSV with all uncertainties, or rename the current file to indicate it covers only the fit range and add a separate full-range file.

### B6. Analysis note draft lacks figures

The draft analysis note (ANALYSIS_NOTE_DRAFT.md) contains no figure references despite 14 figures having been produced in `phase4_inference/figures/`. A publication-quality analysis note must include:
- The unfolded distribution with data/MC ratio panel (exists: `final_result_with_unc.png`)
- The correlation matrix (exists: `cov_correlation.png`)
- Systematic shifts breakdown (exists: `syst_dominant.png`)
- Closure test results (exists: `indep_closure_test.png`)
- Comparison to references (exists: `compare_references.png`)
- The alpha_s chi2 profile (exists: `alphas_chi2_profile.png`)

**Action:** Add figure references throughout the analysis note. Each major result section should reference the corresponding figure.

### B7. Hadronization systematic underestimate needs quantitative bound

The analysis correctly flags the hadronization systematic as a limitation (~0% from reweighting vs. expected 2-5% from genuine alternative generators). However, the draft note and INFERENCE_EXPECTED.md do not provide a quantitative estimate of the missing uncertainty. Published LEP analyses typically quote 2-5% for hadronization model dependence of event-shape distributions.

**Action:** Add a sentence in the systematic budget section stating the expected magnitude from published references (e.g., "Published LEP analyses report 2-5% hadronization model uncertainty for thrust; our reweighting approach captures only the prior-sensitivity component, underestimating the true uncertainty by this amount"). Consider whether the total uncertainty should include an ad hoc floor based on published values, or whether this should be deferred to Phase 4c when better generators might be available.

---

## Category C: Suggestions

### C1. The alpha_s chi2 profile plot confirms the degeneracy

The chi2 profile plot shows an essentially flat line across the full alpha_s scan range, confirming the degeneracy described in the text. This is useful for the note -- it visually demonstrates why the LO extraction is unreliable. Consider adding a panel showing what a well-behaved chi2 parabola should look like (e.g., from a toy study with actual NLO shape variation) to help readers understand the contrast.

### C2. Normalization convention precision

The analysis note states normalization is to "unit integral over the full range tau in [0, 0.5]" (Section 4.3), but the alpha_s extraction renormalizes to "unit fit-range integral" (Section 7.2). These are different normalizations. Clarify which normalization applies to which result and ensure the CSV files document which convention is used.

### C3. The 1.1-sigma tension calculation should show its work

The INFERENCE_EXPECTED.md claims 1.1-sigma tension between alpha_s = 0.1066 +/- 0.0113 and the LEP combination 0.1202 +/- 0.0048. The pull is |0.1202 - 0.1066| / sqrt(0.0113^2 + 0.0048^2) = 0.0136/0.0123 = 1.1. This checks out, but the calculation should be shown explicitly, and a caveat added that the two uncertainties are not independent (both include theory scale variations).

### C4. Bin-by-bin correction formula

Section 5.3 of the analysis note defines BBB as C_BBB = N_gen/N_reco per bin. In principle, this should include an efficiency correction: C_BBB = N_gen_total / N_reco_matched or similar. Clarify whether the BBB correction accounts for events that are generated but not reconstructed (acceptance/efficiency).

### C5. ISR treatment systematic description

The ISR systematic is described as "Inclusive vs. leading-order ISR model comparison" but the exact implementation is unclear. What specifically was varied -- was an ISR reweighting applied, or were events with/without ISR photons compared? A sentence of implementation detail would help a referee.

### C6. Per-category kinematic validation

`conventions/unfolding.md` requires "per-category kinematic distributions with data/MC ratio panels" before building the response matrix. These were presumably produced in Phase 2/3 but are not referenced in the Phase 4a artifact. The analysis note should reference or include these validation plots.

---

## Figures Assessment

The 14 figures produced are of good quality with proper ALEPH labeling and sqrt(s) annotation. The ratio panels are present where needed. Key observations:

- `final_result_with_unc.png`: Clear presentation with log scale, ratio panel, fit range highlighted. The gray uncertainty band in the ratio panel correctly shows the total uncertainty growing at low and high tau.
- `cov_correlation.png`: Shows the near-100% correlation structure in the fit range clearly. The dashed lines marking the fit range boundaries are helpful.
- `syst_dominant.png`: Effective breakdown showing BBB dominance at the fit range edges. The green shaded region for BBB makes the scale of this systematic immediately apparent.
- `compare_references.png`: Good overlay of this analysis with ALEPH 2004 and archived ALEPH. The ratio panel is somewhat small and hard to read -- consider enlarging for the final note.
- `alphas_chi2_profile.png`: Effectively demonstrates the flat profile / degeneracy problem. The Delta-chi2 = 1 line sits just above the profile, confirming no meaningful minimum exists.

---

## Verdict

**Phase 4a gate: PASS with conditions.**

The artifact meets the hard gate requirements. The unfolded distribution, systematic budget, covariance matrix, closure test, and alpha_s extraction are all present and documented. The analysis is transparent about its limitations.

The B-category items (especially B1 stress test, B2 response matrix properties, and B6 figures in the note) should be addressed before the analysis note is considered publication-ready. None of them block Phase 4b/4c progression, but they represent gaps that a journal referee would flag.
