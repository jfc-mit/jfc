# slopspec

A specification for LLM-driven High Energy Physics (HEP) collider analyses.

Give an LLM agent a physics question, a data sample, and this spec — it runs
the analysis end-to-end, from strategy through statistical inference to a
draft analysis note. No bespoke framework, just prose guidelines that agents
interpret using standard scikit-hep tooling.

## Key concepts

**Phases.** The analysis proceeds through 5 phases: Strategy, Exploration,
Selection, Inference (with staged unblinding), and Documentation. Each phase
produces a self-contained artifact. No shared conversation history — the
artifact is the interface between phases.

**Review.** Every phase is reviewed before proceeding. Critical gates (strategy,
pre-unblinding, documentation) get a 3-agent review: a critic, an advocate,
and an arbiter. Lighter phases get a single reviewer or self-review. Reviewers
are told to think like journal referees — checking both correctness (is what's
here right?) and completeness (is anything missing?).

**Conventions.** Domain knowledge about specific analysis techniques lives in
`conventions/`. These are living documents maintained across analyses — what
systematics are standard for unfolded measurements, what validation is
required before building a response matrix, what pitfalls to avoid. The spec
says *what* must happen; conventions say *how* it's typically done right.

**CLAUDE.md.** Non-negotiable rules (required tools, coding practices, review
expectations) loaded into every agent session automatically.

## Repository structure

```
methodology/              # The spec (source of truth, split by section)
  01-principles.md          Scope and design principles
  02-inputs.md              Physics prompt + RAG corpus
  03-phases.md              Phases 1-5 (Strategy -> Documentation)
  04-blinding.md            Blinding protocol + staged unblinding
  05-artifacts.md           Artifact format (logs, reports, feedback)
  06-review.md              Review protocol (framing, focus, completeness checks)
  07-tools.md               Preferred tool stack + paradigms
  08-context.md             Context management across phases
  09-multichannel.md        Multi-channel analysis handling
  10-scaling.md             Scaling to multiple agents
  11-coding.md              Version control and coding practices
  12-downscoping.md         Scope management + future directions
  appendix-*.md             Dependency graph, checklists, tool heuristics

orchestration/            # How to run it (session management, automation)

conventions/              # Domain knowledge per analysis technique
  README.md                 Role and maintenance model
  unfolding.md              Unfolded measurements (systematics, validation, pitfalls)

analyses/                 # Actual analyses run with this spec

CLAUDE.md                 # Always-loaded rules for every agent session
build_spec.py             # Concatenates split files -> methodology.md, etc.
pyproject.toml            # pixi + dependencies
```

`pixi run build` concatenates the split files into `methodology.md`,
`orchestration.md`, and `conventions.md` for agent consumption.

## Design principles

- **Prose over code.** Agents interpret guidelines, not execute templates.
- **Artifacts over memory.** Each phase reads upstream reports, not prior
  conversations.
- **Standard tools.** uproot, awkward-array, hist, coffea, pyhf, mplhep —
  the scikit-hep ecosystem. No custom frameworks.
- **Conventions over silence.** Accumulated domain knowledge is written down
  in `conventions/`, not assumed. Agents consult conventions; reviewers check
  against them.
- **Completeness over consistency.** Internal consistency (closure tests pass)
  is necessary but not sufficient. Reviews also check external completeness
  (are we doing what the field considers standard?).
- **Blinding by default.** Asimov-only until the agent gate passes, then
  staged unblinding (10% data, then full) with a human gate before the
  final step.
- **Downscope, don't block.** Missing resources? Use a simpler method,
  document the limitation, flag it for future work.

## Status

Tested against ALEPH/LEP archived data (thrust measurement). Conventions
and review protocol updated based on post-mortem comparison with an
independent analysis of the same data. Expect continued evolution.
