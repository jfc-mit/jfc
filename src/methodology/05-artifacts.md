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
`<Plot name>. <Context and conclusion.>` A caption must be 2-4 sentences:
name the plot, state context not visible in the plot (selection,
normalization, what this validates), and give the key conclusion. **Do not
restate what is already in the legend or axis labels** — the caption adds
information the plot alone cannot convey. Anything under two full sentences
is Category A. See `appendix-plotting.md` § "Captions" for examples.

**Caption co-generation.** Every figure must have a draft caption written
at the time the figure is produced — in the same script or in the artifact
that first references it. Captions written hours or phases after the plot
was made lose the context of what the plot shows and why. The Phase 5 AN
writing subagent refines and polishes these draft captions, but it should
never have to write captions from scratch for figures it didn't produce.

**Flagship figures.** Phase 1 defines ~6 flagship ("money") figures that
would represent the measurement in a journal paper. These are produced at
the highest quality in Phase 5 and receive extra attention at review:
tighter axis limits, careful legend placement, considered color choices.
The flagship list propagates from the strategy artifact through to the
AN writing subagent. Every flagship figure must appear in the Results or
Comparison section of the AN, not buried in an appendix.

**Supplementary files** (`.npz`, `.json`, workspaces, trained models) must
include a brief description in the artifact: what the file contains, how to
load it, which pixi task produced it.

**Supplementary artifacts:** `UPSTREAM_FEEDBACK.md` (non-blocking feedback
to an earlier phase) and `REGRESSION_TICKET.md` (regression investigation
output). See §6.7.

---
