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

### Sub-task 3: Typesetting (LaTeX expert subagent)

**This subagent runs AFTER the AN writing subagent.** It is a LaTeX
typesetting expert that transforms the pandoc output into a
publication-quality PDF. It does NOT modify physics content — only layout
and formatting.

**Workflow:**

1. **Convert markdown to LaTeX** (not directly to PDF):
   ```bash
   cd phase5_documentation/exec
   pandoc ANALYSIS_NOTE.md -o ANALYSIS_NOTE.tex --standalone \
     --include-in-header=../../conventions/preamble.tex \
     --number-sections --toc --filter pandoc-crossref --citeproc
   ```

2. **Read and improve the `.tex` file.** Specific tasks:

   - **Fix margins.** Pandoc's default margin (`margin=1in` or
     `margin=0.75in`) may be too wide for a figure-heavy technical
     note. Replace the geometry line in the preamble with
     `\usepackage[margin=0.75in]{geometry}` for letter paper or
     `\usepackage[a4paper,margin=2cm]{geometry}` for A4. The goal is
     to maximize the usable text width for figures and tables.

   - **Combine related figures.** Pandoc produces one `\begin{figure}`
     per markdown image. Group related figures into composite floats
     using `\subfloat` or side-by-side `\includegraphics`. Candidates:
     data/MC comparisons for related variables (p, pT, theta, phi →
     2×2 grid), reco vs gen Lund plane (side-by-side), systematic shift
     maps for related sources, closure check projections (kt + dtheta).
     Use `\begin{figure*}` for full-width composites. Rewrite captions
     to describe the composite ("(a) ... (b) ... (c) ...").
     Use HEIGHT-based sizing (not width) because figures with colorbars
     are wider than plain plots at the same nominal figsize. All figures
     are square (10×10 inches), so height = plot-area width.
     For 2-across: `\includegraphics[height=0.45\linewidth]{...}`
     For 3-across: `\includegraphics[height=0.3\linewidth]{...}`

   - **Fix float placement.** Add `\FloatBarrier` at section boundaries
     (`\section`, `\subsection`) to prevent figures from drifting far
     from their text. Add `\clearpage` before appendices and before
     dense figure sequences.

   - **Fix table formatting.** Use `booktabs` rules (`\toprule`,
     `\midrule`, `\bottomrule`). Apply `\small` or `\resizebox` to
     wide tables. Ensure no column overflows the text width.

   - **Verify section content.** Every `\section` and `\subsection`
     must have at least one paragraph of text before any `\begin{figure}`
     or `\begin{table}`. If not, flag for the AN writing agent.

   - **Optimize page breaks.** Prevent orphaned section headings at
     page bottoms (`\needspace{4\baselineskip}` before headings).
     Add `\newpage` before major sections (Results, Discussion) for
     clean chapter starts.

   - **Check cross-references and citations.** Grep for `??` (unresolved
     refs) and `[?]` (unresolved citations) in the compiled output.

3. **Compile to PDF:**
   ```bash
   tectonic ANALYSIS_NOTE.tex
   ```
   Fix any compilation errors. The final `ANALYSIS_NOTE.pdf` is the
   deliverable.

4. **Verify the PDF.** Read the compiled PDF and check:
   - All figures render (no broken placeholders)
   - No content overflows page boundaries
   - Cross-references resolve (no "??")
   - Citations resolve (no "[?]")
   - Page count in 50-100 range
   - Figure captions ≥ 2 sentences each
   - Tables fit within margins

**What the typesetting agent MUST NOT do:**
- Change numbers, results, or physics conclusions
- Rewrite captions beyond grammar/clarity fixes
- Remove or add figures (only group existing ones)
- Modify section structure or ordering
- Change the bibliography

If the agent finds a physics issue (missing figure, inconsistent number,
empty section), it documents the issue and flags it for the orchestrator
to route back to the AN writing agent. It does not fix physics content.

## Output artifacts

- `exec/ANALYSIS_NOTE.md` — pandoc-compatible markdown (from sub-task 2)
- `exec/ANALYSIS_NOTE.tex` — typeset LaTeX (from sub-task 3)
- `exec/ANALYSIS_NOTE.pdf` — final compiled PDF (from sub-task 3)

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
- **Machine-readable results.** `results/` directory with CSV/JSON for
  spectra, uncertainties, and covariance matrices.

## Review

**5-bot review** — see `methodology/06-review.md` for protocol.
The rendering reviewer inspects the **typeset PDF** (from sub-task 3),
not the raw pandoc output.
Write findings to `review/REVIEW_NOTES.md`.
