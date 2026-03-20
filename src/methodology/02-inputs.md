## 2. Inputs

### 2.1 Physics Prompt

A brief natural-language description of the physics goal. States the target
and constraints (dataset, final state, energy range). Need not specify
methodology.

### 2.2 Experiment Context (When Available)

The agent **may** have access to a RAG corpus (SciTreeRAG over collaboration
publications) exposed as MCP tools. When available, query for: detector
specs, object definitions, MC samples, performance numbers, prior analyses.
Cite all retrieved information.

**When RAG is not available:** Proceed using training knowledge and any
documentation in a `docs/` directory. Mark uncorroborated claims as
"unverified — based on training knowledge" and flag for human review.

**Retrieve, then verify.** Data is ground truth; the corpus provides
starting points. Discrepancies → trust data, document the inconsistency.

**When retrieval fails:** Log the failed query in `retrieval_log.md`. Try
rephrased queries. If still unhelpful, proceed with training knowledge and
flag the gap.

### 2.3 Numeric Constants and Reference Values

**Never quote numeric constants from training data.** Every number that
enters the analysis — PDG masses, widths, branching ratios, coupling
constants, cross-sections, world-average measurements — must come from
a retrievable, citable source. Acceptable sources:

1. **RAG corpus** — search for the value, cite the paper ID and table/equation
2. **Web fetch** — fetch from PDG live tables, HEPData, or official sources
3. **Published paper** — cite with full reference

LLM training data is NOT a source. The training cutoff may be years old,
values may be misremembered, and there is no way to verify or cite them.
An analysis that uses $M_Z = 91.1876$ GeV must cite where that number
came from — not assert it from memory.

**This applies to:** particle masses, widths, coupling constants, SM
predictions, published cross-sections, luminosity values, beam energies,
QCD coefficients, radiative correction formulae, any number used as input
to the analysis or as a validation target.

**At review:** Any numeric constant without a citation is Category A.
The reviewer must verify that validation targets (PDG values, reference
measurements) were fetched from a source, not recalled from training data.

### 2.4 Self-Consistency Check for Derived Constants

For every derived constant used in the extraction (e.g., $R_l^{\mathrm{EW}}$,
QCD correction coefficients, radiative correction parameters), verify
self-consistency before using it: substitute the PDG world-average values
into the formula and confirm it reproduces the known PDG result within
the quoted precision. A discrepancy exceeding ~1% indicates a wrong input,
a convention mismatch, or an approximation level that doesn't match the
analysis precision. This check catches errors like using a Born-level
parametrization where higher-order corrections matter.

### 2.5 External Input Validation

When the analysis uses an external measurement as input (e.g., published
leptonic widths, theoretical cross-sections, borrowed efficiencies),
the executor must attempt a data-driven estimate of the same quantity
as a cross-check — even a rough one.

**Protocol:**
1. **Identify** every external input: list the quantity, its source, and
   its role in the extraction chain.
2. **Estimate from data** where feasible. Even an order-of-magnitude or
   low-precision estimate is valuable. Examples: if using a published
   $\Gamma_l$, attempt to estimate the leptonic rate from the data
   (even with poor efficiency); if using a theoretical cross-section,
   compare to a simple counting estimate; if using MC-derived
   efficiencies, cross-check with data-driven tag-and-probe.
3. **Compare.** If the data-driven estimate is broadly consistent with
   the external input (within ~2σ of its own uncertainty), use the
   external input as the primary value and document the cross-check.
   If the estimates are inconsistent, investigate before proceeding —
   the disagreement may indicate a calibration issue or a problem with
   the external input's applicability.
4. **Report both.** When an external input dominates the uncertainty
   (contributes >30% of the total), report the result both with the
   external input and with the data-driven estimate (if feasible). This
   shows the reader what the measurement would look like with full
   internal information vs. borrowed precision.
5. **Document infeasibility.** If no data-driven estimate is possible
   (e.g., no leptonic events in a hadronic-only dataset), document why
   and what would be needed to make it feasible.

This is not about replacing external inputs with worse estimates. It is
about verifying that external inputs are compatible with the data before
trusting them, and showing the reader what the analysis can determine
independently.

---
