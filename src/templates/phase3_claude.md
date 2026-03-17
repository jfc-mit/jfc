# Phase 3: Processing

> Read `methodology/03-phases.md` → "Phase 3" for full requirements.
> Read `methodology/appendix-plotting.md` for figure standards.

You are implementing the analysis approach defined in the Phase 1 strategy
for a **{{analysis_type}}** analysis. Read the strategy first — it determines
what this phase must deliver.

**Start in plan mode.** Before writing any code, produce a plan: what scripts
you will write, what selection you will implement, what figures you will
produce, what the artifact structure will be. Execute after the plan is set.

## Output artifact

`exec/SELECTION.md` — final object definitions, event selection with
optimization, cutflow table, and technique-specific deliverables.

## Methodology references

- Phase requirements: `methodology/03-phases.md` → Phase 3
- Technique-specific requirements: `methodology/03-phases.md` → Phase 3 "Correction infrastructure" / "Background estimation" subsections
- Review protocol: `methodology/06-review.md` → §6.2 (1-bot), §6.4
- Plotting: `methodology/appendix-plotting.md`
- Coding: `methodology/11-coding.md`

## RAG queries (mandatory)

Query the experiment corpus for:
1. Published selection criteria for similar analyses
2. Known correction factors or efficiency maps
3. Background estimation techniques used in reference analyses

Cite sources in the artifact.

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
- Flavour tagging (b vs. light, b vs. c) — always.
- Signal/background separation in searches — always, unless the signal
  is a simple mass peak with no combinatoric background.
- Event categorization — when more than 2 variables are relevant.

**When rectangular cuts are fine:**
- Preselection (hadronic event selection, basic quality cuts)
- Single-variable selections with clear physical motivation
- When the sample size is too small for training (~< 1000 events)

**Training protocol:**
1. Split MC into train/test (fixed random seed). Never evaluate on training set.
2. Train the classifier. For BDTs: `xgboost.XGBClassifier` with early stopping.
3. **Train at least one alternative architecture** (e.g., fully connected NN
   if primary is BDT, or vice versa). This is cheap and provides a genuine
   cross-check of the classifier. Report both performances.
4. **When the physics has >2 classes** (e.g., b vs. c vs. light in flavour
   tagging), try multiclass classification — not just binary. Multiclass
   often outperforms chained binary classifiers and directly models the
   background composition.
5. Produce validation plots: ROC curve, score distributions (train/test
   overlaid), feature importance ranking. **Check data/MC agreement on
   the classifier output** — if mismodeling is visible, investigate
   whether input variable cuts or calibration can improve it before
   accepting the MVA systematic as-is.
6. Choose working point by optimizing a figure of merit. Document the choice.
7. The trained model, hyperparameters, split seed, and validation plots are
   required artifacts.

**Sub-delegate MVA training.** Classifier training is a self-contained task
with its own iteration cycle (hyperparameter tuning, overtraining checks,
feature selection). Delegate it to a sub-agent rather than running it in
the main executor context. The sub-agent receives the training data spec
and returns the trained model + performance metrics + validation plots.
See `methodology/03a-orchestration.md` → §3a.5.1.

## Sensitivity optimization (when initial selection is insufficient)

If the initial selection does not meet the physics goal, systematically
explore alternatives. Maintain a **sensitivity log** (`sensitivity_log.md`)
tracking each approach, figure of merit, and limiting factor.

Progress through qualitatively different strategies (not just parameter
tuning). Not all apply to every analysis type — select those relevant:
1. Optimize the current approach (tune cuts for S/sqrt(B) or equivalent)
2. Try a more powerful discriminant (cut-based → BDT → GNN)
3. Try different inference strategies (shape fit vs. counting, different
   discriminant variables) — primarily for searches and template fits
4. Revisit region design (tighter SR, different background decomposition,
   alternative efficiency binning)

**Stop when:** sensitivity meets the goal, OR 3+ materially different
approaches tried AND marginal improvement (<10% relative). Document all
attempts — "we tried X, Y, Z; Y performed best because [reason]" is a
valid conclusion. See `methodology/03-phases.md` → Phase 3 for full details.

## Review

**1-bot review** — see `methodology/06-review.md` for protocol.
Write findings to `review/REVIEW_NOTES.md`.
