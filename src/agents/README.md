# Agent Definitions

Self-contained definitions for every agent role in the analysis pipeline.
Each file is a complete, auditable specification: role, inputs, outputs,
methodology references, and prompt template.

The orchestrator uses these definitions when spawning subagents.

## Executor agents

| Agent | File | Role |
|-------|------|------|
| Executor | `executor.md` | Phase execution — plan, code, figures, artifacts |
| Note writer | `note_writer.md` | AN prose — reads artifacts, writes the analysis note |
| Fixer | `fixer.md` | Targeted fixes for review findings and regression tickets |

## Reviewer agents

| Agent | File | Role |
|-------|------|------|
| Physics reviewer | `physics_reviewer.md` | Senior collaboration member review ("would I approve?") |
| Critical reviewer | `critical_reviewer.md` | Find all flaws in correctness and completeness |
| Constructive reviewer | `constructive_reviewer.md` | Strengthen the analysis — clarity, validation, presentation |
| Plot validator | `plot_validator.md` | Programmatic validation of plotting code and histogram data |
| BibTeX validator | `bibtex_validator.md` | Verify citations resolve to real, accurate bibliographic records |
| Rendering reviewer | `rendering_reviewer.md` | PDF compilation and rendering inspection |

## Adjudication agents

| Agent | File | Role |
|-------|------|------|
| Arbiter | `arbiter.md` | Adjudicate reviews — PASS / ITERATE / ESCALATE |
| Investigator | `investigator.md` | Regression investigation and scoped fix tickets |

## Specialist agents

| Agent | File | Role |
|-------|------|------|
| Typesetter | `typesetter.md` | LaTeX expert for PDF production |

## Phase activation

### Execution pipeline

Each phase runs execution agents in sequence. Later agents depend on
earlier outputs.

| Phase | Step 1 | Step 2 | Step 3 |
|-------|--------|--------|--------|
| Ph1 | executor (strategy) | | |
| Ph2 | executor (explore) | | |
| Ph3 | executor (selection) | | |
| Ph4a | executor (stats) | note writer (AN v1) | typesetter (compile) |
| Ph4b | executor (10% stats) | note writer (update AN) | typesetter (compile) |
| Ph4c | executor (full stats) | note writer (update AN) | |
| Ph5 | executor (figures) | note writer (final AN) | typesetter (final PDF) |

The fixer replaces the executor during ITERATE cycles at any phase.

### Review panel by phase

"x" = agent is active at that phase's review gate.

| Agent | Ph1 | Ph2 | Ph3 | Ph4a | Ph4b | Ph4c | Ph5 |
|-------|-----|-----|-----|------|------|------|-----|
| Physics reviewer | x | | | x | x | | x |
| Critical reviewer | x | | x | x | x | x | x |
| Constructive reviewer | x | | | x | x | | x |
| Plot validator | | x | x | x | x | x | x |
| BibTeX validator | | | | x | x | | x |
| Rendering reviewer | | | | | | | x |
| Arbiter | x | | | x | x | | x |

**Plot validator** runs at every phase that produces figures (Phases 2-5).
At Phase 2 (self-review), it runs alongside the executor's self-check.
At Phase 1, it is skipped (strategy phase typically has no figures).

**BibTeX validator** runs at phases where the AN exists and has citations
(4a, 4b, 5). It verifies DOIs, arXiv IDs, and INSPIRE records actually
resolve to the expected papers — catching hallucinated entries.

**Rendering reviewer** runs only at Phase 5 where the final PDF is the
deliverable. At Phase 4a/4b, the typesetter's compilation serves as the
rendering check.

## Review panel composition

| Review tier | Phases | Parallel agents | Then |
|-------------|--------|----------------|------|
| 4-bot | 1 | physics + critical + constructive | arbiter |
| 4-bot+bib | 4a, 4b | physics + critical + constructive + plot validator + bibtex | arbiter |
| 5-bot | 5 | physics + critical + constructive + plot validator + rendering + bibtex | arbiter |
| 1-bot | 3, 4c | critical + plot validator | (no arbiter) |
| Self | 2 | executor self-check + plot validator | — |

## Context assembly

Context assembly follows §3a.4 (three layers: bird's-eye framing,
relevant methodology sections, upstream artifacts). The phase CLAUDE.md
files (from `templates/`) are what agents read at runtime; these
definitions specify how the *orchestrator* launches agents that will
read those files.
