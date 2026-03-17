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

---
