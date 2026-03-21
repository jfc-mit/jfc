# Phase 2: Exploration

> Read `methodology/03-phases.md` → "Phase 2" for full requirements.
> Read `methodology/appendix-plotting.md` for figure standards.

You are exploring the data and MC samples for a **{{analysis_type}}** analysis.

**Start in plan mode.** Before loading any data, produce a plan: which files
to inspect first, what variables to survey, what plots to make. Execute
after the plan is set.

## Output artifact

`outputs/EXPLORATION.md` — sample inventory, data quality assessment, key
variable distributions, variable ranking, and preselection cutflow.

## Methodology references

- Phase requirements: `methodology/03-phases.md` → Phase 2
- Plotting: `methodology/appendix-plotting.md`
- Coding: `methodology/11-coding.md`

## RAG queries (mandatory)

Query the experiment corpus for:
1. Standard object definitions for this experiment (lepton ID, jet clustering, etc.)
2. Known data quality issues or detector effects relevant to the observables

Cite sources in the artifact.

## Data discovery

Expect to discover the data format at runtime. See
`methodology/03-phases.md` → Phase 2 "Data discovery" for the protocol
(metadata first → small slice → identify jagged structure → document schema).

## PDF build test (independent — can run in parallel)

Verify the PDF toolchain works by creating a minimal stub file at
`phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md` (a few lines of markdown with
a math expression and a citation) and running `pixi run build-pdf`. Delete
the stub after confirming. This is independent of exploration and can be
sub-delegated.

## Key requirements

These are the critical actionable items for Phase 2. See
`methodology/03-phases.md` → Phase 2 for full details.

- **Inventory samples completely.** For each file: tree names, branch names
  and types, number of events, cross-section, luminosity. Document the
  schema — this is artifact content.
- **Validate data quality.** Check for pathologies: empty branches, outliers,
  discontinuities, unphysical values. Document all findings.
- **Apply standard object definitions.** Retrieve from the experiment corpus
  (RAG). Verify data/MC agreement in inclusive distributions.
- **Survey discriminating variables.** Produce signal vs. background
  distributions for all candidate kinematic variables. Rank by separation
  power (ROC AUC, significance improvement, or equivalent).
- **Establish baseline yields.** Report event counts after preselection for
  data and each MC sample, with cross-section normalization.
- **PDF build test.** Run a stub `pixi run build-pdf` at the end of this
  phase to catch toolchain issues early.

## Rules

- Prototype on small subsets (~1000 events). Do not process full data to
  "see what's there."
- Append findings to experiment_log.md as you go.

## Pre-review self-check

Before submitting for review, verify:

- [ ] Sample inventory: every file with tree names, branches, events
- [ ] Data quality: no pathologies, outliers, unphysical values
- [ ] Object definitions applied from corpus and cited
- [ ] Variable survey with data/MC comparisons for all candidates
- [ ] Baseline yields after preselection
- [ ] PDF build test passed
- [ ] Experiment log updated with discoveries
- [ ] All figures pass plotting rules (see quick reference below)

### Plotting quick reference

These are the rules most commonly caught at review. Full spec in
`methodology/appendix-plotting.md`.

1. `figsize=(10, 10)` always — never custom sizes
2. `mpl_magic(ax)` after all plotting to prevent legend-data overlap
3. 2D colorbars: `make_square_add_cbar(ax)` or `cbarextend=True` —
   never `fig.colorbar(im)` or `fig.colorbar(im, ax=ax)`
4. `mh.histplot()` for all binned data — never `ax.step()`, `ax.bar()`
5. No absolute `fontsize=N` — use `'x-small'` etc.
6. `exp_label()` on every independent axes, NEVER on ratio panels
7. Separate matplotlib outputs composed in LaTeX — only use multi-panel
   matplotlib for ratio plots with `sharex=True`

## Review

**Self-review + plot validator.** Explicitly check: sample inventory
complete? Data quality checked? Experiment log updated? Distributions
look physical? The plot validator runs alongside self-review to validate
figures programmatically.
Write findings to `review/{role}/` using session-named files
(see `methodology/appendix-sessions.md` for naming conventions).
