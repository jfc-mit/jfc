# Phase 3: Selection and Modeling

> **End goal.** This analysis produces a publication-quality analysis note
> for journal submission. Every phase contributes to that goal. Work should
> meet the standard of external scrutiny — a journal referee, a collaboration
> review committee, or a competing group doing the same measurement.

You are implementing the analysis approach defined in the Phase 1 strategy.
Read the strategy first — it determines what this phase must deliver.

**Start in plan mode.** Before writing any code, produce a plan: what scripts
you will write, what selection you will implement, what figures you will
produce, what the artifact structure will be. Execute after the plan is set.

## Required deliverables

- Final object definitions
- Event selection with optimization
- Cutflow table with data and MC yields
- For searches: background estimation, control/validation regions, closure tests
- For measurements: correction chain (response matrix, unfolding, closure tests)

## Output artifact

You MUST produce `exec/SELECTION.md` before Phase 4 begins.
This is a hard gate — the artifact is both the handoff document and the
proof that the phase was completed with appropriate rigor.

## Technique-specific requirements

Read the Phase 1 strategy to determine which technique applies.

**For unfolding measurements:**
- Produce data/MC comparison plots for ALL kinematic variables entering the
  observable, resolved by reconstructed object category
- Document the level of agreement per category
- Identify and document any discrepancies
- These plots are evidence that the MC response model is adequate — required
  even if observable-level data/MC looks fine

**For template fit / search analyses:**
- Control region definitions with purity and kinematic relationship to SR
- Validation region closure tests (predicted vs. observed, chi2)

## Plotting

Style setup: `import mplhep as mh; mh.style.use("CMS")`

Figure size: `figsize=(10*ncols, 10*nrows)` — always. No exceptions.

No `ax.set_title()` — captions in the note, not on axes.

Save as PDF + PNG, `bbox_inches="tight"`, `dpi=200`. Close after saving.

Reference figures in the artifact using:
```markdown
![Detailed caption describing what is plotted.](figures/filename.pdf)
```

## Review

This phase gets **1-bot review** — a single critical reviewer. The reviewer
classifies findings as:
- **(A) Must resolve** — blocks advancement
- **(B) Must fix before PASS** — weakens the analysis, must be resolved
- **(C) Suggestion** — style, clarity. Applied before commit, not re-reviewed

The executor addresses Category A and B items and re-submits. No arbiter
needed. A fresh reviewer is added each iteration. Warn after 4 iterations,
escalate after 6.

The reviewer will check:
- Is every cut motivated by a plot?
- Does the background model / correction close?
- Per-category data/MC validation done? (Category A if missing for unfolded
  measurements)
- Cutflow complete with per-cut and cumulative efficiencies?

Write review findings to `review/REVIEW_NOTES.md`.
