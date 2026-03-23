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

   **Covariance construction.** The construction method must match the
   correction method. Before choosing, consult how published analyses
   of the same observable constructed their covariance — the literature
   (arXiv, INSPIRE) is the best guide for method-specific pitfalls.
   Common approaches:

   - **Bootstrap** (preferred for bin-by-bin): resample events N times
     (N ≥ 500), recompute the full correction chain for each replica,
     compute sample covariance of corrected distributions. Must resample
     at event level, not bin level.
   - **Toy MC** (preferred for iterative unfolding): fluctuate the input
     distribution according to Poisson statistics N times, unfold each,
     compute sample covariance.
   - **Analytical propagation** (acceptable for simple bin-by-bin):
     propagate Poisson uncertainties through the correction formula.
     Simpler but misses correlations from shared correction denominators.

   The covariance must be computed on the full dataset. Scaling a
   covariance from a subset by N/n is approximate — it assumes the
   correlation structure is sample-size independent, which is often
   false for unfolded distributions. If computational cost prevents
   full-dataset bootstrap, document the approximation.

   **Chi2 computation.** When a covariance matrix is available, chi2
   must be computed using the full covariance (not diagonal only).
   Diagonal chi2 ignores bin-to-bin correlations and underestimates
   the true chi2 when bins are positively correlated. Report both
   chi2/ndf (covariance) and chi2/ndf (diagonal) for transparency.
   If the condition number exceeds 10^8, note that the covariance-based
   chi2 may be unreliable due to ill-conditioning.

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
- **Observable redefinition is not a systematic.** Removing an entire
  particle category (e.g., dropping all neutrals from energy-flow
  thrust to get charged-only thrust) changes WHAT is measured, not
  the uncertainty on the measurement. The resulting distribution is a
  different observable with a different particle-level definition,
  different correction factors, and potentially different theory
  sensitivity. Treating the difference as a detector systematic
  inflates the uncertainty with a physically meaningless number.
  Instead: (a) keep the redefined observable as a cross-check that
  validates the analysis chain with different detector inputs,
  (b) evaluate detector-response uncertainties by varying the response
  parameters (energy scale, efficiency) while keeping the particle-level
  definition fixed, (c) run the full unfolding chain for both
  definitions if both are physics-relevant, with separate covariance
  matrices.

---

## References

- Cowan, G., "Statistical Data Analysis" (Oxford University Press, 1998).
  General reference for unfolding and covariance propagation in HEP.
