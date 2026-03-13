"""Prompt construction for each agent role."""

from pathlib import Path

from .artifacts import artifact_filename, timestamp_str

# Phase instructions — minimal "must do" lists extracted from the methodology.
# The full methodology is in the system prompt; these focus the task.
PHASE_INSTRUCTIONS = {
    "phase1_strategy": """\
Develop the analysis strategy. You must produce a strategy artifact containing:
- Signal and background process enumeration with expected cross-sections
- Selection approach (cut-based, MVA, or hybrid) with justification
- Region definitions (signal region, control regions, validation regions)
- Blinding plan
- Systematic uncertainty categories (experimental, theory, modeling)
- Literature review with citations from the RAG corpus

Read the physics prompt for the analysis goal. Query the RAG corpus for
relevant prior analyses, detector performance, and object definitions.""",

    "phase2_exploration": """\
Explore the data and MC samples. You must produce an exploration artifact containing:
- Sample inventory (files, trees, branches, event counts)
- Data quality assessment (missing branches, anomalous distributions)
- Key variable distributions with data/MC comparisons
- Variable ranking for discrimination power
- Preselection cutflow
- Preliminary object definitions

This is exploratory — try things, plot distributions, build intuition.
Append findings to the experiment log as you go.""",

    "phase3_selection": """\
Develop the event selection and background model for your assigned channel.
You must produce a selection artifact containing:
- Final object definitions with calibrations applied
- Signal region selection (cut-based or MVA) with optimization
- Control region definitions with validation
- Background estimation method and closure tests
- Cutflow table with data and MC yields
- Systematic variation impact on yields

Read upstream artifacts (strategy, exploration) and any calibration artifacts.""",

    "phase3_consolidate": """\
Consolidate per-channel selection results into a combined selection artifact.
Read all channel artifacts, check for consistency, and produce a unified
summary with combined cutflows and region definitions.""",

    "phase4a_expected": """\
Build the statistical model and compute expected results (Asimov dataset only).
You must produce an inference artifact containing:
- pyhf workspace (JSON) with all regions, samples, and systematics
- Expected significance and/or expected limits
- Systematic uncertainty ranking (impact plot)
- Signal injection tests (inject signal, recover it)
- Fit diagnostics on Asimov (pulls, constraints, correlations)

Do NOT use real data. All results must be computed on Asimov datasets.""",

    "phase4b_partial": """\
Run the analysis on 10% of real data (partial unblinding). Scale MC predictions
to match the luminosity fraction of the data subsample. You must produce:
- Observed fit results on the 10% subsample
- Post-fit diagnostics (pulls, GoF, residuals)
- Data/MC comparisons in all regions
- Anomaly assessment: any unexpected features?
- Draft analysis note covering all phases so far

Flag any significant discrepancies between expected and observed.""",

    "phase4c_observed": """\
Run the full unblinding on the complete dataset. You must produce:
- Final observed fit results
- Post-fit diagnostics on full data
- Final data/MC comparisons
- Anomaly assessment
- Updated analysis note with final results""",

    "phase5_documentation": """\
Produce the final analysis note. This is a complete document suitable for
internal review, containing:
- Abstract and introduction
- Data and MC samples
- Object definitions and calibrations
- Event selection and background estimation
- Systematic uncertainties
- Statistical analysis and results
- Discussion and future directions (see Section 12.5 — collect all
  downscoping decisions into a concrete roadmap of what to improve next,
  with quantitative estimates where possible)
- Conclusions
- All figures and tables
- Complete bibliography from RAG corpus""",
}


def _identity_block(session_name: str) -> str:
    ts = timestamp_str()
    return f"""\
=== SESSION IDENTITY ===
You are {session_name}. Timestamp: {ts}.
Name all output files as: {{ARTIFACT}}_{session_name}_{ts}.md
Append to experiment_log.md with entries prefixed [{session_name}]."""


def _data_paths_block(data_paths: dict) -> str:
    if not data_paths:
        return ""
    lines = ["=== DATA PATHS ==="]
    for name, path in data_paths.items():
        if isinstance(path, dict):
            for sub, p in path.items():
                lines.append(f"- {name}/{sub}: {p}")
        else:
            lines.append(f"- {name}: {path}")
    return "\n".join(lines)


def build_executor_prompt(
    *,
    session_name: str,
    phase: str,
    data_paths: dict,
    upstream_artifacts: list[str] | None = None,
    iteration: int | None = None,
    review_feedback_path: str | None = None,
) -> str:
    """Build the prompt for an executor agent."""
    parts = [
        _identity_block(session_name),
        "",
        "=== YOUR ROLE ===",
        "You are an executor. Carry out the analysis task described below.",
        "Write code, produce plots, and generate the phase artifact.",
        "",
        "=== CRITICAL: PROTOTYPE FIRST ===",
        "NEVER run on the full dataset first. Develop and validate every script",
        "on a small subset (~1000 events or a single file). Only scale up once",
        "the logic is confirmed working. If a step takes more than a few minutes,",
        "you are probably processing too much data too early. The full dataset is",
        "for production runs, not for debugging.",
        "",
        "=== READ THE API, DON'T HACK AROUND IT ===",
        "When a library behaves unexpectedly, read the docstring or docs FIRST.",
        "Do NOT write workarounds for behavior that has a documented parameter.",
        "Run help(function) before adding post-hoc fixups. If the tool has an",
        "entry in Appendix C (Tool Heuristics), check it. If not, read the docs,",
        "solve it properly, and add the idiom to Appendix C.",
        "",
        "=== DOWNSCOPE, DON'T BLOCK ===",
        "If a resource is unavailable (missing MC, no GPU, insufficient stats,",
        "inaccessible data), downscope to the best achievable method and document",
        "the limitation. A finished analysis with a simpler method is always better",
        "than an unfinished one. Log constraints in the experiment log, quantify",
        "the impact where possible, and flag it for future directions.",
        "",
        "=== PHASE INSTRUCTIONS ===",
        PHASE_INSTRUCTIONS.get(phase, f"Execute {phase}."),
        "",
        _data_paths_block(data_paths),
    ]

    if upstream_artifacts:
        parts.append("\n=== INPUTS ===")
        parts.append("Read these files before beginning:")
        for p in upstream_artifacts:
            parts.append(f"- {p}")

    if iteration and review_feedback_path:
        parts.append(f"\n=== ITERATION {iteration} ===")
        parts.append(
            f"Your previous artifact was reviewed. Read the review feedback at:"
        )
        parts.append(f"- {review_feedback_path}")
        parts.append("Address all Category A issues listed in the review.")

    return "\n".join(parts)


def build_critical_reviewer_prompt(
    *,
    session_name: str,
    phase_dir: str,
) -> str:
    return f"""\
{_identity_block(session_name)}

=== YOUR ROLE ===
You are a critical reviewer (the Critic). Your job is to find flaws.

Review the executor's artifact and code in {phase_dir}/.
Focus exclusively on problems:
- Category A (must fix): Bugs, physics errors, broken analysis logic,
  missing required components, results that cannot be trusted.
- Category B (should fix): Suboptimal choices, missing cross-checks,
  unclear documentation, style issues.

If you find that a problem originates in an upstream phase (not this one),
flag it as a "regression trigger" with the origin phase name.

Write your review to {phase_dir}/review/
End with a summary: list of Category A issues, list of Category B issues."""


def build_constructive_reviewer_prompt(
    *,
    session_name: str,
    phase_dir: str,
) -> str:
    return f"""\
{_identity_block(session_name)}

=== YOUR ROLE ===
You are a constructive reviewer (the Advocate). Your job is to see the good
and suggest improvements.

Review the executor's artifact and code in {phase_dir}/.
- What works well?
- What could be improved without being a blocker?
- Are there alternative approaches worth considering?
- Any physics insights or cross-checks that could strengthen the result?

Write your review to {phase_dir}/review/"""


def build_arbiter_prompt(
    *,
    session_name: str,
    phase_dir: str,
    critical_review_path: str,
    constructive_review_path: str,
) -> str:
    return f"""\
{_identity_block(session_name)}

=== YOUR ROLE ===
You are the arbiter. You read the executor's work and both reviews,
then make a decision.

Read:
- The executor's artifact in {phase_dir}/
- Critical review: {critical_review_path}
- Constructive review: {constructive_review_path}

Decide:
- PASS: The work is sound. Category A issues (if any) are false positives.
- ITERATE: Real Category A issues exist. Summarize exactly what must be fixed.
- ESCALATE: Fundamental problems that require human intervention.

End your assessment with exactly one of: PASS, ITERATE, or ESCALATE
on its own line.

Write your assessment to {phase_dir}/review/"""


def build_investigator_prompt(
    *,
    session_name: str,
    regression_source_dir: str,
    trigger_review_path: str,
) -> str:
    return f"""\
{_identity_block(session_name)}

=== YOUR ROLE ===
You are an investigator. A downstream review flagged a regression originating
in {regression_source_dir}.

Read the regression trigger at: {trigger_review_path}
Investigate the origin phase code and artifact in {regression_source_dir}/.

Produce a scoped regression ticket:
- What is broken and why
- What specifically needs to change
- What downstream phases will need to re-run

Write to {regression_source_dir}/REGRESSION_TICKET.md"""
