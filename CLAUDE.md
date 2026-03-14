# Project Rules

This is a HEP (High Energy Physics) analysis project using LLM-driven agents.
The full methodology is in `methodology.md`. These rules are the short version
that must always be followed.

## Project structure and isolation

```
reslop/                   # SPEC — do not modify during analysis
  methodology/              Methodology spec (source of truth)
  orchestration/            Session management spec
  conventions/              Domain knowledge (consult, update after analysis)
  templates/                Base templates for new analyses
  CLAUDE.md                 This file (global rules)

analyses/<name>/          # ANALYSIS — agents work here
  pixi.toml                 Analysis-specific environment (agents can modify)
  CLAUDE.md                 Analysis-level instructions
  phase*/CLAUDE.md          Phase-level instructions
  phase*/scripts/           Analysis code
  ...
```

**Boundary rules:**
- Agents **never modify** files outside `analyses/<name>/` during execution.
- Each analysis has its own `pixi.toml` with its own dependencies.
- To add a dependency: edit the analysis's `pixi.toml`, then `pixi install`
  from the analysis directory.
- `conventions/` is updated **after** an analysis completes, not during.

## Environment: pixi is mandatory

All code runs through pixi. Never use bare `python`, `pip install`, or
`conda`.

**From the project root** (spec building, scaffolding):
```bash
pixi run build
pixi run scaffold analyses/my_analysis --type measurement --technique unfolding
```

**From an analysis directory** (all analysis code):
```bash
cd analyses/my_analysis
pixi run py path/to/script.py           # run a script
pixi run py -c "import uproot; ..."     # quick check
pixi shell                              # interactive shell
```

**Never:**
- `python script.py` — use `pixi run py script.py`
- `pip install X` — add to `pixi.toml`, then `pixi install`
- `conda activate` / `conda install` — pixi manages everything

## Required tools

Use these — not alternatives. Non-negotiable.

| Task | Use | NOT |
|------|-----|-----|
| ROOT file I/O | `uproot` | PyROOT, ROOT C++ macros |
| Array operations | `awkward-array`, `numpy` | Event loops, pandas |
| Histogramming | `hist`, `boost-histogram` | ROOT TH1, numpy.histogram (for filling) |
| Plotting | `matplotlib` + `mplhep` | ROOT TCanvas, plotly |
| Statistical model | `pyhf` (binned), `zfit` (unbinned) | RooFit, RooStats, custom likelihood code |
| Jet clustering | `fastjet` (Python) | manual clustering |
| Event processing | `coffea` (columnar) | Event-by-event loops |
| Logging | `logging` + `rich` | `print()` — never use bare print |

## Scale-out rules

**Always estimate before running at full scale.** Check input size, time a
1000-event slice, extrapolate.

| Estimated time | Action |
|---|---|
| < 2 min | Single-core local — just run it |
| 2–15 min | `ProcessPoolExecutor` or equivalent multicore |
| > 15 min | SLURM: `sbatch --wait` (single) or `--array` (per-file) |

- **Never wait > 15 min on a login node** when SLURM is available.
- **Prefer the simplest pattern.** Don't use coffea when ProcessPoolExecutor
  works. Don't use dask when SLURM array jobs work.
- **SLURM is fast on requeue partitions.** `--requeue` flag + short walltime
  = near-instant scheduling. Use `sbatch --wait` to block until done.
- See Section 7.3 of the methodology for code patterns.

## Coding rules

- **Columnar analysis.** Arrays, not event loops. Selections are boolean masks.
- **Prototype on a slice.** ~1000 events first, full data only for production.
- **Read the API.** `help(function)` before workarounds.
- **No bare `print()`.** Use `logging` + `rich`. Ruff T201 enforces this.
- **Conventional commits.** `<type>(phase): <description>`.
- **Scripts as pixi tasks.** Every analysis script gets a named task in
  `pixi.toml`. Each task runs independently. The `all` task runs the full
  chain in order — this is the reproducibility contract.
  ```toml
  select = "python phase3_selection/scripts/apply_selection.py"
  unfold = "python phase4_inference/scripts/unfold.py"
  all = "python phase3_selection/scripts/apply_selection.py && python phase4_inference/scripts/unfold.py"
  ```
  Update `pixi.toml` tasks whenever you add or rename a script.

## Conventions

Before starting work on a technique (unfolding, template fits, etc.), read
the applicable file in `conventions/`. This is mandatory at two checkpoints:

1. **Phase 1 (Strategy):** Read conventions before writing the systematic
   plan. Verify your plan covers the standard sources listed there.
2. **Phase 4a (Inference):** Re-read conventions before finalizing
   systematics. Check that every required source is implemented, not just
   planned. Produce a completeness table comparing your sources against
   conventions AND reference analyses from Phase 1.

If a convention requires something you plan to omit, justify the omission
explicitly — do not silently skip it.

## Review expectations

Check both **correctness** (is what's here right?) and **completeness**
(is anything missing?). The question is not "does this pass its own tests"
but "would a journal referee accept this."

The end goal of every analysis is a publication-quality analysis note
suitable for submission to a top-tier journal. Every phase contributes to
that goal. Reviewers should evaluate work against the standard of external
scrutiny: "Would a journal referee send this back? If a competing group
published a measurement of the same quantity, what would they have that
we don't?"
