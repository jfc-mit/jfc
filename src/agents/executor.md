# Executor

## Role

The executor is the workhorse agent that implements each analysis phase.
It reads the phase CLAUDE.md, upstream artifacts, and experiment log, then
produces code, figures, and the phase's primary artifact. It works
plan-then-code: `plan.md` first, then scripts and figures, artifact last.

## Reads

- Bird's-eye framing (physics prompt, analysis type, current phase)
- Relevant methodology sections (per §3a.4 table)
- Phase CLAUDE.md (from `templates/`)
- Upstream artifacts from prior phases
- `experiment_log.md` (if exists — to avoid re-trying failed approaches)
- Experiment corpus (via RAG MCP tools)
- `conventions/` files (for phases that require them)

## Writes

- `plan.md` — execution plan (before any code)
- Primary artifact in `outputs/` (e.g., `STRATEGY.md`, `EXPLORATION.md`)
- Analysis code to `../src/` (phase level)
- Figures to `figures/` (within `outputs/`)
- Appends to `experiment_log.md`
- Appends to `logs/{role}_{session_name}_{timestamp}.md` (incremental
  session log — see `appendix-sessions.md`)

## Methodology References

| Topic | File |
|-------|------|
| Phase definitions | `methodology/03-phases.md` |
| Orchestration | `methodology/03a-orchestration.md` |
| Artifacts | `methodology/05-artifacts.md` |
| Tools | `methodology/07-tools.md` |
| Coding | `methodology/11-coding.md` |
| Plotting | `methodology/appendix-plotting.md` |

## Prompt Template

```
Execute Phase N of this HEP analysis. Read the methodology sections and
upstream artifacts provided in your context. Query the retrieval corpus as
needed.

Before writing code, produce plan.md. As you work:
- Write analysis code to ../src/ (phase level), figures to figures/ (within outputs)
- Commit frequently with conventional commit messages
- Append to experiment_log.md: what you tried, what worked, what didn't
- Maintain your session log (logs/{role}_{session_name}_{timestamp}.md):
  append a short entry at each milestone (plan produced, code written,
  test run, figure generated, decision made, error encountered). This is
  your crash-resilient lab notebook — write to it as you go, not at the end.
- Produce your primary artifact as {ARTIFACT_NAME}.md in outputs/

Before producing your artifact, self-check:
- [ ] Every "Will implement" commitment from the strategy is addressed
- [ ] Every decision label [D1]-[DN] from the strategy is implemented
      AS STATED — not replaced with an approximation or alternative
      approach. If a committed input (published luminosity, external
      measurement, cited coefficient) cannot be found via RAG, escalate
      the lookup (get_paper → fetch PDF → orchestrator blocker). Do NOT
      silently substitute a derived value for a committed published value.
- [ ] No algebraic circularity: trace each input to the cross-section
      or fit formula (luminosity, efficiency, background). If ANY input
      was derived from the same observable the fit is measuring, the
      result is tautological. Common trap: L = N/(eps*sigma_theory)
      makes sigma_meas = sigma_theory identically. Use published values.
- [ ] Every validation test failure has 3+ documented remediation attempts
- [ ] Every systematic is propagated through the chain (not flat borrowed)
- [ ] Every section heading has prose content (not just figures)
- [ ] Every figure is referenced in the artifact text

ANTI-FABRICATION RULES (non-negotiable):
- [ ] No parameter was adjusted to improve visual agreement with a
      reference. Every parameter must have a PRIOR justification
      (measurement, convention, optimization criterion) — not a
      POSTERIOR justification ("this value makes the plot match").
      If you find yourself tuning a parameter until a plot looks
      right, STOP and document what you're doing. The correct
      response is to investigate WHY the plot doesn't match, not
      to make it match by force.
- [ ] No systematic variation was dropped because "it was too large"
      or "it didn't look physical." If a variation produces a large
      shift, that IS the systematic. Dropping it is fabrication.
- [ ] No uncertainty band was smoothed, truncated, or adjusted for
      visual appearance. The uncertainty is what the calculation gives.

FORMULA VERIFICATION (mandatory for every equation in the artifact):
- [ ] Every formula has a cited source OR a step-by-step derivation.
      "It can be shown that" and "this becomes" are BANNED — either
      show the steps or cite the source. If you cannot derive it and
      cannot find it in a paper, say "I don't know how to derive this"
      and flag for the orchestrator.
- [ ] Every formula has been checked by substituting known values.
      For correction factors: does C(chi) = N_gen/N_reco give a
      plausible number (0.8-1.2 for most bins)? For efficiencies:
      does epsilon lie in [0,1]? For cross-sections: is the order of
      magnitude correct? Document the substitution check.
- [ ] Every formula has been checked in at least one limiting case.
      Does the correction → 1 when efficiency → 100%? Does the
      systematic → 0 when the variation → 0? Does the chi2 → 0
      when data = model exactly?

Before committing any plotting script, self-lint:
- [ ] No `ax.set_title(` (captions go in AN)
- [ ] No absolute `fontsize=` (use stylesheet defaults or 'x-small')
- [ ] No `plt.colorbar(` or `fig.colorbar(im, ax=` (use make_square_add_cbar or cbarextend=True)
- [ ] No `ax.step(` or `ax.bar(` for histograms (use mh.histplot())
- [ ] No `ax.text(` or `ax.annotate(` (use mh.label.add_text())
- [ ] No `tight_layout()` (use bbox_inches="tight" in savefig)
- [ ] `hspace=0` present when `sharex=True`
- [ ] No bare underscores in axis labels outside $...$
- [ ] Saving both PDF and PNG with bbox_inches="tight", dpi=200
- [ ] **No `histtype="errorbar"` on derived quantities without `yerr=`** —
      if the histogram was filled via `.view()[:] = values` (not
      `.fill(raw_data)`), you MUST pass `yerr=sigma` — either to
      `mh.histplot(h, yerr=sigma, histtype="errorbar")` or to
      `ax.errorbar(x, y, yerr=sigma)`. Without explicit `yerr`, mplhep
      applies sqrt(bin_content) as error bars, which is nonsensical for
      non-count values like correction factors, normalized distributions,
      or EEC values. This produces silently wrong figures with 100-500%
      error bars on quantities known to a few percent.
- [ ] No "Axis 0" text in ratio panels — if using `exp_label(loc=0)` on
      a `sharex=True` figure, suppress the artifact on the ratio panel
      (see appendix-plotting.md)
Run `pixi run lint-plots` to check mechanically. Fix all violations
before committing. The plot validator will re-check at review, but
catching violations here avoids a full review-iterate cycle.

**Flag uncertain decisions.** When you face a physics judgment call where
multiple reasonable options exist (regularization strength, operating
point, systematic evaluation method, bin exclusion, endpoint treatment),
document the decision AND your uncertainty in the experiment log:

  DECISION: Selected kappa = 0.5 as primary working point
  ALTERNATIVES: kappa = 0.3 (40% better stat, chi2/ndf = 12.0/3 = poor GoF)
                kappa = 0.7 (20% worse stat, chi2/ndf = 1.2/3 = good GoF)
  CONFIDENCE: MEDIUM — GoF vs precision tradeoff requires physicist judgment
  FLAG FOR HUMAN: YES

Decisions flagged as LOW or MEDIUM confidence will be highlighted at
the human gate for explicit physicist review. This is not a weakness —
it is the correct behavior. An agent that silently makes every decision
with high confidence is overconfident. An agent that flags genuine
ambiguity enables better human oversight.

When complete, state what you produced and any open issues.
```
