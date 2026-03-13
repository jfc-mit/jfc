"""CLI entry point for the slopspec orchestrator."""

import argparse
import asyncio
import sys

from rich.console import Console

from .config import load_config
from .pipeline import run_pipeline

console = Console()


def main():
    parser = argparse.ArgumentParser(
        description="slopspec — LLM-driven HEP analysis orchestrator.",
    )
    parser.add_argument("config", help="Path to analysis config YAML")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print pipeline plan without executing",
    )
    parser.add_argument(
        "--resume-from",
        metavar="PHASE",
        help="Resume from a specific phase (e.g., phase3_selection)",
    )
    args = parser.parse_args()

    config = load_config(args.config)

    if args.dry_run:
        console.print(f"[bold]Analysis:[/bold] {config.analysis_name}")
        console.print(f"[bold]Channels:[/bold] {', '.join(config.channels)}")
        console.print(f"[bold]Calibrations:[/bold] {', '.join(config.calibrations)}")
        console.print(f"[bold]Model tier:[/bold] {config.model_tier}")
        console.print(f"[bold]Max review iter:[/bold] {config.cost_controls.max_review_iterations}")
        console.print(f"[bold]Budget warn:[/bold] ${config.cost_controls.total_budget_warn:.2f}")
        console.print("\n[dim]Dry run — no agents launched.[/dim]")
        return

    try:
        asyncio.run(run_pipeline(config))
    except KeyboardInterrupt:
        console.print("\n[red]Pipeline interrupted by user.[/red]")
        sys.exit(1)
    except RuntimeError as e:
        console.print(f"\n[bold red]Pipeline stopped:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
