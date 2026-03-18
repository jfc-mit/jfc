# Phase 5: Documentation

> Read `methodology/analysis-note.md` for the full AN specification.
> Read `methodology/03-phases.md` → "Phase 5" for phase requirements.
> Read `methodology/appendix-plotting.md` for figure standards.
> Read `methodology/appendix-checklist.md` for the review checklist.

You are producing the final analysis note for a **{{analysis_type}}** analysis.

## Phase 5 has two separate sub-tasks

These should be handled by **separate subagents**:

### Sub-task 1: Figures (code-writing subagent)

Produce any AN-specific figures not already generated in Phases 2-4.
Read data/MC files, write plotting scripts, save to
`phase5_documentation/exec/figures/`. Also symlink existing phase figures:

```bash
ln -sf ../../../phase2_exploration/figures/*.pdf phase5_documentation/exec/figures/
ln -sf ../../../phase3_selection/figures/*.pdf phase5_documentation/exec/figures/
ln -sf ../../../phase4_inference/figures/*.pdf phase5_documentation/exec/figures/
```

The AN typically needs ~30+ figures. Phases 2-4 produce some, but the AN
usually needs additional per-variable distribution plots, per-cut before/after
comparisons, and per-systematic impact figures.

**Figure path verification (mandatory).** After aggregating figures, run:
```bash
# Verify every figure reference in the AN resolves to a file
grep -oP 'figures/[^)]+\.pdf' exec/ANALYSIS_NOTE.md | sort -u | while read f; do
  [ -f "exec/$f" ] || echo "MISSING: $f"
done
```
Any missing figure is Category A. Fix before proceeding to the AN
writing subagent.

### Sub-task 2: AN writing (prose-writing subagent)

**This subagent does NOT read data files or write code.** It reads:
- All phase artifacts (STRATEGY.md, EXPLORATION.md, SELECTION.md,
  INFERENCE_EXPECTED.md, INFERENCE_OBSERVED.md)
- The figures directory (to reference figure paths)
- The conventions files (for completeness checks)
- The experiment log

And writes: `exec/ANALYSIS_NOTE.md` — the complete analysis note.

**The gold standard:** a physicist who has never seen the analysis should
be able to reproduce every number from the AN alone. Under 30 rendered
pages is Category A.

**No empty sections rule.** Every section heading (`##`, `###`) must be
followed by at least one paragraph (2-3 sentences minimum) of prose
before any figure or table. A bare heading followed immediately by a
figure reference produces an empty-looking section in the rendered PDF
and is Category A.

**Start in plan mode.** Before writing any prose, produce a plan: the AN
section structure, which figures go where, which results tables are needed.
Execute after the plan is set.

## Output artifact

`exec/ANALYSIS_NOTE.md` — publication-quality analysis note in pandoc-compatible
markdown.

## Methodology references

- AN specification: `methodology/analysis-note.md`
- Review protocol: `methodology/06-review.md` → §6.2 (5-bot), §6.4
- Plotting / captions: `methodology/appendix-plotting.md`
- Checklist: `methodology/appendix-checklist.md`

## Pre-review gate

Before submitting for review, these must succeed:
1. `pixi run all` — full analysis chain reproduces from scratch
2. `pixi run build-pdf` — PDF compiles with all figures rendering

If either fails, fix it before requesting review.

## Analysis note structure

The AN must be **pandoc-compatible markdown** (see root CLAUDE.md for syntax).
See `methodology/analysis-note.md` for the full AN specification including
all 12 required sections, depth calibration, completeness test, and
bibliography requirements.

**Cross-references and citations (quick reference):**
- Figures: `![Caption](figures/name.pdf){#fig:name}` → `@fig:name`
- At sentence start: `Figure @fig:name`. Never `[-@fig:...]`.
- Citations: `[@key]` with `references.bib`. BibTeX must include `doi`,
  `url`, `eprint` fields. Use `unsrt`-style. Use `get_paper` for metadata.
- Tables: `{#tbl:name}` / `@tbl:name`. Equations: `{#eq:name}` / `@eq:name`.

## Key requirements

- **The AN is the complete record — not an executive summary.** Every detail
  needed to reproduce the analysis must be present.
- **Depth calibration.** ~50-100 rendered pages. Under 30 = Category A.
  Rule of thumb: every cut needs a distribution plot, every systematic needs
  an impact figure, every cross-check needs a comparison plot.
- **Per-systematic subsections.** Each source gets its own subsection:
  description, method, impact figure, per-bin table.
- **Figure captions.** Follow `<Plot name>. <2-5 sentence description.>`
  Anything under two sentences is Category A.
- **Table formatting.** No monospace overflow. Short labels, consistent
  numeric precision. Test with `build-pdf`.
- **Derived quantity viability.** Don't quote results with >3σ pulls from
  well-measured values without quantitative explanation (§6.8). Document
  as "not reliably extractable" when appropriate.
- **Completeness test.** A physicist unfamiliar with the analysis can
  reproduce every number from the AN alone.
- **Machine-readable results.** `results/` directory with JSON for spectra,
  uncertainties, and covariance matrices.

## Building the PDF

Run `pixi run build-pdf` from the analysis root. This converts
`ANALYSIS_NOTE.md` to PDF via pandoc with tectonic, numbered sections,
TOC, and `0.45\linewidth` figure width (single panels). Override with
`width=100%` attribute for full-width figures.

**Never use an LLM to convert markdown to LaTeX.** Pandoc handles this.

## Review

**5-bot review** — see `methodology/06-review.md` for protocol.
Write findings to `review/REVIEW_NOTES.md`.
