## Session Logs

Every agent session produces a `session.log`. Not read by other agents
(artifacts are the interface), but serves as audit trail for debugging and
reproducibility.

## RAG Integration

Available to all sessions as a tool call. Agents query as needed, cite
sources in artifacts. Failed retrievals logged in experiment log (see
methodology §2.2).

## Mapping to Claude Code Agent Teams

### Team Structure

The **lead agent** is the orchestrator — spawns teammates, manages
dependencies, handles gates. Does not do analysis work.

Per phase (3-bot example):
```
Lead (orchestrator, opus)
  ├── Executor      (sonnet for phases 2-4, opus for phase 1)
  ├── Critical Rev  (opus)
  ├── Constructive Rev (opus)
  └── Arbiter       (opus)
```

For 1-bot phases, the lead spawns only Executor + Critical Rev.
For self-review phases, only Executor.

### Isolation Guarantees

- Each teammate has its **own context window**
- Communication via **shared files only**
- Critical and constructive reviewers cannot see each other's work
- The experiment log is the only shared mutable state within a phase

### Configuration

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  },
  "mcpServers": {
    "scitreerag": {
      "command": "...",
      "args": ["--corpus", "path/to/experiment/corpus"]
    }
  }
}
```

### Cost Estimates (with tiering)

| Phase | Sessions (no iteration) | Model mix (auto mode) | Relative cost |
|-------|------------------------|-----------------------|---------------|
| Phase 1 | 4 (exec + 3-bot) | 1 opus exec + 3 opus review | ████████ |
| Phase 2 | 1 (exec, self-review) | 1 sonnet | █ |
| Phase 3 | 4-6 (exec per channel + 1-bot per channel + consolidate) | sonnet | ██ |
| Calibrations | 2-3 | sonnet | █ |
| Phase 4a | 4 | 1 sonnet exec + 3 opus review | ███████ |
| Phase 4b | 4 | 1 sonnet exec + 3 opus review | ███████ |
| Phase 4c | 2 | sonnet | █ |
| Phase 5 | 4 | 1 sonnet exec + 3 opus review | ███████ |
| **Total** | **~26-30** | | |

With `auto` tiering, opus is used for strategy execution (Phase 1) and all
3-bot review sessions (critical, constructive, arbiter). Sonnet handles all
other execution and 1-bot reviews. The `uniform_high` switch runs everything
on opus for benchmarking quality differences. The `uniform_mid` switch runs
everything on sonnet for budget-constrained analyses.

## Adapting to Other Agent Systems

Requirements:
- Isolated agent sessions with file read/write and code execution
- RAG corpus accessible as a tool
- Parallel execution support
- Model selection per session (for tiering)
- Mechanism to pause for human review
- Git integration

The methodology spec is portable; this orchestration doc is the Claude Code
adapter.
