## 8. Context Management

### 8.1 Artifacts as Handoffs

The only information that crosses phase boundaries is the written artifact. No
conversation history, no shared variables, no implicit state. Each agent session
starts from artifacts and instructions, not from prior conversations.

### 8.2 What Each Agent Receives

Every agent — executor, reviewer, arbiter — receives a curated context
assembled by the orchestrating agent or the human launching the session. The
context has three layers:

**Layer 1: Bird's-eye framing (~1 page).** All agents receive this. It
provides the analysis-level context that prevents agents from losing sight of
the end goal:

- The physics prompt (what we're measuring/searching for)
- The analysis type (measurement or search) and technique
- The current phase and what it must deliver
- The applicable conventions (by reference: "read `conventions/unfolding.md`")
- The end goal: a publication-quality analysis note suitable for journal
  submission. Every phase contributes to this goal.

This framing is critical. Without it, agents optimize for local phase
completion rather than the overall analysis quality. A reviewer who knows the
result will be submitted to a journal applies a higher standard than one who
thinks it's an internal exercise.

**Layer 2: Relevant methodology sections (~2-5 pages).** The orchestrating
agent selects which methodology sections each agent needs. Not every agent
reads the full spec — that would waste context on irrelevant material. The
selection depends on the role:

| Role | Methodology sections |
|------|---------------------|
| Phase 1 executor | Sections 1, 2, 3 (Phase 1), 5, 7 |
| Phase 2 executor | Sections 3 (Phase 2), 5, 7 |
| Phase 3 executor | Sections 3 (Phase 3), 5, 7, 11 |
| Phase 4 executor | Sections 3 (Phase 4), 4, 5, 7, 11 |
| Phase 5 executor | Sections 3 (Phase 5), 5 |
| 3-bot reviewer | Sections 6, applicable phase from 3, applicable conventions, appendix checklist |
| 1-bot reviewer | Section 6, applicable phase from 3, applicable conventions |
| Arbiter | Section 6, applicable conventions |
| Plot subagent | Appendix D (Plotting Template) |

The CLAUDE.md files (project-root and per-phase) are always loaded
automatically by Claude Code. These provide the essential rules (tool
requirements, pixi, coding standards) without needing to load the full
methodology.

**Layer 3: Upstream artifacts (~2-10 pages per phase).** The phase's input
artifacts from prior phases, plus the experiment log if continuing a session
within a phase.

### 8.3 Context Budget

Even at Phase 5, the total curated input should be bounded at ~20-30 pages.
The orchestrating agent is responsible for keeping context lean:

- Include only relevant methodology sections, not the full spec
- Summarize long upstream artifacts if they exceed ~5 pages
- The experiment log is consulted on demand, not loaded in full

### 8.4 What Goes Where

- **Artifact:** Decisions, results, reasoning, key figures (by path),
  validation outcomes. Everything a reader needs to evaluate the analysis.
- **Scripts directory:** Code that produced the results. Referenced from the
  artifact for reproducibility, but not read by downstream phases.
- **Supplementary files:** Full tables, workspaces, trained models. Referenced
  from the artifact, consulted only when needed.

### 8.5 Artifacts Before Speed

When context pressure mounts (approaching context limits, long session),
the agent must prioritize writing the current phase's artifact over rushing
to start the next phase. A completed Phase 3 with a written `SELECTION.md`
artifact is far more valuable than a half-finished Phase 4 with no
intermediate artifacts.

- The artifact is the checkpoint. Code on disk without a written artifact is
  recoverable but expensive — the next session must re-derive the reasoning.
- **Never skip an artifact to "save context."** Writing an artifact costs
  fewer tokens than re-doing the work it documents.
- If the session must stop, commit the current phase's work (artifact +
  scripts + experiment log) and stop cleanly. The next session reads the
  artifacts and resumes.

---
