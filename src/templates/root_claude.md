# Analysis: {{name}}

Type: {{analysis_type}}

---

## Execution Model

**You are the orchestrator.** You do NOT write analysis code yourself. You
delegate to subagents. Your context stays small; heavy work happens in
subagent contexts.

**All executor subagents start in plan mode.** When spawning an executor,
instruct it to first produce a plan: what scripts it will write, what figures
it will produce, what the artifact structure will be. The subagent executes
only after the plan is set. This prevents agents from diving into code
without thinking.

**The orchestrator loop for each phase:**

```
for each phase in [1, 2, 3, 4a, (4b, 4c if search), 5]:

  1. EXECUTE — spawn a phase executor subagent (start in plan mode) with:
     - The physics prompt
     - The phase CLAUDE.md (read from disk, pass in prompt)
     - Paths to upstream artifacts (subagent reads from disk)
     - The experiment log path (subagent appends to it)
     - The conventions directory path (for phases that need it)
     - Instruction to write the phase artifact to disk

  2. REVIEW — spawn reviewer subagent(s) with:
     - Path to the phase artifact just written
     - The review criteria for this phase
     - The conventions directory path
     - Instruction to write REVIEW_NOTES.md in the phase directory

  3. CHECK — read the review findings (short).
     If regression trigger (physics issue from earlier phase):
       → enter Phase Regression protocol (see below).
     If Category A or B issues: spawn a fix agent to address ALL of them,
       then re-review with a fresh reviewer added to the panel.
     If only Category C or no issues: proceed.

  4. COMMIT — commit the phase's work.

  5. HUMAN GATE (after 4a for measurements, after 4b for searches):
     Present the draft AN or results to the human. Pause until approved.

  6. ADVANCE — proceed to next phase.
```

**Measurement vs. search flow for Phase 4:**
- **Measurements:** Phase 4a is the primary inference phase (systematics,
  correction, covariance, reference comparisons). Phases 4b and 4c are
  **skipped** — there is nothing to blind. The human gate happens after the
  Phase 4a 3-bot review passes.
- **Searches:** All three sub-phases (4a → 4b → 4c) are required. The human
  gate is between 4b and 4c (before full unblinding).

**What the orchestrator does NOT do:**
- Read full scripts or data files (subagents do this)
- Debug code (subagents do this)
- Produce figures (subagents do this)
- Write analysis prose (subagents do this)

**What the orchestrator MUST do:**
- Ensure review quality. Do NOT conserve tokens by accepting weak reviews
  or rushing past issues. If a reviewer finds problems, have the work redone
  properly — not minimally patched.
- Trigger phase regression when ANY review finds physics issues traceable
  to an earlier phase (see Phase Regression section below). This is
  especially common after Phase 4a/4b and Phase 5 reviews.

**Anti-patterns:**
- Running straight from Phase 1 to Phase 5 with no intermediate artifacts
- The orchestrator writing analysis scripts itself
- Using an LLM for format conversion — use pandoc, not an agent
- Writing a workaround when a maintained tool exists — `pixi add` it instead
- Accepting reviewer PASS too easily — the arbiter should ITERATE liberally

---

## Environment

This analysis has its own pixi environment defined in `pixi.toml`.
All scripts must run through pixi:

```bash
pixi run py path/to/script.py          # run a script
pixi run py -c "import uproot; ..."     # quick check
pixi shell                              # interactive shell with all deps
```

**Never use bare `python`, `pip install`, or `conda`.** If you need a
package, add it to `pixi.toml` and run `pixi install`. Never use system
calls to install packages — that is already a failure you are trying to
recover from.

---

## Tool Requirements

Non-negotiable. Use these — not alternatives.

| Task | Use | NOT |
|------|-----|-----|
| ROOT file I/O | `uproot` | PyROOT, ROOT C++ macros |
| Array operations | `awkward-array`, `numpy` | pandas (for HEP event data) |
| Histogramming | `hist`, `boost-histogram` | ROOT TH1, numpy.histogram (for filling) |
| Plotting | `matplotlib` + `mplhep` | ROOT TCanvas, plotly |
| Statistical model | `pyhf` (binned), `zfit` (unbinned) | RooFit, RooStats, custom likelihood code |
| Jet clustering | `fastjet` (Python) | manual clustering |
| Logging | `logging` + `rich` | `print()` — never use bare print |
| Document prep | `pandoc` (>=3.0) + pdflatex | LLM-based markdown→LaTeX conversion |
| Dependency mgmt | `pixi` | pip, conda |

**Optional:** `coffea` (`NanoEvents` for schema-driven array access,
`PackedSelection` for cutflow management) when the event structure benefits.
Not required for every analysis.

---

## Coding Rules

- **Columnar analysis.** Arrays, not event loops. Selections are boolean masks.
- **Prototype on a slice.** ~1000 events first, full data only for production.
- **Read the API.** `help(function)` before workarounds. Most "unexpected"
  behavior has a documented parameter.
- **No bare `print()`.** Use `logging` + `rich`. Ruff T201 enforces this.

Standard logging setup:
```python
import logging
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)
```

- **Conventional commits.** `<type>(phase): <description>`.
  Types: feat, fix, data, plot, doc, refactor, test, chore.
- **Scripts as pixi tasks.** Every script gets a named task in `pixi.toml`.
  The `all` task runs the full chain — this is the reproducibility contract.
- **KISS.** Obvious numpy/awkward operations over clever metaprogramming.
- **YAGNI.** No CLIs, config systems, or plugin architectures. Write scripts.
- **Immutable cuts.** Express selections as named boolean masks. Never modify
  underlying arrays — apply masks to produce filtered views.
- **Workspace as artifact.** pyhf JSON workspaces are version-controlled files.
- **Deterministic.** Pin random seeds. Record software versions.
- **Use up-to-date libraries.** Always use current stable versions of
  dependencies, not legacy ones. But avoid bleeding edge — when a new Python
  minor version is released, allow ~1 year for ecosystem compatibility
  (numba, scipy, etc. lag behind). When in doubt, use the version in
  conda-forge's main channel.

---

## Scale-Out Rules

**Always estimate before running at full scale.** Check input size, time a
1000-event slice, extrapolate.

| Estimated time | Action |
|---|---|
| < 2 min | Single-core local — just run it |
| 2–15 min | `ProcessPoolExecutor` or equivalent multicore |
| > 15 min | SLURM: `sbatch --wait` (single) or `--array` (per-file) |

- **Never wait > 15 min on a login node** when SLURM is available.
- **Prefer the simplest pattern.** Don't use coffea when ProcessPoolExecutor
  works. Don't use dask when SLURM array jobs work.
- **SLURM is fast on requeue partitions.** `--requeue` flag + short walltime
  = near-instant scheduling. Use `sbatch --wait` to block until done.

---

## Plotting Rules

All figures must follow these rules. Violations are Category A review findings.

**Setup:**
```python
import matplotlib.pyplot as plt
import mplhep as mh
import numpy as np

np.random.seed(42)
mh.style.use("CMS")
```

**Figure size is LOCKED at `figsize=(10, 10)`.** Do not use any other size.
For MxN subplots: `figsize=(10*ncols, 10*nrows)`. For ratio plots:
`figsize=(10, 10)` with `height_ratios=[3, 1]`.

**Font sizes are LOCKED.** Do not pass `fontsize=` to ANY matplotlib call
(`set_xlabel`, `set_ylabel`, `set_title`, `tick_params`, `annotate`, `text`).
The CMS stylesheet sets all font sizes for the 10x10 figure size. The ONLY
exception is `ax.legend(fontsize="x-small")`.

**No titles.** Never `ax.set_title()`. Captions go in the analysis note.

**Axis labels with units.** Always `ax.set_xlabel(...)` and
`ax.set_ylabel(...)` with units in brackets, e.g. `r"$p_T$ [GeV]"`.

**Experiment label on every axes:**
```python
mh.label.exp_label(
    exp="ALEPH",     # Set to your experiment
    text="",         # e.g. "Preliminary"
    loc=0,
    data=False,      # True when real data is used
    rlabel=None,     # e.g. r"$\sqrt{s} = 91.2$ GeV" for non-LHC
    ax=ax,
)
```

**Save as PDF + PNG.** Always `bbox_inches="tight"`, `dpi=200`,
`transparent=True`. Close figures after saving: `plt.close(fig)`.

**Never use `tight_layout()` or `constrained_layout=True`** — they conflict
with mplhep's label positioning.

**2D plots with colorbars:** Use `mh.hist2dplot(H, cbarextend=True)` or
`cax = mh.utils.make_square_add_cbar(ax)` to keep square aspect. Never bare
`fig.colorbar(im)`.

**Prefer mplhep functions** (`mh.histplot`, `mh.hist2dplot`) over raw
matplotlib for HEP conventions.

**Figures in artifacts:** Use `![Detailed caption](figures/name.pdf)`.
No other format.

---

## Phase Gates — Non-Negotiable

Every phase must produce its **written artifact** on disk before the next
phase begins. No exceptions.

| Phase | Required artifact | Review type |
|-------|-------------------|-------------|
| 1 | `phase1_strategy/exec/STRATEGY.md` | 3-bot |
| 2 | `phase2_exploration/exec/EXPLORATION.md` | Self |
| 3 | `phase3_selection/exec/SELECTION.md` | 1-bot |
| 4a | `phase4_inference/exec/INFERENCE_EXPECTED.md` | 3-bot |
| 4b | `phase4_inference/exec/INFERENCE_PARTIAL.md` | 3-bot (search only) |
| 4c | `phase4_inference/exec/INFERENCE_OBSERVED.md` | 1-bot (search only) |
| 5 | `phase5_documentation/exec/ANALYSIS_NOTE.md` | 4-bot (3 + rendering) |

**Measurements skip 4b/4c.** For measurements, Phase 4a produces the final
result. The human gate follows the 4a review. Phase 5 follows directly.

**Review before advancing.** After each artifact, spawn a reviewer subagent
(preferred) or self-review. Write findings to `phase*/review/REVIEW_NOTES.md`.

**Experiment log.** Append to `experiment_log.md` throughout. An empty
experiment log at the end of a phase is a process failure.

**`all` task.** `pixi.toml` must have an `all` task that runs the full
analysis chain. Update it whenever scripts are added.

---

## Review Protocol

### Classification

- **(A) Must resolve:** Errors or missing elements that would cause a referee
  to reject. Work cannot proceed.
- **(B) Must fix before PASS:** Issues that weaken the analysis. These are
  fixed in the same iteration cycle as Category A — the arbiter must not
  PASS with unresolved B items. A "good enough" analysis with known B
  issues produces a bad AN.
- **(C) Suggestions:** Style, clarity, minor improvements. Do not trigger
  re-review — the fix agent addresses them in the same pass as A/B items.
  If only C items remain, the arbiter PASses and the executor applies them
  before committing. No C item should be silently dropped.

### Review Types

**3-bot review** = critical reviewer + constructive reviewer + arbiter.
Run reviewers in parallel; arbiter reads both and issues PASS / ITERATE /
ESCALATE.

**1-bot review** = single critical reviewer. Executor addresses Category A
and B items and re-submits. No arbiter.

**Self-review** = the executing agent reviews its own work before producing
the artifact. No separate agent.

### Reviewer Harshness

**Reviewers must be adversarial.** The critical reviewer's job is to find
what is WRONG and what is MISSING — not to validate what is present. The
constructive reviewer proposes concrete improvements, not compliments.

**The arbiter must ITERATE liberally.** PASS only when the work is genuinely
publication-ready. The arbiter should ask: "Would I stake my reputation on
this analysis?" If the answer is no, ITERATE. Erring on the side of another
iteration is always preferable to passing weak work.

**The orchestrator must not optimize for speed.** If a reviewer flags
Category A or B issues, the orchestrator spawns a fix agent to address ALL
of them — not just the A items. A and B issues are both fixed before the
arbiter can PASS. If large sections need rework, that is fine. The cost of
iteration is tokens; the cost of a bad analysis is a retraction.

**Fresh eyes after each iteration.** After each fix-and-re-review cycle,
add a fresh reviewer to the panel (spawn a new critical or constructive
reviewer that has not seen previous iterations). Stale reviewers develop
blind spots — a fresh reviewer catches issues the original panel normalized.

### Review Focus by Phase

| Phase | Focus |
|-------|-------|
| Strategy | Backgrounds complete? Approach motivated by literature? Systematic plan covers standard sources (conventions)? Reference analyses identified with systematic programs tabulated? |
| Exploration | Samples complete? Data quality checked? Distributions physical? |
| Selection | Background model closes? Every cut motivated by a plot? Per-category data/MC validation? |
| 4a: Expected | Fit healthy? Systematics complete vs conventions AND references? Signal injection passes? |
| 4b: Partial | Draft note publication-quality? 10% results consistent? Diagnostics clean? |
| 4c: Full | Post-fit diagnostics healthy? Anomalies characterized? |
| Documentation | See Phase Regression below — this is where most bugs are caught. |

### Reviewer Framing

The key question is not "does this pass its tests?" but "what would a
knowledgeable referee ask for that isn't here?"

Before concluding review, explicitly answer:
1. Are all systematic sources in conventions either implemented or justified?
2. Have 2-3 reference analyses been identified with systematic programs tabulated?
3. If a competing group published the same measurement, what would they have
   that we don't?

### Iteration

- 3-bot: repeats until arbiter PASS with no A or B items remaining. Warn
  after 6 iterations, strong warn after 10.
- 1-bot: warn after 4, escalate after 6.
- Self: no formal iteration.

Each iteration adds a fresh reviewer. The arbiter must not PASS if any
Category B items remain unresolved.

---

## Phase Regression

**Regression can trigger at any review, not just Phase 5.** When a reviewer
at Phase N finds a physics issue whose root cause is in Phase M < N, this
triggers regression — rework of the earlier phase and its downstream
dependents.

**This is the expected path, not an exception.** Most serious issues (wrong
systematic treatment, missing background, flawed correction, inadequate
cross-checks) surface during later reviews when more context is available.
Common trigger points:
- **Phase 4a/4b review** finds a selection flaw (Phase 3) or a missing
  systematic that should have been planned (Phase 1)
- **Phase 5 review** finds a methodological gap visible only when the full
  analysis is assembled

### Phase 5 review structure (4-bot)

Phase 5 uses an extended review with a rendering reviewer:
1. **Critical reviewer** — reads the AN as a referee. Finds physics errors
   and missing content.
2. **Constructive reviewer** — identifies what would strengthen the analysis.
3. **Rendering reviewer** — reads the compiled PDF using the Read tool
   (which supports PDF viewing) and checks: figures render correctly, math
   compiles, layout is readable, no overlapping text or clipped figures,
   cross-references resolve. Run `pixi run build-pdf` first, then
   `Read("phase5_documentation/exec/ANALYSIS_NOTE.pdf")` to inspect.
4. **Arbiter** — reads all three reviews, classifies findings, issues verdict.

### Regression trigger

When any review finds a **physics issue** traceable to an earlier phase:

1. The arbiter (or 1-bot reviewer) classifies the finding as a **regression
   trigger** and identifies the origin phase.
2. The orchestrator spawns an **Investigator** to assess impact:
   - Reads the finding and the origin phase artifact
   - Traces forward: which downstream artifacts depend on the wrong
     conclusion?
   - Produces `REGRESSION_TICKET.md`: root cause, affected phases, fix scope
3. The orchestrator dispatches fixes in phase order:
   - Origin phase executor re-runs with the regression ticket
   - Affected downstream phases re-run with updated upstream artifacts
   - Unaffected phases are skipped
4. After fixes, review resumes from the phase where regression was triggered.

### Regression vs. local fix

- **Physics issue traceable to earlier phase** (wrong systematic, missing
  background, flawed correction, selection bug) → regression trigger.
- **Issue fixable within the current phase** (axis label, caption, code bug
  in current phase's scripts) → normal Category A fix-and-re-review cycle.

---

## Feasibility Evaluation

When the analysis encounters a limitation (missing MC samples, unavailable
detector simulation, missing calibration data, etc.), the agent must not
silently downscope. Instead:

1. **State the limitation clearly.** What is missing and why does it matter?
2. **Evaluate feasibility.** Can this be obtained, generated, or approximated?
   - Is documentation/code available to produce what's needed?
   - How complex is the implementation?
   - What is the risk of failure?
3. **Estimate cost.** How much compute time, how many SLURM jobs, how much
   agent time? Will it require external data or tools not in the environment?
4. **Decision.** Compare against the improvement to the result:
   - If the limitation affects a dominant systematic or the core result:
     attempt to resolve it if feasibility is reasonable.
   - If it affects a sub-leading correction or a minor cross-check:
     document as a limitation and move on.
   - If resolution requires resources outside the analysis scope (new data,
     new detector simulation, new MC generation campaign): document as a
     limitation. Agents cannot build detectors or collect new data.
5. **Log the decision.** Record the evaluation in `experiment_log.md` with
   the reasoning. This is auditable — reviewers will check that limitations
   were evaluated, not just accepted.

---

## Conventions

Read the applicable files in `conventions/` at three mandatory checkpoints:

1. **Phase 1 (Strategy):** Read all applicable conventions before writing
   the systematic plan. Enumerate every required source with "Will implement"
   or "Not applicable because [reason]."
2. **Phase 4a (Inference):** Re-read conventions before finalizing
   systematics. Produce a completeness table comparing sources against
   conventions AND reference analyses.
3. **Phase 5 (Documentation):** Final conventions check — verify everything
   required is present in the analysis note.

If a convention requires something you plan to omit, justify explicitly.

---

## Reference Analyses

To be filled during Phase 1. The strategy must identify 2-3 published
reference analyses and tabulate their systematic programs. This table is
a binding input to Phase 4 and Phase 5 reviews.

---

## Analysis Note Requirements

The analysis note (`ANALYSIS_NOTE.md`) must be written as **pandoc-compatible
markdown** that compiles cleanly to PDF. This means:

- **LaTeX math:** Use `$...$` for inline and `$$...$$` for display math.
  Write `$\alpha_s$`, not `alpha_s`.
- **Figures:** `![Caption text](figures/name.pdf)` — pandoc converts these
  to LaTeX `\includegraphics` automatically.
- **No raw HTML.** Pandoc markdown only.
- **Tables:** Use pipe tables (`| col1 | col2 |`). They render in both
  markdown and PDF.
- **Cross-references:** Use pandoc-crossref syntax (`{#fig:label}`,
  `@fig:label`) for numbered figure/table/equation references.
- **Section structure:** Use `#`, `##`, `###` headings. Pandoc adds
  numbering with `--number-sections`.

The note must contain at minimum these sections:
1. Introduction — physics motivation, observable definition, prior measurements
2. Data samples — complete inventory (experiment, √s, luminosity, MC details)
3. Event selection — every cut with motivation, distribution plot, efficiency
4. Corrections / unfolding (measurements) — full procedure, closure tests
5. Systematic uncertainties — one subsection per source with method and impact
6. Cross-checks — one subsection per cross-check with quantitative result
7. Statistical method — likelihood, fit validation, uncertainty propagation
8. Results — primary result with full uncertainties, per-bin tables
9. Comparison to prior results and theory — overlay plots, chi2/p-values
10. Conclusions — summary, precision, dominant limitations
11. Future directions — concrete roadmap
12. Appendices — covariance matrices as tables, extended cutflow, auxiliary plots

### PDF Build

The `build-pdf` pixi task compiles the analysis note:

```bash
pixi run build-pdf
```

**Never use an LLM to convert markdown to LaTeX.** Pandoc handles this.

---

## Technique-Specific Requirements

These apply based on the technique chosen in the Phase 1 strategy.

### For unfolding measurements

If the strategy specifies unfolding as the correction technique:

**Phase 3 — additional requirements:**
- Produce data/MC comparison plots for ALL kinematic variables entering the
  observable, resolved by reconstructed object category
- Document the level of agreement per category
- These plots are evidence that the MC response model is adequate — required
  even if observable-level data/MC looks fine

**Phase 4 — additional requirements:**
- **Prior-sensitivity check.** Repeat unfolding with a flat prior at nominal
  regularization. If any bin changes by >20%, the result is prior-dominated.
- **Alternative method.** At least one independent unfolding method or
  cross-check (e.g., OmniFold, SVD, bin-by-bin).
- **Hadronization model.** If only one generator is available for the response
  matrix, document as a limitation. Data-driven reweighting is not a
  substitute for a genuine alternative-generator comparison.

### For template fit analyses

If the strategy specifies template fitting:

**Phase 3 — additional requirements:**
- Control region definitions with purity and kinematic relationship to SR
- Validation region closure tests (predicted vs. observed, chi2)

**Phase 4 — additional requirements:**
- Pre-fit and post-fit data/MC agreement in all regions
- Nuisance parameter pulls and constraints
- Impact ranking of systematics

---

## Pixi Reference

Common patterns and pitfalls for `pixi.toml`:

```toml
# === Structure ===
[workspace]
name = "my-analysis"
channels = ["conda-forge"]
platforms = ["linux-64"]

# Conda packages (compiled, from conda-forge)
[dependencies]
python = ">=3.11"
pandoc = ">=3.0"

# Python packages (from PyPI)
[pypi-dependencies]
uproot = ">=5.0"
numpy = ">=1.24"

# Named tasks
[tasks]
py = "python"
select = "python phase3_selection/scripts/apply_selection.py"
all = "python phase3_selection/scripts/apply_selection.py && ..."
```

**Common pitfalls:**
- PyPI packages go in `[pypi-dependencies]`, NOT `[dependencies]`. The
  `[dependencies]` section is for conda-forge packages only.
- After editing `pixi.toml`, run `pixi install` to update the environment.
- Task values are shell command strings. Chain with `&&` for sequential.
- The `py` task (`py = "python"`) lets you run arbitrary scripts:
  `pixi run py my_script.py`.

---

## Git

This analysis has its own git repository (initialized by the scaffolder).
Commit work within this directory. Do not modify files outside this
directory — the spec repository is separate.
