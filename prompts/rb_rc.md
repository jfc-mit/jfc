# R_b and R_c — ALEPH at √s = 91.2 GeV

Type: measurement

Start a new claude instance at the reslop repo root and paste one of
the prompts below.

---

## Short prompt

````text
Scaffold and run a measurement analysis of the partial width ratios
R_b = Γ(Z→bb̄)/Γ(Z→hadrons) and R_c = Γ(Z→cc̄)/Γ(Z→hadrons)
in hadronic Z decays using archived ALEPH data at √s = 91.2 GeV.

Setup: scaffold analyses/rb_rc as a measurement, set
data_dir=/n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ in
.analysis_config, install the pixi environment, then begin orchestrating.

Observable: R_b and R_c are the fractions of hadronic Z decays to
bb̄ and cc̄ respectively. Tag b and c events using lifetime-based
methods: signed impact parameter significance of charged tracks
(pwflag == 0, highPurity == 1) relative to the primary vertex, and/or
secondary vertex reconstruction. Use a double-tag method to reduce
dependence on MC tagging efficiency.

Deliverables:
1. R_b and R_c with statistical and systematic uncertainties
2. b-tagging and c-tagging performance (efficiency, purity, mistag
   rates) validated against MC
3. Double-tag consistency checks
4. Comparison to published ALEPH R_b/R_c values and the SM prediction
5. Machine-readable results

Key references:
- ALEPH, Phys. Lett. B401 (1997) 150 — R_b measurement
- ALEPH, Eur. Phys. J. C62 (2009) 1 — heavy flavour electroweak review
- LEP/SLD EWWG combination — R_b = 0.21629±0.00066, R_c = 0.1721±0.0030
- Query the LEP corpus for ALEPH heavy flavour and R_b/R_c papers

Data:
- Data: /n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ALEPH/
  (LEP1Data{1992..1995}_recons_aftercut-MERGED.root, 6 files)
- MC:   /n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ALEPHMC/
  (LEP1MC1994_recons_aftercut-{001..041}.root, 41 files)
````

---

## Full prompt

````text
Scaffold and run a measurement analysis of the partial width ratios
R_b = Γ(Z→bb̄)/Γ(Z→hadrons) and R_c = Γ(Z→cc̄)/Γ(Z→hadrons)
in hadronic Z decays using archived ALEPH data at √s = 91.2 GeV.

Setup: scaffold analyses/rb_rc as a measurement, set
data_dir=/n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ in
.analysis_config, install the pixi environment, then begin orchestrating.

### Observable

R_b and R_c are the ratios of partial widths:

R_b = Γ(Z → bb̄) / Γ(Z → hadrons)
R_c = Γ(Z → cc̄) / Γ(Z → hadrons)

These are measured by tagging b- and c-quark events using the long
lifetimes of B and D hadrons. The primary method uses the signed impact
parameter significance S = d₀/σ(d₀) of charged tracks with respect to
the reconstructed primary vertex, where d₀ is the transverse impact
parameter and σ(d₀) its uncertainty.

Use charged particles only (pwflag == 0, highPurity == 1).

### Measurements

1. **b-tagging:** For each hemisphere (defined by the thrust axis),
   count tracks with signed impact parameter significance S above a
   threshold (e.g., S > 3). The number of significant tracks N_sig
   per hemisphere discriminates b from c and light flavours due to
   the longer B-hadron lifetime and higher track multiplicity.

2. **Double-tag method for R_b:** Count single-tagged (N_s) and
   double-tagged (N_d) events. Then:
   R_b = N_s² / (4 N_d N_had)  (to first approximation)
   with correlation corrections. This extracts R_b with reduced
   dependence on the absolute tagging efficiency.

3. **R_c extraction:** Use a discriminant that separates c from b
   and light flavours — e.g., a looser lifetime tag combined with
   kinematic properties of the secondary vertex (vertex mass, track
   multiplicity). Alternatively, use the charm fraction from a
   fit to the impact parameter or secondary vertex mass distribution.

4. **Flavour composition fit:** Fit the N_sig distribution in data
   to MC templates for b, c, and uds hemispheres to extract all
   three fractions simultaneously.

### Correction strategy

The double-tag method is largely self-calibrating for R_b — the MC
enters primarily through hemisphere correlations and the charm/light
contamination fractions. For R_c, MC templates are needed for the
discriminant shapes. Validate MC modelling of:
- Impact parameter resolution (compare d₀ distributions in data/MC)
- B/D hadron lifetimes and decay multiplicities
- Gluon splitting g→bb̄ and g→cc̄ rates

### Systematics

- Impact parameter resolution: compare d₀ distributions in data vs MC;
  apply resolution smearing corrections if needed
- Hemisphere correlations: the double-tag formula assumes independent
  hemispheres — correct for QCD correlations (hard gluon radiation,
  g→bb̄) using MC, and vary the correlation within uncertainties
- Charm contamination in b-tag: uncertainty on R_c feeds into R_b
  (and vice versa) — extract simultaneously or propagate
- Gluon splitting rates: g→bb̄ and g→cc̄ fractions affect the
  flavour composition — vary within measured uncertainties
- MC model dependence: single generator limitation — reweight
  B-hadron fragmentation function (Peterson vs Bowler-Lund), vary
  B/D lifetimes and branching ratios
- Track quality cut variations
- Year-by-year stability
- Primary vertex resolution: vary vertex finding and refit

### Reference analyses

- ALEPH, "A measurement of R_b using a lifetime-mass tag",
  Phys. Lett. B401 (1997) 150 — primary methodology reference
- ALEPH, "Heavy quark tagging with leptons" and "A precise
  measurement of Γ(Z→bb̄)/Γ(Z→hadrons)", Phys. Lett. B313 (1993) 549
- LEP/SLD Heavy Flavour EWWG, "Precision electroweak measurements
  on the Z resonance", Phys. Rep. 427 (2006) 257 — combined results
  and methodology overview
- SM predictions: R_b = 0.21578, R_c = 0.17221 (ZFITTER/EW library)
- Query the LEP corpus for ALEPH R_b, R_c, heavy flavour tagging,
  and lifetime tag papers

### Motivation

R_b was historically one of the most important LEP measurements due
to its sensitivity to the top quark mass (via Z→bb̄ vertex
corrections) and to new physics in the Zbb̄ vertex. The 1990s R_b
"crisis" (measurement 3σ above SM) drove major detector and analysis
improvements before converging with the SM. Reanalysis with the full
archived dataset, modern track reconstruction, and a double-tag
approach provides a valuable cross-check and a demonstration of
heavy-flavour techniques with archival data. R_c is complementary
and sensitive to different systematic effects.

### Goals

1. R_b and R_c with full uncertainty breakdown (statistical,
   systematic by source)
2. b-tag and c-tag working points with efficiency/purity curves
3. Double-tag consistency checks and hemisphere correlation
   measurement
4. Comparison to published ALEPH values and SM predictions
5. Machine-readable results

### Data

- Data: /n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ALEPH/
  (LEP1Data{1992..1995}_recons_aftercut-MERGED.root, 6 files)
- MC:   /n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ALEPHMC/
  (LEP1MC1994_recons_aftercut-{001..041}.root, 41 files)
````
