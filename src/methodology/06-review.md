## 6. Review Protocol

Review is mandatory at every phase gate. Skipping review is a process failure.

### 6.1 Classification

- **(A) Must resolve** — blocks advancement.
- **(B) Should address** — weakens the analysis. Must fix before PASS.
- **(C) Suggestions** — style, clarity.

### 6.2 Review Tiers

| Phase | Type | Notes |
|-------|------|-------|
| 1: Strategy | 4-bot | Sets direction; physics errors propagate |
| 2: Exploration | Self-review | Mechanical; errors caught in Phase 3 |
| 3: Processing | 1-bot | External eye on closure/modeling |
| 4a: Expected | 4-bot | Gates 10% validation |
| 4b: 10% validation | 4-bot → human gate | Draft AN must be polished |
| 4c: Full data | 1-bot | Methodology already human-approved |
| 5: Documentation | 5-bot (4 + rendering) | Final product |

**4-bot:** Physics + critical + constructive reviewers (parallel), then
arbiter. Physics reviewer receives ONLY physics prompt + artifact. See
`appendix-prompts.md` for literal prompts.

**5-bot:** Adds rendering reviewer who runs `pixi run build-pdf` and
inspects the compiled PDF.

**1-bot:** Single critical reviewer. Category A items → fix → re-submit.

**No self-review fallback.** All phases except Phase 2 require independent
reviewer subagents.

### 6.3 Reviewer Framing

The key question: **"What would a knowledgeable referee ask for that isn't
here?"** Check external completeness, not just internal consistency.

Before concluding, the reviewer must answer:
1. Are all sources in the applicable `conventions/` document implemented
   or justified as inapplicable?
2. Do 2-3 reference analyses exist, and does this analysis match their
   systematic coverage?
3. If a competing group published next month, what would they have that
   we don't?

"No" or "non-empty" without justification → Category A.

### 6.4 Review Focus by Phase

| Phase | Focus |
|-------|-------|
| Strategy | Backgrounds complete? Systematic plan covers conventions? 2-3 reference analyses tabulated? |
| Exploration | Samples complete? Data quality OK? Distributions physical? |
| Processing | Background model closes? Every cut motivated by plot? Cutflow monotonic? **MVA:** data/MC on classifier OK? Alternative architecture tried? |
| 4a: Expected | Systematics complete vs. conventions + references? Signal injection/closure passes? Operating point stable (Category A if not)? MC coverage matches data periods? |
| 4b: 10% | Draft AN publication-quality? Results consistent with expected? Diagnostics clean? |
| 4c: Full data | Post-fit diagnostics healthy? Anomalies characterized? |
| 5: Documentation | See §6.4.3. |

#### 6.4.1 Completeness Review (Phases 1 and 4a)

**Phase 1:** Verify systematic plan covers conventions sources. Reference
analysis table present. Omissions without justification → Category A.

**Phase 4a:** Executor must produce a **systematic completeness table:**

```
| Source | Conventions | Ref 1 | Ref 2 | This analysis | Status |
```

Reviewer verifies row-by-row. MISSING without justification → Category A.
Cross-check conventions "required validation checks" against the artifact.

#### 6.4.2 Figure Review

**Reviewers must read every plot** and verify it makes physical sense. See
`appendix-plotting.md` for the complete figure checklist and standards.
Key Category A items: wrong metadata (√s, experiment, luminosity), missing
axis labels, no figure titles, clipped content, inappropriate scales.

#### 6.4.3 Documentation Review (Phase 5)

Reviewer reads the AN as a standalone document — as a journal referee would.
Check: every systematic described with method + impact? Every comparison
quantitative? Reproducible from the note alone? Conventions covered?

### 6.5 Iteration and Escalation

**4/5-bot:** Repeat until arbiter PASS. Warn at 3, strong warn at 5, hard
cap at 10. The arbiter should ESCALATE rather than loop indefinitely.

**1-bot:** Warn at 2, escalate to human after 3.

### 6.6 Human Gate

Between Phase 4b and 4c for both measurements and searches. The human
receives a publication-quality draft AN with 10% results. Approves,
requests changes, or halts.

### 6.7 Phase Regression

**Regression must be triggered, not avoided.** Do not paper over upstream
problems. Concrete triggers (must not be rationalized away):
- Data/MC disagreement on observable or MVA inputs
- Closure test failure (p < 0.05)
- Operating point instability
- Unexplained dominant systematic
- MC used for periods without corresponding simulation

**Procedure:**
1. Document issue, identify origin phase
2. Classify as regression trigger in review artifact
3. Orchestrator spawns **Investigator**: reads trigger → reads origin
   artifact → traces forward to identify affected phases →
   produces `REGRESSION_TICKET.md`
4. Fix origin phase → re-review → re-run affected downstream phases

**Timing:** Regression only before the human gate. After human approval,
issues become Phase 5 iteration items.

**Not regression:** Presentation issues (labels, captions, formatting) →
Phase 5 iteration, not regression.

**Upstream feedback (non-blocking):** Any executor may produce
`UPSTREAM_FEEDBACK.md` for issues an earlier phase missed. Routed to the
next review gate.

---
