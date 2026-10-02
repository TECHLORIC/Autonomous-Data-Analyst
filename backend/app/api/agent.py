from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.agents.orchestrator.orchestrator import AnalysisOrchestrator
from app.data.ingestion.service import read_dataset
from app.data.profiling.service import profile_dataframe
from app.schemas.agent import (
    AnalysisPlanResponse,
    AnalysisRequest,
)


router = APIRouter(
    prefix="/agent",
    tags=["Agent"],
)


UPLOAD_DIRECTORY = Path("storage/uploads")


@router.post(
    "/plan",
    response_model=AnalysisPlanResponse,
)
async def create_analysis_plan(
    request: AnalysisRequest,
) -> AnalysisPlanResponse:

    matching_files = list(
        UPLOAD_DIRECTORY.glob(
            f"{request.dataset_id}.*"
        )
    )

    if not matching_files:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found.",
        )

    file_path = matching_files[0]

    try:
        dataframe = read_dataset(file_path)
        profile = profile_dataframe(dataframe)

        orchestrator = AnalysisOrchestrator()

        state = await orchestrator.create_plan(
            dataset_id=request.dataset_id,
            question=request.question,
            dataset_profile=profile,
        )

    except (ValueError, RuntimeError) as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to create an analysis plan.",
        ) from exc

    return AnalysisPlanResponse(
        dataset_id=request.dataset_id,
        question=request.question,
        plan=state.plan,
    )
