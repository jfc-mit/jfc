## 11. Version Control and Coding Practices

### 11.1 Git

**Conventional commits:** `<type>(phase): <description>`. Types: feat, fix,
data, plot, doc, refactor, test, chore.

**Commit after every meaningful step.** Commits are checkpoints — if the
agent crashes, resume from the last commit.

**Branch per phase** (`phase1_strategy`, etc.). Merge to main after review
passes.

### 11.2 Code Quality

- **KISS/YAGNI.** Scripts, not frameworks. No CLIs, config systems, plugins.
- **Columnar.** Arrays + masks, not event loops.
- **Logging, not printing.** `logging` + `rich.logging.RichHandler`. Ruff
  `T201` enforces no `print()`. Standard setup:

```python
import logging
from rich.logging import RichHandler
logging.basicConfig(level=logging.INFO, format="%(message)s",
                    handlers=[RichHandler(rich_tracebacks=True)])
log = logging.getLogger(__name__)
```

- **Ruff + pre-commit** for formatting and linting on every commit.

### 11.3 Testing

Focus on **structural bugs** (wrong branch, wrong weight, inverted cut) —
not unit test coverage. These are catastrophic because they require re-running
everything and produce plausible-looking wrong numbers.

**Always:** Smoke test per phase (~100 events, no crashes). Integration test
(output files exist, correct structure, no NaN).

**Check:** Variable names → right quantities. Cut inversions → correct
complement. Object efficiencies → consistent with published. Cutflow →
monotonically decreasing. Systematic variations → expected direction.
**Parallel outputs not identical.** If a parallel processing step
produces N independent results (e.g., per-file histograms, per-year
densities), verify they are not bit-for-bit identical. Identical
outputs from independent inputs indicate a fork/threading bug.

### 11.4 Task Graph

**Every script → pixi task.** `pixi run all` reproduces the full analysis
from raw data. Task names are human-readable. Scripts are idempotent (fixed
seeds, fixed output paths).

Split scripts exceeding ~5 min into stages with intermediate outputs.
Update `pixi.toml` whenever scripts are added or removed.

### 11.5 Debug Code

Prefix with `debug_` or place in `scratch/`. Never include in `all` task.
Clean up before review.

---
