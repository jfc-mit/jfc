# slopspec

A specification for LLM-driven High Energy Physics (HEP) collider analyses.

The idea: give an LLM agent a physics question, a data sample, and this spec — it runs the analysis end-to-end, from strategy through statistical inference to a draft analysis note. No bespoke framework, just prose guidelines that agents interpret using standard scikit-hep tooling.

## What's in here

```
spec/
  methodology/          # The analysis methodology (split by section)
    01-principles.md      Scope and design principles
    02-inputs.md          Physics prompt + RAG corpus
    03-phases.md          Phases 1-5 (Strategy → Documentation)
    04-blinding.md        Blinding protocol + staged unblinding
    05-artifacts.md       Artifact format (logs, reports, feedback)
    06-review.md          Review protocol (3-bot, 1-bot, self)
    07-tools.md           Preferred tool stack + paradigms
    08-context.md         Context management across phases
    09-multichannel.md    Multi-channel analysis handling
    10-scaling.md         Scaling to multiple agents
    11-coding.md          Version control and coding practices
    12-downscoping.md     Scope management + future directions
    appendix-*.md         Dependency graph, checklists, tool heuristics
  orchestration/        # How to run it (split by concern)
    sessions.md           Session isolation, identity, directory layout
    reviews.md            Review tiers, model tiering, cost controls
    regression.md         Phase regression protocol
    agents.md             Agent session definitions
    automation.md         Automation pseudocode
    integration.md        RAG, git, Claude Code mapping
  orchestrator/         # Python implementation (Claude Agent SDK)
    main.py               CLI entry point
    pipeline.py           Full phase 1-5 pipeline
    review.py             3-bot and 1-bot review loops
    sessions.py           Agent session runner
    prompts.py            Prompt construction per role
    config.py             YAML config loading
    names.py              Session naming pool
    artifacts.py          File discovery + decision extraction
    example_config.yaml   Example analysis config
  build_spec.py         # Concatenates split files → methodology.md / orchestration.md
  pyproject.toml        # pixi + dependencies
```

The split files under `methodology/` and `orchestration/` are the source of truth. `pixi run build` concatenates them into single `methodology.md` and `orchestration.md` files that the orchestrator feeds to agents as system prompts.

## Quickstart

```bash
# Install pixi if you don't have it
curl -fsSL https://pixi.sh/install.sh | bash

# Set up environment
pixi install

# Set your API key
export ANTHROPIC_API_KEY=your-key

# Dry run — check config without launching agents
pixi run gad --dry-run orchestrator/example_config.yaml

# Run the pipeline
pixi run gad orchestrator/example_config.yaml
```

## Design philosophy

- **Prose over code.** Agents interpret guidelines, not execute scripts. Pseudocode is illustrative.
- **Artifacts over memory.** Each phase produces a self-contained markdown report. No shared conversation history between phases — the artifact is the interface.
- **Standard tools.** uproot, awkward-array, hist, coffea, pyhf, mplhep — the scikit-hep ecosystem. No custom frameworks.
- **Tiered review.** 3-bot review for critical gates, 1-bot for routine phases, self-review for mechanical tasks.
- **Blinding by default.** Asimov-only until the agent gate passes, then staged unblinding (10% data, then full) with a human gate before the final step.
- **Downscope, don't block.** Missing resources? Use a simpler method, document the limitation, flag it for future work.

## Status

First draft. Tested against ALEPH/LEP data with modern tooling. Expect rough edges.
