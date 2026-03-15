## 4. Blinding Protocol

Blinding prevents the analyst (human or agent) from tuning the analysis to
produce a desired result in the signal region. The protocol is procedural,
with staged unblinding.

**What is blinded:** The distribution of the final discriminant variable (the
variable used for statistical inference — e.g., invariant mass, BDT output
score) in the signal region. Other distributions in the signal region (control
variables, event counts in sidebands) may be examined for debugging and
validation purposes.

### 4.1 Blinding Stages

**Fully blinded (Phases 1–3):** The signal region discriminant distribution in
data is not examined. Background estimates in the SR rely on extrapolation from
control regions or simulation.

**Asimov-only (Phase 4, expected results):** Expected limits and sensitivity
use Asimov data (background-only pseudo-data). Signal injection tests use
pseudo-data at known signal strengths.

**Partial unblinding — 10% data (Phase 4, agent-gated):** After the expected
results and fit validation pass rigorous agent review (see Section 4.2), the
agent performs a partial unblinding using a 10% random subsample of the SR data.
This is a standard HEP practice that provides a meaningful but low-stakes
reality check — the results will have large statistical uncertainties but will
expose any gross modeling failures (wrong background normalization, misshapen
discriminant, fit pathologies) that Asimov data cannot reveal.

The agent:
- Selects 10% of SR data events using a fixed random seed for reproducibility
- Scales MC predictions to match the luminosity fraction of the data subsample
  (i.e., MC is normalized to the luminosity corresponding to 10% of data, not
  to 10% of MC events). This is standard practice — MC is always normalized to
  the luminosity of the data being compared.
- Runs the full fit on this subsample with the appropriately scaled MC
- Evaluates goodness-of-fit, nuisance parameter pulls, and impact ranking
- Compares observed and expected results — they should be statistically
  compatible given the large uncertainties
- Documents any discrepancies and their likely explanations
- If problems are found, fixes them *before* seeing more data, then re-runs
  the partial unblinding

**Full unblinding (Phase 4, human-gated):** After partial unblinding succeeds,
the agent produces a near-final analysis note including the 10% observed
results and presents it to a human reviewer. The human sees an essentially
complete product — methodology, validation, and weak but real results — and
decides whether to proceed to full unblinding. See Section 4.3.

**Post-unblinding:** The full observed result is computed. Post-unblinding
modifications must be explicitly documented and justified.

### 4.2 Agent Gate: Earning Partial Unblinding

The agent does not proceed to partial unblinding until the analysis passes a
rigorous multi-reviewer process. This is the agent's internal quality bar —
it must be high enough that a senior physicist would be comfortable with the
analysis as presented.

The review structure for the pre-unblinding assessment:

1. **Critical reviewer ("bad cop"):** Reviews the analysis artifacts with the
   goal of finding flaws. Looks for incomplete background estimates, missing
   systematics, unjustified assumptions, potential biases, and any way the
   analysis could produce a misleading result. Every issue is a potential
   Category A.

2. **Constructive reviewer ("good cop"):** Reviews the analysis with the goal
   of strengthening it. Identifies areas where the argument could be clearer,
   where additional validation would build confidence, and where the
   presentation could be improved. Focuses on Category B and C issues but
   escalates to A if warranted.

3. **Arbiter:** Reads both reviews and the original artifacts. Adjudicates
   disagreements between reviewers. Produces a final assessment with a clear
   PASS / ITERATE / ESCALATE decision.

This cycle repeats until the arbiter issues a PASS with no unresolved Category A
items. Correctness is the termination condition, not an iteration count. (The
orchestrator imposes a configurable hard cap as a safety net — see Section 6.8.
In practice, if the cycle hasn't converged after 3-4 rounds, the issues are
likely fundamental enough to require human input, and the arbiter should
escalate.)

Only after PASS does the agent proceed to partial unblinding.

### 4.3 Human Gate: Approving Full Unblinding

After partial unblinding, the agent produces and presents to a human:

- The draft analysis note, now including 10% observed results, post-fit
  diagnostics, and goodness-of-fit assessment
- The unblinding checklist:
  1. Background model validated (closure tests pass in all VRs)
  2. Systematic uncertainties evaluated and fit model stable
  3. Expected results physically sensible
  4. Signal injection tests confirm fit recovers injected signals
  5. 10% partial unblinding shows no unexpected pathologies
  6. All agent review cycles resolved (arbiter PASS)
  7. Draft analysis note reviewed and considered publication-ready modulo
     full observed results

The human reviews the complete package and either approves full unblinding,
requests changes, or halts the analysis. The agent does not fully unblind
autonomously.

---
