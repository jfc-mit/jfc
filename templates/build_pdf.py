#!/usr/bin/env python
"""Build the analysis note PDF from markdown source.

Usage (from the analysis root):
    pixi run py phase5_documentation/exec/build_pdf.py

What this does:
1. Collects all figures from phase*/figures/ into a flat symlink tree under
   phase5_documentation/exec/figures/, so that ![](figures/name.pdf) references
   in the markdown resolve relative to the exec/ directory.
2. Converts any raw path references (bare filenames in backtick blocks) to
   proper markdown image syntax if needed.
3. Runs pandoc with:
   --filter pandoc-crossref   (enables {#fig:label} / @fig:label numbering)
   --number-sections          (1.1, 1.2, etc.)
   --toc                      (table of contents)
   --pdf-engine=xelatex       (Unicode support)
   Figure width: 0.5\\textwidth by default (overridable per figure)

Output: phase5_documentation/exec/ANALYSIS_NOTE.pdf

Requirements: pandoc >= 3.0, pandoc-crossref >= 0.3, xelatex (texlive-xetex)
All available via the analysis pixi environment.
"""

import logging
import os
import subprocess
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration — edit if your layout differs
# ---------------------------------------------------------------------------

# Root of the analysis (where pixi.toml lives). Assumes this script is run
# from the analysis root or that the analysis root is the parent of this file.
ANALYSIS_ROOT = Path(__file__).resolve().parents[2]

# Source markdown for the analysis note
SOURCE_MD = Path(__file__).resolve().parent / "ANALYSIS_NOTE.md"

# Output PDF
OUTPUT_PDF = Path(__file__).resolve().parent / "ANALYSIS_NOTE.pdf"

# Where to collect figure symlinks
FIGURES_DIR = Path(__file__).resolve().parent / "figures"

# Phase figure directories to collect from (in order)
PHASE_FIGURE_DIRS = [
    ANALYSIS_ROOT / "phase2_exploration" / "figures",
    ANALYSIS_ROOT / "phase3_selection" / "figures",
    ANALYSIS_ROOT / "phase4_inference" / "figures",
]

# Default figure width for pandoc LaTeX output
FIGURE_WIDTH = r"0.5\textwidth"

# Pandoc metadata defaults — override in ANALYSIS_NOTE.md YAML front matter
PANDOC_DEFAULTS = {
    "fig-width": FIGURE_WIDTH,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def collect_figures() -> None:
    """Symlink all figures from phase figure dirs into FIGURES_DIR."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    collected = 0
    for phase_dir in PHASE_FIGURE_DIRS:
        if not phase_dir.is_dir():
            log.debug("Phase figure dir not found, skipping: %s", phase_dir)
            continue
        for fig in sorted(phase_dir.iterdir()):
            if fig.suffix.lower() in {".pdf", ".png", ".svg"}:
                link = FIGURES_DIR / fig.name
                if link.exists() or link.is_symlink():
                    link.unlink()
                link.symlink_to(fig.resolve())
                collected += 1
                log.debug("  linked %s -> %s", link.name, fig)
    log.info("Collected %d figures into %s", collected, FIGURES_DIR)


def build_pdf() -> None:
    """Run pandoc to produce the analysis note PDF."""
    if not SOURCE_MD.exists():
        log.error("Source markdown not found: %s", SOURCE_MD)
        sys.exit(1)

    cmd = [
        "pandoc",
        str(SOURCE_MD),
        "--output", str(OUTPUT_PDF),
        "--filter", "pandoc-crossref",
        "--number-sections",
        "--toc",
        "--pdf-engine=xelatex",
        f"--variable=graphics:true",
        f"--variable=figureTitle:Figure",
        # Default figure width applied via a LaTeX header include
        "--variable=geometry:margin=1in",
    ]

    # Inject default figure width via a raw LaTeX header snippet
    # pandoc-crossref respects \setkeys{Gin}{width=...} as a default
    latex_header = (
        r"\usepackage{graphicx}"
        r"\setkeys{Gin}{width=" + FIGURE_WIDTH + r",keepaspectratio}"
    )
    cmd += ["--include-in-header", "/dev/stdin"]

    log.info("Running pandoc...")
    log.debug("Command: %s", " ".join(cmd))

    result = subprocess.run(
        cmd,
        input=latex_header,
        text=True,
        capture_output=True,
        cwd=str(Path(__file__).resolve().parent),
    )

    if result.returncode != 0:
        log.error("pandoc failed (exit %d):\n%s", result.returncode, result.stderr)
        sys.exit(result.returncode)

    if result.stderr:
        log.warning("pandoc warnings:\n%s", result.stderr)

    log.info("Output: %s", OUTPUT_PDF)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    log.info("Collecting figures...")
    collect_figures()

    log.info("Building PDF...")
    build_pdf()

    log.info("Done. PDF written to %s", OUTPUT_PDF.relative_to(ANALYSIS_ROOT))


if __name__ == "__main__":
    main()
