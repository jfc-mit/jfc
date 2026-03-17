## 5. Artifact Format

### 5.1 Experiment Log

Each phase maintains `experiment_log.md` — an append-only lab notebook of
what was tried and what happened. Never deleted, never modified. An empty
log at phase end is a review finding.

Append after every material decision, discovery, or failed attempt. The
formal artifact references the log for alternatives explored. Agents read
the log on demand (not loaded by default) to avoid re-trying failed
approaches.

### 5.2 Primary Artifact

Every phase produces a markdown artifact — the handoff to subsequent phases
and the permanent record. Artifacts must be **self-contained**: a reader
with only the artifact and experiment corpus should understand what was done
and why.

**Artifacts are AN source material.** Phase 4 artifacts must be written at
publication quality — the Phase 4b/5 agent reads them to draft the analysis
note. Terse artifacts produce terse AN sections.

**Standard sections:**
1. **Summary** — what was accomplished (1 paragraph)
2. **Method** — reproducible detail
3. **Results** — tables, figures (by path), numbers with uncertainties
4. **Validation** — checks performed, quantitative outcomes
5. **Open issues** — what subsequent phases should be aware of
6. **Code reference** — `pixi run <task>` commands that produced results

**Figure captions must be self-contained** and follow the format:
`<Plot name>. <Full description in complete sentences.>` A caption must
be 2-5 sentences: name the plot, describe what is shown (axes, curves,
markers, bands), state the key conclusion, and note any selection or
normalization. Anything under two full sentences is Category A. See
`appendix-plotting.md` § "Captions" for examples of good and bad captions.

**Supplementary files** (`.npz`, `.json`, workspaces, trained models) must
include a brief description in the artifact: what the file contains, how to
load it, which pixi task produced it.

**Supplementary artifacts:** `UPSTREAM_FEEDBACK.md` (non-blocking feedback
to an earlier phase) and `REGRESSION_TICKET.md` (regression investigation
output). See §6.7.

---
