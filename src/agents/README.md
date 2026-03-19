# Agent Definitions

Self-contained definitions for every agent role in the analysis pipeline.
Each file is a complete, auditable specification: role, inputs, outputs,
methodology references, and prompt template.

The orchestrator uses these definitions when spawning subagents.

## Executor agents

| Agent | File | Role |
|-------|------|------|
| Executor | `executor.md` | Phase execution — plan, code, figures, artifacts |
| Note writer | `note_writer.md` | Phase 5 AN prose — reads artifacts, writes the analysis note |
| Fixer | `fixer.md` | Targeted fixes for review findings and regression tickets |

## Reviewer agents

| Agent | File | Role |
|-------|------|------|
| Physics reviewer | `physics_reviewer.md` | Senior collaboration member review ("would I approve?") |
| Critical reviewer | `critical_reviewer.md` | Find all flaws in correctness and completeness |
| Constructive reviewer | `constructive_reviewer.md` | Strengthen the analysis — clarity, validation, presentation |
| Plot validator | `plot_validator.md` | Programmatic validation of plotting code and histogram data |
| Rendering reviewer | `rendering_reviewer.md` | Phase 5 PDF compilation and rendering inspection |

## Adjudication agents

| Agent | File | Role |
|-------|------|------|
| Arbiter | `arbiter.md` | Adjudicate reviews — PASS / ITERATE / ESCALATE |
| Investigator | `investigator.md` | Regression investigation and scoped fix tickets |

## Specialist agents

| Agent | File | Role |
|-------|------|------|
| Typesetter | `typesetter.md` | LaTeX expert for Phase 5 PDF production |

## Context assembly

Context assembly follows §3a.4 (three layers: bird's-eye framing,
relevant methodology sections, upstream artifacts). The phase CLAUDE.md
files (from `templates/`) are what agents read at runtime; these
definitions specify how the *orchestrator* launches agents that will
read those files.

## Review panel composition

| Review tier | Agents (parallel) | Then |
|-------------|-------------------|------|
| 4-bot | physics + critical + constructive + plot validator | arbiter |
| 5-bot | physics + critical + constructive + plot validator + rendering | arbiter |
| 1-bot | critical + plot validator | (no arbiter — check findings directly) |
| Self | executor self-check | (Phase 2 only) |
