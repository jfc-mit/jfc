# Extraction Measurements (Double-Tag / Hemisphere Counting)

Conventions for analyses that extract a physical parameter using double-tag
or hemisphere-counting methods — where the result comes from a closed-form
formula applied to observed yields and MC-derived efficiencies, exploiting
the self-calibrating properties of multi-tag counting.

## When this applies

Any analysis where the primary result is computed from a closed-form
expression of tagged and untagged yields in hemisphere pairs — not from a
template fit or unfolding procedure. The canonical example is R_b extraction
from N_tt / N_had using hemisphere tagging efficiencies.

Other extraction techniques (tag-and-probe efficiency measurements,
branching fraction ratios, cross-section ratios) share some conventions
with this file but have distinct requirements. They should use dedicated
conventions files when available.

If the analysis uses a binned likelihood fit to a discriminant shape, the
`unfolding.md` or search conventions apply instead.

---

## Standard configuration

- **MC pseudo-data for Phase 4a.** The expected result must be computed on
  MC-generated pseudo-data counts, not on real data. Generate counts from
  MC truth parameters using the extraction formula (e.g., for R_b:
  N_t = 2 * N_had * [eps_b * R_b + eps_nonb * (1 - R_b)]). Optionally
  Poisson-fluctuate to assess statistical reach.
- **Fixed random seed.** All pseudo-data generation and 10% subsample
  selection use documented fixed seeds for reproducibility.
- **Per-subperiod granularity.** When multiple data-taking periods exist,
  track the result per period as a standard cross-check.
- **Counting vs. likelihood extraction.** Pure counting (closed-form
  formula applied to yields) is appropriate when the extraction formula is
  simple and the systematic treatment is transparent. Likelihood extraction
  (fitting a model to binned or unbinned data) is preferred when: multiple
  parameters are extracted simultaneously, nuisance parameters need profiling,
  or correlations between inputs are complex. Document the choice and justify.
- **Uncertainty propagation.** For counting extractions with few inputs,
  analytical error propagation (partial derivatives) is standard. For
  extractions with many correlated inputs or non-linear formulas, toy-based
  propagation (Poisson-fluctuate inputs, repeat extraction, take RMS) is
  more robust. Report which method is used and, if analytical, verify
  against toys for at least the dominant sources.
- **Efficiency binning.** Efficiency corrections must be derived in bins
  fine enough to capture kinematic dependence but coarse enough for adequate
  statistics per bin. As a rule of thumb, each efficiency bin should contain
  at least ~100 MC events; below this, statistical noise in the correction
  dominates. Document the binning choice and its motivation.
- **Data-derived calibration (scale factors).** When the extraction depends
  on MC-derived efficiencies (e.g., tagging efficiency), derive data/MC
  scale factors from a control sample using tag-and-probe or similar
  methods. Apply these scale factors to the MC before extraction. If
  data-derived calibration is not feasible, assign the full data/MC
  difference as a systematic — but document why calibration was not done.
  Relying on uncalibrated MC efficiencies without justification is
  Category A.

  **Calibration independence is mandatory.** Each calibration must come
  from an observable that is independent of the primary result. For
  example, tagging efficiency can be calibrated from the d0 resolution
  (measured in a lifetime-independent way), or from a tag-and-probe
  method on a known sample. Deriving the correction by assuming the
  primary result equals a reference value (back-substitution) is a
  diagnostic, not a calibration — see `methodology/06-review.md` §6.8
  Tier 2 for the full independence classification. When a parameter
  cannot be independently calibrated, use the MC value with an inflated
  systematic covering the data-implied range.

---

## Required systematic sources

### Efficiency modeling

| Source | What to vary | Rationale |
|--------|-------------|-----------|
| Tag/selection efficiency | Vary efficiency corrections within their uncertainties | The extracted quantity depends directly on efficiency estimates |
| Efficiency correlation | Evaluate hemisphere or object correlation effects | Double-tag methods assume independence; violations bias the result |
| MC efficiency model | Compare efficiencies from alternative MC generators | Generator-dependent fragmentation affects tagging efficiency |

### Background contamination

| Source | What to vary | Rationale |
|--------|-------------|-----------|
| Non-signal contamination | Vary background fractions within estimated uncertainties | Residual backgrounds in the tagged sample bias the yield |
| Background composition | Use alternative models for background mixture | The relative contribution of different backgrounds affects the correction |

### MC model dependence

| Source | What to vary | Rationale |
|--------|-------------|-----------|
| Hadronization model | Compare generators with different fragmentation (string vs. cluster) | Fragmentation model affects both efficiencies and acceptance |
| Physics parameters | Vary heavy-quark mass, fragmentation function parameters | Input physics parameters propagate to the extracted quantity |

### Sample composition

| Source | What to vary | Rationale |
|--------|-------------|-----------|
| Flavour composition | Vary assumed non-signal flavour fractions | Extraction formulas depend on the composition of the inclusive sample |
| Production fractions | Vary assumed production ratios if used as inputs | Any external input contributes its uncertainty |

---

## Required validation checks

1. **Independent closure test (Category A if fails).** Apply the full
   extraction procedure to a statistically independent MC sample (not the
   sample used to derive efficiencies or corrections). Extract the quantity
   and compare to MC truth. The pull (extracted value minus truth, divided
   by the method's uncertainty) must be < 2 sigma. Failure indicates a bias
   in the method.

2. **Parameter sensitivity table.** For each MC-derived input parameter,
   compute |dResult/dParam| * sigma_param. Flag any parameter contributing
   more than 5x the data statistical uncertainty — these are the dominant
   systematics and require careful evaluation.

3. **Operating point stability (Category A if fails).** Scan the extracted
   result vs. the primary selection variable (e.g., the classifier working
   point or the cut threshold) over a range spanning at least 2x the
   optimized region. The result must be flat within uncertainties — a
   dramatic variation indicates the measurement is not robust and the
   operating point is not in a stable plateau. This is a physics red flag,
   not just a systematic: it means the result depends critically on an
   arbitrary choice. Investigate before proceeding.

   **The stability scan must include fit quality.** Report chi2/ndf (or
   equivalent GoF metric) at each scan point alongside the extracted
   value. A configuration that produces a small statistical uncertainty
   but poor GoF (chi2/ndf > 3) is not a stable operating point — it
   indicates the model does not describe the data at that configuration.
   When selecting among multiple configurations (e.g., kappa values,
   binning choices), the selection criterion must balance precision and
   GoF. If the minimum-variance configuration has poor GoF while other
   configurations have acceptable GoF, the latter should be preferred
   unless the GoF failure is understood and demonstrated not to bias the
   result.

4. **Per-subperiod consistency.** Extract the result independently for each
   data-taking period. Compute chi2/ndof across periods. A chi2/ndof >> 1
   indicates time-dependent effects (detector aging, calibration drift) not
   captured by the MC model.

5. **10% diagnostic sensitivity (Phase 4b).** The 10% data validation must
   include at least one diagnostic genuinely sensitive to data/MC
   differences — not just a comparison of the extracted quantity (which is
   dominated by correlated systematics and insensitive to subsample size).
   Required: data-derived tag rates or double-tag fractions compared to MC,
   and self-calibrated parameter comparison between 10% data and MC.

---

## Pitfalls

- **Running on real data in Phase 4a.** The entire point of the 4a → 4b →
  4c staged validation is that 4a uses MC-only pseudo-data. Computing the
  extraction on real data counts in 4a makes 4a and 4c identical and
  defeats the staged validation protocol.

- **Insensitive 10% test.** Comparing only the final extracted quantity on
  10% data vs. MC tells you almost nothing — the statistical uncertainty
  dominates and hides real data/MC differences. The 10% test must include
  intermediate diagnostics (tag rates, efficiency comparisons, per-period
  results) that are sensitive at the 10% statistics level.

- **Missing independent MC for closure.** The closure test must use an MC
  sample statistically independent from the one used to derive corrections
  and efficiencies. Using the same sample tests self-consistency, not the
  method's validity. If only one MC sample is available, split it (using a
  documented fixed seed) into derivation and validation halves. **A
  self-consistent extraction (deriving efficiencies and counting yields
  from the same sample) always recovers the correct answer by
  construction — this is an algebra check, not a closure test.** If a
  closure test produces pull = 0.00 at every operating point, this is
  a red flag that it is self-consistent rather than independent.
  Investigate before proceeding.

- **Assuming hemisphere independence.** Double-tag methods often assume that
  tagging in one hemisphere is independent of the other. QCD correlations
  (gluon splitting, color reconnection) violate this. Evaluate the
  correlation coefficient from MC and propagate its uncertainty.

- **MVA-induced hemisphere correlations.** When using an MVA (BDT, NN)
  for hemisphere tagging in a double-tag analysis, classifier inputs
  that are correlated with event-level properties (total multiplicity,
  event shapes, or hemisphere quantities like mass that are coupled
  across hemispheres) inflate the hemisphere correlation factors C_q.
  Check C_q at the working point: values far from 1.0 (C_b < 0.8 or
  C_b > 1.3) indicate the classifier introduces correlations beyond
  the QCD effects. Identify which inputs cause the correlation and
  consider removing them — the loss in AUC may be small while the
  gain in C_b stability is large. The self-calibrating advantage of
  the double-tag method relies on C_b ~ 1; large corrections amplify
  the systematic uncertainty on C_b.

- **MVA inputs correlated with the discriminant.** Every MVA input is
  correlated with the classifier output (the discriminant) — that is
  why it is an input. If the input is poorly modelled in MC (data/MC
  chi^2/ndf > 5), the discriminant distribution will differ between data
  and MC, and the efficiency at a given cut will not transfer. This
  failure mode is invisible to MC closure tests (which use only MC).
  The input variable quality gate (§3, Phase 3) exists to catch this
  before training. Inputs that are strong discriminators but poorly
  modelled should be calibrated (reweighted) or discarded — see §7.5
  for the required before/after verification.

- **Neglecting non-primary flavours.** Extraction formulas typically include
  terms for non-signal flavours (e.g., charm and light quark contributions
  in an R_b measurement). Setting these to nominal MC values without
  uncertainty propagation underestimates the systematic error.

- **Circular luminosity derivation.** When the analysis derives
  luminosities from the data using theoretical cross-sections (because
  no independent luminosity measurement is available), the lineshape or
  rate fit becomes tautological — chi^2 = 0 by construction, because the
  data exactly satisfies the model that generated the luminosities. The
  artifact must: (a) state the circularity explicitly with the derivation
  formula, (b) identify which diagnostics remain informative (per-subperiod
  consistency, comparison to published cross-sections, alternative
  luminosity sources), (c) frame observed-vs-expected comparisons as
  self-consistency checks, not independent validations. Presenting
  chi^2 = 0 as "excellent goodness-of-fit" without noting the circularity
  is Category A.
- **Inflated uncertainties from MC-evaluated systematics.** When a
  systematic is evaluated by scanning a parameter (e.g., kappa, binning
  choice, alternative method) on MC pseudo-data and then applied to the
  full data result, verify that the data-evaluated spread is consistent
  with the MC spread. If the data spread is significantly smaller (>2x),
  the MC evaluation may be inflated — the MC configuration space may
  include unphysical or irrelevant variations that the data naturally
  constrains. Use the data evaluation as the primary systematic, with
  the MC evaluation as an upper bound only if the data scan has too few
  points to be reliable. Inflated systematics are not "conservative" —
  they obscure the measurement's true sensitivity and make validation
  checks (pull < 2σ) meaningless. A measurement where the dominant
  systematic is 3x larger than necessary is not a measurement of the
  observable — it's a measurement of the systematic evaluation procedure.
- **Correlated uncertainties in combinations.** When combining results
  from multiple observables, methods, or subsamples, identify which
  systematic sources are shared (e.g., renormalization scale variation
  affects all observables identically; generator choice affects all
  channels). Shared sources must enter the combination as 100%
  correlated — not added in quadrature as if independent. Treating
  a dominant correlated systematic as uncorrelated can reduce the
  combined uncertainty by a factor of sqrt(N_observables), which is
  fictitious. Document the correlation assumption for each source
  in the combination formula.

---

## References

- LEP/SLD EWWG combination: "Precision electroweak measurements on the Z
  resonance" (Phys. Rept. 427, 257, 2006). INSPIRE: ALEPH:2005ab.
  Defines the standard methodology for heavy-flavour extraction at the Z.
- ALEPH R_b measurement: "A measurement of R_b using a lifetime-mass tag"
  (Phys. Lett. B401, 163, 1997). INSPIRE: Barate:1997ha. Reference for
  double-tag counting with hemisphere correlations.
- DELPHI R_b/R_c: DELPHI double-tag measurements of R_b and R_c — multiple
  papers across 1995-2000. Use `search_lep_corpus` with query "DELPHI R_b
  double tag" to retrieve specific papers and their systematic programs.
- SLD R_b: "A measurement of R_b using a vertex mass tag" (Phys. Rev. Lett.
  80, 660, 1998). INSPIRE: Abe:1997sb. Reference for high-purity
  single/double tag methods with self-calibrating efficiencies.
- PDG review: "Electroweak model and constraints on new physics" in the
  Review of Particle Physics. Current world averages for R_b, R_c, and
  correlation matrices between electroweak observables.
