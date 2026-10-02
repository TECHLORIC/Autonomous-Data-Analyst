import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base


class AnalysisRun(Base):

    __tablename__ = "analysis_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    dataset_id: Mapped[uuid.UUID] = (
        mapped_column(
            UUID(as_uuid=True),
            ForeignKey("datasets.id"),
            nullable=False,
            index=True,
        )
    )

    question: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
    )

    plan: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    results: Mapped[list | None] = (
        mapped_column(
            JSON,
            nullable=True,
        )
    )

    visualizations: Mapped[list | None] = (
        mapped_column(
            JSON,
            nullable=True,
        )
    )

    insights: Mapped[dict | None] = (
        mapped_column(
            JSON,
            nullable=True,
        )
    )

    errors: Mapped[list | None] = (
        mapped_column(
            JSON,
            nullable=True,
        )
    )

    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    created_at: Mapped[datetime] = (
        mapped_column(
            DateTime(timezone=True),
            default=datetime.utcnow,
            nullable=False,
        )
    )

    completed_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    steps: Mapped[list["AnalysisStep"]] = relationship(
        "AnalysisStep",
        back_populates="run",
        cascade="all, delete-orphan",
    )


class AnalysisStep(Base):

    __tablename__ = "analysis_steps"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analysis_runs.id"),
        nullable=False,
        index=True,
    )

    tool_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    task_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    query_executed: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    results: Mapped[dict | list | None] = mapped_column(
        JSON,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="completed",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    run: Mapped["AnalysisRun"] = relationship(
        "AnalysisRun",
        back_populates="steps",
    )

