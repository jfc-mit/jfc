## Appendix A: Phase Dependency Graph

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

---
