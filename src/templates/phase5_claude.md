# Phase 5: Documentation

> Read `methodology/03-phases.md` → "Phase 5" for full requirements.
> Read `methodology/appendix-plotting.md` for figure standards.
> Read `methodology/appendix-checklist.md` for the review checklist.

You are producing the final analysis note for a **{{analysis_type}}** analysis.

**Start in plan mode.** Before writing any prose, produce a plan: the AN
section structure, which figures go where, which results tables are needed.
Execute after the plan is set.

## Output artifact

`exec/ANALYSIS_NOTE.md` — publication-quality analysis note in pandoc-compatible
markdown.

## Methodology references

- Phase requirements: `methodology/03-phases.md` → Phase 5
- Review protocol: `methodology/06-review.md` → §6.2 (5-bot), §6.4
- Plotting: `methodology/appendix-plotting.md`
- Checklist: `methodology/appendix-checklist.md`

## Pre-review gate

Before submitting for review, these must succeed:
1. `pixi run all` — full analysis chain reproduces from scratch
2. `pixi run build-pdf` — PDF compiles with all figures rendering

If either fails, fix it before requesting review.

## Analysis note structure

The AN must be **pandoc-compatible markdown** (see root CLAUDE.md for syntax).

**Cross-references and citations:**
- Every figure MUST have a label: `![Caption](figures/name.pdf){#fig:name}`
- Reference as `@fig:name`. At sentence start: `Figure @fig:name`. Never `[-@fig:...]`.
- Citations: `[@key]` with `references.bib`. BibTeX entries must include
  `doi`, `url` (journal or arXiv link), and `eprint` (arXiv ID) fields
  where available. Use `unsrt`-style formatting as a reference. Use
  `get_paper` for RAG-discovered papers — always retrieve full metadata.
- Tables: `{#tbl:name}` and `@tbl:name`. Equations: `{#eq:name}` and `@eq:name`.

Required sections:

1. **Introduction** — physics motivation, observable definition, prior measurements
2. **Data samples** — experiment, sqrt(s), luminosity, MC generators, cross-sections, event counts
3. **Event selection** — every cut with motivation, distribution plot, efficiency
4. **Corrections / unfolding** (measurements) — full procedure, closure tests
5. **Systematic uncertainties** — one subsection per source: method, impact
6. **Statistical method** — likelihood, fit validation, uncertainty propagation
7. **Results** — primary result with full uncertainties, per-bin tables
8. **Comparison to prior results and theory** — overlay plots, chi2/p-values
9. **Conclusions** — summary, precision, dominant limitations
10. **Future directions** — concrete roadmap
11. **Appendices** — covariance matrices as tables, extended cutflow, auxiliary plots

**Cross-checks belong with their relevant result, not in a separate
section.** A BDT cross-check goes in the selection section. An alternative
inference strategy goes in the statistical method section. An operating
point stability scan goes in the systematics section. If a cross-check is
large (>2 pages), move it to an appendix with a forward reference from the
relevant section. Do not create a standalone "Cross-checks" section — it
disconnects the check from its context.

## Key requirements

These are the critical items for the analysis note. See
`methodology/03-phases.md` → Phase 5 for full details.

- **The AN is the complete record — not an executive summary or a
  journal-length paper.** Every detail needed to reproduce the analysis
  from scratch must be in the note. If a reviewer has to read the code to
  understand a choice, the AN has a gap.
- **Depth calibration.** A measurement with ~5 systematics, ~3 cross-checks,
  ~6 cuts, ~18 bins should produce ~50-100 rendered pages. Under 30 pages
  means detail is missing.
- **Per-systematic subsections.** Each systematic source gets its own
  subsection: description, method, impact figure, per-bin table. A summary
  table alone is insufficient.
- **Cross-checks with their results.** Each cross-check appears as a
  subsection within the relevant results section (not in a standalone
  "Cross-checks" section). Include comparison plots, chi2/p-value, and
  interpretation. One-liners are not subsections.
- **Completeness test.** A physicist unfamiliar with the analysis should be
  able to read the AN alone and understand every choice, reproduce every
  number, and evaluate whether conclusions are supported.
- **Machine-readable results.** `results/` directory with CSV/JSON for
  spectra, uncertainties, and covariance matrices. Results that exist only
  in a PDF are not reusable.

## Figure setup

Symlink phase figures into `phase5_documentation/exec/figures/` so that
`![caption](figures/name.pdf)` references resolve correctly when pandoc
compiles the PDF. The `build_pdf.py` script collects figures automatically;
if setting up manually:
```bash
mkdir -p phase5_documentation/exec/figures
ln -sf ../../phase*/figures/*.pdf phase5_documentation/exec/figures/
```

## Building the PDF

Run `pixi run build-pdf` from the analysis root. This converts
`ANALYSIS_NOTE.md` to PDF via pandoc with xelatex, numbered sections,
TOC, and half-page-width figures.

**Never use an LLM to convert markdown to LaTeX.** Pandoc handles this.

## Review

**5-bot review** — see `methodology/06-review.md` for protocol.
Write findings to `review/REVIEW_NOTES.md`.
