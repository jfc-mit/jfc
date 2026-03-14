# Unfolding Measurements

Conventions for analyses that correct a measured distribution for detector
effects to produce a particle-level result.

## When this applies

Any analysis that constructs a response matrix from simulation and applies a
correction procedure (IBU, SVD, TUnfold, OmniFold, bin-by-bin correction
factors) to transform a detector-level distribution into a generator-level
(particle-level) truth distribution.

---

## Particle-level definition

Before anything else, define the particle-level target precisely:

- What particles are included (stable hadrons, charged-only, with/without
  neutrinos, etc.)
- What phase space (fiducial vs. full, any generator-level cuts)
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
- Efficiency as a function of truth-level observable

---

## Regularization and iteration

### Choosing the regularization strength

For iterative methods (IBU), the number of iterations is the regularization
parameter. For matrix methods (SVD), it's the number of kept singular values
or a Tikhonov parameter.

The selection criterion should be:
1. Closure test passes (unfolding MC truth through the response recovers
   the truth within statistical precision)
2. Stress test passes (unfolding a reweighted truth through the response
   recovers the reweighted truth)
3. Stable plateau (result does not change significantly with small changes
   in regularization)

**Additionally:** verify that the result is not prior-dominated in any bin.
Repeat the unfolding with a flat (uniform) prior at the nominal
regularization. If any bin within the measurement region changes by more
than 20%, the regularization is insufficient for that bin — increase
iterations, merge bins, or exclude the bin.

Rationale: closure and stress tests use the correct (or nearly correct)
prior. They can pass even when the regularization is too weak to overcome a
wrong prior. The flat-prior test exposes this.

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

- Positive semi-definiteness (eigenvalue check)
- Condition number (report; flag if > 10^10 for the fit sub-matrix)
- Correlation matrix visualization

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
- **Covariance condition number.** A very large condition number (>10^8)
  means the inverse is numerically unstable. Consider regularizing the
  covariance or restricting the chi2 calculation to a well-conditioned
  sub-matrix.
