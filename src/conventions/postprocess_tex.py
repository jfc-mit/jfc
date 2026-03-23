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


def fix_title_math(lines):
    r"""Replace literal sqrt(s) with $\sqrt{s}$ in \title{...}.

    Pandoc's YAML title: field is plain text, so $\sqrt{s}$ renders
    literally.  This fix catches the common sqrt(s) pattern in titles
    and converts it to proper LaTeX math.
    """
    count = 0
    for i, line in enumerate(lines):
        if '\\title{' in line:
            # Replace literal sqrt(s) with $\sqrt{s}$
            new_line = re.sub(r'sqrt\(s\)', r'$\\sqrt{s}$', line)
            # Also catch $\sqrt{s}$ that pandoc escaped to \$\\sqrt\{s\}\$
            new_line = re.sub(r'\\\$\\sqrt\{s\}\\\$', r'$\\sqrt{s}$', new_line)
            # Also catch literal $\sqrt{s}$ (dollar signs as text)
            new_line = re.sub(r'\$\\sqrt\{s\}\$', r'$\\sqrt{s}$', new_line)
            if new_line != line:
                lines[i] = new_line
                count += 1
    return f'{count} title-math' if count else None


def fix_escaped_pm(lines):
    r"""Fix pandoc-escaped $\pm$ that renders with visible dollar signs.

    When markdown contains $\pm$ as standalone math, pandoc sometimes
    produces \$\\pm\$ in the .tex output, rendering with visible $
    characters.  Replace with proper $\pm$.  Also fix escaped < > ~.
    """
    count = 0
    for i, line in enumerate(lines):
        new_line = line
        # \$\pm\$ or \$±\$ -> $\pm$
        new_line = re.sub(r'\\\$\\pm\\\$', r'$\\pm$', new_line)
        new_line = re.sub(r'\\\$±\\\$', r'$\\pm$', new_line)
        # \$<\$ -> $<$  and \$>\$ -> $>$
        new_line = re.sub(r'\\\$<\\\$', r'$<$', new_line)
        new_line = re.sub(r'\\\$>\\\$', r'$>$', new_line)
        # \$\sim\$ -> $\sim$
        new_line = re.sub(r'\\\$\\sim\\\$', r'$\\sim$', new_line)
        if new_line != line:
            lines[i] = new_line
            count += 1
    return f'{count} escaped-math' if count else None


def fix_longtable_short(lines):
    r"""Convert short longtables (< 15 rows) to table+tabular floats.

    Pandoc generates \begin{longtable} for all tables, but short tables
    should not split across pages.  This converts longtables with fewer
    than 15 data rows to regular table floats.
    """
    count = 0
    text = ''.join(lines)

    # Find each longtable block
    pattern = re.compile(
        r'(\\begin\{longtable\}(?:\[[^\]]*\])?)(\{[^}]*\})(.*?)(\\end\{longtable\})',
        re.DOTALL)

    def convert_if_short(match):
        nonlocal count
        header = match.group(1)
        col_spec = match.group(2)
        body = match.group(3)
        # Count data rows (lines with \\ that aren't header/rule lines)
        data_lines = [
            l for l in body.split('\n')
            if '\\\\' in l
            and '\\toprule' not in l
            and '\\midrule' not in l
            and '\\bottomrule' not in l
            and '\\endhead' not in l
            and '\\endfoot' not in l
            and '\\endlastfoot' not in l
        ]
        if len(data_lines) >= 15:
            return match.group(0)  # keep as longtable

        # Remove longtable-specific commands
        new_body = body
        new_body = re.sub(r'\\endhead\s*\n?', '', new_body)
        new_body = re.sub(r'\\endfoot\s*\n?', '', new_body)
        new_body = re.sub(r'\\endlastfoot\s*\n?', '', new_body)

        # Extract caption if present
        caption_match = re.search(
            r'\\caption\{.*?\}(?:\\label\{[^}]*\})?\\\\',
            new_body, re.DOTALL)
        caption = ''
        if caption_match:
            # Remove trailing \\ from caption line
            caption = caption_match.group(0).rstrip('\\').rstrip() + '\n'
            new_body = new_body.replace(caption_match.group(0), '')

        # Build table float
        result = '\\begin{table}[htbp]\n\\centering\n\\small\n'
        if caption:
            result += caption
        result += f'\\begin{{tabular}}{col_spec}\n'
        result += new_body.strip() + '\n'
        result += '\\end{tabular}\n\\end{table}'
        count += 1
        return result

    new_text = pattern.sub(convert_if_short, text)
    if count:
        lines.clear()
        lines.extend(new_text.splitlines(keepends=True))
        # Ensure last line has newline
        if lines and not lines[-1].endswith('\n'):
            lines[-1] += '\n'
    return f'{count} longtable-conversions' if count else None


def fix_stale_phase_labels(lines):
    r"""Warn about internal phase labels in table headers and captions.

    Prints warnings to stderr for patterns like "(4a)", "Phase 4b",
    "Expected (4a)" in captions and table headers.  Does not modify
    the file — this is a diagnostic.
    """
    warnings = []
    past_changelog = False
    for i, line in enumerate(lines):
        if '\\section' in line and 'Introduction' in line:
            past_changelog = True
        if not past_changelog:
            continue
        # Check captions and table content for phase labels
        if re.search(r'\\caption\{', line) or re.search(r'\\toprule|\\midrule', line):
            if re.search(r'\(4[abc]\)|Phase\s+[1-5]\b', line):
                warnings.append(
                    f"  line {i+1}: internal phase label in: "
                    f"{line.strip()[:80]}")
    if warnings:
        sys.stderr.write(
            f"WARNING: {len(warnings)} internal phase label(s) found "
            f"in captions/headers:\n")
        for w in warnings:
            sys.stderr.write(w + '\n')
        return f'{len(warnings)} phase-label-warnings'
    return None


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
    # Insert after \documentclass (handle multiline \documentclass[...]{...})
    for i, line in enumerate(lines):
        if line.strip().startswith('\\documentclass'):
            # Find the closing brace of \documentclass{...}
            insert_pos = i + 1
            for j in range(i, min(i + 5, len(lines))):
                if '{article}' in lines[j] or '{report}' in lines[j] or '{book}' in lines[j]:
                    insert_pos = j + 1
                    break
            lines.insert(insert_pos, target)
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


def fix_figure_placement(lines):
    r"""Add [!htbp] to bare \begin{figure} and strip \pandocbounded wrapper.

    Pandoc >=3.8 wraps every includegraphics in \pandocbounded{...} which
    scales images to fill \textheight — leaving no room for captions and
    defeating LaTeX's float placement.  We strip the wrapper and let the
    preamble's default figure height (0.45\linewidth) handle sizing.

    Also adds [!htbp] placement so LaTeX can use float pages when a
    figure doesn't fit on the current page.
    """
    count = 0
    for i, line in enumerate(lines):
        stripped = line.rstrip('\n')
        if stripped == '\\begin{figure}':
            lines[i] = '\\begin{figure}[htbp]\n'
            # Insert \needspace before the figure to prevent starting a
            # figure that won't fit.  0.4\textheight matches our height cap.
            lines.insert(i, '\\needspace{0.4\\textheight}\n')
            count += 1
    # Add height= to pandocbounded includegraphics calls so LaTeX knows
    # the size before float placement.  Also neuter pandocbounded to no-op.
    for i, line in enumerate(lines):
        # Add height constraint to pandocbounded figures
        if '\\pandocbounded{\\includegraphics[keepaspectratio' in line and \
           'height=' not in line:
            lines[i] = line.replace(
                '\\includegraphics[keepaspectratio',
                '\\includegraphics[height=0.35\\textheight,width=\\linewidth,keepaspectratio')
            count += 1
    # Redefine pandocbounded as identity (passthrough) — the height=
    # constraint above makes the scaling unnecessary.
    for i, line in enumerate(lines):
        if '\\newcommand*\\pandocbounded[1]{% scales' in line:
            for j in range(i, min(i + 12, len(lines))):
                if lines[j].strip() == '}' and j > i:
                    lines[i:j+1] = ['\\newcommand*\\pandocbounded[1]{#1}%\n']
                    count += 1
                    break
            break
    return f'{count} figure-placements' if count else None


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


def fix_references_placement(lines):
    """Move CSLReferences block to immediately after the References heading.

    pandoc-citeproc places the bibliography at the end of the document,
    after appendix content.  This function moves the CSLReferences block
    to appear right after the \\section*{References} heading, before
    \\appendix.
    """
    # Find the References heading
    ref_heading = None
    for i, line in enumerate(lines):
        if re.search(r'\\section\*\{References\}', line):
            ref_heading = i
            break
    if ref_heading is None:
        return None

    # Find the CSLReferences block
    csl_start = None
    csl_end = None
    for i, line in enumerate(lines):
        if '\\begin{CSLReferences}' in line:
            # Include the \phantomsection\label{refs} line before it
            csl_start = i
            if i > 0 and 'phantomsection' in lines[i - 1]:
                csl_start = i - 1
        if '\\end{CSLReferences}' in line:
            csl_end = i + 1  # inclusive
            break

    if csl_start is None or csl_end is None:
        return None

    # Check if CSLReferences is already right after the References heading
    # (within a few lines)
    if csl_start <= ref_heading + 5:
        return None

    # Extract the CSLReferences block
    csl_block = lines[csl_start:csl_end]

    # Remove the CSLReferences block from its current position
    del lines[csl_start:csl_end]

    # Re-find the References heading (may have shifted)
    ref_heading = None
    for i, line in enumerate(lines):
        if re.search(r'\\section\*\{References\}', line):
            ref_heading = i
            break
    if ref_heading is None:
        return None

    # Find the insertion point: after the References heading line,
    # skip any \clearpage that follows it
    insert_pos = ref_heading + 1
    while insert_pos < len(lines) and lines[insert_pos].strip() in (
            '\\clearpage', ''):
        # Remove \clearpage between References heading and bibliography
        if lines[insert_pos].strip() == '\\clearpage':
            del lines[insert_pos]
        else:
            insert_pos += 1

    # Insert the CSLReferences block
    for j, bline in enumerate(csl_block):
        lines.insert(insert_pos + j, bline)

    # Insert \clearpage and \appendix after the CSLReferences block
    after_csl = insert_pos + len(csl_block)
    # Check if \appendix already follows
    has_appendix = False
    for k in range(after_csl, min(after_csl + 5, len(lines))):
        if '\\appendix' in lines[k]:
            has_appendix = True
            break
    if not has_appendix:
        lines.insert(after_csl, '\\appendix\n')
        lines.insert(after_csl, '\\clearpage\n')

    return 'references-placement'


def fix_crossref_prefixes(lines):
    r"""Strip redundant pandoc-crossref prefixes.

    pandoc-crossref inserts 'fig.~\ref{...}', 'sec.~\ref{...}', etc.
    When the author writes 'Figure @fig:name', pandoc produces
    'Figure fig.~\ref{fig:name}' — strip the redundant lowercase prefix.
    Also handles Table/Section/Equation variants, and bare prefixes at
    line starts or after punctuation.
    """
    count = 0
    # Regex-based approach: match prefix patterns at word boundaries.
    # Each tuple: (regex_pattern, replacement_string)
    patterns = [
        # "Figure fig.~\ref{" or "Figures fig.~\ref{" -> keep word + ~\ref{
        (r'(Figure[s]?)\s+fig\.~\\ref\{', r'\1~\\ref{'),
        (r'(figure[s]?)\s+fig\.~\\ref\{', r'Figure~\\ref{'),
        (r'(Section[s]?)\s+sec\.~\\ref\{', r'\1~\\ref{'),
        (r'(section[s]?)\s+sec\.~\\ref\{', r'Section~\\ref{'),
        (r'(Table[s]?)\s+tbl\.~\\ref\{', r'\1~\\ref{'),
        (r'(table[s]?)\s+tbl\.~\\ref\{', r'Table~\\ref{'),
        (r'(Equation[s]?)\s+eq\.~\\ref\{', r'\1~\\ref{'),
        (r'(equation[s]?)\s+eq\.~\\ref\{', r'Equation~\\ref{'),
        # Same with space instead of tilde before \ref
        (r'(Figure[s]?)\s+fig\.\s*\\ref\{', r'\1~\\ref{'),
        (r'(Section[s]?)\s+sec\.\s*\\ref\{', r'\1~\\ref{'),
        (r'(Table[s]?)\s+tbl\.\s*\\ref\{', r'\1~\\ref{'),
        (r'(Equation[s]?)\s+eq\.\s*\\ref\{', r'\1~\\ref{'),
        # Bare prefixes (at line start, after punctuation, after parentheses)
        # These appear when pandoc-crossref outputs just "fig.~\ref{}" without
        # a preceding word like "Figure"
        (r'(?<![A-Za-z])fig\.~\\ref\{', r'Figure~\\ref{'),
        (r'(?<![A-Za-z])sec\.~\\ref\{', r'Section~\\ref{'),
        (r'(?<![A-Za-z])tbl\.~\\ref\{', r'Table~\\ref{'),
        (r'(?<![A-Za-z])eq\.~\\ref\{', r'Equation~\\ref{'),
        # Same bare prefixes with space instead of tilde
        (r'(?<![A-Za-z])fig\.\s*\\ref\{', r'Figure~\\ref{'),
        (r'(?<![A-Za-z])sec\.\s*\\ref\{', r'Section~\\ref{'),
        (r'(?<![A-Za-z])tbl\.\s*\\ref\{', r'Table~\\ref{'),
        (r'(?<![A-Za-z])eq\.\s*\\ref\{', r'Equation~\\ref{'),
    ]
    # Also fix double-word artifacts like "Figures Figure" from earlier passes
    cleanup = [
        (r'Figures\s+Figure~', r'Figures~'),
        (r'Figure\s+Figure~', r'Figure~'),
        (r'Sections\s+Section~', r'Sections~'),
        (r'Section\s+Section~', r'Section~'),
        (r'Tables\s+Table~', r'Tables~'),
        (r'Table\s+Table~', r'Table~'),
    ]
    for i, line in enumerate(lines):
        new_line = line
        for pat, repl in patterns + cleanup:
            new_line = re.sub(pat, repl, new_line)
        if new_line != line:
            count += 1
            lines[i] = new_line

    # Cross-line pass: pandoc sometimes breaks "Figure\nFigure~\ref{}"
    # across lines.  Join, deduplicate, split back.
    text = ''.join(lines)
    cross_line = [
        (r'(Figure)\s+(Figure~\\ref\{)', r'\2'),
        (r'(Figures)\s+(Figure~\\ref\{)', r'Figures~\\ref{'),
        (r'(Section)\s+(Section~\\ref\{)', r'\2'),
        (r'(Table)\s+(Table~\\ref\{)', r'\2'),
        (r'(Equation)\s+(Equation~\\ref\{)', r'\2'),
    ]
    for pat, repl in cross_line:
        text, n = re.subn(pat, repl, text)
        count += n
    lines.clear()
    lines.extend(text.splitlines(keepends=True))

    return f'{count} crossref-prefixes' if count else None


def fix_subfig_package(lines):
    """Add \\usepackage{subfig} if \\subfloat is used anywhere in the file."""
    text = ''.join(lines)
    if '\\subfloat' not in text:
        return None
    # Check if already present
    for line in lines:
        if re.search(r'\\usepackage.*\{subfig\}', line):
            return None
    # Insert after geometry line
    for i, line in enumerate(lines):
        if '\\usepackage' in line and 'geometry' in line:
            lines.insert(i + 1, '\\usepackage{subfig}\n')
            return 'subfig'
    # Fallback: insert after \documentclass
    for i, line in enumerate(lines):
        if line.strip().startswith('\\documentclass'):
            lines.insert(i + 1, '\\usepackage{subfig}\n')
            return 'subfig'
    return None


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
    # duplicate fixes before structural changes.  Title math and escaped-pm
    # run early (before structural rearrangement).  Longtable conversion runs
    # after table spacing (which targets longtables that survive).  Phase
    # label warnings run last (diagnostic only, no modifications).
    for fix_fn in [
        fix_title_math,
        fix_escaped_pm,
        fix_margins,
        fix_abstract,
        fix_references,
        fix_crossref_prefixes,
        fix_table_spacing,
        fix_longtable_short,
        fix_figure_placement,
        fix_float_barriers,
        fix_needspace,
        fix_duplicate_headers,
        fix_duplicate_labels,
        fix_subfig_package,
        fix_appendix,
        fix_clearpage,
        fix_references_placement,
        fix_stale_phase_labels,
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
