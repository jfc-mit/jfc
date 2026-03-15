# Critical Review: Phase 1 Strategy

**Reviewer:** Critical Reviewer (adversarial)
**Date:** 2026-03-15
**Artifact:** `phase1_strategy/exec/STRATEGY.md`
**Conventions checked:** `conventions/unfolding.md`

---

## Summary Judgment

The strategy is substantially complete and demonstrates familiarity with the measurement technique. The conventions compliance table (Section 6.1) is a strong feature -- every required source from `conventions/unfolding.md` is enumerated with a planned treatment. Three reference analyses are identified with a comparative systematics table. However, there are several issues that range from potentially blocking to worth addressing.

---

## Category A Findings (Must Resolve -- Blocks Advancement)

### A1. Hadronization systematic is structurally weaker than all three reference analyses

The strategy plans to assess the hadronization systematic by **reweighting** the Pythia 6.1 particle-level distribution to match Herwig 7 (Section 6.1.3). The conventions file (`conventions/unfolding.md`, lines 121-129) explicitly states:

> "Data-driven reweighting of a single generator's response matrix is not a substitute -- it probes data/MC shape differences but not the fundamental dependence on the fragmentation model."

and:

> "If alternative generators with full detector simulation are unavailable, reweighting at particle level is acceptable but **must be documented as a limitation**."

The strategy acknowledges this in passing but does not confront the severity of the issue. All three reference analyses used **multiple fully simulated generators** (Ref 1: Pythia/Herwig/Ariadne; Ref 2: JETSET/Ariadne/Herwig; Ref 3: Pythia 6/8 + Herwig 7 at generator level). This analysis has only one reconstructed MC sample (Pythia 6.1). Reweighting the response matrix at particle level does not probe how a different fragmentation model interacts with the detector -- the very thing the hadronization systematic is meant to capture.

**Required resolution:** The strategy must explicitly (a) acknowledge that this is the dominant limitation of the analysis relative to the original ALEPH publications, (b) explain why the resulting systematic is expected to be conservative or not (with quantitative reasoning), and (c) state whether any attempt will be made to generate a fast-simulated alternative sample (e.g., using parametric smearing derived from the Pythia 6.1 response). Without this, a referee would immediately flag the hadronization uncertainty as potentially underestimated.

### A2. The actual ALEPH event shape publication is not cited as a reference analysis

The strategy cites the ALEPH result through the LEP combination paper (hep-ex/0411006) and the archived-data QGP search (inspire:1793969), but the primary ALEPH event shape publication -- Eur.Phys.J.C35:457-486,2004 -- is referenced only in passing (Section 2.2) and is **not** one of the three tabulated reference analyses. This is the most directly comparable measurement: same detector, same observable, same dataset era. Its systematic program should be tabulated in Section 7, not merely cited for the particle-level definition.

**Required resolution:** Replace one of the current three reference analyses (likely Ref 2, the DELPHI oriented-shapes paper, which measures a different observable -- oriented event shapes as functions of thrust-axis polar angle, not the inclusive thrust distribution) with the primary ALEPH event shapes paper. Tabulate its systematic program. If all four are kept, add a fourth row to the comparison table.

### A3. No discussion of how the "aftercut" pre-selection interacts with the systematic program

The data files are labeled "aftercut" (Section 3.1), meaning an unknown subset of the baseline selection has already been applied. The strategy acknowledges this (Section 4.1, final note) but defers the investigation entirely to Phase 2. This is problematic because:

- If the pre-applied cuts are tight enough that some of the planned selection-cut variations (Section 6.1.1) are already absorbed, the corresponding systematic evaluations become meaningless (you cannot loosen a cut that was already applied upstream).
- The planned variation of the charged energy cut from 15 to 10 GeV may be impossible if the "aftercut" already enforces 15 GeV.

**Required resolution:** The strategy must identify the risk that pre-applied cuts may constrain the systematic program. At minimum, add a Phase 2 gate condition: "Before finalizing the systematic plan, verify which cuts are pre-applied. If any planned variation is precluded by the pre-selection, document the limitation and consider alternative probes of the same effect."

---

## Category B Findings (Should Address -- Weakens but Does Not Invalidate)

### B1. Covariance matrix construction is not specified in the strategy

The conventions (`conventions/unfolding.md`, Section "Covariance matrix") require explicit planning for statistical covariance (bootstrap/toys vs. analytical propagation), systematic covariances (outer product of shift vectors), total covariance construction, and validation (positive semi-definiteness, condition number, correlation matrix visualization). The strategy mentions the covariance matrix only in the context of the alpha_s chi2 fit (Section 9.1) but never specifies how it will be constructed. This is a measurement deliverable, not just a fit input.

**Action:** Add a subsection to the strategy specifying the covariance matrix construction approach, at least at the level of: statistical covariance method (bootstrap vs. analytical), how systematic covariances will be formed, and what validation checks will be performed.

### B2. Fit range sensitivity is under-specified for alpha_s extraction

The strategy plans to vary the fit range by +/-1 bin (Section 9.2). This is standard but insufficient on its own. Published analyses (e.g., the DELPHI paper cited as Ref 2) performed extensive fit-range stability studies, varying both lower and upper bounds independently and reporting stability plots. The strategy should specify that stability of alpha_s vs. fit range will be demonstrated, not just that the fit range will be varied as a systematic.

**Action:** Expand the fit-range variation plan: specify that alpha_s will be reported as a function of lower and upper fit-range bounds, and that any instability will be investigated.

### B3. No mention of energy-energy correlation (EEC) or other event shapes as cross-checks

The original ALEPH analyses and the LEP combination extracted alpha_s from multiple event shapes simultaneously (thrust, C-parameter, heavy jet mass, jet broadenings, y23). The strategy measures only thrust. While this is acceptable for a focused measurement, a competing group would likely measure at least 2-3 event shapes to demonstrate consistency. This is not blocking (the strategy is explicitly a thrust measurement), but the absence of even a brief justification for why only thrust is measured leaves an opening for a referee.

**Action:** Add a sentence justifying the single-observable focus (e.g., thrust has the best perturbative convergence and smallest hadronization corrections among event shapes, or the scope is limited by available resources). Alternatively, consider measuring C-parameter as a secondary observable -- the computational cost is negligible since the same event sample is used.

### B4. No discussion of the statistical correlation between the unfolded distribution and the alpha_s fit

The strategy plans to (1) unfold the thrust distribution and (2) fit alpha_s to the unfolded distribution. The unfolded distribution's covariance matrix is a crucial input to the alpha_s fit, but unfolding introduces non-trivial bin-to-bin correlations (especially IBU). If the covariance matrix fed to the alpha_s fit does not properly account for these correlations, the fit uncertainty will be wrong. This is a known subtlety that should be acknowledged in the strategy.

**Action:** Add a note that the alpha_s fit will use the full unfolded covariance matrix (stat + syst), and that the statistical component will properly propagate the correlations introduced by unfolding.

### B5. Pythia 8 and Herwig 7 sample generation is vague

The strategy states these will be "generated if not available" (Section 3.2) but provides no detail on tune, settings, number of events, or validation criteria. For the hadronization systematic -- the dominant uncertainty -- this is too vague.

**Action:** Specify the Pythia 8 tune (Monash 2013 is mentioned but should be explicit), Herwig 7 tune (default or specific), target statistics (at minimum matching the data statistics), and whether any retuning or parameter scanning is planned.

### B6. Missing discussion of charged-only vs. charged+neutral observable definition

Section 10.1 mentions "charged-only vs. charged+neutral thrust" as a validation check, but the main observable definition (Section 2.2) includes both charged and neutral particles. The response matrix from Pythia 6.1 requires that both charged tracks and calorimeter clusters are used at detector level. The strategy does not discuss how neutral particles (photons, K_L, neutrons) are reconstructed at detector level in the archived data, or what systematic effects the calorimeter response introduces. For a full-phase-space measurement including neutrals, the calorimeter modeling is part of the "object-level response" systematic (Section 6.1.1), but the planned variations mention only tracking quantities in detail. Calorimeter energy scale variation is mentioned in one clause but not elaborated.

**Action:** Expand the object-level response systematic to explicitly address calorimeter-based objects (photons from pi0, K_L clusters) with the same level of detail as tracking.

---

## Category C Findings (Suggestions -- Style, Clarity)

### C1. Reference Analysis 2 relevance is marginal

The DELPHI oriented event shapes paper (inspire:1661561) measures event shapes as functions of the thrust-axis polar angle -- a fundamentally different measurement from the inclusive thrust distribution. While the systematic program is informative, it is not the most relevant comparison. A more relevant choice would be the primary ALEPH event shapes publication or the OPAL thrust measurement. (See also A2.)

### C2. Section 5.4 normalization statement could be more precise

The statement "Normalization is performed after unfolding and efficiency correction, not before (per conventions)" is correct, but the strategy should clarify whether the efficiency correction is applied within the unfolding (response matrix includes efficiency) or as a separate step. This affects how the normalization is implemented.

### C3. Expected systematic budget (Section 6.2) should cite specific bin ranges

The statement that hadronization is "1-3% per bin" is reasonable but should note that this is based on published analyses that used fully simulated alternative generators. The systematic from particle-level reweighting may not capture the full effect. (Related to A1.)

### C4. The strategy does not mention blind analysis procedures

While not standard for LEP reanalyses, blinding (e.g., not looking at alpha_s fit results until systematics are finalized) is increasingly expected. A brief statement on whether blinding will be used would strengthen the document.

---

## Conventions Completeness Check

Systematic sources from `conventions/unfolding.md`:

| Convention Source | Addressed in Strategy? | Adequate? |
|---|---|---|
| Object-level response | Yes (Section 6.1.1) | Partial -- tracking detailed, calorimeter under-specified (B6) |
| Selection cuts | Yes (Section 6.1.1) | Yes, but may be constrained by pre-selection (A3) |
| Background contamination | Yes (Section 6.1.1) | Yes |
| Regularization strength | Yes (Section 6.1.2) | Yes |
| Prior dependence | Yes (Section 6.1.2) | Yes |
| Alternative method | Yes (Section 6.1.2) | Yes |
| Hadronization model | Yes (Section 6.1.3) | Structurally weak (A1) |
| ISR treatment | Yes (Section 6.1.4) | Yes |
| Heavy flavor | Yes (Section 6.1.4) | Yes |
| Normalized vs. absolute | Yes (Section 5.4) | Yes |
| Covariance matrix | Not in strategy | Missing (B1) |
| Response matrix validation | Mentioned in Phase 2 plan | Acceptable for Phase 1 |
| Comparison to reference measurements | Yes (Section 10.2) | Yes |

---

## Answers to Concrete Operating Questions

**1. Are all systematic sources listed in conventions/unfolding.md either implemented or explicitly justified as inapplicable?**

Yes, all sources from the "Required systematic sources" section are enumerated. However, the covariance matrix construction requirements from the conventions are not addressed in the strategy (B1), and the hadronization treatment is structurally weaker than what the conventions envision (A1).

**2. Have 2-3 published reference analyses been identified, and does this analysis match or exceed their systematic coverage?**

Three reference analyses are identified with a comparison table. However, the most directly relevant reference -- the primary ALEPH event shapes publication -- is not among them (A2). The systematic coverage nominally matches or exceeds the references (regularization, prior dependence, and alternative method go beyond Refs 1-3), but the hadronization systematic is weaker in implementation (A1).

**3. If a competing group published a measurement of the same quantity next month, what would they have that we don't?**

A competing group would likely have:
- Multiple event shapes measured simultaneously (thrust, C-parameter, heavy jet mass at minimum), not just thrust alone (B3)
- A more robust hadronization systematic using at least two fully simulated generators, or a careful study of why reweighting captures the dominant effect (A1)
- Multiple alpha_s extractions at different perturbative orders (NLO+NLL, NNLO, NNLO+N3LL) to demonstrate perturbative convergence, with the state-of-the-art (NNLO+N3LL) as the primary result -- the strategy lists these but does not commit to which will be the primary result
- A published covariance matrix enabling reinterpretation (B1)
- Potentially a comparison to the Dokshitzer-Webber power correction approach as more than a secondary option, since this removes MC-model dependence from the alpha_s fit

---

## Recommendation

**Do not advance to Phase 2 until A1, A2, and A3 are resolved.** The remaining findings (B1-B6, C1-C4) should be addressed but do not block advancement.
