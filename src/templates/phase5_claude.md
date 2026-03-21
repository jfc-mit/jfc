# Phase 5: Documentation

> Read `methodology/analysis-note.md` for the full AN specification.
> Read `methodology/03-phases.md` → "Phase 5" for phase requirements.
> Read `methodology/appendix-plotting.md` for figure standards.
> Read `methodology/appendix-checklist.md` for the review checklist.

You are producing the final analysis note for a **{{analysis_type}}** analysis.

## Phase 5 has three separate sub-tasks

These should be handled by **separate subagents** in sequence:

### Sub-task 1: Figures (code-writing subagent)

Produce any AN-specific figures not already generated in Phases 2-4.
Read data/MC files, write plotting scripts, save to
`phase5_documentation/outputs/figures/`. Also symlink existing phase figures:

```bash
ln -sf ../../../phase2_exploration/outputs/figures/*.pdf phase5_documentation/outputs/figures/
ln -sf ../../../phase3_selection/outputs/figures/*.pdf phase5_documentation/outputs/figures/
ln -sf ../../../phase4_inference/4a_expected/outputs/figures/*.pdf phase5_documentation/outputs/figures/
ln -sf ../../../phase4_inference/4b_partial/outputs/figures/*.pdf phase5_documentation/outputs/figures/
ln -sf ../../../phase4_inference/4c_observed/outputs/figures/*.pdf phase5_documentation/outputs/figures/
```

The AN typically needs ~30+ figures. Phases 2-4 produce some, but the AN
usually needs additional per-variable distribution plots, per-cut before/after
comparisons, and per-systematic impact figures.

**Figure path verification (mandatory).** After aggregating figures, run:
```bash
# Verify every figure reference in the AN resolves to a file
grep -oP 'figures/[^)]+\.pdf' outputs/ANALYSIS_NOTE_5_v*.md | sort -u | while read f; do
  [ -f "outputs/$f" ] || echo "MISSING: $f"
done
```
Any missing figure is Category A. Fix before proceeding to the AN
writing subagent.

### Sub-task 2: AN polishing (prose-writing subagent)

The complete AN already exists from Phase 4a (updated with observed results
in 4b/4c). **This subagent does NOT rewrite the AN from scratch.** It reads:
- The existing `ANALYSIS_NOTE_4c_v*.md` (latest version from Phase 4c)
- All phase artifacts (STRATEGY.md, EXPLORATION.md, SELECTION.md,
  INFERENCE_EXPECTED.md, INFERENCE_OBSERVED.md)
- The figures directory (to verify figure references)
- The conventions files (for completeness checks)
- The experiment log

And produces `outputs/ANALYSIS_NOTE_5_v1.md` by polishing the existing AN.

**This subagent does NOT read data files or write code.** Its tasks:
- Review the existing AN for completeness against the checklist in
  `methodology/appendix-checklist.md`
- Add any missing figure references for Phase 5-produced figures
- Ensure all diagnostic figures (MVA, per-cut, per-systematic, fit
  diagnostics, cross-checks) are referenced in the appropriate sections
- Polish prose quality — fix unclear passages, ensure natural flow,
  verify every section has adequate introductory text
- Verify the completeness test: a physicist unfamiliar with the analysis
  can reproduce every number from the AN alone

**The gold standard:** a physicist who has never seen the analysis should
be able to reproduce every number from the AN alone. Under 30 rendered
pages is Category A.

**No local filesystem paths.** The AN must not contain cluster paths,
absolute filesystem paths, or machine-specific locations (e.g.,
`/n/holystore01/LABS/.../ALEPH/`). These are meaningless to a reader and
expose infrastructure details. Replace with a generic description ("the
ALEPH open data archive") or omit entirely. The data path belongs in the
experiment log and `.analysis_config`, not the AN.

**Appendix numbering.** Supplementary material (per-period stability
details, efficiency ratio estimates, limitation indices, design decision
tables) should use appendix-style headings, not continuation of the main
section numbering. In the markdown, place these after a comment
`<!-- Appendices -->` and the typesetting agent will convert them to
`\appendix` sections (Appendix A, B, C, ...).

**No empty sections rule.** Every section heading (`##`, `###`) must be
followed by at least one paragraph (2-3 sentences minimum) of prose
before any figure or table. A bare heading followed immediately by a
figure reference produces an empty-looking section in the rendered PDF
and is Category A.

**Start in plan mode.** Before writing any prose changes, produce a plan:
what gaps exist in the current AN, which figures need references added,
which sections need prose improvement. Execute after the plan is set.

### Sub-task 3: Typesetting (LaTeX expert subagent)

**This subagent runs AFTER the AN writing subagent.** Spawn the typesetter
agent (read `agents/typesetter.md` for the full prompt). Provide the
phase-stamped filename (e.g., `ANALYSIS_NOTE_5_v1.md`).

**Phase 5-specific context to pass to the typesetter:**
- Figure path: `phase5_documentation/outputs/` (Sub-task 1 symlinked
  all phase figures here)
- Target: 30-50% reduction in figure count through combination. A
  65-page AN with 35 standalone figures should become ~45-50 pages
  with ~15-20 composites plus a handful of standalone flagships.
- Flagship figures (from Phase 1 strategy) get full-page treatment.
- If typeset PDF has more standalone figures than composites, the
  combination was not aggressive enough.

**Verification (after typesetter completes):**
- All figures render (no broken placeholders)
- No content overflows page boundaries
- Cross-references resolve (no "??")
- Citations resolve (no "[?]")
- Page count in 50-100 range
- Figure captions >= 2 sentences each
- Tables fit within margins
- No duplicate table headers
- No local filesystem paths in body text
- Abstract before TOC, unnumbered
- References section unnumbered
- Appendix sections use letter numbering (A, B, C)
- More composite figures than standalone (excluding flagships)

## Output artifacts

- `outputs/ANALYSIS_NOTE_5_v1.md` — pandoc-compatible markdown (from sub-task 2)
- `outputs/ANALYSIS_NOTE_5_v1.tex` — typeset LaTeX (from sub-task 3)
- `outputs/ANALYSIS_NOTE_5_v1.pdf` — final compiled PDF (from sub-task 3)

## Methodology references

- AN specification: `methodology/analysis-note.md`
- Review protocol: `methodology/06-review.md` → §6.2 (5-bot), §6.4
- Plotting / captions: `methodology/appendix-plotting.md`
- Checklist: `methodology/appendix-checklist.md`

## Pre-review gate

Before submitting for review, these must succeed:
1. `pixi run all` — full analysis chain reproduces from scratch
2. PDF compiles with all figures rendering (the typesetting agent
   handles this as part of sub-task 3)

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
- **Per-systematic subsections.** Each source gets its own subsection
  written in running prose: physical origin, evaluation method, numerical
  impact, and interpretation. Do NOT use bold-labeled paragraph headings
  ("**Origin:**", "**Method:**") — write natural prose that reads like an
  analysis note, not a form.
- **Figure captions.** Follow `<Plot name>. <2-5 sentence description.>`
  Anything under two sentences is Category A.
- **Table formatting.** No monospace overflow. Short labels, consistent
  numeric precision. Test with `build-pdf`.
- **Derived quantity viability.** Don't quote results with >3-sigma pulls from
  well-measured values without quantitative explanation (§6.8). Document
  as "not reliably extractable" when appropriate.
- **Completeness test.** A physicist unfamiliar with the analysis can
  reproduce every number from the AN alone.
- **Machine-readable results.** `results/` directory with CSV/JSON for
  spectra, uncertainties, and covariance matrices.

## Review

**5-bot review** — see `methodology/06-review.md` for protocol.
The rendering reviewer inspects the **typeset PDF** (from sub-task 3),
not the raw pandoc output.
Write findings to `review/{role}/` using session-named files
(see `methodology/appendix-sessions.md` for naming conventions).
