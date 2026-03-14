#!/usr/bin/env python
"""Concatenate split spec files into single files for agent consumption.

Usage:
    python build_spec.py
    pixi run build
"""

from pathlib import Path

HERE = Path(__file__).parent


def concat_dir(src_dir: Path, output: Path):
    """Concatenate all .md files in src_dir (sorted by name) into output."""
    parts = sorted(src_dir.glob("*.md"))
    if not parts:
        print(f"  WARNING: no .md files in {src_dir}")
        return

    with open(output, "w") as f:
        for i, part in enumerate(parts):
            text = part.read_text().rstrip()
            # Strip trailing --- separators (the build script adds its own)
            while text.endswith("\n---") or text.endswith("---"):
                text = text.rsplit("---", 1)[0].rstrip()
            if i > 0:
                f.write("\n\n---\n\n")
            f.write(text)
        f.write("\n")

    total = sum(1 for _ in output.open())
    print(f"  {output.name}: {len(parts)} files -> {total} lines")


def main():
    print("Building spec files...")
    concat_dir(HERE / "methodology", HERE / "methodology.md")
    concat_dir(HERE / "orchestration", HERE / "orchestration.md")
    conventions_dir = HERE / "conventions"
    if conventions_dir.is_dir() and list(conventions_dir.glob("*.md")):
        concat_dir(conventions_dir, HERE / "conventions.md")
    print("Done.")


if __name__ == "__main__":
    main()
