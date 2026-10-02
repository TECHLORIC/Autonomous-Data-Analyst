from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.core.config import settings
from app.db.session import get_db
from app.schemas.health import (
    HealthResponse,
)


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get(
    "",
    response_model=HealthResponse,
)
async def health_check() -> HealthResponse:

    return HealthResponse(
        status="healthy",
        service=settings.app_name,
        environment=settings.environment,
    )


@router.get("/ready")
async def readiness_check(
    db: AsyncSession = Depends(
        get_db
    ),
):

    database_status = "healthy"

    try:

        await db.execute(
            text("SELECT 1")
        )

    except Exception:

        database_status = "unhealthy"

    return {
        "status": (
            "ready"
            if database_status == "healthy"
            else "not_ready"
        ),
        "database": database_status,
    }