from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.execution.duckdb import DuckDBEngine
from app.schemas.analysis import QueryRequest, QueryResponse


router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"],
)


UPLOAD_DIRECTORY = Path("storage/uploads")


@router.post(
    "/query",
    response_model=QueryResponse,
)
async def execute_query(
    request: QueryRequest,
) -> QueryResponse:

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

    engine = DuckDBEngine()

    try:
        engine.load_file(file_path)

        rows = engine.execute(
            request.query
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Query execution failed: {exc}",
        ) from exc

    finally:
        engine.close()

    return QueryResponse(
        dataset_id=request.dataset_id,
        query=request.query,
        rows=rows,
    )