#!/usr/bin/env python
"""Scaffold a new analysis directory with per-phase CLAUDE.md files.

Usage:
    python scaffold_analysis.py analyses/my_analysis --type measurement --technique unfolding
    python scaffold_analysis.py analyses/my_analysis --type search
    pixi run scaffold analyses/my_analysis --type measurement --technique unfolding

The script creates the directory structure and generates CLAUDE.md files
tailored to the analysis type and technique. These are loaded automatically
by Claude Code when an agent works in that directory.
"""

import argparse
from pathlib import Path

HERE = Path(__file__).parent

# ---------------------------------------------------------------------------
# Phase directories and review types
# ---------------------------------------------------------------------------

PHASES = [
    ("phase1_strategy", "3-bot"),
    ("phase2_exploration", "self"),
    ("phase3_selection", "1-bot"),
    ("phase4_inference", "3-bot"),
    ("phase5_documentation", "3-bot"),
]

PHASE_SUBDIRS = ["exec", "scripts", "figures", "review"]

# ---------------------------------------------------------------------------
# Templates — keyed by (phase, analysis_type)
# Technique-specific blocks are injected where applicable.
# ---------------------------------------------------------------------------

# The analysis-root CLAUDE.md
ROOT_TEMPLATE = """\
# Analysis: {name}

Type: {analysis_type}
{technique_line}

## Environment

This analysis has its own pixi environment defined in `pixi.toml`.
All scripts must run through pixi:

```bash
pixi run py path/to/script.py          # run a script
pixi run py -c "import uproot; ..."     # quick check
pixi shell                              # interactive shell with all deps
```

**Never use bare `python`, `pip install`, or `conda`.** If you need a
package, add it to `pixi.toml` under `[pypi-dependencies]` and run
`pixi install`.

## Applicable conventions

{conventions_list}

## Reference analyses

To be filled during Phase 1. The strategy must identify 2-3 published
reference analyses and tabulate their systematic programs. This table is
a binding input to Phase 4 and Phase 5 reviews.

## General rules

See the project-root CLAUDE.md for tool requirements and coding rules.
See `conventions/` for technique-specific guidance.
"""

# Common preamble prepended to every phase CLAUDE.md
PHASE_PREAMBLE = """\
> **End goal.** This analysis produces a publication-quality analysis note
> for journal submission. Every phase contributes to that goal. Work should
> meet the standard of external scrutiny — a journal referee, a collaboration
> review committee, or a competing group doing the same measurement.
"""

# Per-phase CLAUDE.md templates
PHASE_TEMPLATES = {
    "phase1_strategy": """\
# Phase 1: Strategy

{preamble}
You are developing the analysis strategy for a **{analysis_type}** analysis.

## Required deliverables

- Physics motivation and observable definition
- Sample inventory (data + MC)
- Selection approach with justification
- Systematic uncertainty plan
- Literature review from RAG corpus

## Completeness requirements

1. **Reference analyses.** Identify 2-3 published analyses closest in
   technique/observable. Tabulate their systematic programs. This table
   is a binding input to later reviews.

2. **Conventions check.** Read the applicable conventions:
{conventions_block}
   Enumerate every required systematic source listed there. For each one,
   state in the strategy: "Will implement" or "Not applicable because [reason]."
   This enumeration is binding — Phase 4a reviews against it. Silent
   omissions are Category A findings.

## Review

This phase gets 3-bot review. The reviewer will check:
- Is the approach motivated by the literature?
- Does the systematic plan cover standard sources (per conventions)?
- Are reference analyses identified with systematics tabulated?
""",
    "phase2_exploration": """\
# Phase 2: Exploration

{preamble}
You are exploring the data and MC samples.

## Required deliverables

- Sample inventory (files, trees, branches, event counts)
- Data quality assessment
- Key variable distributions with data/MC comparisons
- Variable ranking for discrimination power
- Preselection cutflow

## Output artifact

You MUST produce `exec/EXPLORATION.md` before Phase 3 begins.
This is a hard gate — see methodology Section 3.0.

## Rules

- Prototype on small subsets (~1000 events). Do not process full data to
  "see what's there."
- Append findings to experiment_log.md as you go. An empty experiment log
  at the end of this phase is a process failure.
- Self-review only — no external reviewer. Be thorough.

## Plotting

Import the shared plotting utility for all figures:
```python
from common.plotting import create_figure, create_ratio_figure, save_figure, add_experiment_label
```

Do NOT use raw `plt.subplots()` or custom `figsize`. The utility enforces
the required figure size (10x10), style, and save conventions. Violations
are Category A review findings.

Reference figures in the artifact using markdown image syntax:
```markdown
![Detailed caption describing what is plotted.](figures/filename.pdf)
```
""",
    "phase3_selection": """\
# Phase 3: Selection and Modeling

{preamble}
You are implementing the analysis approach defined in the Phase 1 strategy.
Read the strategy first — it determines what this phase must deliver.

## Required deliverables

- Final object definitions
- Event selection with optimization
- Cutflow table with data and MC yields
- For searches: background estimation, control/validation regions, closure tests
- For measurements: correction chain (response matrix, unfolding, closure tests)

## Output artifact

You MUST produce `exec/SELECTION.md` before Phase 4 begins.
This is a hard gate — see methodology Section 3.0.

{technique_block_phase3}
## Plotting

Import the shared plotting utility for all figures:
```python
from common.plotting import create_figure, create_ratio_figure, save_figure, add_experiment_label
```

Do NOT use raw `plt.subplots()` or custom `figsize`. The utility enforces
the required figure size (10x10), style, and save conventions. Violations
are Category A review findings.

Reference figures in the artifact using markdown image syntax:
```markdown
![Detailed caption describing what is plotted.](figures/filename.pdf)
```

## Review

This phase gets 1-bot review. The reviewer will check:
- Is every cut motivated by a plot?
- Does the background model / correction close?
{review_extras_phase3}
""",
    "phase4_inference": """\
# Phase 4: Inference

{preamble}
You are building the statistical model and computing results.

## Required deliverables

- Statistical model or corrected spectrum with full uncertainties
- Systematic uncertainty evaluation
- Validation diagnostics
- Comparison to reference measurements

## Output artifacts

Phase 4 has sub-phases, each with its own artifact (hard gates):
- 4a: `exec/INFERENCE_EXPECTED.md` — expected results, systematics, validation
- 4b: `exec/INFERENCE_PARTIAL.md` — partial data results + draft AN
- 4c: `exec/INFERENCE_OBSERVED.md` — full observed results

See methodology Section 3.0 for the gate protocol.

## Completeness requirements (critical)

1. **Systematic completeness table.** Compare your implemented sources
   against the reference analyses from Phase 1 and the conventions:
{conventions_block}
   Format:
   ```
   | Source | This analysis | Ref 1 | Ref 2 | Status |
   ```
   Any MISSING source without justification is a blocker.

{technique_block_phase4}
## Plotting

Import the shared plotting utility for all figures:
```python
from common.plotting import create_figure, create_ratio_figure, save_figure, add_experiment_label
```

Do NOT use raw `plt.subplots()` or custom `figsize`. The utility enforces
the required figure size (10x10), style, and save conventions. Violations
are Category A review findings.

Reference figures in the artifact using markdown image syntax:
```markdown
![Detailed caption describing what is plotted.](figures/filename.pdf)
```

## Review

This phase gets 3-bot review. Reviewers will check:
- Are systematics complete relative to conventions AND reference analyses?
- Do all validation checks pass?
- If chi2/ndf vs. a reference measurement exceeds 1.5, has it been investigated?
""",
    "phase5_documentation": """\
# Phase 5: Documentation

{preamble}
You are producing the final analysis note.

## Reviewer framing

The review will evaluate this note **as a standalone document**, the way a
journal referee would. The reviewer will not consult experiment logs or
phase artifacts — only the note itself.

The question: "Based solely on what is written here, am I convinced this
result is correct and complete?"

## Required checks

- Every systematic source in the uncertainty table: is the method described,
  is the magnitude reported, is validation evidence shown?
- Every comparison to a reference: is a quantitative compatibility metric
  given and interpreted?
- Does the note contain enough detail for an independent analyst to
  reproduce the measurement?
- Conventions check (final):
{conventions_block}
  Is anything required there that is absent from the note?

## Depth requirements

The AN is the complete record — not a summary. Minimum expectations:
- One subsection per systematic source (not just a summary table)
- One subsection per cross-check with quantitative result
- Per-cut event selection with individual distributions and efficiencies
- Full covariance matrix in appendix (table, not just figure)
- Machine-readable `results/` directory (CSV/JSON for spectrum, covariance)
- LaTeX math throughout (`$\\alpha_s$` not `alpha_s`)
- `pixi.toml` must have an `all` task for full reproducibility

A measurement analysis with ~5 systematics, ~3 cross-checks, ~6 cuts, and
~18 bins should produce ~50-100 rendered pages. Under 30 pages means
detail is missing.

## Plotting

Import the shared plotting utility for all figures:
```python
from common.plotting import create_figure, create_ratio_figure, save_figure, add_experiment_label
```

Do NOT use raw `plt.subplots()` or custom `figsize`. The utility enforces
the required figure size (10x10), style, and save conventions. Violations
are Category A review findings.

Reference figures in the artifact using markdown image syntax:
```markdown
![Detailed caption describing what is plotted.](figures/filename.pdf)
```

To build the final PDF, run `pixi run build-pdf` (task defined in pixi.toml).

## Review

This phase gets 3-bot review. The cost of iteration here is acceptable —
better to loop than to publish an incomplete result.
""",
}

# Technique-specific blocks injected into phase templates
TECHNIQUE_BLOCKS = {
    "unfolding": {
        "conventions_list": "- `conventions/unfolding.md` — required systematics, "
        "response matrix validation, regularization, covariance",
        "conventions_block": "   - `conventions/unfolding.md`\n",
        "technique_block_phase3": """\
## Technique-specific: Unfolding

Before constructing the response matrix:
- Produce data/MC comparison plots for ALL kinematic variables entering the
  observable, resolved by reconstructed object category
- Document the level of agreement per category
- Identify and document any discrepancies

These plots are evidence that the MC response model is adequate. They are
required — not optional — even if observable-level data/MC looks fine.

""",
        "review_extras_phase3": """\
- Are particle-level inputs validated per object category with data/MC plots?
  (Category A if missing for unfolded measurements)
""",
        "technique_block_phase4": """\
2. **Prior-sensitivity check.** Repeat the unfolding with a flat prior at
   nominal regularization. If any bin changes by >20%, the result is
   prior-dominated there. Increase iterations, merge bins, or exclude.

3. **Alternative method.** At least one independent unfolding method or
   cross-check (e.g., OmniFold, SVD, bin-by-bin) must be available.

4. **Hadronization model.** If only one generator is available for the
   response matrix, document this as a limitation. Data-driven reweighting
   is not a substitute for a genuine alternative-generator comparison.

""",
    },
    "template_fit": {
        "conventions_list": "- `conventions/template-fit.md` (to be created "
        "after first template-fit analysis)",
        "conventions_block": "   - `conventions/template-fit.md` (if it exists)\n",
        "technique_block_phase3": "",
        "review_extras_phase3": "",
        "technique_block_phase4": "",
    },
}

DEFAULT_TECHNIQUE_BLOCKS = {
    "conventions_list": "- No technique-specific conventions yet. "
    "Add to `conventions/` after this analysis.",
    "conventions_block": "   - (no technique-specific conventions yet)\n",
    "technique_block_phase3": "",
    "review_extras_phase3": "",
    "technique_block_phase4": "",
}


def scaffold(analysis_dir: Path, analysis_type: str, technique: str | None):
    """Create the analysis directory structure with CLAUDE.md files."""
    analysis_dir.mkdir(parents=True, exist_ok=True)

    technique_blocks = TECHNIQUE_BLOCKS.get(
        technique or "", DEFAULT_TECHNIQUE_BLOCKS
    )

    # Common format kwargs
    fmt = {
        "name": analysis_dir.name,
        "analysis_type": analysis_type,
        "technique_line": f"Technique: {technique}" if technique else "",
        "preamble": PHASE_PREAMBLE,
        **technique_blocks,
    }

    # Analysis-root CLAUDE.md
    root_claude = analysis_dir / "CLAUDE.md"
    if not root_claude.exists():
        root_claude.write_text(ROOT_TEMPLATE.format(**fmt))
        print(f"  wrote {root_claude}")

    # Per-phase directories and CLAUDE.md
    for phase_name, _review_type in PHASES:
        phase_dir = analysis_dir / phase_name
        phase_dir.mkdir(exist_ok=True)
        for subdir in PHASE_SUBDIRS:
            (phase_dir / subdir).mkdir(exist_ok=True)

        # Phase CLAUDE.md
        claude_path = phase_dir / "CLAUDE.md"
        template = PHASE_TEMPLATES.get(phase_name, "")
        if template and not claude_path.exists():
            claude_path.write_text(template.format(**fmt))
            print(f"  wrote {claude_path}")

    # scripts/common/ — shared plotting utilities
    common_dir = analysis_dir / "scripts" / "common"
    common_dir.mkdir(parents=True, exist_ok=True)
    template_common = HERE / "templates" / "scripts" / "common"
    for src in [template_common / "plotting.py", template_common / "__init__.py"]:
        dst = common_dir / src.name
        if not dst.exists():
            if src.exists():
                dst.write_text(src.read_text())
                print(f"  wrote {dst}")
            else:
                print(f"  WARNING: {src} not found, skipping")

    # phase5_documentation/exec/build_pdf.py from template
    build_pdf_src = HERE / "templates" / "build_pdf.py"
    build_pdf_dst = analysis_dir / "phase5_documentation" / "exec" / "build_pdf.py"
    if not build_pdf_dst.exists():
        if build_pdf_src.exists():
            build_pdf_dst.write_text(build_pdf_src.read_text())
            print(f"  wrote {build_pdf_dst}")
        else:
            print(f"  WARNING: {build_pdf_src} not found, skipping build_pdf.py")

    # Analysis-local pixi.toml from template
    pixi_path = analysis_dir / "pixi.toml"
    if not pixi_path.exists():
        template_path = HERE / "templates" / "pixi.toml"
        if template_path.exists():
            pixi_text = template_path.read_text().replace("{name}", fmt["name"])
            pixi_path.write_text(pixi_text)
            print(f"  wrote {pixi_path}")
        else:
            print(f"  WARNING: {template_path} not found, skipping pixi.toml")

    # Experiment log and retrieval log
    for log_name in ["experiment_log.md", "retrieval_log.md"]:
        log_path = analysis_dir / log_name
        if not log_path.exists():
            log_path.write_text(f"# {log_name.replace('_', ' ').replace('.md', '').title()}\n")
            print(f"  wrote {log_path}")

    print(f"\nScaffolded {analysis_dir}/ ({analysis_type}"
          f"{f', {technique}' if technique else ''})")
    print(f"\nNext: cd {analysis_dir} && pixi install")


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold a new analysis with per-phase CLAUDE.md files."
    )
    parser.add_argument("dir", type=Path, help="Analysis directory to create")
    parser.add_argument(
        "--type",
        choices=["measurement", "search"],
        required=True,
        dest="analysis_type",
        help="Analysis type",
    )
    parser.add_argument(
        "--technique",
        choices=["unfolding", "template_fit"],
        default=None,
        help="Analysis technique (determines which conventions apply)",
    )
    args = parser.parse_args()
    scaffold(args.dir, args.analysis_type, args.technique)


if __name__ == "__main__":
    main()
