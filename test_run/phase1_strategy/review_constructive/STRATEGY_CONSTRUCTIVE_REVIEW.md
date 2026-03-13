# Constructive Review: Zh → bb̄ Strategy at LEP2 with ALEPH

**Reviewer role:** Constructive reviewer (good cop)
**Artifact reviewed:** `spec/test_run/phase1_strategy/exec/STRATEGY.md`
**Date:** 2026-03-12

---

## Overall Assessment

This is a solid strategy document that correctly identifies the signal process, the two most important final states, and the principal backgrounds. The choice of a cut-based analysis with a binned likelihood fit to the dijet mass is well-motivated for this dataset and channel. The document is largely self-contained, and a physicist picking it up cold could understand the analysis approach.

The issues below are aimed at strengthening the strategy before execution begins. Most are clarifications or additions that would make the document more robust under collaboration-level scrutiny.

---

## Category A — Must Resolve

### A1. Missing background: WW → qqqq and WW → qqℓν

The WW pair-production background is absent from the background table entirely. At √s ~ 206 GeV the WW cross-section is approximately 17 pb — large compared to the signal. For the missing energy channel, WW → qqτν (where the tau decays hadronically and the neutrino carries missing energy) is a non-trivial background. For the leptonic channel, WW → qqℓν can mimic the signal when combined with a fake second lepton. WW should be listed with its estimation method and expected yield.

### A2. Missing background: ZZ → bbνν and ZZ → bbℓℓ

The ZZ process is the irreducible background to this search — it produces the identical final state as the signal. ZZ → bbνν and ZZ → bbℓℓ are topologically indistinguishable from Zh except via the dijet mass distribution. The ZZ cross-section at 206 GeV is ~1 pb, small but not negligible, and it peaks at mZ in the dijet mass, providing separation from the signal. This must be listed explicitly as it will be a key component of the likelihood fit.

### A3. Blinding variable is inconsistent with discriminant

The blinding protocol states the blinding variable is "the visible energy distribution in events passing the full selection," but the statistical approach section states the fit is performed on "the reconstructed dijet mass distribution in the signal region." These are different distributions. Per the methodology spec (Section 4), the blinded quantity should be the final discriminant — which is the dijet mass. The blinding section should be corrected to state that the dijet mass distribution in the signal region is the blinded quantity.

---

## Category B — Should Address

### B1. Zh → qqbb̄ channel not discussed

The hadronic channel Zh → qqbb̄ has the largest branching ratio (BR(Z→qq) ≈ 70%) but is omitted without discussion. This is likely a deliberate choice given the enormous QCD background, but the strategy should state this explicitly and briefly justify the omission. A sentence noting the overwhelming qq̄ background and the lack of a clean kinematic handle would suffice. Without this, a reviewer will ask.

### B2. Jet algorithm choice — JADE vs Durham

The strategy specifies the JADE algorithm for jet clustering. ALEPH's published Higgs searches (e.g., ALEPH Collaboration, Phys. Lett. B 526 (2002) 191) used the Durham (kT) algorithm, which has better theoretical properties and was the LEP-era standard for e+e- analyses. The JADE algorithm is known to have issues with soft-gluon sensitivity. If JADE is chosen deliberately, the rationale should be stated. Otherwise, Durham should be adopted to align with established ALEPH practice.

### B3. Kinematic fit description is incomplete for the missing energy channel

The strategy describes a 5C kinematic fit for the leptonic channel (constraining dilepton mass and total 4-momentum), which is appropriate. However, no kinematic fit is mentioned for the missing energy channel. A fit constraining the recoil mass to mZ would significantly improve the dijet mass resolution in the νν̄bb̄ channel. If this is intentionally omitted, the reasoning should be documented.

### B4. b-tagging working point not specified

The strategy references "lifetime-based b-tag using impact parameter significance" and cites a 1997 ALEPH publication, but does not specify the working point (efficiency/mistag rate) to be used. Different working points will significantly affect the signal-to-background ratio. The strategy should state the target b-tagging efficiency (e.g., ~80% per jet for a ~1% light-quark mistag rate, or tighter/looser) and note that this will be optimized during the selection phase.

### B5. Cross-section reference needs updating

The signal cross-section is cited as "approximately 80 fb for mH = 115 GeV (HZHA generator, Fleischer & Jegerlehner 1983)." The HZHA generator was indeed used at LEP, but the 1983 reference predates LEP by nearly a decade and refers to the original cross-section calculation, not the generator itself. The strategy should cite the HZHA generator documentation (P. Janot, Physics at LEP2, CERN 96-01, Vol. 2) and/or the cross-section values tabulated in the LEP Higgs Working Group reports for precision.

### B6. Control region strategy could be more specific

The anti-b-tag CR and Z sideband CR are described, but there is no CR proposed for WW or ZZ backgrounds (once those are added per A1/A2). The strategy should outline how WW-enriched and ZZ-enriched regions will be constructed — for example, selecting events with different-flavor leptons (for WW) or using the dilepton mass in the Z peak with anti-b-tag (for light-flavor ZZ).

### B7. Systematic uncertainty on b-tagging needs more detail

The b-tagging efficiency uncertainty is described as coming from "data/MC comparison of Z→bb̄ at LEP1 energies" but no magnitude is quoted. This is typically one of the largest experimental systematics in a Zh→bb analysis. An order-of-magnitude estimate (e.g., 2-5% per jet) would help scope the expected sensitivity.

---

## Category C — Suggestions

### C1. Target sensitivity estimate could show more detail

The target sensitivity section states an expected limit of ~50 fb and exclusion below ~112 GeV but does not show how these numbers were obtained. Even a back-of-envelope calculation (expected signal events, expected background, approximate CLs limit) would make this section more convincing and help catch errors early.

### C2. Preselection could reference expected efficiencies

The preselection cuts are listed but without expected signal or background efficiencies. Even approximate numbers (e.g., "the visible energy cut retains ~90% of signal while rejecting ~60% of qq̄ background") would help a reviewer assess whether the preselection is reasonable before the exploration phase.

### C3. Simulation generator versions should be pinned

The strategy mentions "PYTHIA 6.1" for simulation but does not specify a patch version. It also mentions comparing PYTHIA vs HERWIG for fragmentation systematics — the HERWIG version should be specified. During execution, the agent should verify which generator versions are actually available in the simulation samples.

### C4. Missing energy channel — photon veto

For the missing energy channel, events with hard ISR photons escaping down the beampipe are noted as the dominant background. The strategy should mention whether an explicit photon veto (in the ECAL endcaps or LCAL/SICAL) will be applied as part of the selection, or whether the missing momentum direction cut (|cos θ_miss| < 0.95) is considered sufficient.

### C5. Document structure could match methodology template

The methodology spec (Section 5) suggests a standard artifact structure: Summary, Method, Results, Validation, Open Issues, Code Reference. The strategy document uses a different structure. While the content is adequate, aligning with the template would make cross-referencing easier in later phases.

---

## Summary of Findings

| Category | Count | Items |
|----------|-------|-------|
| A (Must resolve) | 3 | A1 (WW background), A2 (ZZ background), A3 (blinding variable) |
| B (Should address) | 7 | B1–B7 |
| C (Suggestions) | 5 | C1–C5 |

The three Category A issues are all straightforward to fix: adding WW and ZZ to the background table, and correcting the blinding variable. None require a fundamental rethinking of the analysis approach. Once these are resolved, this strategy provides a sound foundation for the exploration phase.
