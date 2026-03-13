## 8. Context Management

### 8.1 Artifacts as Handoffs

The only information that crosses phase boundaries is the written artifact. No
conversation history, no shared variables, no implicit state. Each agent session
starts with:

1. This methodology spec (~4 pages)
2. Upstream phase artifacts (~2-5 pages each)
3. The physics prompt (~1 paragraph)
4. Access to the experiment retrieval corpus

Even at Phase 5, the total input is bounded at ~20-25 pages. Context does not
accumulate unboundedly.

### 8.2 What Goes Where

- **Artifact:** Decisions, results, reasoning, key figures (by path), validation
  outcomes. Everything a reader needs to evaluate the analysis.
- **Scripts directory:** Code that produced the results. Referenced from the
  artifact for reproducibility, but not read by downstream phases.
- **Supplementary files:** Full tables, workspaces, trained models. Referenced
  from the artifact, consulted only when needed.

### 8.3 Handling Large Outputs

If a phase produces extensive tabular data, the artifact includes a summary
table with the most impactful entries, references the full table as a
supplementary file, and states conclusions in prose.

---
