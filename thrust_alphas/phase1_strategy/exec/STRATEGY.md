# Strategy: Precision Measurement of the Thrust Distribution and $\alpha_s$ Extraction in $e^+e^-$ Collisions at $\sqrt{s} = 91.2$ GeV Using Archived ALEPH Data

## 1. Physics Motivation

Thrust is one of the most extensively studied event shape observables in $e^+e^-$ annihilation. It is infrared- and collinear-safe, calculable in perturbative QCD, and provides a clean handle on $\alpha_s(M_Z)$ through fits of theory predictions to the corrected (particle-level) distribution. The LEP experiments measured thrust at the $Z$ pole with high statistics, enabling percent-level extractions of the strong coupling constant.

This analysis uses archived ALEPH data at $\sqrt{s} = 91.2$ GeV to:
1. Measure the thrust distribution at particle level, corrected for detector effects.
2. Compare the corrected distribution to MC predictions (Pythia, Herwig) and to published ALEPH results as validation.
3. Extract $\alpha_s(M_Z)$ from fits of pQCD predictions to the measured thrust distribution.

The archived ALEPH dataset provides an opportunity to reproduce and potentially extend the original collaboration's measurements using modern analysis tools, serving both as a validation of open-data analysis techniques and as a physics measurement in its own right.

## 2. Observable Definition

### 2.1 Thrust

Thrust $T$ is defined as:
$$T = \max_{\hat{n}} \frac{\sum_i |\vec{p}_i \cdot \hat{n}|}{\sum_i |\vec{p}_i|}$$
where the sum runs over all final-state particles and $\hat{n}$ is optimized to maximize the expression (defining the thrust axis $\hat{n}_T$). The conventional variable for distributions is $\tau = 1 - T$, which ranges from 0 (perfectly back-to-back 2-jet topology) to 0.5 (isotropic/spherical).

### 2.2 Particle-Level Definition

The particle-level target for the unfolded measurement is defined as follows:

- **Particles included:** All stable charged and neutral particles with lifetime $c\tau > 10$ mm. This includes charged hadrons ($\pi^\pm$, $K^\pm$, $p/\bar{p}$), neutral hadrons ($K^0_L$, neutrons), and photons. It excludes neutrinos.
- **Phase space:** Full $4\pi$ acceptance (no fiducial cuts at particle level). This is a full-phase-space measurement.
- **ISR treatment:** ISR photons are excluded from the particle-level thrust calculation. The measurement targets the hadronic system from the $Z$ decay. Events with hard ISR ($E_\gamma^{\text{ISR}} > 1$ GeV) are removed at both detector and particle level. The effective $\sqrt{s}$ is the $Z$ pole mass, not the reduced $\sqrt{s'}$ after ISR.
- **Hadron decays:** Particles are defined at the "stable particle" level — $K_S^0$, $\Lambda$, and other particles with $c\tau < 10$ mm are allowed to decay; their daughters enter the thrust calculation.

This definition follows the standard LEP convention used in the original ALEPH event shape publications (e.g., ALEPH, Eur.Phys.J.C35:457-486, 2004).

## 3. Sample Inventory

### 3.1 Data

| Sample | File | Years | Description |
|--------|------|-------|-------------|
| LEP1Data1992 | `LEP1Data1992_recons_aftercut-MERGED.root` | 1992 | Reconstructed, post-selection |
| LEP1Data1993 | `LEP1Data1993_recons_aftercut-MERGED.root` | 1993 | Reconstructed, post-selection |
| LEP1Data1994P1 | `LEP1Data1994P1_recons_aftercut-MERGED.root` | 1994 (period 1) | Reconstructed, post-selection |
| LEP1Data1994P2 | `LEP1Data1994P2_recons_aftercut-MERGED.root` | 1994 (period 2) | Reconstructed, post-selection |
| LEP1Data1994P3 | `LEP1Data1994P3_recons_aftercut-MERGED.root` | 1994 (period 3) | Reconstructed, post-selection |
| LEP1Data1995 | `LEP1Data1995_recons_aftercut-MERGED.root` | 1995 | Reconstructed, post-selection |

All data files are located at `/n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ALEPH/`. The files contain reconstructed events that have already passed a baseline cut ("aftercut"). The combined dataset is expected to contain $\sim$2--4 million hadronic $Z$ decays across the 1992--1995 running periods.

### 3.2 Monte Carlo

| Sample | Files | Generator | Description |
|--------|-------|-----------|-------------|
| LEP1MC1994 | 40 files (`LEP1MC1994_recons_aftercut-001.root` through `-040.root`) | Pythia 6.1 | Reconstructed MC with full ALEPH detector simulation |

Located at `/n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ALEPHMC/`. This is the archived reconstructed Pythia 6.1 sample that was used in prior analyses of the archived data (inspire:1793969). It contains both detector-level reconstructed quantities and generator-level truth information, enabling construction of the response matrix for unfolding.

**Generator-level samples for comparison (to be generated if not available):**
- Pythia 8 (modern Monash tune): for hadronization model comparison at particle level
- Herwig 7: for alternative hadronization model (cluster vs. string fragmentation)

These generator-level samples do not require detector simulation and can be produced locally for theory-level comparisons and as alternative priors for the hadronization systematic.

## 4. Event Selection Approach

### 4.1 Hadronic $Z$ Decay Selection

The standard ALEPH hadronic event selection will be applied, following the criteria used in published ALEPH analyses and in the archived data analysis (inspire:1793969):

**Track-level quality cuts:**
- At least 4 TPC coordinate hits per track
- Distance of closest approach to IP: $|d_0| < 2$ cm (transverse), $|z_0| < 10$ cm (longitudinal)
- Polar angle: $|\cos\theta| < 0.95$
- Minimum transverse momentum: $p_T > 0.2$ GeV/$c$

**Event-level cuts:**
- At least 5 good charged tracks
- Total charged energy (assuming $\pi$ mass): $E_{\text{ch}} > 15$ GeV ($\sim$15% of $\sqrt{s}$)
- At least 13 total accepted tracks (charged + neutral)
- Event sphericity axis: $|\cos\theta_{\text{sph}}| < 0.82$ (ensures good containment)
- Total missing momentum: $< 20$ GeV/$c$
- Removal of $e^+e^-$ background from detector material interactions

**Note:** The data files are labeled "aftercut," indicating some baseline selection has already been applied. Phase 2 will verify which cuts have been applied and whether additional cuts are needed.

**Phase 2 gate condition -- "aftercut" discovery:** The data files are labeled "aftercut." Phase 2 must discover exactly which cuts have been pre-applied by examining the file metadata, any accompanying documentation, and the distributions of selection variables at the boundaries of the specified cuts. Any systematic variation (Section 6.1.1) that involves loosening a cut that was already applied upstream will be replaced with an alternative approach -- for example, tightening the cut only, or estimating the efficiency as a function of the cut threshold from MC. The systematic program in Section 6 is contingent on this discovery. If Phase 2 finds that a key systematic probe (e.g., the charged-energy cut variation 15 GeV $\to$ 10 GeV) is precluded by the pre-selection, the strategy will be updated to document the limitation and substitute alternative probes of the same detector effect before Phase 3 begins.

### 4.2 Selection Efficiency and Background

Based on published ALEPH analyses:
- Selection efficiency for hadronic $Z$ decays: $\sim$94--95%, approximately flavor-independent to $< 1\%$
- $\tau^+\tau^-$ background: $< 0.3\%$
- $\gamma\gamma$ background: negligible
- Two-photon events: negligible at $\sqrt{s} = M_Z$
- ISR return events: not relevant at the $Z$ pole (no higher-energy return)

The very high efficiency and low background make this a clean environment. Background subtraction will be performed using MC estimates, with systematic variations on the background normalization.

## 5. Correction/Unfolding Strategy

### 5.1 Method

The primary correction method will be **iterative Bayesian unfolding (IBU)**, also known as D'Agostini unfolding. This is chosen because:
- It is well-established for event shape measurements
- It naturally handles bin-to-bin migrations
- The regularization parameter (number of iterations) is intuitive
- It does not require matrix inversion (avoiding instabilities)

As an alternative/cross-check method, **bin-by-bin multiplicative correction factors** will also be computed. This was the standard approach in the original ALEPH event shape publications:
$$\left(\frac{1}{N}\frac{dN}{d\tau}\right)_{\text{corrected}} = C(\tau) \cdot \left(\frac{1}{N}\frac{dN}{d\tau}\right)_{\text{detector}}$$
where $C(\tau) = f_{\text{gen}}(\tau) / f_{\text{det}}(\tau)$ is the ratio of generator-level to detector-level distributions from MC. This approach is approximately model-independent by construction but does not properly handle bin migrations.

### 5.2 Response Matrix

The response matrix will be constructed from the Pythia 6.1 MC sample, mapping detector-level $\tau$ bins to particle-level $\tau$ bins. The matrix encodes:
- Detector resolution effects (momentum smearing, angular resolution)
- Selection efficiency as a function of $\tau$
- Bin migration patterns

### 5.3 Binning

The measurement will use approximately 20--30 bins in $\tau = 1 - T$, spanning the range $0.0 \leq \tau \leq 0.5$. The binning will be refined during Phase 2 based on:
- Statistical precision per bin
- Response matrix diagonal fraction
- Consistency with prior publications for comparison purposes

### 5.4 Normalization

This is a **normalized shape measurement**: $(1/N)\,dN/d\tau$. Normalization is performed **after** unfolding and efficiency correction, not before (per conventions). Normalization-only systematics (luminosity, total cross-section, trigger efficiency) cancel and are excluded from the systematic budget.

### 5.5 Covariance Matrix Construction

The full covariance matrix $C_{ij}$ of the unfolded distribution is a measurement deliverable in its own right, required for the $\alpha_s$ fit (Section 9.1) and for comparison with published results (Section 10.2). It is constructed as the sum of statistical and systematic components.

**Statistical covariance.** The statistical covariance is estimated by bootstrap resampling: the input data histogram is resampled $N_{\text{toy}} \geq 500$ times (Poisson resampling of each bin count), each replica is passed through the full unfolding chain with the nominal response matrix, and the covariance is computed from the spread of unfolded replicas. This correctly propagates the bin-to-bin correlations introduced by IBU into the statistical covariance matrix. Analytical uncertainty propagation through the IBU iterations will also be computed as a cross-check.

**Systematic covariance.** Each systematic source $k$ produces an upward-shifted unfolded distribution $\vec{y}^{(k,+)}$ and a downward-shifted distribution $\vec{y}^{(k,-)}$ (or a one-sided shift $\Delta\vec{y}^{(k)}$ where only a one-sided variation is meaningful). The systematic covariance for source $k$ is:
$$C^{(k)}_{ij} = \Delta y^{(k)}_i \cdot \Delta y^{(k)}_j$$
where $\Delta y^{(k)}_i = \frac{1}{2}(y^{(k,+)}_i - y^{(k,-)}_i)$ is the half-difference shift. This outer-product form assumes each systematic source is fully correlated across bins, which is conservative. The total systematic covariance is the sum over all sources $k$.

**Total covariance.** The total covariance matrix is the sum of statistical and all systematic components:
$$C_{ij}^{\text{total}} = C_{ij}^{\text{stat}} + \sum_k C_{ij}^{(k)}$$

**Validation.** The covariance matrix will be validated with the following checks before it is used in the $\alpha_s$ fit:
1. **Positive semi-definiteness:** All eigenvalues must be $\geq 0$. Negative eigenvalues indicate numerical issues and will be investigated.
2. **Condition number:** The ratio of the largest to smallest eigenvalue. A large condition number ($> 10^3$) indicates the matrix is nearly singular and the $\chi^2$ fit may be ill-conditioned; the fit range or binning will be adjusted accordingly.
3. **Correlation matrix visualization:** The correlation matrix $\rho_{ij} = C_{ij}/\sqrt{C_{ii} C_{jj}}$ will be plotted as a heat map. Off-diagonal structure from unfolding correlations and hadronization systematics is expected and should be physically interpretable.
4. **Diagonal comparison:** Per-bin total uncertainty computed from the diagonal of $C^{\text{total}}$ will be compared to the published ALEPH uncertainties as a sanity check.

## 6. Systematic Uncertainty Plan

### 6.1 Conventions Compliance

The following table enumerates every required systematic source from `conventions/unfolding.md` with the planned treatment for this analysis.

#### 6.1.1 Detector and Reconstruction

| Required Source | Convention Description | Plan | Status |
|----------------|----------------------|------|--------|
| **Object-level response** | Scale/smear/remove reconstructed objects by category | **Will implement.** Vary tracking quantities: (a) smear track momenta by varying the momentum resolution, (b) vary TPC hit requirements (4 to 7 hits), (c) remove fraction of tracks to probe tracking efficiency. For calorimetric objects, vary the energy scale. | Will implement |
| **Selection cuts** | Vary each event-level cut with non-negligible rejection | **Will implement.** Vary: (a) minimum charged energy (15 GeV $\to$ 10 GeV), (b) $|\cos\theta_{\text{sph}}|$ cut ($\pm$5%), (c) minimum number of tracks, (d) minimum track $p_T$, (e) $|d_0|$ and $|z_0|$ requirements. | Will implement |
| **Background contamination** | Vary background normalization or removal | **Will implement.** Vary $\tau^+\tau^-$ and $\gamma\gamma$ background estimates by $\pm$50% (conservative given the $< 0.3\%$ contamination). Expected to be negligible. | Will implement |

#### 6.1.2 Unfolding Method

| Required Source | Convention Description | Plan | Status |
|----------------|----------------------|------|--------|
| **Regularization strength** | Vary iterations or regularization parameter | **Will implement.** Scan the number of IBU iterations; report closure and stress test $\chi^2$/ndf vs. iteration count. Nominal chosen by plateau criterion. | Will implement |
| **Prior dependence** | Alternative priors (reweighted truth, flat) | **Will implement.** Repeat unfolding with (a) flat prior and (b) Herwig-reweighted prior. Report per-bin shift; flag any bin where flat-prior shift exceeds 20% relative. | Will implement |
| **Alternative method** | At least one independent unfolding method | **Will implement.** Bin-by-bin correction factors as the alternative method. Compare the corrected distributions from IBU and bin-by-bin; half-difference as systematic. | Will implement |

#### 6.1.3 Generator Model (Hadronization)

| Required Source | Convention Description | Plan | Status |
|----------------|----------------------|------|--------|
| **Hadronization model** | Compare generators with fundamentally different fragmentation models | **Will implement.** This is expected to be the dominant systematic. Two approaches: (a) **Primary:** reweight the Pythia 6.1 particle-level distribution to match Herwig 7 generator-level distributions, propagate through the response matrix, and take the full shift as the systematic. (b) **Cross-check:** compare bin-by-bin correction factors derived from Pythia 6.1 vs. those derived from a Herwig-reweighted sample. Note: full detector simulation with an alternative generator is not available. Particle-level reweighting is the accepted fallback (per conventions), documented as a limitation. See extended discussion below. | Will implement |

**Structural limitation -- particle-level reweighting (documented):** Only one generator with full ALEPH detector simulation is available (Pythia 6.1). The reference analyses (including the primary ALEPH publication, Ref 2 in Section 7) used three fully simulated generators (PYTHIA, HERWIG, ARIADNE), allowing the hadronization systematic to capture both fragmentation-model differences and their interaction with the detector response. The particle-level reweighting approach used here cannot probe how a different fragmentation model (e.g., cluster fragmentation in Herwig) interacts with the ALEPH detector -- it only probes differences in the particle-level thrust spectrum.

This is documented as **the dominant methodological limitation of this analysis relative to the original ALEPH publications.** It is expected to be conservative for the thrust observable specifically, for the following reason: the dominant detector effect on thrust is tracking efficiency and momentum resolution, which operate at the level of individual tracks. The response of the detector to a given track depends primarily on its kinematics ($p$, $\theta$), not on whether it originated from string or cluster fragmentation. The response matrix is therefore expected to be relatively insensitive to the hadronization model, and the particle-level difference between Pythia 6.1 and Herwig 7 should capture the bulk of the hadronization uncertainty. Nevertheless, any residual fragmentation-detector correlation (e.g., different mean track multiplicities per event affecting track reconstruction efficiency) is not captured by this approach.

**Phase 2 evaluation:** The feasibility of a parametric fast-simulation cross-check will be evaluated in Phase 2. If the ALEPH detector response can be adequately parameterized by a smearing model derived from the Pythia 6.1 response matrix (e.g., Gaussian resolution smearing plus efficiency correction), then a Herwig 7 sample can be passed through this fast simulation to provide a more complete alternative-generator systematic. This cross-check will be pursued if Phase 2 indicates the particle-level reweighting systematic is unusually large or unstable.

#### 6.1.4 Theory Inputs

| Required Source | Convention Description | Plan | Status |
|----------------|----------------------|------|--------|
| **ISR treatment** | Correct for ISR or define measurement as ISR-inclusive | **Will implement.** The measurement is defined as ISR-exclusive (hadronic system only). Events with hard ISR will be removed. The MC-based correction accounts for residual soft ISR. Systematic: vary the ISR removal threshold. | Will implement |
| **Heavy flavor** | Vary b-quark mass or fragmentation if observable is sensitive | **Will implement.** Thrust is sensitive to $b$-quark fragmentation (harder fragmentation $\to$ higher thrust). Vary the $b$-quark fragmentation function parameters in the MC (Peterson $\epsilon_b$ parameter) and assess the impact on the response matrix. Additionally, compare results with and without $b\bar{b}$ events as a cross-check. | Will implement |

#### 6.1.5 Additional Sources (Not Required by Conventions but Standard Practice)

| Source | Plan | Rationale |
|--------|------|-----------|
| **MC statistics** | Bootstrap the response matrix entries; propagate to the unfolded result. | Limited MC sample size introduces statistical fluctuations in the correction. |
| **Year-to-year consistency** | Compare corrected distributions from individual data-taking years (1992, 1993, 1994, 1995). | Probes time-dependent detector effects. |

### 6.2 Summary of Expected Systematic Budget

Based on published ALEPH event shape analyses and the LEP QCD working group combination (hep-ex/0411006), the expected hierarchy of systematic uncertainties is:

1. **Hadronization model** (dominant): $\sim$1--3% per bin, largest in the 2-jet ($\tau \to 0$) and multi-jet ($\tau \to 0.5$) regions where fragmentation effects are largest.
2. **Detector effects** (tracking, selection): $\sim$0.5--1% per bin, assessed from cut variations.
3. **Unfolding method/regularization**: $\sim$0.3--1% per bin.
4. **ISR/heavy flavor**: $\sim$0.1--0.5% per bin.
5. **Background subtraction**: negligible ($< 0.1\%$).
6. **MC statistics**: depends on bin width; estimated during Phase 2.

For the $\alpha_s$ extraction, the dominant uncertainty is **theoretical** (missing higher-order terms, renormalization scale variation), not experimental. This is consistent with all prior LEP $\alpha_s$ determinations from event shapes.

## 7. Reference Analyses

### 7.1 Reference Analysis 1: ALEPH QCD Studies and $\alpha_s$ at LEP (hep-ex/0411006)

LEP QCD working group combination using final event shape measurements from all four experiments. At 91.2 GeV, combined result: $\alpha_s(M_Z) = 0.1202 \pm 0.0003(\text{stat}) \pm 0.0007(\text{exp}) \pm 0.0012(\text{hadr}) \pm 0.0048(\text{theo})$.

| Systematic Source | Treatment |
|-------------------|-----------|
| Experimental (detector) | Cut variations, selection efficiency |
| Hadronization | Three generators: Pythia, Herwig, Ariadne |
| Theory (dominant) | Renormalization scale variation, matching scheme |
| Statistical | From data |

### 7.2 Reference Analysis 2: ALEPH Event Shape Measurements (Eur.Phys.J.C35:457-486, 2004; hep-ex/0409098)

Primary ALEPH measurement of 16 event shape distributions (including thrust) using data from 1991--1995 $e^+e^-$ runs at $\sqrt{s} = M_Z$, with $\alpha_s$ extracted from fits to NLO+NLL theory predictions. This is the single most directly relevant reference: same detector, same observable, and the same archived dataset era as this analysis.

| Systematic Source | Treatment |
|-------------------|-----------|
| Detector (tracking) | Varied TPC hit requirements, $d_0$ and $z_0$ cuts, track $p_T$ threshold; tracking efficiency varied by $\pm 1\%$ |
| Detector (calorimeter) | Varied energy scale and clustering thresholds for electromagnetic and hadronic calorimeters |
| Selection cuts | Varied event-level cuts: charged energy threshold, sphericity axis cut, track multiplicity |
| Hadronization | Three generators each with full ALEPH detector simulation: PYTHIA 6.1, HERWIG 5.9, ARIADNE 4.1; full shift from nominal (PYTHIA) treated as systematic |
| ISR | Residual ISR correction applied via MC; hard-ISR events removed |
| Theory ($\alpha_s$ fit) | Renormalization scale varied $x_\mu \in [0.5, 2]$; two matching schemes (log-R and R-matching) |

The ALEPH hadronization systematic used three fully simulated generators (PYTHIA, HERWIG, ARIADNE). This is the gold standard against which the present analysis's particle-level reweighting approach is evaluated (see Section 6.1.3 and Section 7.4).

### 7.3 Reference Analysis 3: Archived ALEPH QGP Search (inspire:1793969)

Modern analysis of the same archived ALEPH dataset, measuring thrust and two-particle correlations. Validated the archived data by reproducing the ALEPH thrust distribution.

| Systematic Source | Treatment |
|-------------------|-----------|
| Tracking | TPC hit requirement varied (4 to 7 hits); 0.7% uncertainty |
| Event selection | Charged energy cut (15 $\to$ 10 GeV), track multiplicity variation |
| MC correction | Statistical uncertainty on Pythia 6.1 correction factors |
| Generator comparison | Pythia 6.1 (reconstructed), Pythia 8.230, Herwig 7.1.5 at generator level |

### 7.4 Systematic Program Comparison

| Systematic | Ref 1 (LEP comb.) | Ref 2 (ALEPH 2004) | Ref 3 (Archived ALEPH) | This Analysis |
|------------|-------------------|--------------------|------------------------|---------------|
| Track/object response | Yes | Yes (TPC hits, $d_0$, $z_0$, $p_T$) | Yes (TPC hits) | Yes |
| Calorimeter response | Yes | Yes (energy scale, clustering) | Implicit | Yes |
| Selection cut variation | Yes | Yes | Yes | Yes |
| Background | Yes | Yes | Implicit | Yes |
| Regularization/iterations | N/A (bin-by-bin) | N/A (bin-by-bin) | N/A | Yes (IBU) |
| Prior dependence | N/A | N/A | N/A | Yes |
| Alternative unfolding | N/A | N/A | N/A | Yes (bin-by-bin cross-check) |
| Hadronization model | Pythia/Herwig/Ariadne (full sim) | Pythia/Herwig/Ariadne (full sim) | Pythia 6/8, Herwig 7 (gen. level) | Pythia 6.1 + Herwig reweighting (particle-level) -- see Section 6.1.3 |
| ISR | Yes | Yes | N/A (Z pole) | Yes |
| Heavy flavor ($b$ frag.) | Not separately | Not separately | No | Yes |
| Renorm. scale ($\alpha_s$ fit) | Yes (dominant) | Yes (dominant) | N/A | Yes |
| MC statistics | Implicit | Implicit | Yes | Yes |

## 8. Theory Predictions for Comparison

### 8.1 Monte Carlo Generators

| Generator | Fragmentation Model | Purpose |
|-----------|-------------------|---------|
| Pythia 6.1 | Lund string | Response matrix construction, baseline corrections |
| Pythia 8 (Monash) | Lund string | Modern tune comparison, generator-level |
| Herwig 7 | Cluster | Alternative hadronization, systematic assessment |

### 8.2 Perturbative QCD Predictions

The thrust distribution has been calculated to high precision in perturbative QCD:

- **NLO + NLL resummation** ($\mathcal{O}(\alpha_s^2)$ + NLLA): This was the standard theory used in the LEP era for $\alpha_s$ extraction from event shapes. Available from the EVENT2 program (NLO) combined with analytic resummation.
- **NNLO** ($\mathcal{O}(\alpha_s^3)$): Available from calculations by Gehrmann-De Ridder, Gehrmann, Glover, Heinrich (2007--2009). Provides improved perturbative precision.
- **NNLO + N$^3$LL resummation**: The state-of-the-art theory calculation, combining third-order fixed-order with next-to-next-to-next-to-leading logarithmic resummation. Calculations by Becher and Schwartz (2008), Abbate et al. (2010, 2012) using soft-collinear effective theory (SCET).

For the $\alpha_s$ extraction, we will use $\mathcal{O}(\alpha_s^2)$ + NLLA matched predictions as the baseline (consistent with the original LEP analyses) and, if available, NNLO + N$^3$LL as the modern benchmark.

### 8.3 Non-Perturbative Corrections

Two approaches to non-perturbative corrections in the $\alpha_s$ fit:
1. **MC-based hadronization correction:** Ratio of parton-level to hadron-level MC distributions applied as multiplicative correction to the pQCD prediction. This is the standard LEP approach.
2. **Power corrections (Dokshitzer-Webber):** Analytic $1/Q$ power corrections with a universal infrared coupling $\alpha_0(\mu_I)$. This provides a simultaneous fit of $\alpha_s$ and $\alpha_0$, reducing dependence on MC hadronization models.

## 9. $\alpha_s$ Extraction Approach

### 9.1 Fit Procedure

1. Compute the theory prediction for $(1/\sigma)\,d\sigma/d\tau$ as a function of $\alpha_s$ at a given perturbative order.
2. Apply non-perturbative corrections (hadronization factors from MC or power corrections).
3. Perform a $\chi^2$ fit to the measured distribution using the full covariance matrix:
$$\chi^2 = \sum_{i,j} \left[y_i^{\text{data}} - y_i^{\text{theory}}(\alpha_s)\right] C_{ij}^{-1} \left[y_j^{\text{data}} - y_j^{\text{theory}}(\alpha_s)\right]$$
4. The fit range is restricted to the region where perturbative predictions are reliable: typically $0.05 \leq \tau \leq 0.30$. The lower bound avoids the 2-jet region where resummation effects and non-perturbative corrections are large; the upper bound avoids the multi-jet region where fixed-order calculations are unreliable.

### 9.2 Theoretical Uncertainties

- **Renormalization scale variation:** Vary $\mu_R$ between $\sqrt{s}/2$ and $2\sqrt{s}$ (i.e., $x_\mu \in [0.5, 2]$).
- **Matching scheme:** Compare log-R and R-matching for combining fixed-order and resummed predictions.
- **Fit range variation:** Shift the lower and upper bounds of the fit range by $\pm 1$ bin.
- **Hadronization correction:** Use Pythia vs. Herwig correction factors.

### 9.3 Expected Result

Based on the LEP combination and prior ALEPH measurements, we expect $\alpha_s(M_Z) \approx 0.120 \pm 0.006$ (total), with the theoretical uncertainty dominating.

## 10. Validation Plan

### 10.1 Internal Consistency

- Year-by-year comparison of corrected thrust distributions
- Charged-only vs. charged+neutral thrust (if both are available in the data)
- Data/MC comparison of all input kinematic variables before unfolding (per conventions: per-category distributions with ratio panels)

### 10.2 External Validation

- Compare the corrected thrust distribution to the published ALEPH result (Eur.Phys.J.C35:457-486, 2004) using the full covariance matrix
- Compare to the archived-data thrust result from inspire:1793969
- Report $\chi^2$/ndf and $p$-value for each comparison
- If $\chi^2$/ndf $> 1.5$, investigate and document the source of tension (per conventions)

## 11. Analysis Chain Summary

| Phase | Key Deliverables |
|-------|-----------------|
| Phase 1 (Strategy) | This document |
| Phase 2 (Exploration) | Sample inventory, data/MC distributions, response matrix validation |
| Phase 3 (Selection) | Final event selection, control distributions, cutflow |
| Phase 4a (Inference - Expected) | Closure/stress tests, systematic enumeration, expected $\alpha_s$ from MC pseudo-data |
| Phase 4b (Inference - Partial) | Unfolded thrust distribution with systematics |
| Phase 4c (Inference - Observed) | $\alpha_s$ extraction, comparison to published results |
| Phase 5 (Documentation) | Analysis note |
