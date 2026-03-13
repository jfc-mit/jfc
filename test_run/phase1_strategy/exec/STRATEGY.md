# Analysis Strategy: Zh → bb̄ at LEP2 with ALEPH

## Summary

This document outlines the strategy for searching for the Standard Model Higgs
boson produced via Zh associated production at LEP2 energies (200–209 GeV),
using the ALEPH detector. Two final states are considered: the missing energy
channel (Zh → νν̄bb̄) and the leptonic channel (Zh → ℓ⁺ℓ⁻bb̄). The analysis
uses a cut-based selection followed by a binned likelihood fit to the
reconstructed Higgs candidate mass.

## Signal Process

The signal is e⁺e⁻ → Zh, where the Z decays to neutrinos or charged leptons,
and the Higgs decays to bb̄. At √s = 206 GeV, the Zh production cross-section
is approximately 80 fb for mH = 115 GeV (HZHA generator, Fleischer & Jegerlehner
1983). The bb̄ branching ratio is ~85% at this mass.

The two channels provide complementary sensitivity:
- **Missing energy channel** (Zh → νν̄bb̄): BR(Z→νν̄) ≈ 20%, large branching
  ratio but challenging missing energy signature
- **Leptonic channel** (Zh → ℓ⁺ℓ⁻bb̄): BR(Z→ℓℓ) ≈ 3.4% per lepton flavor,
  clean signature with full kinematic reconstruction

## Backgrounds

The principal backgrounds are:

| Background | Process | Relative importance | Estimation method |
|-----------|---------|-------------------|------------------|
| qq̄(γ) | e⁺e⁻ → qq̄ with ISR | Dominant | Simulation (PYTHIA) |
| Zee | e⁺e⁻ → Zee | Moderate | Simulation |
| Single W | e⁺e⁻ → Weν | Small | Simulation |

For the missing energy channel, the dominant background is qq̄ production with
hard ISR photon(s) escaping down the beampipe, mimicking missing energy. The
Zee background contributes when the electron is lost.

For the leptonic channel, the dominant background is qq̄ with fake or
non-isolated leptons.

## Dataset and Luminosity

The analysis uses ALEPH data collected at √s = 200–209 GeV during the year
2000 LEP2 run. The integrated luminosity is approximately 217 pb⁻¹.

Simulation samples are generated with PYTHIA 6.1 for all signal and background
processes, with full ALEPH detector simulation.

## Object Definitions

Physics objects follow ALEPH standard definitions:

- **Good tracks**: charged particles with ≥ 4 TPC hits, |cos θ| < 0.94,
  pT > 0.2 GeV, |d0| < 2 cm, |z0| < 20 cm
- **Good neutrals**: neutral energy flow objects with |cos θ| < 0.98,
  E > 0.4 GeV
- **Jets**: clustered using the JADE algorithm with ycut optimized per channel
- **Electrons**: good tracks with E/p > 0.5, identified via ECAL shower shape
- **Muons**: good tracks with ≥ 10 HCAL hits and muon chamber match
- **b-tagging**: lifetime-based b-tag using impact parameter significance,
  following the method described in ALEPH Collaboration, Phys. Lett. B 401
  (1997) 150

## Blinding Protocol

**Blinding variable:** the visible energy distribution in events passing
the full selection.

The signal region is defined by the reconstructed Higgs candidate mass window
100 < mH < 130 GeV. The discriminant distribution in data within this window
is not examined until the background model is validated.

Staged unblinding:
1. Validate background model in sidebands (mH < 100 GeV and mH > 130 GeV)
2. Partial unblinding with 10% of SR data
3. Full unblinding after human approval

## Event Selection Strategy

### Missing energy channel (Zh → νν̄bb̄)

Preselection:
- Number of good tracks ≥ 5
- Visible energy between 0.3√s and 0.7√s
- Missing momentum pointing away from beam (|cos θ_miss| < 0.95)
- No isolated leptons

The events are forced into 2 jets using the JADE algorithm. The b-tag
discriminant is applied to both jets.

Final selection based on:
- Acoplanarity of the dijet system
- b-tag output of both jets
- Dijet invariant mass

### Leptonic channel (Zh → ℓ⁺ℓ⁻bb̄)

Preselection:
- Exactly 2 identified isolated leptons (same flavor, opposite sign)
- Dilepton invariant mass consistent with Z: 81 < mℓℓ < 101 GeV
- Remaining tracks forced into 2 jets

Final selection based on:
- b-tag output of both jets
- Dijet invariant mass
- 5C kinematic fit χ² (constraining mℓℓ = mZ and total 4-momentum)

## Background Estimation

All backgrounds are estimated from simulation, normalized to theoretical
cross-sections and measured luminosity. No data-driven estimation is used.

Control regions:
- **Anti-b-tag CR**: events passing all selection except b-tag requirement is
  inverted. Enriched in light-quark qq̄ events. Used to validate qq̄ modeling.
- **Z sideband CR**: dilepton mass sidebands (60–81 GeV and 101–120 GeV) for
  validating lepton-related backgrounds.

Validation:
- Closure tests in validation regions formed by loosening the dijet mass cut
  to 80–100 GeV (below the signal window).

## Systematic Uncertainties

### Experimental
- Jet energy scale: 1% (ALEPH standard)
- b-tagging efficiency: from data/MC comparison of Z→bb̄ at LEP1 energies
- Luminosity: 0.5%
- Tracking efficiency: negligible

### Theoretical
- Signal cross-section: vary mH by ±1 GeV (parametric)
- Background qq̄ cross-section: 2% normalization uncertainty
- Fragmentation modeling: compare PYTHIA vs HERWIG

## Statistical Approach

A binned maximum likelihood fit to the reconstructed dijet mass distribution
in the signal region. The signal is parameterized as a function of mH. Nuisance
parameters encode systematic uncertainties as log-normal constraints (rate) or
vertical template morphing (shape).

Expected and observed upper limits on the Zh production cross-section are
computed using the CLs method with the profile likelihood ratio as the test
statistic.

## Target Sensitivity

At mH = 115 GeV with 217 pb⁻¹, the expected 95% CL upper limit on
σ(Zh) × BR(H→bb̄) is approximately 50 fb, corresponding to an expected
exclusion of the SM Higgs boson at masses below ~112 GeV.

## Quality Gate Criteria

The strategy is considered complete when:
1. All signal and background processes identified with cross-section estimates
2. Object definitions specified with references
3. Selection strategy defined for both channels
4. Blinding protocol established
5. Systematic uncertainty categories enumerated
6. Statistical method specified
