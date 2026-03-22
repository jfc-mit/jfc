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

**AN versioning.** The analysis note is phase-stamped and never overwritten:
`ANALYSIS_NOTE_{phase}_v{N}.{md,tex,pdf}`. Each phase (4a, 4b, 4c, 5)
produces a new phase-stamped v1; review/fix cycles within a phase increment
the version (v2, v3, ...). All versions are preserved on disk for audit and
comparison. Each phase's note writer reads the latest version from the
previous phase and produces a new phase-stamped v1.

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

**Dead-end approaches.** The experiment log records all approaches
tried, including failures. The AN presents the variable survey, the
selection rationale, the final method, and the result.

Any approach that was seriously attempted and rejected (e.g., a BDT
tagger rejected for data/MC disagreement, an alternative unfolding
method that failed closure) must be documented with **evidence** in
an appendix subsection:
1. What was tried (1-2 sentences)
2. Why it failed — with a quantitative criterion (e.g., "data/MC
   chi2/ndf > 5 on 3 of 13 input variables", "closure test bias
   of 15% in forward bins")
3. At least one diagnostic figure showing the failure mode (e.g.,
   the data/MC comparison on the BDT score, the failed closure
   test residuals). The figure must be produced and saved during
   the phase that rejected the approach.
4. What the analysis uses instead and why it's better (1 sentence)

"Rejected due to data/MC disagreement" without showing the
disagreement is Category B — the reader and reviewer cannot
assess whether the rejection was justified without seeing the
evidence. The diagnostic figures are produced in Phase 3 (where
approaches are compared) and must be preserved for the AN.

Purely exploratory dead ends (e.g., trying a cut value that gave
worse S/B) do not need appendix subsections — a sentence in the
experiment log suffices. The threshold: if the approach involved
writing and running code, its failure deserves a figure.

**Numerical self-consistency.** Every numerical value in the AN must
appear consistently wherever it is quoted — per-section tables, summary
tables, discussion prose, derived-quantity calculations, and appendix
tables. When a fix cycle changes a result, ALL instances must be
updated. The `results/*.json` files are the single source of truth;
the AN is a rendering of those values into prose. A per-section table
that contradicts the summary table is Category A regardless of which
one is correct — the inconsistency itself is the problem. See the
fixer agent's PROPAGATE step and the note writer's NUMBERS CONSISTENCY
LINT for the enforcement mechanisms.

**Supplementary files** (`.npz`, `.json`, workspaces, trained models) must
include a brief description in the artifact: what the file contains, how to
load it, which pixi task produced it.

**Supplementary artifacts:** `UPSTREAM_FEEDBACK.md` (non-blocking feedback
to an earlier phase) and `REGRESSION_TICKET.md` (regression investigation
output). See §6.7.

---
