# Spec Refactor Plan: Doc Phase Architecture + LaTeX-First Pipeline

**Baseline:** tag `v3` (commit f1fb3c9)
**Date:** 2026-03-25

---

## Design Summary

### Phase flow

```
Phase 1 (strategy)        → 4-bot review
Phase 2 (exploration)     → self + plot validator (full visual)
Phase 3 (processing)      → 1-bot + plot validator

Phase 4a (inference, expected)     → 1-bot + plot validator [blocking]
Doc 4a   (write full AN in LaTeX)  → 5-bot+bib review

Phase 4b (inference, 10% data)     → 1-bot + plot validator [blocking]
Doc 4b   (update AN with 10% data) → 5-bot+bib review → HUMAN GATE

Phase 4c (inference, full data)    → 1-bot + plot validator [blocking]
Doc 4c   (update AN with full data)→ 5-bot+bib review = FINAL DELIVERABLE
```

### Key principles

- **LaTeX first-class.** The AN is written directly in LaTeX. No pandoc.
  Typesetter fixes persist across phases because the .tex IS the source.
- **Inference separated from documentation.** 4x phases do physics
  (fits, systematics, figures). Doc phases write the document (prose,
  compositing, compilation). The note writer does NOT run analysis code.
  It CAN produce methodology diagrams.
- **Plot validator at every figure-producing phase.** Phases 2, 3, 4a,
  4b, 4c all get full visual plot validation. Catches legend overlap,
  label sizing, etc. at the source instead of at Doc review.
- **Reviews never lighter.** All Doc phases get 5-bot+bib. The
  expectation is that Doc 4b/4c find fewer issues, but the review panel
  is identical.
- **Doc 4a is the heavy lift.** Writes the complete AN with \tbd{}
  placeholders. Gets the structure, compositing, and rendering right
  once. Doc 4b/4c are evolution, not rebuilds.
- **Flagship figures are tracked in COMMITMENTS.md.** All figures meet
  the same quality bar. Flagship = storytelling prominence, not extra
  polish. The list evolves as the analysis progresses.

### Regression protocol

- **UPDATE** (narrow: parameter fix, bug fix, added component): Doc
  agent edits existing AN, creates new version.
- **REWRITE** (deep: approach changed, selection changed, >30% of
  content affected): Doc agent writes fresh AN from current artifacts.
  Orchestrator restarts from the earliest affected Doc phase.
- **Decision rule:** Approach changed → REWRITE. Parameter changed →
  UPDATE. When in doubt, REWRITE.

### Physics reviewer model

The physics reviewer receives ONLY the compiled PDF and the initial
physics prompt (with any extensions/refinements discovered during the
analysis). It operates as a senior reviewer / PI: assumes everyone else
could have made mistakes or misrepresentations. Its responsibility is
that the result going to journal is correct, true, and scientifically
impactful — produces a real measurement or limit, not just a conclusion
that the inputs were bad. No methodology spec, no conventions, no code.
Pure physics judgment on the document as a referee would see it.

### Plot validator model

The plot validator reads every PNG and evaluates on its own — "look at
this plot, what's wrong with it?" — not just checking against a
checklist. Claude agents can pick up on faults in plots when asked to
look critically. The code linter (`lint_plots.py`) runs first as a
mechanical pre-filter; the visual validator then reads every rendered
figure as a critical human reviewer would.

---

## Implementation Stages

### Stage 1: Infrastructure fixes (compatible with both old and new architecture)

These changes improve the spec regardless of the architecture refactor.
They can be committed independently and don't break anything.

#### S-1.1 COMMITMENTS.md stub + Phase 1 instruction
- [ ] `scaffold_analysis.py`: create empty `COMMITMENTS.md` at analysis root
- [ ] `src/templates/phase1_claude.md`: add instruction to populate COMMITMENTS.md
  with all binding commitments including flagship figures

#### S-1.2 references.bib at analysis root
- [ ] `scaffold_analysis.py`: move stub from `phase5_documentation/outputs/` to
  analysis root

#### S-1.3 lint-plots pixi task
- [ ] `src/templates/pixi.toml`: add `lint-plots = "python conventions/lint_plots.py"`

#### S-1.4 tectonic dependency
- [ ] `src/templates/pixi.toml`: add `tectonic` to `[dependencies]`

#### S-1.5 Category B in arbiter
- [ ] `src/agents/arbiter.md`: update prompt — ITERATE includes A and B findings
- [ ] `src/methodology/06-review.md` §6.1: clarify B must be fixed before PASS
- [ ] `src/methodology/06-review.md` §6.5: clarify arbiter PASS requires no A or B

#### S-1.6 Physics reviewer: rewrite prompt
- [ ] `src/agents/physics_reviewer.md`: rewrite prompt to the senior PI model —
  receives only PDF + physics prompt, assumes everyone could have made mistakes,
  evaluates correctness/truth/impact. Remove convention drift check (that's
  the critical reviewer's job). Remove methodology references (intentionally
  not given). Keep: skeptical stance, statistical methodology check,
  suspiciously good agreement check, figure inspection, method health.

#### S-1.7 Constructive reviewer: add plotting standards
- [ ] `src/agents/constructive_reviewer.md`: add `appendix-plotting.md` to
  methodology references

#### S-1.8 Fixer agent: add RAG access
- [ ] `src/agents/fixer.md`: add RAG MCP tools to Reads section

#### S-1.9 Executor: add JSON output requirements
- [ ] `src/agents/executor.md`: add MACHINE-READABLE OUTPUTS section with
  JSON schema requirements for 4a/4b/4c

#### S-1.10 Asimov vs pseudo-data clarification
- [ ] `src/methodology/04-blinding.md` §4.1: add note about extraction
  measurements using Poisson-fluctuated pseudo-data

#### S-1.11 Covariance cross-reference
- [ ] `src/methodology/03-phases.md` Phase 4a: add cross-reference to
  `conventions/unfolding.md` for any corrected distribution

#### S-1.12 Trials factor guidance
- [ ] `src/methodology/06-review.md` §6.8: add trials factor caveat

#### S-1.13 Numerical precision note
- [ ] `src/methodology/11-coding.md` §11.2: add float64 and no-intermediate-
  rounding note

#### S-1.14 lint_plots.py dedup
- [ ] `src/conventions/lint_plots.py`: deduplicate data=False violation
  (same-line check + context-window check producing duplicates)

#### S-1.15 Minor robustness additions
- [ ] `src/templates/root_claude.md`: add model opus enforcement note
- [ ] `src/templates/root_claude.md`: clarify re-review protocol
- [ ] `src/methodology/07-tools.md` §7.1: add pixi install failure guidance
- [ ] `src/methodology/07-tools.md` §7.3: add SLURM availability detection
- [ ] Reviewer prompts (critical, constructive): add RAG unavailability fallback
- [ ] `src/templates/root_claude.md`: add crash recovery protocol

---

### Stage 2: Architecture refactor (the big changes)

These changes implement the Doc phase architecture and LaTeX-first
pipeline. They should be done together as a coherent set.

#### S-2.1 Directory structure + scaffolder
- [ ] `scaffold_analysis.py`: create Phase 4 subdirs (4a_expected/,
  4b_partial/, 4c_observed/) with standard subdirs
- [ ] `scaffold_analysis.py`: create `analysis_note/` directory with
  outputs/, figures/, review/{doc4a,doc4b,doc4c}/, logs/
- [ ] `scaffold_analysis.py`: update PHASES list for new structure
- [ ] `scaffold_analysis.py`: remove `phase5_documentation/` creation
  (replaced by `analysis_note/`)

#### S-2.2 LaTeX AN template
- [ ] NEW `src/conventions/an_template.tex`: complete document skeleton
  - Preamble include (`conventions/preamble.tex`)
  - `\tbd{}` command for placeholders
  - All 13 required sections as stubs with comments
  - Figure inclusion pattern (standalone, pair, grid)
  - Table patterns (results, systematic, cutflow)
  - Bibliography setup (`\bibliography{../../references}`)
  - Change Log section (unnumbered)

#### S-2.3 Phase 4a/4b/4c CLAUDE.md templates (inference-only)
- [ ] NEW `src/templates/phase4a_claude.md`: expected results, MC-only,
  JSON output requirements, artifact = INFERENCE_EXPECTED.md
- [ ] NEW `src/templates/phase4b_claude.md`: 10% data, compare to expected,
  JSON output, artifact = INFERENCE_PARTIAL.md
- [ ] NEW `src/templates/phase4c_claude.md`: full data, compare to both,
  JSON output, artifact = INFERENCE_OBSERVED.md
- [ ] Remove old `src/templates/phase4_claude.md`

#### S-2.4 Doc phase CLAUDE.md templates
- [ ] NEW `src/templates/doc4a_claude.md`: write full AN from template,
  all artifacts, figure compositing, compile after each section,
  \tbd{} conventions, self-check metrics, flagship figure placement
- [ ] NEW `src/templates/doc4b_claude.md`: copy from Doc 4a AN, update
  results with 10% data, regenerate comparison figures, verify number
  consistency, compile
- [ ] NEW `src/templates/doc4c_claude.md`: copy from Doc 4b AN, update
  with full results, final figures, compile

#### S-2.5 Note writer prompt rewrite
- [ ] `src/agents/note_writer.md`: major rewrite for LaTeX-native output
  - Replace markdown syntax guide with LaTeX syntax guide
  - Add figure compositing patterns (from typesetter)
  - Add compilation instructions (tectonic, fix errors as you go)
  - Add \tbd{} placeholder conventions
  - Keep: figure inventory, numbers consistency lint, self-check,
    data staging, post-regression cohesion, Change Log
  - Add: comparison plot placeholder entries (greyed-out future data
    where meaningful — agreement plots, NOT data/MC distributions)
  - Add: methodology diagram production (note writer can produce or
    delegate)

#### S-2.6 Plot validator prompt update
- [ ] `src/agents/plot_validator.md`: add emphasis on independent visual
  evaluation — "look at this plot, what's wrong with it?" — not just
  checklist matching. The agent should catch problems a critical human
  reviewer would catch when shown the figure.

#### S-2.7 Rendering reviewer update
- [ ] `src/agents/rendering_reviewer.md`: remove pandoc compilation steps,
  update to tectonic, keep all PDF inspection checks, remove pandoc-
  specific checks (Abstract as §1, etc.)

#### S-2.8 Deprecate typesetter agent
- [ ] `src/agents/typesetter.md`: add deprecation header noting this role
  is merged into the note writer. Keep file for reference.
- [ ] `src/agents/README.md`: update activation matrix — remove typesetter,
  add note_writer at Doc phases

#### S-2.9 Root CLAUDE.md template overhaul
- [ ] `src/templates/root_claude.md`: rewrite for new phase flow
  - Update phase sequence (4a → Doc 4a → 4b → Doc 4b → ... )
  - Update progress tracking structure
  - Update review protocol table
  - Update orchestrator loop for interleaved flow
  - Update human gate placement (after Doc 4b 5-bot review passes)
  - Add regression UPDATE/REWRITE decision framework
  - Add session name assignment instructions
  - Remove pandoc-specific AN guidance
  - Add LaTeX AN guidance (cross-refs, citations, figures, tables)
  - Update anti-patterns list
  - Update `build-pdf` description (just tectonic)

#### S-2.10 Methodology section rewrites
- [ ] `src/methodology/03-phases.md`: rewrite Phase 4 section for
  inference-only phases + Doc phases. Remove Phase 5 section (fold
  into Doc 4c description). Update all cross-references.
- [ ] `src/methodology/03a-orchestration.md`: update orchestrator
  architecture for new flow, context management table
- [ ] `src/methodology/05-artifacts.md`: update AN versioning for
  Doc phases, remove pandoc-specific AN format rules
- [ ] `src/methodology/06-review.md`: new review tier table (§6.2),
  new review focus sections for Doc phases (§6.4), update Phase 2
  to include plot validator
- [ ] `src/methodology/analysis-note.md`: remove "LaTeX compilation"
  pandoc pipeline, remove "Pandoc pitfalls" section, update figure
  cross-referencing to LaTeX \label/\ref, update table formatting
  for direct LaTeX, keep all quality standards and completeness
  requirements
- [ ] `src/methodology/appendix-plotting.md`: update "Figure
  cross-referencing" section for LaTeX, update "Figure compositing
  in the AN" to remove COMPOSE annotations (note writer does LaTeX
  directly), keep all matplotlib/mplhep rules unchanged
- [ ] `src/methodology/appendix-checklist.md`: update artifact file
  names for new phase structure
- [ ] `src/methodology/appendix-sessions.md`: update directory layout
  diagram for new structure

#### S-2.11 Deprecate postprocess_tex.py
- [ ] `src/conventions/postprocess_tex.py`: add deprecation header.
  Keep `fix_stale_phase_labels` and `fix_duplicate_labels` as optional
  diagnostics. Note that most functions addressed pandoc artifacts.

#### S-2.12 build-pdf pixi task
- [ ] `src/templates/pixi.toml`: add `build-pdf` task. With LaTeX-first
  this is essentially `tectonic <path>`. Create a small wrapper script
  that accepts a .tex path argument for flexibility.

#### S-2.13 Session naming
- [ ] `src/templates/root_claude.md`: add session name assignment block
  with name pool and naming convention for output files

#### S-2.14 Regression framework
- [ ] `src/methodology/06-review.md` §6.7: add UPDATE vs REWRITE
  decision framework
- [ ] `src/templates/root_claude.md`: add regression decision to
  orchestrator loop

---

### Stage 3: Consistency sweep

After Stage 2, systematic verification that no orphaned references
or contradictions remain.

- [ ] Grep all .md files for "Phase 5" — update or remove every reference
- [ ] Grep for "pandoc" — remove or update every reference
- [ ] Grep for "postprocess_tex" — mark as optional/legacy
- [ ] Grep for "typesetter" — update to note writer where appropriate
- [ ] Grep for "@fig:" / "@tbl:" / "@eq:" — replace with \ref{} guidance
- [ ] Grep for "build-pdf" — verify consistent with new pipeline
- [ ] Grep for "\$\\pm\$" and other pandoc pitfall patterns — remove warnings
- [ ] Verify `agents/README.md` activation matrix matches §6.2 review table
- [ ] Verify all templates reference correct methodology sections
- [ ] Read each agent prompt end-to-end for internal consistency
- [ ] Verify preamble.tex figure height defaults work with direct LaTeX
  (no postprocessor interaction)

---

## Files Touched (complete inventory)

### Modified
- `src/scaffold_analysis.py`
- `src/templates/root_claude.md`
- `src/templates/phase1_claude.md`
- `src/templates/phase2_claude.md`
- `src/templates/pixi.toml`
- `src/agents/arbiter.md`
- `src/agents/physics_reviewer.md`
- `src/agents/critical_reviewer.md`
- `src/agents/constructive_reviewer.md`
- `src/agents/executor.md`
- `src/agents/fixer.md`
- `src/agents/note_writer.md`
- `src/agents/plot_validator.md`
- `src/agents/rendering_reviewer.md`
- `src/agents/typesetter.md` (deprecation header)
- `src/agents/README.md`
- `src/methodology/03-phases.md`
- `src/methodology/03a-orchestration.md`
- `src/methodology/04-blinding.md`
- `src/methodology/05-artifacts.md`
- `src/methodology/06-review.md`
- `src/methodology/07-tools.md`
- `src/methodology/11-coding.md`
- `src/methodology/analysis-note.md`
- `src/methodology/appendix-plotting.md`
- `src/methodology/appendix-checklist.md`
- `src/methodology/appendix-sessions.md`
- `src/conventions/postprocess_tex.py` (deprecation header)
- `src/conventions/lint_plots.py`

### New
- `src/conventions/an_template.tex`
- `src/templates/phase4a_claude.md`
- `src/templates/phase4b_claude.md`
- `src/templates/phase4c_claude.md`
- `src/templates/doc4a_claude.md`
- `src/templates/doc4b_claude.md`
- `src/templates/doc4c_claude.md`

### Removed
- `src/templates/phase4_claude.md` (replaced by 4a/4b/4c)
- `src/templates/phase5_claude.md` (replaced by doc4a/4b/4c)
