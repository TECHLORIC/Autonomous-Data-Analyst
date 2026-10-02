from celery import Celery
from celery.signals import worker_process_init
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.worker.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)

@worker_process_init.connect
def init_worker(**kwargs):
    import app.db.session as session_module
    from sqlalchemy.ext.asyncio import create_async_engine
    
    session_module.engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        pool_pre_ping=True,
    )
    session_module.AsyncSessionLocal.configure(bind=session_module.engine)
