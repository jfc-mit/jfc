# Phase 4: Inference

> **End goal.** This analysis produces a publication-quality analysis note
> for journal submission. Every phase contributes to that goal. Work should
> meet the standard of external scrutiny — a journal referee, a collaboration
> review committee, or a competing group doing the same measurement.

You are building the statistical model and computing results.

**Start in plan mode.** Before writing any code, produce a plan: what
systematics you will evaluate, what validation checks you will run, what
the artifact structure will be. Execute after the plan is set.

## Required deliverables

- Statistical model or corrected spectrum with full uncertainties
- Systematic uncertainty evaluation
- Validation diagnostics
- Comparison to reference measurements

## Output artifacts and flow

**For measurements:** Phase 4a is the primary (and usually only) inference
phase. Phases 4b and 4c are skipped — there is nothing to blind. The human
gate follows the 4a review.

**For searches:** All three sub-phases are required:
- 4a → 4b (10% unblinding) → human gate → 4c (full unblinding)

| Sub-phase | Artifact | When |
|-----------|----------|------|
| 4a | `exec/INFERENCE_EXPECTED.md` | Always |
| 4b | `exec/INFERENCE_PARTIAL.md` | Search only |
| 4c | `exec/INFERENCE_OBSERVED.md` | Search only |

## Completeness requirements (critical)

1. **Systematic completeness table.** Compare your implemented sources
   against the reference analyses from Phase 1 and the conventions
   (read all applicable files in `conventions/`).

   Format:
   ```
   | Source | Conventions | Ref 1 | Ref 2 | This analysis | Status |
   ```
   Any MISSING source without justification is a blocker. The reviewer
   will check this table row by row.

## Technique-specific requirements

Read the Phase 1 strategy to determine which technique applies.

**For unfolding measurements:**
- **Prior-sensitivity check.** Repeat unfolding with a flat prior at nominal
  regularization. If any bin changes by >20%, the result is prior-dominated.
  Increase iterations, merge bins, or exclude.
- **Alternative method.** At least one independent unfolding method or
  cross-check (e.g., OmniFold, SVD, bin-by-bin).
- **Hadronization model.** If only one generator is available for the
  response matrix, document as a limitation. Data-driven reweighting is not
  a substitute for a genuine alternative-generator comparison.
- **Covariance matrix.** Full bin-to-bin covariance (stat + each systematic
  separately + total). Provide as tables/heatmaps in the artifact AND as
  machine-readable files (NumPy `.npy`, JSON, or CSV).

**For template fit / search analyses:**
- Pre-fit and post-fit data/MC agreement in all regions
- Nuisance parameter pulls and constraints
- Impact ranking of systematics
- Signal injection tests at known strengths

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

This phase gets **3-bot review**. Three reviewer agents run in parallel:
1. Critical reviewer — finds everything wrong or missing
2. Constructive reviewer — identifies what would make this stronger
3. Arbiter — reads both reviews, issues PASS / ITERATE / ESCALATE

The arbiter should ITERATE unless systematics are genuinely complete and
all validation checks pass. A systematic completeness table with MISSING
rows must not PASS.

Reviewers will check:
- Are systematics complete relative to conventions AND reference analyses?
- Do all validation checks pass?
- If chi2/ndf vs. a reference measurement exceeds 1.5, has it been investigated?
- Is the systematic completeness table present with all rows resolved?
- For measurements: is the full covariance matrix produced?

Findings are classified as:
- **(A) Must resolve** — blocks advancement
- **(B) Must fix before PASS** — weakens the analysis, must be resolved
- **(C) Suggestion** — style, clarity. Applied before commit, not re-reviewed

Write review findings to `review/REVIEW_NOTES.md`.
