# Methodology Specification

## Structure

The spec is organized into three tiers:

### Tier 1: Core physics analysis — "what to do"
- `03-phases.md` — Phase 1–5 definitions (requirements, deliverables, gates)
- `04-blinding.md` — Staged unblinding protocol
- `09-multichannel.md` — Multi-channel analysis guidance

### Tier 2: Process and scaffolding — "how to manage it"
- `01-principles.md` — Scope and design principles
- `02-inputs.md` — Physics prompt, RAG retrieval
- `03a-orchestration.md` — Orchestrator loop, subagent management, context, scaling
- `05-artifacts.md` — Artifact format and experiment log
- `06-review.md` — Review protocol (classification, iteration, per-phase focus)
- `12-downscoping.md` — Scope management and feasibility

### Tier 3: Craft — "how to write good code, notes, and plots"
- `07-tools.md` — Tool preferences, paradigms, scale-out patterns
- `11-coding.md` — Git, code quality, testing, pixi tasks
- `appendix-plotting.md` — Figure template, sizing, labels, styling
- `appendix-heuristics.md` — Tool idioms (agent-maintained)

### Appendices — reference material
- `analysis-note.md` — Analysis note specification (required sections, depth, bibliography)
- `appendix-dependencies.md` — Phase dependency graph
- `appendix-checklist.md` — Per-phase artifact checklists

### Appendices — operational (agent execution)
- `appendix-prompts.md` — Literal prompt templates for each agent role
- `appendix-automation.md` — Orchestration pseudocode (review tiers, pipeline flow)
- `appendix-sessions.md` — Session naming, directory layout, isolation model
- `appendix-integration.md` — RAG/MCP setup, Claude Code team mapping (platform-specific)

## Reading guide

- **For a new analysis:** Read Tier 1 (phases, blinding) to understand what each phase does
- **For orchestration:** Read §3a for the architecture, then appendix-prompts/automation/sessions for operational details
- **For coding:** Read Tier 3 for tool choices, code style, and plotting rules
- **Templates** (`src/templates/`) are thin entry points pointing to these files
