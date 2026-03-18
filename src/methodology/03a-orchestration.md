## 3a. Orchestration and Agent Architecture

---

### 3a.1 Orchestrator Architecture

The orchestrator is a **thin coordinator** — it spawns subagents, reads
summaries, makes phase-transition decisions, and commits. It never writes
analysis code, produces figures, or debugs. Subagent contexts are discarded
after each phase; the orchestrator stays small.

**The orchestrator loop** is EXECUTE → REVIEW → CHECK → COMMIT → ADVANCE.
The canonical loop (with human gates, anti-patterns) lives in
`templates/root_claude.md` (auto-loaded at runtime). This section provides
architectural rationale; the template provides operational instructions.

**Review is always by subagent.** Self-review is not acceptable except for
Phase 2. All other phases require independent reviewer agents.

**Anti-patterns:** Skipping phases. Writing code as orchestrator. Accepting
weak reviews to save tokens. Spawning subagents without `model: "opus"`.

**Binding commitment tracking.** The orchestrator must maintain awareness
of all "Will implement" commitments from the Phase 1 strategy. At each
phase gate, verify that all commitments scheduled for that phase have
been fulfilled. Unfulfilled binding commitments are Category A at review
regardless of whether the reviewer catches them — the orchestrator is
the last line of defense. When a commitment is deferred (e.g., generator
comparison moved from Phase 4a to 4b), the deferral must be explicitly
documented with justification and a hard deadline. Commitments cannot be
deferred indefinitely.

---

### 3a.2 Subagent Roles and Context

Subagents are **executors** or **reviewers**. Each receives curated context
(§3a.4). See `appendix-prompts.md` for literal prompt templates.

**Executors** receive phase CLAUDE.md, upstream artifacts, experiment log,
conventions. They work plan-then-code: `plan.md` first, then scripts/figures,
artifact last.

**Reviewers:**

| Role | Context | Goal |
|------|---------|------|
| Physics reviewer | Physics prompt + artifact only | "Would I approve this for publication?" |
| Critical reviewer | Full context + conventions + RAG corpus | Find all flaws in correctness and completeness |
| Constructive reviewer | Same as critical (including RAG) | Strengthen: clarity, validation, presentation |
| Arbiter | All reviews + artifact + conventions | PASS / ITERATE / ESCALATE |

**Reviewer RAG access.** Critical and constructive reviewers have access
to the experiment corpus (MCP tools). They should query it to verify claims,
check how reference analyses handled similar concerns, and identify
published standards. When a reviewer encounters a questionable approach
(e.g., a flat systematic estimate, a novel validation criterion), they
should search for how this was handled in published analyses before
accepting or rejecting it.

**4-bot review:** first three in parallel, then arbiter. See §6.2–6.4 for
the full protocol. The bar is high: ITERATE liberally.

---

### 3a.3 Health Monitoring

- **Commit before spawning** each subagent (checkpoint).
- **Respawn stalled agents** — no commit in >10 min and no progress → terminate, respawn from last commit.
- **Context splitting** for Phase 4b/5: separate subagents for statistical analysis and AN writing.

---

### 3a.4 Context Management

**Artifacts are the only handoff.** No conversation history, no shared
variables. Each session starts from artifacts + instructions.

**Three context layers per agent:**

1. **Bird's-eye framing (~1 page):** physics prompt, analysis type, current
   phase, applicable conventions, end goal (publication-quality AN).
2. **Relevant methodology sections (~2-5 pages):**

| Role | Sections |
|------|----------|
| Phase 1 executor | §1, §2, §3 (Phase 1), §5, §7 |
| Phase 2 executor | §3 (Phase 2), §5, §7, Appendix D |
| Phase 3 executor | §3 (Phase 3), §5, §7, §11, Appendix D |
| Phase 4 executor | §3 (Phase 4), §4, §5, §7, §11, Appendix D |
| Phase 5 executor | §3 (Phase 5), §5, Appendix D |
| 4/5-bot reviewer | §6, applicable phase from §3, conventions, checklist |
| 1-bot reviewer | §6, applicable phase from §3, conventions |
| Arbiter | §6, conventions |

3. **Upstream artifacts (~2-10 pages):** prior phase artifacts + experiment
   log if continuing within a phase.

**Context budget:** ~20-30 pages max at Phase 5. Summarize artifacts
exceeding ~5 pages. Experiment log consulted on demand, not loaded in full.

**Artifacts before speed.** When context pressure mounts, write the current
artifact and stop cleanly. Never skip an artifact to "save context."

---

### 3a.5 Parallelism and Sub-delegation

- **Within a phase:** parallel sub-agents writing to separate directories,
  consolidated before review.
- **Across phases:** sequential (Phase N reads Phase N-1 artifact).
- **Per-channel:** channel-specific work in Phases 2-3 can run in parallel.

**Sub-delegation within a phase:** Delegate compute-heavy tasks (MVA
training, systematic evaluation, plot generation, closure tests) to
sub-agents. The executor coordinates and integrates. Sub-agents handle
execution; the executor retains judgment (which backgrounds, whether
closure tests pass).

---
