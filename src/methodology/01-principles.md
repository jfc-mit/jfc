# LLM-Driven HEP Analysis: Methodology Specification

## 1. Scope and Principles

This spec defines *what* each phase must produce, not *how*. The agent
selects tools, writes code, and makes physics judgments within these
constraints.

**Quality bar: publication-ready.** Every phase must meet the standard:
would a senior physicist on a review committee approve this? Not "good
enough to move on" — good enough to publish.

**Design principles:**
- **Artifacts over memory.** Each phase produces a self-contained report.
  Subsequent phases read reports, not conversation history.
- **Review at every level.** Plans, code, results, and writeup all reviewed.
- **The agent adapts.** Omitting an unnecessary step is correct; performing
  it without justification is not.
- **Conventions over encoded physics.** Operational knowledge in
  `conventions/`; agent consults at Phases 1, 4a, 5.
- **Downscope, don't block.** See §12.

