# Z Lineshape and α_s — ALEPH at √s ≈ 91.2 GeV

Type: measurement

Start a new claude instance at the reslop repo root and paste one of
the prompts below.

---

## Short prompt

````text
Scaffold and run a measurement analysis of the Z lineshape parameters
and an extraction of α_s from the hadronic-to-leptonic width ratio R_l
in hadronic and leptonic Z decays using archived ALEPH data at
√s ≈ 91.2 GeV.

Setup: scaffold analyses/zlineshape_alphas as a measurement, set
data_dir=/n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ in
.analysis_config, install the pixi environment, then begin orchestrating.

Observable: Measure the hadronic and leptonic cross sections at the
Z pole. From their ratio extract R_l = Γ_had/Γ_lep. Extract α_s(M_Z)
using the QCD correction to R_l:
R_l = R_l^EW × (1 + δ_QCD(α_s))
where δ_QCD is known to N⁴LO. Use charged particles (pwflag == 0,
highPurity == 1) for hadronic event selection; identify leptonic events
(e⁺e⁻, μ⁺μ⁻, τ⁺τ⁻) separately.

Deliverables:
1. Hadronic and leptonic event counts with selection efficiencies
2. Cross-section ratio R_l with statistical and systematic uncertainties
3. α_s(M_Z) extracted from R_l with full uncertainty propagation
4. Comparison to published ALEPH lineshape results and the LEP combined
   α_s
5. Machine-readable results

Key references:
- ALEPH, Eur. Phys. J. C14 (2000) 1 — Z lineshape and lepton
  asymmetries
- LEP EWWG, Phys. Rep. 427 (2006) 257 — combined Z-pole results
- Baikov et al., Phys. Rev. Lett. 108 (2012) 222003 — N⁴LO QCD
  corrections to R_l
- Query the LEP corpus for ALEPH Z lineshape and cross-section papers

Data:
- Data: /n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ALEPH/
  (LEP1Data{1992..1995}_recons_aftercut-MERGED.root, 6 files)
- MC:   /n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ALEPHMC/
  (LEP1MC1994_recons_aftercut-{001..041}.root, 41 files)
````

---

## Full prompt

````text
Scaffold and run a measurement analysis of the Z lineshape parameters
and an extraction of α_s from the hadronic-to-leptonic width ratio R_l
in hadronic and leptonic Z decays using archived ALEPH data at
√s ≈ 91.2 GeV.

Setup: scaffold analyses/zlineshape_alphas as a measurement, set
data_dir=/n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ in
.analysis_config, install the pixi environment, then begin orchestrating.

### Observable

The Z lineshape is parametrized by M_Z, Γ_Z, and the peak hadronic
cross section σ⁰_had. The key derived quantity is:

R_l = Γ_had / Γ_lep = σ⁰_had / σ⁰_lep

which receives QCD corrections:

R_l = R_l^EW × (1 + α_s/π + 1.41 (α_s/π)² − 12.8 (α_s/π)³ − 80.0 (α_s/π)⁴ + ...)

This relation, known to N⁴LO in perturbative QCD, allows a precise
extraction of α_s(M_Z) from the measured R_l.

If the archived data contains events from multiple √s points (the
LEP1 energy scan), perform a lineshape fit to extract M_Z, Γ_Z, and
σ⁰_had directly. If only Z-peak data is available, measure R_l at the
peak and extract α_s from it.

### Measurements

1. **Event classification:** Classify events as:
   - Hadronic (Z → qq̄): high charged-track multiplicity (N_ch ≥ 5),
     large visible energy (E_vis > 0.5√s)
   - e⁺e⁻: two back-to-back electromagnetic clusters, low multiplicity
   - μ⁺μ⁻: two back-to-back tracks with MIP signature
   - τ⁺τ⁻: low-multiplicity, narrow jets, missing energy
   Use charged particles (pwflag == 0, highPurity == 1) and apply
   standard ALEPH hadronic event selection.

2. **Cross sections:** Measure σ_had and σ_lep (per lepton species)
   at each available √s point, corrected for selection efficiency,
   acceptance, and luminosity (or use the ratio to cancel luminosity).

3. **R_l extraction:** Form the ratio R_l = N_had ε_lep / (N_lep ε_had)
   where ε are the selection efficiencies estimated from MC. The
   luminosity cancels in the ratio.

4. **α_s extraction:** Extract α_s(M_Z) from R_l using the N⁴LO
   perturbative relation, accounting for:
   - Electroweak corrections (parametric via M_Z, m_t, m_H)
   - Non-perturbative corrections (negligible at this precision)
   - Quark mass effects (m_b, m_c threshold corrections)

5. **Lineshape fit (if scan data available):** Fit the hadronic
   cross section vs. √s to the Breit-Wigner form including
   initial-state radiation:
   σ_had(s) ∝ s Γ_Z² / [(s − M_Z²)² + s² Γ_Z²/M_Z²]
   convolved with the ISR radiator function. Extract M_Z, Γ_Z,
   σ⁰_had.

### Correction strategy

The primary observable is a counting ratio — corrections are:
- Selection efficiency for hadronic and leptonic events from MC
- Feed-through between channels (τ→hadrons misidentified as qq̄,
  two-photon background, cosmic rays)
- ISR corrections to the cross section (analytically from QED)

The double ratio R_l cancels many common systematics (luminosity,
trigger). The MC is used only for efficiency and feed-through
estimation.

### Systematics

- Hadronic event selection: vary N_ch and E_vis/√s cuts; the largest
  effect is the low-multiplicity boundary where τ⁺τ⁻ contaminates
- Lepton identification: vary e/μ/τ selection criteria; estimate
  cross-contamination between channels
- Two-photon and beam-gas backgrounds: estimate from low-E_vis
  sidebands and MC
- τ contamination in hadronic sample: τ⁺τ⁻ events with hadronic
  τ decays can pass hadronic selection — estimate and subtract
- MC modelling of selection efficiency: vary fragmentation parameters,
  compare efficiency stability
- Luminosity (if absolute cross sections needed): not needed for R_l
- Year-by-year stability across 1992–1995 data
- Beam energy uncertainty (if lineshape fit): propagates into M_Z, Γ_Z
- Theory uncertainty on α_s extraction: N⁴LO truncation, parametric
  (m_t, m_H, M_Z), quark mass corrections

### Reference analyses

- ALEPH, "Measurement of the Z resonance parameters at LEP",
  Eur. Phys. J. C14 (2000) 1 — the definitive ALEPH lineshape
  paper; primary validation target
- LEP EWWG, "Precision electroweak measurements on the Z resonance",
  Phys. Rep. 427 (2006) 257 — combined LEP results:
  R_l = 20.767 ± 0.025, α_s(M_Z) = 0.1226 ± 0.0038 (from R_l)
- Baikov, Chetyrkin, Kühn, Rittinger, "Complete O(α_s⁴) QCD
  corrections to hadronic Z decays", Phys. Rev. Lett. 108 (2012)
  222003 — N⁴LO perturbative coefficients
- d'Enterria et al., "α_s(M_Z) determination from the Z-boson
  width", Eur. Phys. J. C85 (2025) — modern α_s extraction from
  electroweak precision data
- PDG α_s world average: α_s(M_Z) = 0.1180 ± 0.0009
- Query the LEP corpus for ALEPH Z lineshape, cross-section, and
  R_l papers (inspire:524404, inspire:271sergei)

### Motivation

The extraction of α_s from R_l is theoretically among the cleanest
determinations: it uses a fully inclusive observable (total hadronic
width) that avoids hadronization uncertainties, and the perturbative
series is known to N⁴LO with excellent convergence. The LEP combined
R_l gives α_s(M_Z) = 0.1226 ± 0.0038, limited by experimental
precision. Reanalysis of the full ALEPH archived dataset (potentially
with improved event classification) provides a cross-check of the
original measurement and a testbed for the full analysis chain from
raw events to a precision SM parameter.

The measurement is also pedagogically important: it is the simplest
complete measurement (counting events), yet connects directly to
fundamental parameters of the Standard Model.

### Goals

1. Hadronic and leptonic event counts with selection efficiencies
   and purities
2. R_l = Γ_had/Γ_lep with full uncertainty breakdown
3. α_s(M_Z) from R_l with statistical, systematic, and theoretical
   uncertainties separated
4. Lineshape parameters (M_Z, Γ_Z, σ⁰_had) if scan data available
5. Comparison to published ALEPH results and LEP combination
6. Machine-readable results

### Data

- Data: /n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ALEPH/
  (LEP1Data{1992..1995}_recons_aftercut-MERGED.root, 6 files)
- MC:   /n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ALEPHMC/
  (LEP1MC1994_recons_aftercut-{001..041}.root, 41 files)
````
