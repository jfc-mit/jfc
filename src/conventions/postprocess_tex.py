#!/usr/bin/env python3
"""Post-process pandoc-generated .tex files for publication-quality output.

Applies deterministic structural fixes that pandoc cannot produce natively.
Runs in-place on a .tex file. Stdlib only — no pip dependencies.

Usage:
    python postprocess_tex.py ANALYSIS_NOTE_4a_v1.tex
"""

import re
import sys
from pathlib import Path


def fix_margins(lines):
    """Ensure margin=0.75in geometry. Insert if absent."""
    target = '\\usepackage[margin=0.75in]{geometry}\n'
    for i, line in enumerate(lines):
        if re.search(r'\\usepackage\[.*\]\{geometry\}', line) or \
           re.search(r'\\usepackage\{geometry\}', line):
            if line == target:
                return None  # already correct
            lines[i] = target
            return 'margins'
    # Insert after \documentclass
    for i, line in enumerate(lines):
        if line.strip().startswith('\\documentclass'):
            lines.insert(i + 1, target)
            return 'margins'
    return None


def fix_abstract(lines):
    """Convert \\section{Abstract} to \\begin{abstract}...\\end{abstract},
    move before \\tableofcontents."""
    # Find the abstract section (may have hypertarget wrapper)
    abstract_start = None
    abstract_content_start = None
    abstract_end = None

    for i, line in enumerate(lines):
        # Match \section{Abstract} or hypertarget variant
        if re.search(r'\\section\{Abstract\}', line) or \
           re.search(r'\\section\[Abstract\]', line):
            abstract_start = i
            # Check if previous line is a hypertarget
            if abstract_start > 0 and '\\hypertarget{abstract}' in lines[abstract_start - 1]:
                abstract_start = abstract_start - 1
            abstract_content_start = i + 1
            break

    if abstract_start is None:
        return None

    # Find the next \section (end of abstract content)
    for i in range(abstract_content_start, len(lines)):
        if re.search(r'\\(section|chapter)\b', lines[i]) and i > abstract_content_start:
            abstract_end = i
            break

    if abstract_end is None:
        return None

    # Extract abstract content (strip blank lines at edges)
    content_lines = lines[abstract_content_start:abstract_end]
    while content_lines and content_lines[0].strip() == '':
        content_lines.pop(0)
    while content_lines and content_lines[-1].strip() == '':
        content_lines.pop()

    if not content_lines:
        return None

    # Build abstract block
    abstract_block = ['\\begin{abstract}\n'] + content_lines + ['\\end{abstract}\n', '\n']

    # Remove original abstract section
    del lines[abstract_start:abstract_end]

    # Find \tableofcontents or \maketitle to insert before
    insert_pos = None
    for i, line in enumerate(lines):
        if '\\tableofcontents' in line:
            insert_pos = i
            break
    if insert_pos is None:
        for i, line in enumerate(lines):
            if '\\maketitle' in line:
                insert_pos = i + 1  # after \maketitle
                break

    if insert_pos is not None:
        for j, aline in enumerate(abstract_block):
            lines.insert(insert_pos + j, aline)
    else:
        # Fallback: insert after \begin{document}
        for i, line in enumerate(lines):
            if '\\begin{document}' in line:
                for j, aline in enumerate(abstract_block):
                    lines.insert(i + 1 + j, aline)
                break

    return 'abstract'


def fix_references(lines):
    """Convert \\section{References} to unnumbered with TOC entry."""
    for i, line in enumerate(lines):
        if re.search(r'\\section\{References\}', line):
            lines[i] = '\\section*{References}\\addcontentsline{toc}{section}{References}\n'
            return 'references'
    return None


def fix_table_spacing(lines):
    """Insert \\vspace{1em} before \\begin{longtable}."""
    count = 0
    offset = 0
    indices = [i for i, line in enumerate(lines) if '\\begin{longtable}' in line]
    for idx in indices:
        pos = idx + offset
        # Don't insert if already preceded by \vspace
        if pos > 0 and '\\vspace' in lines[pos - 1]:
            continue
        lines.insert(pos, '\\vspace{1em}\n')
        offset += 1
        count += 1
    return f'{count} table-spacings' if count else None


def fix_float_barriers(lines):
    """Insert \\FloatBarrier before each \\section{ (not \\section*)."""
    count = 0
    offset = 0
    indices = []
    for i, line in enumerate(lines):
        # Match \section{ but not \section*{
        if re.search(r'\\section\{', line) and not re.search(r'\\section\*\{', line):
            indices.append(i)
    for idx in indices:
        pos = idx + offset
        # Don't insert if already preceded by \FloatBarrier
        if pos > 0 and '\\FloatBarrier' in lines[pos - 1]:
            continue
        # Don't insert if preceded by \needspace (we'll insert before that)
        if pos > 0 and '\\needspace' in lines[pos - 1]:
            # Insert before the \needspace line
            lines.insert(pos - 1, '\\FloatBarrier\n')
        else:
            lines.insert(pos, '\\FloatBarrier\n')
        offset += 1
        count += 1
    return f'{count} FloatBarriers' if count else None


def fix_needspace(lines):
    """Insert \\needspace{4\\baselineskip} before \\section and \\subsection."""
    count = 0
    offset = 0
    indices = []
    for i, line in enumerate(lines):
        if re.search(r'\\(sub)?section[\{*]', line):
            indices.append(i)
    for idx in indices:
        pos = idx + offset
        # Don't insert if already preceded by \needspace
        if pos > 0 and '\\needspace' in lines[pos - 1]:
            continue
        # Check if preceded by \FloatBarrier — insert before it
        if pos > 0 and '\\FloatBarrier' in lines[pos - 1]:
            if pos > 1 and '\\needspace' in lines[pos - 2]:
                continue
            lines.insert(pos - 1, '\\needspace{4\\baselineskip}\n')
        else:
            lines.insert(pos, '\\needspace{4\\baselineskip}\n')
        offset += 1
        count += 1
    return f'{count} needspace' if count else None


def fix_duplicate_headers(lines):
    """Remove duplicate table header blocks (two \\toprule within 5 lines)."""
    count = 0
    i = 0
    while i < len(lines):
        if '\\toprule' in lines[i]:
            # Look for another \toprule within the next 5 lines
            for j in range(i + 1, min(i + 6, len(lines))):
                if '\\toprule' in lines[j]:
                    # Found duplicate. Remove from second \toprule through
                    # the next \midrule (inclusive) — that's the duplicate
                    # header block.
                    end = j + 1
                    while end < len(lines):
                        if '\\midrule' in lines[end] or '\\endhead' in lines[end]:
                            end += 1
                            break
                        end += 1
                    del lines[j:end]
                    count += 1
                    break
        i += 1
    return f'{count} dup-headers' if count else None


def fix_duplicate_labels(lines):
    """Remove consecutive duplicate \\label{...}\\label{...}."""
    count = 0
    text = ''.join(lines)
    pattern = r'(\\label\{([^}]+)\})(\s*\\label\{\2\})+'
    text_new, n = re.subn(pattern, r'\1', text)
    if n > 0:
        count = n
        lines.clear()
        lines.extend(text_new.splitlines(keepends=True))
    return f'{count} dup-labels' if count else None


def fix_appendix(lines):
    """Insert \\appendix before appendix marker comments."""
    for i, line in enumerate(lines):
        if re.search(r'%%\s*Appendices', line) or \
           re.search(r'<!--\s*Appendices\s*-->', line):
            # Insert \appendix after the comment line
            if i + 1 < len(lines) and '\\appendix' in lines[i + 1]:
                return None  # already present
            lines.insert(i + 1, '\\appendix\n')
            return 'appendix'
    return None


def fix_clearpage(lines):
    """Insert \\clearpage before \\appendix and \\section*{References}."""
    count = 0
    offset = 0
    indices = []
    for i, line in enumerate(lines):
        if '\\appendix' in line and line.strip() == '\\appendix':
            indices.append(('appendix', i))
        elif re.search(r'\\section\*\{References\}', line):
            indices.append(('references', i))

    for label, idx in indices:
        pos = idx + offset
        if pos > 0 and '\\clearpage' in lines[pos - 1]:
            continue
        # Find the right insertion point — before any \needspace or
        # \FloatBarrier that precede this line
        insert_at = pos
        while insert_at > 0 and lines[insert_at - 1].strip() in (
            '\\FloatBarrier', '') or (
                insert_at > 0 and '\\needspace' in lines[insert_at - 1]):
            if lines[insert_at - 1].strip() == '':
                insert_at -= 1
                continue
            if '\\FloatBarrier' in lines[insert_at - 1] or \
               '\\needspace' in lines[insert_at - 1]:
                insert_at -= 1
                continue
            break
        if insert_at > 0 and '\\clearpage' in lines[insert_at - 1]:
            continue
        lines.insert(insert_at, '\\clearpage\n')
        offset += 1
        count += 1
    return 'clearpage' if count else None


def postprocess(path):
    """Apply all fixes to the .tex file at path. Returns summary string."""
    text = Path(path).read_text()
    lines = text.splitlines(keepends=True)

    # Ensure file ends with newline
    if lines and not lines[-1].endswith('\n'):
        lines[-1] += '\n'

    fixes = []

    # Order matters: abstract before clearpage (abstract removal shifts lines),
    # needspace before float barriers (needspace goes before FloatBarrier),
    # duplicate fixes before structural changes.
    for fix_fn in [
        fix_margins,
        fix_abstract,
        fix_references,
        fix_table_spacing,
        fix_float_barriers,
        fix_needspace,
        fix_duplicate_headers,
        fix_duplicate_labels,
        fix_appendix,
        fix_clearpage,
    ]:
        result = fix_fn(lines)
        if result:
            fixes.append(result)

    Path(path).write_text(''.join(lines))

    if fixes:
        summary = f"postprocess_tex: {len(fixes)} fixes applied ({', '.join(fixes)})"
    else:
        summary = "postprocess_tex: no fixes needed"
    return summary


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <file.tex>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"Error: {path} not found", file=sys.stderr)
        sys.exit(1)

    summary = postprocess(path)
    print(summary)


if __name__ == '__main__':
    main()
