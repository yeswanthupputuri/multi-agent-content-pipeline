from datetime import datetime, timezone
from typing import Any

from app.state.content_state import ContentState


def start_metrics(state: ContentState, thread_id: str) -> ContentState:
    """Initialize metrics when a workflow starts."""

    state["metrics"] = {
        "thread_id": thread_id,
        "status": "running",
        "execution_time_seconds": 0.0,
        "revision_count": 0,
        "editor_decisions": 0,
        "fact_check_decisions": 0,
        "claims_checked": 0,
        "errors": 0,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
    }

    return state


def update_metrics(
    state: ContentState,
    *,
    editor_decision: bool = False,
    fact_check_decision: bool = False,
    claims_checked: int = 0,
) -> ContentState:
    """Update workflow metrics during execution."""

    metrics = state.setdefault("metrics", {})

    if editor_decision:
        metrics["editor_decisions"] = (
            metrics.get("editor_decisions", 0) + 1
        )

    if fact_check_decision:
        metrics["fact_check_decisions"] = (
            metrics.get("fact_check_decisions", 0) + 1
        )

    metrics["claims_checked"] = (
        metrics.get("claims_checked", 0) + claims_checked
    )

    metrics["revision_count"] = state.get(
        "revision_count",
        0
    )

    metrics["errors"] = len(
        state.get("errors", [])
    )

    return state


def finish_metrics(
    state: ContentState
) -> ContentState:
    """Finalize metrics when workflow execution ends."""

    metrics = state.setdefault("metrics", {})

    started_at = metrics.get("started_at")

    if started_at:
        start_time = datetime.fromisoformat(started_at)
        elapsed = (
            datetime.now(timezone.utc) - start_time
        ).total_seconds()

        metrics["execution_time_seconds"] = round(
            elapsed,
            2
        )

    metrics["status"] = state.get(
        "status",
        "unknown"
    )

    metrics["revision_count"] = state.get(
        "revision_count",
        0
    )

    metrics["errors"] = len(
        state.get("errors", [])
    )

    metrics["completed_at"] = (
        datetime.now(timezone.utc).isoformat()
    )

    return state