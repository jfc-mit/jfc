# Experiment Log

## Phase 1: Strategy

### 2026-03-15 — Strategy Development

**Corpus searches performed:**
- Thrust distribution and alpha_s extraction at LEP (ALEPH + DELPHI)
- Hadronic event selection criteria for ALEPH
- Systematic uncertainties for event shape measurements
- Archived ALEPH data samples and MC configurations
- Detector performance (tracking, calorimetry)
- Alpha_s extraction methods (NLO, resummed predictions)

**Key reference analyses identified:**
1. LEP QCD working group combination (hep-ex/0411006): Combined alpha_s from event shapes using all four LEP experiments. Result at Z pole: alpha_s(M_Z) = 0.1202 +/- 0.0003(stat) +/- 0.0007(exp) +/- 0.0012(hadr) +/- 0.0048(theo). Hadronization assessed using Pythia, Herwig, Ariadne.
2. DELPHI oriented event shapes (inspire:1661561): 1.4M events from 1994, 18 event shape distributions vs. thrust axis polar angle. Detailed systematic program including JETSET/Ariadne/Herwig comparison, Q0 variation, scale optimization.
3. Archived ALEPH QGP search (inspire:1793969): Uses the same archived dataset we have. Validated thrust distribution against published ALEPH results. Track selection: >= 4 TPC hits, |d0| < 2 cm, |z0| < 10 cm, |cos(theta)| < 0.95. Event selection: >= 5 charged tracks, E_ch > 15 GeV, >= 13 total tracks, |cos(theta_sph)| < 0.82.

**Material decisions:**
- Observable: Thrust tau = 1 - T, normalized distribution (1/N) dN/dtau
- Particle-level definition: All stable particles (c*tau > 10 mm) excluding neutrinos, full 4pi, ISR-exclusive
- Primary unfolding method: Iterative Bayesian unfolding (IBU)
- Alternative method: Bin-by-bin correction factors (cross-check)
- Response matrix MC: Pythia 6.1 reconstructed (40 files available)
- Hadronization systematic: Pythia 6.1 vs. Herwig 7 via particle-level reweighting (no alternative full-sim available)
- Alpha_s extraction: chi2 fit of O(alpha_s^2) + NLLA predictions to corrected distribution, fit range ~0.05 < tau < 0.30

**Data inventory:**
- Data: 6 files spanning 1992-1995, located at /n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ALEPH/
- MC: 40 Pythia 6.1 reconstructed files, located at /n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ALEPHMC/
- Files are post-baseline-selection ("aftercut"). Exact applied cuts to be verified in Phase 2.

**Conventions check:**
- Read conventions/unfolding.md in full
- All required systematic sources enumerated in strategy with "Will implement" or justification
- No sources omitted silently
- Measurement is normalized shape -> normalization-only systematics excluded (documented)

**Open questions for Phase 2:**
- What cuts have already been applied in the "aftercut" files?
- What tree structure and branch names are in the ROOT files?
- How many events per data year and in MC?
- Is generator-level truth information stored in the MC files (needed for response matrix)?
- What is the MC/data agreement quality for input kinematic variables?
