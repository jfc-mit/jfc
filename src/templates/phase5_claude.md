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

**Interpretive quality standards (mandatory self-check by note writer):**

1. **Equation count.** Every analysis must contain equations defining:
   the observable (what is measured), the correction/unfolding procedure
   (how raw data becomes a physics result), the systematic evaluation
   formula (how uncertainties are computed), and the fit/extraction model
   (how parameters are determined). Minimum 4 equations. An AN with
   zero equations is Category A — it means the reader cannot verify the
   mathematics independently.

2. **Interpretive paragraphs.** After every results table, key figure,
   or systematic evaluation, include 2-3 sentences interpreting what the
   numbers mean physically. Don't just report — explain. Is the result
   consistent with the reference? Is it expected or surprising? What
   does it tell us? A table of systematic values without physical
   interpretation is a spreadsheet, not a physics analysis.

3. **Validation summary table.** Include a section (or appendix) that
   tabulates every validation test performed, its outcome (chi2/ndf,
   p-value, PASS/FAIL), and what it proves. This is the reader's
   evidence that the analysis is trustworthy. Format:
   ```
   | Test | Phase | chi2/ndf | p-value | Verdict | What it validates |
   ```

4. **Resolving power statement.** After the final result, state
   explicitly what deviations the measurement can detect. Example:
   "With a total uncertainty of 3.8%, this measurement can distinguish
   predictions differing by more than ~8% at 2-sigma significance."
   A measurement without a resolving-power statement leaves the reader
   unable to judge its physics impact.

5. **Comparison figure with published results.** At least one figure
   must overlay the measurement with published values from reference
   analyses, with chi2 or pull annotation. This figure IS the core
   physics result — it shows what the measurement adds to existing
   knowledge. If no published measurement exists for the exact
   observable, compare to the closest available published result and
   explain the differences.

6. **Figure-scrolling test.** Scroll through the figure sequence in the
   AN without reading any text. Can you follow the complete physics
   story? The sequence should cover:
   - Data quality / sample characterization (Phase 2 figures)
   - Event selection / cut distributions (Phase 3 figures)
   - Corrections / response / closure (Phase 3-4 figures)
   - Systematic impacts (Phase 4 figures)
   - Results with uncertainty bands (Phase 4 figures)
   - Comparison to published results (Phase 4-5 figures)
   If any step has no figure, add one or note the gap. If the figure
   sequence jumps from "selection" to "results" with no correction or
   validation figures in between, the AN is missing critical visuals.

7. **Systematic breakdown figure.** Verify the systematic uncertainties
   section contains a visual breakdown (waterfall, bar chart, or stacked
   bars) showing each source's contribution to the total. A summary
   table alone is insufficient — the visual makes relative magnitudes
   immediately apparent.

**Number consistency gate (mandatory before PDF compilation).** The
note writer (or typesetter) must verify that all numerical results in
the AN body text and tables match the latest machine-readable outputs
in `results/*.json`. Specifically:
- Every systematic uncertainty value in tables must match the JSON
- Central values in abstract and summary must match JSON
- Event counts, selection efficiencies, and derived quantities must
  match the inference artifacts
Any discrepancy > 1% relative is Category A. This gate exists because
stale numbers from earlier iterations have propagated to final ANs —
the human gate caught a 9.3% vs 1.7% discrepancy that passed all
agent reviews.

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

**Automated content gates (mandatory before typesetting).** Run these
checks on the markdown source. All must pass before Sub-task 3:

```bash
MD=$(ls -t outputs/ANALYSIS_NOTE_5_v*.md | head -1)
FAIL=0
# 1. No $\pm$ standalone math (causes visible dollar signs in PDF)
if grep -Pn '\$\\pm\$|\$<\$|\$>\$|\$\\sim\$' "$MD"; then
  echo "FAIL: Use Unicode ±/</>/~ not standalone \$math\$"; FAIL=1
fi
# 2. Luminosity stated somewhere in the note
if ! grep -qi 'luminosity\|pb.*-1\|fb.*-1\|nb.*-1' "$MD"; then
  echo "FAIL: No luminosity found in AN"; FAIL=1
fi
# 3. Reference count >= 15
REFS=$(grep -oP '\[@[^\]]+\]' "$MD" | sort -u | wc -l)
echo "Unique citation keys: $REFS"
[ "$REFS" -lt 15 ] && echo "FAIL: Fewer than 15 unique references (Category A)" && FAIL=1
# 4. No local filesystem paths in body text
if grep -Pn '/n/home|/n/holy|/tmp/|/scratch/' "$MD"; then
  echo "FAIL: Local filesystem paths found in AN"; FAIL=1
fi
# 5. No internal phase labels in body (after Change Log)
BODY=$(sed -n '/^# Introduction/,$ p' "$MD")
if echo "$BODY" | grep -Pn '\(4[abc]\)|Phase [1-5][^.]' | head -5; then
  echo "WARN: Internal phase labels found in body text — review and remove"
fi
# 6. Configuration label consistency
PRIMARY=$(echo "$BODY" | grep -oi 'primary.*kappa\|primary.*working.point\|primary.*configuration' | sort -u)
echo "Primary configuration labels found: $PRIMARY"
echo "Verify these are consistent throughout."
[ "$FAIL" -eq 0 ] && echo "ALL CONTENT GATES PASSED" || echo "FIX FAILURES BEFORE TYPESETTING"
```

**Start in plan mode.** Before writing any prose changes, produce a plan:
what gaps exist in the current AN, which figures need references added,
which sections need prose improvement. Execute after the plan is set.

**Figure composition annotations (mandatory).** When referencing groups of
related figures, annotate the grouping so the typesetter can merge them
without re-discovering the relationships:

```markdown
<!-- COMPOSE: 2x3 grid -->
![Multiplicity...](figures/datamc_nch.pdf){#fig:datamc-a}
![Energy...](figures/datamc_evis.pdf){#fig:datamc-b}
...
```

Use `<!-- COMPOSE: NxM grid -->` for grids, `<!-- COMPOSE: side-by-side -->`
for pairs (nominal + uncertainty), `<!-- COMPOSE: 1xN row -->` for rows,
and `<!-- FLAGSHIP -->` for standalone money plots. You have the physics
context to decide what belongs together — this is a physics grouping
decision, not a typesetting decision. See `methodology/03-phases.md` →
Phase 5 "Figure composition annotations" for the full specification.

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
- **Read note writer composition annotations first.** Search the
  markdown source for `<!-- COMPOSE: ... -->` and `<!-- FLAGSHIP -->`
  comments. These tell you which figures to merge and how. Convert
  each annotated group to side-by-side `\includegraphics` calls
  with `\hspace{0.01-0.02\linewidth}` gaps inside a single
  `\begin{figure}` environment. Do NOT use `\subfloat` — use the
  `\includegraphics` + `\hspace` pattern with unified captions
  containing (a)/(b)/(c) labels. This is your primary grouping
  input — the merge scan below is a safety net for anything the
  note writer missed.
- **Mandatory merge scan (safety net).** After processing annotations,
  scan the remaining ungrouped figures and identify:
  **(a)** Runs of 3+ sequential figures that share the same
  axes/layout and differ only in a label or parameter (e.g.,
  per-angular-range EEC spectra, per-variable data/MC,
  per-systematic shifts).
  **(b)** Nominal + uncertainty pairs — any 2D map (migration,
  response, correction, efficiency) immediately followed by its
  uncertainty or relative-uncertainty map. These share the same
  binning axes and MUST be placed side-by-side as (a)/(b) panels
  in a single `figure` environment. Look for filenames or captions containing
  "uncertainty", "error", "sigma", "stat_unc", "rel_unc".
  Leaving either pattern as standalone figures is Category A.
- **Uncertainty sanity gate.** While reviewing rendered figures, flag
  any figure where error bars are visibly larger than the signal or
  span the full y-axis range. This usually indicates missing explicit
  `yerr` on derived quantities. Such figures are Category A — return
  them to the figure subagent for correction before proceeding.
- **Iterate until it looks right.** The typesetter must compile the
  PDF, read it, and fix any visual issues — then recompile and
  re-read. Repeat until the output passes visual inspection (max 3
  iterations). A single compile-and-ship pass is not acceptable.
  Check: composite panel sizing is consistent, no overflow, text is
  legible at rendered size, page breaks are sensible.

**Verification (after typesetter completes):**
- All figures render (no broken placeholders)
- No content overflows page boundaries
- Cross-references resolve (no "??") — `grep '??' ANALYSIS_NOTE.log` = 0
- Citations resolve (no "[?]")
- **TOC page numbers match actual PDF** — spot-check the first appendix
  entry and two body sections against the rendered PDF page numbers
- Page count in 50-100 range
- Figure captions >= 2 sentences each
- Tables fit within margins
- No duplicate table headers
- No local filesystem paths in body text
- Abstract before TOC, unnumbered
- References section unnumbered
- Appendix sections use letter numbering (A, B, C)
- **No `\subfloat` in .tex** — use `\includegraphics` composites
- More composite figures than standalone (excluding flagships)
- No runs of 3+ sequential standalone figures of the same type
- No figures with error bars visibly larger than the signal (yerr sanity)
- **No `$\pm$` with visible dollar signs** — grep the .tex for `\$\pm\$`
- **All composite figures preserve both original labels** — every merged
  figure's `\label{fig:...}` appears in the .tex (as `\phantomsection\label`)
- **Title renders math correctly** — check page 1 for literal "sqrt(s)"
  or "$\sqrt{s}$" with visible dollar signs
- **Change log is ≤ 1 page** — if longer, condense or move to appendix
- **≥ 15 unique references** in the bibliography

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
