#!/usr/bin/env python3
"""Convert ANALYSIS_NOTE.md to PDF via pandoc 3.x + pdflatex.

Collects all referenced figures into a local figures/ directory (symlinks),
converts inline figure references to markdown image syntax, then runs
pandoc -> tex -> pdf.

Usage: pixi run build-pdf
"""
import re
import subprocess
import logging
from pathlib import Path
from rich.logging import RichHandler

logging.basicConfig(level=logging.INFO, format="%(message)s",
                    handlers=[RichHandler(rich_tracebacks=True)])
log = logging.getLogger(__name__)

EXEC_DIR = Path(__file__).parent
AN_MD = EXEC_DIR / "ANALYSIS_NOTE.md"
FIG_DIR = EXEC_DIR / "figures"


def collect_and_link_figures(md_text: str) -> dict[str, Path]:
    """Find all figure paths in backticks, symlink into figures/."""
    paths = re.findall(r'`(\.\./\.\./[^`]+\.pdf)`', md_text)
    FIG_DIR.mkdir(exist_ok=True)
    for f in FIG_DIR.iterdir():
        if f.is_symlink():
            f.unlink()

    mapping = {}
    for rel_path in paths:
        src = (EXEC_DIR / rel_path).resolve()
        name = src.name
        if name in mapping and mapping[name] != src:
            phase = rel_path.split('/')[2]
            name = f"{phase}_{name}"
        if src.exists():
            dst = FIG_DIR / name
            if not dst.exists():
                dst.symlink_to(src)
            mapping[rel_path] = f"figures/{name}"
        else:
            log.warning("MISSING: %s", src)
            mapping[rel_path] = rel_path
    return mapping


def convert_to_images(md_text: str, mapping: dict[str, str]) -> str:
    """Convert **Figure:** `path` — caption to ![caption](local_path)."""

    def replace_fig_block(m):
        block = m.group(0)
        paths = re.findall(r'`(\.\./\.\./[^`]+\.pdf)`', block)
        if not paths:
            return block

        # Extract caption: text after the last path reference
        caption = ""
        last_path_end = block.rfind('.pdf`')
        if last_path_end != -1:
            rest = block[last_path_end + 5:].strip()
            rest = re.sub(r'^[.,;]?\s*', '', rest)
            rest = re.sub(r'^[—–-]\s*', '', rest)
            caption = rest.strip().rstrip('.')

        parts = []
        for p in paths:
            local = mapping.get(p, p)
            parts.append(f"\n![{caption}]({local})\n")
        return "\n".join(parts)

    md_text = re.sub(
        r'\*\*Figures?:\*\*.*?(?:\n(?![\n#*\-|1-9]).*)*',
        replace_fig_block,
        md_text
    )

    # Catch any remaining standalone backtick figure references
    for orig, local in mapping.items():
        md_text = md_text.replace(f'`{orig}`', f'\n![](  {local})\n')

    return md_text


def main():
    log.info("Reading %s", AN_MD)
    md_text = AN_MD.read_text()

    mapping = collect_and_link_figures(md_text)
    log.info("Linked %d figures", len(mapping))

    md_converted = convert_to_images(md_text, mapping)
    n_imgs = len(re.findall(r'!\[', md_converted))
    log.info("Converted %d image references", n_imgs)

    converted_md = EXEC_DIR / "ANALYSIS_NOTE_for_pdf.md"
    converted_md.write_text(md_converted)

    # Run pandoc 3.x
    tex_file = EXEC_DIR / "ANALYSIS_NOTE.tex"
    pdf_file = EXEC_DIR / "ANALYSIS_NOTE.pdf"

    log.info("Running pandoc 3.x -> PDF...")
    cmd = [
        "pandoc", str(converted_md),
        "-o", str(pdf_file),
        "--pdf-engine=pdflatex",
        "-V", "geometry:margin=1in",
        "-V", "documentclass:article",
        "-V", "fontsize:11pt",
        "-V", r"header-includes:\usepackage{graphicx}\setkeys{Gin}{width=0.5\textwidth,keepaspectratio}",
        "--number-sections",
        "--toc",
        "--toc-depth=3",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(EXEC_DIR), timeout=120)

    if r.returncode != 0:
        log.error("pandoc failed:\n%s", r.stderr[-2000:] if len(r.stderr) > 2000 else r.stderr)
        # Try without --toc in case that's the issue
        cmd_notoc = [c for c in cmd if c != "--toc" and c != "--toc-depth=3"]
        log.info("Retrying without TOC...")
        r = subprocess.run(cmd_notoc, capture_output=True, text=True, cwd=str(EXEC_DIR), timeout=120)
        if r.returncode != 0:
            log.error("pandoc failed again:\n%s", r.stderr[-2000:])
            return

    if pdf_file.exists():
        size_kb = pdf_file.stat().st_size / 1024
        log.info("SUCCESS: %s (%.0f KB)", pdf_file, size_kb)
    else:
        log.error("PDF not produced")


if __name__ == "__main__":
    main()
