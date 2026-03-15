# reslop

LLM-driven HEP analysis framework. An orchestrator agent delegates work to
subagents through five sequential phases, producing a publication-quality
analysis note.

## Quick start

```bash
pixi run scaffold analyses/my_analysis --type measurement
cd analyses/my_analysis
# Edit .analysis_config → set data_dir=/path/to/data, add allow= lines
pixi install
claude   # pass your physics prompt
```

## How it works

```
┌─────────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR                             │
│  Never writes code. Holds: prompt, summaries, verdicts only  │
└─────┬───────────────────────────────────────────────────────┘
      │
      ▼
 ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
 │ Phase 1  │──▶│ Phase 2  │──▶│ Phase 3  │──▶│ Phase 4a │──▶│ Phase 5  │
 │ Strategy │   │ Explore  │   │ Selection│   │ Inference│   │ Document │
 │ (3-bot)  │   │ (self)   │   │ (1-bot)  │   │ (3-bot)  │   │ (4-bot)  │
 └──────────┘   └──────────┘   └──────────┘   └────┬─────┘   └──────────┘
                                                    │
                                              HUMAN GATE
                                          (measurements)
```

Each phase runs the same loop:

```
  1. EXECUTE ── spawn executor subagent (enters plan mode first)
  2. REVIEW ─── spawn reviewer(s) per review type
  3. CHECK:
       Regression trigger? → Investigator → fix origin + downstream → resume
       A or B items?       → fix agent + fresh reviewer → re-review (loop)
       Only C items?       → PASS, executor applies Cs before commit
  4. COMMIT
  5. HUMAN GATE (after 4a for measurements / after 4b for searches)
  6. ADVANCE
```

### Phases

| Phase | Review | Key deliverable |
|-------|--------|-----------------|
| **1. Strategy** | 3-bot | Technique selection, systematic plan, reference analysis table, conventions enumeration |
| **2. Exploration** | Self | Sample inventory, data quality, variable ranking, preselection cutflow |
| **3. Selection** | 1-bot | Event selection, correction chain or background model, closure tests |
| **4a. Inference** | 3-bot | Systematic completeness table, covariance matrix, reference comparisons |
| **5. Documentation** | 4-bot | Analysis note (pandoc markdown → PDF, 50-100 pages), machine-readable results |

Measurements skip Phases 4b/4c (nothing to blind). Searches add 4b (10%
unblinding) and 4c (full unblinding) with a human gate between them.

### Review classification

| Cat | Meaning | Action |
|-----|---------|--------|
| **A** | Would cause rejection | Fix + re-review + fresh reviewer |
| **B** | Weakens the analysis | Same — must be zero before PASS |
| **C** | Style / clarity | Arbiter PASses; executor applies before commit |

Fresh reviewer added each iteration cycle. Limits: 3-bot warn at 6, strong
warn at 10. 1-bot warn at 4, escalate at 6.

### Phase regression

Any review can trigger regression when a physics issue is traceable to an
earlier phase. Most common after Phase 4a/4b and Phase 5 reviews.

```
Reviewer finds physics issue from Phase M < current Phase N
  → Investigator traces impact → REGRESSION_TICKET.md
  → Fix cycle: re-run Phase M, re-run affected downstream, skip unaffected
  → Resume review at Phase N
```

### Phase 5: 4-bot review

```
Critical (referee) + Constructive + Rendering (reads compiled PDF) + Arbiter
```

The rendering reviewer runs `pixi run build-pdf` and uses the Read tool to
visually inspect the PDF for figure rendering, math compilation, layout, and
cross-references.

## Key concepts

**Technique decided at Phase 1, not scaffold time.** The scaffolder only
takes `--type measurement|search`. The strategy phase selects the technique
(unfolding, template fit, etc.), which activates technique-specific
requirements in later phases.

**Conventions.** Domain knowledge in `src/conventions/` (symlinked into each
analysis). Mandatory reads at Phases 1, 4a, and 5. Updated after analysis
completion.

**Feasibility evaluation.** When hitting a limitation (missing MC, etc.),
agents must: state it → evaluate feasibility → estimate cost → decide
(attempt if it affects the core result, document if minor or infeasible) →
log the reasoning.

**Isolation.** A PreToolUse hook checks every file access against
`.analysis_config` (which lists `data_dir` and `allow=` paths). Symlinks
within the analysis dir (like `conventions/`) are allowed via logical path
checking.

**Pixi everywhere.** Each analysis has its own `pixi.toml` with deps and
tasks. `pixi run all` is the reproducibility contract. `pixi run build-pdf`
compiles the analysis note via pandoc.

## Directory structure

```
reslop/
  src/                        Spec infrastructure
    methodology/              Methodology spec (human reference)
    orchestration/            Session management (human reference)
    conventions/              Domain knowledge (symlinked into analyses)
    templates/                CLAUDE.md and pixi.toml templates
    scaffold_analysis.py      Scaffolder
  analyses/                   Each is its own git repo
    <name>/
      CLAUDE.md               ~570 lines — self-contained instructions
      pixi.toml               Environment + task graph
      .analysis_config        data_dir + allow paths for isolation hook
      conventions/ → src/conventions/
      phase{1..5}_*/          Phase dirs with CLAUDE.md, exec/, scripts/, figures/, review/
```

## Requirements

- [pixi](https://pixi.sh) for environment management
- [Claude Code](https://claude.ai/claude-code) as the agent runtime
