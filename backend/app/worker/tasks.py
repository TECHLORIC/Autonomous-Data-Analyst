import asyncio
import logging
from datetime import datetime, timezone
import uuid

from app.core.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.db.models import AnalysisRun, AnalysisStep
from app.agents.orchestrator.graph import AutonomousAnalysisGraph
from app.data.ingestion.service import read_dataset
from app.data.profiling.service import profile_dataframe
from app.services.storage import storage
from pathlib import Path

logger = logging.getLogger(__name__)

async def _run_analysis_async(run_id: str):
    async with AsyncSessionLocal() as db:
        db_run = await db.get(AnalysisRun, uuid.UUID(run_id))
        if not db_run:
            logger.error(f"AnalysisRun {run_id} not found")
            return

        db_run.status = "running"
        await db.commit()
        
        try:
            # We need the dataset for profiling and the graph
            from app.db.models import Dataset
            dataset = await db.get(Dataset, db_run.dataset_id)
            if not dataset:
                raise ValueError("Dataset not found")
                
            temp_file = storage.download_to_temp_file(dataset.storage_path)
            
            try:
                dataframe = read_dataset(Path(temp_file))
                profile = profile_dataframe(dataframe)
                
                graph = AutonomousAnalysisGraph()
                state = await graph.run(
                    dataset_id=str(dataset.id),
                    file_path=temp_file,
                    question=db_run.question,
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
            finally:
                if temp_file != dataset.storage_path:
                    Path(temp_file).unlink(missing_ok=True)
                    
        except Exception as e:
            logger.exception("Background task failed")
            db_run.status = "failed"
            db_run.errors = [str(e)]
            await db.commit()

@celery_app.task(name="execute_analysis_task")
def execute_analysis_task(run_id: str):
    logger.info(f"Starting Celery task for AnalysisRun {run_id}")
    asyncio.run(_run_analysis_async(run_id))
    logger.info(f"Completed Celery task for AnalysisRun {run_id}")
