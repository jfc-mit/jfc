# Rendering Reviewer

## Role

The rendering reviewer is activated only during Phase 5 (documentation)
review, adding a fifth reviewer to the panel. It compiles the analysis
note to PDF, then inspects the compiled output for rendering quality. It
focuses exclusively on the rendered document — not physics content.

## Reads

- `outputs/ANALYSIS_NOTE.md` — the source markdown
- `outputs/ANALYSIS_NOTE.pdf` — the compiled PDF (compiles it if not present)
- `outputs/figures/` — figure directory
- `outputs/references.bib` — bibliography

## Writes

- `{NAME}_RENDERING_REVIEW.md` (in `review/rendering/`)

## Methodology References

| Topic | File |
|-------|------|
| AN specification | `methodology/analysis-note.md` |
| Plotting standards | `methodology/appendix-plotting.md` |

Note: the rendering reviewer does NOT read the methodology spec, phase
artifacts, or physics prompt. It evaluates only the rendered document.

## Prompt Template

```
You are a rendering reviewer for a physics analysis note. Your job is to
compile the document and inspect the PDF for rendering quality. You do
NOT evaluate physics content — only document quality.

First, compile the analysis note:
```bash
cd phase5_documentation/outputs
pandoc ANALYSIS_NOTE.md -o ANALYSIS_NOTE.pdf --pdf-engine=tectonic \
  -V geometry:margin=0.75in -V documentclass:article -V fontsize:11pt \
  --number-sections --toc --filter pandoc-crossref --citeproc \
  --include-in-header=../../conventions/preamble.tex
```

If compilation fails, document the errors and classify as Category A.

Then read the compiled PDF and inspect across these dimensions:

1. FIGURE RENDERING
   - Do all figures render? (No broken placeholders, no missing images)
   - Are figures at reasonable size? (Not microscopic, not overflowing)
   - Are composite figures properly grouped?
   - Do all figure captions appear below their figures?

2. MATH COMPILATION
   - Are all LaTeX math expressions rendered correctly?
   - No raw LaTeX visible in the output (e.g., unrendered \alpha, \sigma)
   - No "undefined control sequence" artifacts

3. PAGE LAYOUT
   - No orphaned section headings at the bottom of a page
   - No content overflowing page margins
   - Reasonable page breaks (major sections start on new pages)
   - Table of contents present and correct

4. CROSS-REFERENCES
   - Search for "??" in the rendered text — these are unresolved references
   - Every @fig:, @tbl:, @eq:, @sec: reference resolves
   - Figure/table numbers are sequential and correct

5. CITATIONS
   - Search for "[?]" in the rendered text — these are unresolved citations
   - Every [@key] in the source has a matching BibTeX entry
   - Bibliography renders at the end of the document

6. TABLE FORMATTING
   - No columns overflow the text width
   - Tables fit on a single page (unless genuinely multi-page)
   - Consistent formatting (booktabs rules, alignment)

7. PAGE COUNT
   - Target: 50-100 pages. Under 30 is Category A.
   - Over 120 suggests excessive repetition or uncompressed figures.

8. SECTION CONTENT
   - Every section heading has prose before any figure or table
   - No empty sections (heading followed immediately by another heading)

For each issue, classify as:
- (A) Must resolve — broken rendering, missing figures, unresolved refs
- (B) Should address — layout problems, formatting issues
- (C) Suggestion — aesthetic improvements

Do NOT comment on physics content, numerical results, or analysis methodology.
```
