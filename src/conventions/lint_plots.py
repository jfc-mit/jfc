#!/usr/bin/env python3
"""Plot linter for slopspec analyses.

Scans all plotting scripts (*/src/*.py) for mechanical violations of
appendix-plotting.md. Returns exit code 1 if any violations are found.

Usage:
    python lint_plots.py              # scan from analysis root
    python lint_plots.py path/to/dir  # scan specific directory

Each violation is printed as:
    VIOLATION: <file>:<line> — <rule description>

This script is the mechanical counterpart to the visual plot validator
agent. It catches code-level issues; the agent catches rendered-output
issues (overlap, readability, layout).
"""

import re
import sys
from pathlib import Path


def find_plotting_scripts(root: Path) -> list[Path]:
    """Find all Python files under */src/ directories."""
    scripts = []
    for p in sorted(root.rglob("*/src/*.py")):
        if ".pixi" in str(p) or "__pycache__" in str(p):
            continue
        scripts.append(p)
    return scripts


def lint_file(path: Path) -> list[str]:
    """Return list of violation strings for a single file."""
    violations = []
    text = path.read_text(errors="replace")
    lines = text.splitlines()

    def v(lineno: int, msg: str) -> None:
        violations.append(f"VIOLATION: {path}:{lineno} — {msg}")

    # --- Banned patterns (Category A) ---
    banned = [
        (r"ax\.set_title\(", "No ax.set_title() — captions go in AN"),
        (r"fontsize\s*=\s*\d", "No absolute fontsize=N — use stylesheet or 'x-small'"),
        (r"plt\.colorbar\(", "No plt.colorbar() — use make_square_add_cbar or cbarextend=True"),
        (r"fig\.colorbar\([^)]*\bax\s*=", "No fig.colorbar(ax=) — use fig.colorbar(cax=cax)"),
        (r"ax\.step\(", "No ax.step() for histograms — use mh.histplot()"),
        (r"ax\.bar\(", "No ax.bar() for histograms — use mh.histplot()"),
        (r"ax\.text\(", "No ax.text() — use mh.label.add_text()"),
        (r"ax\.annotate\(", "No ax.annotate() — use mh.label.add_text()"),
        (r"tight_layout\(\)", "No tight_layout() — use bbox_inches='tight' in savefig"),
    ]

    for i, line in enumerate(lines, 1):
        # Skip comments
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        for pattern, msg in banned:
            if re.search(pattern, line):
                v(i, msg)

    # --- Derived-quantity error bar trap ---
    # Look for .view()[:] = or .view()[:] += (signals non-count histogram)
    has_view_assign = False
    view_lines = []
    for i, line in enumerate(lines, 1):
        if re.search(r"\.view\(\)\s*\[.*\]\s*[+]?=", line):
            has_view_assign = True
            view_lines.append(i)

    if has_view_assign:
        # Check if histtype="errorbar" is used WITHOUT yerr=
        for i, line in enumerate(lines, 1):
            if 'histtype="errorbar"' in line or "histtype='errorbar'" in line:
                # Search nearby lines (within 5) for yerr=
                context = "\n".join(lines[max(0, i - 6) : i + 4])
                if "yerr=" not in context:
                    v(
                        i,
                        'histtype="errorbar" on derived quantity without yerr= '
                        f"(view assignment at line(s) {view_lines}). "
                        "mplhep will apply sqrt(N) — pass yerr= explicitly",
                    )

    # --- data=False stacking trap ---
    for i, line in enumerate(lines, 1):
        if "data=False" in line and "llabel" in line:
            v(i, 'data=False with llabel= stacks "Simulation" text — use data=True')
        # Also check for data=False on its own line near llabel
        if "data=False" in line:
            context = "\n".join(lines[max(0, i - 3) : i + 3])
            if "llabel" in context and "data=True" not in context:
                v(i, 'data=False near llabel= stacks "Simulation" text — use data=True')

    # --- Missing hspace=0 when sharex=True ---
    has_sharex = any("sharex=True" in line for line in lines)
    has_hspace = any("hspace=0" in line or "hspace = 0" in line for line in lines)
    if has_sharex and not has_hspace:
        v(0, "sharex=True without hspace=0 — ratio panel will have a gap")

    # --- Figure size check ---
    for i, line in enumerate(lines, 1):
        if "figsize=" in line or "figsize =" in line:
            # Extract figsize value
            m = re.search(r"figsize\s*=\s*\((\d+),\s*(\d+)\)", line)
            if m:
                w, h = int(m.group(1)), int(m.group(2))
                # Single panel must be (10, 10). Multi-panel scales proportionally.
                if w == h and w != 10:
                    v(i, f"figsize=({w}, {h}) — single-panel must be (10, 10)")

    # --- Missing save format checks ---
    saves_pdf = any(".pdf" in line and "savefig" in line for line in lines)
    saves_png = any(".png" in line and "savefig" in line for line in lines)
    has_savefig = any("savefig" in line for line in lines)
    if has_savefig:
        if not saves_pdf:
            v(0, "Missing PDF save — must save both PDF and PNG")
        if not saves_png:
            v(0, "Missing PNG save — must save both PDF and PNG")

    # --- Missing bbox_inches, dpi, transparent ---
    for i, line in enumerate(lines, 1):
        if "savefig(" in line:
            if "bbox_inches" not in line:
                # Check next line for continuation
                next_line = lines[i] if i < len(lines) else ""
                if "bbox_inches" not in next_line:
                    v(i, 'savefig without bbox_inches="tight"')
            if "dpi=" not in line:
                next_line = lines[i] if i < len(lines) else ""
                if "dpi=" not in next_line:
                    v(i, "savefig without dpi=200")

    # --- exp_label on ratio panels ---
    # Count exp_label calls and subplots — heuristic check
    exp_label_count = sum(1 for line in lines if "exp_label(" in line)
    subplot_calls = sum(1 for line in lines if "subplots(" in line)
    if exp_label_count > 1 and has_sharex:
        # Multiple exp_label calls on a sharex figure = likely ratio panel label
        v(
            0,
            f"Multiple exp_label() calls ({exp_label_count}) on sharex figure — "
            "label main panel only, not ratio panel",
        )

    # --- Bare underscores in labels ---
    for i, line in enumerate(lines, 1):
        # Check set_xlabel, set_ylabel, label= for bare underscores
        for fn in ("set_xlabel", "set_ylabel", "label="):
            if fn in line:
                # Extract the string argument
                m = re.search(r'["\']([^"\']+)["\']', line[line.index(fn) :])
                if m:
                    label_text = m.group(1)
                    # Check for underscores outside $...$ math
                    outside_math = re.sub(r"\$[^$]+\$", "", label_text)
                    if "_" in outside_math and "\\_" not in outside_math:
                        v(i, f"Bare underscore in label '{label_text}' — use LaTeX math or escape")

    return violations


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    scripts = find_plotting_scripts(root)

    if not scripts:
        print("No plotting scripts found in */src/*.py")
        return 0

    all_violations: list[str] = []
    for script in scripts:
        all_violations.extend(lint_file(script))

    if all_violations:
        for v in all_violations:
            print(v)
        print(f"\n{len(all_violations)} violation(s) found in {len(scripts)} file(s).")
        return 1
    else:
        print(f"No plotting violations found in {len(scripts)} file(s).")
        return 0


if __name__ == "__main__":
    sys.exit(main())
