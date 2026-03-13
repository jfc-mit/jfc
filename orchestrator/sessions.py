"""Agent session runner — wraps claude_agent_sdk.query() into run_agent()."""

import time
from dataclasses import dataclass, field
from pathlib import Path

from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query
from rich.console import Console

console = Console()


@dataclass
class SessionResult:
    session_id: str = ""
    cost_usd: float = 0.0
    duration_ms: int = 0
    num_turns: int = 0
    success: bool = False


@dataclass
class CostTracker:
    total_usd: float = 0.0
    sessions: list[dict] = field(default_factory=list)

    def add(self, name: str, result: SessionResult):
        self.total_usd += result.cost_usd
        self.sessions.append({"name": name, "cost": result.cost_usd})

    def check_budget(self, warn_threshold: float, on_exceeded: str) -> bool:
        """Returns True if pipeline should pause."""
        if self.total_usd >= warn_threshold:
            console.print(
                f"[bold yellow]Budget warning:[/] ${self.total_usd:.2f} spent "
                f"(threshold: ${warn_threshold:.2f})"
            )
            if on_exceeded == "pause":
                return True
        return False


async def run_agent(
    *,
    name: str,
    prompt: str,
    model: str,
    cwd: str,
    system_prompt: str,
    allowed_tools: list[str] | None = None,
    mcp_servers: dict | None = None,
    max_turns: int | None = None,
    max_budget_usd: float | None = None,
) -> SessionResult:
    """Run a single isolated agent session via claude_agent_sdk.query()."""
    if allowed_tools is None:
        allowed_tools = ["Read", "Write", "Edit", "Bash", "Glob", "Grep"]

    # Ensure working directory exists
    Path(cwd).mkdir(parents=True, exist_ok=True)

    options = ClaudeAgentOptions(
        model=model,
        system_prompt=system_prompt,
        cwd=cwd,
        permission_mode="bypassPermissions",
        allowed_tools=allowed_tools,
        max_turns=max_turns,
        max_budget_usd=max_budget_usd,
    )
    if mcp_servers:
        options.mcp_servers = mcp_servers

    result = SessionResult()
    t0 = time.monotonic()

    console.print(f"  [dim]Launching session [bold]{name}[/bold] ({model})...[/dim]")

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, ResultMessage):
            result.session_id = getattr(message, "session_id", "")
            result.cost_usd = getattr(message, "total_cost_usd", 0.0) or 0.0
            result.success = getattr(message, "subtype", "") == "success"

    result.duration_ms = int((time.monotonic() - t0) * 1000)

    status = "[green]done[/green]" if result.success else "[red]failed[/red]"
    console.print(
        f"  [dim]Session {name} {status} "
        f"(${result.cost_usd:.2f}, {result.duration_ms / 1000:.0f}s)[/dim]"
    )
    return result
