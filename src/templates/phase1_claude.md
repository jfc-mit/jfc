# Phase 1: Strategy

> **End goal.** This analysis produces a publication-quality analysis note
> for journal submission. Every phase contributes to that goal. Work should
> meet the standard of external scrutiny — a journal referee, a collaboration
> review committee, or a competing group doing the same measurement.

You are developing the analysis strategy for a **{{analysis_type}}** analysis.

**Start in plan mode.** Before writing any code or prose, produce a plan:
what literature you will query, what samples you expect, what the artifact
structure will be. Execute after the plan is set.

## Required deliverables

- Physics motivation and observable definition
- Sample inventory (data + MC)
- Selection approach with justification
- Systematic uncertainty plan
- Literature review from RAG corpus
- **Technique selection** — determine the analysis technique (unfolding,
  template fit, etc.) and justify the choice. This determines which
  technique-specific requirements apply in later phases.

## Completeness requirements

1. **Reference analyses.** Identify 2-3 published analyses closest in
   technique/observable. Tabulate their systematic programs. This table
   is a binding input to later reviews.

2. **Conventions check.** Read all applicable files in `conventions/`.
   Enumerate every required systematic source listed there. For each one,
   state in the strategy: "Will implement" or "Not applicable because [reason]."
   This enumeration is binding — Phase 4a reviews against it. Silent
   omissions are Category A findings.

## Review

This phase gets **3-bot review**. Three reviewer agents run in parallel:
1. Critical reviewer — finds everything wrong or missing
2. Constructive reviewer — identifies what would make this stronger
3. Arbiter — reads both reviews, issues PASS / ITERATE / ESCALATE

The arbiter should ITERATE unless the strategy is genuinely complete. A
strategy that omits systematic sources, lacks reference analyses, or has
unjustified technique choices should not PASS.

The reviewers will check:
- Is the approach motivated by the literature?
- Does the systematic plan cover standard sources (per conventions)?
- Are reference analyses identified with systematics tabulated?
- Are backgrounds complete and classified?
- Is the selection approach justified?
- Is the technique choice justified?

Findings are classified as:
- **(A) Must resolve** — blocks advancement
- **(B) Must fix before PASS** — weakens the analysis, must be resolved
- **(C) Suggestion** — style, clarity. Applied before commit, not re-reviewed

Write review findings to `review/REVIEW_NOTES.md`.
