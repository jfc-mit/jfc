## Agent Prompt Templates

Full agent definitions — role, inputs/outputs, methodology references, and
prompt templates — live in `../agents/*.md`. See `../agents/README.md` for
the index.

This appendix provides a summary of roles and context assembly rules.

Context assembly follows §3a.4 (three layers: bird's-eye framing,
relevant methodology sections, upstream artifacts). The phase CLAUDE.md
files (from `../templates/`) are what agents read at runtime; the agent
definitions in `../agents/` specify how the *orchestrator* launches agents
that will read those files.

### Agent summary

**Executor agents:**

| Role | Definition | Context | Writes |
|------|-----------|---------|--------|
| Executor | `agents/executor.md` | Full methodology + RAG | `outputs/` artifacts, `../src/` code, `outputs/figures/` |
| Note writer | `agents/note_writer.md` | Phase artifacts + conventions | `outputs/ANALYSIS_NOTE.md` |
| Fixer | `agents/fixer.md` | Arbiter verdict or regression ticket + existing code | Updated artifact + code |

**Reviewer agents:**

| Role | Definition | Context | Writes |
|------|-----------|---------|--------|
| Physics reviewer | `agents/physics_reviewer.md` | Physics prompt + artifact only | `review/physics/` |
| Critical reviewer | `agents/critical_reviewer.md` | Full methodology + RAG | `review/critical/` |
| Constructive reviewer | `agents/constructive_reviewer.md` | Full methodology + RAG | `review/constructive/` |
| Plot validator | `agents/plot_validator.md` | Plotting scripts + histogram data | `review/validation/` |
| Rendering reviewer | `agents/rendering_reviewer.md` | Compiled PDF only | `review/rendering/` |

**Adjudication and specialist agents:**

| Role | Definition | Context | Writes |
|------|-----------|---------|--------|
| Arbiter | `agents/arbiter.md` | All reviews + artifact + conventions | `review/arbiter/` |
| Investigator | `agents/investigator.md` | Review output + origin phase | `REGRESSION_TICKET.md` |
| Typesetter | `agents/typesetter.md` | LaTeX + figures only | `outputs/ANALYSIS_NOTE.{tex,pdf}` |

### Review panel composition

| Review tier | Parallel agents | Sequential |
|-------------|----------------|------------|
| 4-bot | physics + critical + constructive + plot validator | arbiter |
| 5-bot | physics + critical + constructive + plot validator + rendering | arbiter |
| 1-bot | critical + plot validator | (check findings directly) |
