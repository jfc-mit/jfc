# Phase 5: Documentation

> **End goal.** This analysis produces a publication-quality analysis note
> for journal submission. Every phase contributes to that goal. Work should
> meet the standard of external scrutiny — a journal referee, a collaboration
> review committee, or a competing group doing the same measurement.

You are producing the final analysis note.

## Reviewer framing

The review will evaluate this note **as a standalone document**, the way a
journal referee would. The reviewer will not consult experiment logs or
phase artifacts — only the note itself.

The question: "Based solely on what is written here, am I convinced this
result is correct and complete?"

## Required checks

- Every systematic source in the uncertainty table: is the method described,
  is the magnitude reported, is validation evidence shown?
- Every comparison to a reference: is a quantitative compatibility metric
  given and interpreted?
- Does the note contain enough detail for an independent analyst to
  reproduce the measurement?
- Conventions check (final):
   - `conventions/unfolding.md`

  Is anything required there that is absent from the note?

## Depth requirements

The AN is the complete record — not a summary. Minimum expectations:
- One subsection per systematic source (not just a summary table)
- One subsection per cross-check with quantitative result
- Per-cut event selection with individual distributions and efficiencies
- Full covariance matrix in appendix (table, not just figure)
- Machine-readable `results/` directory (CSV/JSON for spectrum, covariance)
- LaTeX math throughout (`$\alpha_s$` not `alpha_s`)
- `pixi.toml` must have an `all` task for full reproducibility

A measurement analysis with ~5 systematics, ~3 cross-checks, ~6 cuts, and
~18 bins should produce ~50-100 rendered pages. Under 30 pages means
detail is missing.

## Review

This phase gets 3-bot review. The cost of iteration here is acceptable —
better to loop than to publish an incomplete result.
