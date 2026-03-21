# Unfolding Measurements

Conventions for analyses that correct a measured distribution for detector
effects to produce a particle-level result.

## When this applies

Any analysis that corrects a detector-level distribution to a
particle-level result — regardless of the correction method used
(matrix inversion, iterative, bin-by-bin, machine-learning, or other).

---

## What the measurement must deliver

1. **A precise particle-level definition.** What particles are included,
   what phase space, ISR/FSR treatment, lifetime threshold. This
   definition determines what the measurement *means*. It must be stated
   in the strategy phase and held fixed throughout.

2. **A correction procedure that passes validation.** The method is the
   analyst's choice — but it must pass the quality gates below.

3. **A covariance matrix.** Statistical + systematic components + total.
   Must be positive semi-definite. Must be provided in machine-readable
   format.

4. **An alternative method cross-check.** At least one independent
   correction procedure applied to the same data. Agreement validates
   the primary method; disagreement requires investigation.

---

## Literature requirement

**Before choosing a correction method, read how >=2 published analyses
of the same or a similar observable handled the correction.** Query the
RAG corpus for published measurements. For each reference analysis,
document:

- What correction method was used
- How the response matrix was constructed (what was matched to what)
- What validation tests were performed
- What the dominant systematic sources were

The strategy must cite these references and justify any deviation from
established practice. If published analyses successfully unfold an
observable that the current analysis claims is unfoldable, the burden of
proof is on the current analysis to explain the discrepancy.

---

## Quality gates

These are pass/fail requirements. The specific method that satisfies
them is the analyst's choice.

1. **Closure test.** The correction procedure applied to MC must recover
   the MC truth within statistical precision (chi2 p-value > 0.05).
   For bin-by-bin correction, a split-sample closure is required (derive
   factors from one half, apply to the other).

2. **Stress test.** The correction applied to a reweighted MC truth
   (different shape from nominal) must recover the reweighted truth.
   Use graded magnitudes (5%, 10%, 20%, 50%) to characterize the
   method's resolving power.

3. **Prior/model dependence.** Quantify how much the result depends on
   the MC model used to derive the correction. This is typically the
   dominant systematic for shape measurements.

4. **Covariance validation.** Positive semi-definite (all eigenvalues
   >= 0). Condition number < 10^10. Visualize the correlation matrix.

5. **Data/MC input validation.** Before building any correction, produce
   data/MC comparisons for all kinematic variables entering the
   observable. Document discrepancies and their expected impact.

**If any gate fails:** investigate and attempt remediation before
accepting as a limitation. Document what was tried.

---

## Known pitfalls

These are things that have gone wrong in past analyses. They are
warnings, not a checklist.

- **Normalizing before correcting.** Normalize after correction +
  efficiency, not before. Pre-normalization introduces bin correlations
  the correction doesn't model.
- **Confusing closure with validation.** Applying correction factors to
  the same MC that derived them is an algebraic identity, not a test.
- **Flat systematic estimates.** A perfectly flat relative shift across
  all bins of a shape measurement likely means the systematic was
  assigned, not propagated. Propagate through the analysis chain.
- **Double-counting model dependence.** If two "independent" systematic
  sources use the same variation mechanism (e.g., both use a 50% tilt
  of the MC truth), they are not independent. Merge or orthogonalize.
- **Wrong matching strategy for the response matrix.** For observables
  with variable multiplicity per event (jet substructure, fragmentation
  functions, Lund declusterings), matching individual sub-objects
  (1st reco ↔ 1st gen) can produce artificially terrible response
  matrices. Read how published analyses construct theirs.

---

## References

- Cowan, G., "Statistical Data Analysis" (Oxford University Press, 1998).
  General reference for unfolding and covariance propagation in HEP.
