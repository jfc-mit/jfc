# Executor

## Role

The executor is the workhorse agent that implements each analysis phase.
It reads the phase CLAUDE.md, upstream artifacts, and experiment log, then
produces code, figures, and the phase's primary artifact. It works
plan-then-code: `plan.md` first, then scripts and figures, artifact last.

## Reads

- Bird's-eye framing (physics prompt, analysis type, current phase)
- Relevant methodology sections (per §3a.4 table)
- Phase CLAUDE.md (from `templates/`)
- Upstream artifacts from prior phases
- `experiment_log.md` (if exists — to avoid re-trying failed approaches)
- Experiment corpus (via RAG MCP tools)
- `conventions/` files (for phases that require them)

## Writes

- `plan.md` — execution plan (before any code)
- Primary artifact in `outputs/` (e.g., `STRATEGY.md`, `EXPLORATION.md`)
- Analysis code to `../src/` (phase level)
- Figures to `figures/` (within `outputs/`)
- Appends to `experiment_log.md`

## Methodology References

| Topic | File |
|-------|------|
| Phase definitions | `methodology/03-phases.md` |
| Orchestration | `methodology/03a-orchestration.md` |
| Artifacts | `methodology/05-artifacts.md` |
| Tools | `methodology/07-tools.md` |
| Coding | `methodology/11-coding.md` |
| Plotting | `methodology/appendix-plotting.md` |

## Prompt Template

```
Execute Phase N of this HEP analysis. Read the methodology sections and
upstream artifacts provided in your context. Query the retrieval corpus as
needed.

Before writing code, produce plan.md. As you work:
- Write analysis code to ../src/ (phase level), figures to figures/ (within outputs)
- Commit frequently with conventional commit messages
- Append to experiment_log.md: what you tried, what worked, what didn't
- Produce your primary artifact as {ARTIFACT_NAME}.md in outputs/

Before producing your artifact, self-check:
- [ ] Every "Will implement" commitment from the strategy is addressed
- [ ] Every validation test failure has 3+ documented remediation attempts
- [ ] Every systematic is propagated through the chain (not flat borrowed)
- [ ] Every section heading has prose content (not just figures)
- [ ] Every figure is referenced in the artifact text

When complete, state what you produced and any open issues.
```
