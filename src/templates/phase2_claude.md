# Phase 2: Exploration

> **End goal.** This analysis produces a publication-quality analysis note
> for journal submission. Every phase contributes to that goal. Work should
> meet the standard of external scrutiny — a journal referee, a collaboration
> review committee, or a competing group doing the same measurement.

You are exploring the data and MC samples.

**Start in plan mode.** Before loading any data, produce a plan: which files
to inspect first, what variables to survey, what plots to make. Execute
after the plan is set.

## Required deliverables

- Sample inventory (files, trees, branches, event counts)
- Data quality assessment
- Key variable distributions with data/MC comparisons
- Variable ranking for discrimination power
- Preselection cutflow

## Output artifact

You MUST produce `exec/EXPLORATION.md` before Phase 3 begins.
This is a hard gate — the artifact is both the handoff document and the
proof that the phase was completed with appropriate rigor.

## RAG queries (mandatory)

Query the experiment corpus for:
1. Standard object definitions for this experiment (lepton ID, jet clustering, etc.)
2. Known data quality issues or detector effects relevant to the observables

Cite sources in the artifact.

## Rules

- Prototype on small subsets (~1000 events). Do not process full data to
  "see what's there."
- Append findings to experiment_log.md as you go. An empty experiment log
  at the end of this phase is a process failure.
- Self-review only — no external reviewer. Be thorough.

## Data discovery

Expect to discover the data format at runtime. To avoid wasting time/memory:
1. **Metadata first.** Inspect tree names, branch names, types before loading.
2. **Small slice of scalars.** Load ~1000 events of scalar branches first.
3. **Identify jagged structure.** Determine which branches are variable-length
   before bulk loading.
4. **Document the schema.** The discovered structure is artifact content.

## Plotting

Style setup: `import mplhep as mh; mh.style.use("CMS")`

Figure size: `figsize=(10*ncols, 10*nrows)` — always. No exceptions.

No `ax.set_title()` — captions in the note, not on axes.

Save as PDF + PNG, `bbox_inches="tight"`, `dpi=200`. Close after saving.

Reference figures in the artifact using:
```markdown
![Detailed caption describing what is plotted.](figures/filename.pdf)
```

## PDF build test

At the end of this phase, run a stub PDF build to verify the toolchain:
1. Create a minimal `phase5_documentation/exec/ANALYSIS_NOTE.md` with a
   title, one section heading, and one figure reference
2. Run `pixi run build-pdf`
3. Fix any issues (missing packages, broken pandoc flags) now

This catches toolchain problems early — not in Phase 5.

## Review

Self-review. Explicitly check:
- Sample inventory complete?
- Data quality checked?
- Experiment log updated?
- Distributions look physical?
