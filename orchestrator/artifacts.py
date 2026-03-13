"""Artifact file discovery, naming, and decision extraction."""

from datetime import datetime, timezone
from pathlib import Path


def timestamp_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M")


def artifact_filename(artifact_type: str, session_name: str) -> str:
    return f"{artifact_type}_{session_name}_{timestamp_str()}.md"


def find_latest_artifact(directory: str | Path, pattern: str = "*.md") -> Path | None:
    """Find the most recent artifact matching pattern, sorted by filename timestamp."""
    d = Path(directory)
    if not d.exists():
        return None
    candidates = sorted(d.glob(pattern), key=lambda p: p.name, reverse=True)
    return candidates[0] if candidates else None


def find_latest_review_artifact(review_dir: str | Path) -> Path | None:
    return find_latest_artifact(review_dir)


def extract_decision(arbiter_artifact: str | Path) -> str:
    """Extract PASS / ITERATE / ESCALATE from arbiter output.

    Searches from the bottom of the file for the decision token.
    Returns ESCALATE as safe default if parsing fails.
    """
    text = Path(arbiter_artifact).read_text()
    # Search from the end — the decision should be near the bottom
    for line in reversed(text.splitlines()):
        line_upper = line.strip().upper()
        if line_upper in ("PASS", "ITERATE", "ESCALATE"):
            return line_upper
        for token in ("PASS", "ITERATE", "ESCALATE"):
            if token in line_upper:
                return token
    return "ESCALATE"  # safe default


def review_has_category_a(review_artifact: str | Path) -> bool:
    """Check if a review artifact flags Category A issues."""
    text = Path(review_artifact).read_text().upper()
    return "CATEGORY A" in text


def extract_regression_origin(review_artifact: str | Path) -> str | None:
    """Extract the origin phase from a regression trigger."""
    text = Path(review_artifact).read_text()
    for line in text.splitlines():
        lower = line.lower()
        if "regression" in lower and "phase" in lower:
            # Try to extract phase name like "phase1_strategy"
            for token in line.split():
                if token.startswith("phase"):
                    return token.strip(".,;:")
    return None
