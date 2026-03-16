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

**Both measurements and searches follow the same 4a → 4b → 4c structure:**
- **4a:** Statistical analysis — systematics, expected results. Artifact: `INFERENCE_EXPECTED.md`. No AN draft here.
- **4b:** 10% data validation. Compare to expected. Write full AN draft with 10% results. Review + PDF render. Human gate after review passes.
- **4c:** Full data. Compare to 10% and expected. Update AN with full results.

| Sub-phase | Artifact | Review |
|-----------|----------|--------|
| 4a | `exec/INFERENCE_EXPECTED.md` | 4-bot |
| 4b | `exec/INFERENCE_PARTIAL.md` + `ANALYSIS_NOTE_DRAFT.md` | 4-bot → human gate |
| 4c | `exec/INFERENCE_OBSERVED.md` | 1-bot |

## RAG queries (mandatory)

Query the experiment corpus for:
1. Systematic evaluation methods used in reference analyses
2. Published measurements for comparison (use `compare_measurements` for
   cross-experiment results)
3. Theory predictions or MC generator comparisons for the observable

Cite sources in the artifact.

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

**Goodness-of-fit (all analyses):**
- Report **both** chi2/ndf for quick assessment **and** toy-based p-value
  using the saturated model GoF statistic where binned results are involved.
  chi2/ndf ~ 1 is good; >>1 indicates mismodeling; <<1 indicates
  overestimated uncertainties.
- For binned results: use the saturated model as the GoF reference.
  Generate toys and report the p-value with the toy distribution.

**For template fit / search analyses:**
- Pre-fit and post-fit data/MC agreement in all regions
- Nuisance parameter pulls and constraints
- Impact ranking of systematics
- Signal injection tests at known strengths

**For extraction / counting measurements** (e.g., double-tag, ratio, branching fraction):

Extraction measurements solve equations using MC-derived parameters to extract
a physical quantity from observed counts. The result depends critically on
these parameters. The following are required:

- **Independent closure test (Category A if fails).** Apply the full
  extraction procedure to a statistically independent MC sample (e.g.,
  train/test split, or a held-out MC set not used for parameter estimation).
  Extract the quantity and compare to MC truth. The pull must be < 2σ.
  An algebraic closure (using the same MC for both parameters and test counts)
  is necessary but not sufficient — it only verifies the solver, not the method.
- **Parameter sensitivity table.** For each MC-derived input parameter
  (efficiency, correlation factor, mistag rate, etc.), compute the derivative
  dResult/dParam and the parameter's uncertainty σ_param. Report
  |dResult/dParam| × σ_param for each. If any single parameter contributes
  > 5× the data statistical uncertainty, flag it as a dominant systematic
  and investigate whether a data-driven constraint exists.
- **Operating point stability.** Scan the result vs. the primary operating
  point (BDT cut, selection threshold, etc.) over a range that spans at least
  2× the optimized region. The extracted quantity should be flat within
  uncertainties. A statistically significant trend indicates method bias
  (MC parameters have cut-dependent errors that don't cancel). This is
  Category A if the trend exceeds the quoted systematic uncertainty.
- **Expected results from MC pseudo-data, not real data.** The Phase 4a
  "expected result" must be computed on MC pseudo-data (counts derived from
  MC truth fractions and efficiencies, optionally Poisson-fluctuated) — never
  on actual data counts. Applying the extraction to real data counts in 4a
  makes 4c a tautology. The purpose of 4a is to validate the method and
  quantify expected precision before seeing data.

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

This phase gets **4-bot review**. Four reviewer agents (first three in parallel):
1. Physics reviewer — reviews as a senior collaboration member; receives only
   the physics prompt and artifact (no methodology or conventions)
2. Critical reviewer — finds everything wrong or missing
3. Constructive reviewer — identifies what would make this stronger
4. Arbiter — reads all reviews, issues PASS / ITERATE / ESCALATE

The arbiter should ITERATE unless systematics are genuinely complete and
all validation checks pass. A systematic completeness table with MISSING
rows must not PASS.

Reviewers will check:
- Are systematics complete relative to conventions AND reference analyses?
- Do all validation checks pass?
- If GoF vs. a reference measurement is poor, has it been investigated?
- Is the systematic completeness table present with all rows resolved?
- For measurements: is the full covariance matrix produced?

Findings are classified as:
- **(A) Must resolve** — blocks advancement
- **(B) Must fix before PASS** — weakens the analysis, must be resolved
- **(C) Suggestion** — style, clarity. Applied before commit, not re-reviewed

Write review findings to `review/REVIEW_NOTES.md`.
