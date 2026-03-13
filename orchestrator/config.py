"""Configuration loading and model resolution."""

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class CostControls:
    max_review_iterations: int = 10
    review_warn_threshold: int = 3
    review_strong_warn_threshold: int = 5
    total_budget_warn: float = 50.0  # USD
    on_budget_exceeded: str = "pause"  # "pause" | "warn_and_continue"


DEFAULT_TIERS = {
    "executor_strategy": "opus",
    "executor_default": "sonnet",
    "reviewer_3bot": "opus",
    "reviewer_1bot": "sonnet",
    "arbiter": "opus",
    "investigator": "opus",
    "calibration": "sonnet",
    "mechanical": "haiku",
}


@dataclass
class AnalysisConfig:
    analysis_name: str
    physics_prompt_path: str
    methodology_path: str = "methodology.md"
    data_paths: dict = field(default_factory=dict)
    channels: list[str] = field(default_factory=lambda: ["default"])
    calibrations: list[str] = field(default_factory=list)
    model_tier: str = "auto"  # "auto" | "uniform_high" | "uniform_mid"
    tiers: dict[str, str] = field(default_factory=lambda: dict(DEFAULT_TIERS))
    cost_controls: CostControls = field(default_factory=CostControls)
    rag: dict | None = None
    git_enabled: bool = True

    @property
    def base_dir(self) -> Path:
        return Path(self.analysis_name)


def load_config(path: str) -> AnalysisConfig:
    """Load analysis config from YAML."""
    with open(path) as f:
        raw = yaml.safe_load(f)

    cost_raw = raw.pop("cost_controls", {})
    cost = CostControls(**cost_raw)

    tiers = {**DEFAULT_TIERS, **raw.pop("tiers", {})}
    return AnalysisConfig(**raw, cost_controls=cost, tiers=tiers)


def resolve_model(config: AnalysisConfig, role: str) -> str:
    """Resolve a role to a concrete model string."""
    if config.model_tier == "uniform_high":
        return "opus"
    if config.model_tier == "uniform_mid":
        return "sonnet"
    # auto: look up in tiers, fall back to sonnet
    return config.tiers.get(role, "sonnet")
