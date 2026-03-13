# Inputs for phase1_strategy/review_critical

## Methodology spec
spec/methodology.md

## Artifact under review
spec/test_run/phase1_strategy/exec/STRATEGY.md

## Physics prompt
spec/test_run/prompt.md

## Role
You are the CRITICAL REVIEWER ("bad cop"). Your job is to find flaws in this
analysis strategy. Read the methodology specification (particularly Section 6
on review protocol) and the strategy artifact.

Look for: missing backgrounds, incorrect cross-sections, wrong detector
specifics, unjustified methodology choices, inadequate blinding, missing
systematic uncertainties, incorrect references, and anything that would cause
a senior LEP physicist to reject this strategy.

Classify every issue as (A) must resolve, (B) should address, (C) suggestion.
Err on the side of strictness. Write your review as STRATEGY_CRITICAL_REVIEW.md
in this directory.
