# Phase 4: Inference

> Read `methodology/03-phases.md` → "Phase 4" for full requirements.
> Read `methodology/appendix-plotting.md` for figure standards.
> Read `methodology/04-blinding.md` for the blinding protocol.

You are building the statistical model and computing results for a
**{{analysis_type}}** analysis.

**Start in plan mode.** Before writing any code, produce a plan: what
systematics you will evaluate, what validation checks you will run, what
the artifact structure will be. Execute after the plan is set.

## Output artifacts and flow

**Both measurements and searches follow the same 4a → 4b → 4c structure:**
- **4a:** Statistical analysis — systematics, expected results. Executor
  (stats) → note writer (AN v1 with expected results) → typesetter
  (compile). Review includes BibTeX validation.
- **4b:** 10% data validation. Compare to expected. Executor (stats) →
  note writer (update AN with 10% results) → typesetter (compile for
  human gate). Review includes BibTeX validation. Human gate after review.
- **4c:** Full data. Compare to 10% and expected. Executor (stats) →
  note writer (update AN with full results).

**Typesetting at 4a/4b/4c.** Spawn the typesetter agent (read
`agents/typesetter.md` for the full prompt). The typesetter handles the
entire pipeline: pandoc → postprocess_tex.py → figure combining → compile
→ verify. Provide the phase-stamped filename (e.g.,
`ANALYSIS_NOTE_4a_v1.md`). The 4a/4b/4c PDFs are review inputs — they
must meet the same formatting standard as the final Phase 5 PDF.

| Sub-phase | Artifact | Review |
|-----------|----------|--------|
| 4a | `outputs/INFERENCE_EXPECTED.md` + `outputs/ANALYSIS_NOTE_4a_v1.{md,tex,pdf}` | 4-bot+bib |
| 4b | `outputs/INFERENCE_PARTIAL.md` + `outputs/ANALYSIS_NOTE_4b_v1.{md,tex,pdf}` | 4-bot+bib → human gate |
| 4c | `outputs/INFERENCE_OBSERVED.md` + `outputs/ANALYSIS_NOTE_4c_v1.{md,tex,pdf}` | 1-bot |

## Human gate (after 4b review)

After the 4b review panel returns PASS, present the **compiled PDF** and
the unblinding checklist to the human. Do NOT proceed to 4c without
explicit human approval.

The human may:
- **APPROVE** — proceed to 4c (full data)
- **ITERATE** — fix issues within 4b scope, re-review, re-present
- **REGRESS(N)** — fundamental issue traced to Phase N; follow the
  non-destructive regression protocol in `methodology/06-review.md` §6.6
- **PAUSE** — wait for external input

On regression: the Investigator assesses cascade scope, the executor
creates new artifact versions (not overwrites), downstream phases
re-evaluate, and the note writer produces a new AN version with a
cohesive narrative. Re-present the updated PDF to the human.

## Methodology references

- Phase requirements: `methodology/03-phases.md` → Phase 4
- Technique-specific requirements: `methodology/03-phases.md` → Phase 4 sub-phase descriptions
- Blinding: `methodology/04-blinding.md`
- Review protocol: `methodology/06-review.md` → §6.2 (4-bot / 1-bot), §6.4
- Goodness-of-fit: `methodology/03-phases.md` → Phase 4 GoF requirements
- Plotting: `methodology/appendix-plotting.md`

## RAG queries (mandatory)

Query the experiment corpus for:
1. Systematic evaluation methods used in reference analyses
2. Published measurements for comparison (use `compare_measurements` for
   cross-experiment results)
3. Theory predictions or MC generator comparisons for the observable

Cite sources in the artifact.

## Applicable conventions

{{conventions_files}}

Re-read these before finalizing systematics.

## Key requirements

These are the critical items for Phase 4. See
`methodology/03-phases.md` → Phase 4 for full details.

- **Systematic completeness table.** Compare your implemented sources
  against the reference analyses from Phase 1 and the applicable
  `conventions/` files (see root CLAUDE.md → Conventions for which files
  apply). Format: `| Source | Conventions | Ref 1 | Ref 2 | This | Status |`.
  Any MISSING source without justification is a blocker. In particular,
  any source listed in the Phase 1 conventions enumeration as "Will
  implement" that is absent here is Category A (must resolve before
  advancing).
- **Statistical model construction.** Build a binned likelihood with all
  samples, Asimov data (pseudo-data generated under the background-only or
  nominal hypothesis), and systematic terms as nuisance parameters (NPs —
  parameters that encode systematic uncertainties in the fit). Validate:
  NP pulls small, fit converges, results physically sensible.
- **Fit validation.** Signal injection tests (searches) or closure tests
  (measurements) to confirm the model recovers known inputs.
- **Goodness-of-fit.** Report **both** chi2/ndf (quick assessment) **and**
  toy-based p-value using the saturated model GoF statistic (the saturated
  model treats each bin as an independent parameter — standard reference in
  pyhf/HistFactory). For pure counting extractions without a binned fit,
  use chi2 across bins or subperiods instead. chi2/ndf ~ 1 is good; >>1
  indicates mismodeling; <<1 indicates overestimated uncertainties.
- **Expected results on Asimov/MC only.** Phase 4a results must come from
  pseudo-data — never real data.
- **MC coverage must match data.** Do not derive MC-dependent quantities
  (efficiencies, corrections, scale factors) for data-taking periods that
  lack corresponding MC simulation. If MC covers only one period, either
  restrict the measurement to that period or justify (with evidence) that
  the MC is applicable to other periods. Silently extrapolating MC-derived
  corrections to uncovered periods underestimates uncertainties.

  **General principle:** when any MC-derived quantity is applied beyond
  the conditions it was derived from (different periods, different
  detector configurations, different kinematic regions), the
  uncertainties on the result must reflect the extrapolation. A
  per-subset consistency plot where all points carry identical
  uncertainties despite unequal MC coverage is a red flag.
- **Covariance matrix (measurements).** Full bin-to-bin covariance
  (statistical + each systematic + total) in the artifact and as
  machine-readable files.
- **Theory comparison (measurements).** Compare to at least one theory
  prediction or MC generator using the full covariance. If none available,
  justify and compare to published measurements.

**For extraction measurements:** read `conventions/extraction.md` for
additional required checks (independent closure test, parameter sensitivity
table, operating point stability, per-subperiod consistency, 10% diagnostic
sensitivity). These are technique-specific requirements defined in the
conventions file — do not skip them.

## Pre-review self-check

Before submitting for review, verify:

- [ ] Systematic completeness table: every conventions source + every
      reference analysis source, row-by-row
- [ ] Every systematic has measured/cited variation size (not arbitrary
      round numbers — ±50% requires measured justification)
- [ ] No flat borrowed systematics (unless all 3 conditions documented:
      confirmed subdominant + propagation infeasible + cited measurement)
- [ ] Signal injection or closure test passes
- [ ] GoF: chi2/ndf AND toy-based p-value both reported
- [ ] Covariance matrix validated (PSD, reasonable condition number)
- [ ] Per-systematic documentation: running prose with physical origin,
      evaluation method, numerical impact, interpretation
- [ ] AN draft complete with PDF compiled (4a, 4b)
- [ ] For extraction: all `conventions/extraction.md` checks completed
- [ ] All figures pass plotting rules (see Phase 2 quick reference)
- [ ] Validation target check: results compared to PDG/references,
      any pull > 3-sigma or deviation > 30% triggers investigation (§6.8)
- [ ] Phase 1 traceability: re-read STRATEGY.md, verify every committed
      systematic/variation was implemented or formally downscoped ([D] label)
- [ ] Zero-systematic sanity: no source has impact exactly 0 without
      verified non-trivial variation input (0 = likely broken, not negligible)

Also check `methodology/appendix-checklist.md` for the full artifact and
AN completeness checklists.

**Your reviewer will check** (§6.4): Systematics complete vs conventions +
references? Variation sizes justified? Signal injection/closure passes?
MC coverage matches data? Validation targets (§6.8)?

## Review

**Review is mandatory at all three sub-phases — 4a, 4b, and 4c.**

| Sub-phase | Review tier | Panel composition | Then |
|-----------|-------------|-------------------|------|
| 4a | 4-bot+bib | physics + critical + constructive + plot validator + bibtex | arbiter |
| 4b | 4-bot+bib | physics + critical + constructive + plot validator + bibtex | arbiter → human gate |
| 4c | 1-bot | critical + plot validator | (no arbiter) |

4b is NOT "human gate only" — it gets the full 4-bot+bib review panel
first, then the human gate after the arbiter returns PASS. 4c is NOT
unreviewed — it gets 1-bot (critical + plot validator). Skipping or
omitting these reviews is a process failure.

See `methodology/06-review.md` for protocol. Write findings to
`review/{role}/` using session-named files (see
`methodology/appendix-sessions.md` for naming conventions).
