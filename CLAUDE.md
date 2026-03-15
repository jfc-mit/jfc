# Project Rules

This is a HEP (High Energy Physics) analysis project using LLM-driven agents.

## Project structure

```
reslop/
  src/                      # Spec infrastructure (do not modify during analysis)
    methodology/              Methodology spec (human reference)
    orchestration/            Session management spec (human reference)
    conventions/              Domain knowledge (symlinked into analyses)
    templates/                Templates for new analyses
    scaffold_analysis.py      Creates analysis directories
  analyses/                 # Each is its own git repo
    <name>/
      CLAUDE.md               Self-contained analysis instructions
      pixi.toml               Environment + task graph
      phase*/                 Phase directories with CLAUDE.md files
  CLAUDE.md                 This file
  README.md                 Human-readable project overview
  pyproject.toml            Root pixi config (scaffolding only)
```

## Boundary rules

- Agents **never modify** files outside `analyses/<name>/` during execution.
- Each analysis has its own git repo and pixi environment.
- `src/conventions/` is updated **after** an analysis completes, not during.
- `src/methodology/` and `src/orchestration/` are human reference only —
  agents get their instructions from analysis-level CLAUDE.md files.

## Environment: pixi is mandatory

All code runs through pixi. Never use bare `python`, `pip install`, or `conda`.

**From the project root** (scaffolding):
```bash
pixi run scaffold analyses/my_analysis --type measurement
pixi run scaffold analyses/my_analysis --type search
```

**From an analysis directory** (all analysis code):
```bash
cd analyses/my_analysis
pixi run py path/to/script.py
pixi shell
```

## Scaffolding a new analysis

```bash
pixi run scaffold analyses/foo --type measurement
pixi run scaffold analyses/foo --type search
```

This creates the directory structure, CLAUDE.md files, pixi.toml,
conventions symlink, .analysis_config, and initializes a git repo.

After scaffolding, edit `.analysis_config` to set `data_dir` to the path
where input data lives (the isolation hook needs this to allow data access).

## Running an analysis

```bash
cd analyses/foo
pixi install
claude    # starts the orchestrator agent
```

The analysis-root CLAUDE.md contains everything the agent needs:
tool requirements, coding rules, scale-out rules, plotting conventions,
phase gates, review protocol, phase regression, feasibility evaluation,
orchestrator execution model, and pixi reference.
