from typing import Any

from pydantic import BaseModel


class AnalysisRequest(BaseModel):

    dataset_id: str

    question: str


class AnalysisPlanResponse(BaseModel):

    dataset_id: str

    question: str

    plan: dict[str, Any]


class ValidationResponse(BaseModel):

    valid: bool

    reason: str

    suggestion: str


class AnalysisResponse(BaseModel):

    dataset_id: str

    question: str

    plan: dict[str, Any]

    results: list[dict[str, Any]]

    visualizations: list[
        dict[str, Any]
    ]

    insights: dict[str, Any] = {}

    errors: list[str]

    retry_count: int
