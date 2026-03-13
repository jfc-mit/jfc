# Inputs for phase1_strategy/arbiter

## Methodology spec
spec/methodology.md

## Artifact under review
spec/test_run/phase1_strategy/exec/STRATEGY.md

## Reviews
spec/test_run/phase1_strategy/review_critical/STRATEGY_CRITICAL_REVIEW.md
spec/test_run/phase1_strategy/review_constructive/STRATEGY_CONSTRUCTIVE_REVIEW.md

## Physics prompt
spec/test_run/prompt.md

## Role
You are the ARBITER. Read the strategy artifact and both reviews. For each
issue raised:
- If both reviewers agree: accept the classification
- If they disagree: make your own assessment with justification
- If an issue was missed by both: raise it yourself

Produce STRATEGY_ARBITER.md in this directory with a consolidated review.
End with a clear decision: PASS, ITERATE (list Category A items to fix),
or ESCALATE (issues requiring human input).
