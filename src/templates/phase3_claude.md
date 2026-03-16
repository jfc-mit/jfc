# Phase 3: Processing

> **End goal.** This analysis produces a publication-quality analysis note
> for journal submission. Every phase contributes to that goal. Work should
> meet the standard of external scrutiny — a journal referee, a collaboration
> review committee, or a competing group doing the same measurement.

You are implementing the analysis approach defined in the Phase 1 strategy.
Read the strategy first — it determines what this phase must deliver.

**Start in plan mode.** Before writing any code, produce a plan: what scripts
you will write, what selection you will implement, what figures you will
produce, what the artifact structure will be. Execute after the plan is set.

## Required deliverables

- Final object definitions
- Event selection with optimization
- Cutflow table with data and MC yields
- For searches: background estimation, control/validation regions, closure tests
- For measurements: correction chain (response matrix, unfolding, closure tests)

## Output artifact

You MUST produce `exec/SELECTION.md` before Phase 4 begins.
This is a hard gate — the artifact is both the handoff document and the
proof that the phase was completed with appropriate rigor.

## RAG queries (mandatory)

Query the experiment corpus for:
1. Published selection criteria for similar analyses
2. Known correction factors or efficiency maps
3. Background estimation techniques used in reference analyses

Cite sources in the artifact.

## Technique-specific requirements

Read the Phase 1 strategy to determine which technique applies.

**For unfolding measurements:**
- Produce data/MC comparison plots for ALL kinematic variables entering the
  observable, resolved by reconstructed object category
- Document the level of agreement per category
- Identify and document any discrepancies
- These plots are evidence that the MC response model is adequate — required
  even if observable-level data/MC looks fine

**For template fit / search analyses:**
- Control region definitions with purity and kinematic relationship to SR
- Validation region closure tests (predicted vs. observed, chi2)

## Multivariate classification: use it

When the analysis requires separating signal from background, tagging
flavour, or classifying event types, **default to training a BDT or
neural network** — do not default to rectangular cuts unless the
separation is trivially one-dimensional.

Modern HEP analyses use multivariate techniques as standard practice.
The available tools (`xgboost`, `scikit-learn`, and optionally
`pytorch` via `pixi add`) make this straightforward. A trained
classifier almost always outperforms hand-tuned cuts, and the training
process itself reveals which variables carry discriminating power.

**When to train a classifier:**
- Flavour tagging (b vs. light, b vs. c) — always. Impact parameter
  `d0`, `z0`, track multiplicity, vertex detector hits, and jet
  kinematics are natural inputs. A BDT on these variables will
  outperform any single-variable cut.
- Signal/background separation in searches — always, unless the signal
  is a simple mass peak with no combinatoric background.
- Event categorization (e.g., 2-jet vs. 3-jet topology quality) — when
  more than 2 variables are relevant.

**When rectangular cuts are fine:**
- Preselection (hadronic event selection, basic quality cuts)
- Single-variable selections with clear physical motivation (e.g.,
  thrust > 0.7 to select 2-jet events)
- When the sample size is too small for training (~< 1000 events)

**Training protocol:**
1. Split MC into train/test (e.g., 50/50 or 70/30). Use a fixed random
   seed. Never evaluate performance on the training set.
2. Train the classifier. For BDTs: `xgboost.XGBClassifier` with
   early stopping on the test set. Start with defaults; tune only if
   performance is poor.
3. Produce standard validation plots: ROC curve, score distributions
   for signal and background (train and test overlaid to check
   overtraining), feature importance ranking.
4. Choose the working point by optimizing a figure of merit (efficiency
   × purity, S/√(S+B), or analysis-specific metric). Document the
   choice.
5. The trained model, its hyperparameters, the training/test split
   seed, and all validation plots are required artifacts.

**Do not avoid ML because it seems complex.** A basic XGBoost BDT with
5 input features trains in seconds on the available MC sample sizes.
The complexity cost is near zero; the performance gain is often
substantial. Reviewers will ask why a multivariate approach was not
used if the analysis relies on cuts in a multi-dimensional space.

## Plotting

Style setup: `import mplhep as mh; mh.style.use("CMS")`

Figure size: `figsize=(10*ncols, 10*nrows)` — always. No exceptions.

No `ax.set_title()` — captions in the note, not on axes.

Save as PDF + PNG, `bbox_inches="tight"`, `dpi=200`. Close after saving.

Reference figures in the artifact using:
```markdown
![Detailed caption describing what is plotted.](figures/filename.pdf)
```

## Review

This phase gets **1-bot review** — a single critical reviewer. The reviewer
classifies findings as:
- **(A) Must resolve** — blocks advancement
- **(B) Must fix before PASS** — weakens the analysis, must be resolved
- **(C) Suggestion** — style, clarity. Applied before commit, not re-reviewed

The executor addresses Category A and B items and re-submits. No arbiter
needed. A fresh reviewer is added each iteration. Warn after 2 iterations,
escalate after 3.

The reviewer will check:
- Is every cut motivated by a plot?
- Does the background model / correction close?
- Per-category data/MC validation done? (Category A if missing for unfolded
  measurements)
- Cutflow complete with per-cut and cumulative efficiencies?

Write review findings to `review/REVIEW_NOTES.md`.
