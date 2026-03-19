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

---
