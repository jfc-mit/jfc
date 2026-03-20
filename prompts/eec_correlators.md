# Projected Energy-Energy Correlators — ALEPH at √s = 91.2 GeV

Type: measurement

Start a new claude instance at the reslop repo root and paste one of
the prompts below.

---

## Short prompt

````text
Scaffold and run a measurement analysis of the projected two-point
energy-energy correlator (EEC) and its asymmetry (AEEC) in hadronic
Z decays using archived ALEPH data at √s = 91.2 GeV.

Setup: scaffold analyses/eec_correlators as a measurement, set
data_dir=/n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ in
.analysis_config, install the pixi environment, then begin orchestrating.

Observable: The energy-weighted angular correlation function
EEC(χ) = (1/N_evt) Σ (E_i E_j / E_vis²) δ(χ_ij − χ)
summed over all charged-particle pairs per event. The asymmetry is
AEEC(χ) = EEC(π−χ) − EEC(χ). Use charged particles only
(pwflag == 0, highPurity == 1).

Deliverables:
1. EEC(χ) in ~50 uniform bins from 0 to π, corrected to
   charged-particle level
2. AEEC(χ) with full systematic uncertainties
3. Collinear limit: re-bin small angles with log spacing in
   R_L = χ from ~0.02 to ~1
4. Full bin-to-bin covariance matrix (stat + syst)
5. Comparison to published ALEPH EEC as validation
6. Machine-readable results for theory comparison

Key references:
- ALEPH EEC (CERN-PPE/92-113, inspire:322679 or 232620) — original
- Query the LEP corpus for ALEPH QCD studies with EEC results

Data:
- Data: /n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ALEPH/
  (LEP1Data{1992..1995}_recons_aftercut-MERGED.root, 6 files)
- MC:   /n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ALEPHMC/
  (LEP1MC1994_recons_aftercut-{001..041}.root, 41 files)
````

---

## Full prompt

````text
Scaffold and run a measurement analysis of the projected two-point
energy-energy correlator (EEC) and its asymmetry (AEEC) in hadronic
Z decays using archived ALEPH data at √s = 91.2 GeV.

Setup: scaffold analyses/eec_correlators as a measurement, set
data_dir=/n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ in
.analysis_config, install the pixi environment, then begin orchestrating.

### Observable

The energy-energy correlator is the energy-weighted angular correlation
function:

EEC(χ) = (1/σ_had) dΣ/d cos χ
       = (1/N_evt) Σ_events Σ_{i,j} (E_i E_j / E_vis²) δ(cos χ_ij − cos χ)

where the sum runs over all charged-particle pairs in each event,
E_i, E_j are particle energies, and χ_ij is the opening angle between
particles i and j. The asymmetry is AEEC(χ) = EEC(π−χ) − EEC(χ).

Use only charged particles (pwflag == 0, highPurity == 1). The visible
energy E_vis is the sum of all charged particle energies in the event.

### Measurements

1. **EEC(χ):** Full two-point correlator from 0 to π, ~50 uniform bins
   in χ, corrected to charged-particle level
2. **AEEC(χ):** The asymmetry for χ ∈ (0, π/2), sensitive to α_s with
   reduced hadronization corrections
3. **Collinear limit:** Re-bin the small-angle region using R_L = χ
   with logarithmic binning from R_L ~ 0.02 to R_L ~ 1. Probes the
   transition from perturbative scaling (EEC ~ R_L⁻¹) to the
   non-perturbative regime.

### Correction strategy

Correct for detector effects using the PYTHIA 6/JETSET MC. Use either
bin-by-bin correction factors (if the response is diagonal) or
iterative Bayesian unfolding (if significant bin migration in the
angular variable). The choice should be justified in Phase 3 from the
migration matrix. The thrust analysis unfolding infrastructure may be
reusable.

### Systematics

- Tracking efficiency and fake rate: vary track quality cuts
- Charged-only vs. all-particle: MC-level comparison
- MC model dependence: single generator limitation — document, use
  reweighting to assess sensitivity
- Event selection variations
- Year-by-year stability (data spans 1992–1995, MC is 1994 only)

### Reference analyses

- ALEPH EEC (CERN-PPE/92-113) — the original measurement with ~186k
  events; primary validation target
- SLD, "Measurement of α_s from the EEC" — independent e⁺e⁻ at Z pole
- OPAL, "Energy correlations in e⁺e⁻ → hadrons" — LEP comparison
- CMS EEC in pp — modern methodology reference
- Query the LEP corpus for the original ALEPH EEC paper
  (inspire:322679 or 232620) and ALEPH QCD studies with EEC results
  (Eur. Phys. J. C35 (2004) 457)

### Motivation

The EEC has undergone a theoretical renaissance: N³LO fixed-order and
NNLL resummed predictions now exist. The original ALEPH measurement
used ~186k events; the full archived dataset has ~3M hadronic Z decays.
A modern measurement using the projected correlator framework, compared
to N³LO+NNLL theory, would be the most precise e⁺e⁻ EEC and would
provide a competitive α_s extraction in a theoretically clean
environment. The collinear limit probes the perturbative-to-
non-perturbative transition, studied theoretically but never measured
with modern precision.

### Goals

1. EEC(χ) over full angular range with ~50 bins
2. AEEC(χ) with full systematic uncertainties
3. Full bin-to-bin covariance matrix (stat + syst)
4. Comparison to published ALEPH EEC as primary validation
5. Machine-readable results for N³LO+NNLL theory comparison

### Data

- Data: /n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ALEPH/
  (LEP1Data{1992..1995}_recons_aftercut-MERGED.root, 6 files)
- MC:   /n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ALEPHMC/
  (LEP1MC1994_recons_aftercut-{001..041}.root, 41 files)
````
