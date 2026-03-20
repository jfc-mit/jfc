# Primary Lund Jet Plane Density — ALEPH at √s = 91.2 GeV

Type: measurement

Start a new claude instance at the reslop repo root and paste one of
the prompts below.

---

## Short prompt

````text
Scaffold and run a measurement analysis of the primary Lund jet plane
density in hadronic Z decays using archived ALEPH data at √s = 91.2 GeV.

Setup: scaffold analyses/lund_plane as a measurement, set
data_dir=/n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ in
.analysis_config, install the pixi environment, then begin orchestrating.

Observable: The 2D density of primary Cambridge/Aachen declusterings
in each thrust hemisphere, mapped to coordinates
(ln 1/Δθ, ln k_t/GeV), where Δθ is the emission angle and
k_t = E_soft sin Δθ. Use charged particles only (pwflag == 0,
highPurity == 1). One jet = one hemisphere.

Deliverables:
1. 2D density ρ(ln 1/Δθ, ln k_t) corrected to charged-particle level,
   ~10–15 × 10–15 bins
2. 1D projections (k_t spectrum, angular spectrum) with covariance
3. Number of primary declusterings vs. minimum k_t threshold
4. Comparison to PYTHIA 6 MC
5. Machine-readable results (CSV/NPY)

Key references:
- Dreyer, Salam, Soyez, JHEP 12 (2018) 064 — Lund plane proposal
- ATLAS, Phys. Rev. Lett. 124 (2020) 222002 — first measurement (pp)
- Query the LEP corpus for ALEPH jet substructure and Cambridge
  algorithm studies

Data:
- Data: /n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ALEPH/
  (LEP1Data{1992..1995}_recons_aftercut-MERGED.root, 6 files)
- MC:   /n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ALEPHMC/
  (LEP1MC1994_recons_aftercut-{001..041}.root, 41 files)

This is the first Lund plane measurement in e⁺e⁻ collisions.
````

---

## Full prompt

````text
Scaffold and run a measurement analysis of the primary Lund jet plane
density in hadronic Z decays using archived ALEPH data at √s = 91.2 GeV.

Setup: scaffold analyses/lund_plane as a measurement, set
data_dir=/n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ in
.analysis_config, install the pixi environment, then begin orchestrating.

### Observable

The Lund jet plane maps each emission in the Cambridge/Aachen (C/A)
clustering tree to coordinates (ln 1/Δθ, ln k_t). The primary plane
follows only the harder branch at each declustering step.

Adaptation to e⁺e⁻ at the Z pole:
- Cluster all charged particles in each hemisphere (defined by the
  thrust axis) using C/A with the e⁺e⁻ distance measure:
  d_ij = 2(1 − cos θ_ij)
- Decluster following the harder branch at each step
- At each declustering record (Δθ, k_t) where Δθ is the angle between
  the softer and harder prong, and k_t = E_soft sin Δθ
- Fill the 2D density ρ(ln 1/Δθ, ln k_t), normalized per jet
  (hemisphere)

Use charged particles only (pwflag == 0, highPurity == 1).

### Measurements

1. **2D density:**
   ρ(ln 1/Δθ, ln k_t/GeV) =
     (1/N_jet) d²n / d ln(1/Δθ) d ln(k_t/GeV)
   in a grid of ~10–15 × 10–15 bins:
   - ln(1/Δθ): 0 to ~5  (angles from ~π to ~0.007 rad)
   - ln(k_t/GeV): ~−2 to ~3.5  (k_t from ~0.1 to ~30 GeV)

2. **1D projections:**
   - ρ(ln k_t) integrated over angle
   - ρ(ln 1/Δθ) integrated over k_t
   - Number of primary declusterings per jet vs. minimum k_t threshold

### Correction strategy

Correct for detector effects using the PYTHIA 6/JETSET MC. Start with
2D bin-by-bin correction factors C_ij = truth_ij / reco_ij. In Phase 3,
inspect the migration matrix — if significant off-diagonal migration
exists, switch to 2D unfolding. The 1D projections can be unfolded
independently as a cross-check.

### Systematics

- Tracking efficiency: vary track quality requirements
- Charged-only effect: compare charged-particle-level to all-particle
  MC truth
- Hemisphere boundary: vary hemisphere definition (thrust axis
  variations) to quantify boundary effects
- MC model dependence: single generator — document as limitation;
  reweight fragmentation parameters to assess sensitivity
- Year-by-year stability
- Resolution thresholds: minimum k_t and Δθ cuts (resolution effects
  at small angles and low momenta)

### Reference analyses

- Dreyer, Salam, Soyez, "The Lund Jet Plane", JHEP 12 (2018) 064 —
  the proposal with analytic predictions
- ATLAS, "Measurement of the Lund Jet Plane in pp collisions at
  √s = 13 TeV", Phys. Rev. Lett. 124 (2020) 222002 — first
  measurement, methodology reference
- ALEPH, "Studies of QCD at e⁺e⁻ centre-of-mass energies between
  91 and 209 GeV", Eur. Phys. J. C35 (2004) 457 — event selection
  and detector effects baseline
- Query the LEP corpus for ALEPH jet substructure studies, Cambridge
  algorithm usage at LEP, and jet declustering analyses
  (inspire:457159, inspire:388806)

### Motivation

The Lund plane has never been measured in e⁺e⁻ collisions. The Z pole
is the cleanest environment: no UE, no MPI, no ISR contamination, exact
qq̄ initial state. The perturbative region probes α_s C_F/π; the
non-perturbative region discriminates string vs. cluster hadronization.
The single-generator correction makes this a direct test of the PYTHIA
model.

### Goals

1. 2D primary Lund plane density corrected to charged-particle level
2. 1D k_t and angular projections with full covariance
3. Comparison to PYTHIA 6 (correction MC)
4. Machine-readable results (CSV/NPY)

### Data

- Data: /n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ALEPH/
  (LEP1Data{1992..1995}_recons_aftercut-MERGED.root, 6 files)
- MC:   /n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ALEPHMC/
  (LEP1MC1994_recons_aftercut-{001..041}.root, 41 files)
````
