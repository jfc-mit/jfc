# Orchestration Guide

> See `03a-orchestration.md` for the architectural rationale.
> See `appendix-prompts.md` for the agent prompt templates that populate this layout.

How to execute the methodology specification using Claude Code or any
multi-session LLM agent system.

## Core Principle: Session Isolation

Every agent invocation — execution, review, arbitration — is a **separate,
isolated session** with explicitly defined inputs and outputs. No shared
conversation history, no shared memory, no implicit state. Each session
reads files, writes files, and exits. The files are the interface.

```
┌─────────────┐     ┌──────────┐     ┌──────────────┐
│   inputs/   │────►│  agent   │────►│   outputs/   │
│  (read-only)│     │ session  │     │  (new files) │
└─────────────┘     └──────────┘     └──────────────┘
                         │
                         ▼
                    logs/{role}_{name}_{timestamp}.md
                (full conversation transcript via cc /export)
```

**Exception: the experiment log.** Each phase has an `experiment_log.md` that
persists across executor sessions within that phase. Every executor session
reads the existing log and appends to it. This is the only mutable shared state
within a phase — it prevents agents from re-trying failed approaches and gives
humans visibility into decision-making.

**Concurrency note:** Parallel tracks (per-channel work in Phase 3, concurrent
calibrations) each have their own experiment log in their own directory. The
experiment log is shared only across *sequential* sessions within a single
track — never across parallel agents. If sub-agents within a single session
need to append to the same log, they must do so sequentially.

## Agent Session Identity

Every agent session is assigned a **session name** — a random human first name
drawn from the pool below. The orchestrator never reuses a name within an
analysis run. This serves two purposes:

1. **Traceability.** Every file produced by a session includes the session name
   and timestamp. When reading artifacts, agents and humans can trace who
   produced what and when.

2. **No clobbering.** Iteration produces new files rather than overwriting
   previous versions. The second executor run creates a new artifact alongside
   the first. Agents always read the most recent artifact (by timestamp);
   humans can compare versions.

**Name pool** (88 names — from `orchestrator/names.py`):
Ada, Agnes, Albert, Alfred, Amara, Andrzej, Anselm, Basil, Boris,
Brigitte, Casimir, Celeste, Claude, Cosima, Dagmar, Dmitri, Dolores,
Dorothea, Edmund, Eloise, Emeric, Eric, Estelle, Fabian, Fabiola,
Felix, Fiona, Florence, Gerald, Gertrude, Greta, Gunnar, Hana, Hedwig,
Hiroshi, Hugo, Ingrid, Isolde, Ivan, Jasper, Joe, Johanna, Jules,
Katya, Kenji, Klaus, Lena, Leopold, Ludmila, Magnus, Marcel, Margaret,
Mireille, Nadia, Nikolai, Nora, Odette, Oscar, Otto, Pavel, Peter,
Petra, Phil, Philippa, Quentin, Rainer, Renata, Rosa, Sabine, Sally,
Sam, Sigrid, Sven, Theo, Tomas, Tomoko, Ulrich, Ursula, Valentina,
Vera, Viktor, Wanda, Wolfgang, Xena, Yuki, Yvette, Zelda, Zoran.

**Naming convention for handoff files:**
```
{ARTIFACT}_{session_name}_{YYYY-MM-DD}_{HH-MM}.md
```

Examples:
- `STRATEGY_fabiola_2026-03-13_14-30.md`
- `STRATEGY_CRITICAL_REVIEW_phil_2026-03-13_15-00.md`
- `STRATEGY_ARBITER_albert_2026-03-13_15-30.md`
- `inputs_dolores_2026-03-13_15-45.md`

The orchestrator tells each agent its assigned session name in the input
prompt. The agent uses this name when naming its output files. Downstream
agents discover the current artifact by finding the most recent file matching
the artifact type pattern (e.g., `STRATEGY_*_*.md`), sorted by timestamp.
This eliminates the need to overwrite files on iteration — each session's
work is preserved and the history is self-documenting.

## Agent Session Logs

Each phase has a `logs/` directory that centralizes all agent session
records. Every agent maintains an **incremental session log** — a
per-session file written to progressively as the agent works, not just
at session end. This is the crash-resilient lab notebook: if an agent
dies mid-task, the log up to that point survives.

**File naming:**
```
logs/{role}_{session_name}_{YYYY-MM-DD}_{HH-MM}.md
```

Examples:
- `logs/executor_sam_2026-03-13_14-30.md`
- `logs/critical_andrzej_2026-03-13_15-00.md`
- `logs/arbiter_sally_2026-03-13_15-30.md`

**When to append.** Agents write to their session log at natural
milestones, not after every line of thought. Typical milestones:

| Milestone | What to log |
|-----------|-------------|
| Session start | Role, assigned task, key inputs received |
| Plan produced | Summary of plan (not the full plan — that's in `plan.md`) |
| Code written | What script was written, what it does, key design choices |
| Test/validation run | What was run, result (pass/fail/numbers), interpretation |
| Figure generated | Which figure, what it shows, any issues |
| Decision point | What alternatives were considered, what was chosen, why |
| Error/retry | What failed, what was tried next |
| Artifact produced | What was written, summary of content |
| Session end | What was accomplished, what remains, any open issues |

**Format.** Each entry is a timestamped markdown block. Keep entries
concise — 2-5 sentences each. The log is a lab notebook, not a transcript.

```markdown
### 14:32 — Session start
Executor for Phase 3 selection. Inputs: STRATEGY.md, EXPLORATION.md,
experiment_log.md. Task: implement BDT-based signal selection per strategy.

### 14:35 — Plan produced
Plan: (1) preselection cuts, (2) BDT training with XGBoost, (3) alternative
NN architecture, (4) optimize working point, (5) closure tests. See plan.md.

### 14:48 — Preselection implemented
Wrote preselection.py: 4 cuts (ncharged>=5, thrust<0.9, Evis>0.5*sqrt(s), |cos(theta)|<0.9).
Cutflow: 847k→612k→589k→571k→498k. All cuts motivated by EXPLORATION.md distributions.

### 15:12 — BDT training complete
XGBoost with 12 features, 500 rounds. AUC=0.94 on test set. Train/test score
distributions overlap well (no overtraining). Saved ROC, scores, feature importance
to figures/.
```

**Supplement: `/export`.** At session end, agents should still run
`cc /export` to save the full conversation transcript alongside the
session log. The transcript is a complete record; the session log is the
crash-safe summary. If the agent crashes before `/export`, the session
log is still available.

All session logs for a phase live in one auditable location (`logs/`),
replacing the previous pattern of scattering logs across `outputs/` and
`review/` subdirectories.

---

## Directory Layout

```
analysis_name/
  prompt.md
  regression_log.md              # Tracks any phase regressions (if triggered)

  calibrations/                  # Shared sub-analyses (may scale to near-full
    calibration_1/               #   sub-analysis structure if complexity warrants)
      experiment_log.md          #   e.g., btag, jet_corrections, trigger_eff
      retrieval_log.md
      CALIBRATION_1.md
      src/
      outputs/
        figures/
    calibration_2/
      experiment_log.md
      retrieval_log.md
      CALIBRATION_2.md
      src/
      outputs/
        figures/

  phase1_strategy/
    experiment_log.md            # Lab notebook for this phase
    retrieval_log.md
    UPSTREAM_FEEDBACK.md         # Feedback from downstream phases (if any)
    REGRESSION_TICKET.md         # Regression investigation output (if triggered)
    src/                         # Phase-level codebase (can grow to thousands of lines)
    outputs/                     # All produced artifacts
      figures/                   # Plots
      inputs_fabiola_2026-03-13_14-30.md       # Session-named inputs
      plan_fabiola_2026-03-13_14-30.md
      STRATEGY_fabiola_2026-03-13_14-30.md     # Session-named artifact
      # On iteration, new files appear alongside (no overwrites):
      # inputs_peter_2026-03-13_16-00.md
      # STRATEGY_peter_2026-03-13_16-00.md
    review/
      critical/
        inputs_andrzej_2026-03-13_15-00.md
        STRATEGY_CRITICAL_REVIEW_andrzej_2026-03-13_15-00.md
      constructive/
        inputs_dolores_2026-03-13_15-00.md
        STRATEGY_CONSTRUCTIVE_REVIEW_dolores_2026-03-13_15-00.md
      validation/                  # Plot validator (programmatic checks)
        STRATEGY_PLOT_VALIDATION_joe_2026-03-13_15-00.md
      arbiter/
        inputs_albert_2026-03-13_15-30.md
        STRATEGY_ARBITER_albert_2026-03-13_15-30.md
    logs/                        # Agent session logs (incremental + /export)
      executor_fabiola_2026-03-13_14-30.md
      critical_andrzej_2026-03-13_15-00.md
      constructive_dolores_2026-03-13_15-00.md
      arbiter_albert_2026-03-13_15-30.md

  phase2_exploration/
    experiment_log.md
    retrieval_log.md
    UPSTREAM_FEEDBACK.md
    REGRESSION_TICKET.md
    src/
    outputs/
      figures/
      ...
    logs/
    # Self-review only — no review/ directory

  phase3_selection/              # Per-channel if multi-channel
    channel_a/                   # Replace with analysis-specific names
      experiment_log.md
      retrieval_log.md
      sensitivity_log.md         # Tracks optimization attempts
      UPSTREAM_FEEDBACK.md
      REGRESSION_TICKET.md
      src/                       # Per-channel codebase
      outputs/
        figures/
        ...
        SELECTION_CHANNEL_A.md
      review/
        critical/                # 1-bot review per channel
          ...
      logs/
    channel_b/
      experiment_log.md
      retrieval_log.md
      sensitivity_log.md
      UPSTREAM_FEEDBACK.md
      REGRESSION_TICKET.md
      src/
      outputs/
        figures/
        ...
        SELECTION_CHANNEL_B.md
      review/
        critical/
          ...
      logs/
    SELECTION_COMBINED.md        # Consolidation artifact

  phase4_inference/
    4a_expected/
      experiment_log.md
      retrieval_log.md
      UPSTREAM_FEEDBACK.md
      REGRESSION_TICKET.md
      src/
      outputs/
        figures/
        ...
        INFERENCE_EXPECTED.md
        ANALYSIS_NOTE_4a_v1.md
        ANALYSIS_NOTE_4a_v1.tex
        ANALYSIS_NOTE_4a_v1.pdf
      review/
        physics/                # 4-bot+bib review (agent gate)
          ...
        critical/
          ...
        constructive/
          ...
        arbiter/
          ...
      logs/
    4b_partial/
      experiment_log.md
      retrieval_log.md
      UPSTREAM_FEEDBACK.md
      REGRESSION_TICKET.md
      src/
      outputs/
        figures/
        ...
        INFERENCE_PARTIAL.md
        ANALYSIS_NOTE_4b_v1.md
        ANALYSIS_NOTE_4b_v1.tex
        ANALYSIS_NOTE_4b_v1.pdf
        UNBLINDING_CHECKLIST.md
      review/
        physics/                # 4-bot review before human
          ...
        critical/
          ...
        constructive/
          ...
        arbiter/
          ...
      logs/
    4c_observed/                 # Created after human approval
      experiment_log.md
      retrieval_log.md
      UPSTREAM_FEEDBACK.md
      REGRESSION_TICKET.md
      src/
      outputs/
        figures/
        ...
        INFERENCE_OBSERVED.md
        ANALYSIS_NOTE_4c_v1.md
        ANALYSIS_NOTE_4c_v1.tex
        ANALYSIS_NOTE_4c_v1.pdf
      review/
        critical/               # 1-bot review
          ...
      logs/

  phase5_documentation/
    retrieval_log.md
    UPSTREAM_FEEDBACK.md
    REGRESSION_TICKET.md
    outputs/
      figures/
      ...
      ANALYSIS_NOTE_5_v1.md
      ANALYSIS_NOTE_5_v1.tex
      ANALYSIS_NOTE_5_v1.pdf
    review/
      physics/                  # 5-bot review
        ...
      critical/
        ...
      constructive/
        ...
      rendering/
        ...
      arbiter/
        ...
    logs/
```
