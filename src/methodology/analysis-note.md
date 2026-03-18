## Analysis Note Specification

The AN is a single evolving document across Phases 4b, 4c, and 5. Phase 4b
writes the complete AN with 10% results. Phase 4c updates numbers. Phase 5
polishes and renders. Structure is written in 4b; later phases update results.

**The gold standard: a physicist who has never seen the analysis should be
able to reproduce every number from the AN alone.** This is the completeness
test. If a reader needs to look at the code to understand a choice, the AN
has a gap. If a reader can't tell how a systematic was evaluated without
reading the script, the AN has a gap. If a reader can't reconstruct the
event selection from the AN text and figures, the AN has a gap.

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
- Summary tables without supporting figures
- Methods described in one sentence instead of full paragraphs with
  equations

The rule of thumb: every selection cut needs a before/after distribution
plot, every systematic needs an impact figure, every cross-check needs a
comparison plot. A 5-energy-point lineshape fit should have ~30+ figures
minimum (data/MC for each variable, cutflow, efficiency, backgrounds,
lineshape, residuals, profiles, correlations, systematics, comparisons).

---

### Required sections

1. **Introduction** — motivation, observable definition, prior measurements
2. **Data samples** — experiment, √s, luminosity, MC generators, event counts
3. **Event selection** — every cut with motivation, distribution plot,
   efficiency (per-cut and cumulative)
4. **Corrections / unfolding** (measurements) — full procedure, closure/stress
   tests, response matrix, regularization
5. **Systematic uncertainties** — one subsection per source: physical
   origin, evaluation method (with justification of variation size),
   numerical impact (table + figure), interpretation and caveats.
   Document failed evaluation attempts. Summary budget table with
   footnotes explaining any capped, excluded, or sub-leading terms.
6. **Cross-checks** — each as a subsection within the section it validates
   (not a standalone section). Comparison plots, chi2/p-value, interpretation.
   Large cross-checks → appendix with forward reference.
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

Markdown → PDF via **pandoc** (≥3.0) + tectonic (or xelatex). The
`build-pdf` pixi task runs pandoc with
`--number-sections --toc --filter pandoc-crossref --citeproc`, default
figure width `0.45\linewidth`. Do not use an LLM for conversion.

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

---
