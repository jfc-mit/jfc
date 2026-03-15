# Phase 4: Inference

> **End goal.** This analysis produces a publication-quality analysis note
> for journal submission. Every phase contributes to that goal. Work should
> meet the standard of external scrutiny — a journal referee, a collaboration
> review committee, or a competing group doing the same measurement.

You are building the statistical model and computing results.

## Required deliverables

- Statistical model or corrected spectrum with full uncertainties
- Systematic uncertainty evaluation
- Validation diagnostics
- Comparison to reference measurements

## Output artifacts

Phase 4 has sub-phases, each with its own artifact (hard gates):
- 4a: `exec/INFERENCE_EXPECTED.md` — expected results, systematics, validation
- 4b: `exec/INFERENCE_PARTIAL.md` — partial data results + draft AN
- 4c: `exec/INFERENCE_OBSERVED.md` — full observed results

See methodology Section 3.0 for the gate protocol.

## Completeness requirements (critical)

1. **Systematic completeness table.** Compare your implemented sources
   against the reference analyses from Phase 1 and the conventions:
   - `conventions/unfolding.md`

   Format:
   ```
   | Source | This analysis | Ref 1 | Ref 2 | Status |
   ```
   Any MISSING source without justification is a blocker.

2. **Prior-sensitivity check.** Repeat the unfolding with a flat prior at
   nominal regularization. If any bin changes by >20%, the result is
   prior-dominated there. Increase iterations, merge bins, or exclude.

3. **Alternative method.** At least one independent unfolding method or
   cross-check (e.g., OmniFold, SVD, bin-by-bin) must be available.

4. **Hadronization model.** If only one generator is available for the
   response matrix, document this as a limitation. Data-driven reweighting
   is not a substitute for a genuine alternative-generator comparison.


## Review

This phase gets 3-bot review. Reviewers will check:
- Are systematics complete relative to conventions AND reference analyses?
- Do all validation checks pass?
- If chi2/ndf vs. a reference measurement exceeds 1.5, has it been investigated?
