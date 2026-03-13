# Critical Review: Zh → bb̄ Strategy at LEP2 with ALEPH

**Reviewer role:** Critical reviewer ("bad cop")
**Artifact under review:** `phase1_strategy/exec/STRATEGY.md`
**Review date:** 2026-03-12

---

## Overall Assessment

The strategy document describes a search for the SM Higgs boson in the Zh channel at LEP2 using ALEPH data. While it covers the main elements required by the methodology specification, it contains several serious omissions, physics errors, and unjustified choices that would cause this strategy to be rejected in a collaboration review. The most critical issues are: (1) an incomplete and incorrectly classified background enumeration that omits the dominant irreducible background WW→qqqq/qqℓν, (2) an incorrect blinding variable definition, (3) a missing major analysis channel (Zh→qqbb), and (4) fabricated or incorrect references and cross-section values.

---

## Issue List

### A-1. Missing dominant background: W⁺W⁻ production (Category A)

The background table lists only qq(γ), Zee, and single-W. This is a major omission. At LEP2 energies of 200–209 GeV, W-pair production e⁺e⁻ → W⁺W⁻ has a cross-section of approximately 17 pb — far larger than Zee or single-W. The WW → qqqq final state produces 4-jet events that are a severe background to the missing energy channel when jets are poorly measured or merged, and to the hadronic channel (see A-2). The WW → qqℓν final state is a background to the leptonic channel when the lepton is misidentified or the event topology overlaps.

In every published ALEPH Higgs search at LEP2 (e.g., ALEPH Collaboration, Phys. Lett. B 526 (2002) 191), WW is listed as one of the principal backgrounds. Its absence here is disqualifying.

**Resolution required:** Add W⁺W⁻ (fully hadronic and semileptonic) to the background enumeration with cross-section estimates, classification (reducible), and estimation method. Also add ZZ → qqbb̄ as an irreducible background (see A-3).

### A-2. Missing major analysis channel: Zh → qqbb̄ (four-jet channel) (Category A)

The strategy considers only the missing energy (Z→νν) and leptonic (Z→ℓℓ) channels. The four-jet channel, where Z→qq̄ and H→bb̄, has BR(Z→hadrons) ≈ 70% and is the dominant channel in terms of signal yield. Every published LEP Higgs search includes this channel — indeed, at ALEPH it historically provided the single strongest constraint on mH.

Omitting the four-jet channel discards approximately 70% of the signal and would make the analysis dramatically less sensitive than the published ALEPH result. The physics prompt does specify "Zh → νν̄bb̄ and Zh → ℓ⁺ℓ⁻bb̄", so the strategy is following the prompt, but the strategy document should at minimum acknowledge this limitation and its impact on expected sensitivity. If the prompt is taken as constraining the channels, the target sensitivity estimate (see B-3) must be adjusted accordingly.

**Resolution required:** Either include the four-jet channel or explicitly document that it is excluded per the physics prompt and revise all sensitivity estimates to reflect only the included channels.

### A-3. Missing irreducible background: ZZ production (Category A)

The process e⁺e⁻ → ZZ, with one Z→bb̄ and the other Z→νν/ℓℓ, is topologically identical to the signal. At √s ≈ 206 GeV the ZZ cross-section is approximately 1 pb. While small compared to WW, it is the irreducible background for this search — it produces events with exactly the signal topology and cannot be reduced by any selection except mass discrimination. This is the background that fundamentally limits the search sensitivity.

The absence of ZZ from the background table is a critical omission. Any collaboration reviewer would immediately flag this.

**Resolution required:** Add ZZ with cross-section, classify as irreducible, and discuss its role in limiting sensitivity.

### A-4. Incorrect blinding variable (Category A)

The strategy states: "Blinding variable: the visible energy distribution in events passing the full selection."

This is wrong. According to the methodology specification (Section 4), the blinding variable is "the distribution of the final discriminant variable (the variable used for statistical inference)." The strategy itself states the statistical inference is performed via a "binned maximum likelihood fit to the reconstructed dijet mass distribution." Therefore the blinding variable must be the reconstructed dijet mass (mH candidate) distribution in the signal region, not the visible energy.

Visible energy is not even the discriminant — it is a preselection variable. Blinding the wrong variable means the actual discriminant could be examined in the signal region before the background model is validated, violating the blinding protocol.

**Resolution required:** Correct the blinding variable to be the reconstructed dijet mass distribution in the signal region. Revise the blinding protocol description accordingly.

### A-5. Incorrect or fabricated signal cross-section reference (Category A)

The strategy cites "HZHA generator, Fleischer & Jegerlehner 1983" for the Zh cross-section of ~80 fb at √s = 206 GeV for mH = 115 GeV. There are multiple problems:

1. The HZHA generator was written by P. Janot and is documented in internal LEP notes from the late 1990s, not by Fleischer & Jegerlehner in 1983. The Fleischer & Jegerlehner reference is to radiative correction calculations, not to a Monte Carlo generator.
2. The cross-section value of 80 fb at √s = 206 GeV for mH = 115 GeV is too high. The SM Zh production cross-section at this energy and mass is closer to 40–50 fb before any branching ratio. At mH = 115 GeV, the Zh cross-section is significantly suppressed relative to lower masses due to phase space — √s = 206 GeV is only ~6 GeV above the Zh kinematic threshold (mZ + mH ≈ 91 + 115 = 206 GeV). The cross-section drops sharply near threshold.

**Resolution required:** Correct the reference to the actual HZHA documentation. Verify and correct the cross-section value, ideally cross-checking against published LEP Higgs working group numbers (e.g., LHWG Note 2001-04 or ALEPH 2002-019 CONF).

### A-6. Jet algorithm choice: JADE instead of Durham (Category A)

The strategy specifies the JADE algorithm for jet clustering. While JADE was used historically at LEP1, the Durham (kT) algorithm became the standard at LEP2 for Higgs searches because it has better theoretical properties (reduced sensitivity to soft radiation, better mass resolution for boosted topologies). All published ALEPH Higgs searches at LEP2 use the Durham algorithm, not JADE.

Using JADE will produce inferior dijet mass resolution and potentially different selection efficiencies than expected from the literature. This is not just a preference — it affects the physics performance and makes comparison with published results invalid.

**Resolution required:** Switch to the Durham algorithm (kT clustering) with ycut as the resolution parameter, consistent with published ALEPH analyses. Cite the relevant ALEPH publication for the algorithm choice.

### A-7. Incomplete systematic uncertainties: missing critical sources (Category A)

Several important systematic uncertainty sources are absent:

1. **Beam energy uncertainty:** At LEP2, the beam energy calibration uncertainty was significant (~20–50 MeV depending on the running period) and directly affects the kinematic reconstruction of the Higgs candidate mass. This is a leading systematic for mass-based searches.
2. **MC statistics:** The statistical uncertainty on the background prediction from finite MC sample sizes is often one of the dominant systematics at LEP2. It must be included as a bin-by-bin statistical uncertainty (Barlow-Beeston or similar).
3. **ISR modeling:** The qq(γ) background normalization depends critically on ISR modeling. A flat 2% normalization uncertainty is not adequate — shape uncertainties from ISR modeling must also be evaluated.
4. **Lepton identification efficiency:** For the leptonic channel, the lepton ID efficiency uncertainty is missing.
5. **Missing energy modeling:** For the νν channel, the modeling of missing energy (affected by cracks, dead material, beam-related backgrounds) is a critical systematic.

**Resolution required:** Add all missing systematic sources with preliminary estimates. The beam energy and MC statistics omissions are particularly serious.

### B-1. Background classification missing (Category B)

The methodology specification requires backgrounds to be classified as "irreducible, reducible, instrumental" with expected relative importance. The background table provides no such classification. The qq(γ) background is reducible (can be suppressed by b-tagging and kinematic cuts), Zee is reducible, and ZZ (once added) is irreducible. This classification matters because it determines the estimation strategy.

**Resolution required:** Add the classification column to the background table.

### B-2. No quantitative background yield estimates (Category B)

The methodology requires "quantitative estimates (cross-sections, expected yields)" with citations. The background table lists only vague relative importance ("Dominant", "Moderate", "Small") with no cross-section values, no expected yields after selection, and no citations. This makes it impossible to assess whether the analysis has adequate sensitivity or whether the signal-to-background ratio is reasonable.

**Resolution required:** Add cross-section values for all backgrounds, expected yields after preselection, and citations.

### B-3. Target sensitivity estimate is questionable (Category B)

The strategy claims an expected 95% CL upper limit of ~50 fb on σ(Zh)×BR(H→bb̄) at mH = 115 GeV. This needs scrutiny:

1. With only the νν and ℓℓ channels (combined BR ~26%), the expected sensitivity will be significantly worse than the published ALEPH result which includes the dominant qq channel.
2. At mH = 115 GeV, the Zh cross-section × BR(H→bb̄) is approximately 40 fb × 0.85 ≈ 34 fb (SM). Claiming an expected limit of 50 fb implies the analysis can nearly exclude the SM Higgs at this mass with only 26% of the signal — this seems optimistic.
3. No source or calculation method is cited for this estimate.

**Resolution required:** Provide a back-of-envelope calculation or citation supporting the sensitivity estimate, accounting for the channel selection.

### B-4. Kinematic fit description for leptonic channel is incorrect (Category B)

The strategy describes a "5C kinematic fit (constraining mℓℓ = mZ and total 4-momentum)." A constraint on mℓℓ = mZ is 1 constraint; conservation of total 4-momentum (E, px, py, pz) is 4 constraints. This gives 5C total, which is correct in counting but the description should note that equal-mass constraints or beam energy constraints are being used. More importantly, at LEP2 where ISR is significant, the 4-momentum conservation constraints must account for ISR, typically by allowing a longitudinal ISR photon — making it effectively a 4C fit. Using a naive 5C fit without ISR treatment will produce poor χ² distributions and biased mass reconstruction.

**Resolution required:** Clarify the kinematic fit constraints, describe ISR treatment, and verify the constraint count is correct for the actual implementation.

### B-5. Control region design is underdeveloped (Category B)

Only two control regions are defined: anti-b-tag and Z mass sidebands. For the missing energy channel, there is no dedicated control region. The anti-b-tag CR validates light-quark qq̄ but does not validate WW (once added) or the ISR modeling that drives the missing energy spectrum. The WW background needs its own control region — for example, events with higher jet multiplicity or inconsistent with 2-jet topology.

**Resolution required:** Design control regions that cover all major backgrounds in each channel, particularly WW.

### B-6. Validation region design is weak (Category B)

The validation region is defined only as "loosening the dijet mass cut to 80–100 GeV." This is a single region that does not test the background model in the kinematic regime most relevant to the signal. A proper validation strategy should include:
- Regions above and below the signal window in mH
- Regions with varied b-tag requirements (single b-tag)
- For the missing energy channel: regions with different missing energy ranges

**Resolution required:** Define a more comprehensive set of validation regions.

### B-7. Electron definition is incomplete (Category B)

The electron identification is described as "E/p > 0.5, identified via ECAL shower shape" but no specific shower shape variable or cut value is given. At ALEPH, the standard electron ID used the estimator from the ECAL (compactness, longitudinal profile) and the dE/dx from the TPC. The muon definition mentions HCAL hits and muon chamber match, but the minimum number of HCAL planes or the matching criterion is not specified.

**Resolution required:** Provide complete lepton identification criteria with reference to the ALEPH publication where they are defined.

### B-8. b-tagging reference and working point (Category B)

The b-tagging reference (Phys. Lett. B 401 (1997) 150) describes a LEP1 b-tagging method. At LEP2 energies, the b-tagging performance and methodology evolved significantly. The ALEPH LEP2 Higgs searches used a neural-network-based b-tagger that combined lifetime, mass, and multiplicity information from secondary vertices. The working point (efficiency, mistag rate) is not specified.

**Resolution required:** Reference the LEP2-era b-tagging algorithm and specify the working point to be used, including expected efficiency and light-quark rejection.

### C-1. Missing energy channel: acoplanarity cut not quantified (Category C)

The acoplanarity is listed as a discriminating variable but no nominal cut value or expected range is given. While exact optimization is for Phase 3, an indicative value helps assess feasibility.

### C-2. Generator version should be specified more precisely (Category C)

"PYTHIA 6.1" is specified, but the exact version matters for ISR treatment and fragmentation tuning. Published ALEPH analyses at LEP2 typically used PYTHIA 6.156 or later. Additionally, the signal process was generated with HZHA interfaced to PYTHIA for parton showering, not PYTHIA alone.

### C-3. No mention of τ channel (Category C)

The Zh → τ⁺τ⁻bb̄ channel has a non-trivial branching ratio (BR(Z→ττ) ≈ 3.4%). While more challenging experimentally than e/μ channels, some published analyses included it. It would be worth noting its exclusion and the sensitivity impact.

### C-4. Single-W background needs clarification (Category C)

The single-W process listed as "e⁺e⁻ → Weν" is more precisely a t-channel process (e⁺e⁻ → Weν via γ/Z exchange with the electron going forward). Its relevance to the Zh search is marginal and channel-dependent. Clarify which channel it affects and why it is included while WW is not.

### C-5. No discussion of two-photon backgrounds (Category C)

Two-photon processes (γγ → hadrons) can produce low-multiplicity events with missing energy. While they are typically removed by preselection, they should be mentioned and their rejection discussed, especially for the missing energy channel.

---

## Summary of Issues by Category

| Category | Count | Issues |
|----------|-------|--------|
| **(A) Must resolve** | 7 | A-1 through A-7 |
| **(B) Should address** | 8 | B-1 through B-8 |
| **(C) Suggestions** | 5 | C-1 through C-5 |

**Recommendation:** This strategy cannot proceed to Phase 2 without resolving the Category A issues. The missing WW and ZZ backgrounds (A-1, A-3), incorrect blinding variable (A-4), wrong jet algorithm (A-6), and incomplete systematics (A-7) are individually disqualifying. Collectively they indicate that the strategy was not adequately informed by the published ALEPH Higgs search literature. The revised strategy should demonstrate close engagement with ALEPH Collaboration, Phys. Lett. B 526 (2002) 191 (the actual published ALEPH Higgs search result at LEP2).
