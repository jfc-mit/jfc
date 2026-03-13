"""Top-level pipeline — phases 1-5 with gates, reviews, and regression handling."""

import asyncio
import subprocess
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from .artifacts import find_latest_artifact
from .config import AnalysisConfig, resolve_model
from .names import NamePool
from .prompts import build_executor_prompt, build_investigator_prompt
from .review import ReviewOutcome, run_1bot_review, run_3bot_review
from .sessions import CostTracker, run_agent

console = Console()


def _load_system_prompt(config: AnalysisConfig) -> str:
    """Load methodology.md as the system prompt for all agents."""
    path = Path(config.methodology_path)
    if not path.exists():
        raise FileNotFoundError(f"Methodology file not found: {path}")
    return path.read_text()


def _git(cmd: str, cwd: str):
    """Run a git command if git is enabled."""
    subprocess.run(["git"] + cmd.split(), cwd=cwd, check=True, capture_output=True)


def _find_upstream_artifacts(config: AnalysisConfig, phase: str) -> list[str]:
    """Find artifacts from upstream phases that should be read."""
    base = config.base_dir
    artifacts = []

    # Physics prompt is always an input
    if Path(config.physics_prompt_path).exists():
        artifacts.append(config.physics_prompt_path)

    # Phase-specific upstream dependencies
    if phase.startswith("phase2"):
        a = find_latest_artifact(base / "phase1_strategy", "STRATEGY_*.md")
        if a:
            artifacts.append(str(a))

    elif phase.startswith("phase3"):
        for prev in ["phase1_strategy", "phase2_exploration"]:
            a = find_latest_artifact(base / prev, "*.md")
            if a:
                artifacts.append(str(a))
        # Calibration artifacts
        cal_dir = base / "calibrations"
        if cal_dir.exists():
            for cal in cal_dir.iterdir():
                a = find_latest_artifact(cal, "*.md")
                if a:
                    artifacts.append(str(a))

    elif phase.startswith("phase4"):
        for prev in ["phase1_strategy", "phase3_selection"]:
            a = find_latest_artifact(base / prev, "*.md")
            if a:
                artifacts.append(str(a))

    elif phase.startswith("phase5"):
        # Documentation reads everything
        for d in base.iterdir():
            if d.is_dir() and d.name.startswith("phase"):
                a = find_latest_artifact(d, "*.md")
                if a:
                    artifacts.append(str(a))

    return artifacts


async def _run_phase(
    phase: str,
    phase_dir: str,
    config: AnalysisConfig,
    name_pool: NamePool,
    cost_tracker: CostTracker,
    system_prompt: str,
    model_role: str = "executor_default",
):
    """Run a single executor phase."""
    exec_name = name_pool.pick()
    upstream = _find_upstream_artifacts(config, phase)

    console.print(f"\n[bold blue]Phase: {phase}[/bold blue]")
    result = await run_agent(
        name=exec_name,
        prompt=build_executor_prompt(
            session_name=exec_name,
            phase=phase,
            data_paths=config.data_paths,
            upstream_artifacts=upstream,
        ),
        model=resolve_model(config, model_role),
        cwd=phase_dir,
        system_prompt=system_prompt,
    )
    cost_tracker.add(exec_name, result)
    return result


def _handle_outcome(
    outcome: ReviewOutcome,
    phase_name: str,
    fatal_on_fail: bool = False,
):
    """Handle review outcome — raise on fatal failures."""
    if outcome.status == "pass":
        console.print(
            f"  [green]Review passed[/green] after {outcome.iterations} iteration(s)"
        )
        return

    if outcome.status == "regression":
        console.print(
            f"  [yellow]Regression detected[/yellow] — origin: "
            f"{outcome.regression_origin}"
        )
        # Regression handling would re-run origin phase + downstream
        # For now, raise to halt the pipeline
        raise RuntimeError(
            f"Regression in {phase_name} from {outcome.regression_origin}. "
            f"Manual intervention required."
        )

    if outcome.status == "escalated":
        msg = (
            f"Review escalated for {phase_name} after "
            f"{outcome.iterations} iteration(s)"
        )
        if fatal_on_fail:
            raise RuntimeError(msg + " — cannot proceed.")
        console.print(f"  [bold red]{msg}[/bold red]")


async def _human_gate(phase_dir: str) -> str:
    """Pause for human review. Returns the decision."""
    console.print(
        Panel(
            f"[bold]Human gate reached.[/bold]\n\n"
            f"Review the artifacts in:\n  {phase_dir}\n\n"
            f"Options: APPROVE / REQUEST_CHANGES / HALT",
            title="Human Review Required",
            border_style="red",
        )
    )

    while True:
        decision = input("\nDecision: ").strip().upper()
        if decision in ("APPROVE", "REQUEST_CHANGES", "HALT"):
            return decision
        console.print("[red]Invalid. Enter APPROVE, REQUEST_CHANGES, or HALT.[/red]")


async def run_pipeline(config: AnalysisConfig) -> None:
    """Run the full analysis pipeline."""
    name_pool = NamePool(seed=42)
    cost_tracker = CostTracker()
    system_prompt = _load_system_prompt(config)
    base = str(config.base_dir)

    console.print(Panel(f"[bold]slopspec: {config.analysis_name}[/bold]"))

    # --- Phase 1: Strategy (opus, 3-bot review) ---
    phase1_dir = f"{base}/phase1_strategy"
    await _run_phase(
        "phase1_strategy", phase1_dir, config, name_pool,
        cost_tracker, system_prompt, model_role="executor_strategy",
    )
    outcome = await run_3bot_review(
        phase1_dir, config, name_pool, cost_tracker, system_prompt,
    )
    _handle_outcome(outcome, "phase1_strategy")
    if config.git_enabled:
        _git("merge phase1_strategy", base)

    # --- Phase 2: Exploration (sonnet, self-review) ---
    phase2_dir = f"{base}/phase2_exploration"
    await _run_phase(
        "phase2_exploration", phase2_dir, config, name_pool,
        cost_tracker, system_prompt,
    )
    console.print("  [dim]Self-review only — no external review gate[/dim]")
    if config.git_enabled:
        _git("merge phase2_exploration", base)

    # --- Calibrations + Phase 3 channels (parallel) ---
    cal_tasks = []
    for cal in config.calibrations:
        cal_dir = f"{base}/calibrations/{cal}"
        cal_tasks.append(
            _run_phase(
                f"calibration_{cal}", cal_dir, config, name_pool,
                cost_tracker, system_prompt, model_role="calibration",
            )
        )

    ch_tasks = []
    for ch in config.channels:
        ch_dir = f"{base}/phase3_selection/channel_{ch}"
        ch_tasks.append(
            _run_phase(
                "phase3_selection", ch_dir, config, name_pool,
                cost_tracker, system_prompt,
            )
        )

    if cal_tasks or ch_tasks:
        console.print(
            f"\n[bold blue]Running {len(cal_tasks)} calibrations + "
            f"{len(ch_tasks)} channels in parallel[/bold blue]"
        )
        await asyncio.gather(*cal_tasks, *ch_tasks)

    # Sequential 1-bot review per channel
    for ch in config.channels:
        ch_dir = f"{base}/phase3_selection/channel_{ch}"
        outcome = await run_1bot_review(
            ch_dir, config, name_pool, cost_tracker, system_prompt,
        )
        _handle_outcome(outcome, f"phase3/{ch}")

    # Consolidate channels
    phase3_dir = f"{base}/phase3_selection"
    await _run_phase(
        "phase3_consolidate", phase3_dir, config, name_pool,
        cost_tracker, system_prompt,
    )
    if config.git_enabled:
        _git("merge phase3_selection", base)

    # Budget check
    if cost_tracker.check_budget(
        config.cost_controls.total_budget_warn,
        config.cost_controls.on_budget_exceeded,
    ):
        decision = await _human_gate(base)
        if decision == "HALT":
            console.print("[red]Pipeline halted by user at budget check.[/red]")
            return

    # --- Phase 4a: Expected inference (agent gate — must pass) ---
    phase4a_dir = f"{base}/phase4_inference/4a_expected"
    await _run_phase(
        "phase4a_expected", phase4a_dir, config, name_pool,
        cost_tracker, system_prompt,
    )
    outcome = await run_3bot_review(
        phase4a_dir, config, name_pool, cost_tracker, system_prompt,
    )
    _handle_outcome(outcome, "phase4a_expected", fatal_on_fail=True)
    if config.git_enabled:
        _git("merge phase4a_expected", base)

    # --- Phase 4b: Partial unblinding (3-bot review + human gate) ---
    phase4b_dir = f"{base}/phase4_inference/4b_partial"
    await _run_phase(
        "phase4b_partial", phase4b_dir, config, name_pool,
        cost_tracker, system_prompt,
    )
    outcome = await run_3bot_review(
        phase4b_dir, config, name_pool, cost_tracker, system_prompt,
    )
    _handle_outcome(outcome, "phase4b_partial")

    decision = await _human_gate(phase4b_dir)
    if decision == "HALT":
        console.print("[red]Pipeline halted by human at partial unblinding.[/red]")
        return
    if decision == "REQUEST_CHANGES":
        console.print("[yellow]Human requested changes — re-run phase 4b.[/yellow]")
        # For now, just halt. Full implementation would loop.
        return

    if config.git_enabled:
        _git("merge phase4b_partial", base)

    # --- Phase 4c: Full unblinding (1-bot review) ---
    phase4c_dir = f"{base}/phase4_inference/4c_observed"
    await _run_phase(
        "phase4c_observed", phase4c_dir, config, name_pool,
        cost_tracker, system_prompt,
    )
    outcome = await run_1bot_review(
        phase4c_dir, config, name_pool, cost_tracker, system_prompt,
    )
    _handle_outcome(outcome, "phase4c_observed")
    if config.git_enabled:
        _git("merge phase4c_observed", base)

    # --- Phase 5: Documentation (3-bot review) ---
    phase5_dir = f"{base}/phase5_documentation"
    await _run_phase(
        "phase5_documentation", phase5_dir, config, name_pool,
        cost_tracker, system_prompt,
    )
    outcome = await run_3bot_review(
        phase5_dir, config, name_pool, cost_tracker, system_prompt,
    )
    _handle_outcome(outcome, "phase5_documentation")
    if config.git_enabled:
        _git("merge phase5_documentation", base)

    # --- Done ---
    console.print(
        Panel(
            f"[bold green]Pipeline complete.[/bold green]\n\n"
            f"Total cost: ${cost_tracker.total_usd:.2f}\n"
            f"Sessions: {len(cost_tracker.sessions)}",
            title="slopspec complete",
        )
    )
