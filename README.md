# slopspec

A specification for LLM-driven High Energy Physics (HEP) collider analyses.

The idea: give an LLM agent a physics question, a data sample, and this spec — it runs the analysis end-to-end, from strategy through statistical inference to a draft analysis note. No bespoke framework, just prose guidelines that agents interpret using standard scikit-hep tooling.

## What's in here

- **[methodology.md](methodology.md)** — The analysis methodology. Five phases (Strategy, Exploration, Selection & Modeling, Inference, Documentation), blinding protocol, review tiers, calibration guidance, and the preferred tool stack.
- **[orchestration.md](orchestration.md)** — How to actually run it. Session management, agent identity, artifact handoffs, cost controls, and automation pseudocode for multi-session execution.

## Design philosophy

- **Prose over code.** Agents interpret guidelines, not execute scripts. Pseudocode is illustrative.
- **Artifacts over memory.** Each phase produces a self-contained markdown report. No shared conversation history between phases — the artifact is the interface.
- **Standard tools.** uproot, awkward-array, hist, coffea, pyhf, mplhep — the scikit-hep ecosystem. No custom frameworks.
- **Tiered review.** 3-bot review for critical gates, 1-bot for routine phases, self-review for mechanical tasks.
- **Blinding by default.** Asimov-only until the agent gate passes, then staged unblinding (10% data, then full) with a human gate before the final step.

## Status

First draft. Tested against ALEPH/LEP data with modern tooling. Expect rough edges.
