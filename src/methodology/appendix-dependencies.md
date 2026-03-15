## Appendix A: Phase Dependency Graph

### Search flow (full blinding protocol)

```
                         Experiment Corpus
                              (RAG)
                                │
                                │  queried throughout
                                ▼
Physics Prompt ──────► Phase 1: Strategy ◄──────────────────────┐
                                │                               │
                                ▼                               │
                       Phase 2: Exploration ◄───────────────┐   │
                                │                           │   │
                     ┌──────────┼──────────┐                │   │
                     │     (per channel)   │                │   │
                     ▼                     ▼                │   │
                  Phase 3a            Phase 3b ...          │   │
                  Channel A           Channel B             │   │
                     │                     │                │   │
                     └──────────┬──────────┘         phase regression
                                │                    (if fundamental
                                ▼                     issue found)
                       Phase 4a: Expected Results           │   │
                                │                           │   │
                        ★ AGENT GATE ★ (3-bot) ─────────────┘   │
                                │                               │
                       Phase 4b: Partial Unblinding (10%)       │
                                │                               │
                        ★ 3-BOT REVIEW ★ ──────────────────────┘
                                │
                        ★ HUMAN GATE ★
                        (draft note + 10% results → human)
                                │
                       Phase 4c: Full Unblinding
                                │
                                ▼
                       Phase 5: Documentation
```

### Measurement flow (no blinding)

```
Physics Prompt ──────► Phase 1: Strategy
                                │
                                ▼
                       Phase 2: Exploration
                                │
                                ▼
                       Phase 3: Selection & Correction
                                │
                                ▼
                       Phase 4a: Inference + Systematics
                                │
                        ★ AGENT GATE ★ (3-bot)
                                │
                        ★ HUMAN GATE ★
                        (result + draft note → human)
                                │
                                ▼
                       Phase 5: Documentation
```

Measurements skip Phases 4b/4c — the result is visible throughout and
there is nothing to unblind. The 3-bot review and human gate still apply
at Phase 4a. See §3 (Phase 4) for details.

---
