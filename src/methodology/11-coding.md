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
- **`__file__`-relative output paths.** Scripts must resolve output paths
  relative to the script file, not the current working directory:
  ```python
  HERE = Path(__file__).resolve().parent
  OUT = HERE.parent / "outputs"
  FIG = OUT / "figures"
  ```
  This ensures `pixi run py path/to/script.py` produces the same output
  regardless of the shell's CWD. CWD-relative paths like
  `Path("phase4_inference/outputs/figures")` break when the script is
  invoked from a different directory.
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

### 11.4 Separation of Analysis and Plotting

**Analysis code and plotting code must be independent.** Analysis scripts
produce machine-readable artifacts (JSON, NPZ, CSV) — histograms, yields,
fit results, systematic shifts. Plotting scripts read those artifacts and
produce figures. The two must never be entangled in the same script.

This separation provides three benefits:
1. **Plots are rerunnable.** Tweaking a legend, axis range, or color does
   not require re-running the analysis chain. `pixi run plot-X` regenerates
   the figure in seconds from the saved artifact.
2. **Artifacts are the handoff.** Downstream phases and the AN read
   artifacts, not figures. If a plotting script crashes, no data is lost.
3. **Review is cleaner.** Code reviewers can audit the analysis logic
   without wading through matplotlib boilerplate, and vice versa.

**In practice:**
- Analysis scripts write to `outputs/` (JSON, NPZ): yields, efficiencies,
  fit parameters, systematic shifts, histograms.
- Plotting scripts read from `outputs/` and write to `outputs/figures/`
  (PDF, PNG).
- Each plotting script has its own pixi task (e.g., `p3-plots`,
  `p4a-plots`). The `all` task runs analysis first, then plots.
- Plotting scripts must NOT call `uproot.open()` or process ROOT files
  directly. If a plot needs data not in the artifacts, the analysis script
  must be extended to produce it — do not bypass the artifact layer.

**Exception:** Quick data/MC overlay plots during Phase 2 exploration may
read ROOT files directly (exploration is inherently interactive). From
Phase 3 onward, the separation is mandatory.

### 11.5 Task Graph

**Every script → pixi task.** `pixi run all` reproduces the full analysis
from raw data. Task names are human-readable. Scripts are idempotent (fixed
seeds, fixed output paths).

Split scripts exceeding ~5 min into stages with intermediate outputs.
Update `pixi.toml` whenever scripts are added or removed.

### 11.6 Debug Code and Diagnostic Outputs

Debug scripts are prefixed with `debug_` or placed in `scratch/`. They are
never included in the `all` task and are not part of the reproducibility
chain.

**But debug outputs are valuable — preserve them in logs.** Debug plots,
diagnostic tables, intermediate sanity checks, and exploratory figures
should NOT be deleted or "cleaned up before review." They should be saved
to `logs/` or `outputs/debug/` and referenced in the experiment log. A
reviewer or future analyst tracing a decision ("why did you choose this
binning?") should be able to find the debug plot that motivated it.

What goes where:
- **`outputs/`** — production artifacts (JSON, NPZ). These enter the
  analysis chain and the AN.
- **`outputs/figures/`** — publication-quality figures for the AN.
- **`outputs/debug/`** — diagnostic figures and intermediate outputs.
  Not in the AN, but preserved and referenced in the experiment log.
  Examples: alternative binning comparisons, failed fit attempts,
  variable correlations checked during exploration, quick-and-dirty
  plots used to make decisions.
- **`logs/`** — session logs, experiment log entries. The narrative
  record of what was tried and why.

The rule is: anything that informed a decision should be traceable.
"I chose 8 bins because the 12-bin version had empty bins" is only
useful if the 12-bin plot is in `outputs/debug/` and referenced in the
experiment log.

---
