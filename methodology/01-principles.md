# LLM-Driven HEP Analysis: A Minimal Methodology Specification

## 1. Scope and Principles

This document specifies a methodology for conducting a complete High Energy
Physics (HEP) collider analysis using LLM-based agents. The specification is
intentionally minimal: it defines *what* must happen and *what* each phase must
produce, not *how* the agent should implement it. The agent selects tools,
writes code, and makes physics judgments within the constraints described here.

**Design principles:**

- **Prose over code.** The methodology is expressed in natural language. No
  bespoke library is required — agents use standard, community-maintained HEP
  software directly.
- **Artifacts over memory.** Each phase produces a self-contained written
  report. Subsequent phases read these reports, not prior conversation history.
  This bounds context consumption and makes the analysis auditable.
- **Review at every level.** Plans are reviewed before execution. Code is
  reviewed before results are trusted. Results are reviewed before they are
  written up. The final writeup is reviewed before the analysis is considered
  complete. Review artifacts are first-class outputs.
- **The agent adapts to the analysis.** Not every analysis needs multivariate
  techniques, multiple signal regions, or data-driven background estimates. The
  agent evaluates what is appropriate and documents its reasoning. Omitting an
  unnecessary step is correct; performing it without justification is not.
- **No encoded physics.** This specification describes methodology, not physics.
  The agent derives its physics approach from the literature (via retrieval from
  the experiment's publication corpus) and first principles, not from templates
  or recipes. HEP is an evolving field; hardcoded physics guidance goes stale.
- **Cost-aware execution.** Not every task requires the most capable model.
  The orchestrator assigns model tiers based on task complexity (see Section
  6.6). This is configurable — a top-level switch controls whether to use
  tiered models or a uniform model (useful for benchmarking).
- **Downscope, don't block.** When a resource is unavailable (missing MC,
  insufficient statistics, inaccessible data, no GPU for large training),
  the agent downscopes to what is achievable now and documents what would
  improve the result with more resources. A complete analysis with a simpler
  method beats an incomplete analysis waiting for the ideal method. This is
  standard scientific practice — see Section 12.

