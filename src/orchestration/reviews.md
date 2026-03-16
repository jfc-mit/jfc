## Git Integration

All work is tracked in git with conventional commits (see methodology §11.1).

**Branch strategy:**
```
main                           # Always reflects reviewed, passed work
├── phase1_strategy            # Merged after arbiter PASS
├── phase2_exploration         # Merged after self-review complete
├── phase3_selection           # Merged after 1-bot review PASS
├── phase4a_expected           # Merged after 4-bot PASS
├── phase4b_partial            # Merged after 4-bot PASS + human approval
├── phase4c_observed           # Merged after 1-bot review
└── phase5_documentation       # Merged after 5-bot PASS (final)
```

Agents commit frequently within their branch. Each commit is a checkpoint.
If an agent session crashes mid-phase, the next session picks up from the
last commit on the branch.

## Review Tiers

The review structure varies by phase (see methodology §6.2):

```
Phase 1:  Executor → [Physics + Critical + Constructive] → Arbiter  (4-bot)
Phase 2:  Executor (self-review)                                     (self)
Phase 3:  Executor → Critical                                        (1-bot)
Phase 4a: Executor → [Physics + Critical + Constructive] → Arbiter  (4-bot)
Phase 4b: Executor → [Physics + Critical + Constructive] → Arbiter  (4-bot, → human)
Phase 4c: Executor → Critical                                        (1-bot)
Phase 5:  Executor → [Physics + Critical + Constructive + Rendering] → Arbiter  (5-bot)
```

## Cost Controls

**Review iteration limits:** Correctness (arbiter PASS or no Category A
issues) is the intended termination condition for review cycles. Warnings
at 3 and 5 iterations flag potential problems. A hard cap
(`max_review_iterations`, default 10) prevents infinite loops if the
review cycle is pathologically stuck — hitting this cap forces escalation
to a human.

- After 3 iterations: orchestrator logs a warning
- After 5 iterations: orchestrator logs a strong warning
- At `max_review_iterations`: orchestrator forces human escalation
- Normal termination: arbiter PASS (4/5-bot) or no Category A issues (1-bot)

Methodology §6 is the canonical source for review iteration limits and
cost control policy. The values below must match.

```yaml
cost_controls:
  max_review_iterations: 10      # Hard cap on review cycles (prevents infinite loops)
  review_warn_threshold: 3       # Soft warn after this many iterations (4/5-bot)
  review_strong_warn_threshold: 5 # Strongly warn (4/5-bot)
  onebot_warn_threshold: 2       # Soft warn for 1-bot reviews
  onebot_escalate_threshold: 3   # Force human escalation for 1-bot reviews
```
