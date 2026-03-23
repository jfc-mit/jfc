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
is missing** — this is Category A at Phase 5 review unless the reviewer
can confirm that the analysis is genuinely simple (single observable,
fewer than 5 systematic sources, no MVA, no unfolding) AND the
completeness test still passes. A simple, fully documented 35-page AN
is acceptable; a complex analysis crammed into 40 pages is not.

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

**Change log length.** The change log must not exceed 1 rendered page.
For multi-iteration analyses, condense earlier phases to one-line summaries
and keep full detail only for the last 2 versions. Move the full change
history to an appendix if needed. The change log is a navigation aid for
what changed between versions, not a process diary — internal phase
labels, Finding numbers, and agent debug details do not belong here.

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

   **Data summary table** — one row per data-taking era/period.
   **Integrated luminosity is mandatory.** Every data-taking period must
   have a luminosity column. If the integrated luminosity is not published
   for archived/open data, estimate it from the hadronic cross-section and
   event count: $\mathcal{L} = N_\text{had} / \sigma_\text{had}$. State
   the method used. An analysis note without luminosity figures is
   **Category B**.

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
   tests, response matrix, regularization. **Key equations must be displayed**
   as `$$...$$` — the correction/unfolding formula, the likelihood or chi2
   used for fitting, and the systematic propagation formula. A reader should
   be able to implement the method from the equations in the AN without
   reading the code. "The correction is applied bin-by-bin" without showing
   $C(\chi) = N_\text{gen}(\chi) / N_\text{reco}(\chi)$ is incomplete.

   **Validation documentation standard.** Each validation test (closure,
   stress, flat-prior, alternative method) must include ALL of:
   (a) what was tested and why, (b) what the expected result is,
   (c) what was observed (chi2/ndf, p-value, max deviation), (d) figure
   showing the test result (not just a number), (e) interpretation —
   does the test pass? If not, what was tried to fix it (3+ attempts
   required)? What does this mean for the result's reliability?
   "Closure test passes" without (a-e) is Category B.

   **Stress test formula.** The AN must state the stress test reweighting
   formula (e.g., $w = 1 + \alpha(T - \langle T \rangle)/\sigma_T$),
   the variable used, the magnitudes tested (5%, 10%, 20%), and the
   recovery accuracy at each level. A table showing magnitude vs max
   bin deviation is the minimum. This tells the reader the method's
   resolving power — "robust for expected data/MC differences of a
   few percent" is useful; "stress test passes" is not.

   **Statistical methodology standards (Category A if violated).**

   - **Full covariance is mandatory.** When a covariance matrix exists
     (statistical, systematic, or total), ALL chi-squared tests MUST use
     the full covariance matrix: $\chi^2 = (\mathbf{d} - \mathbf{m})^T
     C^{-1} (\mathbf{d} - \mathbf{m})$. Diagonal-only chi-squared may
     be reported alongside for reference but MUST NOT be the primary
     metric. Diagonal chi-squared systematically underestimates the true
     chi-squared when bins are positively correlated (the common case for
     systematic-dominated measurements), producing artificially good
     p-values. If the covariance matrix is ill-conditioned (condition
     number > $10^8$), note this and report both metrics with caveats.
   - **Pull distribution diagnostics.** When reporting pull distributions:
     state the expected number of bins with |pull| > 2σ (= 4.6%) and
     > 3σ (= 0.27%). If actual >> expected: uncertainties are
     underestimated or there is a genuine data-MC difference — state
     which. If actual << expected (or pull RMS < 0.7): uncertainties are
     overestimated — see overcoverage protocol in §3. Pull RMS must be
     quoted: 1.0 ± 0.1 is healthy; < 0.7 is overcoverage; > 1.3 is
     undercoverage. Both extremes require discussion.
   - **Goodness-of-fit for the primary result.** The primary extraction
     must have $\chi^2/\text{ndf} < 3$ ($p > 0.01$). A primary result
     with $p < 0.01$ is Category A unless: (a) the source of poor GoF is
     identified, (b) it is demonstrated not to bias the extracted
     parameter, and (c) a configuration with acceptable GoF is shown as a
     cross-check. Selecting the best-precision configuration while
     ignoring fit quality is forbidden.
   - **Closure test criteria.** Closure tests pass when chi-squared
     $p > 0.05$. Ad hoc thresholds (e.g., "$\chi^2/\text{ndf} < 5$ is
     acceptable") are not valid — they are ndf-dependent and can mask
     genuine failures. When $p < 0.01$, the closure has failed and 3+
     remediation attempts are required before the failure can be accepted
     as a limitation.

5. **Systematic uncertainties** — one subsection per source following
   this template (the z_lineshape analysis is the model):
   - **Physical origin** (1-2 sentences: what physical effect causes this)
   - **Evaluation method** (how the variation is defined, what is varied,
     through what chain it propagates — cite the formula or reference).
     State the variation size and justify it with a measurement or
     published uncertainty. "±50% on the background" is Category A
     unless 50% IS the measured uncertainty.
   - **Numerical impact** (table row + impact figure showing how the
     result shifts bin-by-bin). Flat shifts on shape measurements are
     Category A — see executor self-check.
   - **Interpretation** (is this dominant? subdominant? correlated with
     other sources? what would reduce it?)
   A subsection that only states a number without explaining the
   propagation chain is incomplete — the reader must understand HOW
   the uncertainty was derived, not just its value. Document failed
   evaluation attempts.

   **Error budget narrative (required).** After the per-source
   subsections and summary budget table, include a narrative paragraph
   discussing: (a) which sources dominate and why, (b) whether the
   measurement is statistically or systematically limited, (c) what
   concrete improvements could reduce the dominant sources (better MC,
   data-driven calibration, additional control regions), and (d) the
   measurement's **resolving power** — can it distinguish the SM from
   a ±20% deviation at 2σ? If chi2/ndf << 1 (all pulls < 0.5σ), the
   AN must explicitly discuss whether the systematic uncertainties are
   conservatively overestimated and what this means for the measurement's
   discriminating power. An overcovered measurement is honest but should
   acknowledge the cost.
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
   Every comparison must state a number: chi2/ndf, pull in sigma, or
   ratio with uncertainty. "Consistent with published values" without
   a chi2 or pull is Category B. When prior measurements exist at the
   same kinematic points, overlay them on the result figure or provide
   a table with bin-by-bin comparison. The comparison section should
   address: (a) how does this result compare to the best published
   measurement? (b) is the precision competitive, comparable, or
   exploratory? (c) what does the comparison tell us about the method's
   validity?
10. **Conclusions** — result, precision, dominant limitations
11. **Future directions** — concrete roadmap (§12)
12. **Known limitations and open questions** — a concise, honest
    assessment of what remains imperfect. For each of the 3-5 most
    significant limitations:
    - What the limitation is (one sentence)
    - Whether it was attempted to be solved (what was tried, what
      failed — per the "solve problems, don't accept limitations"
      philosophy in §3)
    - What its impact is on the result (quantitative: "shifts the
      central value by < X%" or "inflates the total uncertainty by Y%")
    - What would fix it (concrete next action, not "future work")

    This section is distinct from the Limitation Index (appendix).
    The Limitation Index is a complete registry of ALL constraints,
    limitations, and decisions with labels [A1], [L1], [D1] for audit.
    Known Limitations is a physicist-facing narrative that highlights
    the most significant open issues and their implications for
    interpreting the result. It answers: "what should I keep in mind
    when using these numbers?" An AN that hides all limitations in an
    appendix but has no honest assessment in the main body is
    Category B.
13. **Appendices** — per-bin systematic tables, covariance matrices,
    extended cutflow, auxiliary plots, **limitation index**,
    **reproduction contract**. Appendices are where the bulk of detail
    lives.

The **limitation index** (in appendices) collects all constraints [A1],
limitations [L1], and design decisions [D1] introduced in Phase 1 and
propagated through the analysis. Each entry has: label, one-line
description, where introduced, impact on result, mitigation. This enables
a reviewer to see the full scope of known issues in one place and verify
each was properly addressed.

The **reproduction contract** (required appendix) documents the exact
command sequence to reproduce the full analysis from raw data to final
result. This goes beyond "pixi run all exists" — it is a self-contained
recipe with:
- Environment setup (`pixi install`, any required data paths)
- The exact pixi task sequence in execution order, with expected
  outputs at each step
- A workflow diagram showing the execution DAG: inputs → processing
  steps → outputs, with systematic variation branches shown
- Any manual steps or configuration that cannot be automated
- Expected runtime estimates per step

The reproduction contract must be sufficient for a physicist who has
never seen the analysis to reproduce every number by following the
commands verbatim.

**Covariance matrix presentation.** Covariance matrices in the appendix
must include:
- **Per-source correlation matrices** — one panel per uncertainty
  component (statistical, regularization, experimental, theory/model,
  and any analysis-specific corrections), all on the same color scale
  for direct comparison. Interpret each matrix's structure physically:
  what pattern of correlations does each source produce, and why?
- **Total covariance and correlation matrices.** State the maximum
  off-diagonal correlation $|\rho_{ij}|$ and identify which component
  dominates the off-diagonal structure.
- **Recommendation for downstream use.** If certain bins or regions
  have unreliable covariance (edge bins, low-statistics tails),
  recommend a fit window for downstream extractions.

### Number and configuration consistency across phases

When a primary operating point, configuration, or method changes between
Phase 4a (expected) and Phase 4c (observed), the AN must:

1. **State the change explicitly** in the relevant results section (not
   only in the Change Log). Example: "The primary working point was
   changed from κ = 0.5 (Phase 4a expected) to κ = 0.3 (full data)
   based on the multi-WP fit performance on observed data."
2. **Re-evaluate ALL systematics at the new operating point**, or
   document quantitatively why the original evaluation transfers (e.g.,
   "the tracking systematic varies by < 5% across κ values, so the
   κ = 0.5 evaluation is used").
3. **Ensure label consistency**: if Section 10 says "primary κ = 0.5"
   but Section 13 says "primary κ = 0.3", the earlier section must be
   updated or clearly labeled as "expected results at the Phase 4a
   operating point (κ = 0.5)". The Phase 5 note writer must search the
   AN body for the old operating-point label and update or annotate
   every occurrence. A reader who encounters conflicting "primary"
   labels will lose trust in the analysis.
4. **Never compute pulls between results at different operating points**
   without flagging the comparison as approximate. A pull of 0.04σ
   between κ = 0.5 (expected) and κ = 0.3 (observed) is not a
   meaningful consistency check — it compares apples to oranges.

**Event count consistency.** A single dataset must have a single
post-selection event count used consistently in the cutflow table, body
text, and summary tables. If different counts appear (e.g., 2,889,000
in a table vs 2,889,543 in text), the discrepancy must be explained
(rounding, subset, additional quality cut). Unexplained event count
mismatches are **Category B**.

**Rounding consistency.** Uncertainties must be rounded consistently:
if the abstract says "±0.01" and a table says "±0.011", choose one
precision and use it everywhere. When displaying component uncertainties
and a total, verify that $\sqrt{\sigma_1^2 + \sigma_2^2}$ matches the
displayed total to the displayed precision — a reader will check this.

### Standard diagnostic figures

The following diagnostic figures are required in the AN when applicable.
Most are produced during Phases 2–4 and saved as figure artifacts; Phase 5
aggregates them. Missing diagnostics are Category A at review.

- **Per-variable data/MC comparisons.** Every selection variable and every
  MVA training feature. Group into grids in appendix when numerous.
- **Per-category validation grids.** When the observable combines multiple
  reconstructed object types (energy-flow categories, charged vs neutral,
  different particle species), produce a complete kinematic validation
  grid (angular acceptance, momentum, quality variables, data/MC ratio)
  FOR EACH CATEGORY separately. A single aggregate data/MC comparison
  can hide category-specific mismodeling that propagates into the
  detector response. Missing per-category validation for a category
  that enters the observable is Category B.
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

- **Mandatory comparison overlay.** The Results section must contain at
  least one figure that overlays the measurement with published values
  from reference analyses on the SAME axes (not separate panels, not a
  table). This overlay IS the core physics deliverable — it shows what
  the measurement adds to existing knowledge. Requirements: published
  data points with their uncertainties, this measurement with its total
  uncertainty band, a ratio or pull panel showing the quantitative
  comparison, and a chi2/ndf annotation (using full covariance if
  available). If no published measurement exists at the exact kinematic
  points, use the closest available and explain the differences in the
  caption. A results section without a comparison overlay is Category B.
  A results section that says "consistent with published values" without
  showing the comparison is Category A.

- **Systematic breakdown figure.** The systematic uncertainties section
  must contain a figure showing the relative contribution of each source
  to the total. Acceptable formats: waterfall chart (cumulative quadrature
  addition), horizontal bar chart (per-source fractional contribution),
  or stacked bar chart (per-bin breakdown). This figure makes the error
  budget visually assessable — a reader should see at a glance which
  source dominates and by how much. A summary table alone is insufficient
  because tables do not convey relative magnitudes as effectively as
  visualizations.

---

### Requirements

- Self-contained: all results inline, publication-quality figures
- **Machine-readable results** in `results/` (CSV/JSON for spectra,
  covariance matrices)
- **Completeness test:** a physicist unfamiliar with the analysis should
  reproduce every number from the AN alone
- **BibTeX:** `[@key]` with `references.bib`. Entries must include `doi`,
  `url`, `eprint`. Use `unsrt`-style. Use `get_paper` for RAG papers.
  **Never generate BibTeX entries from training data.** Every BibTeX
  entry must be obtained from a verifiable source: `get_paper` MCP tool,
  DOI lookup, INSPIRE search, or the actual paper PDF. An agent that
  writes `@article{ALEPH:2005foo, ...}` from memory is almost certainly
  hallucinating — the INSPIRE key, author list, journal metadata, and
  even the existence of the paper may be fabricated. When you need a
  citation: (1) search for the paper by title, author, or topic,
  (2) obtain its INSPIRE record or DOI, (3) construct the BibTeX from
  verified metadata. A BibTeX entry that cannot be traced to a real
  source is Category A.

### Literature requirements

- **Foundational citations (Category A if missing).** The AN must cite the
  original theoretical papers that defined the observable being measured
  (e.g., Basham, Brown, Ellis, Love 1978 for EEC; Ellis, Georgi, Machacek
  et al. for event shapes). "Mentioned by name but not cited" is Category A.
- **Published data overlay.** When prior measurements of the same observable
  exist at the same or similar energy, the Results section must include a
  quantitative comparison figure: overlay the published data points on the
  corrected result, or show a ratio/pull plot. Stating "consistent with
  published values" without showing the comparison is Category B. If
  published data points are not available in machine-readable form, state
  this explicitly and provide a table comparing values at representative
  bins/points.
- **Cross-experiment context.** The Introduction must cite at least 2
  measurements of the same or closely related observable from other
  experiments (LEP, Tevatron, LHC) where they exist. For a first
  measurement, cite the closest precursor measurements and explain
  what is new.
- **Reference citation count diagnostic.** A 50+ page AN with fewer than
  25 references almost certainly has citation gaps — missing foundational
  theory, missing prior measurements, missing methodology references, or
  missing detector papers. **Fewer than 15 references in a 50+ page AN is
  Category A** — all four pilot analyses had 6-11 references, which is
  unacceptable. Fewer than 20 is Category B. A thorough AN cites
  foundational theory (~3-5), reference analyses (~3-5), detector papers
  (~2-3), methodology references (~3-5), and PDG/world-average sources
  (~3-5) — 15-25 is typical. The note writer must verify the reference
  count exceeds 15 before submitting for typesetting.
- **Phase 1 data extraction (binding).** When reference analyses are
  identified in Phase 1, the executor must extract not just the systematic
  list but also the **published numerical results** (central values and
  uncertainties at specific kinematic points) for use as quantitative
  comparison targets in Phase 4. These become binding comparison points
  at Phase 4c review (per the validation target rule §6.8). Ad-hoc
  literature lookup at Phase 5 is too late — the comparison data must
  be on disk before Phase 4a.

---

### LaTeX compilation

Markdown → PDF via a three-step pipeline: **pandoc** (>=3.0) produces a
`.tex` file, **`postprocess_tex.py`** applies deterministic structural
fixes (title math, escaped standalone math, margins, abstract→environment,
references unnumbering, table spacing, short longtable→table conversion,
FloatBarrier, needspace, duplicate headers/labels, appendix, clearpage,
stale phase label warnings), then **tectonic** (or xelatex) compiles to
PDF. The
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

- **Never use `$\pm$`, `$<$`, `$>$`, `$-$`, `$\sim$` as standalone math.**
  Use Unicode instead: `±`, `<`, `>`, `−`, `~`. Bare single-symbol math
  delimiters confuse pandoc-crossref and produce garbled output. In
  particular, `$-$0.0939` in a table cell renders as literal `$-$0.0939`
  with visible dollar signs in the PDF. Use the Unicode minus sign `−`
  (U+2212) for negative numbers outside math mode: `−0.0939`.
  Only use `$...$` for actual mathematical expressions (`$M_Z$`,
  `$\chi^2/ndf = 1.5$`).
- **YAML title field does not render LaTeX math.** Pandoc's `title:`
  field in the YAML frontmatter is treated as plain text — `$\sqrt{s}$`
  renders literally as `$\sqrt{s}$`. For mathematical symbols in titles,
  use Unicode: `√s = 91.2 GeV` or handle in `postprocess_tex.py` by
  replacing the literal string in the `.tex` output.
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
- **Figure overflow (mandatory post-compilation check).** After PDF
  compilation, run `grep "Overfull.*hbox" *.log` on the TeX log. Any
  overfull hbox involving a figure or table environment is Category A.
  The typesetter must verify that 2D plots with colorbars and multi-panel
  figures fit within `\linewidth`. Figures taller than `0.7\textheight`
  will push captions to the next page — add explicit `height=` attributes
  to oversized figures. The `build-pdf` task should be run and the log
  checked before submitting for review.

---
