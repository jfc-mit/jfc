"""
common.plotting — standardized figure creation and saving for HEP analyses.

WHY THIS MODULE EXISTS
----------------------
Methodology Appendix D specifies a strict set of plotting rules that every
executor must follow.  Because those rules are non-trivial (correct figsize,
mplhep CMS style, no titles, dual PDF+PNG output, sidecar captions, …) and
because Category A review findings are triggered by any deviation, this module
*encodes* the rules so that executors cannot accidentally violate them.

The three main guarantees this module provides:

1. **Style is applied once, globally.**  ``mh.style.use("CMS")`` is called at
   import time.  Executors never need to (and must never try to) call it again.

2. **Figure sizing is enforced.**  ``create_figure`` and ``create_ratio_figure``
   compute the correct ``figsize`` from the grid dimensions.  There is no
   parameter to pass a custom size.

3. **Save conventions are enforced.**  ``save_figure`` runs assertions before
   writing — no title on any axes, correct figsize — and always writes both
   ``.pdf`` and ``.png`` with the required options, closes the figure, and
   writes a sidecar ``.caption`` file.

USAGE EXAMPLE
-------------
::

    from common.plotting import (
        create_figure,
        create_ratio_figure,
        add_experiment_label,
        save_figure,
        figure_ref,
    )

    fig, ax = create_figure()
    mh.histplot(counts, bins, ax=ax)
    ax.set_xlabel(r"$p_T$ [GeV]")
    ax.set_ylabel("Events")
    ax.legend(fontsize="x-small")
    add_experiment_label(ax, text="Preliminary", data=True, lumi=160)
    save_figure(fig, "plots/pt_spectrum", caption=r"Transverse momentum spectrum.")
    # → writes plots/pt_spectrum.pdf, plots/pt_spectrum.png,
    #   plots/pt_spectrum.caption

FONT SIZES
----------
Do NOT pass ``fontsize=`` to ``ax.set_xlabel``, ``ax.set_ylabel``,
``ax.tick_params``, ``ax.annotate``, or ``ax.text``.  The CMS stylesheet sets
all font sizes correctly for the 10×10 figure size.  The ONLY allowed
exception is ``ax.legend(fontsize="x-small")`` — which ``create_figure``
documents and which ``save_figure`` does not (cannot) assert on, but reviewers
will flag any deviation.

TITLES
------
Never call ``ax.set_title()``.  Captions belong in the analysis note, not on
the axes.  ``save_figure`` asserts that no axes in the figure has a non-empty
title and will raise ``AssertionError`` if one is found.

LAYOUT HELPERS
--------------
Never call ``fig.tight_layout()`` or pass ``constrained_layout=True`` to
``plt.subplots``.  They conflict with mplhep's label positioning.  Use
``bbox_inches="tight"`` at save time (which ``save_figure`` always does).
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional, Tuple

import matplotlib
import matplotlib.pyplot as plt
import mplhep as mh
from rich.logging import RichHandler

# ---------------------------------------------------------------------------
# Module-level logging — no bare print() anywhere in this module.
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Global style — applied ONCE at import.  Executors must not call this again.
# ---------------------------------------------------------------------------
mh.style.use("CMS")
log.debug("mplhep CMS style applied at import of common.plotting")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Inches per subplot column and per subplot row.  The CMS stylesheet font
#: sizes are calibrated for this value — do not change it.
_INCHES_PER_CELL: int = 10

#: Save parameters enforced by save_figure.
_SAVE_KWARGS: dict = {
    "bbox_inches": "tight",
    "dpi": 200,
    "transparent": True,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def create_figure(
    nrows: int = 1,
    ncols: int = 1,
    **subplot_kwargs,
) -> Tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]:
    """Create a single (or multi-panel) figure with enforced sizing and style.

    Parameters
    ----------
    nrows, ncols:
        Grid dimensions.  ``figsize`` is computed as
        ``(ncols * 10, nrows * 10)`` — this is non-negotiable.
    **subplot_kwargs:
        Passed verbatim to ``plt.subplots``.  Do NOT include ``figsize``,
        ``constrained_layout``, or ``tight_layout`` — they are rejected or
        overridden.

    Returns
    -------
    fig, ax(es)
        Same shape as ``plt.subplots``.

    Raises
    ------
    ValueError
        If the caller attempts to pass a custom ``figsize``.
    """
    if "figsize" in subplot_kwargs:
        raise ValueError(
            "Do not pass figsize to create_figure. "
            "Figure size is locked at 10 inches per subplot cell "
            "(methodology Appendix D). "
            f"Got figsize={subplot_kwargs['figsize']!r}."
        )
    if subplot_kwargs.pop("constrained_layout", None):
        log.warning(
            "constrained_layout=True was stripped — it conflicts with "
            "mplhep label positioning.  Use bbox_inches='tight' at save time."
        )
    if subplot_kwargs.pop("tight_layout", None):
        log.warning(
            "tight_layout was stripped — it conflicts with mplhep label "
            "positioning.  Use bbox_inches='tight' at save time."
        )

    figsize = (ncols * _INCHES_PER_CELL, nrows * _INCHES_PER_CELL)
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize, **subplot_kwargs)
    log.debug("create_figure: %dx%d grid, figsize=%s", nrows, ncols, figsize)
    return fig, axes


def create_ratio_figure() -> Tuple[
    matplotlib.figure.Figure,
    matplotlib.axes.Axes,
    matplotlib.axes.Axes,
]:
    """Create the standard data/MC ratio figure layout.

    The figure is (10, 10) with a 3:1 height split — a main axes on top and
    a ratio axes below, sharing the x-axis.  ``hspace`` is set to 0 so the
    panels are flush.

    Returns
    -------
    fig, ax, rax
        ``ax``  — main (upper) panel.
        ``rax`` — ratio (lower) panel.

    Notes
    -----
    - Set x-axis labels on ``rax``, not ``ax``.
    - Do not call ``ax.set_xlabel`` on the upper panel — the shared x-axis
      means tick labels are already suppressed there.
    - Add the experiment label to BOTH panels::

          add_experiment_label(ax, ...)
          add_experiment_label(rax, ...)
    """
    fig, (ax, rax) = plt.subplots(
        2,
        1,
        figsize=(_INCHES_PER_CELL, _INCHES_PER_CELL),
        gridspec_kw={"height_ratios": [3, 1]},
        sharex=True,
    )
    fig.subplots_adjust(hspace=0.0)
    log.debug("create_ratio_figure: height_ratios=[3,1], hspace=0")
    return fig, ax, rax


def add_experiment_label(
    ax: matplotlib.axes.Axes,
    exp: str = "ALEPH",
    text: str = "",
    loc: int = 0,
    data: bool = False,
    year: Optional[str] = None,
    lumi: Optional[float] = None,
    lumi_format: str = "{0}",
    com: Optional[float] = None,
    llabel: Optional[str] = None,
    rlabel: Optional[str] = None,
) -> None:
    """Add the experiment label to an axes via ``mh.label.exp_label``.

    Defaults are set for ALEPH analyses.  Override as needed.

    Parameters
    ----------
    ax:
        Target axes.
    exp:
        Experiment name, e.g. ``"ALEPH"``, ``"CMS"``.
    text:
        Sub-experiment tag shown after the experiment name, e.g.
        ``"Preliminary"``.  Leave ``""`` for final results.
    loc:
        Label location (mplhep convention: 0 = upper-left).
    data:
        ``True`` when real collision data is shown.  When ``False``, mplhep
        auto-adds "Simulation".  Do NOT also set ``llabel="MC Simulation"``
        when ``data=False`` — that produces overlapping text.
    year:
        Data-taking years, e.g. ``"1992-1995"``.
    lumi:
        Integrated luminosity in pb⁻¹ or fb⁻¹.
    lumi_format:
        Format string for lumi value (default ``"{0}"``).
    com:
        Centre-of-mass energy.  NOTE: CMS style appends "TeV", so for
        non-LHC experiments pass ``com=None`` and use ``rlabel`` instead,
        e.g. ``rlabel=r"$\\sqrt{s} = 91.2$ GeV"``.
    llabel:
        Overrides the left-side text.  Use with care — see ``data`` note.
    rlabel:
        Overrides the right-side text.  Preferred over ``com`` for
        non-LHC experiments.

    Notes
    -----
    Call this function on EVERY axes in a multi-panel figure, not just the
    first one.
    """
    mh.label.exp_label(
        exp=exp,
        text=text,
        loc=loc,
        data=data,
        year=year,
        lumi=lumi,
        lumi_format=lumi_format,
        com=com,
        llabel=llabel,
        rlabel=rlabel,
        ax=ax,
    )
    log.debug(
        "add_experiment_label: exp=%r text=%r data=%r lumi=%r com=%r rlabel=%r",
        exp, text, data, lumi, com, rlabel,
    )


def save_figure(
    fig: matplotlib.figure.Figure,
    path: str | os.PathLike,
    caption: str = "",
) -> None:
    """Save a figure as PDF and PNG, write a sidecar caption file, close it.

    ``path`` is the stem — ``.pdf`` and ``.png`` are appended automatically.
    The parent directory is created if it does not exist.

    Parameters
    ----------
    fig:
        The figure to save.  It is closed after saving regardless of whether
        the save succeeds, to prevent memory leaks in long scripts.
    path:
        Output path *without* extension, e.g. ``"plots/pt_spectrum"``.
    caption:
        Caption text.  Written to ``<path>.caption`` alongside the images
        for later inclusion in the analysis note.  May be an empty string.

    Raises
    ------
    AssertionError
        If any axes in the figure has a non-empty title (use of
        ``ax.set_title`` is prohibited — methodology Appendix D).
    AssertionError
        If the figure size deviates from the expected 10-inches-per-cell
        grid (protects against figsize mutations after ``create_figure``).

    Notes
    -----
    - Never call ``fig.tight_layout()`` before ``save_figure`` — it is not
      needed and conflicts with mplhep labels.
    - Always pass the full stem path; do not append the extension yourself.
    """
    stem = Path(path)
    stem.parent.mkdir(parents=True, exist_ok=True)

    # --- Assertions ---
    _assert_no_titles(fig)
    _assert_correct_figsize(fig)

    # --- Save ---
    pdf_path = stem.with_suffix(".pdf")
    png_path = stem.with_suffix(".png")

    fig.savefig(pdf_path, **_SAVE_KWARGS)
    log.info("Saved %s", pdf_path)

    fig.savefig(png_path, **_SAVE_KWARGS)
    log.info("Saved %s", png_path)

    # --- Sidecar caption ---
    caption_path = stem.with_suffix(".caption")
    caption_path.write_text(caption, encoding="utf-8")
    log.debug("Caption written to %s", caption_path)

    # --- Close ---
    plt.close(fig)
    log.debug("Figure closed")


def figure_ref(path: str | os.PathLike, caption: str) -> str:
    """Return the markdown image reference string for an analysis note artifact.

    Parameters
    ----------
    path:
        Path to the figure file (PDF or PNG).  Pass the full path including
        extension.
    caption:
        Caption text displayed in the markdown rendered view and used as the
        alt-text.

    Returns
    -------
    str
        Markdown string of the form ``![caption](path)``.

    Example
    -------
    ::

        ref = figure_ref("plots/pt_spectrum.png",
                         r"Transverse momentum spectrum.")
        # → "![Transverse momentum spectrum.](plots/pt_spectrum.png)"
        # Paste this string directly into ANALYSIS_NOTE.md or SELECTION.md.
    """
    return f"![{caption}]({path})"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _assert_no_titles(fig: matplotlib.figure.Figure) -> None:
    """Raise AssertionError if any axes in *fig* has a non-empty title."""
    for i, ax in enumerate(fig.axes):
        title = ax.get_title()
        assert not title, (
            f"ax.set_title() is prohibited (methodology Appendix D). "
            f"Axes index {i} has title {title!r}. "
            "Move descriptive text to the analysis note caption instead. "
            "If annotation is necessary, use mh.utils.add_text() or "
            "ax.legend(title=...)."
        )


def _assert_correct_figsize(fig: matplotlib.figure.Figure) -> None:
    """Raise AssertionError if the figure size is not a valid 10-per-cell grid."""
    w, h = fig.get_size_inches()
    # Sizes must be positive integer multiples of _INCHES_PER_CELL.
    w_cells = w / _INCHES_PER_CELL
    h_cells = h / _INCHES_PER_CELL
    assert w_cells == int(w_cells) and int(w_cells) >= 1, (
        f"Figure width {w:.1f} in is not a multiple of {_INCHES_PER_CELL} inches. "
        "Figure size is locked at 10 inches per subplot column "
        "(methodology Appendix D). "
        "Use create_figure() or create_ratio_figure() to construct figures."
    )
    assert h_cells == int(h_cells) and int(h_cells) >= 1, (
        f"Figure height {h:.1f} in is not a multiple of {_INCHES_PER_CELL} inches. "
        "Figure size is locked at 10 inches per subplot row "
        "(methodology Appendix D). "
        "Use create_figure() or create_ratio_figure() to construct figures."
    )
