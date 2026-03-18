# Unfolding Measurements

Conventions for analyses that correct a measured distribution for detector
effects to produce a particle-level result.

## When this applies

Any analysis that constructs a response matrix from simulation and applies a
correction procedure (IBU, SVD, TUnfold, OmniFold, bin-by-bin correction
factors) to transform a detector-level distribution into a particle-level
result.

---

## Particle-level definition

Before anything else, define the particle-level target precisely:

- What particles are included (stable hadrons, charged-only, with/without
  neutrinos, etc.)
- What phase space (fiducial vs. full, any particle-level cuts)
- Treatment of ISR/FSR photons
- Treatment of hadron decays (lifetime threshold, e.g. c*tau > 10 mm)

This definition determines what the measurement *means*. It must be stated
in the strategy phase and held fixed throughout. Changing it invalidates the
response matrix.

---

## Response matrix construction

### Input validation

Before building the response matrix, validate the MC model that will be used
to construct it. Produce data/MC comparisons for all kinematic variables that
enter the observable calculation, resolved by reconstructed object category.

Rationale: the response matrix encodes the detector's effect on the
observable. If the MC mismodels the inputs to the observable, the response
matrix is wrong. Observable-level data/MC agreement can mask compensating
category-level mismodeling.

Required deliverables before proceeding:
- Per-category kinematic distributions with data/MC ratio panels
- Quantitative summary of agreement level
- Documentation of identified discrepancies and expected impact

### Matrix properties to report

- Dimension (N_reco x N_gen bins)
- Diagonal fraction (fraction of events staying in the same bin)
- Column normalization (should sum to 1 if properly constructed)
- Condition number (if matrix inversion is involved)
- Efficiency as a function of the particle-level observable

---

## Regularization and iteration

### Recommended methods

- **SVD (Hoecker & Kartvelishvili)** — default for 1D measurements. Singular
  value truncation naturally handles ill-conditioned response matrices by
  discarding small singular values that amplify statistical noise. Vary the
  number of kept singular values (k) and select the value where closure
  passes and the result is stable over k ± 1.
- **TUnfold (Tikhonov-regularized)** — preferred for 2D measurements or
  when L-curve optimization is desired. The Tikhonov parameter provides
  continuous regularization control.
- **IBU (iterative Bayesian unfolding)** — use as a cross-check method,
  not the primary. IBU is sensitive to the prior and can diverge on
  ill-conditioned matrices where SVD succeeds. When IBU is used as a
  cross-check, agreement with the SVD result validates the procedure;
  disagreement requires investigation.
- **OmniFold** — for complex multi-dimensional cases where traditional
  methods are impractical. Requires careful validation as the method is
  less mature.

### Choosing the regularization strength

For SVD, the regularization parameter is the number of kept singular values
(k). For IBU, it is the number of iterations. For TUnfold, it is the
Tikhonov parameter (selected via L-curve or similar criterion).

The selection criterion should be:
1. Closure test passes (unfolding MC truth through the response recovers
   the truth within statistical precision)
2. Stress test passes (unfolding a reweighted truth through the response
   recovers the reweighted truth)
3. Stable plateau (result does not change significantly with small changes
   in regularization)

**Additionally:** verify that the result is not prior-dominated in any bin.
Repeat the unfolding with a flat (uniform) prior at the nominal
regularization. If any bin's corrected value changes by more than 20%
relative (i.e., |flat − nominal| / nominal > 0.20), the regularization is
insufficient for that bin.

**Remediation is mandatory and ordered.** The following steps must be tried
**in order** before excluding a bin:
1. **Try SVD** — truncate singular values. SVD naturally handles
   ill-conditioned matrices that cause IBU to diverge. Vary the number
   of kept singular values (k) and check closure.
2. **Adjust regularization** (more/fewer iterations for IBU, different
   Tikhonov parameter for TUnfold). Re-run the closure test to verify the
   method still converges. If the flat-prior shift drops below 20% without
   the closure test failing, this is the preferred fix.
3. **Merge the failing bin** with a neighbor. Wider bins have higher
   diagonal fraction and less prior sensitivity.
4. **Use a data-driven prior** for IBU. Initialize with the reco-level
   data shape (smoothed if needed) instead of MC truth. This removes the
   circular dependence on the MC model as prior.
5. **Exclude the bin** — last resort, appropriate only for bins at
   kinematic boundaries or distribution edges where the physics content
   is minimal.

**Wholesale exclusion (> 50% of bins failing) is a red flag** indicating
the binning or method is fundamentally inappropriate. It must trigger
re-evaluation of the binning granularity and/or the unfolding method
before proceeding. Simply excluding most bins and calling the remainder
a "measurement" is not acceptable — see §3 Phase 3 validation failure
remediation.

Rationale: closure and stress tests use the correct (or nearly correct)
prior. They can pass even when the regularization is too weak to overcome a
wrong prior. The flat-prior test exposes this.

### IBU convergence behavior

For IBU, the closure chi2/ndf as a function of iterations should follow
a characteristic pattern: starting near 0 (under-corrected, close to
prior), crossing ~1.0 at the optimal iteration count, then climbing
above 1.0 as statistical noise amplification dominates. **If chi2/ndf
increases monotonically from iteration 1 without a clear plateau
near 1.0**, this indicates a problem — the method may not be converging,
the response matrix may be poorly conditioned, or the binning may be
too fine. Investigate before accepting.

A well-behaved IBU should show a "sweet spot" where chi2/ndf ≈ 1.0
with a stable plateau spanning 2-3 iterations. If the plateau is
narrower than 1 iteration, the regularization is fragile and should be
documented as a limitation.

### Reporting

- State the nominal regularization choice and the criterion used
- Show closure chi2/ndf and stress chi2/ndf vs. regularization strength
- Show the flat-prior sensitivity per bin
- Include the regularization variation in the systematic budget

---

## Required systematic sources

These are the standard sources for an unfolded measurement. Omitting any
of them requires explicit justification.

### Detector and reconstruction

| Source | What to vary | Rationale |
|--------|-------------|-----------|
| Object-level response | Scale/smear/remove reconstructed objects by category (tracking, calorimetry, etc.) | Probes detector modeling without redefining the observable |
| Selection cuts | Vary each event-level cut that has non-negligible rejection | Selection efficiency is part of the correction |
| Background contamination | Vary background normalization or removal | Residual backgrounds bias the measured spectrum |

### Unfolding method

| Source | What to vary | Rationale |
|--------|-------------|-----------|
| Regularization strength | Vary iterations or regularization parameter | Residual regularization bias |
| Prior dependence | Alternative priors (reweighted truth, flat) | Tests sensitivity to assumed shape |
| Alternative method | At least one independent unfolding method | Cross-check of the full procedure |

**BBB validity criterion:**
- Bin-by-bin (BBB) correction factors are a valid alternative method only
  when the response matrix diagonal fraction exceeds ~70% across the fit
  range.
- When diagonal fractions are lower (significant bin migrations), BBB is
  structurally incorrect — compute and report it as a cross-check, but
  exclude it from the systematic budget.
- In this regime, a proper alternative (SVD, TUnfold, or matrix inversion
  with regularization) is required for the method systematic.
- If no valid alternative is available, document this as a limitation.

**When diagonal fraction is low (< 50%) and unfolding fails:**

This situation arises for multi-dimensional observables (2D+) or
observables where the detector response rearranges combinatorial
structure (e.g., jet clustering trees, where tracking inefficiency
changes the tree topology). The remediation hierarchy applies:

1. **SVD with aggressive truncation** — keep only the first few singular
   values. This sacrifices resolution but may produce a stable result.
2. **Coarser binning** — reduce to the point where diagonal fraction
   exceeds 50%.
3. **1D projections** — unfold each projection independently where
   diagonal fractions are higher.
4. **BBB as model-dependent fallback** — document prominently that the
   result depends on the MC model. The hadronization systematic and
   prior dependence must be evaluated conservatively.
5. **Dimensionality reduction** — 2D → 1D projections as the primary
   result, with the 2D density as a BBB cross-check.

If none of these produce a method with diagonal fraction > 50%, the
measurement should be presented as BBB-corrected with explicit
model-dependence caveats. The prior dependence systematic is the
primary estimator of the correction's reliability.

### Generator model (hadronization / fragmentation)

| Source | What to vary | Rationale |
|--------|-------------|-----------|
| Hadronization model | Compare generators with fundamentally different fragmentation models (e.g. string vs. cluster) | The response matrix depends on the particle-level model. Different hadronization produces different detector response. This is typically the dominant systematic for event-shape measurements. |

This is not optional for normalized shape measurements. Data-driven
reweighting of a single generator's response matrix is not a substitute —
it probes data/MC shape differences but not the fundamental dependence on
the fragmentation model.

If alternative generators with full detector simulation are unavailable,
reweighting at particle level is acceptable but must be documented as a
limitation.

### Theory inputs

| Source | What to vary | Rationale |
|--------|-------------|-----------|
| ISR treatment | Correct for ISR or define measurement as ISR-inclusive; document the choice | Affects the particle-level definition |
| Heavy flavor | Vary b-quark mass or fragmentation if the observable is sensitive | Flavor composition affects the response |

### Normalized vs. absolute measurements

Systematic sources that affect only the overall normalization (luminosity,
total cross-section, trigger efficiency) cancel in **normalized** shape
measurements (e.g., (1/N) dN/dx) but remain relevant for **absolute**
cross-sections (e.g., dσ/dx). When planning the systematic program, the
agent must identify which type of measurement is being performed and
include or exclude normalization-only sources accordingly. Document the
reasoning — a reviewer will check that normalization sources are not
silently omitted from an absolute measurement.

---

## Required validation checks

The tests below formalize the criteria from the Regularization and
Covariance sections as explicit pass/fail gates.

1. **Closure test (Category A if fails).** Unfold MC truth through the
   response matrix and verify recovery of the input truth distribution
   within statistical precision (chi2 p-value > 0.05). Failure indicates
   a problem in the response matrix or unfolding procedure.

2. **Stress test (Category A if fails without remediation).** Unfold a
   reweighted MC truth (different shape from the nominal) through the
   nominal response matrix. The unfolded result should recover the
   reweighted truth. Failure indicates the method is sensitive to the
   assumed prior shape. **A stress test failure must trigger at least 3
   independent remediation attempts** (see §3 Phase 3 validation failure
   remediation) before being accepted as a limitation. Accepting a
   stress test failure without investigation is Category A at review.
   Use graded stress tests (5%, 10%, 20%, 50% reweighting magnitudes)
   to characterize the method's resolving power — a method that fails at
   50% tilt but passes at 10% may still be adequate if the expected
   data/MC difference is < 5%.

3. **Flat-prior test.** Repeat the unfolding with a uniform prior at the
   nominal regularization strength. If any bin changes by more than 20%
   relative to the nominal result, the regularization is too strong for
   that bin — increase iterations, merge bins, or exclude the bin.

4. **Alternative method cross-check.** Apply at least one independent
   unfolding method. Agreement validates the procedure; disagreement beyond
   the assigned method systematic requires investigation. (See BBB validity
   criterion in the systematic sources section.)

5. **Covariance matrix validation.** Verify positive semi-definiteness
   (all eigenvalues ≥ 0). Report the condition number; flag if > 10^10
   (numerically unstable inverse). Visualize the correlation matrix.

## BBB-specific validation

When bin-by-bin correction factors are used (either as the primary method
when diagonal fraction > 70%, or as a model-dependent fallback), the
standard validation tests have different interpretations:

**Closure test:** For BBB, applying C_ij to the same MC that derived them
is an algebraic identity. A **split-sample** closure test is required:
derive correction factors from one statistically independent half of the
MC, apply to the reco-level of the other half, and verify recovery of
the second half's gen-level truth. This tests statistical stability, not
method correctness.

**Stress tests:** BBB stress tests (reweight truth, apply nominal C_ij)
are also algebraic identities — the reweighting cancels in the gen/reco
ratio. BBB stress tests provide no diagnostic information. The prior
dependence systematic (reweight gen, recompute C_ij) is the correct
analog.

**Flat-prior test:** Not applicable to BBB (no prior). The prior
dependence systematic serves as the BBB analog.

**Alternative method:** When BBB is the primary method, SVD or TUnfold
(not IBU) should be used as the cross-check. When BBB is a fallback
(diagonal fraction < 70%), the fact that proper unfolding methods fail
must be documented as a limitation, and the prior dependence +
hadronization model systematics must be enlarged to cover the
model-dependent correction.

---

## Covariance matrix

### Construction

- Statistical covariance: from analytical propagation through the unfolding
  or from bootstrap/toy replicas
- Systematic covariances: outer product of shift vectors (fully correlated
  per source) is the standard approach. Template-based approximations
  (using statistical correlation structure for systematic components)
  should be documented as approximations.
- Total: sum of all components

### Validation

See Required validation check #5 above for the specific criteria
(eigenvalue check, condition number threshold, correlation visualization).

---

## Comparison to reference measurements

When comparing the unfolded result to a published measurement of the same
quantity:

- Use the full covariance matrix (not diagonal uncertainties only)
- Report chi2/ndf and the corresponding p-value
- If chi2/ndf > 1.5 with the full covariance, investigate the source of
  tension before proceeding. Document the investigation even if the cause
  is understood.
- For robust validation, generate toy pseudo-experiments from the reference
  measurement (sampling from its covariance) and compare the observed chi2
  to the toy distribution.

---

## Pitfalls

- **Bin 0 with zero diagonal.** If any bin has zero (or near-zero) diagonal
  response, the unfolded result for that bin is entirely model-dependent.
  Either merge it with a neighbor or exclude it.
- **Normalizing before unfolding.** Normalize after unfolding + efficiency
  correction, not before. Pre-normalization introduces bin-to-bin
  correlations that the response matrix doesn't model.
- **Data/MC ratio as "MC modeling" systematic.** Reweighting the response
  matrix by the reco-level data/MC ratio probes shape mismodeling but does
  not replace a genuine alternative-generator comparison. It's a useful
  cross-check, not a substitute.
- **Covariance condition number.** A very large condition number (>10^10)
  means the inverse is numerically unstable. Consider regularizing the
  covariance or restricting the chi2 calculation to a well-conditioned
  sub-matrix.

---

## References

- D'Agostini, G., "A multidimensional unfolding method based on Bayes'
  theorem" (Nucl. Instrum. Meth. A362, 487, 1995). The foundational paper
  for iterative Bayesian unfolding (IBU).
- Hoecker, A. and Kartvelishvili, V., "SVD approach to data unfolding"
  (Nucl. Instrum. Meth. A372, 469, 1996). INSPIRE: Hocker:1995kb.
  Singular value decomposition method with regularization.
- Schmitt, S., "TUnfold: an algorithm for correcting migration effects in
  high energy physics" (JINST 7, T10003, 2012). INSPIRE: Schmitt:2012kp.
  Tikhonov-regularized matrix inversion with L-curve optimization.
- Andreassen, A. et al., "OmniFold: A Method to Simultaneously Unfold All
  Observables" (Phys. Rev. Lett. 124, 182001, 2020). INSPIRE:
  Andreassen:2019cjw. Machine-learning-based unfolding.
- Cowan, G., "Statistical Data Analysis" (Oxford University Press, 1998).
  General reference for unfolding, regularization, and covariance
  propagation in HEP.
