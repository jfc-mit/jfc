"""Review loops — 3-bot and 1-bot review protocols."""

import asyncio
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console

from .artifacts import (
    extract_decision,
    extract_regression_origin,
    find_latest_artifact,
    review_has_category_a,
)
from .config import AnalysisConfig, resolve_model
from .names import NamePool
from .prompts import (
    build_arbiter_prompt,
    build_constructive_reviewer_prompt,
    build_critical_reviewer_prompt,
    build_executor_prompt,
)
from .sessions import CostTracker, run_agent

console = Console()


@dataclass
class ReviewOutcome:
    status: str  # "pass" | "regression" | "escalated"
    iterations: int = 0
    regression_origin: str | None = None


async def run_3bot_review(
    phase_dir: str,
    config: AnalysisConfig,
    name_pool: NamePool,
    cost_tracker: CostTracker,
    system_prompt: str,
) -> ReviewOutcome:
    """3-bot review: critical + constructive (parallel) -> arbiter -> decision loop."""
    max_iter = config.cost_controls.max_review_iterations
    warn_at = config.cost_controls.review_warn_threshold
    review_dir = str(Path(phase_dir) / "review")
    Path(review_dir).mkdir(parents=True, exist_ok=True)

    for i in range(1, max_iter + 1):
        if i == warn_at:
            console.print(
                f"[yellow]Review iteration {i}/{max_iter} for {phase_dir}[/yellow]"
            )
        if i > warn_at:
            console.print(
                f"[bold yellow]WARNING: Review iteration {i}/{max_iter} "
                f"for {phase_dir}[/bold yellow]"
            )

        # Spawn critical + constructive reviewers in parallel
        critic_name = name_pool.pick()
        advocate_name = name_pool.pick()

        critic_result, advocate_result = await asyncio.gather(
            run_agent(
                name=critic_name,
                prompt=build_critical_reviewer_prompt(
                    session_name=critic_name,
                    phase_dir=phase_dir,
                ),
                model=resolve_model(config, "reviewer_3bot"),
                cwd=review_dir,
                system_prompt=system_prompt,
                allowed_tools=["Read", "Write", "Glob", "Grep"],
            ),
            run_agent(
                name=advocate_name,
                prompt=build_constructive_reviewer_prompt(
                    session_name=advocate_name,
                    phase_dir=phase_dir,
                ),
                model=resolve_model(config, "reviewer_3bot"),
                cwd=review_dir,
                system_prompt=system_prompt,
                allowed_tools=["Read", "Write", "Glob", "Grep"],
            ),
        )
        cost_tracker.add(critic_name, critic_result)
        cost_tracker.add(advocate_name, advocate_result)

        # Find the review files just written
        critical_path = find_latest_artifact(review_dir, f"*{critic_name}*")
        constructive_path = find_latest_artifact(review_dir, f"*{advocate_name}*")

        # Arbiter reads both reviews and decides
        arbiter_name = name_pool.pick()
        arbiter_result = await run_agent(
            name=arbiter_name,
            prompt=build_arbiter_prompt(
                session_name=arbiter_name,
                phase_dir=phase_dir,
                critical_review_path=str(critical_path or review_dir),
                constructive_review_path=str(constructive_path or review_dir),
            ),
            model=resolve_model(config, "arbiter"),
            cwd=review_dir,
            system_prompt=system_prompt,
            allowed_tools=["Read", "Write", "Glob", "Grep"],
        )
        cost_tracker.add(arbiter_name, arbiter_result)

        # Extract decision
        arbiter_file = find_latest_artifact(review_dir, f"*{arbiter_name}*")
        if not arbiter_file:
            console.print("[red]Arbiter produced no artifact — escalating[/red]")
            return ReviewOutcome(status="escalated", iterations=i)

        decision = extract_decision(arbiter_file)
        console.print(
            f"  Arbiter {arbiter_name} decision: [bold]{decision}[/bold] "
            f"(iteration {i})"
        )

        if decision == "PASS":
            # Check for regression triggers in the critical review
            if critical_path:
                origin = extract_regression_origin(critical_path)
                if origin:
                    return ReviewOutcome(
                        status="regression",
                        iterations=i,
                        regression_origin=origin,
                    )
            return ReviewOutcome(status="pass", iterations=i)

        if decision == "ESCALATE":
            return ReviewOutcome(status="escalated", iterations=i)

        # ITERATE — run executor again with feedback
        exec_name = name_pool.pick()
        exec_result = await run_agent(
            name=exec_name,
            prompt=build_executor_prompt(
                session_name=exec_name,
                phase=Path(phase_dir).name,
                data_paths=config.data_paths,
                iteration=i + 1,
                review_feedback_path=str(arbiter_file),
            ),
            model=resolve_model(config, "executor_default"),
            cwd=phase_dir,
            system_prompt=system_prompt,
        )
        cost_tracker.add(exec_name, exec_result)

    # Hard cap reached
    console.print(
        f"[bold red]3-bot review hit hard cap ({max_iter} iterations) "
        f"for {phase_dir} — escalating to human[/bold red]"
    )
    return ReviewOutcome(status="escalated", iterations=max_iter)


async def run_1bot_review(
    phase_dir: str,
    config: AnalysisConfig,
    name_pool: NamePool,
    cost_tracker: CostTracker,
    system_prompt: str,
) -> ReviewOutcome:
    """1-bot review: single critical reviewer, no arbiter."""
    max_iter = config.cost_controls.max_review_iterations
    review_dir = str(Path(phase_dir) / "review")
    Path(review_dir).mkdir(parents=True, exist_ok=True)

    for i in range(1, max_iter + 1):
        if i > config.cost_controls.review_warn_threshold:
            console.print(
                f"[yellow]1-bot review iteration {i}/{max_iter} "
                f"for {phase_dir}[/yellow]"
            )

        reviewer_name = name_pool.pick()
        reviewer_result = await run_agent(
            name=reviewer_name,
            prompt=build_critical_reviewer_prompt(
                session_name=reviewer_name,
                phase_dir=phase_dir,
            ),
            model=resolve_model(config, "reviewer_1bot"),
            cwd=review_dir,
            system_prompt=system_prompt,
            allowed_tools=["Read", "Write", "Glob", "Grep"],
        )
        cost_tracker.add(reviewer_name, reviewer_result)

        review_file = find_latest_artifact(review_dir, f"*{reviewer_name}*")
        if not review_file:
            console.print("[red]Reviewer produced no artifact — escalating[/red]")
            return ReviewOutcome(status="escalated", iterations=i)

        if not review_has_category_a(review_file):
            # Check for regression
            origin = extract_regression_origin(review_file)
            if origin:
                return ReviewOutcome(
                    status="regression", iterations=i, regression_origin=origin
                )
            return ReviewOutcome(status="pass", iterations=i)

        # Category A issues — iterate
        exec_name = name_pool.pick()
        exec_result = await run_agent(
            name=exec_name,
            prompt=build_executor_prompt(
                session_name=exec_name,
                phase=Path(phase_dir).name,
                data_paths=config.data_paths,
                iteration=i + 1,
                review_feedback_path=str(review_file),
            ),
            model=resolve_model(config, "executor_default"),
            cwd=phase_dir,
            system_prompt=system_prompt,
        )
        cost_tracker.add(exec_name, exec_result)

    console.print(
        f"[bold red]1-bot review hit hard cap ({max_iter} iterations) "
        f"for {phase_dir} — escalating to human[/bold red]"
    )
    return ReviewOutcome(status="escalated", iterations=max_iter)
