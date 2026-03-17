## 3. Analysis Phases

Five sequential phases. Within a phase, **parallelize where possible** —
sub-delegate independent tasks (MVA training, systematics, plotting). See
§3a.5.

### 3.0 Artifact and Review Gates

**Every phase boundary is a hard gate.** Phase N+1 cannot begin until
Phase N has produced its artifact AND passed review (§6).

Gate protocol: (1) produce artifact → (2) update experiment log → (3)
review (§6) → (4) resolve Category A items → (5) advance.

Artifact existence is a precondition. Never skip an artifact, even under
context pressure — write the artifact and stop cleanly.

See §3a for orchestrator architecture. Phase CLAUDE.md templates (from
`templates/`) are the operational entry points agents read at runtime.

---

### Analysis Types

- **Search:** Signal/background, SR/CR structure, blinding (§4), limits or
  significance.
- **Measurement:** Corrected spectra, event shapes, extracted parameters.
  No S/B per se. Staged validation replaces blinding (§4).

Where phase descriptions reference search concepts (SR, CR, S/B),
measurements substitute: fiducial region, sidebands, purity optimization.

---

### Phase 1: Strategy

**Goal:** Written analysis strategy a collaboration reviewer could approve.

**The agent must:**
- Query experiment corpus for detector capabilities, prior work, datasets
- Identify signal process, backgrounds (classified: irreducible, reducible,
  instrumental), discriminating variables
- Propose selection approach, background estimation strategy, control regions
- **Systematic plan:** read applicable `conventions/` document, enumerate
  every required source with "Will implement" or "Not applicable because
  [reason]." This is binding — Phase 4a reviews against it.
- Identify 2-3 reference analyses, tabulate their systematic programs

**For measurements additionally:** Define observable(s), correction strategy,
prior measurements (validation target), theory predictions for comparison.

**Artifact:** `STRATEGY.md`. **Review:** 4-bot (§6).

---

### Phase 2: Exploration

**Goal:** Characterize data, validate detector model, establish selection
foundation.

**The agent must:**
- Inventory samples (files, trees, branches, events, cross-sections)
- Validate data quality (pathologies, outliers, unphysical values)
- Apply standard object definitions (from corpus), verify data/MC agreement
- Survey discriminating variables, rank by separation power
- Establish baseline yields after preselection

**Data discovery:** Metadata first → small slice (~1000 events) → identify
jagged structure → document schema.

**PDF build test (independent):** Stub `pixi run build-pdf` to verify
toolchain. Can run in parallel.

**Artifact:** `EXPLORATION.md`. **Review:** Self-review (§6).

---

### Phase 3: Processing

**Goal:** Implement the strategy. Searches: selection, regions, background
estimation. Measurements: selection, correction chain. Phase 3 executes
the plan; it does not redesign it.

**Selection:**
- Default to MVA (BDT, NN) for multi-dimensional classification. Cuts
  acceptable only for preselection, single-variable, or tiny samples (<1000).
- If MVA: train, validate, optimize. Train ≥1 alternative architecture.
  Try multiclass if >2 physics classes. Check data/MC on classifier output.
  Sub-delegate training to sub-agent (§3a.5.1).
- Every cut must be motivated by a plot. Cutflow must be monotonically
  non-increasing (Category A if violated).

**Regions (searches):** Define CRs (enriched in backgrounds) and VRs
(between CR and SR, statistically independent).

**Background estimation (searches):** Estimate SR yields from CRs. Closure
test in VRs (p > 0.05 or Category A).

**Correction infrastructure (measurements):**
- Data/MC comparisons for all variables entering the observable, resolved
  by object category (Category A if missing for unfolded measurements)
- Response matrix: dimensions, diagonal fraction, condition number, efficiency
- Closure + stress tests on MC. Failure (p < 0.05) is Category A.
- Prototype full chain on data.
- Binning must be justified (resolution, statistics, physics features).

**Background estimation flow:** Phase 1 defines approach → Phase 2
validates feasibility → Phase 3 builds estimation inputs for Phase 4.

**Sensitivity optimization (when insufficient):** Maintain `sensitivity_log.md`.
Progress through qualitatively different strategies (optimize current → more
powerful discriminant → different inference strategy → revisit regions).
Stop when goal met OR 3+ approaches tried with marginal improvement.

**Artifact:** `SELECTION.md`. **Review:** 1-bot (§6).

---

### Phase 4: Statistical Analysis

Three sub-phases. **Both measurements and searches follow 4a → 4b → 4c.**

#### Phase 4a: Expected Results

**Goal:** Systematics, statistical model, expected results on Asimov only.

- Evaluate experimental + theory systematics as rate/shape variations
- Construct binned likelihood (Asimov data, systematic terms)
- Validate: NP pulls small, fit converges, results sensible
- Signal injection tests (searches) or closure tests (measurements)
- GoF: chi2/ndf AND toy-based p-value (saturated model)
- For measurements: expected result from MC pseudo-data, never real data.
  See `conventions/extraction.md` for extraction-specific protocol.
- For measurements: full covariance matrix (stat + per-syst + total) +
  comparison to ≥1 theory prediction using full covariance

**Artifact:** `INFERENCE_EXPECTED.md`. **Review:** 4-bot (§6).

#### Phase 4b: 10% Data Validation

**Goal:** Reality-check with 10% subsample + produce draft AN.

- 10% data (fixed seed), MC normalized to 10% luminosity
- Run full chain, evaluate GoF, NP pulls, impact ranking
- Compare to Phase 4a expected (overlay, chi2). Discrepancies documented.
- For extraction: include diagnostics sensitive to data/MC differences
  (not just the final quantity). See `conventions/extraction.md` check #5.
- **Draft AN:** Complete AN per `analysis-note.md`. Structure written here;
  Phases 4c/5 update results only.

**Artifact:** `INFERENCE_PARTIAL.md` + `ANALYSIS_NOTE_DRAFT.md`.
**Review:** 4-bot (§6) → **human gate** (§4.2).

#### Phase 4c: Full Data

**Goal:** Final results on full dataset.

- Full chain, post-fit diagnostics
- Compare to **both** 10% and expected. Flag >2σ disagreement with expected
  or disagreement with 10% beyond statistical scaling.
- Investigate anomalies (large NP pulls, poor GoF)

**Artifact:** `INFERENCE_OBSERVED.md`. **Review:** 1-bot (§6).

---

### Phase 5: Documentation

**Goal:** Final analysis note.

Phase 5 updates results in the 4b draft AN, polishes prose, renders PDF.
See `analysis-note.md` for full AN specification.

**Artifact:** `ANALYSIS_NOTE.md` + compiled PDF + `results/` directory.
**Review:** 5-bot (§6).

---
