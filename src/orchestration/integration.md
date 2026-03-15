## Session Logs

Every agent session produces a `session.log`. Not read by other agents
(artifacts are the interface), but serves as audit trail for debugging and
reproducibility.

## RAG Integration

The SciTreeRAG corpus (slopcorpus) is available to all agent sessions via MCP.
The server lazy-loads its index on first tool call; subsequent calls within the
same session are fast. See `.mcp.json` for the concrete server definition.

**Usage expectations:**
- All sessions have the MCP tools available — no per-session setup needed
- Agents query as needed and cite sources in artifacts (paper ID + section)
- Failed retrievals are logged in `retrieval_log.md` per phase (see
  methodology §2.2)
- Prefer `search_lep_corpus` with `mode="hybrid"` (default) for most queries
- Use `compare_measurements` when the analysis needs to cross-check ALEPH vs
  DELPHI results on the same observable
- Use `get_paper` to drill into a specific reference found via search

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
    "lep-corpus": {
      "type": "stdio",
      "command": "pixi",
      "args": ["run", "--manifest-path", "/path/to/slopcorpus/pixi.toml",
               "python", "mcp_servers/rag_server.py"],
      "cwd": "/path/to/slopcorpus",
      "env": { "RAG_MODEL": "small" }
    }
  }
}
```

The `lep-corpus` MCP server exposes four tools:

| Tool | Purpose |
|------|---------|
| `search_lep_corpus(query, top_k, experiment, mode)` | Hybrid (dense + BM25) retrieval over ~2,400 ALEPH/DELPHI papers; returns ranked passages with metadata |
| `get_paper(paper_id)` | Look up a specific paper by arXiv, INSPIRE, or CDS ID |
| `list_corpus_papers(experiment, category, limit)` | Browse corpus with optional experiment/category filters |
| `compare_measurements(topic, top_k_per_experiment)` | Side-by-side ALEPH vs DELPHI retrieval for cross-checking |

Agents should prefer `search_lep_corpus` for general queries and
`compare_measurements` when cross-checking results between experiments.
Use `get_paper` to drill into a specific reference. All retrieved passages
include source paper ID and similarity score — cite these in artifacts.

### Cost Estimates (with tiering)

**Search flow** (full blinding protocol):

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

**Measurement flow** (no blinding — skip 4b/4c):

| Phase | Sessions (no iteration) | Model mix (auto mode) | Relative cost |
|-------|------------------------|-----------------------|---------------|
| Phases 1-3, calibrations | same as above | | |
| Phase 4a | 4 | 1 sonnet exec + 3 opus review | ███████ |
| Phase 5 | 4 | 1 sonnet exec + 3 opus review | ███████ |
| **Total** | **~20-24** | | |

With `auto` tiering, opus is used for strategy execution (Phase 1) and all
3-bot review sessions (critical, constructive, arbiter). Sonnet handles all
other execution and 1-bot reviews.

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
