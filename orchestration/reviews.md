## Git Integration

All work is tracked in git with conventional commits (see methodology §11.1).

**Branch strategy:**
```
main                           # Always reflects reviewed, passed work
├── phase1_strategy            # Merged after arbiter PASS
├── phase2_exploration         # Merged after self-review complete
├── phase3_selection           # Merged after 1-bot review PASS
├── phase4a_expected           # Merged after 3-bot PASS
├── phase4b_partial            # Merged after 3-bot PASS + human approval
├── phase4c_observed           # Merged after 1-bot review
└── phase5_documentation       # Merged after 3-bot PASS (final)
```

Agents commit frequently within their branch. Each commit is a checkpoint.
If an agent session crashes mid-phase, the next session picks up from the
last commit on the branch.

## Review Tiers

The review structure varies by phase (see methodology §6.2):

```
Phase 1:  Executor → [Critical + Constructive] → Arbiter  (3-bot)
Phase 2:  Executor (self-review)                           (self)
Phase 3:  Executor → Critical                              (1-bot)
Phase 4a: Executor → [Critical + Constructive] → Arbiter  (3-bot, agent gate)
Phase 4b: Executor → [Critical + Constructive] → Arbiter  (3-bot, → human)
Phase 4c: Executor → Critical                              (1-bot)
Phase 5:  Executor → [Critical + Constructive] → Arbiter  (3-bot)
```

## Model Tiering

See methodology §6.7 for the policy rationale. The operational config:

```yaml
# analysis_config.yaml (or equivalent)
model_tier: auto  # auto | uniform_high | uniform_mid

# When model_tier: auto, the orchestrator uses:
tiers:
  executor_strategy: opus      # Phase 1 — physics reasoning
  executor_default: sonnet     # Phases 2-4 — code iteration, I/O plumbing, fits
  reviewer_3bot: opus          # All 3-bot reviews (critical, constructive, arbiter)
  reviewer_1bot: sonnet        # Single critical reviewer
  arbiter: opus                # All arbiters
  investigator: opus           # Regression investigation
  calibration: sonnet          # Shared sub-analyses
  plot_generation: haiku       # Mechanical plot tasks
  smoke_tests: haiku           # Test execution
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
- Normal termination: arbiter PASS (3-bot) or no Category A issues (1-bot)

**Execution budget:** Configurable per-phase (tokens or iterations).
When approached, the agent produces best-effort artifact with open issues.

**Total budget:** Orchestrator tracks cumulative cost. Pauses for human
review if threshold exceeded.

```yaml
cost_controls:
  max_review_iterations: 10      # Hard cap on review cycles (prevents infinite loops)
  review_warn_threshold: 3       # Soft warn after this many iterations
  review_strong_warn_threshold: 5 # Strongly warn
  phase2_max_iterations: 20
  phase3_max_iterations: 30
  total_budget_warn: 500000  # tokens, or dollar amount
  on_budget_exceeded: pause  # pause | warn_and_continue
```
