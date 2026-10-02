from app.db.base import Base
from app.db.models import (
    AnalysisRun,
    Dataset,
    User,
)
from app.db.session import engine


async def init_db() -> None:

    # Alembic handles schema creation. We just verify the engine can connect.
    async with engine.begin() as connection:
        pass
