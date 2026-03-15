# Phase 3 Independent Reviewer Notes

**Analysis:** thrust_alphas
**Phase:** 3 (Selection and Modeling)
**Artifact reviewed:** `phase3_selection/exec/SELECTION.md`
**Date:** 2026-03-15
**Reviewer:** 1-bot critical reviewer (external to self-review)
**Review basis:** Methodology Section 6.4, `conventions/unfolding.md`, Phase 1 strategy

---

## Framing

The self-review identified 4 Category B issues and recommended Phase 4 proceed. This
review checks whether those findings are adequately documented, whether they should be
re-classified, and whether anything material is missing. The standard applied is whether
a journal referee or external collaboration reviewer would send this back.

---

## Assessment of Self-Review Findings

### Self-Finding 1: cos(θ_sph) cut not shown directly — Category B

**Assessment: Agree, but note a broader gap.**

The specific finding is valid. More generally, SELECTION.md Section 3.1 describes the
cos(θ_sph) distribution only in prose ("flat in the central region and falls near the
cut boundary"). Unlike the missing-momentum cut, which cites a dedicated figure
(`datamc_missp.{pdf,png}`), the sphericity axis cut has no dedicated figure reference
in Section 3. A figure with the data/MC overlay and the cut boundary marked is present
in the figures directory (`tau_data_mc_phase3.{pdf,png}` appears, though its content is
not the sphericity axis), but Section 3.1 does not cite any figure. This should be
resolved — either cite the existing figure or confirm one exists.

**Reclassification: Remains Category B.** The cut is standard ALEPH practice and
physically well-motivated, but producing the plot was already done (the figures directory
has the data/MC overlay plots); citing it is the only missing step.

### Self-Finding 2: Closure χ²/ndf > 1 — Category B

**Assessment: Partially agree; one aspect needs reclassification.**

The documented χ²/ndf of 1.91 at 2 iterations and 2.55 at 3 iterations (the nominal)
is above 1. The explanation in Section 5.2 is plausible (MC statistical correlations
between truth and response matrix because they are drawn from the same sample), and the
self-review correctly defers a proper independent-halves test to Phase 4a.

However, there is an undocumented tension: the nominal is chosen at **3 iterations** on
the basis of the "plateau criterion," but the minimum χ²/ndf is at **2 iterations**.
This is documented but not resolved — the document states "3 is robust against
under-regularization" while simultaneously acknowledging the closure quality is worse at
3 than at 2. This needs explicit justification of why the plateau criterion is preferred
over the χ²/ndf criterion when they conflict, especially because convention
`conventions/unfolding.md` lists closure test χ²/ndf as criterion 1 for choosing
regularization strength. If 2 iterations gives better closure, the burden of proof is on
3 iterations. The Phase 4a comparison of 2 vs. 4 iterations is planned, but 2 iterations
is listed only as a "cross-check," not as a genuine alternative nominal.

**Reclassification: Escalate to Category A.** The nominal iteration count is not
justified against the conventions criterion. Phase 4a must resolve this by either (a)
demonstrating via independent MC halves that the true closure χ²/ndf at 3 iterations is
≤ that at 2 iterations, or (b) changing the nominal to 2 iterations and documenting why.
This does not block proceeding to Phase 4a — it is the first task Phase 4a must
complete — but it must be resolved before Phase 4b (partial unblinding).

### Self-Finding 3: Data/MC per-category validation complete — Pass

**Assessment: Agree with one additional concern (see Finding A below).**

The completeness of the per-category validation is confirmed: 15 variables are covered,
split across charged (pwflag=0) and neutral (pwflag=4) categories. The convention
requirement (per `conventions/unfolding.md`, "Produce data/MC comparisons for all
kinematic variables that enter the observable calculation, resolved by reconstructed
object category") is met in letter.

One concern not raised in the self-review: the SELECTION.md does not document
**which pwflag categories are present in the data and what fraction of thrust each
contributes**. The analysis uses pwflag 0–5 for the observable but validates only
pwflag=0 and pwflag=4. If other pwflag values carry non-negligible momentum weight, the
validation is incomplete. This is Finding A below.

### Self-Finding 4: Condition number infinity — Category B

**Assessment: Agree, adequately documented.**

The condition number being reported as infinity because zero-content bins are included
is a software issue, not a physics issue. The self-review correctly identifies it as
Category B and notes the fix (restrict to active bins). The active sub-matrix condition
number should be reported in SELECTION.md Section 4 before Phase 4b. This finding is
adequately documented.

---

## New Findings

### Finding A: pwflag categories 1–3 and 5 not validated (Category A)

The observable `Thrust` is computed from all particles with `pwflag = 0–5` (SELECTION.md
Section 1.3: "charged + neutral particles, pwflag 0–5"). The data/MC validation in
Section 7 covers only pwflag=0 (good charged tracks) and pwflag=4 (neutral calorimeter
clusters). Categories pwflag=1 (bad charged tracks), pwflag=2 (V0 daughters), pwflag=3
(secondary charged tracks), and pwflag=5 (other neutral objects) are not validated.

The convention requirement is clear: "data/MC comparisons for all kinematic variables
that enter the observable calculation, resolved by reconstructed object category." Using
pwflag 0–5 in the thrust calculation but validating only pwflag 0 and 4 violates this
requirement if the unvalidated categories contribute non-negligible momentum to the thrust
sum.

**Required action before Phase 4b:** Either (a) demonstrate that pwflag 1–3 and 5 carry
negligible momentum fraction in the thrust sum (< 1% collectively, both data and MC), or
(b) produce data/MC validation plots for the categories that carry non-negligible weight.
If the thrust branch is pre-computed and does incorporate all pwflag categories, the
fractional momentum contribution of each category must be quantified and documented.

This is Category A because `phase3_selection/CLAUDE.md` explicitly states: "Are
particle-level inputs validated per object category with data/MC plots? (Category A if
missing for unfolded measurements)."

### Finding B: No data/MC comparison of the thrust observable itself (Category B)

SELECTION.md Section 8.1 notes the detector-level data and MC reco thrust distributions
are compared (Figure `prototype_detector_level.{pdf,png}`), but this is described only
qualitatively: "generally within ±10% across the fit range." The figure exists (confirmed
in figures directory), but no quantitative agreement table for the thrust distribution is
included in the artifact. For an event-shape unfolding, showing that the observable
data/MC ratio is within known agreement before correcting is standard documentation
practice. A quantitative max-deviation summary for the thrust distribution in the fit
range (0.05 < τ < 0.30) is missing from the artifact.

**Required action:** Add a quantitative summary of the τ distribution data/MC agreement
to SELECTION.md Section 8.1 (or a new subsection). This can be a brief table matching
the format of Section 7. This does not require re-running any code — the figure already
exists.

### Finding C: ISR cut not quantified per plot (Category B)

SELECTION.md Section 3.3 describes the ISR rejection cut motivation but cites no figure.
Unlike the missing momentum cut (which has a dedicated `datamc_missp` figure), there is
no figure reference for the ISR distribution. Only 1% of events are removed, so the
impact is small, but the convention-required "per-cut motivation by a plot" is not met
for this cut. The figures directory does not appear to contain a dedicated ISR
distribution figure.

**Required action:** Either produce and cite a figure showing the ISR variable
distribution with the cut boundary, or explicitly document that the ISR cut is
implemented via a pre-existing flag (`passesISR`) with no associated continuous
distribution available, and cite the ALEPH reference that defines it. A footnote
explaining this for a flag-only cut is acceptable to a referee.

### Finding D: Stress test χ²/ndf explanation is inconsistent with conventions (Category B)

SELECTION.md Section 5.3 states the stress test χ²/ndf = 3.29 at 3 iterations and
attributes the elevated value partially to MC-statistics correlations. However,
`conventions/unfolding.md` states that the stress test passing criterion is that
"unfolding a reweighted truth through the response recovers the reweighted truth."
Section 5.3 says the unfolded distribution "tracks the reweighted truth within ~10% in
the fit range" and states this "passes the key qualitative criterion."

A χ²/ndf of 3.29 with ndf=13 implies a p-value of roughly 0.0003 — this is not
quantitatively passing. Dismissing this as MC-statistics correlations without
quantitative support is not adequate. The stress test with a linear reweight w = 1 + 2τ
should be recoverable to better than this unless the IBU is genuinely struggling with
the reweighted shape. The self-review did not flag this.

**Required action:** Quantify the stress test χ²/ndf improvement expected from
independent-MC-halves evaluation (Phase 4a), and document why χ²/ndf = 3.29 is
acceptable before that test is run. If the answer is simply "the figure shows tracking
within ~10%," say so and note this as a known limitation for Phase 4a to verify.

### Finding E: Particle-level definition not explicitly cross-referenced in Phase 3 (Category B)

The particle-level target for the measurement is defined in STRATEGY.md Section 2.2
(stable particles with cτ > 10 mm, full 4π, ISR-exclusive). SELECTION.md does not
contain an explicit cross-reference to this definition, nor does it confirm that the
`tgenBefore` histogram in the response matrix uses this exact definition. For a
published measurement, the artifact documenting the correction procedure must state
explicitly what particle-level target it corrects to. This is missing.

**Required action:** Add a sentence in SELECTION.md Section 4.1 stating what
particle-level definition the `tgenBefore` histogram corresponds to, citing STRATEGY.md
Section 2.2. This is documentation only, requiring no code changes.

### Finding F: No τ+τ- background estimate in Phase 3 (Category B)

The strategy (Section 4.2) states that τ+τ- background is < 0.3% and will be subtracted
using MC estimates with ±50% normalization variation. SELECTION.md makes no mention of
having done any background subtraction or estimated the τ+τ- contamination in the
selected sample. Section 1.2 describes the missing-momentum cut as rejecting Z→ττ
events, but no residual contamination estimate is given.

For a publication-quality measurement, even a negligible background requires
documentation of (a) the estimate method, (b) the estimated fraction, and (c) the
decision to proceed without explicit subtraction if negligible. The strategy says
< 0.3%; Phase 3 should confirm this in the selected sample.

**Required action:** Add a brief background section (can be short) to SELECTION.md
documenting the estimated τ+τ- fraction in the final selected sample, the method used
to estimate it (MC yield comparison or literature value), and the decision to proceed
without subtraction. This is needed for the systematic budget in Phase 4a to be
justified.

---

## Summary Table

| # | Finding | Category | Status |
|---|---------|----------|--------|
| Self-1 | cos(θ_sph) figure not cited | B | Remains B; cite existing figure |
| Self-2 | Closure χ²/ndf > 1, nominal iteration justification | **A** | **Escalated from B** — must resolve in Phase 4a before Phase 4b |
| Self-3 | Per-category data/MC validation complete | Pass | Agree, with caveat (Finding A) |
| Self-4 | Condition number infinity | B | Adequately documented; fix in Phase 4a |
| A | pwflag 1–3 and 5 not validated but enter thrust sum | **A** | New finding — must resolve before Phase 4b |
| B | No quantitative τ data/MC summary in artifact | B | Add to Section 8.1 |
| C | ISR cut has no associated figure | B | Cite figure or explain flag-only nature |
| D | Stress test χ²/ndf = 3.29 dismissed without quantitative support | B | Quantify or explicitly defer |
| E | Particle-level definition not cross-referenced in Phase 3 | B | Documentation-only fix |
| F | No τ+τ- background estimate in selected sample | B | Add brief background section |

**Category A findings: 2** (Self-2 escalated; Finding A is new)
**Category B findings: 6** (4 from self-review, 2 new)

---

## Phase Gate Decision

**Phase 4a MAY BEGIN** with the following conditions:

1. The two Category A findings must be resolved **before Phase 4b (partial
   unblinding)**. Specifically:
   - Self-2: The nominal iteration choice (3 vs. 2) must be justified by an
     independent-MC-halves closure test. If 3 iterations fails that test, the nominal
     must change.
   - Finding A: The pwflag coverage of the thrust observable must be documented. If
     non-zero pwflag categories carry non-negligible thrust weight, data/MC validation
     for those categories is required.

2. The Category B findings should be addressed at the start of Phase 4a as cleanup tasks
   before the systematic evaluation begins. In particular, Finding F (background
   estimate) is needed to justify the systematic program.

3. The overall quality of Phase 3 is adequate for Phase 4a to proceed: the response
   matrix is constructed, the flat-prior test passes cleanly, the major data/MC
   discrepancies are identified, and the open issues are documented. The work is
   thorough and self-consistent within the scope covered.

---

*Independent review completed 2026-03-15.*
