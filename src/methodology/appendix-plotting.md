## Appendix D: Plotting Template

All plotting code must follow this template. This is the reference for any
agent producing figures — whether the executor itself or a dedicated plotting
subagent.

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
# fig.subplots_adjust(hspace=0.0)

# --- Your plotting code ---

# For histograms: mh.histplot(...)
# For 2D histograms — use hist2dplot with cbarextend to keep square aspect:
#   mh.hist2dplot(H, cbarextend=True)
#   OR for manual control:
#   im = ax.pcolormesh(...)
#   cax = mh.utils.make_square_add_cbar(ax)
#   fig.colorbar(im, cax=cax)
# For data/MC comparisons: use mh.histplot on subaxes with ratio panel

# --- Labels (required on EVERY axes in multi-panel figures) ---
mh.label.exp_label(
    exp="",          # e.g. "ALEPH", "CMS"
    text="",         # e.g. "Preliminary" (leave "" for final)
    loc=0,
    data=False,      # True when real data is used (suppresses "Simulation")
    year=None,       # e.g. "1992-1995"
    lumi=None,       # e.g. 160 (in pb^-1 or fb^-1)
    lumi_format="{0}",
    com=None,        # centre-of-mass energy — NOTE: CMS style prints "TeV",
                     # so for non-LHC experiments use rlabel instead, e.g.
                     # rlabel=r"$\sqrt{s} = 91.2$ GeV"
    llabel=None,     # Overwrites left side (after exp). NOTE: when data=False,
                     # "Simulation" is auto-added. If you set llabel, also set
                     # text="" to avoid "Simulation" + llabel stacking.
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
- **Font sizes are LOCKED.** Do not pass `fontsize=` to ANY matplotlib call
  (`set_xlabel`, `set_ylabel`, `set_title`, `tick_params`, `annotate`,
  `text`). The CMS stylesheet sets all font sizes correctly for the 10x10
  figure size. The ONLY exception is `ax.legend(fontsize="x-small")`. Any
  script that sets a custom font size is a Category A review finding.
- **Legend font size.** Always pass `fontsize="x-small"` to `ax.legend(...)`.
- **Aspect.** Keep figures with square aspect. For 2D plots with colorbars,
  you MUST use one of these to prevent the colorbar from squashing the plot:
  - `mh.hist2dplot(H, cbarextend=True)` — preferred, handles it automatically
  - `cax = mh.utils.make_square_add_cbar(ax)` then `fig.colorbar(im, cax=cax)`
  - `cax = mh.utils.append_axes(ax, extend=True)` then `fig.colorbar(im, cax=cax)`
  Never just do `fig.colorbar(im)` or `plt.colorbar()` — these steal space
  from the axes and break the square aspect.
- **No titles.** Never `ax.set_title()`. Captions go in the analysis note.
  Instead additional info can go into `ax.legend(title="...")`. And when
  truly necessary it can go into `mh.utils.add_text(text, ax=ax)`
- **Axis labels with units.** Always `ax.set_xlabel(...)` and
  `ax.set_ylabel(...)` with units in brackets, e.g. `r"$p_T$ [GeV]"`.
  Do not increase axis label font size beyond the stylesheet default — no
  `fontsize=` argument on `set_xlabel`/`set_ylabel`.
- **Labels on every axes.** In multi-panel figures, call
  `mh.label.exp_label(...)` on EACH axes, not just the first one.
- **Label stacking pitfall.** When `data=False`, mplhep auto-adds
  "Simulation" as the text. If you also set `llabel="MC Simulation"`, you
  get "Simulation MC Simulation" overlapping. Fix: either use `data=False`
  alone (gives "Simulation"), or set `data=True, llabel="MC Simulation"`
  to fully control the left side.
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
- **PDF rendering size.** Figures are rendered at `0.5\textwidth` (half page
  width) in the compiled analysis note PDF. The 10x10 matplotlib figure size
  produces clean, readable plots at this rendered size. Do not make figures
  full-width unless they are genuinely complex (e.g., large correlation
  matrices, multi-panel comparisons). Half-width allows two figures
  side-by-side and keeps the note compact.
- **Prefer mplhep functions** (`mh.histplot`, `mh.hist2dplot`) over raw
  matplotlib `ax.hist` / `ax.pcolormesh`. They handle binning, styling,
  and error bars correctly for HEP conventions.
- **Deterministic.** `np.random.seed(42)` if any randomness is involved.

### Delegation to plotting subagent

Plotting should be delegated to a lightweight (Haiku-tier) subagent. When
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
