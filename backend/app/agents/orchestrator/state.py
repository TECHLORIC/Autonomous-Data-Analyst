from dataclasses import dataclass, field
from typing import Any


@dataclass
class AnalysisState:
    """
    Serializable state for the autonomous analysis workflow.

    Important:
    Do NOT store DataFrames, database connections, LLM clients,
    or other runtime objects here.
    """

    # -------------------------
    # Request
    # -------------------------

    dataset_id: str
    question: str
    file_path: str = ""

    # -------------------------
    # Dataset metadata
    # -------------------------

    dataset_profile: dict[str, Any] = field(
        default_factory=dict
    )

    # -------------------------
    # Planning
    # -------------------------

    plan: dict[str, Any] = field(
        default_factory=dict
    )

    # -------------------------
    # Analysis results
    # -------------------------

    results: list[dict[str, Any]] = field(
        default_factory=list
    )

    # -------------------------
    # Visualization
    # -------------------------

    visualizations: list[dict[str, Any]] = field(
        default_factory=list
    )

    insights: dict[str, Any] = field(default_factory=dict)

    # -------------------------
    # Validation
    # -------------------------

    errors: list[str] = field(
        default_factory=list
    )

    # -------------------------
    # Retry control
    # -------------------------

    retry_count: int = 0

    max_retries: int = 2

    # -------------------------
    # Workflow metadata
    # -------------------------

    current_step: int = 0

    status: str = "pending"
