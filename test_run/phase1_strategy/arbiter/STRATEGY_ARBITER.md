# Arbiter Assessment: Zh → bb̄ Strategy at LEP2 with ALEPH

**Role:** Arbiter
**Artifact under review:** `phase1_strategy/exec/STRATEGY.md`
**Reviews considered:**
- Critical review: `phase1_strategy/review_critical/STRATEGY_CRITICAL_REVIEW.md`
- Constructive review: `phase1_strategy/review_constructive/STRATEGY_CONSTRUCTIVE_REVIEW.md`
**Date:** 2026-03-12

---

## Procedure

For each issue raised by either reviewer, I assess whether the classification is correct and whether it requires resolution before the strategy can advance. Where both reviewers agree, I accept the classification unless I find reason to override. Where they disagree, I provide independent justification. I also check for issues missed by both reviewers.

---

## Consolidated Issue Assessment

### Issues where both reviewers agree

**Issue: Missing WW background (Critical A-1, Constructive A1) — ACCEPTED as Category A**

Both reviewers independently identified the absence of W+W- pair production from the background table. At ~17 pb at LEP2 energies, WW is a major background in both analysis channels. Its omission is unambiguously disqualifying. The strategy must add WW with cross-section, final states relevant to each channel, classification (reducible), and estimation method.

**Issue: Missing ZZ background (Critical A-3, Constructive A2) — ACCEPTED as Category A**

Both reviewers flag the absence of ZZ production. ZZ is the irreducible background to this search — ZZ → bbνν and ZZ → bbℓℓ are topologically identical to the signal. Though the cross-section is small (~1 pb), it is the background that fundamentally limits sensitivity and must appear in the likelihood fit. Its omission is a critical gap.

**Issue: Incorrect blinding variable (Critical A-4, Constructive A3) — ACCEPTED as Category A**

Both reviewers agree the blinding variable is stated as "visible energy distribution" when the methodology spec (Section 4) requires blinding of the final discriminant — which the strategy itself identifies as the reconstructed dijet mass. This is an internal inconsistency and a violation of the methodology. Must be corrected.

### Issues raised by the critical reviewer only

**Issue: Missing Zh → qqbb̄ channel (Critical A-2) — RECLASSIFIED to Category B**

The critical reviewer flags the omission of the four-jet channel (Z → qq̄, H → bb̄), which carries ~70% of the signal yield. However, the physics prompt explicitly constrains the analysis to "Zh → νν̄bb̄ and Zh → ℓ⁺ℓ⁻bb̄." The strategy is following its input specification. That said, the constructive reviewer (B1) correctly notes that the omission should be acknowledged with a brief justification, and the sensitivity estimates must reflect only the included channels. I classify this as Category B: the strategy must document the exclusion and adjust sensitivity estimates, but it is not a physics error.

**Issue: Incorrect signal cross-section reference (Critical A-5) — ACCEPTED as Category A**

The attribution of the HZHA generator to "Fleischer & Jegerlehner 1983" is incorrect — HZHA was written by P. Janot and documented in CERN 96-01. Additionally, the cross-section value of ~80 fb at √s = 206 GeV for mH = 115 GeV needs verification: at this energy, mZ + mH ≈ 206 GeV places the process near the kinematic threshold where the cross-section is sharply suppressed. An incorrect cross-section propagates into sensitivity estimates and background-to-signal ratios. This must be corrected with proper references.

**Issue: JADE vs Durham jet algorithm (Critical A-6) — RECLASSIFIED to Category A (confirmed)**

The critical reviewer classifies this as Category A. The constructive reviewer raises it as B2, suggesting it could remain if deliberately justified. I side with Category A. The Durham (kT) algorithm was the established standard for all published ALEPH Higgs searches at LEP2 (e.g., Phys. Lett. B 526 (2002) 191). Using JADE without justification is not merely a suboptimal choice — it produces materially different jet clustering behavior (worse mass resolution, soft-gluon sensitivity) and makes validation against published results impossible. The strategy must adopt Durham or provide an explicit, physics-motivated justification for JADE.

**Issue: Incomplete systematic uncertainties (Critical A-7) — ACCEPTED as Category A**

The critical reviewer identifies several missing systematic sources: beam energy uncertainty, MC statistics (Barlow-Beeston), ISR modeling shape effects, lepton ID efficiency, and missing energy modeling. The constructive reviewer partially echoes this (B7: b-tagging uncertainty magnitude missing). I agree with Category A. While the strategy need not provide final uncertainty values at this stage, the *enumeration* of systematic categories is a Phase 1 deliverable per the methodology spec. Beam energy and MC statistics are standard and well-known sources — their absence suggests the enumeration was not adequately informed by the literature. The strategy must add all major systematic categories with at least order-of-magnitude estimates.

### Issues raised by the constructive reviewer only

**Issue: Kinematic fit for missing energy channel (Constructive B3) — ACCEPTED as Category B**

The constructive reviewer notes that no kinematic fit is mentioned for the νν̄bb̄ channel (a recoil-mass constraint to mZ would improve resolution). This is a valid observation. Category B is appropriate — the strategy should address whether a kinematic fit will be used in the missing energy channel.

**Issue: b-tagging working point (Constructive B4, Critical B-8) — ACCEPTED as Category B**

Both reviewers note the b-tag working point is unspecified. The critical reviewer additionally notes the reference is to a LEP1-era method. Category B is appropriate: the working point and LEP2-era algorithm should be specified.

### Additional Category B issues (agreed by both or individually valid)

| Issue | Source | Category | Assessment |
|-------|--------|----------|------------|
| Background classification missing | Critical B-1 | B | Methodology requires irreducible/reducible/instrumental classification. Must add. |
| No quantitative background yields | Critical B-2 | B | Methodology requires cross-sections and expected yields with citations. Must add. |
| Target sensitivity questionable | Critical B-3, Constructive C1 | B | Must provide back-of-envelope calculation, especially given channel restriction. |
| Kinematic fit ISR treatment | Critical B-4 | B | 5C fit description must address ISR; likely a 4C fit in practice. |
| Control region design underdeveloped | Critical B-5, Constructive B6 | B | Need CRs for WW/ZZ once those backgrounds are added. |
| Validation region design weak | Critical B-6 | B | Should define multiple VRs testing different aspects. |
| Electron/muon ID incomplete | Critical B-7 | B | Provide full criteria or cite ALEPH publication. |
| Cross-section reference update | Constructive B5 | B | Subsumed by A-5 resolution. |

### Category C issues (accepted as suggestions)

| Issue | Source | Notes |
|-------|--------|-------|
| Acoplanarity cut not quantified | Critical C-1 | Indicative value helpful but not required at strategy phase. |
| Generator version pinning | Critical C-2, Constructive C3 | Exact version matters for reproducibility. |
| Tau channel not discussed | Critical C-3 | Brief mention of exclusion would be useful. |
| Single-W clarification | Critical C-4 | Clarify channel relevance. |
| Two-photon backgrounds | Critical C-5 | Worth mentioning for completeness. |
| Preselection efficiencies | Constructive C2 | Helpful but not required at strategy phase. |
| Photon veto for νν channel | Constructive C4 | Good operational detail for Phase 2/3. |
| Document structure alignment | Constructive C5 | Minor formatting concern. |

---

## Issues missed by both reviewers

**M-1. No mention of four-fermion interference effects (Category C)**

At LEP2 energies, the Zh signal interferes with ZZ → bbνν/bbℓℓ at the amplitude level. For a strategy document this is a detail, but it should be noted that the signal and ZZ background are not fully separable and that the simulation must handle this correctly (typically via a four-fermion generator). This is a suggestion for the revised strategy.

---

## Summary of Consolidated Issues

| Category | Count | Issues |
|----------|-------|--------|
| **A (Must resolve)** | 5 | Missing WW background; Missing ZZ background; Incorrect blinding variable; Incorrect cross-section reference; Incomplete systematic uncertainty enumeration |
| **B (Should address)** | 10 | Acknowledge qqbb̄ exclusion + revise sensitivity; Jet algorithm (Durham); Background classification; Quantitative yields; Sensitivity calculation; Kinematic fit details (both channels); Control region design; Validation regions; Lepton ID; b-tag working point |
| **C (Suggestions)** | 9 | See table above including M-1 |

---

## Decision

### ITERATE

Five Category A issues remain unresolved. Each is individually sufficient to prevent advancement to Phase 2:

1. **Missing WW background** — a ~17 pb process omitted entirely from the background enumeration.
2. **Missing ZZ background** — the irreducible background to the search is absent.
3. **Incorrect blinding variable** — the stated blinding variable contradicts the methodology spec and the strategy's own statistical approach.
4. **Incorrect cross-section reference** — fabricated attribution and potentially incorrect cross-section value near kinematic threshold.
5. **Incomplete systematic uncertainties** — major sources (beam energy, MC statistics, ISR shape, lepton ID) are missing from the enumeration.

The strategy must be revised to address all five Category A issues. The Category B issues should also be addressed in the revision, particularly the jet algorithm choice and the sensitivity estimate, which are closely coupled to the Category A fixes (adding WW/ZZ will change the background landscape and the expected sensitivity).

**Note on the overall approach:** Both reviewers agree that the fundamental analysis approach (cut-based selection with binned likelihood fit to dijet mass in two channels) is sound and well-motivated. The issues are with completeness and correctness of detail, not with the analysis concept. A single focused revision addressing the Category A and B items should be sufficient to reach PASS.
