# Phase 3: Selection and Modeling

> **End goal.** This analysis produces a publication-quality analysis note
> for journal submission. Every phase contributes to that goal. Work should
> meet the standard of external scrutiny — a journal referee, a collaboration
> review committee, or a competing group doing the same measurement.

You are implementing the analysis approach defined in the Phase 1 strategy.
Read the strategy first — it determines what this phase must deliver.

## Required deliverables

- Final object definitions
- Event selection with optimization
- Cutflow table with data and MC yields
- For searches: background estimation, control/validation regions, closure tests
- For measurements: correction chain (response matrix, unfolding, closure tests)

## Output artifact

You MUST produce `exec/SELECTION.md` before Phase 4 begins.
This is a hard gate — see methodology Section 3.0.

## Technique-specific: Unfolding

Before constructing the response matrix:
- Produce data/MC comparison plots for ALL kinematic variables entering the
  observable, resolved by reconstructed object category
- Document the level of agreement per category
- Identify and document any discrepancies

These plots are evidence that the MC response model is adequate. They are
required — not optional — even if observable-level data/MC looks fine.


## Review

This phase gets 1-bot review. The reviewer will check:
- Is every cut motivated by a plot?
- Does the background model / correction close?
- Are particle-level inputs validated per object category with data/MC plots?
  (Category A if missing for unfolded measurements)

