import logging
from pathlib import Path
from datetime import datetime, timezone
import uuid

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from app.core.rate_limit import limiter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.agents.orchestrator.graph import AutonomousAnalysisGraph
from app.data.ingestion.service import read_dataset
from app.data.profiling.service import profile_dataframe
from app.schemas.agent import AnalysisRequest, AnalysisResponse
from app.db.session import get_db
from app.db.models import AnalysisRun, Dataset, AnalysisStep
from app.api.deps import get_current_user
from app.db.models.user import User
from app.services.storage import storage

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/agent",
    tags=["Agent"],
)

async def _prepare_analysis(request: AnalysisRequest, db: AsyncSession, current_user: User | None):
    dataset_id_uuid = uuid.UUID(request.request.dataset_id) if hasattr(request, 'request') else uuid.UUID(request.dataset_id)
    dataset = await db.get(Dataset, dataset_id_uuid)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset record not found in database.")
        
    if dataset.user_id and (not current_user or dataset.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this dataset.")

    db_run = AnalysisRun(
        dataset_id=dataset_id_uuid,
        question=request.question,
        status="pending",
    )
    db.add(db_run)
    await db.commit()
    await db.refresh(db_run)

    temp_file = storage.download_to_temp_file(dataset.storage_path)

    try:
        dataframe = read_dataset(Path(temp_file))
        profile = profile_dataframe(dataframe)
    finally:
        pass
        
    return db_run, profile, temp_file

@router.post("/analyze", response_model=AnalysisResponse, status_code=200)
@limiter.limit("10/minute")
async def analyze(
    request: Request,
    payload: AnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user),
):
    logger.info("Starting analysis: dataset_id=%s question=%s", payload.dataset_id, payload.question)

    try:
        db_run, profile, dataset_storage_path = await _prepare_analysis(payload, db, current_user)
        
        db_run.status = "running"
        await db.commit()

        graph = AutonomousAnalysisGraph()
        
        state = await graph.run(
            dataset_id=payload.dataset_id,
            file_path=dataset_storage_path,
            question=payload.question,
            dataset_profile=profile,
        )
        
        db_run.status = state.status
        db_run.plan = state.plan
        db_run.results = state.results
        db_run.visualizations = state.visualizations
        db_run.insights = state.insights
        db_run.errors = state.errors
        db_run.retry_count = state.retry_count
        db_run.completed_at = datetime.now(timezone.utc)
        
        for res in state.results:
            step = AnalysisStep(
                run_id=db_run.id,
                tool_name=res.get("tool", "unknown"),
                task_description=res.get("task"),
                query_executed=res.get("query"),
                results=res.get("results"),
                status="completed"
            )
            db.add(step)
        
        await db.commit()

        dataset_id_uuid = uuid.UUID(payload.dataset_id)
        dataset = await db.get(Dataset, dataset_id_uuid)
        if dataset and dataset_storage_path != dataset.storage_path:
            Path(dataset_storage_path).unlink(missing_ok=True)
            
        return AnalysisResponse(
            dataset_id=payload.dataset_id,
            question=payload.question,
            plan=state.plan,
            results=state.results,
            visualizations=state.visualizations,
            insights=state.insights,
            errors=state.errors,
            retry_count=state.retry_count,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("FAILED TO RUN ANALYSIS")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(exc)}",
        ) from exc


@router.post("/analyze/stream")
async def analyze_stream(
    request: AnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user),
):
    logger.info("Starting streaming analysis: dataset_id=%s question=%s", request.dataset_id, request.question)
    
    try:
        db_run, profile, dataset_storage_path = await _prepare_analysis(request, db, current_user)
        
        db_run.status = "running"
        await db.commit()

        graph = AutonomousAnalysisGraph()
        
        async def event_generator():
            try:
                async for event in graph.stream(
                    dataset_id=request.dataset_id,
                    file_path=dataset_storage_path,
                    question=request.question,
                    dataset_profile=profile,
                ):
                    yield event
            except Exception as e:
                yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream"
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("AUTONOMOUS STREAMING ANALYSIS FAILED")
        raise HTTPException(
            status_code=500,
            detail="Analysis could not be started.",
        ) from exc


@router.get("/{run_id}/report", response_class=HTMLResponse)
async def generate_report(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user),
):
    """
    Generates a standalone HTML report for the specified analysis run.
    """
    from jinja2 import Environment, FileSystemLoader
    import markdown
    
    db_run = await db.get(AnalysisRun, uuid.UUID(run_id))
    if not db_run:
        raise HTTPException(status_code=404, detail="Analysis run not found.")
        
    dataset = await db.get(Dataset, db_run.dataset_id)
    if dataset.user_id and (not current_user or dataset.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this report.")
        
    stmt = select(AnalysisStep).where(AnalysisStep.run_id == db_run.id).order_by(AnalysisStep.id)
    result = await db.execute(stmt)
    steps = result.scalars().all()
    
    insights_html = ""
    if db_run.insights:
        raw_insights = db_run.insights.get("summary", "") if isinstance(db_run.insights, dict) else str(db_run.insights)
        insights_html = markdown.markdown(raw_insights)
        
    env = Environment(loader=FileSystemLoader("app/templates"))
    template = env.get_template("report.html")
    
    html_content = template.render(
        run=db_run,
        dataset=dataset,
        steps=steps,
        insights_html=insights_html,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    )
    
    return HTMLResponse(content=html_content)
