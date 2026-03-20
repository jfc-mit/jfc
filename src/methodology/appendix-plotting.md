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
  panel is an independent plot (2×2 grids, side-by-side comparisons), call
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
  `height_ratios=[3, 1]`. For 2×2 subplots, use `figsize=(20, 20)`. The
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

  | Plot type | matplotlib figsize | AN height | Example |
  |-----------|-------------------|-----------|---------|
  | Single panel | `(10, 10)` | `0.45\linewidth` (default) | Distribution, spectrum |
  | Ratio plot | `(10, 10)` | `0.45\linewidth` (default) | Data/MC with ratio |
  | 2D with colorbar | `(10, 10)` | `0.45\linewidth` (default) | Lund plane, matrix |
  | Side-by-side | Compose in LaTeX | `height=0.45\linewidth` each | See below |
  | 2×2, 3×2 grid | Compose in LaTeX | `height=0.3\linewidth` each | See below |

  **Prefer LaTeX subfigures over matplotlib grids.** Instead of producing
  a 2×3 matplotlib figure, produce 6 individual `(10, 10)` figures and
  compose them in the AN using pandoc-crossref subfigure syntax or
  side-by-side image includes. This gives better control over layout,
  captions, and cross-referencing, and avoids font-size scaling issues.

  The one exception: **tightly-coupled panels that share axes** (ratio
  plots, pull distributions below a fit) should be produced as a single
  matplotlib figure because they require `sharex=True` and `hspace=0`.

  To override the default width for a figure that genuinely needs full
  width, use pandoc-crossref attributes in the markdown:
  `![Caption](figures/name.pdf){#fig:name width=100%}`
- **Ratio plot `sharex` and `hspace`.** Ratio plots MUST use
  `sharex=True` in `plt.subplots()` AND `fig.subplots_adjust(hspace=0)`.
  Both are non-negotiable. Without `sharex=True`, the upper panel shows
  a redundant x-axis label (e.g., "Axis 0") — this is a Category A
  review finding. Without `hspace=0`, a visible gap appears between the
  main and ratio panels — also Category A.
- **Log scale.** Use `ax.set_yscale("log")` when the y-axis range spans
  more than 2 orders of magnitude. Linear scale is appropriate otherwise.
- **Prefer mplhep functions** (`mh.histplot`, `mh.hist2dplot`) over raw
  matplotlib `ax.hist` / `ax.pcolormesh`. They handle binning, styling,
  and error bars correctly for HEP conventions.
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
  whitespace. Log-scale y-axes should start at ~0.5× the minimum
  non-zero value, not at an arbitrary small number.
- **Sanity check: visually identical distributions.** If two
  distributions that should represent independent quantities (e.g.,
  data from different years, different systematic variations, different
  observables) appear visually indistinguishable in a plot, flag this
  for investigation. It may indicate a bug (plotting the same array
  twice), a tautological comparison, or genuinely high correlation —
  but all three explanations must be considered. Do not silently accept
  identical-looking distributions without explanation.

### Error propagation for derived quantities

When plotting derived quantities (ratios, normalized distributions,
efficiencies), uncertainties must be propagated manually — matplotlib does
not do this automatically.

**Common formulas:**
- **Normalized distribution** `(1/N) dN/dx`: `yerr[i] = sqrt(n[i]) / (N * dx[i])` where `N = sum(n)` and `dx[i]` is the bin width. For Poisson counts, `sqrt(n[i])` is the per-bin uncertainty.
- **Ratio** `R = A/B`: `sigma_R = R * sqrt((sigma_A/A)^2 + (sigma_B/B)^2)` (uncorrelated errors)
- **Efficiency** `ε = k/n`: use Clopper-Pearson (binomial) intervals, not Gaussian propagation. `scipy.stats.binom` provides these.
- **Bin-width-normalized** `dN/dx`: `yerr[i] = sqrt(n[i]) / dx[i]`

Always pass `yerr=` explicitly to `mh.histplot()` or `ax.errorbar()` for
derived quantities. `mh.histplot` auto-errors are only correct for raw event
counts or weighted histograms — NOT for `(1/N) dN/dx`, ratios, efficiencies,
or other post-processed quantities. Relying on auto-errors for derived
quantities is a Category A review finding.

### Captions

See §5.2 for caption requirements. Captions must be self-contained and
follow the format: **`<Plot name>. <Context and conclusion.>`**

A good caption is 2-4 sentences. It must:
1. Name the plot (what observable, what selection stage, what comparison).
2. State context not visible in the plot (selection applied, normalization
   method, which phase/systematic this validates, connection to other results).
3. State the key observation or conclusion the reader should draw.

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
> The fit yields χ²/ndf = 3.07/2 (p = 0.22). The off-peak points at
> 89.4 and 93.0 GeV provide the primary constraint on Γ_Z."

Sparse captions — anything under two full sentences — are Category A.

### Subfigures and figure grouping

Group related figures into grids rather than presenting them as separate
figures. Use letter labels (`(a)`, `(b)`, etc.) with
`mh.label.add_text("(a)", ax=ax)` in each panel.
Write a single caption describing all sub-panels. This keeps the note
compact and makes comparisons easier for the reader.

**Grid sizing:** Selection cut distributions can be grouped into a 3×3 grid
with a single caption. Related comparisons (e.g., data/MC for multiple
variables) should be side-by-side. A 2×2 grid uses `figsize=(20, 20)`, a
3×3 uses `figsize=(30, 30)` — following the 10-inches-per-subplot rule.

**Variable survey and per-cut compositions.** When presenting N
related distributions (input variable data/MC comparisons, per-cut
motivation plots, per-systematic shift maps, per-subperiod
comparisons), compose them as a single multi-panel figure rather than
N separate figures. Produce individual `(10, 10)` figures per the
standard rules, then reference them in the AN as a composed grid.
Sizing for composed grids in the AN:

| Grid | Per-panel height | Example |
|------|-----------------|---------|
| 2×2 | `0.35\linewidth` | Data/MC for 4 key variables |
| 3×3 | `0.28\linewidth` | Full input variable survey |
| 2×3 | `0.30\linewidth` | Per-subperiod comparisons |

Use `(a)`–`(i)` panel labels in each individual figure via
`mh.label.add_text("(a)", ax=ax)`. Write one shared caption for the
composed figure describing all panels. In the AN markdown, use
side-by-side image syntax or pandoc-crossref subfigure syntax.

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
- Annotate cells with values if the matrix is small enough (< 10×10)
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
