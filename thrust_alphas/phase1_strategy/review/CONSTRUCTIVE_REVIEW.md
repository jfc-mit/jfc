# Constructive Review: Phase 1 Strategy

**Reviewer role:** Constructive ("good cop")
**Artifact reviewed:** `phase1_strategy/exec/STRATEGY.md`
**Conventions consulted:** `conventions/unfolding.md`
**Date:** 2026-03-15

---

## Overall Assessment

This is a strong, well-structured strategy document. The physics motivation is clear, the observable definition is precise and follows LEP conventions, the systematic plan is comprehensive and explicitly maps every required convention source, and three reference analyses are identified with a detailed comparison table. The document reads as though written by someone who has done event shape analyses before. The suggestions below are aimed at elevating this from a solid plan to an excellent one.

---

## Completeness Checks

### 1. Are all systematic sources from `conventions/unfolding.md` covered or justified?

**Yes.** Section 6.1 enumerates every required source from the conventions document:
- Object-level response: covered (Section 6.1.1)
- Selection cuts: covered (Section 6.1.1)
- Background contamination: covered (Section 6.1.1)
- Regularization strength: covered (Section 6.1.2)
- Prior dependence: covered (Section 6.1.2)
- Alternative method: covered (Section 6.1.2)
- Hadronization model: covered (Section 6.1.3)
- ISR treatment: covered (Section 6.1.4)
- Heavy flavor: covered (Section 6.1.4)

The enumeration is explicit and binding. No omissions found.

### 2. Are 2-3 reference analyses identified with systematic programs tabulated?

**Yes.** Three reference analyses are identified (Sections 7.1-7.3), with a comparison table in Section 7.4. The references are well-chosen: the LEP QCD combination (the authoritative benchmark), DELPHI oriented event shapes (a modern re-analysis with detailed systematics), and the archived ALEPH QGP search (which uses the same dataset).

### 3. If a competing group published a measurement of the same quantity, what would they have that we don't?

See findings below -- there are a few areas where a competing group might do something additional, but none rise to Category A.

---

## Findings

### (B-1) Covariance matrix construction plan could be more specific

**Section affected:** Sections 5 and 9.1

The strategy mentions using the "full covariance matrix" for the alpha_s fit (Section 9.1) and for external comparisons (Section 10.2), but the plan for *constructing* the covariance matrix is not spelled out. The conventions document (Section "Covariance matrix") requires:

- Statistical covariance from analytical propagation or bootstrap/toy replicas
- Systematic covariances from outer product of shift vectors
- Validation: positive semi-definiteness, condition number, correlation matrix visualization

**Suggestion:** Add a brief subsection (e.g., Section 5.5 or a new Section 6.3) that states the plan for covariance construction. For IBU, bootstrap replicas are the natural choice for statistical covariance. For systematics, the outer-product approach is standard. Stating this now prevents ambiguity later and ensures Phase 4 reviewers have a clear baseline to check against.

**Classification: (B)** -- the intent is clear from context, but the explicit plan is absent.

### (B-2) Ariadne (or a third generator) absent from hadronization comparison

**Section affected:** Section 6.1.3, Table in Section 7.4

Reference Analysis 1 (LEP combination) used three generators: Pythia, Herwig, and Ariadne. Reference Analysis 2 (DELPHI) used four: JETSET, Ariadne, Herwig, and COJETS. The LEP corpus confirms that ALEPH's own event shape publications used Ariadne as a third hadronization model (see inspire:858650, which discusses JETSET/PYTHIA, HERWIG, ARIADNE, and COJETS for fragmentation model comparisons).

This analysis plans only Pythia 6.1 + Herwig 7 (via reweighting). Adding an Ariadne-like comparison (or even a Pythia 8 with a different tune, or Sherpa with cluster hadronization) would strengthen the hadronization systematic, which the strategy itself identifies as the dominant uncertainty.

**Suggestion:** Consider adding a Sherpa or Pythia 8 (with a significantly different tune) generator-level sample as a third hadronization comparison point. Since these are generator-level only (no detector sim needed), the cost is low. If this is judged too costly, document the rationale for restricting to two models and note it as a difference from the reference analyses.

**Classification: (B)** -- two generators (string vs. cluster) is the minimum; three would match the reference analyses and strengthen the result.

### (B-3) Fit range for alpha_s extraction deserves more discussion of sensitivity

**Section affected:** Section 9.1, 9.2

The fit range is stated as $0.05 \leq \tau \leq 0.30$, and fit range variation ($\pm 1$ bin) is listed as a theoretical systematic. This is appropriate, but the strategy does not discuss how the fit range boundaries will be *chosen* or *optimized*.

The LEP corpus (hep-ex/9812004) notes that DELPHI adjusted fit ranges per observable "until the value of alpha_s obtained was stable" and required hadronization corrections below 40% and acceptance above 80%. The ALEPH cluster analysis (inspire:328475) required corrections "typically less than 10%."

**Suggestion:** Add criteria for fit range selection: e.g., require the hadronization correction factor to be below some threshold (e.g., 30-40%) at both boundaries, and require the chi2/ndf to be stable against boundary shifts. This makes the fit range choice less ad hoc and more defensible under review.

**Classification: (B)** -- the fit range variation systematic partially covers this, but documenting the selection criteria strengthens the analysis.

### (B-4) Power corrections approach could be more concrete

**Section affected:** Section 8.3

The strategy mentions the Dokshitzer-Webber power corrections as an alternative to MC-based hadronization corrections, but does not commit to using them. The framing is "two approaches" without stating which is primary.

**Suggestion:** Clarify whether the power corrections approach will be (a) the primary method with MC-based as cross-check, (b) the cross-check with MC-based as primary, or (c) both presented as independent results. The power corrections approach has the advantage of being more model-independent and enables a simultaneous alpha_s + alpha_0 fit, which is a standard deliverable in LEP event shape publications. If it will be implemented, state the planned predictions (which observables, which perturbative order for the power correction calculation). If it will not be implemented, state why and note as a limitation.

**Classification: (B)** -- both approaches are mentioned, but the plan is ambiguous about which will actually be implemented.

### (C-1) Response matrix validation plan should reference conventions explicitly

**Section affected:** Section 5.2

The conventions document requires explicit validation deliverables before building the response matrix: per-category kinematic distributions with data/MC ratio panels, quantitative summary of agreement, and documentation of discrepancies. The strategy mentions data/MC comparisons in Section 10.1 ("Data/MC comparison of all input kinematic variables before unfolding") but does not tie this explicitly to the response matrix construction.

**Suggestion:** Add a sentence in Section 5.2 referencing the per-category validation requirement from conventions, making it clear that the response matrix is not used until the input validation is complete. This is probably the intent already, but making it explicit prevents future ambiguity.

**Classification: (C)** -- the validation is planned (Section 10.1); this is about making the connection to the response matrix more explicit.

### (C-2) Toy pseudo-experiment validation mentioned in conventions but not in plan

**Section affected:** Section 10.2

The conventions document recommends: "For robust validation, generate toy pseudo-experiments from the reference measurement (sampling from its covariance) and compare the observed chi2 to the toy distribution." The strategy plans chi2/ndf comparisons with published results but does not mention the toy pseudo-experiment approach.

**Suggestion:** Add the toy pseudo-experiment comparison as a planned validation step. If the published ALEPH covariance matrix is available (it should be from the EPhJC publication), this is a straightforward and powerful validation that goes beyond a simple chi2 comparison.

**Classification: (C)** -- this would elevate the validation from standard to excellent, but its absence does not weaken the core analysis.

### (C-3) The analysis chain summary could include explicit mention of the `all` task

**Section affected:** Section 11

The methodology requires that `pixi.toml` has an `all` task that runs the full analysis chain. The chain summary in Section 11 is a good roadmap, but it does not mention the reproducibility contract (the `all` task).

**Suggestion:** Add a brief note in Section 11 that the full chain will be encoded as the `all` task in `pixi.toml`, ensuring end-to-end reproducibility.

**Classification: (C)** -- this is a process detail, not a physics issue.

### (C-4) Consider stating expected statistical precision per bin

**Section affected:** Section 5.3, 6.2

The strategy estimates 2-4 million hadronic Z decays and 20-30 bins, which implies ~100k events per bin on average. The expected statistical uncertainty per bin (~0.3% for the peak region) would be useful context for evaluating whether systematic uncertainties truly dominate.

**Suggestion:** Add a rough estimate of the statistical precision per bin (e.g., "with ~3M events in ~25 bins, the statistical precision per bin is ~0.2-0.5%, well below the expected systematic uncertainties"). This demonstrates that the measurement is systematics-limited, which is an important characteristic to state explicitly.

**Classification: (C)** -- helpful context for readers, not essential for the strategy.

---

## Summary

| ID | Finding | Classification |
|----|---------|---------------|
| B-1 | Covariance matrix construction plan not spelled out | (B) Should address |
| B-2 | Only two generators for hadronization (references used three) | (B) Should address |
| B-3 | Fit range selection criteria not documented | (B) Should address |
| B-4 | Power corrections approach ambiguous (primary vs. cross-check) | (B) Should address |
| C-1 | Response matrix validation should reference conventions more explicitly | (C) Suggestion |
| C-2 | Toy pseudo-experiment validation not mentioned | (C) Suggestion |
| C-3 | Analysis chain summary should mention `all` task | (C) Suggestion |
| C-4 | Expected statistical precision per bin would add context | (C) Suggestion |

**No Category A findings.** The strategy is complete with respect to the conventions and reference analyses. The Category B items would strengthen the document but do not block advancement. The Category C items are opportunities to elevate the presentation.

**Recommendation:** Address the B items before finalizing. The C items can be deferred to later phases if needed.
