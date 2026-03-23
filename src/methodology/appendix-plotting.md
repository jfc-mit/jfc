## Appendix D: Plotting Template

All plotting code must follow this template. **These rules are
non-negotiable and must be treated as gospel.** Any deviation requires an
explicit, documented justification in the experiment log explaining why
the rule cannot be followed — not a silent override. The rules exist
because past analyses produced figures with broken aspect ratios, mangled
labels, clipped content, and inconsistent styling. Following them exactly
prevents these problems.

This is the reference for any agent producing figures — whether the
executor itself or a dedicated plotting subagent.

### Base template

```python
import matplotlib.pyplot as plt
import mplhep as mh
import numpy as np

np.random.seed(42)
mh.style.use("CMS")

# --- Single plot ---
fig, ax = plt.subplots(figsize=(10, 10))
# For MxN subplots, scale to keep ratio: 2x2 -> (20, 20), 1x3 -> (30, 10)

# --- Ratio plot ---
# fig, (ax, rax) = plt.subplots(
#     2, 1, figsize=(10, 10),
#     gridspec_kw={"height_ratios": [3, 1]},
#     sharex=True,
# )
# fig.subplots_adjust(hspace=0)  # REQUIRED — no gap between main and ratio

# --- Your plotting code ---

# For histograms: mh.histplot(...)
# For 2D histograms — use hist2dplot with cbarextend to keep square aspect:
#   mh.hist2dplot(H, cbarextend=True)
#   OR for manual control:
#   im = ax.pcolormesh(...)
#   cax = mh.utils.make_square_add_cbar(ax)
#   fig.colorbar(im, cax=cax)
# For data/MC comparisons: use mh.histplot on subaxes with ratio panel

# --- Labels (required on EVERY independent axes, NOT on ratio panels) ---
# For open/archived data (this project), use "Open Data" / "Open Simulation":
#   Data plots:  exp="ALEPH", data=True,  llabel="Open Data"
#   MC plots:    exp="ALEPH", data=True,  llabel="Open Simulation"
# NOTE: always set data=True and use llabel to control the left label.
# Setting data=False auto-adds "Simulation" which stacks with llabel.
mh.label.exp_label(
    exp="<EXPERIMENT>",  # MANDATORY — e.g. "ALEPH", "CMS", "DELPHI"
    text="",         # e.g. "Preliminary" (leave "" for final)
    loc=0,
    data=True,       # Always True for open data — control label via llabel
    llabel="Open Data",  # "Open Data" for data, "Open Simulation" for MC
    year=None,       # e.g. "1992-1995"
    lumi=None,       # e.g. 160 (in pb^-1 or fb^-1)
    lumi_format="{0}",
    com=None,        # centre-of-mass energy — NOTE: CMS style prints "TeV",
                     # so for non-LHC experiments use rlabel instead, e.g.
                     # rlabel=r"$\sqrt{s} = 91.2$ GeV"
    rlabel=None,     # Overwrites right side — use for custom annotations
    ax=ax,
)

fig.savefig("output.pdf", bbox_inches="tight", dpi=200, transparent=True)
fig.savefig("output.png", bbox_inches="tight", dpi=200, transparent=True)
plt.close(fig)
```

### Rules

- **Style:** Always `mh.style.use("CMS")` as the base. Experiment branding
  comes from `exp_label`, not the style.
- **Font sizes are LOCKED.** Do not pass absolute numeric `fontsize=` values
  to ANY matplotlib call (`set_xlabel`, `set_ylabel`, `set_title`,
  `tick_params`, `annotate`, `text`). The CMS stylesheet sets all font sizes
  correctly for the 10x10 figure size. Relative string sizes (`'small'`,
  `'x-small'`, `'xx-small'`) are allowed where needed (e.g., dense legends,
  annotation text). Any script that sets a numeric font size is a Category A
  review finding.
- **Legend font size.** Always pass `fontsize="x-small"` to `ax.legend(...)`.
- **Legend placement.** The default approach is to **scale the y-axis to
  accommodate the legend** using mplhep's `mpl_magic` utility:
  ```python
  from mplhep.plot import mpl_magic
  mpl_magic(ax)  # auto-scales y-axis to fit legend without overlap
  ```
  Place legends in the upper right (`loc="upper right"`) and call
  `mpl_magic(ax)` after all plotting is done — it extends the y-range so
  the legend sits in empty space above the data. This is the preferred
  method for most plots (distributions, spectra, fits).

  Use manual placement (`loc="center right"`, `loc="lower right"`, or
  `bbox_to_anchor`) **only** when the plot has a genuinely empty region
  that the legend fits into without y-axis scaling — e.g., ROC curves
  (upper-left empty), exponential tails with no turn-on (upper-right
  empty), or log-scale plots with large dynamic range.

  **Legend-data overlap is Category A.** The plot validator must visually
  inspect every rendered figure for overlap — checking the `loc=`
  parameter in the script is necessary but not sufficient.
- **Text labels must be publication-quality.** Axis labels, legend entries,
  and tick labels must use human-readable names, not code variable names
  or Python identifiers. "Energy-dep. efficiency" not "efficiency_energy
  _dep". "Two-photon bkg" not "two_photon_bkg". "$\Gamma_l$ (external)"
  not "ext_lep_wid". Any raw code identifier visible in a rendered figure
  is Category A.
- **Aspect and colorbars (Category A if wrong).** Keep figures with square
  aspect. For ANY 2D plot with a colorbar (`pcolormesh`, `imshow`,
  `hist2dplot`), you MUST use one of these three patterns to prevent the
  colorbar from squashing the main axes:
  - `mh.hist2dplot(H, cbarextend=True)` — preferred, handles it automatically
  - `cax = mh.utils.make_square_add_cbar(ax)` then `fig.colorbar(im, cax=cax)`
  - `cax = mh.utils.append_axes(ax, extend=True)` then `fig.colorbar(im, cax=cax)`
  **Any script that uses `fig.colorbar(im)`, `fig.colorbar(im, ax=ax)`,
  `fig.colorbar(im, ax=ax, shrink=...)`, or `plt.colorbar(...)` is a
  Category A review finding.** These patterns steal space from the main
  axes, breaking the square aspect ratio. This applies to ALL 2D plots
  including correlation matrices, migration matrices, response matrices,
  2D systematic shift maps, and efficiency maps — not just the primary
  result figure. Reviewers must grep for these patterns and flag every
  occurrence.
- **2D equal-aspect ratio.** For 2D histograms where both axes use the
  same type of coordinate (e.g., two log-transformed momenta on a Lund
  plane, two spatial coordinates, two bin indices in a response matrix),
  set `ax.set_aspect('equal')` so that bins render as squares. This
  preserves the geometric interpretation of the density — non-square
  bins visually distort gradients and kinematic boundaries. This is
  separate from `figsize=(10, 10)` (which controls the figure canvas);
  `set_aspect('equal')` controls the data-coordinate scaling within the
  axes. When the axis ranges differ (e.g., x spans 7 units, y spans 6),
  the axes will be non-square within the figure — that is correct; the
  bins are square. Axes where the two coordinates have genuinely
  different units (e.g., mass vs. angle) should NOT use equal aspect.
- **No titles.** Never `ax.set_title()`. Captions go in the analysis note.
  Instead additional info can go into `ax.legend(title="...")`. And when
  truly necessary it can go into `mh.label.add_text(text, ax=ax)`.
- **No raw `ax.text()` or `ax.annotate()`.** Use `mh.label.add_text(text,
  ax=ax)` for all text annotations — it respects mplhep styling and
  positioning. This includes panel labels like `(a)`, `(b)` in grids.
- **Axis labels with units.** Always `ax.set_xlabel(...)` and
  `ax.set_ylabel(...)` with units in brackets, e.g. `r"$p_T$ [GeV]"`.
  Do not increase axis label font size beyond the stylesheet default — no
  `fontsize=` argument on `set_xlabel`/`set_ylabel`.
- **Labels on every independent axes.** In multi-panel figures where each
  panel is an independent plot (2x2 grids, side-by-side comparisons), call
  `mh.label.exp_label(...)` on EACH axes.
  **Exception: ratio plots.** For ratio plots (main panel + ratio panel
  with `sharex=True`), call `exp_label` on the MAIN panel ONLY — never
  on the ratio panel. The ratio panel is a subsidiary display, not an
  independent plot. Putting the experiment label on the ratio panel
  clutters it and is Category A.
- **Open data labeling (mandatory for this project).** All analyses in
  this project use archived/open data, not official collaboration data.
  The experiment label must reflect this:
  - **Data plots:** `exp="ALEPH", data=True, llabel="Open Data"` →
    displays "ALEPH Open Data"
  - **MC/simulation plots:** `exp="ALEPH", data=True, llabel="Open Simulation"` →
    displays "ALEPH Open Simulation"
  - Replace "ALEPH" with the appropriate experiment (DELPHI, L3, OPAL, CMS, etc.)
  - Always use `data=True` with explicit `llabel` — never `data=False`
    (which auto-adds "Simulation" and causes stacking).
  Labeling a plot as just "ALEPH" without "Open Data"/"Open Simulation"
  implies an official collaboration result and is Category A.
- **Label stacking pitfall (Category A).** When `data=False`, mplhep
  auto-adds "Simulation" as the left label. Do NOT also set `llabel` or
  `text` — this produces mangled labels like "Simulation Open Simulation".
  The safe pattern is always `data=True` with explicit `llabel`:
  - `data=True, llabel="Open Data"` → "ALEPH Open Data"
  - `data=True, llabel="Open Simulation"` → "ALEPH Open Simulation"
  - `data=True, llabel=""` → "ALEPH" (only for non-open-data contexts)
  - Never use `data=False` with `llabel` — this always stacks
- **Save as PDF and PNG.** PDF for the note, PNG for quick inspection.
  Always `bbox_inches="tight", dpi=200, transparent=True`.
- **Never use `tight_layout()` or `constrained_layout=True` with mplhep.**
  They conflict with mplhep's label positioning. Use `bbox_inches="tight"`
  at save time instead — this handles clipping without breaking the layout.
- **Close figures.** `plt.close(fig)` after saving to prevent memory leaks
  in long scripts.
- **Figure size is LOCKED at `figsize=(10, 10)`.** Do not use any other
  figure size. This is non-negotiable — the font sizes in the CMS stylesheet
  are calibrated for this size. Using `figsize=(8, 6)` or `figsize=(12, 8)`
  produces figures where text is too large or too small relative to the plot
  elements. For ratio plots, use `figsize=(10, 10)` with
  `height_ratios=[3, 1]`. For 2x2 subplots, use `figsize=(20, 20)`. The
  rule is: 10 inches per subplot column, 10 inches per subplot row.
  **Any script that uses a custom figsize is a Category A review finding.**
- **PDF rendering size (height-based).** The pandoc preamble sets the
  default image **height** (not width) to `0.45\linewidth`. Height-based
  sizing is used because figures with colorbars (2D plots, correlation
  matrices) have extended width from the colorbar axes. Setting size by
  height gives consistent visual sizing: a 1D histogram and a 2D
  colormap render at the same plot-area size even though the colormap
  PDF is physically wider. This works because all figures are square
  (`figsize=(10, 10)`), so height = plot-area width.

  Note: `postprocess_tex.py` applies a `height=0.35\textheight` cap to
  pandoc-wrapped figures to prevent overflow. This is tighter than the
  preamble default and may reduce figure size slightly in the compiled
  PDF — this is intentional to prevent captions from being pushed to the
  next page.

  | Plot type | matplotlib figsize | AN height | Example |
  |-----------|-------------------|-----------|---------|
  | Single panel | `(10, 10)` | `0.45\linewidth` (default) | Distribution, spectrum |
  | Ratio plot | `(10, 10)` | `0.45\linewidth` (default) | Data/MC with ratio |
  | 2D with colorbar | `(10, 10)` | `0.45\linewidth` (default) | Lund plane, matrix |
  | Side-by-side | Compose in LaTeX | `height=0.45\linewidth` each | See below |
  | 2x2, 3x2 grid | Compose in LaTeX | `height=0.3\linewidth` each | See below |

  **Prefer LaTeX subfigures over matplotlib grids.** Instead of producing
  a 2x3 matplotlib figure, produce 6 individual `(10, 10)` figures and
  compose them in the AN using pandoc-crossref subfigure syntax or
  side-by-side image includes. This gives better control over layout,
  captions, and cross-referencing, and avoids font-size scaling issues.

  The one exception: **tightly-coupled panels that share a physical
  x-axis** (ratio plots, pull distributions below a fit) should be
  produced as a single matplotlib figure because they require
  `sharex=True` and `hspace=0`. Panels with different x-axis
  variables (e.g., ln(k_t) and ln(1/Delta_theta) projections of the same 2D
  observable) should be produced as separate `(10, 10)` matplotlib
  figures and composed into a single AN figure via side-by-side
  `\includegraphics` in LaTeX — they are semantically related (one
  caption with (a)/(b) labels) but not
  axis-coupled. The test: if you cannot use `sharex=True`, produce
  separate matplotlib outputs.

  To override the default width for a figure that genuinely needs full
  width, use pandoc-crossref attributes in the markdown:
  `![Caption](figures/name.pdf){#fig:name width=100%}`
- **Ratio plot `sharex` and `hspace`.** Ratio plots MUST use
  `sharex=True` in `plt.subplots()` AND `fig.subplots_adjust(hspace=0)`.
  Both are non-negotiable. Without `sharex=True`, the upper panel shows
  a redundant x-axis label (e.g., "Axis 0") — this is a Category A
  review finding. Without `hspace=0`, a visible gap appears between the
  main and ratio panels — also Category A.
- **Known issue: "Axis 0" text on ratio panels with `exp_label(loc=0)`.**
  Some mplhep versions render spurious "Axis 0" text in the lower-right
  corner of ratio panels when `exp_label(loc=0)` is called on the main
  panel of a `sharex=True` figure. **Workaround:** After calling
  `exp_label(ax=ax_main, loc=0)`, suppress the artifact on the ratio
  panel:
  ```python
  # Remove spurious "Axis 0" text from ratio panel
  for txt in rax.texts:
      if "Axis" in txt.get_text():
          txt.remove()
  ```
  Alternatively, use `loc=2` (upper left) instead of `loc=0` (best) to
  avoid triggering the bug. Any figure with visible "Axis 0" text is
  Category B.
- **Ratio panel tick collision.** When using `sharex=True` with
  `hspace=0`, the main panel's bottom y-tick label (e.g., "10^0") and
  the ratio panel's top y-tick label (e.g., "1.2") collide at the
  boundary. To prevent this:
  (a) Hide the main panel's x-axis tick labels:
      `ax.tick_params(labelbottom=False)`.
  (b) Set ratio panel y-limits and ticks so the top tick doesn't crowd
      the boundary — e.g., `rax.set_ylim(0.85, 1.15)` with ticks at
      `[0.9, 1.0, 1.1]`, leaving a small margin at the top. The exact
      values depend on the ratio range; the principle is to avoid a
      y-tick label sitting at the exact panel boundary.
  Overlapping tick labels at the main/ratio boundary are Category B.
- **Y-axis bin width labels.** When labeling with "Events / [bin width]",
  round the bin width to a clean value (0.01, 0.05, 0.1, 0.5, 1, 2, 5,
  10, ...). If the natural bin width is ugly (e.g., "Tracks / 0.04583"),
  either adjust the binning to produce a round width or omit the bin
  width from the label entirely (just "Events" or "Tracks"). A non-round
  bin width in a y-axis label is Category B.
- **Suppress matplotlib offset notation.** Never allow matplotlib's
  automatic "1e6" or "1e7" offset text on axes. Either:
  (a) `ax.ticklabel_format(axis='y', style='plain')` and let tick
      labels show full numbers, or
  (b) absorb the multiplier into the axis label —
      `r"Tracks [$\times 10^6$]"` — and divide the data accordingly, or
  (c) use `ax.yaxis.set_major_formatter(...)` for custom formatting.
  A raw matplotlib offset string in a rendered figure is Category B.
- **Log scale.** Use `ax.set_yscale("log")` when the y-axis range spans
  more than 2 orders of magnitude. Linear scale is appropriate otherwise.
- **Mandatory `mh.histplot()` for raw-count histograms (Category A if violated).**
  When plotting histograms filled from raw event data (event counts, track
  counts, unweighted distributions), use `mh.histplot()`. Never use
  `ax.step()`, `ax.bar()`, or `ax.fill_between()` for these. `mh.histplot`
  computes sqrt(N) Poisson error bars automatically, which is correct for
  raw counts.

  | Data type | Correct | Wrong |
  |-----------|---------|-------|
  | Raw counts (error bars) | `mh.histplot(h, histtype="errorbar")` | `ax.errorbar(centers, h)` without yerr |
  | MC prediction (filled) | `mh.histplot(h, histtype="fill")` | `ax.fill_between()`, `ax.bar()` |
  | Stacked MC | `mh.histplot([h1,h2], stack=True)` | `ax.bar(..., bottom=...)` |
  | Theory curve (continuous) | `ax.plot(x, y)` | (correct — not binned) |

- **Derived quantities MUST pass explicit `yerr` (Category A if violated).**
  When plotting any quantity that is NOT a raw event count — normalized
  distributions, correction factors, EEC values, ratios, efficiencies,
  systematic shifts, or any value computed from raw counts — you MUST pass
  explicit uncertainties via `yerr=`. Without explicit `yerr`, mplhep
  computes error bars as sqrt(bin content), which is meaningless for
  non-count values. For example, an EEC value of 0.03 per radian gets an
  error bar of sqrt(0.03) = 0.17 — a 570% error on a quantity known to
  4%. This is silently wrong and produces figures with nonsensical error
  bars that undermine the measurement.

  You can use either `ax.errorbar()` or `mh.histplot()` — both accept
  `yerr=`. The critical requirement is that `yerr` is always provided
  for derived quantities:

  | Derived quantity | Correct (either works) | **WRONG** (no yerr — garbage errors) |
  |-----------|---------|-------|
  | Correction factors | `ax.errorbar(x, C, yerr=sigma_C)` | `mh.histplot(h_C, histtype="errorbar")` |
  |  | `mh.histplot(h_C, yerr=sigma_C, histtype="errorbar")` | |
  | Normalized dists | `ax.errorbar(x, dNdx, yerr=sigma)` | `mh.histplot(h_norm, histtype="errorbar")` |
  | EEC / event shapes | `ax.errorbar(x, eec, yerr=sigma)` | `mh.histplot(h_eec, histtype="errorbar")` |
  | Ratios | `ax.errorbar(x, ratio, yerr=sigma_r)` | `mh.histplot(h_ratio, histtype="errorbar")` |

  **The test:** Did you fill the histogram with `h.fill(raw_values)`? Then
  `mh.histplot` without explicit `yerr` is correct (auto sqrt(N) is right).
  Did you assign values with `h.view()[:] = ...` or compute the values
  from a formula? Then you MUST pass `yerr=` — either to `mh.histplot()`
  or `ax.errorbar()`. Without `yerr`, the auto-computed errors are wrong.

  **For step-style display of derived quantities** (when you want the
  histogram step aesthetic without error bars), use
  `mh.histplot(h, histtype="step")` — the step style does not draw error
  bars, so the sqrt(N) issue does not apply.

  The only exception where `mh.histplot` auto-errors ARE correct for
  non-raw-count data is weighted histograms filled with
  `h.fill(values, weight=weights)` using `Weight()` storage — mplhep
  correctly computes sqrt(sum of weights squared) in this case.
- **Deterministic.** `np.random.seed(42)` if any randomness is involved.
- **Ratio panel uncertainty bands.** When a ratio plot shows an
  uncertainty band (e.g., MC statistical uncertainty), the band must be
  described in either the legend or the caption. An unexplained shaded
  band is a Category B finding. If the band is suspiciously flat
  (constant width across all bins), verify the error computation —
  constant uncertainty is unusual for binned distributions.
- **Axis limits.** Set axis limits tight to the data range. Do not leave
  large empty regions on either axis. Use `ax.set_xlim()` and
  `ax.set_ylim()` explicitly when the auto-range includes too much
  whitespace. Log-scale y-axes should start at ~0.5x the minimum
  non-zero value, not at an arbitrary small number.
- **Sanity check: visually identical distributions.** If two
  distributions that should represent independent quantities (e.g.,
  data from different years, different systematic variations, different
  observables) appear visually indistinguishable in a plot, flag this
  for investigation. It may indicate a bug (plotting the same array
  twice), a tautological comparison, or genuinely high correlation —
  but all three explanations must be considered. Do not silently accept
  identical-looking distributions without explanation.

### Pre-commit figure verification (executor responsibility)

Before committing any plotting script, the executor MUST self-verify every
figure. This catches issues before they reach review, saving a full
review-fix cycle (~30 minutes of reviewer + fixer time per issue). The
plot validator exists as a safety net, not the primary check.

**Step 1: Code grep.** Run these checks on every plotting script:

```python
# Mandatory violations check — run before committing
import re
with open(script_path) as f:
    code = f.read()
checks = [
    ('ax.step(', 'ax.step -> use mh.histplot'),
    ('ax.bar(', 'ax.bar -> use mh.histplot (unless colorbar-related)'),
    ('ax.text(', 'ax.text -> use mh.label.add_text'),
    ('tight_layout', 'tight_layout forbidden with mplhep'),
    ('plt.colorbar', 'plt.colorbar -> use make_square_add_cbar'),
    ('set_title(', 'set_title forbidden — use caption in AN'),
]
for pattern, msg in checks:
    if pattern in code:
        print(f"VIOLATION: {msg}")
# Regex checks
if re.search(r'fig\.colorbar\(.*, ax=', code):
    print("VIOLATION: fig.colorbar(ax=) -> use cax=")
if re.search(r'fontsize=\d', code):
    print("VIOLATION: absolute fontsize forbidden — use 'x-small' etc.")
# CRITICAL: detect the derived-quantity error bar trap
# Pattern: manually assigned histogram bins + histtype="errorbar" WITHOUT yerr=
if '.view()[' in code and 'histtype="errorbar"' in code:
    # Check if yerr= is passed alongside histtype="errorbar"
    if not re.search(r'histplot\([^)]*yerr\s*=', code):
        print("VIOLATION: .view()[:] = ... with histtype='errorbar' but no yerr= — "
              "mplhep will apply sqrt(N) to non-count values, producing "
              "nonsensical error bars. Pass yerr=sigma explicitly, or use "
              "ax.errorbar(x, y, yerr=sigma) for derived quantities.")
# Positive checks — required patterns
if 'pcolormesh' in code or 'imshow' in code or 'hist2dplot' in code:
    if 'make_square_add_cbar' not in code and 'cbarextend' not in code:
        print("VIOLATION: 2D plot without make_square_add_cbar or cbarextend=True")
if 'ax.legend(' in code and 'mpl_magic' not in code:
    print("VIOLATION: legend without mpl_magic(ax) — legend-data overlap risk")
# Axis 0 suppression check — sharex ratio plots with exp_label need
# suppression of the spurious "Axis 0" text from mplhep
if 'sharex=True' in code and 'exp_label' in code:
    if 'Axis' not in code and 'loc=2' not in code:
        print("VIOLATION: sharex ratio plot with exp_label but no Axis 0 "
              "suppression — add: for txt in rax.texts: if 'Axis' in "
              "txt.get_text(): txt.remove()  OR use loc=2")
```

**Step 2: Visual inspection of every rendered PNG.** Read the PNG at actual
rendered size and check:

- [ ] Legend does not overlap any data, error bars, or curves
- [ ] All text (axis labels, tick marks, legend entries) is readable
- [ ] No duplicate experiment labels (main panel only, never on ratio)
- [ ] Variable names are publication-quality (no `_` outside LaTeX math)
- [ ] Histogram data uses `histplot` step/errorbar style (not smooth lines)
- [ ] Axis ranges are tight to the data (no excessive whitespace)
- [ ] 2D colorbars are same height as main axes (not shorter, not taller)
- [ ] 2D bins appear square when both axes have same coordinate type
- [ ] Figure contains actual data (not empty axes with only labels/ticks,
  not a placeholder, not a white canvas — if no data was plotted, the
  figure should not exist)
- [ ] **Error bar sanity.** For any derived quantity (normalized spectrum,
  EEC, correction factor, ratio, efficiency), error bars must be
  plausible — typically a few percent to tens of percent of the value,
  not larger than the signal. If error bars span the full y-axis or
  are visibly >100% relative, this almost certainly means `yerr` was
  not passed and mplhep is showing sqrt(bin content). Category A.

**Step 3: Label quality grep.** Check that no code variable names leaked
into labels:

```python
# Check legend labels and axis labels for code variable names
label_strings = re.findall(r'label=["\']([^"\']+)["\']', code)
label_strings += re.findall(r'set_xlabel\(["\']([^"\']+)["\']', code)
label_strings += re.findall(r'set_ylabel\(["\']([^"\']+)["\']', code)
for s in label_strings:
    # Skip LaTeX subscripts (underscore inside $...$)
    clean = re.sub(r'\$[^$]+\$', '', s)
    if '_' in clean:
        print(f"CODE VARIABLE NAME IN LABEL: '{s}' — use publication name")
```

Any violations found in Steps 1-3 must be fixed before committing. The
executor who produces a figure with `ax.step()` for histogram data or
`cos_th` in a legend is responsible for the resulting review cycle.

---

### Error propagation for derived quantities

When plotting derived quantities (ratios, normalized distributions,
efficiencies), uncertainties must be propagated manually — matplotlib does
not do this automatically.

**Common formulas:**
- **Normalized distribution** `(1/N) dN/dx`: `yerr[i] = sqrt(n[i]) / (N * dx[i])` where `N = sum(n)` and `dx[i]` is the bin width. For Poisson counts, `sqrt(n[i])` is the per-bin uncertainty.
- **Ratio** `R = A/B`: `sigma_R = R * sqrt((sigma_A/A)^2 + (sigma_B/B)^2)` (uncorrelated errors)
- **Efficiency** `epsilon = k/n`: use Clopper-Pearson (binomial) intervals, not Gaussian propagation. `scipy.stats.binom` provides these.
- **Bin-width-normalized** `dN/dx`: `yerr[i] = sqrt(n[i]) / dx[i]`

Always pass `yerr=` explicitly — either to `mh.histplot()` or
`ax.errorbar()` — for derived quantities. See the derived-quantities rule
above. **Never rely on mplhep auto-errors for anything other than raw
counts or properly weighted histograms.** Omitting `yerr=` on derived
quantities is Category A.

### Captions

See §5.2 for caption requirements. Captions must be self-contained and
follow the structure: **`<What> (<where>) <description/conclusion>.`**

- **What:** Name the observable or quantity being plotted.
- **Where:** For composite figures, indicate which panel: "(left)", "(right)",
  "(top left)", etc. For single figures, omit.
- **Description:** Context not visible in the plot, key observation, conclusion.

A good caption is 2-4 sentences. It must:
1. Name the plot (what observable, what selection stage, what comparison).
2. For composites: identify each panel with a positional pointer, then describe.
3. State context not visible in the plot (selection applied, normalization
   method, which phase/systematic this validates, connection to other results).
4. State the key observation or conclusion the reader should draw.

**Do NOT restate what is already in the legend or axis labels.** If the
legend says "Data (black)" and "MC (blue)", the caption does not need to
repeat this. The caption adds information the plot alone cannot convey.

**Examples:**

Bad (Category A — too sparse):
> "Thrust distribution."

Bad (redundant with legend):
> "Data (black points) are compared to MC simulation (blue histogram).
> The lower panel shows the data/MC ratio; the grey band indicates
> the MC statistical uncertainty."

Good:
> "Charged hadron multiplicity after the hadronic event selection,
> normalized to equal area. The mean multiplicity of ~20 is characteristic
> of hadronic Z decays. Data/MC agreement is within 2% across the full
> range; the low-multiplicity tail is sensitive to two-photon background
> contamination (see §5.3)."

Good:
> "Measured hadronic cross-section as a function of centre-of-mass energy
> with the best-fit BW+ISR curve. The fit uses statistical errors only
> (inner bars); outer bars show total uncertainties including systematics.
> The fit yields chi^2/ndf = 3.07/2 (p = 0.22). The off-peak points at
> 89.4 and 93.0 GeV provide the primary constraint on Gamma_Z."

Sparse captions — anything under two full sentences — are Category A.

### Figure compositing in the AN

Group related figures side-by-side in the AN rather than presenting them
as separate full-page figures. **Do NOT use `\subfloat` or `\subcaptionbox`**
— these produce clunky layouts with redundant sub-captions, excessive
whitespace, and small panels. Instead, use simple side-by-side
`\includegraphics` with a single unified caption.

**Compositing pattern (pairs):**
```latex
\begin{figure}[!htbp]
\centering
\includegraphics[height=0.38\linewidth]{figures/left.pdf}\hspace{1em}
\includegraphics[height=0.38\linewidth]{figures/right.pdf}
\caption{The ln(1/Delta-theta) projection (left) and ln(kt) projection
  (right) of the unfolded Lund plane density from Figure X, compared to
  Pythia 8 Monash and Pythia 6. Both projections show ...}
\label{fig:label}
\end{figure}
```

**Compositing pattern (2x2 grid):**
```latex
\begin{figure}[!htbp]
\centering
\includegraphics[height=0.32\linewidth]{figures/tl.pdf}\hspace{1em}
\includegraphics[height=0.32\linewidth]{figures/tr.pdf}\\[0.5em]
\includegraphics[height=0.32\linewidth]{figures/bl.pdf}\hspace{1em}
\includegraphics[height=0.32\linewidth]{figures/br.pdf}
\caption{Shift maps for four sub-dominant sources: angular resolution
  (top left), non-closure (top right), thrust axis (bottom left), and
  momentum resolution (bottom right). All are below 1\% ...}
\label{fig:label}
\end{figure}
```

**Caption structure for composites:** Follow the `<What> (<where>)
<description>` pattern. Name each panel's content with a positional
pointer, then describe the joint conclusion:

> "The ln(1/Delta-theta) projection (left) and the ln(kt/GeV) projection
> (right) of the unfolded ALEPH data from Figure 27, compared to Pythia 8
> Monash (blue) and Pythia 6 (red dashed). Data lies 10-30% above both
> generators in the perturbative region, confirming the soft radiation
> deficit is not tune-specific."

**Key rules:**
- Use `height=` (not `width=`) so panels with different aspect ratios
  align visually at the same height.
- Minimum panel height: `0.30\linewidth`. Below this, text becomes illegible.
- No `(a)`, `(b)` labels — use "(left)", "(right)" in the caption text.
- The caption is a single paragraph synthesizing both panels, not a
  concatenation of individual captions.

**All compositing MUST be done in LaTeX.** Never use PIL, matplotlib
grid stitching, or any external image-combining tool to create composite
figures. LaTeX `\includegraphics` with `\hspace{1em}` and `\\[0.5em]` gives
correct sizing, centering, and spacing. External stitching produces
inconsistent DPI, wrong font sizes, visual artifacts, and figures that
look qualitatively different from the rest of the document. If LaTeX
compositing cannot achieve the desired layout, that is a signal to
simplify the layout, not to reach for an external tool.

**Visual appeal check (mandatory for composites).** After compositing,
inspect the rendered PDF for visual consistency:
- Are all panels the same size? Different aspect ratios (e.g., 2D
  colormesh vs 1D with ratio panel) produce different-sized panels at
  the same `height=` setting. When mixing types, adjust per-panel
  heights individually or group same-type panels together.
- Is the grid symmetric and centered? No ragged edges.
- Is the overall figure centered on the page with uniform small gaps
  between panels?
- Would a reviewer find the layout professional? If it looks like
  images were haphazardly pasted together, redo it.

**Sizing reference:**

| Grid | Per-panel height | Use case |
|------|-----------------|----------|
| 1x2 (pair) | `0.38\linewidth` | Projection comparisons, matrix pairs |
| 2x2 | `0.32\linewidth` | Sub-dominant shift maps |
| 1x3 (row) | `0.30\linewidth` | Simple data/MC surveys |
| 2x3 | `0.30\linewidth` | Per-subperiod or per-cut comparisons |
| 3x3 | `0.28\linewidth` | Full input variable survey |

**Data/MC comparison surveys.** Simple data/MC distributions (one
main panel + one ratio panel, same axis style) are highly compressible.
Use **3 columns** spanning the full page width — these plots are
visually simple and remain legible at `0.30\linewidth` height. A 7-plot
track variable survey becomes a 3+3+1 or 4+3 grid; a 5-plot event
variable survey becomes a 3+2 grid. Do NOT use 2-column layout for
simple data/MC — it wastes page space and produces unnecessarily large
panels for figures that carry little visual complexity.

**Variable survey and per-cut compositions.** When presenting N
related distributions (input variable data/MC comparisons, per-cut
motivation plots, per-systematic shift maps, per-subperiod
comparisons), compose them as a single multi-panel figure rather than
N separate figures. Produce individual `(10, 10)` figures per the
standard rules, then reference them in the AN as a composed grid.

### Figure cross-referencing

Use pandoc-crossref syntax for numbered figure references in analysis notes:

- **Label every figure:** `![Caption text](figures/name.pdf){#fig:name}`
- **Reference figures:** `@fig:name` (produces "fig. X")
- **At sentence start:** `Figure @fig:name` (capitalized)
- **Never use** `[-@fig:...]` — always use `@fig:name` for full references
- Tables use `{#tbl:name}` and `@tbl:name`; equations use `{#eq:name}` and
  `@eq:name`

### Correlation and covariance visualizations

Correlations between variables, bins, or systematic sources must be shown
as **matrix heatmaps** (using `mh.hist2dplot` or `ax.pcolormesh` with a
diverging colormap like `RdBu_r`, centered at 0 for correlations). Never
show correlations as overlaid 1D distributions or scatter-plot grids —
these are unreadable for more than ~3 variables. For the correlation
matrix specifically:
- Use `vmin=-1, vmax=1` with a diverging colormap
- Annotate cells with values if the matrix is small enough (< 10x10)
- For large matrices, show the heatmap without annotations but with a
  clear colorbar

### Systematic breakdown plots

When a systematic breakdown shows any single source with relative uncertainty
>100% in a bin, investigate — this typically indicates a bug in the variation
processing or an edge effect in a low-stats bin. Clip or flag such bins rather
than letting them dominate the y-axis scale. If the large variation is genuine
(e.g., a very low-stats bin), document the explanation in the artifact.

### Delegation to plotting subagent

Plotting should be delegated to a dedicated subagent. When
spawning a plotting subagent, the parent agent must include in the prompt:

1. **This entire appendix** (copy the template and rules above into the
   subagent prompt so it has the style reference in context)
2. The data to plot (file paths or serialized arrays)
3. What kind of plot (histogram, ratio, 2D, overlay)
4. Axis labels and ranges
5. The experiment label parameters (exp, com, lumi, data flag)
6. Output path

The plotting agent applies this template and produces the figure. It does not
make physics decisions about what to plot or how to interpret the result.

### Conceptual and schematic diagrams

Not all AN figures are data plots. Conceptual diagrams — analysis flow
charts, correction chains, sample composition schematics, region
definitions — fill gaps where data plots alone don't convey the
methodology. These are embedded in the relevant AN sections (not a
standalone chapter): a correction-chain diagram goes in the Corrections
section, a region-definition diagram goes in Event Selection.

**The figure-scrolling test.** The whole physics story should be
understandable by scrolling through the figures alone. If a reader
encounters a non-trivial method (sample merging, correction chain,
tagging strategy) with no visual explanation, a diagram is missing.
This gives reviewers a concrete criterion: can you understand the
analysis flow from figures alone?

**Production rules:**
- Use `mh.style.use("CMS")` for consistent styling with data plots.
- Experiment labels (`exp_label`) are NOT required — these are not data plots.
- The `figsize=(10, 10)` constraint does NOT apply. Use whatever size
  fits the content naturally (e.g., wide flow charts, tall chains).
- Build diagrams with matplotlib patches, arrows, `FancyBboxPatch`,
  `FancyArrowPatch`, and `ax.text()` (exception to the `ax.text` rule —
  conceptual diagrams are not data plots and `mh.label.add_text` is not
  appropriate for schematic elements).
- Save as both PDF and PNG: `bbox_inches="tight", dpi=200, transparent=True`.
- Captions must be 2+ sentences following the standard format.

**Common diagram types:**
- **Analysis flow:** boxes for each processing stage, arrows for data
  flow, branching for signal/control regions
- **Sample composition:** stacked or grouped boxes showing which physics
  processes contribute at each selection stage
- **Correction chain:** sequence of corrections with inputs/outputs at
  each step (e.g., detector→particle level, unfolding, efficiency)
- **Region definitions:** schematic of signal, control, and validation
  regions in discriminant space

Conceptual diagrams are encouraged, not mandatory. They are identified
during Phase 1 (strategy) and produced during Phase 5 (documentation).
The figure-scrolling test is the quality criterion.
