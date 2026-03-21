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

`outputs/SELECTION.md` — final object definitions, event selection with
optimization, cutflow table, and technique-specific deliverables.

## Applicable conventions

Read the Phase 1 `STRATEGY.md` to identify the selected technique, then
open the corresponding convention file and implement every required step:

{{conventions_files}}

Convention requirements (e.g., input validation before response matrix
construction, required validation checks) are **hard requirements** —
omissions are Category A at review.

## Correction infrastructure gate (measurements)

**BEFORE computing correction factors or building the response matrix:**
1. Produce data/MC comparison plots for ALL variables entering the
   observable calculation. This is a hard gate — do not proceed without
   these plots.
2. Compute the response matrix on a small MC subset (~10K events) and
   report the diagonal fraction. If < 50%, reassess the binning/method
   before building the full chain.

**If ANY validation test fails (closure, stress, alternative method):**
You MUST attempt at least 3 independent remediation approaches BEFORE
writing the artifact. Read how published analyses of the same observable
handled the correction — if they succeeded with a method you haven't
tried, try it. Documenting a failure without remediation attempts is
Category A at review.

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

## Selection approach comparison (mandatory)

Phase 3 must try at least two selection approaches before choosing one.
See `methodology/03-phases.md` → Phase 3 "Selection" for full requirements.

- [ ] Identify approaches from Phase 1 exploration plan
- [ ] Implement each to the point where a common figure of merit can be evaluated
- [ ] Report comparison in artifact with figure of merit for each
- [ ] Select final approach based on evidence and document rationale

If selected approach is MVA:

- [ ] Sub-delegate MVA training to a sub-agent (see §3a.5)
- [ ] Train primary classifier (BDT or NN)
- [ ] Train ≥1 alternative architecture (NN if BDT, vice versa)
- [ ] Try multiclass if >2 physics classes (e.g., b/c/light)
- [ ] Produce validation plots: ROC, score distributions (train/test overlaid), feature importance
- [ ] Check data/MC agreement on classifier output — investigate before accepting systematic
- [ ] Optimize working point with figure of merit
- [ ] Save trained model, hyperparameters, split seed, validation plots as artifacts

If selected approach is cut-based, this is a downscope from the default MVA
recommendation. Document the constraint and comparison that justified the
choice (see `methodology/12-downscoping.md`).

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
Write findings to `review/{role}/` using session-named files
(see `methodology/appendix-sessions.md` for naming conventions).
