## Analysis Note Specification

The AN is a versioned document across Phases 4a–5. Phase 4a writes the
complete AN v1 with ALL detail — every diagnostic plot, every systematic
subsection, every cross-check, every comparison — using expected (Asimov/MC)
results only. Phase 4b starts from the latest 4a version and updates numbers
to 10% data. Phase 4c updates to full data. Phase 5 polishes prose and
typesets. Each phase produces a phase-stamped version
(`ANALYSIS_NOTE_{phase}_v{N}.md`); no version is ever overwritten.
Review/fix cycles increment the version within a phase (v1, v2, ...).
All versions are preserved on disk for audit and comparison.

**The gold standard: a physicist who has never seen the analysis should be
able to reproduce every number from the AN alone.** This is the completeness
test. If a reader needs to look at the code to understand a choice, the AN
has a gap. If a reader can't tell how a systematic was evaluated without
reading the script, the AN has a gap. If a reader can't reconstruct the
event selection from the AN text and figures, the AN has a gap.

**Notation consistency.** Every physical quantity must use a single,
consistent symbol throughout the AN. The same variable appearing under
different names in different sections (e.g., $f_s$ in the formalism but
$f_t$ in results tables) is Category A. Define symbols at first use and
maintain a consistent convention. When adopting notation from a reference
paper, note it explicitly if it differs from notation used earlier in the AN.

The AN is the complete record — not a journal paper, not an executive
summary, not a set of results with a brief methods section. ~50-100
rendered pages for a typical measurement. **Under 30 pages means detail
is missing** — this is a Category A finding at Phase 5 review.

Common causes of thin ANs:
- Missing per-cut distribution plots (before and after each cut)
- Missing per-systematic impact figures (how does each source shift
  the result?)
- Missing cross-check result plots (just saying "PASS" is not enough —
  show the comparison)
- Missing MVA diagnostics when a classifier is used (ROC, score
  distributions, feature importance — these are produced in Phase 3
  and must appear in the AN)
- Summary tables without supporting figures
- Methods described in one sentence instead of full paragraphs with
  equations

**No empty sections.** Every section heading must be followed by at least
one paragraph of prose before any figures. A section that contains only
a figure with no introductory text is **Category A** — the reader cannot
understand what the figure shows or why it matters without context. Even
a Results subsection showing a well-captioned figure needs prose
explaining: what is being shown, what the key features are, and how it
relates to the analysis goals. A bare heading followed immediately by a
`![caption](figure.pdf)` line produces an empty-looking section in the
rendered PDF. The AN writing subagent must verify that every `##` and
`###` heading is followed by at least 2-3 sentences of prose before any
figure or table.

The rule of thumb: every selection cut needs a before/after distribution
plot, every systematic needs an impact figure, every cross-check needs a
comparison plot. A 5-energy-point lineshape fit should have ~30+ figures
minimum (data/MC for each variable, cutflow, efficiency, backgrounds,
lineshape, residuals, profiles, correlations, systematics, comparisons).

---

### Change log

The AN must include a **Change Log** section as the first content after the
table of contents, before the Introduction. It is unnumbered
(`# Change Log {-}`) and does not appear in section numbering. The change
log is maintained incrementally — each phase that modifies the AN appends
entries at the top (reverse chronological order). Entries are grouped by
phase/version and use bulleted summaries describing what changed and why.

The first AN version (Phase 4a) initializes the change log with a single
entry: "Initial AN version (Phase 4a)." Subsequent phases (4b, 4c, 5) and
review-fix cycles each add a dated group summarizing the changes made.

Example format:
```
# Change Log {-}

**Phase 5 v2 (review fixes)**
- Expanded systematic §5.3 (tracking efficiency) with per-bin impact figure
- Fixed cross-reference to response matrix in §4.2

**Phase 5 v1**
- Final prose polish, typesetting, flagship figure updates

**Phase 4c v1**
- Updated all results to full dataset (was 10% in 4b)
- Added observed/expected comparison figures

**Phase 4a v1**
- Initial AN version (Phase 4a)
```

---

### Required sections

1. **Introduction** — motivation, observable definition, prior measurements
2. **Data samples** — experiment, sqrt(s), luminosity, MC generators, event
   counts. This section must include **structured sample tables** (not
   free-form prose or file listings):

   **Data summary table** — one row per data-taking era/period:

   | Period | $\sqrt{s}$ [GeV] | Events (pre-sel) | $\mathcal{L}$ [pb$^{-1}$] |
   |--------|-------------------|------------------|---------------------------|
   | 1992   | 91.2              | 450k             | 10.0                      |
   | ...    | ...               | ...              | ...                       |

   **MC sample table** — one row per physics process:

   | Process | Generator | $\sigma$ [nb] | $N_\text{gen}$ | $k$-factor | Notes |
   |---------|-----------|---------------|----------------|------------|-------|
   | $q\bar{q}$ | PYTHIA 6.1 | 30.5 | 4.0M | 1.0 | hadronic Z |
   | ...     | ...       | ...           | ...            | ...        | ...   |

   These are **summary-level tables** — one row per era or per physics
   process, not per-file inventories. For open/archived data, document
   what is known and mark unknowns explicitly (e.g., "cross-section not
   published — estimated from generator-level counting").
3. **Event selection** — every cut with motivation, distribution plot
   (N-1 preferred), efficiency (per-cut and cumulative), sensitivity to
   cut variation
4. **Corrections / unfolding** (measurements) — full procedure, closure/stress
   tests, response matrix, regularization
5. **Systematic uncertainties** — one subsection per source: physical
   origin, evaluation method (with justification of variation size),
   numerical impact (table + figure), interpretation and caveats.
   Document failed evaluation attempts. Summary budget table with
   footnotes explaining any capped, excluded, or sub-leading terms.
6. **Cross-checks** — each as a subsection within the section it validates
   (not a standalone section). Comparison plots (overlay, ratio, or pull —
   not just pass/fail), chi2/p-value, interpretation. Examples: run-period
   stability, subdetector comparisons, alternative selections, alternative
   correction methods, kinematic subsamples, generator comparisons. Large
   cross-checks → appendix with forward reference.
7. **Statistical method** — likelihood, fit validation, GoF
8. **Results** — full uncertainties, per-bin tables, summary figures
9. **Comparison to prior results and theory** — quantitative (chi2 with full
   covariance). "Qualitative consistency" insufficient when data exist.
10. **Conclusions** — result, precision, dominant limitations
11. **Future directions** — concrete roadmap (§12)
12. **Appendices** — per-bin systematic tables, covariance matrices (as
    tables), extended cutflow, auxiliary plots, **limitation index**.
    Appendices are where the bulk of detail lives.

The **limitation index** (in appendices) collects all constraints [A1],
limitations [L1], and design decisions [D1] introduced in Phase 1 and
propagated through the analysis. Each entry has: label, one-line
description, where introduced, impact on result, mitigation. This enables
a reviewer to see the full scope of known issues in one place and verify
each was properly addressed.

### Standard diagnostic figures

The following diagnostic figures are required in the AN when applicable.
Most are produced during Phases 2–4 and saved as figure artifacts; Phase 5
aggregates them. Missing diagnostics are Category A at review.

- **Per-variable data/MC comparisons.** Every selection variable and every
  MVA training feature. Group into grids in appendix when numerous.
- **Per-cut distributions.** N-1 distributions preferred (apply all cuts
  except the one being shown). Include sensitivity to cut variation
  (e.g., ±10% shift in cut value).
- **MVA diagnostics** (when a classifier is used): ROC curve with AUC,
  train/test score distributions (overtraining check), feature importance
  ranking, data/MC comparison on classifier output, alternative
  architecture comparison.
- **Per-systematic impact figures.** How each source shifts the result
  (already required; restated for completeness).
- **Cross-check result figures.** Overlay, ratio, or pull plots showing
  the comparison — not just a pass/fail statement.
- **Fit diagnostics.** Nuisance parameter pulls (pre-fit and post-fit),
  goodness-of-fit (chi2/ndf, p-value), post-fit data/model comparisons,
  corrected result vs theory or prior expectation.
- **Conceptual and methodology diagrams.** Where the analysis methodology
  involves non-trivial multi-step procedures (correction chains, sample
  merging strategies, region definitions, tagging logic), embed a
  schematic diagram in the relevant section — not in a standalone chapter.
  A correction-chain diagram belongs in the Corrections section; a
  region-definition diagram belongs in Event Selection. These diagrams are
  part of the narrative flow, not appendix material.

  The guiding principle is the **figure-scrolling test**: the entire
  physics story should be understandable by scrolling through the figures
  alone, even if not in the same detail as the text. If a reader scrolling
  through figures encounters a non-trivial method with no visual
  explanation, a diagram is missing. Conceptual diagrams fill the gaps
  where data plots alone don't convey the methodology.

  Diagrams are encouraged, not mandatory — but the figure-scrolling test
  gives reviewers a concrete criterion. See `appendix-plotting.md` §D for
  production guidelines.

---

### Requirements

- Self-contained: all results inline, publication-quality figures
- **Machine-readable results** in `results/` (CSV/JSON for spectra,
  covariance matrices)
- **Completeness test:** a physicist unfamiliar with the analysis should
  reproduce every number from the AN alone
- **BibTeX:** `[@key]` with `references.bib`. Entries must include `doi`,
  `url`, `eprint`. Use `unsrt`-style. Use `get_paper` for RAG papers.

---

### LaTeX compilation

Markdown → PDF via a three-step pipeline: **pandoc** (>=3.0) produces a
`.tex` file, **`postprocess_tex.py`** applies deterministic structural
fixes (margins, abstract→environment, references unnumbering, table
spacing, FloatBarrier, needspace, duplicate headers/labels, appendix,
clearpage), then **tectonic** (or xelatex) compiles to PDF. The
`build-pdf` pixi task runs this full pipeline. The preamble
(`conventions/preamble.tex`, symlinked from `src/conventions/`) sets:
default figure **height** `0.45\linewidth` (height-based, not width-based,
so figures with colorbars render at the same plot-area size as plain
plots), narrowed caption width (75%), relaxed float placement (90% max
per page), and widow/orphan penalties.
**Do not modify the preamble per-analysis** unless you have a specific
documented reason. Do not use an LLM for LaTeX conversion.

### Pandoc pitfalls (mandatory rules)

These patterns cause mangled output and must be avoided:

- **Never use `$\pm$`, `$<$`, `$>$`, `$-$` as standalone math.**
  Use Unicode instead: `±`, `<`, `>`, `−`. Bare single-symbol math
  delimiters confuse pandoc-crossref and produce garbled italic text.
  Only use `$...$` for actual mathematical expressions (`$M_Z$`,
  `$\chi^2/ndf = 1.5$`).
- **Never use `\mathrm{}` in figure captions or section headers.**
  Pandoc converts captions to both LaTeX and alt-text; `\mathrm` in
  alt-text produces `\mathrm allowed only in math mode` errors. Use
  plain subscripts (`$\sigma^0_{had}$`) or text in captions.
- **Never put `@ref` cross-references inside `$...$` math.**
  `$\Gamma_Z$ (@eq:width)` is fine; `$\Gamma_Z (@eq:width)$` mangles
  the reference into math-mode italic.
- **Section headers must not contain complex LaTeX.** Use plain text
  for headers: "Gamma-Z interference" not
  `$\gamma$-Z interference ($j_{had} = 0.14$)"`.
- **The abstract must not be a numbered section.** Pandoc converts
  `# Abstract` to `\section{Abstract}`, producing "1 Abstract" in the
  PDF. Auto-fixed by `postprocess_tex.py` (converts to
  `\begin{abstract}...\end{abstract}` and moves before
  `\tableofcontents`).
- **References must be unnumbered.** Pandoc produces
  `\section{References}`. Auto-fixed by `postprocess_tex.py` (converts
  to `\section*{References}\addcontentsline{toc}{section}{References}`).
- **Tables need spacing from preceding text.** Pandoc places
  `\begin{longtable}` directly after the preceding paragraph with no
  visual break, causing table captions to collide with paragraph text.
  Auto-fixed by `postprocess_tex.py` (inserts `\vspace{1em}` before
  each `\begin{longtable}`).

### Table formatting

Pipe tables in markdown become `longtable` in LaTeX. To avoid overflow:

- **Keep columns narrow.** Use abbreviations, symbols, and short headers.
  Move long descriptions to footnotes or prose.
- **Avoid monospace text in tables.** File paths, code identifiers, and
  other long monospace strings will overflow. Use short labels and
  reference a lookup table in an appendix if needed.
- **Split wide tables.** If a table exceeds 6 columns, split into two
  tables or rotate content (rows ↔ columns).
- **Numeric precision.** Use consistent significant figures: 2-3 digits
  for uncertainties, match precision for central values. Don't typeset
  `91.17930000` when `91.179` suffices.
- **Test with `build-pdf`.** Overfull hbox warnings in the TeX log indicate
  table overflow. Fix before submitting for review.

### Rendering quality checklist

The rendering reviewer (Phase 5) and the AN writing subagent must check
for these common rendering defects. All are Category A findings:

- **Orphaned section headings.** A section heading must not be the last
  line on a page. Add `\needspace{4\baselineskip}` before major sections
  in the pandoc preamble, or restructure text to avoid orphans. The
  `build-pdf` preamble should include `\widowpenalty=10000` and
  `\clubpenalty=10000`.
- **Figures off-page.** Any figure that extends beyond the page margins
  (clipped in the PDF) must be resized. Check that `width=` attributes
  are set correctly. 2D plots with colorbars are especially prone to
  this — verify with `make_square_add_cbar`.
- **Table splitting.** Short tables (< 15 rows) should not be split
  across pages. Use `\FloatBarrier` or position tables immediately
  after their first reference. The `longtable` environment splits by
  default — for small tables, consider using the `table` float instead.
- **Caption width.** Figure and table captions must span the full text
  width, not be limited to the figure width. This is the default pandoc
  behavior; do not override it.
- **Consistent cross-references.** All `@fig:`, `@tbl:`, `@eq:`
  references must resolve. Hardcoded section numbers (e.g., "Section 5.6")
  are fragile — use pandoc-crossref `@sec:` labels instead, or verify
  hardcoded numbers match the rendered PDF.
- **Overfull hbox warnings.** These indicate content (usually tables)
  extending past margins. Every overfull hbox warning must be
  investigated and resolved.
- **Abstract formatting.** The abstract must appear before the table of
  contents as an unnumbered block, not as "Section 1: Abstract." This
  is a pandoc structural issue that the typesetter must fix in the
  `.tex` before compilation.
- **Table-caption collision.** Table captions must be visually separated
  from preceding paragraph text. If a table caption reads as a
  continuation of the preceding paragraph (no vertical gap), add
  `\vspace{1em}` before the table environment.

---
