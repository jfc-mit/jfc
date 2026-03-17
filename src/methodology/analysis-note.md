## Analysis Note Specification

The AN is a single evolving document across Phases 4b, 4c, and 5. Phase 4b
writes the complete AN with 10% results. Phase 4c updates numbers. Phase 5
polishes and renders. Structure is written in 4b; later phases update results.

The AN is the complete record — not a journal paper. Every detail needed to
reproduce the analysis from scratch must be present. ~50-100 rendered pages
for a typical measurement. Under 30 pages means detail is missing.

---

### Required sections

1. **Introduction** — motivation, observable definition, prior measurements
2. **Data samples** — experiment, √s, luminosity, MC generators, event counts
3. **Event selection** — every cut with motivation, distribution plot,
   efficiency (per-cut and cumulative)
4. **Corrections / unfolding** (measurements) — full procedure, closure/stress
   tests, response matrix, regularization
5. **Systematic uncertainties** — one subsection per source: what, how
   evaluated, impact (table + figure), correlation info. Summary table.
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
    tables), extended cutflow, auxiliary plots. Appendices are where the
    bulk of detail lives.

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

Markdown → PDF via **pandoc** (≥3.0) + pdflatex. The `build_pdf.py` script
handles figure collection, `--number-sections --toc`, default figure width
`0.5\textwidth`. Do not use an LLM for conversion.

---
