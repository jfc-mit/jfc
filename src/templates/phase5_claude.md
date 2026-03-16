# Phase 5: Documentation

> **End goal.** This analysis produces a publication-quality analysis note
> for journal submission. Every phase contributes to that goal. Work should
> meet the standard of external scrutiny — a journal referee, a collaboration
> review committee, or a competing group doing the same measurement.

You are producing the final analysis note.

**Start in plan mode.** Before writing any prose, produce a plan: the AN
section structure, which figures go where, which results tables are needed.
Execute after the plan is set.

## Pre-review gate

Before submitting for review, these must succeed:
1. `pixi run all` — full analysis chain reproduces from scratch
2. `pixi run build-pdf` — PDF compiles with all figures rendering

If either fails, fix it before requesting review.

## Analysis note structure

The AN must be written as **pandoc-compatible markdown** (see root CLAUDE.md
for syntax rules).

**Cross-references and citations:**
- Every figure MUST have a label: `![Caption](figures/name.pdf){#fig:name}`
- Reference figures as `@fig:name` (produces "fig. X"). At sentence start:
  `Figure @fig:name`. Never use `[-@fig:...]`.
- Citations use `[@key]` syntax with `references.bib` in the exec directory.
  Populate the bib file as you add citations. `build-pdf` uses `--citeproc`.
  BibTeX entries must include DOI and/or INSPIRE-HEP URL. When citing a paper
  discovered via RAG, use `get_paper` to retrieve its metadata and construct a
  proper BibTeX entry with the INSPIRE key. Never cite as bare INSPIRE IDs.
- Tables: `{#tbl:name}` and `@tbl:name`. Equations: `{#eq:name}` and `@eq:name`.

It must contain at minimum:

1. **Introduction** — physics motivation, observable definition, prior
   measurements with citations
2. **Data samples** — complete inventory (experiment, √s, luminosity, MC
   generators, cross-sections, event counts)
3. **Event selection** — every cut with: physical motivation, distribution
   plot showing the effect, numerical efficiency (per-cut and cumulative)
4. **Corrections / unfolding** (measurements) — full procedure, response
   matrix, regularization, closure tests, stress tests
5. **Systematic uncertainties** — one subsection per source: what it is,
   how evaluated, impact on result (table + figure)
6. **Cross-checks** — one subsection per cross-check: what is tested,
   quantitative result (ratio plots, chi2, p-values), interpretation
7. **Statistical method** — likelihood, fit validation, uncertainty
   propagation
8. **Results** — primary result with full uncertainties, per-bin tables
9. **Comparison to prior results and theory** — overlay plots with ratio
   panels, chi2/p-value using full covariance. "Qualitative consistency"
   is insufficient when data points are available.
10. **Conclusions** — summary, precision, dominant limitations
11. **Future directions** — concrete roadmap
12. **Appendices** — covariance matrices (as tables, not just figures),
    extended cutflow, auxiliary distributions, per-bin systematic tables

### Depth calibration

The AN is the complete record — not a summary. A measurement analysis with
~5 systematics, ~3 cross-checks, ~6 cuts, and ~18 bins should produce
~50-100 rendered pages. Under 30 pages means detail is missing.

Machine-readable `results/` directory required (CSV/JSON for spectrum,
covariance matrices).

## Figure setup

Symlink phase figures into `phase5_documentation/exec/figures/` so that
`![caption](figures/name.pdf)` references resolve correctly when pandoc
compiles the PDF.

## Plotting

Style setup: `import mplhep as mh; mh.style.use("CMS")`

Figure size: `figsize=(10*ncols, 10*nrows)` — always. No exceptions.

No `ax.set_title()` — captions in the note, not on axes.

Save as PDF + PNG, `bbox_inches="tight"`, `dpi=200`. Close after saving.

Reference figures in the artifact using:
```markdown
![Detailed caption describing what is plotted.](figures/filename.pdf)
```

## Building the PDF

Run `pixi run build-pdf` from the analysis root. This converts
`ANALYSIS_NOTE.md` to PDF via pandoc with xelatex, numbered sections,
TOC, and half-page-width figures.

**Never use an LLM to convert markdown to LaTeX.** Pandoc handles this.

## Review

Phase 5 uses **5-bot review** — the extended review that is the primary
bug-catching mechanism for the entire analysis:

1. **Physics reviewer** — receives ONLY the physics prompt and the AN.
   Reviews as a senior collaboration member (ARC/L2 convener): "Is this
   physics correct? Is it complete? Would I approve this?"
2. **Critical reviewer** — reads the AN as a journal referee would. Finds
   physics errors, methodological gaps, missing evidence. Does NOT consult
   experiment logs or phase artifacts — only the note itself.
3. **Constructive reviewer** — identifies what would strengthen the analysis.
   Proposes concrete improvements.
4. **Rendering reviewer** — runs `pixi run build-pdf`, then uses the Read
   tool to open the compiled PDF (`phase5_documentation/exec/ANALYSIS_NOTE.pdf`)
   for visual inspection. Checks:
   - Do all figures render (not broken/missing)?
   - Does math compile correctly (`$\alpha_s$` not garbled)?
   - Is the layout readable (no overlapping text, no clipped figures)?
   - Are all cross-references and figure numbers resolved?
   - Are page breaks sensible (no orphaned headings, no half-empty pages)?
5. **Arbiter** — reads all four reviews, classifies findings, issues
   PASS / ITERATE / ESCALATE.

### Regression triggers

Regression can trigger at any review (see Phase Regression in root CLAUDE.md),
but Phase 5 is the most common trigger point because the full analysis is
visible for the first time. When the critical or constructive reviewer finds
a **physics issue** traceable to an earlier phase, the arbiter classifies it
as a **regression trigger** — earlier phases must be re-run.

Examples of regression triggers:
- A systematic source from conventions is missing from the AN
- A closure test that should have been done in Phase 3 was skipped
- The correction method has a flaw not caught in Phase 4 review
- A background was omitted from the systematic evaluation

Examples of NON-regression (Phase 5 iteration only):
- Axis labels are wrong on a figure
- A caption is missing or unclear
- Math notation is inconsistent
- A section is too brief and needs expansion

### Reviewer checklist

The question: "Based solely on what is written here, am I convinced this
result is correct and complete?"

- Every systematic source in the uncertainty table: method described,
  magnitude reported, validation evidence shown?
- Every comparison to a reference: quantitative compatibility metric given?
- Could an independent analyst reproduce the measurement from the note alone?
- Conventions check (final): read all applicable files in `conventions/`.
  Is anything required there that is absent from the note?
- Per-systematic subsections present (not just a summary table)?
- Per-cross-check subsections present with quantitative results?
- `results/` directory populated with machine-readable files?
- Cosmetic checklist:
  - √s and energy labels match the actual dataset
  - Experiment name correct in all figure text
  - No figure titles (`ax.set_title()`)
  - Axis labels include units
  - Luminosity / event count annotations match data sample
  - Legend entries match what is actually plotted
  - Consistent aspect ratios and font sizes

Findings are classified as:
- **(A) Must resolve** — blocks publication
- **(B) Must fix before PASS** — weakens the analysis, must be resolved
- **(C) Suggestion** — style, clarity. Applied before commit, not re-reviewed

The cost of iteration here is acceptable — better to loop than to publish
an incomplete result.

Write review findings to `review/REVIEW_NOTES.md`.
