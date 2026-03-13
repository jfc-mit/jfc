## 11. Version Control and Coding Practices

Analysis code is exploratory by nature, but it must be correct and
reproducible. The engineering bar is **"would this pass review from a physicist
colleague"** — not enterprise software standards.

### 11.1 Git Discipline

All analysis work is tracked in git. This serves as the checkpointing mechanism
within and across phases.

**Conventional commits.** Every commit uses a structured message format:

```
<type>(phase): <description>

Types:
  feat     — new analysis capability (selection, training, fit)
  fix      — bug fix in analysis code
  data     — data exploration, sample inventory
  plot     — figure generation or update
  doc      — artifact writing, note updates
  refactor — restructuring without changing results
  test     — adding or updating tests
  chore    — housekeeping (formatting, dependencies)
```

**Commit frequency:** After every meaningful step — completing a cut study,
producing a set of plots, finishing a closure test, updating the artifact.
Commits within a phase are the checkpoints; if the agent crashes at step 12 of
15, it can resume from the last commit.

**Branch strategy:** Each phase works on a branch (`phase1_strategy`,
`phase2_exploration`, etc.). The branch is merged to main when the phase's
review passes. This keeps main clean — it always reflects reviewed work.

### 11.2 Code Quality

**Formatting and linting:** Use `ruff` (or equivalent) with a pre-commit hook.
Every commit is automatically formatted and checked for common errors (undefined
variables, unused imports, shadowed names). This is cheap and catches real bugs.

**Code style:**
- **KISS.** Obvious numpy/awkward operations over clever metaprogramming. A
  physicist reading the code should be able to follow the analysis flow.
- **DRY.** If multiple channels share the same calibration logic, factor it out.
  But do not prematurely abstract for hypothetical future needs.
- **YAGNI.** Do not build CLIs, config systems, or plugin architectures. Write
  scripts. Refactor when (not before) reuse is actually needed.

**What NOT to do:**
- Do not write unit tests for every function
- Do not create mock data fixtures when real data is available
- Do not add type annotations to exploratory scripts
- Do not write docstrings for functions that run once
- Do not build frameworks when scripts work
- Do not use dependency injection, abstract base classes, or enterprise patterns

### 11.3 Testing

Testing effort should focus on **structural bugs** — errors in the plumbing
that silently propagate through everything downstream. A bug in the final fit
is cheap to fix (re-run the fit). But cutting on the wrong lepton pT branch,
reconstructing a nonsensical 4-lepton mass, or applying a weight meant for
signal to background — these are catastrophic because they require re-running
the entire analysis and are hard to track down (the numbers look plausible
but are wrong).

**Always:** One **smoke test** per phase — does the full pipeline run on ~100
events without crashing? This catches import errors, broken paths, shape
mismatches, and API changes. Fast to run, high value.

**Always:** One **integration test** for the processing chain — does it produce
output files with the expected structure? Not checking physics values — checking
that the machinery works (correct number of bins, files exist, no NaN yields).

**Focus on structural correctness:**
- Test that variable names map to the right physical quantities (is this
  actually lepton pT, not jet pT?)
- Test that cut inversions actually invert (CR selection is complement of SR)
- Test that object definitions produce yields consistent with published
  efficiencies (if the experiment says 99% tracking efficiency and you get 60%,
  something is structurally wrong)
- Test that systematic variations go in the expected direction
- Test that event counts are monotonically decreasing through the cutflow
  (if a cut increases yield, something is wrong)

These structural tests are cheap to write and catch the bugs that are most
expensive to debug later.

**Never:** Full test suites, 100% coverage targets, TDD. The analysis result
is the product, not the code. The physics validation (closure tests, signal
injection, post-fit diagnostics) IS the test suite for correctness.

### 11.4 Code Reuse Across Analyses

Analysis code written for one analysis is a valuable resource for subsequent
analyses — not as a framework to import, but as working examples to consult.

**Within an analysis:** Reusable patterns emerge naturally (data loading,
standard plots, workspace building). When a pattern is used 3+ times, factor
it into a shared utility in the analysis's `scripts/common/` directory. Do not
anticipate reuse — wait until it happens.

**Across analyses:** A **snippets library** (`snippets/`) provides tested,
documented code patterns for common HEP operations. These are not a framework
— they are copy-and-adapt starting points. The agent consults the snippets
library when beginning a task and adapts relevant patterns to the current
analysis. Prior analysis directories are also a resource: "consult
`../prior_analysis/` for patterns that worked in a similar context."

The snippets library grows organically. After completing an analysis, useful
patterns are extracted and added. This is YAGNI in practice — code is
generalized only after it has proven useful in a real analysis, not before.

### 11.5 Pre-commit Configuration

A minimal `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

This is installed once and runs automatically on every commit. No agent
attention required after setup.

---
